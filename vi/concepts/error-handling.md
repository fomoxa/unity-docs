# Lỗi

Package xử lý một lỗi tuỳ theo nơi nó xuất phát: dữ liệu không đọc được, code của chính bạn ném exception, hay hai phía không khớp nhau về object. Trang này liệt kê package làm gì trong từng trường hợp và vì sao, để bạn biết lỗi nào kết thúc kết nối và lỗi nào chỉ bỏ một message.

## Tổng quan <a href="#overview" id="overview"></a>

| Lỗi | Package làm gì | Vì sao | Game của bạn làm gì |
|---|---|---|---|
| Một bundle nhận được không đọc được | Bỏ cả frame và phát `OnReceiveDropped` | Bundle được kiểm tra trước khi giao bất kỳ message nào trong nó, nên chưa có gì trong bundle chạy | Không cần làm gì; mặc định có một cảnh báo trong log |
| Một model trong bundle không decode được | Chỉ bỏ message đó, phát `OnReceiveDropped`, giữ kết nối | Dữ liệu bị hỏng, nhưng các message trước nó đã chạy rồi, nên phần còn lại của bundle vẫn được giao | Không cần làm gì |
| Một message gửi tới object mà phía nhận không có | Bỏ message, giữ kết nối | Message trên các channel khác nhau có thể tới sau khi object đã bị despawn; chuyện này bình thường | Không cần làm gì |
| Một message handler trên server ném exception, ví dụ một server RPC | Phát `OnHandlerException`, rồi đóng kết nối của peer đó với `HandlerException`. Server và các peer khác vẫn chạy | Handler có thể đã để state của game thay đổi dở dang, và một client có dữ liệu làm hỏng handler của server thì không nên được tiếp tục gửi nó | Kiểm tra dữ liệu của client; đặt `Disconnect` thành `false` khi bạn biết exception đó vô hại |
| Một message handler trên client ném exception | Phát `OnHandlerException`, dừng client với `HandlerException`, không thử lại | State của client có thể đã sai, và thử lại sẽ gặp lại đúng handler đó | Sửa handler, hoặc tự gọi `StartConnection` |
| Authenticator, một spawn data source hoặc một object factory ném exception | Phát `OnHandlerException`, rồi đóng kết nối của peer; `Disconnect` bị bỏ qua | Không được cho một peer vào sau khi bước xác thực của nó thất bại, và một client thiếu một object sẽ hỏng về sau ở một chỗ khó lần ra | Sửa đoạn code đã ném exception |
| Server gửi một spawn, despawn hoặc đổi owner mà client không áp dụng được, hoặc một prefab hay scene mà client không có | Phát `OnObjectMismatch`, dừng client với `ObjectMismatch` hoặc `PrefabMismatch`, không thử lại | Các message này đi theo thứ tự trên channel reliable, nên chuyện này chỉ xảy ra khi hai bản build khác nhau hoặc phía gửi có bug; kết nối lại cũng cho cùng kết quả | Phát hành các bản build khớp nhau; báo lỗi |
| Một callback chạy trong tick ném exception: `OnStopServer`, `OnStopClient`, `OnStartServer` của scene object, `apply` của một input model, một `ObserverRule` | Log exception và tiếp tục với các object khác | Callback không thuộc về riêng peer nào, và dừng tick sẽ làm hỏng mọi kết nối | Sửa callback |

