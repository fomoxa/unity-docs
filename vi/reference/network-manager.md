# Tham chiếu NetworkManager

`public sealed class NetworkManager : MonoBehaviour` trong `Fomoxa.Unity`, đánh dấu `[DisallowMultipleComponent]`. Hướng dẫn [NetworkManager](../core/network-manager.md) giải thích cách dùng nó, và các field của nó được liệt kê trong [cấu hình](configuration.md#networkmanager).

## Mục đích <a href="#purpose" id="purpose"></a>

Manager chạy networking cho một scene. Nó đọc cấu hình, đăng ký prefab và scene, tạo các manager server, client, time và transport, và chạy vòng lặp tick bên trong player loop.

## Vòng đời <a href="#lifetime" id="lifetime"></a>

| Unity message | Tác dụng |
|---|---|
| `Awake` | Tạo các manager con. Ném `InvalidOperationException` khi chưa có schema hoặc một system codec chưa được đăng ký. |
| `OnEnable` / `OnDisable` | Thêm hoặc gỡ các entry trong player loop |
| `OnDestroy` | Dừng client và server, giải phóng physics simulation |
| `Application.quitting` | Dừng client và server |

## Property <a href="#properties" id="properties"></a>

| Property | Type | Mô tả |
|---|---|---|
| `Registry` | `FomoxaRegistry` | Schema, codec, channel và RPC id. Đọc và ghi; mặc định là `FomoxaRegistry.Default`. Nó được đọc trong `Awake`, nên registry khác chỉ có tác dụng khi được gán trước đó, ví dụ trên một manager thêm vào GameObject đang tắt. |
| `ServerManager` | `ServerManager` | Phía server. Null trước `Awake`. |
| `ClientManager` | `ClientManager` | Phía client. Null trước `Awake`. |
| `TimeManager` | `TimeManager` | Tick rate, tick và tick event. Null trước `Awake`. |
| `TransportManager` | `TransportManager` | Transport. Null trước `Awake`. |
| `Prefabs` | `PrefabRegistry` | Các prefab manager này có thể spawn |
| `Scenes` | `SceneRegistry` | Các network scene manager này có thể load |

## Thread <a href="#threading" id="threading"></a>

Mọi member phải được gọi từ main thread của Unity, và package không tạo thread riêng.

## TransportManager <a href="#transportmanager" id="transportmanager"></a>

`public sealed class TransportManager` trong `Fomoxa.Unity`.

| Property | Type | Mô tả |
|---|---|---|
| `Transport` | `NetworkTransport` | Component transport đang dùng |
| `Factory` | `ITransportFactory` | Factory mà component đã tạo trong `Awake` |

## PrefabRegistry <a href="#prefabregistry" id="prefabregistry"></a>

`public sealed class PrefabRegistry` trong `Fomoxa.Unity`.

| Member | Mô tả |
|---|---|
| `Count` | Số prefab id đã đăng ký |
| `Contains(uint prefabId)` | Id đã được đăng ký hay chưa |
| `Register(NetworkObject prefab)` | Đăng ký một prefab theo Prefab Id của nó. Ném exception với id 0, id đã đăng ký cho prefab khác, và hierarchy không hợp lệ. Đăng ký lại cùng prefab không có tác dụng. |
| `Register(uint prefabId, uint fingerprint, Func<Vector3, Quaternion, NetworkObject> create, Action<NetworkObject> release = null)` | Đăng ký một factory cho một prefab id. Ném exception với id 0 và id đã đăng ký cho thứ khác. |

## SceneRegistry <a href="#sceneregistry" id="sceneregistry"></a>

`public sealed class SceneRegistry` trong `Fomoxa.Unity`.

| Member | Mô tả |
|---|---|
| `Count` | Số scene id đã đăng ký |
| `Contains(uint sceneId)` | Id đã được đăng ký hay chưa |
| `IdOf(string path)` | Id của một scene trong Collected Scenes theo đường dẫn build; 0 khi không biết |
| `Register(uint sceneId, ISceneLoader loader)` | Đăng ký một loader. Ném exception với id 0 và id đã đăng ký. |

`ISceneLoader` có hai method, `void Load(Action<Scene> loaded, Action<Exception> failed)` và `void Unload(Scene scene, Action unloaded)`.

Các manager con được tài liệu hóa trong các tham chiếu [ServerManager](server-manager.md), [ClientManager](client-manager.md) và [TimeManager](time-manager.md), còn registry trong [messaging API](messaging.md).
