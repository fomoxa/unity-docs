# Ghi chú phát hành

## 0.3.1 <a href="#031" id="031"></a>

Bản phát hành này gồm các phần sau, phát hành cùng nhau:

| Phần | Phiên bản | Cài đặt |
|---|---|---|
| `com.fomoxa.networking` | 0.3.1 | `https://github.com/fomoxa/com.fomoxa.networking.git#0.3.1` |
| `com.fomoxa.rpc` | 0.1.2; cần `com.fomoxa.networking` 0.3.1 | `https://github.com/fomoxa/com.fomoxa.rpc.git#0.1.2` |
| `com.fomoxa.networking.rapier` | 0.2.1; cần `com.fomoxa.networking` 0.3.1 | `https://github.com/fomoxa/networking-rapier.git?path=com.fomoxa.networking.rapier#0.2.1` |

`Fomoxa.Backend.Templates` 0.1.0, directory và gateway ở tag `0.2.0` không có phiên bản mới.

### Nâng cấp từ 0.3.0 <a href="#upgrading-from-030" id="upgrading-from-030"></a>

Hãy cập nhật server trước client, hoặc cùng lúc. Qua UDP, UDP mã hóa và WebSocket, client 0.3.1 gửi handshake của schema có từ 63 message trở lên thành nhiều gói. Server 0.3.0 bỏ các gói đó, và client dừng với `HandshakeFailed` và `Timeout`. Số message này tính cả message của package. Client 0.3.0 vẫn vào được server 0.3.1, còn kết nối TCP và TLS không đổi.

- Cập nhật `com.fomoxa.rpc` lên 0.1.2 và `com.fomoxa.networking.rapier` lên 0.2.1 cùng với package. Với package 0.3.1, `com.fomoxa.rpc` 0.1.1 báo lỗi khi sinh code, còn Rapier 0.2.0 ném lỗi phiên bản khi tạo world.
- Console server biên dịch `Standalone~` và tham chiếu `Runtime/Plugins/Fomoxa.Net.dll` của package, nên hãy build lại nó từ package 0.3.1.

API, schema của handshake và định dạng scene file giống 0.3.0, nên code đã sinh và scene file đã xuất không phải đổi.

### Handshake lớn <a href="#large-handshakes" id="large-handshakes"></a>

