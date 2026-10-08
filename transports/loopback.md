# Loopback

The loopback transport connects a client and a server inside one process by passing frames through in-memory queues, and the package uses it for the host's own client. It does not simulate a network, so it adds no latency, loss or reordering.

## How the host uses it

`ServerManager.StartConnection` opens two listeners, the transport's and a loopback listener. When the same `NetworkManager` then calls `ClientManager.StartConnection`, the client connects to the loopback listener directly. It ignores the address and port, nothing goes through the operating system, and the connection does not reconnect.

The loopback connection still runs the Fomoxa handshake, bundles, reliability and every package message, so from the server's point of view the host's client behaves like a remote client. [Host mode](../core/host-mode.md) describes the rest of the host's behaviour.

## Behavior

| | |
|---|---|
| Connection model | In-process pair of transports, created by the listener |
| Reliability and ordering | Frames arrive in order. Each side holds at most Message Capacity frames (1024 by default); when the queue is full, the oldest frame is dropped. |
| Frame budget | The frame budget of the manager's transport |
| Addressing | None |
| Platforms | Every platform the server runs on; not used in WebGL, where no server can run |

## Using it directly

`LoopbackListener` and `LoopbackTransport`, in `Fomoxa.Networking.Transports`, are public, which makes them useful for tests and for a [custom transport](custom-transport.md) that runs in memory. `new LoopbackListener(maxQueuedPackets)` creates a listener. Its `Connect()` returns the client end of a new pair, and its `Accept()` returns the server end. `LoopbackTransport.CreatePair` creates a connected pair without a listener.

The [transports overview](overview.md) lists the network transports that the loopback connection stands in for.
