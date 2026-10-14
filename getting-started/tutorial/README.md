# Tutorial: your first multiplayer game

This tutorial builds a small multiplayer game in three parts. Every connected player is a capsule. The player who owns a capsule clicks **Jump**, the server moves the capsule up and counts the jump, and every client sees the capsule move and the count change.

<figure><img src="../../.gitbook/assets/screenshots/tutorial-two-players.png" alt="The Game view of the finished tutorial running as a host with a second client connected. Two white capsules stand side by side, one of them higher after a jump. The top-left corner shows the status line server: Started, peers: 2, client: Started, a Stop button and a Jump button."><figcaption><p>The finished game, running as a host with a second client connected.</p></figcaption></figure>

## What you build

| Part | You add | You learn |
|---|---|---|
| [1. Set up the project](project-setup.md) | A `NetworkManager`, a model and a player prefab | Models and generated code, `NetworkObject`, `NetworkBehaviour`, state, RPCs |
| [2. Start a server](server.md) | A launcher that starts a server and spawns a player per client | `ServerManager`, connection events, spawning, dedicated servers |
| [3. Connect clients](clients.md) | Clients and a host | `ClientManager`, reconnection, host mode |

## Before you start

- Complete [installation](../installation.md), with the models folder `Assets/Network/Models` and the generated folder `Assets/Network/Generated`.
- Know how to create scripts, prefabs and scenes in Unity.

The game draws its buttons with `OnGUI`, so it needs no UI setup.

## What happens when a player jumps

Everything in the game follows one path. The owner's client asks the server to jump, the server changes the capsule, and the server sends the result to every client.

```mermaid
sequenceDiagram
    participant Owner as Owner's client
    participant Server
    participant Other as Other clients
    Owner->>Server: server RPC Jump
    Note over Server: runs Jump(): moves the transform<br/>and increments Jumps
    Server->>Owner: transform update and new state
    Server->>Other: transform update and new state
    Note over Owner,Other: NetworkTransform moves the capsule,<br/>OnStatsChanged logs the new count
```

The client never moves the capsule itself, because the server owns the game state. [Authority](../../concepts/authority.md) explains why, and [prediction](../../prediction/overview.md) shows how a game makes its own character respond at once.

## Tested result

The code in this tutorial was run in Unity 6000.5.7f1: as a host, with a second client that connected over UDP, jumped, and disconnected. The screenshots come from that run.

Start with [part 1](project-setup.md).
