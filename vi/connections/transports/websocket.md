# WebSocket

`WebSocketNetworkTransport` mang frame Fomoxa dưới dạng message WebSocket nhị phân, và là transport mà client WebGL cần. Với server và client desktop, package tự hiện thực giao thức WebSocket (RFC 6455), còn bản build WebGL dùng object `WebSocket` của trình duyệt.

## Cách dùng cơ bản <a href="#basic-usage" id="basic-usage"></a>

Thêm `WebSocketNetworkTransport` vào GameObject của `NetworkManager` và gán nó vào field Transport.

Client kết nối bằng host và port, hoặc bằng URL:

```csharp
manager.ClientManager.StartConnection("game.example.com", 8080);
manager.ClientManager.StartConnection("ws://game.example.com:8080/play", 0);
```

Với host và port, client kết nối tới `ws://<host>:<port><Path>`. Với URL `ws://`, nó dùng host, port, path và query của URL và bỏ qua tham số port, và URL không có port sẽ dùng port 80.

## Cấu hình <a href="#configuration" id="configuration"></a>

| Field | Mặc định | Ý nghĩa |
|---|---|---|
| Path | `/` | Path mà server chấp nhận và client yêu cầu khi không có URL. Nó bắt đầu bằng `/` và không chứa dấu cách, `?` hay `#`. |
| Max Handshake Bytes | 8192 | Kích thước lớn nhất của HTTP upgrade request mà server đọc; tối thiểu 256 |
| Handshake Timeout Seconds | 5 | Thời gian cho phép của HTTP upgrade: server chờ request, client desktop chờ response, client trình duyệt chờ socket mở. Với URL `wss://` trên client desktop, thời gian này tính cả bước bắt tay TLS trước upgrade. |
| Allowed Origins | trống | Khi không trống, server từ chối request có header `Origin` không nằm trong danh sách. Request không có header `Origin` được chấp nhận. |
| Max Buffered Bytes | 1048576 | Trong trình duyệt, lượng dữ liệu chưa gửi mà vượt quá thì transport ngừng gửi cho tới khi trình duyệt bắt kịp |

## Hành vi <a href="#behavior" id="behavior"></a>

| | |
|---|---|
| Mô hình kết nối | Kết nối TCP, HTTP/1.1 upgrade, rồi handshake Fomoxa |
| Độ tin cậy và thứ tự | Reliable và có thứ tự, như TCP |
| Frame budget | Frame Fomoxa lớn nhất |
| Message | Mỗi frame Fomoxa là một message WebSocket nhị phân. Không dùng extension hay subprotocol. |
| Server | Bind port trên mọi interface IPv4. Request tới path khác nhận `404 Not Found`, origin bị từ chối nhận `403 Forbidden`, request sai định dạng nhận `400 Bad Request`, và version khác 13 nhận `426 Upgrade Required`. |
| Chặn | Không bao giờ chặn |

## TLS và wss:// <a href="#tls-and-wss" id="tls-and-wss"></a>

Client kết nối qua TLS khi bạn đưa nó một URL `wss://`, và URL `wss://` không ghi port thì dùng port 443:

```csharp
manager.ClientManager.StartConnection("wss://game.example.com/play", 0);
```

Trên client desktop, package tự làm bước bắt tay TLS và kiểm chứng chỉ của server, như [TLS phía client](tls.md) mô tả. Property `Tls` của component giữ các thiết lập đó. Trong trình duyệt, trình duyệt làm TLS.

Server không làm TLS. Hãy đặt một reverse proxy kết thúc TLS phía trước server và để nó chuyển tiếp kết nối đã upgrade tới port `ws://` của server. Trang được phục vụ qua HTTPS chỉ mở được kết nối `wss://`, nên client trình duyệt luôn cần proxy đó.

## Kiểm tra origin <a href="#origin-checks" id="origin-checks"></a>

Trình duyệt gửi header `Origin` chứa origin của trang, như `https://game.example.com`. Đặt Allowed Origins thành các origin host game của bạn sẽ ngăn các trang web khác kết nối qua trình duyệt của khách truy cập. Client desktop không gửi header này và luôn được chấp nhận.

## Giới hạn theo nền tảng <a href="#platform-limitations" id="platform-limitations"></a>

Bản build WebGL chỉ có thể là client và không khởi động được server hay host. Trong Editor và player desktop, component dùng client của chính package, còn trong player WebGL nó dùng trình duyệt.

[WebGL](../../deploy/webgl.md) nói về bản build cho trình duyệt, [nhiều transport](multi-transport.md) cho thấy cách phục vụ WebSocket cùng UDP, và [triển khai](../../deploy/deployment.md) nói về thiết lập proxy trên một server thật.
