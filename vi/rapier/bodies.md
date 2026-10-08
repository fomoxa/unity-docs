# Body và collider

`RapierPhysics` dựng body Rapier cho một network object vào lần đầu có thứ hỏi tới nó: manager khi step world, hoặc code game qua `NetworkObject.Body` hay `Body2D`. Geometry tĩnh lấy từ scene file của network scene. Trang này liệt kê cách component của Unity ánh xạ sang Rapier và cách code game truy cập các world.

## Body của network object <a href="#bodies-of-network-objects" id="bodies-of-network-objects"></a>

Body của một network object được mô tả từ các collider dưới GameObject của nó thuộc về chính `Rigidbody` hoặc `Rigidbody2D` của nó, bằng `BodyDescriptions.TryDescribe` và `TryDescribe2D`. Mô tả giữ:

- loại body: dynamic, kinematic khi `isKinematic` được đặt hoặc body type của `Rigidbody2D` là `Kinematic`, và static với `Rigidbody2D` static hoặc khi không có `Rigidbody`;
- khối lượng, ràng buộc trục, trọng lực (`useGravity` ở 3D, `gravityScale` ở 2D) và damping tuyến tính, damping góc;
- mọi collider đang bật cùng hình dạng, vị trí và góc xoay tương đối với body, physics material, layer và cờ trigger của nó.

Body được tạo trong world Rapier của network scene chứa object. Sau đó `Rigidbody` được chuyển sang kinematic và body type của `Rigidbody2D` sang `Kinematic`, để physics của Unity không còn di chuyển object. Sau mỗi tick, Rapier ghi vị trí và góc xoay của mỗi body ngược lại vào `Transform` của object; body 2D giữ nguyên Z của `Transform`. Khi object despawn, body bị gỡ và thiết lập ban đầu của `Rigidbody` được trả lại.

Collider mà backend không biểu diễn được sẽ log exception gắn với object, và object đó không có body Rapier.

## Collider được hỗ trợ <a href="#supported-colliders" id="supported-colliders"></a>

| 3D | 2D |
|---|---|
| `BoxCollider`, `SphereCollider`, `CapsuleCollider` | `BoxCollider2D`, `CircleCollider2D`, `CapsuleCollider2D` |
| `MeshCollider` lồi, trên mọi body | `PolygonCollider2D`; collider lõm trên body di chuyển được chia thành các mảnh lồi |
| `MeshCollider` không lồi và `TerrainCollider`, chỉ cho geometry tĩnh | `EdgeCollider2D`, chỉ cho geometry tĩnh |

`BoxCollider2D` bật auto tiling trên một `SpriteRenderer` dạng sliced hoặc tiled được mô tả bằng các hình mà Unity đã dựng cho nó. Mesh dùng cho body tạo lúc chạy phải bật Read/Write.

Friction, bounciness và cách kết hợp của chúng lấy từ physics material. Ma trận va chạm layer của project áp dụng như trong Unity; scene file mang chúng theo cho mỗi scene. Trigger collider trở thành sensor của Rapier, báo những gì chồng lên nó và không đẩy gì cả.

## Geometry tĩnh <a href="#static-geometry" id="static-geometry"></a>

Khi một network scene load, `RapierPhysics` đọc scene file của nó và thêm các collider tĩnh của scene vào các world của scene, theo thứ tự file liệt kê. Collider tĩnh là collider đang bật trên một GameObject đang hoạt động, không thuộc `Rigidbody`, `Rigidbody2D` hay `NetworkObject` nào. Collider có `Rigidbody` riêng nhưng không có `NetworkObject`, như một lưỡi cưa di chuyển, không có trong file, và geometry bạn tạo lúc chạy cũng vậy. Hãy thêm chúng bằng các member của `NetworkPhysics`:

