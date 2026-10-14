# Bước 12: Catalogue level

## Mục tiêu <a href="#goal" id="goal"></a>

Bước này dựng phần Rapier của level từ một level catalogue, một file mà Editor xuất ra từ các prefab block. Một tiến trình không có Unity khi đó dựng được cùng level physics từ seed. Game chơi như sau bước 11.

## Điểm xuất phát <a href="#starting-point" id="starting-point"></a>

Game với luật nằm trong `RedRunner.Simulation`, commit `d8a30c4`.

## Vấn đề <a href="#problem" id="problem"></a>

Ở bước 10, collider và body của level đến từ các prefab block mà `TerrainGenerator` instantiate, được mô tả bằng `BodyDescriptions` lúc chạy. Chỉ Unity mới instantiate được prefab và đọc collider của chúng. Server console cần cùng các mô tả đó ở dạng nó đọc được, và client với server phải dựng chúng theo cùng thứ tự với cùng con số.

## Khái niệm Fomoxa <a href="#fomoxa-concepts" id="fomoxa-concepts"></a>

- [Model và codec](../../../messaging/models.md)
- [Physics của console: body của entity](../../../console-server/physics.md#bodies-of-entities)
- [Scene file](../../../advanced/editor-integration.md#scene-files), mà các model collider của nó catalogue dùng lại

## Thiết kế <a href="#design" id="design"></a>

Catalogue là một model được mã hóa bằng codec sinh ra của nó, nên không cần định dạng file riêng:

| Model | Giữ |
|---|---|
| `LevelCatalogue` | Độ dài tick lúc xuất, số block của mỗi phần, các block start, middle và end, và người chơi |
| `CatalogueBlock` | Độ rộng và xác suất; các collider tĩnh tương đối với block, mỗi cái kèm `Surface` và đỉnh của nó; các body không chủ |
| `CatalogueBody` | Vị trí trong block, mô tả body, `Surface` và đỉnh của từng collider, và chu kỳ đường đi tại tick của game |
| `CataloguePlayer` | Body của nhân vật kèm sensor chân, chỉ số sensor, độ lệch đáy capsule, thiết lập chạy, điểm spawn, thời gian chờ hồi sinh và giới hạn số tick lặp |

Collider và body dùng lại các model `SceneFileCollider2D` và `SceneFileBody2D` của package, mà `SceneFileGeometry` chuyển qua lại với `ColliderDesc2D` và `BodyDesc2D`. Thư mục model trở thành assembly `RedRunner.Models` không tham chiếu Unity, để `RedRunner.Simulation` dùng được các type catalogue.

`LevelBuilder` trong `RedRunner.Simulation` dựng level từ catalogue và seed qua một `ILevelPhysics`, mà game Unity hiện thực bằng `RapierPhysics` và server console bằng `RapierScenes`. Client Unity cũng dựng level Rapier của nó từ catalogue, và chỉ giữ các prefab đã instantiate để hiển thị.

## File <a href="#files" id="files"></a>

```
Assets/Scripts/RedRunner/Networking/Models/RedRunner.Models.asmdef
Assets/Scripts/RedRunner/Networking/Models/LevelCatalogue.cs
Assets/Scripts/RedRunner/Networking/LevelCatalogue.bytes
Assets/Editor/RedRunner/Networking/LevelCatalogueExport.cs
Assets/Scripts/RedRunner/Simulation/LevelBuilder.cs
Assets/Scripts/RedRunner/Simulation/RedRunner.Simulation.asmdef
Assets/Scripts/RedRunner/Networking/NetworkLevel.cs
Assets/Scripts/RedRunner/Networking/NetworkPlayer.cs
Assets/Scripts/RedRunner/Utilities/PathFollower.cs
Assets/Scenes/Play.unity
Tools/PortChecks/Editor/PortCatalogue.cs
```

## Triển khai <a href="#implementation" id="implementation"></a>

### Các model <a href="#the-models" id="the-models"></a>

`LevelCatalogue.cs` (rút gọn):

```csharp
[Network]
[Codec("net")]
public class CatalogueBlock
{
    [Network("f32")]
    [Codec("net")]
    public float Width { get; set; }

    [Network("f32")]
    [Codec("net")]
    public float Probability { get; set; }

    [Network("Array<SceneFileCollider2D>")]
    [Codec("net")]
    public List<SceneFileCollider2D> Statics { get; set; } = new List<SceneFileCollider2D>();

    [Network("Array<CatalogueBody>")]
    [Codec("net")]
    public List<CatalogueBody> Bodies { get; set; } = new List<CatalogueBody>();
}
```

Các model không bao giờ được gửi qua mạng. Chúng chỉ dùng codec sinh ra để ghi và đọc file.

### Xuất <a href="#export" id="export"></a>

Tools > RedRunner > Export Level Catalogue mở `Play.unity` nếu cần và đọc tick rate của `Network Manager`, điểm spawn và thiết lập sinh level của `Terrain Generator`. Với mỗi prefab block, nó mô tả các collider tĩnh và các body không dynamic theo luật của bước 10, ghi lại `Surface` và đỉnh của từng collider, và ghi lại chu kỳ của mỗi path follower ở độ dài tick đó. Với người chơi, nó mô tả `RedRunner.prefab` tại điểm spawn, có thêm sensor chân. Nó ghi `Assets/Scripts/RedRunner/Networking/LevelCatalogue.bytes`, file được commit và gán vào field Catalogue của `NetworkLevel` trong `Play.unity`.

Hãy xuất lại catalogue mỗi khi prefab block, thiết lập sinh level hoặc tick rate thay đổi.

### Dựng level <a href="#build-the-level" id="build-the-level"></a>

```csharp
public static BuiltLevel Build(LevelCatalogue catalogue, int seed, float tickDelta, ILevelPhysics physics)
```

`BuiltLevel.Build` bố trí các block bằng `LevelLayout.Lay` từ độ rộng và xác suất của catalogue. Với mỗi block theo thứ tự bố cục, nó thêm một nhóm tĩnh, gồm các collider của catalogue dời tới X của block, rồi từng body không chủ. Nó ném exception khi `tickDelta` khác của catalogue, vì chu kỳ đường đi được lưu theo tick. `BuiltLevel` hiện thực `ISurfaces` từ các surface đã ghi, và `Move(tick)` đặt mọi body di chuyển về vị trí trong chu kỳ của nó.

`NetworkLevel` nay dựng level Rapier của nó như sau:

```csharp
var physics = new RapierLevelPhysics(rapier, gameObject.scene, m_Game.Manager.Scenes.IdOf(gameObject.scene.path));
m_Built = BuiltLevel.Build(Read(m_Catalogue.bytes), (int)m_State.Seed, (float)m_Game.Manager.TimeManager.TickDelta, physics);
```

`RapierLevelPhysics` thêm collider và body bằng `rapier.AddStatic2D` và `rapier.AddBody2D`, và trả về `rapier.Scenes.WorldOf2D(sceneId)` làm world. Mỗi path follower của các block hiển thị được điều khiển bởi chu kỳ của body catalogue cùng chỉ số, nên thứ người chơi thấy di chuyển theo body Rapier. `NetworkLevel.SurfaceOf`, hàm mà `NetworkPlayer` truyền cho `RunnerContacts`, nay trả lời từ `BuiltLevel` thay vì tra collider Unity.

## Kiểm thử <a href="#test" id="test"></a>

`PortCatalogue.Matches` xuất lại catalogue trong bộ nhớ và so từng byte với file đã commit. Nó thất bại kèm gợi ý xuất lại khi prefab không còn khớp. `PortLayout.Seeds` và các phép kiểm Play Mode của bước 10 chạy không đổi.

## Kết quả mong đợi <a href="#expected-result" id="expected-result"></a>

- `LevelCatalogue.bytes` khoảng 240 KB. Phần lớn là chu kỳ đường đi của các chướng ngại di chuyển.
- Game chơi như sau bước 11, và chùy hoặc lưỡi cưa ở cùng một chỗ trên mọi client tại cùng một tick.

## Commit <a href="#commit" id="commit"></a>

```
Commit: c44bcfe
Message: Build the Rapier level from an exported level catalogue
```

Xem [`c44bcfe`](https://github.com/fomoxa/RedRunner/commit/c44bcfee259504c213a1542353a012b0f07d0805) trên GitHub, rồi tiếp tục với [bước 13: server console](step-13-console-server.md).
