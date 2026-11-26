# Tham chiếu attribute

## Attribute của model <a href="#model-attributes" id="model-attributes"></a>

Các attribute này đến từ `Fomoxa.Attributes.dll`, trong namespace `Fomoxa`, và được giải thích trong [model và codec](../messaging/models.md).

| Attribute | Đặt trên | Tham số | Ý nghĩa |
|---|---|---|---|
| `[Network]` | Class | không có | Class là một model |
| `[Codec("name", ...)]` | Class, lặp lại được | Một hoặc nhiều tên codec | Model có các codec này |
| `[Network("type")]` | Property hoặc field | Wire type | Member là một field mang type này |
| `[Codec("name", ...)]` | Property hoặc field, lặp lại được | Một hoặc nhiều tên codec | Member thuộc về các codec này |

`[Codec("net", "compact")]` tương đương `[Codec("net")] [Codec("compact")]`. Một codec chỉ mang một member khi member đó có cả `[Network("type")]` và `[Codec]`.

## NetworkChannelAttribute <a href="#networkchannelattribute" id="networkchannelattribute"></a>

`[NetworkChannel(string codec, Channel channel)]`, trong namespace `Fomoxa.Networking`, đặt trên class và có thể lặp lại, mỗi codec một lần. [Channel](../messaging/channels.md) giải thích cách dùng nó.

| Property | Type | Ý nghĩa |
|---|---|---|
| `Codec` | `string` | Một codec mà model khai báo |
| `Channel` | `Channel` | `Unreliable` hoặc `ReliableOrdered` |

## ServerRpcAttribute <a href="#serverrpcattribute" id="serverrpcattribute"></a>

`[ServerRpc]` hoặc `[ServerRpc("ModelName")]`, trong namespace `Fomoxa.Networking`, đặt trên method. [RPC](../messaging/rpc.md) giải thích cách dùng nó.

| Property | Type | Mặc định | Ý nghĩa |
|---|---|---|---|
| `Model` | `string` | `<Type><Method>` | Tên model được sinh; đặt qua constructor |
| `Channel` | `Channel` | `ReliableOrdered` | Channel của RPC |
| `RequireOwnership` | `bool` | `true` | Chỉ owner được gọi |
| `Codec` | `string` | codec duy nhất của model | Trên `EntityBehaviour`, codec của tham số model |

Trên `NetworkBehaviour`, method là `void M(...)` với tham số bất kỳ, và tham số đầu tiên có type `ulong` nhận peer id của bên gọi. Trên `EntityBehaviour`, method là `void M()`, `void M(ulong peerId)`, `void M(TModel value)` hoặc `void M(ulong peerId, TModel value)`, và `Model`, `Channel` chỉ áp dụng cho hai dạng đầu.

## ClientRpcAttribute <a href="#clientrpcattribute" id="clientrpcattribute"></a>

`[ClientRpc]` hoặc `[ClientRpc("ModelName")]`, trong namespace `Fomoxa.Networking`, đặt trên method.

| Property | Type | Mặc định | Ý nghĩa |
|---|---|---|---|
| `Model` | `string` | `<Type><Method>` | Tên model được sinh |
| `Channel` | `Channel` | `ReliableOrdered` | Channel của RPC |
| `Codec` | `string` | codec duy nhất của model | Trên `EntityBehaviour`, codec của tham số model |

Trên `NetworkBehaviour`, method là `void M(...)` với tham số bất kỳ. Trên `EntityBehaviour`, method là `void M()` hoặc `void M(TModel value)`.

## ServerMessageAttribute và ClientMessageAttribute <a href="#servermessageattribute-and-clientmessageattribute" id="servermessageattribute-and-clientmessageattribute"></a>

