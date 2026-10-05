# Lifecycle

This page gives the order of events for the `NetworkManager`, for connections and for network objects.

## NetworkManager

| Unity message | What the manager does |
|---|---|
| `Awake` | Reads the registered schema and codecs, registers the prefabs of Collected Prefabs and Prefabs, registers the scenes of Collected Scenes, creates the transport factory and the `ServerManager`, `ClientManager`, `TimeManager` and `TransportManager`. Throws if the generated registration has not run. |
| `OnEnable` | Adds its entries to the player loop. |
| `OnDisable` | Removes them. No ticks run, nothing is received or sent. |
| `OnDestroy` | Stops the client and the server, and releases the physics simulation. |

The manager also stops both connections when the application quits.

Because the managers are created in `Awake`, other components can rely on them from `Start` on, while in their own `Awake` the managers may not exist yet.

## Server

```text
ServerManager.StartConnection(port)
    ServerState: Stopped → Starting → Started
    every scene object in the loaded scenes is spawned
    for each client:
        OnRemoteConnectionState: Starting   transport connected, handshake runs
        OnRemoteConnectionState: Started    the client receives the objects it observes
        OnRemoteConnectionState: Stopped    with a StopReason; owned objects are despawned
ServerManager.StopConnection()
    ServerState: Started → Stopping → Stopped
    every client is disconnected, every object is despawned
```

## Client

```text
ClientManager.StartConnection(address, port)
    OnClientConnectionState: Starting
    OnClientConnectionState: Started      scene objects are deactivated until the server spawns them
    ... objects spawn, change and despawn ...
    OnClientConnectionState: Stopped      every object is despawned on the client
        WillRetry = true  → Starting again after the reconnect interval
        WillRetry = false → stays Stopped
ClientManager.StopConnection()
```

## Network objects

### On the server

```text
Instantiate(prefab)            Awake, OnEnable of your components
ServerManager.Spawn(instance)
    OnRegisterRpcs, OnRegisterState, OnRegisterInput   first spawn of this instance only
    initial state captured, spawn message queued to observers
    OnStartServer
... ticks ...
    OnOwnerChangedServer(previousOwnerId)              when the owner changes
ServerManager.Despawn(instance), owner leaves, or server stops
    OnStopServer
    despawn message queued
    prefab instance destroyed, scene object deactivated
```

The spawn message contains the state captured before `OnStartServer`, so set the initial state before calling `Spawn`. A change made in `OnStartServer` reaches clients only with the next tick's state update.

Destroying a spawned `GameObject` on the server despawns it.

### On a client

```text
spawn message arrives
    prefab instantiated, or scene object activated     Awake, OnEnable of your components
    OnRegisterRpcs, OnRegisterState, OnRegisterInput
    initial state applied
    OnStartClient                                      NetworkObject.IsOwner is valid here
... state changes, RPCs, transforms ...
    OnOwnerChangedClient(previousOwnerId)
despawn message, loss of observation, or client stops
    OnStopClient
    prefab instance destroyed or released to its factory, scene object deactivated
```

`NetworkBehaviour.NetworkObject` is set when the object spawns, so in `Awake` of a freshly instantiated prefab it is still null.

If a client destroys a spawned `GameObject` without a despawn from the server, the object is removed from the client's objects and a warning is logged.

### In host mode

In host mode the server and the host's client share one instance. That instance gets `OnStartServer` when the server spawns it and `OnStartClient` when the host's client receives it, and on despawn `OnStopClient` runs before `OnStopServer`. [Host mode](../core/host-mode.md) covers the consequences for your code.

The callbacks themselves are described in [NetworkBehaviour](../core/network-behaviour.md) and listed in [events and callbacks](../reference/callbacks.md). The [networking model](networking-model.md) explains the connection states in more depth.
