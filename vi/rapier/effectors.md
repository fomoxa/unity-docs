# Effector

Backend Rapier mô phỏng năm effector 2D của Unity: `PlatformEffector2D`, `SurfaceEffector2D`, `AreaEffector2D`, `BuoyancyEffector2D` và `PointEffector2D`. Chúng chạy bên trong thư viện native, nên server, client dự đoán và replay áp dụng chúng như nhau. Hành vi của chúng đã được đo so với Box2D trong Unity 6000.5 và làm theo Box2D.

## Effector đến từ đâu <a href="#where-effectors-come-from" id="where-effectors-come-from"></a>

Effector tác động qua các collider trên GameObject của nó có bật Used By Effector, như trong Unity. Backend đọc component một lần và không theo các thay đổi sau đó:

| Collider | Lúc được đọc |
|---|---|
| Collider tĩnh của một network scene | Từ scene file, khi scene load. Editor ghi effector vào file cùng collider |
| Collider của body của một network object | Khi `RapierPhysics` dựng body của object. Effector thuộc body đó và mất đi cùng nó |
| Collider dưới một GameObject truyền cho `AddStatic2D(GameObject)` | Khi nhóm được thêm; `RemoveStatic` gỡ effector cùng nhóm |

Effector tĩnh nằm trong scene file, nên hãy xuất lại các network scene file sau khi thêm hoặc đổi một effector. Console server đọc cùng các file đó, nên world của nó có cùng effector.

## Hành vi <a href="#behavior" id="behavior"></a>

Mọi effector chỉ tác động lên body dynamic. Effector trên collider không phải trigger tác động lên các body chạm vào nó, và mỗi body nhận tác động một lần cho mỗi effector, kể cả khi nó chạm nhiều collider của effector đó. Khi bật Use Collider Mask, mask thay ma trận va chạm layer cho các collider của effector, kể cả với va chạm thường. Các truy vấn như `Raycast` thấy collider của effector như mọi collider khác.

### Platform <a href="#platform" id="platform"></a>

Body đi xuyên qua platform một chiều khi đến từ ngoài Surface Arc, đo từ hướng lên của platform cộng Rotational Offset, và bị giữ lại khi đáp xuống từ trong cung đó. Body bắt đầu chạm từ ngoài cung thì tiếp tục đi xuyên cho tới khi rời platform, nên body nhảy từ dưới lên qua platform không bị dừng giữa chừng. Use One Way Grouping cho một tiếp xúc bị chặn của body chặn mọi tiếp xúc của body đó. Tiếp xúc ở cạnh mất ma sát hoặc độ nảy khi tắt Use Side Friction hoặc Use Side Bounce.

[Character controller](character-controller.md) cũng đi xuyên platform một chiều từ dưới lên và đáp lên nó theo cùng cách.

### Surface <a href="#surface" id="surface"></a>

Sau mỗi bước mô phỏng, effector đổi vận tốc dọc bề mặt của mọi body chạm vào nó, về phía Speed, nhân với Force Scale. Khi bật Use Contact Force, thay đổi này được áp dưới dạng xung lực tại điểm tiếp xúc. Tắt Use Friction và Use Bounce thì tiếp xúc mất ma sát và độ nảy.

### Area <a href="#area" id="area"></a>

Lực được tính sau mỗi bước mô phỏng từ các body trong vùng và áp trong bước kế tiếp. Force Angle tính theo thế giới khi bật Use Global Angle, nếu không thì tương đối với góc xoay của effector. Linear Damping và Angular Damping làm chậm body ngay sau bước mô phỏng. Khi Force Target là Collider, lực đặt ở khối tâm của collider đang chạm thay vì khối tâm của body.

### Buoyancy <a href="#buoyancy" id="buoyancy"></a>

Mặt nước là đường nằm ngang ở Surface Level phía trên GameObject của effector. Mỗi body bị đẩy ngược chiều trọng lực tại tâm phần chìm của nó. Lực bằng Density nhân diện tích phần chìm nhân độ lớn của trọng lực, nhân với gravity scale của body. Linear Damping và Angular Damping làm chậm body theo tỉ lệ với diện tích đó. Flow Magnitude và Flow Angle đẩy phần chìm theo phương ngang. Hình tròn, hộp và đa giác lồi được cắt chính xác ở mặt nước. Viên nang được tính như hộp bao của nó.

### Point <a href="#point" id="point"></a>

