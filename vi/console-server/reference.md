# Tham chiếu backend console

Các type của backend console nằm trong namespace `Fomoxa.Networking.Standalone` và được đóng gói dưới dạng mã nguồn trong `Standalone~`. Các type của backend contract nằm ở tầng 1, trong những namespace nêu bên dưới. Các trang [runtime](runtime.md) và [physics](physics.md) giải thích cách dùng chúng.

## StandaloneRuntime <a href="#standaloneruntime" id="standaloneruntime"></a>

`public static class StandaloneRuntime` có một member, `Create`, mà các tham số của nó được liệt kê trong [runtime](runtime.md#standaloneruntimecreate). Nó ném `ArgumentNullException` khi thiếu `prefabs`, `behaviours`, `scenes` hoặc `log`, và `ArgumentException` với boot scene không có scene file.

## StandaloneEntity <a href="#standaloneentity" id="standaloneentity"></a>

`public class StandaloneEntity : INetworkEntity`, với constructor `StandaloneEntity(uint prefabId, IReadOnlyList<EntityBehaviour> behaviours)`.

| Member | Type | Mô tả |
|---|---|---|
| `PrefabId` | `uint` | Prefab id đưa vào constructor; 0 với scene object |
| `SceneObjectId` | `ulong` | Scene object id của một scene object; nếu không thì 0 |
| `SceneId` | `uint` | Đọc và ghi. Scene mà entity thuộc về; 0 nếu không có |
| `DespawnWithOwner` | `bool` | Đọc và ghi; mặc định true |
| `Visibility` | `NetworkVisibility` | Đọc và ghi; mặc định `Rule` |
| `EntityBehaviours` | `IReadOnlyList<EntityBehaviour>` | Các behaviour, theo thứ tự behaviour index |
| `Record` | `EntityRecord` | Bản ghi của entity khi đang spawn; nếu không thì null |
| `Body`, `Body2D` | `PhysicsBody`, `PhysicsBody2D` | Physics body khi đã spawn với một physics backend |
| `Position`, `Rotation`, `Scale` | `Vector3`, `Quaternion`, `Vector3` | Virtual. Đọc và ghi; vị trí và góc xoay đọc và ghi body khi có body |
| `TryGetBody(out BodyDesc)`, `TryGetBody2D(out BodyDesc2D)` | `bool` | Virtual. Body cần tạo lúc spawn; mặc định là body từ scene file |

## StandalonePrefabs <a href="#standaloneprefabs" id="standaloneprefabs"></a>

| Member | Mô tả |
|---|---|
| `void Register(uint prefabId, uint fingerprint, Func<StandaloneEntity> create)` | Đăng ký một factory. Đăng ký cùng id, fingerprint và factory hai lần không làm gì; fingerprint hoặc factory khác cho cùng id thì ném exception. Prefab id 0 cũng ném exception. |

Trên client console, factory phải trả về một entity chưa spawn.

## StandaloneBehaviours <a href="#standalonebehaviours" id="standalonebehaviours"></a>

| Member | Mô tả |
|---|---|
| `void Register(string typeName, Func<EntityBehaviour> create)` | Đăng ký factory cho các behaviour của scene object có type Unity mang tên đầy đủ này |

## Scene file <a href="#scene-files" id="scene-files"></a>

| Type | Mô tả |
|---|---|
| `public interface ISceneFiles` | `bool Knows(uint sceneId)`, `byte[] Read(uint sceneId)` |
| `public sealed class SceneFileDirectory : ISceneFiles` | Đọc `<scene id>.fomoxascene` từ thư mục đưa vào constructor |
| `SceneFileFormat` (`Fomoxa.Networking.Objects`) | `Read(FomoxaRegistry, ReadOnlyMemory<byte>)` và `Write(FomoxaRegistry, SceneFile)`; `Extension` là `.fomoxascene` |
| `SceneFileGeometry` (`Fomoxa.Networking.Objects`) | Chuyển đổi giữa các model scene file với `ColliderDesc`, `BodyDesc` và dạng 2D của chúng |

## Các type tầng 1 mà console dùng <a href="#layer-1-types-the-console-uses" id="layer-1-types-the-console-uses"></a>

| Type | Namespace | Mô tả |
|---|---|---|
| `NetworkRuntime` | `Fomoxa.Networking` | `ServerManager`, `ClientManager`, `TimeManager`, `Physics`, `BeginFrame(TimeSpan now, double elapsedSeconds)`, `EndFrame()`. `Version` là phiên bản package. |
| `NetworkSettings` | `Fomoxa.Networking` | Các thiết lập mà Inspector của `NetworkManager` giữ trong Unity, dưới dạng property với cùng giá trị mặc định, và `PhysicsBackend` |
| `NetworkLog` | `Fomoxa.Networking` | `NetworkLog(Action<Exception> exception, Action<string> warning)`, một overload thêm `Action<string> error`, và `NetworkLog.Console` |
| `EntityBehaviour` | `Fomoxa.Networking` | Class cơ sở của behaviour console, với các callback và phần đăng ký của `NetworkBehaviour` và `SyncTransform(TransformSync, ITransformSource, ITransformReceiver)` |
| `TransformSync`, `TransformSyncSettings` | `Fomoxa.Networking` | Luật gửi của `NetworkTransform`: `TransformSyncSettings(syncPosition, syncRotation, syncScale, positionThreshold, rotationThreshold, scaleThreshold)`, `TransformSync.Teleport()` |
| `ITransformSource`, `ITransformReceiver`, `TransformSample` | `Fomoxa.Networking` | `ReadLocal(out position, out rotation, out scale)` trên server; `ResetReceive()` và `Receive(in TransformSample)` trên client |
| `INetworkEntity`, `EntityRecord` | `Fomoxa.Networking` | Interface mà manager spawn, và bản ghi của một entity đã spawn: `ObjectId`, `OwnerId`, `IsOwner`, `OnServer`, `OnClient`, `Representation` |

## Backend contract <a href="#backend-contract" id="backend-contract"></a>

`StandaloneRuntime.Create` dựng một `NetworkBackends` từ các interface này. Backend cho engine khác hiện thực chúng và tự truyền một `NetworkBackends` vào constructor của `NetworkRuntime`.

| Interface | Namespace | Vai trò |
|---|---|---|
| `IServerEntityBackend` | `Fomoxa.Networking.Objects` | Kiểm tra spawn, cho fingerprint và scene id, chuẩn bị, kích hoạt và kết thúc entity trên server |
| `IServerSceneHost` | `Fomoxa.Networking.Objects` | Load và unload scene trên server, đưa ra scene object của boot scene, liệt kê scene object của một scene |
| `IClientEntityBackend` | `Fomoxa.Networking.Objects` | Tạo entity cho các lần spawn, đặt scene object, kết thúc entity và ẩn hoặc hiện chúng trên host |
| `ISceneHost` | `Fomoxa.Networking.Objects` | Load và unload scene trên client |
| `IClientPredictionBackend` | `Fomoxa.Networking.Prediction` | Các world và history của entity được dự đoán, proxy, và lúc bắt đầu, kết thúc một lần sửa |
| `IPhysicsWorlds`, `IPhysicsScenes` | `Fomoxa.Networking.Simulation` | Physics cho vòng tick, và physics theo scene id cho backend console |

Constructor là `NetworkRuntime(FomoxaRegistry registry, NetworkSettings settings, ITransportFactory transport, NetworkBackends backends, Func<TimeSpan> clock, NetworkLog log)`.
