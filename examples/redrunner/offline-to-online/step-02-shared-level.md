# Step 02: Shared level

## Goal

After this step every process builds the same finite level. The server picks a seed and keeps it as the state of a network object in the scene, and each client builds the level when the seed arrives.

## Starting point

After step 01 the package is installed and `Play.unity` has a `Network Manager`, but the level is still endless and built while the character runs.

## Problem

```
Offline:
TerrainGenerator.Update
  ↓
character near the last block?
  ↓
ChooseFrom (Random.value)
  ↓
next block
```

Online, each process would draw its own random values, so every player would run on different ground and the server would simulate a level that nobody sees. Building only near one character does not work either, because the server has no single character to follow.

The server could send every block, but it does not need to. If the server and every client run the same layout code with the same seed, only the seed has to cross the network.

## Fomoxa concepts

- [State](../../../synchronization/state.md)
- [Scene objects](../../../objects/spawning.md#scene-objects)
- [Models and codecs](../../../messaging/models.md)
- [Channels and reliability](../../../messaging/channels.md)

## Design

```
Server                                  Client
OnStartServer                           OnStartClient / state callback
  ↓                                       ↓
Seed = random                           Seed from LevelState
  ↓                                       ↓
TerrainGenerator.Build(seed)            TerrainGenerator.Build(seed)
  ↓                                       ↓
22 foreground blocks                    the same 22 blocks
         ── LevelState { Seed } ──→
```

`TerrainGenerationSettings.Layout(seed)` turns a seed into a list of blocks with a private `System.Random`, so other code that draws from `UnityEngine.Random` cannot change the layout, and `TerrainGenerator.Build` creates the whole foreground once. The background of hills and clouds never touches a character, so it stays random and is built only on clients, around the local player.

The seed is a model, `LevelState`, used as the state of `NetworkLevel`, a `NetworkBehaviour` on a scene object. The package spawns scene objects when the server starts and sends their state to every client that joins, so the seed reaches late joiners without extra code.

## Files

```
Assets/Scripts/RedRunner/TerrainGeneration/LevelBlock.cs
Assets/Scripts/RedRunner/TerrainGeneration/TerrainGenerationSettings.cs
Assets/Scripts/RedRunner/TerrainGeneration/TerrainGenerator.cs
Assets/Generation Settings.asset
Assets/Scripts/RedRunner/Networking/Models/LevelState.cs
Assets/Scripts/RedRunner/Networking/NetworkLevel.cs
Assets/Scenes/Play.unity
```

## Implementation

### Lay out the level from a seed

`TerrainGenerationSettings` already lists the start, middle and end blocks and how many of each to use. It now gets a method that turns a seed into a layout:

```csharp
public List<LevelBlock> Layout ( int seed )
{
	if ( m_StartBlocksCount <= 0 || m_MiddleBlocksCount <= 0 || m_EndBlocksCount <= 0 )
	{
		throw new System.InvalidOperationException ( name + " needs positive start, middle and end block counts to lay out a seeded level" );
	}
	System.Random random = new System.Random ( seed );
	List<LevelBlock> layout = new List<LevelBlock> ();
	float x = 0f;
	AddBlocks ( layout, m_StartBlocks, m_StartBlocksCount, LevelPart.Start, random, ref x );
	AddBlocks ( layout, m_MiddleBlocks, m_MiddleBlocksCount, LevelPart.Middle, random, ref x );
	AddBlocks ( layout, m_EndBlocks, m_EndBlocksCount, LevelPart.End, random, ref x );
	return layout;
}
```

`AddBlocks` picks each block with `TerrainGenerator.ChooseFrom ( blocks, ( float )random.NextDouble () )`, a new overload that takes the random value as a parameter, and the original `ChooseFrom ( blocks )` now passes `Random.value` to it. `LevelBlock` is a small struct holding the block prefab, its x position and its part of the level.

### Build the level once

Until now, `Generate` added the next foreground block while the character ran. Instead, `Build` now creates every block of the layout and ignores later calls, and `Generate` handles only the background:

```csharp
public virtual void Build ( int seed )
{
	if ( m_Built )
	{
		return;
	}
	m_Built = true;
	foreach ( LevelBlock levelBlock in m_Settings.Layout ( seed ) )
	{
		if ( levelBlock.Part == LevelPart.End && m_EndX <= 0f )
		{
			m_EndX = levelBlock.X;
		}
		CreateBlock ( levelBlock.Prefab, new Vector3 ( levelBlock.X, 0f, 0f ) );
	}
}
```

`Generate` returns early when it has no character to follow, and `Follow ( Character )` sets one; step 05 calls it with the local player. `EndX`, where the end block starts, is used in step 06. `TerrainGenerator` no longer subscribes to `GameManager.OnReset`, because the level now lives as long as the server.

### Make the level finite

In `Assets/Generation Settings.asset`, set Middle Blocks Count to 20 and End Blocks Count to 1. The project has no end block prefab, so add `Assets/Prefabs/Blocks/Start.prefab` to End Blocks, which makes the level end on the same platform it starts on. With the original endless counts, `Layout` throws.

### Add the seed model

`Assets/Scripts/RedRunner/Networking/Models/LevelState.cs`:

```csharp
using Fomoxa;
using Fomoxa.Networking;

namespace RedRunner.Networking.Models
{
    [Network]
    [Codec("net")]
    [NetworkChannel("net", Channel.ReliableOrdered)]
    public class LevelState
    {
        [Network("u32")]
        [Codec("net")]
        public uint Seed { get; set; }
    }
}
```

State must use the reliable ordered channel. Save the file and let Unity compile it before you write `NetworkLevel`, so that the generator writes `LevelStateNetAdapter`, which the behaviour uses.

### Keep the seed on a network object

`Assets/Scripts/RedRunner/Networking/NetworkLevel.cs`, as it was in this step:

```csharp
public sealed class NetworkLevel : NetworkBehaviour
{
    [SerializeField]
    private TerrainGenerator m_Generator;

    private readonly LevelState m_State = new LevelState();

    public uint Seed => m_State.Seed;

    public TerrainGenerator Generator => m_Generator;

    protected override void OnRegisterState(NetworkState state)
    {
        state.Use(LevelStateNetAdapter.Instance, m_State, changed => Build());
    }

    public override void OnStartServer()
    {
        m_State.Seed = (uint)new System.Random().Next(1, int.MaxValue);
        Build();
    }

    public override void OnStartClient()
    {
        Build();
    }

    private void Build()
    {
        if (m_State.Seed != 0)
        {
            m_Generator.Build((int)m_State.Seed);
        }
    }
}
```

On the server, `OnStartServer` picks the seed and builds the level. On a client, the package has already decoded the state into `m_State` by the time it calls `OnStartClient`. The state callback covers a seed that arrives later; it receives the previous value, which is why `Build` reads `m_State` instead. In host mode the server and the client share one instance, and the second `Build` returns at once.

In `Play.unity`, create a root GameObject named `Network Level` with `NetworkObject` and `NetworkLevel`, put the `Terrain Generator` object in the Generator field and save the scene, which gives the `NetworkObject` a scene object id. The package deactivates scene objects when the scene loads and activates them when they spawn, so the level stays empty until a server starts.

The division of work is that Fomoxa sends the state and decodes it on the client, while the game decides what the seed means and builds the level from it in every process.

## Test

Nothing starts a server yet, so start one from a throwaway component in Play Mode:

```csharp
server.ServerManager.StartConnection(0);
```

## Expected result

- On the next frame `NetworkLevel.Seed` is not 0 and the generator reports `IsBuilt`.
- The scene holds 22 foreground blocks at the positions that `Settings.Layout(seed)` lists.
- `Layout` returns the same blocks for the same seed and other blocks for another seed.

The port's own check is `Tools/PortChecks/LevelCheck.cs`.

## Commit

```
Commit: 0b9d85f
Message: Build a finite level from a seed kept on a network object
```

View [`0b9d85f`](https://github.com/fomoxa/RedRunner/commit/0b9d85fb089698c82ec0bcfccede2d7b59028482) on GitHub, then continue with [step 03: player spawning](step-03-player-spawning.md).
