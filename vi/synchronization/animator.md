# NetworkAnimator

`NetworkAnimator` replicate một `Animator` từ server tới mọi observer. Nó gửi parameter, trigger, tốc độ và trọng số của các layer, và khi một observer thấy object lần đầu, gửi cả state mà mỗi layer đang ở.

## Khi nào dùng <a href="#when-to-use-it" id="when-to-use-it"></a>

Dùng nó khi server điều khiển animation, ví dụ với nhân vật do server di chuyển. Nếu mỗi client có thể tự suy ra animation từ dữ liệu nó đã có, như vận tốc của một transform được interpolate, thì đặt parameter cục bộ rẻ hơn vì không tốn băng thông.

## Cách dùng cơ bản <a href="#basic-usage" id="basic-usage"></a>

1. Thêm `NetworkAnimator` vào GameObject có `Animator`. Component này cần một `Animator` và tự thêm nếu chưa có.
2. Trên server, đặt parameter trên `Animator` như bình thường.
3. Kích hoạt trigger qua `NetworkAnimator.SetTrigger`, không phải `Animator.SetTrigger`:

```csharp
GetComponent<NetworkAnimator>().SetTrigger("Jump");
```

## Cách hoạt động <a href="#how-it-works" id="how-it-works"></a>

`NetworkAnimator` là một `NetworkBehaviour` có state model `AnimatorState` đi qua cơ chế [state](state.md). Sau mỗi tick, server đọc `Animator`:

| Dữ liệu | Đọc bằng |
|---|---|
| Parameter float | `GetFloat`, làm tròn tới bội số của Float Step |
| Parameter int và bool | `GetInteger`, `GetBool` |
| Trigger | Một bộ đếm cho mỗi trigger, tăng bởi `NetworkAnimator.SetTrigger` |
| Tốc độ | `Animator.speed` |
| Trọng số layer | `GetLayerWeight` cho mọi layer sau layer đầu tiên |
| State của layer | `GetCurrentAnimatorStateInfo(layer).fullPathHash` |

Nếu có gì thay đổi, server gửi state mới. Làm tròn các giá trị float giúp những thay đổi rất nhỏ không tạo ra message ở mỗi tick.

## Hành vi trên client <a href="#client-behavior" id="client-behavior"></a>

Ở mỗi bản cập nhật, client đặt parameter, tốc độ và trọng số layer, và kích hoạt mỗi trigger đúng số lần bộ đếm của nó đã tăng. Khi object xuất hiện lần đầu trên client, client còn phát state hiện tại của mỗi layer, để observer vào muộn không bắt đầu từ entry state. State của layer chỉ được áp dụng vào thời điểm đó; sau đó `Animator` của chính client chuyển giữa các state dựa trên các parameter được replicate.

## Controller phải khớp <a href="#matching-controllers" id="matching-controllers"></a>

Server và client phải dùng cùng layout Animator Controller, nghĩa là cùng các parameter theo cùng thứ tự với cùng type, và cùng số layer. Component tính một hash layout và gửi nó kèm state, và khi hai hash khác nhau, client không áp dụng state và log thông báo sau một lần:

`Fomoxa: <name> received Animator state with layout 0x..., but its Animator has layout 0x...; the Animator controllers differ between server and client, so the state is not applied`

## Cấu hình <a href="#configuration" id="configuration"></a>

| Field | Mặc định | Ý nghĩa |
|---|---|---|
| Animator | component trên cùng GameObject | `Animator` cần replicate |
| Float Step | 0.01 | Giá trị float được làm tròn tới bội số của số này; 0 thì gửi không làm tròn |

## Giới hạn <a href="#limitations" id="limitations"></a>

Animation chỉ đi từ server tới client. Trigger phải đi qua `NetworkAnimator.SetTrigger`, method ném `ArgumentException` với tên không phải trigger parameter của controller, vì gọi trực tiếp `Animator.SetTrigger` trên server sẽ không được replicate. State của layer được áp dụng khi object xuất hiện, không liên tục. Trên host, `Animator` của server là cái được hiển thị, và không có gì được áp dụng lần thứ hai.

`NetworkAnimator` dựa trên [state](state.md), và [tham chiếu component](../reference/components.md#networkanimator) liệt kê các member của nó.
