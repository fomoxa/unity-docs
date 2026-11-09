# Truy vấn physics

Một world trả lời bốn loại truy vấn: tia, hình đang di chuyển, các body nằm trong một hình, và điểm tiếp xúc giữa hai body. Cùng các lời gọi này chạy được với `RigidbodyPhysics` lẫn [backend Rapier](../rapier/overview.md), vì cả hai đều hiện thực `IPhysicsWorld` và `IPhysicsWorld2D`. Truy vấn chạy trên state của world ngay lúc gọi, nên server và client dự đoán nhận cùng câu trả lời khi world của hai bên có cùng state.

## Lấy world <a href="#reaching-a-world" id="reaching-a-world"></a>

Điểm tiếp xúc được đọc qua chính body, như phần dưới cho thấy. Các truy vấn khác cần world, và component physics trả về world của một scene:

```csharp
using System.Collections.Generic;
using Fomoxa.Networking.Simulation;
using Fomoxa.Unity;

private readonly List<IPhysicsSimulation> worlds = new List<IPhysicsSimulation>();

private IPhysicsWorld2D World2DOf(NetworkPhysics physics)
{
    worlds.Clear();
    physics.WorldsOf(gameObject.scene, worlds);
    foreach (IPhysicsSimulation world in worlds)
    {
        if (world is IPhysicsWorld2D world2D)
        {
            return world2D;
        }
    }

    return null;
}
```

`physics` là component nằm trong trường Physics của `NetworkManager`. Manager không công khai component này, nên hãy cho behaviour một trường `NetworkPhysics` serialized và kéo cùng component đó vào.

## Bộ lọc <a href="#filters" id="filters"></a>

Mọi truy vấn nhận một `QueryFilter`:

| Member | Ý nghĩa |
|---|---|
| `LayerMask` | Bit `i` bật thì collider ở layer `i` được xét. `-1` là mọi layer |
| `ExcludeBody` | Collider của body này bị bỏ qua. `BodyHandle` mặc định không bỏ body nào |
| `IncludeTriggers` | Có xét trigger collider hay không |

`QueryFilter.All` và `default(QueryFilter)` như nhau: mọi layer, có xét trigger, không bỏ body nào. Bộ lọc cho mặt đất dưới chân người chơi trông như sau:

```csharp
var filter = new QueryFilter(1 << groundLayer, NetworkObject.Body2D.Handle, false);
```

## Raycast và ShapeCast <a href="#raycast-and-shapecast" id="raycast-and-shapecast"></a>

```csharp
bool Raycast(Vector3 origin, Vector3 direction, float maxDistance, in QueryFilter filter, out RayHit hit);
bool ShapeCast(in BodyShape shape, Vector3 position, Quaternion rotation, Vector3 direction, float maxDistance, in QueryFilter filter, out RayHit hit);
```

`Raycast` trả về collider đầu tiên dọc theo tia, còn `ShapeCast` trả về collider đầu tiên mà một hình chạm vào khi nó di chuyển theo `direction`. Bản 2D nhận giá trị `Vector2`, góc xoay theo radian, `BodyShape2D` và `RayHit2D`.

- Hướng được chuẩn hoá trước, và `hit.Distance` tính theo đơn vị của world. Hướng bằng 0 thì trả về false.
- `ShapeCast` nhận hộp, cầu hoặc viên nang ở 3D, và hộp, hình tròn hoặc viên nang ở 2D. Hình khác ném `ArgumentException`. Viên nang nằm dọc trục Y cục bộ, như capsule collider.
- Truy vấn bắt đầu bên trong một collider thì trúng collider đó ở khoảng cách 0. Điểm và pháp tuyến của lần trúng này khác nhau giữa các backend: `RigidbodyPhysics` báo vị trí bắt đầu và `-direction`, Rapier báo giá trị do thư viện hình học của nó tính. Lưới tam giác chỉ được tính khi truy vấn chạm tới bề mặt của nó.
- `hit.Body` là body của collider bị trúng. Nó không hợp lệ với geometry tĩnh và với `Rigidbody` mà world không biết.

```csharp
PhysicsBody2D body = NetworkObject.Body2D;
var feet = BodyShape2D.Box(new Vector2(0.4f, 0.05f));
var filter = new QueryFilter(1 << groundLayer, body.Handle, false);
bool grounded = World2DOf(physics).ShapeCast(feet, body.Position, 0f, -Vector2.UnitY, 0.1f, filter, out RayHit2D hit);
```

Các vector ở đây là kiểu `System.Numerics`.

## Overlap <a href="#overlap" id="overlap"></a>

```csharp
int Overlap(in BodyShape shape, Vector3 position, Quaternion rotation, in QueryFilter filter, BodyHandle[] results);
```

`Overlap` ghi vào `results` các body có collider chồng lên hình, mỗi body một lần và nhiều nhất `results.Length` body, rồi trả về số đã ghi. Collider tĩnh và body không rõ không được ghi, và thứ tự không quy định. Mảng null ném `ArgumentNullException`.

## Điểm tiếp xúc <a href="#contact-points" id="contact-points"></a>

`PhysicsBody.GetContactPoints(other, into)` và `PhysicsBody2D.GetContactPoints(other, into)` liệt kê chỗ body chạm một body khác sau bước mô phỏng gần nhất:

| Trường của `ContactPointInfo`, `ContactPointInfo2D` | Ý nghĩa |
|---|---|
| `Point` | Điểm tiếp xúc, toạ độ thế giới |
| `Normal` | Pháp tuyến đơn vị, hướng từ `other` về phía body được hỏi |
| `Depth` | Dương khi hai collider chồng lên nhau, âm khi chúng còn cách nhau nhưng nằm trong lề tiếp xúc của engine |

Truyền `default(BodyHandle)` làm `other` để lấy tiếp xúc với geometry tĩnh. Một overload nhận `QueryFilter`, áp lên các collider phía `other`; `IncludeTriggers` không có tác dụng ở đây, vì trigger không có điểm tiếp xúc. Hàm xoá `into`, ghi vào đó rồi trả về số điểm.

```csharp
private readonly List<ContactPointInfo2D> points = new List<ContactPointInfo2D>();

private bool StandsOnGround()
{
    NetworkObject.Body2D.GetContactPoints(default, points);
    foreach (ContactPointInfo2D point in points)
    {
        if (point.Normal.Y > 0.7f)
        {
            return true;
        }
    }

    return false;
}
```

Sau một bước mô phỏng, các điểm là điểm của bước đó. Từ một lần `Load` tới bước kế tiếp, chúng là điểm của tick vừa nạp, nên handler input chạy lại trong replay đọc đúng những gì nó đã đọc lần đầu. `RigidbodyPhysics` không trả điểm nào cho body 3D, vì Unity chỉ báo tiếp xúc 3D qua callback va chạm. Với 3D dưới `RigidbodyPhysics`, hãy dùng [các component contact](contacts.md#contact-points).

## Overload cũ <a href="#older-overloads" id="older-overloads"></a>

`Raycast` không có bộ lọc và `Overlap(center, radius, results)` với hình cầu hoặc hình tròn vẫn còn, dưới dạng extension method trong `PhysicsQueries`. Chúng dùng `QueryFilter.All`, nên dưới `RigidbodyPhysics` giờ chúng xét mọi layer, kể cả Ignore Raycast, và trúng cả trigger.

[Tham chiếu physics API](../reference/physics.md) liệt kê các type, còn [PhysicsBody](physics-body.md) nói về lực và mô-men.
