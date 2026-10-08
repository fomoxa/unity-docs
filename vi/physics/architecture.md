# Kiến trúc physics

Trang này mô tả các interface physics ở tầng 1 và component physics của Unity ở tầng 2. Code game thường chỉ cần [`PhysicsBody`](physics-body.md), nên hãy đọc tiếp nếu muốn hiểu rollback hoạt động thế nào hoặc muốn dùng trực tiếp các interface.

## Các tầng <a href="#layers" id="layers"></a>

```text
Fomoxa physics API          PhysicsBody, PhysicsBody2D, PhysicsHistory      layer 1, Fomoxa.Networking.Simulation
        ↓
IPhysicsSimulation          Step, CreateSnapshot, Save, Load                layer 1
        ↓
IPhysicsWorld / IPhysicsWorld2D   bodies, forces, queries                   layer 1
        ↓
Physics component           NetworkPhysics, RigidbodyPhysics                layer 2, Fomoxa.Unity
        ↓
World implementation        UnityPhysicsWorld, UnityPhysicsWorld2D          layer 2
```

Tầng 1 không tham chiếu Unity, nên vector của nó là các type `System.Numerics`, và các world của Unity ánh xạ chúng sang physics của Unity.

## Quy tắc của một world <a href="#the-rule-of-a-world" id="the-rule-of-a-world"></a>

```text
one simulation world → one simulation state → one owner that steps it → exactly one Step per tick
```

World là một simulation state của physics engine. Với `RigidbodyPhysics`, đó là một `PhysicsScene` hoặc một `PhysicsScene2D`, dùng chung bởi mọi scene Unity sử dụng nó. Một `NetworkManager` sở hữu việc step một world, và không manager nào khác trong tiến trình step world đó.

