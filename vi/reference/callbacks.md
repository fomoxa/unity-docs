# Tham chiếu event và callback

Mọi event và callback đều được phát trên main thread của Unity, từ các entry của `NetworkManager` trong player loop hoặc từ chính các lời gọi của bạn vào package.

## Event kết nối <a href="#connection-events" id="connection-events"></a>

| Event | Trên | Tham số | Phát khi |
|---|---|---|---|
| `OnServerConnectionState` | `ServerManager` | `ServerConnectionStateArgs` | `ServerState` của server thay đổi |
| `OnRemoteConnectionState` | `ServerManager` | `ConnectionStateArgs` | Trạng thái kết nối của một client thay đổi |
| `OnClientConnectionState` | `ClientManager` | `ConnectionStateArgs` | Trạng thái của client thay đổi |

`ServerConnectionStateArgs` có một member duy nhất, `ServerState State`. `ConnectionStateArgs` có các member sau:

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
| `OnHandlerException` | cả hai manager | `HandlerExceptionArgs` | Một message handler ném exception; server đóng kết nối của peer đó, hoặc client dừng |
| `OnObjectMismatch` | `ClientManager` | `ObjectMismatchArgs` | Client không áp dụng được một object message và dừng |

| Tham số | Member |
|---|---|
| `SendDroppedArgs` | `ulong PeerId`, `uint MessageId`, `int PayloadLength`, `SendStatus Reason` |
| `ReceiveDroppedArgs` | `ulong PeerId`, `int FrameLength` |
| `HandlerExceptionArgs` | `ulong PeerId`, `uint MessageId`, `Exception Exception`; `MessageId` là 0 khi `OnServerAuthenticating`, `OnClientAuthenticating` hoặc một callback trên cancellation token của lần xác thực ném exception |
| `ObjectMismatchArgs` | `ObjectMismatchKind Kind`, `uint ObjectId`, `uint PrefabId`, `ulong SceneObjectId`, `uint SceneId` |

Mặc định, Log Send Dropped và Log Receive Dropped log hai event đầu. `OnHandlerException` log exception và `OnObjectMismatch` log một lỗi, nhưng chỉ khi không có handler nào subscribe.

## Tick event <a href="#tick-events" id="tick-events"></a>

`TimeManager` có `OnPreTick`, `OnTick` và `OnPostTick`, đều thuộc type `Action`. [Tick và thời gian](../concepts/tick.md#order-of-one-tick) cho thấy chúng được gọi ở đâu trong một tick.

## Scene event <a href="#scene-events" id="scene-events"></a>

`ServerManager.Scenes` có `OnLoaded(uint sceneId)` và `OnLoadFailed(uint sceneId, Exception exception)`.

## Contact event <a href="#contact-events" id="contact-events"></a>

`NetworkCollision`, `NetworkTrigger`, `NetworkCollision2D` và `NetworkTrigger2D` có `OnEnter` và `OnExit`, truyền collider còn lại. Exception trong handler của chúng được log.

## Callback của NetworkBehaviour <a href="#networkbehaviour-callbacks" id="networkbehaviour-callbacks"></a>

| Callback | Phía | Thứ tự |
|---|---|---|
| `OnRegisterRpcs`, `OnRegisterState`, `OnRegisterInput` | Phía đầu tiên instance spawn | Một lần mỗi instance, trước callback start |
| `OnStartServer` | Server | Sau khi message spawn được đưa vào queue |
| `OnStartClient` | Client | Sau khi state ban đầu được áp dụng |
| `OnOwnerChangedServer(previousOwnerId)` | Server | Sau khi owner thay đổi |
| `OnOwnerChangedClient(previousOwnerId)` | Client đang observe | Sau khi thông báo đổi owner tới |
| `OnHostVisibility(visible)` | Host | Khi client của host thôi hoặc bắt đầu observe; exception được log |
| `OnReconciled(tick)` | Client của owner | Sau một lần sửa |
| `OnStopClient` | Client | Trước khi object biến mất; trên host, trước `OnStopServer` |
| `OnStopServer` | Server | Trước message despawn |

## Callback khác <a href="#other-callbacks" id="other-callbacks"></a>

| Callback | Đăng ký bằng | Chạy |
|---|---|---|
| RPC handler | Attribute hoặc `NetworkRpcs` | Khi RPC tới |
| `onChanged(previous)` của state | `NetworkState.Use` | Trên client, sau mỗi thay đổi state |
| `gather`, `apply` | `NetworkInput.Use` | Xem [input](../prediction/input.md#apply) |
| `capture`, `restore`, `matches` | `NetworkInput.Reconcile` | Xem [reconciliation](../prediction/reconciliation.md) |
| `ObserverRule.Observes` | Field Observer Rule | Trên server, khi observer được tính lại |
| `OnServerAuthenticating`, `OnClientAuthenticating` và các handler của authenticator | Field Authenticator | Xem [xác thực](../connections/authentication.md) |
| `ISceneLoader.Load`, `Unload` | `SceneRegistry.Register` | Khi một network scene được load hoặc unload |
| `create`, `release` của prefab factory | `PrefabRegistry.Register` | Trên client, khi một object của prefab id đó spawn hoặc despawn |

Input từ peer không sở hữu object được log dưới dạng cảnh báo, và `ServerManager` không cung cấp event cho trường hợp này.

[Vòng đời](../concepts/lifecycle.md) cho thấy thứ tự các callback, và [lỗi và lý do dừng](errors.md) liệt kê các giá trị mà các event này mang.
