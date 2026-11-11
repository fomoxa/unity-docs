# Debug

## Log message <a href="#log-messages" id="log-messages"></a>

Package log với hai tiền tố. Message từ các bước Editor, như sinh code, prefab id và scene id và kiểm tra khi build, bắt đầu bằng `[Fomoxa]`. Cảnh báo và lỗi lúc chạy, như message bị bỏ, RPC bị từ chối và object mismatch, bắt đầu bằng `Fomoxa`. [Lỗi và lý do dừng](../reference/errors.md) liệt kê các message và nguyên nhân của chúng.

## Event <a href="#events" id="events"></a>

Để log hoặc đếm các vấn đề theo định dạng của riêng bạn, hãy subscribe vào các event sau:

| Event | Trên | Phát khi |
|---|---|---|
| `OnClientConnectionState` | `ClientManager` | Kết nối của client đổi trạng thái |
| `OnServerConnectionState`, `OnRemoteConnectionState` | `ServerManager` | Server hoặc một kết nối client đổi trạng thái |
| `OnSendDropped` | cả hai | Một message trong queue không gửi được, ví dụ `TooLarge` |
| `OnReceiveDropped` | cả hai | Một bundle hoặc model nhận được không đọc được |
| `OnHandlerException` | cả hai | Một message handler ném exception; server đóng kết nối của peer đó, hoặc client dừng |
| `OnObjectMismatch` | `ClientManager` | Client không áp dụng được một object message và dừng |

Package log `OnSendDropped` và `OnReceiveDropped` theo mặc định, có thể tắt bằng Log Send Dropped và Log Receive Dropped trên `NetworkManager`. Nó chỉ log `OnHandlerException` và `OnObjectMismatch` khi không có ai subscribe chúng.

## Giá trị cần theo dõi <a href="#values-to-watch" id="values-to-watch"></a>

