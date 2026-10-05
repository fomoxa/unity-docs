# Giới thiệu

Fomoxa for Unity thêm networking nhiều người chơi vào một project Unity. Một tiến trình chạy làm server và sở hữu game state. Các client kết nối tới nó, gửi yêu cầu và input của mình, rồi hiển thị những gì server gửi về. Host là tiến trình chạy server và một client cùng nhau.

## Game dùng package như thế nào <a href="#how-a-game-uses-the-package" id="how-a-game-uses-the-package"></a>

Một game thông thường đi qua bốn bước.

1. Khai báo các network message dưới dạng class C# gọi là model, đánh dấu bằng `[Network]` và `[Codec]`. Package chạy trình biên dịch `fomoxac` trên các class này và sinh codec cho từng model.
2. Đặt một `NetworkManager` vào scene và chọn transport cho nó, ví dụ `UdpNetworkTransport`.
3. Thêm `NetworkObject` vào mọi prefab tồn tại trên mạng, và viết các script `NetworkBehaviour` cho phần logic networking của những prefab đó.
4. Khởi động server, client hoặc host từ code, và server spawn object cho các client.

Khi object đã được spawn, một `NetworkBehaviour` có thể gọi RPC và đăng ký một state model để server giữ đồng bộ. Thêm `NetworkTransform` để replicate vị trí của object, và đăng ký input model để client tự dự đoán nhân vật của mình.

## Các type chính <a href="#main-types" id="main-types"></a>

| Type | Vai trò |
|---|---|
| [`NetworkManager`](../core/network-manager.md) | Component chạy networking cho một scene: cấu hình, vòng lặp tick, server và client |
| [`ServerManager`](../core/server.md) | Khởi động và dừng server, spawn và despawn object, đổi owner |
| [`ClientManager`](../core/client.md) | Kết nối tới server, kết nối lại, cung cấp các object đã spawn trên client |
| [`NetworkObject`](../core/network-object.md) | Đánh dấu một GameObject là network object, có object id và owner |
| [`NetworkBehaviour`](../core/network-behaviour.md) | Base class cho script networking: callback vòng đời, RPC, state và input |
| [`NetworkTransform`](../synchronization/transform.md) | Replicate vị trí, góc xoay và tỉ lệ từ server |
| [`NetworkAnimator`](../synchronization/animator.md) | Replicate parameter, trigger và trạng thái layer của Animator |
| [`NetworkTransport`](../transports/overview.md) | Base class của các component transport: UDP, TCP, WebSocket, nhiều transport |

## Tình trạng tính năng <a href="#feature-status" id="feature-status"></a>

| Tính năng | Tình trạng |
|---|---|
| Transport UDP, TCP và WebSocket, nhiều transport trên một server | Có |
| Host mode qua kết nối trong cùng tiến trình | Có |
| Spawn, scene object, ownership, observer | Có |
| RPC có và không có model, khai báo bằng attribute hoặc đăng ký thủ công | Có |
| State với delta encoding, `NetworkTransform`, `NetworkAnimator` | Có |
| Network scene | Có |
| Client-side prediction, reconciliation và replay | Có |
| Rollback physics của Unity (`Rigidbody` và `Rigidbody2D`) | Có, gần đúng (xem [rollback](../prediction/rollback.md)) |
| Client WebGL | Có |
| Physics backend Rapier | Chưa hiện thực; giá trị `PhysicsBackend.Rapier` có tồn tại nhưng không có backend |
| Server console (tiến trình server .NET không có Unity) | Chưa đóng gói; xem [server console](../server/server-console.md) |
| Binary `fomoxac` cho macOS | Không đi kèm; sinh code thất bại trong Editor trên macOS |

## Những gì không có <a href="#what-is-not-included" id="what-is-not-included"></a>

Package không có lockstep simulation và không thể ghi lại hay phát lại cả một trận đấu. Package cũng không có bộ sinh số ngẫu nhiên tất định, không có state hashing và không có physics tất định giữa các nền tảng. Tài liệu không mô tả những tính năng này.

Matchmaking, relay server, lobby và NAT traversal cũng nằm ngoài package, cũng như mã hóa và xác thực kết nối. Client WebSocket trong trình duyệt vẫn có thể tới server qua TLS thông qua một proxy, như mô tả trong [WebSocket](../transports/websocket.md).

Tiếp theo là trang [cài đặt](installation.md).
