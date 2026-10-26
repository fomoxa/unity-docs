# Tham chiếu lỗi và lý do dừng

## StopReason <a href="#stopreason" id="stopreason"></a>

`Fomoxa.Networking.Sessions.StopReason` xuất hiện trong `ConnectionStateArgs.Reason` khi một kết nối dừng.

| Giá trị | Ý nghĩa | Client thử lại |
|---|---|---|
| `None` | Kết nối chưa dừng | |
| `LocalStop` | Phía này đã gọi `StopConnection`, `Disconnect` hoặc `Kick` | Không |
| `PeerClosed` | Phía bên kia đã đóng kết nối, hoặc client đã gửi message rời đi | Có |
| `TransportError` | Transport thất bại: kết nối bị từ chối, không phân giải được host, lỗi socket | Có |
| `Timeout` | Heartbeat probe không được trả lời kịp | Có |
| `HandshakeFailed` | Handshake Fomoxa thất bại; xem `Failure` | Chỉ với `Timeout` |
| `HandlerException` | Một message handler ở phía này ném exception. Khi handler trên server ném exception với message của một client, peer trên server dừng với lý do này còn client dừng với `ServerClosed` | Không |
| `PrefabMismatch` | Client không spawn được một object: prefab hoặc scene object không biết hoặc khác, hoặc một network scene không load được | Không |
| `ObjectMismatch` | Client nhận một object message mà nó không áp dụng được | Không |
| `PhysicsBackendMismatch` | Client và server dùng physics backend khác nhau | Không |
| `InvalidFragment` | Phía bên kia gửi các mảnh của một message reliable lớn mà không ghép được với nhau | Không |
| `ServerClosed` | Server chủ động đóng kết nối và gửi kèm lý do, nằm trong `CloseReason` | Không |
| `UnauthenticatedMessage` | Trong lúc kết nối đang `Authenticating`, phía kia gửi một message mà [bước xác thực](../connections/authentication.md#messages-outside-the-authentication) không cho phép | Không |
| `AuthenticationFailed` | Trên server: authenticator đã từ chối peer. Client dừng với `ServerClosed` | |
| `AuthenticationTimeout` | Trên server: peer không được chấp nhận trong Authentication Timeout Seconds. Client dừng với `ServerClosed` | |
| `Transferred` | Server chuyển client sang server khác bằng `ServerManager.Transfer`; cả peer lẫn client dừng với lý do này. Xem [chuyển server](../connections/transfer.md) | Có, ngay lập tức và tới server mới, trừ khi vé kết nối của lần chuyển không hợp với transport của client |

## SessionCloseReason

`Fomoxa.Networking.Sessions.SessionCloseReason` xuất hiện trong `ConnectionStateArgs.CloseReason` khi client dừng với `ServerClosed`. Server gửi nó ngay trước khi đóng kết nối.

| Giá trị | Ý nghĩa |
|---|---|
| `Unspecified` (0) | Không có lý do. Package không bao giờ tự gửi giá trị này |
| `HandlerException` (1) | Một message handler trên server ném exception khi xử lý message của client này |
| `Kicked` (2) | Server đã gọi `ServerManager.Kick` |
| `AuthenticationFailed` (3) | Authenticator của server đã từ chối client |
| `AuthenticationTimeout` (4) | Client không được chấp nhận trong Authentication Timeout Seconds của server |
| `Transferred` (5) | Server chuyển client sang server khác. Server gửi nó sau lệnh chuyển, và client của package dừng với `Transferred` khi lệnh chuyển tới, nên không thấy giá trị này |

Server bản mới hơn có thể gửi một giá trị không có trong danh sách này. Client giữ nguyên giá trị nhận được, và vẫn không thử lại.

## HandshakeFailure <a href="#handshakefailure" id="handshakefailure"></a>

`Fomoxa.Net.HandshakeFailure` xuất hiện trong `ConnectionStateArgs.Failure`.

| Giá trị | Ý nghĩa |
|---|---|
| `VersionMismatch` | Hai bên dùng phiên bản giao thức Fomoxa khác nhau |
| `SchemaConflict` | Hai bên được build từ các model khác nhau |
| `Corrupt` | Dữ liệu handshake không đọc được |
| `Timeout` | Handshake không xong trong Handshake Timeout Seconds |

## ObjectMismatchKind <a href="#objectmismatchkind" id="objectmismatchkind"></a>

`Fomoxa.Networking.Objects.ObjectMismatchKind` xuất hiện trong `ObjectMismatchArgs.Kind`. Bốn loại đầu và `UnknownScene` dừng client với `PrefabMismatch`, các loại còn lại với `ObjectMismatch`.

| Giá trị | Ý nghĩa |
|---|---|
| `UnknownPrefab` | Không có prefab đã đăng ký nào mang prefab id của message spawn |
| `IncompatiblePrefab` | Danh sách `NetworkBehaviour` của prefab khác với của server |
| `UnknownSceneObject` | Không có scene object nào mang scene object id của message spawn |
| `IncompatibleSceneObject` | Danh sách `NetworkBehaviour` của scene object khác với của server |
| `UnknownScene` | Một network scene không load được |
| `DuplicateObject` | Message spawn cho một object id mà client đã có |
| `UnknownObject` | Message cho một object id mà client không có, trong trường hợp bắt buộc phải có |
| `InvalidSpawn` | Message spawn mà client không áp dụng được, như state không decode được hoặc scene client chưa load |
| `InvalidMessage` | Object message hoặc scene message không decode được |

## SendResult <a href="#sendresult" id="sendresult"></a>

`Fomoxa.Networking.Sessions.SendResult` được các method gửi trả về.

| Giá trị | Ý nghĩa |
|---|---|
| `Queued` | Message đã nằm trong send queue |
| `Full` | Queue đang giữ Message Capacity message |
| `BytesFull` | Queue đang giữ quá nhiều byte cho message này |
| `TooLargeForQueue` | Message lớn hơn Byte Capacity |
| `TooLargeForReassembly` | Message `ReliableOrdered` phải chia cho transport mà lớn hơn 1 MiB |
| `TooLarge` | Message lớn hơn mức giao thức cho phép |
| `NotConnected` | Không có kết nối, hoặc không có peer như vậy. Từ một context xác thực: lần xác thực đó đã kết thúc |
| `NotObserver` | Target RPC tới một peer không observe object |

## SendStatus <a href="#sendstatus" id="sendstatus"></a>

`Fomoxa.Net.SendStatus` xuất hiện trong `SendDroppedArgs.Reason`, trong đó `TooLarge` nghĩa là transport không gửi được message và message đã bị bỏ.

## Exception <a href="#exceptions" id="exceptions"></a>

| Exception | Ném bởi | Nguyên nhân |
|---|---|---|
| `InvalidOperationException` | `NetworkManager.Awake` | Phần đăng ký sinh ra chưa chạy |
| `InvalidOperationException` | `StartConnection` | Đang chạy rồi |
| `InvalidOperationException` | `ServerManager.Authenticator`, `ClientManager.Authenticator` | Đặt khi phía đó đang chạy |
| `InvalidOperationException` | `Send`, `Accept`, `Reject` của một context xác thực | Lần xác thực đã được chấp nhận |
| `InvalidOperationException` | `Spawn`, các method về scene | Server chưa khởi động |
| `InvalidOperationException` | `ServerManager.Transfer` | Peer là client chính của host |
| `InvalidOperationException` | Constructor của `TransferTickets` | Registry không có codec của `TransferTicket` |
| `InvalidOperationException` | `ClientManager.StartConnection(address, port)` | Transport cần vé kết nối, như [UDP mã hóa](../connections/transports/encrypted-udp.md) |
| `InvalidOperationException` | `ServerManager.StartConnection` với UDP mã hóa | Transport không có `ConnectTokens` |
| `InvalidOperationException` | Constructor của `ConnectTokens`, của `EncryptedUdpTransportFactory` | Registry không có codec của các model vé kết nối |
| `InvalidOperationException` | Các method gửi RPC | Object chưa spawn ở phía gửi, hoặc RPC không tham số chưa có model được sinh |
| `InvalidOperationException` | Các method thay đổi collection | Gọi trên client với object đã spawn |
| `ArgumentException` | `Spawn` | Asset prefab, đã spawn, prefab id chưa đăng ký, scene object không hợp lệ, owner chưa khởi động |
| `ArgumentException` | `PrefabRegistry.Register`, `SceneRegistry.Register` | Id 0, id đã đăng ký cho thứ khác, hierarchy prefab không hợp lệ |
| `HandlerRegistrationException` | Các hook đăng ký, `MessageDispatcher.Register` | Đăng ký state, collection, input hoặc RPC không hợp lệ; id không có trong schema; handler bị trùng |
| `ArgumentNullException` | Các method thêm hoặc gán phần tử collection | Phần tử, value hoặc key là `null` |
| `ArgumentNullException` | `ServerManager.Transfer`, `TransferTickets` | Địa chỉ, registry, khoá hoặc target là `null` |
| `ArgumentException` | Constructor của `TransferTickets` | Khoá rỗng |
| `ArgumentOutOfRangeException` | `TransferTickets.Lifetime` | Bằng 0 hoặc nhỏ hơn |
| `ArgumentException` | `ClientManager.StartConnection(address, port, connection)` | Transport không nhận vé kết nối, hoặc các byte không phải là vé |
| `ArgumentNullException` | `ConnectTokens` | Registry, khoá hoặc target là `null` |
| `ArgumentException` | Constructor của `ConnectTokens` | Khoá không đúng 32 byte |
| `ArgumentOutOfRangeException` | `ConnectTokens.Issue`, `ConnectTokens.Lifetime` | Mã phiên 0; thời hạn bằng 0 hoặc nhỏ hơn |
| `PlatformNotSupportedException` | Transport, `ServerManager.StartConnection` | UDP, UDP mã hóa hoặc TCP trong trình duyệt; server trong trình duyệt |
| `NotSupportedException` | Client WebSocket trên desktop | Một URL `wss://` |
| `MessageDecodeException` | Adapter | Payload không decode được |

## Log message lúc chạy <a href="#run-time-log-messages" id="run-time-log-messages"></a>

| Message | Ý nghĩa |
|---|---|
| `Fomoxa dropped message 0x... (N bytes) to peer N: <reason>` | Một message trong queue không gửi được |
| `Fomoxa dropped N received bytes from peer N: a message bundle, or a model in it, could not be read` | Một bundle nhận được không đọc được |
| `Fomoxa dropped server RPC 0x... to object N from peer N, which does not own the object` | Server RPC có `RequireOwnership` được gọi từ peer không phải owner |
| `Fomoxa dropped input to object N from peer N, which does not own the object` | Input từ peer không phải owner |
| `Fomoxa stopped the client: object mismatch <kind>, object N, prefab 0x..., scene object 0x...` | `OnObjectMismatch` không có subscriber |
| `Fomoxa: object N (prefab 0x...) was destroyed on the client without a despawn from the server` | Một GameObject đã spawn bị hủy trên client |
| `Fomoxa: <name> received Animator state with layout 0x..., but its Animator has layout 0x...` | Animator controller khác nhau giữa server và client |

Message của Editor bắt đầu bằng `[Fomoxa]` và được nói tới trong [xử lý sự cố](../getting-started/troubleshooting.md#code-generation-fails) và [tích hợp Editor](../advanced/editor-integration.md).

[Xử lý sự cố](../getting-started/troubleshooting.md) đi từ triệu chứng tới các giá trị này, và [event và callback](callbacks.md) liệt kê các event mang chúng.
