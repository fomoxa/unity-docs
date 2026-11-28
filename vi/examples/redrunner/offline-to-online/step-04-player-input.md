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
OnGatherInput: read the keys into the input fields
  ↓
Fomoxa input frames
  ↓
Server, at the input's tick
  ↓
OnApplyInput: RedCharacter.Simulate with the tick length
```

Ba điều khiến controller offline không chạy được trên server:

- Nó đọc bàn phím của tiến trình nó đang chạy, và server không có người chơi ngồi trước bàn phím.
- Nó chạy theo frame với thời gian frame, trong khi server tick 50 lần mỗi giây độc lập với frame. Ở bước 05, client còn phải chạy lại cùng bước đó cho các tick nó đã hiển thị.
- Nó phát âm thanh, particle và trigger animator ngay giữa phần physics, và một tick được replay không được phát chúng hai lần.

## Khái niệm Fomoxa <a href="#fomoxa-concepts" id="fomoxa-concepts"></a>

- [Input](../../../prediction/input.md)
- [Authority](../../../concepts/authority.md#what-a-client-can-send)
- [Tick và thời gian](../../../concepts/tick.md)
- [Khai báo trên NetworkBehaviour](../../../objects/network-behaviour.md#declarations)

## Thiết kế <a href="#design" id="design"></a>

Input của một tick là ba input field của `NetworkPlayer`: trục ngang và hai nút. Package gom chúng vào một model, `PlayerInput`, và gọi hai method của `NetworkPlayer`:

| Method | Chạy trên | Làm gì |
|---|---|---|
| `OnGatherInput` | Client của owner, mỗi tick một lần | Ghi các input field từ các phím |
| `OnApplyInput` | Server tại tick của input, và client của owner khi nó dự đoán | Đọc các input field và gọi `RedCharacter.Simulate` |

`RedCharacter.Simulate` là bước tick. Nó nhận trục, các nút, độ dài tick và việc có phát hiệu ứng hay không. Client chỉ gửi input, còn server quyết định nhân vật kết thúc ở đâu.

## File <a href="#files" id="files"></a>

```
Assets/Scripts/RedRunner/Characters/RedCharacter.cs
Assets/Scripts/RedRunner/Utilities/GroundCheck.cs
Assets/Scripts/RedRunner/Networking/NetworkPlayer.cs
```

## Hiện thực <a href="#implementation" id="implementation"></a>

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

`NetworkPlayer` trở thành `partial` và đặt tên cho input model của nó, như `NetworkLevel` đặt tên cho state model ở bước 02:

```csharp
[RequireComponent(typeof(RedCharacter))]
[NetworkInputModel("PlayerInput")]
public sealed partial class NetworkPlayer : NetworkBehaviour
```

Nửa phần input của class, viết cho `com.fomoxa.networking` 0.6.0:

```csharp
[NetworkInput]
private float move;

[NetworkInput]
private bool jump;

[NetworkInput]
private bool roll;

private void Update()
{
    if (NetworkObject == null || !NetworkObject.IsOwner)
    {
        return;
    }

    m_JumpPressed |= CrossPlatformInputManager.GetButtonDown("Jump");
    m_RollPressed |= CrossPlatformInputManager.GetButtonDown("Roll");
}

protected override void OnGatherInput()
{
    bool playing = GameManager.Singleton.gameRunning;
    move = playing ? CrossPlatformInputManager.GetAxis("Horizontal") : 0f;
    jump = playing && m_JumpPressed;
    roll = playing && m_RollPressed;
    m_JumpPressed = false;
    m_RollPressed = false;
}

protected override void OnApplyInput(InputContext context)
{
    float tickDelta = (float)NetworkManager.TimeManager.TickDelta;
    bool fresh = !context.Repeated;
    m_Character.Simulate(move, fresh && jump, fresh && roll, tickDelta, !context.Replaying);
}
```

Sau `OnGatherInput`, package copy ba field vào một `PlayerInput` và gửi nó đi. Trước `OnApplyInput`, nó copy input của tick trở lại các field, nên `OnApplyInput` đọc `move`, `jump` và `roll` và không bao giờ chạm vào model. Model sinh ra, `Networking/Generated/StateModels/PlayerInput.cs`, không có channel, vì package mang input trong các input frame của riêng mình.

`Update` chạy mỗi frame và giữ các lần bấm nút cho tới `OnGatherInput` tiếp theo, nên một lần bấm ngắn hơn một tick không bị mất. Khi màn hình tạm dừng đang mở, `gameRunning` là false và input trống, nên nhân vật dừng lại trong khi server và người chơi khác vẫn tiếp tục.

Trên server, `OnApplyInput` chạy tại tick mà input thuộc về. Khi không có input nào tới cho một tick, package lặp lại input cuối và đặt `InputContext.Repeated`, và bản port khi đó chỉ lặp lại trục di chuyển, không bao giờ lặp lại nhảy hay lăn. `InputContext.Replaying` được dùng ở bước 05. `OnApplyInput` đọc độ dài tick từ `NetworkManager`, manager đã spawn object, có giá trị trong mọi callback mạng nhưng chưa có trong `Awake`. `NetworkPlayer.Awake` giờ lấy `RedCharacter` và tìm `NetworkGame` một lần, nên `m_Game` được gán trên mọi instance, kể cả instance của owner.

Các reconcile field của bước 05 được viết trong cùng commit.

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

Xem [`7799601`](https://github.com/fomoxa/RedRunner/commit/7799601188dced2c0c67d27a452d50f8bf7c7566) trên GitHub. Commit đó khai báo `PlayerInput` bằng tay với API 0.3, và [`1c1ded1`](https://github.com/fomoxa/RedRunner/commit/1c1ded158105091902d8d352157856eacf0cbc73) chuyển nó sang các field.

Tiếp tục với [bước 05: prediction và reconciliation](step-05-prediction-and-reconciliation.md).
