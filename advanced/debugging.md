# Debugging

## Log messages

The package logs with two prefixes. Messages from Editor steps, such as code generation, prefab and scene ids and build checks, start with `[Fomoxa]`. Run-time warnings and errors, such as dropped messages, rejected RPCs and object mismatches, start with `Fomoxa`. [Errors and stop reasons](../reference/errors.md) lists the messages and what causes them.

## Events

To log or count problems in your own format, subscribe to these events:

| Event | On | Raised when |
|---|---|---|
| `OnClientConnectionState` | `ClientManager` | The client's connection changes state |
| `OnServerConnectionState`, `OnRemoteConnectionState` | `ServerManager` | The server or a client connection changes state |
| `OnSendDropped` | both | A queued message could not be sent, for example `TooLarge` |
| `OnReceiveDropped` | both | A received bundle or model could not be read |
| `OnHandlerException` | both | A message handler threw; the server closes that peer's connection, or the client stops |
| `OnObjectMismatch` | `ClientManager` | The client could not apply an object message and stops |

The package logs `OnSendDropped` and `OnReceiveDropped` by default, which you can turn off with Log Send Dropped and Log Receive Dropped on the `NetworkManager`. It logs `OnHandlerException` and `OnObjectMismatch` only while nothing is subscribed to them.

## Values to watch

