# Host mode

A host runs a server and a client in one process, so the host's player plays on the same machine that serves everyone else.

## Basic usage

Start the server, then the client, on the same `NetworkManager`:

```csharp
manager.ServerManager.StartConnection(7777);
manager.ClientManager.StartConnection("localhost", manager.ServerManager.Port);
```

Because the manager's server is running, the client connects through an in-process [loopback](../transports/loopback.md) connection, ignoring the address and port and bypassing the transport. Other clients connect to the host over the transport, just as they would to a dedicated server.

The host's client gets a peer id like any other client, and the server spawns objects for it in `OnRemoteConnectionState` as usual.

## One instance per object

A host does not create a second copy of each object for its client; the server's instance is also the client's instance. The same component therefore gets `OnStartServer` when the server spawns the object and `OnStartClient` when the host's client receives it, and `NetworkObject.IsOwner` is true for the objects owned by the host's peer id.

Since the instance already holds the server's values, the host's client does not decode state a second time, although `onChanged` callbacks still run. For the same reason `NetworkTransform` does not interpolate on the host, where the transform already is the server's transform. Objects that would be predicted on a remote client are not predicted for the host either: the server gathers and applies the host's input directly in the same tick.

Code that must run once per object, such as starting an effect, should check whether it is running on the server, the client or both. On a host, `NetworkObject.IsSpawned` is true from the server spawn on.

## Objects the host's client does not observe

On a dedicated client, an object the client does not observe simply does not exist. On a host it has to exist because the server needs it, so the package hides it instead, by disabling every enabled `Renderer` under the object and calling `OnHostVisibility(false)` on its behaviours. When the host's client starts observing the object, the renderers come back and `OnHostVisibility(true)` runs.

Override `OnHostVisibility` to hide what renderers do not cover, such as audio or UI:

```csharp
protected override void OnHostVisibility(bool visible)
{
    audioSource.mute = !visible;
}
```

When the host's client stops, every object is shown again.

## Stopping

Stopping the host's client leaves the server running for the other clients, while stopping the server disconnects every client, including the host's.

## Limitations

A host cannot run in a WebGL build, because a browser cannot accept connections. Prediction does not run for the host's own objects, so the host never reconciles, but remote clients of the host predict their own objects normally.

Host mode combines the [server](server.md) and the [client](client.md) over a [loopback](../transports/loopback.md) connection, and [observers](observers.md) explains how the server decides what the host's client should see.
