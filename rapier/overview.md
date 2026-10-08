# Rapier physics

`com.fomoxa.networking.rapier` is a physics backend built on [Rapier](https://rapier.rs). It replaces `RigidbodyPhysics` on the `NetworkManager`, so network objects are simulated in Rapier worlds instead of Unity's PhysX and Box2D. It is a separate package in the [networking-rapier](https://github.com/fomoxa/networking-rapier) repository, and a game that is happy with Unity's physics does not need it.

| | |
|---|---|
| Package | `com.fomoxa.networking.rapier` 0.1.0 |
| Requires | `com.fomoxa.networking` 0.1.0 |
| Unity | 6000.5 or later |
| Platforms | Windows x64 and Linux x64: Editor, players and console servers |
| Rapier | `rapier3d` and `rapier2d` 0.36.0, built with `enhanced-determinism` |
| License | Apache-2.0; Rapier and the other linked crates are listed in `Third Party Notices.md` |

## When to use it

Rollback with `RigidbodyPhysics` is approximate. PhysX and Box2D cannot save their contact data, so a replay that starts from a saved tick can drift from the first run, and the client corrects again. [Rollback with physics](../prediction/rollback.md) describes this in detail.

A Rapier snapshot holds the whole world, contacts included, so a replay after `Load` gives the same ticks as the first run. Rapier is pinned to one version and built with `enhanced-determinism`, and the same steps give the same state on Windows and Linux, under Mono and under .NET. That makes two things possible:

- Corrections only happen when the server's input or state really differs from the client's prediction.
- A [console server](../console-server/overview.md) that runs without Unity can simulate the same physics as the Unity clients, because both build their worlds from the same scene file and the same body descriptions.

## How it fits in

```text
Game code: apply, capture, restore, OnTick
    ↓
NetworkObject.Body / Body2D        PhysicsBody, PhysicsBody2D (unchanged)
    ↓
RapierPhysics                      one Rapier world per network scene and dimension
    ↓
fomoxa_rapier (native library)     rapier3d, rapier2d
```

Game code keeps using `PhysicsBody` and `PhysicsBody2D`, input and reconcile models, and the contact components. What changes is underneath:

| | `RigidbodyPhysics` | `RapierPhysics` |
|---|---|---|
| Engine | PhysX and Box2D, through Unity | Rapier, through a native library |
| Worlds | One per Unity physics scene | One per network scene and dimension |
| Static geometry | The colliders in the Unity scene | The scene file of the network scene, plus groups added at runtime |
| Snapshot | Dynamic bodies only, without contacts | The whole world, contacts included |
| `Rigidbody` and `Rigidbody2D` | Simulated by Unity | Switched to kinematic; Rapier writes the pose back to the `Transform` after every tick |
| Simulation on | When Simulate Physics is checked | Always |
| Console server | Not possible | Same worlds through `RapierScenes` |

The server and every client must use the same backend. A client whose backend differs from the server's stops with `StopReason.PhysicsBackendMismatch`.

## Limitations

- Windows x64 and Linux x64 only. macOS, Android, iOS and WebGL clients cannot use this backend.
- IL2CPP players have not been checked for determinism against Mono and .NET.
- Joints, effectors such as `PlatformEffector2D`, continuous collision settings and contact points are not supported.
- One body per network object.

Continue with [setup](setup.md). [Bodies and colliders](bodies.md) describes how Unity objects become Rapier bodies, [contact events](contacts.md) how the contact components behave, and [determinism](determinism.md) what game code must do to keep the simulation the same on every machine.
