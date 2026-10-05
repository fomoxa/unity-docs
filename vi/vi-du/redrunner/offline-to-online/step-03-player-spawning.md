# Bước 03: Spawn người chơi

## Mục tiêu <a href="#goal" id="goal"></a>

Sau bước này, game khởi động dưới dạng dedicated server, host hoặc client. Server spawn một nhân vật cho mỗi client tham gia, do client đó sở hữu, và mọi client đều thấy tất cả các nhân vật. Các nhân vật chỉ đứng ở điểm bắt đầu của level cho tới khi bước 04 cho chúng di chuyển.

## Điểm xuất phát <a href="#starting-point" id="starting-point"></a>

Sau bước 02, server và mỗi client dựng cùng một level từ seed, nhưng nhân vật duy nhất vẫn là một object trong `Play.unity`.

## Vấn đề <a href="#problem" id="problem"></a>

```
Offline:
Play.unity
  └── RedRunner (the only character)
        ↑ referenced by GameManager, TerrainGenerator, CameraController
RedCharacter.Update reads the keyboard
GameManager pauses with Time.timeScale = 0
```

Một nhân vật trong scene tồn tại một lần trong mỗi tiến trình, không thuộc về ai, và di chuyển theo bất kỳ bàn phím nào tiến trình đó có. Khi online, số nhân vật phụ thuộc vào ai đang kết nối, nên server phải tạo chúng, và mỗi client phải biết nhân vật nào là của mình. Game online cũng không thể tạm dừng, vì `Time.timeScale = 0` sẽ dừng mô phỏng của server, và mọi người chơi khác theo đó, phía sau màn hình tạm dừng của một người chơi.

## Khái niệm Fomoxa <a href="#fomoxa-concepts" id="fomoxa-concepts"></a>

