# Offline baseline

This page describes Red Runner at commit `2b675b5`, the `master` branch of [BayatGames/RedRunner](https://github.com/BayatGames/RedRunner). The fork [fomoxa/RedRunner](https://github.com/fomoxa/RedRunner) contains the same commit with the port on top of it, and everything in the [migration](offline-to-online/README.md) starts from here.

```
git clone https://github.com/fomoxa/RedRunner.git
cd RedRunner
git switch -c my-port 2b675b5
```

## The frame loop

```
Start screen (Play button)
  ↓
GameManager.StartGame: gameRunning = true, Time.timeScale = 1
  ↓
RedCharacter.Update, every frame
  reads CrossPlatformInputManager
  ↓
Move, Jump, roll force on the Rigidbody2D
  ↓
Unity 2D physics
  ↓
Enemy collision callbacks: Die
TerrainGenerator.Update: next block near the character
GameManager.Update: score = furthest x
  ↓
CameraController follows the character
```

Everything happens in one process, every frame, without anything waiting for anything else.

## Entry point

The whole game is in `Assets/Scenes/Play.unity`. The scene list in the build settings names `Assets/Scenes/Gooose.unity`, which does not exist in the repository, so the game is played from `Play.unity` in the Editor.

`GameManager` is a scene singleton. Its `Awake` loads the coin count, the audio setting and the scores with SaveGameFree, and its `Start` subscribes to the main character's `IsDead` property and calls `Init`, which shows the start screen after three seconds. The Play button then opens the in-game screen and calls `StartGame`.

## Player and input

The character is the `RedRunner` object in `Play.unity`, which has `RedCharacter`, a `Rigidbody2D` and an `Animator`. `GameManager`, `TerrainGenerator` and `CameraController` each hold a reference to it in a serialized field.

`RedCharacter.Update` returns early while the game is not running, and otherwise reads the keyboard itself:

```csharp
// Input Processing
Move ( CrossPlatformInputManager.GetAxis ( "Horizontal" ) );
if ( CrossPlatformInputManager.GetButtonDown ( "Jump" ) )
{
	Jump ();
}
```

The guard and punch actions come from the `Guard` and `Fire` buttons, and the Roll button adds a force along `transform.localScale.z`.

## Movement and physics

Movement is Unity 2D physics with the project's fixed timestep of 0.02 seconds. `Update` speeds the character up past its run speed with `Mathf.SmoothDamp`, which uses the frame time and keeps its damping velocity in a field between frames. `Jump` sets the vertical velocity when `GroundCheck.IsGrounded` is true, a flag that `GroundCheck` updates once per frame.

## Level

`TerrainGenerator` builds the level while the character runs. Whenever the character comes within range of the last block, `Generate` adds the next one, chosen by `TerrainGenerator.ChooseFrom` with `Random.value`. With the counts in `Assets/Generation Settings.asset`, the level never ends. Background blocks, such as hills and clouds, are added the same way.

## Hazards

Each enemy kills the character from its own callback:

| Enemy | Callback | Effect played by the enemy |
|---|---|---|
| `Saw` | `OnCollisionEnter2D` | none, calls `Die (true)` for blood |
| `Spike` | `OnCollisionStay2D`, from the top only | spike sound, joint to the skeleton |
| `Water` | `OnTriggerEnter2D` | splash particles and sound |
| `Mace` | `OnCollisionEnter2D` | slam, smile, spike sound |

Falling below y = 0 also kills the character, from `RedCharacter.Update`.

Maces and saws on tracks move with `PathFollower`, whose `Update` moves the object toward the next point with `Time.deltaTime` and stops while `GameManager.gameRunning` is false. With Smart turned on, as on the mace, it waits until a character is within range.

## Game state, death and respawn

`Character.IsDead` is a `Property<bool>`. When it turns true, `GameManager.DeathCrt` records the score, waits 1.5 seconds and opens the end screen. The end screen's button calls `GameManager.Reset`, which raises `OnReset`, and in response the character moves back to its initial position and revives, the terrain clears and regenerates, and the maces reset.

## Score and coins

The score is the furthest x the character has reached. Coins and chests add to `GameManager.m_Coin` when any `Character` touches them, and scores and coins are saved with SaveGameFree when the game quits.

## Camera and pause

`CameraController` follows the `Transform` in its Followee field and moves fast after a death. `GameManager.StopGame` and `ResumeGame` set `Time.timeScale` to 0 and back to 1, which freezes everything behind the pause screen.

## What cannot stay as it is

| Offline behavior | Why it breaks online | Step |
|---|---|---|
| One character in the scene | Every player needs a character, and the server decides who owns which | [Step 03](offline-to-online/step-03-player-spawning.md) |
| `RedCharacter.Update` reads the keyboard | Every character in a process would move with one keyboard | [Step 03](offline-to-online/step-03-player-spawning.md), [Step 04](offline-to-online/step-04-player-input.md) |
| Movement per frame with `Time.deltaTime` | The server and the client must run the same step and replay it | [Step 04](offline-to-online/step-04-player-input.md) |
| Endless level from `Random.value` | Every process would build different ground | [Step 02](offline-to-online/step-02-shared-level.md) |
| Enemies kill in their callbacks | A predicted or interpolated character can be in a different place than on the server | [Step 06](offline-to-online/step-06-death-and-respawn.md) |
| Score and end screen | There is no single main character and no end of a run | [Step 06](offline-to-online/step-06-death-and-respawn.md) |
| `Time.timeScale` pause | The server and other players keep running | [Step 03](offline-to-online/step-03-player-spawning.md) |
| Maces wait for a nearby character | Each process would start its mace at a different time | [Step 07](offline-to-online/step-07-moving-hazards.md) |

The migration that fixes each of these starts with [offline to online](offline-to-online/README.md).
