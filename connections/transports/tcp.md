# TCP

`TcpNetworkTransport` carries Fomoxa frames over a TCP connection, using the TCP transport of Fomoxa.Net.

## Basic usage

Add `TcpNetworkTransport` to the GameObject of the `NetworkManager` and assign it to the Transport field. The server and the clients must all use TCP.

## TLS

The component's Inspector setting, Use Tls, makes a client open TLS before the Fomoxa handshake. Use it when the client connects through a proxy or an ingress that terminates TLS in front of the server. The server ignores the setting. [Client TLS](tls.md) covers the certificate check, the `Tls` property and the failures.

## Behavior

| | |
|---|---|
| Connection model | The client opens a TCP connection, then runs the Fomoxa handshake. |
| Reliability | Reliable stream. The package's reliable channel still numbers and acknowledges its messages. |
| Ordering | In order. A lost packet delays everything behind it until TCP resends it. |
| Frame budget | The largest Fomoxa frame. A flush can pack every queued message into one bundle. |
| Addressing | A host name or an IP address, and a port. The client tries each resolved address in turn, IPv4 first, until one connects. |
| Server | Binds the port on all IPv4 interfaces. Port 0 picks a free port. |
| Blocking | Never blocks; the connection is made with a non-blocking socket. |

## Lifecycle

A refused or failed connection stops the client with `StopReason.TransportError`, after which it retries. With Use Tls, a server certificate the client refuses, or a TLS alert from the server, stops it with `TlsRejected` instead, and it does not retry. When an established connection closes, the session stops with `PeerClosed` or `TransportError`, depending on how it closed.

## Platform limitations

TCP is not available in WebGL builds, where creating the factory throws `TcpNetworkTransport cannot run in a browser; ...`. The server listens on IPv4 only, and its TCP port must be open in the firewall.

The [transports overview](README.md) compares TCP with the other transports. [WebSocket](websocket.md) also runs over TCP and is the option for browsers.
