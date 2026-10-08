# Console server

A console server is a .NET program that runs the server of a game without the Unity Engine. Unity clients connect to it as they connect to a Unity server: the same transports, the same handshake and the same messages. The host only needs the .NET runtime, and the server process carries nothing of Unity's player.

The game logic has to be written twice for it, once as `NetworkBehaviour` components for Unity and once as `EntityBehaviour` classes for the console, or moved into a library without Unity references that both call. Read this section if that trade is worth it for your game. Otherwise run the server as a Unity player, as described in [dedicated server](../server/dedicated-server.md).

## What it is made of

```text
Your console program: Main, game rules as EntityBehaviour classes
    ↓
Console backend: StandaloneRuntime, StandaloneEntity       com.fomoxa.networking/Standalone~ (source)
    ↓
Layer 1: Fomoxa.Networking                                 com.fomoxa.networking/Runtime/Core (source)
    ↓
Fomoxa.Net, Fomoxa.Attributes                              com.fomoxa.networking/Runtime/Plugins
```

The package ships the console backend as source in `Standalone~`, a folder that Unity does not import. A console project compiles it together with the source of layer 1, the generated code of the Unity project and its own code. The Unity project stays the source of the models, the prefab ids and fingerprints, and the scene files.

| In Unity | In a console server |
|---|---|
| `NetworkManager` | `NetworkRuntime`, created by `StandaloneRuntime.Create` and driven by your own loop |
| `NetworkObject` on a prefab | `StandaloneEntity` or a subclass, created by a factory registered for the prefab id |
| `NetworkBehaviour` | `EntityBehaviour`, with the same callbacks and registrations |
| `NetworkTransform` | `EntityBehaviour.SyncTransform` with a `TransformSync` |
| Network scenes and scene objects | Scene files read from a folder; scene objects are built from the file |
| `RigidbodyPhysics` | No Unity physics. Physics comes from an `IPhysicsScenes` such as [Rapier](../rapier/overview.md)'s `RapierScenes` |

The backend also has a client side, so a console program can connect to a server as a client, for example to run bots or tests.

## Requirements

- The .NET 8 SDK or later, on any platform where Fomoxa.Net runs. With the Rapier backend, Windows x64 or Linux x64.
- A Unity project that has generated its code and exported its [scene files](../unity/editor-integration.md#scene-files), with `com.fomoxa.networking` installed from Git or cloned, so that its source is available to the console project.
- C# 9. Layer 1 and the console backend are written for the C# version Unity compiles, so the console project sets `LangVersion` to 9.0.

## Limitations

- The game rules that the server runs have to exist as `EntityBehaviour` classes. The package cannot run a `NetworkBehaviour` without Unity.
- The server's entities must match the client's prefabs: same prefab id, same fingerprint, and behaviours in the same order with the same models, as described in [runtime](runtime.md#prefabs).
- There is no `NetworkAnimator` and no host mode on the console. The console backend draws nothing and hides nothing.
- Without a physics backend, entities have no bodies, and prediction of physics does not apply.

Continue with [the project](project.md).
