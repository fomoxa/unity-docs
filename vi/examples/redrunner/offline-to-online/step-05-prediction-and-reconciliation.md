# Bước 05: Prediction và reconciliation

## Mục tiêu <a href="#goal" id="goal"></a>

Sau bước này, nhân vật của owner di chuyển ngay trong frame phím được bấm. Client áp dụng input của chính nó ngay, so sánh kết quả với kết quả của server sau mỗi tick và tự sửa khi chúng khác nhau. Camera và nền đi theo nhân vật cục bộ, và nhân vật của người chơi khác có animation trong lúc server di chuyển chúng.

## Điểm xuất phát <a href="#starting-point" id="starting-point"></a>

Sau bước 04, `PlayerInput`, `Gather`, `Apply` và `RedCharacter.Simulate` đã tồn tại, và server chạy `Apply` tại tick của mỗi input.

## Vấn đề <a href="#problem" id="problem"></a>

Nếu client chỉ gửi input rồi chờ, mỗi lần bấm phím sẽ hiện ra chậm một vòng round trip, nên client phải tự chạy `Apply` ngay trong tick nó thu thập input.

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
Owner's client                        Server
Gather (tick T)
  ↓
Apply (prediction) ── input T ──→     Apply (tick T)
  ↓                                     ↓
Capture → history[T]                  Capture
  ↓                                     ↓
render at once           ←── motion T ──┘
  ↓
Matches(server T, history[T])?
  yes → nothing
  no  → restore 2D physics to T
        Restore(server motion)
        Apply T+1 … now (Replaying = true)
```

Thứ client so sánh là một model thứ hai, `PlayerMotion`, giữ vị trí, vận tốc và vận tốc damping khi chạy. `NetworkPlayer` đăng ký nó bằng `input.Reconcile` với ba callback, `Capture`, `Restore` và `Matches`.

Nhân vật là một `Rigidbody2D`, và scene có các body khác mà nhân vật chạm vào. Khi bật Simulate Physics, package lưu physics 2D của scene sau mỗi tick và khôi phục nó trước khi replay, nên lần replay bắt đầu từ đúng world mà server đã có.

Các client khác không dự đoán nhân vật này. Chúng thấy nó qua `NetworkTransform`, dưới dạng một body kinematic được interpolate chậm hai tick so với vị trí mới nhất chúng đã nhận.

## File <a href="#files" id="files"></a>

```
Assets/Scripts/RedRunner/Networking/Models/PlayerMotion.cs
Assets/Scripts/RedRunner/Networking/NetworkPlayer.cs
Assets/Scripts/RedRunner/Networking/NetworkGame.cs
Assets/Scripts/RedRunner/Characters/RedCharacter.cs
```

## Hiện thực <a href="#implementation" id="implementation"></a>

### Thêm motion model <a href="#add-the-motion-model" id="add-the-motion-model"></a>

```csharp
using Fomoxa;

namespace RedRunner.Networking.Models
{
    [Network]
    [Codec("net")]
    public class PlayerMotion
    {
        [Network("f32")]
        [Codec("net")]
        public float X { get; set; }

        [Network("f32")]
        [Codec("net")]
        public float Y { get; set; }

        [Network("f32")]
        [Codec("net")]
        public float VelocityX { get; set; }

        [Network("f32")]
        [Codec("net")]
        public float VelocityY { get; set; }

        [Network("f32")]
        [Codec("net")]
        public float RunSmoothVelocity { get; set; }
    }
}
```

`RunSmoothVelocity` nằm trong model vì `Mathf.SmoothDamp` mang vận tốc của nó từ tick này sang tick sau. Nếu thiếu, lần replay sẽ bắt đầu tăng tốc từ một giá trị khác với server, và bị trôi. `RedCharacter` cung cấp field này dưới dạng property `RunSmoothVelocity` cho mục đích đó.

### Chụp, khôi phục và so sánh <a href="#capture-restore-and-compare" id="capture-restore-and-compare"></a>

```csharp
private const float PositionTolerance = 0.01f;
private const float VelocityTolerance = 0.05f;

private void Capture(PlayerMotion motion)
{
    BodyState2D state = NetworkObject.Body2D.State;
    motion.X = state.Position.X;
    motion.Y = state.Position.Y;
    motion.VelocityX = state.Velocity.X;
    motion.VelocityY = state.Velocity.Y;
    motion.RunSmoothVelocity = m_Character.RunSmoothVelocity;
}

private void Restore(PlayerMotion motion)
{
    PhysicsBody2D body = NetworkObject.Body2D;
    BodyState2D state = body.State;
    state.Position = new System.Numerics.Vector2(motion.X, motion.Y);
    state.Velocity = new System.Numerics.Vector2(motion.VelocityX, motion.VelocityY);
    body.State = state;
    m_Character.RunSmoothVelocity = motion.RunSmoothVelocity;
}

private static bool Matches(PlayerMotion server, PlayerMotion predicted) =>
    Math.Abs(server.X - predicted.X) <= PositionTolerance
    && Math.Abs(server.Y - predicted.Y) <= PositionTolerance
    && Math.Abs(server.VelocityX - predicted.VelocityX) <= VelocityTolerance
    && Math.Abs(server.VelocityY - predicted.VelocityY) <= VelocityTolerance
    && Math.Abs(server.RunSmoothVelocity - predicted.RunSmoothVelocity) <= VelocityTolerance;
```

`NetworkObject.Body2D` là cách package nhìn vào `Rigidbody2D` của nhân vật, với vị trí và vận tốc `System.Numerics.Vector2`. Dung sai có thể nhỏ vì server và client chạy cùng physics trên cùng các khối.

Trong lúc replay, `InputContext.Replaying` là true, và `Apply` từ bước 04 truyền `!context.Replaying` làm `effects`, nên một cú nhảy được replay thay đổi vận tốc mà không phát lại âm thanh, particle hay trigger lần thứ hai.

Fomoxa giữ lịch sử, so sánh đúng tick, khôi phục physics world và replay, còn game quyết định thế nào là cùng kết quả và chấp nhận chênh lệch tới đâu.

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

Xem [`7799601`](https://github.com/fomoxa/RedRunner/commit/7799601188dced2c0c67d27a452d50f8bf7c7566) trên GitHub, rồi tiếp tục với [bước 06: chết và hồi sinh](step-06-death-and-respawn.md).
