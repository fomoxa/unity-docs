# Bước 08: Hai client

## Mục tiêu <a href="#goal" id="goal"></a>

Bước này chạy một server với hai client và sửa những gì chỉ lộ ra khi người chơi nhìn thấy nhau: nhân vật của người chơi khác có animation và quay đầu ra sao, cái chết và việc hồi sinh của người chơi khác trông thế nào, và điều gì xảy ra với nhân vật khi người chơi của nó rời đi hoặc bị crash.

## Điểm xuất phát <a href="#starting-point" id="starting-point"></a>

Sau bước 07, game đã hoàn chỉnh với một client, nhưng mọi bước trước đều được test với một client duy nhất, đôi khi ở host mode.

## Vấn đề <a href="#problem" id="problem"></a>

Chạy hai client làm lộ ra ba vấn đề:

1. Khi nhân vật của người chơi khác hồi sinh, animator của nó nhận tốc độ chạy lên tới hàng nghìn. `LateUpdate` tính tốc độ của nhân vật kinematic từ quãng đường đi được trong một frame, và một lần hồi sinh đi hết cả level chỉ trong vài frame.
2. Các client khác vẽ nhân vật đang hồi sinh trượt từ chỗ chết về điểm bắt đầu, vì bộ đệm `NetworkTransform` của chúng giữ hai vị trí liền nhau và interpolate giữa chúng.
3. Khi một client thoát, nhân vật của nó tiếp tục chạy và chết thêm khoảng 20 giây. Qua UDP, server chỉ biết một peer đã đi qua heartbeat, sau 5 giây im lặng và 15 giây nữa không có trả lời, và cho tới lúc đó package lặp lại input cuối của người chơi ở mọi tick.

## Khái niệm Fomoxa <a href="#fomoxa-concepts" id="fomoxa-concepts"></a>

