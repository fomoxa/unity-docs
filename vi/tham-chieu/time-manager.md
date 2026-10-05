# TimeManager

`public sealed class TimeManager` trong `Fomoxa.Unity` không có constructor public; bạn truy cập nó qua `NetworkManager.TimeManager`. [Tick và thời gian](../khai-niem/tick.md) giải thích các khái niệm đằng sau nó.

## Property <a href="#properties" id="properties"></a>

| Property           | Type         | Mô tả                                                                                                                                                                                      |
| ------------------ | ------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `TickRate`         | `int`        | Số tick mỗi giây. Giá trị đã cấu hình, hoặc giá trị của server khi một client ở xa đang kết nối.                                                                                           |
| `TickDelta`        | `double`     | Số giây mỗi tick, `1.0 / TickRate`                                                                                                                                                         |
| `MaxTicksPerFrame` | `int`        | Số tick tối đa một frame được chạy                                                                                                                                                         |
| `Mode`             | `TimingMode` | `Tick` hoặc `Variable`                                                                                                                                                                     |
| `Tick`             | `uint`       | Bộ đếm tick cục bộ, tăng ở đầu mỗi tick                                                                                                                                                    |
| `ServerTick`       | `uint`       | Trên manager chạy server, bằng `Tick`. Ngoài ra là ước lượng của client về tick của server, bằng 0 cho tới câu trả lời clock đầu tiên.                                                     |
| `PredictionTick`   | `uint`       | Trên manager chạy server, bằng `Tick`. Ngoài ra, ở mode Tick là tick mà input của client dành cho, và ở mode Variable là tick server ước lượng; bằng 0 cho tới câu trả lời clock đầu tiên. |
| `ClockSynced`      | `bool`       | True trên manager chạy server. Ngoài ra là true khi client đã nhận câu trả lời clock từ server của nó.                                                                                     |

## Event <a href="#events" id="events"></a>

| Event        | Được gọi                                     |
| ------------ | -------------------------------------------- |
| `OnPreTick`  | Ở đầu một tick, sau khi `Tick` tăng          |
| `OnTick`     | Sau input, physics và contact event của tick |
| `OnPostTick` | Ngay sau `OnTick`                            |

Cả ba đều là event `Action` và được gọi trên main thread bên trong `EarlyUpdate` của player loop.

## TimingMode <a href="#timingmode" id="timingmode"></a>

| Giá trị    | Ý nghĩa                                                         |
| ---------- | --------------------------------------------------------------- |
| `Tick`     | Nhận ở tick đầu tiên của frame, gửi sau mỗi tick; có prediction |
| `Variable` | Nhận ở đầu frame, gửi ở cuối frame; không có prediction         |

Các type liên quan là [NetworkManager](network-manager.md) và [ClientManager](client-manager.md).
