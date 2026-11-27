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
| `PeerIds StartedPeers` | The ids of the peers in `Started`, the ones `Broadcast` sends to; see [the peer list](#the-peer-list) |
| `ConnectionState PeerState(ulong peerId)` | A peer's state; `Stopped` when unknown |
| `void Disconnect(ulong peerId)` | Closes a peer's connection at once with `StopReason.LocalStop` |
| `bool Kick(ulong peerId)` | Sends the queued messages and a notice to the client, then closes the connection; the client stops with `ServerClosed` and does not reconnect. False when the peer is unknown or already closing. |
| `bool Transfer(ulong peerId, string address, ushort port, ReadOnlyMemory<byte> ticket)` | Sends the queued messages, then the address, port and ticket of another server, then closes the connection like `Kick`; the peer stops with `Transferred`. False when the peer is unknown, already closing or not `Started`. Throws `ArgumentNullException` for a null address and `InvalidOperationException` for a host's own client. See [server transfer](../connections/transfer.md). |
| `bool Transfer(ulong peerId, string address, ushort port, ReadOnlyMemory<byte> ticket, ReadOnlyMemory<byte> connection)` | The same, and sends the grant the client needs for a new server on [encrypted UDP](../connections/transports/encrypted-udp.md#server-transfers) |
| `bool HasRtt(ulong peerId)`, `TimeSpan RttOf(ulong peerId)` | Round-trip time reported by the peer's clock pings; `TimeSpan.Zero` when none |
| `int DroppedInputsOf(ulong peerId)` | Inputs from the peer that were dropped |
| `long DroppedInputs` | Dropped inputs of every peer since the server was created, including peers that have left |
| `ServerTrafficStatistics Statistics` | [Traffic counters](../advanced/debugging.md#traffic-counters) of every peer, with `Of(peerId)` for one peer; `null` when Collect Statistics is off |
| `int FrameBudgetOf(ulong peerId)` | Frame budget of the peer's transport; 0 when unknown |
| `IServerAuthenticator Authenticator` | The server side of the [authentication](../connections/authentication.md). Get and set; setting it while the server is running throws `InvalidOperationException`. |

### The peer list

`StartedPeers` is a `PeerIds` in `Fomoxa.Networking.Sessions`, an `IReadOnlyCollection<ulong>` with `Count` and `Contains(ulong peerId)`. A peer joins it when it reaches `Started` and leaves it at the call that kicks, transfers or rejects it, or when it stops. `foreach` over it does not allocate.

The list is live. When it changes while a loop goes over it, the next step of the loop throws `InvalidOperationException`, as a `Dictionary` does. To kick or transfer peers in a loop, copy the list first:

```csharp
foreach (ulong peerId in new List<ulong>(manager.ServerManager.StartedPeers))
{
    manager.ServerManager.Kick(peerId);
}
```

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

The `Scenes` property returns a `NetworkScenes`, a type in `Fomoxa.Networking` with these members. A `NetworkScene` is a readonly struct in `Fomoxa.Networking` that names one loaded instance; its `Id` is the raw value, and `default` means no network scene. `ScenePhysics` is an enum with `Shared` and `Own`.

| Member | Description |
|---|---|
| `IReadOnlyList<NetworkScene> LoadGlobal(IReadOnlyList<uint> sceneIds, bool replace = false, ScenePhysics physics = ScenePhysics.Shared)` | Loads scenes for every peer and returns their global instances, one for each id; an asset that already has a global instance returns it. `replace` unloads the current global instances first. Throws for an unregistered id. |
| `void UnloadGlobal(IReadOnlyList<NetworkScene> scenes)` | Unloads global instances. Throws for an instance that is not global. |
| `NetworkScene Load(uint sceneId, IReadOnlyList<ulong> peerIds, ScenePhysics physics = ScenePhysics.Shared)` | Creates a new instance for some peers, which may be none. Throws for an unregistered id. |
| `int AddPeers(NetworkScene scene, IReadOnlyList<ulong> peerIds)` | Gives a per-peer instance to more peers; returns how many were added |
| `int RemovePeers(NetworkScene scene, IReadOnlyList<ulong> peerIds)` | Removes a per-peer instance from some peers; returns how many were removed. The instance stays loaded. |
| `void Unload(NetworkScene scene)` | Unloads a per-peer instance from its peers and from the server |
| `IReadOnlyList<NetworkScene> Global` | Global instances |
| `bool Contains(NetworkScene scene)`, `bool IsGlobal(NetworkScene scene)` | Whether the instance exists, and whether it is global |
| `bool HasLoaded(ulong peerId, NetworkScene scene)` | Whether the peer reported the instance as loaded |
| `IReadOnlyCollection<ulong> PeersOf(NetworkScene scene)` | Peers that have the instance |
| `IReadOnlyList<NetworkScene> ScenesOf(ulong peerId)` | Instances the peer has |
| `IReadOnlyList<NetworkScene> InstancesOf(uint sceneId)` | Instances of a scene asset |
| `uint SceneIdOf(NetworkScene scene)` | The scene id of an instance; 0 when the instance does not exist |
| `bool TryGetScene(NetworkScene scene, out Scene unityScene)` | The `Scene` the server loaded for the instance; an extension method in `Fomoxa.Unity` |
| `event Action<NetworkScene> OnLoaded` | The server finished loading an instance |
| `event Action<NetworkScene, Exception> OnLoadFailed` | The server failed to load an instance |
| `event Action<NetworkScene> OnUnloaded` | The server finished unloading an instance |
| `event Action<ulong, NetworkScene> OnPeerLoaded` | A peer reported an instance as loaded |

An unknown instance, or an instance of the wrong kind for the call, throws `ArgumentException`. A second `Shared` instance of a scene asset throws `ArgumentException`; give it `ScenePhysics.Own`. The scene methods throw `InvalidOperationException` while the server is stopped.

## Messages

| Member | Description |
|---|---|
| `SendResult Send(ulong peerId, uint messageId, ReadOnlySpan<byte> payload)` | Queues a message for one peer |
| `SendResult Send<T>(ulong peerId, IMessageCodec<T> codec, T value)` | Encodes the value with the codec and queues it for one peer |
| `SendResult SendToObject(ulong peerId, uint messageId, uint objectId, byte behaviourIndex, ReadOnlySpan<byte> body)` | Queues an object message for one peer |
| `int Broadcast(uint messageId, ReadOnlySpan<byte> payload)` | Queues a message for every started peer; returns the count |
| `int Broadcast<T>(IMessageCodec<T> codec, T value)` | Encodes the value once and queues it for every started peer; returns the count |
| `MessageDispatcher Dispatcher` | Handlers for incoming messages |

The two generic methods throw `ArgumentNullException` for a null codec.

## Events

| Event | Argument |
|---|---|
| `OnServerConnectionState` | `ServerConnectionStateArgs` |
| `OnRemoteConnectionState` | `ConnectionStateArgs` |
| `OnSendDropped` | `SendDroppedArgs` |
| `OnReceiveDropped` | `ReceiveDroppedArgs` |
| `OnHandlerException` | `HandlerExceptionArgs`; logged when nobody subscribes; set `Disconnect` to `false` to keep the peer |
| `OnInputRejected` | `InputRejectedArgs`; input from a peer that does not own the object; logged when nobody subscribes |
| `OnServerRpcRejected` | `ServerRpcRejectedArgs`; a server RPC with `RequireOwnership` from a peer that does not own the object; logged when nobody subscribes |

[Events and callbacks](callbacks.md) describes the event arguments.

The related types are [NetworkManager](network-manager.md), [ClientManager](client-manager.md) and [NetworkObject](network-object.md).
