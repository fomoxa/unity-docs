# Step 05: Prediction and reconciliation

## Goal

After this step the owner's character moves in the same frame the key is pressed. The client applies its own input at once, compares its result with the server's after each tick and corrects itself when they differ. The camera and the background follow the local character, and other players' characters animate while the server moves them.

## Starting point

After step 04, `PlayerInput`, `Gather`, `Apply` and `RedCharacter.Simulate` exist, and the server runs `Apply` at each input's tick.

## Problem

If the client only sent input and waited, every key press would show up one round trip later, so the client has to run `Apply` itself in the tick it gathers the input.

The client's result can then drift from the server's, for example when a packet arrives a tick late and the server repeats the previous input, or when the two physics engines round differently. The client needs to notice the drift and go back to the server's result without losing the input it has applied since.

## Fomoxa concepts

- [Prediction](../../../concepts/prediction.md)
- [Prediction overview](../../../prediction/overview.md)
- [Reconciliation](../../../prediction/reconciliation.md)
- [Rollback with physics](../../../prediction/rollback.md)
- [PhysicsBody2D](../../../physics/physics-body.md#physicsbody2d)
- [Three tick numbers](../../../concepts/tick.md#three-tick-numbers)

## Design

```
Owner's client                        Server
Gather (tick T)
  ↓
Apply (prediction) ── input T ──→     Apply (tick T)
  ↓                                     ↓
Capture → history[T]                  Capture
  ↓                                     ↓
render at once           ←── motion T ──┘
  ↓
Matches(server T, history[T])?
  yes → nothing
  no  → restore 2D physics to T
        Restore(server motion)
        Apply T+1 … now (Replaying = true)
```

What the client compares is a second model, `PlayerMotion`, holding the position, the velocity and the run damping velocity. `NetworkPlayer` registers it with `input.Reconcile` and three callbacks, `Capture`, `Restore` and `Matches`.

The character is a `Rigidbody2D`, and the scene has other bodies the character touches. With Simulate Physics on in the `RigidbodyPhysics` of the `Network Manager`, the package saves the 2D physics of the scene every tick and restores it before a replay, so the replay starts from the same world the server had.

Other clients do not predict this character. They see it through `NetworkTransform`, as a kinematic body interpolated two ticks behind the newest position they have received.

## Files

```
Assets/Scripts/RedRunner/Networking/Models/PlayerMotion.cs
Assets/Scripts/RedRunner/Networking/NetworkPlayer.cs
Assets/Scripts/RedRunner/Networking/NetworkGame.cs
Assets/Scripts/RedRunner/Characters/RedCharacter.cs
```

## Implementation

### Add the motion model

```csharp
using Fomoxa;

namespace RedRunner.Networking.Models
{
    [Network]
    [Codec("net")]
    public class PlayerMotion
    {
        [Network("f32")]
        [Codec("net")]
        public float X { get; set; }

        [Network("f32")]
        [Codec("net")]
        public float Y { get; set; }

        [Network("f32")]
        [Codec("net")]
        public float VelocityX { get; set; }

        [Network("f32")]
        [Codec("net")]
        public float VelocityY { get; set; }

        [Network("f32")]
        [Codec("net")]
        public float RunSmoothVelocity { get; set; }
    }
}
```

`RunSmoothVelocity` is in the model because `Mathf.SmoothDamp` carries its velocity from one tick to the next. Without it, a replay would start the acceleration from a different value than the server did, and drift. `RedCharacter` exposes the field as a `RunSmoothVelocity` property for this purpose.

### Capture, restore and compare

```csharp
private const float PositionTolerance = 0.01f;
private const float VelocityTolerance = 0.05f;

private void Capture(PlayerMotion motion)
{
    BodyState2D state = NetworkObject.Body2D.State;
    motion.X = state.Position.X;
    motion.Y = state.Position.Y;
    motion.VelocityX = state.Velocity.X;
    motion.VelocityY = state.Velocity.Y;
    motion.RunSmoothVelocity = m_Character.RunSmoothVelocity;
}

private void Restore(PlayerMotion motion)
{
    PhysicsBody2D body = NetworkObject.Body2D;
    BodyState2D state = body.State;
    state.Position = new System.Numerics.Vector2(motion.X, motion.Y);
    state.Velocity = new System.Numerics.Vector2(motion.VelocityX, motion.VelocityY);
    body.State = state;
    m_Character.RunSmoothVelocity = motion.RunSmoothVelocity;
}

private static bool Matches(PlayerMotion server, PlayerMotion predicted) =>
    Math.Abs(server.X - predicted.X) <= PositionTolerance
    && Math.Abs(server.Y - predicted.Y) <= PositionTolerance
    && Math.Abs(server.VelocityX - predicted.VelocityX) <= VelocityTolerance
    && Math.Abs(server.VelocityY - predicted.VelocityY) <= VelocityTolerance
    && Math.Abs(server.RunSmoothVelocity - predicted.RunSmoothVelocity) <= VelocityTolerance;
```

`NetworkObject.Body2D` is the package's view of the character's `Rigidbody2D`, with `System.Numerics.Vector2` positions and velocities. The tolerances can be small because the server and the client run the same physics on the same blocks.

During a replay `InputContext.Replaying` is true, and `Apply` from step 04 passes `!context.Replaying` as `effects`, so a replayed jump changes the velocity without playing the sound, the particles or the trigger a second time.

Fomoxa keeps the history, compares at the right tick, restores the physics world and replays, while the game decides what counts as the same result and how much difference to accept.

### Follow the local player

`NetworkGame.SetLocalPlayer` now points the camera and the background at the owner's character:

```csharp
internal void SetLocalPlayer(NetworkPlayer player)
{
    LocalPlayer = player;
    if (CameraController.Singleton != null)
    {
        CameraController.Singleton.Follow(player != null ? player.transform : null);
    }

    if (TerrainGenerator.Singleton != null)
    {
        TerrainGenerator.Singleton.Follow(player != null ? player.Character : null);
    }
    LocalPlayerChanged?.Invoke(player);
}
```

### Animate characters you do not control

`RedCharacter.LateUpdate` fed the animator from the `Rigidbody2D` velocity. On a client, another player's character is kinematic and moved by its `NetworkTransform`, so that velocity is zero and the character would slide along in its idle pose. For a kinematic body the velocity now comes from the distance moved since the last frame:

```csharp
Vector2 velocity = m_Rigidbody2D.linearVelocity;
if ( m_Rigidbody2D.bodyType == RigidbodyType2D.Kinematic && Time.deltaTime > 0f )
{
	velocity = ( transform.position - m_LastPosition ) / Time.deltaTime;
}
m_LastPosition = transform.position;
```

Step 08 adds a limit to this calculation for respawns.

## Test

Join a server and press the arrow keys and Space.

The port's own check is `Tools/PortChecks/MoveCheck.cs`. It joins a server process through the start screen and drives the `CrossPlatformInputManager` virtual axes with two seconds to the right, a jump and one second to the left.

## Expected result

- The character runs and jumps without waiting for the server.
- The camera and the background follow it.
- Other clients see it run, slightly in the past.

`MoveCheck` passes when the client predicts its character, the character runs at least 5 units, rises at least 1.5 units and turns, and the camera and the background follow it. In one run the character moved 9.65 units and jumped 4.77 units high, and six seconds of running and jumping needed one correction.

## Commit

```
Commit: 7799601
Message: Predict the local character and send input through the network
```

View [`7799601`](https://github.com/fomoxa/RedRunner/commit/7799601188dced2c0c67d27a452d50f8bf7c7566) on GitHub, then continue with [step 06: death and respawn](step-06-death-and-respawn.md).
