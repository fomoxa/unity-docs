# Runtime

Trang này viết một server console cho game ở [project đầu tiên của bạn](../getting-started/first-project.md): mỗi người chơi một capsule, state `PlayerStats` với bộ đếm số lần nhảy, và một RPC `Jump` không tham số. Client Unity build từ hướng dẫn đó kết nối tới nó mà không cần sửa.

## Entity và behaviour <a href="#entities-and-behaviours" id="entities-and-behaviours"></a>

Trên console, một network object là một `StandaloneEntity`, và logic mạng của nó nằm trong các class `EntityBehaviour`. `EntityBehaviour` có các callback và phần đăng ký của `NetworkBehaviour`: `OnStartServer`, `OnStopServer`, `OnStartClient`, `OnStopClient`, các callback đổi owner, `OnRegisterRpcs`, `OnRegisterState`, `OnRegisterInput`, `OnReconciled`, các method `SendServerRpc`, `SendObserversRpc` và `SendTargetRpc`, cùng `IsPredicting`, `IsReplaying` và `ReconcileCount`.

Prefab `Player` của hướng dẫn có một `NetworkTransform` và một behaviour `Player`, theo thứ tự đó. Entity console có một behaviour cho mỗi cái, theo cùng thứ tự:

```csharp
using System.Numerics;
using Fomoxa.Networking;
using Fomoxa.Networking.Standalone;
using Generated;
using MyGame.Network.Models;

namespace MyGame.Network
{
    public sealed class PlayerEntity : StandaloneEntity
    {
        public PlayerEntity()
            : this(new PlayerTransform(), new Player())
        {
        }

        private PlayerEntity(PlayerTransform transform, Player player)
            : base(FomoxaPrefabs.PlayerId, new EntityBehaviour[] { transform, player })
        {
            transform.Entity = this;
            player.Entity = this;
        }
    }

    public sealed class PlayerTransform : EntityBehaviour, ITransformSource, ITransformReceiver
    {
        public PlayerTransform()
        {
            SyncTransform(new TransformSync(new TransformSyncSettings(true, true, false, 0.01f, 0.1f, 0.01f)), this, this);
        }

        public StandaloneEntity Entity { get; set; }

        public void ReadLocal(out Vector3 localPosition, out Quaternion localRotation, out Vector3 localScale)
        {
            localPosition = Entity.Position;
            localRotation = Entity.Rotation;
            localScale = Entity.Scale;
        }

        public void ResetReceive()
        {
        }

        public void Receive(in TransformSample sample)
        {
        }
    }

    public sealed class Player : EntityBehaviour
    {
        private readonly PlayerStats stats = new PlayerStats();

        public StandaloneEntity Entity { get; set; }

        protected override void OnRegisterState(NetworkState state)
        {
            state.Use(PlayerStatsNetAdapter.Instance, stats);
        }

        protected override void OnRegisterRpcs(NetworkRpcs rpc)
        {
            rpc.OnServer(nameof(Jump), peerId => Jump());
        }

        private void Jump()
        {
            Entity.Position += Vector3.UnitY;
            stats.Jumps++;
        }
    }
}
```

`PlayerTransform` thay chỗ `NetworkTransform`. `SyncTransform` cho behaviour một `TransformSync`, và server đọc tư thế của entity qua `ITransformSource.ReadLocal` ở cuối mỗi tick rồi gửi phần thay đổi, với cùng luật như `NetworkTransform`. Hãy dùng thiết lập của `NetworkTransform` trên prefab: có đồng bộ vị trí, góc xoay và scale hay không, rồi ba ngưỡng. `ITransformReceiver` được gọi trên client console; server để trống. `TransformSync.Teleport()` làm việc giống `NetworkTransform.Teleport()`.

`EntityBehaviour` không giữ tham chiếu tới entity của nó, nên entity tự truyền chính nó cho các behaviour, như trên.

### Prefab <a href="#prefabs" id="prefabs"></a>

Client kiểm tra một lần spawn theo prefab id và fingerprint, rồi giao message của behaviour index *n* cho `NetworkBehaviour` thứ *n* của prefab. Vì vậy entity console phải khớp prefab:

