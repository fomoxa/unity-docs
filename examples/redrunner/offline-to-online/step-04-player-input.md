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
OnGatherInput: read the keys into the input fields
  ↓
Fomoxa input frames
  ↓
Server, at the input's tick
  ↓
OnApplyInput: RedCharacter.Simulate with the tick length
```

Three things keep the offline controller from running on the server:

- It reads the keyboard of the process it runs in, and the server has no player at its keyboard.
- It runs per frame with the frame time, while the server ticks 50 times per second independently of frames. In step 05 the client will also have to run the same step again for ticks it has already shown.
- It plays sounds, particles and animator triggers in the middle of the physics, and a replayed tick must not play them twice.

## Fomoxa concepts

- [Input](../../../prediction/input.md)
- [Authority](../../../concepts/authority.md#what-a-client-can-send)
- [Ticks and timing](../../../concepts/tick.md)
- [NetworkBehaviour declarations](../../../objects/network-behaviour.md#declarations)

## Design

The input of one tick is three input fields of `NetworkPlayer`: the horizontal axis and two buttons. The package gathers them into a model, `PlayerInput`, and calls two methods of `NetworkPlayer`:

| Method | Runs on | Does |
|---|---|---|
| `OnGatherInput` | The owner's client, once per tick | Writes the input fields from the keys |
| `OnApplyInput` | The server at the input's tick, and the owner's client when it predicts | Reads the input fields and calls `RedCharacter.Simulate` |

`RedCharacter.Simulate` is the tick step. It takes the axis, the buttons, the tick length and whether to play effects. The client only sends input, and the server decides where the character ends up.

## Files

```
Assets/Scripts/RedRunner/Characters/RedCharacter.cs
Assets/Scripts/RedRunner/Utilities/GroundCheck.cs
Assets/Scripts/RedRunner/Networking/NetworkPlayer.cs
```

## Implementation

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

`NetworkPlayer` becomes `partial` and names its input model, as `NetworkLevel` named its state model in step 02:

```csharp
[RequireComponent(typeof(RedCharacter))]
[NetworkInputModel("PlayerInput")]
public sealed partial class NetworkPlayer : NetworkBehaviour
```

The input half of the class, written for `com.fomoxa.networking` 0.5.0:

```csharp
[NetworkInput]
private float move;

[NetworkInput]
private bool jump;

[NetworkInput]
private bool roll;

private void Update()
{
    if (NetworkObject == null || !NetworkObject.IsOwner)
    {
        return;
    }

    m_JumpPressed |= CrossPlatformInputManager.GetButtonDown("Jump");
    m_RollPressed |= CrossPlatformInputManager.GetButtonDown("Roll");
}

protected override void OnGatherInput()
{
    bool playing = GameManager.Singleton.gameRunning;
    move = playing ? CrossPlatformInputManager.GetAxis("Horizontal") : 0f;
    jump = playing && m_JumpPressed;
    roll = playing && m_RollPressed;
    m_JumpPressed = false;
    m_RollPressed = false;
}

protected override void OnApplyInput(InputContext context)
{
    float tickDelta = (float)NetworkManager.TimeManager.TickDelta;
    bool fresh = !context.Repeated;
    m_Character.Simulate(move, fresh && jump, fresh && roll, tickDelta, !context.Replaying);
}
```

After `OnGatherInput` the package copies the three fields into a `PlayerInput` and sends it. Before `OnApplyInput` it copies the input of the tick back into the fields, so `OnApplyInput` reads `move`, `jump` and `roll` and never touches the model. The generated model, `Networking/Generated/StateModels/PlayerInput.cs`, has no channel, because the package carries input in its own input frames.

`Update` runs every frame and keeps button presses until the next `OnGatherInput`, so a press shorter than a tick is not lost. While the pause screen is open, `gameRunning` is false and the input is empty, so the character stops while the server and the other players keep going.

On the server, `OnApplyInput` runs at the tick the input belongs to. When no input has arrived for a tick, the package repeats the last one and sets `InputContext.Repeated`, and the port then repeats only the axis, never a jump or a roll. `InputContext.Replaying` comes into play in step 05. `OnApplyInput` reads the tick length from `NetworkManager`, the manager that spawned the object, which is set in every network callback but not yet in `Awake`. `NetworkPlayer.Awake` now gets `RedCharacter` and finds `NetworkGame` once, so `m_Game` is set on every instance, the owner's included.

The reconcile fields of step 05 were written in the same commit.

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

View [`7799601`](https://github.com/fomoxa/RedRunner/commit/7799601188dced2c0c67d27a452d50f8bf7c7566) on GitHub. That commit declares `PlayerInput` by hand with the 0.3 API, and [`1c1ded1`](https://github.com/fomoxa/RedRunner/commit/1c1ded158105091902d8d352157856eacf0cbc73) moves it to fields.

Continue with [step 05: prediction and reconciliation](step-05-prediction-and-reconciliation.md).
