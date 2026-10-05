# Host mode

Host chạy một server và một client trong cùng tiến trình, nên người chơi của host chơi trên chính máy đang phục vụ mọi người khác.

## Cách dùng cơ bản <a href="#basic-usage" id="basic-usage"></a>

Khởi động server, rồi tới client, trên cùng một `NetworkManager`:

```csharp
manager.ServerManager.StartConnection(7777);
manager.ClientManager.StartConnection("localhost", manager.ServerManager.Port);
```

Vì server của manager đang chạy, client kết nối qua một kết nối [loopback](../transports/loopback.md) trong tiến trình, bỏ qua địa chỉ, port và không đi qua transport. Các client khác kết nối tới host qua transport, giống như với một dedicated server.

Client của host nhận peer id như mọi client khác, và server spawn object cho nó trong `OnRemoteConnectionState` như thường lệ.

## Mỗi object một instance <a href="#one-instance-per-object" id="one-instance-per-object"></a>

Host không tạo bản copy thứ hai của mỗi object cho client của mình; instance của server cũng là instance của client. Do đó cùng một component nhận `OnStartServer` khi server spawn object và `OnStartClient` khi client của host nhận nó, và `NetworkObject.IsOwner` là true với các object thuộc peer id của host.

Vì instance đã chứa giá trị của server, client của host không decode state lần thứ hai, dù các callback `onChanged` vẫn chạy. Cũng vì vậy `NetworkTransform` không interpolate trên host, nơi transform vốn đã là transform của server. Các object lẽ ra được dự đoán trên client ở xa thì cũng không được dự đoán cho host: server thu thập và áp dụng input của host trực tiếp trong cùng tick.

Code chỉ được chạy một lần cho mỗi object, như bắt đầu một hiệu ứng, nên kiểm tra mình đang chạy trên server, client hay cả hai. Trên host, `NetworkObject.IsSpawned` là true kể từ lúc server spawn.

## Object mà client của host không observe <a href="#objects-the-hosts-client-does-not-observe" id="objects-the-hosts-client-does-not-observe"></a>

Trên một client riêng, object mà client không observe đơn giản là không tồn tại. Trên host nó vẫn phải tồn tại vì server cần nó, nên package ẩn nó đi bằng cách tắt mọi `Renderer` đang bật bên dưới object và gọi `OnHostVisibility(false)` trên các behaviour của nó. Khi client của host bắt đầu observe object, các renderer hiện lại và `OnHostVisibility(true)` chạy.

Override `OnHostVisibility` để ẩn những gì renderer không bao quát, như âm thanh hay UI:

```csharp
protected override void OnHostVisibility(bool visible)
{
    audioSource.mute = !visible;
}
```

Khi client của host dừng, mọi object được hiện lại.

## Dừng <a href="#stopping" id="stopping"></a>

Dừng client của host vẫn để server chạy cho các client khác, còn dừng server sẽ ngắt mọi client, kể cả client của host.

## Giới hạn <a href="#limitations" id="limitations"></a>

Host không chạy được trong bản build WebGL, vì trình duyệt không nhận kết nối tới. Prediction không chạy cho object của chính host, nên host không bao giờ reconcile, nhưng các client ở xa của host vẫn dự đoán object của chúng bình thường.

Host mode kết hợp [server](server.md) và [client](client.md) qua một kết nối [loopback](../transports/loopback.md), còn [observer](observers.md) giải thích cách server quyết định client của host nên thấy gì.
