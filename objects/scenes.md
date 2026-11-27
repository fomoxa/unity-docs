# Network scenes

A network scene is a scene that the server loads additively, both on itself and on selected clients. Each load creates an instance of the scene asset, and the server can hold several instances of one asset at the same time, such as one copy of a dungeon for each group of players. An instance is either global, meaning every client loads it, or loaded only for chosen peers. Objects in an instance, including objects spawned into it, only reach peers that have loaded that instance.

The scene a game starts with is not a network scene. Both sides open it the usual way, and its scene objects are visible to every peer that passes the observer rules.

## Scene ids

A scene id names a scene asset: it is a 32-bit hash of the asset's GUID. The Editor writes the ids into two files. `FomoxaSceneList.asset` holds the id and path of every scene in the Build Profiles scene list and is refreshed whenever that list or a scene asset changes. `FomoxaScenes.cs` holds a constant `<SceneName>Id` for every scene asset under `Assets`, including scenes outside the build list.

Assign `FomoxaSceneList.asset` to Collected Scenes on the `NetworkManager`. The manager then registers each listed scene with a loader that loads it additively with `SceneManager.LoadSceneAsync` and unloads it with `UnloadSceneAsync`, and `NetworkManager.Scenes.IdOf("Assets/Scenes/Arena.unity")` returns the id of a listed scene, or 0 for one that is not listed.

## Instances

A `NetworkScene` names one loaded instance. The server hands out instance ids counting up from 1 and never reuses one while it runs, so an instance that was unloaded is not confused with a later instance of the same asset. `default(NetworkScene)` means no network scene. The load calls take scene ids and return `NetworkScene` values, and every other scene call takes a `NetworkScene`.

## Load a scene for everyone

```csharp
NetworkScene arena = manager.ServerManager.Scenes.LoadGlobal(new[] { FomoxaScenes.ArenaId })[0];
```

The server starts loading the scene and, in the same call, tells every started peer to load it, so the server and the clients load in parallel. A peer that connects later loads every global scene when it starts. A scene asset has at most one global instance: calling `LoadGlobal` for an asset that already has one returns that instance and sends nothing. `LoadGlobal(sceneIds, replace: true)` unloads the current global instances before loading the new ones.

`UnloadGlobal(scenes)` unloads global instances and throws for one that is not global.

## Load a scene for some peers

```csharp
NetworkScene dungeon = manager.ServerManager.Scenes.Load(FomoxaScenes.DungeonId, new[] { peerA, peerB });
```

`Load` always creates a new instance, even when the asset already has one, so two groups that each call it get two separate dungeons. The list of peers can be empty. Peers that are not started are skipped. Keep the returned `NetworkScene` with your room or match, because the later calls need it.

`AddPeers(dungeon, peerIds)` and `RemovePeers(dungeon, peerIds)` change who has the instance and return how many peers they added or removed. A peer that is removed gets the despawns of the instance's objects, then the unload. The instance stays loaded on the server even when no peer has it any more, and when its last peer disconnects. `Unload(dungeon)` despawns its objects, unloads it on its peers and then unloads it on the server.

A global instance and a per-peer instance are always two different instances. `AddPeers`, `RemovePeers` and `Unload` throw for a global instance, and `UnloadGlobal` throws for a per-peer one.

## Physics of an instance

Every load call takes an optional `ScenePhysics`. With the default, `Shared`, the instance's colliders and rigidbodies join the default physics world. Two `Shared` instances of one map would then overlap and collide with each other, so a scene asset can have only one `Shared` instance at a time and loading a second one throws `ArgumentException`. Loading a `Shared` instance of an asset whose previous instance is still unloading waits until that unload has finished.

`ScenePhysics.Own` loads the instance with `LocalPhysicsMode.Physics3D | LocalPhysicsMode.Physics2D`, which gives it its own 3D and 2D physics worlds. Use it for every room when one server process runs several rooms of the same map:

```csharp
NetworkScene red = manager.ServerManager.Scenes.Load(FomoxaScenes.ArenaId, redPeers, ScenePhysics.Own);
NetworkScene blue = manager.ServerManager.Scenes.Load(FomoxaScenes.ArenaId, bluePeers, ScenePhysics.Own);
```