Lực có độ lớn Force Magnitude theo đường từ nguồn tới body, đổi theo khoảng cách nhân Distance Scale tuỳ Force Mode: không đổi, nghịch đảo tuyến tính hoặc nghịch đảo bình phương. Dưới khoảng cách 1, hai chế độ nghịch đảo dùng 1. Nguồn là vị trí của body mang effector, hoặc tâm của collider mang effector khi Force Source là Collider. Khi Force Target là Collider, lực đặt ở khối tâm của collider đang chạm. Lực được áp trong bước kế tiếp, và damping tác động ngay sau mỗi bước mô phỏng, như với area.

## Phần không được mô phỏng <a href="#what-is-not-simulated" id="what-is-not-simulated"></a>

Speed Variation, Force Variation và Flow Variation là ngẫu nhiên trong Unity. Backend coi chúng bằng 0, và Editor cùng `RapierPhysics` log một cảnh báo cho mỗi component có giá trị khác 0.

## Chênh lệch đo được so với Box2D <a href="#measured-differences-from-box2d" id="measured-differences-from-box2d"></a>

Lực và mô-men khớp Box2D tới bốn hoặc năm chữ số ở các bước đầu. Vị trí lệch khoảng 1% quãng đường đã đi, vì Rapier tích phân vị trí qua nhiều substep mỗi bước; body rơi tự do không có effector cũng lệch như vậy. Với cùng mô-men, viên nang 2D quay chậm hơn dưới Rapier so với Box2D, vì hai engine tính quán tính của nó khác nhau.

## Effector tạo từ code <a href="#effectors-from-code" id="effectors-from-code"></a>

`EffectorDesc2D` mô tả một effector, với một factory cho mỗi loại, nhận các tham số của component Unity, góc theo radian:

| Factory |
|---|
| `Platform(bool oneWay, bool oneWayGrouping, float rotationalOffset, float surfaceArc, bool sideFriction, bool sideBounce, float sideArc)` |
| `Surface(float speed, float forceScale, bool contactForce, bool friction, bool bounce)` |
| `Area(float forceAngle, bool globalAngle, float forceMagnitude, EffectorSelection forceTarget, float linearDamping, float angularDamping)` |
| `Buoyancy(float surfaceLevel, float density, float linearDamping, float angularDamping, float flowAngle, float flowMagnitude)` |
| `Point(float forceMagnitude, float distanceScale, EffectorSelection forceSource, EffectorSelection forceTarget, EffectorForceMode forceMode, float linearDamping, float angularDamping)` |

`EffectorSelection` là `Rigidbody` hoặc `Collider`, còn `EffectorForceMode` là `Constant`, `InverseLinear` hoặc `InverseSquared`.

`WithFrame(Vector2 origin, float rotation)` đặt effector trong khung của body mang nó, hoặc trong toạ độ thế giới với nhóm tĩnh, còn `WithColliderMask(uint? mask)` đặt collider mask; `null` là dùng ma trận va chạm layer.

| Member | Thêm effector vào |
|---|---|
| `RapierScenes.AddEffector(INetworkEntity owner, PhysicsBody2D body, IReadOnlyList<int> colliders, in EffectorDesc2D desc)` | Một body của network object hoặc của entity console |
| `RapierScenes.AddEffector(StaticGroup group, IReadOnlyList<int> colliders, in EffectorDesc2D desc)` | Một nhóm tĩnh do `RapierScenes.AddStatic2D` trả về |
| `RapierScenes.AddEffector(PhysicsBody2D body, IReadOnlyList<int> colliders, in EffectorDesc2D desc)` | Một body không network object nào sở hữu, như một bục di chuyển |

`colliders` là chỉ số trong danh sách collider của mô tả body hoặc của nhóm. Mỗi lời gọi trả về một `EffectorHandle`. `RapierWorld2D.SetEffector(handle, desc)` đổi mô tả và giữ các collider, `RemoveEffector(handle)` gỡ effector, và gỡ body hay nhóm thì gỡ cả effector của nó. Collider đã có effector, chỉ số ngoài phạm vi hoặc mô tả không hợp lệ đều ném `ArgumentException`.

## Effector khi replay <a href="#effectors-in-a-replay" id="effectors-in-a-replay"></a>

Snapshot giữ các effector cùng mô tả của chúng. Khi client nạp một tick cũ, effector có từ lúc đó lấy mô tả của tick đó, effector thêm sau giữ mô tả hiện tại, và effector gỡ sau vẫn bị gỡ, như với [joint](joints.md#joints-in-a-replay). Hãy thêm và đổi effector trong prediction callback và tick event, theo cùng thứ tự trên mọi peer.
