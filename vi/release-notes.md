# Ghi chú phát hành

## 0.2.0 <a href="#020" id="020"></a>

Bản phát hành này gồm các phần sau, phát hành cùng nhau:

| Phần | Phiên bản | Cài đặt |
|---|---|---|
| `com.fomoxa.networking` | 0.2.0 | `https://github.com/fomoxa/com.fomoxa.networking.git#0.2.0` |
| `com.fomoxa.rpc` | 0.1.0, bản phát hành đầu; cần `com.fomoxa.networking` 0.2.0 | `https://github.com/fomoxa/com.fomoxa.rpc.git#0.1.0` |
| `com.fomoxa.networking.rapier` | 0.1.1; cần `com.fomoxa.networking` 0.2.0 | `https://github.com/fomoxa/networking-rapier.git?path=com.fomoxa.networking.rapier#0.1.1` |
| `Fomoxa.Backend.Templates` | 0.1.0, bản phát hành đầu | `dotnet new install Fomoxa.Backend.Templates::0.1.0` |
| `fomoxa-directory`, `fomoxa-gateway` | 0.2.0, bản phát hành đầu, dạng mã nguồn | [fomoxa/gateway](https://github.com/fomoxa/gateway) ở tag `0.2.0`; build bằng Cargo |

### Nâng cấp từ 0.1.0 <a href="#upgrading-from-010" id="upgrading-from-010"></a>

Server 0.2.0 không nhận client 0.1.0, và client 0.2.0 không vào được server 0.1.0. Package có thêm model hệ thống nên handshake thấy schema khác, và mỗi datagram UDP giờ mang mã phiên. Hãy cập nhật server và mọi bản build của client cùng lúc.

- Cập nhật `com.fomoxa.networking.rapier` lên 0.1.1 cùng với package. Backend Rapier 0.1.0 báo lỗi phiên bản khi chạy với package 0.2.0.
- Package giờ mang `BouncyCastle.Cryptography.dll` và `Fomoxa.Net.WebSockets.dll` trong `Runtime/Plugins`. Nếu project của bạn có bản riêng của một trong hai assembly này, hãy xoá bản đó.
- Console server biên dịch `Standalone~` của package, nên hãy build lại nó từ package 0.2.0.
- Client bị server đóng kèm thông báo sẽ không kết nối lại nữa. Server gửi thông báo khi gọi `Kick`, khi [chuyển server](connections/transfer.md), và khi một handler phía server ném exception; ở 0.1.0, exception trong handler làm rớt kết nối và client kết nối lại. Client dừng với `StopReason.ServerClosed`, hoặc `Transferred` sau khi chuyển server. [Tham chiếu ClientManager](reference/client-manager.md) liệt kê mọi lý do mà sau đó client không thử lại.
- Object không có peer nào quan sát không gửi cập nhật state và transform nữa. Peer bắt đầu quan sát một object như vậy vẫn nhận state hiện tại của nó.

### Kết nối <a href="#connections" id="connections"></a>

- [Xác thực](connections/authentication.md): peer đi qua trạng thái mới `Authenticating` trước `Started`. `IServerAuthenticator` và `IClientAuthenticator`, hoặc component `NetworkAuthenticator`, trao đổi message với client, nhận hoặc từ chối nó kèm lý do, và có thể kiểm bất đồng bộ với cancellation token.
- `ServerManager.Kick(peerId)` báo cho client lý do nó bị đóng, sau khi gửi hết phần đang xếp hàng trong thời hạn Close Timeout Seconds. Xem [server](connections/server.md#peers).
- [Chuyển server](connections/transfer.md): `ServerManager.Transfer` gửi client sang server khác kèm một vé. Client tự kết nối tới đó và phát `OnTransferring`. `TransferTickets` cấp và kiểm vé HMAC-SHA256 có hạn dùng và nonce dùng một lần.
- [UDP mã hóa](connections/transports/encrypted-udp.md), mặc định tắt: `EncryptedUdpNetworkTransport` mã hoá mọi datagram bằng khoá riêng của mỗi kết nối. Dịch vụ đăng nhập của bạn cấp vé kết nối bằng `ConnectTokens`, và client truyền vé cho `StartConnection(address, port, connection)`.
- [TLS phía client](connections/transports/tls.md), mặc định tắt: client native kết nối qua TLS trên TCP và bằng `wss://` trên WebSocket. Package kiểm chứng chỉ với bộ gốc của Mozilla mang theo trong package. Chứng chỉ bị từ chối làm client dừng với `StopReason.TlsRejected`.
- [WebSocket mã hóa](connections/transports/encrypted-websocket.md): datagram UDP mã hoá chở trên WebSocket, để client WebGL tới được cùng các pod qua gateway.
- Listener UDP mã hoá chạy được [sau gateway](connections/transports/encrypted-udp.md#behind-a-gateway). `ServerManager.ArrivedOverWebSocket(peerId)` cho biết peer vào bằng đường nào.

### Message và đồng bộ <a href="#messages-and-synchronization" id="messages-and-synchronization"></a>

- Message reliable lớn hơn một bundle được chia nhỏ rồi ghép lại, tối đa 1 MiB. Gửi message lớn hơn trả `SendResult.TooLargeForReassembly`. Xem [channel](messaging/channels.md#message-size).
- [Tập hợp](synchronization/collections.md): `NetworkList<T>`, `NetworkDictionary<TKey, TValue>` và `NetworkSet<T>` gửi các thao tác làm trên chúng. Client lỡ thao tác thì xin lại toàn bộ tập hợp.
- [State](synchronization/state.md#marking-changes) có thể chỉ gửi khi bạn đánh dấu thay đổi, bằng `state.Use(..., onlyWhenDirty: true)` và `SetStateDirty()`.
- [Observer](objects/observers.md): `ServerManager.Groups` giữ các nhóm peer cho observer rule, và rule nào chỉ đổi kết quả khi game đổi gì đó thì tắt được việc tính lại theo chu kỳ bằng `RebuildsPeriodically`.
- Transform chỉ được đọc khi nguồn báo có thay đổi: `IPhysicsMotion` cho backend physics, và `SyncTransform(sync, receiver)` cho entity của console server.

### Hiệu năng <a href="#performance" id="performance"></a>

Server làm ít việc hơn mỗi tick. Nó tra observer bằng hash set, chỉ duyệt object có input, và bỏ qua object không ai quan sát. Runtime Fomoxa.Net tra peer theo id bằng bảng băm.

### Fomoxa.Net <a href="#fomoxanet" id="fomoxanet"></a>

Package mang một bản build tạm của Fomoxa.Net 0.1.3 với một bản sửa: lệnh gửi TCP hoặc WebSocket không còn chặn trong Mono của Unity trên Windows khi bộ đệm gửi của socket đầy. [Cài đặt](getting-started/installation.md) giải thích các phần dùng để lách giới hạn của Mono; một phiên bản sau cho Unity chạy trên CoreCLR sẽ bỏ chúng.

### fRPC: `com.fomoxa.rpc` 0.1.0 <a href="#frpc-comfomoxarpc-010" id="frpc-comfomoxarpc-010"></a>

Package mới thêm service fRPC vào project Unity. Bạn khai service bằng một interface C#, và client của nó gọi backend qua TCP, hoặc qua WebSocket trong WebGL. Package cũng chứa phía pod của directory, `DirectoryPod`: nó đăng ký server game với directory, nhận phòng, báo tải, và báo cho game khi pod bị rút để game chuyển phòng đi. Xem [README](https://github.com/fomoxa/com.fomoxa.rpc) của package.

### Cụm server <a href="#cluster" id="cluster"></a>

Trang [cụm server](deploy/cluster.md) cho thấy các phần mới ghép với nhau thế nào. Backend của game, tạo từ template `fomoxa-backend`, đăng nhập người chơi và hỏi directory xin phòng. Directory xếp phòng lên pod và cấp vé kết nối, gateway cho các pod một địa chỉ UDP công khai và một endpoint WebSocket, và pod bị rút chuyển người chơi của nó sang pod khác.

Directory và gateway chỉ phát hành dạng mã nguồn. Chưa có binary build sẵn hay container image.

### Backend Rapier 0.1.1 <a href="#rapier-backend-011" id="rapier-backend-011"></a>

- Báo các body đã di chuyển trong mỗi bước qua `IPhysicsMotion`, để `NetworkTransform` chỉ đọc các body đó.
- Trên Linux, thư viện native cần glibc 2.34 trở lên.