| Value | Meaning |
|---|---|
| `ClientManager.Rtt` | The client's round-trip time to the server |
| `ServerManager.RttOf(peerId)` | A client's round-trip time, as the client reported it |
| `ServerManager.DroppedInputsOf(peerId)` | Inputs from a client that arrived too late or too early |
| `ServerManager.DroppedInputs` | Dropped inputs of every client since the server was created, including clients that have left |
| `ServerManager.PeerCount` | Connected clients |
| `ClientManager.Statistics`, `ServerManager.Statistics` | [Traffic counters](#traffic-counters), while Collect Statistics is on |
| `TimeManager.ClockSynced` | The client has a clock estimate and can predict |
| `TimeManager.ServerTick`, `PredictionTick` | The client's view of the server tick and its input tick |
| `NetworkBehaviour.IsPredicting` | The owner's client predicts this behaviour |
| `NetworkBehaviour.ReconcileCount` | Corrections since the behaviour was created |
| `NetworkTransform.LastCorrection` | How far the last [correction](#prediction-corrections) moved the object |

## On-screen statistics

`NetworkStatsDisplay` draws the most useful of these values in a corner of the Game view. Add it to the GameObject that holds the `NetworkManager`, or to any GameObject and assign the manager to its Manager field.

```text
Client Started, RTT 42 ms
Client sent 30 bundles/s, 2.1 KiB/s, 28 messages/s, 0 resent/s
Client received 30 bundles/s, 1.8 KiB/s, 29 messages/s, 0 duplicates/s
Reconciles 120, 2.0/s
Tick 1200, server 1200, prediction 1203, clock synced
```

A client shows the client lines, a server the server lines and a host both. The server lines read `Server Started, 3 peers`, the traffic of every peer added together, and `Dropped inputs 4`.

| Field | Default | Meaning |
|---|---|---|
| Manager | none, then the `NetworkManager` on the same GameObject | The manager to read |
| Show Connection | on | State, round-trip time and peer count |
| Show Traffic | off | Bundles, KiB, messages and repeats per second in each direction; needs Collect Statistics on the manager |
| Show Time | on | Tick, server tick, prediction tick and whether the clock is synced |
| Show Prediction | off | `ReconcileCount` of every spawned object added together, with a rate, on a client; `ServerManager.DroppedInputs` on a server |
| Corner | `TopLeft` | `TopLeft`, `TopRight`, `BottomLeft` or `BottomRight` |
| Average Seconds | 1 | How often the numbers are read; rates are the change over that time. At least 0.1. |
| Run In Release Builds | off | When off, the component does nothing in a release build. The Editor and Development builds always show it. |

`resent/s` counts messages the sender sent again, and `duplicates/s` counts messages that the receiver already had, from extra resends or duplicated packets. A host's client does not predict, so its `Reconciles` stays at 0. The numbers use the invariant culture, and the time is real time, so `Time.timeScale` does not change the rates.

## Traffic counters

Turn on Collect Statistics on the `NetworkManager` to count what the package sends and receives. The manager reads the field once, when it starts, and the counters cost nothing while it is off. A console server sets `NetworkSettings.CollectStatistics`.

`ClientManager.Statistics` is a `TrafficStatistics` and `ServerManager.Statistics` a `ServerTrafficStatistics`, both in `Fomoxa.Networking.Sessions` and both `null` while Collect Statistics is off. The server's totals include peers that have left, `Of(peerId)` returns the counters of one connected peer or `null`, and none of the counters reset when a client reconnects or a server restarts.

| Member | Meaning |
|---|---|
| `Sent`, `Received` | One `TrafficDirection` for each direction |
| `TrafficDirection.Bundles` | A `TrafficCount` of the bundles and their bytes |
| `TrafficDirection.Total` | A `MessageTraffic` of every message added together |
| `TrafficDirection.Messages` | `IReadOnlyDictionary<uint, MessageTraffic>` by message id; a row appears the first time its id is counted |
| `TrafficCount` | `long Count` and `long Bytes` |

Each `MessageTraffic` holds five `TrafficCount` values:

| Member | Sent | Received |
|---|---|---|
| `New` | Messages sent for the first time | Messages received for the first time, including a resend whose original was lost |
| `Repeated` | Resent reliable messages | Reliable messages already received, from extra resends or duplicated packets |
| `Ack` | Acknowledgements | Acknowledgements |
| `Fragment` | Pieces of messages too large for one bundle, in the rows of the fragment ids | Pieces received |
| `Split` | Large messages whose last piece has been sent, in the row of the original id, with the bytes of the whole message | Large messages put back together |

The counters measure the package's bundles and messages. A message's bytes include its reliable sequence number and object header. Fomoxa frames, heartbeats, the handshake and encryption are not counted, so the bytes on the network are somewhat higher. `Split` repeats bytes that `Fragment` already counted, so leave it out when you add bytes up.

`FomoxaRegistry.NameOf(messageId)` turns an id into the name that the code generation records, such as `Greeting.net`, or `null` when it has none. Projects generated before version 0.3.4 get the names at the next generation.

```csharp
using System.Linq;
using Fomoxa.Networking.Sessions;
using Fomoxa.Unity;
using UnityEngine;

public sealed class TopMessages : MonoBehaviour
{
    [SerializeField] private NetworkManager manager;

    [ContextMenu("Log top messages")]
    private void LogTopMessages()
    {
        TrafficStatistics statistics = manager.ClientManager.Statistics;
        if (statistics == null)
        {
            Debug.Log("Turn on Collect Statistics on the NetworkManager");
            return;
        }

        foreach (var row in statistics.Sent.Messages.OrderByDescending(row => row.Value.New.Bytes).Take(5))
        {
            string name = manager.Registry.NameOf(row.Key) ?? row.Key.ToString("X8");
            Debug.Log($"{name}: {row.Value.New.Count} messages, {row.Value.New.Bytes} bytes, {row.Value.Repeated.Count} resent");
        }
    }
}
```

## Simulating a bad network

[`SimulatedNetworkTransport`](../connections/transports/simulated.md) wraps the real transport and adds latency, jitter, loss, duplicates and reordering in the Editor and in Development builds. A host's own client is not simulated.

## Prediction corrections

`NetworkTransform` reports how far each prediction correction moves the object on the owner's client.

| Member | Meaning |
|---|---|
| `event Action<TransformCorrection> OnCorrected` | Raised after every replay that includes the object. An object replayed only because it shares a physics world with a corrected one also raises it, usually with an offset near 0. An exception in a handler is logged. |
| `TransformCorrection? LastCorrection` | The last correction; `null` until the first one |
| Draw Corrections, `DrawCorrections` | Draws each correction in the Scene view, and in the Game view while Gizmos is on: a red dot where the object was, a green dot where it is after the replay and a yellow line between them. Editor only, off by default. |
| Correction Seconds, `CorrectionSeconds` | How long a drawn correction stays, 2 by default, at least 0.1. At most 64 corrections are drawn at once. |

| `TransformCorrection` member | Meaning |
|---|---|
| `Tick` | The tick of the server state that was corrected |
| `PositionBefore`, `RotationBefore` | The world pose shown just before the correction |
| `PositionAfter`, `RotationAfter` | The world pose just after the replay |
| `PositionOffset` | `PositionAfter - PositionBefore` |
| `RotationDegrees` | The angle between the two rotations |

The pose is the Visual's when the field is set, and otherwise the object's own transform. With a Visual, the pose before a correction includes what is left of the smoothing of the previous one, which is the jump the player sees.

```csharp
using Fomoxa.Unity;
using UnityEngine;

public sealed class LogLargeCorrections : MonoBehaviour
{
    [SerializeField] private NetworkTransform networkTransform;
    [SerializeField] private float threshold = 0.5f;

    private void OnEnable() => networkTransform.OnCorrected += Report;

    private void OnDisable() => networkTransform.OnCorrected -= Report;

    private void Report(TransformCorrection correction)
    {
        if (correction.PositionOffset.magnitude > threshold)
        {
            Debug.Log($"tick {correction.Tick}: moved {correction.PositionOffset.magnitude:0.00} m, turned {correction.RotationDegrees:0.0} degrees");
        }
    }
}
```

## Testing with several processes

The simplest setup is a server build with the Editor connecting to it as a client, or the other way round. Host mode tests a server and a client in one process, but keep in mind that the host shares instances and does not predict. A scene can also hold several `NetworkManager` components, for example a server and a client that connect through their transport, in which case only one of them steps each physics world.

## Inspecting the wire

Each generation writes `.fomoxa/schema.json` and `.fomoxa/schema.inspect.json` into the project. The second file describes every message, including the package's Unity type codecs, for Fomoxa's inspection tools, which are not part of the package.

[Troubleshooting](../getting-started/troubleshooting.md) goes from symptoms to causes, [events and callbacks](../reference/callbacks.md) lists every event, and [performance](performance.md) covers the settings that change what the package sends.
