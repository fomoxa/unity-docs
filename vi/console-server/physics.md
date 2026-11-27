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

`RapierScenes` giữ một world cho mỗi bản scene và mỗi chiều, khóa theo `NetworkScene`. Khi server load một bản, scene file của scene đó thêm các collider tĩnh, ma trận va chạm layer và [effector 2D](../rapier/effectors.md) trên collider tĩnh của nó vào các world của bản, nên hai phòng của một map có hai world, và unload bản thì giải phóng các world đó. Boot scene và entity nằm ngoài network scene dùng các world của `default(NetworkScene)`, giữ vai world mặc định của Unity: file của mọi boot scene đều thêm geometry vào đó. Ma trận va chạm layer lấy từ cài đặt của project, nên mọi scene file của một bản build mang cùng một ma trận.

## Body của entity <a href="#bodies-of-entities" id="bodies-of-entities"></a>

Khi một entity spawn, backend console hỏi nó về body và thêm body đó vào các world của `Scene` của entity, hoặc vào các world mặc định khi `Scene` là `default`:

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

## Nhiều body <a href="#several-bodies" id="several-bodies"></a>

Prefab Unity có `Rigidbody` trên nhiều GameObject thì có [nhiều body](../physics/overview.md#several-bodies). Entity console khai cùng các body đó bằng cách override `GetChildBodies` hoặc `GetChildBodies2D`. Mỗi `ChildBodyDesc` giữ một `BodyDesc` và pose của body con so với entity, không tính scale; `ChildBodyDesc2D` nhận một `BodyDesc2D`, vị trí `Vector2` và góc theo radian:

```csharp
public override void GetChildBodies2D(List<ChildBodyDesc2D> into)
{
    var wheel = new ColliderDesc2D(BodyShape2D.Circle(0.25f), Vector2.Zero, 0f, ColliderMaterial.Default, 0, false);
    into.Add(new ChildBodyDesc2D(new BodyDesc2D(BodyKind.Dynamic, new[] { wheel }, Vector2.Zero, 0f, 0.5f), new Vector2(-0.6f, -0.4f), 0f));
    into.Add(new ChildBodyDesc2D(new BodyDesc2D(BodyKind.Dynamic, new[] { wheel }, Vector2.Zero, 0f, 0.5f), new Vector2(0.6f, -0.4f), 0f));
}
```

Backend đọc danh sách một lần, khi tạo body, và đặt mỗi body con ở pose của entity kết hợp với pose cục bộ của body con. Sau đó `Bodies` và `Bodies2D` liệt kê body gốc trước, nếu có, rồi tới các body con theo thứ tự của danh sách, như `NetworkObject.Bodies` trong Unity. Hãy giữ thứ tự đó trùng với thứ tự trong hierarchy của các component `Rigidbody` của prefab.

Behaviour gửi pose của một body con bằng `SyncTransform(sync, ChildBody.Of2D(index), receiver)`, với `index` là vị trí trong `GetChildBodies2D` (`ChildBody.Of` cho 3D). Lời gọi này thay cho `NetworkTransform` trên GameObject con trong Unity. Pose được gửi tương đối với entity, và `SyncScale` phải tắt vì body không có scale. Body con không có slot như vậy thì client console tự mô phỏng, như trên client Unity.

Scene object lấy body con từ scene file, do Editor ghi từ các component `Rigidbody` dưới mỗi scene object theo cùng quy tắc với [nhiều body](../physics/overview.md#several-bodies). Behaviour của chúng biết được GameObject của mình mang body nào qua overload `BehaviourSite` của `StandaloneBehaviours.Register`, mô tả ở mục [scene object](runtime.md#scene-objects-and-boot-scenes).

## Geometry level và body không chủ <a href="#level-geometry-and-unowned-bodies" id="level-geometry-and-unowned-bodies"></a>

`RapierScenes` có cùng các member lúc chạy như `NetworkPhysics`, theo `NetworkScene` thay vì `Scene`: `AddStatic(scene, colliders)`, `AddStatic2D`, `RemoveStatic`, `AddBody(scene, body)`, `AddBody2D`, `RemoveBody` và `RemoveBody2D`. `WorldOf(scene)` và `WorldOf2D(scene)` trả về các world, `WorldOf(default)` trả về world mặc định, mà method `Touching` của chúng đọc tập contact như mô tả trong [body và collider của Rapier](../rapier/bodies.md#reading-the-worlds). Hãy dựng geometry lúc chạy theo cùng thứ tự như client.

Backend console không chạy các component contact event, vì chúng là component của Unity. Luật server phụ thuộc contact thì đọc tập contact của các world.

## Prediction trên client console <a href="#prediction-on-console-clients" id="prediction-on-console-clients"></a>

Client console tạo với một `RapierScenes` dự đoán và rollback entity của nó như client Unity, qua `IPhysicsScenes.HistoryOf`, `PlaceProxy` và `EndProxy`.
