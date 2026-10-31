# Agones

[Agones](https://agones.dev) chạy server game trên Kubernetes thành các tài nguyên `GameServer`, gom trong một `Fleet` mà Agones tự co giãn. Một pod của Fomoxa chạy được thành một game server như vậy. Fomoxa không tự gọi Agones. Server của bạn gọi SDK của Agones bên cạnh `DirectoryPod`, và trang này chỉ ra lời gọi nào đặt ở đâu.

> **Kết quả:** các pod của bạn chạy trong một `Fleet` của Agones, đăng ký với directory, ở trạng thái `Allocated` khi đang giữ phòng, và rời fleet sau khi bị rút.

Cấu hình trên trang này chạy Agones 1.61.0 trên Kubernetes 1.36, với một console server dùng SDK C# `AgonesSDK` 1.61.0. Agones cũng có SDK cho Unity với cùng các lời gọi, dùng cho server build thành Unity player.

## Cần có trước <a href="#prerequisites" id="prerequisites"></a>

- Một cụm Kubernetes đã cài Agones. Xem [cài đặt Agones](https://agones.dev/site/docs/installation/).
- Directory và backend của game chạy trong cụm, và gateway nếu bạn dùng. Trang [cụm server](cluster.md) cho thấy chúng ghép với nhau thế nào.
- Một server game đăng ký qua `DirectoryPod`, như mục "Running as a pod" trong [README của `com.fomoxa.rpc`](https://github.com/fomoxa/com.fomoxa.rpc).

## Agones cần gì từ pod <a href="#what-agones-needs-from-a-pod" id="what-agones-needs-from-a-pod"></a>

| Agones cần | Pod làm khi nào |
|---|---|
| `Ready()` | Lúc khởi động, trước khi đăng ký với directory |
| `Health()` vài giây một lần | Suốt thời gian chạy |
| `Allocate()` | Khi bắt đầu giữ phòng đầu tiên |
| `Ready()` lần nữa | Khi trả phòng cuối cùng, trừ khi đang bị rút |
| `Shutdown()` | Sau khi rút, khi các người chơi đã chuyển đi hết |
| Địa chỉ và cổng của nó | Chỉ khi không có gateway: pod đăng ký chúng với directory |

Agones chỉ xoá các game server ở `Ready` khi co fleet lại. Pod đang giữ phòng ở `Allocated`, nên co fleet không bao giờ xoá pod đang có người chơi.

## 1. Thêm SDK <a href="#1-add-the-sdk" id="1-add-the-sdk"></a>

Trong project của server:

```
dotnet add package AgonesSDK --version 1.61.0
```

SDK nói chuyện với một sidecar mà Agones thêm vào mỗi pod game server, qua `localhost`. Ngoài Agones, khi chạy ở máy, bản phát hành của Agones có SDK server cục bộ (`sdk-server.linux.amd64 --local` trong `agonessdk-server-1.61.0.zip`) trả lời cùng các lời gọi.

## 2. Khởi động game server <a href="#2-start-the-game-server" id="2-start-the-game-server"></a>

Gọi `ReadyAsync` trước khi pod đăng ký với directory. Sidecar có thể khởi động chậm hơn pod một chút, nên hãy thử lại tới khi lời gọi thành công:

```csharp
using System;
using System.Linq;
using System.Threading.Tasks;
using Agones;
using Agones.Dev.Sdk;
using Grpc.Core;

var agones = new AgonesSDK();
await Retry(async () =>
{
    Status status = await agones.ReadyAsync();
    if (status.StatusCode != StatusCode.OK)
    {
        throw new InvalidOperationException(status.Detail);
    }
});

static async Task Retry(Func<Task> call)
{
    for (int attempt = 1; ; attempt++)
    {
        try
        {
            await call();
            return;
        }
        catch (Exception) when (attempt < 60)
        {
            await Task.Delay(500);
        }
    }
}
```

**Có gateway:** pod đăng ký bằng địa chỉ của chính nó trong cụm, như trang [cụm server](cluster.md), và bật Behind Gateway trên transport mã hoá.

**Không có gateway:** client kết nối tới địa chỉ và cổng mà Agones cấp cho game server. Đọc chúng ra và đăng ký với directory:

```csharp
GameServer server = await agones.GetGameServerAsync();
string address = server.Status.Address;
ushort advertisedPort = (ushort)server.Status.Ports.First(port => port.Port_ > 0).Port_;

var pod = new DirectoryPod(runtime, new DirectoryPodSettings
{
    DirectoryAddress = "fomoxa-directory",
    DirectoryPort = 9500,
    Key = podKey,
    Address = address,
    Port = advertisedPort,
    Target = podName,
    Version = "1.0.0",
    MaxPlayers = 64,
});
```

Server vẫn nghe trên cổng của container (7777 trong các manifest bên dưới). Agones chuyển cổng của node vào cổng đó, nên `Port` trong cấu hình là cổng công bố, còn `StartConnection` nhận cổng của container. Ở cách này, để Behind Gateway tắt.

**Kiểm tra:** `kubectl get gameservers` liệt kê các game server ở `Ready`.

## 3. Gửi health ping <a href="#3-send-health-pings" id="3-send-health-pings"></a>

Gọi `HealthAsync` hai giây một lần từ vòng lặp của server, ví dụ trong mỗi tick:

```csharp
if (lastHealth == null || now - lastHealth.Value >= TimeSpan.FromSeconds(2))
{
    lastHealth = now;
    _ = agones.HealthAsync();
}
```

`lastHealth` là field kiểu `TimeSpan?`, `now` là thời điểm của tick. Agones đánh dấu game server `Unhealthy` và thay nó khi không có ping nào tới trong chu kỳ health của fleet (mặc định 5 giây, lỡ 3 lần liên tiếp).

## 4. Đánh dấu phòng <a href="#4-mark-the-rooms" id="4-mark-the-rooms"></a>

Gọi `AllocateAsync` khi `AcquireRoom` thành công cho phòng đầu tiên của pod, và `ReadyAsync` khi pod trả phòng cuối cùng:

```csharp
await pod.AcquireRoom(roomKey);
if (pod.Rooms.Count == 1)
{
    await agones.AllocateAsync();
}
```

```csharp
await pod.ReleaseRoom(roomKey);
if (pod.Rooms.Count == 0 && !pod.IsDraining)
{
    await agones.ReadyAsync();
}
```

Agones dùng `Allocated` cho game server đã giao cho một trận. Ở đây nó nghĩa là pod đang giữ ít nhất một phòng.

## 5. Rút và tắt <a href="#5-drain-and-shut-down" id="5-drain-and-shut-down"></a>

Rút pod như trang [cụm server](cluster.md#draining-a-pod): khi có `OnDrain`, chuyển từng phòng bằng `Relocate` và chuyển người chơi của nó bằng `ServerManager.Transfer`. Khi các người chơi đã chuyển đi hết, gọi `ShutDownAsync`, và Agones xoá game server:

```csharp
if (roomsMoved && !shuttingDown && runtime.ServerManager.PeerCount == 0)
{
    shuttingDown = true;
    _ = agones.ShutDownAsync();
}
```

Hãy chờ `PeerCount` về 0. Pod tắt ngay sau `Transfer` có thể bị dừng trước khi lệnh chuyển tới được client.

Khi Kubernetes dừng pod, ví dụ lúc co fleet hoặc rút node, process nhận SIGTERM. Bắt tín hiệu đó và gọi `RequestDrain`, như README của `com.fomoxa.rpc`. Đặt `terminationGracePeriodSeconds` của pod dài hơn `drain_seconds` của directory, để việc rút xong trước khi Kubernetes giết process.

## 6. Fleet <a href="#6-the-fleet" id="6-the-fleet"></a>

Có gateway thì pod không cần cổng trên node, nên cổng game dùng `portPolicy: None`:

```yaml
apiVersion: agones.dev/v1
kind: Fleet
metadata:
  name: game-pod
spec:
  replicas: 2
  template:
    metadata:
      labels:
        app: game-pod
    spec:
      ports:
        - name: game
          portPolicy: None
          containerPort: 7777
          protocol: UDP
      health:
        initialDelaySeconds: 10
        periodSeconds: 5
        failureThreshold: 3
      template:
        metadata:
          labels:
            app: game-pod
        spec:
          terminationGracePeriodSeconds: 330
          containers:
            - name: game
              image: my-game-server:1.0.0
              env:
                - { name: POD_NAME, valueFrom: { fieldRef: { fieldPath: metadata.name } } }
                - { name: POD_IP, valueFrom: { fieldRef: { fieldPath: status.podIP } } }
```

Không có gateway thì dùng `portPolicy: Dynamic`. Agones khi đó chọn một cổng trên node cho mỗi game server và chuyển nó vào `containerPort`. Bỏ `public_address` và `public_websocket` khỏi cấu hình của directory, để vé mang địa chỉ mà mỗi pod đã đăng ký.

`POD_NAME` dùng tốt làm `Target` của pod, `POD_IP` làm địa chỉ của nó khi có gateway. Khoá của vai `pod` lấy từ một Secret, như các phần khác của cụm.

Để luôn có sẵn game server trống khi phòng lấp đầy các pod, gắn một `FleetAutoscaler` với chính sách buffer. Buffer của nó đếm các game server ở `Ready`, ở đây là các pod chưa có phòng:

```yaml
apiVersion: autoscaling.agones.dev/v1
kind: FleetAutoscaler
metadata:
  name: game-pod-autoscaler
spec:
  fleetName: game-pod
  policy:
    type: Buffer
    buffer:
      bufferSize: 2
      minReplicas: 2
      maxReplicas: 20
```

## Kiểm tra kết quả <a href="#verify-the-result" id="verify-the-result"></a>

1. `kubectl get gameservers` cho thấy mọi game server ở `Ready` sau khi fleet khởi động.
2. Sau khi một người chơi vào phòng, game server của pod giữ phòng chuyển sang `Allocated`.
3. Sau khi bạn rút pod đó, người chơi tới một pod khác, game server của nó sang `Shutdown` rồi biến mất, và fleet khởi động một game server mới.
4. `kubectl scale fleet game-pod --replicas=0` xoá các game server ở `Ready` và giữ lại các game server ở `Allocated`.

## Lỗi thường gặp <a href="#common-mistakes" id="common-mistakes"></a>

- **Không gửi health ping.** Game server chuyển sang `Unhealthy` vài giây sau khi khởi động, và Agones thay nó.
- **Tắt quá sớm.** Gọi `ShutDownAsync` ngay sau `Transfer` có thể cắt lệnh chuyển trước khi nó tới client.
- **Bật Behind Gateway mà không có gateway.** Pod bỏ mọi datagram, vì không datagram nào mang đầu bọc của gateway.
- **Client WebGL không có gateway.** Client trình duyệt kết nối bằng [WebSocket mã hóa](../connections/transports/encrypted-websocket.md), mà chỉ gateway phục vụ, nên chúng cần cách có gateway.

## Bước tiếp theo <a href="#next-steps" id="next-steps"></a>

- [Cụm server](cluster.md): các phần của cụm và cách một phòng được chuyển.
- [Backend của game](backend.md): dịch vụ trao vé cho người chơi.
- [Tài liệu của Agones](https://agones.dev/site/docs/): fleet, autoscale và các cách cài đặt.
