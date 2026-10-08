# Kiến trúc

Package được xây theo tầng, và mỗi tầng chỉ dùng các tầng bên dưới nó. Tầng 1, tức Core, không biết tới Unity. Tầng 2 nối Core với Unity.

```text
Your game: MonoBehaviours, NetworkBehaviours, models
    ↓
Layer 2: Fomoxa.Unity                Unity integration
    ↓
Layer 1: Fomoxa.Networking           the Core: engine-independent networking
    ↓
Fomoxa.Net                           Fomoxa protocol: framing, handshake, heartbeat
    ↓
Transport                            UDP, TCP, WebSocket, in-process loopback
    ↓
Network
```

Hai đầu của một kết nối có cùng một stack:

```text
Unity client                              Server
Game code                                 Game code
    ↓                                         ↑
Layer 2: Fomoxa.Unity                     Layer 2: Fomoxa.Unity
    ↓                                         ↑
Layer 1: Fomoxa.Networking                Layer 1: Fomoxa.Networking
    ↓                                         ↑
Fomoxa.Net and transport  ─── network ──→ Fomoxa.Net and transport
```

Message từ server tới client đi qua đúng các tầng đó theo chiều ngược lại.

## Assembly <a href="#assemblies" id="assemblies"></a>

| Assembly | Thư mục | Tham chiếu UnityEngine | Nội dung |
|---|---|---|---|
| `Fomoxa.Net` | `Runtime/Plugins/Fomoxa.Net.dll` | Không | Runtime của giao thức Fomoxa: frame, handshake, heartbeat, `Schema`, transport TCP và UDP |
| `Fomoxa.Attributes` | `Runtime/Plugins/Fomoxa.Attributes.dll` | Không | `[Network]` và `[Codec]`, trong namespace `Fomoxa` |
| `Fomoxa.Networking` | `Runtime/Core` | Không | Tầng 1, kèm source generator cho RPC trong `Runtime/Core/Generators` |
| `Fomoxa.Unity` | `Runtime/Unity` | Có | Tầng 2 |
| `Fomoxa.Unity.Editor` | `Editor` | Có, chỉ trong Editor | Hook sinh code, các bước gán prefab id và scene id, scene file, kiểm tra khi build |

## Tầng 1: Fomoxa.Networking <a href="#layer-1-fomoxanetworking" id="layer-1-fomoxanetworking"></a>

Tầng 1 chứa mọi thứ có thể chạy mà không cần Unity. Assembly definition của nó đặt `noEngineReferences`, nên trình biên dịch từ chối mọi chỗ dùng `UnityEngine` bên trong. Vector và quaternion trong API của nó là các type của `System.Numerics`.

| Mảng | Namespace | Chức năng |
|---|---|---|
| Manager | `Fomoxa.Networking` | `ServerManager`, `ClientManager` và `TimeManager`, thứ tự công việc trong một tick, `FomoxaRegistry`, các attribute cho RPC và channel, và các type đăng ký `NetworkRpcs`, `NetworkState`, `NetworkInput` |
| Messaging | `Fomoxa.Networking.Messaging` | Message id, `IMessageCodec<T>`, message bundle, channel reliable-ordered, dispatcher chuyển message id tới handler, delta encoding, các system model của package |
| Sessions | `Fomoxa.Networking.Sessions` | Session của client và server: trạng thái kết nối, send queue và giới hạn của chúng, flush, kết nối lại, event kết nối |
| Objects | `Fomoxa.Networking.Objects` | Bảng object, message spawn, despawn và đổi owner, tập observer, network scene theo từng peer |
| Timing | `Fomoxa.Networking.Timing` | Ước lượng của client về tick của server và prediction tick, ping và pong |
| Prediction | `Fomoxa.Networking.Prediction` | Bộ đệm input của server theo object và peer, cùng prediction, reconciliation và replay của client |
| Simulation | `Fomoxa.Networking.Simulation` | Các interface physics `IPhysicsSimulation`, `IPhysicsWorld` và `IPhysicsWorld2D`, `PhysicsBody`, `PhysicsHistory` và việc theo dõi contact |
| Transports | `Fomoxa.Networking.Transports` | `ITransportFactory`, connector không chặn, giao thức WebSocket, loopback, listener kết hợp |

Spawn, ownership, việc chuyển RPC và state, quyết định observer và quyết định khi nào gửi transform đều diễn ra ở tầng 1. `NetworkBehaviour` chuyển callback và phần đăng ký của nó xuống một behaviour của tầng 1, nên luật là một dù cái gì điều khiển chúng.

Tầng 1 ghi warning và error qua một `NetworkLog` do tầng 2 cung cấp, và tầng 2 đưa chúng vào Console của Unity.

## Tầng 2: Fomoxa.Unity <a href="#layer-2-fomoxaunity" id="layer-2-fomoxaunity"></a>

Tầng 2 nối tầng 1 với GameObject, scene, player loop và physics của Unity. `NetworkManager` đọc các field trong Inspector, dựng tầng 1 từ chúng và chạy tầng 1 từ player loop của Unity. `TransportManager`, `NetworkObject` và `NetworkBehaviour` cũng thuộc tầng này, cùng hai component `NetworkTransform` và `NetworkAnimator`.

Registry của prefab và scene, việc load scene và các asset observer rule cũng nằm ở tầng 2, cùng với component `RigidbodyPhysics` và các world `Rigidbody`, `Rigidbody2D`, các component contact event và các component transport, kể cả WebSocket của trình duyệt cho WebGL.

## Code sinh ra <a href="#generated-code" id="generated-code"></a>

Code của game làm việc cùng với code mà package sinh ra trong project:

```text
Models (your classes with [Network] and [Codec])
    ↓ fomoxac
Codecs (<Model><Codec>Codec) and NetSchema
    ↓ package Editor step
Adapters (<Model><Codec>Adapter : IMessageCodec<T>), FomoxaAdapters.RegisterAll, FomoxaUnityRegistration
    ↓ at startup
FomoxaRegistry.Default
    ↓ in Awake
NetworkManager
```

Các message của chính package, như message spawn và transform, cũng là model. Package copy chúng vào thư mục `FomoxaSystemModels` của project và sinh code cùng với model của bạn, nên mọi message game gửi đều thuộc về một schema duy nhất, thứ mà client và server so sánh trong lúc handshake. [Tích hợp Editor](../unity/editor-integration.md) liệt kê mọi file được sinh.

## Vì sao chia tầng <a href="#why-the-split" id="why-the-split"></a>

Tầng 1 không phụ thuộc Unity, nên nó có thể được biên dịch và test bên ngoài Unity. Physics cũng chia theo cách đó: code game dùng các interface và `PhysicsBody` của tầng 1, còn các world của Unity hiện thực chúng ở tầng 2, như [kiến trúc physics](../physics/architecture.md) giải thích.

Các trang [mô hình networking](networking-model.md) và [tick và thời gian](tick.md) xây tiếp trên trang này, còn [danh mục API](../reference/api.md) liệt kê public API theo type.
