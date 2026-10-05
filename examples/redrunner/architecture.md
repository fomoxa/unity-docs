# Red Runner online architecture

This page describes the finished port on the `master` branch of [fomoxa/RedRunner](https://github.com/fomoxa/RedRunner), with its game code as of commit [`c239d2a`](https://github.com/fomoxa/RedRunner/commit/c239d2a0988dcf2af5821b41f1ba7cc2f6372baf). The [migration](offline-to-online/README.md) explains how each part got there.

```
                         Red Runner (one player build)
                                    │
               ┌────────────────────┴────────────────────┐
               │                                         │
             Client                                   Server
               │                                         │
     Start screen: address               NetworkGame: -server, -port
               │                                         │
     NetworkPlayer.Gather              OnRemoteConnectionState → Spawn
     (keys → PlayerInput)                                │
               │                          NetworkPlayer.Apply at the tick
     Apply (prediction)                     (RedCharacter.Simulate)
     RedCharacter.Simulate                               │
               │                           2D physics step, enemy contacts
     Reconcile with PlayerMotion                         │
     (restore, replay)                     ServerTick: death, fall, end block
               │                                         │
     ShowState: death effects             PlayerState, NetworkTransform
     NetworkTransform: other players                     │
     Camera, background, coins                           │
               │                                         │
               └────────────── Fomoxa over UDP ──────────┘
                     input frames  →
                     ←  spawn, state, transforms, reconcile states

     Both sides: NetworkLevel builds the level from LevelState.Seed
                 and moves path followers by tick number
```

## Scene and prefab

`Assets/Scenes/Play.unity` holds the networking objects next to the original game objects:

| Object | Components | Role |
|---|---|---|
| Network Manager | `NetworkManager`, `UdpNetworkTransport`, `NetworkGame` | Connections and ticks; the game's start, spawn and local player logic |
| Network Level | `NetworkObject`, `NetworkLevel` | Scene object with the level seed; moves path followers |
| Terrain Generator | `TerrainGenerator` | Builds the level from a seed; background around the local player |
| Canvas/Start Screen | `StartScreen`, Address Field | Joins the address |
| Canvas/Pause Screen | `PauseScreen` | Leaves the server |

The `NetworkManager` uses Tick Rate 50, Timing Mode Tick, Simulate Physics on and Max Reconnect Retries 3, with Collected Prefabs and Collected Scenes set to the generated lists. Everything else is at its default.

`Assets/Prefabs/RedRunner.prefab` is the network player. It has `RedCharacter`, `Rigidbody2D`, `NetworkObject`, `NetworkTransform` (with Sync Rotation off and Sync Scale on) and `NetworkPlayer`.

## Models

All models are in `Assets/Scripts/RedRunner/Networking/Models`, and the generated code is in `Networking/Generated` under the namespace `Generated`.

| Model | Used as | Registered by | Carries |
|---|---|---|---|
| `LevelState` | State | `NetworkLevel` | `Seed` |
| `PlayerState` | State | `NetworkPlayer` | `Dead`, `Cause` |
| `PlayerInput` | Input | `NetworkPlayer` | `Move`, `Jump`, `Roll` |
| `PlayerMotion` | Reconcile state | `NetworkPlayer` | Position, velocity, `RunSmoothVelocity` |

The game uses no RPCs and no raw messages, and the positions of other players travel through `NetworkTransform`.

## Server

The server is authoritative for everything that affects more than one player. It picks the level seed in `NetworkLevel.OnStartServer`, and it decides which characters exist by spawning them in `NetworkGame.OnRemoteConnectionState` and despawning them with their owner. It moves every character by running `Apply` with the input that arrived for the tick.

Deaths are decided on the server too, from enemy contacts during the physics step and from the fall check in `NetworkPlayer.ServerTick`, and so are respawns, which happen 100 ticks after a death or when a character passes `TerrainGenerator.EndX`. The server ignores coins and chests. A dedicated server caps its frame rate at 60 with `Application.targetFrameRate`.

## Client

A client builds the level from the seed, predicts its own character and shows everything else as the server sends it. It gathers input once per tick in `NetworkPlayer.Gather` and predicts its own character, which `PlayerMotion` from the server corrects. Other characters are interpolated by `NetworkTransform` as kinematic bodies, and `ShowState` shows death effects and respawns when `PlayerState` changes. The camera, the background and the coins stay local, since only the local player affects them.

No character decides its own death on a client, so an enemy touched by a predicted or interpolated character does nothing there.

## One tick

The following table follows the package's [order of one tick](../../concepts/tick.md#order-of-one-tick) and shows Red Runner's code at each point:

| Step | Server | Owner's client |
|---|---|---|
| `OnPreTick` | `NetworkLevel` moves path followers to the server tick | `NetworkLevel` moves path followers to the prediction tick |
| Input | `NetworkPlayer.Apply` for each character with the input for this tick | Reconcile, then `Gather` and `Apply` for its own character |
| Physics | One 2D physics step; enemies call `Die` on characters with `DecidesDeath` | One 2D physics step |
| After physics | Reconcile states (`PlayerMotion`) to each owner | Records `PlayerMotion` and saves physics for the tick |
| `OnTick` | `NetworkPlayer.ServerTick`: death, fall, respawn, end block | |
| Send | Changed `PlayerState`, `LevelState` and transforms | Input frames |

## Discontinuities

A respawn moves a character across the level in one tick, and each part of the game that sees the jump handles it in its own way:

| Who sees it | Handled by |
|---|---|
| Other clients' interpolation | `NetworkTransform.Teleport()` in `Respawn`, which starts a new teleport generation |
| The owner's prediction | An ordinary reconcile mismatch and replay |
| Other clients' animator | `RedCharacter.LateUpdate` treats a move over 2 units as a teleport |

## Players who leave

| Case | What happens |
|---|---|
| The player clicks Home or quits | `ClientManager.StopConnection` sends `PeerLeave`; the server ends the peer and despawns the character at once |
| The client crashes or loses its network | The server repeats the last input; after 10 repeated ticks `Apply` drops the axis and the character stands still; the heartbeat ends the session about 20 seconds later and the character despawns |

## Not in the online game

The online game drops the score, the high score and the end screen, as well as the coins and settings saved with SaveGameFree and the guard and punch actions. Players do not collide with each other, because the `Characters` layer does not collide with itself. There are no lobbies, rooms or matchmaking, and the pause screen no longer stops the game; it only empties the player's input.
