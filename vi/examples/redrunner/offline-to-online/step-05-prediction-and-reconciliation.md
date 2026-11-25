# Bước 05: Prediction và reconciliation

## Mục tiêu <a href="#goal" id="goal"></a>

Sau bước này, nhân vật của owner di chuyển ngay trong frame phím được bấm. Client áp dụng input của chính nó ngay, so sánh kết quả với kết quả của server sau mỗi tick và tự sửa khi chúng khác nhau. Camera và nền đi theo nhân vật cục bộ, và nhân vật của người chơi khác có animation trong lúc server di chuyển chúng.

## Điểm xuất phát <a href="#starting-point" id="starting-point"></a>

Sau bước 04, các input field, `OnGatherInput`, `OnApplyInput` và `RedCharacter.Simulate` đã tồn tại, và server chạy `OnApplyInput` tại tick của mỗi input.

## Vấn đề <a href="#problem" id="problem"></a>

Nếu client chỉ gửi input rồi chờ, mỗi lần bấm phím sẽ hiện ra chậm một vòng round trip, nên client phải tự chạy `OnApplyInput` ngay trong tick nó thu thập input.

Kết quả của client sau đó có thể lệch khỏi kết quả của server, ví dụ khi một gói tới muộn một tick và server lặp lại input trước đó, hoặc khi hai physics engine làm tròn khác nhau. Client cần phát hiện độ lệch và quay về kết quả của server mà không mất các input đã áp dụng kể từ đó.

## Khái niệm Fomoxa <a href="#fomoxa-concepts" id="fomoxa-concepts"></a>

