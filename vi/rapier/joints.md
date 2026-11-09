# Joint

Joint nối hai body của một network object với nhau, hoặc nối một body với thế giới. Backend Rapier đọc các component joint của Unity khi dựng body của network object, và code game cũng tự tạo được joint qua các world. Joint là một phần của world Rapier, nên snapshot lưu chúng và replay khôi phục chúng cùng các body.

## Component joint <a href="#joint-components" id="joint-components"></a>

`RapierPhysics` đọc các component joint trên mọi body của một network object, sau khi đã dựng xong mọi [body](bodies.md#several-bodies) của object:

| Component | Thành |
|---|---|
| `FixedJoint`, `FixedJoint2D` | Joint cố định. `FixedJoint2D` có frequency lớn hơn 0 thì mềm |
| `HingeJoint`, `HingeJoint2D` | Joint quay, với giới hạn và motor của component. Spring của `HingeJoint` thành motor vị trí |
| `SliderJoint2D` | Joint trượt theo góc của component, với giới hạn và motor của nó |
| `CharacterJoint` | Joint cầu, với giới hạn xoắn và hai giới hạn swing |
| `SpringJoint` | Lò xo có độ dài nghỉ bằng Max Distance cộng Tolerance, cùng Spring và Damper |
| `SpringJoint2D` | Lò xo với distance, frequency và damping ratio của component. Frequency bằng 0 thì giữ khoảng cách cố định |
| `DistanceJoint2D` | Dây có độ dài bằng distance của component; tắt Max Distance Only thì khoảng cách được giữ cố định |

Anchor, connected anchor (hoặc Auto Configure Connected Anchor) và Enable Collision áp dụng như trong Unity. Connected Body phải để trống, tức là nối body với thế giới, hoặc là một `Rigidbody` của cùng network object. Joint nối sang network object khác log `the connected body is not a body of the same NetworkObject` và không được dựng.

Các trường hợp sau được báo trong Console, mỗi component một lần cho mỗi lần dựng object:

| Trường hợp | Kết quả |
|---|---|
| `ConfigurableJoint`, `WheelJoint2D`, `RelativeJoint2D`, `TargetJoint2D`, `FrictionJoint2D` và các loại joint khác | Lỗi `is not supported under Rapier`; không có joint |
| Break Force hoặc Break Torque hữu hạn | Lỗi `Rapier joints do not break`; joint vẫn được dựng và không bao giờ gãy |
| Tham số mà backend bỏ qua, theo bảng dưới | Một cảnh báo nêu tên các tham số |

| Component | Bị bỏ qua khi khác mặc định của Unity |
|---|---|
| Mọi joint 3D | Mass Scale, Connected Mass Scale, Enable Preprocessing |
| `HingeJoint` | Độ nảy của giới hạn, Free Spin của motor, và Use Spring cùng Use Motor (motor được dùng) |
| `SpringJoint` | Min Distance |
| `CharacterJoint` | Độ nảy và lò xo của giới hạn, Enable Projection |

Joint chỉ được đọc một lần, khi dựng object. Đổi component joint sau đó không có tác dụng; hãy đổi joint qua world.

## Joint tạo từ code <a href="#joints-from-code" id="joints-from-code"></a>

`RapierWorld.CreateJoint(BodyHandle a, BodyHandle b, in JointDesc desc)` và `RapierWorld2D.CreateJoint` với `JointDesc2D` tạo một joint và trả về `JointHandle` của nó. `b` là `default(BodyHandle)` thì `a` được nối với thế giới. `SetJoint(handle, desc)` thay mô tả của joint và giữ hai body của nó, `RemoveJoint(handle)` gỡ joint, và gỡ một body thì gỡ cả các joint của body đó.

`JointDesc` đặt joint trong không gian cục bộ của từng body: một điểm neo và một khung có trục X là trục chính của joint. Góc tính theo radian, độ dài theo mét.

| Member | Mô tả |
|---|---|
| `JointDesc(JointKind kind, Vector3 anchorA, Quaternion frameA, Vector3 anchorB, Quaternion frameB)` | `Fixed`, `Revolute`, `Prismatic` hoặc `Spherical`. `JointDesc2D` nhận điểm neo `Vector2` và góc, không có `Spherical` |
| `JointDesc.Rope(anchorA, anchorB, maxLength)` | Dây giữ khoảng cách không quá `maxLength` |
| `JointDesc.Spring(anchorA, anchorB, restLength, stiffness, damping)` | Lò xo kéo về `restLength` |
| `WithLimit(JointLimit)` | Khoảng góc của joint quay, khoảng cách của joint trượt, độ xoắn của joint cầu, hoặc khoảng độ dài của dây |
| `WithSwingLimits(JointLimit y, JointLimit z)` | Swing của joint cầu |
| `WithMotor(JointMotorDesc)` | Motor trên joint quay hoặc joint trượt |
| `WithSoftness(JointSoftness)` | Ràng buộc mềm với frequency và damping ratio |
| `WithLength(float)`, `WithContacts(bool)` | Độ dài của dây hoặc lò xo, và hai body còn va chạm nhau hay không |

`JointMotorDesc.Velocity(targetVelocity, damping, maxForce)` đẩy về một vận tốc, `JointMotorDesc.Position(targetPosition, stiffness, damping, maxForce)` đẩy về một vị trí. Lực của motor là `stiffness · (targetPosition − x) + damping · (targetVelocity − v)`, chặn ở `maxForce`. Kiểu này tên là `JointMotorDesc` để không trùng `UnityEngine.JointMotor` trong tệp dùng cả hai namespace.

Một cánh cửa quay trên bản lề trong khoảng 0 tới 100 độ và tự đóng lại:

```csharp
using System;
using System.Numerics;
using Fomoxa.Networking.Rapier;
using Fomoxa.Networking.Simulation;

PhysicsBody door = networkObject.Body;
var hinge = new JointDesc(JointKind.Revolute, new Vector3(-0.5f, 0f, 0f), Quaternion.CreateFromAxisAngle(Vector3.UnitZ, MathF.PI / 2f), hingePoint, Quaternion.CreateFromAxisAngle(Vector3.UnitZ, MathF.PI / 2f))
    .WithLimit(new JointLimit(0f, 100f * MathF.PI / 180f))
    .WithMotor(JointMotorDesc.Position(0f, 40f, 4f, 200f));
JointHandle joint = rapier.Scenes.CreateJoint(networkObject, door, default, hinge);
```

`rapier` là component `RapierPhysics` của `NetworkManager`. Body thứ hai là thế giới, nên `hingePoint` là bản lề theo toạ độ thế giới. Cả hai khung xoay trục X của joint thành trục đứng, nên cửa quay quanh trục đó. `RapierScenes.CreateJoint(INetworkEntity owner, PhysicsBody a, PhysicsBody b, in JointDesc desc)` kiểm tra `a` là body của `owner` và gắn joint vào body đó, nên joint mất đi cùng object. Đổi hoặc gỡ joint sau đó qua `rapier.Scenes.WorldOf(sceneId)`. Console server gọi cùng hàm với `StandaloneEntity` của nó.

## Joint khi replay <a href="#joints-in-a-replay" id="joints-in-a-replay"></a>

Snapshot giữ mọi joint cùng mô tả và trạng thái của bộ giải. Khi client nạp một tick cũ:

- joint có trong snapshot và vẫn còn tới giờ lấy mô tả và trạng thái của snapshot, nên một `SetJoint` gọi sau tick đó bị huỷ;
- joint tạo sau tick đó được giữ với mô tả hiện tại, và bắt đầu lại mà không có trạng thái bộ giải của các bước trước;
- joint gỡ sau tick đó vẫn bị gỡ.

Hãy tạo và đổi joint trong prediction callback và tick event, theo cùng thứ tự trên mọi peer, như [tính tất định](determinism.md) mô tả.
