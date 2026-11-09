# PhysicsBody

`PhysicsBody` and `PhysicsBody2D` are the package's view of a network object's physics body, and you use them in `apply`, `capture` and `restore` to read and change the body. They work with `System.Numerics` vectors and do not depend on Unity's `Rigidbody` API.

```csharp
using Fomoxa.Networking.Simulation;
using Fomoxa.Unity;

PhysicsBody body = NetworkObject.Body;
PhysicsBody2D body2D = NetworkObject.Body2D;
```

Both are small structs, so get a fresh one when you need it instead of storing it across spawns.

## When it is valid

`IsValid` is true when two conditions hold: the object has a `Rigidbody` (for `Body`) or a `Rigidbody2D` (for `Body2D`) on the same GameObject as its `NetworkObject`, and the object is spawned on this side. Reading or writing an invalid body throws.

`Body` and `Body2D` are the body on the GameObject of the `NetworkObject`. An object with more bodies lists all of them in `NetworkObject.Bodies` and `Bodies2D`, as described under [several bodies](overview.md#several-bodies).

## PhysicsBody (3D)

| Member | Type | Meaning |
|---|---|---|
| `Position` | `Vector3` | World position |
| `Rotation` | `Quaternion` | World rotation |
| `Velocity` | `Vector3` | Linear velocity |
| `AngularVelocity` | `Vector3` | Angular velocity, radians per second |
| `Mass` | `float` | Mass |
| `IsKinematic` | `bool` | The body is kinematic |
| `State` | `BodyState` | Position, rotation, velocity and angular velocity at once |
| `AddForce(Vector3 force)` | | A force, applied over the next step |
| `AddImpulse(Vector3 impulse)` | | An instant change of velocity by `impulse / Mass`; ignored for a kinematic body |
| `AddTorque(Vector3 torque)` | | A torque in world axes, applied over the next step |
| `AddTorqueImpulse(Vector3 torqueImpulse)` | | An instant change of angular velocity through the inertia of the body |
| `AddForceAtPoint(Vector3 force, Vector3 point)` | | A force at a world point: the force plus the torque it causes about the center of mass, over the next step |
| `AddImpulseAtPoint(Vector3 impulse, Vector3 point)` | | An impulse at a world point, changing velocity and angular velocity at once |
| `GetContactPoints(BodyHandle other, List<ContactPointInfo> into)` | `int` | Where the body touches `other` after the last step; see [contact points](queries.md#contact-points) |

## PhysicsBody2D

| Member | Type | Meaning |
|---|---|---|
| `Position` | `Vector2` | World position |
| `Rotation` | `float` | Rotation in radians |
| `Velocity` | `Vector2` | Linear velocity |
| `AngularVelocity` | `float` | Angular velocity, radians per second |
| `Mass` | `float` | Mass |
| `IsKinematic` | `bool` | The body is kinematic |
| `State` | `BodyState2D` | Position, rotation, velocity and angular velocity at once |
| `AddForce(Vector2 force)` | | A force, applied over the next step |
| `AddImpulse(Vector2 impulse)` | | An instant change of velocity by `impulse / Mass`; ignored for a body that is not dynamic |
| `AddTorque(float torque)` | | A torque, positive counterclockwise, applied over the next step |
| `AddTorqueImpulse(float torqueImpulse)` | | An instant change of angular velocity |
| `AddForceAtPoint(Vector2 force, Vector2 point)`, `AddImpulseAtPoint(Vector2 impulse, Vector2 point)` | | As in 3D |
| `GetContactPoints(BodyHandle other, List<ContactPointInfo2D> into)` | `int` | Where the body touches `other` after the last step |

`Vector2`, `Vector3` and `Quaternion` here are the `System.Numerics` types.

## Reading and writing state

Each property setter reads the whole state, changes one part and writes it back, so to change several parts, go through `State` once:

```csharp
PhysicsBody body = NetworkObject.Body;
BodyState state = body.State;
state.Position = new System.Numerics.Vector3(0f, 2f, 0f);
state.Velocity = System.Numerics.Vector3.Zero;
body.State = state;
```

Writing a state moves the body and its transform at once and wakes the body up. Velocity and angular velocity are written only to a dynamic body.

## Forces and impulses

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

A force changes the velocity during the next physics step, which the `NetworkManager` runs in the same tick after input, whereas an impulse changes the velocity at once. Torques follow the same rule: `AddTorque` and `AddForceAtPoint` act during the next step, `AddTorqueImpulse` and `AddImpulseAtPoint` at once. All four do nothing on a kinematic body, wake a sleeping one, and throw `ArgumentException` for a body that is not in the world.

```csharp
PhysicsBody body = NetworkObject.Body;
body.AddForceAtPoint(new System.Numerics.Vector3(0f, 0f, thrust), body.Position + new System.Numerics.Vector3(wingOffset, 0f, 0f));
```

On a locked axis, the Rapier backend drops the impulse at once, while PhysX and Box2D drop it during the next step at the latest. After the step both backends agree.

## Continuous collision

A fast body can pass through a thin collider between two steps. `BodyMotion.ContinuousCollision` and `BodyMotion2D.ContinuousCollision` ask the backend for the strongest continuous detection it has for the body. `BodyDescriptions` sets it from the Collision Detection field: any mode other than Discrete on a `Rigidbody`, and Continuous on a `Rigidbody2D`.

| Backend | Off | On |
|---|---|---|
| `RigidbodyPhysics` 3D | `Discrete` | `ContinuousDynamic` for a dynamic body, `ContinuousSpeculative` for a kinematic one |
| `RigidbodyPhysics` 2D | `Discrete` | `Continuous` |
| Rapier | A fast dynamic body still sweeps against static colliders, but can pass through kinematic and dynamic bodies | Also sweeps against kinematic and dynamic bodies, except other bodies with the flag on |

With the flag off, a fast body therefore stops at a thin static wall under Rapier and can pass it under `RigidbodyPhysics`. The server and its clients use the same backend, so this does not cause corrections.

## Teleporting

To move a body instantly on the server, write its position and tell clients not to interpolate:

```csharp
PhysicsBody body = NetworkObject.Body;
BodyState state = body.State;
state.Position = respawnPoint;
state.Velocity = System.Numerics.Vector3.Zero;
body.State = state;
GetComponent<NetworkTransform>().Teleport();
```

Here `respawnPoint` is a `System.Numerics.Vector3`. [NetworkTransform](../synchronization/transform.md#teleporting) describes what `Teleport()` does on clients.

The [physics overview](overview.md) explains when bodies are stepped, the [physics API reference](../reference/physics.md) lists every member, and [rollback with physics](../prediction/rollback.md) shows bodies in a predicted object.
