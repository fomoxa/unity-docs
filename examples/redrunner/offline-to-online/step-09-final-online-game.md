# Step 09: Final online game

## Goal

This last step builds the finished game, runs it as a dedicated server with clients, and checks the start screen in a player build.

## Starting point

After step 08 the game works with several clients and handles players who leave or crash.

## Problem

The steps so far ran mostly in the Editor, and a player build shows things the Editor hides. In the build, the address field on the start screen showed no text, because the game's font did not fit the default input field.

## Fomoxa concepts

- [Dedicated server](../../../deploy/dedicated-server.md)
- [Deployment](../../../deploy/deployment.md)
- [Editor integration: build checks](../../../advanced/editor-integration.md#build-checks)

## Design

One player build serves every role, and the command line chooses which:

| Command | Role |
|---|---|
| `RedRunner.exe -batchmode -nographics -server -port 7777 -logFile server.log` | Dedicated server, frame rate capped at 60 |
| `RedRunner.exe -host` | Server and client in one process |
| `RedRunner.exe` | Client; the player types the address on the start screen |

## Files

```
Assets/Scenes/Play.unity
```

The commit also adds screenshot tooling under `Tools/PortChecks`, along with the screenshots used on these pages.

## Implementation

### Fix the address field

Move `Address Field` below the start screen buttons and set Vertical Overflow to Overflow on its text and placeholder; [step 03](step-03-player-spawning.md#add-the-address-field) lists the final settings.

### Build and run

Build a Windows player with `Play.unity` as its only scene. Start the server, then start clients and click Play with the server's address in the field under the buttons.

In the game, the left and right arrow keys run, Space, W or the up arrow jump, and Shift rolls.

## Test

Run a dedicated server and two clients from the build, as in [step 08](step-08-two-clients.md#test). The port's checks ran the server and the clients on one machine. To play across machines, clients enter the server's address and the server must accept UDP on its port, as described in [deployment](../../../deploy/deployment.md).

## Expected result

![Two players running near the start of a seeded level](../../../.gitbook/assets/redrunner-two-players.png)

- The start screen shows `localhost` in the address field.
- Every client runs on the same level, sees the others, and dies and respawns as the server decides.

## Commit

```
Commit: 7396f92
Message: Finish the GitBook guide with screenshots and a quick start
```

View [`7396f92`](https://github.com/fomoxa/RedRunner/commit/7396f9279b5796ffb35d97765cbe5cb1794d5357) on GitHub.

In the history, `7396f92` comes after `52e1696` and before the other three commits of step 08.

The [online architecture](../architecture.md) page describes what runs where in the finished game, and [troubleshooting](../troubleshooting.md) helps if something does not work.
