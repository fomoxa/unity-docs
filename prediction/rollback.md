# Rollback with physics

When a predicted object moves with a `Rigidbody` or `Rigidbody2D`, its result depends on the whole physics world, including other bodies, contacts and gravity. Correcting it therefore means rolling the physics world back to the corrected tick and stepping it forward again, which the package does when physics simulation is on.

## Requirements

The `RigidbodyPhysics` component of the `NetworkManager` must have Simulate Physics on, both on the server and on the clients, so that the manager steps physics once per tick (see [physics](../physics/overview.md#turning-it-on)). The predicted object must have its `Rigidbody` or `Rigidbody2D` on the same GameObject as its `NetworkObject`. `apply` moves the body through forces, impulses or velocity, and `capture` and `restore` read and write the body through `NetworkObject.Body` or `Body2D`:

```csharp
private void Apply(MoveInput input, InputContext context)
{
    var push = new System.Numerics.Vector3(input.X, 0f, input.Z) * pushStrength;
    NetworkObject.Body.AddImpulse(push);
}

private void Capture(PushState state)
{
    BodyState body = NetworkObject.Body.State;
    state.X = body.Position.X;
    state.Z = body.Position.Z;
    state.VelocityX = body.Velocity.X;
    state.VelocityZ = body.Velocity.Z;
}

private void Restore(PushState state)
{
    PhysicsBody body = NetworkObject.Body;
    BodyState current = body.State;
    current.Position = new System.Numerics.Vector3(state.X, current.Position.Y, state.Z);
    current.Velocity = new System.Numerics.Vector3(state.VelocityX, current.Velocity.Y, state.VelocityZ);
    body.State = current;
}

private static bool Matches(PushState server, PushState predicted) =>
    Math.Abs(server.X - predicted.X) <= 0.01f
    && Math.Abs(server.Z - predicted.Z) <= 0.01f
    && Math.Abs(server.VelocityX - predicted.VelocityX) <= 0.05f
    && Math.Abs(server.VelocityZ - predicted.VelocityZ) <= 0.05f;
```

`PushState` is a model with four `f32` properties, `X`, `Z`, `VelocityX` and `VelocityZ`. `BodyState` and `PhysicsBody` are in `Fomoxa.Networking.Simulation`, and `Math` is `System.Math`. The example moves on the ground plane and leaves the vertical axis to gravity.

## Timeline

Every tick, after stepping physics, the owner's client saves the state of each physics world that holds one of its predicted objects and records the state of each predicted behaviour. The history keeps Prediction History ticks (64 by default).

```text
T0 → T1 → T2 → T3 → T4                  client has predicted up to T4
             ↑
        server state for T2 does not match

Load(T2)                                 every world of the group goes back to T2
restore(server state for T2)
T2 → T3 → T4                             apply input, step every world, capture, save
```

For each tick of the replay, from T3 to T4, `apply` runs for every predicted object of the group and then each world steps once.

## Rollback groups

A replay covers a rollback group, which is the set of physics worlds that the client's predicted objects live in.

```text
Rollback group
 ├── 3D world of scene A
 ├── 3D world of scene B        scenes A and B share one physics scene, so they are one world
 └── 2D world of scene A
```

Each scene with a predicted object brings its 3D world and its 2D world into a group. Two scenes that share a Unity physics scene also share a world, and their groups merge, while groups that share no world are corrected independently.

The tick of a correction is the newest tick with a server state among the group's behaviours. Every predicted object of the group replays, including those whose own state matched, because they live in the worlds that move back.

## No partial loads

A group is loaded only when every world in it has a saved state for the corrected tick, because loading some worlds and not others would put objects of one simulation at different ticks. If one world is missing that tick, for example because its scene was loaded later, no world of the group is loaded. The client still restores the server's states and replays its input, starting from the worlds' current state, but does not save the replayed ticks.

## What a saved state contains

For each world, a saved state holds the position, rotation, velocity, angular velocity and sleep state of every dynamic body that is not a proxy. Kinematic bodies are not saved. The bodies of objects the client does not predict are proxies: the client turns them kinematic and places them at their `NetworkTransform` position every tick, so they are not rolled back and stay where the client shows them.

Spawns and despawns are not replayed either. Bodies created after a saved tick keep their current state when that tick is loaded, and bodies destroyed after it are not recreated.

The physics engine's contact data is not saved, so a replay can differ from the first run even with identical input. Expect occasional corrections, and use tolerances in `matches`.

## Contact events during a replay

[Contact components](../physics/contacts.md) record the contacts of every tick. A replay restores the contacts of the corrected tick and updates them as the worlds step. Only after the replay does it raise enter and exit events, once, for the difference from what was shown before, so the same event is never raised twice.

## Server and host

The server does not save or load physics and simply steps each world once per tick. A host does not predict its own objects and so never rolls back.

Rollback extends [reconciliation](reconciliation.md) to physics. The [physics overview](../physics/overview.md) and [PhysicsBody](../physics/physics-body.md) describe the bodies involved, and [deterministic simulation](../concepts/deterministic-simulation.md) explains why rollback of Unity physics is approximate.
