# Physics

Server console không có physics của Unity. Nó mô phỏng physics qua một `IPhysicsScenes` truyền vào `StandaloneRuntime.Create`, và [backend Rapier](../rapier/overview.md) cung cấp một cái, `RapierScenes`. Client Unity khi đó dùng `RapierPhysics`, nên hai phía chạy cùng các world Rapier từ cùng scene file.

## Thêm Rapier vào project <a href="#adding-rapier-to-the-project" id="adding-rapier-to-the-project"></a>

Assembly `Fomoxa.Networking.Rapier`, trong `Runtime/Rapier` của package `com.fomoxa.networking.rapier`, không tham chiếu Unity. Project console biên dịch nó như tầng 1 và copy thư viện native cạnh file chạy:

```xml
<PropertyGroup>
  <Rapier Condition="'$(Rapier)' == ''">$(Game)/../networking-rapier/com.fomoxa.networking.rapier</Rapier>
</PropertyGroup>

<ItemGroup>
  <Compile Include="$(Rapier)/Runtime/Rapier/**/*.cs" />
</ItemGroup>

<ItemGroup>
  <None Include="$(Rapier)/Runtime/Plugins/Linux/x86_64/libfomoxa_rapier.so" Link="libfomoxa_rapier.so" CopyToOutputDirectory="PreserveNewest" />
  <None Include="$(Rapier)/Runtime/Plugins/Windows/x86_64/fomoxa_rapier.dll" Link="fomoxa_rapier.dll" CopyToOutputDirectory="PreserveNewest" />
</ItemGroup>
```

Ở đây `$(Rapier)` là một bản clone của [networking-rapier](https://github.com/fomoxa/networking-rapier) nằm cạnh các thư mục khác.

## Tạo runtime <a href="#creating-the-runtime" id="creating-the-runtime"></a>

```csharp
var physics = new RapierScenes(new Vector3(0f, -9.81f, 0f));
var settings = new NetworkSettings { PhysicsBackend = PhysicsBackend.Rapier };
NetworkRuntime runtime = StandaloneRuntime.Create(
    registry, settings, new UdpTransportFactory(), prefabs, behaviours,
    new SceneFileDirectory(scenesFolder), () => clock.Elapsed, NetworkLog.Console,
    physics, new[] { FomoxaScenes.GameId });
```

`NetworkSettings.PhysicsBackend` phải là `Rapier`, vì server báo cho mỗi client backend của nó và client có `RapierPhysics` sẽ dừng với `PhysicsBackendMismatch` nếu không khớp. Hãy dùng trọng lực của `RapierPhysics` trên client. Dispose `RapierScenes` khi chương trình kết thúc, sau `ServerManager.StopConnection()`, để giải phóng các world native.

`RapierScenes` giữ một world cho mỗi scene id và mỗi chiều. Scene file của mỗi boot scene và của mỗi network scene được load thêm các collider tĩnh và ma trận va chạm layer của nó vào các world của scene đó.

## Body của entity <a href="#bodies-of-entities" id="bodies-of-entities"></a>

Khi một entity spawn, backend console hỏi nó về body và thêm body đó vào các world của `SceneId` của entity:

- Scene object dùng body được mô tả trong scene file, do Editor ghi từ collider và `Rigidbody` hoặc `Rigidbody2D` của nó.
- Entity từ prefab override `TryGetBody` hoặc `TryGetBody2D` và trả về một `BodyDesc` hoặc `BodyDesc2D`. Backend đặt nó tại vị trí và góc xoay của entity.

Sau khi spawn, `StandaloneEntity.Body` và `Body2D` trả về body, còn `Position` và `Rotation` đọc và ghi nó, nên transform sync và code game thấy tư thế đã mô phỏng. Despawn gỡ body.

```csharp
public override bool TryGetBody2D(out BodyDesc2D body)
{
    var collider = new ColliderDesc2D(BodyShape2D.Capsule(0.3f, 0.4f), Vector2.Zero, 0f, ColliderMaterial.Default, 0, false);
    body = new BodyDesc2D(BodyKind.Dynamic, new[] { collider }, Vector2.Zero, 0f, 1f, new BodyMotion2D(BodyLocks2D.Rotation, 1f, 0f, 0f));
    return true;
}
```

Mô tả phải khớp với mô tả mà client Unity dựng từ collider của prefab, nếu không server và client dự đoán mô phỏng hai body khác nhau. Một cách giữ chúng bằng nhau là xuất các mô tả từ Editor bằng `BodyDescriptions.TryDescribe2D` vào một file mà server console đọc, như [ví dụ Red Runner](../examples/redrunner/rapier-and-console/step-12-level-catalogue.md) làm.

## Geometry level và body không chủ <a href="#level-geometry-and-unowned-bodies" id="level-geometry-and-unowned-bodies"></a>

`RapierScenes` có cùng các member lúc chạy như `NetworkPhysics`, theo scene id thay vì `Scene`: `AddStatic(sceneId, colliders)`, `AddStatic2D`, `RemoveStatic`, `AddBody(sceneId, body)`, `AddBody2D`, `RemoveBody` và `RemoveBody2D`. `WorldOf(sceneId)` và `WorldOf2D(sceneId)` trả về các world, mà method `Touching` của chúng đọc tập contact như mô tả trong [body và collider của Rapier](../rapier/bodies.md#reading-the-worlds). Hãy dựng geometry lúc chạy theo cùng thứ tự như client.

Backend console không chạy các component contact event, vì chúng là component của Unity. Luật server phụ thuộc contact thì đọc tập contact của các world.

## Prediction trên client console <a href="#prediction-on-console-clients" id="prediction-on-console-clients"></a>

Client console tạo với một `RapierScenes` dự đoán và rollback entity của nó như client Unity, qua `IPhysicsScenes.HistoryOf`, `PlaceProxy` và `EndProxy`.
