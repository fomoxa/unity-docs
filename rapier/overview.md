# Rapier physics

`com.fomoxa.networking.rapier` is a physics backend built on [Rapier](https://rapier.rs). It replaces `RigidbodyPhysics` on the `NetworkManager`, so network objects are simulated in Rapier worlds instead of Unity's PhysX and Box2D. It is a separate package in the [networking-rapier](https://github.com/fomoxa/networking-rapier) repository, and a game that is happy with Unity's physics does not need it.

| | |
|---|---|
| Package | `com.fomoxa.networking.rapier` 0.2.0 |
| Requires | `com.fomoxa.networking` 0.3.0 |
| Unity | 6000.5 or later |
| Platforms | Windows x64 and arm64, Linux x64 and arm64, macOS, Android `arm64-v8a` and `armeabi-v7a`, iOS, Web; see [setup](setup.md#platforms) |
| Rapier | `rapier3d` and `rapier2d` 0.36.0, built with `enhanced-determinism` |
| License | Apache-2.0; Rapier and the other linked crates are listed in `Third Party Notices.md` |

## When to use it

Rollback with `RigidbodyPhysics` is approximate. PhysX and Box2D cannot save their contact data, so a replay that starts from a saved tick can drift from the first run, and the client corrects again. [Rollback with physics](../prediction/rollback.md) describes this in detail.

A Rapier snapshot holds the whole world, contacts included, so a replay after `Load` gives the same ticks as the first run. Rapier is pinned to one version and built with `enhanced-determinism`, and the same steps give the same state on every platform that has been checked, under Mono, IL2CPP and .NET. That makes two things possible:

- Corrections only happen when the server's input or state really differs from the client's prediction.
- A [console server](../console-server/overview.md) that runs without Unity can simulate the same physics as the Unity clients, because both build their worlds from the same scene file and the same body descriptions.

Rapier also reports which bodies moved in each step. The server reads the transform of a network object only when it changed, so objects at rest cost the server no transform reads. With `RigidbodyPhysics`, every `NetworkTransform` is read after every tick, as described in [NetworkTransform](../synchronization/transform.md#server-behavior).

## How it fits in

<figure><img src="../.gitbook/assets/diagrams/rapier-stack.svg" alt="In a Unity client or server, game code with apply, capture, restore and OnTick uses PhysicsBody and PhysicsBody2D, which are unchanged, and those use RapierPhysics, with one world per network scene and dimension. In a console server without Unity, your console program with EntityBehaviour classes and the same models uses RapierScenes, which builds the same worlds from the same scene file. Both sit on the native library fomoxa_rapier, built from rapier3d and rapier2d 0.36.0 with enhanced-determinism. A snapshot holds the whole Rapier world, contacts included, so a replay gives the same ticks as the first run."><figcaption><p>Game code stays the same; only the layers under PhysicsBody change.</p></figcaption></figure>

Game code keeps using `PhysicsBody` and `PhysicsBody2D`, input and reconcile models, and the contact components. What changes is underneath:

| | `RigidbodyPhysics` | `RapierPhysics` |
|---|---|---|
| Engine | PhysX and Box2D, through Unity | Rapier, through a native library |
| Worlds | One per Unity physics scene | One per network scene and dimension |
| Static geometry | The colliders in the Unity scene | The scene file of the network scene, plus groups added at runtime |
| Snapshot | Dynamic bodies only, without contacts | The whole world, contacts included |
| `Rigidbody` and `Rigidbody2D` | Simulated by Unity | Switched to kinematic; Rapier writes the pose back to the `Transform` after every tick |
| Transforms read by the server | Every `NetworkTransform`, after every tick | A `NetworkTransform` on the object with the body only when it changed, unless Sync Scale is on |
| Simulation on | When Simulate Physics is checked | Always |
| Console server | Not possible | Same worlds through `RapierScenes` |

The server and every client must use the same backend. A client whose backend differs from the server's stops with `StopReason.PhysicsBackendMismatch`.

## What it supports

| Area | Page |
|---|---|
| Bodies and colliders, several bodies per network object, continuous collision | [Bodies and colliders](bodies.md) |
| Rays, shape casts, overlaps, contact points, forces and torques | [Physics queries](../physics/queries.md) and [PhysicsBody](../physics/physics-body.md), the same API as `RigidbodyPhysics` |
| Contact components | [Contact events](contacts.md) |
| Unity joint components and joints created from code | [Joints](joints.md) |
| Moving a kinematic character along walls, steps and slopes | [Character controller](character-controller.md) |
| The five 2D effectors of Unity | [Effectors](effectors.md) |

## Limitations

- `CharacterController`, `WheelCollider`, `ConfigurableJoint`, `WheelJoint2D`, `RelativeJoint2D`, `TargetJoint2D` and `FrictionJoint2D` are not supported, and 3D has no effectors because Unity has no 3D effector components.
- Joints do not break.
- The Web library does not work with Enable C/C++ Native Multithreading.
- Players on Linux, macOS and iOS have not been run with the hash check that the Windows, Web and Android players pass. See [determinism](determinism.md#checked-platforms).

Continue with [setup](setup.md). [Determinism](determinism.md) describes what game code must do to keep the simulation the same on every machine.
