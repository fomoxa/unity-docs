# Dedicated server

Dedicated server là bản build game chỉ chạy server, không có người chơi và thường không có đồ họa. Nó được build từ cùng project Unity và cùng các scene với client, chỉ được khởi động theo cách khiến code của bạn gọi `ServerManager.StartConnection` thay vì `ClientManager.StartConnection`.

## Khởi động server từ dòng lệnh <a href="#starting-the-server-from-the-command-line" id="starting-the-server-from-the-command-line"></a>

Package không đọc tham số dòng lệnh, nên code của bạn quyết định một bản build trở thành server như thế nào:

```csharp
using System;
using Fomoxa.Networking;
using Fomoxa.Unity;
using UnityEngine;

public sealed class ServerBootstrap : MonoBehaviour
{
    [SerializeField] private NetworkManager manager;
    [SerializeField] private ushort defaultPort = 7777;
    [SerializeField] private int serverFrameRate = 60;

    private void Start()
    {
        string[] arguments = Environment.GetCommandLineArgs();
        if (Array.IndexOf(arguments, "-server") < 0)
        {
            return;
        }

        Application.targetFrameRate = serverFrameRate;
        manager.ServerManager.StartConnection(ReadPort(arguments));
        Debug.Log($"server listening on port {manager.ServerManager.Port}");
    }

    private ushort ReadPort(string[] arguments)
    {
        int index = Array.IndexOf(arguments, "-port");
        return index >= 0 && index + 1 < arguments.Length && ushort.TryParse(arguments[index + 1], out ushort port)
            ? port
            : defaultPort;
    }
}
```

Build player và chạy nó không có đồ họa:

```
MyGame.exe -batchmode -nographics -server -port 7777 -logFile server.log
```

`-batchmode` và `-nographics` là tùy chọn của Unity để chạy không có cửa sổ và không có thiết bị đồ họa, còn `-logFile` ghi log Unity, kể cả cảnh báo của package, ra một file.

## Frame rate và tick <a href="#frame-rate-and-ticks" id="frame-rate-and-ticks"></a>

Tick chạy bên trong các frame của Unity. Mỗi frame chạy mọi tick đã tới hạn, tối đa Max Ticks Per Frame (mặc định 3), và bỏ phần còn lại. Hãy giữ frame rate của server ít nhất bằng tick rate để mỗi tick chạy trong frame riêng, và giới hạn nó bằng `Application.targetFrameRate` để server không dùng nhiều CPU hơn mức cần.

## Hành vi khi chạy headless <a href="#headless-behavior" id="headless-behavior"></a>

Server cần cùng các prefab, scene và code sinh ra như client, vì spawn được kiểm tra theo prefab id và fingerprint, và handshake so sánh schema. Hãy build server và client từ cùng một trạng thái project.

Renderer, âm thanh và UI không có tác dụng gì trên dedicated server, nhưng package không tắt chúng. Hãy để nguyên, hoặc loại bỏ chúng trong quy trình build của riêng bạn.

## Dừng <a href="#stopping" id="stopping"></a>

Khi ứng dụng thoát bình thường, `NetworkManager` dừng các kết nối của nó, còn tiến trình bị kill thì không có cơ hội làm vậy. Trong cả hai trường hợp, client thấy kết nối dừng, với `PeerClosed` nếu thông báo đóng của server tới được chúng hoặc với `Timeout` sau heartbeat timeout, rồi thử kết nối lại theo thiết lập của chúng.

Trang [server](../core/server.md) nói về bản thân `ServerManager`, và [triển khai](deployment.md) nói về những gì máy chủ và mạng của nó cần. [Server đầu tiên](../getting-started/first-server.md) build một dedicated server trong phần hướng dẫn.
