# Tham chiếu event và callback

Mọi event và callback đều được phát trên main thread của Unity, từ các entry của `NetworkManager` trong player loop hoặc từ chính các lời gọi của bạn vào package.

## Event kết nối <a href="#connection-events" id="connection-events"></a>

| Event | Trên | Tham số | Phát khi |
|---|---|---|---|
| `OnServerConnectionState` | `ServerManager` | `ServerConnectionStateArgs` | `ServerState` của server thay đổi |
| `OnRemoteConnectionState` | `ServerManager` | `ConnectionStateArgs` | Trạng thái kết nối của một client thay đổi |
| `OnClientConnectionState` | `ClientManager` | `ConnectionStateArgs` | Trạng thái của client thay đổi |
| `OnTransferring` | `ClientManager` | `TransferringArgs` | Server chuyển client sang server khác; phát trước khi object của client despawn và trước `Stopped` |

`ServerConnectionStateArgs` có một member duy nhất, `ServerState State`. `TransferringArgs` có `string Address` và `ushort Port`, server mà client chuyển tới. `ConnectionStateArgs` có các member sau:

| Member | Type | Mô tả |
|---|---|---|
| `PeerId` | `ulong` | Peer id của client trên server; 0 trên client |
| `State` | `ConnectionState` | `Stopped`, `Starting`, `Authenticating` hoặc `Started` |
| `Reason` | `StopReason` | Lý do dừng; `None` trong các trường hợp khác |
| `Failure` | `HandshakeFailure` | Lỗi handshake khi `Reason` là `HandshakeFailed` |
| `DiscardedMessages` | `int` | Số message trong queue bị bỏ khi kết nối dừng |
| `WillRetry` | `bool` | Trên client, có lần thử mới tiếp theo hay không |
| `CloseReason` | `SessionCloseReason` | Trên client dừng với `ServerClosed`, lý do server đã gửi; ngoài trường hợp đó là `Unspecified` |

## Event message <a href="#message-events" id="message-events"></a>

| Event | Trên | Tham số | Phát khi |
|---|---|---|---|
| `OnSendDropped` | cả hai manager | `SendDroppedArgs` | Một message trong queue không gửi được |
| `OnReceiveDropped` | cả hai manager | `ReceiveDroppedArgs` | Một bundle nhận được, hoặc một model trong đó, không đọc được |
| `OnHandlerException` | cả hai manager | `HandlerExceptionArgs` | Một message handler ném exception; server đóng kết nối của peer đó trừ khi một subscriber bỏ `Disconnect`, hoặc client dừng |
| `OnObjectMismatch` | `ClientManager` | `ObjectMismatchArgs` | Client không áp dụng được một object message và dừng |
| `OnInputRejected` | `ServerManager` | `InputRejectedArgs` | Server bỏ input từ peer không sở hữu object |
| `OnServerRpcRejected` | `ServerManager` | `ServerRpcRejectedArgs` | Server bỏ một server RPC có `RequireOwnership` từ peer không sở hữu object |

| Tham số | Member |
|---|---|
| `SendDroppedArgs` | `ulong PeerId`, `uint MessageId`, `int PayloadLength`, `SendStatus Reason` |
| `ReceiveDroppedArgs` | `ulong PeerId`, `int FrameLength` |
| `HandlerExceptionArgs` | `ulong PeerId`, `uint MessageId`, `Exception Exception`, `bool Disconnect`; `Disconnect` ban đầu là `true`, đặt thành `false` thì peer được giữ sau khi một message handler trên server ném exception; server bỏ qua nó với authenticator, spawn data source và object factory, còn client bỏ qua nó; `MessageId` là 0 khi `OnServerAuthenticating`, `OnClientAuthenticating` hoặc một callback trên cancellation token của lần xác thực ném exception |
| `ObjectMismatchArgs` | `ObjectMismatchKind Kind`, `uint ObjectId`, `uint PrefabId`, `ulong SceneObjectId`, `NetworkScene Scene` |
| `InputRejectedArgs` | `ulong PeerId`, `uint ObjectId`, `byte BehaviourIndex` |
| `ServerRpcRejectedArgs` | `ulong PeerId`, `uint ObjectId`, `byte BehaviourIndex`, `uint MessageId` |

Mặc định, Log Send Dropped và Log Receive Dropped log hai event đầu. `OnHandlerException` log exception, `OnInputRejected` và `OnServerRpcRejected` log một cảnh báo, còn `OnObjectMismatch` log một lỗi, nhưng chỉ khi không có handler nào subscribe.

