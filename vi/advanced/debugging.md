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
| `OnHandlerException` | cả hai | Một message handler ném exception; peer bị ngắt kết nối hoặc client dừng |
| `OnObjectMismatch` | `ClientManager` | Client không áp dụng được một object message và dừng |

Package log `OnSendDropped` và `OnReceiveDropped` theo mặc định, có thể tắt bằng Log Send Dropped và Log Receive Dropped trên `NetworkManager`. Nó chỉ log `OnHandlerException` và `OnObjectMismatch` khi không có ai subscribe chúng.

## Giá trị cần theo dõi <a href="#values-to-watch" id="values-to-watch"></a>

| Giá trị | Ý nghĩa |
|---|---|
| `ClientManager.Rtt` | Round-trip time từ client tới server |
| `ServerManager.RttOf(peerId)` | Round-trip time của một client, theo client đó báo |
| `ServerManager.DroppedInputsOf(peerId)` | Số input từ một client tới quá muộn hoặc quá sớm |
| `ServerManager.PeerCount` | Số client đã kết nối |
| `TimeManager.ClockSynced` | Client đã có ước lượng đồng hồ và có thể dự đoán |
| `TimeManager.ServerTick`, `PredictionTick` | Góc nhìn của client về tick của server và tick của input |
| `NetworkBehaviour.IsPredicting` | Client của owner đang dự đoán behaviour này |
| `NetworkBehaviour.ReconcileCount` | Số lần sửa kể từ khi behaviour được tạo |

Một overlay nhỏ trên màn hình có thể hiển thị những giá trị hữu ích nhất trong số này:

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

## Test với nhiều tiến trình <a href="#testing-with-several-processes" id="testing-with-several-processes"></a>

Cách đơn giản nhất là chạy một bản build server và dùng Editor làm client kết nối tới nó, hoặc ngược lại. Host mode cho phép test server và client trong cùng tiến trình, nhưng cần nhớ host dùng chung instance và không dự đoán. Một scene cũng có thể có nhiều component `NetworkManager`, ví dụ một server và một client kết nối qua transport của chúng, và khi đó chỉ một trong số chúng step mỗi physics world.

## Kiểm tra dữ liệu trên wire <a href="#inspecting-the-wire" id="inspecting-the-wire"></a>

Mỗi lần sinh code ghi `.fomoxa/schema.json` và `.fomoxa/schema.inspect.json` vào project. File thứ hai mô tả mọi message, kể cả các codec cho type Unity của package, cho các công cụ inspect của Fomoxa, vốn không thuộc package.

[Xử lý sự cố](../getting-started/troubleshooting.md) đi từ triệu chứng tới nguyên nhân, [event và callback](../reference/callbacks.md) liệt kê mọi event, và [hiệu năng](performance.md) nói về các thiết lập thay đổi những gì package gửi đi.
