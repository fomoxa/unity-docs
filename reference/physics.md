# Physics API reference

Unless stated otherwise, the types on this page are in the namespace `Fomoxa.Unity.Simulation` and the assembly `Fomoxa.Unity.Core`, and their vectors and quaternions are `System.Numerics` types. The [physics overview](../physics/overview.md), [PhysicsBody](../physics/physics-body.md) and [physics architecture](../physics/architecture.md) guides explain how they are used.

## PhysicsBody

`public readonly struct PhysicsBody`, with the constructor `PhysicsBody(IPhysicsWorld world, BodyHandle handle)`.

| Member | Type | Description |
|---|---|---|
| `IsValid` | `bool` | The world exists and contains the body |
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
| `public enum PhysicsBackend : byte` | `Rigidbody = 1`, `Rapier = 2` (not implemented) |
| `public enum BodyKind` | `Dynamic`, `Kinematic`, `Static` |
| `public readonly struct BodyHandle` | `int Value`, `bool IsValid` (false for 0) |
| `public readonly struct BodyShape` | `Box(Vector3 halfExtents)`, `Sphere(float radius)`, `Capsule(float radius, float halfHeight)`; `Kind`, `HalfExtents`, `Radius`, `HalfHeight` |
| `public readonly struct BodyShape2D` | `Box(Vector2 halfExtents)`, `Circle(float radius)`, `Capsule(float radius, float halfHeight)` |
| `public readonly struct BodyDesc` | `BodyDesc(BodyKind kind, BodyShape shape, Vector3 position, Quaternion rotation, float mass)` |
| `public readonly struct BodyDesc2D` | `BodyDesc2D(BodyKind kind, BodyShape2D shape, Vector2 position, float rotation, float mass)` |
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

## Unity backend

`UnityPhysicsWorld : IPhysicsWorld` and `UnityPhysicsWorld2D : IPhysicsWorld2D` are in `Fomoxa.Unity`.

| Member | Description |
|---|---|
| Constructor `(Scene scene)` | A world for the scene's physics scene; throws for an invalid scene |
| `PhysicsScene` | The Unity `PhysicsScene` or `PhysicsScene2D` |
| `Scenes` | The Unity scenes that use this world |
| `Register(Rigidbody)` / `Register(Rigidbody2D)` | Handle of an existing body |
| `Backend` | Always `PhysicsBackend.Rigidbody` |

`NetworkObject.Body` and `Body2D` are listed in the [NetworkObject reference](network-object.md), and the physics fields of the `NetworkManager` in [configuration](configuration.md#networkmanager).
