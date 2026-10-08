# Bước 10: Backend Rapier

## Mục tiêu <a href="#goal" id="goal"></a>

Bước này chạy game online trên physics backend Rapier. Server và các client mô phỏng nhân vật, level và chướng ngại di chuyển trong các world Rapier, và server quyết định cái chết từ tập contact của Rapier thay vì callback của PhysX.

## Điểm xuất phát <a href="#starting-point" id="starting-point"></a>

Game online ở cuối phần một, commit `f164d56`, với một `RigidbodyPhysics` trên `Network Manager`.

## Vấn đề <a href="#problem" id="problem"></a>

Với `RigidbodyPhysics`, replay trên client của owner bắt đầu từ một state đã lưu không có contact, nên sau một lần sửa nhân vật có thể tiếp đất hơi khác và bị sửa lần nữa. Rapier lưu cả world, nhưng chuyển sang nó làm thay đổi ba điều mà game đã dựa vào:

- Rapier dựng geometry tĩnh từ scene file, mà scene file chỉ biết các collider đã lưu trong `Play.unity`. Các block của level được instantiate lúc chạy từ seed, nên Rapier không thấy chúng.
- Rapier tự di chuyển body và ghi tư thế ngược lại vào `Transform`, nên code đặt `Rigidbody2D.linearVelocity` hoặc gọi `AddForce` không còn di chuyển nhân vật.
- Kẻ thù giết nhân vật từ `OnCollisionEnter2D` và `OnTriggerEnter2D`, và việc kiểm tra chạm đất bắn ray, tất cả qua physics của Unity. Dưới Rapier nhân vật do Rapier di chuyển, nên server cần quyết định cái chết và chạm đất từ contact của Rapier.

## Khái niệm Fomoxa <a href="#fomoxa-concepts" id="fomoxa-concepts"></a>