| Member | Thêm |
|---|---|
| `AddStatic(Scene, IReadOnlyList<ColliderDesc>)`, `AddStatic2D(Scene, IReadOnlyList<ColliderDesc2D>)` | Một nhóm mô tả collider vào các world của một network scene |
| `AddStatic(GameObject)`, `AddStatic2D(GameObject)` | Các collider tĩnh dưới một GameObject; các component contact trên những collider đó sau đó báo contact của Rapier |
| `AddBody(Scene, in BodyDesc)`, `AddBody2D(Scene, in BodyDesc2D)` | Một body không network object nào sở hữu, như một bục mà mọi peer di chuyển giống nhau theo số tick |

`RemoveStatic`, `RemoveBody` và `RemoveBody2D` gỡ chúng ra. Nhóm tĩnh và body không chủ là một phần của world, nên snapshot lưu chúng và replay khôi phục chúng.

## Đọc world <a href="#reading-the-worlds" id="reading-the-worlds"></a>

`RapierPhysics.Scenes` trả về `RapierScenes` giữ các world, hoặc null trước khi `NetworkManager` chạy `Awake`. `WorldOf(sceneId)` và `WorldOf2D(sceneId)` trả về `RapierWorld` hoặc `RapierWorld2D` của một network scene; chúng hiện thực `IPhysicsWorld` và `IPhysicsWorld2D` và thêm vài member riêng:

| Member | Mô tả |
|---|---|
| `void Touching(RapierCollider collider, List<RapierCollider> into)` | Thêm mọi collider chạm hoặc chồng lên `collider` sau bước mô phỏng gần nhất |
| `void SetKind(BodyHandle body, BodyKind kind)` | Đổi một body giữa dynamic, kinematic và static |
| `ulong StateHash` | Hash của toàn bộ state world, để so hai lần chạy |

`RapierCollider` chỉ tới một collider của world. `RapierCollider.OfBody(handle, index)` là collider ở vị trí `index` trong mô tả của body, còn `RapierCollider.Static(index)` là một collider tĩnh, đánh số trước theo scene file rồi theo các nhóm tĩnh theo thứ tự được thêm (`StaticGroup.FirstIndex`). `IsStatic` phân biệt hai loại.

Các overload của `BodyDescriptions.TryDescribe` và `TryDescribe2D` nhận một danh sách sẽ trả về collider nguồn của từng mô tả, nên vị trí của một collider Unity trong danh sách đó là chỉ số của nó trong body:

```csharp
using System.Collections.Generic;
using Fomoxa.Networking.Rapier;
using Fomoxa.Networking.Simulation;
using Fomoxa.Unity;
using Fomoxa.Unity.Rapier;
using UnityEngine;

public sealed class FootSensor : NetworkBehaviour
{
    [SerializeField] private Collider2D foot;

    private readonly List<Collider2D> sources = new List<Collider2D>();
    private readonly List<RapierCollider> touching = new List<RapierCollider>();

    public bool Grounded(RapierPhysics rapier, uint sceneId)
    {
        PhysicsBody2D body = NetworkObject.Body2D;
        if (!body.IsValid || !BodyDescriptions.TryDescribe2D(gameObject, out _, sources))
        {
            return false;
        }

        touching.Clear();
        rapier.Scenes.WorldOf2D(sceneId).Touching(RapierCollider.OfBody(body.Handle, sources.IndexOf(foot)), touching);
        return touching.Count > 0;
    }
}
```

`sceneId` là id của network scene chứa object, do `NetworkManager.Scenes.IdOf(gameObject.scene.path)` trả về. Tập contact đọc theo cách này là một phần của mô phỏng, nên chúng giống nhau trên server và trên client dự đoán, và giống nhau lần nữa khi replay. [Ví dụ Red Runner](../examples/redrunner/rapier-and-console/step-10-rapier-backend.md) quyết định chạm đất và cái chết theo cách này.

[Contact event](contacts.md) mô tả các component event, còn [tham chiếu physics API](../reference/physics.md) liệt kê các type mô tả.