[Tham chiếu lỗi](../reference/errors.md) liệt kê mọi lý do dừng, lý do đóng và loại mismatch, còn [kết nối lại](../connections/client.md#reconnection) liệt kê những lý do mà client thử lại.

## Exception trong handler phía server <a href="#exceptions-in-server-handlers" id="exceptions-in-server-handlers"></a>

Mặc định, một handler trên server ném exception sẽ ngắt kết nối peer mà nó đang xử lý message. Peer dừng với `StopReason.HandlerException`, còn client dừng với `ServerClosed` và `CloseReason` là `HandlerException`, nên nó không kết nối lại rồi gặp lại đúng lỗi đó. Nếu không có ai subscribe `OnHandlerException`, package tự log exception.

Subscriber có thể giữ peer lại. `HandlerExceptionArgs.Disconnect` ban đầu là `true`; đặt nó thành `false` thì server giữ kết nối, giao phần còn lại của bundle và mọi message sau đó như bình thường:

```csharp
using System;
using Fomoxa.Networking.Sessions;
using Fomoxa.Unity;
using UnityEngine;

public sealed class InvalidRequestException : Exception
{
    public InvalidRequestException(string message) : base(message)
    {
    }
}

public sealed class HandlerErrors : MonoBehaviour
{
    [SerializeField] private NetworkManager manager;

    private void OnEnable() => manager.ServerManager.OnHandlerException += Decide;

    private void OnDisable() => manager.ServerManager.OnHandlerException -= Decide;

    private static void Decide(HandlerExceptionArgs args)
    {
        Debug.LogException(args.Exception);
        if (args.Exception is InvalidRequestException)
        {
            args.Disconnect = false;
        }
    }
}
```

Event được phát ngay khi handler ném exception, trước message kế tiếp của bundle, nên quyết định áp dụng cho phần còn lại của bundle đó. Mọi subscriber nhận cùng một đối tượng tham số; subscriber sau thấy giá trị mà subscriber trước đã đặt. Chỉ giữ peer khi bạn biết state của game vẫn đúng, ví dụ khi exception đến từ phép kiểm tra input của chính bạn.

`Disconnect` chỉ có tác dụng với message handler trên server, như server RPC và [raw message](../messaging/messages.md). Server luôn ngắt kết nối peer khi authenticator, một spawn data source hoặc một object factory ném exception, và client luôn dừng khi một handler của nó ném exception.

## Kiểm tra dữ liệu của client trong handler phía server <a href="#validate-client-data-in-server-handlers" id="validate-client-data-in-server-handlers"></a>

Server RPC chạy với tham số do client chọn, và trong game mà server có thẩm quyền, client đó có thể gửi bất cứ thứ gì. Hãy kiểm tra mọi tham số trước khi dùng, và khi yêu cầu sai thì `return` khỏi handler mà không ném exception. Ví dụ dùng một model chỉ ra một món đồ:

```csharp
using Fomoxa;

namespace MyGame.Network.Models
{
    [Network]
    [Codec("net")]
    public class ItemRequest
    {
        [Network("u32")]
        [Codec("net")]
        public uint ItemId { get; set; }
    }
}
```

Server giữ số lượng của từng món đồ người chơi có và kiểm tra yêu cầu với số đó:

```csharp
using System.Collections.Generic;
using Fomoxa.Networking;
using Fomoxa.Unity;
using MyGame.Network.Models;

public sealed partial class Inventory : NetworkBehaviour
{
    private readonly Dictionary<uint, int> counts = new Dictionary<uint, int>();

    [ServerRpc]
    private void UseItem(ulong peerId, ItemRequest request)
    {
        if (!counts.TryGetValue(request.ItemId, out int count) || count == 0)
        {
            return;
        }

        counts[request.ItemId] = count - 1;
    }
}
```

Nếu truy cập dictionary bằng `counts[request.ItemId]` trước phép kiểm tra, một id do client tự bịa ra sẽ làm nó ném `KeyNotFoundException`, và exception đó sẽ ngắt kết nối client.

Package đã bỏ các message tới object không tồn tại và các message không decode được, nên handler chỉ nhận model đúng định dạng cho object còn sống, nhưng giá trị bên trong model là thứ client đã gửi.

## Trang liên quan <a href="#related-pages" id="related-pages"></a>

- Event kết nối của [server](../connections/server.md) và [client](../connections/client.md)
- [RPC](../messaging/rpc.md#errors-in-handlers)
- [Xác thực](../connections/authentication.md)
- [Debug](../advanced/debugging.md)
