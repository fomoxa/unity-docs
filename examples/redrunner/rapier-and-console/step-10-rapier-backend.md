# Step 10: Rapier backend

## Goal

This step runs the online game on the Rapier physics backend. The server and the clients simulate the character, the level and the moving hazards in Rapier worlds, and the server decides deaths from Rapier contact sets instead of PhysX callbacks.

## Starting point

The online game at the end of the first part, commit `f164d56`, with a `RigidbodyPhysics` on the `Network Manager`.

## Problem

With `RigidbodyPhysics`, a replay on the owner's client starts from a saved state without contacts, so after a correction the character can land a little differently and be corrected again. Rapier saves its whole world, but switching to it changes three things the game relied on:

- Rapier builds static geometry from the scene file, which only knows the colliders saved in `Play.unity`. The level's blocks are instantiated at runtime from the seed, so Rapier does not see them.
- Rapier moves bodies itself and writes their poses back to the `Transform`, so code that sets `Rigidbody2D.linearVelocity` or calls `AddForce` no longer moves the character.
- Enemies kill the character from `OnCollisionEnter2D` and `OnTriggerEnter2D`, and the ground check casts rays, all through Unity's physics. Under Rapier the character is moved by Rapier, so the server should decide deaths and grounding from Rapier's contacts.

## Fomoxa concepts

