# Mô hình networking

## Server và peer <a href="#server-and-peers" id="server-and-peers"></a>

Một game có một server và số client bất kỳ. Server sở hữu game state và quyết định điều gì xảy ra, còn client gửi yêu cầu và input rồi hiển thị những gì server gửi về. Host là một server và một client chạy trong cùng một tiến trình.

Server cấp cho mỗi client đã kết nối một peer id, một số `ulong` không bao giờ bằng 0, vì peer id 0 nghĩa là "không có peer". Do đó object có owner 0 thuộc về server. Client chỉ có một bên ở xa là server, nên các event mang peer id đều báo 0 trên client.

## Message là model <a href="#messages-are-models" id="messages-are-models"></a>

Mọi thứ package gửi đi đều là model, tức một class C# đánh dấu bằng `[Network]` và `[Codec]` có codec do `fomoxac` sinh ra. Điều này đúng với message của chính package, như message spawn, despawn, state và transform, cũng như với tham số RPC, state và input của game.

Mỗi cặp model và codec có một message id, và `NetSchema` sinh ra liệt kê mọi message id cùng fingerprint layout của nó. Trong lúc handshake, Fomoxa.Net so sánh schema của client với của server và từ chối kết nối bằng `HandshakeFailure.SchemaConflict` nếu chúng không khớp, nên client và server phải được build từ cùng các model. [Model và codec](../messaging/models.md) hướng dẫn cách khai báo chúng.

## Ba loại message <a href="#three-kinds-of-message" id="three-kinds-of-message"></a>

| Loại | Gửi tới | Ví dụ | Hướng dẫn |
|---|---|---|---|
| System message | Package ở phía bên kia | Spawn, despawn, đổi owner, clock ping, acknowledgement | Không dùng trực tiếp |
| Object message | Một `NetworkBehaviour` của một `NetworkObject` | RPC, state, cập nhật transform, input | [RPC](../messaging/rpc.md), [State](../synchronization/state.md) |
| Plain message | Handler đăng ký cho message id của nó | Message của game gửi bằng `ClientManager.Send` | [Raw message](../messaging/messages.md) |

Object message mang một header 5 byte đứng trước model, gồm object id 4 byte và behaviour index 1 byte của component đích.

## Channel <a href="#channels" id="channels"></a>

Mỗi message id có một channel. Mặc định là `Unreliable`, nghĩa là message có thể bị mất hoặc tới sai thứ tự so với các message khác. Message `ReliableOrdered` tới đúng một lần, theo thứ tự gửi so với mọi message reliable khác của cùng kết nối. Nó mang một sequence number 2 byte, bên nhận gửi acknowledgement, và bên gửi tiếp tục gửi lại cho tới khi nhận được acknowledgement.

Model khai báo channel của nó bằng `[NetworkChannel]`, như mô tả trong [channel và độ tin cậy](../messaging/channels.md).

## Send queue và bundle <a href="#send-queue-and-bundles" id="send-queue-and-bundles"></a>

Lệnh gửi không ghi ra mạng ngay. Nó thêm message vào send queue của kết nối và trả về một `SendResult`, rồi `NetworkManager` flush các queue sau đó: mỗi tick một lần ở timing mode Tick, hoặc mỗi frame một lần vào cuối frame ở timing mode Variable.

Khi flush, các message trong queue được đóng vào bundle. Mỗi bundle là một frame của transport và chứa nhiều message nhất có thể trong frame budget của transport, tức 1200 byte với UDP và frame Fomoxa lớn nhất với TCP và WebSocket. Nhờ vậy nhiều message nhỏ đi chung trong một datagram.

Queue của mỗi kết nối có giới hạn, đặt trên `NetworkManager`:

| Field | Mặc định | Ý nghĩa |
|---|---|---|
| Message Capacity | 1024 | Số message chờ trong một queue |
| Byte Capacity | 1 MiB | Số byte chờ trong một queue |
| Reliable Window | 1024 | Số message reliable đã gửi mà chưa được acknowledge |

Lệnh gửi nào vượt một trong hai giới hạn đầu sẽ không được đưa vào queue và trả về `SendResult.Full` hoặc `SendResult.BytesFull`. Các object message của chính package, như spawn, được miễn hai giới hạn này. Message reliable vượt quá window sẽ chờ trong queue cho tới khi acknowledgement tới.

## Kết nối <a href="#connections" id="connections"></a>

Một kết nối đi qua ba trạng thái, do `ConnectionState` báo:

```text
Stopped → Starting → Started → Stopped
```

`Starting` bao gồm việc kết nối transport và handshake Fomoxa, còn `Started` nghĩa là hai bên đã thống nhất schema và message đang truyền. Bản thân server có trạng thái riêng, `ServerState`, đi từ `Stopped` qua `Starting`, `Started` và `Stopping` rồi về `Stopped`.

Fomoxa.Net theo dõi mọi kết nối để phát hiện im lặng. Khi không có gì tới trong Heartbeat Interval Seconds (mặc định 5), nó gửi một probe, và khi probe không được trả lời trong Heartbeat Timeout Seconds (mặc định 15), kết nối dừng với `StopReason.Timeout`. Với giá trị mặc định, client biến mất mà không đóng kết nối, như một tiến trình bị crash, sẽ bị gỡ khoảng 20 giây sau message cuối cùng của nó. Client dừng bình thường thì gửi message rời đi trước, và server gỡ nó ngay.

[Kiến trúc](architecture.md) cho thấy các tầng mà message đi qua, [tick và thời gian](tick.md) giải thích khi nào chúng được nhận và gửi, [vòng đời](lifecycle.md) đưa ra thứ tự các sự kiện kết nối, và [lỗi và lý do dừng](../reference/errors.md) liệt kê mọi cách một kết nối có thể dừng.
