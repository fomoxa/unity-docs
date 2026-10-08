# Step 13: Console server

## Goal

This step adds a .NET program in `Server~/` that runs the Red Runner server without Unity. Clients built from the Unity project join it from the start screen as they join the Unity server, and the game plays the same.

## Starting point

The game with its Rapier level built from the catalogue, commit `c44bcfe`.

## Problem

After step 12, every rule the server applies is in `RedRunner.Simulation`, and the level's physics comes from the catalogue. What still needs Unity on the server is the networking glue: `NetworkGame` spawns players, `NetworkLevel` picks the seed, and `NetworkPlayer` applies input, decides deaths and respawns, all as `NetworkBehaviour` components.

## Fomoxa concepts

- [Console server](../../../console-server/overview.md)
- [The project](../../../console-server/project.md)
- [The runtime](../../../console-server/runtime.md), in particular [prefabs](../../../console-server/runtime.md#prefabs) and [boot scenes](../../../console-server/runtime.md#scene-objects-and-boot-scenes)
- [Console physics](../../../console-server/physics.md)

## Design

The console server mirrors the three Unity components:

| Unity | Console | Role |
|---|---|---|
| `NetworkGame` | `ServerGame` | Creates the runtime, spawns a player for each peer that starts, builds the level and moves the hazards |
| `NetworkLevel` on the `Network Level` scene object | `LevelBehaviour`, registered for the type name `RedRunner.Networking.NetworkLevel` | Picks the seed and holds it in `LevelState` |
| `RedRunner.prefab` with `NetworkTransform` and `NetworkPlayer` | `PlayerEntity` with `PlayerTransform` and `PlayerBehaviour` | Sends the pose, applies input, decides deaths and respawns |

`Play.unity` is a boot scene: clients open it before they connect, and its scene file gives the server the `Network Level` scene object and the scene's physics settings. The player's body comes from the catalogue's `CataloguePlayer`, so it matches the body the client builds from the prefab.

## Files

```
Server~/RedRunner.Server.csproj
Server~/Program.cs
Server~/ServerGame.cs
Server~/LevelBehaviour.cs
Server~/PlayerEntity.cs
.gitignore
```

## Implementation

### The project

`Server~/RedRunner.Server.csproj` compiles, as source: layer 1 and the console backend from `com.fomoxa.networking`, `Runtime/Rapier` from `com.fomoxa.networking.rapier`, and the game's `Models`, `Generated` and `Simulation` folders. It copies `LevelCatalogue.bytes`, the scene files as `Scenes/<scene id>.fomoxascene` and the Rapier native libraries next to the executable. It targets .NET 8 with C# 9 and treats warnings as errors. The package folders default to clones next to the RedRunner folder:

```xml
<Game>..</Game>
<Core Condition="'$(Core)' == ''">$(Game)/../com.fomoxa.networking</Core>
<Rapier Condition="'$(Rapier)' == ''">$(Game)/../networking-rapier/com.fomoxa.networking.rapier</Rapier>
```

`.gitignore` leaves out `Server~/bin` and `Server~/obj`.

### The game

`ServerGame` creates the runtime with a tick rate of 50, the Rapier backend and `Play` as a boot scene:

```csharp
var registry = new FomoxaRegistry();
FomoxaAdapters.RegisterAll(registry);
var prefabs = new StandalonePrefabs();
prefabs.Register(FomoxaPrefabs.RedRunnerId, FomoxaPrefabs.RedRunnerFingerprint, () => new PlayerEntity(this));
var behaviours = new StandaloneBehaviours();
behaviours.Register(LevelBehaviour, () => new LevelBehaviour(this));
var settings = new NetworkSettings { TickRate = TickRate, PhysicsBackend = PhysicsBackend.Rapier };
var networkLog = new NetworkLog(exception => log(exception.ToString()), warning => log(warning), error => log(error));
Runtime = StandaloneRuntime.Create(registry, settings, new UdpTransportFactory(), prefabs, behaviours, new SceneFileDirectory(scenes), clock, networkLog, physics, new[] { FomoxaScenes.PlayId });
```

Here `physics` is a `RapierScenes` with gravity (0, -9.81, 0), the same as the clients' `RapierPhysics`. When a peer reaches `Started`, `ServerGame` spawns a `PlayerEntity` in the `Play` scene at the catalogue's spawn point. `TimeManager.OnPreTick` moves the level's hazards to the prediction tick, as `NetworkLevel.MoveFollowers` does in Unity.

`LevelBehaviour.OnStartServer` picks the seed, logs `[RedRunner] level seed <seed>` and builds the level with `BuiltLevel.Build`, through an `ILevelPhysics` that adds the colliders and bodies to `RapierScenes` under the `Play` scene id.

### The player

`PlayerEntity` is a `StandaloneEntity` with two behaviours, in the order of the prefab's `NetworkTransform` and `NetworkPlayer`:

- `PlayerTransform` sends the pose with a `TransformSync` whose settings match the prefab's `NetworkTransform`: position and scale on, rotation off. `PlayerEntity.Scale` returns the facing direction as the X scale, which turns the character on the clients.
- `PlayerBehaviour` registers `PlayerInput`, the `PlayerMotion` reconcile model and `PlayerState`, as `NetworkPlayer` does. Its `Apply` calls `RunnerMotion.Simulate` on the entity's `Body2D`, and its server tick calls `RunnerContacts.Hazard` and the fall check, then respawns after the delay with `PlayerEntity.Teleport()`.

`PlayerEntity.TryGetBody2D` returns the catalogue's body for the player, placed at the entity's position.

### The program

`Program.Main` reads `-port` (7777 by default), `-logFile` and `-log-paths`, loads `LevelCatalogue.bytes` from the executable's folder, and runs the frame loop: `BeginFrame` and `EndFrame` once per millisecond.

## Running it

You need the .NET 8 SDK on Windows x64 or Linux x64. Clone the three repositories next to each other:

```
git clone https://github.com/fomoxa/com.fomoxa.networking.git
git clone https://github.com/fomoxa/networking-rapier.git
git clone https://github.com/fomoxa/RedRunner.git
```

Then start the server from the `RedRunner` folder:

```
dotnet run --project Server~ -c Release -- -port 7777 -logFile server.log
```

The log shows `[RedRunner] server listening on UDP port 7777`, then `[RedRunner] level seed <seed>`. Start the game in the Unity Editor or a player build, type the server's address on the start screen and press Play. With the packages elsewhere, pass their folders as absolute paths with `-p:Core=<folder>` and `-p:Rapier=<folder>`.

## Test

Every Play Mode check that joins a separate server runs against the console server as well: `JoinCheck`, `MoveCheck`, `LifeCheck`, `PathCheck` (with `-log-paths`), `CrowdCheck` and `CrashCheck`. `Tools/unity-windows.sh play-console <check>` builds `Server~` with the Windows .NET SDK, starts it, runs the check in the Editor and stops it again. `PathCheck` compares the server's logged hazard positions with the client's at the same ticks.

## Expected result

- `dotnet run` builds without warnings and the server listens on UDP port 7777.
- A client joins, runs, jumps, dies in water and respawns at the start as with the Unity server.
- Two clients see each other's characters, and the hazards are at the same place on both at the same tick.

## Commit

```
Commit: 125e3b8
Message: Add a .NET console server without Unity
```

View [`125e3b8`](https://github.com/fomoxa/RedRunner/commit/125e3b8f34182d77bb9184f1a5e192460354bc6b) on GitHub. This is the last step of the example.
