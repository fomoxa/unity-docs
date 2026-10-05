# NetworkManager reference

`public sealed class NetworkManager : MonoBehaviour` in `Fomoxa.Unity`, marked `[DisallowMultipleComponent]`. The [NetworkManager](../core/network-manager.md) guide explains how to use it, and its fields are listed in [configuration](configuration.md#networkmanager).

## Purpose

The manager runs networking for a scene. It reads the configuration, registers prefabs and scenes, creates the server, client, time and transport managers, and runs the tick loop inside the player loop.

## Lifetime

| Unity message | Effect |
|---|---|
| `Awake` | Creates the sub-managers. Throws `InvalidOperationException` when no schema or a system codec is registered. |
| `OnEnable` / `OnDisable` | Adds or removes the player loop entries |
| `OnDestroy` | Stops the client and the server, releases the physics simulation |
| `Application.quitting` | Stops the client and the server |

## Properties

| Property | Type | Description |
|---|---|---|
| `Registry` | `FomoxaRegistry` | Schema, codecs, channels and RPC ids. Get and set; defaults to `FomoxaRegistry.Default`. It is read in `Awake`, so another registry only takes effect when set before, for example on a manager added to an inactive GameObject. |
| `ServerManager` | `ServerManager` | The server side. Null before `Awake`. |
| `ClientManager` | `ClientManager` | The client side. Null before `Awake`. |
| `TimeManager` | `TimeManager` | Tick rate, ticks and tick events. Null before `Awake`. |
| `TransportManager` | `TransportManager` | The transport. Null before `Awake`. |
| `Prefabs` | `PrefabRegistry` | Prefabs this manager can spawn |
| `Scenes` | `SceneRegistry` | Network scenes this manager can load |

## Threading

Every member must be called from Unity's main thread, and the package does not create threads of its own.

## TransportManager

`public sealed class TransportManager` in `Fomoxa.Unity`.

| Property | Type | Description |
|---|---|---|
| `Transport` | `NetworkTransport` | The transport component in use |
| `Factory` | `ITransportFactory` | The factory the component created in `Awake` |

## PrefabRegistry

`public sealed class PrefabRegistry` in `Fomoxa.Unity`.

| Member | Description |
|---|---|
| `Count` | Registered prefab ids |
| `Contains(uint prefabId)` | Whether the id is registered |
| `Register(NetworkObject prefab)` | Registers a prefab by its Prefab Id. Throws for id 0, for an id registered to another prefab, and for an invalid hierarchy. Registering the same prefab again does nothing. |
| `Register(uint prefabId, uint fingerprint, Func<Vector3, Quaternion, NetworkObject> create, Action<NetworkObject> release = null)` | Registers a factory for a prefab id. Throws for id 0 and for an id registered to something else. |

## SceneRegistry

`public sealed class SceneRegistry` in `Fomoxa.Unity`.

| Member | Description |
|---|---|
| `Count` | Registered scene ids |
| `Contains(uint sceneId)` | Whether the id is registered |
| `IdOf(string path)` | The id of a scene of Collected Scenes by its build path; 0 when unknown |
| `Register(uint sceneId, ISceneLoader loader)` | Registers a loader. Throws for id 0 and for an id already registered. |

`ISceneLoader` has two methods, `void Load(Action<Scene> loaded, Action<Exception> failed)` and `void Unload(Scene scene, Action unloaded)`.

The sub-managers are documented in the [ServerManager](server-manager.md), [ClientManager](client-manager.md) and [TimeManager](time-manager.md) references, and the registry in the [messaging API](messaging.md).
