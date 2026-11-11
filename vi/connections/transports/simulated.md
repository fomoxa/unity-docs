# Giả lập mạng

`SimulatedNetworkTransport` bọc một transport khác và thêm độ trễ, jitter, mất gói, lặp gói và sai thứ tự vào những gì nó gửi và nhận. Nhờ vậy bạn chơi được trên một mạng xấu ngay trong Editor và thấy đúng thứ người chơi sẽ thấy.

## Cách dùng cơ bản <a href="#basic-usage" id="basic-usage"></a>

1. Giữ transport thật trên một GameObject, ví dụ `UdpNetworkTransport`.
2. Thêm `SimulatedNetworkTransport` và gán transport thật vào field Transport của nó.
3. Gán `SimulatedNetworkTransport` vào field Transport của `NetworkManager`.
4. Đặt các field bên dưới.

Mỗi tiến trình giả lập chiều gửi và chiều nhận của chính nó với cùng các giá trị. Vì vậy một client có Latency 50 ms nối với một server không giả lập sẽ thấy round-trip time tăng khoảng 100 ms, 50 ms mỗi chiều.

## Field <a href="#fields" id="fields"></a>

| Field | Mặc định | Ý nghĩa |
|---|---|---|
| Transport | không có | Transport được giả lập |
| Latency Milliseconds | 0 | Độ trễ của mỗi gói, ở mỗi chiều |
| Jitter Milliseconds | 0 | Độ trễ của mỗi gói là Latency cộng một lượng ngẫu nhiên trong khoảng từ trừ tới cộng Jitter, và không nhỏ hơn 0 |
| Packet Loss | 0 | Phần trăm gói bị bỏ |
| Duplicate | 0 | Phần trăm gói tới hai lần; bản sao có độ trễ riêng |
| Reorder | 0 | Phần trăm gói bị giữ lại tới khi gói kế tiếp cùng chiều đã đi, hoặc tới khi đã chờ gấp đôi độ trễ của nó |
| Max Held Packets | 1024 | Số gói được giữ ở mỗi chiều; khi đầy, gói cũ nhất bị bỏ |

Khi mọi field bằng 0, gói đi thẳng qua. Thay đổi trong Inspector lúc đang chơi có tác dụng từ gói tiếp theo.

Gói bị giữ được nhả ở lần tiếp theo package gửi hoặc nhận, việc package làm mỗi tick, nên độ trễ được làm tròn lên theo tick. Độ trễ của một gói nhận được tính từ lúc package đọc nó từ transport thật.

## Gói và byte stream <a href="#packets-and-byte-streams" id="packets-and-byte-streams"></a>

Mất gói, lặp gói và sai thứ tự chỉ áp cho transport giữ ranh giới gói: UDP, UDP mã hóa, WebSocket và WebSocket mã hóa. TCP, có hay không có TLS, chỉ nhận độ trễ và jitter, và byte vẫn tới đúng thứ tự. Khi đã có Max Held Packets lần gửi đang chờ trên một byte stream, transport từ chối nhận thêm dữ liệu và package gửi phần đó sau.

## Những gì không được giả lập <a href="#what-is-not-simulated" id="what-is-not-simulated"></a>

Client của chính host kết nối qua [loopback](loopback.md) trong tiến trình, không bao giờ đi qua transport, nên nó không được giả lập. Để thử một client trên mạng xấu, hãy chạy client ở một tiến trình thứ hai, hoặc cho một `NetworkManager` thứ hai một client riêng.

Với [`MultiNetworkTransport`](multi-transport.md), gán nó vào field Transport của `SimulatedNetworkTransport` để giả lập mọi mục, hoặc đặt một `SimulatedNetworkTransport` vào một mục để chỉ giả lập transport đó. Mỗi kết nối giữ frame budget của transport mà nó đi vào.

## Bản build release <a href="#release-builds" id="release-builds"></a>

Việc giả lập chỉ chạy trong Editor và bản build Development. Trong bản build release, `SimulatedNetworkTransport` dùng thẳng transport thật và ghi cảnh báo này khi `NetworkManager` tạo transport:

```text
Simulated: network simulation runs only in the Editor and in Development builds; UdpNetworkTransport is used directly
```

Từ đầu tiên là tên của GameObject, và type cuối cùng là transport được bọc.

## Trên server console <a href="#on-a-console-server" id="on-a-console-server"></a>

Một [server console](../../console-server/overview.md) truyền một `SimulatedTransportFactory` trong `Fomoxa.Networking.Transports` làm transport. Factory này giả lập ở mọi bản build.

```csharp
var conditions = new NetworkConditions
{
    Latency = TimeSpan.FromMilliseconds(50),
    Jitter = TimeSpan.FromMilliseconds(10),
    PacketLoss = 2,
};
var transport = new SimulatedTransportFactory(new UdpTransportFactory(), conditions, () => clock.Elapsed, seed: 1);
```

| Thành viên | Ý nghĩa |
|---|---|
| `NetworkConditions` | `Latency`, `Jitter` (`TimeSpan`), `PacketLoss`, `Duplicate`, `Reorder` (phần trăm, `double`) và `MaxHeldPackets`, với mặc định như các field ở trên. Thời gian âm, phần trăm ngoài khoảng 0 tới 100 hoặc ít hơn 1 gói giữ thì ném `ArgumentOutOfRangeException`. Thay đổi có tác dụng từ gói tiếp theo. |
| `SimulatedTransportFactory(ITransportFactory inner, NetworkConditions conditions, Func<TimeSpan> clock, int? seed = null)` | Bọc `inner`. Truyền cùng đồng hồ với runtime. Có seed thì cùng các kết nối theo cùng thứ tự sẽ mất cùng các gói. |

[Tổng quan transport](README.md) liệt kê các transport bạn bọc được, và [debug](../../advanced/debugging.md) nói về các con số cần theo dõi khi thử.
