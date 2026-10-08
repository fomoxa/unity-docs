# Bodies and colliders

`RapierPhysics` builds a Rapier body for a network object the first time something asks for it: the manager when it steps the world, or game code through `NetworkObject.Body` or `Body2D`. Static geometry comes from the scene file of the network scene. This page lists how Unity components map to Rapier and how game code reaches the worlds.

## Bodies of network objects

The body of a network object is described from the colliders under its GameObject that belong to its own `Rigidbody` or `Rigidbody2D`, with `BodyDescriptions.TryDescribe` and `TryDescribe2D`. The description keeps:

- the kind: dynamic, kinematic when `isKinematic` is set or the `Rigidbody2D` body type is `Kinematic`, and static for a static `Rigidbody2D` or when there is no `Rigidbody`;
- the mass, the axis constraints, gravity (`useGravity` in 3D, `gravityScale` in 2D) and the linear and angular damping;
- every enabled collider with its shape, position and rotation relative to the body, its physics material, its layer and its trigger flag.

The body is created in the Rapier world of the object's network scene. The `Rigidbody` is then switched to kinematic and the `Rigidbody2D` body type to `Kinematic`, so Unity's physics no longer moves the object. After every tick, Rapier writes each body's position and rotation back to the object's `Transform`; a 2D body keeps the `Transform`'s Z. When the object despawns, the body is removed and the original `Rigidbody` settings come back.

A collider that the backend cannot represent logs its exception against the object, and the object then has no Rapier body.

## Supported colliders

| 3D | 2D |
|---|---|
| `BoxCollider`, `SphereCollider`, `CapsuleCollider` | `BoxCollider2D`, `CircleCollider2D`, `CapsuleCollider2D` |
| Convex `MeshCollider`, on any body | `PolygonCollider2D`; a concave one on a moving body is split into convex pieces |
| Non-convex `MeshCollider` and `TerrainCollider`, static geometry only | `EdgeCollider2D`, static geometry only |

A `BoxCollider2D` with auto tiling on a sliced or tiled `SpriteRenderer` is described by the shapes Unity built for it. Meshes used by a body that is created at runtime must have Read/Write enabled.

Friction, bounciness and their combine modes come from the physics material. The layer collision matrices of the project apply as in Unity; the scene file carries them for each scene. Trigger colliders become Rapier sensors, which report what overlaps them and do not push anything.

## Static geometry

When a network scene loads, `RapierPhysics` reads its scene file and adds the scene's static colliders to the scene's worlds, in the order the file lists them. A static collider is an enabled collider on an active GameObject that belongs to no `Rigidbody` or `Rigidbody2D` and to no `NetworkObject`. A collider with its own `Rigidbody` but no `NetworkObject`, such as a moving saw, is not in the file, and neither is geometry that you create at runtime. Add them with the members of `NetworkPhysics`:

| Member | Adds |
|---|---|
| `AddStatic(Scene, IReadOnlyList<ColliderDesc>)`, `AddStatic2D(Scene, IReadOnlyList<ColliderDesc2D>)` | A group of collider descriptions to the worlds of a network scene |
| `AddStatic(GameObject)`, `AddStatic2D(GameObject)` | The static colliders under a GameObject; the contact components on those colliders then report Rapier contacts |
| `AddBody(Scene, in BodyDesc)`, `AddBody2D(Scene, in BodyDesc2D)` | A body that no network object owns, such as a platform that every peer moves the same way from the tick number |

`RemoveStatic`, `RemoveBody` and `RemoveBody2D` take the result back out. Static groups and unowned bodies are part of the world, so a snapshot saves them and a replay restores them.

## Reading the worlds

`RapierPhysics.Scenes` returns the `RapierScenes` that holds the worlds, or null before the `NetworkManager` has run its `Awake`. `WorldOf(sceneId)` and `WorldOf2D(sceneId)` return the `RapierWorld` or `RapierWorld2D` of a network scene, which implement `IPhysicsWorld` and `IPhysicsWorld2D` and add a few members of their own:

| Member | Description |
|---|---|
| `void Touching(RapierCollider collider, List<RapierCollider> into)` | Adds every collider that touches or overlaps `collider` after the last step |
| `void SetKind(BodyHandle body, BodyKind kind)` | Changes a body between dynamic, kinematic and static |
| `ulong StateHash` | A hash of the whole world state, for comparing two runs |

A `RapierCollider` names one collider of a world. `RapierCollider.OfBody(handle, index)` is the collider at `index` in the body's description, and `RapierCollider.Static(index)` is a static collider, numbered first by the scene file and then by the static groups in the order they were added (`StaticGroup.FirstIndex`). `IsStatic` tells the two apart.

The overloads of `BodyDescriptions.TryDescribe` and `TryDescribe2D` that take a list return the source collider of each description, so the position of a Unity collider in that list is its index in the body:

```csharp
using System.Collections.Generic;
using Fomoxa.Networking.Rapier;
using Fomoxa.Networking.Simulation;
using Fomoxa.Unity;
using Fomoxa.Unity.Rapier;
using UnityEngine;

public sealed class FootSensor : NetworkBehaviour
{
    [SerializeField] private Collider2D foot;

    private readonly List<Collider2D> sources = new List<Collider2D>();
    private readonly List<RapierCollider> touching = new List<RapierCollider>();

    public bool Grounded(RapierPhysics rapier, uint sceneId)
    {
        PhysicsBody2D body = NetworkObject.Body2D;
        if (!body.IsValid || !BodyDescriptions.TryDescribe2D(gameObject, out _, sources))
        {
            return false;
        }

        touching.Clear();
        rapier.Scenes.WorldOf2D(sceneId).Touching(RapierCollider.OfBody(body.Handle, sources.IndexOf(foot)), touching);
        return touching.Count > 0;
    }
}
```

`sceneId` is the id of the object's network scene, which `NetworkManager.Scenes.IdOf(gameObject.scene.path)` returns. Contact sets read this way are part of the simulation, so they are the same on the server and the predicting client, and the same again in a replay. The [Red Runner example](../examples/redrunner/rapier-and-console/step-10-rapier-backend.md) decides grounding and deaths this way.

[Contact events](contacts.md) describes the event components, and the [physics API reference](../reference/physics.md) lists the description types.
