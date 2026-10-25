# NetworkObject and NetworkBehaviour reference

## NetworkObject

`public sealed class NetworkObject : MonoBehaviour, INetworkEntity` in `Fomoxa.Unity`, marked `[DisallowMultipleComponent]` and explained in the [NetworkObject](../objects/network-object.md) guide. `INetworkEntity` is the interface through which layer 1 handles the object, so a `NetworkObject` can be passed wherever the managers take an `INetworkEntity`.

| Member | Type | Description |
|---|---|---|
| `ObjectId` | `uint` | Assigned by the server at spawn; 0 while not spawned |
| `PrefabId` | `uint` | The prefab id |
| `SceneObjectId` | `ulong` | The scene object id; 0 for prefab instances |
| `OwnerId` | `ulong` | The owner's peer id; 0 for the server or when not spawned |
| `IsOwner` | `bool` | True on the owning client, including a host's client; false on a dedicated server |
| `IsSpawned` | `bool` | Spawned on the server or on a client in this process |
| `DespawnWithOwner` | `bool` | Get and set. Despawn when the owner disconnects; otherwise the server takes ownership. |
| `Visibility` | `NetworkVisibility` | Get and set. `Rule`, `Everyone` or `OwnerOnly`. |
| `Behaviours` | `IReadOnlyList<NetworkBehaviour>` | The object's behaviours in behaviour index order; filled at spawn |
| `Body` | `PhysicsBody` | The body of the `Rigidbody` on this GameObject, from the physics component of the `NetworkManager`; invalid when there is none or the object is not spawned |
| `Body2D` | `PhysicsBody2D` | The body of the `Rigidbody2D` on this GameObject |

### NetworkVisibility

`public enum NetworkVisibility` in `Fomoxa.Networking`.

| Value | Observers |
|---|---|
| `Rule` | Decided by the `NetworkManager`'s Observer Rule; everyone when there is none |
| `Everyone` | Every peer |
| `OwnerOnly` | The owner only |

Whatever the value, the owner always observes its objects, and network scenes restrict observers in every case.

## NetworkBehaviour

`public abstract class NetworkBehaviour : MonoBehaviour` in `Fomoxa.Unity`, explained in the [NetworkBehaviour](../objects/network-behaviour.md) guide.

### Properties

| Member | Type | Description |
|---|---|---|
| `NetworkObject` | `NetworkObject` | The owning object; null until its first spawn |
| `BehaviourIndex` | `byte` | Position in `NetworkObject.Behaviours` |
| `IsPredicting` | `bool` | The owner's client predicts this behaviour |
| `IsReplaying` | `bool` | The client replays input |
| `ReconcileCount` | `int` | Corrections since the behaviour was created |

### Overridable callbacks

| Member | Access | Runs |
|---|---|---|
| `OnStartServer()` | `public virtual` | After the object spawned on the server |
| `OnStopServer()` | `public virtual` | Before the object despawns on the server |
| `OnStartClient()` | `public virtual` | After the object appeared on a client and its initial state was applied |
| `OnStopClient()` | `public virtual` | Before the object disappears from a client |
| `OnOwnerChangedServer(ulong previousOwnerId)` | `public virtual` | On the server after an owner change |
| `OnOwnerChangedClient(ulong previousOwnerId)` | `public virtual` | On observing clients after an owner change |
| `OnHostVisibility(bool visible)` | `protected virtual` | On a host when its client stops or starts observing the object |
| `OnRegisterRpcs(NetworkRpcs rpc)` | `protected virtual` | Once per instance, at its first spawn |
| `OnRegisterState(NetworkState state)` | `protected virtual` | Once per instance, at its first spawn |
| `OnRegisterInput(NetworkInput input)` | `protected virtual` | Once per instance, at its first spawn |
| `OnReconciled(uint tick)` | `protected virtual` | On the owner's client after a correction at `tick` |

`OnRegisterGeneratedRpcs` is used by the source generator and hidden from IntelliSense, so do not override it.

### Send methods

All send methods are `protected`.

| Member | Returns |
|---|---|
| `SendServerRpc<T>(IMessageCodec<T> codec, T value)` | `SendResult` |
| `SendServerRpc(string rpc)` | `SendResult` |
| `SendObserversRpc<T>(IMessageCodec<T> codec, T value)` | `int`, observers queued for |
| `SendObserversRpc(string rpc)` | `int` |
| `SendTargetRpc<T>(ulong peerId, IMessageCodec<T> codec, T value)` | `SendResult` |
| `SendTargetRpc(ulong peerId, string rpc)` | `SendResult` |