Chủ sở hữu step world mỗi tick một lần. Một lần replay step lại world, nhưng chỉ sau khi đã load một state cũ hơn. Do đó rollback làm việc theo world và theo nhóm world, không bao giờ theo object, như mô tả ở mục [rollback group](../prediction/rollback.md#rollback-groups).

## IPhysicsSimulation <a href="#iphysicssimulation" id="iphysicssimulation"></a>

`IPhysicsSimulation` là phần của một world mà vòng lặp tick và rollback cần:

| Member | Ý nghĩa |
|---|---|
| `Backend` | `PhysicsBackend` của world |
| `Step(float seconds)` | Cho world tiến một bước |
| `CreateSnapshot()` | Tạo một snapshot rỗng cho backend này |
| `Save(PhysicsSnapshot into)` | Ghi state hiện tại vào một snapshot |
| `Load(PhysicsSnapshot from)` | Khôi phục một state đã lưu |

Snapshot không biết nó thuộc tick nào; `PhysicsHistory` theo dõi điều đó.

## IPhysicsWorld và IPhysicsWorld2D <a href="#iphysicsworld-and-iphysicsworld2d" id="iphysicsworld-and-iphysicsworld2d"></a>

Cả hai interface đều kế thừa `IPhysicsSimulation`. Chúng tách riêng vì state khác nhau: góc xoay 3D là quaternion, còn góc xoay 2D là một góc.

| Member | 3D | 2D |
|---|---|---|
| Tạo body | `CreateBody(in BodyDesc)` | `CreateBody(in BodyDesc2D)` |
| Gỡ, kiểm tra | `RemoveBody(BodyHandle)`, `Contains(BodyHandle)` | như trên |
| Đọc | `GetBody` trả về `BodyState`, `GetKind`, `GetMass` | `GetBody` trả về `BodyState2D`, `GetKind`, `GetMass` |
| Ghi | `SetBody(BodyHandle, in BodyState)` | `SetBody(BodyHandle, in BodyState2D)` |
| Loại khỏi snapshot | `SetRewindable(BodyHandle, bool)` | như trên |
| Lực | `AddForce`, `AddImpulse` với `Vector3` | với `Vector2` |
| Truy vấn | `Raycast(origin, direction, maxDistance, out RayHit)`, `Overlap(center, radius, BodyHandle[])` | `Raycast(..., out RayHit2D)`, `Overlap(Vector2, float, BodyHandle[])` |

Các interface dùng một tập nhỏ type dữ liệu. `BodyHandle` là một id mờ có `IsValid` là false với giá trị mặc định. `BodyKind` là một trong `Dynamic`, `Kinematic` và `Static`. Các hình dạng là `BodyShape` (`Box`, `Sphere`, `Capsule`, `ConvexHull`, `TriangleMesh`) và `BodyShape2D` (`Box`, `Circle`, `Capsule`, `ConvexPolygon`, `Polyline`). Một `ColliderDesc` hoặc `ColliderDesc2D` đặt một hình dạng kèm `ColliderMaterial`, layer và cờ trigger, còn `BodyDesc` và `BodyDesc2D` mô tả một body mới theo loại, các collider, vị trí, góc xoay, khối lượng và một `BodyMotion` hoặc `BodyMotion2D` (khóa trục, trọng lực, damping). Các type còn lại là `BodyState` và `BodyState2D`, và `RayHit` và `RayHit2D`. [Tham chiếu physics API](../reference/physics.md) liệt kê member của chúng.

`PhysicsBody` và `PhysicsBody2D` bọc một world và một handle, nên code game không phải làm việc với handle.

## PhysicsHistory <a href="#physicshistory" id="physicshistory"></a>

`PhysicsHistory(world, capacity)` giữ snapshot của một world trong một vòng tròn `capacity` tick:

| Member | Ý nghĩa |
|---|---|
| `Save(uint tick)` | Lưu state hiện tại của world cho một tick, dùng lại snapshot của ô đó |
| `Has(uint tick)` | Tick vẫn còn trong vòng tròn |
| `Load(uint tick)` | Khôi phục tick; trả về false khi tick không còn trong vòng tròn |
| `Clear()` | Quên mọi tick |
| `Capacity` | Kích thước vòng tròn |

Client giữ một history cho mỗi world được dự đoán, với Prediction History làm capacity.

## NetworkPhysics <a href="#networkphysics" id="networkphysics"></a>

`NetworkPhysics` là component trừu tượng mà field Physics của `NetworkManager` giữ, và `RigidbodyPhysics` là component package cung cấp. Manager hỏi nó những world nào cần step, một object thuộc world nào, body của một `NetworkObject` và history của một world. `WorldsOf(Scene, List<IPhysicsSimulation>)` trả về các world của một scene, còn các member `AddStatic` và `AddBody` mô tả trong [tổng quan physics](overview.md#geometry-and-bodies-added-at-runtime) thêm geometry và body lúc chạy.

## Các world của Unity <a href="#the-unity-worlds" id="the-unity-worlds"></a>

`UnityPhysicsWorld` và `UnityPhysicsWorld2D` hiện thực các interface trên một physics scene của Unity. `RigidbodyPhysics` tạo chúng cho các scene nó step, và bạn cũng có thể tự tạo một world từ một `Scene` để dùng các interface bên ngoài vòng lặp network, ví dụ trong test.

| Hành vi | 3D | 2D |
|---|---|---|
| `Step` | `PhysicsScene.Simulate(seconds)` | `PhysicsScene2D.Simulate(seconds)` |
| Nội dung snapshot | Mọi `Rigidbody` dynamic không bị loại: vị trí, góc xoay, vận tốc, vận tốc góc, trạng thái ngủ | Như vậy với `Rigidbody2D` |
| `Register(rigidbody)` | Trả về handle của một `Rigidbody` có sẵn | Như vậy với `Rigidbody2D` |
| `CreateBody` | Tạo một GameObject tên `FomoxaBody` có các collider và một `Rigidbody` trong scene đầu tiên đã load của world, và áp các thiết lập chuyển động của body; `Static` tạo body kinematic | Tạo `FomoxaBody2D` có các collider và một `Rigidbody2D`; `Static` tạo body kinematic |
| Đơn vị | Vận tốc góc tính bằng radian mỗi giây | Góc xoay tính bằng radian, vận tốc góc tính bằng radian mỗi giây |

Dữ liệu contact không thuộc snapshot, khiến replay chỉ là gần đúng. Proxy được loại khỏi snapshot bằng `SetRewindable(handle, false)`.

Để biết package dùng các interface này ra sao, xem [tổng quan physics](overview.md). [Tham chiếu physics API](../reference/physics.md) liệt kê mọi member, và [kiến trúc](../concepts/architecture.md) mô tả tổng thể các tầng.
