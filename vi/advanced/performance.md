# Hiệu năng

Trang này liệt kê các thiết lập và thói quen ảnh hưởng tới lượng dữ liệu package gửi và lượng tính toán nó làm. Giá trị phù hợp tùy vào từng game, nên hãy đo trước và sau mỗi thay đổi.

## Tick rate <a href="#tick-rate" id="tick-rate"></a>

Phần lớn công việc diễn ra mỗi tick một lần, gồm input, physics, chụp state và transform, cập nhật observer và flush. Vì vậy giảm tick rate một nửa sẽ giảm khoảng một nửa khối lượng việc đó và số gói tin. Hãy chọn tick rate thấp nhất mà game vẫn phản hồi tốt và khớp với physics của nó.

## Băng thông <a href="#bandwidth" id="bandwidth"></a>

| Đòn bẩy | Tác dụng |
|---|---|
| Bundling | Các message vào queue trong một tick đi cùng nhau, đóng vào các frame theo frame budget của transport (1200 byte với UDP). Nhiều message nhỏ tốn ít gói tin. |
| State | Chỉ gửi khi bản encode thay đổi, và gửi dạng delta khi delta nhỏ hơn. Giữ state model nhỏ và cố định kích thước để delta áp dụng được. Tách dữ liệu ít thay đổi và dữ liệu thay đổi thường xuyên vào các behaviour khác nhau. |
| `NetworkTransform` | Chỉ gửi phần di chuyển quá ngưỡng, và không gửi gì khi đứng yên. Tắt các phần không cần; tăng ngưỡng cho object không cần độ chính xác cao. |
| `NetworkAnimator` | Float Step làm tròn parameter float, để thay đổi rất nhỏ không tạo message. |
| Observer | Một [observer rule](../objects/observers.md) giữ cho mỗi client không nhận object nó không cần. Đây thường là mức tiết kiệm lớn nhất trong thế giới lớn. Trên server có nhiều phòng, [nhóm](../objects/observers.md#groups) giữ object của mỗi phòng ở trong phòng đó. |
| Input Redundancy | Mỗi input message mang chừng này input. Giá trị cao hơn chịu được mất gói nhiều hơn nhưng tốn nhiều byte hơn. |
| Reconcile Interval | Server gửi reconcile state sau mỗi chừng này tick. Giá trị cao hơn gửi ít hơn và sửa muộn hơn. |
| Channel | Message reliable mang sequence number và cần acknowledgement. Dùng channel unreliable cho dữ liệu sắp được thay thế. |

## CPU của server <a href="#server-cpu" id="server-cpu"></a>

Việc tính lại observer được trải trên Observer Interval tick, nên khoảng dài hơn tốn ít hơn mỗi tick nhưng phản ứng chậm hơn với chuyển động. `ObserverRule.Observes` chạy cho mỗi peer và object đang được tính lại và nên rẻ; ví dụ `DistanceRule` cache vị trí các object mà mỗi peer sở hữu theo từng tick.

Một rule mà kết quả không phụ thuộc chuyển động có thể trả false từ `RebuildsPeriodically`, khi đó server bỏ qua việc tính lại theo chu kỳ. Với [nhóm](../objects/observers.md#groups), server chỉ tính lại và chỉ hỏi rule về các cặp object và peer cùng nhóm, nên phần chi phí này tăng theo kích thước nhóm.

Mọi behaviour có state được encode mỗi tick một lần để phát hiện thay đổi, nên nhiều object với state model lớn sẽ tốn thời gian encode kể cả khi không có gì thay đổi. Behaviour đăng ký state bằng `onlyWhenDirty` chỉ được encode sau khi nó gọi `SetStateDirty()`, như mô tả trong [đánh dấu thay đổi](../synchronization/state.md#marking-changes).

Transform được đọc sau mỗi tick, trừ khi server biết lúc nào chúng đổi. `NetworkTransform` trên object do [Rapier](../rapier/overview.md) mô phỏng, và entity console đồng bộ bằng `SyncTransform(sync, receiver)`, chỉ được đọc khi di chuyển, nên object đứng yên không thêm lần đọc nào. [NetworkTransform](../synchronization/transform.md#server-behavior) liệt kê những transform được đọc sau mỗi tick.

## CPU của client <a href="#client-cpu" id="client-cpu"></a>

Một lần sửa replay mọi tick kể từ tick được sửa, và khi có physics thì còn step mọi world của rollback group một lần cho mỗi tick được replay. Hãy giữ Prediction History và số world được dự đoán nhỏ nhất mà game cho phép, và giữ cho việc sửa hiếm khi xảy ra, như mô tả trong [reconciliation](../prediction/reconciliation.md#diagnosing-frequent-corrections). Max Ticks Per Frame giới hạn mức client đuổi theo sau một frame chậm, và bỏ các tick vượt quá.

## Queue và giới hạn <a href="#queues-and-limits" id="queues-and-limits"></a>

Mỗi kết nối có một send queue giới hạn bởi Message Capacity và Byte Capacity, cùng một reliable window. Lệnh gửi không vừa sẽ không được đưa vào queue và trả về `SendResult.Full`, `BytesFull` hoặc `TooLargeForQueue`. Tăng giới hạn tốn thêm bộ nhớ cho mỗi kết nối, và chạm tới giới hạn thường có nghĩa là game gửi nhanh hơn khả năng mang của kết nối.

## Cấp phát bộ nhớ <a href="#allocations" id="allocations"></a>

Adapter encode vào một buffer được dùng lại, và lệnh gửi RPC copy các byte vào queue. State và input decode vào các instance bạn đã đăng ký, còn mỗi RPC có model nhận được sẽ tạo một instance model mới cho handler.

[Channel và độ tin cậy](../messaging/channels.md) giải thích bundling và reliable window, [debug](debugging.md) liệt kê các giá trị đáng theo dõi khi đo, và [cấu hình](../reference/configuration.md) liệt kê mọi thiết lập được nhắc tới ở đây.
