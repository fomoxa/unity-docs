# Physics queries

A world answers four kinds of query: a ray, a moving shape, the bodies inside a shape, and the contact points between two bodies. The same calls work with `RigidbodyPhysics` and with the [Rapier backend](../rapier/overview.md), because both implement `IPhysicsWorld` and `IPhysicsWorld2D`. The calls on this page take and return Unity's `Vector3`, `Vector2` and `Quaternion`; they are extension methods in `NetworkPhysicsQueries` (`Fomoxa.Unity`) on those two interfaces. Queries run on the state of the world at the moment of the call, so the server and a predicting client get the same answer when their worlds hold the same state.

## Reaching a world

Contact points are read through the body itself, as shown below. For the other queries you need the world, which the physics component returns for a scene:

```csharp
using System.Collections.Generic;
using Fomoxa.Networking.Simulation;
using Fomoxa.Unity;

private readonly List<IPhysicsSimulation> worlds = new List<IPhysicsSimulation>();

private IPhysicsWorld2D World2DOf(NetworkPhysics physics)
{
    worlds.Clear();
    physics.WorldsOf(gameObject.scene, worlds);
    foreach (IPhysicsSimulation world in worlds)
    {
        if (world is IPhysicsWorld2D world2D)
        {
            return world2D;
        }
    }

    return null;
}
```

`physics` is the component in the Physics field of the `NetworkManager`. The manager does not expose it, so give the behaviour a serialized `NetworkPhysics` field and drag the same component into it.

## Filters

Every query takes a `QueryFilter`:

| Member | Meaning |
|---|---|
| `LayerMask` | Bit `i` set means colliders on layer `i` are considered. `-1` is every layer |
| `ExcludeBody` | The colliders of this body are skipped. The default `BodyHandle` skips nothing |
| `IncludeTriggers` | Whether trigger colliders are considered |

`QueryFilter.All` and `default(QueryFilter)` are the same: every layer, triggers included, no body skipped. A filter for the ground under a player looks like this:

```csharp
var filter = new QueryFilter(1 << groundLayer, NetworkObject.Body2D.Handle, false);
```

## Raycast and ShapeCast

```csharp
bool Raycast(Vector3 origin, Vector3 direction, float maxDistance, in QueryFilter filter, out NetworkRayHit hit);
bool ShapeCast(in BodyShape shape, Vector3 position, Quaternion rotation, Vector3 direction, float maxDistance, in QueryFilter filter, out NetworkRayHit hit);
```

`Raycast` returns the first collider along a ray and `ShapeCast` the first collider that a shape touches while it moves along `direction`. The 2D versions take `Vector2` values, a rotation in radians, `BodyShape2D` and `NetworkRayHit2D`. `NetworkRayHit` has `Body` (a `BodyHandle`), `Point`, `Normal` and `Distance`.

`BodyShape.Sphere(radius)`, `BodyShape.Capsule(radius, halfHeight)`, `BodyShape2D.Circle(radius)` and `BodyShape2D.Capsule(radius, halfHeight)` make the round shapes. For a box, `NetworkShapes.Box(Vector3 halfExtents)` and `NetworkShapes.Box2D(Vector2 halfExtents)` take Unity vectors.

- The direction is normalized first, and `hit.Distance` is in world units. A zero direction returns false.
- `ShapeCast` takes a box, a sphere or a capsule in 3D, and a box, a circle or a capsule in 2D. Other shapes throw `ArgumentException`. A capsule lies along its local Y axis, as a capsule collider does.
- A query that starts inside a collider hits it at distance 0. The point and normal of such a hit differ between backends: `RigidbodyPhysics` reports the start position and `-direction`, Rapier reports the values its geometry library computes. A triangle mesh only counts when the query reaches its surface.
- `hit.Body` is the body of the collider that was hit. It is invalid for static geometry and for a `Rigidbody` that the world does not know.

```csharp
NetworkBody2D body = NetworkObject.Body2D;
BodyShape2D feet = NetworkShapes.Box2D(new Vector2(0.4f, 0.05f));
var filter = new QueryFilter(1 << groundLayer, body.Handle, false);
bool grounded = World2DOf(physics).ShapeCast(feet, body.Position, 0f, Vector2.down, 0.1f, filter, out NetworkRayHit2D hit);
```

## Overlap

```csharp
int Overlap(in BodyShape shape, Vector3 position, Quaternion rotation, in QueryFilter filter, BodyHandle[] results);
int Overlap(Vector3 center, float radius, BodyHandle[] results);
```

`Overlap` writes the bodies whose colliders overlap the shape into `results`, each body once and at most `results.Length` of them, and returns how many it wrote. Static colliders and unknown bodies are not written, and the order is not defined. A null array throws `ArgumentNullException`. The overload with a center and a radius uses a sphere, or a circle in 2D, and `QueryFilter.All`.

## Contact points

`NetworkBody.GetContactPoints(other, into)` and `NetworkBody2D.GetContactPoints(other, into)` list where the body touches another one after the last step, as `NetworkContactPoint` or `NetworkContactPoint2D` values:

| Field of `NetworkContactPoint`, `NetworkContactPoint2D` | Meaning |
|---|---|
| `Point` | The contact point in world space |
| `Normal` | A unit normal that points from `other` towards the body you asked about |
| `Depth` | Positive when the colliders overlap, negative when they are still apart but within the contact margin of the engine |

Pass `default(BodyHandle)` as `other` to get the contacts with static geometry. An overload takes a `QueryFilter` that applies to the colliders on the side of `other`; `IncludeTriggers` has no effect there, because triggers have no contact points. The method clears `into`, fills it and returns the number of points.

```csharp
private readonly List<NetworkContactPoint2D> points = new List<NetworkContactPoint2D>();

private bool StandsOnGround()
{
    NetworkObject.Body2D.GetContactPoints(default, points);
    foreach (NetworkContactPoint2D point in points)
    {
        if (point.Normal.y > 0.7f)
        {
            return true;
        }
    }

    return false;
}
```

After a step, the points are those of that step. Between a `Load` and the next step, they are the points of the loaded tick, so an input handler that runs again during a replay reads what it read the first time. `RigidbodyPhysics` returns no points for 3D bodies, because Unity only reports 3D contacts through collision callbacks. Use the [contact components](contacts.md#contact-points) for 3D under `RigidbodyPhysics`.

## Queries without a filter

`Raycast` without a filter and `Overlap(center, radius, results)` use `QueryFilter.All`, so under `RigidbodyPhysics` they consider every layer, including Ignore Raycast, and hit triggers.

## Queries with System.Numerics types

The methods of `IPhysicsWorld` and `IPhysicsWorld2D` themselves take `System.Numerics` vectors and return `RayHit`, `RayHit2D`, `ContactPointInfo` and `ContactPointInfo2D`. Code shared with the [console server](../console-server/overview.md) calls those, together with the extension methods in `PhysicsQueries` (`Fomoxa.Networking.Simulation`) that drop the filter.

The [physics API reference](../reference/physics.md) lists the types, and [NetworkBody](physics-body.md) covers forces and torques.
