# Console backend reference

The console backend types are in the namespace `Fomoxa.Networking.Standalone` and ship as source in `Standalone~`. The backend contract types are in layer 1, in the namespaces given below. The [runtime](runtime.md) and [physics](physics.md) pages explain how they are used.

## StandaloneRuntime

`public static class StandaloneRuntime` has one member, `Create`, whose parameters are listed in [runtime](runtime.md#standaloneruntimecreate). It throws `ArgumentNullException` for a missing `prefabs`, `behaviours`, `scenes` or `log`, and `ArgumentException` for a boot scene without a scene file.

## StandaloneEntity

`public class StandaloneEntity : INetworkEntity`, with the constructor `StandaloneEntity(uint prefabId, IReadOnlyList<EntityBehaviour> behaviours)`.

| Member | Type | Description |
|---|---|---|
| `PrefabId` | `uint` | The prefab id given to the constructor; 0 for scene objects |
| `SceneObjectId` | `ulong` | The scene object id of a scene object; 0 otherwise |
| `SceneId` | `uint` | Get and set. The scene the entity belongs to; 0 for none |
| `DespawnWithOwner` | `bool` | Get and set; true by default |
| `Visibility` | `NetworkVisibility` | Get and set; `Rule` by default |
| `EntityBehaviours` | `IReadOnlyList<EntityBehaviour>` | The behaviours, in behaviour index order |
| `Record` | `EntityRecord` | The entity's record while spawned; null otherwise |
| `Body`, `Body2D` | `PhysicsBody`, `PhysicsBody2D` | The physics body while spawned with a physics backend |
| `Position`, `Rotation`, `Scale` | `Vector3`, `Quaternion`, `Vector3` | Virtual. Get and set; position and rotation read and write the body when there is one |
| `TryGetBody(out BodyDesc)`, `TryGetBody2D(out BodyDesc2D)` | `bool` | Virtual. The body to create at spawn; by default the body from the scene file |

## StandalonePrefabs

| Member | Description |
|---|---|
| `void Register(uint prefabId, uint fingerprint, Func<StandaloneEntity> create)` | Registers a factory. Registering the same id, fingerprint and factory twice does nothing; another fingerprint or factory for the same id throws. Prefab id 0 throws. |

On a console client, the factory must return an entity that is not spawned.

## StandaloneBehaviours

| Member | Description |
|---|---|
| `void Register(string typeName, Func<EntityBehaviour> create)` | Registers the factory for the behaviours of scene objects whose Unity type has this full name |

## Scene files

| Type | Description |
|---|---|
| `public interface ISceneFiles` | `bool Knows(uint sceneId)`, `byte[] Read(uint sceneId)` |
| `public sealed class SceneFileDirectory : ISceneFiles` | Reads `<scene id>.fomoxascene` from the folder given to its constructor |
| `SceneFileFormat` (`Fomoxa.Networking.Objects`) | `Read(FomoxaRegistry, ReadOnlyMemory<byte>)` and `Write(FomoxaRegistry, SceneFile)`; `Extension` is `.fomoxascene` |
| `SceneFileGeometry` (`Fomoxa.Networking.Objects`) | Converts between the scene file models and `ColliderDesc`, `BodyDesc` and their 2D forms |

## Layer 1 types the console uses

| Type | Namespace | Description |
|---|---|---|
| `NetworkRuntime` | `Fomoxa.Networking` | `ServerManager`, `ClientManager`, `TimeManager`, `Physics`, `BeginFrame(TimeSpan now, double elapsedSeconds)`, `EndFrame()`. `Version` is the package version. |
| `NetworkSettings` | `Fomoxa.Networking` | The settings that the `NetworkManager` Inspector holds in Unity, as properties with the same defaults, and `PhysicsBackend` |
| `NetworkLog` | `Fomoxa.Networking` | `NetworkLog(Action<Exception> exception, Action<string> warning)`, an overload that adds `Action<string> error`, and `NetworkLog.Console` |
| `EntityBehaviour` | `Fomoxa.Networking` | The base class of console behaviours, with the callbacks and registrations of `NetworkBehaviour`, `SetStateDirty()`, `SyncTransform(TransformSync, ITransformReceiver)` for the pose of the entity and `SyncTransform(TransformSync, ITransformSource, ITransformReceiver)` for another source |
| `TransformSync`, `TransformSyncSettings` | `Fomoxa.Networking` | The send rules of `NetworkTransform`: `TransformSyncSettings(syncPosition, syncRotation, syncScale, positionThreshold, rotationThreshold, scaleThreshold)`, `TransformSync.Teleport()` |
| `ITransformSource`, `ITransformReceiver`, `TransformSample` | `Fomoxa.Networking` | `ReadLocal(out position, out rotation, out scale)` on the server; `ResetReceive()` and `Receive(in TransformSample)` on a client |
| `INetworkEntity`, `EntityRecord` | `Fomoxa.Networking` | The interface the managers spawn, and the record of a spawned entity: `ObjectId`, `OwnerId`, `IsOwner`, `OnServer`, `OnClient`, `Representation` |

## Backend contract

`StandaloneRuntime.Create` builds a `NetworkBackends` from these interfaces. A backend for another engine implements them and passes a `NetworkBackends` to the `NetworkRuntime` constructor itself.

| Interface | Namespace | Role |
|---|---|---|
| `IServerEntityBackend` | `Fomoxa.Networking.Objects` | Validates spawns, gives fingerprints and scene ids, prepares, activates and ends entities on the server |
| `IServerSceneHost` | `Fomoxa.Networking.Objects` | Loads and unloads scenes on the server, presents boot scene objects, lists the scene objects of a scene |
| `IClientEntityBackend` | `Fomoxa.Networking.Objects` | Creates entities for spawns, places scene objects, ends entities and hides or shows them on a host |
| `ISceneHost` | `Fomoxa.Networking.Objects` | Loads and unloads scenes on a client |
| `IClientPredictionBackend` | `Fomoxa.Networking.Prediction` | The worlds and histories of predicted entities, proxies, and the start and end of a correction |
| `IPhysicsWorlds`, `IPhysicsScenes`, `IPhysicsMotion` | `Fomoxa.Networking.Simulation` | Physics for the tick loop, physics by scene id for the console backend, and the optional report of moved entities that lets the server skip resting transforms |

`NetworkRuntime(FomoxaRegistry registry, NetworkSettings settings, ITransportFactory transport, NetworkBackends backends, Func<TimeSpan> clock, NetworkLog log)` is the constructor.