Ở 0.3.0, handshake đi trong một gói, và gói đó dài thêm 14 byte cho mỗi message của schema. Qua UDP thường nó vượt 1200 byte từ 84 message, sớm hơn khi có mã hóa, và mạng bỏ mảnh IP thì bỏ luôn gói đó, nên client không kết nối được qua mạng ấy. Package giờ mang Fomoxa.Net 0.1.4: handshake dài hơn 900 byte được chia thành nhiều phần, mỗi phần một gói. Khi có mã hóa, mỗi datagram không quá 1200 byte với vé dài tới 249 byte. Như ở 0.2.0, bản build Fomoxa.Net của package giữ bản sửa cho lệnh gửi trong Mono của Unity (xem [Fomoxa.Net](#fomoxanet) của 0.2.0).

## 0.3.0 <a href="#030" id="030"></a>

Bản phát hành này gồm các phần sau, phát hành cùng nhau:

| Phần | Phiên bản | Cài đặt |
|---|---|---|
| `com.fomoxa.networking` | 0.3.0 | `https://github.com/fomoxa/com.fomoxa.networking.git#0.3.0` |
| `com.fomoxa.rpc` | 0.1.1; cần `com.fomoxa.networking` 0.3.0 | `https://github.com/fomoxa/com.fomoxa.rpc.git#0.1.1` |
| `com.fomoxa.networking.rapier` | 0.2.0; cần `com.fomoxa.networking` 0.3.0 | `https://github.com/fomoxa/networking-rapier.git?path=com.fomoxa.networking.rapier#0.2.0` |

`Fomoxa.Backend.Templates` 0.1.0, directory và gateway ở tag `0.2.0` không có phiên bản mới.

### Nâng cấp từ 0.2.0 <a href="#upgrading-from-020" id="upgrading-from-020"></a>

Server 0.3.0 không nhận client 0.2.0, và client 0.2.0 không vào được server 0.3.0. Các model scene file của package có thêm trường nên handshake thấy schema khác. Hãy cập nhật server và mọi bản build của client cùng lúc.

- Cập nhật `com.fomoxa.rpc` lên 0.1.1 và `com.fomoxa.networking.rapier` lên 0.2.0 cùng với package. Với package 0.3.0, `com.fomoxa.rpc` 0.1.0 báo lỗi khi sinh code, còn Rapier 0.1.1 ném lỗi phiên bản khi tạo world.
- Package từ chối scene file do 0.2.0 ghi. Hãy xuất lại bằng Tools > Fomoxa > Export Network Scene Files rồi chép file mới sang console server. Trước khi build player, package tự ghi lại những file nó không đọc được.
- Dữ liệu game tự mã hoá bằng model scene file của package có thể giải mã lỗi với `MessageDecodeException`, ví dụ một catalogue màn chơi chứa mảng giá trị `SceneFileCollider2D`. Hãy mã hoá lại dữ liệu đó.
- Console server biên dịch `Standalone~` của package, nên hãy build lại nó từ package 0.3.0.
- Với `RigidbodyPhysics`, `Raycast` không có bộ lọc và `Overlap` theo bán kính giờ dùng `QueryFilter.All`. Chúng xét mọi layer, kể cả Ignore Raycast, trúng cả trigger, và truy vấn bắt đầu bên trong một collider trúng collider đó ở khoảng cách 0. Truyền một [`QueryFilter`](physics/queries.md#filters) để bỏ bớt layer hoặc trigger.
- Ở 0.2.0, client từ xa chỉ đặt body trên GameObject của network object làm proxy. Body trên GameObject con giờ theo quy tắc của [nhiều body](physics/overview.md#several-bodies): body con mà GameObject của nó có `NetworkTransform` cũng là proxy, còn body con không có thì client tự mô phỏng. `Rigidbody2D` tắt Simulated không phải là body.

### Physics <a href="#physics" id="physics"></a>

- [Truy vấn physics](physics/queries.md): mọi truy vấn nhận một `QueryFilter` gồm layer mask, một body cần bỏ qua và việc có tính trigger hay không. World có thêm `ShapeCast` và `Overlap` theo hình, còn `NetworkPhysics.WorldsOf` trả các world của một scene.
- [PhysicsBody](physics/physics-body.md) có thêm `AddTorque`, `AddTorqueImpulse`, `AddForceAtPoint` và `AddImpulseAtPoint`. [Va chạm liên tục](physics/physics-body.md#continuous-collision) bật qua `BodyMotion.ContinuousCollision`, được `BodyDescriptions` lấy từ trường Collision Detection.
- `PhysicsBody.GetContactPoints` liệt kê chỗ hai body chạm nhau sau bước gần nhất, còn [`NetworkCollision.GetContactPoints`](physics/contacts.md#contact-points) liệt kê các điểm của một sự kiện va chạm. Qua `PhysicsBody`, `RigidbodyPhysics` không trả điểm nào cho body 3D.
- `NetworkObject.Bodies` và `Bodies2D` liệt kê các [body](physics/overview.md#several-bodies) của một ragdoll hay một chiếc xe, và `NetworkTransform` trên GameObject con có body đồng bộ body đó.

### Console server và scene file <a href="#console-servers-and-scene-files" id="console-servers-and-scene-files"></a>

- Entity khai báo body con bằng `GetChildBodies` và `GetChildBodies2D`, và gửi pose của chúng bằng `SyncTransform(sync, ChildBody.Of(index), receiver)`. Xem [nhiều body](console-server/physics.md#several-bodies).
- Scene file mang body con của scene object, body mà mỗi behaviour nằm trên, và effector 2D của collider tĩnh. Overload `BehaviourSite` của `StandaloneBehaviours.Register` cho behaviour biết GameObject của nó mang body nào. Xem [scene file](advanced/editor-integration.md#scene-files).

### Backend Rapier 0.2.0 <a href="#rapier-backend-020" id="rapier-backend-020"></a>

- Ngoài Windows x64 và Linux x64, giờ có thư viện native cho Windows arm64, Linux arm64, macOS, Android `arm64-v8a` và `armeabi-v7a`, iOS và Web. Một workflow build so hash của chúng với danh sách tham chiếu, và player Windows dưới Mono và IL2CPP, player Web và player Android cho cùng hash. Xem [nền tảng](rapier/setup.md#platforms) và [nền tảng đã kiểm](rapier/determinism.md#checked-platforms).
- Truy vấn, lực, mô-men, va chạm liên tục, điểm tiếp xúc và nhiều body ở trên chạy cùng API như với `RigidbodyPhysics`, và Rapier trả cả điểm tiếp xúc của body 3D.
- [Joint](rapier/joints.md) từ component joint của Unity và từ code.
- `MoveCharacter`, một [character controller](rapier/character-controller.md) cho body kinematic.
- Năm [effector](rapier/effectors.md) 2D của Unity.

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
