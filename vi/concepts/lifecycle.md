# Vòng đời

Trang này đưa ra thứ tự các sự kiện của `NetworkManager`, của kết nối và của network object.

## NetworkManager <a href="#networkmanager" id="networkmanager"></a>

| Unity message | Manager làm gì |
|---|---|
| `Awake` | Đọc schema và codec đã đăng ký, đăng ký các prefab của Collected Prefabs và Prefabs, đăng ký các scene của Collected Scenes, tạo transport factory cùng `ServerManager`, `ClientManager`, `TimeManager` và `TransportManager`. Ném exception nếu phần đăng ký sinh ra chưa chạy. |
| `OnEnable` | Thêm các entry của nó vào player loop. |
| `OnDisable` | Gỡ các entry đó. Không tick nào chạy, không gì được nhận hay gửi. |
| `OnDestroy` | Dừng client và server, và giải phóng physics simulation. |

Manager cũng dừng cả hai kết nối khi ứng dụng thoát.

Vì các manager được tạo trong `Awake`, component khác có thể dùng chúng từ `Start` trở đi, còn trong `Awake` của chính component đó các manager có thể chưa tồn tại.

## Server <a href="#server" id="server"></a>

```text
ServerManager.StartConnection(port)
    ServerState: Stopped → Starting → Started
    every scene object in the loaded scenes is spawned
    for each client:
        OnRemoteConnectionState: Starting   transport connected, handshake runs
        OnRemoteConnectionState: Started    the client receives the objects it observes
        OnRemoteConnectionState: Stopped    with a StopReason; owned objects are despawned
ServerManager.StopConnection()
    ServerState: Started → Stopping → Stopped
    every client is disconnected, every object is despawned
```

## Client <a href="#client" id="client"></a>

```text
ClientManager.StartConnection(address, port)
    OnClientConnectionState: Starting
    OnClientConnectionState: Started      scene objects are deactivated until the server spawns them
    ... objects spawn, change and despawn ...
    OnClientConnectionState: Stopped      every object is despawned on the client
        WillRetry = true  → Starting again after the reconnect interval
        WillRetry = false → stays Stopped
ClientManager.StopConnection()
```

## Network object <a href="#network-objects" id="network-objects"></a>

### Trên server <a href="#on-the-server" id="on-the-server"></a>

```text
Instantiate(prefab)            Awake, OnEnable of your components
ServerManager.Spawn(instance)
    OnRegisterRpcs, OnRegisterState, OnRegisterInput   first spawn of this instance only
    initial state captured, spawn message queued to observers
    OnStartServer
... ticks ...
    OnOwnerChangedServer(previousOwnerId)              when the owner changes
ServerManager.Despawn(instance), owner leaves, or server stops
    OnStopServer
    despawn message queued
    prefab instance destroyed, scene object deactivated
```

Message spawn chứa state được chụp trước `OnStartServer`, nên hãy đặt state ban đầu trước khi gọi `Spawn`. Thay đổi trong `OnStartServer` chỉ tới client cùng lần cập nhật state ở tick sau.

Hủy một `GameObject` đã spawn trên server sẽ despawn nó.

### Trên client <a href="#on-a-client" id="on-a-client"></a>

```text
spawn message arrives
    prefab instantiated, or scene object activated     Awake, OnEnable of your components
    OnRegisterRpcs, OnRegisterState, OnRegisterInput
    initial state applied
    OnStartClient                                      NetworkObject.IsOwner is valid here
... state changes, RPCs, transforms ...
    OnOwnerChangedClient(previousOwnerId)
despawn message, loss of observation, or client stops
    OnStopClient
    prefab instance destroyed or released to its factory, scene object deactivated
```

`NetworkBehaviour.NetworkObject` được gán khi object spawn, nên trong `Awake` của một prefab vừa instantiate nó vẫn là null.

Nếu client hủy một `GameObject` đã spawn mà không có lệnh despawn từ server, object bị gỡ khỏi danh sách object của client và một cảnh báo được log.

### Ở host mode <a href="#in-host-mode" id="in-host-mode"></a>

Ở host mode, server và client của host dùng chung một instance. Instance đó nhận `OnStartServer` khi server spawn nó và `OnStartClient` khi client của host nhận nó, còn khi despawn thì `OnStopClient` chạy trước `OnStopServer`. [Host mode](../core/host-mode.md) nói về hệ quả đối với code của bạn.

Bản thân các callback được mô tả trong [NetworkBehaviour](../core/network-behaviour.md) và liệt kê trong [event và callback](../reference/callbacks.md). [Mô hình networking](networking-model.md) giải thích sâu hơn về các trạng thái kết nối.
