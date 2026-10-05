# Step 06: Death and respawn

## Goal

After this step only the server decides that a character dies. Clients show the death and the respawn from the server's state, the character respawns at the start two seconds later, and a player who reaches the end block goes back to the start. Coins stay on each client, and the score is removed.

## Starting point

After step 05 every character moves, the owner's by prediction and the others by interpolation. Enemies still kill from their own collision callbacks in every process, though, and the offline end screen and score still exist.

## Problem

```
Offline:
Saw.OnCollisionEnter2D
  ↓
character.Die (true)
  ↓
GameManager: score, end screen, Reset
```

Online, the same collision happens in several processes, and they do not agree. The owner's client predicts its character, so if the server saw the jump one tick earlier, the client's character can touch a saw that the server's character cleared. Other clients see the character two ticks in the past, so their collisions come late. Only the server's collision matches the authoritative position.

If every process ran `Die`, a client could show a death that never happened. A respawn adds a second problem, because the character jumps from the death point to the start in one tick, and both interpolation and prediction treat such a jump like ordinary movement unless they are told otherwise.

Finally, the offline score and end screen assume one main character and a run that ends, and the online game has neither.

## Fomoxa concepts

- [Authority](../../../concepts/authority.md#what-only-the-server-does)
- [State](../../../synchronization/state.md)
- [Tick events](../../../concepts/tick.md#tick-events)
- [Teleporting with NetworkTransform](../../../synchronization/transform.md#teleporting)
- [Teleporting a PhysicsBody](../../../physics/physics-body.md#teleporting)
- [Reconciliation](../../../prediction/reconciliation.md#correction-and-replay)

## Design

```
Server, after each tick (TimeManager.OnTick)
  ↓
collision already called Die? fell below y = 0?
  ↓ yes
PlayerState { Dead = true, Cause }
  ↓ 100 ticks later
Respawn: Reset, body to spawn point, NetworkTransform.Teleport
PlayerState { Dead = false }
        │
        │ state
        ↓
Client: ShowState
  Dead  → character.Die(cause): skeleton, blood, splash
  !Dead → character.Reset()
Owner's client: the jump in position is a prediction mismatch → correction
Other clients: the teleport clears the interpolation buffer
```

Two flags on `Character` decide who acts:

| Flag | Server | Owner's client | Other clients |
|---|---|---|---|
| `DecidesDeath` | true | false | false |
| `CollectsItems` | false | true | false |

In host mode the server sets both flags first and the owner's client then turns `CollectsItems` on, so the host's own character does both.

After this step the work is divided like this:

| Client | Server |
|---|---|
| Input | Deaths and their cause |
| Prediction of its own character | Respawn time and place |
| Death effects, shown from the state | Reaching the end block |
| Coins and chests, for its own character | |

## Files

```
Assets/Scripts/RedRunner/Characters/DeathCause.cs
Assets/Scripts/RedRunner/Characters/Character.cs
Assets/Scripts/RedRunner/Characters/RedCharacter.cs
Assets/Scripts/RedRunner/Enemies/Saw.cs
Assets/Scripts/RedRunner/Enemies/Spike.cs
Assets/Scripts/RedRunner/Enemies/Water.cs
Assets/Scripts/RedRunner/Enemies/Mace.cs
Assets/Scripts/RedRunner/Collectables/Coin.cs
Assets/Scripts/RedRunner/Collectables/Chest.cs
Assets/Scripts/RedRunner/GameManager.cs
Assets/Scripts/RedRunner/Utilities/CameraController.cs
Assets/Scripts/RedRunner/UI/UIScreen/StartScreen.cs
Assets/Scripts/RedRunner/Networking/Models/PlayerState.cs
Assets/Scripts/RedRunner/Networking/NetworkPlayer.cs
Assets/Scenes/Play.unity
```

## Implementation

### Name the cause of a death

A client needs the cause of a death to show the right effect. `DeathCause` is an enum with `Fall`, `Saw`, `Spike`, `Water` and `Mace`, `Character.Die ( bool blood )` becomes `Die ( DeathCause cause )`, and `Character` gets three properties:

```csharp
public virtual DeathCause DeathCause { get; protected set; }

public virtual bool DecidesDeath { get; set; } = true;

public virtual bool CollectsItems { get; set; } = true;
```

Both flags default to true, which matches the offline behavior.

`RedCharacter.Die ( DeathCause cause )` now plays every effect of a death itself: blood for saws, spikes and the mace, the spike sound for spikes and the mace, and the splash for water. Previously the enemy that killed the character played some of these. With all the effects in `Die`, the same call shows a death on the server and on a client. The camera's fast move applies only when the camera follows this character, and the fall check moves out of `RedCharacter.Update` to the server.

### Let only the server kill

Each enemy now checks `DecidesDeath` and passes its cause:

Before:

```csharp
if (character != null) {
	Kill (character);
}
```

After:

```csharp
if (character != null && character.DecidesDeath) {
	Kill (character);
}
```

The example is `Saw`, and `Spike`, `Water` and `Mace` get the same check.

### Keep the death in a state

```csharp
using Fomoxa;
using Fomoxa.Unity;

namespace RedRunner.Networking.Models
{
    [Network]
    [Codec("net")]
    [NetworkChannel("net", Channel.ReliableOrdered)]
    public class PlayerState
    {
        [Network("bool")]
        [Codec("net")]
        public bool Dead { get; set; }

        [Network("u8")]
        [Codec("net")]
        public byte Cause { get; set; }
    }
}
```

`NetworkPlayer` registers this state next to its input and sets the flags when the character starts:

```csharp
protected override void OnRegisterState(NetworkState state)
{
    state.Use(PlayerStateNetAdapter.Instance, m_State, previous => ShowState());
}

public override void OnStartServer()
{
    m_Character.DecidesDeath = true;
    m_Character.CollectsItems = false;
    m_Game.Manager.TimeManager.OnTick += ServerTick;
}

public override void OnStartClient()
{
    m_Character.CollectsItems = NetworkObject.IsOwner;
    if (!m_Game.IsServer)
    {
        m_Character.DecidesDeath = false;
        ShowState();
    }

    if (NetworkObject.IsOwner)
    {
        m_Game.SetLocalPlayer(this);
    }
}
```

`OnStopServer` unsubscribes `ServerTick`. The state callback receives the previous value while `m_State` already holds the new one, so `ShowState` reads `m_State`:

```csharp
private void ShowState()
{
    if (m_Game.IsServer)
    {
        return;
    }

    if (m_State.Dead && !m_Character.IsDead.Value)
    {
        m_Character.Die((DeathCause)m_State.Cause);
    }
    else if (!m_State.Dead && m_Character.IsDead.Value)
    {
        m_Character.Reset();
    }
}
```

### Decide after each tick

`TimeManager.OnTick` is raised after the package has stepped the physics of a tick, so by then the enemies' collision callbacks for that tick have run:

```csharp
private void ServerTick()
{
    TimeManager time = m_Game.Manager.TimeManager;
    if (m_State.Dead)
    {
        if (time.Tick >= m_RespawnTick)
        {
            Respawn();
        }

        return;
    }

    if (!m_Character.IsDead.Value && transform.position.y < 0f)
    {
        m_Character.Die(DeathCause.Fall);
    }

    if (m_Character.IsDead.Value)
    {
        m_State.Dead = true;
        m_State.Cause = (byte)m_Character.DeathCause;
        m_RespawnTick = time.Tick + (uint)Mathf.CeilToInt(m_RespawnDelay * time.TickRate);
        Debug.Log($"[RedRunner] player {NetworkObject.OwnerId} died: {m_Character.DeathCause}");
    }
    else if (TerrainGenerator.Singleton.IsBuilt && transform.position.x >= TerrainGenerator.Singleton.EndX)
    {
        Debug.Log($"[RedRunner] player {NetworkObject.OwnerId} reached the end block");
        Respawn();
    }
}
```

`m_RespawnDelay` is 2 seconds, which is 100 ticks at 50 ticks per second. The respawn tick is counted in server ticks, so it does not depend on the server's frame rate.

### Respawn

```csharp
private void Respawn()
{
    m_Character.Reset();
    PhysicsBody2D body = NetworkObject.Body2D;
    BodyState2D state = body.State;
    state.Position = new System.Numerics.Vector2(m_Game.SpawnPoint.x, m_Game.SpawnPoint.y);
    state.Velocity = System.Numerics.Vector2.Zero;
    body.State = state;
    m_NetworkTransform.Teleport();
    m_Character.RunSmoothVelocity = 0f;
    m_State.Dead = false;
    m_State.Cause = 0;
}
```

`Reset` revives the character and turns its `Rigidbody2D` back on. The body then moves to the spawn point through `NetworkObject.Body2D`, the same view of the body that `Restore` uses, and the run damping velocity resets as well, so the next reconcile state matches a character standing still.

The respawn reaches the two kinds of client differently. Other clients interpolate the character, and `NetworkTransform.Teleport()` tells them that this move is a jump, so they clear their interpolation buffer and place the character at the start. `NetworkPlayer.Awake` keeps the `NetworkTransform` in `m_NetworkTransform` for this call.

The owner's client predicts the character and does not take positions from `NetworkTransform`. Its next reconcile state from the server is far from its prediction, `Matches` returns false, and the client restores the server's motion and replays. The respawn is corrected like any other difference, without code of its own.

The `Teleport()` line was added later, in commit `c75cebd` during step 08, after a check found other clients drawing the character sliding across the level. Commit `a148ea7` has the rest of this method.

### Keep coins and chests on each client

`Coin` and `Chest` react only to a character with `CollectsItems`:

```csharp
if (m_UseOnTriggerEnter2D && character != null && character.CollectsItems) {
	Collect ();
}
```

Each client collects the coins its own character touches. Nobody else sees those coins disappear, and the server ignores them.

### Remove the score

`GameManager` no longer loads or saves coins, scores or the audio setting with SaveGameFree, and there is no main character to score anymore. In `Play.unity`, deactivate `Coin Panel`, `High Score Text` and `Score Text` under `Canvas/In-Game Screen`.

### Leave the start screen cleanly

The start screen's handler for a stopped connection becomes a method, `Network_ClientStateChanged`, which `OnDestroy` unsubscribes. Without that, quitting while connected ran the handler after Unity had already destroyed the screen's `Animator`.

## Test

Join a server and run into the water.

The port has two checks for this step. `HostLifeCheck` starts a host and moves the host's character below the level, checking that it dies of `Fall`, stays dead for the delay and respawns at the start. It then moves the character onto the end block and checks that it returns to the start. `LifeCheck` joins a server process and runs right and jumps until the character dies, checking that the client shows the death only when the server's state says so and then shows the respawn.

## Expected result

The server log names the cause:

```
[RedRunner] player 1 died: Water
```

The skeleton drops, and two seconds later the character stands at the start again. In one run of `LifeCheck` the character died in the water 3.1 seconds after starting, respawned at the start and had collected one coin.

![A character falling into the water](../../../.gitbook/assets/redrunner-death.png)

## Commit

```
Commit: a148ea7
Message: Decide deaths on the server and respawn players at the start
```

View [`a148ea7`](https://github.com/fomoxa/RedRunner/commit/a148ea70ca4eea0ec407c9cd85af57ca1acdf589) on GitHub.

The `Teleport()` call in `Respawn` comes from `c75cebd`, which is listed in step 08.

Continue with [step 07: moving hazards](step-07-moving-hazards.md).
