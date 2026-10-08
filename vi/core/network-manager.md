# NetworkManager

`NetworkManager` là component chạy networking cho một scene. Nó giữ cấu hình, chạy vòng lặp tick bên trong player loop của Unity, và sở hữu một `ServerManager`, một `ClientManager`, một `TimeManager` và một `TransportManager`.

Package không cung cấp cách truy cập manager dạng static, nên hãy giữ một tham chiếu tới nó, ví dụ trong một serialized field, và truy cập server và client qua tham chiếu đó.

## Cách dùng cơ bản <a href="#basic-usage" id="basic-usage"></a>

1. Tạo một GameObject trống, ví dụ `Network Manager`.
2. Thêm một component transport, như `UdpNetworkTransport`.
3. Thêm `NetworkManager` và gán transport vào field Transport của nó.
4. Gán `FomoxaPrefabList.asset` đã sinh vào Collected Prefabs và `FomoxaSceneList.asset` vào Collected Scenes.

Sau đó khởi động nó từ code:

```csharp
manager.ServerManager.StartConnection(7777);
manager.ClientManager.StartConnection("127.0.0.1", 7777);
```

Gọi cả hai method trên cùng một manager sẽ biến nó thành host.

## Các manager con <a href="#sub-managers" id="sub-managers"></a>

| Property | Type | Mục đích |
|---|---|---|
| `ServerManager` | [`ServerManager`](server.md) | Khởi động và dừng server, spawn object, observer, network scene |
| `ClientManager` | [`ClientManager`](client.md) | Kết nối tới server, kết nối lại, các object đã spawn trên client |
| `TimeManager` | [`TimeManager`](../reference/time-manager.md) | Tick rate, số tick, tick event |
| `TransportManager` | `TransportManager` | Component transport và factory tạo từ nó |
| `Prefabs` | `PrefabRegistry` | Các prefab manager có thể spawn; xem [spawn](spawning.md) |
| `Scenes` | `SceneRegistry` | Các network scene manager có thể load; xem [network scene](scenes.md) |
| `Registry` | `FomoxaRegistry` | Schema, codec, channel và RPC id. Mặc định là `FomoxaRegistry.Default`, do code sinh ra điền vào |

Các manager con được tạo trong `Awake`, nên hãy dùng chúng từ `Start` trở đi.

## Field <a href="#fields" id="fields"></a>

Bạn đặt các field này trong Inspector. Manager đọc chúng một lần, trong `Awake`, nên thay đổi chúng trong Play Mode không có tác dụng.

### Transport và thời gian <a href="#transport-and-timing" id="transport-and-timing"></a>

| Field | Mặc định | Ý nghĩa |
|---|---|---|
| Transport | không có | Component transport. Nếu không có, manager thêm một `UdpNetworkTransport` vào GameObject của nó. |
| Tick Rate | 30 | Số tick mỗi giây. Client theo tick rate của server khi đang kết nối. |
| Timing Mode | Tick | `Tick` nhận và gửi theo tick và cho phép prediction. `Variable` nhận ở đầu và gửi ở cuối mỗi frame. Xem [tick và thời gian](../concepts/tick.md). |
| Max Ticks Per Frame | 3 | Số tick tối đa một frame được chạy. Tick vượt quá bị bỏ. |

### Send queue <a href="#send-queue" id="send-queue"></a>

| Field | Mặc định | Ý nghĩa |
|---|---|---|
| Message Capacity | 1024 | Số message queue của một kết nối giữ được trước khi lệnh gửi trả về `Full` |
| Byte Capacity | 1048576 | Số byte queue của một kết nối giữ được trước khi lệnh gửi trả về `BytesFull` |
| Reliable Window | 1024 | Số message reliable đang bay chưa được acknowledge, theo từng kết nối |
| Log Send Dropped | bật | Log cảnh báo khi một message trong queue không gửi được |
| Log Receive Dropped | bật | Log cảnh báo khi một bundle nhận được không đọc được |

### Kết nối <a href="#connection" id="connection"></a>

