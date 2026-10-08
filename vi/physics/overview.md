# Tổng quan physics

Package có thể chạy physics 3D và 2D của Unity theo tick của network. Khi bật mô phỏng physics, `NetworkManager` step physics mỗi tick một lần, client giữ các body nó không dự đoán ở vị trí được replicate, và prediction có thể rollback physics. Code game truy cập body của một network object qua các type riêng của package, `PhysicsBody` và `PhysicsBody2D`.

```text
Game code: apply, capture, restore, OnTick
    ↓
NetworkObject.Body / Body2D        PhysicsBody, PhysicsBody2D
    ↓
IPhysicsWorld / IPhysicsWorld2D    one per Unity physics scene, both extend IPhysicsSimulation
    ↓
RigidbodyPhysics                   Unity PhysicsScene and PhysicsScene2D
```

Code dùng `PhysicsBody` không phụ thuộc vào API `Rigidbody` của Unity.

## Bật tính năng <a href="#turning-it-on" id="turning-it-on"></a>

Field Physics của `NetworkManager` giữ component chạy physics cho nó, tức `RigidbodyPhysics`. Manager có field Physics trống sẽ tự thêm một `RigidbodyPhysics` vào GameObject của nó khi khởi động, với mô phỏng physics tắt.

1. Thêm `RigidbodyPhysics` vào GameObject của `NetworkManager`.
2. Tick field Simulate Physics của nó.
3. Kéo nó vào field Physics của `NetworkManager`.

Làm như vậy cho server và cho mọi client. Khi có ít nhất một manager mô phỏng physics, package đặt `Physics.simulationMode` và `Physics2D.simulationMode` thành `Script`, để Unity không còn step physics sau `FixedUpdate`, và khôi phục mode ban đầu khi manager cuối cùng như vậy bị hủy.

Từ đó, manager làm bốn việc mỗi tick:

1. Trên client ở xa, đặt các proxy (mô tả bên dưới).
2. Áp dụng input.
3. Step physics world 3D và 2D của mọi scene đã load một lần, bằng `TimeManager.TickDelta`.
4. Truy vấn contact cho các [component contact](contacts.md).

`FixedUpdate` vẫn chạy theo fixed timestep của Unity, nhưng physics không còn tiến lên ở đó, nên lực và thay đổi vận tốc cần được network hóa phải đặt trong `apply` hoặc một tick event.

Hãy đặt tick rate bằng tần số mà physics của game đã được tinh chỉnh. Ví dụ, project tinh chỉnh cho fixed timestep 0.02 s khớp với 50 tick mỗi giây.

## Một world, một chủ <a href="#one-world-one-owner" id="one-world-one-owner"></a>

World là một physics scene của Unity, hoặc `PhysicsScene` 3D hoặc `PhysicsScene2D` của các scene dùng nó. Nhiều scene dùng chung một world trừ khi chúng được load với physics cục bộ riêng.

Mỗi world có một simulation state và được step bởi đúng một `NetworkManager`, đúng một lần mỗi tick. Manager đầu tiên step một world sẽ sở hữu nó, và mọi manager khác trong cùng tiến trình để yên world đó, nên một server manager và một client manager trong cùng tiến trình không bao giờ step cùng một physics hai lần.

## Body được dự đoán và body được interpolate trong cùng world <a href="#predicted-and-interpolated-bodies-in-one-world" id="predicted-and-interpolated-bodies-in-one-world"></a>

Trên client ở xa, body của một networked object đóng một trong hai vai:

| Vai | Object | Client làm gì |
|---|---|---|
| Predicted | Object client sở hữu và dự đoán | Mô phỏng body; rollback nó khi có sửa |
| Proxy | Mọi networked object khác có body | Biến body thành kinematic và đặt nó vào vị trí `NetworkTransform` trước mỗi lần step |

Proxy cho phép body được dự đoán va chạm với object của người chơi khác tại vị trí client đang hiển thị. Khi một object thôi là proxy, ví dụ vì client trở thành owner của nó, các thiết lập body ban đầu được khôi phục. Server và host mô phỏng mọi body bình thường.

## Body <a href="#bodies" id="bodies"></a>

`NetworkObject.Body` trả về một `PhysicsBody` cho `Rigidbody` của object, và `NetworkObject.Body2D` trả về một `PhysicsBody2D` cho `Rigidbody2D` của nó. Component body phải nằm trên cùng GameObject với `NetworkObject`. [PhysicsBody](physics-body.md) mô tả cả hai type.

## Geometry và body thêm lúc chạy <a href="#geometry-and-bodies-added-at-runtime" id="geometry-and-bodies-added-at-runtime"></a>

Một level dựng lúc chạy có thể giao geometry của nó cho component physics. `NetworkPhysics.AddStatic(Scene, IReadOnlyList<ColliderDesc>)` và `AddStatic2D` thêm một nhóm collider tĩnh vào một scene, `AddStatic(GameObject)` và `AddStatic2D(GameObject)` thêm các collider dưới một GameObject, còn `RemoveStatic` gỡ một nhóm ra. `AddBody` và `AddBody2D` thêm một body không thuộc network object nào, như một bục mà mọi peer di chuyển giống nhau theo số tick, và `RemoveBody`, `RemoveBody2D` gỡ nó. `BodyDescriptions.TryDescribe` và `TryDescribe2D` dựng một `BodyDesc` hoặc `BodyDesc2D` từ các collider và `Rigidbody` hoặc `Rigidbody2D` của một GameObject.

Với `RigidbodyPhysics`, một nhóm tĩnh là một GameObject ẩn trong scene, mỗi collider là một con. `AddStatic(GameObject)` trả về nhóm rỗng, vì physics của Unity đã có các collider của GameObject đó. Body dynamic thêm bằng `AddBody` được lưu và khôi phục cùng world của nó, còn body kinematic thì không.

## Physics backend <a href="#physics-backend" id="physics-backend"></a>

Server báo cho mỗi client physics backend nó dùng, và client dùng backend khác sẽ dừng với `StopReason.PhysicsBackendMismatch` và không kết nối lại. Hãy cho server và client cùng một component physics.

## Khi không bật mô phỏng physics <a href="#without-physics-simulation" id="without-physics-simulation"></a>

Khi Simulate Physics tắt, Unity step physics theo fixed timestep của nó, độc lập với tick. Body trên server vẫn di chuyển và `NetworkTransform` vẫn replicate chúng, nhưng bản copy của các body dynamic trên client tự mô phỏng giữa các bản cập nhật. Không có proxy, và prediction không thể rollback physics.

## Giới hạn <a href="#limitations" id="limitations"></a>

Physics của Unity không tất định giữa các máy, và state đã lưu không chứa dữ liệu contact, nên rollback chỉ gần đúng, như [rollback với physics](../prediction/rollback.md) giải thích. Joint, character controller và wheel collider không được lưu hay khôi phục.

Mỗi network object có một body, trên GameObject của `NetworkObject`. Body trên object con vẫn được mô phỏng và lưu như một phần của world, nhưng không có `PhysicsBody` và không được làm proxy.

Các trang [PhysicsBody](physics-body.md) và [contact event](contacts.md) nói về những gì code game dùng, còn [kiến trúc physics](architecture.md) mô tả các interface bên dưới.
