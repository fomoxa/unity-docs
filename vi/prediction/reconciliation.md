# Reconciliation

Reconciliation là cách client của owner sửa lại dự đoán của mình. Sau khi áp dụng một input, server chụp state của object và gửi nó tới owner kèm số tick. Client so sánh nó với state đã dự đoán cho cùng tick, và nếu hai bên khác nhau, nó khôi phục state của server rồi replay input cho mọi tick sau đó.

## Đăng ký <a href="#registering" id="registering"></a>

Reconcile model được đăng ký sau input model:

```csharp
protected override void OnRegisterInput(NetworkInput input)
{
    input.Use(MoveInputNetAdapter.Instance, Gather, Apply);
    input.Reconcile(MoveStateNetAdapter.Instance, Capture, Restore, Matches);
}
```

`NetworkInput.Reconcile<TState>(codec, capture, restore, matches = null)` nhận ba callback:

| Callback | Chạy khi | Làm gì |
|---|---|---|
| `capture(TState state)` | Sau mỗi input được áp dụng trên server; sau mỗi tick được dự đoán hoặc replay trên client | Copy state của behaviour vào model |
| `restore(TState state)` | Trên client, khi bắt đầu một lần sửa | Copy state của server ngược vào behaviour |
| `matches(TState server, TState predicted)` | Trên client, cho mỗi state tới | Trả về dự đoán có đủ gần hay không |

`Reconcile` ném `HandlerRegistrationException` khi được gọi trước `Use` hoặc bị gọi hai lần.

## Reconcile model chứa gì <a href="#what-goes-in-the-reconcile-model" id="what-goes-in-the-reconcile-model"></a>

Reconcile model phải giữ mọi thứ mà `apply` đọc, thay đổi và mang từ tick này sang tick sau, như vị trí, vận tốc, bộ đếm cooldown hay vận tốc damping. Nếu thiếu thứ gì, lần replay bắt đầu từ một giá trị khác với server, và lần so sánh tiếp theo lại thất bại.

## So sánh <a href="#comparing" id="comparing"></a>

Không có `matches`, package so sánh các byte đã encode của hai state, nên mọi khác biệt đều tính là mismatch, kể cả nhiễu số thực ở bit cuối. Với số thực, hãy truyền một hàm `matches` có dung sai:

```csharp
private static bool Matches(MoveState server, MoveState predicted) =>
    Vector3.Distance(server.Position, predicted.Position) <= 0.01f;
```

## Sửa và replay <a href="#correction-and-replay" id="correction-and-replay"></a>

```text
predicted   T10  T11  T12  T13  T14       client is at T14
                  ↑
            server state for T11 arrives, does not match

restore(server state of T11)
replay      T12  T13  T14                 apply(input, Replaying = true), capture each
```

Client giữ input và state của Prediction History tick gần nhất (mặc định 64). Một lần replay bao các tick từ tick được sửa tới tick dự đoán mới nhất, dùng các input client đã ghi lại, và sau lần sửa package gọi `OnReconciled(tick)` trên behaviour và tăng `ReconcileCount` của nó.

Khi nhiều state tới giữa hai tick, client chỉ xử lý state mới nhất. State cho một tick mà client không có dự đoán được tính là mismatch.

Trong lúc replay, `NetworkBehaviour.IsReplaying` và `ClientManager.IsReplaying` là true, và `InputContext.Replaying` trong `apply` cũng vậy.

## Bắt đầu và dừng dự đoán <a href="#starting-and-stopping-prediction" id="starting-and-stopping-prediction"></a>

Client của owner bắt đầu dự đoán khi reconcile state đầu tiên từ server tới, và trước đó nó chỉ gửi input.

Khi object mất owner hoặc đổi owner, owner cũ thôi dự đoán nó, xóa lịch sử và quay về đi theo `NetworkTransform`. Owner mới bắt đầu dự đoán khi server đã gửi cho nó một state.

## Server gửi thường xuyên tới mức nào <a href="#how-often-the-server-sends" id="how-often-the-server-sends"></a>

Server gửi state sau mỗi Reconcile Interval tick (mặc định 1), cho các tick mà nó đã áp dụng input. Khoảng lớn hơn tiết kiệm băng thông, và các lần sửa trở nên thưa hơn nhưng lớn hơn.

## Hiển thị lần sửa mượt mà <a href="#showing-corrections-smoothly" id="showing-corrections-smoothly"></a>

Một lần sửa di chuyển object ngay lập tức. Để che điều đó, hãy gán một object con chứa các phần hiển thị vào field Visual của `NetworkTransform` trên object. Package khi đó giữ object con ở chỗ nó đang hiện trên màn hình rồi đưa nó về dần trong Smoothing Time, như mô tả trong [NetworkTransform](../synchronization/transform.md#prediction).

## Chẩn đoán việc sửa thường xuyên <a href="#diagnosing-frequent-corrections" id="diagnosing-frequent-corrections"></a>

`ReconcileCount` nên giữ ở mức thấp chừng nào không có gì bất thường xảy ra. Khi nó cứ tăng, nguyên nhân thường gặp là:

- `apply` dùng `Time.deltaTime` thay vì `TimeManager.TickDelta`.
- `apply` đọc dữ liệu khác nhau giữa server và client, như object khác hoặc số ngẫu nhiên không có seed.
- Reconcile model thiếu state được mang qua các tick.
- `matches` bị thiếu hoặc quá chặt.
- Input tới server muộn và bị lặp lại, điều mà `ServerManager.DroppedInputsOf` cho thấy.

[Mô phỏng tất định](../concepts/deterministic-simulation.md) giải thích vì sao mỗi nguyên nhân trên làm hai bên khác nhau.

## Với physics <a href="#with-physics" id="with-physics"></a>

Khi object di chuyển bằng `Rigidbody` hoặc `Rigidbody2D` và Simulate Physics đang bật, một lần sửa còn rollback cả các physics world, như mô tả trong [rollback với physics](rollback.md).

Reconciliation xây trên [input](input.md), và [tổng quan prediction](overview.md) cho thấy cả hai trong một nhân vật hoàn chỉnh. [NetworkBehaviour](../core/network-behaviour.md) liệt kê `OnReconciled` và các callback khác.
