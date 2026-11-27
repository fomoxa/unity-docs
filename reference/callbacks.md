# Events and callbacks reference

Every event and callback is raised on Unity's main thread, either from the `NetworkManager`'s player loop entries or from your own calls into the package.

## Connection events

| Event | On | Argument | Raised when |
|---|---|---|---|
| `OnServerConnectionState` | `ServerManager` | `ServerConnectionStateArgs` | The server's `ServerState` changes |
| `OnRemoteConnectionState` | `ServerManager` | `ConnectionStateArgs` | A client connection's state changes |
| `OnClientConnectionState` | `ClientManager` | `ConnectionStateArgs` | The client's state changes |
| `OnTransferring` | `ClientManager` | `TransferringArgs` | The server moved the client to another server; raised before the client's objects despawn and before `Stopped` |

`ServerConnectionStateArgs` has a single member, `ServerState State`. `TransferringArgs` has `string Address` and `ushort Port`, the server the client moves to. `ConnectionStateArgs` has these members:

| Member | Type | Description |
|---|---|---|
| `PeerId` | `ulong` | The client's peer id on the server; 0 on a client |
| `State` | `ConnectionState` | `Stopped`, `Starting`, `Authenticating` or `Started` |
| `Reason` | `StopReason` | Why it stopped; `None` otherwise |
| `Failure` | `HandshakeFailure` | The handshake failure when `Reason` is `HandshakeFailed` |
| `DiscardedMessages` | `int` | Queued messages dropped when the connection stopped |
| `WillRetry` | `bool` | On a client, whether a new attempt follows |
| `CloseReason` | `SessionCloseReason` | On a client stopped with `ServerClosed`, the reason the server sent; `Unspecified` otherwise |

## Message events

| Event | On | Argument | Raised when |
|---|---|---|---|
| `OnSendDropped` | both managers | `SendDroppedArgs` | A queued message could not be sent |
| `OnReceiveDropped` | both managers | `ReceiveDroppedArgs` | A received bundle, or a model in it, could not be read |
| `OnHandlerException` | both managers | `HandlerExceptionArgs` | A message handler threw; the server closes that peer's connection unless a subscriber clears `Disconnect`, or the client stops |
| `OnObjectMismatch` | `ClientManager` | `ObjectMismatchArgs` | The client could not apply an object message and stops |
| `OnInputRejected` | `ServerManager` | `InputRejectedArgs` | The server dropped input from a peer that does not own the object |
| `OnServerRpcRejected` | `ServerManager` | `ServerRpcRejectedArgs` | The server dropped a server RPC with `RequireOwnership` from a peer that does not own the object |

| Argument | Members |
|---|---|
| `SendDroppedArgs` | `ulong PeerId`, `uint MessageId`, `int PayloadLength`, `SendStatus Reason` |
| `ReceiveDroppedArgs` | `ulong PeerId`, `int FrameLength` |
| `HandlerExceptionArgs` | `ulong PeerId`, `uint MessageId`, `Exception Exception`, `bool Disconnect`; `Disconnect` starts as `true`, and setting it to `false` keeps the peer after a server message handler threw; the server ignores it for the authenticator, spawn data sources and object factories, and the client ignores it; `MessageId` is 0 when `OnServerAuthenticating`, `OnClientAuthenticating` or a callback on the authentication's cancellation token threw |
| `ObjectMismatchArgs` | `ObjectMismatchKind Kind`, `uint ObjectId`, `uint PrefabId`, `ulong SceneObjectId`, `NetworkScene Scene` |
| `InputRejectedArgs` | `ulong PeerId`, `uint ObjectId`, `byte BehaviourIndex` |
| `ServerRpcRejectedArgs` | `ulong PeerId`, `uint ObjectId`, `byte BehaviourIndex`, `uint MessageId` |

