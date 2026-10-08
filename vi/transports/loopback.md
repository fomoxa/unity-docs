# Loopback

Transport loopback nối một client và một server trong cùng tiến trình bằng cách truyền frame qua các queue trong bộ nhớ, và package dùng nó cho client của chính host. Nó không mô phỏng mạng, nên không thêm độ trễ, mất gói hay đảo thứ tự.

## Host dùng nó thế nào <a href="#how-the-host-uses-it" id="how-the-host-uses-it"></a>

`ServerManager.StartConnection` mở hai listener, của transport và một listener loopback. Khi cùng `NetworkManager` đó gọi `ClientManager.StartConnection`, client kết nối thẳng tới listener loopback. Nó bỏ qua địa chỉ và port, không gì đi qua hệ điều hành, và kết nối không tự kết nối lại.

Kết nối loopback vẫn chạy handshake Fomoxa, bundle, độ tin cậy và mọi message của package, nên từ góc nhìn của server, client của host hành xử như một client ở xa. [Host mode](../core/host-mode.md) mô tả phần còn lại của hành vi host.

## Hành vi <a href="#behavior" id="behavior"></a>

| | |
|---|---|
| Mô hình kết nối | Cặp transport trong tiến trình, do listener tạo |
| Độ tin cậy và thứ tự | Frame tới đúng thứ tự. Mỗi phía giữ tối đa Message Capacity frame (mặc định 1024); khi queue đầy, frame cũ nhất bị bỏ. |
| Frame budget | Frame budget của transport của manager |
| Địa chỉ | Không có |
| Nền tảng | Mọi nền tảng server chạy được; không dùng trong WebGL, nơi không server nào chạy được |

## Dùng trực tiếp <a href="#using-it-directly" id="using-it-directly"></a>

`LoopbackListener` và `LoopbackTransport`, trong `Fomoxa.Networking.Transports`, là public, nên hữu ích cho test và cho một [transport tùy chỉnh](custom-transport.md) chạy trong bộ nhớ. `new LoopbackListener(maxQueuedPackets)` tạo một listener. `Connect()` của nó trả về đầu client của một cặp mới, và `Accept()` của nó trả về đầu server. `LoopbackTransport.CreatePair` tạo một cặp đã kết nối mà không cần listener.

[Tổng quan transport](overview.md) liệt kê các transport mạng mà kết nối loopback thay thế.
