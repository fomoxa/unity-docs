# Bước 07: Chướng ngại di chuyển

## Mục tiêu <a href="#goal" id="goal"></a>

Sau bước này, chùy và các lưỡi cưa chạy trên đường ray đứng ở cùng một chỗ trên server và trên mọi client tại cùng một tick, mà vị trí của chúng không cần gửi qua mạng.

## Điểm xuất phát <a href="#starting-point" id="starting-point"></a>

Sau bước 06, server quyết định cái chết, nhưng các path follower vẫn di chuyển trong `PathFollower.Update` bằng `Time.deltaTime`.

## Vấn đề <a href="#problem" id="problem"></a>

```
Offline:
PathFollower.Update (every frame)
  ↓
Smart: a character within range? start
gameRunning false? stop
  ↓
move toward the next point with Time.deltaTime
```

Khi online, điều đó cho mỗi tiến trình một cái chùy riêng. Dedicated server không bao giờ gọi `GameManager.StartGame`, nên `gameRunning` giữ false và chùy của nó không bao giờ di chuyển. Chùy của mỗi client bắt đầu khi nhân vật của chính client đó tới gần, điều xảy ra vào thời điểm khác nhau ở mỗi tiến trình.

Từ bước 06, chùy trên server là cái giết người chơi, nên một người chơi có thể bị đập trên màn hình bởi một cái chùy đang ở chỗ khác trên server, hoặc chết trên server vì một cái chùy mà client hiển thị ở chỗ khác.

## Khái niệm Fomoxa <a href="#fomoxa-concepts" id="fomoxa-concepts"></a>

