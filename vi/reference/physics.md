# Tham chiếu Physics API

Trừ khi có ghi chú khác, các type trên trang này nằm trong namespace `Fomoxa.Networking.Simulation` và assembly `Fomoxa.Networking`, và vector cùng quaternion của chúng là các type `System.Numerics`. Các hướng dẫn [tổng quan physics](../physics/overview.md), [PhysicsBody](../physics/physics-body.md) và [kiến trúc physics](../physics/architecture.md) giải thích cách dùng chúng.

## PhysicsBody <a href="#physicsbody" id="physicsbody"></a>

`public readonly struct PhysicsBody`, với constructor `PhysicsBody(IPhysicsWorld world, BodyHandle handle)`.

| Member | Type | Mô tả |
|---|---|---|
| `IsValid` | `bool` | World tồn tại và chứa body |
| `Handle` | `BodyHandle` | Handle của body trong world của nó |
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
| `public enum PhysicsBackend : byte` | `Rigidbody = 1`, `Rapier = 2`; [backend Rapier](../rapier/overview.md) là một package riêng |
| `public enum BodyKind` | `Dynamic`, `Kinematic`, `Static` |
| `public readonly struct BodyHandle` | `int Value`, `bool IsValid` (false với 0) |
| `public readonly struct BodyShape` | `Box(Vector3 halfExtents)`, `Sphere(float radius)`, `Capsule(float radius, float halfHeight)`, `ConvexHull(IReadOnlyList<Vector3> points)` (tối thiểu 4 điểm), `TriangleMesh(IReadOnlyList<Vector3> vertices, IReadOnlyList<int> triangles)`; `Kind`, `HalfExtents`, `Radius`, `HalfHeight`, `Points`, `Triangles` |
| `public readonly struct BodyShape2D` | `Box(Vector2 halfExtents)`, `Circle(float radius)`, `Capsule(float radius, float halfHeight)`, `ConvexPolygon(IReadOnlyList<Vector2> points)` (tối thiểu 3 điểm), `Polyline(IReadOnlyList<Vector2> points)` (tối thiểu 2 điểm, chỉ dùng cho geometry tĩnh) |
| `public enum CombineRule` | `Average`, `Minimum`, `Multiply`, `Maximum`, `Mean` |
| `public readonly struct ColliderMaterial` | `ColliderMaterial(float friction, float restitution, CombineRule frictionCombine, CombineRule restitutionCombine)`; `Default` có friction 0.6, restitution 0, cả hai `Average` |
| `public readonly struct ColliderDesc` | `ColliderDesc(BodyShape shape, Vector3 position, Quaternion rotation, ColliderMaterial material, int layer, bool isTrigger)`; vị trí và góc xoay tính tương đối với body |
| `public readonly struct ColliderDesc2D` | `ColliderDesc2D(BodyShape2D shape, Vector2 position, float rotation, ColliderMaterial material, int layer, bool isTrigger)` |
| `[Flags] public enum BodyLocks` | `None`, `PositionX`, `PositionY`, `PositionZ`, `RotationX`, `RotationY`, `RotationZ` |
| `[Flags] public enum BodyLocks2D` | `None`, `PositionX`, `PositionY`, `Rotation` |
| `public readonly struct BodyMotion` | `BodyMotion(BodyLocks locks, bool useGravity, float linearDamping, float angularDamping)`; `Default` không khóa trục, bật trọng lực, không damping |
| `public readonly struct BodyMotion2D` | `BodyMotion2D(BodyLocks2D locks, float gravityScale, float linearDamping, float angularDamping)`; `Default` không khóa trục, gravity scale 1, không damping |
| `public readonly struct BodyDesc` | `BodyDesc(BodyKind kind, BodyShape shape, Vector3 position, Quaternion rotation, float mass)`, và các constructor nhận `IReadOnlyList<ColliderDesc> colliders` thay cho một hình dạng, có thể kèm `in BodyMotion motion` ở cuối |
| `public readonly struct BodyDesc2D` | Tương tự với `BodyShape2D`, `ColliderDesc2D`, `Vector2`, góc xoay `float` và `BodyMotion2D` |
| `public readonly struct StaticGroup` | `uint SceneId`, `int Id`, `int FirstIndex`, `int Count`, `bool IsValid` (false với giá trị mặc định); một nhóm collider tĩnh thêm lúc chạy |
| `public readonly struct RayHit` | `BodyHandle Body`, `Vector3 Point`, `Vector3 Normal`, `float Distance` |
| `public readonly struct RayHit2D` | `BodyHandle Body`, `Vector2 Point`, `Vector2 Normal`, `float Distance` |
| `public abstract class PhysicsSnapshot` | Class cơ sở cho snapshot của một backend |

`HalfHeight` của capsule là một nửa khoảng cách giữa tâm hai hình cầu ở hai đầu.

## PhysicsHistory <a href="#physicshistory" id="physicshistory"></a>

`public sealed class PhysicsHistory`, với constructor `PhysicsHistory(IPhysicsSimulation world, int capacity)`, trong đó capacity tối thiểu là 1.

| Member | Mô tả |
|---|---|
| `int Capacity` | Kích thước vòng |
| `void Save(uint tick)` | Lưu world cho một tick |
| `bool Has(uint tick)` | Tick có trong vòng hay không |
| `bool Load(uint tick)` | Khôi phục tick; false khi không có |
| `void Clear()` | Quên mọi tick |

