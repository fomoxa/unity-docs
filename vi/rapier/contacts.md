# Contact event với Rapier

`NetworkTrigger`, `NetworkCollision`, `NetworkTrigger2D` và `NetworkCollision2D` giữ nguyên API với backend Rapier, nên code trong [contact event](../physics/contacts.md) chạy không cần sửa. Thứ thay đổi là nguồn của contact.

## Contact đến từ đâu <a href="#where-the-contacts-come-from" id="where-the-contacts-come-from"></a>

`RapierPhysics` tiếp quản các component này trên network object mà nó mô phỏng, trên các object tĩnh của network scene mà nó load, và trên các GameObject truyền vào `AddStatic(GameObject)` hoặc `AddStatic2D(GameObject)`. Component đã bị tiếp quản báo `IsAttached` là true, bỏ qua callback của Unity và báo các cặp contact và giao nhau của world Rapier:

- `NetworkCollision` hoặc `NetworkCollision2D` báo các collider có hình đặc chạm vào collider của nó;
- `NetworkTrigger` hoặc `NetworkTrigger2D` báo các collider chồng lên sensor của nó.

Các cặp này là một phần state của world, nên snapshot lưu chúng và replay khôi phục chúng cùng với body. Giống `RigidbodyPhysics`, component gọi event enter và exit một lần mỗi tick, và sau replay chỉ gọi cho phần thay đổi.

## Khác biệt so với RigidbodyPhysics <a href="#differences-from-rigidbodyphysics" id="differences-from-rigidbodyphysics"></a>

- `AdditionalSize` không có tác dụng. Contact là các cặp mà Rapier tính trong khoảng contact prediction của nó, và contact đứng yên được giữ, nên một object nằm trên mặt đất vẫn chạm mặt đất. Để phát hiện object ở gần mà không chạm, hãy thêm một trigger collider lớn hơn.
- Tick mà một contact bắt đầu hoặc kết thúc có thể lệch một so với PhysX hoặc Box2D, vì các engine tính contact khác nhau.
- Component thêm vào object tĩnh sau khi scene của nó đã load sẽ không bị tiếp quản và tiếp tục báo callback của Unity.

Với các luật game mà server và client dự đoán phải quyết định giống nhau, như chạm đất hay cái chết, bạn cũng có thể đọc trực tiếp tập contact của một world, như mô tả trong [đọc world](bodies.md#reading-the-worlds).
