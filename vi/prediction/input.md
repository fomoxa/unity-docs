# Input

Field input mang những gì người chơi của owner đã làm trong một tick. Package thu thập chúng trên client của owner mỗi tick và gửi tới server kèm số tick. `OnApplyInput` của bạn chạy với chúng trên server khi tick ấy tới, và chạy ngay trên client của owner nếu client đang dự đoán.

## Khai báo <a href="#declaring" id="declaring"></a>

```csharp
using Fomoxa.Networking;
using Fomoxa.Unity;
using UnityEngine;

public sealed partial class Walker : NetworkBehaviour
{
    [NetworkInput]
    private float x;

    [NetworkInput]
    private float z;

    protected override void OnGatherInput()
    {
        x = Input.GetAxisRaw("Horizontal");
        z = Input.GetAxisRaw("Vertical");
    }

    protected override void OnApplyInput(InputContext context)
    {
        transform.position += new Vector3(x, 0f, z) * 0.1f;
    }
}
```

Field input là một field instance không phải `readonly`, và có thể là private. Type của field quyết định cách nó được gửi, như với [field state](../synchronization/state.md#state-fields), còn `[NetworkInput("...")]` cho nó một wire type. Behaviour có field input phải override cả `OnGatherInput` lẫn `OnApplyInput`, và class phải là `partial`.

Package gom các field input của một class, kể cả của các class cha, vào một model mang tên class theo sau là `Input`, ở đây là `WalkerInput`, trong thư mục con `StateModels` của Generated Folder. Đặt tên khác cho model bằng `[NetworkInputModel("...")]` trên class. Như với state, Play mode và build bị chặn chừng nào model còn thiếu hoặc cũ, và thêm một field sau field cuối cùng vẫn giữ được kết nối với bản build cũ, như trang [state](../synchronization/state.md#changing-the-fields) giải thích. Khi `NetworkManager` dùng timing mode Variable, object ném `HandlerRegistrationException` lúc spawn.

Không có [field `[NetworkReconcile]`](reconciliation.md), owner chỉ gửi input mà không dự đoán, nên object di chuyển khi kết quả của server tới, như mọi object khác.

## Gather <a href="#gather" id="gather"></a>

`OnGatherInput` chạy mỗi tick một lần trên client của owner, cho `TimeManager.PredictionTick`, khi client đang kết nối tới server ở xa và đồng hồ đã đồng bộ. Trên host nó chạy trên server, cho các object mà client của host sở hữu. Sau khi nó trả về, package chép các field input. Lần replay ghi các input cũ hơn vào cùng các field đó, nên hãy đặt mọi field input mỗi lần.

Input xảy ra giữa các tick, như một nút được bấm trong một frame, được bắt trong `Update` và chuyển sang trong `OnGatherInput`. Ví dụ sau thêm một field input `jump` vào `PredictedMover` từ trang [tổng quan](overview.md):

```csharp
[NetworkInput]
private bool jump;

private bool jumpPressed;

private void Update()
{
    if (NetworkObject != null && NetworkObject.IsOwner && Input.GetButtonDown("Jump"))
    {
        jumpPressed = true;
    }
}

protected override void OnGatherInput()
{
    x = Input.GetAxisRaw("Horizontal");
    z = Input.GetAxisRaw("Vertical");
    jump = jumpPressed;
    jumpPressed = false;
}
```

## Apply <a href="#apply" id="apply"></a>

Trước mỗi lần gọi `OnApplyInput`, package ghi input của tick đó vào các field input. `OnApplyInput` chạy trong bốn tình huống:

| Ở đâu | Khi nào | `context.Replaying` |
|---|---|---|
| Server | Mỗi tick, với object có owner, bằng input của tick đó | false |
| Client của owner, khi đang dự đoán | Ngay sau `OnGatherInput` | false |
| Client của owner, trong lúc reconciliation | Lại một lần cho mỗi tick sau tick được sửa | true |
| Host | Mỗi tick, với input vừa thu thập của host | false |

Server không gọi `OnApplyInput` cho object do chính nó sở hữu, cũng không gọi trước khi input đầu tiên từ owner tới.

`InputContext` cho `OnApplyInput` biết thêm về input trong các field:

| Property | Ý nghĩa |
|---|---|
| `Tick` | Tick mà input này dành cho |
| `Repeated` | Server hoặc lần replay không có input cho tick này và dùng lại input cuối |
| `RepeatedTicks` | Khi `Repeated`, số tick đã qua kể từ tick của input đang được dùng lại |
| `Replaying` | Lời gọi là một phần của lần replay trên client của owner |

`Replaying` cho phép bỏ qua các hiệu ứng đã hiển thị, như âm thanh và particle, còn `Repeated` cho phép tránh lặp lại các hành động một lần:

```csharp
protected override void OnApplyInput(InputContext context)
{
    Move(x, z, (float)manager.TimeManager.TickDelta);
    if (jump && !context.Repeated)
    {
        Jump(playEffects: !context.Replaying);
    }
}
```

Exception ném ra trong `OnApplyInput` hoặc `OnGatherInput` được log và không ngắt kết nối ai.

## Gửi <a href="#sending" id="sending"></a>

Mỗi tick, client của owner gửi một input message unreliable cho mỗi behaviour. Message chứa input mới nhất cùng các input trước đó, tổng cộng Input Redundancy input (mặc định 3), nên một gói bị mất không làm mất input.

<figure><img src="../.gitbook/assets/diagrams/input-redundancy.svg" alt="Client của owner gửi một input message mỗi tick. Message của tick 22 mang input 22, 21 và 20, message của tick 23 mang 23, 22 và 21, và message của tick 24 mang 24, 23 và 22. Message của tick 23 bị mất, nhưng input 23 vẫn tới server trong message của tick 24."><figcaption><p>Với Input Redundancy mặc định là 3, mất một message không làm mất input nào.</p></figcaption></figure>

## Trên server <a href="#on-the-server" id="on-the-server"></a>

Server giữ các input nhận được theo object và behaviour, sắp theo tick. Nó chấp nhận input cho các tick từ tick hiện tại của nó tới tối đa Max Input Lead tick phía trước (mặc định 30). Message có input mới nhất dành cho một tick đã qua, hoặc xa hơn giới hạn đó, sẽ bị bỏ và được đếm trong `ServerManager.DroppedInputsOf(peerId)`.

Ở mỗi tick, server áp dụng input của tick đó, và nếu không có input nào tới kịp, nó áp dụng lại input cuối với `Repeated` được đặt. Input từ peer không sở hữu object bị bỏ, và server log `Fomoxa dropped input to object <id> from peer <id>, which does not own the object`. Khi owner thay đổi hoặc object bị despawn, input đã đệm bị xóa.

Client cố gắng để mỗi input tới sớm Input Buffer tick (mặc định 2) trước khi server cần nó, như mô tả ở mục [đồng bộ đồng hồ](../concepts/tick.md#clock-synchronization).

## Kiểm tra input <a href="#validating-input" id="validating-input"></a>

Server áp dụng bất cứ gì owner gửi lên, nên hãy kẹp hoặc từ chối giá trị trong `OnApplyInput`, ví dụ bằng `Vector3.ClampMagnitude` trên một hướng, để một client bị sửa đổi không thể di chuyển nhanh hơn mức cho phép. Vì cùng `OnApplyInput` chạy trên client của owner, một client trung thực sẽ dự đoán ra đúng kết quả đã kẹp.

Input làm việc cùng [reconciliation](reconciliation.md) và đồng hồ tick mô tả trong [tick và thời gian](../concepts/tick.md). [NetworkBehaviour](../objects/network-behaviour.md) liệt kê các method mà một behaviour override.