* [Tick và thời gian](../../../khai-niem/tick.md)
* [Tick event](../../../khai-niem/tick.md#tick-events)
* [Ba số tick](../../../khai-niem/tick.md#three-tick-numbers)
* [Mô phỏng tất định](../../../khai-niem/deterministic-simulation.md)

## Thiết kế <a href="#design" id="design"></a>

Chuyển động của một follower không phụ thuộc vào người chơi nào, nên nó có thể được tính chỉ từ số tick:

```
BuildCycle(tickDelta): run the path rules once, tick by tick,
                       until the follower is back at its first point
  ↓
cycle = [position after tick 0, 1, 2, … N-1]
  ↓
position(tick) = cycle[tick % N]
```

`NetworkLevel` di chuyển mọi follower trước mỗi tick, dùng tick mà tiến trình đang mô phỏng. Trên server đó là tick của server. Trên client đó là prediction tick, tick mà client đang dự đoán, cũng là số mà server dùng khi áp dụng input của tick đó. Vì vậy chùy đứng đúng chỗ nó sẽ đứng trên server khi nhân vật cục bộ tới nơi.

Không có gì được replicate. Server và client tính ra cùng một vị trí vì chúng chạy cùng code trên cùng số tick, và chỉ va chạm trên server mới giết người chơi.

## File <a href="#files" id="files"></a>

```
Assets/Scripts/RedRunner/Utilities/PathFollower.cs
Assets/Scripts/RedRunner/Networking/NetworkLevel.cs
Assets/Scripts/RedRunner/Enemies/Mace.cs
```

## Hiện thực <a href="#implementation" id="implementation"></a>

### Biến đường đi thành một chu kỳ <a href="#turn-the-path-into-a-cycle" id="turn-the-path-into-a-cycle"></a>

`PathFollower.BuildCycle (float tickDelta)` chạy các kiểu di chuyển của các điểm trên đường đi (MoveTowards, Lerp, SmoothDamp, Acceleration) với độ dài tick thay cho thời gian frame. Nó bắt đầu ở điểm đầu tiên, chạy cho tới khi follower quay lại điểm đầu tiên, và lưu vị trí sau mỗi tick. Để chu kỳ khép kín chính xác, ba chi tiết khác với phiên bản theo frame: khi tới nơi, follower được đặt đúng vào điểm và vận tốc làm mượt của nó được đặt lại, nó đứng yên trong lúc chờ ở một điểm, và Acceleration tăng tốc mỗi tick một lần. Vòng lặp dừng sau 600 giây tính theo tick, giới hạn chỉ một đường đi không bao giờ quay về mới chạm tới.

### Đặt follower cho một tick <a href="#place-the-follower-for-a-tick" id="place-the-follower-for-a-tick"></a>

```csharp
public virtual Vector3 PositionAt (uint tick)
{
	return m_Cycle [(int)(tick % (uint)m_Cycle.Count)];
}
```

```csharp
public virtual void FollowTick (uint tick, float tickDelta)
{
	if (m_PathDefinition == null) {
		return;
	}
	if (m_Cycle == null || m_CycleTickDelta != tickDelta) {
		BuildCycle (tickDelta);
	}
	Vector3 position = PositionAt (tick);
	m_Velocity = (PositionAt (tick - 1) - position) / tickDelta;
	if (!m_Driven) {
		m_Driven = true;
		StopAllCoroutines ();
		m_Rigidbody2D = GetComponent<Rigidbody2D> ();
		transform.position = position;
		if (m_Rigidbody2D != null) {
			m_Rigidbody2D.position = position;
		}
	} else if (m_Rigidbody2D != null) {
		m_Rigidbody2D.MovePosition (position);
	} else {
		transform.position = position;
	}
}
```

Chùy có một `Rigidbody2D` kinematic, và `MovePosition` di chuyển nó trong bước physics tiếp theo, nên nhân vật bị nó đập trúng bị đẩy giống như bị một body đang chuyển động đẩy. `Velocity` giữ dấu mà code va chạm của chùy chờ đợi (vị trí trước trừ vị trí hiện tại), nên chùy vẫn quyết định có đập hay không dựa trên hướng của nó. Khi `FollowTick` đã chạy, `Update` return ngay ở dòng đầu tiên, và phép kiểm tra tầm, cờ `Stopped` cùng chuyển động theo frame không còn tác dụng.

### Điều khiển các follower từ level <a href="#drive-the-followers-from-the-level" id="drive-the-followers-from-the-level"></a>

`NetworkLevel` biết khi nào level tồn tại, nên nó điều khiển các follower. Sau khi dựng các khối, nó thu thập follower của chúng và subscribe `TimeManager.OnPreTick`, event chạy trước khi package step physics:

```csharp
private void Build()
{
    if (m_State.Seed == 0 || m_Generator.IsBuilt)
    {
        return;
    }

    m_Generator.Build((int)m_State.Seed);
    m_Followers = FindObjectsByType<PathFollower>(FindObjectsSortMode.None);
    m_Game.Manager.TimeManager.OnPreTick += MoveFollowers;
}

private void MoveFollowers()
{
    TimeManager time = m_Game.Manager.TimeManager;
    uint tick = time.PredictionTick;
    float tickDelta = (float)time.TickDelta;
    foreach (PathFollower follower in m_Followers)
    {
        follower.FollowTick(tick, tickDelta);
    }
}
```

Trên server và ở host mode, `TimeManager.PredictionTick` bằng tick của server. `NetworkLevel` tìm `NetworkGame` trong `Awake` và hủy subscribe trong `OnDestroy`.

Khi một client replay các tick để sửa nhân vật của mình, các follower giữ ở vị trí của tick hiện tại. Một lần replay chỉ bao vài tick, nên chênh lệch nhỏ, và server vẫn quyết định chùy có giết ai hay không.

Fomoxa cung cấp số tick, độ dài tick và thời điểm trước mỗi tick, còn game biến chúng thành một vị trí.

## Test <a href="#test" id="test"></a>

Kết nối tới một server và quan sát một cái chùy mà không lại gần.

Bài kiểm tra riêng của bản port là `Tools/PortChecks/PathCheck.cs`, chạy với tham số server `-log-paths`. Trên server, `PathLog` log vị trí của follower di chuyển đầu tiên trong level sau mỗi 10 tick. Client log tương tự trong 10 giây, và bài kiểm tra so sánh hai log tại các tick mà cả hai đều có.

## Kết quả mong đợi <a href="#expected-result" id="expected-result"></a>

* Chùy di chuyển ngay cả khi không có nhân vật nào ở gần.
* Mọi client hiển thị nó ở cùng một điểm trong cú đung đưa.

Trong một lần chạy `PathCheck`, chùy ở cùng một vị trí ở cả hai phía tại 49 tick, với chu kỳ 436 tick (8.7 giây ở 50 tick mỗi giây).

## Commit <a href="#commit" id="commit"></a>

```
Commit: f277dad
Message: Move maces and track saws on a cycle of server ticks
```

Xem [`f277dad`](https://github.com/fomoxa/RedRunner/commit/f277dad4cc29eccef696158280185c9117a270ae) trên GitHub, rồi tiếp tục với [bước 08: hai client](step-08-two-clients.md).
