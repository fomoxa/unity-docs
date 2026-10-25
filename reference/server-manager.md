# ServerManager reference

`public sealed class ServerManager` in `Fomoxa.Networking` has no public constructor; you reach it through `NetworkManager.ServerManager`. The [server](../connections/server.md) guide explains how to use it.

## Connection

| Member | Description |
|---|---|
| `void StartConnection(ushort port)` | Opens the transport's listener and the in-process listener, then spawns the scene objects of the loaded scenes. Port 0 picks a free port. Throws `InvalidOperationException` when already running, `PlatformNotSupportedException` in a browser. |
| `void StopConnection()` | Disconnects every peer, despawns every object, unloads the network scenes |
| `ServerState State` | `Stopped`, `Starting`, `Started` or `Stopping` |
| `ushort Port` | The bound port; 0 while stopped |
| `int PeerCount` | Connected peers, including those not started yet |
| `ConnectionState PeerState(ulong peerId)` | A peer's state; `Stopped` when unknown |
| `void Disconnect(ulong peerId)` | Closes a peer's connection at once with `StopReason.LocalStop` |
| `bool Kick(ulong peerId)` | Sends the queued messages and a notice to the client, then closes the connection; the client stops with `ServerClosed` and does not reconnect. False when the peer is unknown or already closing. |
| `bool HasRtt(ulong peerId)`, `TimeSpan RttOf(ulong peerId)` | Round-trip time reported by the peer's clock pings; `TimeSpan.Zero` when none |
| `int DroppedInputsOf(ulong peerId)` | Inputs from the peer that were dropped |
| `int FrameBudgetOf(ulong peerId)` | Frame budget of the peer's transport; 0 when unknown |
| `IServerAuthenticator Authenticator` | The server side of the [authentication](../connections/authentication.md). Get and set; setting it while the server is running throws `InvalidOperationException`. |

## Objects

| Member | Description |
|---|---|
| `void Spawn(INetworkEntity networkObject, ulong ownerId = 0)` | Spawns an instance. Throws `ArgumentNullException`, `InvalidOperationException` when the server is not started, `ArgumentException` for a prefab asset, an object already spawned, an unregistered prefab id, an invalid scene object or an owner that is not a started peer. |
| `bool Despawn(INetworkEntity networkObject)` | Despawns and destroys an instance, or deactivates a scene object. False when not spawned by this server. |
| `bool ChangeOwner(INetworkEntity networkObject, ulong ownerId)` | Changes the owner; 0 for the server. False when not spawned by this server or the owner is not a started peer. |
| `IReadOnlyDictionary<uint, INetworkEntity> Spawned` | Spawned objects by object id |

## Observers

| Member | Description |
|---|---|
| `IObserverRule ObserverRule` | The rule for objects with `Visibility.Rule`, usually an `ObserverRule` asset. Get and set. |
| `int ObserverInterval` | Ticks over which every object is recalculated once. At least 1. |
| `ObserverGroups Groups` | The [groups](../objects/observers.md#groups) of peers and objects |
| `bool IsObserver(INetworkEntity networkObject, ulong peerId)` | Whether the peer observes the object |
| `bool RebuildObservers(INetworkEntity networkObject)` | Recalculates one object for every peer |
| `void RebuildObserversOfPeer(ulong peerId)` | Recalculates every object for one peer |
| `void RebuildObservers()` | Recalculates every object for every peer |

`NetworkObject` implements `INetworkEntity`, so you pass a `NetworkObject` to these methods. Calling a spawn, despawn, owner, rebuild or group method from inside `ObserverRule.Observes` throws.

### ObserverGroups

`public sealed class ObserverGroups`, reached through `ServerManager.Groups`. A group id is any `uint`. Each method that changes a group recalculates the affected pairs and queues their spawns and despawns before it returns.

| Member | Description |
|---|---|
| `void Add(uint groupId, ulong peerId)` | Adds the peer to the group. If the peer has started, recalculates the group's spawned objects for that peer. |
| `bool Remove(uint groupId, ulong peerId)` | Removes the peer from the group and recalculates the same pairs. False when the peer was not in the group. |
| `void Add(uint groupId, INetworkEntity networkObject)` | Adds the object to the group. If this server spawned it, recalculates it for every peer. Throws `ArgumentNullException` for null. |
| `bool Remove(uint groupId, INetworkEntity networkObject)` | Removes the object from the group and recalculates it in the same way. False when the object was not in the group. Throws `ArgumentNullException` for null. |
| `bool Contains(uint groupId, ulong peerId)` | Whether the peer is in the group |
| `bool Contains(uint groupId, INetworkEntity networkObject)` | Whether the object is in the group |

A peer leaves all its groups when it disconnects, an object leaves all its groups when it is despawned, and stopping the server clears every group.

## Scenes

The `Scenes` property returns a `NetworkScenes`, a type in `Fomoxa.Networking` with these members:

| Member | Description |
|---|---|
| `void LoadGlobal(IReadOnlyList<uint> sceneIds, bool replace = false)` | Loads scenes for every peer; `replace` unloads the current global scenes first. Throws for an unregistered id. |
| `void UnloadGlobal(IReadOnlyList<uint> sceneIds)` | Unloads global scenes. Throws for an id that is not global. |
| `int LoadForPeers(uint sceneId, IReadOnlyList<ulong> peerIds)` | Loads a scene for some peers; returns how many were added. Throws for a global scene or an unregistered id. |
| `int UnloadForPeers(uint sceneId, IReadOnlyList<ulong> peerIds)` | Removes a per-peer scene from some peers; returns how many were removed |
| `void Unload(uint sceneId)` | Removes a per-peer scene from every peer |
| `IReadOnlyList<uint> Global` | Global scene ids |
| `bool Contains(uint sceneId)`, `bool IsGlobal(uint sceneId)` | Whether the scene is in use, and whether it is global |
| `bool HasLoaded(ulong peerId, uint sceneId)` | Whether the peer reported the scene as loaded |
| `IReadOnlyCollection<ulong> PeersOf(uint sceneId)` | Peers that have the scene |
| `bool TryGetScene(uint sceneId, out Scene scene)` | The `Scene` the server loaded; an extension method in `Fomoxa.Unity` |
| `event Action<uint> OnLoaded` | The server finished loading a scene |
| `event Action<uint, Exception> OnLoadFailed` | The server failed to load a scene |

The scene methods throw `InvalidOperationException` while the server is stopped.

## Messages

| Member | Description |
|---|---|
| `SendResult Send(ulong peerId, uint messageId, ReadOnlySpan<byte> payload)` | Queues a message for one peer |
| `SendResult SendToObject(ulong peerId, uint messageId, uint objectId, byte behaviourIndex, ReadOnlySpan<byte> body)` | Queues an object message for one peer |
| `int Broadcast(uint messageId, ReadOnlySpan<byte> payload)` | Queues a message for every started peer; returns the count |
| `MessageDispatcher Dispatcher` | Handlers for incoming messages |

## Events

| Event | Argument |
|---|---|
| `OnServerConnectionState` | `ServerConnectionStateArgs` |
| `OnRemoteConnectionState` | `ConnectionStateArgs` |
| `OnSendDropped` | `SendDroppedArgs` |
| `OnReceiveDropped` | `ReceiveDroppedArgs` |
| `OnHandlerException` | `HandlerExceptionArgs`; logged when nobody subscribes |

[Events and callbacks](callbacks.md) describes the event arguments.

The related types are [NetworkManager](network-manager.md), [ClientManager](client-manager.md) and [NetworkObject](network-object.md).