Clients load each instance with the mode the server chose. A raycast or overlap query only sees the colliders of one world, so query through the instance's world, for example `unityScene.GetPhysicsScene().Raycast(...)`, and not through the static `Physics.Raycast`, which only sees the default world.

Unity never steps the worlds of scenes loaded with `LocalPhysicsMode` by itself. Each `NetworkManager` steps the Unity worlds of the `Own` instances it loaded, unless the backend is `RigidbodyPhysics` with Simulate Physics on. With `RapierPhysics` the manager steps them too, because they still hold the Unity physics outside network objects. The steps follow Unity's simulation mode: after Unity's own step in every fixed update with `Time.fixedDeltaTime` when `Physics.simulationMode` (or `Physics2D.simulationMode`) is `FixedUpdate`, once a frame with `Time.deltaTime` when it is `Update`, and not at all when it is `Script`, because a game in that mode steps physics itself. When Simulate Physics is on, the package steps every world once a tick, `Own` instances included.

With the [Rapier backend](../rapier/setup.md#export-the-scene-files), network objects are simulated in Rapier worlds, and every instance gets its own, whichever mode it was loaded with. The mode then only decides which Unity world takes the instance's Unity physics.

Observer rules and [groups](observers.md#groups) decide which peers see an object. They do not separate physics: objects of two rooms that share a world still collide.

## Objects in network scenes

```mermaid
sequenceDiagram
    participant Code as Your code
    participant Server
    participant Client as Client of peer A
    Code->>Server: Load(DungeonId, peerA)
    Server->>Client: scene load
    Note over Server: loads Dungeon additively,<br/>then spawns its scene objects
    Note over Client: loads Dungeon additively
    Client->>Server: scene loaded
    Note over Server: peer A now passes the scene check,<br/>its observers are rebuilt
    Server->>Client: spawns of the objects in that instance it observes
```

When the server finishes loading an instance, it spawns the scene objects in it, and when it unloads the instance, it despawns every object in it. Each instance has its own copies of the scene objects, so the same scene object id can be spawned once in every instance.

An object the server spawns into an instance, by moving it into that instance's `Scene` before `Spawn`, only reaches peers that have loaded the instance, as shown in [spawning](spawning.md#spawning-into-a-network-scene). A peer starts observing such an object only after its client reports that it has finished loading the instance.

## Server events and queries

| Member | Meaning |
|---|---|
| `OnLoaded(NetworkScene scene)` | The server finished loading an instance |
| `OnLoadFailed(NetworkScene scene, Exception exception)` | The server could not load it; the exception is also logged |
| `OnUnloaded(NetworkScene scene)` | The server finished unloading an instance |
| `OnPeerLoaded(ulong peerId, NetworkScene scene)` | A peer's client reported an instance as loaded |
| `Global` | The global instances |
| `Contains(scene)` | The instance exists |
| `IsGlobal(scene)` | The instance is global |
| `HasLoaded(peerId, scene)` | The peer's client reported the instance as loaded |
| `PeersOf(scene)` | Peers that have the instance |
| `ScenesOf(peerId)` | Instances the peer has |
| `InstancesOf(sceneId)` | Instances of a scene asset |
| `SceneIdOf(scene)` | The scene id of an instance, or 0 |
| `TryGetScene(scene, out Scene unityScene)` | The Unity `Scene` the server loaded for the instance |
| `TryGetNetworkScene(unityScene, out NetworkScene scene)` | The instance a Unity `Scene` of the server belongs to |

All of these members are on `ServerManager.Scenes`.

## On the client

The client loads and unloads instances one at a time, in the order the server asked for them, and reports each finished load to the server. If a load fails, the client logs the exception and stops with `PrefabMismatch`, raising `OnObjectMismatch` with the kind `UnknownScene`. When the connection stops, the client keeps the instances it has loaded. After a reconnect it keeps an instance only when the server lists it again with the same instance id, scene id and physics mode, and replaces it otherwise.

`ClientManager.Scenes` has the client side of the queries and events:

| Member | Meaning |
|---|---|
| `OnLoadStarted(NetworkScene scene, uint sceneId)` | The client started loading an instance |
| `OnLoadProgress(NetworkScene scene, float progress)` | The loader reported progress, from 0 to 1, for the instance being loaded |
| `OnLoaded(NetworkScene scene)` | The client finished loading an instance |
| `OnUnloaded(NetworkScene scene)` | The client finished unloading an instance |
| `SceneIdOf(scene)` | The scene id of an instance the client has or is loading, or 0 |
| `TryGetScene(scene, out Scene unityScene)` | The Unity `Scene` the client loaded for the instance |
| `TryGetNetworkScene(unityScene, out NetworkScene scene)` | The instance a Unity `Scene` of the client belongs to |

A host's client uses the instances the server loaded instead of loading them again, so it raises no progress, and its `TryGetScene` and `TryGetNetworkScene` answer with the server's scenes.

## Custom loaders

A scene that is not in the build list, such as an Addressables scene, needs a loader of your own, registered on the server and on every client:

```csharp
using System;
using System.Collections.Generic;
using Fomoxa.Unity;
using UnityEngine.AddressableAssets;
using UnityEngine.ResourceManagement.AsyncOperations;
using UnityEngine.ResourceManagement.ResourceProviders;
using UnityEngine.SceneManagement;

public sealed class AddressableSceneLoader : ISceneLoader
{
    private readonly string address;
    private readonly Dictionary<Scene, AsyncOperationHandle<SceneInstance>> handles = new Dictionary<Scene, AsyncOperationHandle<SceneInstance>>();

    public AddressableSceneLoader(string address)
    {
        this.address = address;
    }

    public void Load(SceneLoadRequest request, Action<float> progress, Action<Scene> loaded, Action<Exception> failed)
    {
        var parameters = new LoadSceneParameters(LoadSceneMode.Additive, request.Physics);
        Addressables.LoadSceneAsync(address, parameters).Completed += handle =>
        {
            if (handle.Status != AsyncOperationStatus.Succeeded)
            {
                failed(handle.OperationException ?? new InvalidOperationException($"{address} did not load"));
                return;
            }

            Scene scene = handle.Result.Scene;
            handles[scene] = handle;
            loaded(scene);
        };
    }

    public void Unload(Scene scene, Action unloaded)
    {
        if (!handles.Remove(scene, out AsyncOperationHandle<SceneInstance> handle))
        {
            unloaded();
            return;
        }

        Addressables.UnloadSceneAsync(handle).Completed += _ => unloaded();
    }
}
```

```csharp
manager.Scenes.Register(FomoxaScenes.ArenaId, new AddressableSceneLoader("Arena"));
```

`SceneLoadRequest` carries the instance (`Scene`), the scene id (`SceneId`) and the `LocalPhysicsMode` to load with (`Physics`). A loader must load with `request.Physics` and call `loaded` with the exact `Scene` that this load produced, here `SceneInstance.Scene`. Do not look the scene up with `SceneManager.GetSceneByName` or `GetSceneByPath`: with two instances of one asset loaded, both return the first. The loader calls `failed` with an exception when the load fails, may call `progress` with values from 0 to 1 while it loads, and calls `unloaded` once unloading is done. The example reports no progress; a loader that wants a progress bar polls `handle.PercentComplete` every frame and passes it on.

Register a loader before the server or the client needs the scene, because `LoadGlobal` and `Load` throw `scene 0x... is not in the scene registry` for an unregistered id. Scene id 0 cannot be registered. The built-in loader for the build list loads with `request.Physics` and takes the scene from `SceneManager.sceneLoaded` of its own load; a scene with the same path that other code loads at the same moment can be mistaken for it.

## Limitations

All scene loading is additive, and the package neither switches the active scene nor unloads the starting scene. A peer can have several instances, including two instances of the same asset.

Network scenes take part in the [observer](observers.md) decision and in [spawning](spawning.md), and the [ServerManager reference](../reference/server-manager.md) lists the scene members.
