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

`[NetworkChannel(string codec, Channel channel)]`, trong namespace `Fomoxa.Unity`, đặt trên class và có thể lặp lại, mỗi codec một lần. [Channel](../messaging/channels.md) giải thích cách dùng nó.

| Property | Type | Ý nghĩa |
|---|---|---|
| `Codec` | `string` | Một codec mà model khai báo |
| `Channel` | `Channel` | `Unreliable` hoặc `ReliableOrdered` |

## ServerRpcAttribute <a href="#serverrpcattribute" id="serverrpcattribute"></a>

`[ServerRpc]` hoặc `[ServerRpc("ModelName")]`, trong namespace `Fomoxa.Unity`, đặt trên method. [RPC](../messaging/rpc.md) giải thích cách dùng nó.

| Property | Type | Mặc định | Ý nghĩa |
|---|---|---|---|
| `Model` | `string` | `<Type><Method>` | Tên model được sinh của RPC không tham số; đặt qua constructor |
| `Codec` | `string` | codec duy nhất của model | Codec của tham số model; bắt buộc khi model có nhiều codec |
| `Channel` | `Channel` | `ReliableOrdered` | Channel của RPC không tham số |
| `RequireOwnership` | `bool` | `true` | Chỉ owner được gọi |

Method có thể có một trong các chữ ký `void M()`, `void M(ulong peerId)`, `void M(TModel value)` và `void M(ulong peerId, TModel value)`.

## ClientRpcAttribute <a href="#clientrpcattribute" id="clientrpcattribute"></a>

`[ClientRpc]` hoặc `[ClientRpc("ModelName")]`, trong namespace `Fomoxa.Unity`, đặt trên method.

| Property | Type | Mặc định | Ý nghĩa |
|---|---|---|---|
| `Model` | `string` | `<Type><Method>` | Tên model được sinh của RPC không tham số |
| `Codec` | `string` | codec duy nhất của model | Codec của tham số model |
| `Channel` | `Channel` | `ReliableOrdered` | Channel của RPC không tham số |

Method có thể có chữ ký `void M()` hoặc `void M(TModel value)`.

## NetworkRpcAttribute <a href="#networkrpcattribute" id="networkrpcattribute"></a>

`[NetworkRpc]` hoặc `[NetworkRpc("ModelName")]`, trong namespace `Fomoxa.Unity`, đặt trên method không tham số. Nó sinh model của RPC không tham số mà không sinh phần đăng ký, nên bạn tự đăng ký RPC trong `OnRegisterRpcs`.

| Property | Type | Mặc định | Ý nghĩa |
|---|---|---|---|
| `Model` | `string` | `<Type><Method>` | Tên model được sinh |
| `Channel` | `Channel` | `ReliableOrdered` | Channel của RPC |

## MessageAdapterAttribute <a href="#messageadapterattribute" id="messageadapterattribute"></a>

`[MessageAdapter(string codec)]`, trong namespace `Fomoxa.Unity`, được viết trên mọi class adapter được sinh, và source generator cho RPC dùng nó để tìm adapter của một model và codec. Đừng đặt nó trên class của riêng bạn.

## Quy tắc <a href="#rules" id="rules"></a>

Một method mang nhiều nhất một trong `[NetworkRpc]`, `[ServerRpc]` và `[ClientRpc]`, và class có method `[ServerRpc]` hoặc `[ClientRpc]` phải là `partial`, mọi class chứa nó cũng vậy. `Model` và `Channel` chỉ áp dụng cho RPC không có tham số model, và `Codec` chỉ áp dụng cho RPC có tham số model. Không có hai RPC không tham số nào trong project được trùng tên model.

[RPC](../messaging/rpc.md#compile-errors) liệt kê các lỗi biên dịch khi vi phạm quy tắc.
