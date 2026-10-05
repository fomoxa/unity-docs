# WebGL

A WebGL build runs in a browser and can only be a client. It connects to the server through the browser's `WebSocket` object by way of the package's `FomoxaWebSocket.jslib` plugin, while the server runs as a desktop or server build with a WebSocket listener.

## Setup

1. On the server side, use a `WebSocketNetworkTransport`, alone or as an entry of a `MultiNetworkTransport` next to UDP for desktop clients.
2. In the scene the WebGL build uses, give the `NetworkManager` a `WebSocketNetworkTransport`, or a `MultiNetworkTransport` that contains one. In a browser, `MultiNetworkTransport` skips the entries that cannot run there.
3. Connect with the WebSocket port or with a URL:

```csharp
manager.ClientManager.StartConnection("wss://game.example.com/play", 0);
```

Both `ws://` and `wss://` URLs work in the browser, since the browser handles TLS. With a host name and port, the client connects to `ws://<host>:<port><Path>`.

## Behavior in the browser

The connection opens asynchronously, and if the socket has not opened within Handshake Timeout Seconds, the client fails the attempt and retries. When more than Max Buffered Bytes are waiting in the browser's send buffer, the transport reports that it cannot send, and the package keeps the messages queued until the buffer drains. Everything else, including prediction, observers and scenes, works as it does on desktop clients.

## What does not work

| Action | Result |
|---|---|
| `ServerManager.StartConnection` | Throws `PlatformNotSupportedException`: `a server cannot listen in a browser; WebGL builds are clients only` |
| Host mode | Not possible, because it starts a server |
| `UdpNetworkTransport` or `TcpNetworkTransport` as the transport | The `NetworkManager` throws when it starts: `<Transport> cannot run in a browser; assign a WebSocketNetworkTransport or a MultiNetworkTransport to the NetworkManager for WebGL builds` |

## Hosting

Browsers refuse `ws://` connections from HTTPS pages, so serve the page over HTTPS and the game server over `wss://` through a TLS-terminating proxy. Set Allowed Origins on the server's `WebSocketNetworkTransport` as well. [Deployment](../server/deployment.md) covers the server side of this setup.

The [WebSocket](../transports/websocket.md) page describes the transport's settings, and [multiple transports](../transports/multi-transport.md) shows how one server serves WebGL and desktop clients together.