- [Cài đặt Rapier](../../../rapier/setup.md)
- [Body và collider](../../../rapier/bodies.md), đặc biệt là [đọc world](../../../rapier/bodies.md#reading-the-worlds)
- [Geometry và body thêm lúc chạy](../../../physics/overview.md#geometry-and-bodies-added-at-runtime)
- [PhysicsBody](../../../physics/physics-body.md)

## Thiết kế <a href="#design" id="design"></a>

`NetworkLevel` thêm level vào Rapier sau khi dựng các block từ seed, trên server và trên mọi client, theo thứ tự vị trí X của block. Mỗi block thành một nhóm tĩnh gồm các collider của nó. Các object `Rigidbody2D` không dynamic của block thành body không chủ: gai là body tĩnh, còn chùy và lưỡi cưa là body kinematic mà `NetworkLevel` đặt về vị trí của tick. Đồng xu và rương ở ngoài Rapier, vì chúng chỉ là đồ trang trí cục bộ.

Nhân vật di chuyển qua `PhysicsBody2D` của nó. Việc kiểm tra chạm đất hỏi một sensor ở chân xem nó chạm collider nào, và server hỏi các collider của nhân vật xem chúng chạm hiểm họa nào. Để đổi một `RapierCollider` ngược về collider Unity nguồn, `NetworkLevel` giữ một bảng từ chỉ số tĩnh và handle của body tới các collider nguồn.

## File <a href="#files" id="files"></a>

```
Packages/manifest.json
Assets/Scenes/Play.unity
Assets/Scripts/RedRunner/Networking/NetworkLevel.cs
Assets/Scripts/RedRunner/Networking/NetworkPlayer.cs
Assets/Scripts/RedRunner/Characters/RedCharacter.cs
Assets/Scripts/RedRunner/Utilities/GroundCheck.cs
```

## Triển khai <a href="#implementation" id="implementation"></a>

### Cài backend <a href="#install-the-backend" id="install-the-backend"></a>

Thêm package từ Git URL, như mô tả trong [cài đặt Rapier](../../../rapier/setup.md#install-the-package). `Packages/manifest.json` khi đó có:

```json
"com.fomoxa.networking.rapier": "https://github.com/fomoxa/networking-rapier.git?path=com.fomoxa.networking.rapier",
```

Trên `Network Manager` trong `Play.unity`, gỡ `RigidbodyPhysics`, thêm `RapierPhysics` với trọng lực mặc định, và kéo nó vào field Physics. Hệ số trọng lực 1.5 và khóa xoay của nhân vật lấy từ `Rigidbody2D` của nó, mà backend đọc vào mô tả body.

### Thêm level vào Rapier <a href="#add-the-level-to-rapier" id="add-the-level-to-rapier"></a>

`NetworkLevel.cs`, sau `m_Generator.Build`:

```csharp
private void AddToRapier(RapierPhysics rapier)
{
    foreach (PathFollower follower in m_Followers)
    {
        if (!follower.TryGetComponent(out Rigidbody2D _))
        {
            follower.gameObject.AddComponent<Rigidbody2D>().bodyType = RigidbodyType2D.Kinematic;
        }
    }

    foreach (Block block in FindObjectsByType<Block>(FindObjectsSortMode.None).OrderBy(block => block.transform.position.x))
    {
        AddStatics(rapier, block.gameObject);
        AddBodies(rapier, block.gameObject);
    }

    World = rapier.Scenes.WorldOf2D(m_Game.Manager.Scenes.IdOf(gameObject.scene.path));
}
```

Path follower được thêm một `Rigidbody2D` kinematic để collider của nó được tính là body thay vì geometry tĩnh. `AddStatics` mô tả các collider tĩnh của một block bằng `BodyDescriptions.StaticColliders2D` và `DescribeStatic2D`, bỏ qua collider của collectable, rồi thêm chúng bằng `rapier.AddStatic2D(gameObject.scene, colliders)`; nó ghi lại collider nguồn của từng chỉ số bắt đầu từ `StaticGroup.FirstIndex`. `AddBodies` mô tả từng `Rigidbody2D` không dynamic của block bằng `BodyDescriptions.TryDescribe2D` và thêm nó bằng `rapier.AddBody2D`, khóa theo handle của body.

Mỗi tick, `MoveFollowers` đặt body của mỗi chùy và lưỡi cưa về vị trí trong chu kỳ của nó ở tick đó, và đưa cả `Transform` của nó tới đó, vì PhysX không còn di chuyển nó:

```csharp
Vector3 position = follower.PositionAt(tick);
BodyState2D state = body.State;
state.Position = new System.Numerics.Vector2(position.x, position.y);
body.State = state;
follower.transform.position = position;
```

### Di chuyển nhân vật qua body của nó <a href="#move-the-character-through-its-body" id="move-the-character-through-its-body"></a>

`RedCharacter` có thêm `BodySource` trả về `PhysicsBody2D` của nhân vật. Việc đọc ghi vận tốc và lực lăn đi qua body đó khi nó hợp lệ:

```csharp
Fomoxa.Networking.Simulation.PhysicsBody2D body = BodySource ();
if ( body.IsValid )
{
    body.Velocity = new System.Numerics.Vector2 ( value.x, value.y );
    return;
}
```

`NetworkPlayer.Awake` đặt `BodySource` thành `NetworkObject.Body2D` khi `Network Manager` có `RapierPhysics`.

### Chạm đất và hiểm họa từ tập contact <a href="#ground-and-hazards-from-contact-sets" id="ground-and-hazards-from-contact-sets"></a>

`GroundCheck` có thêm `Probe`, thay thế ba tia của nó khi được đặt. `NetworkPlayer` thêm một trigger `Ground Sensor` dưới collider chạm đất của nhân vật, rộng bằng collider đó và cao bằng khoảng cách tia, và đặt probe thành:

```csharp
private bool Grounded()
{
    if (!TryGetContacts(m_Sensor))
    {
        return false;
    }

    foreach (RapierCollider other in m_Touching)
    {
        Collider2D source = m_Level.SourceOf(other);
        if (source != null && source.gameObject.layer == LayerMask.NameToLayer(GroundName) && source.CompareTag(GroundName))
        {
            return true;
        }
    }

    return false;
}
```

`TryGetContacts` tìm chỉ số của từng collider của nhân vật bằng `BodyDescriptions.TryDescribe2D(gameObject, out _, m_Sources)` và gọi `World.Touching(RapierCollider.OfBody(body.Handle, index), m_Touching)`.

Trên server, `RedCharacter.DecidesDeath` nay là false dưới Rapier, và `NetworkPlayer.ServerTick` gọi `DieOfHazards` trước kiểm tra rơi. Nó tra `Enemy` phía trên mỗi collider nguồn đang chạm: nước, lưỡi cưa và chùy giết ngay, còn gai giết khi đáy capsule của nhân vật không thấp hơn đỉnh gai quá 0.2.

### Body của nhân vật chết và hồi sinh <a href="#dead-bodies-and-respawns" id="dead-bodies-and-respawns"></a>

PhysX ngừng mô phỏng nhân vật đã chết, vì bộ xương tắt `Rigidbody2D` của nó. Rapier vẫn tiếp tục mô phỏng body, nên nó chìm qua nước và kéo nhân vật được nội suy trên các client khác xuống theo. `HoldWhileDead` giữ body tại vị trí lúc chết, không có vận tốc, trên server và trên client dự đoán.

`RapierPhysics` ghi `Transform` sau bước physics, trong khi `NetworkTransform.Teleport()` lấy `Transform` hiện tại. Vì vậy `Respawn` đưa `Transform` về điểm hồi sinh cùng với body, trước khi gọi `Teleport()`.

## Kiểm thử <a href="#test" id="test"></a>

Chạy các bài kiểm như cuối phần một, giờ với `RapierPhysics` trên mọi `Network Manager`: vào một dedicated server với hai client, chạy vào nước và vào lưỡi cưa, chờ hồi sinh, và quan sát một chiếc chùy từ cả hai client. Các phép kiểm của bản port là các phép kiểm Play Mode của phần một (`JoinCheck`, `MoveCheck`, `LifeCheck`, `PathCheck`, `CrowdCheck`, `CrashCheck` và các phép kiểm host), chạy với backend này; `PortSetup.RapierBackend` thiết lập `Network Manager`.

## Kết quả mong đợi <a href="#expected-result" id="expected-result"></a>

- Console không có cảnh báo `[Fomoxa]` về scene file và không có exception từ `RapierPhysics`.
- Nhân vật chạy, nhảy, lăn và chết như trước, và hồi sinh ở điểm bắt đầu mà không trượt qua level trên các client khác.
- Chùy hoặc lưỡi cưa ở cùng một chỗ trên mọi client tại cùng một tick.
- `Rigidbody2D` của nhân vật hiện là kinematic trong Inspector khi game chạy.

## Commit <a href="#commit" id="commit"></a>

```
Commit: beb18a4
Message: Run the online game on the Rapier physics backend
```

Xem [`beb18a4`](https://github.com/fomoxa/RedRunner/commit/beb18a475db7cd27e9db29271c7bb1cb465f45e3) trên GitHub, rồi tiếp tục với [bước 11: thư viện mô phỏng](step-11-simulation-library.md).
