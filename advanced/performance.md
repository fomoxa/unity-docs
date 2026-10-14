# Performance

This page lists the settings and habits that change how much the package sends and computes. The right values depend on the game, so measure before and after each change.

## Tick rate

Most of the work happens once per tick, including input, physics, state and transform capture, observer updates and flushing. Halving the tick rate therefore roughly halves that work and the number of packets. Choose the lowest rate that keeps the game responsive and matches its physics.

## Bandwidth

| Lever | Effect |
|---|---|
| Bundling | Messages queued in one tick leave together, packed into frames of the transport's frame budget (1200 bytes for UDP). Many small messages cost few packets. |
| State | Sent only when its encoding changed, and as a delta when that is smaller. Keep state models small and fixed in size so deltas apply. Split rarely and often changing data into different behaviours. |
| `NetworkTransform` | Sends only the parts that moved more than their threshold, and nothing while still. Turn off the parts you do not need; raise thresholds for objects where precision matters less. |
| `NetworkAnimator` | Float Step rounds float parameters, so tiny changes do not trigger a message. |
| Observers | An [observer rule](../objects/observers.md) keeps each client from receiving objects it does not need. This is usually the largest saving in big worlds. |
| Input Redundancy | Each input message carries this many inputs. Higher values survive more loss and cost more bytes. |
| Reconcile Interval | The server sends reconcile states every this many ticks. Higher values send less and correct later. |
| Channels | Reliable messages carry a sequence number and need acknowledgements. Use the unreliable channel for data that is replaced soon anyway. |

## Server CPU

Observer recalculation is spread over Observer Interval ticks, so a longer interval costs less per tick but reacts more slowly to movement. `ObserverRule.Observes` runs for each peer and object being recalculated and should be cheap; `DistanceRule`, for example, caches the positions of each peer's owned objects per tick.

Every behaviour with state is encoded once per tick to detect changes, so many objects with large state models cost encoding time even when nothing has changed.

## Client CPU

A correction replays every tick since the corrected one, and with physics it also steps every world of the rollback group once per replayed tick. Keep Prediction History and the number of predicted worlds as small as the game allows, and keep corrections rare, as described in [reconciliation](../prediction/reconciliation.md#diagnosing-frequent-corrections). Max Ticks Per Frame limits how much a client catches up after a slow frame, and drops the ticks beyond it.

## Queues and limits

Each connection has a send queue limited by Message Capacity and Byte Capacity, plus a reliable window. A send that does not fit is not queued and returns `SendResult.Full`, `BytesFull` or `TooLargeForQueue`. Raising the limits costs more memory per connection, and hitting them usually means the game sends faster than the connection can carry.

## Allocations

Adapters encode into a reused buffer, and RPC sends copy the bytes into the queue. State and input decode into the instances you registered, whereas each received RPC with a model creates a new instance of the model for the handler.

[Channels and reliability](../messaging/channels.md) explains bundling and the reliable window, [debugging](debugging.md) lists the values worth watching while you measure, and [configuration](../reference/configuration.md) lists every setting mentioned here.