By default, Log Send Dropped and Log Receive Dropped log the first two events. `OnHandlerException` logs the exception, `OnInputRejected` and `OnServerRpcRejected` log a warning, and `OnObjectMismatch` logs an error, but only while no handler is subscribed.

`OnInputRejected` and `OnServerRpcRejected` let the server count or punish a client that sends input or RPCs for an object it does not own, for example with `Kick` after several rejections. An honest client can trigger them too: input or an RPC it sent just before an [owner change](../objects/ownership.md#setting-the-owner) reached it arrives after the server has moved the object to another owner. Both events run inside the server's message handler, so an exception thrown by a subscriber goes to `OnHandlerException`.

## Tick events

`TimeManager` has `OnPreTick`, `OnTick` and `OnPostTick`, all of type `Action`. [Ticks and timing](../concepts/tick.md#order-of-one-tick) shows where they fire within a tick.

## Scene events

`ServerManager.Scenes` has `OnLoaded(NetworkScene scene)`, `OnLoadFailed(NetworkScene scene, Exception exception)`, `OnUnloaded(NetworkScene scene)` and `OnPeerLoaded(ulong peerId, NetworkScene scene)`. `ClientManager.Scenes` has `OnLoadStarted(NetworkScene scene, uint sceneId)`, `OnLoaded(NetworkScene scene)` and `OnUnloaded(NetworkScene scene)`.

## Contact events

`NetworkCollision`, `NetworkTrigger`, `NetworkCollision2D` and `NetworkTrigger2D` have `OnEnter` and `OnExit`, which pass the other collider. Exceptions in their handlers are logged.

## NetworkBehaviour callbacks

| Callback | Side | Order |
|---|---|---|
| Registration of RPCs, state and input | First side the instance spawns on | Once per instance, before the start callback |
| `OnStartServer` | Server | After the spawn message is queued |
| `OnStartClient` | Client | After the initial state is applied |
| `OnOwnerChangedServer(previousOwnerId)` | Server | After the owner changed |
| `OnOwnerChangedClient(previousOwnerId)` | Observing clients | After the owner change arrived |
| `OnHostVisibility(visible)` | Host | When the host's client stops or starts observing; exceptions are logged |
| `OnReconciled(tick)` | Owner's client | After a correction |
| `OnStopClient` | Client | Before the object disappears; on a host, before `OnStopServer`. When the client stops, before `OnClientConnectionState` reports `Stopped` |
| `OnStopServer` | Server | Before the despawn message |

## Other callbacks

| Callback | Registered with | Runs |
|---|---|---|
| RPC methods | `[ServerRpc]`, `[ClientRpc]` | When the RPC arrives |
| State `OnChanged(previous, current)` | `[NetworkState(OnChanged = ...)]` | On clients, after a change of the field |
| Collection `OnChanged(operation, index or key, old, new)` | `[NetworkState(Index = ..., OnChanged = ...)]` | On clients, after each operation; once with `Reset` after a [recovery](../synchronization/collections.md#recovery) |
| `OnGatherInput`, `OnApplyInput` | `[NetworkInput]` fields | See [input](../prediction/input.md#apply) |
| `OnCaptureState`, `OnRestoreState` | `[NetworkReconcile]` fields | See [reconciliation](../prediction/reconciliation.md) |
| `ObserverRule.Observes` | Observer Rule field | On the server, when observers are recalculated |
| `OnServerAuthenticating`, `OnClientAuthenticating` and the authenticator's handlers | Authenticator field | See [authentication](../connections/authentication.md) |
| `ISceneLoader.Load`, `Unload` | `SceneRegistry.Register` | When a network scene is loaded or unloaded |
| Prefab factory `create`, `release` | `PrefabRegistry.SetFactory`, `PrefabRegistry.Register` | On clients, when an object of that prefab id spawns or despawns |

[Lifecycle](../concepts/lifecycle.md) shows the callbacks in order, and [errors and stop reasons](errors.md) lists the values these events carry.
