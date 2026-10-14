# Bước 06: Chết và hồi sinh

## Mục tiêu <a href="#goal" id="goal"></a>

Sau bước này, chỉ server quyết định một nhân vật chết. Client hiển thị cái chết và việc hồi sinh từ state của server, nhân vật hồi sinh ở điểm bắt đầu hai giây sau, và người chơi tới khối kết thúc sẽ quay về điểm bắt đầu. Đồng xu vẫn nằm trên từng client, và điểm số bị bỏ.

## Điểm xuất phát <a href="#starting-point" id="starting-point"></a>

Sau bước 05, mọi nhân vật đều di chuyển, của owner bằng prediction và của người khác bằng interpolation. Tuy vậy kẻ địch vẫn giết từ các collision callback của chúng trong mọi tiến trình, và màn hình kết thúc cùng điểm số offline vẫn còn.

## Vấn đề <a href="#problem" id="problem"></a>

```
Offline:
Saw.OnCollisionEnter2D
  ↓
character.Die (true)
  ↓
GameManager: score, end screen, Reset
```

Khi online, cùng một va chạm xảy ra trong nhiều tiến trình, và chúng không thống nhất với nhau. Client của owner dự đoán nhân vật, nên nếu server thấy cú nhảy sớm hơn một tick, nhân vật trên client có thể chạm vào một lưỡi cưa mà nhân vật trên server đã vượt qua. Các client khác thấy nhân vật chậm hai tick về quá khứ, nên va chạm của chúng tới muộn. Chỉ va chạm trên server khớp với vị trí authoritative.

Nếu mọi tiến trình đều chạy `Die`, một client có thể hiển thị một cái chết chưa từng xảy ra. Hồi sinh thêm một vấn đề thứ hai, vì nhân vật nhảy từ chỗ chết về điểm bắt đầu trong một tick, và cả interpolation lẫn prediction đều coi cú nhảy như vậy là chuyển động thông thường trừ khi được báo khác.

Cuối cùng, điểm số và màn hình kết thúc offline giả định có một nhân vật chính và một lượt chạy có kết thúc, và game online không có cả hai.

## Khái niệm Fomoxa <a href="#fomoxa-concepts" id="fomoxa-concepts"></a>