Với `OnInputRejected` và `OnServerRpcRejected`, server đếm hay phạt được client gửi input hay RPC cho object mà nó không sở hữu, ví dụ `Kick` sau vài lần bị bỏ. Client trung thực cũng có thể gây ra hai event này: input hay RPC nó gửi ngay trước khi tin [đổi owner](../objects/ownership.md#setting-the-owner) tới nó sẽ đến server sau khi server đã giao object cho owner khác. Cả hai event chạy trong message handler của server, nên exception do người subscribe ném ra đi tới `OnHandlerException`.

## Tick event <a href="#tick-events" id="tick-events"></a>

`TimeManager` có `OnPreTick`, `OnTick` và `OnPostTick`, đều thuộc type `Action`. [Tick và thời gian](../concepts/tick.md#order-of-one-tick) cho thấy chúng được gọi ở đâu trong một tick.

## Scene event <a href="#scene-events" id="scene-events"></a>

`ServerManager.Scenes` có `OnLoaded(NetworkScene scene)`, `OnLoadFailed(NetworkScene scene, Exception exception)`, `OnUnloaded(NetworkScene scene)` và `OnPeerLoaded(ulong peerId, NetworkScene scene)`. `ClientManager.Scenes` có `OnLoadStarted(NetworkScene scene, uint sceneId)`, `OnLoadProgress(NetworkScene scene, float progress)`, `OnLoaded(NetworkScene scene)` và `OnUnloaded(NetworkScene scene)`. `OnLoadProgress` phát từ callback `progress` của loader trong lúc bản đó là lần load đang chạy, giá trị được kẹp vào khoảng 0 tới 1.

## Contact event <a href="#contact-events" id="contact-events"></a>

`NetworkCollision`, `NetworkTrigger`, `NetworkCollision2D` và `NetworkTrigger2D` có `OnEnter` và `OnExit`, truyền collider còn lại. Exception trong handler của chúng được log.

## Callback của NetworkBehaviour <a href="#networkbehaviour-callbacks" id="networkbehaviour-callbacks"></a>

| Callback | Phía | Thứ tự |
|---|---|---|
| Đăng ký RPC, state và input | Phía đầu tiên instance spawn | Một lần mỗi instance, trước callback start |
| `OnStartServer` | Server | Sau khi message spawn được đưa vào queue |
| `OnStartClient` | Client | Sau khi state ban đầu được áp dụng |
| `OnOwnerChangedServer(previousOwnerId)` | Server | Sau khi owner thay đổi |
| `OnOwnerChangedClient(previousOwnerId)` | Client đang observe | Sau khi thông báo đổi owner tới |
| `OnHostVisibility(visible)` | Host | Khi client của host thôi hoặc bắt đầu observe; exception được log |
| `OnReconciled(tick)` | Client của owner | Sau một lần sửa |
| `OnStopClient` | Client | Trước khi object biến mất; trên host, trước `OnStopServer`. Khi client dừng, trước khi `OnClientConnectionState` báo `Stopped` |
| `OnStopServer` | Server | Trước message despawn |

## Callback khác <a href="#other-callbacks" id="other-callbacks"></a>

| Callback | Đăng ký bằng | Chạy |
|---|---|---|
| Method RPC | `[ServerRpc]`, `[ClientRpc]` | Khi RPC tới |
| `OnChanged(previous, current)` của state | `[NetworkState(OnChanged = ...)]` | Trên client, sau một thay đổi của field |
| `OnChanged(operation, index hoặc key, old, new)` của collection | `[NetworkState(Index = ..., OnChanged = ...)]` | Trên client, sau mỗi thao tác; một lần với `Reset` sau khi [khôi phục](../synchronization/collections.md#recovery) |
| `OnGatherInput`, `OnApplyInput` | Field `[NetworkInput]` | Xem [input](../prediction/input.md#apply) |
| `OnCaptureState`, `OnRestoreState` | Field `[NetworkReconcile]` | Xem [reconciliation](../prediction/reconciliation.md) |
| `ObserverRule.Observes` | Field Observer Rule | Trên server, khi observer được tính lại |
| `OnServerAuthenticating`, `OnClientAuthenticating` và các handler của authenticator | Field Authenticator | Xem [xác thực](../connections/authentication.md) |
| `ISceneLoader.Load`, `Unload` | `SceneRegistry.Register` | Khi một network scene được load hoặc unload |
| `create`, `release` của prefab factory | `PrefabRegistry.SetFactory`, `PrefabRegistry.Register` | Trên client, khi một object của prefab id đó spawn hoặc despawn |

[Vòng đời](../concepts/lifecycle.md) cho thấy thứ tự các callback, và [lỗi và lý do dừng](errors.md) liệt kê các giá trị mà các event này mang.
