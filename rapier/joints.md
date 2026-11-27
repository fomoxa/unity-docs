# Joints

A joint ties two bodies of a network object together, or one body to the world. The Rapier backend reads Unity's joint components when it builds the bodies of a network object, and game code can create joints itself through the worlds. Joints are part of the Rapier world, so a snapshot saves them and a replay restores them with the bodies.

## Joint components

`RapierPhysics` reads the joint components of every body of a network object after it has built all of the object's [bodies](bodies.md#several-bodies):

| Component | Becomes |
|---|---|
| `FixedJoint`, `FixedJoint2D` | A fixed joint. A `FixedJoint2D` with a frequency above 0 is soft |
| `HingeJoint`, `HingeJoint2D` | A revolute joint with the component's limits and motor. The spring of a `HingeJoint` becomes a position motor |
| `SliderJoint2D` | A prismatic joint along the component's angle, with its limits and motor |
| `CharacterJoint` | A spherical joint with the twist and both swing limits |
| `SpringJoint` | A spring with a rest length of Max Distance plus Tolerance, Spring and Damper |
| `SpringJoint2D` | A spring with the component's distance, frequency and damping ratio. A frequency of 0 holds the distance fixed |
| `DistanceJoint2D` | A rope of the component's distance; with Max Distance Only off, the distance is held fixed |

The anchor, the connected anchor (or Auto Configure Connected Anchor) and Enable Collision apply as in Unity. Connected Body must be empty, which joins the body to the world, or a `Rigidbody` of the same network object. A joint to another network object logs `the connected body is not a body of the same NetworkObject` and is not built.

These cases are reported in the Console, once per component each time the object is built:

| Case | Result |
|---|---|
| `ConfigurableJoint`, `WheelJoint2D`, `RelativeJoint2D`, `TargetJoint2D`, `FrictionJoint2D` and other joint types | An error, `is not supported under Rapier`; no joint |
| A finite Break Force or Break Torque | An error, `Rapier joints do not break`; the joint is built and never breaks |
| A parameter the backend ignores, from the table below | One warning that names the parameters |

| Component | Ignored when it differs from Unity's default |
|---|---|
| Every 3D joint | Mass Scale, Connected Mass Scale, Enable Preprocessing |
| `HingeJoint` | The bounciness of the limits, Free Spin of the motor, and Use Spring together with Use Motor (the motor wins) |
| `SpringJoint` | Min Distance |
| `CharacterJoint` | The bounciness and springs of the limits, Enable Projection |

Joints are read once, when the object is built. Changing a joint component afterwards has no effect; change the joint through the world instead.

## Joints from code

`RapierWorld.CreateJoint(BodyHandle a, BodyHandle b, in JointDesc desc)` and `RapierWorld2D.CreateJoint` with a `JointDesc2D` create a joint and return its `JointHandle`. A `b` of `default(BodyHandle)` joins `a` to the world. `SetJoint(handle, desc)` replaces the description of a joint and keeps its two bodies, `RemoveJoint(handle)` removes it, and removing a body removes its joints.

A `JointDesc` places the joint in each body's local space: an anchor point and a frame whose X axis is the main axis of the joint. Angles are in radians and lengths in meters.

| Member | Description |
|---|---|
| `NetworkJoints.Create(JointKind kind, Vector3 anchorA, Quaternion frameA, Vector3 anchorB, Quaternion frameB)` | `Fixed`, `Revolute`, `Prismatic` or `Spherical`. `NetworkJoints.Create2D` takes `Vector2` anchors and angles, and has no `Spherical` |
| `NetworkJoints.Rope(anchorA, anchorB, maxLength)` | A rope that keeps the distance at most `maxLength` |
| `NetworkJoints.Spring(anchorA, anchorB, restLength, stiffness, damping)` | A spring towards `restLength` |
| `WithLimit(JointLimit)` | The angle range of a revolute joint, the distance range of a prismatic joint, the twist of a spherical joint, or the length range of a rope |
| `WithSwingLimits(JointLimit y, JointLimit z)` | The swing of a spherical joint |
| `WithMotor(JointMotorDesc)` | A motor on a revolute or prismatic joint |
| `WithSoftness(JointSoftness)` | A soft constraint with a frequency and a damping ratio |
| `WithLength(float)`, `WithContacts(bool)` | The length of a rope or spring, and whether the two bodies still collide |

`JointMotorDesc.Velocity(targetVelocity, damping, maxForce)` drives towards a speed and `JointMotorDesc.Position(targetPosition, stiffness, damping, maxForce)` towards a position. The motor force is `stiffness · (targetPosition − x) + damping · (targetVelocity − v)`, capped at `maxForce`. The type is named `JointMotorDesc` so that it does not clash with `UnityEngine.JointMotor` in files that use both namespaces.

`NetworkJoints` in `Fomoxa.Unity.Rapier` builds a `JointDesc` from Unity's `Vector3` and `Quaternion`, and `Create2D`, `Rope2D` and `Spring2D` build a `JointDesc2D` from `Vector2`. A console server has no Unity, so it uses the `JointDesc` constructor, `JointDesc.Rope` and `JointDesc.Spring` with `System.Numerics` types.

A door that swings on a hinge between 0 and 100 degrees and closes itself:

```csharp
using Fomoxa.Networking.Rapier;
using Fomoxa.Unity;
using Fomoxa.Unity.Rapier;
using UnityEngine;

NetworkBody door = networkObject.Body;
var hinge = NetworkJoints.Create(JointKind.Revolute, new Vector3(-0.5f, 0f, 0f), Quaternion.AngleAxis(90f, Vector3.forward), hingePoint, Quaternion.AngleAxis(90f, Vector3.forward))
    .WithLimit(new JointLimit(0f, 100f * Mathf.Deg2Rad))
    .WithMotor(JointMotorDesc.Position(0f, 40f, 4f, 200f));
JointHandle joint = rapier.Scenes.CreateJoint(networkObject, door, default, hinge);
```

`rapier` is the `RapierPhysics` component of the `NetworkManager`. The second body is the world, so `hingePoint` is the hinge in world coordinates. Both frames turn the X axis of the joint onto the vertical axis, which makes the door swing around it. `RapierScenes.CreateJoint(INetworkEntity owner, NetworkBody a, NetworkBody b, in JointDesc desc)` and the `NetworkBody2D` overload with a `JointDesc2D` check that `a` is a body of `owner` and attach the joint to it, so the joint goes away with the object. Change or remove it later through `rapier.Scenes.WorldOf(scene)`, where `scene` is the `NetworkScene` of the object's scene, as described in [reading the worlds](bodies.md#reading-the-worlds). A console server makes the same call with its `StandaloneEntity` and `PhysicsBody` values.

When the object [moves to another instance](../objects/scenes.md#move-an-object-to-another-instance), `RapierPhysics` builds its bodies and its joint components again in the worlds of the new instance. A joint created with `CreateJoint` is removed with the old bodies, so create it again in `OnSceneChangedServer` or `OnSceneChangedClient`.

## Joints in a replay

A snapshot holds every joint with its description and solver state. When a client loads an earlier tick:

- a joint that exists in the snapshot and still exists now takes the description and state of the snapshot, so a `SetJoint` made after that tick is undone;
- a joint created after that tick is kept with its current description, and starts again without the solver state of earlier steps;
- a joint removed after that tick stays removed.

Create and change joints in prediction callbacks and tick events in the same order on every peer, as described in [determinism](determinism.md).
