# Rapier and a console server

The [offline to online](../offline-to-online/README.md) migration ends with a game that runs on Unity's 2D physics and a Unity server. This part continues from there in four steps. It moves the game onto the [Rapier backend](../../../rapier/overview.md), takes the game rules out of Unity code, and adds a [console server](../../../console-server/overview.md) that runs the same game without Unity.

The game plays the same at the end. What changes is underneath:

- Prediction replays reproduce the server's physics exactly, because Rapier saves and restores its whole world, contacts included.
- The rules for running, jumping, grounding, deaths and moving hazards live in a `RedRunner.Simulation` assembly without Unity references, which the Unity game and the console server both call.
- The level's physics is built from an exported level catalogue instead of from the prefabs, so a process without Unity can build it.
- A .NET program in `Server~/` runs the server. Unity clients join it through the same start screen.

## Steps

| Step | What it adds | Main Fomoxa pages |
|---|---|---|
| [10 Rapier backend](step-10-rapier-backend.md) | `RapierPhysics` on the `Network Manager`, the level as static groups and unowned bodies, grounding and deaths from contact sets | [Rapier setup](../../../rapier/setup.md), [Bodies and colliders](../../../rapier/bodies.md) |
| [11 Simulation library](step-11-simulation-library.md) | The game rules in `RedRunner.Simulation`, a seeded random generator of its own | [Rapier determinism](../../../rapier/determinism.md) |
| [12 Level catalogue](step-12-level-catalogue.md) | `RedRunner.Models`, an exported catalogue of blocks, bodies and paths, `LevelBuilder` | [Console physics](../../../console-server/physics.md) |
| [13 Console server](step-13-console-server.md) | `Server~/`, a .NET server built on the console backend and `RapierScenes` | [Console server](../../../console-server/overview.md) |

## Commits

| Step | Commit |
|---|---|
| 10 | [`beb18a4`](https://github.com/fomoxa/RedRunner/commit/beb18a475db7cd27e9db29271c7bb1cb465f45e3) Run the online game on the Rapier physics backend |
| 11 | [`d8a30c4`](https://github.com/fomoxa/RedRunner/commit/d8a30c4e8f1baef53fc3125eddeb5a6b9d63c93d) Move the game simulation into RedRunner.Simulation |
| 12 | [`c44bcfe`](https://github.com/fomoxa/RedRunner/commit/c44bcfee259504c213a1542353a012b0f07d0805) Build the Rapier level from an exported level catalogue |
| 13 | [`125e3b8`](https://github.com/fomoxa/RedRunner/commit/125e3b8f34182d77bb9184f1a5e192460354bc6b) Add a .NET console server without Unity |

The steps start from [`f164d56`](https://github.com/fomoxa/RedRunner/commit/f164d5624f171b64c8bfc6f029b12be2cfe41e27), the end of the first part. Unlike the first part, each page shows the code as it is at its own commit, and a later step names what it changes.

## Requirements

- Everything the first part needs, on a Windows x64 or Linux x64 machine, since the Rapier backend has native libraries for those two only.
- The .NET 8 SDK, from step 13 on.
- The checks of these steps run against the Rapier backend with `Tools/unity-windows.sh`, as in the first part. Step 13 adds `play-console`, which runs the same Play Mode checks against the console server.

## Troubleshooting

- A client stops right after joining with `PhysicsBackendMismatch`: the client and the server use different physics components. Every `Network Manager` of the build, and the console server's `NetworkSettings.PhysicsBackend`, must use Rapier.
- The Console warns `scene 0x... has no scene file`: export the network scene files with Tools > Fomoxa > Export Network Scene Files and commit `Generated/<scene id>.fomoxascene`.
- Characters sink through the level or fall at the start: the level was not added to Rapier. `NetworkLevel` must build it in both `OnStartServer` and `OnStartClient`, after the seed arrives, and in the same order on every peer.
- `the level catalogue was exported for a tick of ... s, the game ticks every ... s`: the tick rate of the `Network Manager` changed after the catalogue was exported. Export it again with Tools > RedRunner > Export Level Catalogue.
- The console server prints `behaviour type ... is not registered with StandaloneBehaviours`: a scene object of `Play.unity` got a new `NetworkBehaviour`. Register a console behaviour for its type name in `ServerGame`.
- The client fails the handshake with `SchemaConflict` against the console server: the console server was built from other generated code. Let Unity generate, then build `Server~` again.

Start with [step 10: Rapier backend](step-10-rapier-backend.md).