- prefab id và fingerprint lấy từ các hằng số `FomoxaPrefabs` được sinh ra;
- các behaviour theo thứ tự các component `NetworkBehaviour` của prefab, tức thứ tự Inspector hiển thị, con đứng sau cha;
- mỗi behaviour đăng ký cùng model state, input và RPC như bản Unity tương ứng.

RPC không tham số được tìm theo tên đầy đủ của type behaviour và tên method, như các `RpcModels` được sinh đã đăng ký. Hãy cho behaviour console cùng namespace và tên class với bản Unity, như `MyGame.Network.Player` ở trên, hoặc dùng RPC có model, vốn được khớp chỉ theo model.

## Chương trình <a href="#program" id="program"></a>

```csharp
using System;
using System.Diagnostics;
using System.IO;
using System.Numerics;
using System.Threading;
using Fomoxa.Networking;
using Fomoxa.Networking.Sessions;
using Fomoxa.Networking.Standalone;
using Fomoxa.Networking.Transports;
using Generated;
using MyGame.Network;

namespace MyGame.Server
{
    public static class Program
    {
        public static void Main()
        {
            var registry = new FomoxaRegistry();
            FomoxaAdapters.RegisterAll(registry);

            var prefabs = new StandalonePrefabs();
            prefabs.Register(FomoxaPrefabs.PlayerId, FomoxaPrefabs.PlayerFingerprint, () => new PlayerEntity());

            var clock = Stopwatch.StartNew();
            NetworkRuntime runtime = StandaloneRuntime.Create(
                registry,
                new NetworkSettings(),
                new UdpTransportFactory(),
                prefabs,
                new StandaloneBehaviours(),
                new SceneFileDirectory(Path.Combine(AppContext.BaseDirectory, "Scenes")),
                () => clock.Elapsed,
                NetworkLog.Console);

            runtime.ServerManager.OnRemoteConnectionState += args =>
            {
                if (args.State == ConnectionState.Started)
                {
                    var player = new PlayerEntity { Position = new Vector3(args.PeerId * 2f, 0f, 0f) };
                    runtime.ServerManager.Spawn(player, args.PeerId);
                }
            };

            runtime.ServerManager.StartConnection(7777);
            Console.WriteLine($"server listening on port {runtime.ServerManager.Port}");

            TimeSpan last = clock.Elapsed;
            while (true)
            {
                TimeSpan now = clock.Elapsed;
                runtime.BeginFrame(now, (now - last).TotalSeconds);
                runtime.EndFrame();
                last = now;
                Thread.Sleep(1);
            }
        }
    }
}
```

Chạy nó bằng `dotnet run --project Server~ -c Release`, khởi động một client từ hướng dẫn Unity và bấm Jump: capsule đi lên và bộ đếm tăng, đúng như với server Unity.

## StandaloneRuntime.Create <a href="#standaloneruntimecreate" id="standaloneruntimecreate"></a>

```csharp
public static NetworkRuntime Create(
    FomoxaRegistry registry,
    NetworkSettings settings,
    ITransportFactory transport,
    StandalonePrefabs prefabs,
    StandaloneBehaviours behaviours,
    ISceneFiles scenes,
    Func<TimeSpan> clock,
    NetworkLog log,
    IPhysicsScenes physics = null,
    IReadOnlyList<uint> bootScenes = null)
```

| Tham số | Ý nghĩa |
|---|---|
| `registry` | Một `FomoxaRegistry` được `FomoxaAdapters.RegisterAll` sinh ra điền sẵn |
| `settings` | Các giá trị mà Inspector của `NetworkManager` giữ trong Unity: tick rate, timing mode, kích thước queue, timeout, thiết lập prediction và physics backend. Hãy dùng tick rate mà client mong đợi. |
| `transport` | `UdpTransportFactory`, `TcpTransportFactory`, `WebSocketTransportFactory`, hoặc một `MultiTransportFactory` lắng nghe nhiều loại cùng lúc |
| `prefabs` | Các prefab id mà runtime có thể spawn, mỗi cái kèm fingerprint và một factory |
| `behaviours` | Factory cho behaviour của scene object, theo tên đầy đủ của type Unity của chúng |
| `scenes` | Nơi lấy scene file. `SceneFileDirectory(folder)` đọc `<scene id>.fomoxascene` từ một thư mục. |
| `clock` | Một đồng hồ đơn điệu |
| `log` | Nơi warning và error đi tới. `NetworkLog.Console` ghi ra standard error; `new NetworkLog(exception, warning, error)` gửi chúng đi nơi khác. |
| `physics` | Một `IPhysicsScenes`, hoặc null cho server không có physics; xem [physics](physics.md) |
| `bootScenes` | Các scene id có scene object tồn tại từ đầu, như mô tả bên dưới |

