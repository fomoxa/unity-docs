# Tham chiếu lỗi và lý do dừng

## StopReason <a href="#stopreason" id="stopreason"></a>

`Fomoxa.Networking.Sessions.StopReason` xuất hiện trong `ConnectionStateArgs.Reason` khi một kết nối dừng.

| Giá trị | Ý nghĩa | Client thử lại |
|---|---|---|
| `None` | Kết nối chưa dừng | |
| `LocalStop` | Phía này đã gọi `StopConnection` hoặc `Disconnect` | Không |
| `PeerClosed` | Phía bên kia đã đóng kết nối, hoặc client đã gửi message rời đi | Có |
| `TransportError` | Transport thất bại: kết nối bị từ chối, không phân giải được host, lỗi socket | Có |
| `Timeout` | Heartbeat probe không được trả lời kịp | Có |
| `HandshakeFailed` | Handshake Fomoxa thất bại; xem `Failure` | Chỉ với `Timeout` |
| `HandlerException` | Một message handler ném exception | Không |
| `PrefabMismatch` | Client không spawn được một object: prefab hoặc scene object không biết hoặc khác, hoặc một network scene không load được | Không |
| `ObjectMismatch` | Client nhận một object message mà nó không áp dụng được | Không |
| `PhysicsBackendMismatch` | Client và server dùng physics backend khác nhau | Không |
| `InvalidFragment` | Phía bên kia gửi các mảnh của một message reliable lớn mà không ghép được với nhau | Không |

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
| `NotConnected` | Không có kết nối, hoặc không có peer như vậy |
| `NotObserver` | Target RPC tới một peer không observe object |

## SendStatus <a href="#sendstatus" id="sendstatus"></a>

`Fomoxa.Net.SendStatus` xuất hiện trong `SendDroppedArgs.Reason`, trong đó `TooLarge` nghĩa là transport không gửi được message và message đã bị bỏ.

## Exception <a href="#exceptions" id="exceptions"></a>

| Exception | Ném bởi | Nguyên nhân |
|---|---|---|
| `InvalidOperationException` | `NetworkManager.Awake` | Phần đăng ký sinh ra chưa chạy |
| `InvalidOperationException` | `StartConnection` | Đang chạy rồi |
| `InvalidOperationException` | `Spawn`, các method về scene | Server chưa khởi động |
| `InvalidOperationException` | Các method gửi RPC | Object chưa spawn ở phía gửi, hoặc RPC không tham số chưa có model được sinh |
| `ArgumentException` | `Spawn` | Asset prefab, đã spawn, prefab id chưa đăng ký, scene object không hợp lệ, owner chưa khởi động |
| `ArgumentException` | `PrefabRegistry.Register`, `SceneRegistry.Register` | Id 0, id đã đăng ký cho thứ khác, hierarchy prefab không hợp lệ |
| `HandlerRegistrationException` | Các hook đăng ký, `MessageDispatcher.Register` | Đăng ký state, input hoặc RPC không hợp lệ; id không có trong schema; handler bị trùng |
| `PlatformNotSupportedException` | Transport, `ServerManager.StartConnection` | UDP hoặc TCP trong trình duyệt; server trong trình duyệt |
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
