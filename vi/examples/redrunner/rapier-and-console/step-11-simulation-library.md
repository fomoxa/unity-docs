# Bước 11: Thư viện mô phỏng

## Mục tiêu <a href="#goal" id="goal"></a>

Bước này đưa luật game ra khỏi code Unity vào một assembly không tham chiếu `UnityEngine`, để một server không có Unity chạy được cùng các luật đó. Game chơi giống hệt sau bước 10.

## Điểm xuất phát <a href="#starting-point" id="starting-point"></a>

Game trên backend Rapier, commit `beb18a4`.

## Vấn đề <a href="#problem" id="problem"></a>

Sau bước 10, các luật quyết định chuyện xảy ra trong một tick nằm rải rác trên các component Unity. `RedCharacter.Simulate` chạy và nhảy bằng `Mathf.SmoothDamp` và `transform.localScale`, `NetworkPlayer` đọc tập contact và ánh xạ chúng qua collider Unity, `PathFollower` dựng chu kỳ của nó bằng `Vector3.MoveTowards`, và `TerrainGenerationSettings.Layout` bố trí level bằng `System.Random`. Một server console không biên dịch được cái nào trong số đó.

`System.Random` còn một vấn đề nữa. Level giống nhau trên mọi peer chỉ vì mỗi peer lấy cùng các số từ seed, mà .NET không hứa `System.Random` giữ nguyên thuật toán qua các phiên bản, trong khi Unity chạy Mono còn server console chạy .NET.

## Khái niệm Fomoxa <a href="#fomoxa-concepts" id="fomoxa-concepts"></a>