- [NetworkTransform](../../../synchronization/transform.md)
- [Teleport](../../../synchronization/transform.md#teleporting)
- [Input trên server](../../../prediction/input.md#on-the-server)
- [Client](../../../core/client.md#connect-and-disconnect)
- [UDP](../../../transports/udp.md)
- [Cấu hình](../../../reference/configuration.md)

## Thiết kế <a href="#design" id="design"></a>

| Vấn đề | Cách sửa | Ở đâu |
|---|---|---|
| Tốc độ animator sau khi hồi sinh | Di chuyển quá 2 đơn vị trong một frame được tính là teleport, và tốc độ bị giới hạn | `RedCharacter.LateUpdate` |
| Trượt ngang qua level | `NetworkTransform.Teleport()` sau khi hồi sinh | `NetworkPlayer.Respawn`, bước 06 |
| Người chơi đã thoát vẫn chạy | `ClientManager.StopConnection` gửi `PeerLeave`, và server despawn nhân vật ngay | Package |
| Người chơi bị crash vẫn chạy | `Apply` bỏ trục di chuyển khi input đã bị lặp hơn 10 tick | `NetworkPlayer.Apply` |

Hai dòng cuối là hai trường hợp khác nhau. Client chủ động dừng có thể báo cho server, nhưng client bị crash hoặc mất mạng thì không, nên server vẫn phải chờ heartbeat, và game quyết định nhân vật làm gì trong lúc đó.

## File <a href="#files" id="files"></a>

```
Assets/Scripts/RedRunner/Characters/RedCharacter.cs
Assets/Scripts/RedRunner/Networking/NetworkPlayer.cs
Assets/Scripts/RedRunner/Networking/Generated/
FomoxaSystemModels/PeerLeave.cs
FomoxaSystemModels/TransformSettle.cs
FomoxaSystemModels/TransformUpdate.cs
.fomoxa/
```

Các file sinh ra thay đổi vì system model của package thay đổi: các message transform giờ mang teleport generation, và `PeerLeave` là message mới. Hãy sinh lại bằng Tools > Fomoxa > Generate sau khi cập nhật package.

## Hiện thực <a href="#implementation" id="implementation"></a>

### Animation cho nhân vật teleport <a href="#animate-a-character-that-teleports" id="animate-a-character-that-teleports"></a>

```csharp
void LateUpdate ()
{
	Vector2 velocity = m_Rigidbody2D.linearVelocity;
	if ( m_Rigidbody2D.bodyType == RigidbodyType2D.Kinematic && Time.deltaTime > 0f )
	{
		Vector2 moved = transform.position - m_LastPosition;
		velocity = moved.magnitude > m_TeleportDistance ? Vector2.zero : Vector2.ClampMagnitude ( moved / Time.deltaTime, m_MaxRunSpeed + m_JumpStrength );
	}
	m_LastPosition = transform.position;
```

`m_TeleportDistance` là một serialized field mới, mặc định 2 đơn vị, còn mức giới hạn là tốc độ nhanh nhất nhân vật có thể đạt được bằng chạy và nhảy.

### Đánh dấu hồi sinh là teleport <a href="#mark-the-respawn-as-a-teleport" id="mark-the-respawn-as-a-teleport"></a>

`NetworkPlayer.Respawn` gọi `m_NetworkTransform.Teleport()` ngay sau khi di chuyển body, như trong [bước 06](step-06-death-and-respawn.md#respawn). Server khi đó gửi vị trí mới dưới dạng một settle bắt đầu một teleport generation mới. Client nhận được nó sẽ xóa bộ đệm interpolation và đặt nhân vật ở điểm bắt đầu, và nếu message đó bị mất, bản cập nhật đầu tiên của generation mới cũng có cùng tác dụng.

### Chủ động rời server <a href="#leave-the-server-on-purpose" id="leave-the-server-on-purpose"></a>

Game không cần thay đổi gì cho trường hợp này. `NetworkGame.Leave` đã gọi `ClientManager.StopConnection`, và `NetworkManager` gọi nó khi ứng dụng thoát. Với package hiện tại, `StopConnection` gửi message `PeerLeave` ba lần trước khi đóng kết nối, server kết thúc peer đó ngay, và nhân vật bị despawn cùng owner như ở bước 03.

### Dừng nhân vật khi người chơi biến mất <a href="#stop-a-character-whose-player-vanished" id="stop-a-character-whose-player-vanished"></a>

`InputContext.RepeatedTicks` cho `Apply` biết server đã lặp lại input cuối bao nhiêu tick liên tiếp:

Trước:

```csharp
m_Character.Simulate(input.Move, fresh && input.Jump, fresh && input.Roll, tickDelta, !context.Replaying);
```

Sau:

```csharp
private void Apply(PlayerInput input, InputContext context)
{
    float tickDelta = (float)m_Game.Manager.TimeManager.TickDelta;
    bool fresh = !context.Repeated;
    float move = context.RepeatedTicks > m_MaxRepeatedTicks ? 0f : input.Move;
    m_Character.Simulate(move, fresh && input.Jump, fresh && input.Roll, tickDelta, !context.Replaying);
}
```

`m_MaxRepeatedTicks` là 10, tức 0.2 giây ở 50 tick mỗi giây. Một khoảng trống ngắn trong input vẫn lặp lại việc chạy, còn người chơi đã biến mất thì đứng yên cho tới khi heartbeat kết thúc session. Commit `0edd3a4` ban đầu làm việc này bằng một bộ đếm riêng trong `NetworkPlayer`, và `c239d2a` thay bộ đếm đó bằng `RepeatedTicks`.

Thời gian heartbeat đến từ Heartbeat Interval Seconds (5) và Heartbeat Timeout Seconds (15) trên `NetworkManager`, và Red Runner giữ giá trị mặc định.

## Test <a href="#test" id="test"></a>

Build một player Windows, rồi khởi động một server và hai client:

```
RedRunner.exe -batchmode -nographics -server -port 7777 -logFile server.log
RedRunner.exe
RedRunner.exe
```

Kết nối tới `localhost` từ cả hai client, hoặc dùng Editor làm một trong hai. Chạy bằng một client trong khi quan sát bằng client kia, chết và hồi sinh, rồi cuối cùng thoát một client.

Bản port có hai bài kiểm tra cho bước này. `CrowdCheck` kết nối tới server từ Editor và đứng yên trong khi một bản build player thứ hai chạy dưới dạng bot client (`-bot 127.0.0.1 -bot-seconds 45`, do `BotPlayer` xử lý), bot này chạy sang phải, nhảy và rời đi sau 45 giây. `CrashCheck` khởi động bot theo cùng cách và kill tiến trình của nó sau tám giây, để không có `PeerLeave` nào được gửi.

## Kết quả mong đợi <a href="#expected-result" id="expected-result"></a>

- Cả hai nhân vật bắt đầu trên khối bắt đầu và chồng lên nhau mà không đẩy nhau.
- Khi một người chơi chạy, client kia thấy nhân vật chạy với animation chạy và quay mặt theo hướng chạy.
- Khi một người chơi chết, client kia thấy bộ xương, rồi hai giây sau thấy nhân vật trở lại điểm bắt đầu, không trượt ngang qua level.
- Khi một client thoát, nhân vật của nó biến mất khỏi client kia trong khoảng 2 giây.
- Khi một client bị crash, nhân vật của nó đứng yên và biến mất khoảng 20 giây sau.

`CrowdCheck` cũng thất bại nếu hai snapshot liền nhau trong bộ đệm `NetworkTransform` của bot cách nhau quá 2 đơn vị. Trong lần chạy gần nhất, client Editor thấy nhân vật của bot chạy tới x 24, chết và hồi sinh chín lần mà không có cặp nào như vậy, với tốc độ animator tối đa 11.5. Khi không có lời gọi `Teleport()`, bài kiểm tra đếm được 268 frame có chỗ chết và điểm bắt đầu nằm liền nhau trong bộ đệm. Server despawn nhân vật của bot ngay khi bot rời đi. Trong lần chạy gần nhất của `CrashCheck`, nhân vật đứng yên và bị despawn 20.0 giây sau khi bị kill, còn khi không có quy tắc `RepeatedTicks`, nó chạy thêm 11.4 đơn vị và chết thêm ba lần.

## Commit <a href="#commit" id="commit"></a>

Bước này trải trên bốn commit:

```
Commit: 52e1696
Message: Check a server with two clients and fix teleport animation

Commit: 0edd3a4
Message: Stop a departed player's character after ten repeated ticks

Commit: c75cebd
Message: Mark respawns as teleports with NetworkTransform.Teleport

Commit: c239d2a
Message: Leave the server with PeerLeave and stop vanished players by RepeatedTicks
```

Chúng nằm trên GitHub tại [`52e1696`](https://github.com/fomoxa/RedRunner/commit/52e1696b2e5b8db09e0178f827febf9ae712a02f), [`0edd3a4`](https://github.com/fomoxa/RedRunner/commit/0edd3a46a0f5bf48a76786e6242ea2f523e1ec21), [`c75cebd`](https://github.com/fomoxa/RedRunner/commit/c75cebdee36f6edfc3869964157bd45093eae543), [`c239d2a`](https://github.com/fomoxa/RedRunner/commit/c239d2a0988dcf2af5821b41f1ba7cc2f6372baf).

`c75cebd` và `c239d2a` cần một package có teleport generation, `PeerLeave` và `InputContext.RepeatedTicks`, và package đã phát hành có tất cả những thứ đó.

Tiếp tục với [bước 09: game online hoàn chỉnh](step-09-final-online-game.md).
