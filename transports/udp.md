# UDP

`UdpNetworkTransport` sends Fomoxa frames as UDP datagrams, using the UDP transport of Fomoxa.Net. It is the default transport, which a `NetworkManager` adds to itself when none is assigned.

## Basic usage

Add `UdpNetworkTransport` to the GameObject of the `NetworkManager` and assign it to the Transport field. The component has no settings of its own.

```csharp
manager.ServerManager.StartConnection(7777);
manager.ClientManager.StartConnection("203.0.113.10", 7777);
```

## Behavior

| | |
|---|---|
| Connection model | UDP has no connection. The client's transport is ready at once, and the Fomoxa handshake establishes the session. |
| Reliability | None at the transport. The package resends `ReliableOrdered` messages; `Unreliable` messages can be lost. |
| Ordering | None at the transport. The package orders `ReliableOrdered` messages. |
| Frame budget | 1200 bytes. A flush packs messages into bundles up to that size. A larger single message is sent alone, up to one datagram (65507 bytes). |
| Addressing | A host name or an IP address, and a port. The client uses the first resolved address, IPv4 first. |
| Server | Binds the port on all IPv4 interfaces. Port 0 picks a free port. |
| Blocking | Never blocks. |

## Lifecycle

The client's state is `Starting` while it resolves the address and runs the handshake, and becomes `Started` when the handshake succeeds. Because UDP has no connection step, an unreachable server is only noticed through the handshake timeout (Handshake Timeout Seconds, 5 by default), after which the client retries. On the server, a client that disappears is noticed through the heartbeat timeout, while a client that stops normally sends a leave message first.

## Platform limitations

UDP is not available in WebGL builds. Creating the factory in a browser throws `UdpNetworkTransport cannot run in a browser; assign a WebSocketNetworkTransport or a MultiNetworkTransport to the NetworkManager for WebGL builds`. The server listens on IPv4 only, and its UDP port must be open in the firewall.

The [transports overview](overview.md) compares UDP with the other transports, and [channels and reliability](../messaging/channels.md) explains how the package adds reliability on top of it.
