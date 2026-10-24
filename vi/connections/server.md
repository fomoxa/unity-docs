# Server

`ServerManager`, truy cập qua `NetworkManager.ServerManager`, chạy phía server của game. Nó lắng nghe client, theo dõi các peer đã kết nối, spawn object và quyết định ai observe chúng.

## Khởi động và dừng <a href="#start-and-stop" id="start-and-stop"></a>

```csharp
manager.ServerManager.StartConnection(7777);
Debug.Log($"listening on {manager.ServerManager.Port}");

manager.ServerManager.StopConnection();
```

`State` là một `ServerState`, và `OnServerConnectionState` báo mỗi lần thay đổi:

```mermaid
stateDiagram-v2
    direction LR
    [*] --> Stopped
    Stopped --> Starting: StartConnection(port)
    Starting --> Started: listener đã mở
    Started --> Stopping: StopConnection()
    Stopping --> Stopped: mọi client đã ngắt
```

`StartConnection(port)` mở listener của transport, cùng một listener trong tiến trình cho client của host. Port 0 để hệ điều hành chọn port, và `Port` báo port đang dùng, hoặc 0 khi server đã dừng. Gọi `StartConnection` trên server đang chạy sẽ ném `the server is already running`. Ngay sau khi tới `Started`, server spawn mọi `NetworkObject` đặt trong các scene đã load, như mô tả trong [spawn](../objects/spawning.md#scene-objects).

`StopConnection()` ngắt mọi client. Khi state đã là `Stopped`, server despawn mọi object theo thứ tự ngược với lúc spawn, hủy các instance prefab và tắt các scene object, rồi unload các network scene nó đã load.

## Peer <a href="#peers" id="peers"></a>

Mỗi client nhận một peer id khi transport của nó kết nối, và `OnRemoteConnectionState` báo các trạng thái của client:

```csharp
manager.ServerManager.OnRemoteConnectionState += args =>
{
    switch (args.State)
    {
        case ConnectionState.Starting:
            Debug.Log($"peer {args.PeerId} is connecting");
            break;
        case ConnectionState.Started:
            Debug.Log($"peer {args.PeerId} joined");
            break;
        case ConnectionState.Stopped:
            Debug.Log($"peer {args.PeerId} left: {args.Reason}, {args.DiscardedMessages} messages discarded");
            break;
    }
};
```

Một peer ở `Starting` trong lúc handshake chạy và tới `Started` khi handshake thành công. Hãy spawn object của peer ở thời điểm đó, vì trước đó nó chưa nhận được chúng. Server không cung cấp danh sách peer id, nên nếu cần, hãy tự giữ một tập từ các event này. [Vòng đời](../concepts/lifecycle.md#server) đưa ra toàn bộ trình tự cho một client.

| Member | Mục đích |
|---|---|
| `PeerCount` | Số peer đã kết nối, kể cả peer còn đang handshake |
| `PeerState(peerId)` | `ConnectionState` của một peer; `Stopped` với peer không biết |
| `Disconnect(peerId)` | Đóng kết nối của một peer; nó dừng với `LocalStop` |
| `HasRtt(peerId)`, `RttOf(peerId)` | Round-trip time mà client của peer báo qua các clock ping |
| `DroppedInputsOf(peerId)` | Số input từ peer mà server không dùng được |
| `FrameBudgetOf(peerId)` | Frame budget của transport mà peer kết nối qua |

Khi một peer dừng, server despawn các object nó sở hữu. Object có `NetworkObject` tắt Despawn With Owner thì được giữ lại và chuyển sang do server sở hữu; xem [ownership](../objects/ownership.md).

## Object <a href="#objects" id="objects"></a>

| Member | Hướng dẫn |
|---|---|
| `Spawn(networkObject, ownerId)`, `Despawn(networkObject)` | [Spawn](../objects/spawning.md) |
| `ChangeOwner(networkObject, ownerId)` | [Ownership](../objects/ownership.md) |
| `IsObserver`, `RebuildObservers`, `ObserverRule`, `ObserverInterval`, `Groups` | [Observer](../objects/observers.md) |
| `Scenes` | [Network scene](../objects/scenes.md) |
| `Spawned` | Mọi object server này đã spawn, theo object id. Giá trị là `INetworkEntity`; trong Unity mỗi giá trị là một `NetworkObject`. |

## Message <a href="#messages" id="messages"></a>

`Send(peerId, messageId, payload)`, `SendToObject(...)` và `Broadcast(messageId, payload)` gửi các message không gắn với RPC, còn `Dispatcher` đăng ký handler cho message tới. [Raw message](../messaging/messages.md) hướng dẫn cách dùng chúng.

## Lỗi trong handler <a href="#errors-in-handlers" id="errors-in-handlers"></a>

Khi một handler ném exception lúc server xử lý message của một peer, ví dụ một server RPC, server ngắt kết nối peer đó với `StopReason.HandlerException` và phát `OnHandlerException` kèm peer id, message id và exception. Nếu không có ai subscribe event này, package tự log exception. Message không decode được thì không làm ngắt kết nối peer; nó bị bỏ và phát `OnReceiveDropped`.

Exception ném ra trong `apply` của input model hoặc trong một `ObserverRule` được log và không ngắt kết nối ai.

[Tham chiếu ServerManager](../reference/server-manager.md) liệt kê mọi member. Để chạy server riêng hoặc cùng một client, xem [dedicated server](../deploy/dedicated-server.md) và [host mode](host-mode.md).
