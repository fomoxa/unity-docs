# PhysicsBody

`PhysicsBody` và `PhysicsBody2D` là cách package nhìn vào physics body của một network object, và bạn dùng chúng trong `apply`, `capture` và `restore` để đọc và thay đổi body. Chúng làm việc với vector `System.Numerics` và không phụ thuộc vào API `Rigidbody` của Unity.

```csharp
using Fomoxa.Networking.Simulation;
using Fomoxa.Unity;

PhysicsBody body = NetworkObject.Body;
PhysicsBody2D body2D = NetworkObject.Body2D;
```

Cả hai là struct nhỏ, nên hãy lấy mới mỗi khi cần thay vì giữ chúng qua các lần spawn.

## Khi nào hợp lệ <a href="#when-it-is-valid" id="when-it-is-valid"></a>

`IsValid` là true khi hai điều kiện cùng đúng: object có `Rigidbody` (với `Body`) hoặc `Rigidbody2D` (với `Body2D`) trên cùng GameObject với `NetworkObject`, và object đã spawn ở phía này. Đọc hoặc ghi một body không hợp lệ sẽ ném exception.

## PhysicsBody (3D) <a href="#physicsbody-3d" id="physicsbody-3d"></a>

| Member | Type | Ý nghĩa |
|---|---|---|
| `Position` | `Vector3` | Vị trí world |
| `Rotation` | `Quaternion` | Góc xoay world |
| `Velocity` | `Vector3` | Vận tốc thẳng |
| `AngularVelocity` | `Vector3` | Vận tốc góc, radian mỗi giây |
| `Mass` | `float` | Khối lượng |
| `IsKinematic` | `bool` | Body là kinematic |
| `State` | `BodyState` | Vị trí, góc xoay, vận tốc và vận tốc góc cùng lúc |
| `AddForce(Vector3 force)` | | Một lực, tác dụng trong bước tiếp theo |
| `AddImpulse(Vector3 impulse)` | | Thay đổi vận tốc tức thời bằng `impulse / Mass`; bị bỏ qua với body kinematic |

## PhysicsBody2D <a href="#physicsbody2d" id="physicsbody2d"></a>

| Member | Type | Ý nghĩa |
|---|---|---|
| `Position` | `Vector2` | Vị trí world |
| `Rotation` | `float` | Góc xoay tính bằng radian |
| `Velocity` | `Vector2` | Vận tốc thẳng |
| `AngularVelocity` | `float` | Vận tốc góc, radian mỗi giây |
| `Mass` | `float` | Khối lượng |
| `IsKinematic` | `bool` | Body là kinematic |
| `State` | `BodyState2D` | Vị trí, góc xoay, vận tốc và vận tốc góc cùng lúc |
| `AddForce(Vector2 force)` | | Một lực, tác dụng trong bước tiếp theo |
| `AddImpulse(Vector2 impulse)` | | Thay đổi vận tốc tức thời bằng `impulse / Mass`; bị bỏ qua với body không phải dynamic |

`Vector2`, `Vector3` và `Quaternion` ở đây là các type `System.Numerics`.

## Đọc và ghi state <a href="#reading-and-writing-state" id="reading-and-writing-state"></a>

Mỗi setter của property đọc toàn bộ state, đổi một phần rồi ghi lại, nên để đổi nhiều phần, hãy đi qua `State` một lần:

```csharp
PhysicsBody body = NetworkObject.Body;
BodyState state = body.State;
state.Position = new System.Numerics.Vector3(0f, 2f, 0f);
state.Velocity = System.Numerics.Vector3.Zero;
body.State = state;
```

Ghi state sẽ di chuyển body và transform của nó ngay lập tức và đánh thức body. Vận tốc và vận tốc góc chỉ được ghi vào body dynamic.

## Lực và xung lực <a href="#forces-and-impulses" id="forces-and-impulses"></a>

```csharp
private void Apply(MoveInput input, InputContext context)
{
    PhysicsBody body = NetworkObject.Body;
    body.AddForce(new System.Numerics.Vector3(input.X, 0f, input.Z) * moveForce);
    if (input.Jump && !context.Repeated)
    {
        body.AddImpulse(new System.Numerics.Vector3(0f, jumpImpulse, 0f));
    }
}
```

Lực thay đổi vận tốc trong bước physics tiếp theo, bước mà `NetworkManager` chạy trong cùng tick sau input, còn xung lực thay đổi vận tốc ngay lập tức.

## Teleport <a href="#teleporting" id="teleporting"></a>

Để di chuyển tức thời một body trên server, hãy ghi vị trí của nó và báo client không interpolate:

```csharp
PhysicsBody body = NetworkObject.Body;
BodyState state = body.State;
state.Position = respawnPoint;
state.Velocity = System.Numerics.Vector3.Zero;
body.State = state;
GetComponent<NetworkTransform>().Teleport();
```

Ở đây `respawnPoint` là một `System.Numerics.Vector3`. [NetworkTransform](../synchronization/transform.md#teleporting) mô tả `Teleport()` làm gì trên client.

[Tổng quan physics](overview.md) giải thích khi nào body được step, [tham chiếu physics API](../reference/physics.md) liệt kê mọi member, và [rollback với physics](../prediction/rollback.md) cho thấy body trong một object được dự đoán.
