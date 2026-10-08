# Ticks and timing

The package advances the network in fixed steps called ticks. During a tick the server applies input, steps physics and captures state and transforms, and messages are sent at the end of it. The tick belongs to `TimeManager`, which you reach through `NetworkManager.TimeManager`.

## Tick rate

The Tick Rate field of the `NetworkManager` sets the number of ticks per second, 30 by default, and `TimeManager.TickDelta` gives the length of one tick in seconds, `1.0 / TickRate`.

The server decides the tick rate. When a client connects, the server tells it the rate, and the client's `TimeManager.TickRate` follows that value until the connection stops. The client's own Tick Rate field only applies while it is not connected.

## Where ticks run

An enabled `NetworkManager` has two entries in Unity's player loop, one at the start of `EarlyUpdate` and one at the end of `PostLateUpdate`. It adds them when it is enabled and removes them when it is disabled.

At the start of each frame the manager adds the frame's unscaled time (`Time.unscaledDeltaTime`) to an accumulator and runs every tick that is due, up to Max Ticks Per Frame (3 by default). Ticks beyond that limit are dropped rather than carried to the next frame, so a long frame does not lead to a burst of catch-up ticks afterwards. Because the accumulator uses unscaled time, `Time.timeScale` does not slow the network down.

On a client connected to a remote server, the manager also runs its ticks slightly faster or slower to keep its prediction tick at the right distance ahead of the server, as described under [clock synchronization](#clock-synchronization).

## Order of one tick

In the Tick timing mode, one tick runs these steps in order. Physics simulation is on when the `RigidbodyPhysics` component of the `NetworkManager` has Simulate Physics checked, as described in the [physics overview](../physics/overview.md).

1. `TimeManager.Tick` increases by one and `OnPreTick` fires.
2. In the first tick of the frame only, both managers read the messages that arrived, and the client updates its clock estimate.
3. With physics simulation on, the client places the networked bodies it does not predict at their transforms.
4. The client reconciles, then gathers input for its predicted objects, applies it and sends it.
5. The server applies the input for this tick to every object that has an input model.
6. With physics simulation on, the manager steps physics once and queries contacts.
7. The client records its predicted state for this tick, together with the physics state when physics simulation is on. The server sends reconcile states to owners.
8. With physics simulation on, contact events fire.
9. `OnTick` fires, then `OnPostTick`.
10. The server rebuilds part of its observer sets, captures state and transforms, and queues what changed.
11. Both managers flush their send queues.

In the Variable timing mode, step 2 runs once at the start of every frame before the ticks, and step 11 runs once at the end of the frame instead of after each tick. Input and prediction are not available in this mode.

## Timing modes

| Mode | Receive | Send | Prediction |
|---|---|---|---|
| `Tick` (default) | In the first tick of a frame | After every tick | Available |
| `Variable` | At the start of every frame | At the end of every frame | Not available; registering an input model throws |

In both modes, state, transforms and observers are processed per tick.

## Tick events

```csharp
using Fomoxa.Networking;
using Fomoxa.Networking.Sessions;
using Fomoxa.Unity;
using UnityEngine;

public sealed class RoundClock : MonoBehaviour
{
    [SerializeField] private NetworkManager manager;

    public double Elapsed { get; private set; }

    private void Start()
    {
        manager.TimeManager.OnTick += CountTick;
    }

    private void OnDestroy()
    {
        if (manager != null && manager.TimeManager != null)
        {
            manager.TimeManager.OnTick -= CountTick;
        }
    }

    private void CountTick()
    {
        if (manager.ServerManager.State == ServerState.Started)
        {
            Elapsed += manager.TimeManager.TickDelta;
        }
    }
}
```

The example subscribes in `Start` because `NetworkManager` creates its `TimeManager` in `Awake`, and Unity runs every `Awake` of a scene before any `Start`.

`OnPreTick`, `OnTick` and `OnPostTick` fire on both sides for every tick. State and transforms are captured after them, in step 10, so server game logic that must change state before it is sent belongs in `OnTick` or `OnPostTick`.

## Three tick numbers

| Property | On a manager running a server, including a host | On a client connected to a remote server |
|---|---|---|
| `TimeManager.Tick` | The local tick counter | The local tick counter |
| `TimeManager.ServerTick` | Same as `Tick` | The client's estimate of the server's current tick |
| `TimeManager.PredictionTick` | Same as `Tick` | The tick the client's input is for, ahead of the server |

On a manager that runs neither a server nor a connected client, `ServerTick` and `PredictionTick` are 0 and `ClockSynced` is false.

The client sends its input for `PredictionTick`. That tick is ahead of the server by about half the round trip plus a small buffer, so the input reaches the server before the server needs it.

```text
server            ... 98   99   100  101  102  103 ...
                              ↑ ServerTick (estimated)
client input                             ↑ PredictionTick
                              ←── RTT/2 + Input Buffer ──→
```

## Clock synchronization

A remote client sends a ping three times right after connecting and then once every Clock Ping Interval Seconds (1 by default). The server answers with its tick and with how far ahead the client's input has been arriving, and from these answers the client estimates the round-trip time (`ClientManager.Rtt`) and the server tick.

The client aims for a lead of half the round trip, in ticks, plus Input Buffer ticks (2 by default). Once the server reports the actual input lead, the client corrects towards a margin of Input Buffer ticks at the server. It closes the gap by running its ticks up to Max Tick Speed Adjust faster or slower (0.1, that is 10 %), and when the error exceeds Clock Reset Ticks (10) it jumps straight to the target instead.

`TimeManager.ClockSynced` stays false until the first answer arrives, and the client does not predict before then. The [prediction overview](../prediction/overview.md) shows how prediction uses these ticks, [lifecycle](lifecycle.md) gives the order of events for connections and network objects, and the [TimeManager reference](../reference/time-manager.md) lists its members.
