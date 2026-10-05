# Physics overview

The package can run Unity's 3D and 2D physics on the network tick. With Simulate Physics on, the `NetworkManager` steps physics once per tick, a client keeps the bodies it does not predict at their replicated positions, and prediction can roll physics back. Game code reaches a network object's body through the package's own types, `PhysicsBody` and `PhysicsBody2D`.

```text
Game code: apply, capture, restore, OnTick
    ↓
NetworkObject.Body / Body2D        PhysicsBody, PhysicsBody2D
    ↓
IPhysicsWorld / IPhysicsWorld2D    one per Unity physics scene, both extend IPhysicsSimulation
    ↓
Backend                            Rigidbody: Unity PhysicsScene and PhysicsScene2D
```

The backend is an implementation detail, and code that uses `PhysicsBody` does not depend on Unity's `Rigidbody` API.

## Turning it on

Turn on Simulate Physics on the `NetworkManager` of the server and of every client. While at least one manager has it on, the package sets `Physics.simulationMode` and `Physics2D.simulationMode` to `Script`, so that Unity no longer steps physics after `FixedUpdate`, and it restores the original modes when the last such manager is destroyed.

From then on, the manager does four things each tick:

1. On a remote client, it places the proxies (described below).
2. It applies input.
3. It steps the 3D and 2D physics world of every loaded scene once, by `TimeManager.TickDelta`.
4. It queries contacts for the [contact components](contacts.md).

`FixedUpdate` still runs at Unity's fixed timestep, but physics no longer advances there, so forces and velocity changes that should be networked belong in `apply` or a tick event.

Set the tick rate to the rate your game's physics was tuned for. A project tuned for a 0.02 s fixed timestep, for example, matches 50 ticks per second.

## One world, one owner

A world is one Unity physics scene, either the 3D `PhysicsScene` or the 2D `PhysicsScene2D` of the scenes that use it. Several scenes share one world unless they are loaded with their own local physics.

Each world has one simulation state and is stepped by exactly one `NetworkManager`, exactly once per tick. The first manager that steps a world owns it, and any other manager in the same process leaves it alone, so a server manager and a client manager in one process never step the same physics twice.

## Predicted and interpolated bodies in one world

On a remote client, a networked object's body plays one of two roles:

| Role | Objects | What the client does |
|---|---|---|
| Predicted | Objects the client owns and predicts | Simulates the body; rolls it back on corrections |
| Proxy | Every other networked object with a body | Makes the body kinematic and places it at its `NetworkTransform` position before each step |

Proxies let predicted bodies collide with other players' objects at the positions the client shows. When an object stops being a proxy, for example because the client becomes its owner, its original body settings come back. The server and the host simulate every body normally.

## Bodies

`NetworkObject.Body` returns a `PhysicsBody` for the object's `Rigidbody`, and `NetworkObject.Body2D` a `PhysicsBody2D` for its `Rigidbody2D`. The body component must be on the same GameObject as the `NetworkObject`. [PhysicsBody](physics-body.md) describes both types.

## Backend

The Physics Backend field selects the backend. `Rigidbody`, the default, uses Unity's built-in 3D and 2D physics and is the only backend implemented. `Rapier` is declared but not implemented, and with it selected, `Body` and `Body2D` return invalid bodies.

The server tells each client which backend it uses, and a client with a different backend stops with `StopReason.PhysicsBackendMismatch` and does not reconnect.

## Without Simulate Physics

With Simulate Physics off, Unity steps physics on its own fixed timestep, independently of ticks. The server's bodies still move and `NetworkTransform` still replicates them, but a client's copies of dynamic bodies keep simulating on their own between updates. There are no proxies, and prediction cannot roll physics back.

## Limitations

Unity physics is not deterministic across machines, and a saved state does not include contact data, so rollback is approximate, as [rollback with physics](../prediction/rollback.md) explains. Joints, character controllers and wheel colliders are not saved or restored.

Each network object has one body, on the GameObject of its `NetworkObject`. Bodies on children are simulated and saved as part of the world, but they have no `PhysicsBody` and are not proxied.

The [PhysicsBody](physics-body.md) and [contact events](contacts.md) pages cover what game code uses, and [physics architecture](architecture.md) describes the interfaces underneath.
