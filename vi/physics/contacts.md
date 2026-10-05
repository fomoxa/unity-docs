# Contact event

Unity phát `OnCollisionEnter`, `OnTriggerEnter` và các event exit tương ứng từ bên trong mỗi bước physics. Khi client replay các tick trong lúc reconciliation, các bước đó chạy lại, và Unity sẽ phát cùng event lần thứ hai. Các component contact của package tránh điều đó bằng cách phát event enter và exit một lần mỗi tick, và sau một lần replay thì chỉ cho những gì đã thay đổi.

| Component | Collider trên GameObject của nó | Báo |
|---|---|---|
| `NetworkCollision` | 3D, không phải trigger | Collider đang chạm vào chúng |
| `NetworkTrigger` | 3D, trigger | Collider đang ở bên trong chúng |
| `NetworkCollision2D` | 2D, không phải trigger | Collider đang chạm vào chúng |
| `NetworkTrigger2D` | 2D, trigger | Collider đang ở bên trong chúng |

## Cách dùng cơ bản <a href="#basic-usage" id="basic-usage"></a>

Thêm component vào GameObject có các collider và subscribe vào event của nó:

```csharp
using Fomoxa.Unity;
using UnityEngine;

[RequireComponent(typeof(NetworkTrigger2D))]
public sealed class Pickup : MonoBehaviour
{
    private void OnEnable()
    {
        GetComponent<NetworkTrigger2D>().OnEnter += Collect;
    }

    private void OnDisable()
    {
        GetComponent<NetworkTrigger2D>().OnEnter -= Collect;
    }

    private void Collect(Collider2D other)
    {
        Debug.Log($"{other.name} entered {name}");
    }
}
```

| Member | Ý nghĩa |
|---|---|
| `OnEnter` | Một collider bắt đầu chạm, hoặc đi vào trigger |
| `OnExit` | Một collider thôi chạm, hoặc rời trigger |
| `Touching` | Các collider đang chạm, tính tới tick đã công bố gần nhất |

Trong một tick, exit được phát trước enter. Exception trong một handler được log và không ngăn các handler khác chạy.

## Cách hoạt động <a href="#how-it-works" id="how-it-works"></a>

Khi một `NetworkManager` step physics world của component, component bỏ qua callback của Unity và thay vào đó truy vấn, sau mỗi bước, xem collider nào đang chạm collider của nó. `NetworkCollision` và `NetworkTrigger` chạy truy vấn overlap với hình dạng của từng collider, nới rộng thêm Additional Size. Các truy vấn này tôn trọng layer collision matrix và `Physics.IgnoreCollision`, và bỏ qua các collider của cùng một `Rigidbody`. `NetworkCollision2D` và `NetworkTrigger2D` hỏi physics 2D của Unity về các contact hiện tại của collider.

Cuối tick, kết quả được so sánh với tập đã công bố trước đó, và phần khác biệt được phát thành event.

Trên client của owner, các component còn ghi lại tập đang chạm của mỗi tick. Một lần replay khôi phục tập của tick được sửa, cập nhật nó khi các world step lại và công bố một lần sau khi replay xong. Event đã phát ở lần chạy gốc không phát lại, còn contact bị lần replay loại bỏ sẽ phát một exit.

Khi không có `NetworkManager` nào step world, ví dụ khi Simulate Physics tắt, các component chỉ chuyển tiếp callback của Unity thành `OnEnter` và `OnExit`.

## Cấu hình <a href="#configuration" id="configuration"></a>

| Field | Trên | Mặc định | Ý nghĩa |
|---|---|---|---|
| Additional Size | `NetworkCollision` | `Physics.defaultContactOffset` × 2 | Khoảng nới rộng hình dạng truy vấn, để contact đang nằm yên được tính là đang chạm |
| Additional Size | `NetworkTrigger` | 0 | Khoảng nới rộng hình dạng truy vấn |

## Event được phát ở đâu <a href="#where-events-fire" id="where-events-fire"></a>

Các component phát event ở mọi phía chạy chúng, dù là server, client hay host. Luật game ảnh hưởng tới người chơi khác, như nhặt một vật phẩm, nên được thực hiện trên server, còn client dùng event cho các hiệu ứng cục bộ.

## Giới hạn <a href="#limitations" id="limitations"></a>

Truy vấn 3D xử lý chính xác collider box, sphere và capsule, và dùng bounding box cho các loại collider khác. Các component chỉ thấy collider trên chính GameObject của chúng, được thu thập khi component được bật.

Component contact phụ thuộc vào việc step mô tả trong [tổng quan physics](overview.md) và vào replay mô tả trong [rollback với physics](../prediction/rollback.md). [Tham chiếu component](../reference/components.md#contact-components) liệt kê các member của chúng.