Kết quả là một `NetworkRuntime`, giữ `ServerManager`, `ClientManager` và `TimeManager` mà code Unity truy cập qua `NetworkManager`. Mọi thứ trong các trang [server](../core/server.md) và [client](../core/client.md) đều áp dụng cho chúng, trừ những gì liên quan tới object Unity.

## Vòng lặp frame <a href="#the-frame-loop" id="the-frame-loop"></a>

`NetworkRuntime` không tự làm gì. Hãy gọi `BeginFrame(now, elapsedSeconds)` rồi `EndFrame()` một lần mỗi frame của vòng lặp. `BeginFrame` chạy mọi tick đến hạn, theo thứ tự mô tả trong [tick và thời gian](../concepts/tick.md#order-of-one-tick), còn `EndFrame` gửi những gì timing mode Variable đã xếp hàng. Gọi sai thứ tự, hoặc từ bên trong một tick event, sẽ ném exception.

Vòng lặp ở trên ngủ giữa các frame để tiến trình không quay vòng. Mỗi frame chạy mọi tick đến hạn, tối đa `NetworkSettings.MaxTicksPerFrame`, nên một lần ngủ dài hơn một tick không làm game chậm đi miễn là nó ngắn hơn chừng đó tick.

## Spawn <a href="#spawning" id="spawning"></a>

`ServerManager.Spawn(entity, ownerId)` spawn một `StandaloneEntity` giống cách nó spawn một `NetworkObject` trong Unity. Hãy đặt `Position`, `Rotation`, `Scale`, `SceneId`, `DespawnWithOwner` và `Visibility` trước lời gọi, vì message spawn mang chúng. `Despawn` và `ChangeOwner` hoạt động như trong Unity. Server từ chối entity không phải `StandaloneEntity`, và prefab id chưa đăng ký với `StandalonePrefabs`.

`SceneId` đặt entity vào một network scene, giới hạn observer của nó ở các peer đã load scene đó, và chọn các physics world của nó.

## Scene object và boot scene <a href="#scene-objects-and-boot-scenes" id="scene-objects-and-boot-scenes"></a>

Một scene object được mô tả bởi scene file của scene chứa nó: scene object id, fingerprint, tư thế, tên đầy đủ của type các behaviour và body của nó. Backend console dựng một `StandaloneEntity` cho nó với các behaviour mà `StandaloneBehaviours` tạo cho những tên type đó:

```csharp
var behaviours = new StandaloneBehaviours();
behaviours.Register("MyGame.Network.Door", () => new Door());
```

Tên type không có factory sẽ ném `behaviour type ... is not registered with StandaloneBehaviours` khi scene load.

Network scene mà server load qua `ServerManager.Scenes` đọc file của nó khi load. Scene mà client mở trước khi kết nối, như scene game của hướng dẫn, không được load qua mạng. Hãy truyền scene id của nó vào `bootScenes` khi nó có scene object hoặc geometry physics: backend đọc file của nó trong `Create`, spawn scene object của nó khi server khởi động, và load geometry của nó vào các physics world. Client khớp những object đó với scene mà họ đã mở sẵn, như với server Unity. Entity của boot scene đặt `SceneId` bằng id của scene đó để dùng chung physics world của nó, và server vẫn gửi chúng như object nằm ngoài mọi network scene.

Trang [physics](physics.md) thêm một physics backend, còn [tham chiếu](reference.md) liệt kê các type console và backend contract.
