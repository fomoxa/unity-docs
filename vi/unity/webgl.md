# WebGL

Bản build WebGL chạy trong trình duyệt và chỉ có thể là client. Nó kết nối tới server qua object `WebSocket` của trình duyệt thông qua plugin `FomoxaWebSocket.jslib` của package, còn server chạy dưới dạng bản build desktop hoặc server có WebSocket listener.

## Thiết lập <a href="#setup" id="setup"></a>

1. Ở phía server, dùng `WebSocketNetworkTransport`, riêng lẻ hoặc là một mục của `MultiNetworkTransport` bên cạnh UDP cho client desktop.
2. Trong scene mà bản build WebGL dùng, gán cho `NetworkManager` một `WebSocketNetworkTransport`, hoặc một `MultiNetworkTransport` có chứa nó. Trong trình duyệt, `MultiNetworkTransport` bỏ qua các mục không chạy được ở đó.
3. Kết nối bằng port WebSocket hoặc bằng URL:

```csharp
manager.ClientManager.StartConnection("wss://game.example.com/play", 0);
```

Cả URL `ws://` và `wss://` đều dùng được trong trình duyệt, vì trình duyệt lo TLS. Với host name và port, client kết nối tới `ws://<host>:<port><Path>`.

## Hành vi trong trình duyệt <a href="#behavior-in-the-browser" id="behavior-in-the-browser"></a>

Kết nối được mở bất đồng bộ, và nếu socket không mở được trong Handshake Timeout Seconds, client đánh dấu lần thử thất bại và thử lại. Khi có hơn Max Buffered Bytes đang chờ trong send buffer của trình duyệt, transport báo nó không gửi được, và package giữ message trong queue cho tới khi buffer vơi đi. Mọi thứ khác, kể cả prediction, observer và scene, hoạt động như trên client desktop.

## Những gì không hoạt động <a href="#what-does-not-work" id="what-does-not-work"></a>

| Hành động | Kết quả |
|---|---|
| `ServerManager.StartConnection` | Ném `PlatformNotSupportedException`: `a server cannot listen in a browser; WebGL builds are clients only` |
| Host mode | Không thể, vì nó khởi động server |
| Dùng `UdpNetworkTransport` hoặc `TcpNetworkTransport` làm transport | `NetworkManager` ném exception khi khởi động: `<Transport> cannot run in a browser; assign a WebSocketNetworkTransport or a MultiNetworkTransport to the NetworkManager for WebGL builds` |

## Hosting <a href="#hosting" id="hosting"></a>

Trình duyệt từ chối kết nối `ws://` từ trang HTTPS, nên hãy phục vụ trang qua HTTPS và game server qua `wss://` thông qua một proxy kết thúc TLS. Đặt cả Allowed Origins trên `WebSocketNetworkTransport` của server. [Triển khai](../server/deployment.md) nói về phía server của thiết lập này.

Trang [WebSocket](../transports/websocket.md) mô tả các thiết lập của transport, và [nhiều transport](../transports/multi-transport.md) cho thấy cách một server phục vụ cùng lúc client WebGL và client desktop.
