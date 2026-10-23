# UDP

`UdpNetworkTransport` gửi frame Fomoxa dưới dạng datagram UDP, dùng transport UDP của Fomoxa.Net. Đây là transport mặc định, thứ `NetworkManager` tự thêm khi không có transport nào được gán.

## Cách dùng cơ bản <a href="#basic-usage" id="basic-usage"></a>

Thêm `UdpNetworkTransport` vào GameObject của `NetworkManager` và gán nó vào field Transport. Component không có thiết lập riêng.

```csharp
manager.ServerManager.StartConnection(7777);
manager.ClientManager.StartConnection("203.0.113.10", 7777);
```

## Hành vi <a href="#behavior" id="behavior"></a>

| | |
|---|---|
| Mô hình kết nối | UDP không có kết nối. Transport của client sẵn sàng ngay, và handshake Fomoxa thiết lập session. |
| Độ tin cậy | Transport không có. Package gửi lại message `ReliableOrdered`; message `Unreliable` có thể mất. |
| Thứ tự | Transport không có. Package sắp thứ tự message `ReliableOrdered`. |
| Frame budget | 1200 byte. Khi flush, message được đóng vào bundle tới kích thước đó. Message `ReliableOrdered` lớn hơn được chia thành các mảnh cỡ đó, tổng tối đa 1 MiB. Message `Unreliable` lớn hơn được gửi riêng, tối đa một datagram (frame 65499 byte). Xem [kích thước message](../../messaging/channels.md#message-size). |
| Mã phiên | Mỗi datagram bắt đầu bằng một mã 8 byte do server cấp, nên datagram dài hơn frame của nó 8 byte. Client giữ session khi địa chỉ nguồn đổi, ví dụ khi điện thoại chuyển từ wifi sang dữ liệu di động. Mã này không được mã hóa và không xác thực client. |
| Địa chỉ | Host name hoặc địa chỉ IP, và port. Client dùng địa chỉ phân giải được đầu tiên, ưu tiên IPv4. |
| Server | Bind port trên mọi interface IPv4. Port 0 chọn một port trống. |
| Chặn | Không bao giờ chặn. |

## Vòng đời <a href="#lifecycle" id="lifecycle"></a>

Trạng thái của client là `Starting` khi nó phân giải địa chỉ và chạy handshake, và chuyển thành `Started` khi handshake thành công. Vì UDP không có bước kết nối, server không tới được chỉ bị phát hiện qua handshake timeout (Handshake Timeout Seconds, mặc định 5), sau đó client thử lại. Trên server, client biến mất bị phát hiện qua heartbeat timeout, còn client dừng bình thường thì gửi message rời đi trước.

## Giới hạn theo nền tảng <a href="#platform-limitations" id="platform-limitations"></a>

UDP không dùng được trong bản build WebGL. Tạo factory trong trình duyệt sẽ ném `UdpNetworkTransport cannot run in a browser; assign a WebSocketNetworkTransport or a MultiNetworkTransport to the NetworkManager for WebGL builds`. Server chỉ lắng nghe trên IPv4, và port UDP của nó phải được mở trong firewall.

[Tổng quan transport](README.md) so sánh UDP với các transport khác, và [channel và độ tin cậy](../../messaging/channels.md) giải thích cách package thêm độ tin cậy lên trên nó.
