# Client

`ClientManager`, which you reach through `NetworkManager.ClientManager`, connects to a server and keeps the connection alive, reconnecting when it drops. It also holds the objects the server has spawned on this client.

## Connect and disconnect

```csharp
manager.ClientManager.StartConnection("game.example.com", 7777);

manager.ClientManager.StopConnection();
```

`StartConnection(address, port)` accepts a host name or an IP address. Host names are resolved without blocking the main thread, and IPv4 addresses are tried first. With a WebSocket transport the address may also be a `ws://` URL, as described in [WebSocket](../transports/websocket.md). Calling `StartConnection` on a running client throws `the client is already running`.

If the same `NetworkManager` is running a server, `StartConnection` ignores the address and port and connects through the in-process connection instead. This is [host mode](host-mode.md).

`StopConnection()` sends a leave message to the server, closes the connection, despawns every object on the client and cancels any pending reconnect.

## Connection states

`State` is a `ConnectionState`, one of `Stopped`, `Starting` and `Started`, and `OnClientConnectionState` reports each change with a `ConnectionStateArgs`:

| Field | Meaning |
|---|---|
| `State` | The new state |
| `Reason` | Why the connection stopped; `None` while starting or started |
| `Failure` | The handshake failure when `Reason` is `HandshakeFailed` |
| `DiscardedMessages` | Messages still queued that were dropped when the connection stopped |
| `WillRetry` | True when the client will start again after the reconnect interval |

```csharp
manager.ClientManager.OnClientConnectionState += args =>
{
    if (args.State == ConnectionState.Stopped && !args.WillRetry)
    {
        Debug.Log($"disconnected for good: {args.Reason} {args.Failure}");
    }
};
```

## Reconnection

After a connection fails or drops, the client starts again after Reconnect Interval Seconds (0.5 by default), up to Max Reconnect Retries times (by default -1, which means without limit). The retry count resets whenever a connection reaches `Started`.

Some stop reasons end the connection for good. The client does not retry after `LocalStop`, which means your code called `StopConnection`, or after `HandlerException`, which means a message handler on the client threw. It also stays stopped after `PrefabMismatch` or `ObjectMismatch`, when it could not apply an object message, after `PhysicsBackendMismatch`, when the server uses another physics backend, and after `HandshakeFailed` with any failure other than `Timeout`. A host's in-process client never retries.

Every reconnect is a new connection. The client despawns all objects when the connection stops, and the server spawns them again once the new connection has started.

## Objects and timing

| Member | Purpose |
|---|---|
| `Spawned` | Objects spawned on this client, by object id. The values are `INetworkEntity`; in Unity each one is a `NetworkObject`. |
| `Rtt` | Round-trip time to the server; 0 for a host's client |
| `IsReplaying` | True while the client replays input during reconciliation |

`NetworkObject.IsOwner` tells whether this client owns an object. The client does not expose its own peer id, so compare ownership through `IsOwner`.

## Messages

`Send(messageId, payload)` and `SendToObject(...)` send messages that are not RPCs, and `Dispatcher` registers handlers for incoming ones, as shown in [raw messages](../messaging/messages.md).

## Errors

A message handler that throws, such as a client RPC, stops the client with `HandlerException` and raises `OnHandlerException`. An object message the client cannot apply stops it with `PrefabMismatch` or `ObjectMismatch` and raises `OnObjectMismatch`. In both cases the package logs the problem itself when nothing subscribes, for a mismatch with the message `Fomoxa stopped the client: object mismatch ...`. A message that fails to decode only gets dropped and raises `OnReceiveDropped`. [Troubleshooting](../getting-started/troubleshooting.md#client-connects-then-stops-with-prefabmismatch-or-objectmismatch) explains what each mismatch kind means.

The [ClientManager reference](../reference/client-manager.md) lists every member, [lifecycle](../concepts/lifecycle.md) gives the order of client events, and [transports](../transports/overview.md) describes what the client connects through.
