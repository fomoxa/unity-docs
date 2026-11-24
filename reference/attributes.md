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
| `Model` | `string` | `<Type><Method>` | Name of the generated model; set with the constructor |
| `Channel` | `Channel` | `ReliableOrdered` | Channel of the RPC |
| `RequireOwnership` | `bool` | `true` | Only the owner may call it |
| `Codec` | `string` | the model's only codec | On an `EntityBehaviour`, the codec of the model argument |

On a `NetworkBehaviour` the method is `void M(...)` with any parameters, and a first parameter of type `ulong` receives the caller's peer id. On an `EntityBehaviour` it is `void M()`, `void M(ulong peerId)`, `void M(TModel value)` or `void M(ulong peerId, TModel value)`, and `Model` and `Channel` apply only to the first two.

## ClientRpcAttribute

`[ClientRpc]` or `[ClientRpc("ModelName")]`, in the namespace `Fomoxa.Networking`, goes on a method.

| Property | Type | Default | Meaning |
|---|---|---|---|
| `Model` | `string` | `<Type><Method>` | Name of the generated model |
| `Channel` | `Channel` | `ReliableOrdered` | Channel of the RPC |
| `Codec` | `string` | the model's only codec | On an `EntityBehaviour`, the codec of the model argument |

On a `NetworkBehaviour` the method is `void M(...)` with any parameters. On an `EntityBehaviour` it is `void M()` or `void M(TModel value)`.

## NetworkTypeAttribute

`[NetworkType("type")]`, in the namespace `Fomoxa.Networking`, goes on a parameter of an RPC on a `NetworkBehaviour`. The string is the wire type of the parameter, written like the argument of `[Network("type")]`, for example `"f16"` or `"Array<u32>"`.

## NetworkStateAttribute

`[NetworkState]` or `[NetworkState("type")]`, in the namespace `Fomoxa.Networking`, goes on an instance field of a `NetworkBehaviour`. [State](../synchronization/state.md) and [collections](../synchronization/collections.md) explain how it is used.

| Property | Type | Default | Meaning |
|---|---|---|---|
| `WireType` | `string` | inferred from the field's type | Wire type of a state field; set with the constructor |
| `OnChanged` | `string` | none | Method called on clients after a change: `void M(T previous, T current)` for a state field, the collection's callback signature for a collection |
| `Index` | `byte` | none | Index of a collection field; required on a collection and not allowed otherwise |

## NetworkStateModelAttribute

`[NetworkStateModel]` or `[NetworkStateModel("ModelName")]`, in the namespace `Fomoxa.Networking`, goes on a `NetworkBehaviour` class and applies to that class only, not to derived classes.

| Property | Type | Default | Meaning |
|---|---|---|---|
| `Model` | `string` | `<Type>State` | Name of the generated state model; set with the constructor |
| `OnlyWhenDirty` | `bool` | `false` | The server compares the state only after `SetStateDirty()` |

## NetworkInputAttribute and NetworkReconcileAttribute

`[NetworkInput]` or `[NetworkInput("type")]`, and `[NetworkReconcile]` or `[NetworkReconcile("type")]`, in the namespace `Fomoxa.Networking`, go on instance fields of a `NetworkBehaviour`. [Input](../prediction/input.md) and [reconciliation](../prediction/reconciliation.md) explain how they are used.

| Property | Type | Default | Meaning |
|---|---|---|---|
| `WireType` | `string` | inferred from the field's type | Wire type of the field; set with the constructor |
| `Tolerance` | `float` | none | `[NetworkReconcile]` only: how far the predicted value may be from the server's, for `float`, `double`, `Vector2`, `Vector3`, `Vector4` (per component) and `Quaternion` (in degrees) |

## NetworkInputModelAttribute and NetworkReconcileModelAttribute

`[NetworkInputModel("ModelName")]` and `[NetworkReconcileModel("ModelName")]`, in the namespace `Fomoxa.Networking`, go on a `NetworkBehaviour` class and name its generated input model and reconcile model. Without them the names are `<Type>Input` and `<Type>Reconcile`.

## NetworkRpcAttribute

`[NetworkRpc]` or `[NetworkRpc("ModelName")]`, in the namespace `Fomoxa.Networking`, goes on a parameterless method of an `EntityBehaviour` whose RPC is registered by hand in `OnRegisterRpcs`. On a `NetworkBehaviour` it is the compile error `FOMOXA022`; use `[ServerRpc]` or `[ClientRpc]` there.

| Property | Type | Default | Meaning |
|---|---|---|---|
| `Model` | `string` | `<Type><Method>` | Name of the model |
| `Channel` | `Channel` | `ReliableOrdered` | Channel of the RPC |

## MessageAdapterAttribute

`[MessageAdapter(string codec)]`, in the namespace `Fomoxa.Networking`, is written on every generated adapter class, and the RPC source generator uses it to find the adapter of a model and codec. Do not put it on your own classes.

## Rules

A method carries at most one of `[NetworkRpc]`, `[ServerRpc]` and `[ClientRpc]`, and a field at most one of `[NetworkState]`, `[NetworkInput]` and `[NetworkReconcile]`. A class with RPC methods or with such fields, its own or inherited, must be `partial`, as must every class containing it. No two RPCs in the project can have the same model name, and no two state, input or reconcile models either.

[RPCs](../messaging/rpc.md#compile-errors), [state](../synchronization/state.md#errors) and [collections](../synchronization/collections.md#errors) list the compile errors for broken rules.
