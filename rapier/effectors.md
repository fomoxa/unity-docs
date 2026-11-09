# Effectors

The Rapier backend simulates the five 2D effectors of Unity: `PlatformEffector2D`, `SurfaceEffector2D`, `AreaEffector2D`, `BuoyancyEffector2D` and `PointEffector2D`. They run inside the native library, so the server, the predicting client and a replay apply them the same way. Their behavior was measured against Box2D in Unity 6000.5 and follows it.

## Where effectors come from

An effector acts through the colliders on its GameObject that have Used By Effector checked, as in Unity. The backend reads the component once and does not follow later changes to it:

| Collider | When it is read |
|---|---|
| A static collider of a network scene | From the scene file, when the scene loads. The Editor writes the effector into the file with the collider |
| A collider of a network object's body | When `RapierPhysics` builds the bodies of the object. The effector belongs to that body and goes away with it |
| A collider under a GameObject passed to `AddStatic2D(GameObject)` | When the group is added; `RemoveStatic` removes the effector with the group |

Because a static effector is part of the scene file, export the network scene files again after you add or change one. A console server reads the same files, so its worlds have the same effectors.

## Behavior

All effectors act only on dynamic bodies. An effector on a collider that is not a trigger acts on the bodies that touch it, and a body gets the effect once per effector even when it touches several of its colliders. With Use Collider Mask on, the mask replaces the layer collision matrix for the effector's colliders, also for ordinary collisions. Queries such as `Raycast` see the colliders of an effector like any other collider.

### Platform

A body passes through a one-way platform when it comes from outside the Surface Arc, measured from the platform's up direction plus Rotational Offset, and is held when it lands from inside it. A body that started touching outside the arc keeps passing until it has left the platform, so a body that jumps up through the platform does not stop halfway. Use One Way Grouping lets one blocked contact of a body block all of its contacts. Side contacts lose their friction or bounce when Use Side Friction or Use Side Bounce is off.

The [character controller](character-controller.md) passes up through one-way platforms and lands on them in the same way.

### Surface

After each step, the effector changes the velocity of every body that touches it along its surface, towards Speed, scaled by Force Scale. With Use Contact Force on, the change is applied as an impulse at the contact point instead. Use Friction and Use Bounce off remove the friction and bounce of the contact.

### Area

The force is computed after each step from the bodies inside the area and applied during the next step. Force Angle is in world space with Use Global Angle on, and otherwise relative to the rotation of the effector. Linear Damping and Angular Damping slow the bodies right after the step. With Force Target set to Collider, the force acts at the center of mass of the touching collider instead of the body's.

### Buoyancy

The surface is the horizontal line at Surface Level above the effector's GameObject. Each body is pushed against gravity at the center of its submerged part. The force is Density times the submerged area times the strength of gravity, scaled by the body's gravity scale. Linear Damping and Angular Damping slow the body in proportion to that area. Flow Magnitude and Flow Angle push the submerged part sideways. Circles, boxes and convex polygons are cut exactly at the surface. A capsule is treated as its bounding box.

### Point

The force is Force Magnitude along the line from the source towards the body, scaled by the distance times Distance Scale according to Force Mode: constant, inverse linear or inverse squared. Below a distance of 1 the inverse modes use 1. The source is the position of the effector's body or, with Force Source set to Collider, the center of the effector's collider. With Force Target set to Collider, it acts at the center of mass of the touching collider. The force is applied during the next step, and damping acts right after each step, as for an area.

## What is not simulated

Speed Variation, Force Variation and Flow Variation are random in Unity. The backend treats them as 0, and the Editor and `RapierPhysics` log a warning once for each component where one is not 0.

## Measured differences from Box2D

Forces and torques match Box2D to four or five digits in the first steps. Positions drift by about 1% of the distance travelled, because Rapier integrates positions over several substeps per step; a body in free fall without any effector shows the same drift. A 2D capsule turns more slowly under Rapier than under Box2D for the same torque, because the two engines compute its inertia differently.

## Effectors from code

`EffectorDesc2D` describes an effector, with one factory per kind that takes the parameters of the Unity component, angles in radians:

| Factory |
|---|
| `Platform(bool oneWay, bool oneWayGrouping, float rotationalOffset, float surfaceArc, bool sideFriction, bool sideBounce, float sideArc)` |
| `Surface(float speed, float forceScale, bool contactForce, bool friction, bool bounce)` |
| `Area(float forceAngle, bool globalAngle, float forceMagnitude, EffectorSelection forceTarget, float linearDamping, float angularDamping)` |
| `Buoyancy(float surfaceLevel, float density, float linearDamping, float angularDamping, float flowAngle, float flowMagnitude)` |
| `Point(float forceMagnitude, float distanceScale, EffectorSelection forceSource, EffectorSelection forceTarget, EffectorForceMode forceMode, float linearDamping, float angularDamping)` |

`EffectorSelection` is `Rigidbody` or `Collider`, and `EffectorForceMode` is `Constant`, `InverseLinear` or `InverseSquared`.

`WithFrame(Vector2 origin, float rotation)` places the effector in the frame of its body, or in world space on a static group, and `WithColliderMask(uint? mask)` sets the collider mask, where `null` uses the layer collision matrix.

| Member | Adds an effector to |
|---|---|
| `RapierScenes.AddEffector(INetworkEntity owner, PhysicsBody2D body, IReadOnlyList<int> colliders, in EffectorDesc2D desc)` | A body of a network object or console entity |
| `RapierScenes.AddEffector(StaticGroup group, IReadOnlyList<int> colliders, in EffectorDesc2D desc)` | A static group returned by `RapierScenes.AddStatic2D` |
| `RapierScenes.AddEffector(PhysicsBody2D body, IReadOnlyList<int> colliders, in EffectorDesc2D desc)` | A body that no network object owns, such as a moving platform |

`colliders` are indices into the colliders of the body description or of the group. Each call returns an `EffectorHandle`. `RapierWorld2D.SetEffector(handle, desc)` changes the description and keeps the colliders, `RemoveEffector(handle)` removes the effector, and removing the body or group removes its effectors. A collider that already has an effector, an index out of range or an invalid description throws `ArgumentException`.

## Effectors in a replay

A snapshot holds the effectors with their descriptions. When a client loads an earlier tick, an effector that existed then takes the description of that tick, an effector added later keeps its current description, and an effector removed later stays removed, as for [joints](joints.md#joints-in-a-replay). Add and change effectors in prediction callbacks and tick events in the same order on every peer.
