# Character controller

Backend Rapier di chuyển một body kinematic theo cách của character controller: trượt dọc tường, leo bậc và dốc tới một giới hạn, bám mặt đất và có thể đẩy body dynamic. Nó thay cho `CharacterController` của Unity, thứ backend không hỗ trợ. Lần di chuyển là một phần của mô phỏng, nên server và client dự đoán tính giống nhau và replay lặp lại đúng như vậy.

## Chuẩn bị body <a href="#setting-up-the-body" id="setting-up-the-body"></a>

Nhân vật là một network object có `Rigidbody` hoặc `Rigidbody2D` kinematic và đúng một collider không phải trigger: hộp, cầu hoặc viên nang ở 3D, hộp, hình tròn hoặc viên nang ở 2D. Body đó có thể có thêm trigger collider. Lần di chuyển không xoay body.

## Di chuyển <a href="#moving" id="moving"></a>

Gọi `MoveCharacter` trong `apply`, mỗi tick một lần, với độ dời mong muốn của tick đó:

```csharp
using Fomoxa.Networking;
using Fomoxa.Networking.Rapier;
using Fomoxa.Unity;
using Fomoxa.Unity.Rapier;
using UnityEngine;

public sealed class Walker : NetworkBehaviour
{
    [SerializeField] private NetworkManager manager;
    [SerializeField] private RapierPhysics rapier;
    [SerializeField] private float speed = 4f;
    [SerializeField] private float fallSpeed = 6f;

    private static readonly CharacterSettings2D Settings = default(CharacterSettings2D)
        .WithAutostep(new CharacterAutostep(CharacterLength.Absolute(0.3f), CharacterLength.Absolute(0.2f), true));

    private bool grounded;

    private void Apply(MoveInput input, InputContext context)
    {
        float seconds = (float)manager.TimeManager.TickDelta;
        var desired = new System.Numerics.Vector2(input.X * speed, -fallSpeed) * seconds;
        CharacterMove2D move = rapier.Scenes.MoveCharacter(NetworkObject, NetworkObject.Body2D, desired, seconds, Settings);
        grounded = move.Grounded;
    }
}
```

`MoveInput` đại diện cho model input của game, đăng ký trong `OnRegisterInput` như ở trang [input](../prediction/input.md); `manager` và `rapier` là `NetworkManager` và `RapierPhysics` của nó. Cho gọn, ví dụ rơi với tốc độ không đổi; game thường giữ vận tốc theo phương đứng trong state được dự đoán. Lời gọi tính body đi được bao xa và đặt chỗ đó làm vị trí kinematic kế tiếp, nên body tới đó trong bước mô phỏng của cùng tick và `Transform` theo sau. Gọi lần nữa trước bước mô phỏng thì độ dời được tính lại từ vị trí cũ và thay lần đầu.

Kết quả cho biết chuyện gì đã xảy ra:

| Member | Ý nghĩa |
|---|---|
| `Moved` | Độ dời đã áp dụng, sau khi tính tường, bậc và dốc |
| `Grounded` | Cuối lần dời, nhân vật đứng trên một thứ gì đó |
| `Sliding` | Lần dời đi xuống và nhân vật đứng trên dốc nghiêng hơn `MinSlopeSlideAngle` |

`RapierScenes.MoveCharacter(INetworkEntity owner, PhysicsBody body, Vector3 desired, float seconds, in CharacterSettings settings)` và overload `PhysicsBody2D` kiểm tra `body` thuộc `owner`. Body không network object nào sở hữu thì di chuyển qua world của nó, `rapier.Scenes.WorldOf2D(sceneId).MoveCharacter(body.Handle, desired, seconds, settings)`. Cả hai đều có overload nhận thêm `QueryFilter` ở cuối. Console server gọi cùng các hàm với `StandaloneEntity` của nó.

## Lần dời va chạm với gì <a href="#what-the-move-collides-with" id="what-the-move-collides-with"></a>

- Trigger collider không bao giờ chặn nhân vật.
- Ma trận va chạm layer áp dụng giữa layer của collider nhân vật và layer của các collider khác.
- `QueryFilter` thu hẹp thêm bằng `LayerMask` và `ExcludeBody` của nó. `IncludeTriggers` không được dùng.
- [Platform effector](effectors.md#platform) một chiều cho nhân vật đi xuyên từ dưới lên và giữ nó lại khi từ trên xuống.

## Thiết lập <a href="#settings" id="settings"></a>

`default(CharacterSettings)` và `CharacterSettings.Default` cho mặc định của Rapier. Mỗi hàm `With` trả về một bản sao với một thay đổi:

| Thiết lập | Mặc định | Ý nghĩa |
|---|---|---|
| `WithUp(up)` | (0, 1, 0) | Hướng lên, dùng cho dốc, bậc và mặt đất |
| `WithOffset(length)` | 1% chiều cao của nhân vật | Khe hở nhỏ giữ giữa nhân vật và thứ nó chạm |
| `WithSlide(bool)` | bật | Trượt dọc vật cản thay vì dừng lại |
| `WithAutostep(CharacterAutostep?)` | không có | Leo bậc tới một chiều cao tối đa, với bề rộng sàn trống tối thiểu ở trên; `CharacterAutostep.Default` là một phần tư chiều cao và một nửa bề rộng của nhân vật, và tính cả body dynamic |
| `WithSlopeAngles(maxClimb, minSlide)` | 45°, 45° | Dốc nghiêng nhất mà nhân vật leo được, và từ góc nào nó bắt đầu trượt xuống |
| `WithSnapToGround(CharacterLength?)` | 20% chiều cao của nhân vật | Giữ nhân vật trên mặt đất khi đi qua đỉnh dốc hoặc xuống bậc; `null` thì tắt |
| `WithNormalNudgeFactor(float)` | 0.0001 | Nhân vật được đẩy ra khỏi bề mặt bao xa để không bị kẹt |
| `WithPushMass(float)` | 0 | Lớn hơn 0 thì body dynamic bị lần dời chạm vào nhận xung lực như thể nhân vật có khối lượng này |

Góc tính theo radian. `CharacterLength.Absolute(meters)` là độ dài theo đơn vị của world, còn `CharacterLength.Relative(fraction)` là một phần của collider nhân vật: của chiều cao theo hướng lên, hoặc của bề rộng vuông góc với nó với bề rộng bậc tối thiểu. `CharacterSettings2D` có cùng các member, với hướng lên kiểu `Vector2`.

## Tính tất định <a href="#determinism" id="determinism"></a>

Cùng chuỗi lời gọi trên cùng world cho cùng kết quả, và replay sau `Load` lặp lại đúng từng bit. Server và client không có cùng world, vì client đặt các object khác làm proxy, nên một lần dời có thể lệch giữa hai bên như mọi phần dự đoán khác. Client sửa lại ở lần reconcile kế tiếp.

Lần dời chạm body kinematic phụ thuộc vận tốc của body đó, mà Rapier suy ra từ vị trí kế tiếp của nó. Body kinematic vừa tạo chưa có vận tốc cho tới bước mô phỏng đầu tiên, nên lần dời trước bước đó có thể khác cùng lần dời sau nó.
