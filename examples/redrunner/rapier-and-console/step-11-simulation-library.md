# Step 11: Simulation library

## Goal

This step moves the game rules out of Unity code into an assembly that does not reference `UnityEngine`, so that a server without Unity can run the same rules. The game plays exactly as after step 10.

## Starting point

The game on the Rapier backend, commit `beb18a4`.

## Problem

After step 10 the rules that decide what happens in a tick are spread over Unity components. `RedCharacter.Simulate` runs and jumps with `Mathf.SmoothDamp` and `transform.localScale`, `NetworkPlayer` reads contact sets and maps them through Unity colliders, `PathFollower` builds its cycle with `Vector3.MoveTowards`, and `TerrainGenerationSettings.Layout` lays out the level with `System.Random`. A console server can compile none of these.

`System.Random` has a second problem. The level is the same on every peer only because each peer draws the same numbers from the seed, and .NET does not promise that `System.Random` keeps its algorithm across versions, while Unity runs Mono and a console server runs .NET.

## Fomoxa concepts

- [Rapier determinism](../../../rapier/determinism.md)
- [Console server: game code shared with Unity](../../../console-server/project.md#game-code-shared-with-unity)

## Design

`Assets/Scripts/RedRunner/Simulation/` becomes the assembly `RedRunner.Simulation`, with `noEngineReferences` on and references to `Fomoxa.Networking` and `Fomoxa.Networking.Rapier`. It holds:

| Type | Replaces |
|---|---|
| `RunnerMotion`, `RunnerSettings` | The networked part of `RedCharacter.Simulate`: running, jumping and rolling on a `PhysicsBody2D` |
| `ISurfaces`, `Surface`, `RunnerContacts` | Grounding and the hazard rules of `NetworkPlayer`, over Rapier contact sets |
| `PathCycle`, `PathStop` | The cycle of a path follower |
| `Smoothing` | `Mathf.SmoothDamp`, `Vector3.SmoothDamp`, `Vector3.MoveTowards` and `Vector3.Lerp`, with Unity's formulas on `System.Numerics` |
| `LevelLayout`, `SeededRandom` | The seeded level layout of `TerrainGenerationSettings` |

The Unity components keep the presentation, animations, particles and sounds, and call into the library for the rules. The single-player methods of `RedCharacter` stay as they were.

## Files

```
Assets/Scripts/RedRunner/Simulation/RedRunner.Simulation.asmdef
Assets/Scripts/RedRunner/Simulation/RunnerMotion.cs
Assets/Scripts/RedRunner/Simulation/Surfaces.cs
Assets/Scripts/RedRunner/Simulation/PathCycle.cs
Assets/Scripts/RedRunner/Simulation/Smoothing.cs
Assets/Scripts/RedRunner/Simulation/LevelLayout.cs
Assets/Scripts/RedRunner/Simulation/SeededRandom.cs
Assets/Scripts/RedRunner/Characters/RedCharacter.cs
Assets/Scripts/RedRunner/Networking/NetworkPlayer.cs
Assets/Scripts/RedRunner/Networking/NetworkLevel.cs
Assets/Scripts/RedRunner/Utilities/PathFollower.cs
Assets/Scripts/RedRunner/TerrainGeneration/TerrainGenerationSettings.cs
Tools/PortChecks/Editor/PortLayout.cs
```

## Implementation

### The assembly

`RedRunner.Simulation.asmdef` (abridged; the other fields have their defaults):

```json
{
    "name": "RedRunner.Simulation",
    "rootNamespace": "RedRunner.Simulation",
    "references": [
        "Fomoxa.Networking",
        "Fomoxa.Networking.Rapier"
    ],
    "autoReferenced": true,
    "noEngineReferences": true
}
```

`autoReferenced` lets the game's own scripts in `Assembly-CSharp` use it without an assembly definition of their own. The code in the folder is limited to C# 9, the version Unity compiles.

### Character motion

`RunnerMotion.Simulate` takes the body, the settings, the input, whether the character is grounded and whether it is dead, and returns which actions happened so that Unity can play their effects:

```csharp
public RunnerActions Simulate(PhysicsBody2D body, in RunnerSettings settings, float move, bool jump, bool roll, bool grounded, bool dead, float deltaTime)
```

The facing direction, which used to be the sign of `transform.localScale.x`, is now `RunnerMotion.Facing`, and `RedCharacter` applies it to the scale for display. `NetworkPlayer` sets `BodySource` with either backend now, because the motion always goes through `PhysicsBody2D`; with `RigidbodyPhysics`, `NetworkObject.Body2D` is the character's PhysX body.

### Contacts

`RunnerContacts.Grounded(world, body, sensorIndex, surfaces, scratch)` and `RunnerContacts.Hazard(world, body, colliderCount, bottom, surfaces, scratch)` read the contact sets with `RapierWorld2D.Touching` and ask an `ISurfaces` what each collider is. `NetworkLevel` implements `ISurfaces` from the source colliders it recorded in step 10, and `NetworkPlayer` turns the `Surface` that `Hazard` returns into a `DeathCause`.

### The level layout

`LevelLayout.Lay(seed, ...)` lays out blocks from their widths and probabilities, as `TerrainGenerationSettings.Layout` did, but draws its numbers from `SeededRandom`, a SplitMix64 generator with integer arithmetic only:

```csharp
public ulong NextBits()
{
    state += Golden;
    ulong mixed = state;
    mixed = (mixed ^ (mixed >> 30)) * 0xBF58476D1CE4E5B9UL;
    mixed = (mixed ^ (mixed >> 27)) * 0x94D049BB133111EBUL;
    return mixed ^ (mixed >> 31);
}
```

A seed therefore gives a different layout than before this step. The server picks a new seed at every start, so nothing stored depends on the old layout.

## Test

`PortLayout.Seeds` lays out five seeds and compares a hash of each layout with the value computed under .NET 8, which shows that Mono in the Editor and .NET lay out the same level. The Play Mode checks of step 10 run unchanged, because the rules did not change. Outside Unity, `dotnet build` of a project that compiles the folder succeeds.

## Expected result

- The project compiles, and `RedRunner.Simulation` shows no reference to `UnityEngine`.
- The game plays as after step 10, on a new layout for each seed.

## Commit

```
Commit: d8a30c4
Message: Move the game simulation into RedRunner.Simulation
```

View [`d8a30c4`](https://github.com/fomoxa/RedRunner/commit/d8a30c4e8f1baef53fc3125eddeb5a6b9d63c93d) on GitHub, then continue with [step 12: level catalogue](step-12-level-catalogue.md).
