# TCP

`TcpNetworkTransport` mang frame Fomoxa qua một kết nối TCP, dùng transport TCP của Fomoxa.Net.

## Cách dùng cơ bản <a href="#basic-usage" id="basic-usage"></a>

Thêm `TcpNetworkTransport` vào GameObject của `NetworkManager` và gán nó vào field Transport. Component không có thiết lập riêng, và server cùng mọi client đều phải dùng TCP.

## Hành vi <a href="#behavior" id="behavior"></a>

| | |
|---|---|
| Mô hình kết nối | Client mở một kết nối TCP, rồi chạy handshake Fomoxa. |
| Độ tin cậy | Stream reliable. Channel reliable của package vẫn đánh số và acknowledge message của nó. |
| Thứ tự | Có thứ tự. Một gói bị mất làm chậm mọi thứ phía sau cho tới khi TCP gửi lại nó. |
| Frame budget | Frame Fomoxa lớn nhất. Một lần flush có thể đóng mọi message trong queue vào một bundle. |
| Địa chỉ | Host name hoặc địa chỉ IP, và port. Client thử lần lượt từng địa chỉ đã phân giải, ưu tiên IPv4, cho tới khi một địa chỉ kết nối được. |
| Server | Bind port trên mọi interface IPv4. Port 0 chọn một port trống. |
| Chặn | Không bao giờ chặn; kết nối được tạo bằng socket không chặn. |

## Vòng đời <a href="#lifecycle" id="lifecycle"></a>

Kết nối bị từ chối hoặc thất bại sẽ dừng client với `StopReason.TransportError`, sau đó nó thử lại. Khi một kết nối đã thiết lập bị đóng, session dừng với `PeerClosed` hoặc `TransportError`, tùy cách kết nối bị đóng.

## Giới hạn theo nền tảng <a href="#platform-limitations" id="platform-limitations"></a>

TCP không dùng được trong bản build WebGL, nơi việc tạo factory ném `TcpNetworkTransport cannot run in a browser; ...`. Server chỉ lắng nghe trên IPv4, và port TCP của nó phải được mở trong firewall.

[Tổng quan transport](overview.md) so sánh TCP với các transport khác. [WebSocket](websocket.md) cũng chạy qua TCP và là lựa chọn cho trình duyệt.
