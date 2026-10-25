# Physics API reference

Unless stated otherwise, the types on this page are in the namespace `Fomoxa.Networking.Simulation` and the assembly `Fomoxa.Networking`, and their vectors and quaternions are `System.Numerics` types. The [physics overview](../physics/overview.md), [PhysicsBody](../physics/physics-body.md) and [physics architecture](../physics/architecture.md) guides explain how they are used.

## PhysicsBody

`public readonly struct PhysicsBody`, with the constructor `PhysicsBody(IPhysicsWorld world, BodyHandle handle)`.

| Member | Type | Description |
|---|---|---|
| `IsValid` | `bool` | The world exists and contains the body |
| `Handle` | `BodyHandle` | The body's handle in its world |
| `Position` | `Vector3` | Get and set |
| `Rotation` | `Quaternion` | Get and set |
| `Velocity` | `Vector3` | Get and set; written only to a dynamic body |
| `AngularVelocity` | `Vector3` | Radians per second. Get and set; written only to a dynamic body. |
| `Mass` | `float` | |
| `IsKinematic` | `bool` | |
| `State` | `BodyState` | Get and set all four at once |
| `AddForce(Vector3 force)` | `void` | Force over the next step |
| `AddImpulse(Vector3 impulse)` | `void` | Velocity change of `impulse / Mass`; ignored by kinematic bodies |

## PhysicsBody2D

`public readonly struct PhysicsBody2D`, with the constructor `PhysicsBody2D(IPhysicsWorld2D world, BodyHandle handle)`. It has the same members as `PhysicsBody`, but with `Vector2` positions and velocities, a `float` rotation in radians, a `float` angular velocity in radians per second, and `BodyState2D`.

## State types

| Type | Fields |
|---|---|
| `public struct BodyState` | `Vector3 Position`, `Quaternion Rotation`, `Vector3 Velocity`, `Vector3 AngularVelocity` |
| `public struct BodyState2D` | `Vector2 Position`, `float Rotation`, `Vector2 Velocity`, `float AngularVelocity` |

## Interfaces

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

`IPhysicsWorld : IPhysicsSimulation` adds these members:

| Member | Description |
|---|---|
| `BodyHandle CreateBody(in BodyDesc desc)` | Creates a body |
| `bool RemoveBody(BodyHandle body)` | Removes a body; false when unknown |
| `bool Contains(BodyHandle body)` | Whether the body exists |
| `BodyState GetBody(BodyHandle body)`, `void SetBody(BodyHandle body, in BodyState state)` | Read and write the state |
| `BodyKind GetKind(BodyHandle body)`, `float GetMass(BodyHandle body)` | Kind and mass |
| `void SetRewindable(BodyHandle body, bool rewindable)` | Includes or excludes the body from snapshots |
| `void AddForce(BodyHandle body, Vector3 force)`, `void AddImpulse(BodyHandle body, Vector3 impulse)` | Forces |
| `bool Raycast(Vector3 origin, Vector3 direction, float maxDistance, out RayHit hit)` | First hit along a ray |
| `int Overlap(Vector3 center, float radius, BodyHandle[] results)` | Bodies overlapping a sphere; returns how many were written |

`IPhysicsWorld2D : IPhysicsSimulation` has the same members with `BodyDesc2D`, `BodyState2D`, `Vector2` and `RayHit2D`, and its `Overlap` tests a circle.

## Data types

