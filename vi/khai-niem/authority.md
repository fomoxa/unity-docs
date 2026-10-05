# Authority

Package theo mô hình server-authoritative. Server giữ game state thật và là bên duy nhất có thể thay đổi những gì người chơi khác thấy, nên client chỉ có thể yêu cầu một thay đổi và server quyết định nó có xảy ra hay không.

## Những việc chỉ server làm <a href="#what-only-the-server-does" id="what-only-the-server-does"></a>

Chỉ server spawn, despawn network object và đổi owner của chúng. Gọi `ServerManager.Spawn` trên một tiến trình không chạy server sẽ ném `the server is not started`.

State model thay đổi trên server và truyền tới client, không bao giờ theo chiều ngược lại. Chuyển động cũng vậy: `NetworkTransform` gửi transform của server tới client và không gửi thay đổi transform của client, và chỉ parameter `NetworkAnimator` của server mới tới được người chơi khác.

Server cũng load và unload network scene và quyết định client nào observe object nào.

## Client có thể gửi gì <a href="#what-a-client-can-send" id="what-a-client-can-send"></a>

| Đường gửi | Package kiểm tra | Hướng dẫn |
|---|---|---|
| Server RPC | Bên gọi phải sở hữu object, trừ khi RPC đặt `RequireOwnership = false`. Lời gọi từ peer khác bị bỏ kèm cảnh báo. | [RPC](../messaging/rpc.md) |
| Input cho object được dự đoán | Bên gửi phải sở hữu object. Input từ peer khác bị bỏ kèm cảnh báo. Input cho tick đã qua hoặc quá xa phía trước bị bỏ và được đếm. | [Input](../prediction/input.md) |
| Raw message | Không kiểm tra. Handler nhận peer id của bên gửi và phải tự kiểm tra nội dung. | [Raw message](../messaging/messages.md) |

Package kiểm tra ai được gửi, nhưng không kiểm tra nội dung có hợp lý không, ví dụ một tốc độ hay một vị trí. Hãy kiểm tra tham số trong handler RPC hoặc input trên server.

## Ownership không phải là authority <a href="#ownership-is-not-authority" id="ownership-is-not-authority"></a>

Owner là peer mà object thuộc về, như nhân vật thuộc về người chơi điều khiển nó. Ownership cho client đó gọi server RPC của object, và nếu object có input model, owner còn dự đoán nó. Server vẫn chạy object, và sửa lại dự đoán của owner khi nó khác kết quả của server. [Ownership](../core/ownership.md) mô tả cách gán và đổi owner.

## Prediction vẫn giữ server-authoritative <a href="#prediction-stays-server-authoritative" id="prediction-stays-server-authoritative"></a>

Với prediction, owner áp dụng input của mình ngay thay vì chờ server. Server áp dụng cùng input đó khi nó tới và gửi kết quả về, và nếu hai kết quả khác nhau, client khôi phục kết quả của server rồi chạy lại các input mới hơn lên trên. Dù client đã dự đoán gì, kết quả của server mới là kết quả được giữ lại. [Prediction](prediction.md) giải thích vòng lặp này chi tiết hơn.

Để biết quyết định của server tới client như thế nào, xem [mô hình networking](networking-model.md) và [replication](replication.md).
