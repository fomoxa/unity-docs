# PhysicsBody

`PhysicsBody` and `PhysicsBody2D` are the package's view of a network object's physics body, and you use them in `apply`, `capture` and `restore` to read and change the body. They work with `System.Numerics` vectors, so the same code would work with another backend.

```csharp
using Fomoxa.Unity.Simulation;

PhysicsBody body = NetworkObject.Body;
PhysicsBody2D body2D = NetworkObject.Body2D;
```

Both are small structs, so get a fresh one when you need it instead of storing it across spawns.

## When it is valid

`IsValid` is true when three conditions hold: the object has a `Rigidbody` (for `Body`) or a `Rigidbody2D` (for `Body2D`) on the same GameObject as its `NetworkObject`, the object is spawned on this side, and the Physics Backend is `Rigidbody`. Reading or writing an invalid body throws.

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

A force changes the velocity during the next physics step, which the `NetworkManager` runs in the same tick after input, whereas an impulse changes the velocity at once.

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
