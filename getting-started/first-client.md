# Your first client

This page connects clients to the server from [your first server](first-server.md), tries out the Jump RPC and the state, and finally runs the game as a host.

## How the client part works

The launcher's Client button calls:

```csharp
manager.ClientManager.StartConnection(address, port);
```

The address can be a host name or an IP address. The client resolves it, opens the transport and runs the Fomoxa handshake, and `ClientManager.OnClientConnectionState` reports its progress: `Starting` while it connects, `Started` once messages can flow and `Stopped` when the connection ends.

If the connection fails or drops, the client tries again every 0.5 seconds, by default without limit. On a `Stopped` event, `ConnectionStateArgs.Reason` tells why the connection stopped and `ConnectionStateArgs.WillRetry` tells whether a new attempt follows. [Client](../core/client.md) explains reconnection and its settings.

Once the client reaches `Started`, the server spawns a player for it and the client creates its own instance of the `Player` prefab. Objects the server spawned earlier, such as the other players, arrive the same way.

## 1. Connect a client to the dedicated server

1. Start the dedicated server build from the previous page, or enter Play Mode in a second copy of the project and click Server.
2. In the Editor, enter Play Mode, keep `127.0.0.1` in the text field and click Client.

Expected result:

- The Console shows `client: Starting None`, then `client: Started None`.
- A capsule appears at an x position of twice the client's peer id.
- The Console shows `player <id> spawned, owner <peer id>, mine: True, jumps: 0`.
- A Jump button appears for the capsule this client owns.
- On a dedicated server, `server.log` shows `peer <id>: Starting None` and `peer <id>: Started None`.

## 2. Call the RPC

Click Jump. The capsule moves up by one unit and the Console shows `player <id> jumps: 0 -> 1`.

The click sent a server RPC, and the server ran `Jump`, which moved the transform and changed the state. At the end of the tick the server sent the new position through `NetworkTransform` and the new state through the state model. The client applied both, and applying the state change called `OnStatsChanged`.

## 3. Add a second client

Build a player again, or reuse the build from the previous page, and start it without `-server` so that it opens a window. Click Client in it.

Both clients should now show two capsules, each with one Jump button for the capsule it owns. A jump on one client moves its capsule on both clients and logs the new count on both.

## 4. Run a host

Stop everything, then enter Play Mode in the Editor and click Host. The launcher starts a server and then connects a client in the same process. That client ignores the address and connects over an in-process loopback connection instead of UDP.

Expected result:

- The label shows `server: Started, peers: 1, client: Started`.
- A capsule spawns for the host's own client, with a Jump button.
- A client in another process can connect to the host with Client, just as it did to the dedicated server.

In host mode the server and the host's client share one instance of each object. [Host mode](../core/host-mode.md) explains what that means for your code.

## 5. Disconnect

Click Stop on a client. The client stops and its objects disappear, and the server despawns that client's player for everyone else.

## What you built

| Step | Feature | Guide |
|---|---|---|
| Network Manager with a UDP transport | Transport and tick loop | [NetworkManager](../core/network-manager.md), [UDP](../transports/udp.md) |
| `PlayerStats` model | Models and generated codecs | [Models and codecs](../messaging/models.md) |
| Player prefab with `NetworkObject` | Network objects and prefab ids | [NetworkObject](../core/network-object.md), [Spawning](../core/spawning.md) |
| `ServerManager.Spawn` with an owner | Spawning and ownership | [Ownership](../core/ownership.md) |
| `[ServerRpc] Jump` | RPCs | [RPCs](../messaging/rpc.md) |
| `state.Use` | State | [State](../synchronization/state.md) |
| `NetworkTransform` | Transform replication | [NetworkTransform](../synchronization/transform.md) |
| Host button | Host mode | [Host mode](../core/host-mode.md) |

The jump in this tutorial waits for the server before anything moves. A game that moves its characters every frame lets the client predict its own character instead, as [prediction](../prediction/overview.md) shows. If something in the tutorial does not work, see [troubleshooting](troubleshooting.md).