- [Prediction](../../../concepts/prediction.md)
- [Tổng quan prediction](../../../prediction/overview.md)
- [Reconciliation](../../../prediction/reconciliation.md)
- [Rollback với physics](../../../prediction/rollback.md)
- [PhysicsBody2D](../../../physics/physics-body.md#physicsbody2d)
- [Ba số tick](../../../concepts/tick.md#three-tick-numbers)

## Thiết kế <a href="#design" id="design"></a>

```
Owner's client                               Server
OnGatherInput (tick T)
  ↓
OnApplyInput (prediction) ── input T ──→     OnApplyInput (tick T)
  ↓                                            ↓
OnCaptureState → history[T]                  OnCaptureState
  ↓                                            ↓
render at once                  ←── motion T ──┘
  ↓
server T within Tolerance of history[T]?
  yes → nothing
  no  → restore 2D physics to T
        server motion → fields, OnRestoreState
        OnApplyInput T+1 … now (Replaying = true)
```

Thứ client so sánh là một nhóm field thứ hai của `NetworkPlayer`, đánh dấu `[NetworkReconcile]`, giữ vị trí, vận tốc và vận tốc damping khi chạy. Package gom chúng vào model `PlayerMotion`. `OnCaptureState` copy body vào các field, `OnRestoreState` copy các field trở lại body, và `Tolerance` của từng field quyết định giá trị của server và giá trị dự đoán có khớp nhau hay không.

Nhân vật là một `Rigidbody2D`, và scene có các body khác mà nhân vật chạm vào. Khi bật Simulate Physics trên `RigidbodyPhysics` của `Network Manager`, package lưu physics 2D của scene sau mỗi tick và khôi phục nó trước khi replay, nên lần replay bắt đầu từ đúng world mà server đã có.

Các client khác không dự đoán nhân vật này. Chúng thấy nó qua `NetworkTransform`, dưới dạng một body kinematic được interpolate chậm hai tick so với vị trí mới nhất chúng đã nhận.

## File <a href="#files" id="files"></a>

```
Assets/Scripts/RedRunner/Networking/NetworkPlayer.cs
Assets/Scripts/RedRunner/Networking/NetworkGame.cs
Assets/Scripts/RedRunner/Characters/RedCharacter.cs
```

## Hiện thực <a href="#implementation" id="implementation"></a>

### Chụp, khôi phục và so sánh <a href="#capture-restore-and-compare" id="capture-restore-and-compare"></a>

Class đặt tên cho reconcile model cạnh input model của nó:

```csharp
[RequireComponent(typeof(RedCharacter))]
[NetworkInputModel("PlayerInput")]
[NetworkReconcileModel("PlayerMotion")]
public sealed partial class NetworkPlayer : NetworkBehaviour
```

Nửa phần reconcile của class:

```csharp
private const float PositionTolerance = 0.01f;
private const float VelocityTolerance = 0.05f;

[NetworkReconcile(Tolerance = PositionTolerance)]
private float x;

[NetworkReconcile(Tolerance = PositionTolerance)]
private float y;

[NetworkReconcile(Tolerance = VelocityTolerance)]
private float velocityX;

[NetworkReconcile(Tolerance = VelocityTolerance)]
private float velocityY;

[NetworkReconcile(Tolerance = VelocityTolerance)]
private float runSmoothVelocity;

protected override void OnCaptureState()
{
    BodyState2D state = NetworkObject.Body2D.State;
    x = state.Position.X;
    y = state.Position.Y;
    velocityX = state.Velocity.X;
    velocityY = state.Velocity.Y;
    runSmoothVelocity = m_Character.RunSmoothVelocity;
}

protected override void OnRestoreState()
{
    PhysicsBody2D body = NetworkObject.Body2D;
    BodyState2D state = body.State;
    state.Position = new System.Numerics.Vector2(x, y);
    state.Velocity = new System.Numerics.Vector2(velocityX, velocityY);
    body.State = state;
    m_Character.RunSmoothVelocity = runSmoothVelocity;
}
```

Package gọi `OnCaptureState` trước khi copy các field vào một `PlayerMotion`, và gọi `OnRestoreState` sau khi đã copy `PlayerMotion` của server vào các field. Hai state khớp nhau khi mọi field nằm trong `Tolerance` của nó so với giá trị của server; với `float`, đó là hiệu tuyệt đối.

`runSmoothVelocity` là một reconcile field vì `Mathf.SmoothDamp` mang vận tốc của nó từ tick này sang tick sau. Nếu thiếu, lần replay sẽ bắt đầu tăng tốc từ một giá trị khác với server, và bị trôi. `RedCharacter` cung cấp giá trị này dưới dạng property `RunSmoothVelocity` cho mục đích đó.

`NetworkObject.Body2D` là cách package nhìn vào `Rigidbody2D` của nhân vật, với vị trí và vận tốc `System.Numerics.Vector2`. Dung sai có thể nhỏ vì server và client chạy cùng physics trên cùng các khối.

Trong lúc replay, `InputContext.Replaying` là true, và `OnApplyInput` từ bước 04 truyền `!context.Replaying` làm `effects`, nên một cú nhảy được replay thay đổi vận tốc mà không phát lại âm thanh, particle hay trigger lần thứ hai.

### Đi theo người chơi cục bộ <a href="#follow-the-local-player" id="follow-the-local-player"></a>

`NetworkGame.SetLocalPlayer` giờ hướng camera và nền vào nhân vật của owner:

```csharp
internal void SetLocalPlayer(NetworkPlayer player)
{
    LocalPlayer = player;
    if (CameraController.Singleton != null)
    {
        CameraController.Singleton.Follow(player != null ? player.transform : null);
    }

    if (TerrainGenerator.Singleton != null)
    {
        TerrainGenerator.Singleton.Follow(player != null ? player.Character : null);
    }
    LocalPlayerChanged?.Invoke(player);
}
```

### Animation cho nhân vật bạn không điều khiển <a href="#animate-characters-you-do-not-control" id="animate-characters-you-do-not-control"></a>

`RedCharacter.LateUpdate` lấy dữ liệu cho animator từ vận tốc của `Rigidbody2D`. Trên client, nhân vật của người chơi khác là kinematic và được `NetworkTransform` di chuyển, nên vận tốc đó bằng 0 và nhân vật sẽ trượt đi trong tư thế đứng yên. Với body kinematic, vận tốc giờ được tính từ quãng đường đã đi kể từ frame trước:

```csharp
Vector2 velocity = m_Rigidbody2D.linearVelocity;
if ( m_Rigidbody2D.bodyType == RigidbodyType2D.Kinematic && Time.deltaTime > 0f )
{
	velocity = ( transform.position - m_LastPosition ) / Time.deltaTime;
}
m_LastPosition = transform.position;
```

Bước 08 thêm một giới hạn cho phép tính này để xử lý hồi sinh.

## Test <a href="#test" id="test"></a>

Kết nối tới một server rồi bấm các phím mũi tên và Space.

Bài kiểm tra riêng của bản port là `Tools/PortChecks/MoveCheck.cs`. Nó kết nối tới một tiến trình server qua màn hình bắt đầu và điều khiển các trục ảo của `CrossPlatformInputManager` với hai giây sang phải, một cú nhảy và một giây sang trái.

## Kết quả mong đợi <a href="#expected-result" id="expected-result"></a>

- Nhân vật chạy và nhảy mà không phải chờ server.
- Camera và nền đi theo nó.
- Các client khác thấy nó chạy, hơi chậm về quá khứ.

`MoveCheck` đạt khi client dự đoán nhân vật của mình, nhân vật chạy được ít nhất 5 đơn vị, lên cao ít nhất 1.5 đơn vị và quay đầu, và camera cùng nền đi theo nó. Trong một lần chạy, nhân vật di chuyển 9.65 đơn vị và nhảy cao 4.77 đơn vị, và sáu giây chạy nhảy cần một lần sửa.

## Commit <a href="#commit" id="commit"></a>

```
Commit: 7799601
Message: Predict the local character and send input through the network
```

Xem [`7799601`](https://github.com/fomoxa/RedRunner/commit/7799601188dced2c0c67d27a452d50f8bf7c7566) trên GitHub. Commit đó khai báo `PlayerMotion` bằng tay với API 0.3 và so sánh nó trong một method `Matches`, còn [`1c1ded1`](https://github.com/fomoxa/RedRunner/commit/1c1ded158105091902d8d352157856eacf0cbc73) chuyển nó sang các field, mỗi field có một `Tolerance`.

Tiếp tục với [bước 06: chết và hồi sinh](step-06-death-and-respawn.md).
