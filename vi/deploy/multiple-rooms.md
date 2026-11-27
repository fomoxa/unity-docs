# Nhiều phòng trên một server

Một [dedicated server](dedicated-server.md) có thể chứa nhiều trận của cùng một map trong một process. Mỗi trận chạy trong bản riêng của scene map, và mỗi bản có các physics world riêng, nên người chơi và object ở phòng này không bao giờ va chạm với phòng khác, còn client chỉ nhận object của phòng mình. Trang này dựng cách bố trí đó: một sảnh mà mọi client load, các phòng mà server mở cho từng nhóm người chơi, và bước chuyển từ sảnh vào phòng. Mục cuối chỉ cách đo một phòng tốn bao nhiêu trên phần cứng của bạn.

## Phòng là gì <a href="#what-a-room-is" id="what-a-room-is"></a>

Một phòng là một [bản của network scene](../objects/scenes.md#instances) map, chỉ load cho các peer chơi trong đó:

- `ServerManager.Scenes.Load(mapId, peers, ScenePhysics.Own)` lần nào cũng tạo một bản mới, kể cả khi map đã có bản, và trả về `NetworkScene` của nó.
- `ScenePhysics.Own` cho bản đó physics world 3D và 2D riêng. Hai phòng của một map load với mặc định `Shared` sẽ chồng lên nhau trong world mặc định, nên mỗi map chỉ có được một bản `Shared` tại một thời điểm.
- Object trong bản, kể cả object server spawn vào đó, chỉ tới các peer đã load bản này.

Sảnh là một bản toàn cục, load bằng `LoadGlobal`, và mọi client load nó khi kết nối. Người chơi spawn ở sảnh rồi chuyển vào phòng khi phòng đã sẵn sàng.

## Mở phòng và đưa người chơi vào <a href="#open-a-room-and-move-the-players-in" id="open-a-room-and-move-the-players-in"></a>

Chuyển một người chơi vào phòng chỉ gửi lệnh chuyển scene khi client của người đó đã load xong phòng. Client còn đang load sẽ nhận despawn, rồi nhận spawn mới khi báo load xong, và object của nó chạy lại từ `OnStartClient`. Vì vậy class dưới đây load phòng, chờ tới khi server và mọi peer của phòng load xong, rồi mới chuyển người chơi:

```csharp
using System.Collections.Generic;
using Fomoxa.Networking;
using Fomoxa.Unity;

public sealed class RoomHost
{
    private readonly NetworkManager manager;
    private readonly uint mapId;
    private readonly Dictionary<NetworkScene, PendingRoom> pending = new Dictionary<NetworkScene, PendingRoom>();

    public RoomHost(NetworkManager manager, uint mapId)
    {
        this.manager = manager;
        this.mapId = mapId;
        manager.ServerManager.Scenes.OnLoaded += OnLoaded;
        manager.ServerManager.Scenes.OnPeerLoaded += OnPeerLoaded;
    }

    public NetworkScene Open(IReadOnlyList<ulong> peers, IReadOnlyList<NetworkObject> players)
    {
        NetworkScene room = manager.ServerManager.Scenes.Load(mapId, peers, ScenePhysics.Own);
        pending.Add(room, new PendingRoom(peers, players));
        return room;
    }

    private void OnLoaded(NetworkScene room)
    {
        if (pending.TryGetValue(room, out PendingRoom waiting))
        {
            waiting.ServerLoaded = true;
            TryMoveIn(room, waiting);
        }
    }

    private void OnPeerLoaded(ulong peerId, NetworkScene room)
    {
        if (pending.TryGetValue(room, out PendingRoom waiting))
        {
            waiting.LoadedPeers.Add(peerId);
            TryMoveIn(room, waiting);
        }
    }

    private void TryMoveIn(NetworkScene room, PendingRoom waiting)
    {
        if (!waiting.ServerLoaded || waiting.LoadedPeers.Count < waiting.Peers.Count)
        {
            return;
        }

        pending.Remove(room);
        foreach (NetworkObject player in waiting.Players)
        {
            manager.ServerManager.MoveToScene(player, room);
        }
    }

    private sealed class PendingRoom
    {
        public PendingRoom(IReadOnlyList<ulong> peers, IReadOnlyList<NetworkObject> players)
        {
            Peers = peers;
            Players = players;
        }

        public IReadOnlyList<ulong> Peers { get; }

        public IReadOnlyList<NetworkObject> Players { get; }

        public HashSet<ulong> LoadedPeers { get; } = new HashSet<ulong>();

        public bool ServerLoaded { get; set; }
    }
}
```

`mapId` là scene id của map, ví dụ `FomoxaScenes.ArenaId` hoặc `manager.Scenes.IdOf("Assets/Scenes/Arena.unity")`. Tạo `RoomHost` khi server đã start, và truyền cho `Open` các peer của trận cùng các object người chơi mà họ sở hữu, do server spawn ở sảnh. `Load` bỏ qua peer chưa start, nên hãy bỏ peer đã ngắt kết nối khỏi danh sách của bạn trước khi gọi `Open`, và xử lý việc ngắt kết nối trong lúc load ở code ghép trận, vì phòng ở trên sẽ chờ peer đó mãi.

Lần chuyển giữ nguyên vị trí và vận tốc của từng body. Các phòng của một map thường cho người chơi bắt đầu ở điểm spawn cố định, nên hãy đặt từng người chơi sau lần chuyển qua body của nó, cách này chạy được với cả hai backend physics:

```csharp
NetworkBody body = player.Body;
NetworkBodyState state = body.State;
state.Position = spawnPoint;
state.Velocity = Vector3.zero;
body.State = state;
```

Đọc `player.Body` sau `MoveToScene`, vì lần chuyển dựng lại các body trong world của phòng. Owner đang dự đoán người chơi của mình sẽ ngừng dự đoán khi lệnh chuyển tới và dự đoán lại từ state đầu tiên server gửi từ phòng, như [chuyển object](../objects/scenes.md#move-an-object-to-another-instance) mô tả.

## Đặt object vào phòng <a href="#fill-the-room" id="fill-the-room"></a>

Object thuộc về trận, như vật phẩm hay thùng, được spawn vào phòng bằng cách chuyển chúng vào Unity scene của phòng trước `Spawn`, như ở [spawn vào network scene](../objects/spawning.md#spawning-into-a-network-scene). Làm việc này trong handler `OnLoaded` của phòng hoặc muộn hơn, vì `TryGetScene` chỉ tìm thấy Unity scene khi server đã load xong.

## Truy vấn physics trong phòng <a href="#physics-queries-in-a-room" id="physics-queries-in-a-room"></a>

Một raycast hay overlap chỉ thấy collider của một world. Hỏi physics component các world của scene phòng, như ở [lấy world](../physics/queries.md#reaching-a-world), rồi truy vấn trên đó. `Physics.Raycast` và `Physics2D.Raycast` tĩnh chỉ thấy world mặc định, nơi có sảnh và scene game khởi động cùng, nhưng không có phòng nào load với `Own`.

## Chọn backend physics <a href="#choosing-a-physics-backend" id="choosing-a-physics-backend"></a>

Cả hai backend đều tách các phòng:

| Backend | Phòng | Server step gì mỗi tick |
|---|---|---|
| `RigidbodyPhysics` với Simulate Physics bật | Mỗi bản `Own` có world PhysX và Box2D riêng | Mọi world của mọi scene đã load, gồm cả các phòng |
| `RapierPhysics` | Mỗi bản có world Rapier riêng, dù load với `ScenePhysics` nào | Các world Rapier; manager còn step các world Unity của bản `Own`, vốn chỉ chứa physics nằm ngoài network object |

Với Rapier, hãy export [scene file](../rapier/setup.md#export-the-scene-files) của sảnh và map, vì Rapier đọc hình học tĩnh của phòng từ đó.

## Đóng phòng <a href="#closing-a-room" id="closing-a-room"></a>

`ServerManager.Scenes.Unload(room)` despawn mọi object trong phòng, kể cả người chơi, unload phòng trên các peer của nó rồi trên server. Để giữ người chơi cho trận sau, chuyển họ về sảnh bằng `MoveToScene(player, lobby)` trước khi unload phòng. Một bản vẫn được load trên server khi peer cuối cùng rời đi, nên hãy unload các phòng đã hết trận; nếu không, world của chúng vẫn tiếp tục được step.

## Đo server của bạn <a href="#measure-your-server" id="measure-your-server"></a>

Một phòng tốn bao nhiêu tùy vào map, số body và máy, nên hãy đo chính bản build của bạn. Chạy player server như khi chạy thật, với `-batchmode -nographics`, load số phòng muốn so sánh, cho mỗi phòng các object mà một trận thật có, và để nó chạy vài trăm tick trước khi bắt đầu đo.

### Thời gian tick <a href="#tick-time" id="tick-time"></a>

Với timing mode Tick, mọi tick tới hạn trong một frame chạy bên trong bước đầu tiên của manager trong player loop của Unity, ở ngay đầu `EarlyUpdate` (xem [khi nào nó chạy](../connections/network-manager.md#when-it-runs)). Class dưới đây thêm một bước trước và một bước sau bước đó, rồi cộng dồn thời gian giữa hai bước. Cuối mỗi frame có chạy tick, nó chia thời gian gom được từ frame có tick trước đó cho số tick, và ghi một giá trị cho mỗi tick. Tạo nó sau khi manager đã bật, ví dụ trong `Start`, để bước của manager đã đứng đầu:

```csharp
using System;
using System.Collections.Generic;
using System.Diagnostics;
using Fomoxa.Networking;
using UnityEngine.LowLevel;
using UnityEngine.PlayerLoop;

public sealed class TickTimer : IDisposable
{
    private readonly TimeManager time;
    private readonly Stopwatch stopwatch = new Stopwatch();
    private readonly List<double> milliseconds = new List<double>();
    private double pending;
    private int ticksThisFrame;

    public TickTimer(TimeManager time)
    {
        this.time = time;
        time.OnPreTick += CountTick;
        PlayerLoopSystem root = PlayerLoop.GetCurrentPlayerLoop();
        for (int index = 0; index < root.subSystemList.Length; index++)
        {
            ref PlayerLoopSystem phase = ref root.subSystemList[index];
            if (phase.type == typeof(EarlyUpdate))
            {
                var systems = new List<PlayerLoopSystem>(phase.subSystemList);
                systems.Insert(1, new PlayerLoopSystem { type = typeof(TickTimer), updateDelegate = End });
                systems.Insert(0, new PlayerLoopSystem { type = typeof(TickTimer), updateDelegate = stopwatch.Restart });
                phase.subSystemList = systems.ToArray();
            }
            else if (phase.type == typeof(PostLateUpdate))
            {
                var systems = new List<PlayerLoopSystem>(phase.subSystemList);
                systems.Add(new PlayerLoopSystem { type = typeof(TickTimer), updateDelegate = Record });
                phase.subSystemList = systems.ToArray();
            }
        }

        PlayerLoop.SetPlayerLoop(root);
    }

    public IReadOnlyList<double> Milliseconds => milliseconds;

    public void Dispose()
    {
        time.OnPreTick -= CountTick;
        PlayerLoopSystem root = PlayerLoop.GetCurrentPlayerLoop();
        for (int index = 0; index < root.subSystemList.Length; index++)
        {
            ref PlayerLoopSystem phase = ref root.subSystemList[index];
            if (phase.subSystemList != null)
            {
                phase.subSystemList = Array.FindAll(phase.subSystemList, system => system.type != typeof(TickTimer));
            }
        }

        PlayerLoop.SetPlayerLoop(root);
    }

    private void CountTick() => ticksThisFrame++;

    private void End()
    {
        stopwatch.Stop();
        pending += stopwatch.Elapsed.TotalMilliseconds;
    }

    private void Record()
    {
        if (ticksThisFrame == 0)
        {
            return;
        }

        for (int tick = 0; tick < ticksThisFrame; tick++)
        {
            milliseconds.Add(pending / ticksThisFrame);
        }

        pending = 0;
        ticksThisFrame = 0;
    }
}
```

Báo cáo mean, trung vị, phân vị 95 và giá trị lớn nhất của `Milliseconds`, không chỉ mean, vì người chơi nhận ra chính những tick chậm. Ở 60 tick mỗi giây, một tick có 16,7 ms, và server còn cần thời gian cho phần còn lại của mỗi frame.

### Bộ nhớ <a href="#memory" id="memory"></a>

Đọc bộ nhớ sau khi đo xong, khi các phòng vẫn còn load:

| Giá trị | Đọc bằng | Bao gồm |
|---|---|---|
| Managed heap | `GC.GetTotalMemory(false)` | Object C# của game và của package |
| Bộ nhớ Unity giữ | `Profiler.GetTotalReservedMemoryLong()` (`UnityEngine.Profiling`) | Bộ nhớ các allocator của Unity đang giữ, gồm cả scene và physics |
| Working set | `Process.WorkingSet64`, hoặc công cụ của hệ điều hành | Toàn bộ process |

Trong player Windows dùng scripting backend Mono, `Process.WorkingSet64` có thể trả về 0. Khi đó hãy đọc working set từ Task Manager, hoặc gọi `K32GetProcessMemoryInfo` của `kernel32.dll`.

### So sánh các lần chạy <a href="#comparing-runs" id="comparing-runs"></a>

Chạy mỗi số phòng trong một process mới, và với cả hai backend nếu bạn đang chọn giữa chúng. Hiệu giữa hai số phòng là chi phí của các phòng thêm vào, dễ so giữa các máy hơn so với tổng.

## Giới hạn <a href="#limits" id="limits"></a>

Mọi phòng của một process dùng chung main thread của Unity: server step world của từng phòng và chạy code game của từng phòng lần lượt, nên một phòng chậm làm trễ tick của mọi phòng. Khi một process không còn đủ, hãy chạy thêm process, như mô tả ở [cụm server](cluster.md). Một process load cùng một map nhiều lần cũng giữ một bản sao scene object của map cho mỗi phòng.
