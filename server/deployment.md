# Deployment

This page lists what a server host and its network need. Hosting, matchmaking and relay services are not part of the package.

## Ports and protocols

| Transport | Protocol to open | Port |
|---|---|---|
| UDP | UDP inbound | The port passed to `StartConnection` |
| TCP | TCP inbound | The port passed to `StartConnection` |
| WebSocket | TCP inbound | The port passed to `StartConnection`, or the proxy's port |
| Multiple | Each entry's protocol | The first entry on the port passed to `StartConnection`, the others on their configured ports |

Servers bind all IPv4 interfaces, so clients must reach the server over IPv4.

## Browser clients

A page served over HTTPS can only open `wss://` connections, so run a reverse proxy that terminates TLS and forwards WebSocket upgrades to the server's `ws://` port. The server's WebSocket Path must match the path the proxy forwards to. Set Allowed Origins on the `WebSocketNetworkTransport` to the origins that serve your game. [WebSocket](../transports/websocket.md) describes these settings.

## Versions

A client can only connect to a server built from the same models, because the handshake compares schemas and refuses any other with `SchemaConflict`. Prefabs and scene objects must match as well, or clients stop with `PrefabMismatch` when objects spawn. When you release a new version, update the server and the clients together, or run the old and the new server side by side on different ports.

## Timeouts

| Setting | Default | Effect |
|---|---|---|
| Handshake Timeout Seconds | 5 | A client that does not finish the handshake in time fails and retries |
| Heartbeat Interval Seconds | 5 | Silence after which a connection sends a probe |
| Heartbeat Timeout Seconds | 15 | Time a probe may go unanswered before the connection stops |

With the defaults, the server removes a client that vanished without closing about 20 seconds after its last message, and despawns its objects. Lower values free resources sooner, but they also disconnect players on poor networks sooner.

## Server load

The server's work grows with the number of objects, observers and peers. You can lower it with an [observer rule](../core/observers.md), small state models and a tick rate no higher than the game needs, as [performance](../advanced/performance.md) explains in more detail.

To build the server itself, see [dedicated server](dedicated-server.md). The [transports overview](../transports/overview.md) compares the transports whose ports you open.
