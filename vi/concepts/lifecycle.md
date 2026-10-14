# Vòng đời

Trang này đưa ra thứ tự event của `NetworkManager`, của kết nối và của network object. Hãy dùng nó để quyết định một đoạn code nên nằm ở đâu: trong `Awake`, trong `OnStartServer`, trong một event kết nối hay trong `OnStopClient`.

## NetworkManager <a href="#networkmanager" id="networkmanager"></a>

| Message của Unity | Manager làm gì |
|---|---|
| `Awake` | Đọc schema và codec đã đăng ký, đăng ký prefab của Collected Prefabs và Prefabs, đăng ký scene của Collected Scenes, tạo transport factory cùng `ServerManager`, `ClientManager`, `TimeManager` và `TransportManager`. Ném exception nếu phần đăng ký sinh ra chưa chạy. |
| `OnEnable` | Thêm các mục của nó vào player loop. |
| `OnDisable` | Gỡ các mục đó. Không tick nào chạy, không gì được nhận hay gửi. |
| `OnDestroy` | Dừng client và server, và giải phóng physics simulation. |

Manager cũng dừng cả hai kết nối khi ứng dụng thoát.

Vì các manager được tạo trong `Awake`, các component khác có thể dùng chúng từ `Start` trở đi. Trong `Awake` của chính các component đó, manager có thể chưa tồn tại.

## Server <a href="#server" id="server"></a>

```mermaid
sequenceDiagram
    participant Code as Code của bạn
    participant SM as ServerManager
    participant Peer as Một client
    Code->>SM: StartConnection(port)
    Note over SM: ServerState Stopped → Starting → Started<br/>spawn mọi scene object trong các scene đã load
    Peer->>SM: transport kết nối
    SM-->>Code: OnRemoteConnectionState: Starting (handshake đang chạy)
    SM-->>Code: OnRemoteConnectionState: Started
    Note over SM,Peer: client nhận các object nó observe
    Peer->>SM: rời đi, hết thời gian chờ hoặc thất bại
    SM-->>Code: OnRemoteConnectionState: Stopped, kèm một StopReason
    Note over SM: despawn các object mà peer sở hữu
    Code->>SM: StopConnection()
    Note over SM: ServerState Started → Stopping → Stopped<br/>ngắt mọi client, despawn mọi object
```

## Client <a href="#client" id="client"></a>

```mermaid
stateDiagram-v2
    direction LR
    [*] --> Starting: StartConnection(address, port)
    Starting --> Started: handshake thành công
    Started --> Stopped: kết nối kết thúc
    Starting --> Stopped: kết nối thất bại
    Stopped --> Starting: WillRetry, sau khoảng reconnect interval
    Stopped --> [*]: WillRetry là false, hoặc StopConnection()
```

`OnClientConnectionState` báo từng thay đổi. Khi client tới `Started`, các scene object trong các scene nó đã load bị tắt cho tới khi server spawn chúng. Sau đó các object được spawn, thay đổi và despawn. Khi kết nối dừng, mọi object trên client bị despawn, và `ConnectionStateArgs.WillRetry` cho biết client có khởi động lại sau khoảng reconnect interval hay không.

## Network object <a href="#network-objects" id="network-objects"></a>

### Trên server <a href="#on-the-server" id="on-the-server"></a>

```mermaid
sequenceDiagram
    participant Code as Code của bạn
    participant Obj as Object
    participant SM as ServerManager
    Code->>Obj: Instantiate(prefab): Awake, OnEnable
    Code->>SM: Spawn(instance, owner)
    SM->>Obj: OnRegisterRpcs, OnRegisterState, OnRegisterInput (chỉ ở lần spawn đầu của instance)
    Note over SM: chụp state ban đầu,<br/>đưa message spawn vào hàng đợi cho observer
    SM->>Obj: OnStartServer
    Note over Obj: ... các tick ...
    SM->>Obj: OnOwnerChangedServer(previousOwnerId), khi owner thay đổi
    Code->>SM: Despawn(instance), hoặc owner rời đi, hoặc server dừng
    SM->>Obj: OnStopServer
    Note over SM: đưa message despawn vào hàng đợi,<br/>hủy instance của prefab hoặc tắt scene object
```

Message spawn chứa state được chụp trước `OnStartServer`, nên hãy đặt state ban đầu trước khi gọi `Spawn`. Một thay đổi làm trong `OnStartServer` chỉ tới client cùng cập nhật state của tick sau.

Hủy một `GameObject` đã spawn trên server sẽ despawn nó.

### Trên client <a href="#on-a-client" id="on-a-client"></a>

```mermaid
sequenceDiagram
    participant CM as ClientManager
    participant Obj as Object
    CM->>Obj: spawn tới: tạo instance của prefab hoặc bật scene object (Awake, OnEnable)
    CM->>Obj: OnRegisterRpcs, OnRegisterState, OnRegisterInput
    Note over CM: áp state ban đầu
    CM->>Obj: OnStartClient (IsOwner đã đúng ở đây)
    Note over Obj: ... state thay đổi, RPC, transform ...
    CM->>Obj: OnOwnerChangedClient(previousOwnerId)
    CM->>Obj: despawn, mất quyền observe, hoặc client dừng: OnStopClient
    Note over CM: hủy instance hoặc trả nó về factory,<br/>hoặc tắt scene object
```

`NetworkBehaviour.NetworkObject` được gán khi object spawn, nên trong `Awake` của một prefab vừa tạo instance nó vẫn là null.

Nếu một client hủy một `GameObject` đã spawn mà không có despawn từ server, object bị gỡ khỏi danh sách object của client và một cảnh báo được log.

### Trong host mode <a href="#in-host-mode" id="in-host-mode"></a>

Trong host mode, server và client của host dùng chung một instance. Instance đó nhận `OnStartServer` khi server spawn nó và `OnStartClient` khi client của host nhận nó. Khi despawn, `OnStopClient` chạy trước `OnStopServer`. [Host mode](../connections/host-mode.md) nói về hệ quả với code của bạn.

Các callback được mô tả trong [NetworkBehaviour](../objects/network-behaviour.md) và liệt kê trong [event và callback](../reference/callbacks.md). [Server, client và message](networking-model.md) giải thích kỹ hơn các trạng thái kết nối.
