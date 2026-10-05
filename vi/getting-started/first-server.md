# Server đầu tiên

Trang này thêm một launcher vào scene từ [project đầu tiên](first-project.md). Launcher khởi động server, host hoặc client, và server spawn một `Player` cho mỗi client kết nối tới. Ở đây bạn chỉ thử server; [client đầu tiên](first-client.md) sẽ kết nối client tới nó.

## 1. Viết launcher <a href="#1-write-the-launcher" id="1-write-the-launcher"></a>

Tạo `Assets/Network/Launcher.cs`:

```csharp
using System;
using Fomoxa.Unity;
using Fomoxa.Unity.Sessions;
using UnityEngine;

namespace MyGame.Network
{
    public sealed class Launcher : MonoBehaviour
    {
        [SerializeField] private NetworkManager manager;
        [SerializeField] private NetworkObject playerPrefab;
        [SerializeField] private ushort port = 7777;

        private string address = "127.0.0.1";

        private void Start()
        {
            manager.ServerManager.OnRemoteConnectionState += OnRemoteConnectionState;
            manager.ClientManager.OnClientConnectionState += OnClientConnectionState;
            if (Array.IndexOf(Environment.GetCommandLineArgs(), "-server") >= 0)
            {
                StartServer();
            }
        }

        private void OnDestroy()
        {
            if (manager != null && manager.ServerManager != null)
            {
                manager.ServerManager.OnRemoteConnectionState -= OnRemoteConnectionState;
                manager.ClientManager.OnClientConnectionState -= OnClientConnectionState;
            }
        }

        private void OnGUI()
        {
            bool serverRunning = manager.ServerManager.State != ServerState.Stopped;
            bool clientRunning = manager.ClientManager.State != ConnectionState.Stopped;
            if (serverRunning || clientRunning)
            {
                GUILayout.Label($"server: {manager.ServerManager.State}, peers: {manager.ServerManager.PeerCount}, client: {manager.ClientManager.State}");
                if (GUILayout.Button("Stop"))
                {
                    manager.ClientManager.StopConnection();
                    manager.ServerManager.StopConnection();
                }

                return;
            }

            address = GUILayout.TextField(address);
            if (GUILayout.Button("Server"))
            {
                StartServer();
            }

            if (GUILayout.Button("Host"))
            {
                StartServer();
                manager.ClientManager.StartConnection(address, manager.ServerManager.Port);
            }

            if (GUILayout.Button("Client"))
            {
                manager.ClientManager.StartConnection(address, port);
            }
        }

        private void StartServer()
        {
            manager.ServerManager.StartConnection(port);
            Debug.Log($"server listening on port {manager.ServerManager.Port}");
        }

        private void OnRemoteConnectionState(ConnectionStateArgs args)
        {
            Debug.Log($"peer {args.PeerId}: {args.State} {args.Reason}");
            if (args.State != ConnectionState.Started)
            {
                return;
            }

            var position = new Vector3(args.PeerId * 2f, 0f, 0f);
            NetworkObject player = Instantiate(playerPrefab, position, Quaternion.identity);
            manager.ServerManager.Spawn(player, args.PeerId);
        }

        private void OnClientConnectionState(ConnectionStateArgs args)
        {
            Debug.Log($"client: {args.State} {args.Reason}");
        }
    }
}
```

## 2. Phần server hoạt động thế nào <a href="#2-how-the-server-part-works" id="2-how-the-server-part-works"></a>

`ServerManager.StartConnection(port)` mở listener của transport trên port đó. Port 0 để hệ điều hành chọn một port trống, và `ServerManager.Port` luôn báo port đang thực sự được dùng.

`ServerManager.OnRemoteConnectionState` báo mọi thay đổi trong kết nối của client. Mỗi client có một peer id, `args.PeerId`, và đi qua ba trạng thái: `Starting` khi transport đã kết nối và handshake Fomoxa đang chạy, `Started` khi handshake thành công và message bắt đầu truyền được, cuối cùng là `Stopped`.

Khi một client tới `Started`, launcher instantiate prefab và gọi `ServerManager.Spawn(player, args.PeerId)`. Việc spawn gán object id, đặt peer làm owner và gửi object tới mọi client đang observe nó. Object truyền vào phải là một instance trong scene chứ không phải asset prefab, và prefab của nó phải được đăng ký với `NetworkManager`, việc mà danh sách Collected Prefabs đã lo ở trang trước.

Mặc định `NetworkObject` bị despawn cùng owner của nó, nên khi client rời đi, package despawn player của client đó, và despawn trên server sẽ hủy instance. `ServerManager.StopConnection()` ngắt mọi client và despawn mọi object.

## 3. Thêm launcher vào scene <a href="#3-add-the-launcher-to-the-scene" id="3-add-the-launcher-to-the-scene"></a>

1. Chọn `Network Manager` và thêm component `Launcher`.
2. Kéo component `NetworkManager` vào field Manager của nó và prefab `Player` vào Player Prefab.
3. Lưu scene.

## 4. Thử server <a href="#4-test-the-server" id="4-test-the-server"></a>

Vào Play Mode và bấm Server. Console sẽ hiện `server listening on port 7777`, và nhãn trên màn hình sẽ là `server: Started, peers: 0, client: Stopped`. Bấm Stop rồi thoát Play Mode.

Nếu `StartConnection` ném `SocketException`, port không mở được, ví dụ vì một tiến trình khác đang dùng UDP port 7777. Đổi field Port của launcher rồi thử lại.

## 5. Chạy dedicated server <a href="#5-run-a-dedicated-server" id="5-run-a-dedicated-server"></a>

Dedicated server là một bản build player chạy không có đồ họa, và launcher khởi động server khi dòng lệnh có `-server`.

1. Mở File > Build Profiles, chọn nền tảng desktop và build player, ví dụ ra `Builds/MyGame.exe` trên Windows.
2. Chạy nó từ terminal:

```
MyGame.exe -batchmode -nographics -server -logFile server.log
```

`server.log` sẽ chứa `server listening on port 7777`. Để tiến trình chạy tiếp cho trang sau, và dừng nó bằng công cụ quản lý tiến trình của hệ điều hành khi xong. [Dedicated server](../server/dedicated-server.md) nói thêm về frame rate, port và các chi tiết khác.

Tiếp theo là [client đầu tiên](first-client.md).