* [Spawn](../../../core/spawning.md)
* [Ownership](../../../core/ownership.md)
* [Server](../../../core/server.md)
* [Client](../../../core/client.md)
* [Host mode](../../../core/host-mode.md)
* [NetworkTransform](../../../dong-bo/transform.md)
* [Tổng quan physics](../../../physics/overview.md)
* [Tích hợp Editor](../../../unity/editor-integration.md#prefab-step)

## Thiết kế <a href="#design" id="design"></a>

```
Client                         Server
Start screen: Play               NetworkGame.Start (-server)
  ↓                                ↓
NetworkGame.Join(address)        ServerManager.StartConnection(port)
  ↓ ── connect ──→                 ↓
                                 OnRemoteConnectionState(Started)
                                   ↓
                                 Instantiate RedRunner.prefab
                                 ServerManager.Spawn(player, peerId)
  ↓ ←── spawn ──
NetworkPlayer.OnStartClient
  IsOwner? → NetworkGame.SetLocalPlayer
```

`NetworkGame`, một `MonoBehaviour` nằm cạnh `NetworkManager`, giữ các quyết định networking của game: khởi động thế nào, spawn người chơi ở đâu và người chơi nào là cục bộ. `NetworkPlayer`, một `NetworkBehaviour` trên prefab nhân vật, báo người chơi cục bộ. Nhân vật trong scene bị xóa, và prefab `RedRunner.prefab` trở thành người chơi trên mạng.

## File <a href="#files" id="files"></a>

```
Assets/Prefabs/RedRunner.prefab
Assets/Scenes/Play.unity
Assets/Scripts/RedRunner/Characters/RedCharacter.cs
Assets/Scripts/RedRunner/GameManager.cs
Assets/Scripts/RedRunner/Utilities/CameraController.cs
Assets/Scripts/RedRunner/UI/UIScreen/StartScreen.cs
Assets/Scripts/RedRunner/UI/UIScreen/PauseScreen.cs
Assets/Scripts/RedRunner/Networking/NetworkGame.cs
Assets/Scripts/RedRunner/Networking/NetworkPlayer.cs
Assets/Scripts/RedRunner/Networking/Generated/FomoxaPrefabList.asset
Assets/Scripts/RedRunner/Networking/Generated/FomoxaPrefabs.cs
```

## Hiện thực <a href="#implementation" id="implementation"></a>

### Biến nhân vật thành network prefab <a href="#make-the-character-a-network-prefab" id="make-the-character-a-network-prefab"></a>

Mở `Assets/Prefabs/RedRunner.prefab` và thêm vào gốc của nó:

1. `NetworkObject`.
2. `NetworkTransform`, với Sync Rotation tắt (`Rigidbody2D` khóa góc xoay) và Sync Scale bật (`RedCharacter` quay trái hoặc phải bằng `localScale.x`).
3. `NetworkPlayer`, mô tả bên dưới.

Lưu prefab và chọn Tools > Fomoxa > Assign Prefab Ids, việc này gán cho prefab một id trong `Generated/FomoxaPrefabList.asset`.

Sau đó xóa object `RedRunner` khỏi `Play.unity`. Việc này để trống field Main Character của Game Manager, field Character của Terrain Generator và field Followee của camera.

### Cho game chạy mà không có nhân vật trong scene <a href="#let-the-game-run-without-a-scene-character" id="let-the-game-run-without-a-scene-character"></a>

`GameManager.Start` và `Update` giờ kiểm tra `m_MainCharacter` có null hay không. `CameraController.Follow ()` return sớm khi không có gì để đi theo, và có thêm một overload đặt followee:

```csharp
public void Follow ( Transform followee )
{
	m_Followee = followee;
}
```

`GameManager.StopGame` và `ResumeGame` giờ chỉ đặt cờ và không động tới `Time.timeScale`:

Trước:

```csharp
public void StopGame()
{
    m_GameRunning = false;
    Time.timeScale = 0f;
}
```

Sau:

```csharp
public void StopGame()
{
    m_GameRunning = false;
}
```

`RedCharacter.Update` không còn đọc bàn phím hay di chuyển nhân vật, vì bước 04 gửi input qua mạng. Hành động đỡ và đấm bị bỏ khỏi game online.

### Cấu hình NetworkManager <a href="#configure-the-networkmanager" id="configure-the-networkmanager"></a>

| Field                 | Giá trị                            | Lý do                                                                                                                                                            |
| --------------------- | ---------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Tick Rate             | 50                                 | Fixed timestep của project là 0.02 giây, nên physics step thường xuyên như trong game offline.                                                                   |
| Simulate Physics      | bật                                | Manager step physics 2D mỗi tick một lần. Trên client, `Rigidbody2D` networked mà client không dự đoán trở thành kinematic và đi theo `NetworkTransform` của nó. |
| Max Reconnect Retries | 3                                  | Mặc định -1 thử lại mãi. Với 3, client không tới được server sẽ dừng và game quay về màn hình bắt đầu.                                                           |
| Collected Prefabs     | `Generated/FomoxaPrefabList.asset` | Xem bên dưới.                                                                                                                                                    |
| Collected Scenes      | `Generated/FomoxaSceneList.asset`  | Xem bên dưới.                                                                                                                                                    |

Package tự gán cả hai danh sách khi Unity chuẩn bị scene cho Play Mode, nhưng trong Editor việc đó xảy ra sau khi `NetworkManager.Awake` đã đăng ký prefab, và khi đó việc spawn thất bại với `prefab id 0x... of RedRunner(Clone) is not registered`. Bản build player nhận các danh sách trong lúc build. Gán chúng trong scene thì dùng được cho cả hai trường hợp.

### Khởi động server, host hoặc client <a href="#start-a-server-a-host-or-a-client" id="start-a-server-a-host-or-a-client"></a>

`NetworkGame.cs` (rút gọn; file đầy đủ nằm trong `Assets/Scripts/RedRunner/Networking`):

```csharp
private void Start()
{
    m_Manager.ServerManager.OnRemoteConnectionState += OnRemoteConnectionState;
    m_Manager.ClientManager.OnClientConnectionState += OnClientConnectionState;
    string[] arguments = Environment.GetCommandLineArgs();
    ushort port = ReadPort(arguments);
    if (Array.IndexOf(arguments, "-server") >= 0)
    {
        Application.targetFrameRate = m_ServerFrameRate;
        StartServer(port);
    }
    else if (Array.IndexOf(arguments, "-host") >= 0)
    {
        Host(port);
    }
}

public void StartServer(ushort port)
{
    m_Manager.ServerManager.StartConnection(port);
    Debug.Log($"[RedRunner] server listening on UDP port {m_Manager.ServerManager.Port}");
}

public void Host(ushort port)
{
    StartServer(port);
    m_Manager.ClientManager.StartConnection("localhost", m_Manager.ServerManager.Port);
}

public void Join(string address, ushort port)
{
    m_Manager.ClientManager.StartConnection(string.IsNullOrWhiteSpace(address) ? "localhost" : address.Trim(), port);
}

public void Leave()
{
    m_Manager.ClientManager.StopConnection();
    if (IsServer)
    {
        m_Manager.ServerManager.StopConnection();
    }
}

private void OnRemoteConnectionState(ConnectionStateArgs args)
{
    if (args.State != ConnectionState.Started)
    {
        return;
    }

    NetworkObject player = Instantiate(m_PlayerPrefab, m_SpawnPoint, Quaternion.identity);
    m_Manager.ServerManager.Spawn(player, args.PeerId);
    Debug.Log($"[RedRunner] spawned a player for peer {args.PeerId} at {m_SpawnPoint}");
}
```

`-server` khởi động dedicated server và giới hạn frame rate ở `m_ServerFrameRate` (60), vì player ở batch mode nếu không sẽ chạy frame nhanh nhất CPU cho phép. `-host` chạy server và client trong cùng tiến trình, và `-port` đổi port UDP khỏi giá trị mặc định 7777. Để phục vụ màn hình bắt đầu, class này còn phát `ClientStateChanged` với mỗi `ConnectionState` của client.

Server spawn một nhân vật với peer làm owner ngay khi peer tới `ConnectionState.Started`. Lúc đó level đã tồn tại, vì `NetworkLevel` dựng nó khi server khởi động. Khi peer rời đi, package despawn nhân vật, vì Despawn With Owner bật theo mặc định.

`NetworkPlayer.cs` ở bước này chỉ báo người chơi cục bộ:

```csharp
public sealed class NetworkPlayer : NetworkBehaviour
{
    private NetworkGame m_Game;

    public override void OnStartClient()
    {
        if (NetworkObject.IsOwner)
        {
            m_Game = FindFirstObjectByType<NetworkGame>();
            m_Game?.SetLocalPlayer(this);
        }
    }

    public override void OnStopClient()
    {
        m_Game?.ClearLocalPlayer(this);
        m_Game = null;
    }
}
```

`NetworkObject.IsOwner` đã hợp lệ trong `OnStartClient`. Package không cho client biết peer id của chính nó, nên ownership là cách client tìm nhân vật cục bộ của mình.

Thêm `NetworkGame` vào object `Network Manager`, với `NetworkManager` trong Manager và `RedRunner.prefab` trong Player Prefab. Điểm spawn mặc định, (7.24, 12.59), là chỗ nhân vật trong scene từng đứng.

Fomoxa tạo nhân vật trên mọi client, gán owner và despawn nhân vật khi owner rời đi, còn game quyết định khi nào spawn, ở đâu và dùng prefab nào.

### Thêm ô địa chỉ <a href="#add-the-address-field" id="add-the-address-field"></a>

Dưới `Canvas/Start Screen`, thêm một GameObject > UI > Legacy > Input Field tên `Address Field`, bên dưới hàng nút nhỏ (vị trí 0, -222, kích thước 320 × 48). Đặt text của nó là `localhost` và placeholder là `Server address`. Cho cả hai text dùng font của game, `Baloo-Regular`, cỡ 24, căn giữa, với Vertical Overflow đặt là Overflow, vì với Truncate thì chiều cao dòng của Baloo che mất chữ. Các thiết lập bố cục này đến từ commit `7396f92` ở bước 09; trong `1b65628`, ô này nằm ở chỗ khác trên màn hình và chữ của nó không hiện.

![Màn hình bắt đầu với ô địa chỉ](../../../.gitbook/assets/redrunner-start-screen.png)

`StartScreen` có thêm field `AddressField` và `Network`. Nút Play gọi `Network.Join(AddressField.text)` trước khi mở màn hình trong game, và nếu kết nối của client dừng trong lúc game chạy, màn hình bắt đầu hiện lại. `PauseScreen` cũng có field `Network`, và nút Home của nó gọi `Network.Leave()` trước `GameManager.Init()`.

## Test <a href="#test" id="test"></a>

Build một player Windows với `Play.unity` là scene duy nhất và khởi động một server:

```
RedRunner.exe -batchmode -nographics -server -port 7777 -logFile server.log
```

Bấm Play trong Editor, giữ `localhost` trong ô địa chỉ và bấm Play. Khởi động thêm client từ bản build để thấy thêm nhân vật, hoặc chạy bản build với `-host` để thử mọi thứ trong một tiến trình.

Các bài kiểm tra riêng của bản port là `HostCheck`, `JoinCheck` và `PlayerCheck` trong `Tools/PortChecks`.

## Kết quả mong đợi <a href="#expected-result" id="expected-result"></a>

Log của server hiện seed, port và từng lần spawn. Dòng seed đến từ một `Debug.Log` trong `NetworkLevel.OnStartServer`, cũng được thêm ở bước này:

```
[RedRunner] level seed 1535992127
[RedRunner] server listening on UDP port 7777
[RedRunner] spawned a player for peer 1 at (7.24, 12.59)
```

Mỗi client dựng level từ seed của server, và nhân vật của nó rơi xuống khối bắt đầu. Nhiều nhân vật đứng cùng một chỗ và đi xuyên qua nhau, vì layer collision matrix 2D đã tắt va chạm giữa `Characters` với `Characters`. Chưa ai di chuyển.

## Commit <a href="#commit" id="commit"></a>

```
Commit: 1b65628
Message: Join a dedicated server, a host or a client from the start screen
```

Xem [`1b65628`](https://github.com/fomoxa/RedRunner/commit/1b656285a486c6be727309e48d6612a3e483da80) trên GitHub, rồi tiếp tục với [bước 04: input của người chơi](step-04-player-input.md).