They throw `ArgumentNullException` for a null codec, value or name, and `InvalidOperationException` when the object is not spawned on the sending side. For a name without a generated model they also throw `InvalidOperationException`, with the message `... has no generated parameterless RPC model ...`.

### State

`protected void SetStateDirty()` marks the behaviour's state as changed, so the server compares and sends it after the current tick. It only has an effect on a state registered with `onlyWhenDirty`, as described in [marking changes](../synchronization/state.md#marking-changes), and does nothing otherwise.

## Registration types

### NetworkRpcs

`public sealed class NetworkRpcs` is passed to `OnRegisterRpcs`, as described in [RPCs](../messaging/rpc.md#registering-by-hand).

| Member | Description |
|---|---|
| `OnServer<T>(IMessageCodec<T> codec, Action<ulong, T> handler, bool requireOwnership = true) where T : new()` | Server RPC with a model |
| `OnClient<T>(IMessageCodec<T> codec, Action<T> handler) where T : new()` | Client RPC with a model |
| `OnServer(string rpc, Action<ulong> handler, bool requireOwnership = true)` | Parameterless server RPC |
| `OnClient(string rpc, Action handler)` | Parameterless client RPC |

Registering the same message id twice on one behaviour throws `HandlerRegistrationException`.

### NetworkState

`public sealed class NetworkState` is passed to `OnRegisterState`, as described in [state](../synchronization/state.md).

| Member | Description |
|---|---|
| `Use<T>(IMessageCodec<T> codec, T instance, Action<T> onChanged = null, bool onlyWhenDirty = false) where T : class, new()` | Registers the behaviour's state. `onChanged` receives the previous values. With `onlyWhenDirty`, the server compares the state only after `SetStateDirty()`. |
| `Use<T>(byte index, NetworkList<T> list, IMessageCodec<T> codec, NetworkListChanged<T> onChanged = null) where T : class, new()` | Registers a list of models under `index`, as described in [collections](../synchronization/collections.md). |
| `Use<T>(byte index, NetworkList<T> list, NetworkListChanged<T> onChanged = null)` | Registers a list of a primitive type. |
| `Use<TKey, TValue>(byte index, NetworkDictionary<TKey, TValue> dictionary, IMessageCodec<TValue> codec, NetworkDictionaryChanged<TKey, TValue> onChanged = null) where TValue : class, new()` | Registers a dictionary whose values are models. |
| `Use<TKey, TValue>(byte index, NetworkDictionary<TKey, TValue> dictionary, NetworkDictionaryChanged<TKey, TValue> onChanged = null)` | Registers a dictionary whose values are a primitive type. |
| `Use<T>(byte index, NetworkSet<T> set, NetworkSetChanged<T> onChanged = null)` | Registers a set of a primitive type. |

### Collections

The collection types are in `Fomoxa.Networking`. Their operations and callbacks are described in [collections](../synchronization/collections.md).

| Type | Description |
|---|---|
| `NetworkList<T>` | A list; implements `IReadOnlyList<T>` |
| `NetworkDictionary<TKey, TValue>` | A dictionary; implements `IReadOnlyDictionary<TKey, TValue>` |
| `NetworkSet<T>` | A set; implements `IReadOnlyCollection<T>` |
| `NetworkListOperation`, `NetworkDictionaryOperation`, `NetworkSetOperation` | The operation passed to a callback |
| `NetworkListChanged<T>`, `NetworkDictionaryChanged<TKey, TValue>`, `NetworkSetChanged<T>` | The callback types |
| `NetworkCollections` | The `Modify` extension methods for lists and dictionaries of models |

### NetworkInput

`public sealed class NetworkInput` is passed to `OnRegisterInput`, as described in [input](../prediction/input.md) and [reconciliation](../prediction/reconciliation.md).

| Member | Description |
|---|---|
| `Use<T>(IMessageCodec<T> codec, Action<T> gather, Action<T, InputContext> apply) where T : class, new()` | Registers the input model |
| `Reconcile<TState>(IMessageCodec<TState> codec, Action<TState> capture, Action<TState> restore, Func<TState, TState, bool> matches = null) where TState : class, new()` | Registers the reconcile model, after `Use` |

### InputContext

`public readonly struct InputContext`.

| Member | Type | Description |
|---|---|---|
| `Tick` | `uint` | The tick of the input |
| `Repeated` | `bool` | The last input is reused for a tick without input |
| `RepeatedTicks` | `uint` | When repeated, the ticks since the reused input's tick; otherwise 0 |
| `Replaying` | `bool` | The call is part of a replay on the owner's client |

The other components are listed in the [components reference](components.md). The [ServerManager reference](server-manager.md) covers spawning and ownership, and the [physics API](physics.md) covers `PhysicsBody`.
