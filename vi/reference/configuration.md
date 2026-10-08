# Tham chiếu cấu hình

Trang này liệt kê các field Inspector của mọi component và asset. Trừ khi có ghi chú khác, một field được đọc khi component của nó khởi động.

## NetworkManager <a href="#networkmanager" id="networkmanager"></a>

Hướng dẫn [NetworkManager](../core/network-manager.md) giải thích tác dụng của từng field.

| Field | Type | Mặc định | Phạm vi |
|---|---|---|---|
| Transport | `NetworkTransport` | không có, khi đó một `UdpNetworkTransport` được thêm vào | |
| Tick Rate | `int` | 30 | 1 tới 65535 |
| Timing Mode | `TimingMode` | `Tick` | |
| Max Ticks Per Frame | `int` | 3 | tối thiểu 1 |
| Message Capacity | `int` | 1024 | tối thiểu 1 |
| Byte Capacity | `int` | 1048576 | tối thiểu 1 |
| Reliable Window | `int` | 1024 | 1 tới 16384 |
| Log Send Dropped | `bool` | true | |
| Log Receive Dropped | `bool` | true | |
| Max Reconnect Retries | `int` | -1 (không giới hạn) | |
| Reconnect Interval Seconds | `float` | 0.5 | |
| Handshake Timeout Seconds | `float` | 5 | |
| Heartbeat Interval Seconds | `float` | 5 | |
| Heartbeat Timeout Seconds | `float` | 15 | |
| Collect Prefabs | `bool` | true | |
| Collected Prefabs | `NetworkPrefabList` | không có | |
| Collected Scenes | `NetworkSceneList` | không có | |
| Prefabs | `List<NetworkObject>` | trống | |
| Observer Rule | `ObserverRule` | không có | |
| Observer Interval | `int` | 15 | tối thiểu 1 |
| Clock Ping Interval Seconds | `float` | 1 | lớn hơn 0 |
| Input Buffer | `int` | 2 | tối thiểu 0 |
| Max Tick Speed Adjust | `float` | 0.1 | từ 0 tới nhỏ hơn 1 |
| Clock Reset Ticks | `int` | 10 | tối thiểu 1 |
| Input Redundancy | `int` | 3 | tối thiểu 1 |
| Max Input Lead | `int` | 30 | tối thiểu 1 |
| Prediction History | `int` | 64 | tối thiểu 1 |
| Reconcile Interval | `int` | 1 | tối thiểu 1 |
| Physics | `NetworkPhysics` | không có; manager tự thêm một `RigidbodyPhysics` | |

Giá trị nằm ngoài phạm vi sẽ ném exception khi manager khởi động.

## RigidbodyPhysics <a href="#rigidbodyphysics" id="rigidbodyphysics"></a>

| Field | Type | Mặc định |
|---|---|---|
| Simulate Physics | `bool` | false |

## NetworkObject <a href="#networkobject" id="networkobject"></a>

| Field | Type | Mặc định |
|---|---|---|
| Prefab Id | `uint` | do Editor gán |
| Explicit Prefab Id | `bool` | false |
| Scene Object Id | `ulong` | do Editor gán cho scene object |
| Despawn With Owner | `bool` | true; đọc khi owner rời đi |
| Visibility | `NetworkVisibility` | `Rule`; đọc khi observer được tính lại |

## NetworkTransform <a href="#networktransform" id="networktransform"></a>

| Field | Type | Mặc định |
|---|---|---|
| Sync Position | `bool` | true |
| Sync Rotation | `bool` | true |
| Sync Scale | `bool` | false |
| Position Threshold | `float` | 0.01 |
| Rotation Threshold | `float` | 0.1 (độ) |
| Scale Threshold | `float` | 0.01 |
| Interpolation Ticks | `int` | 2 |
| Visual | `Transform` | không có |
| Smoothing Time | `float` | 0.1 |

## NetworkAnimator <a href="#networkanimator" id="networkanimator"></a>

| Field | Type | Mặc định |
|---|---|---|
| Animator | `Animator` | cái trên cùng GameObject |
| Float Step | `float` | 0.01 |

## WebSocketNetworkTransport <a href="#websocketnetworktransport" id="websocketnetworktransport"></a>

| Field | Type | Mặc định |
|---|---|---|
| Path | `string` | `/` |
| Max Handshake Bytes | `int` | 8192, tối thiểu 256 |
| Handshake Timeout Seconds | `float` | 5 |
| Allowed Origins | `string[]` | trống |
| Max Buffered Bytes | `int` | 1048576 |

## MultiNetworkTransport <a href="#multinetworktransport" id="multinetworktransport"></a>

| Field | Type | Mặc định |
|---|---|---|
| Transports | danh sách mục: `NetworkTransport` Transport, `int` Port | trống |

## Observer <a href="#observers" id="observers"></a>

| Asset hoặc component | Field | Type | Mặc định |
|---|---|---|---|
| `DistanceRule` | Radius | `float` | 50 |
| `ObserverRange` | Radius | `float` | 50 |

## Component contact <a href="#contact-components" id="contact-components"></a>

| Component | Field | Type | Mặc định |
|---|---|---|---|
| `NetworkCollision` | Additional Size | `float` | `Physics.defaultContactOffset` × 2 |
| `NetworkTrigger` | Additional Size | `float` | 0 |

## FomoxaSettings <a href="#fomoxasettings" id="fomoxasettings"></a>

| Field | Type | Mặc định |
|---|---|---|
| Models Folder | `string` | `Assets/Models` |
| Generated Folder | `string` | `Assets/Generated` |

Các member đứng sau những field này được liệt kê trong [tham chiếu NetworkManager](network-manager.md) và [tham chiếu component](components.md). [Tích hợp Editor](../unity/editor-integration.md) giải thích asset `FomoxaSettings`.
