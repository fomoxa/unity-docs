# Tham chiếu NetworkObject và NetworkBehaviour

## NetworkObject <a href="#networkobject" id="networkobject"></a>

`public sealed class NetworkObject : MonoBehaviour, INetworkEntity` trong `Fomoxa.Unity`, đánh dấu `[DisallowMultipleComponent]` và được giải thích trong hướng dẫn [NetworkObject](../objects/network-object.md). `INetworkEntity` là interface mà tầng 1 dùng để xử lý object, nên có thể truyền một `NetworkObject` vào mọi chỗ manager nhận `INetworkEntity`.

| Member | Type | Mô tả |
|---|---|---|
| `ObjectId` | `uint` | Do server gán khi spawn; 0 khi chưa spawn |
| `PrefabId` | `uint` | Prefab id |
| `SceneObjectId` | `ulong` | Scene object id; 0 với instance prefab |
| `OwnerId` | `ulong` | Peer id của owner; 0 với server hoặc khi chưa spawn |
| `IsOwner` | `bool` | True trên client sở hữu, kể cả client của host; false trên dedicated server |
| `IsSpawned` | `bool` | Đã spawn trên server hoặc trên một client trong tiến trình này |
| `DespawnWithOwner` | `bool` | Đọc và ghi. Despawn khi owner ngắt kết nối; nếu không, server nhận ownership. |
| `Visibility` | `NetworkVisibility` | Đọc và ghi. `Rule`, `Everyone` hoặc `OwnerOnly`. |
| `Behaviours` | `IReadOnlyList<NetworkBehaviour>` | Các behaviour của object theo thứ tự behaviour index; được điền khi spawn |
| `Body` | `PhysicsBody` | Body của `Rigidbody` trên GameObject này, lấy từ component physics của `NetworkManager`; không hợp lệ khi không có hoặc object chưa spawn |
| `Body2D` | `PhysicsBody2D` | Body của `Rigidbody2D` trên GameObject này; không hợp lệ khi nó tắt Simulated |
| `Bodies` | `IReadOnlyList<PhysicsBody>` | Mọi body của object, body trên GameObject này đứng đầu; rỗng trước khi spawn. Xem [nhiều body](../physics/overview.md#several-bodies) |
| `Bodies2D` | `IReadOnlyList<PhysicsBody2D>` | Như trên với `Rigidbody2D` |

### NetworkVisibility <a href="#networkvisibility" id="networkvisibility"></a>

`public enum NetworkVisibility` trong `Fomoxa.Networking`.

| Giá trị | Observer |
|---|---|
| `Rule` | Do Observer Rule của `NetworkManager` quyết định; mọi người khi không có rule |
| `Everyone` | Mọi peer |
| `OwnerOnly` | Chỉ owner |

Dù giá trị là gì, owner luôn observe object của nó, và network scene giới hạn observer trong mọi trường hợp.

## NetworkBehaviour <a href="#networkbehaviour" id="networkbehaviour"></a>

`public abstract class NetworkBehaviour : MonoBehaviour` trong `Fomoxa.Unity`, được giải thích trong hướng dẫn [NetworkBehaviour](../objects/network-behaviour.md).

### Property <a href="#properties" id="properties"></a>

| Member | Type | Mô tả |
|---|---|---|
| `NetworkObject` | `NetworkObject` | Object chứa nó; null cho tới lần spawn đầu tiên |
| `BehaviourIndex` | `byte` | Vị trí trong `NetworkObject.Behaviours` |
| `IsPredicting` | `bool` | Client của owner đang dự đoán behaviour này |
| `IsReplaying` | `bool` | Client đang replay input |
| `ReconcileCount` | `int` | Số lần sửa kể từ khi behaviour được tạo |

### Callback có thể override <a href="#overridable-callbacks" id="overridable-callbacks"></a>

| Member | Truy cập | Chạy |
|---|---|---|
| `OnStartServer()` | `public virtual` | Sau khi object spawn trên server |
| `OnStopServer()` | `public virtual` | Trước khi object despawn trên server |
| `OnStartClient()` | `public virtual` | Sau khi object xuất hiện trên client và state ban đầu được áp dụng |
| `OnStopClient()` | `public virtual` | Trước khi object biến mất khỏi client |
| `OnOwnerChangedServer(ulong previousOwnerId)` | `public virtual` | Trên server sau khi đổi owner |
| `OnOwnerChangedClient(ulong previousOwnerId)` | `public virtual` | Trên các client đang observe sau khi đổi owner |
| `OnHostVisibility(bool visible)` | `protected virtual` | Trên host khi client của nó thôi hoặc bắt đầu observe object |
| `OnGatherInput()` | `protected virtual` | Trên client của owner mỗi tick một lần, trước khi các field `[NetworkInput]` được chép |
| `OnApplyInput(InputContext context)` | `protected virtual` | Sau khi input của một tick đã được ghi vào các field `[NetworkInput]` |
| `OnCaptureState()` | `protected virtual` | Trước khi các field `[NetworkReconcile]` được chép |
| `OnRestoreState()` | `protected virtual` | Sau khi state của server đã được ghi vào các field `[NetworkReconcile]` |
| `OnReconciled(uint tick)` | `protected virtual` | Trên client của owner sau một lần sửa tại `tick` |

`OnRegisterGeneratedRpcs`, `OnRegisterGeneratedState` và `OnRegisterGeneratedInput` được source generator dùng và ẩn khỏi IntelliSense, nên đừng override chúng.

### Method gửi <a href="#send-methods" id="send-methods"></a>

Mọi method gửi đều là `protected`. Với mỗi RPC, source generator thêm `Send<Method>ServerRpc(...)`, hoặc `Send<Method>ObserversRpc(...)` và `Send<Method>TargetRpc(ulong peerId, ...)`, nhận các tham số được gửi của RPC, như mô tả trong [RPC](../messaging/rpc.md#sending). Chúng gọi các member sau:

| Member | Trả về |
|---|---|
| `SendServerRpc(string rpc)` | `SendResult` |
| `SendServerRpc<TValues>(string rpc, TValues values)` | `SendResult` |
| `SendObserversRpc(string rpc)` | `int`, số observer đã đưa vào queue |
| `SendObserversRpc<TValues>(string rpc, TValues values)` | `int` |
| `SendTargetRpc(ulong peerId, string rpc)` | `SendResult` |
| `SendTargetRpc<TValues>(ulong peerId, string rpc, TValues values)` | `SendResult` |

`values` là một giá trị, hoặc một tuple khi có nhiều giá trị. Các member ném `ArgumentNullException` khi tên là null hoặc một giá trị `string` hay model là null, `InvalidOperationException` khi object chưa spawn ở phía gửi hoặc RPC chưa có model được sinh (`... has no generated parameterless RPC model ...` hoặc `... has no generated RPC model for its parameters ...`), và `ArgumentException` khi `values` không có đúng type các tham số của RPC.

### State <a href="#state" id="state"></a>

`protected void SetStateDirty()` đánh dấu state của behaviour là đã thay đổi, để server so sánh và gửi nó sau tick hiện tại. Nó chỉ có tác dụng khi class mang `[NetworkStateModel(OnlyWhenDirty = true)]`, như mô tả trong [đánh dấu thay đổi](../synchronization/state.md#marking-changes), và không làm gì trong trường hợp khác.

## Type đăng ký <a href="#registration-types" id="registration-types"></a>

`NetworkBehaviour` đăng ký RPC, state và input qua attribute. Các type dưới đây là API đăng ký của `EntityBehaviour`, mà [console server](../console-server/runtime.md) dùng.

### NetworkRpcs <a href="#networkrpcs" id="networkrpcs"></a>

`public sealed class NetworkRpcs` được truyền vào `EntityBehaviour.OnRegisterRpcs`.

| Member | Mô tả |
|---|---|
| `OnServer<T>(IMessageCodec<T> codec, Action<ulong, T> handler, bool requireOwnership = true) where T : new()` | Server RPC có model |
| `OnClient<T>(IMessageCodec<T> codec, Action<T> handler) where T : new()` | Client RPC có model |
| `OnServer(string rpc, Action<ulong> handler, bool requireOwnership = true)` | Server RPC không tham số |
| `OnClient(string rpc, Action handler)` | Client RPC không tham số |

Đăng ký cùng một message id hai lần trên một behaviour sẽ ném `HandlerRegistrationException`.

### NetworkState <a href="#networkstate" id="networkstate"></a>

`public sealed class NetworkState` được truyền vào `EntityBehaviour.OnRegisterState`.

| Member | Mô tả |
|---|---|
| `Use<T>(IMessageCodec<T> codec, T instance, Action<T> onChanged = null, bool onlyWhenDirty = false) where T : class, new()` | Đăng ký state của behaviour. `onChanged` nhận giá trị trước đó. Với `onlyWhenDirty`, server chỉ so sánh state sau `SetStateDirty()`. |
| `Use<T>(byte index, NetworkList<T> list, IMessageCodec<T> codec, NetworkListChanged<T> onChanged = null) where T : class, new()` | Đăng ký một list model dưới `index`. |
| `Use<T>(byte index, NetworkList<T> list, NetworkListChanged<T> onChanged = null)` | Đăng ký một list kiểu nguyên thuỷ. |
| `Use<TKey, TValue>(byte index, NetworkDictionary<TKey, TValue> dictionary, IMessageCodec<TValue> codec, NetworkDictionaryChanged<TKey, TValue> onChanged = null) where TValue : class, new()` | Đăng ký một dictionary có value là model. |
| `Use<TKey, TValue>(byte index, NetworkDictionary<TKey, TValue> dictionary, NetworkDictionaryChanged<TKey, TValue> onChanged = null)` | Đăng ký một dictionary có value kiểu nguyên thuỷ. |
| `Use<T>(byte index, NetworkSet<T> set, NetworkSetChanged<T> onChanged = null)` | Đăng ký một set kiểu nguyên thuỷ. |

### Collection <a href="#collections" id="collections"></a>

Các type collection nằm trong `Fomoxa.Networking`. Thao tác và callback của chúng được mô tả trong [collection](../synchronization/collections.md).

| Type | Mô tả |
|---|---|
| `NetworkList<T>` | Một list; hiện thực `IReadOnlyList<T>` |
| `NetworkDictionary<TKey, TValue>` | Một dictionary; hiện thực `IReadOnlyDictionary<TKey, TValue>` |
| `NetworkSet<T>` | Một set; hiện thực `IReadOnlyCollection<T>` |
| `NetworkListOperation`, `NetworkDictionaryOperation`, `NetworkSetOperation` | Thao tác truyền vào callback |
| `NetworkListChanged<T>`, `NetworkDictionaryChanged<TKey, TValue>`, `NetworkSetChanged<T>` | Các type callback |
| `NetworkCollections` | Các extension method `Modify` cho list và dictionary chứa model |

### NetworkInput <a href="#networkinput" id="networkinput"></a>

`public sealed class NetworkInput` được truyền vào `EntityBehaviour.OnRegisterInput`.

| Member | Mô tả |
|---|---|
| `Use<T>(IMessageCodec<T> codec, Action<T> gather, Action<T, InputContext> apply) where T : class, new()` | Đăng ký input model |
| `Reconcile<TState>(IMessageCodec<TState> codec, Action<TState> capture, Action<TState> restore, Func<TState, TState, bool> matches = null) where TState : class, new()` | Đăng ký reconcile model, sau `Use` |

### InputContext <a href="#inputcontext" id="inputcontext"></a>

`public readonly struct InputContext`.

| Member | Type | Mô tả |
|---|---|---|
| `Tick` | `uint` | Tick của input |
| `Repeated` | `bool` | Input cuối được dùng lại cho một tick không có input |
| `RepeatedTicks` | `uint` | Khi bị lặp, số tick kể từ tick của input được dùng lại; ngoài ra là 0 |
| `Replaying` | `bool` | Lời gọi là một phần của lần replay trên client của owner |

Các component khác được liệt kê trong [tham chiếu component](components.md). [Tham chiếu ServerManager](server-manager.md) nói về spawn và ownership, và [physics API](physics.md) nói về `PhysicsBody`.