- [Rapier setup](../../../rapier/setup.md)
- [Bodies and colliders](../../../rapier/bodies.md), in particular [reading the worlds](../../../rapier/bodies.md#reading-the-worlds)
- [Geometry and bodies added at runtime](../../../physics/overview.md#geometry-and-bodies-added-at-runtime)
- [PhysicsBody](../../../physics/physics-body.md)

## Design

`NetworkLevel` adds the level to Rapier after it builds the blocks from the seed, on the server and on every client, in the order of the blocks' X position. Each block becomes a static group of its colliders. Its non-dynamic `Rigidbody2D` objects become unowned bodies: spikes are static bodies, and maces and saws are kinematic bodies that `NetworkLevel` moves to the position of the tick. Coins and chests stay out of Rapier, because they are local decoration.

The character moves through its `PhysicsBody2D`. The ground check asks a foot sensor which colliders it touches, and the server asks the character's colliders which hazards they touch. To turn a `RapierCollider` back into the Unity collider it came from, `NetworkLevel` keeps a table from static index and body handle to the source colliders.

## Files

```
Packages/manifest.json
Assets/Scenes/Play.unity
Assets/Scripts/RedRunner/Networking/NetworkLevel.cs
Assets/Scripts/RedRunner/Networking/NetworkPlayer.cs
Assets/Scripts/RedRunner/Characters/RedCharacter.cs
Assets/Scripts/RedRunner/Utilities/GroundCheck.cs
```

## Implementation

### Install the backend

Add the package from its Git URL, as described in [Rapier setup](../../../rapier/setup.md#install-the-package). `Packages/manifest.json` then has:

```json
"com.fomoxa.networking.rapier": "https://github.com/fomoxa/networking-rapier.git?path=com.fomoxa.networking.rapier",
```

On the `Network Manager` in `Play.unity`, remove `RigidbodyPhysics`, add `RapierPhysics` with the default gravity, and drag it into the Physics field. The character's gravity scale of 1.5 and its frozen rotation come from its `Rigidbody2D`, which the backend reads into the body description.

### Add the level to Rapier

`NetworkLevel.cs`, after `m_Generator.Build`:

```csharp
private void AddToRapier(RapierPhysics rapier)
{
    foreach (PathFollower follower in m_Followers)
    {
        if (!follower.TryGetComponent(out Rigidbody2D _))
        {
            follower.gameObject.AddComponent<Rigidbody2D>().bodyType = RigidbodyType2D.Kinematic;
        }
    }

    foreach (Block block in FindObjectsByType<Block>(FindObjectsSortMode.None).OrderBy(block => block.transform.position.x))
    {
        AddStatics(rapier, block.gameObject);
        AddBodies(rapier, block.gameObject);
    }

    World = rapier.Scenes.WorldOf2D(m_Game.Manager.Scenes.IdOf(gameObject.scene.path));
}
```

A path follower gets a kinematic `Rigidbody2D` so that its colliders count as a body instead of static geometry. `AddStatics` describes the static colliders of a block with `BodyDescriptions.StaticColliders2D` and `DescribeStatic2D`, skips those of collectables, and adds them with `rapier.AddStatic2D(gameObject.scene, colliders)`; it records the source collider of each index from `StaticGroup.FirstIndex` on. `AddBodies` describes each non-dynamic `Rigidbody2D` of the block with `BodyDescriptions.TryDescribe2D` and adds it with `rapier.AddBody2D`, keyed by the body's handle.

Each tick, `MoveFollowers` puts the body of each mace and saw at the position of its cycle for the tick, and moves its `Transform` there too, because PhysX no longer moves it:

```csharp
Vector3 position = follower.PositionAt(tick);
BodyState2D state = body.State;
state.Position = new System.Numerics.Vector2(position.x, position.y);
body.State = state;
follower.transform.position = position;
```

### Move the character through its body

`RedCharacter` gets a `BodySource` that returns the character's `PhysicsBody2D`. Its velocity reads and writes, and the roll force, go through that body when it is valid:

```csharp
Fomoxa.Networking.Simulation.PhysicsBody2D body = BodySource ();
if ( body.IsValid )
{
    body.Velocity = new System.Numerics.Vector2 ( value.x, value.y );
    return;
}
```

`NetworkPlayer.Awake` sets `BodySource` to `NetworkObject.Body2D` when the `Network Manager` has a `RapierPhysics`.

### Ground and hazards from contact sets

`GroundCheck` gets a `Probe`, which replaces its three rays when set. `NetworkPlayer` adds a trigger `Ground Sensor` below the character's ground collider, as wide as that collider and as tall as the ray distance, and sets the probe to:

```csharp
private bool Grounded()
{
    if (!TryGetContacts(m_Sensor))
    {
        return false;
    }

    foreach (RapierCollider other in m_Touching)
    {
        Collider2D source = m_Level.SourceOf(other);
        if (source != null && source.gameObject.layer == LayerMask.NameToLayer(GroundName) && source.CompareTag(GroundName))
        {
            return true;
        }
    }

    return false;
}
```

`TryGetContacts` finds the index of each of the character's colliders with `BodyDescriptions.TryDescribe2D(gameObject, out _, m_Sources)` and calls `World.Touching(RapierCollider.OfBody(body.Handle, index), m_Touching)`.

On the server, `RedCharacter.DecidesDeath` is now false under Rapier, and `NetworkPlayer.ServerTick` calls `DieOfHazards` before the fall check. It looks up the `Enemy` above each touching source collider: water, saws and maces kill at once, and a spike kills when the bottom of the character's capsule is no more than 0.2 below the spike's top.

### Dead bodies and respawns

PhysX stopped simulating a dead character, because the skeleton turns its `Rigidbody2D` off. Rapier keeps simulating the body, which then sinks through the water and drags the interpolated character of other clients down with it. `HoldWhileDead` keeps the body at the position where it died, with no velocity, on the server and on the predicting client.

`RapierPhysics` writes the `Transform` after the physics step, while `NetworkTransform.Teleport()` takes the current `Transform`. `Respawn` therefore moves the `Transform` to the spawn point together with the body, before it calls `Teleport()`.

## Test

Run the same tests as at the end of the first part, now with `RapierPhysics` on every `Network Manager`: join a dedicated server with two clients, run into water and onto a saw, wait for the respawn, and watch a mace from both clients. The port's checks are the Play Mode checks of the first part (`JoinCheck`, `MoveCheck`, `LifeCheck`, `PathCheck`, `CrowdCheck`, `CrashCheck` and the host checks), run with this backend; `PortSetup.RapierBackend` sets up the `Network Manager`.

## Expected result

- The Console shows no `[Fomoxa]` warning about scene files and no exceptions from `RapierPhysics`.
- The character runs, jumps, rolls and dies as before, and respawns at the start without sliding across the level on other clients.
- A mace or a saw is at the same place on every client at the same tick.
- The `Rigidbody2D` of a character shows as kinematic in the Inspector while the game runs.

## Commit

```
Commit: beb18a4
Message: Run the online game on the Rapier physics backend
```

View [`beb18a4`](https://github.com/fomoxa/RedRunner/commit/beb18a475db7cd27e9db29271c7bb1cb465f45e3) on GitHub, then continue with [step 11: simulation library](step-11-simulation-library.md).
