# Bước 04: Input của người chơi

## Mục tiêu <a href="#goal" id="goal"></a>

Sau bước này, mỗi client gửi phím của người chơi tới server mỗi tick một lần, và server di chuyển nhân vật theo đó. Để làm được vậy, chuyển động của nhân vật trở thành một bước tick mà cả server và client đều chạy được.

## Điểm xuất phát <a href="#starting-point" id="starting-point"></a>

Sau bước 03, server spawn một nhân vật cho mỗi client, và mỗi client biết nhân vật nào là của mình. Vì `RedCharacter.Update` không còn đọc bàn phím, chưa có gì di chuyển.

## Vấn đề <a href="#problem" id="problem"></a>

```
Offline:
RedCharacter.Update (every frame)
  ↓
reads CrossPlatformInputManager
  ↓
Move, Jump, roll force with Time.deltaTime
```

```
Online:
Owner's client, every tick
  ↓
Gather: read the keys into PlayerInput
  ↓
Fomoxa input frames
  ↓
Server, at the input's tick
  ↓
Apply: RedCharacter.Simulate with the tick length
```

Ba điều khiến controller offline không chạy được trên server:

* Nó đọc bàn phím của tiến trình nó đang chạy, và server không có người chơi ngồi trước bàn phím.
* Nó chạy theo frame với thời gian frame, trong khi server tick 50 lần mỗi giây độc lập với frame. Ở bước 05, client còn phải chạy lại cùng bước đó cho các tick nó đã hiển thị.
* Nó phát âm thanh, particle và trigger animator ngay giữa phần physics, và một tick được replay không được phát chúng hai lần.

## Khái niệm Fomoxa <a href="#fomoxa-concepts" id="fomoxa-concepts"></a>

