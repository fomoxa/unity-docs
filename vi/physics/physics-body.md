# NetworkBody

`NetworkBody` và `NetworkBody2D` là cách package nhìn vào physics body của một network object. Bạn dùng chúng trong `OnApplyInput`, `OnCaptureState` và `OnRestoreState` để đọc và thay đổi body. Chúng nhận và trả `Vector3`, `Vector2` và `Quaternion` của Unity, và chạy như nhau với `RigidbodyPhysics` lẫn [backend Rapier](../rapier/overview.md).

```csharp
using Fomoxa.Unity;

NetworkBody body = NetworkObject.Body;
NetworkBody2D body2D = NetworkObject.Body2D;
```

Cả hai là struct nhỏ, nên hãy lấy mới mỗi khi cần thay vì giữ chúng qua các lần spawn.

## Khi nào hợp lệ <a href="#when-it-is-valid" id="when-it-is-valid"></a>

`IsValid` là true khi hai điều kiện cùng đúng. Object có `Rigidbody` (với `Body`) hoặc `Rigidbody2D` (với `Body2D`) trên cùng GameObject với `NetworkObject`, và object đã spawn ở phía này. Đọc hoặc ghi một body không hợp lệ sẽ ném exception.

Một giá trị `NetworkBody` lấy trước khi object [chuyển sang bản khác](../objects/scenes.md#move-an-object-to-another-instance) sẽ không hợp lệ sau đó, vì lần chuyển dựng lại body trong world của bản mới. Hãy đọc lại `Body` sau lần chuyển.

`Body` và `Body2D` là body trên GameObject của `NetworkObject`. Object có nhiều body liệt kê tất cả trong `NetworkObject.Bodies` và `Bodies2D`, như mục [nhiều body](overview.md#several-bodies) mô tả.

## NetworkBody (3D) <a href="#networkbody-3d" id="networkbody-3d"></a>

| Member | Type | Ý nghĩa |
|---|---|---|
| `Position` | `Vector3` | Vị trí world |
| `Rotation` | `Quaternion` | Góc xoay world |
| `Velocity` | `Vector3` | Vận tốc thẳng |
| `AngularVelocity` | `Vector3` | Vận tốc góc, radian mỗi giây |
| `Mass` | `float` | Khối lượng |
| `IsKinematic` | `bool` | Body là kinematic |
| `State` | `NetworkBodyState` | Vị trí, góc xoay, vận tốc và vận tốc góc cùng lúc |
| `AddForce(Vector3 force)` | | Một lực, tác dụng trong bước tiếp theo |
| `AddImpulse(Vector3 impulse)` | | Thay đổi vận tốc tức thời bằng `impulse / Mass`; bị bỏ qua với body kinematic |
| `AddTorque(Vector3 torque)` | | Mô-men theo các trục thế giới, tác dụng trong bước tiếp theo |
| `AddTorqueImpulse(Vector3 torqueImpulse)` | | Thay đổi vận tốc góc tức thời qua quán tính của body |
| `AddForceAtPoint(Vector3 force, Vector3 point)` | | Lực tại một điểm thế giới: lực cộng mô-men nó gây ra quanh khối tâm, trong bước tiếp theo |
| `AddImpulseAtPoint(Vector3 impulse, Vector3 point)` | | Xung lực tại một điểm thế giới, đổi vận tốc và vận tốc góc ngay lập tức |
| `GetContactPoints(BodyHandle other, List<NetworkContactPoint> into)` | `int` | Chỗ body chạm `other` sau bước mô phỏng gần nhất; xem [điểm tiếp xúc](queries.md#contact-points) |
| `Handle` | `BodyHandle` | Handle của body trong world của nó, dùng cho bộ lọc truy vấn và điểm tiếp xúc |
| `Core` | `PhysicsBody` | Cùng body đó với type `System.Numerics`, cho code dùng chung với [server console](../console-server/overview.md) |

## NetworkBody2D <a href="#networkbody2d" id="networkbody2d"></a>

| Member | Type | Ý nghĩa |
|---|---|---|
| `Position` | `Vector2` | Vị trí world |
| `Rotation` | `float` | Góc xoay tính bằng radian |
| `Velocity` | `Vector2` | Vận tốc thẳng |
| `AngularVelocity` | `float` | Vận tốc góc, radian mỗi giây |
| `Mass` | `float` | Khối lượng |
| `IsKinematic` | `bool` | Body là kinematic |
| `State` | `NetworkBodyState2D` | Vị trí, góc xoay, vận tốc và vận tốc góc cùng lúc |
| `AddForce(Vector2 force)` | | Một lực, tác dụng trong bước tiếp theo |
| `AddImpulse(Vector2 impulse)` | | Thay đổi vận tốc tức thời bằng `impulse / Mass`; bị bỏ qua với body không phải dynamic |
| `AddTorque(float torque)` | | Mô-men, dương là ngược chiều kim đồng hồ, tác dụng trong bước tiếp theo |
| `AddTorqueImpulse(float torqueImpulse)` | | Thay đổi vận tốc góc tức thời |
| `AddForceAtPoint(Vector2 force, Vector2 point)`, `AddImpulseAtPoint(Vector2 impulse, Vector2 point)` | | Như ở 3D |
| `GetContactPoints(BodyHandle other, List<NetworkContactPoint2D> into)` | `int` | Chỗ body chạm `other` sau bước mô phỏng gần nhất |
| `Handle`, `Core` | `BodyHandle`, `PhysicsBody2D` | Như ở 3D |

## Đọc và ghi state <a href="#reading-and-writing-state" id="reading-and-writing-state"></a>

Mỗi setter của property đọc toàn bộ state, đổi một phần rồi ghi lại, nên để đổi nhiều phần, hãy đi qua `State` một lần:

```csharp
NetworkBody body = NetworkObject.Body;
NetworkBodyState state = body.State;
state.Position = new Vector3(0f, 2f, 0f);
state.Velocity = Vector3.zero;
body.State = state;
```

`NetworkBodyState` có bốn trường ghi được: `Position`, `Rotation`, `Velocity` và `AngularVelocity`. `NetworkBodyState2D` có vị trí và vận tốc kiểu `Vector2`, góc xoay và vận tốc góc kiểu `float`.

Ghi state sẽ di chuyển body và transform của nó ngay lập tức và đánh thức body. Vận tốc và vận tốc góc chỉ được ghi vào body dynamic.

## Lực và xung lực <a href="#forces-and-impulses" id="forces-and-impulses"></a>

```csharp
protected override void OnApplyInput(InputContext context)
{
    NetworkBody body = NetworkObject.Body;
    body.AddForce(new Vector3(x, 0f, z) * moveForce);
    if (jump && !context.Repeated)
    {
        body.AddImpulse(new Vector3(0f, jumpImpulse, 0f));
    }
}
```

Lực thay đổi vận tốc trong bước physics tiếp theo, bước mà `NetworkManager` chạy trong cùng tick sau input. Xung lực thay đổi vận tốc ngay lập tức. Mô-men theo cùng quy tắc: `AddTorque` và `AddForceAtPoint` tác dụng trong bước tiếp theo, `AddTorqueImpulse` và `AddImpulseAtPoint` tác dụng ngay. Cả bốn không làm gì với body kinematic, đánh thức body đang ngủ, và ném `ArgumentException` với body không có trong world.

```csharp
NetworkBody body = NetworkObject.Body;
body.AddForceAtPoint(new Vector3(0f, 0f, thrust), body.Position + new Vector3(wingOffset, 0f, 0f));
```

Trên trục bị khoá, backend Rapier bỏ xung lực ngay lúc gọi, còn PhysX và Box2D bỏ nó chậm nhất trong bước tiếp theo. Sau bước đó hai backend như nhau.

## Code dùng chung với server console <a href="#code-shared-with-the-console-server" id="code-shared-with-the-console-server"></a>

[Server console](../console-server/overview.md) không có type của Unity, nên một thư viện mô phỏng chạy ở cả hai phía dùng `PhysicsBody` và `BodyState` trong `Fomoxa.Networking.Simulation`, với vector `System.Numerics`. `body.Core` đưa cho code như vậy body của một `NetworkBody`. Ở đây `MoveRules.Apply(PhysicsBody body, float x, float z)` là đại diện cho một method của thư viện đó:

```csharp
MoveRules.Apply(NetworkObject.Body.Core, x, z);
```

Để xem một `PhysicsBody` bạn đã có dưới dạng `NetworkBody`, ví dụ body do `NetworkPhysics.AddBody` trả về, hãy tạo nó: `new NetworkBody(physics.AddBody(scene, desc))`.

## Va chạm liên tục <a href="#continuous-collision" id="continuous-collision"></a>

Body chạy nhanh có thể xuyên qua collider mỏng giữa hai bước mô phỏng. `BodyMotion.ContinuousCollision` và `BodyMotion2D.ContinuousCollision` yêu cầu backend dùng cách dò va chạm liên tục mạnh nhất nó có cho body. `BodyDescriptions` đặt cờ này từ trường Collision Detection: mọi chế độ khác Discrete trên `Rigidbody`, và Continuous trên `Rigidbody2D`.

| Backend | Tắt | Bật |
|---|---|---|
| `RigidbodyPhysics` 3D | `Discrete` | `ContinuousDynamic` với body dynamic, `ContinuousSpeculative` với body kinematic |
| `RigidbodyPhysics` 2D | `Discrete` | `Continuous` |
| Rapier | Body dynamic chạy nhanh vẫn quét với collider tĩnh, nhưng có thể xuyên body kinematic và body dynamic | Quét thêm với body kinematic và body dynamic, trừ body khác cũng bật cờ |

Vì vậy, khi tắt cờ, body chạy nhanh dừng ở bức tường tĩnh mỏng dưới Rapier và có thể xuyên qua nó dưới `RigidbodyPhysics`. Server và các client dùng cùng backend, nên điều này không gây sửa lệch.

## Teleport <a href="#teleporting" id="teleporting"></a>

Để di chuyển tức thời một body trên server, hãy ghi vị trí của nó và báo client không interpolate:

```csharp
NetworkBody body = NetworkObject.Body;
NetworkBodyState state = body.State;
state.Position = respawnPoint;
state.Velocity = Vector3.zero;
body.State = state;
GetComponent<NetworkTransform>().Teleport();
```

[NetworkTransform](../synchronization/transform.md#teleporting) mô tả `Teleport()` làm gì trên client.

[Tổng quan physics](overview.md) giải thích khi nào body được step, [tham chiếu physics API](../reference/physics.md) liệt kê mọi member, và [rollback với physics](../prediction/rollback.md) cho thấy body trong một object được dự đoán.
