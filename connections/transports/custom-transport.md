# Custom transport

A custom transport connects the package to another way of moving bytes, such as a relay service, a platform SDK or an in-memory link for tests. It is a `NetworkTransport` component that creates an `ITransportFactory`, and neither the rest of the package nor your game code has to change.

## The pieces

| Type | Namespace | Role |
|---|---|---|
| `NetworkTransport` | `Fomoxa.Unity` | The component on the `NetworkManager`; `CreateFactory()` returns the factory |
| `ITransportFactory` | `Fomoxa.Networking.Transports` | `FrameBudget`, `CreateListener(port, out boundPort)`, `CreateConnector(address, port)` |
| `ITransportConnector` | `Fomoxa.Networking.Transports` | A connection attempt. `Poll(out ITransport)` returns `Pending`, `Connected` or `Failed`; `Dispose()` cancels it |
| `IListenerTransport` | `Fomoxa.Net.Transports` | The server side. `Accept()` returns an `AcceptOutcome`; `Dispose()` closes it |
| `ITransport` | `Fomoxa.Net.Transports` | One connection: `Kind`, `Send`, `Receive`, `CloseGracefully`, `Dispose` |

## Rules

The most important rule is never to block. The package calls every method from the main thread, each tick, and expects an answer at once. `Poll` therefore returns `Pending` until the connection is ready, `Receive` returns `ReceiveOutcome.WouldBlock` when nothing has arrived, and `Send` returns `SendOutcome.WouldBlock` when it cannot take the bytes right now. `Accept` returns `AcceptOutcome.Pending` when nobody is waiting, `Accepted(transport)` for a new connection, `Progress` when it made progress without having a connection yet, and `Error` on failure.

`Kind` is `TransportKind.Message` when each `Send` arrives as one `Receive`, as with datagrams and WebSocket messages, and `TransportKind.Stream` when bytes arrive as a stream, as with TCP.

Apart from `WouldBlock`, `Receive(buffer)` returns `ReceiveOutcome.NeedCapacity(size)` when the next message does not fit in the buffer, `Ok(count)` with the number of bytes copied, `Closed` after a graceful close by the other side, and `Error` on failure. `Send` returns `SendOutcome.TooLarge` for bytes it can never send, `Closed` after the connection has closed, and `Error` on failure.

`FrameBudget` is the largest frame the package should build. Use the size your link carries without splitting, or `FomoxaWire.MaxDataFrameSize` for links without a practical limit.

## Example: an in-memory transport

The following transport connects clients to a server in the same process through the package's loopback types, and shows the shape of every piece.

```csharp
using Fomoxa.Net;
using Fomoxa.Net.Transports;
using Fomoxa.Networking.Transports;
using Fomoxa.Unity;

public sealed class InMemoryNetworkTransport : NetworkTransport
{
    private InMemoryTransportFactory factory;

    public override ITransportFactory CreateFactory() => factory ??= new InMemoryTransportFactory();

    private sealed class InMemoryTransportFactory : ITransportFactory
    {
        private LoopbackListener network;

        public int FrameBudget => FomoxaWire.MaxDataFrameSize;

        public IListenerTransport CreateListener(ushort port, out ushort boundPort)
        {
            boundPort = port;
            network = new LoopbackListener(64);
            return network;
        }

        public ITransportConnector CreateConnector(string address, ushort port) => new InMemoryConnector(this);

        private sealed class InMemoryConnector : ITransportConnector
        {
            private readonly InMemoryTransportFactory owner;

            public InMemoryConnector(InMemoryTransportFactory owner)
            {
                this.owner = owner;
            }

            public ConnectStatus Poll(out ITransport transport)
            {
                transport = owner.network?.Connect();
                return transport == null ? ConnectStatus.Failed : ConnectStatus.Connected;
            }

            public void Dispose()
            {
            }
        }
    }
}
```

The component returns the same factory instance on every call, so the server and the client share it, and two `NetworkManager` components that use the same `InMemoryNetworkTransport` component connect to each other.

## Browser builds

A transport that cannot run in a browser should throw `PlatformNotSupportedException` from `CreateFactory` in a WebGL player, because `MultiNetworkTransport` skips entries that throw it in a browser.

The [transports overview](README.md) describes how the factory plugs into the `NetworkManager`, and [loopback](loopback.md) documents the in-memory types used in the example.