* [Input](../../../prediction/input.md)
* [Authority](../../../khai-niem/authority.md#what-a-client-can-send)
* [Tick và thời gian](../../../khai-niem/tick.md)
* [Hook đăng ký của NetworkBehaviour](../../../core/network-behaviour.md#registration-hooks)

## Thiết kế <a href="#design" id="design"></a>

Input của một tick là một model, `PlayerInput`, giữ trục ngang và hai nút. `NetworkPlayer` đăng ký nó trong `OnRegisterInput` với hai callback:

| Callback | Chạy trên                                                     | Làm gì                         |
| -------- | ------------------------------------------------------------- | ------------------------------ |
| `Gather` | Client của owner, mỗi tick một lần                            | Điền `PlayerInput` từ các phím |
| `Apply`  | Server tại tick của input, và client của owner khi nó dự đoán | Gọi `RedCharacter.Simulate`    |

`RedCharacter.Simulate` là bước tick. Nó nhận trục, các nút, độ dài tick và việc có phát hiệu ứng hay không. Client chỉ gửi input, còn server quyết định nhân vật kết thúc ở đâu.

## File <a href="#files" id="files"></a>

```
Assets/Scripts/RedRunner/Networking/Models/PlayerInput.cs
Assets/Scripts/RedRunner/Characters/RedCharacter.cs
Assets/Scripts/RedRunner/Utilities/GroundCheck.cs
Assets/Scripts/RedRunner/Networking/NetworkPlayer.cs
```

## Hiện thực <a href="#implementation" id="implementation"></a>

### Thêm input model <a href="#add-the-input-model" id="add-the-input-model"></a>

```csharp
using Fomoxa;

namespace RedRunner.Networking.Models
{
    [Network]
    [Codec("net")]
    public class PlayerInput
    {
        [Network("f32")]
        [Codec("net")]
        public float Move { get; set; }

        [Network("bool")]
        [Codec("net")]
        public bool Jump { get; set; }

        [Network("bool")]
        [Codec("net")]
        public bool Roll { get; set; }
    }
}
```

Input model không cần `[NetworkChannel]`, vì package mang nó trong các input frame của riêng mình. Lưu file và để bộ sinh code ghi `PlayerInputNetAdapter` trước khi viết `NetworkPlayer`.

### Biến controller thành một bước tick <a href="#turn-the-controller-into-a-tick-step" id="turn-the-controller-into-a-tick-step"></a>

```csharp
public virtual void Simulate ( float horizontalAxis, bool jump, bool roll, float deltaTime, bool effects )
{
	float speed = Mathf.Abs ( m_Rigidbody2D.linearVelocity.x );
	m_CurrentRunSpeed = m_RunSpeed;
	if ( speed >= m_RunSpeed )
	{
		m_CurrentRunSpeed = Mathf.SmoothDamp ( speed, m_MaxRunSpeed, ref m_CurrentSmoothVelocity, m_RunSmoothTime, Mathf.Infinity, deltaTime );
	}
	Move ( horizontalAxis );
	if ( jump )
	{
		Jump ( effects );
	}
	if ( roll )
	{
		Roll ( effects );
	}
}
```

`Update` offline gọi `Mathf.SmoothDamp` không có tham số thời gian, nên nó dùng thời gian frame, còn `Simulate` truyền độ dài tick.

`Jump ( bool effects )` chỉ phát trigger animator, particle và âm thanh khi `effects` là true. Nó cũng kiểm tra mặt đất ngay tại thời điểm chạy:

Trước:

```csharp
if ( m_GroundCheck.IsGrounded )
```

Sau:

```csharp
if ( m_GroundCheck.Check () )
```

`IsGrounded` chỉ được cập nhật mỗi frame một lần, nhưng trong lúc replay nhân vật ở một vị trí cũ hơn, nên phép kiểm tra phải chạy ngay lúc đó. `GroundCheck.Update` giờ cũng gọi `Check ()`.

Lăn trở thành `Roll ( bool effects )`. Code offline đẩy theo `localScale.z`, luôn bằng 1, nên nhân vật luôn lăn sang phải. Bản port đẩy theo `localScale.x`, hướng nhân vật đang quay mặt:

```csharp
m_Rigidbody2D.AddForce ( new Vector2 ( Mathf.Sign ( transform.localScale.x ) * m_RollForce, 0f ) );
```

### Gather và apply <a href="#gather-and-apply" id="gather-and-apply"></a>

Nửa phần input của `NetworkPlayer`, như đã commit:

```csharp
protected override void OnRegisterInput(NetworkInput input)
{
    input.Use(PlayerInputNetAdapter.Instance, Gather, Apply);
    input.Reconcile(PlayerMotionNetAdapter.Instance, Capture, Restore, Matches);
}

private void Update()
{
    if (NetworkObject == null || !NetworkObject.IsOwner)
    {
        return;
    }

    m_JumpPressed |= CrossPlatformInputManager.GetButtonDown("Jump");
    m_RollPressed |= CrossPlatformInputManager.GetButtonDown("Roll");
}

private void Gather(PlayerInput input)
{
    bool playing = GameManager.Singleton.gameRunning;
    input.Move = playing ? CrossPlatformInputManager.GetAxis("Horizontal") : 0f;
    input.Jump = playing && m_JumpPressed;
    input.Roll = playing && m_RollPressed;
    m_JumpPressed = false;
    m_RollPressed = false;
}

private void Apply(PlayerInput input, InputContext context)
{
    float tickDelta = (float)m_Game.Manager.TimeManager.TickDelta;
    bool fresh = !context.Repeated;
    m_Character.Simulate(input.Move, fresh && input.Jump, fresh && input.Roll, tickDelta, !context.Replaying);
}
```

`Update` chạy mỗi frame và giữ các lần bấm nút cho tới `Gather` tiếp theo, nên một lần bấm ngắn hơn một tick không bị mất. Khi màn hình tạm dừng đang mở, `gameRunning` là false và input trống, nên nhân vật dừng lại trong khi server và người chơi khác vẫn tiếp tục.

Trên server, `Apply` chạy tại tick mà input thuộc về. Khi không có input nào tới cho một tick, package lặp lại input cuối và đặt `InputContext.Repeated`, và bản port khi đó chỉ lặp lại trục di chuyển, không bao giờ lặp lại nhảy hay lăn. `InputContext.Replaying` được dùng ở bước 05. `NetworkPlayer.Awake` giờ lấy `RedCharacter` và tìm `NetworkGame` một lần, nên `m_Game` được gán trên mọi instance chứ không chỉ trên instance của owner.

Dòng `Reconcile` và ba callback của nó thuộc bước 05, dù chúng được viết trong cùng commit.

Fomoxa thu thập, đánh số, gửi, đệm và lặp lại input, và gọi `Apply` đúng tick. Game quyết định input chứa gì và một tick di chuyển làm gì.

## Test <a href="#test" id="test"></a>

Bước này và bước 05 được làm trong một commit, và bản port chỉ được test một lần, sau cả hai. Hãy test ở cuối [bước 05](step-05-prediction-and-reconciliation.md#test).

## Kết quả mong đợi <a href="#expected-result" id="expected-result"></a>

Kết quả mong đợi được mô tả trong [bước 05](step-05-prediction-and-reconciliation.md#expected-result).

## Commit <a href="#commit" id="commit"></a>

Bước này không có commit riêng. Phần việc của nó nằm trong:

```
Commit: 7799601
Message: Predict the local character and send input through the network
```

Xem [`7799601`](https://github.com/fomoxa/RedRunner/commit/7799601188dced2c0c67d27a452d50f8bf7c7566) trên GitHub, rồi tiếp tục với [bước 05: prediction và reconciliation](step-05-prediction-and-reconciliation.md).
