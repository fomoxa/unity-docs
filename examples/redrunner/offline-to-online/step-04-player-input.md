# Step 04: Player input

## Goal

After this step each client sends its player's keys to the server once per tick, and the server moves the character with them. To make that possible, the character's movement becomes a tick step that the server and the client can both run.

## Starting point

After step 03 the server spawns a character for every client, and each client knows which one is its own. Since `RedCharacter.Update` no longer reads the keyboard, nothing moves yet.

## Problem

```
Offline:
RedCharacter.Update (every frame)
  ↓
reads CrossPlatformInputManager
  ↓
Move, Jump, roll force with Time.deltaTime
```

```
Online:
Owner's client, every tick
  ↓
Gather: read the keys into PlayerInput
  ↓
Fomoxa input frames
  ↓
Server, at the input's tick
  ↓
Apply: RedCharacter.Simulate with the tick length
```

Three things keep the offline controller from running on the server:

- It reads the keyboard of the process it runs in, and the server has no player at its keyboard.
- It runs per frame with the frame time, while the server ticks 50 times per second independently of frames. In step 05 the client will also have to run the same step again for ticks it has already shown.
- It plays sounds, particles and animator triggers in the middle of the physics, and a replayed tick must not play them twice.

## Fomoxa concepts

- [Input](../../../prediction/input.md)
- [Authority](../../../concepts/authority.md#what-a-client-can-send)
- [Ticks and timing](../../../concepts/tick.md)
- [NetworkBehaviour registration hooks](../../../core/network-behaviour.md#registration-hooks)

## Design

The input of one tick is a model, `PlayerInput`, holding the horizontal axis and two buttons. `NetworkPlayer` registers it in `OnRegisterInput` with two callbacks:

| Callback | Runs on | Does |
|---|---|---|
| `Gather` | The owner's client, once per tick | Fills `PlayerInput` from the keys |
| `Apply` | The server at the input's tick, and the owner's client when it predicts | Calls `RedCharacter.Simulate` |

`RedCharacter.Simulate` is the tick step. It takes the axis, the buttons, the tick length and whether to play effects. The client only sends input, and the server decides where the character ends up.

## Files

```
Assets/Scripts/RedRunner/Networking/Models/PlayerInput.cs
Assets/Scripts/RedRunner/Characters/RedCharacter.cs
Assets/Scripts/RedRunner/Utilities/GroundCheck.cs
Assets/Scripts/RedRunner/Networking/NetworkPlayer.cs
```

## Implementation

### Add the input model

```csharp
using Fomoxa;

namespace RedRunner.Networking.Models
{
    [Network]
    [Codec("net")]
    public class PlayerInput
    {
        [Network("f32")]
        [Codec("net")]
        public float Move { get; set; }

        [Network("bool")]
        [Codec("net")]
        public bool Jump { get; set; }

        [Network("bool")]
        [Codec("net")]
        public bool Roll { get; set; }
    }
}
```

An input model needs no `[NetworkChannel]`, because the package carries it in its own input frames. Save the file and let the generator write `PlayerInputNetAdapter` before you write `NetworkPlayer`.

### Turn the controller into a tick step

```csharp
public virtual void Simulate ( float horizontalAxis, bool jump, bool roll, float deltaTime, bool effects )
{
	float speed = Mathf.Abs ( m_Rigidbody2D.linearVelocity.x );
	m_CurrentRunSpeed = m_RunSpeed;
	if ( speed >= m_RunSpeed )
	{
		m_CurrentRunSpeed = Mathf.SmoothDamp ( speed, m_MaxRunSpeed, ref m_CurrentSmoothVelocity, m_RunSmoothTime, Mathf.Infinity, deltaTime );
	}
	Move ( horizontalAxis );
	if ( jump )
	{
		Jump ( effects );
	}
	if ( roll )
	{
		Roll ( effects );
	}
}
```

The offline `Update` called `Mathf.SmoothDamp` without a time argument, so it used the frame time, whereas `Simulate` passes the tick length.

`Jump ( bool effects )` plays the animator trigger, the particles and the sound only when `effects` is true. It also tests the ground at the moment it runs:

Before:

```csharp
if ( m_GroundCheck.IsGrounded )
```

After:

```csharp
if ( m_GroundCheck.Check () )
```

`IsGrounded` is only updated once per frame, but during a replay the character is at an earlier position, so the test has to run at that moment. `GroundCheck.Update` now calls `Check ()` as well.

Rolling becomes `Roll ( bool effects )`. The offline code pushed along `localScale.z`, which is always 1, so the character always rolled right. The port pushes along `localScale.x`, the direction the character faces:

```csharp
m_Rigidbody2D.AddForce ( new Vector2 ( Mathf.Sign ( transform.localScale.x ) * m_RollForce, 0f ) );
```

### Gather and apply

The input half of `NetworkPlayer`, as committed:

```csharp
protected override void OnRegisterInput(NetworkInput input)
{
    input.Use(PlayerInputNetAdapter.Instance, Gather, Apply);
    input.Reconcile(PlayerMotionNetAdapter.Instance, Capture, Restore, Matches);
}

private void Update()
{
    if (NetworkObject == null || !NetworkObject.IsOwner)
    {
        return;
    }

    m_JumpPressed |= CrossPlatformInputManager.GetButtonDown("Jump");
    m_RollPressed |= CrossPlatformInputManager.GetButtonDown("Roll");
}

private void Gather(PlayerInput input)
{
    bool playing = GameManager.Singleton.gameRunning;
    input.Move = playing ? CrossPlatformInputManager.GetAxis("Horizontal") : 0f;
    input.Jump = playing && m_JumpPressed;
    input.Roll = playing && m_RollPressed;
    m_JumpPressed = false;
    m_RollPressed = false;
}

private void Apply(PlayerInput input, InputContext context)
{
    float tickDelta = (float)m_Game.Manager.TimeManager.TickDelta;
    bool fresh = !context.Repeated;
    m_Character.Simulate(input.Move, fresh && input.Jump, fresh && input.Roll, tickDelta, !context.Replaying);
}
```

`Update` runs every frame and keeps button presses until the next `Gather`, so a press shorter than a tick is not lost. While the pause screen is open, `gameRunning` is false and the input is empty, so the character stops while the server and the other players keep going.

On the server, `Apply` runs at the tick the input belongs to. When no input has arrived for a tick, the package repeats the last one and sets `InputContext.Repeated`, and the port then repeats only the axis, never a jump or a roll. `InputContext.Replaying` comes into play in step 05. `NetworkPlayer.Awake` now gets `RedCharacter` and finds `NetworkGame` once, so `m_Game` is set on every instance and not only on the owner's.

The `Reconcile` line and its three callbacks belong to step 05, although they were written in the same commit.

Fomoxa gathers, numbers, sends, buffers and repeats the input, and calls `Apply` at the right tick. The game decides what the input contains and what one tick of movement does.

## Test

This step and step 05 were made in one commit, and the port was tested only once, after both. Test at the end of [step 05](step-05-prediction-and-reconciliation.md#test).

## Expected result

The expected result is described in [step 05](step-05-prediction-and-reconciliation.md#expected-result).

## Commit

This step has no commit of its own. Its work is part of:

```
Commit: 7799601
Message: Predict the local character and send input through the network
```

View [`7799601`](https://github.com/fomoxa/RedRunner/commit/7799601188dced2c0c67d27a452d50f8bf7c7566) on GitHub, then continue with [step 05: prediction and reconciliation](step-05-prediction-and-reconciliation.md).
