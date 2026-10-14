# Step 08: Two clients

## Goal

This step runs a server with two clients and fixes what only shows up when players see each other: how another player's character animates and turns, how another player's death and respawn look, and what happens to a character whose player leaves or crashes.

## Starting point

After step 07 the game is complete for one client, but every earlier step was tested with a single client, sometimes in host mode.

## Problem

Running two clients turned up three problems:

1. When another player's character respawned, its animator received a running speed in the thousands. `LateUpdate` computes the speed of a kinematic character from the distance moved in a frame, and a respawn covers the whole level in a few frames.
2. Other clients drew the respawning character sliding from the death point to the start, because their `NetworkTransform` buffer held both positions next to each other and interpolated between them.
3. When a client quit, its character kept running and dying for about 20 seconds. Over UDP the server learns that a peer is gone only from the heartbeat, after 5 seconds of silence and 15 more without an answer, and until then the package repeated the player's last input on every tick.

## Fomoxa concepts

- [NetworkTransform](../../../synchronization/transform.md)
- [Teleporting](../../../synchronization/transform.md#teleporting)
- [Input on the server](../../../prediction/input.md#on-the-server)
- [Client](../../../connections/client.md#connect-and-disconnect)
- [UDP](../../../connections/transports/udp.md)
- [Configuration](../../../reference/configuration.md)

## Design

| Problem | Fix | Where |
|---|---|---|
| Animator speed after a respawn | A move longer than 2 units in a frame counts as a teleport, and the speed is capped | `RedCharacter.LateUpdate` |
| Sliding across the level | `NetworkTransform.Teleport()` after the respawn | `NetworkPlayer.Respawn`, step 06 |
| A player who quits keeps running | `ClientManager.StopConnection` sends `PeerLeave`, and the server despawns the character at once | The package |
| A player who crashes keeps running | `Apply` drops the axis once the input has been repeated for more than 10 ticks | `NetworkPlayer.Apply` |

The last two rows are different cases. A client that stops on purpose can tell the server, but a client that crashes or loses its network cannot, so the server still has to wait for the heartbeat, and the game decides what the character does in the meantime.

## Files

```
Assets/Scripts/RedRunner/Characters/RedCharacter.cs
Assets/Scripts/RedRunner/Networking/NetworkPlayer.cs
Assets/Scripts/RedRunner/Networking/Generated/
FomoxaSystemModels/PeerLeave.cs
FomoxaSystemModels/TransformSettle.cs
FomoxaSystemModels/TransformUpdate.cs
.fomoxa/
```

The generated files change because the package's system models changed: the transform messages now carry a teleport generation, and `PeerLeave` is new. Regenerate with Tools > Fomoxa > Generate after updating the package.

## Implementation

### Animate a character that teleports

```csharp
void LateUpdate ()
{
	Vector2 velocity = m_Rigidbody2D.linearVelocity;
	if ( m_Rigidbody2D.bodyType == RigidbodyType2D.Kinematic && Time.deltaTime > 0f )
	{
		Vector2 moved = transform.position - m_LastPosition;
		velocity = moved.magnitude > m_TeleportDistance ? Vector2.zero : Vector2.ClampMagnitude ( moved / Time.deltaTime, m_MaxRunSpeed + m_JumpStrength );
	}
	m_LastPosition = transform.position;
```

`m_TeleportDistance` is a new serialized field, 2 units by default, and the cap is the fastest the character can move by running and jumping.

### Mark the respawn as a teleport

`NetworkPlayer.Respawn` calls `m_NetworkTransform.Teleport()` right after it moves the body, as shown in [step 06](step-06-death-and-respawn.md#respawn). The server then sends the new position as a settle that starts a new teleport generation. A client that receives it clears its interpolation buffer and places the character at the start, and if that message is lost, the first update of the new generation has the same effect.

### Leave the server on purpose

The game needs no change for this case. `NetworkGame.Leave` already calls `ClientManager.StopConnection`, and `NetworkManager` calls it when the application quits. With the current package, `StopConnection` sends a `PeerLeave` message three times before it closes the connection, the server ends that peer at once, and the character despawns with its owner as in step 03.

### Stop a character whose player vanished

`InputContext.RepeatedTicks` tells `Apply` how many ticks in a row the server has repeated the last input:

Before:

```csharp
m_Character.Simulate(input.Move, fresh && input.Jump, fresh && input.Roll, tickDelta, !context.Replaying);
```

After:

```csharp
private void Apply(PlayerInput input, InputContext context)
{
    float tickDelta = (float)m_Game.Manager.TimeManager.TickDelta;
    bool fresh = !context.Repeated;
    float move = context.RepeatedTicks > m_MaxRepeatedTicks ? 0f : input.Move;
    m_Character.Simulate(move, fresh && input.Jump, fresh && input.Roll, tickDelta, !context.Replaying);
}
```

`m_MaxRepeatedTicks` is 10, which is 0.2 seconds at 50 ticks per second. A short gap in the input still repeats the run, while a vanished player stands still until the heartbeat ends the session. Commit `0edd3a4` first did this with its own counter in `NetworkPlayer`, and `c239d2a` replaced that counter with `RepeatedTicks`.

The heartbeat timing comes from Heartbeat Interval Seconds (5) and Heartbeat Timeout Seconds (15) on the `NetworkManager`, and Red Runner keeps the defaults.

## Test

Build a Windows player, then start a server and two clients:

```
RedRunner.exe -batchmode -nographics -server -port 7777 -logFile server.log
RedRunner.exe
RedRunner.exe
```

Join `localhost` from both clients, or use the Editor as one of them. Run with one client while you watch with the other, die and respawn, and finally quit one client.

The port has two checks for this step. `CrowdCheck` joins the server from the Editor and stands still while a second player build runs as a bot client (`-bot 127.0.0.1 -bot-seconds 45`, handled by `BotPlayer`) that runs right, jumps and leaves after 45 seconds. `CrashCheck` starts the bot the same way and kills its process after eight seconds, so that no `PeerLeave` is sent.

## Expected result

- Both characters start on the start block and overlap without pushing each other.
- When one player runs, the other client sees the character run with its running animation and face the way it runs.
- When one player dies, the other client sees the skeleton, then the character back at the start two seconds later, without sliding across the level.
- When a client quits, its character disappears from the other client within about 2 seconds.
- When a client crashes, its character stands still and disappears about 20 seconds later.

`CrowdCheck` also fails if two neighbouring snapshots in the bot's `NetworkTransform` buffer are more than 2 units apart. In the last run, the Editor client saw the bot's character run to x 24, die and respawn nine times without a single such pair, with an animator speed of at most 11.5. Without the `Teleport()` call, the check counted 268 frames with the death point and the start next to each other in the buffer. The server despawned the bot's character as the bot left. In the last run of `CrashCheck`, the character stood still and was despawned 20.0 seconds after the kill, whereas without the `RepeatedTicks` rule it ran 11.4 units further and died three more times.

## Commit

This step spans four commits:

```
Commit: 52e1696
Message: Check a server with two clients and fix teleport animation

Commit: 0edd3a4
Message: Stop a departed player's character after ten repeated ticks

Commit: c75cebd
Message: Mark respawns as teleports with NetworkTransform.Teleport

Commit: c239d2a
Message: Leave the server with PeerLeave and stop vanished players by RepeatedTicks
```

They are on GitHub as [`52e1696`](https://github.com/fomoxa/RedRunner/commit/52e1696b2e5b8db09e0178f827febf9ae712a02f), [`0edd3a4`](https://github.com/fomoxa/RedRunner/commit/0edd3a46a0f5bf48a76786e6242ea2f523e1ec21), [`c75cebd`](https://github.com/fomoxa/RedRunner/commit/c75cebdee36f6edfc3869964157bd45093eae543), [`c239d2a`](https://github.com/fomoxa/RedRunner/commit/c239d2a0988dcf2af5821b41f1ba7cc2f6372baf).

`c75cebd` and `c239d2a` need a package with teleport generations, `PeerLeave` and `InputContext.RepeatedTicks`, all of which the published package has.

Continue with [step 09: final online game](step-09-final-online-game.md).
