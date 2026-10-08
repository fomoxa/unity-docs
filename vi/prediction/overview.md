# Tổng quan prediction

Client-side prediction cho owner của một object áp dụng input của chính mình ngay, thay vì chờ một vòng round trip tới server. Server áp dụng cùng input đó khi nó tới và gửi kết quả về, và client tự sửa nếu hai kết quả khác nhau. [Prediction](../concepts/prediction.md) giải thích ý tưởng, còn trang này xây từng bước một nhân vật được dự đoán.

## Yêu cầu <a href="#requirements" id="requirements"></a>

`NetworkManager` phải dùng Timing Mode Tick, và object cần một `NetworkBehaviour` đăng ký input model và reconcile model trong `OnRegisterInput`. Object cũng cần có owner, vì chỉ client sở hữu mới dự đoán và server chỉ chấp nhận input của object từ owner.

## Một nhân vật được dự đoán <a href="#a-predicted-character" id="a-predicted-character"></a>

Nhân vật cần hai model. Model đầu tiên mang input của một tick:

```csharp
using Fomoxa;

namespace MyGame.Network.Models
{
    [Network]
    [Codec("net")]
    public class MoveInput
    {
        [Network("f32")]
        [Codec("net")]
        public float X { get; set; }

        [Network("f32")]
        [Codec("net")]
        public float Z { get; set; }
    }
}
```

Model thứ hai giữ state mà client so sánh với state của server sau mỗi tick:

```csharp
using Fomoxa;
using UnityEngine;

namespace MyGame.Network.Models
{
    [Network]
    [Codec("net")]
    public class MoveState
    {
        [Network("Vector3")]
        [Codec("net")]
        public Vector3 Position { get; set; }
    }
}
```

Cả hai model đều không cần `[NetworkChannel]`, vì package mang input và reconcile state bên trong các message của riêng nó.

Behaviour nối chúng lại với nhau:

```csharp
using Fomoxa.Networking;
using Fomoxa.Unity;
using Generated;
using MyGame.Network.Models;
using UnityEngine;

public sealed class PredictedMover : NetworkBehaviour
{
    private const float Tolerance = 0.01f;

    [SerializeField] private float speed = 5f;

    private NetworkManager manager;

    private void Awake()
    {
        manager = FindFirstObjectByType<NetworkManager>();
    }

    protected override void OnRegisterInput(NetworkInput input)
    {
        input.Use(MoveInputNetAdapter.Instance, Gather, Apply);
        input.Reconcile(MoveStateNetAdapter.Instance, Capture, Restore, Matches);
    }

    private void Gather(MoveInput input)
    {
        input.X = Input.GetAxisRaw("Horizontal");
        input.Z = Input.GetAxisRaw("Vertical");
    }

    private void Apply(MoveInput input, InputContext context)
    {
        Vector3 direction = Vector3.ClampMagnitude(new Vector3(input.X, 0f, input.Z), 1f);
        transform.position += direction * speed * (float)manager.TimeManager.TickDelta;
    }

    private void Capture(MoveState state)
    {
        state.Position = transform.position;
    }

    private void Restore(MoveState state)
    {
        transform.position = state.Position;
    }

    private static bool Matches(MoveState server, MoveState predicted) =>
        Vector3.Distance(server.Position, predicted.Position) <= Tolerance;
}
```

Ví dụ đọc Input Manager cũ; với package Input System, hãy đọc input action của bạn trong `Gather`.

Đặt `NetworkObject`, `NetworkTransform` và `PredictedMover` lên prefab người chơi, và spawn nó với peer id của người chơi làm owner.

## Mỗi tick diễn ra gì <a href="#what-happens-each-tick" id="what-happens-each-tick"></a>

| Ai | Làm gì |
|---|---|
| Client của owner | Gọi `Gather` cho prediction tick của nó và gửi input cùng các input trước đó. Khi đã dự đoán, nó còn gọi `Apply` với input đó và ghi lại state từ `Capture`. Nó bắt đầu dự đoán khi state đầu tiên từ server tới. |
| Server | Khi tick của nó tới tick của input, gọi `Apply` với input đó, rồi `Capture`, và gửi state đã chụp tới owner. |
| Client của owner | Khi state của server cho một tick tới, so sánh nó với bản ghi của tick đó bằng `Matches`. Nếu không khớp, nó gọi `Restore` với state của server và gọi lại `Apply` cho mọi tick sau đó mà nó có input. |
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
