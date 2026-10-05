# Server

`ServerManager`, which you reach through `NetworkManager.ServerManager`, runs the server side of a game. It listens for clients, keeps track of the connected peers, spawns objects and decides who observes them.

## Start and stop

```csharp
manager.ServerManager.StartConnection(7777);
Debug.Log($"listening on {manager.ServerManager.Port}");

manager.ServerManager.StopConnection();
```

`StartConnection(port)` opens the transport's listener, plus an in-process listener for a host client. Port 0 lets the operating system choose a port, and `Port` reports the port in use, or 0 while the server is stopped. Calling `StartConnection` on a running server throws `the server is already running`. As it starts, the server spawns every `NetworkObject` placed in the loaded scenes, as described in [spawning](spawning.md#scene-objects).

`StopConnection()` disconnects every client and despawns every object in reverse spawn order, destroying prefab instances and deactivating scene objects. It then unloads the network scenes the server loaded and sets `State` to `Stopped`.

`State` is a `ServerState`, one of `Stopped`, `Starting`, `Started` and `Stopping`, and `OnServerConnectionState` reports each change.

## Peers

Every client gets a peer id when its transport connects, and `OnRemoteConnectionState` reports the client's states:

```csharp
manager.ServerManager.OnRemoteConnectionState += args =>
{
    switch (args.State)
    {
        case ConnectionState.Starting:
            Debug.Log($"peer {args.PeerId} is connecting");
            break;
        case ConnectionState.Started:
            Debug.Log($"peer {args.PeerId} joined");
            break;
        case ConnectionState.Stopped:
            Debug.Log($"peer {args.PeerId} left: {args.Reason}, {args.DiscardedMessages} messages discarded");
            break;
    }
};
```

Spawn a peer's objects once it reaches `Started`, since it cannot receive them before that. The server does not expose a list of peer ids, so if you need one, keep your own set from these events.

| Member | Purpose |
|---|---|
| `PeerCount` | Connected peers, including those still in the handshake |
| `PeerState(peerId)` | A peer's `ConnectionState`; `Stopped` for an unknown peer |
| `Disconnect(peerId)` | Closes a peer's connection; it stops with `LocalStop` |
| `HasRtt(peerId)`, `RttOf(peerId)` | The round-trip time the peer's client reported with its clock pings |
| `DroppedInputsOf(peerId)` | Inputs from the peer that the server could not use |
| `FrameBudgetOf(peerId)` | The frame budget of the transport the peer connected through |

When a peer stops, the server despawns the objects it owned. Objects whose `NetworkObject` has Despawn With Owner turned off stay and become server-owned instead; see [ownership](ownership.md).

## Objects

| Member | Guide |
|---|---|
| `Spawn(networkObject, ownerId)`, `Despawn(networkObject)` | [Spawning](spawning.md) |
| `ChangeOwner(networkObject, ownerId)` | [Ownership](ownership.md) |
| `IsObserver`, `RebuildObservers`, `ObserverRule`, `ObserverInterval` | [Observers](observers.md) |
| `Scenes` | [Network scenes](scenes.md) |
| `Spawned` | All objects spawned by this server, by object id |

## Messages

`Send(peerId, messageId, payload)`, `SendToObject(...)` and `Broadcast(messageId, payload)` send messages that are not tied to RPCs, and `Dispatcher` registers handlers for incoming messages. [Raw messages](../messaging/messages.md) shows how to use them.

## Errors in handlers

When a handler throws while the server processes a peer's message, such as a server RPC, the server disconnects that peer with `StopReason.HandlerException` and raises `OnHandlerException` with the peer id, the message id and the exception. If nothing subscribes to the event, the package logs the exception. A message that fails to decode does not disconnect the peer; it is dropped and raises `OnReceiveDropped`.

Exceptions thrown in `apply` of an input model or in an `ObserverRule` are logged and do not disconnect anyone.

The [ServerManager reference](../reference/server-manager.md) lists every member. For running the server on its own or together with a client, see [dedicated server](../server/dedicated-server.md) and [host mode](host-mode.md).
