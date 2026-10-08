# Bước 13: Server console

## Mục tiêu <a href="#goal" id="goal"></a>

Bước này thêm một chương trình .NET trong `Server~/` chạy server Red Runner mà không cần Unity. Client build từ project Unity vào nó từ màn hình bắt đầu như khi vào server Unity, và game chơi giống nhau.

## Điểm xuất phát <a href="#starting-point" id="starting-point"></a>

Game với level Rapier dựng từ catalogue, commit `c44bcfe`.

## Vấn đề <a href="#problem" id="problem"></a>

Sau bước 12, mọi luật server áp dụng đều nằm trong `RedRunner.Simulation`, và physics của level đến từ catalogue. Thứ vẫn cần Unity trên server là phần keo nối mạng: `NetworkGame` spawn người chơi, `NetworkLevel` chọn seed, còn `NetworkPlayer` áp input, quyết định cái chết và hồi sinh, tất cả dưới dạng component `NetworkBehaviour`.

## Khái niệm Fomoxa <a href="#fomoxa-concepts" id="fomoxa-concepts"></a>

- [Server console](../../../console-server/overview.md)
- [Project](../../../console-server/project.md)
- [Runtime](../../../console-server/runtime.md), đặc biệt là [prefab](../../../console-server/runtime.md#prefabs) và [boot scene](../../../console-server/runtime.md#scene-objects-and-boot-scenes)
- [Physics của console](../../../console-server/physics.md)

## Thiết kế <a href="#design" id="design"></a>

Server console phản chiếu ba component Unity:

| Unity | Console | Vai trò |
|---|---|---|
| `NetworkGame` | `ServerGame` | Tạo runtime, spawn một người chơi cho mỗi peer khởi động, dựng level và di chuyển các chướng ngại |
| `NetworkLevel` trên scene object `Network Level` | `LevelBehaviour`, đăng ký cho tên type `RedRunner.Networking.NetworkLevel` | Chọn seed và giữ nó trong `LevelState` |
| `RedRunner.prefab` với `NetworkTransform` và `NetworkPlayer` | `PlayerEntity` với `PlayerTransform` và `PlayerBehaviour` | Gửi tư thế, áp input, quyết định cái chết và hồi sinh |

`Play.unity` là một boot scene: client mở nó trước khi kết nối, và scene file của nó cho server scene object `Network Level` cùng các thiết lập physics của scene. Body của người chơi lấy từ `CataloguePlayer` của catalogue, nên khớp với body mà client dựng từ prefab.

## File <a href="#files" id="files"></a>

```
Server~/RedRunner.Server.csproj
Server~/Program.cs
Server~/ServerGame.cs
Server~/LevelBehaviour.cs
Server~/PlayerEntity.cs
.gitignore
```

## Triển khai <a href="#implementation" id="implementation"></a>

### Project <a href="#the-project" id="the-project"></a>

`Server~/RedRunner.Server.csproj` biên dịch, dưới dạng mã nguồn: tầng 1 và backend console từ `com.fomoxa.networking`, `Runtime/Rapier` từ `com.fomoxa.networking.rapier`, và các thư mục `Models`, `Generated` và `Simulation` của game. Nó copy `LevelCatalogue.bytes`, các scene file thành `Scenes/<scene id>.fomoxascene` và các thư viện native của Rapier cạnh file chạy. Nó nhắm .NET 8 với C# 9 và coi warning là lỗi. Các thư mục package mặc định là bản clone nằm cạnh thư mục RedRunner:

```xml
<Game>..</Game>
<Core Condition="'$(Core)' == ''">$(Game)/../com.fomoxa.networking</Core>
<Rapier Condition="'$(Rapier)' == ''">$(Game)/../networking-rapier/com.fomoxa.networking.rapier</Rapier>
```

`.gitignore` loại `Server~/bin` và `Server~/obj`.

### Game <a href="#the-game" id="the-game"></a>

`ServerGame` tạo runtime với tick rate 50, backend Rapier và `Play` làm boot scene:

```csharp
var registry = new FomoxaRegistry();
FomoxaAdapters.RegisterAll(registry);
var prefabs = new StandalonePrefabs();
prefabs.Register(FomoxaPrefabs.RedRunnerId, FomoxaPrefabs.RedRunnerFingerprint, () => new PlayerEntity(this));
var behaviours = new StandaloneBehaviours();
behaviours.Register(LevelBehaviour, () => new LevelBehaviour(this));
var settings = new NetworkSettings { TickRate = TickRate, PhysicsBackend = PhysicsBackend.Rapier };
var networkLog = new NetworkLog(exception => log(exception.ToString()), warning => log(warning), error => log(error));
Runtime = StandaloneRuntime.Create(registry, settings, new UdpTransportFactory(), prefabs, behaviours, new SceneFileDirectory(scenes), clock, networkLog, physics, new[] { FomoxaScenes.PlayId });
```

Ở đây `physics` là một `RapierScenes` với trọng lực (0, -9.81, 0), giống `RapierPhysics` của các client. Khi một peer đạt `Started`, `ServerGame` spawn một `PlayerEntity` trong scene `Play` tại điểm spawn của catalogue. `TimeManager.OnPreTick` đưa các chướng ngại của level về prediction tick, như `NetworkLevel.MoveFollowers` làm trong Unity.

`LevelBehaviour.OnStartServer` chọn seed, log `[RedRunner] level seed <seed>` và dựng level bằng `BuiltLevel.Build`, qua một `ILevelPhysics` thêm collider và body vào `RapierScenes` dưới scene id của `Play`.

### Người chơi <a href="#the-player" id="the-player"></a>

`PlayerEntity` là một `StandaloneEntity` với hai behaviour, theo thứ tự `NetworkTransform` và `NetworkPlayer` của prefab:

- `PlayerTransform` gửi tư thế bằng một `TransformSync` có thiết lập khớp `NetworkTransform` của prefab: bật vị trí và scale, tắt góc xoay. `PlayerEntity.Scale` trả về hướng nhìn làm scale X, khiến nhân vật quay đầu trên các client.
- `PlayerBehaviour` đăng ký `PlayerInput`, model reconcile `PlayerMotion` và `PlayerState`, như `NetworkPlayer` làm. `Apply` của nó gọi `RunnerMotion.Simulate` trên `Body2D` của entity, còn tick server của nó gọi `RunnerContacts.Hazard` và kiểm tra rơi, rồi hồi sinh sau thời gian chờ bằng `PlayerEntity.Teleport()`.

`PlayerEntity.TryGetBody2D` trả về body của người chơi trong catalogue, đặt tại vị trí của entity.

### Chương trình <a href="#the-program" id="the-program"></a>

`Program.Main` đọc `-port` (mặc định 7777), `-logFile` và `-log-paths`, load `LevelCatalogue.bytes` từ thư mục của file chạy, và chạy vòng lặp frame: `BeginFrame` và `EndFrame` mỗi frame, ngủ một mili giây giữa các frame.

## Chạy thử <a href="#running-it" id="running-it"></a>

Bạn cần .NET 8 SDK trên Windows x64 hoặc Linux x64. Clone ba repository cạnh nhau:

```
git clone https://github.com/fomoxa/com.fomoxa.networking.git
git clone https://github.com/fomoxa/networking-rapier.git
git clone https://github.com/fomoxa/RedRunner.git
```

Sau đó khởi động server từ thư mục `RedRunner`:

```
dotnet run --project Server~ -c Release -- -port 7777 -logFile server.log
```

Log hiện `[RedRunner] server listening on UDP port 7777`, rồi `[RedRunner] level seed <seed>`. Khởi động game trong Unity Editor hoặc bản build player, nhập địa chỉ server trên màn hình bắt đầu và bấm Play. Khi các package ở chỗ khác, hãy truyền thư mục của chúng bằng đường dẫn tuyệt đối với `-p:Core=<folder>` và `-p:Rapier=<folder>`.

## Kiểm thử <a href="#test" id="test"></a>

Mọi phép kiểm Play Mode vào một server riêng đều chạy với server console: `JoinCheck`, `MoveCheck`, `LifeCheck`, `PathCheck` (với `-log-paths`), `CrowdCheck` và `CrashCheck`. `Tools/unity-windows.sh play-console <check>` build `Server~` bằng .NET SDK của Windows, khởi động nó, chạy phép kiểm trong Editor rồi dừng nó. `PathCheck` so vị trí chướng ngại mà server log với vị trí trên client tại cùng các tick.

## Kết quả mong đợi <a href="#expected-result" id="expected-result"></a>

- `dotnet run` build không có warning và server lắng nghe trên UDP port 7777.
- Client vào, chạy, nhảy, chết trong nước và hồi sinh ở điểm bắt đầu như với server Unity.
- Hai client thấy nhân vật của nhau, và các chướng ngại ở cùng một chỗ trên cả hai tại cùng một tick.

## Commit <a href="#commit" id="commit"></a>

```
Commit: 125e3b8
Message: Add a .NET console server without Unity
```

Xem [`125e3b8`](https://github.com/fomoxa/RedRunner/commit/125e3b8f34182d77bb9184f1a5e192460354bc6b) trên GitHub. Đây là bước cuối của ví dụ.