| Field | Mặc định | Ý nghĩa |
|---|---|---|
| Max Reconnect Retries | -1 | Số lần client thử lại sau khi mất hoặc không tạo được kết nối. -1 là thử mãi. |
| Reconnect Interval Seconds | 0.5 | Thời gian chờ trước mỗi lần thử lại |
| Handshake Timeout Seconds | 5 | Thời gian handshake được phép kéo dài trước khi kết nối thất bại |
| Heartbeat Interval Seconds | 5 | Khoảng im lặng mà sau đó kết nối gửi một probe |
| Heartbeat Timeout Seconds | 15 | Thời gian một probe được phép không có trả lời trước khi kết nối dừng với `Timeout` |

### Prefab và scene <a href="#prefabs-and-scenes" id="prefabs-and-scenes"></a>

| Field | Mặc định | Ý nghĩa |
|---|---|---|
| Collect Prefabs | bật | Đăng ký các prefab của Collected Prefabs. Bản build chỉ gán danh sách khi field này bật. |
| Collected Prefabs | không có | `FomoxaPrefabList.asset` đã sinh |
| Collected Scenes | không có | `FomoxaSceneList.asset` đã sinh |
| Prefabs | trống | Các prefab đăng ký thêm |

### Observer <a href="#observers" id="observers"></a>

| Field | Mặc định | Ý nghĩa |
|---|---|---|
| Observer Rule | không có | Một asset [`ObserverRule`](observers.md). Nếu không có, mọi client observe mọi object. |
| Observer Interval | 15 | Số tick mà server trải một lần tính lại toàn bộ các tập observer |

### Prediction <a href="#prediction" id="prediction"></a>

| Field | Mặc định | Ý nghĩa |
|---|---|---|
| Clock Ping Interval Seconds | 1 | Khoảng cách giữa các clock ping của client ở xa |
| Input Buffer | 2 | Số tick biên mà client giữ giữa lúc input tới server và lúc server dùng nó |
| Max Tick Speed Adjust | 0.1 | Mức thay đổi lớn nhất của tốc độ tick trên client khi đuổi theo, dưới dạng tỉ lệ |
| Clock Reset Ticks | 10 | Sai số đồng hồ, tính theo tick, mà từ đó client nhảy thẳng thay vì điều chỉnh tốc độ |
| Input Redundancy | 3 | Số input trong mỗi input message: input hiện tại và các input trước, để bù gói bị mất |
| Max Input Lead | 30 | Số tick tối đa input được đi trước server; input xa hơn bị bỏ |
| Prediction History | 64 | Số tick input, state dự đoán và physics mà client giữ để replay |
| Reconcile Interval | 1 | Server gửi state cho owner sau mỗi chừng này tick |

### Physics <a href="#physics" id="physics"></a>

| Field | Mặc định | Ý nghĩa |
|---|---|---|
| Physics | không có | Component physics, `RigidbodyPhysics`. Khi trống, manager tự thêm một `RigidbodyPhysics` với Simulate Physics tắt. Server và client phải dùng cùng một physics backend. Xem [physics](../physics/overview.md#turning-it-on). |

`RigidbodyPhysics` có một field, Simulate Physics (mặc định tắt). Khi bật, manager step physics của Unity mỗi tick một lần và bật rollback physics.

## Nhiều manager <a href="#several-managers" id="several-managers"></a>

Một scene có thể có nhiều hơn một `NetworkManager`, ví dụ một server và một client trong cùng tiến trình để test, và mỗi manager có server, client và tick riêng. Hai manager kết nối với nhau qua transport của chúng. Kết nối trong tiến trình của host không áp dụng ở đây, vì nó chỉ nối một client với server của cùng manager.

Mỗi physics scene chỉ do một manager step; xem [physics](../physics/overview.md#one-world-one-owner).

## Giới hạn <a href="#limitations" id="limitations"></a>

Không thể đặt các field từ code; `Registry` là property duy nhất có thể gán. Do đó manager thêm bằng `AddComponent` dùng giá trị mặc định, và nó tự thêm `UdpNetworkTransport` và `RigidbodyPhysics` trừ khi các component đó được gán qua Inspector. Manager chỉ chạy tick khi đang bật và nằm trong một scene đã load.

[Tham chiếu NetworkManager](../reference/network-manager.md) và [cấu hình](../reference/configuration.md) liệt kê mọi member và field. Các trang [server](server.md), [client](client.md) và [host mode](host-mode.md) mô tả những gì manager chạy.
