# Components reference

This page covers the components and assets in `Fomoxa.Unity` other than `NetworkManager`, `NetworkObject` and `NetworkBehaviour`. Their Inspector fields are listed in [configuration](configuration.md).

## NetworkTransform

`public sealed class NetworkTransform : NetworkBehaviour`, explained in the [NetworkTransform](../synchronization/transform.md) guide.

| Member | Type | Description |
|---|---|---|
| `SyncPosition`, `SyncRotation`, `SyncScale` | `bool` | Which parts are replicated; read only |
| `InterpolationTicks` | `int` | Ticks behind the newest snapshot that clients show; read only |
| `Visual` | `Transform` | Get and set. Child smoothed after prediction corrections. |
| `SmoothingTime` | `float` | Get and set; negative values become 0 |
| `Teleport()` | `void` | On the server, makes clients jump to the next transform instead of interpolating. Does nothing elsewhere. |

## NetworkAnimator

`public sealed class NetworkAnimator : NetworkBehaviour`, marked `[RequireComponent(typeof(Animator))]` and explained in the [NetworkAnimator](../synchronization/animator.md) guide.

| Member | Type | Description |
|---|---|---|
| `Animator` | `Animator` | The replicated `Animator` |
| `FloatStep` | `float` | Rounding step of float parameters; read only |
| `SetTrigger(string triggerName)`, `SetTrigger(int hash)` | `void` | Fires a trigger and, on the server, replicates it. Throws `ArgumentException` for an unknown trigger. |

## Contact components

`NetworkCollision` and `NetworkTrigger` (3D) and `NetworkCollision2D` and `NetworkTrigger2D` (2D) are all `public sealed class ... : MonoBehaviour, IContactSource<...>`, explained in the [contact events](../physics/contacts.md) guide.

| Member | Type | Description |
|---|---|---|
| `OnEnter` | `event Action<Collider>` or `Action<Collider2D>` | A collider started touching |
| `OnExit` | same | A collider stopped touching |
| `Touching` | `IReadOnlyCollection<Collider>` or `<Collider2D>` | Colliders touching as of the last published tick |
| `AdditionalSize` | `float` | `NetworkCollision` and `NetworkTrigger` only. Get and set; negative values become 0. |
| `IsAttached` | `bool` | A physics component has taken the component over and reports contacts from its own world |
| `Attach(tracker, query)`, `Detach(query)` | `bool`, `void` | Called by a physics component that reports contacts itself; `RigidbodyPhysics` does not use them |

## Observers

### ObserverRule

`public abstract class ObserverRule : ScriptableObject`, explained in the [observers](../objects/observers.md) guide.

| Member | Description |
|---|---|
| `public abstract bool Observes(NetworkObject networkObject, ulong peerId)` | Whether the peer observes the object. Runs on the server. Must not spawn, despawn, change owners or rebuild observers. |

### DistanceRule

`public sealed class DistanceRule : ObserverRule`, which you create with Assets > Create > Fomoxa > Distance Rule.

| Member | Type | Description |
|---|---|---|
| `Radius` | `float` | Get and set. Observation distance from any object the peer owns; negative values become 0. |

### ObserverRange

`public sealed class ObserverRange : MonoBehaviour`, marked `[DisallowMultipleComponent]`. Put it on a `NetworkObject` to replace the `DistanceRule` radius for that object.

| Member | Type | Description |
|---|---|---|
| `Radius` | `float` | Get and set; negative values become 0 |

## Transports

| Component | Description |
|---|---|
| `NetworkTransport` | `public abstract class NetworkTransport : MonoBehaviour` with `public abstract ITransportFactory CreateFactory()` |
| `UdpNetworkTransport` | UDP; no fields |
| `TcpNetworkTransport` | TCP; no fields |
| `WebSocketNetworkTransport` | WebSocket; native code on desktop, the browser in WebGL |
| `MultiNetworkTransport` | Several transports, each with a port, on one server |

The [transports overview](../connections/transports/README.md) explains each transport.

## Generated assets

| Type | Description |
|---|---|
| `NetworkPrefabList` | `ScriptableObject` with `IReadOnlyList<NetworkObject> Prefabs`; written as `FomoxaPrefabList.asset` |
| `NetworkSceneList` | `ScriptableObject` with `Count`, `SceneIdAt(int)`, `PathAt(int)`; written as `FomoxaSceneList.asset` |

`NetworkObject` and `NetworkBehaviour` have their own [reference page](network-object.md), and [configuration](configuration.md) lists the Inspector fields of every component.