- [Authority](../../../concepts/authority.md#what-only-the-server-does)
- [State](../../../synchronization/state.md)
- [Tick event](../../../concepts/tick.md#tick-events)
- [Teleport với NetworkTransform](../../../synchronization/transform.md#teleporting)
- [Teleport một PhysicsBody](../../../physics/physics-body.md#teleporting)
- [Reconciliation](../../../prediction/reconciliation.md#correction-and-replay)

## Thiết kế <a href="#design" id="design"></a>

```
Server, after each tick (TimeManager.OnTick)
  ↓
collision already called Die? fell below y = 0?
  ↓ yes
PlayerState { Dead = true, Cause }
  ↓ 100 ticks later
Respawn: Reset, body to spawn point, NetworkTransform.Teleport
PlayerState { Dead = false }
        │
        │ state
        ↓
Client: ShowState
  Dead  → character.Die(cause): skeleton, blood, splash
  !Dead → character.Reset()
Owner's client: the jump in position is a prediction mismatch → correction
Other clients: the teleport clears the interpolation buffer
```

Hai cờ trên `Character` quyết định ai hành động:

| Cờ | Server | Client của owner | Client khác |
|---|---|---|---|
| `DecidesDeath` | true | false | false |
| `CollectsItems` | false | true | false |

Ở host mode, server đặt cả hai cờ trước rồi client của owner bật `CollectsItems`, nên nhân vật của chính host làm cả hai việc.

Sau bước này, công việc được chia như sau:

| Client | Server |
|---|---|
| Input | Cái chết và nguyên nhân |
| Dự đoán nhân vật của mình | Thời điểm và vị trí hồi sinh |
| Hiệu ứng chết, hiển thị từ state | Tới khối kết thúc |
| Đồng xu và rương, cho nhân vật của mình | |

## File <a href="#files" id="files"></a>

```
Assets/Scripts/RedRunner/Characters/DeathCause.cs
Assets/Scripts/RedRunner/Characters/Character.cs
Assets/Scripts/RedRunner/Characters/RedCharacter.cs
Assets/Scripts/RedRunner/Enemies/Saw.cs
Assets/Scripts/RedRunner/Enemies/Spike.cs
Assets/Scripts/RedRunner/Enemies/Water.cs
Assets/Scripts/RedRunner/Enemies/Mace.cs
Assets/Scripts/RedRunner/Collectables/Coin.cs
Assets/Scripts/RedRunner/Collectables/Chest.cs
Assets/Scripts/RedRunner/GameManager.cs
Assets/Scripts/RedRunner/Utilities/CameraController.cs
Assets/Scripts/RedRunner/UI/UIScreen/StartScreen.cs
Assets/Scripts/RedRunner/Networking/Models/PlayerState.cs
Assets/Scripts/RedRunner/Networking/NetworkPlayer.cs
Assets/Scenes/Play.unity
```

## Hiện thực <a href="#implementation" id="implementation"></a>

### Đặt tên cho nguyên nhân cái chết <a href="#name-the-cause-of-a-death" id="name-the-cause-of-a-death"></a>

Client cần biết nguyên nhân cái chết để hiển thị đúng hiệu ứng. `DeathCause` là một enum với `Fall`, `Saw`, `Spike`, `Water` và `Mace`, `Character.Die ( bool blood )` trở thành `Die ( DeathCause cause )`, và `Character` có thêm ba property:

```csharp
public virtual DeathCause DeathCause { get; protected set; }

public virtual bool DecidesDeath { get; set; } = true;

public virtual bool CollectsItems { get; set; } = true;
```

Cả hai cờ mặc định là true, khớp với hành vi offline.

`RedCharacter.Die ( DeathCause cause )` giờ tự phát mọi hiệu ứng của cái chết: máu với lưỡi cưa, gai và chùy, âm thanh gai với gai và chùy, và tiếng bắn nước với nước. Trước đây kẻ địch giết nhân vật phát một phần trong số này. Khi mọi hiệu ứng nằm trong `Die`, cùng một lời gọi hiển thị cái chết trên server và trên client. Cú di chuyển nhanh của camera chỉ áp dụng khi camera đi theo nhân vật này, và phép kiểm tra rơi chuyển từ `RedCharacter.Update` sang server.

### Chỉ server được giết <a href="#let-only-the-server-kill" id="let-only-the-server-kill"></a>

Mỗi kẻ địch giờ kiểm tra `DecidesDeath` và truyền nguyên nhân của nó:

Trước:

```csharp
if (character != null) {
	Kill (character);
}
```

Sau:

```csharp
if (character != null && character.DecidesDeath) {
	Kill (character);
}
```

Ví dụ trên là `Saw`, và `Spike`, `Water`, `Mace` có cùng phép kiểm tra.

### Giữ cái chết trong một state <a href="#keep-the-death-in-a-state" id="keep-the-death-in-a-state"></a>

```csharp
using Fomoxa;
using Fomoxa.Networking;

namespace RedRunner.Networking.Models
{
    [Network]
    [Codec("net")]
    [NetworkChannel("net", Channel.ReliableOrdered)]
    public class PlayerState
    {
        [Network("bool")]
        [Codec("net")]
        public bool Dead { get; set; }

        [Network("u8")]
        [Codec("net")]
        public byte Cause { get; set; }
    }
}
```

`NetworkPlayer` đăng ký state này cạnh input của nó và đặt các cờ khi nhân vật khởi động:

```csharp
protected override void OnRegisterState(NetworkState state)
{
    state.Use(PlayerStateNetAdapter.Instance, m_State, previous => ShowState());
}

public override void OnStartServer()
{
    m_Character.DecidesDeath = true;
    m_Character.CollectsItems = false;
    m_Game.Manager.TimeManager.OnTick += ServerTick;
}

public override void OnStartClient()
{
    m_Character.CollectsItems = NetworkObject.IsOwner;
    if (!m_Game.IsServer)
    {
        m_Character.DecidesDeath = false;
        ShowState();
    }

    if (NetworkObject.IsOwner)
    {
        m_Game.SetLocalPlayer(this);
    }
}
```

`OnStopServer` hủy subscribe `ServerTick`. Callback của state nhận giá trị trước đó trong khi `m_State` đã giữ giá trị mới, nên `ShowState` đọc `m_State`:

```csharp
private void ShowState()
{
    if (m_Game.IsServer)
    {
        return;
    }

    if (m_State.Dead && !m_Character.IsDead.Value)
    {
        m_Character.Die((DeathCause)m_State.Cause);
    }
    else if (!m_State.Dead && m_Character.IsDead.Value)
    {
        m_Character.Reset();
    }
}
```

### Quyết định sau mỗi tick <a href="#decide-after-each-tick" id="decide-after-each-tick"></a>

`TimeManager.OnTick` được phát sau khi package đã step physics của một tick, nên lúc đó các collision callback của kẻ địch cho tick đó đã chạy:

```csharp
private void ServerTick()
{
    TimeManager time = m_Game.Manager.TimeManager;
    if (m_State.Dead)
    {
        if (time.Tick >= m_RespawnTick)
        {
            Respawn();
        }

        return;
    }

    if (!m_Character.IsDead.Value && transform.position.y < 0f)
    {
        m_Character.Die(DeathCause.Fall);
    }

    if (m_Character.IsDead.Value)
    {
        m_State.Dead = true;
        m_State.Cause = (byte)m_Character.DeathCause;
        m_RespawnTick = time.Tick + (uint)Mathf.CeilToInt(m_RespawnDelay * time.TickRate);
        Debug.Log($"[RedRunner] player {NetworkObject.OwnerId} died: {m_Character.DeathCause}");
    }
    else if (TerrainGenerator.Singleton.IsBuilt && transform.position.x >= TerrainGenerator.Singleton.EndX)
    {
        Debug.Log($"[RedRunner] player {NetworkObject.OwnerId} reached the end block");
        Respawn();
    }
}
```

`m_RespawnDelay` là 2 giây, tức 100 tick ở 50 tick mỗi giây. Tick hồi sinh được đếm theo tick của server, nên nó không phụ thuộc vào frame rate của server.

### Hồi sinh <a href="#respawn" id="respawn"></a>

```csharp
private void Respawn()
{
    m_Character.Reset();
    PhysicsBody2D body = NetworkObject.Body2D;
    BodyState2D state = body.State;
    state.Position = new System.Numerics.Vector2(m_Game.SpawnPoint.x, m_Game.SpawnPoint.y);
    state.Velocity = System.Numerics.Vector2.Zero;
    body.State = state;
    m_NetworkTransform.Teleport();
    m_Character.RunSmoothVelocity = 0f;
    m_State.Dead = false;
    m_State.Cause = 0;
}
```

`Reset` làm nhân vật sống lại và bật lại `Rigidbody2D` của nó. Sau đó body được đưa tới điểm spawn qua `NetworkObject.Body2D`, cùng cách nhìn vào body mà `Restore` dùng, và vận tốc damping khi chạy cũng được đặt lại, nên reconcile state tiếp theo khớp với một nhân vật đang đứng yên.

Việc hồi sinh tới hai loại client theo cách khác nhau. Các client khác interpolate nhân vật, và `NetworkTransform.Teleport()` báo cho chúng biết lần di chuyển này là một cú nhảy, nên chúng xóa bộ đệm interpolation và đặt nhân vật ở điểm bắt đầu. `NetworkPlayer.Awake` giữ `NetworkTransform` trong `m_NetworkTransform` cho lời gọi này.

Client của owner dự đoán nhân vật và không lấy vị trí từ `NetworkTransform`. Reconcile state tiếp theo từ server cách xa dự đoán của nó, `Matches` trả về false, và client khôi phục motion của server rồi replay. Việc hồi sinh được sửa như mọi khác biệt khác, không cần code riêng.

Dòng `Teleport()` được thêm sau, trong commit `c75cebd` ở bước 08, sau khi một bài kiểm tra phát hiện các client khác vẽ nhân vật trượt ngang qua level. Commit `a148ea7` chứa phần còn lại của method này.

### Giữ đồng xu và rương trên từng client <a href="#keep-coins-and-chests-on-each-client" id="keep-coins-and-chests-on-each-client"></a>

`Coin` và `Chest` chỉ phản ứng với nhân vật có `CollectsItems`:

```csharp
if (m_UseOnTriggerEnter2D && character != null && character.CollectsItems) {
	Collect ();
}
```

Mỗi client thu thập đồng xu mà nhân vật của chính nó chạm vào. Không ai khác thấy những đồng xu đó biến mất, và server bỏ qua chúng.

### Bỏ điểm số <a href="#remove-the-score" id="remove-the-score"></a>

`GameManager` không còn load hay lưu đồng xu, điểm số hay thiết lập âm thanh bằng SaveGameFree, và không còn nhân vật chính để tính điểm. Trong `Play.unity`, tắt `Coin Panel`, `High Score Text` và `Score Text` dưới `Canvas/In-Game Screen`.

### Rời màn hình bắt đầu gọn gàng <a href="#leave-the-start-screen-cleanly" id="leave-the-start-screen-cleanly"></a>

Handler của màn hình bắt đầu cho kết nối đã dừng trở thành một method, `Network_ClientStateChanged`, được `OnDestroy` hủy subscribe. Nếu không, việc thoát game khi đang kết nối sẽ chạy handler sau khi Unity đã hủy `Animator` của màn hình.

## Test <a href="#test" id="test"></a>

Kết nối tới một server và chạy xuống nước.

Bản port có hai bài kiểm tra cho bước này. `HostLifeCheck` khởi động một host và đưa nhân vật của host xuống dưới level, kiểm tra nó chết vì `Fall`, giữ trạng thái chết đúng khoảng chờ và hồi sinh ở điểm bắt đầu. Sau đó nó đưa nhân vật lên khối kết thúc và kiểm tra nhân vật quay về điểm bắt đầu. `LifeCheck` kết nối tới một tiến trình server và chạy sang phải, nhảy cho tới khi nhân vật chết, kiểm tra client chỉ hiển thị cái chết khi state của server báo như vậy và sau đó hiển thị việc hồi sinh.

## Kết quả mong đợi <a href="#expected-result" id="expected-result"></a>

Log của server ghi nguyên nhân:

```
[RedRunner] player 1 died: Water
```

Bộ xương rơi xuống, và hai giây sau nhân vật lại đứng ở điểm bắt đầu. Trong một lần chạy `LifeCheck`, nhân vật chết dưới nước 3.1 giây sau khi bắt đầu, hồi sinh ở điểm bắt đầu và đã nhặt được một đồng xu.

![Một nhân vật rơi xuống nước](../../../.gitbook/assets/redrunner-death.png)

## Commit <a href="#commit" id="commit"></a>

```
Commit: a148ea7
Message: Decide deaths on the server and respawn players at the start
```

Xem [`a148ea7`](https://github.com/fomoxa/RedRunner/commit/a148ea70ca4eea0ec407c9cd85af57ca1acdf589) trên GitHub.

Lời gọi `Teleport()` trong `Respawn` đến từ `c75cebd`, được liệt kê ở bước 08.

Tiếp tục với [bước 07: chướng ngại di chuyển](step-07-moving-hazards.md).
