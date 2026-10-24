# Tham chiếu component

Trang này nói về các component và asset trong `Fomoxa.Unity` ngoài `NetworkManager`, `NetworkObject` và `NetworkBehaviour`. Các field Inspector của chúng được liệt kê trong [cấu hình](configuration.md).

## NetworkTransform <a href="#networktransform" id="networktransform"></a>

`public sealed class NetworkTransform : NetworkBehaviour`, được giải thích trong hướng dẫn [NetworkTransform](../synchronization/transform.md).

| Member | Type | Mô tả |
|---|---|---|
| `SyncPosition`, `SyncRotation`, `SyncScale` | `bool` | Những phần được replicate; chỉ đọc |
| `InterpolationTicks` | `int` | Số tick client hiển thị chậm so với snapshot mới nhất; chỉ đọc |
| `Visual` | `Transform` | Đọc và ghi. Object con được làm mượt sau các lần sửa prediction. |
| `SmoothingTime` | `float` | Đọc và ghi; giá trị âm thành 0 |
| `Teleport()` | `void` | Trên server, khiến client nhảy tới transform tiếp theo thay vì interpolate. Ở nơi khác không làm gì. |

## NetworkAnimator <a href="#networkanimator" id="networkanimator"></a>

`public sealed class NetworkAnimator : NetworkBehaviour`, đánh dấu `[RequireComponent(typeof(Animator))]` và được giải thích trong hướng dẫn [NetworkAnimator](../synchronization/animator.md).

| Member | Type | Mô tả |
|---|---|---|
| `Animator` | `Animator` | `Animator` được replicate |
| `FloatStep` | `float` | Bước làm tròn parameter float; chỉ đọc |
| `SetTrigger(string triggerName)`, `SetTrigger(int hash)` | `void` | Kích hoạt một trigger và, trên server, replicate nó. Ném `ArgumentException` với trigger không tồn tại. |

## Component contact <a href="#contact-components" id="contact-components"></a>

`NetworkCollision` và `NetworkTrigger` (3D), `NetworkCollision2D` và `NetworkTrigger2D` (2D) đều là `public sealed class ... : MonoBehaviour, IContactSource<...>`, được giải thích trong hướng dẫn [contact event](../physics/contacts.md).

| Member | Type | Mô tả |
|---|---|---|
| `OnEnter` | `event Action<Collider>` hoặc `Action<Collider2D>` | Một collider bắt đầu chạm |
| `OnExit` | như trên | Một collider thôi chạm |
| `Touching` | `IReadOnlyCollection<Collider>` hoặc `<Collider2D>` | Các collider đang chạm tính tới tick đã công bố gần nhất |
| `AdditionalSize` | `float` | Chỉ có trên `NetworkCollision` và `NetworkTrigger`. Đọc và ghi; giá trị âm thành 0. |
| `IsAttached` | `bool` | Một component physics đã tiếp quản component này và báo contact từ world của chính nó |
| `Attach(tracker, query)`, `Detach(query)` | `bool`, `void` | Do component physics tự báo contact gọi; `RigidbodyPhysics` không dùng chúng |

## Observer <a href="#observers" id="observers"></a>

### ObserverRule <a href="#observerrule" id="observerrule"></a>

`public abstract class ObserverRule : ScriptableObject`, được giải thích trong hướng dẫn [observer](../objects/observers.md).

| Member | Mô tả |
|---|---|
| `public abstract bool Observes(NetworkObject networkObject, ulong peerId)` | Peer có observe object hay không. Chạy trên server. Không được spawn, despawn, đổi owner, dựng lại observer hay đổi nhóm. |
| `public virtual bool RebuildsPeriodically` | Server có tính lại observer sau mỗi Observer Interval tick hay không. True nếu không override. |

### DistanceRule <a href="#distancerule" id="distancerule"></a>

`public sealed class DistanceRule : ObserverRule`, tạo bằng Assets > Create > Fomoxa > Distance Rule.

| Member | Type | Mô tả |
|---|---|---|
| `Radius` | `float` | Đọc và ghi. Khoảng cách observe tính từ bất kỳ object nào peer sở hữu; giá trị âm thành 0. |
| `IsAttached` | `bool` | Một component physics đã tiếp quản component này và báo contact từ world của chính nó |
| `Attach(tracker, query)`, `Detach(query)` | `bool`, `void` | Do component physics tự báo contact gọi; `RigidbodyPhysics` không dùng chúng |

### ObserverRange <a href="#observerrange" id="observerrange"></a>

`public sealed class ObserverRange : MonoBehaviour`, đánh dấu `[DisallowMultipleComponent]`. Đặt nó trên một `NetworkObject` để thay bán kính của `DistanceRule` cho riêng object đó.

| Member | Type | Mô tả |
|---|---|---|
| `Radius` | `float` | Đọc và ghi; giá trị âm thành 0 |

## Transport <a href="#transports" id="transports"></a>

| Component | Mô tả |
|---|---|
| `NetworkTransport` | `public abstract class NetworkTransport : MonoBehaviour` với `public abstract ITransportFactory CreateFactory()` |
| `UdpNetworkTransport` | UDP; không có field |
| `TcpNetworkTransport` | TCP; không có field |
| `WebSocketNetworkTransport` | WebSocket; code native trên desktop, trình duyệt trong WebGL |
| `MultiNetworkTransport` | Nhiều transport, mỗi transport một port, trên một server |

[Tổng quan transport](../connections/transports/README.md) giải thích từng transport.

## Asset được sinh <a href="#generated-assets" id="generated-assets"></a>

| Type | Mô tả |
|---|---|
| `NetworkPrefabList` | `ScriptableObject` có `IReadOnlyList<NetworkObject> Prefabs`; được ghi thành `FomoxaPrefabList.asset` |
| `NetworkSceneList` | `ScriptableObject` có `Count`, `SceneIdAt(int)`, `PathAt(int)`; được ghi thành `FomoxaSceneList.asset` |

`NetworkObject` và `NetworkBehaviour` có [trang tham chiếu](network-object.md) riêng, và [cấu hình](configuration.md) liệt kê các field Inspector của mọi component.
