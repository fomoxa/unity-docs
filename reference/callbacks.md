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
| `OnHandlerException` | both managers | `HandlerExceptionArgs` | A message handler threw; the server closes that peer's connection, or the client stops |
| `OnObjectMismatch` | `ClientManager` | `ObjectMismatchArgs` | The client could not apply an object message and stops |

| Argument | Members |
|---|---|
| `SendDroppedArgs` | `ulong PeerId`, `uint MessageId`, `int PayloadLength`, `SendStatus Reason` |
| `ReceiveDroppedArgs` | `ulong PeerId`, `int FrameLength` |
| `HandlerExceptionArgs` | `ulong PeerId`, `uint MessageId`, `Exception Exception`; `MessageId` is 0 when `OnServerAuthenticating`, `OnClientAuthenticating` or a callback on the authentication's cancellation token threw |
| `ObjectMismatchArgs` | `ObjectMismatchKind Kind`, `uint ObjectId`, `uint PrefabId`, `ulong SceneObjectId`, `uint SceneId` |

By default, Log Send Dropped and Log Receive Dropped log the first two events. `OnHandlerException` logs the exception and `OnObjectMismatch` logs an error, but only while no handler is subscribed.

## Tick events

`TimeManager` has `OnPreTick`, `OnTick` and `OnPostTick`, all of type `Action`. [Ticks and timing](../concepts/tick.md#order-of-one-tick) shows where they fire within a tick.

## Scene events

`ServerManager.Scenes` has `OnLoaded(uint sceneId)` and `OnLoadFailed(uint sceneId, Exception exception)`.

## Contact events

`NetworkCollision`, `NetworkTrigger`, `NetworkCollision2D` and `NetworkTrigger2D` have `OnEnter` and `OnExit`, which pass the other collider. Exceptions in their handlers are logged.

## NetworkBehaviour callbacks

| Callback | Side | Order |
|---|---|---|
| `OnRegisterRpcs`, `OnRegisterState`, `OnRegisterInput` | First side the instance spawns on | Once per instance, before the start callback |
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
| RPC handlers | Attributes or `NetworkRpcs` | When the RPC arrives |
| State `onChanged(previous)` | `NetworkState.Use` | On clients, after each state change |
| Collection `onChanged(operation, index or key, old, new)` | `NetworkState.Use` | On clients, after each operation; once with `Reset` after a [recovery](../synchronization/collections.md#recovery) |
| `gather`, `apply` | `NetworkInput.Use` | See [input](../prediction/input.md#apply) |
| `capture`, `restore`, `matches` | `NetworkInput.Reconcile` | See [reconciliation](../prediction/reconciliation.md) |
| `ObserverRule.Observes` | Observer Rule field | On the server, when observers are recalculated |
| `OnServerAuthenticating`, `OnClientAuthenticating` and the authenticator's handlers | Authenticator field | See [authentication](../connections/authentication.md) |
| `ISceneLoader.Load`, `Unload` | `SceneRegistry.Register` | When a network scene is loaded or unloaded |
| Prefab factory `create`, `release` | `PrefabRegistry.Register` | On clients, when an object of that prefab id spawns or despawns |

Input from a peer that does not own the object is logged as a warning, and `ServerManager` does not expose an event for it.

[Lifecycle](../concepts/lifecycle.md) shows the callbacks in order, and [errors and stop reasons](errors.md) lists the values these events carry.
