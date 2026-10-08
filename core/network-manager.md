# NetworkManager

`NetworkManager` is the component that runs networking for a scene. It holds the configuration, runs the tick loop inside Unity's player loop, and owns one `ServerManager`, one `ClientManager`, one `TimeManager` and one `TransportManager`.

The package offers no static access to a manager, so keep a reference to it, for example in a serialized field, and reach the server and the client through that reference.

## Basic usage

1. Create an empty GameObject, for example `Network Manager`.
2. Add a transport component, such as `UdpNetworkTransport`.
3. Add `NetworkManager` and assign the transport to its Transport field.
4. Assign the generated `FomoxaPrefabList.asset` to Collected Prefabs and `FomoxaSceneList.asset` to Collected Scenes.

Then start it from code:

```csharp
manager.ServerManager.StartConnection(7777);
manager.ClientManager.StartConnection("127.0.0.1", 7777);
```

Calling both methods on the same manager makes it a host.

## Sub-managers

| Property | Type | Purpose |
|---|---|---|
| `ServerManager` | [`ServerManager`](server.md) | Starts and stops the server, spawns objects, observers, network scenes |
| `ClientManager` | [`ClientManager`](client.md) | Connects to a server, reconnects, the client's spawned objects |
| `TimeManager` | [`TimeManager`](../reference/time-manager.md) | Tick rate, tick numbers, tick events |
| `TransportManager` | `TransportManager` | The transport component and the factory created from it |
| `Prefabs` | `PrefabRegistry` | Prefabs the manager can spawn; see [spawning](spawning.md) |
| `Scenes` | `SceneRegistry` | Network scenes the manager can load; see [network scenes](scenes.md) |
| `Registry` | `FomoxaRegistry` | Schema, codecs, channels and RPC ids. Defaults to `FomoxaRegistry.Default`, which the generated code fills |

The sub-managers are created in `Awake`, so use them from `Start` or later.

## Fields

You set these fields in the Inspector. The manager reads them once, in `Awake`, so changing them in Play Mode has no effect.

### Transport and timing

| Field | Default | Meaning |
|---|---|---|
| Transport | none | The transport component. Without one, the manager adds a `UdpNetworkTransport` to its GameObject. |
| Tick Rate | 30 | Ticks per second. A client follows the server's rate while connected. |
| Timing Mode | Tick | `Tick` receives and sends per tick and allows prediction. `Variable` receives at the start and sends at the end of each frame. See [ticks and timing](../concepts/tick.md). |
| Max Ticks Per Frame | 3 | Ticks a single frame may run. Ticks beyond it are dropped. |

### Send queue

| Field | Default | Meaning |
|---|---|---|
| Message Capacity | 1024 | Messages one connection's queue holds before a send returns `Full` |
| Byte Capacity | 1048576 | Bytes one connection's queue holds before a send returns `BytesFull` |
| Reliable Window | 1024 | Reliable messages in flight without acknowledgement, per connection |
| Log Send Dropped | on | Logs a warning when a queued message could not be sent |
| Log Receive Dropped | on | Logs a warning when a received bundle could not be read |

### Connection

| Field | Default | Meaning |
|---|---|---|
| Max Reconnect Retries | -1 | Times a client tries again after losing or failing a connection. -1 retries forever. |
| Reconnect Interval Seconds | 0.5 | Wait before each retry |
| Handshake Timeout Seconds | 5 | Time the handshake may take before the connection fails |
| Heartbeat Interval Seconds | 5 | Silence after which a connection sends a probe |
| Heartbeat Timeout Seconds | 15 | Time a probe may stay unanswered before the connection stops with `Timeout` |

### Prefabs and scenes

| Field | Default | Meaning |
|---|---|---|
| Collect Prefabs | on | Registers the prefabs of Collected Prefabs. A build assigns the list only while this is on. |
| Collected Prefabs | none | The generated `FomoxaPrefabList.asset` |
| Collected Scenes | none | The generated `FomoxaSceneList.asset` |
| Prefabs | empty | Additional prefabs to register |

### Observers

| Field | Default | Meaning |
|---|---|---|
| Observer Rule | none | A [`ObserverRule`](observers.md) asset. Without one, every client observes every object. |
| Observer Interval | 15 | Ticks over which the server spreads one full recalculation of the observer sets |

### Prediction

| Field | Default | Meaning |
|---|---|---|
| Clock Ping Interval Seconds | 1 | Time between clock pings of a remote client |
| Input Buffer | 2 | Ticks of margin the client keeps between its input's arrival and the server's use of it |
| Max Tick Speed Adjust | 0.1 | Largest change of the client's tick speed while it catches up, as a fraction |
| Clock Reset Ticks | 10 | Clock error, in ticks, at which the client jumps instead of adjusting speed |
| Input Redundancy | 3 | Inputs per input message: the current one and the previous ones, to cover lost packets |
| Max Input Lead | 30 | Ticks ahead of the server that input may be; input further ahead is dropped |
| Prediction History | 64 | Ticks of input, predicted state and physics the client keeps for replay |
| Reconcile Interval | 1 | The server sends the owner its state every this many ticks |

### Physics

| Field | Default | Meaning |
|---|---|---|
| Physics | none | The physics component, `RigidbodyPhysics`. Without one, the manager adds a `RigidbodyPhysics` with Simulate Physics off. Server and clients must use the same physics backend. See [physics](../physics/overview.md#turning-it-on). |

`RigidbodyPhysics` has one field, Simulate Physics (off by default). With it on, the manager steps Unity physics once per tick and enables physics rollback.

## Several managers

A scene may hold more than one `NetworkManager`, for example a server and a client in one process for tests, and each manager has its own server, client and tick. Two managers connect to each other through their transports. The host's in-process connection does not apply here, because it only joins a client to the server of the same manager.

Only one manager steps a given physics scene; see [physics](../physics/overview.md#one-world-one-owner).

## Limitations

The fields cannot be set from code; `Registry` is the only settable property. A manager added with `AddComponent` therefore uses the defaults, and it adds a `UdpNetworkTransport` and a `RigidbodyPhysics` unless those components are assigned through the Inspector. A manager only ticks while it is enabled and in a loaded scene.

The [NetworkManager reference](../reference/network-manager.md) and [configuration](../reference/configuration.md) list every member and field. The [server](server.md), [client](client.md) and [host mode](host-mode.md) pages describe what the manager runs.
