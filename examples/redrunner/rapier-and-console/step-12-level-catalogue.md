# Step 12: Level catalogue

## Goal

This step builds the Rapier part of the level from a level catalogue, a file that the Editor exports from the block prefabs. A process without Unity can then build the same physics level from the seed. The game plays as after step 11.

## Starting point

The game with its rules in `RedRunner.Simulation`, commit `d8a30c4`.

## Problem

In step 10 the level's colliders and bodies come from the block prefabs that `TerrainGenerator` instantiates, described with `BodyDescriptions` at runtime. Only Unity can instantiate prefabs and read their colliders. The console server needs the same descriptions in a form it can read, and the client and the server must build them in the same order with the same numbers.

## Fomoxa concepts

- [Models and codecs](../../../messaging/models.md)
- [Console physics: bodies of entities](../../../console-server/physics.md#bodies-of-entities)
- [Scene files](../../../advanced/editor-integration.md#scene-files), whose collider models the catalogue reuses

## Design

The catalogue is a model encoded with its generated codec, so it needs no file format of its own:

| Model | Holds |
|---|---|
| `LevelCatalogue` | The tick length it was exported for, the block counts of each part, the start, middle and end blocks, and the player |
| `CatalogueBlock` | Width and probability; static colliders relative to the block, each with its `Surface` and top; unowned bodies |
| `CatalogueBody` | Position in the block, the body description, the `Surface` and top of each collider, and the path cycle at the game's tick |
| `CataloguePlayer` | The character's body with its ground sensor, the sensor index, the capsule's bottom offset, the running settings, the spawn point, the respawn delay and the limit of repeated ticks |

Colliders and bodies reuse the package's `SceneFileCollider2D` and `SceneFileBody2D` models, which `SceneFileGeometry` converts to and from `ColliderDesc2D` and `BodyDesc2D`. The model folder becomes the assembly `RedRunner.Models` without Unity references, so `RedRunner.Simulation` can use the catalogue types.

`LevelBuilder` in `RedRunner.Simulation` builds the level from the catalogue and the seed through an `ILevelPhysics`, which the Unity game implements with `RapierPhysics` and the console server with `RapierScenes`. The Unity client builds its Rapier level from the catalogue too, and keeps the instantiated prefabs only for display.

## Files

```
Assets/Scripts/RedRunner/Networking/Models/RedRunner.Models.asmdef
Assets/Scripts/RedRunner/Networking/Models/LevelCatalogue.cs
Assets/Scripts/RedRunner/Networking/LevelCatalogue.bytes
Assets/Editor/RedRunner/Networking/LevelCatalogueExport.cs
Assets/Scripts/RedRunner/Simulation/LevelBuilder.cs
Assets/Scripts/RedRunner/Simulation/RedRunner.Simulation.asmdef
Assets/Scripts/RedRunner/Networking/NetworkLevel.cs
Assets/Scripts/RedRunner/Networking/NetworkPlayer.cs
Assets/Scripts/RedRunner/Utilities/PathFollower.cs
Assets/Scenes/Play.unity
Tools/PortChecks/Editor/PortCatalogue.cs
```

## Implementation

### The models

`LevelCatalogue.cs` (abridged):

```csharp
[Network]
[Codec("net")]
public class CatalogueBlock
{
    [Network("f32")]
    [Codec("net")]
    public float Width { get; set; }

    [Network("f32")]
    [Codec("net")]
    public float Probability { get; set; }

    [Network("Array<SceneFileCollider2D>")]
    [Codec("net")]
    public List<SceneFileCollider2D> Statics { get; set; } = new List<SceneFileCollider2D>();

    [Network("Array<CatalogueBody>")]
    [Codec("net")]
    public List<CatalogueBody> Bodies { get; set; } = new List<CatalogueBody>();
}
```

The models are never sent over the network. They only use the generated codec to write and read the file.

### Export

Tools > RedRunner > Export Level Catalogue opens `Play.unity` if needed and reads the tick rate of its `Network Manager`, the spawn point and the generation settings of the `Terrain Generator`. For each block prefab it describes the static colliders and the non-dynamic bodies with the rules of step 10, records the `Surface` and top of each collider, and records the cycle of each path follower at that tick length. For the player it describes `RedRunner.prefab` at the spawn point, with the ground sensor added. It writes `Assets/Scripts/RedRunner/Networking/LevelCatalogue.bytes`, which is committed and assigned to the Catalogue field of `NetworkLevel` in `Play.unity`.

Export the catalogue again whenever a block prefab, the generation settings or the tick rate changes.

### Build the level

```csharp
public static BuiltLevel Build(LevelCatalogue catalogue, int seed, float tickDelta, ILevelPhysics physics)
```

`BuiltLevel.Build` lays out the blocks with `LevelLayout.Lay` from the catalogue's widths and probabilities. For each block in layout order it adds one static group, the catalogue's colliders moved to the block's X, and then each unowned body. It throws when `tickDelta` differs from the catalogue's, because the path cycles are stored per tick. `BuiltLevel` implements `ISurfaces` from the recorded surfaces, and `Move(tick)` puts every moving body at the position of its cycle.

`NetworkLevel` now builds its Rapier level like this:

```csharp
var physics = new RapierLevelPhysics(rapier, gameObject.scene, m_Game.Manager.Scenes.IdOf(gameObject.scene.path));
m_Built = BuiltLevel.Build(Read(m_Catalogue.bytes), (int)m_State.Seed, (float)m_Game.Manager.TimeManager.TickDelta, physics);
```

`RapierLevelPhysics` adds the colliders and bodies with `rapier.AddStatic2D` and `rapier.AddBody2D` and returns `rapier.Scenes.WorldOf2D(sceneId)` as the world. Each path follower of the displayed blocks is driven by the cycle of the catalogue body with the same index, so what the player sees moves with the Rapier body. `NetworkLevel.SurfaceOf`, which `NetworkPlayer` passes to `RunnerContacts`, now answers from `BuiltLevel` instead of looking up Unity colliders.

## Test

`PortCatalogue.Matches` exports the catalogue again in memory and compares it byte for byte with the committed file. It fails with a hint to export again when the prefabs no longer match. `PortLayout.Seeds` and the Play Mode checks of step 10 run unchanged.

## Expected result

- `LevelCatalogue.bytes` is about 240 KB. Most of it holds the path cycles of the moving hazards.
- The game plays as after step 11, and a mace or saw is at the same place on every client at the same tick.

## Commit

```
Commit: c44bcfe
Message: Build the Rapier level from an exported level catalogue
```

View [`c44bcfe`](https://github.com/fomoxa/RedRunner/commit/c44bcfee259504c213a1542353a012b0f07d0805) on GitHub, then continue with [step 13: console server](step-13-console-server.md).
