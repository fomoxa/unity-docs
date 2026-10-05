# Kiến trúc

Package được xây theo tầng, và mỗi tầng chỉ dùng các tầng bên dưới nó. Tầng 2 là tầng thấp nhất biết tới Unity.

```
Your game: MonoBehaviours, NetworkBehaviours, models
    ↓
Layer 2: Fomoxa.Unity                Unity integration
    ↓
Layer 1: Fomoxa.Unity.Core           engine-independent networking
    ↓
Fomoxa.Net                           Fomoxa protocol: framing, handshake, heartbeat
    ↓
Transport                            UDP, TCP, WebSocket, in-process loopback
    ↓
Network
```

Hai đầu của một kết nối có cùng một stack:

```
Unity client                              Server
Game code                                 Game code
    ↓                                         ↑
Layer 2: Fomoxa.Unity                     Layer 2: Fomoxa.Unity
    ↓                                         ↑
Layer 1: Fomoxa.Unity.Core                Layer 1: Fomoxa.Unity.Core
    ↓                                         ↑
Fomoxa.Net and transport  ─── network ──→ Fomoxa.Net and transport
```

Message từ server tới client đi qua đúng các tầng đó theo chiều ngược lại.

## Assembly <a href="#assemblies" id="assemblies"></a>

| Assembly              | Thư mục                                 | Tham chiếu UnityEngine | Nội dung                                                                                  |
| --------------------- | --------------------------------------- | ---------------------- | ----------------------------------------------------------------------------------------- |
| `Fomoxa.Net`          | `Runtime/Plugins/Fomoxa.Net.dll`        | Không                  | Runtime của giao thức Fomoxa: frame, handshake, heartbeat, `Schema`, transport TCP và UDP |
| `Fomoxa.Attributes`   | `Runtime/Plugins/Fomoxa.Attributes.dll` | Không                  | `[Network]` và `[Codec]`, trong namespace `Fomoxa`                                        |
| `Fomoxa.Unity.Core`   | `Runtime/Core`                          | Không                  | Tầng 1                                                                                    |
| `Fomoxa.Unity`        | `Runtime/Unity`                         | Có                     | Tầng 2, kèm source generator cho RPC trong `Runtime/Unity/Generators`                     |
| `Fomoxa.Unity.Editor` | `Editor`                                | Có, chỉ trong Editor   | Hook sinh code, các bước gán prefab id và scene id, kiểm tra khi build                    |

## Tầng 1: Fomoxa.Unity.Core <a href="#layer-1-fomoxaunitycore" id="layer-1-fomoxaunitycore"></a>

Tầng 1 chứa mọi thứ có thể chạy mà không cần Unity. Assembly definition của nó đặt `noEngineReferences`, nên trình biên dịch từ chối mọi chỗ dùng `UnityEngine` bên trong.

| Mảng       | Namespace                 | Chức năng                                                                                                                                                        |
| ---------- | ------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Messaging  | `Fomoxa.Unity.Messaging`  | Message id, `IMessageCodec<T>`, message bundle, channel reliable-ordered, dispatcher chuyển message id tới handler, delta encoding, các system model của package |
| Sessions   | `Fomoxa.Unity.Sessions`   | Session của client và server: trạng thái kết nối, send queue và giới hạn của chúng, flush, kết nối lại, event kết nối                                            |
| Objects    | `Fomoxa.Unity.Objects`    | Bảng object, message spawn, despawn và đổi owner, tập observer, network scene theo từng peer                                                                     |
| Timing     | `Fomoxa.Unity.Timing`     | Ước lượng của client về tick của server và prediction tick, ping và pong                                                                                         |
| Prediction | `Fomoxa.Unity.Prediction` | Bộ đệm input của server theo object và peer                                                                                                                      |
| Simulation | `Fomoxa.Unity.Simulation` | Các interface physics `IPhysicsSimulation`, `IPhysicsWorld` và `IPhysicsWorld2D`, `PhysicsBody`, và `PhysicsHistory`                                             |
| Transports | `Fomoxa.Unity.Transports` | `ITransportFactory`, connector không chặn, giao thức WebSocket, loopback, listener kết hợp                                                                       |
| Registry   | `Fomoxa.Unity`            | `FomoxaRegistry`, nơi giữ schema, codec, channel và RPC id; các attribute cho RPC và channel                                                                     |

Tầng 1 không bao giờ log. Nó báo những gì xảy ra qua event, và tầng 2 chuyển các event đó thành log message của Unity.

## Tầng 2: Fomoxa.Unity <a href="#layer-2-fomoxaunity" id="layer-2-fomoxaunity"></a>

Tầng 2 nối tầng 1 với GameObject, scene, player loop và physics của Unity. Nó chứa `NetworkManager` cùng các entry trong player loop, cùng với `ServerManager`, `ClientManager`, `TimeManager` và `TransportManager`. Nó cũng chứa `NetworkObject` và `NetworkBehaviour` cùng phần đăng ký RPC, state và input, prediction và replay, và hai component `NetworkTransform`, `NetworkAnimator`.

Registry của prefab và scene, việc load scene và các observer rule cũng nằm ở tầng 2, cùng với physics backend cho `Rigidbody` và `Rigidbody2D`, các component contact event và các component transport, kể cả WebSocket của trình duyệt cho WebGL.

## Code sinh ra <a href="#generated-code" id="generated-code"></a>

Code của game làm việc cùng với code mà package sinh ra trong project:

```
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

Vì tầng 1 không phụ thuộc Unity, nó có thể được biên dịch và test riêng, và một server viết bằng chương trình .NET thuần có thể dùng nó. Package không kèm server như vậy; [server console](../server/server-console.md) mô tả những gì hiện có. Physics cũng chia theo cách đó: code game dùng các interface và `PhysicsBody` của tầng 1, còn backend Unity hiện thực chúng ở tầng 2, như [kiến trúc physics](../physics/architecture.md) giải thích.

Các trang [mô hình networking](networking-model.md) và [tick và thời gian](tick.md) xây tiếp trên trang này, còn [danh mục API](../tham-chieu/api.md) liệt kê public API theo type.
