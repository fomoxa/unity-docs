# Agones

[Agones](https://agones.dev) runs game servers on Kubernetes as `GameServer` resources, grouped in a `Fleet` that it scales. A Fomoxa pod can run as one of these game servers. Fomoxa does not call Agones itself. Your server calls the Agones SDK next to `DirectoryPod`, and this page shows which calls go where.

> **Outcome:** your pods run in an Agones `Fleet`, register with the directory, are marked `Allocated` while they hold rooms, and leave the fleet after a drain.

The setup on this page runs Agones 1.61.0 on Kubernetes 1.36, with a console server that uses the C# SDK `AgonesSDK` 1.61.0. Agones also has an SDK for Unity with the same calls, for a server built as a Unity player.

## Prerequisites

- A Kubernetes cluster with Agones installed. See [installing Agones](https://agones.dev/site/docs/installation/).
- The directory and the game backend running in the cluster, and the gateway if you use one. The [cluster](cluster.md) page shows how they fit together.
- A game server that registers through `DirectoryPod`, as described under "Running as a pod" in the [`com.fomoxa.rpc` README](https://github.com/fomoxa/com.fomoxa.rpc).

## What Agones needs from a pod

| Agones expects | When the pod does it |
|---|---|
| `Ready()` | At startup, before it registers with the directory |
| `Health()` every few seconds | The whole time it runs |
| `Allocate()` | When it starts holding its first room |
| `Ready()` again | When it releases its last room, unless it is draining |
| `Shutdown()` | After a drain, once the transferred players have left |
| Its address and port | Without a gateway only: it registers them with the directory |

Agones only scales down game servers that are `Ready`. A pod that holds rooms stays `Allocated`, so scaling the fleet down never removes a pod with players on it.

## 1. Add the SDK

In the project of your server:

```
dotnet add package AgonesSDK --version 1.61.0
```

The SDK talks to a sidecar that Agones adds to every game server pod, on `localhost`. Outside Agones, for a local run, the Agones release has a local SDK server (`sdk-server.linux.amd64 --local` in `agonessdk-server-1.61.0.zip`) that answers the same calls.

## 2. Start the game server

Call `ReadyAsync` before the pod registers with the directory. The sidecar can take a moment to start with the pod, so retry until the call succeeds:

```csharp
using System;
using System.Linq;
using System.Threading.Tasks;
using Agones;
using Agones.Dev.Sdk;
using Grpc.Core;

var agones = new AgonesSDK();
await Retry(async () =>
{
    Status status = await agones.ReadyAsync();
    if (status.StatusCode != StatusCode.OK)
    {
        throw new InvalidOperationException(status.Detail);
    }
});

static async Task Retry(Func<Task> call)
{
    for (int attempt = 1; ; attempt++)
    {
        try
        {
            await call();
            return;
        }
        catch (Exception) when (attempt < 60)
        {
            await Task.Delay(500);
        }
    }
}
```

**With a gateway**, the pod registers with its own address inside the cluster, as on the [cluster](cluster.md) page, and turns on Behind Gateway on its encrypted transport.

**Without a gateway**, clients connect to the address and port that Agones gave the game server. Read them and register those with the directory:

```csharp
GameServer server = await agones.GetGameServerAsync();
string address = server.Status.Address;
ushort advertisedPort = (ushort)server.Status.Ports.First(port => port.Port_ > 0).Port_;

var pod = new DirectoryPod(runtime, new DirectoryPodSettings
{
    DirectoryAddress = "fomoxa-directory",
    DirectoryPort = 9500,
    Key = podKey,
    Address = address,
    Port = advertisedPort,
    Target = podName,
    Version = "1.0.0",
    MaxPlayers = 64,
});
```

The server still listens on the container port (7777 in the manifests below). Agones forwards the node's port to it, so `Port` in the settings is the advertised port and `StartConnection` takes the container port. Leave Behind Gateway off in this setup.

**Check:** `kubectl get gameservers` lists your game servers as `Ready`.

## 3. Send health pings

Call `HealthAsync` every two seconds from the server loop, for example in each tick:

```csharp
if (lastHealth == null || now - lastHealth.Value >= TimeSpan.FromSeconds(2))
{
    lastHealth = now;
    _ = agones.HealthAsync();
}
```

`lastHealth` is a `TimeSpan?` field and `now` is the time of the tick. Agones marks a game server `Unhealthy` and replaces it when no ping arrives within the health period of the fleet (5 seconds by default, 3 misses in a row).

## 4. Mark the rooms

Call `AllocateAsync` when `AcquireRoom` succeeds for the first room of the pod, and `ReadyAsync` when the pod releases its last room:

```csharp
await pod.AcquireRoom(roomKey);
if (pod.Rooms.Count == 1)
{
    await agones.AllocateAsync();
}
```

```csharp
await pod.ReleaseRoom(roomKey);
if (pod.Rooms.Count == 0 && !pod.IsDraining)
{
    await agones.ReadyAsync();
}
```

Agones uses `Allocated` for a game server handed to a match. Here it means the pod holds at least one room.

## 5. Drain and shut down

Drain the pod as on the [cluster](cluster.md#draining-a-pod) page: on `OnDrain`, move each room with `Relocate` and transfer its players with `ServerManager.Transfer`. Once the transferred players have left, call `ShutDownAsync`, and Agones removes the game server:

```csharp
if (roomsMoved && !shuttingDown && runtime.ServerManager.PeerCount == 0)
{
    shuttingDown = true;
    _ = agones.ShutDownAsync();
}
```

Wait for `PeerCount` to reach zero. A pod that shuts down right after `Transfer` can be stopped before the transfer reaches its clients.

When Kubernetes stops the pod, for example when the fleet scales down or the node drains, the process receives SIGTERM. Catch it and call `RequestDrain`, as the `com.fomoxa.rpc` README shows. Set `terminationGracePeriodSeconds` of the pod longer than `drain_seconds` of the directory, so the drain can finish before Kubernetes kills the process.

## 6. The fleet

With a gateway the pods need no port on the node, so the game port uses `portPolicy: None`:

```yaml
apiVersion: agones.dev/v1
kind: Fleet
metadata:
  name: game-pod
spec:
  replicas: 2
  template:
    metadata:
      labels:
        app: game-pod
    spec:
      ports:
        - name: game
          portPolicy: None
          containerPort: 7777
          protocol: UDP
      health:
        initialDelaySeconds: 10
        periodSeconds: 5
        failureThreshold: 3
      template:
        metadata:
          labels:
            app: game-pod
        spec:
          terminationGracePeriodSeconds: 330
          containers:
            - name: game
              image: my-game-server:1.0.0
              env:
                - { name: POD_NAME, valueFrom: { fieldRef: { fieldPath: metadata.name } } }
                - { name: POD_IP, valueFrom: { fieldRef: { fieldPath: status.podIP } } }
```

Without a gateway, use `portPolicy: Dynamic` instead. Agones then picks a port on the node for each game server and forwards it to `containerPort`. Leave `public_address` and `public_websocket` out of the directory's settings, so tickets carry the address each pod registered.

`POD_NAME` makes a good `Target` for the pod and `POD_IP` its address with a gateway. The key of the `pod` role comes from a Secret, as for the other parts of the cluster.

To keep spare game servers ready as rooms fill pods, attach a `FleetAutoscaler` with a buffer policy. Its buffer counts `Ready` game servers, which here are the pods without rooms:

```yaml
apiVersion: autoscaling.agones.dev/v1
kind: FleetAutoscaler
metadata:
  name: game-pod-autoscaler
spec:
  fleetName: game-pod
  policy:
    type: Buffer
    buffer:
      bufferSize: 2
      minReplicas: 2
      maxReplicas: 20
```

## Verify the result

1. `kubectl get gameservers` shows every game server `Ready` after the fleet starts.
2. After a player joins a room, the game server of its pod is `Allocated`.
3. After you drain that pod, its players arrive on another pod, its game server goes to `Shutdown` and disappears, and the fleet starts a new one.
4. `kubectl scale fleet game-pod --replicas=0` removes the `Ready` game servers and keeps the `Allocated` ones.

## Common mistakes

- **No health pings.** The game server turns `Unhealthy` a few seconds after it starts, and Agones replaces it.
- **Shutting down too early.** Calling `ShutDownAsync` right after `Transfer` can cut the transfer off before it reaches clients.
- **Behind Gateway on without a gateway.** The pod drops every datagram, since none carries the gateway's header.
- **WebGL clients without a gateway.** Browser clients connect over [encrypted WebSocket](../connections/transports/encrypted-websocket.md), which only the gateway serves, so they need the gateway setup.

## Next steps

- [Cluster](cluster.md): the parts of the cluster and how a room moves.
- [Game backend](backend.md): the service that hands players their tickets.
- [Agones documentation](https://agones.dev/site/docs/): fleets, autoscaling and installation options.
