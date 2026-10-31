# WebSocket

`WebSocketNetworkTransport` carries Fomoxa frames as binary WebSocket messages, and it is the transport a WebGL client needs. Servers and desktop clients use `Fomoxa.Net.WebSockets`, a library bundled with the package that implements the WebSocket protocol (RFC 6455). WebGL builds use the browser's `WebSocket` object.

## Basic usage

Add `WebSocketNetworkTransport` to the GameObject of the `NetworkManager` and assign it to the Transport field.

A client connects either with a host and a port or with a URL:

```csharp
manager.ClientManager.StartConnection("game.example.com", 8080);
manager.ClientManager.StartConnection("ws://game.example.com:8080/play", 0);
```

With a host and a port, the client connects to `ws://<host>:<port><Path>`. With a `ws://` URL, it uses the URL's host, port, path and query and ignores the port argument, and a URL without a port uses port 80.

## Configuration

| Field | Default | Meaning |
|---|---|---|
| Path | `/` | The path the server accepts and the client requests when no URL is given. It starts with `/` and has no space, `?` or `#`. |
| Max Handshake Bytes | 8192 | Largest HTTP upgrade request the server reads; at least 256 |
| Handshake Timeout Seconds | 5 | Time allowed for the HTTP upgrade: the server waiting for the request, a desktop client waiting for the response, a browser client waiting for the socket to open. For a `wss://` URL on a desktop client, the time also covers the TLS handshake before the upgrade. |
| Allowed Origins | empty | When not empty, the server refuses a request whose `Origin` header is not in the list. Requests without an `Origin` header are accepted. |
| Max Buffered Bytes | 1048576 | In a browser, the amount of unsent data above which the transport stops sending until the browser catches up |

## Behavior

| | |
|---|---|
| Connection model | TCP connection, HTTP/1.1 upgrade, then the Fomoxa handshake |
| Reliability and ordering | Reliable and ordered, like TCP |
| Frame budget | The largest Fomoxa frame |
| Messages | One binary WebSocket message per Fomoxa frame. Extensions and subprotocols are not used. |
| Server | Binds the port on all IPv4 interfaces. A request for another path gets `404 Not Found`, a refused origin `403 Forbidden`, a malformed request `400 Bad Request`, and a version other than 13 `426 Upgrade Required`. |
| Blocking | Never blocks |

## TLS and wss://

A client connects over TLS when you give it a `wss://` URL, and a `wss://` URL without a port uses port 443:

```csharp
manager.ClientManager.StartConnection("wss://game.example.com/play", 0);
```

On a desktop client the package does the TLS handshake itself and checks the server's certificate, as [client TLS](tls.md) describes. The component's `Tls` property holds those settings. In a browser, the browser does TLS.

The server does not do TLS. Put a reverse proxy that terminates TLS in front of it and have it forward the upgraded connection to the server's `ws://` port. Pages served over HTTPS can only open `wss://` connections, so browser clients always need that proxy.

## Origin checks

Browsers send an `Origin` header with the page's origin, such as `https://game.example.com`. Setting Allowed Origins to the origins that host your game keeps other web pages from connecting through a visitor's browser. Desktop clients do not send the header and are always accepted.

## Platform limitations

A WebGL build can only be a client and cannot start a server or a host. In the Editor and in desktop players the component uses the package's own client, and in a WebGL player it uses the browser.

[WebGL](../../deploy/webgl.md) covers browser builds, [multiple transports](multi-transport.md) shows how to serve WebSocket next to UDP, and [deployment](../../deploy/deployment.md) covers the proxy setup on a real server.
