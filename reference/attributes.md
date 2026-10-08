# Attributes reference

## Model attributes

These attributes come from `Fomoxa.Attributes.dll`, in the namespace `Fomoxa`, and are explained in [models and codecs](../messaging/models.md).

| Attribute | Target | Arguments | Meaning |
|---|---|---|---|
| `[Network]` | Class | none | The class is a model |
| `[Codec("name", ...)]` | Class, repeatable | One or more codec names | The model has these codecs |
| `[Network("type")]` | Property or field | Wire type | The member is a field of this type |
| `[Codec("name", ...)]` | Property or field, repeatable | One or more codec names | The member belongs to these codecs |

`[Codec("net", "compact")]` is the same as `[Codec("net")] [Codec("compact")]`. A codec carries a member only when the member has both `[Network("type")]` and `[Codec]`.

## NetworkChannelAttribute

`[NetworkChannel(string codec, Channel channel)]`, in the namespace `Fomoxa.Networking`, goes on a class and can be repeated once per codec. [Channels](../messaging/channels.md) explains how it is used.

| Property | Type | Meaning |
|---|---|---|
| `Codec` | `string` | A codec the model declares |
| `Channel` | `Channel` | `Unreliable` or `ReliableOrdered` |

## ServerRpcAttribute

`[ServerRpc]` or `[ServerRpc("ModelName")]`, in the namespace `Fomoxa.Networking`, goes on a method. [RPCs](../messaging/rpc.md) explains how it is used.

| Property | Type | Default | Meaning |
|---|---|---|---|
| `Model` | `string` | `<Type><Method>` | Name of the generated model of a parameterless RPC; set with the constructor |
| `Codec` | `string` | the model's only codec | Codec of the model argument; required when the model has several |
| `Channel` | `Channel` | `ReliableOrdered` | Channel of a parameterless RPC |
| `RequireOwnership` | `bool` | `true` | Only the owner may call it |

The method can have one of the signatures `void M()`, `void M(ulong peerId)`, `void M(TModel value)` and `void M(ulong peerId, TModel value)`.

## ClientRpcAttribute

`[ClientRpc]` or `[ClientRpc("ModelName")]`, in the namespace `Fomoxa.Networking`, goes on a method.

| Property | Type | Default | Meaning |
|---|---|---|---|
| `Model` | `string` | `<Type><Method>` | Name of the generated model of a parameterless RPC |
| `Codec` | `string` | the model's only codec | Codec of the model argument |
| `Channel` | `Channel` | `ReliableOrdered` | Channel of a parameterless RPC |

The method can have the signature `void M()` or `void M(TModel value)`.

## NetworkRpcAttribute

`[NetworkRpc]` or `[NetworkRpc("ModelName")]`, in the namespace `Fomoxa.Networking`, goes on a method without parameters. It generates the model of a parameterless RPC without generating its registration, so you register the RPC yourself in `OnRegisterRpcs`.

| Property | Type | Default | Meaning |
|---|---|---|---|
| `Model` | `string` | `<Type><Method>` | Name of the generated model |
| `Channel` | `Channel` | `ReliableOrdered` | Channel of the RPC |

## MessageAdapterAttribute

`[MessageAdapter(string codec)]`, in the namespace `Fomoxa.Networking`, is written on every generated adapter class, and the RPC source generator uses it to find the adapter of a model and codec. Do not put it on your own classes.

## Rules

A method carries at most one of `[NetworkRpc]`, `[ServerRpc]` and `[ClientRpc]`, and a class with `[ServerRpc]` or `[ClientRpc]` methods must be `partial`, as must every class containing it. `Model` and `Channel` apply only to RPCs without a model argument, and `Codec` only to RPCs with one. No two parameterless RPCs in the project can have the same model name.

[RPCs](../messaging/rpc.md#compile-errors) lists the compile errors for broken rules.
