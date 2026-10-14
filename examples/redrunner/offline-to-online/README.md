# Offline to online

The migration takes nine steps. Each step leaves a game that compiles and runs, so you can test and commit it before you start the next one.

```
Offline game (2b675b5)
  ↓
01 Network foundation: package, settings, NetworkManager
  ↓
02 Shared level: a seed as state on a scene object
  ↓
03 Player spawning: server, host, client, one character per peer
  ↓
04 Player input: a tick step that the server runs
  ↓
05 Prediction and reconciliation: the owner moves at once
  ↓
06 Death and respawn: the server decides
  ↓
07 Moving hazards: maces on the server's tick
  ↓
08 Two clients: what other players see, leaving and crashing
  ↓
09 Final online game
```

## Steps

| Step | What changes | Fomoxa pages |
|---|---|---|
| [01 Network foundation](step-01-network-foundation.md) | Unity 6000.5, the package, code generation, a `NetworkManager` in `Play.unity` | [Installation](../../../getting-started/installation.md), [NetworkManager](../../../connections/network-manager.md) |
| [02 Shared level](step-02-shared-level.md) | A finite level built from a seed that the server keeps in a state | [State](../../../synchronization/state.md), [Spawning](../../../objects/spawning.md#scene-objects) |
| [03 Player spawning](step-03-player-spawning.md) | The character becomes a network prefab; the game starts as a server, a host or a client | [Spawning](../../../objects/spawning.md), [Server](../../../connections/server.md), [Client](../../../connections/client.md) |
| [04 Player input](step-04-player-input.md) | The input model and the tick step that the server applies | [Input](../../../prediction/input.md), [Authority](../../../concepts/authority.md) |
| [05 Prediction and reconciliation](step-05-prediction-and-reconciliation.md) | The motion model, rollback of 2D physics, the camera on the local player | [Reconciliation](../../../prediction/reconciliation.md), [Rollback with physics](../../../prediction/rollback.md) |
| [06 Death and respawn](step-06-death-and-respawn.md) | Deaths on the server, a player state, teleporting respawns | [State](../../../synchronization/state.md), [Teleporting](../../../synchronization/transform.md#teleporting) |
| [07 Moving hazards](step-07-moving-hazards.md) | Path followers placed by tick number | [Ticks and timing](../../../concepts/tick.md) |
| [08 Two clients](step-08-two-clients.md) | Animation of remote characters, players who leave or crash | [NetworkTransform](../../../synchronization/transform.md), [Input](../../../prediction/input.md) |
| [09 Final online game](step-09-final-online-game.md) | A player build, a dedicated server, screenshots | [Dedicated server](../../../deploy/dedicated-server.md) |

## Commits

The steps were made as commits on the `master` branch of [fomoxa/RedRunner](https://github.com/fomoxa/RedRunner), starting from upstream commit `2b675b5`. Each step page ends with a Commit section that names the commit by its short hash and message and links to it.

| Step | Commits |
|---|---|
| 01 | [`8983a5a`](https://github.com/fomoxa/RedRunner/commit/8983a5ae2105e4ce79b8b127c9e5564147707eb1) |
| 02 | [`0b9d85f`](https://github.com/fomoxa/RedRunner/commit/0b9d85fb089698c82ec0bcfccede2d7b59028482) |
| 03 | [`1b65628`](https://github.com/fomoxa/RedRunner/commit/1b656285a486c6be727309e48d6612a3e483da80) |
| 04 and 05 | [`7799601`](https://github.com/fomoxa/RedRunner/commit/7799601188dced2c0c67d27a452d50f8bf7c7566) |
| 06 | [`a148ea7`](https://github.com/fomoxa/RedRunner/commit/a148ea70ca4eea0ec407c9cd85af57ca1acdf589) |
| 07 | [`f277dad`](https://github.com/fomoxa/RedRunner/commit/f277dad4cc29eccef696158280185c9117a270ae) |
| 08 | [`52e1696`](https://github.com/fomoxa/RedRunner/commit/52e1696b2e5b8db09e0178f827febf9ae712a02f), [`0edd3a4`](https://github.com/fomoxa/RedRunner/commit/0edd3a46a0f5bf48a76786e6242ea2f523e1ec21), [`c75cebd`](https://github.com/fomoxa/RedRunner/commit/c75cebdee36f6edfc3869964157bd45093eae543), [`c239d2a`](https://github.com/fomoxa/RedRunner/commit/c239d2a0988dcf2af5821b41f1ba7cc2f6372baf) |
| 09 | [`7396f92`](https://github.com/fomoxa/RedRunner/commit/7396f9279b5796ffb35d97765cbe5cb1794d5357) |

Steps 04 and 05 share one commit, while step 08 spans four. In the history, `7396f92` from step 09 sits between `52e1696` and `0edd3a4` from step 08.

## Following along

To follow the steps in your own project, work on a branch of the original commit, and compare your work with a step by running `git diff` against that step's commit:

1. Clone [fomoxa/RedRunner](https://github.com/fomoxa/RedRunner) and create a branch from `2b675b5`: `git switch -c my-port 2b675b5`.
2. Do step 01, run its test, and commit.
3. Continue with the next step the same way.

The pages show the code as it is at the end of the migration, in commit [`f164d56`](https://github.com/fomoxa/RedRunner/commit/f164d5624f171b64c8bfc6f029b12be2cfe41e27), which moves the finished game to the current package. Where a later step changes code that an earlier step added, the earlier step shows its own version and the later step shows the change.

Replaying the history exactly has some limits:

- Steps 04 and 05 were made in one commit, so the game is tested only once, at the end of step 05.
- Step 08 spans four commits. Two of them, `c75cebd` and `c239d2a`, rely on package changes made during the port: teleport generations in `NetworkTransform`, the `PeerLeave` message and `InputContext.RepeatedTicks`. The published package has all of them.
- The step commits use the package under its earlier name, `com.fomoxa.unity`, from a local copy next to the project (`file:../../fomoxa-unity/com.fomoxa.unity`). To build one of them, replace that entry in `Packages/manifest.json` with `"com.fomoxa.unity": "https://github.com/fomoxa/com.fomoxa.unity.git"`. Commit `f164d56` moves the game to `com.fomoxa.networking`: it installs the package from the Git URL in [installation](../../../getting-started/installation.md), changes the `using` directives to the `Fomoxa.Networking` namespaces, and turns physics simulation on through a `RigidbodyPhysics` component on the `Network Manager`.
- Nobody has checked commit by commit whether an early commit compiles with the current package after its code is regenerated.
- `Play.unity`, `RedRunner.prefab` and `Generation Settings.asset` are stored in a form that `git diff` shows as binary, so the steps describe their changes as Inspector settings.
- Each commit also adds automated checks under `Tools/PortChecks`, together with a script, `Tools/unity-windows.sh`, that runs them from WSL against a Windows Editor. The steps describe what each check verifies so that you can test by hand instead.

Start with [step 01: network foundation](step-01-network-foundation.md).
