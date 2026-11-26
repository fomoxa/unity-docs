# Tổng quan prediction

Client-side prediction cho owner của một object áp dụng input của chính mình ngay, thay vì chờ một vòng round trip tới server. Server áp dụng cùng input đó khi nó tới và gửi kết quả về, và client tự sửa nếu hai kết quả khác nhau. [Prediction](../concepts/prediction.md) giải thích ý tưởng, còn trang này xây từng bước một nhân vật được dự đoán.

## Yêu cầu <a href="#requirements" id="requirements"></a>

`NetworkManager` phải dùng Timing Mode Tick, và object cần một `NetworkBehaviour` có field `[NetworkInput]` và field `[NetworkReconcile]`. Object cũng cần có owner, vì chỉ client sở hữu mới dự đoán và server chỉ chấp nhận input của object từ owner.

## Một nhân vật được dự đoán <a href="#a-predicted-character" id="a-predicted-character"></a>

Behaviour giữ input của một tick trong các field `[NetworkInput]`, và state mà client so sánh với state của server sau mỗi tick trong các field `[NetworkReconcile]`:

```csharp
using Fomoxa.Networking;
using Fomoxa.Unity;
using UnityEngine;

public sealed partial class PredictedMover : NetworkBehaviour
{
    [SerializeField] private float speed = 5f;

    [NetworkInput]
    private float x;

    [NetworkInput]
    private float z;

    [NetworkReconcile(Tolerance = 0.01f)]
    private Vector3 position;

    protected override void OnGatherInput()
    {
        x = Input.GetAxisRaw("Horizontal");
        z = Input.GetAxisRaw("Vertical");
    }

    protected override void OnApplyInput(InputContext context)
    {
        Vector3 direction = Vector3.ClampMagnitude(new Vector3(x, 0f, z), 1f);
        transform.position += direction * speed * (float)NetworkManager.TimeManager.TickDelta;
    }

    protected override void OnCaptureState()
    {
        position = transform.position;
    }

    protected override void OnRestoreState()
    {
        transform.position = position;
    }
}
```

Class phải là `partial`. Package gom các field input vào một model tên `PredictedMoverInput` và các field reconcile vào `PredictedMoverReconcile`, cả hai trong thư mục con `StateModels` của Generated Folder, và mang chúng bên trong các message của riêng nó. `Tolerance` cho mỗi thành phần của `position` lệch tối đa 0.01 trước khi client tự sửa.

`NetworkManager` là manager đã spawn object, nên `OnApplyInput` đọc độ dài tick từ đúng manager, kể cả khi scene có nhiều manager. Ví dụ đọc Input Manager cũ; với package Input System, hãy đọc input action của bạn trong `OnGatherInput`.

Đặt `NetworkObject`, `NetworkTransform` và `PredictedMover` lên prefab người chơi, và spawn nó với peer id của người chơi làm owner.

## Mỗi tick diễn ra gì <a href="#what-happens-each-tick" id="what-happens-each-tick"></a>

| Ai | Làm gì |
|---|---|
| Client của owner | Gọi `OnGatherInput` cho prediction tick của nó, chép các field input và gửi chúng cùng các input trước đó. Khi đã dự đoán, nó còn gọi `OnApplyInput` và ghi lại các field reconcile sau `OnCaptureState`. Nó bắt đầu dự đoán khi state đầu tiên từ server tới. |
| Server | Khi tick của nó tới tick của input, ghi input đó vào các field input và gọi `OnApplyInput`, rồi `OnCaptureState`, và gửi các field reconcile tới owner. |
| Client của owner | Khi state của server cho một tick tới, so sánh nó với bản ghi của tick đó, từng field trong phạm vi `Tolerance`. Nếu không khớp, nó ghi state của server vào các field reconcile, gọi `OnRestoreState`, và gọi lại `OnApplyInput` cho mọi tick sau đó mà nó có input. |
| Client khác | Không làm gì với input. Chúng thấy object qua `NetworkTransform`. |

## Kết quả mong đợi <a href="#expected-result" id="expected-result"></a>

- Nhân vật của owner di chuyển ngay trong frame phím được bấm.
- Client khác thấy nó di chuyển, hơi chậm về quá khứ.
- `ReconcileCount` của `PredictedMover` trên owner giữ quanh 0 khi nhân vật di chuyển tự do.

## Đọc tiếp <a href="#where-to-go-next" id="where-to-go-next"></a>

| Chủ đề | Trang |
|---|---|
| Thu thập, gửi, lặp lại và bỏ input | [Input](input.md) |
| Chụp, khôi phục, so sánh và replay | [Reconciliation](reconciliation.md) |
| Nhân vật di chuyển bằng physics | [Rollback với physics](rollback.md) |
| Làm mượt các lần sửa trên màn hình | [NetworkTransform](../synchronization/transform.md#prediction) |

## Host mode <a href="#host-mode" id="host-mode"></a>

Host không dự đoán object của chính nó. Server thu thập và áp dụng input của host trực tiếp trong cùng tick, nên không có gì cần sửa, còn các client ở xa của host vẫn dự đoán bình thường.
