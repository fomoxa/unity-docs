# Tick và thời gian

Package cho network tiến lên theo các bước cố định gọi là tick. Trong một tick, server áp dụng input, step physics, chụp state và transform, và message được gửi vào cuối tick. Tick thuộc về `TimeManager`, truy cập qua `NetworkManager.TimeManager`.

## Tick rate <a href="#tick-rate" id="tick-rate"></a>

Field Tick Rate của `NetworkManager` đặt số tick mỗi giây, mặc định 30, và `TimeManager.TickDelta` cho độ dài một tick tính bằng giây, `1.0 / TickRate`.

Server quyết định tick rate. Khi client kết nối, server báo tick rate cho nó, và `TimeManager.TickRate` của client theo giá trị đó cho tới khi kết nối dừng. Field Tick Rate của chính client chỉ có tác dụng khi nó chưa kết nối.

## Tick chạy ở đâu <a href="#where-ticks-run" id="where-ticks-run"></a>

`NetworkManager` đang bật có hai entry trong player loop của Unity, một ở đầu `EarlyUpdate` và một ở cuối `PostLateUpdate`. Nó thêm hai entry này khi được bật và gỡ chúng khi bị tắt.

Đầu mỗi frame, manager cộng thời gian không scale của frame (`Time.unscaledDeltaTime`) vào một bộ tích lũy và chạy mọi tick đã tới hạn, tối đa Max Ticks Per Frame (mặc định 3). Tick vượt giới hạn này bị bỏ chứ không dồn sang frame sau, nên một frame dài không gây ra một loạt tick đuổi theo sau đó. Vì bộ tích lũy dùng thời gian không scale, `Time.timeScale` không làm network chậm lại.

Trên client kết nối tới server ở xa, manager còn chạy tick nhanh hơn hoặc chậm hơn một chút để giữ prediction tick ở khoảng cách đúng phía trước server, như mô tả ở mục [đồng bộ đồng hồ](#clock-synchronization).

## Thứ tự một tick <a href="#order-of-one-tick" id="order-of-one-tick"></a>

Ở timing mode Tick, một tick chạy các bước sau theo thứ tự:

1. `TimeManager.Tick` tăng thêm một và `OnPreTick` được gọi.
2. Chỉ ở tick đầu tiên của frame, cả hai manager đọc các message đã tới, và client cập nhật ước lượng đồng hồ.
3. Khi bật Simulate Physics, client ở xa đặt các body networked mà nó không dự đoán vào vị trí transform của chúng.
4. Client chạy reconcile, rồi thu thập input cho các object nó dự đoán, áp dụng và gửi đi. Khi không bật Simulate Physics, nó cũng ghi lại state dự đoán ở bước này.
5. Server áp dụng input của tick này cho mọi object có input model.
6. Khi bật Simulate Physics, manager step physics một lần và truy vấn contact.
7. Khi bật Simulate Physics, client ghi lại state dự đoán và lưu physics cho tick này. Server gửi reconcile state tới các owner.
8. Khi bật Simulate Physics, các contact event được gọi.
9. `OnTick` được gọi, rồi tới `OnPostTick`.
10. Server dựng lại một phần các tập observer, chụp state và transform, và đưa phần thay đổi vào queue.
11. Cả hai manager flush send queue.

Ở timing mode Variable, bước 2 chạy một lần ở đầu mỗi frame trước các tick, và bước 11 chạy một lần ở cuối frame thay vì sau mỗi tick. Input và prediction không dùng được ở mode này.

## Timing mode <a href="#timing-modes" id="timing-modes"></a>

| Mode | Nhận | Gửi | Prediction |
|---|---|---|---|
| `Tick` (mặc định) | Ở tick đầu tiên của frame | Sau mỗi tick | Có |
| `Variable` | Ở đầu mỗi frame | Ở cuối mỗi frame | Không; đăng ký input model sẽ ném exception |

Ở cả hai mode, state, transform và observer đều được xử lý theo tick.

## Tick event <a href="#tick-events" id="tick-events"></a>

```csharp
using Fomoxa.Unity;
using Fomoxa.Unity.Sessions;
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

Ví dụ subscribe trong `Start` vì `NetworkManager` tạo `TimeManager` trong `Awake`, và Unity chạy mọi `Awake` của một scene trước mọi `Start`.

`OnPreTick`, `OnTick` và `OnPostTick` được gọi ở cả hai bên cho mỗi tick. State và transform được chụp sau chúng, ở bước 10, nên logic game trên server cần thay đổi state trước khi gửi phải đặt trong `OnTick` hoặc `OnPostTick`.

## Ba số tick <a href="#three-tick-numbers" id="three-tick-numbers"></a>

| Property | Trên manager chạy server, kể cả host | Trên client kết nối tới server ở xa |
|---|---|---|
| `TimeManager.Tick` | Bộ đếm tick cục bộ | Bộ đếm tick cục bộ |
| `TimeManager.ServerTick` | Bằng `Tick` | Ước lượng của client về tick hiện tại của server |
| `TimeManager.PredictionTick` | Bằng `Tick` | Tick mà input của client dành cho, đi trước server |

Trên manager không chạy server cũng không có client đang kết nối, `ServerTick` và `PredictionTick` bằng 0 và `ClockSynced` là false.

Client gửi input cho `PredictionTick`. Tick đó đi trước server khoảng nửa round trip cộng một khoảng đệm nhỏ, nên input tới server trước khi server cần đến nó.

```text
server            ... 98   99   100  101  102  103 ...
                              ↑ ServerTick (estimated)
client input                             ↑ PredictionTick
                              ←── RTT/2 + Input Buffer ──→
```

## Đồng bộ đồng hồ <a href="#clock-synchronization" id="clock-synchronization"></a>

Client ở xa gửi ping ba lần ngay sau khi kết nối, rồi cứ mỗi Clock Ping Interval Seconds (mặc định 1) một lần. Server trả lời bằng tick của nó và cho biết input của client đã tới sớm bao nhiêu, và từ các câu trả lời này client ước lượng round-trip time (`ClientManager.Rtt`) và tick của server.

Client nhắm tới khoảng đi trước bằng nửa round trip, tính theo tick, cộng Input Buffer tick (mặc định 2). Khi server báo khoảng đi trước thực tế của input, client điều chỉnh để giữ biên Input Buffer tick ở phía server. Nó thu hẹp khoảng lệch bằng cách chạy tick nhanh hơn hoặc chậm hơn tối đa Max Tick Speed Adjust (0.1, tức 10 %), và khi sai số vượt Clock Reset Ticks (10) thì nó nhảy thẳng tới mục tiêu.

`TimeManager.ClockSynced` là false cho tới khi câu trả lời đầu tiên tới, và client không dự đoán trước thời điểm đó. [Tổng quan prediction](../prediction/overview.md) cho thấy prediction dùng các tick này ra sao, [vòng đời](lifecycle.md) đưa ra thứ tự sự kiện của kết nối và network object, và [tham chiếu TimeManager](../reference/time-manager.md) liệt kê các member của nó.
