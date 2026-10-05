# Server console

{% hint style="warning" %}
Chưa đóng gói. Phiên bản 0.1.0 không kèm server console, project mẫu hay quy trình được hỗ trợ cho nó. Trang này mô tả những gì cấu trúc tầng của package cho phép và những gì còn thiếu.
{% endhint %}

## Server console là gì <a href="#what-a-server-console-is" id="what-a-server-console-is"></a>

Server console là server viết bằng chương trình .NET thuần, không load Unity Engine. Client Unity sẽ kết nối tới nó giống như kết nối tới một server Unity.

## Những gì đã có <a href="#what-exists" id="what-exists"></a>

Tầng 1 của package, assembly `Fomoxa.Unity.Core` trong `Runtime/Core`, không tham chiếu Unity; assembly definition của nó đặt `noEngineReferences`, nên trình biên dịch từ chối mọi phụ thuộc vào Unity. Nó chứa các phần phía server mà một console sẽ cần:

| Phần | Type |
|---|---|
| Session và event kết nối | `ServerSession`, `SessionLimits`, `ConnectionStateArgs` |
| Object, ownership, observer | `ServerObjects` |
| Network scene | `ServerScenes` |
| Đồng hồ và bộ đệm input | `ServerClock`, `ServerInputs` |
| Transport | `TcpTransportFactory`, `UdpTransportFactory`, `WebSocketTransportFactory`, `MultiTransportFactory` |
| Registry | `FomoxaRegistry`, do `FomoxaAdapters.RegisterAll` sinh ra điền vào |
| Interface physics | `IPhysicsWorld`, `IPhysicsWorld2D`, `PhysicsHistory` |

Code sinh ra cũng cho một server không có Unity cách tham chiếu tới prefab và scene, qua các hằng số trong `FomoxaPrefabs.cs` và `FomoxaScenes.cs`. `FomoxaAdapters.RegisterAll(registry)` sinh ra cũng chạy được ngoài Unity, và chỉ `FomoxaUnityRegistration.cs` là phụ thuộc Unity.

## Những gì còn thiếu <a href="#what-is-missing" id="what-is-missing"></a>

Không có project file hay thiết lập build để biên dịch `Runtime/Core` và code sinh ra ngoài Unity, và không có vòng lặp tick. Trong Unity, `NetworkManager` điều khiển session, đồng hồ, input, state và transform mỗi tick, và một console sẽ phải làm điều tương tự.

Ngoài Unity, object cũng không có cơ chế định tuyến state, transform hay RPC, vì `NetworkObject`, `NetworkBehaviour`, `NetworkTransform` và cơ chế state là các component Unity ở tầng 2. Physics backend duy nhất dùng physics của Unity, và backend `Rapier` chưa được hiện thực. Ngoài [danh mục API](../reference/api.md), các type của tầng 1 chưa được tài liệu hóa.

Cho tới khi package hỗ trợ server console, hãy chạy dedicated server dưới dạng player Unity ở batch mode, như mô tả trong [dedicated server](dedicated-server.md). [Kiến trúc](../concepts/architecture.md) và [kiến trúc physics](../physics/architecture.md) giải thích cấu trúc tầng mà trang này dựa vào.
