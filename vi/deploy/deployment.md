# Đưa server lên môi trường thật

Trang này liệt kê những gì một máy chủ và mạng của nó cần. Hosting, matchmaking và dịch vụ relay không thuộc package.

<figure><img src="../.gitbook/assets/diagrams/deploy-topology.svg" alt="Một client desktop dùng UdpNetworkTransport tới máy server qua UDP ở port 7777, port này phải mở inbound và là entry 0 của một MultiNetworkTransport, trên port truyền vào StartConnection. Một client trình duyệt tải trang qua HTTPS và kết nối bằng wss:// tới một reverse proxy kết thúc TLS, rồi proxy chuyển tiếp ws:// tới entry 1 của server, port 8080 với Path /play. Client tới server qua IPv4, Allowed Origins liệt kê các origin phục vụ trang game, và server với client phải được build từ cùng model, prefab và scene."><figcaption><p>Một server cho cả client desktop lẫn trình duyệt, với các phần mà trang này đề cập.</p></figcaption></figure>

## Port và giao thức <a href="#ports-and-protocols" id="ports-and-protocols"></a>

| Transport | Giao thức cần mở | Port |
|---|---|---|
| UDP | UDP chiều vào | Port truyền vào `StartConnection` |
| TCP | TCP chiều vào | Port truyền vào `StartConnection` |
| WebSocket | TCP chiều vào | Port truyền vào `StartConnection`, hoặc port của proxy |
| Nhiều transport | Giao thức của từng mục | Mục đầu tiên trên port truyền vào `StartConnection`, các mục khác trên port đã cấu hình |

Server bind mọi interface IPv4, nên client phải tới server qua IPv4.

## Client trình duyệt <a href="#browser-clients" id="browser-clients"></a>

Trang được phục vụ qua HTTPS chỉ mở được kết nối `wss://`, nên hãy chạy một reverse proxy kết thúc TLS và chuyển tiếp các WebSocket upgrade tới port `ws://` của server. WebSocket Path của server phải khớp với path mà proxy chuyển tiếp tới. Đặt Allowed Origins trên `WebSocketNetworkTransport` thành các origin phục vụ game của bạn. [WebSocket](../connections/transports/websocket.md) mô tả các thiết lập này.

Client desktop và mobile có thể dùng cùng proxy đó với `wss://`, hoặc TLS qua TCP với một proxy chuyển tiếp TCP. Client kiểm chứng chỉ của proxy bằng bộ gốc của Mozilla, nên chứng chỉ của một CA công khai dùng được ngay. [TLS phía client](../connections/transports/tls.md) mô tả trường hợp CA riêng.

## Phiên bản <a href="#versions" id="versions"></a>

Client chỉ kết nối được tới server build từ cùng các model, vì handshake so sánh schema và từ chối mọi schema khác bằng `SchemaConflict`. Prefab và scene object cũng phải khớp, nếu không client dừng với `PrefabMismatch` khi object spawn. Khi phát hành phiên bản mới, hãy cập nhật server và client cùng lúc, hoặc chạy song song server cũ và mới trên các port khác nhau.

## Timeout <a href="#timeouts" id="timeouts"></a>

| Thiết lập | Mặc định | Tác dụng |
|---|---|---|
| Handshake Timeout Seconds | 5 | Client không hoàn tất handshake kịp sẽ thất bại và thử lại |
| Heartbeat Interval Seconds | 5 | Khoảng im lặng mà sau đó kết nối gửi một probe |
| Heartbeat Timeout Seconds | 15 | Thời gian một probe được phép không có trả lời trước khi kết nối dừng |

Với giá trị mặc định, server gỡ một client biến mất mà không đóng kết nối khoảng 20 giây sau message cuối cùng của nó, và despawn các object của nó. Giá trị thấp hơn giải phóng tài nguyên sớm hơn, nhưng cũng ngắt kết nối người chơi mạng kém sớm hơn.

## Tải của server <a href="#server-load" id="server-load"></a>

Khối lượng việc của server tăng theo số object, observer và peer. Bạn có thể giảm nó bằng một [observer rule](../objects/observers.md), state model nhỏ và tick rate không cao hơn mức game cần, như [hiệu năng](../advanced/performance.md) giải thích chi tiết hơn.

Để build chính server, xem [dedicated server](dedicated-server.md). [Tổng quan transport](../connections/transports/README.md) so sánh các transport có port cần mở.
