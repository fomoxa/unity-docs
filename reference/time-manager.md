# TimeManager reference

`public sealed class TimeManager` in `Fomoxa.Unity` has no public constructor; you reach it through `NetworkManager.TimeManager`. [Ticks and timing](../concepts/tick.md) explains the concepts behind it.

## Properties

| Property | Type | Description |
|---|---|---|
| `TickRate` | `int` | Ticks per second. The configured value, or the server's while a remote client is connected. |
| `TickDelta` | `double` | Seconds per tick, `1.0 / TickRate` |
| `MaxTicksPerFrame` | `int` | Ticks a frame may run |
| `Mode` | `TimingMode` | `Tick` or `Variable` |
| `Tick` | `uint` | The local tick counter, increased at the start of every tick |
| `ServerTick` | `uint` | On a manager running a server, equal to `Tick`. Otherwise the client's estimate of the server tick, 0 until the first clock answer. |
| `PredictionTick` | `uint` | On a manager running a server, equal to `Tick`. Otherwise, in the Tick mode, the tick the client's input is for, and in the Variable mode the estimated server tick; 0 until the first clock answer. |
| `ClockSynced` | `bool` | True on a manager running a server. Otherwise true once the client has received a clock answer from its server. |

## Events

| Event | Fires |
|---|---|
| `OnPreTick` | At the start of a tick, after `Tick` increased |
| `OnTick` | After input, physics and contact events of the tick |
| `OnPostTick` | Right after `OnTick` |

All three are `Action` events and fire on the main thread inside the player loop's `EarlyUpdate`.

## TimingMode

| Value | Meaning |
|---|---|
| `Tick` | Receive in the first tick of a frame, send after every tick; prediction available |
| `Variable` | Receive at the start of a frame, send at its end; prediction not available |

The related types are [NetworkManager](network-manager.md) and [ClientManager](client-manager.md).