`[ServerMessage]`, `[ServerMessage("ModelName")]`, `[ClientMessage]` và `[ClientMessage("ModelName")]`, trong namespace `Fomoxa.Unity`, đặt trên method của một `NetworkMessageBehaviour`. [Raw message](../messaging/messages.md#declaring-messages) giải thích cách dùng chúng.

| Property | Type | Mặc định | Ý nghĩa |
|---|---|---|---|
| `Model` | `string` | `<Type><Method>` | Tên model được sinh; đặt qua constructor |
| `Channel` | `Channel` | `ReliableOrdered` | Channel của message |

Method `[ServerMessage]` là `void M(...)`, và tham số đầu tiên có type `ulong` nhận peer id của bên gửi. Method `[ClientMessage]` là `void M(...)`, và mọi tham số đều được gửi.

## NetworkTypeAttribute <a href="#networktypeattribute" id="networktypeattribute"></a>

`[NetworkType("type")]`, trong namespace `Fomoxa.Networking`, đặt trên một tham số của RPC trên `NetworkBehaviour` hoặc của message trên `NetworkMessageBehaviour`. Chuỗi là wire type của tham số, viết giống đối số của `[Network("type")]`, ví dụ `"f16"` hoặc `"Array<u32>"`.

## NetworkStateAttribute <a href="#networkstateattribute" id="networkstateattribute"></a>

`[NetworkState]` hoặc `[NetworkState("type")]`, trong namespace `Fomoxa.Networking`, đặt trên một field instance của `NetworkBehaviour`. [State](../synchronization/state.md) và [collection](../synchronization/collections.md) giải thích cách dùng nó.

| Property | Type | Mặc định | Ý nghĩa |
|---|---|---|---|
| `WireType` | `string` | suy ra từ type của field | Wire type của field state; đặt qua constructor |
| `OnChanged` | `string` | không có | Method được gọi trên client sau một thay đổi: `void M(T previous, T current)` với field state, chữ ký callback của collection với collection |
| `Index` | `byte` | không có | Index của field collection; bắt buộc với collection và không được dùng cho field khác |

## NetworkStateModelAttribute <a href="#networkstatemodelattribute" id="networkstatemodelattribute"></a>

`[NetworkStateModel]` hoặc `[NetworkStateModel("ModelName")]`, trong namespace `Fomoxa.Networking`, đặt trên một class `NetworkBehaviour` và chỉ áp dụng cho class đó, không áp cho class con.

| Property | Type | Mặc định | Ý nghĩa |
|---|---|---|---|
| `Model` | `string` | `<Type>State` | Tên state model được sinh; đặt qua constructor |
| `OnlyWhenDirty` | `bool` | `false` | Server chỉ so sánh state sau `SetStateDirty()` |

## NetworkInputAttribute và NetworkReconcileAttribute <a href="#networkinputattribute-and-networkreconcileattribute" id="networkinputattribute-and-networkreconcileattribute"></a>

`[NetworkInput]` hoặc `[NetworkInput("type")]`, và `[NetworkReconcile]` hoặc `[NetworkReconcile("type")]`, trong namespace `Fomoxa.Networking`, đặt trên các field instance của `NetworkBehaviour`. [Input](../prediction/input.md) và [reconciliation](../prediction/reconciliation.md) giải thích cách dùng chúng.

| Property | Type | Mặc định | Ý nghĩa |
|---|---|---|---|
| `WireType` | `string` | suy ra từ type của field | Wire type của field; đặt qua constructor |
| `Tolerance` | `float` | không có | Chỉ với `[NetworkReconcile]`: giá trị dự đoán được lệch khỏi giá trị của server bao xa, cho `float`, `double`, `Vector2`, `Vector3`, `Vector4` (từng thành phần) và `Quaternion` (tính bằng độ) |

## NetworkInputModelAttribute và NetworkReconcileModelAttribute <a href="#networkinputmodelattribute-and-networkreconcilemodelattribute" id="networkinputmodelattribute-and-networkreconcilemodelattribute"></a>

`[NetworkInputModel("ModelName")]` và `[NetworkReconcileModel("ModelName")]`, trong namespace `Fomoxa.Networking`, đặt trên một class `NetworkBehaviour` và đặt tên cho input model và reconcile model được sinh của nó. Không có chúng, tên là `<Type>Input` và `<Type>Reconcile`.

## NetworkRpcAttribute <a href="#networkrpcattribute" id="networkrpcattribute"></a>

`[NetworkRpc]` hoặc `[NetworkRpc("ModelName")]`, trong namespace `Fomoxa.Networking`, đặt trên method không tham số của một `EntityBehaviour` mà RPC được đăng ký thủ công trong `OnRegisterRpcs`. Trên `NetworkBehaviour` nó là lỗi biên dịch `FOMOXA022`; ở đó hãy dùng `[ServerRpc]` hoặc `[ClientRpc]`.

| Property | Type | Mặc định | Ý nghĩa |
|---|---|---|---|
| `Model` | `string` | `<Type><Method>` | Tên model |
| `Channel` | `Channel` | `ReliableOrdered` | Channel của RPC |

## MessageAdapterAttribute <a href="#messageadapterattribute" id="messageadapterattribute"></a>

`[MessageAdapter(string codec)]`, trong namespace `Fomoxa.Networking`, được viết trên mọi class adapter được sinh, và source generator cho RPC dùng nó để tìm adapter của một model và codec. Đừng đặt nó trên class của riêng bạn.

## Quy tắc <a href="#rules" id="rules"></a>

Một method mang nhiều nhất một trong `[NetworkRpc]`, `[ServerRpc]` và `[ClientRpc]`, và nhiều nhất một trong `[ServerMessage]` và `[ClientMessage]`. Một field mang nhiều nhất một trong `[NetworkState]`, `[NetworkInput]` và `[NetworkReconcile]`. Class có method RPC hoặc có field như vậy, của chính nó hay được kế thừa, phải là `partial`, mọi class chứa nó cũng vậy. Class có method message cũng phải `partial` như thế. Không có hai RPC nào trong project được trùng tên model, và hai state model, input model hay reconcile model cũng vậy. Tên model của một message phải khác tên của mọi model message, RPC và state khác.

[RPC](../messaging/rpc.md#compile-errors), [raw message](../messaging/messages.md#compile-errors), [state](../synchronization/state.md#errors) và [collection](../synchronization/collections.md#errors) liệt kê các lỗi biên dịch khi vi phạm quy tắc.
