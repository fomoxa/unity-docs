# Steam

`SteamNetworkTransport` nối người chơi với nhau qua Steam. Client tìm host bằng SteamID thay vì địa chỉ IP, và Steam chở dữ liệu. Khi hai máy không nối thẳng được với nhau, dữ liệu đi qua mạng relay của Valve. Nhờ vậy người chơi host được một trận từ mạng ở nhà, sau NAT, mà không cần mở cổng.

Transport này nằm trong một package riêng, `com.fomoxa.networking.steam`, và gọi Steam qua [Steamworks.NET](https://github.com/rlabrecque/Steamworks.NET). Package không mang thư viện của Steam. Bạn tự cài Steamworks.NET.

## Yêu cầu <a href="#requirements" id="requirements"></a>

- `com.fomoxa.networking` 0.3.4. Package được dựng cho đúng phiên bản đó và kiểm nó, như mô tả ở [Phiên bản](#versions).
- Steamworks.NET 2025.165.0 trở lên, cài dưới dạng package của Unity.
- Build target standalone Windows, Linux hoặc macOS. Trên WebGL, Android, iOS và các target khác, component không được biên dịch.
- Steam client đang chạy và đã đăng nhập trên mọi máy, mỗi người chơi một tài khoản Steam riêng.
- Một AppID của Steam. Trong lúc phát triển, bạn dùng được 480, app thử nghiệm Spacewar của Valve.

## Cài đặt <a href="#install" id="install"></a>

1. Cài `com.fomoxa.networking` như trong trang [cài đặt](../../getting-started/installation.md).
2. Trong Package Manager, chọn **Install package from git URL** rồi thêm Steamworks.NET:

```
https://github.com/rlabrecque/Steamworks.NET.git?path=/com.rlabrecque.steamworks.net#2025.165.0
```

3. Thêm package này theo cùng cách:

```
https://github.com/fomoxa/com.fomoxa.networking.steam.git#0.1.0
```

`SteamNetworkTransport` nằm trong assembly `Fomoxa.Unity.Steam`. Unity chỉ biên dịch assembly đó khi đã cài Steamworks.NET và build target là Windows, Linux hoặc macOS. Chưa cài Steamworks.NET thì project vẫn biên dịch, chỉ là component không có trong menu **Add Component**.

## Khởi động Steam trong game <a href="#start-steam-in-your-game" id="start-steam-in-your-game"></a>

Transport không khởi động Steam. Game của bạn khởi tạo Steam API trước khi chạy server hay client, gọi callback của Steam mỗi frame, và tắt Steam khi thoát, như component dưới đây:

```csharp
using Steamworks;
using UnityEngine;

public sealed class SteamSession : MonoBehaviour
{
    private bool started;

    private void Awake()
    {
        ESteamAPIInitResult result = SteamAPI.InitEx(out string error);
        if (result != ESteamAPIInitResult.k_ESteamAPIInitResult_OK)
        {
            Debug.LogError($"Steam did not start ({result}): {error}");
            return;
        }

        started = true;
        Debug.Log($"Steam ID {SteamUser.GetSteamID().m_SteamID}");
    }

    private void Update()
    {
        if (started)
        {
            SteamAPI.RunCallbacks();
        }
    }

    private void OnDestroy()
    {
        if (started)
        {
            started = false;
            SteamAPI.Shutdown();
        }
    }
}
```

Đặt nó trong cùng scene với `NetworkManager`, và chạy server hay client sau `Awake`, ví dụ trong `Start` hoặc từ một nút bấm. Transport biết một kết nối đã mở hay đã đóng qua callback của Steam. Nếu không có gì gọi `SteamAPI.RunCallbacks()`, kết nối không bao giờ mở xong.

### Tệp AppID <a href="#the-appid-file" id="the-appid-file"></a>

Khi game không được Steam mở, `SteamAPI.InitEx` đọc AppID từ tệp `steam_appid.txt` trong thư mục làm việc. Trong Editor, đó là thư mục gốc của project. Trong bản build, đó là thư mục chứa tệp chạy. Lúc phát triển, tệp chỉ có một dòng:

```text
480
```

Steamworks.NET ghi tệp này vào thư mục gốc của project bằng một script của Editor, nhưng script đó có thể chạy sau khi lượt Play đầu tiên đã khởi động Steam, và lượt Play đó báo `No appID found`. Steamworks.NET cũng không chép tệp ra cạnh bản build. Hãy tự tạo tệp ở thư mục gốc của project, và chép nó ra cạnh bản build, bằng tay hoặc bằng một bước sau khi build. Game do Steam mở thì nhận AppID từ Steam và không đọc tệp này.

## Thiết lập NetworkManager <a href="#set-up-the-networkmanager" id="set-up-the-networkmanager"></a>

1. Thêm `SteamNetworkTransport` vào một GameObject. Nó không có field nào.
2. Gán nó vào field **Transport** của `NetworkManager`.

## Host và vào trận <a href="#host-and-join" id="host-and-join"></a>

Server nghe trên một cổng ảo của Steam, một con số chỉ có nghĩa bên trong Steam. `ServerManager.StartConnection(port)` mở một listen socket của Steam trên cổng ảo đó, và `ServerManager.Port` báo lại đúng số đó. Không có cổng UDP hay TCP nào của máy được mở.

Client truyền SteamID64 của host làm địa chỉ, viết dưới dạng số thập phân, cùng với cổng ảo đó:

```csharp
networkManager.ClientManager.StartConnection("76561198000000001", 7777);
```

Host đọc SteamID64 của mình bằng `SteamUser.GetSteamID().m_SteamID`. Package không có lobby, lời mời hay matchmaking, nên game của bạn tự quyết người chơi gửi SteamID cho nhau thế nào, ví dụ bằng lobby hoặc lời mời bạn bè của Steam qua Steamworks.NET.

Người chơi làm host dùng [host mode](../host-mode.md): `ServerManager.StartConnection(port)`, rồi `ClientManager.StartConnection` với địa chỉ bất kỳ. Client của chính host luôn nối qua [loopback](loopback.md) trong tiến trình, nên không bao giờ đi qua Steam.

Kết nối tới một địa chỉ không phải SteamID64 hỏng ngay với `TransportError`, như khi không tới được một server UDP. Steam cũng từ chối kết nối tới SteamID của chính game, nên một bản thứ hai của game trên cùng tài khoản Steam không vào được trận của bản thứ nhất. Muốn thử với hai người chơi, hãy dùng hai tài khoản Steam trên hai máy.

## Dữ liệu kết nối <a href="#connection-data" id="connection-data"></a>

Ở server, `ServerAuthenticationContext.ConnectionData` chứa SteamID của client dưới dạng 8 byte little-endian. Đọc nó trong [authenticator](../authentication.md):

```csharp
ulong steamId = BinaryPrimitives.ReadUInt64LittleEndian(context.ConnectionData.Span);
```

`BinaryPrimitives` nằm trong `System.Buffers.Binary`. Steam xác thực cả hai đầu của kết nối bằng chứng chỉ do Steam cấp, nên client không thể đưa ra SteamID của tài khoản khác. Package không có authenticator riêng. Cấm người chơi, trận chỉ cho bạn bè và các luật tương tự do game của bạn quyết. Với client của chính host, `ConnectionData` rỗng.

## Hành vi <a href="#behavior" id="behavior"></a>

| | Steam |
|---|---|
| Mô hình kết nối | Một kết nối mạng của Steam, rồi tới handshake của Fomoxa |
| Độ tin cậy của transport | Không dùng; mọi bundle đi dưới dạng message không tin cậy của Steam, và package tự lo độ tin cậy |
| Frame budget cho bundle | 1200 byte |
| Địa chỉ | SteamID64 và cổng ảo |
| Server nghe trên | Một cổng ảo của Steam |
| Mã hoá | Steam mã hoá mọi kết nối |
| Đường đi | Steam chọn: nối thẳng khi hai máy tới được nhau, nếu không thì qua mạng relay của Valve |

Package luôn dùng cách chọn đường mặc định của Steam. RTT và lưu lượng trong [`NetworkStatsDisplay`](../../advanced/debugging.md) tính cả đoạn qua relay khi Steam dùng relay.

## Giới hạn <a href="#limitations" id="limitations"></a>

- Chỉ game chạy cùng Steam client mới host được. Package không dùng API game server của Steam, nên không có bản build server dedicated và không có [server console](../../console-server/overview.md) qua Steam.
- Một tiến trình có một SteamID và không nối được tới chính nó.
- Không có lobby, lời mời hay matchmaking.

## Xử lý sự cố <a href="#troubleshooting" id="troubleshooting"></a>

### `Steam is not initialized` <a href="#steam-is-not-initialized" id="steam-is-not-initialized"></a>

`ServerManager.StartConnection` hoặc `ClientManager.StartConnection` ném:

```text
Steam is not initialized: call SteamAPI.Init() and run SteamAPI.RunCallbacks() every frame before starting a Steam connection
```

Steam chưa khởi động, hoặc khởi động không thành công. Tìm lỗi của `SteamAPI.InitEx` trong log. Nguyên nhân thường gặp là Steam client chưa chạy, hoặc thư mục làm việc thiếu `steam_appid.txt`.

### Client đứng ở `Starting` <a href="#the-client-stays-in-starting" id="the-client-stays-in-starting"></a>

Client đã xin Steam một kết nối và Steam chưa trả lời. Kiểm lần lượt:

1. Cả hai game đều gọi `SteamAPI.RunCallbacks()` mỗi frame.
2. Steam đang online trên cả hai máy. `SteamAPI.InitEx` vẫn thành công và vẫn có SteamID khi Steam client không tới được máy chủ của Steam, nhưng nối thì cần các máy chủ đó. Nếu Steam client báo Offline, cứ đang kết nối mãi, hoặc báo lỗi -101, hãy sửa mạng trước.
3. Địa chỉ là SteamID64 của host, và cổng ảo là cổng host đang nghe.

Muốn xem Steam đang làm gì, hãy ghi log các thay đổi kết nối và thông báo của Steam trong game. Steamworks.NET gọi mọi callback đã đăng ký cho một sự kiện, nên đoạn này không lấy mất sự kiện của transport:

```csharp
using System.Text;
using Steamworks;
using UnityEngine;

public sealed class SteamNetworkingLog : MonoBehaviour
{
    private Callback<SteamNetConnectionStatusChangedCallback_t> statusChanged;
    private FSteamNetworkingSocketsDebugOutput output;

    private void Start()
    {
        statusChanged = Callback<SteamNetConnectionStatusChangedCallback_t>.Create(LogStatus);
        output = LogMessage;
        SteamNetworkingUtils.SetDebugOutputFunction(ESteamNetworkingSocketsDebugOutputType.k_ESteamNetworkingSocketsDebugOutputType_Msg, output);
    }

    private void OnDestroy()
    {
        statusChanged?.Dispose();
    }

    private static void LogStatus(SteamNetConnectionStatusChangedCallback_t status)
    {
        Debug.Log($"Steam connection {status.m_eOldState} -> {status.m_info.m_eState}: {status.m_info.m_szEndDebug}");
    }

    private static void LogMessage(ESteamNetworkingSocketsDebugOutputType type, StringBuilder message)
    {
        Debug.Log($"Steam networking {type}: {message}");
    }
}
```

Đặt nó trong cùng scene với `SteamSession`. `SteamSession` khởi động Steam trong `Awake`, và mọi `Awake` chạy trước mọi `Start`. Máy không tới được máy chủ của Steam sẽ ghi `We're not logged into Steam`.

## Phiên bản <a href="#versions" id="versions"></a>

Package được dựng cho một phiên bản của `com.fomoxa.networking`, ghi trong `SteamPackage.CoreVersion`. Khi `NetworkManager` tạo transport trong `Awake` mà project có phiên bản khác, transport ném `InvalidOperationException`:

```text
com.fomoxa.networking.steam needs com.fomoxa.networking 0.3.4; the project has 0.3.5
```

Hãy cài phiên bản của package này mà [ghi chú phát hành](../../release-notes.md) ghi cho phiên bản `com.fomoxa.networking` của bạn.