| Type | Members |
|---|---|
| `public enum PhysicsBackend : byte` | `Rigidbody = 1`, `Rapier = 2`; the [Rapier backend](../rapier/overview.md) is a separate package |
| `public enum BodyKind` | `Dynamic`, `Kinematic`, `Static` |
| `public readonly struct BodyHandle` | `int Value`, `bool IsValid` (false for 0) |
| `public readonly struct BodyShape` | `Box(Vector3 halfExtents)`, `Sphere(float radius)`, `Capsule(float radius, float halfHeight)`, `ConvexHull(IReadOnlyList<Vector3> points)` (at least 4 points), `TriangleMesh(IReadOnlyList<Vector3> vertices, IReadOnlyList<int> triangles)`; `Kind`, `HalfExtents`, `Radius`, `HalfHeight`, `Points`, `Triangles` |
| `public readonly struct BodyShape2D` | `Box(Vector2 halfExtents)`, `Circle(float radius)`, `Capsule(float radius, float halfHeight)`, `ConvexPolygon(IReadOnlyList<Vector2> points)` (at least 3 points), `Polyline(IReadOnlyList<Vector2> points)` (at least 2 points, static geometry only) |
| `public enum CombineRule` | `Average`, `Minimum`, `Multiply`, `Maximum`, `Mean` |
| `public readonly struct ColliderMaterial` | `ColliderMaterial(float friction, float restitution, CombineRule frictionCombine, CombineRule restitutionCombine)`; `Default` is friction 0.6, restitution 0, both `Average` |
| `public readonly struct ColliderDesc` | `ColliderDesc(BodyShape shape, Vector3 position, Quaternion rotation, ColliderMaterial material, int layer, bool isTrigger)`; position and rotation are relative to the body |
| `public readonly struct ColliderDesc2D` | `ColliderDesc2D(BodyShape2D shape, Vector2 position, float rotation, ColliderMaterial material, int layer, bool isTrigger)` |
| `[Flags] public enum BodyLocks` | `None`, `PositionX`, `PositionY`, `PositionZ`, `RotationX`, `RotationY`, `RotationZ` |
| `[Flags] public enum BodyLocks2D` | `None`, `PositionX`, `PositionY`, `Rotation` |
| `public readonly struct BodyMotion` | `BodyMotion(BodyLocks locks, bool useGravity, float linearDamping, float angularDamping)`; `Default` has no locks, gravity on and no damping |
| `public readonly struct BodyMotion2D` | `BodyMotion2D(BodyLocks2D locks, float gravityScale, float linearDamping, float angularDamping)`; `Default` has no locks, gravity scale 1 and no damping |
| `public readonly struct BodyDesc` | `BodyDesc(BodyKind kind, BodyShape shape, Vector3 position, Quaternion rotation, float mass)`, and constructors that take `IReadOnlyList<ColliderDesc> colliders` instead of one shape, optionally followed by `in BodyMotion motion` |
| `public readonly struct BodyDesc2D` | The same with `BodyShape2D`, `ColliderDesc2D`, `Vector2`, a `float` rotation and `BodyMotion2D` |
| `public readonly struct StaticGroup` | `uint SceneId`, `int Id`, `int FirstIndex`, `int Count`, `bool IsValid` (false for the default value); a group of static colliders added at runtime |
| `public readonly struct RayHit` | `BodyHandle Body`, `Vector3 Point`, `Vector3 Normal`, `float Distance` |
| `public readonly struct RayHit2D` | `BodyHandle Body`, `Vector2 Point`, `Vector2 Normal`, `float Distance` |
| `public abstract class PhysicsSnapshot` | Base class of a backend's snapshots |

A capsule's `HalfHeight` is half the distance between the centers of its two end spheres.

## PhysicsHistory

`public sealed class PhysicsHistory`, with the constructor `PhysicsHistory(IPhysicsSimulation world, int capacity)`, where the capacity is at least 1.

| Member | Description |
|---|---|
| `int Capacity` | Ring size |
| `void Save(uint tick)` | Saves the world for a tick |
| `bool Has(uint tick)` | Whether the tick is in the ring |
| `bool Load(uint tick)` | Restores the tick; false when absent |
| `void Clear()` | Forgets every tick |

`PhysicsHistories` keeps one `PhysicsHistory` per world: `PhysicsHistory Of(IPhysicsSimulation world, int capacity)` returns the history of a world and creates a new one when the capacity changed, and `Forget(world)` drops it.

## Physics components

`public abstract class NetworkPhysics : MonoBehaviour, IPhysicsWorlds` in `Fomoxa.Unity` is the type of the Physics field of the `NetworkManager`. Members a game uses:

