# Authority

Package theo mô hình server-authoritative. Server giữ game state thật và là phía duy nhất thay đổi được những gì người chơi khác nhìn thấy. Client chỉ có thể xin một thay đổi, còn server quyết định nó có xảy ra hay không. Một client gian lận vì thế có thể gửi yêu cầu sai, nhưng không thể trực tiếp thay đổi thế giới game.

<figure><img src="../.gitbook/assets/diagrams/authority.svg" alt="Client gửi bốn loại message tới server. Server RPC được kiểm tra: người gọi phải là owner của object, trừ khi RequireOwnership là false. Input được kiểm tra: người gửi phải là owner và tick không được quá cũ hay quá xa. Raw message không được kiểm tra; handler nhận peer id của người gửi. Owner transform được kiểm tra: người gửi phải là owner hiện tại và được server cho quyết định, và OwnerSampleFilter kiểm tra được giá trị. Package kiểm tra ai gửi, không kiểm tra nội dung gửi. Chỉ server spawn, despawn, đổi owner, đổi state, load network scene và chọn observer. Server cũng dời object, trừ khi cho owner quyết định một NetworkTransform."><figcaption><p>Bốn đường client có thể tới server, và package kiểm tra gì trên mỗi đường.</p></figcaption></figure>

## Những việc chỉ server làm <a href="#what-only-the-server-does" id="what-only-the-server-does"></a>

Chỉ server spawn, despawn network object và đổi owner của chúng. Gọi `ServerManager.Spawn` trên một tiến trình không chạy server sẽ ném `the server is not started`.

State model và [collection](../synchronization/collections.md) thay đổi trên server rồi đi xuống client, không bao giờ theo chiều ngược lại. Thay đổi một collection đã spawn trên client sẽ ném exception. Chuyển động cũng vậy: `NetworkTransform` gửi transform của server xuống client và không gửi thay đổi transform của client lên, trừ khi server cho owner quyết định như mô tả bên dưới, và chỉ parameter `NetworkAnimator` của server tới được người chơi khác.

Server cũng load và unload network scene, và quyết định client nào observe object nào.

## Client gửi được gì <a href="#what-a-client-can-send" id="what-a-client-can-send"></a>

| Đường | Package kiểm tra | Hướng dẫn |
|---|---|---|
| Server RPC | Người gọi phải là owner của object, trừ khi RPC đặt `RequireOwnership = false`. Lời gọi từ peer khác bị bỏ kèm một cảnh báo. | [RPC](../messaging/rpc.md) |
| Input cho object được dự đoán | Người gửi phải là owner của object. Input từ peer khác bị bỏ kèm một cảnh báo. Input cho tick đã qua, hoặc quá xa phía trước, bị bỏ và được đếm. | [Input](../prediction/input.md) |
| Raw message | Không kiểm tra. Handler nhận peer id của người gửi và phải tự kiểm tra nội dung. | [Raw message](../messaging/messages.md) |
| Transform của owner, cho `NetworkTransform` bật Owner Authority | Người gửi phải là owner hiện tại, và server phải đã cho nó quyết định. Mẫu từ một lượt trước hoặc từ trước một bản sửa bị bỏ. `OwnerSampleFilter` kiểm tra được giá trị. | [NetworkTransform](../synchronization/transform.md#letting-the-owner-decide) |

Package kiểm tra ai được gửi, nhưng không kiểm tra nội dung có hợp lý hay không, như một tốc độ hay một vị trí. Hãy kiểm tra tham số trong handler RPC hoặc handler input trên server.

## Ownership không phải authority <a href="#ownership-is-not-authority" id="ownership-is-not-authority"></a>

Owner là peer mà object thuộc về, như nhân vật thuộc về người chơi của nó. Ownership cho phép client đó gọi server RPC của object, và nếu object có input model, owner cũng dự đoán nó. Server vẫn là bên chạy object, và sửa prediction của owner khi nó khác kết quả của chính server. [Ownership](../objects/ownership.md) mô tả cách gán và đổi owner.

## Khi owner quyết định một transform <a href="#when-the-owner-decides-a-transform" id="when-the-owner-decides-a-transform"></a>

`NetworkTransform` bật Owner Authority cho client của owner quyết định đúng transform đó, nên owner di chuyển ngay mà không cần prediction. Server vẫn quyết định khi nào owner được làm vậy, chỉ nhận mẫu từ owner hiện tại, bỏ được bất kỳ mẫu nào trong `OwnerSampleFilter` và đưa owner về chỗ cũ được bằng `Teleport()`. Mọi thứ khác của object vẫn thuộc về server. Một owner gian lận có thể dời object như vậy tới bất cứ đâu bộ lọc cho phép, và trên server, va chạm và trigger sẽ dùng pose đó. Hãy dùng chế độ này cho object mà điều đó chấp nhận được, hoặc kiểm tra mẫu trong bộ lọc.

## Prediction vẫn do server quyết định <a href="#prediction-stays-server-authoritative" id="prediction-stays-server-authoritative"></a>

Với prediction, owner áp input của mình ngay thay vì đợi server. Server áp cùng input đó khi nó tới và gửi kết quả về. Nếu hai kết quả khác nhau, client khôi phục kết quả của server và phát lại các input mới hơn lên trên. [Prediction](prediction.md) giải thích vòng lặp này chi tiết hơn.

Về cách quyết định của server tới được client, xem [server, client và message](networking-model.md) và [replication](replication.md).