| Giá trị | Ý nghĩa |
|---|---|
| `ClientManager.Rtt` | Round-trip time từ client tới server |
| `ServerManager.RttOf(peerId)` | Round-trip time của một client, theo client đó báo |
| `ServerManager.DroppedInputsOf(peerId)` | Số input từ một client tới quá muộn hoặc quá sớm |
| `ServerManager.DroppedInputs` | Số input bị bỏ của mọi client kể từ khi server được tạo, kể cả client đã rời |
| `ServerManager.PeerCount` | Số client đã kết nối |
| `ClientManager.Statistics`, `ServerManager.Statistics` | [Bộ đếm lưu lượng](#traffic-counters), khi Collect Statistics đang bật |
| `TimeManager.ClockSynced` | Client đã có ước lượng đồng hồ và có thể dự đoán |
| `TimeManager.ServerTick`, `PredictionTick` | Góc nhìn của client về tick của server và tick của input |
| `NetworkBehaviour.IsPredicting` | Client của owner đang dự đoán behaviour này |
| `NetworkBehaviour.ReconcileCount` | Số lần sửa kể từ khi behaviour được tạo |
| `NetworkTransform.LastCorrection` | [Lần sửa](#prediction-corrections) gần nhất đã dời object bao xa |

## Số liệu trên màn hình <a href="#on-screen-statistics" id="on-screen-statistics"></a>

`NetworkStatsDisplay` vẽ những giá trị hữu ích nhất trong số này ở một góc của Game view. Thêm nó vào GameObject chứa `NetworkManager`, hoặc vào GameObject bất kỳ rồi gán manager vào field Manager của nó.

```text
Client Started, RTT 42 ms
Client sent 30 bundles/s, 2.1 KiB/s, 28 messages/s, 0 resent/s
Client received 30 bundles/s, 1.8 KiB/s, 29 messages/s, 0 duplicates/s
Reconciles 120, 2.0/s
Tick 1200, server 1200, prediction 1203, clock synced
```

Client hiện các dòng của client, server hiện các dòng của server, và host hiện cả hai. Các dòng của server là `Server Started, 3 peers`, lưu lượng của mọi peer cộng lại, và `Dropped inputs 4`.

| Field | Mặc định | Ý nghĩa |
|---|---|---|
| Manager | không có, khi đó là `NetworkManager` trên cùng GameObject | Manager được đọc |
| Show Connection | bật | Trạng thái, round-trip time và số peer |
| Show Traffic | tắt | Bundle, KiB, message và số lần lặp mỗi giây ở mỗi chiều; cần bật Collect Statistics trên manager |
| Show Time | bật | Tick, tick của server, tick dự đoán và đồng hồ đã đồng bộ hay chưa |
| Show Prediction | tắt | Trên client, `ReconcileCount` của mọi object đã spawn cộng lại, kèm tốc độ; trên server, `ServerManager.DroppedInputs` |
| Corner | `TopLeft` | `TopLeft`, `TopRight`, `BottomLeft` hoặc `BottomRight` |
| Average Seconds | 1 | Bao lâu đọc số một lần; tốc độ là mức thay đổi trong khoảng đó. Ít nhất 0.1. |
| Run In Release Builds | tắt | Khi tắt, component không làm gì trong bản build release. Editor và bản build Development luôn hiện. |

`resent/s` đếm message mà bên gửi gửi lại, còn `duplicates/s` đếm message mà bên nhận đã có, do gửi lại thừa hoặc gói bị lặp. Client của host không dự đoán, nên `Reconciles` của nó luôn là 0. Số được in theo invariant culture, và thời gian là thời gian thật, nên `Time.timeScale` không đổi tốc độ.

## Bộ đếm lưu lượng <a href="#traffic-counters" id="traffic-counters"></a>

Bật Collect Statistics trên `NetworkManager` để đếm những gì package gửi và nhận. Manager chỉ đọc field này một lần, lúc khởi động, và bộ đếm không tốn gì khi tắt. Server console đặt `NetworkSettings.CollectStatistics`.

`ClientManager.Statistics` là một `TrafficStatistics` và `ServerManager.Statistics` là một `ServerTrafficStatistics`, cả hai trong `Fomoxa.Networking.Sessions` và cả hai là `null` khi Collect Statistics tắt. Tổng của server gồm cả peer đã rời, `Of(peerId)` trả bộ đếm của một peer đang kết nối hoặc `null`, và không bộ đếm nào reset khi client kết nối lại hay server khởi động lại.

| Thành viên | Ý nghĩa |
|---|---|
| `Sent`, `Received` | Một `TrafficDirection` cho mỗi chiều |
| `TrafficDirection.Bundles` | Một `TrafficCount` của các bundle và số byte của chúng |
| `TrafficDirection.Total` | Một `MessageTraffic` của mọi message cộng lại |
| `TrafficDirection.Messages` | `IReadOnlyDictionary<uint, MessageTraffic>` theo message id; một dòng xuất hiện ở lần đầu id của nó được đếm |
| `TrafficCount` | `long Count` và `long Bytes` |

Mỗi `MessageTraffic` giữ năm giá trị `TrafficCount`:

| Thành viên | Chiều gửi | Chiều nhận |
|---|---|---|
| `New` | Message gửi lần đầu | Message nhận lần đầu, kể cả bản gửi lại khi bản gốc đã mất |
| `Repeated` | Message reliable được gửi lại | Message reliable đã nhận rồi, do gửi lại thừa hoặc gói bị lặp |
| `Ack` | Ack | Ack |
| `Fragment` | Các mảnh của message quá lớn cho một bundle, ở dòng của id mảnh | Các mảnh nhận được |
| `Split` | Message lớn đã gửi xong mảnh cuối, ở dòng của id gốc, với số byte của cả message | Message lớn đã ghép lại |

Bộ đếm đo bundle và message của package. Byte của một message gồm cả số thứ tự reliable và header object của nó. Frame của Fomoxa, heartbeat, handshake và mã hóa không được đếm, nên số byte trên mạng cao hơn một chút. `Split` lặp lại số byte mà `Fragment` đã đếm, nên hãy bỏ nó ra khi cộng byte.

`FomoxaRegistry.NameOf(messageId)` đổi một id thành tên mà bước sinh code ghi lại, ví dụ `Greeting.net`, hoặc `null` khi không có. Project sinh code trước phiên bản 0.3.4 có tên ở lần sinh code tiếp theo.

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

## Giả lập mạng xấu <a href="#simulating-a-bad-network" id="simulating-a-bad-network"></a>

[`SimulatedNetworkTransport`](../connections/transports/simulated.md) bọc transport thật và thêm độ trễ, jitter, mất gói, lặp gói và sai thứ tự trong Editor và bản build Development. Client của chính host không được giả lập.

## Lần sửa của prediction <a href="#prediction-corrections" id="prediction-corrections"></a>

`NetworkTransform` báo mỗi lần sửa của prediction dời object bao xa trên client của owner.

| Thành viên | Ý nghĩa |
|---|---|
| `event Action<TransformCorrection> OnCorrected` | Phát sau mỗi lần replay có object. Object chỉ được replay vì chung physics world với một object bị sửa cũng phát event này, thường với độ lệch gần 0. Exception trong handler được log. |
| `TransformCorrection? LastCorrection` | Lần sửa gần nhất; `null` cho tới lần đầu |
| Draw Corrections, `DrawCorrections` | Vẽ mỗi lần sửa trong Scene view, và trong Game view khi Gizmos đang bật: chấm đỏ ở chỗ object đã ở, chấm xanh lá ở chỗ object sau replay và một đoạn vàng nối hai chấm. Chỉ trong Editor, mặc định tắt. |
| Correction Seconds, `CorrectionSeconds` | Một lần sửa được vẽ giữ bao lâu, mặc định 2, ít nhất 0.1. Vẽ tối đa 64 lần sửa cùng lúc. |

| Thành viên của `TransformCorrection` | Ý nghĩa |
|---|---|
| `Tick` | Tick của state server bị sửa |
| `PositionBefore`, `RotationBefore` | Pose thế giới đang hiện ngay trước lần sửa |
| `PositionAfter`, `RotationAfter` | Pose thế giới ngay sau replay |
| `PositionOffset` | `PositionAfter - PositionBefore` |
| `RotationDegrees` | Góc giữa hai rotation |

Pose là của Visual khi field đó có giá trị, nếu không thì là transform của chính object. Khi có Visual, pose trước lần sửa gồm cả phần làm mượt còn lại của lần sửa trước, tức đúng cú nhảy người chơi thấy.

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

## Test với nhiều tiến trình <a href="#testing-with-several-processes" id="testing-with-several-processes"></a>

Cách đơn giản nhất là chạy một bản build server và dùng Editor làm client kết nối tới nó, hoặc ngược lại. Host mode cho phép test server và client trong cùng tiến trình, nhưng cần nhớ host dùng chung instance và không dự đoán. Một scene cũng có thể có nhiều component `NetworkManager`, ví dụ một server và một client kết nối qua transport của chúng, và khi đó chỉ một trong số chúng step mỗi physics world.

## Kiểm tra dữ liệu trên wire <a href="#inspecting-the-wire" id="inspecting-the-wire"></a>

Mỗi lần sinh code ghi `.fomoxa/schema.json` và `.fomoxa/schema.inspect.json` vào project. File thứ hai mô tả mọi message, kể cả các codec cho type Unity của package, cho các công cụ inspect của Fomoxa, vốn không thuộc package.

[Xử lý sự cố](../getting-started/troubleshooting.md) đi từ triệu chứng tới nguyên nhân, [event và callback](../reference/callbacks.md) liệt kê mọi event, và [hiệu năng](performance.md) nói về các thiết lập thay đổi những gì package gửi đi.
