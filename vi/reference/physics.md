# Tham chiếu Physics API

Trừ khi có ghi chú khác, các type trên trang này nằm trong namespace `Fomoxa.Unity.Simulation` và assembly `Fomoxa.Unity.Core`, và vector cùng quaternion của chúng là các type `System.Numerics`. Các hướng dẫn [tổng quan physics](../physics/overview.md), [PhysicsBody](../physics/physics-body.md) và [kiến trúc physics](../physics/architecture.md) giải thích cách dùng chúng.

## PhysicsBody <a href="#physicsbody" id="physicsbody"></a>

`public readonly struct PhysicsBody`, với constructor `PhysicsBody(IPhysicsWorld world, BodyHandle handle)`.

| Member | Type | Mô tả |
|---|---|---|
| `IsValid` | `bool` | World tồn tại và chứa body |
| `Position` | `Vector3` | Đọc và ghi |
| `Rotation` | `Quaternion` | Đọc và ghi |
| `Velocity` | `Vector3` | Đọc và ghi; chỉ được ghi vào body dynamic |
| `AngularVelocity` | `Vector3` | Radian mỗi giây. Đọc và ghi; chỉ được ghi vào body dynamic. |
| `Mass` | `float` | |
| `IsKinematic` | `bool` | |
| `State` | `BodyState` | Đọc và ghi cả bốn giá trị cùng lúc |
| `AddForce(Vector3 force)` | `void` | Lực trong bước tiếp theo |
| `AddImpulse(Vector3 impulse)` | `void` | Thay đổi vận tốc bằng `impulse / Mass`; body kinematic bỏ qua |

## PhysicsBody2D <a href="#physicsbody2d" id="physicsbody2d"></a>

`public readonly struct PhysicsBody2D`, với constructor `PhysicsBody2D(IPhysicsWorld2D world, BodyHandle handle)`. Nó có cùng các member như `PhysicsBody`, nhưng với vị trí và vận tốc `Vector2`, góc xoay `float` tính bằng radian, vận tốc góc `float` tính bằng radian mỗi giây, và `BodyState2D`.

## Type state <a href="#state-types" id="state-types"></a>

| Type | Field |
|---|---|
| `public struct BodyState` | `Vector3 Position`, `Quaternion Rotation`, `Vector3 Velocity`, `Vector3 AngularVelocity` |
| `public struct BodyState2D` | `Vector2 Position`, `float Rotation`, `Vector2 Velocity`, `float AngularVelocity` |

## Interface <a href="#interfaces" id="interfaces"></a>

```csharp
public interface IPhysicsSimulation
{
    PhysicsBackend Backend { get; }
    void Step(float seconds);
    PhysicsSnapshot CreateSnapshot();
    void Save(PhysicsSnapshot into);
    void Load(PhysicsSnapshot from);
}
```

`IPhysicsWorld : IPhysicsSimulation` thêm các member sau:

| Member | Mô tả |
|---|---|
| `BodyHandle CreateBody(in BodyDesc desc)` | Tạo một body |
| `bool RemoveBody(BodyHandle body)` | Gỡ một body; false khi không biết |
| `bool Contains(BodyHandle body)` | Body có tồn tại hay không |
| `BodyState GetBody(BodyHandle body)`, `void SetBody(BodyHandle body, in BodyState state)` | Đọc và ghi state |
| `BodyKind GetKind(BodyHandle body)`, `float GetMass(BodyHandle body)` | Loại và khối lượng |
| `void SetRewindable(BodyHandle body, bool rewindable)` | Đưa body vào hoặc loại khỏi snapshot |
| `void AddForce(BodyHandle body, Vector3 force)`, `void AddImpulse(BodyHandle body, Vector3 impulse)` | Lực |
| `bool Raycast(Vector3 origin, Vector3 direction, float maxDistance, out RayHit hit)` | Điểm chạm đầu tiên dọc theo tia |
| `int Overlap(Vector3 center, float radius, BodyHandle[] results)` | Các body chồng lên một hình cầu; trả về số body đã ghi |

`IPhysicsWorld2D : IPhysicsSimulation` có cùng các member với `BodyDesc2D`, `BodyState2D`, `Vector2` và `RayHit2D`, và `Overlap` của nó kiểm tra một hình tròn.

## Type dữ liệu <a href="#data-types" id="data-types"></a>

| Type | Member |
|---|---|
| `public enum PhysicsBackend : byte` | `Rigidbody = 1`, `Rapier = 2` (chưa hiện thực) |
| `public enum BodyKind` | `Dynamic`, `Kinematic`, `Static` |
| `public readonly struct BodyHandle` | `int Value`, `bool IsValid` (false với 0) |
| `public readonly struct BodyShape` | `Box(Vector3 halfExtents)`, `Sphere(float radius)`, `Capsule(float radius, float halfHeight)`; `Kind`, `HalfExtents`, `Radius`, `HalfHeight` |
| `public readonly struct BodyShape2D` | `Box(Vector2 halfExtents)`, `Circle(float radius)`, `Capsule(float radius, float halfHeight)` |
| `public readonly struct BodyDesc` | `BodyDesc(BodyKind kind, BodyShape shape, Vector3 position, Quaternion rotation, float mass)` |
| `public readonly struct BodyDesc2D` | `BodyDesc2D(BodyKind kind, BodyShape2D shape, Vector2 position, float rotation, float mass)` |
| `public readonly struct RayHit` | `BodyHandle Body`, `Vector3 Point`, `Vector3 Normal`, `float Distance` |
| `public readonly struct RayHit2D` | `BodyHandle Body`, `Vector2 Point`, `Vector2 Normal`, `float Distance` |
| `public abstract class PhysicsSnapshot` | Base class của snapshot của một backend |

`HalfHeight` của capsule là một nửa khoảng cách giữa tâm hai hình cầu ở hai đầu.

## PhysicsHistory <a href="#physicshistory" id="physicshistory"></a>

`public sealed class PhysicsHistory`, với constructor `PhysicsHistory(IPhysicsSimulation world, int capacity)`, trong đó capacity tối thiểu là 1.

| Member | Mô tả |
|---|---|
| `int Capacity` | Kích thước vòng tròn |
| `void Save(uint tick)` | Lưu world cho một tick |
| `bool Has(uint tick)` | Tick có trong vòng tròn hay không |
| `bool Load(uint tick)` | Khôi phục tick; false khi không có |
| `void Clear()` | Quên mọi tick |

## Backend Unity <a href="#unity-backend" id="unity-backend"></a>

`UnityPhysicsWorld : IPhysicsWorld` và `UnityPhysicsWorld2D : IPhysicsWorld2D` nằm trong `Fomoxa.Unity`.

| Member | Mô tả |
|---|---|
| Constructor `(Scene scene)` | Một world cho physics scene của scene; ném exception với scene không hợp lệ |
| `PhysicsScene` | `PhysicsScene` hoặc `PhysicsScene2D` của Unity |
| `Scenes` | Các scene Unity dùng world này |
| `Register(Rigidbody)` / `Register(Rigidbody2D)` | Handle của một body có sẵn |
| `Backend` | Luôn là `PhysicsBackend.Rigidbody` |

`NetworkObject.Body` và `Body2D` được liệt kê trong [tham chiếu NetworkObject](network-object.md), còn các field physics của `NetworkManager` trong [cấu hình](configuration.md#networkmanager).