| Member | Description |
|---|---|
| `PhysicsBackend Backend` | The backend the component implements |
| `bool Simulates` | Whether the manager steps physics with this component |
| `void WorldsOf(Scene scene, List<IPhysicsSimulation> worlds)` | The worlds of a scene |
| `PhysicsBody BodyOf(NetworkObject)`, `PhysicsBody2D Body2DOf(NetworkObject)` | What `NetworkObject.Body` and `Body2D` return |
| `StaticGroup AddStatic(Scene scene, IReadOnlyList<ColliderDesc> colliders)`, `AddStatic2D(Scene, IReadOnlyList<ColliderDesc2D>)` | Adds a group of static colliders to a scene |
| `StaticGroup AddStatic(GameObject root)`, `AddStatic2D(GameObject root)` | Adds the colliders under a GameObject |
| `void RemoveStatic(StaticGroup group)` | Removes a group; removing it twice does nothing |
| `PhysicsBody AddBody(Scene scene, in BodyDesc body)`, `PhysicsBody2D AddBody2D(Scene, in BodyDesc2D)` | Adds a body that no network object owns |
| `void RemoveBody(PhysicsBody body)`, `void RemoveBody2D(PhysicsBody2D body)` | Removes such a body |

The other abstract members (`Begin`, `Release`, `HistoryOf`, `PlaceProxy`, `EndProxy`, `ForgetDestroyedProxies`, `WorldsToStep`, `TrackerOf`) are called by the `NetworkManager`.

`public sealed class RigidbodyPhysics : NetworkPhysics` in `Fomoxa.Unity` runs Unity's PhysX and Box2D. Its `Backend` is `PhysicsBackend.Rigidbody`, and `Simulates` returns its Simulate Physics field. `AddStatic(GameObject)` and `AddStatic2D(GameObject)` return an empty group, because Unity's physics already has those colliders.

## Unity worlds

`UnityPhysicsWorld : IPhysicsWorld` and `UnityPhysicsWorld2D : IPhysicsWorld2D` are in `Fomoxa.Unity`.

| Member | Description |
|---|---|
| Constructor `(Scene scene)` | A world for the scene's physics scene; throws for an invalid scene |
| `PhysicsScene` | The Unity `PhysicsScene` or `PhysicsScene2D` |
| `Scenes` | The Unity scenes that use this world |
| `Register(Rigidbody)` / `Register(Rigidbody2D)` | Handle of an existing body |
| `Backend` | Always `PhysicsBackend.Rigidbody` |

`public static class BodyDescriptions` in `Fomoxa.Unity` turns Unity colliders into descriptions:

| Member | Description |
|---|---|
| `bool TryDescribe(GameObject root, out BodyDesc desc)`, `TryDescribe2D(GameObject root, out BodyDesc2D desc)` | Describes the body of a GameObject from its colliders and its `Rigidbody` or `Rigidbody2D`; false when there is no collider. Overloads also return the source colliders. |
| `StaticColliders(Scene scene, List<Collider> into)`, `StaticColliders2D(Scene, List<Collider2D>)` | The colliders of a scene that belong to no body, in a fixed order |
| `StaticColliders(GameObject root, List<Collider> into)`, `StaticColliders2D(GameObject, List<Collider2D>)` | The same under one GameObject |
| `DescribeStatic(Collider collider, Transform space, List<ColliderDesc> into)`, `DescribeStatic2D(Collider2D, Transform, List<ColliderDesc2D>)` | Adds the description of a static collider, relative to `space` or to the world when `space` is null |

A collider type the descriptions cannot represent throws `NotSupportedException`.

## Backend contract

`IPhysicsWorlds` is what the tick loop needs from a physics backend: its `Backend`, `WorldsToStep(List<IPhysicsSimulation>)` and `TrackerOf(IPhysicsSimulation)`, which returns the contact tracker of a world or null. `IPhysicsScenes : IPhysicsWorlds` adds what the [console backend](../console-server/physics.md) needs: loading a scene file into worlds, bodies per entity and per scene, static groups, the worlds of an entity, histories and proxies. A backend can also implement `IPhysicsMotion`: `ReportsMotion(INetworkEntity)` says whether it tracks the movement of every body of an entity, and `CollectMoved(List<INetworkEntity>)` adds the entities whose bodies moved since the last call. The server calls it once per tick, after the tick callbacks, and reads the transforms of those entities only when they move. `RapierPhysics` and `RapierScenes` implement it. `IContactTracker`, `IContactSource<TContact>`, `ContactTracker<TContact>` and `ContactSet<TContact>` track contacts per tick and restore them during a replay.

`NetworkObject.Body` and `Body2D` are listed in the [NetworkObject reference](network-object.md), and the Physics field of the `NetworkManager` in [configuration](configuration.md#networkmanager).
