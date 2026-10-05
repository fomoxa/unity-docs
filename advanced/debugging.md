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
| `OnHandlerException` | both | A message handler threw; the peer is disconnected or the client stops |
| `OnObjectMismatch` | `ClientManager` | The client could not apply an object message and stops |

The package logs `OnSendDropped` and `OnReceiveDropped` by default, which you can turn off with Log Send Dropped and Log Receive Dropped on the `NetworkManager`. It logs `OnHandlerException` and `OnObjectMismatch` only while nothing is subscribed to them.

## Values to watch

| Value | Meaning |
|---|---|
| `ClientManager.Rtt` | The client's round-trip time to the server |
| `ServerManager.RttOf(peerId)` | A client's round-trip time, as the client reported it |
| `ServerManager.DroppedInputsOf(peerId)` | Inputs from a client that arrived too late or too early |
| `ServerManager.PeerCount` | Connected clients |
| `TimeManager.ClockSynced` | The client has a clock estimate and can predict |
| `TimeManager.ServerTick`, `PredictionTick` | The client's view of the server tick and its input tick |
| `NetworkBehaviour.IsPredicting` | The owner's client predicts this behaviour |
| `NetworkBehaviour.ReconcileCount` | Corrections since the behaviour was created |

A small on-screen overlay can show the most useful of these values:

```csharp
using Fomoxa.Unity;
using UnityEngine;

public sealed class NetworkStats : MonoBehaviour
{
    [SerializeField] private NetworkManager manager;

    private void OnGUI()
    {
        TimeManager time = manager.TimeManager;
        GUILayout.Label($"client {manager.ClientManager.State}, rtt {manager.ClientManager.Rtt.TotalMilliseconds:0} ms");
        GUILayout.Label($"tick {time.Tick}, server {time.ServerTick}, prediction {time.PredictionTick}, synced {time.ClockSynced}");
        GUILayout.Label($"server {manager.ServerManager.State}, peers {manager.ServerManager.PeerCount}");
    }
}
```

## Testing with several processes

The simplest setup is a server build with the Editor connecting to it as a client, or the other way round. Host mode tests a server and a client in one process, but keep in mind that the host shares instances and does not predict. A scene can also hold several `NetworkManager` components, for example a server and a client that connect through their transport, in which case only one of them steps each physics world.

## Inspecting the wire

Each generation writes `.fomoxa/schema.json` and `.fomoxa/schema.inspect.json` into the project. The second file describes every message, including the package's Unity type codecs, for Fomoxa's inspection tools, which are not part of the package.

[Troubleshooting](../getting-started/troubleshooting.md) goes from symptoms to causes, [events and callbacks](../reference/callbacks.md) lists every event, and [performance](performance.md) covers the settings that change what the package sends.