- [Tính tất định của Rapier](../../../rapier/determinism.md)
- [Server console: code game dùng chung với Unity](../../../console-server/project.md#game-code-shared-with-unity)

## Thiết kế <a href="#design" id="design"></a>

`Assets/Scripts/RedRunner/Simulation/` trở thành assembly `RedRunner.Simulation`, bật `noEngineReferences` và tham chiếu `Fomoxa.Networking` và `Fomoxa.Networking.Rapier`. Nó chứa:

| Type | Thay thế |
|---|---|
| `RunnerMotion`, `RunnerSettings` | Phần mạng của `RedCharacter.Simulate`: chạy, nhảy và lăn trên một `PhysicsBody2D` |
| `ISurfaces`, `Surface`, `RunnerContacts` | Luật chạm đất và hiểm họa của `NetworkPlayer`, trên tập contact của Rapier |
| `PathCycle`, `PathStop` | Chu kỳ của một path follower |
| `Smoothing` | `Mathf.SmoothDamp`, `Vector3.SmoothDamp`, `Vector3.MoveTowards` và `Vector3.Lerp`, với công thức của Unity trên `System.Numerics` |
| `LevelLayout`, `SeededRandom` | Bố cục level theo seed của `TerrainGenerationSettings` |

Các component Unity giữ phần hiển thị, hoạt ảnh, hạt và âm thanh, và gọi vào thư viện cho các luật. Các method chơi đơn của `RedCharacter` giữ nguyên.

## File <a href="#files" id="files"></a>

```
Assets/Scripts/RedRunner/Simulation/RedRunner.Simulation.asmdef
Assets/Scripts/RedRunner/Simulation/RunnerMotion.cs
Assets/Scripts/RedRunner/Simulation/Surfaces.cs
Assets/Scripts/RedRunner/Simulation/PathCycle.cs
Assets/Scripts/RedRunner/Simulation/Smoothing.cs
Assets/Scripts/RedRunner/Simulation/LevelLayout.cs
Assets/Scripts/RedRunner/Simulation/SeededRandom.cs
Assets/Scripts/RedRunner/Characters/RedCharacter.cs
Assets/Scripts/RedRunner/Networking/NetworkPlayer.cs
Assets/Scripts/RedRunner/Networking/NetworkLevel.cs
Assets/Scripts/RedRunner/Utilities/PathFollower.cs
Assets/Scripts/RedRunner/TerrainGeneration/TerrainGenerationSettings.cs
Tools/PortChecks/Editor/PortLayout.cs
```

## Triển khai <a href="#implementation" id="implementation"></a>

### Assembly <a href="#the-assembly" id="the-assembly"></a>

`RedRunner.Simulation.asmdef` (rút gọn; các field khác có giá trị mặc định):

```json
{
    "name": "RedRunner.Simulation",
    "rootNamespace": "RedRunner.Simulation",
    "references": [
        "Fomoxa.Networking",
        "Fomoxa.Networking.Rapier"
    ],
    "autoReferenced": true,
    "noEngineReferences": true
}
```

`autoReferenced` cho phép các script của chính game trong `Assembly-CSharp` dùng nó mà không cần assembly definition riêng. Code trong thư mục bị giới hạn ở C# 9, phiên bản Unity biên dịch.

### Chuyển động của nhân vật <a href="#character-motion" id="character-motion"></a>

`RunnerMotion.Simulate` nhận body, thiết lập, input, nhân vật có đang chạm đất không và có đang chết không, rồi trả về những hành động đã xảy ra để Unity chạy hiệu ứng của chúng:

```csharp
public RunnerActions Simulate(PhysicsBody2D body, in RunnerSettings settings, float move, bool jump, bool roll, bool grounded, bool dead, float deltaTime)
```

Hướng nhìn, trước đây là dấu của `transform.localScale.x`, nay là `RunnerMotion.Facing`, và `RedCharacter` áp nó vào scale để hiển thị. `NetworkPlayer` nay đặt `BodySource` với cả hai backend, vì chuyển động luôn đi qua `PhysicsBody2D`; với `RigidbodyPhysics`, `NetworkObject.Body2D` là body PhysX của nhân vật.

### Contact <a href="#contacts" id="contacts"></a>

`RunnerContacts.Grounded(world, body, sensorIndex, surfaces, scratch)` và `RunnerContacts.Hazard(world, body, colliderCount, bottom, surfaces, scratch)` đọc tập contact bằng `RapierWorld2D.Touching` và hỏi một `ISurfaces` mỗi collider là gì. `NetworkLevel` hiện thực `ISurfaces` từ các collider nguồn nó đã ghi lại ở bước 10, và `NetworkPlayer` đổi `Surface` mà `Hazard` trả về thành một `DeathCause`.

### Bố cục level <a href="#the-level-layout" id="the-level-layout"></a>

`LevelLayout.Lay(seed, ...)` bố trí các block từ độ rộng và xác suất của chúng, như `TerrainGenerationSettings.Layout` đã làm, nhưng lấy số từ `SeededRandom`, một bộ sinh SplitMix64 chỉ dùng số học số nguyên:

```csharp
public ulong NextBits()
{
    state += Golden;
    ulong mixed = state;
    mixed = (mixed ^ (mixed >> 30)) * 0xBF58476D1CE4E5B9UL;
    mixed = (mixed ^ (mixed >> 27)) * 0x94D049BB133111EBUL;
    return mixed ^ (mixed >> 31);
}
```

Vì vậy cùng một seed nay cho bố cục khác trước bước này. Server chọn seed mới mỗi lần khởi động, nên không có gì được lưu lại phụ thuộc vào bố cục cũ.

## Kiểm thử <a href="#test" id="test"></a>

`PortLayout.Seeds` bố trí năm seed và so hash của mỗi bố cục với giá trị tính dưới .NET 8, cho thấy Mono trong Editor và .NET bố trí cùng một level. Các phép kiểm Play Mode của bước 10 chạy không đổi, vì các luật không đổi. Bên ngoài Unity, `dotnet build` một project biên dịch thư mục đó thành công.

## Kết quả mong đợi <a href="#expected-result" id="expected-result"></a>

- Project biên dịch được, và `RedRunner.Simulation` không có tham chiếu tới `UnityEngine`.
- Game chơi như sau bước 10, trên một bố cục mới cho mỗi seed.

## Commit <a href="#commit" id="commit"></a>

```
Commit: d8a30c4
Message: Move the game simulation into RedRunner.Simulation
```

Xem [`d8a30c4`](https://github.com/fomoxa/RedRunner/commit/d8a30c4e8f1baef53fc3125eddeb5a6b9d63c93d) trên GitHub, rồi tiếp tục với [bước 12: catalogue level](step-12-level-catalogue.md).
