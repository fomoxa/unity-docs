# Configuration reference

This page lists the Inspector fields of every component and asset. Unless noted otherwise, a field is read when its component starts.

## NetworkManager

The [NetworkManager](../connections/network-manager.md) guide explains what each field does.

| Field | Type | Default | Range |
|---|---|---|---|
| Transport | `NetworkTransport` | none, then a `UdpNetworkTransport` is added | |
| Tick Rate | `int` | 30 | 1 to 65535 |
| Timing Mode | `TimingMode` | `Tick` | |
| Max Ticks Per Frame | `int` | 3 | at least 1 |
| Message Capacity | `int` | 1024 | at least 1 |
| Byte Capacity | `int` | 1048576 | at least 1 |
| Reliable Window | `int` | 1024 | 1 to 16384 |
| Close Timeout Seconds | `float` | 1 | |
| Authentication Timeout Seconds | `float` | 30 | 0 or less: no limit |
| Authenticator | `NetworkAuthenticator` | none | |
| Log Send Dropped | `bool` | true | |
| Log Receive Dropped | `bool` | true | |
| Max Reconnect Retries | `int` | -1 (no limit) | |
| Reconnect Interval Seconds | `float` | 0.5 | |
| Handshake Timeout Seconds | `float` | 5 | |
| Heartbeat Interval Seconds | `float` | 5 | |
| Heartbeat Timeout Seconds | `float` | 15 | |
| Collect Prefabs | `bool` | true | |
| Collected Prefabs | `NetworkPrefabList` | none | |
| Collected Scenes | `NetworkSceneList` | none | |
| Prefabs | `List<NetworkObject>` | empty | |
| Observer Rule | `ObserverRule` | none | |
| Observer Interval | `int` | 15 | at least 1 |
| Clock Ping Interval Seconds | `float` | 1 | above 0 |
| Input Buffer | `int` | 2 | at least 0 |
| Max Tick Speed Adjust | `float` | 0.1 | 0 to below 1 |
| Clock Reset Ticks | `int` | 10 | at least 1 |
| Input Redundancy | `int` | 3 | at least 1 |
| Max Input Lead | `int` | 30 | at least 1 |
| Prediction History | `int` | 64 | at least 1 |
| Reconcile Interval | `int` | 1 | at least 1 |
| Physics | `NetworkPhysics` | none; the manager adds a `RigidbodyPhysics` | |

A value outside its range throws when the manager starts.

## RigidbodyPhysics

| Field | Type | Default |
|---|---|---|
| Simulate Physics | `bool` | false |

## NetworkObject

| Field | Type | Default |
|---|---|---|
| Prefab Id | `uint` | assigned by the Editor |
| Explicit Prefab Id | `bool` | false |
| Scene Object Id | `ulong` | assigned by the Editor for scene objects |
| Despawn With Owner | `bool` | true; read when the owner leaves |
| Visibility | `NetworkVisibility` | `Rule`; read when observers are recalculated |

## NetworkTransform

| Field | Type | Default |
|---|---|---|
| Sync Position | `bool` | true |
| Sync Rotation | `bool` | true |
| Sync Scale | `bool` | false |
| Position Threshold | `float` | 0.01 |
| Rotation Threshold | `float` | 0.1 (degrees) |
| Scale Threshold | `float` | 0.01 |
| Interpolation Ticks | `int` | 2 |
| Visual | `Transform` | none |
| Smoothing Time | `float` | 0.1 |

## NetworkAnimator

| Field | Type | Default |
|---|---|---|
| Animator | `Animator` | the one on the same GameObject |
| Float Step | `float` | 0.01 |

## WebSocketNetworkTransport

| Field | Type | Default |
|---|---|---|
| Path | `string` | `/` |
| Max Handshake Bytes | `int` | 8192, at least 256 |
| Handshake Timeout Seconds | `float` | 5 |
| Allowed Origins | `string[]` | empty |
| Max Buffered Bytes | `int` | 1048576 |

## MultiNetworkTransport

| Field | Type | Default |
|---|---|---|
| Transports | list of entries: `NetworkTransport` Transport, `int` Port | empty |

## Observers

| Asset or component | Field | Type | Default |
|---|---|---|---|
| `DistanceRule` | Radius | `float` | 50 |
| `ObserverRange` | Radius | `float` | 50 |

## Contact components

| Component | Field | Type | Default |
|---|---|---|---|
| `NetworkCollision` | Additional Size | `float` | `Physics.defaultContactOffset` × 2 |
| `NetworkTrigger` | Additional Size | `float` | 0 |

## FomoxaSettings

| Field | Type | Default |
|---|---|---|
| Models Folder | `string` | `Assets/Models` |
| Generated Folder | `string` | `Assets/Generated` |

The members behind these fields are listed in the [NetworkManager reference](network-manager.md) and the [components reference](components.md). [Editor integration](../advanced/editor-integration.md) explains the `FomoxaSettings` asset.
