# Network simulation

`SimulatedNetworkTransport` wraps another transport and adds latency, jitter, packet loss, duplicates and reordering to what it sends and receives. You can then play on a bad network in the Editor and see what your players will see.

## Basic usage

1. Keep the real transport on a GameObject, for example `UdpNetworkTransport`.
2. Add `SimulatedNetworkTransport` and assign the real transport to its Transport field.
3. Assign `SimulatedNetworkTransport` to the Transport field of the `NetworkManager`.
4. Set the fields below.

Each process simulates its own sends and receives with the same values. A client with a Latency of 50 ms and a server without simulation therefore see about 100 ms more round-trip time, 50 ms each way.

## Fields

| Field | Default | Meaning |
|---|---|---|
| Transport | none | The transport to simulate |
| Latency Milliseconds | 0 | Delay of each packet, in each direction |
| Jitter Milliseconds | 0 | Each packet's delay is Latency plus a random amount between minus and plus Jitter, and never below 0 |
| Packet Loss | 0 | Percentage of packets dropped |
| Duplicate | 0 | Percentage of packets that arrive twice; the copy gets its own delay |
| Reorder | 0 | Percentage of packets held back until the next packet in the same direction has left, or until twice their delay has passed |
| Max Held Packets | 1024 | Packets held in each direction; when it is full, the oldest one is dropped |

With every field at 0, packets pass straight through. A change made in the Inspector while playing applies from the next packet on.

Held packets leave the next time the package sends or receives, which it does every tick, so delays are rounded up to the tick. A received packet's delay starts when the package reads it from the real transport.

## Packets and byte streams

Loss, duplicates and reordering apply only to transports that keep packet boundaries: UDP, encrypted UDP, WebSocket and encrypted WebSocket. TCP, with or without TLS, gets latency and jitter only, and its bytes still arrive in order. When Max Held Packets sends are waiting on a byte stream, the transport refuses more data and the package sends it later.

## What is not simulated

A host's own client connects through the in-process [loopback](loopback.md), which never goes through the transport, so it is not simulated. To test a client on a bad network, run it in a second process, or give a second `NetworkManager` its own client.

With a [`MultiNetworkTransport`](multi-transport.md), assign it to the Transport field of `SimulatedNetworkTransport` to simulate every entry, or put a `SimulatedNetworkTransport` into one entry to simulate only that transport. Each connection keeps the frame budget of the transport it came in on.

## Release builds

The simulation runs only in the Editor and in Development builds. In a release build, `SimulatedNetworkTransport` uses the real transport directly and logs this warning when the `NetworkManager` creates its transport:

```text
Simulated: network simulation runs only in the Editor and in Development builds; UdpNetworkTransport is used directly
```

The first word is the GameObject's name and the last type is the transport it wraps.

## On a console server

A [console server](../../console-server/overview.md) passes a `SimulatedTransportFactory` from `Fomoxa.Networking.Transports` as its transport. It simulates in every build.

```csharp
var conditions = new NetworkConditions
{
    Latency = TimeSpan.FromMilliseconds(50),
    Jitter = TimeSpan.FromMilliseconds(10),
    PacketLoss = 2,
};
var transport = new SimulatedTransportFactory(new UdpTransportFactory(), conditions, () => clock.Elapsed, seed: 1);
```

| Member | Meaning |
|---|---|
| `NetworkConditions` | `Latency`, `Jitter` (`TimeSpan`), `PacketLoss`, `Duplicate`, `Reorder` (percent, `double`) and `MaxHeldPackets`, with the defaults of the fields above. A negative time, a percentage outside 0 to 100 or fewer than 1 held packet throws `ArgumentOutOfRangeException`. Changes apply from the next packet on. |
| `SimulatedTransportFactory(ITransportFactory inner, NetworkConditions conditions, Func<TimeSpan> clock, int? seed = null)` | Wraps `inner`. Pass the same clock as the runtime. With a seed, the same connections in the same order lose the same packets. |

The [transports overview](README.md) lists the transports you can wrap, and [debugging](../../advanced/debugging.md) covers the numbers to watch while you test.
