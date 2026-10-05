# Nhiều transport

`MultiNetworkTransport` cho một server lắng nghe trên nhiều transport cùng lúc, mỗi transport trên một port riêng. Cách dùng điển hình là một server duy nhất nhận client desktop qua UDP và client trình duyệt qua WebSocket.

## Cách dùng cơ bản <a href="#basic-usage" id="basic-usage"></a>

1. Thêm các transport cần dùng vào GameObject của `NetworkManager`, ví dụ `UdpNetworkTransport` và `WebSocketNetworkTransport`.
2. Thêm `MultiNetworkTransport` và điền danh sách Transports của nó. Mỗi mục có một Transport và một Port.
3. Gán `MultiNetworkTransport` vào field Transport của `NetworkManager`.

| Mục | Transport | Port |
|---|---|---|
| 0 | `UdpNetworkTransport` | bị bỏ qua, xem bên dưới |
| 1 | `WebSocketNetworkTransport` | 8080 |

```csharp
manager.ServerManager.StartConnection(7777);
```

## Port <a href="#ports" id="ports"></a>

Mục đầu tiên lắng nghe trên port truyền vào `ServerManager.StartConnection`, và `ServerManager.Port` báo port đó. Mọi mục khác lắng nghe trên port ghi trong mục, từ 0 tới 65535. Port 0 để hệ điều hành chọn, nhưng khi đó client không thể biết trước port.

## Client <a href="#clients" id="clients"></a>

Client có `MultiNetworkTransport` kết nối qua mục đầu tiên. Trong bản build WebGL, các mục không chạy được trong trình duyệt bị bỏ qua, nên một danh sách UDP rồi WebSocket cho bản build desktop dùng UDP và bản build WebGL dùng WebSocket từ cùng một scene. Client WebGL kết nối tới port bạn truyền vào `StartConnection`, nên hãy truyền port của mục WebSocket vào đó.

Nếu không mục nào chạy được, việc tạo factory ném `<name> has no transports`, hoặc trong trình duyệt là `<name> cannot run in a browser; ...`.

## Frame budget theo kết nối <a href="#frame-budget-per-connection" id="frame-budget-per-connection"></a>

Mỗi kết nối dùng frame budget của transport mà nó đi vào, nên peer UDP có 1200 byte và peer WebSocket có frame lớn nhất. `ServerManager.FrameBudgetOf(peerId)` báo budget của một peer.

## Cấu hình <a href="#configuration" id="configuration"></a>

| Field | Ý nghĩa |
|---|---|
| Transports | Danh sách các mục, mỗi mục gồm một component transport và một port |

Mục không có transport sẽ ném `<name> has an empty transport entry`, và port nằm ngoài 0 tới 65535 cũng ném exception.

[Tổng quan transport](overview.md) so sánh các transport có thể kết hợp, các trang [WebSocket](websocket.md) và [UDP](udp.md) mô tả cặp thường dùng, và [WebGL](../unity/webgl.md) nói về phía trình duyệt.