`PhysicsHistories` giữ một `PhysicsHistory` cho mỗi world: `PhysicsHistory Of(IPhysicsSimulation world, int capacity)` trả về history của một world và tạo history mới khi capacity đổi, còn `Forget(world)` bỏ nó đi.

## Component physics <a href="#physics-components" id="physics-components"></a>

`public abstract class NetworkPhysics : MonoBehaviour, IPhysicsWorlds` trong `Fomoxa.Unity` là type của field Physics trên `NetworkManager`. Các member game dùng:

| Member | Mô tả |
|---|---|
| `PhysicsBackend Backend` | Backend mà component hiện thực |
| `bool Simulates` | Manager có step physics bằng component này hay không |
| `void WorldsOf(Scene scene, List<IPhysicsSimulation> worlds)` | Các world của một scene |
| `PhysicsBody BodyOf(NetworkObject)`, `PhysicsBody2D Body2DOf(NetworkObject)` | Thứ mà `NetworkObject.Body` và `Body2D` trả về |
| `StaticGroup AddStatic(Scene scene, IReadOnlyList<ColliderDesc> colliders)`, `AddStatic2D(Scene, IReadOnlyList<ColliderDesc2D>)` | Thêm một nhóm collider tĩnh vào một scene |
| `StaticGroup AddStatic(GameObject root)`, `AddStatic2D(GameObject root)` | Thêm các collider dưới một GameObject |
| `void RemoveStatic(StaticGroup group)` | Gỡ một nhóm; gỡ hai lần không làm gì |
| `PhysicsBody AddBody(Scene scene, in BodyDesc body)`, `PhysicsBody2D AddBody2D(Scene, in BodyDesc2D)` | Thêm một body không thuộc network object nào |
| `void RemoveBody(PhysicsBody body)`, `void RemoveBody2D(PhysicsBody2D body)` | Gỡ body như vậy |

Các member trừu tượng còn lại (`Begin`, `Release`, `HistoryOf`, `PlaceProxy`, `EndProxy`, `ForgetDestroyedProxies`, `WorldsToStep`, `TrackerOf`) do `NetworkManager` gọi.

`public sealed class RigidbodyPhysics : NetworkPhysics` trong `Fomoxa.Unity` chạy PhysX và Box2D của Unity. `Backend` của nó là `PhysicsBackend.Rigidbody`, và `Simulates` trả về field Simulate Physics. `AddStatic(GameObject)` và `AddStatic2D(GameObject)` trả về nhóm rỗng, vì physics của Unity đã có các collider đó.

## Các world của Unity <a href="#unity-worlds" id="unity-worlds"></a>

`UnityPhysicsWorld : IPhysicsWorld` và `UnityPhysicsWorld2D : IPhysicsWorld2D` nằm trong `Fomoxa.Unity`.

| Member | Mô tả |
|---|---|
| Constructor `(Scene scene)` | Một world cho physics scene của scene đó; ném exception với scene không hợp lệ |
| `PhysicsScene` | `PhysicsScene` hoặc `PhysicsScene2D` của Unity |
| `Scenes` | Các scene Unity dùng world này |
| `Register(Rigidbody)` / `Register(Rigidbody2D)` | Handle của một body có sẵn |
| `Backend` | Luôn là `PhysicsBackend.Rigidbody` |

`public static class BodyDescriptions` trong `Fomoxa.Unity` chuyển collider của Unity thành mô tả:

| Member | Mô tả |
|---|---|
| `bool TryDescribe(GameObject root, out BodyDesc desc)`, `TryDescribe2D(GameObject root, out BodyDesc2D desc)` | Mô tả body của một GameObject từ các collider và `Rigidbody` hoặc `Rigidbody2D` của nó; false khi không có collider. Có overload trả thêm các collider nguồn. |
| `StaticColliders(Scene scene, List<Collider> into)`, `StaticColliders2D(Scene, List<Collider2D>)` | Các collider của một scene không thuộc body nào, theo một thứ tự cố định |
| `StaticColliders(GameObject root, List<Collider> into)`, `StaticColliders2D(GameObject, List<Collider2D>)` | Như trên nhưng chỉ dưới một GameObject |
| `DescribeStatic(Collider collider, Transform space, List<ColliderDesc> into)`, `DescribeStatic2D(Collider2D, Transform, List<ColliderDesc2D>)` | Thêm mô tả của một collider tĩnh, tương đối với `space`, hoặc với world khi `space` là null |

Loại collider mà mô tả không biểu diễn được sẽ ném `NotSupportedException`.

## Backend contract <a href="#backend-contract" id="backend-contract"></a>

`IPhysicsWorlds` là thứ vòng tick cần từ một physics backend: `Backend`, `WorldsToStep(List<IPhysicsSimulation>)` và `TrackerOf(IPhysicsSimulation)`, hàm trả về contact tracker của một world hoặc null. `IPhysicsScenes : IPhysicsWorlds` thêm những gì [backend console](../console-server/physics.md) cần: load scene file vào các world, body theo entity và theo scene, nhóm tĩnh, các world của một entity, history và proxy. `IContactTracker`, `IContactSource<TContact>`, `ContactTracker<TContact>` và `ContactSet<TContact>` theo dõi contact theo tick và khôi phục chúng trong lúc replay.

`NetworkObject.Body` và `Body2D` được liệt kê trong [tham chiếu NetworkObject](network-object.md), còn field Physics của `NetworkManager` trong [cấu hình](configuration.md#networkmanager).
