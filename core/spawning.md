# Spawning

Spawning makes an object exist on the network. The server spawns an instance, every client that observes it creates its own instance from the same prefab, and despawning removes the object everywhere again. Objects placed in a scene are spawned as well, only without instantiating anything.

## Prefab ids and the prefab registry

The server and the clients identify a prefab by its prefab id, a 32-bit number stored in its `NetworkObject`. The Editor computes the id from the prefab's asset GUID whenever the prefab is saved, when you choose Tools > Fomoxa > Assign Prefab Ids, and before every player build, and it reports two prefabs with the same id as an error.

To keep a fixed id, for example when a prefab's GUID is going to change, turn on Explicit Prefab Id and type the id yourself. Prefab id 0 is not allowed.

Alongside the ids, the Editor writes `FomoxaPrefabList.asset`, which lists every prefab with a `NetworkObject` under `Assets`, and `FomoxaPrefabs.cs`, which holds a pair of constants per prefab, such as `PlayerId` and `PlayerFingerprint`.

A `NetworkManager` can only spawn prefabs registered in its `Prefabs` registry. In `Awake` it registers the prefabs of its Prefabs list, and those of Collected Prefabs as long as Collect Prefabs is on. You can also register a prefab at run time, before its first spawn:

```csharp
manager.Prefabs.Register(bulletPrefab);
```

Registering the same prefab twice does nothing, but registering a different prefab under an id that is already taken throws.

## Spawn

Spawning happens on the server:

```csharp
NetworkObject player = Instantiate(playerPrefab, spawnPoint, Quaternion.identity);
manager.ServerManager.Spawn(player, peerId);
```

`Spawn(networkObject, ownerId = 0)` needs a started server and throws `the server is not started` otherwise. The object must be an instance in a scene rather than the prefab asset, must not be spawned already, and must have a registered prefab id. The owner must be 0 or a connected peer in the `Started` state.

The spawn message carries the object's world position and rotation, its local scale and the initial state of each behaviour as they are at the moment of `Spawn`, so place the object and set its state before calling it. A client instantiates the prefab at that position and rotation, sets the scale and calls `OnStartClient`.

## Despawn

```csharp
manager.ServerManager.Despawn(player);
```

`Despawn` calls `OnStopServer`, tells the observers and destroys the instance, or returns false when this server did not spawn the object. Destroying a spawned `GameObject` on the server despawns it as well.

The server also despawns objects on its own: those owned by a client that disconnects, unless Despawn With Owner is off, those in a network scene that the server unloads, and all of them when the server stops.

## Scene objects

A `NetworkObject` placed directly in a scene is a scene object. The Editor gives it a scene object id when the scene is saved and checks the ids before a build. In Play Mode an unsaved scene object gets a temporary id and the package logs a warning, so save the scene to make every build use the same ids.

The server spawns scene objects automatically: those in the loaded scenes when it starts, and those in a [network scene](scenes.md) when that scene finishes loading. On a client, scene objects are deactivated when the connection starts and activated when their spawn arrives. A despawn deactivates a scene object instead of destroying it, and `ServerManager.Spawn` accepts a despawned scene object to spawn it again.

The client must have the same scene open, with scene objects that have the same ids and the same behaviours. Otherwise it stops with `PrefabMismatch` (`UnknownSceneObject` or `IncompatibleSceneObject`).

## Spawning into a network scene

An object spawned in a network scene only reaches the peers that have loaded that scene. To spawn one there, move the instance into the scene before calling `Spawn`:

```csharp
if (manager.ServerManager.Scenes.TryGetScene(FomoxaScenes.ArenaId, out Scene arena))
{
    NetworkObject enemy = Instantiate(enemyPrefab, position, Quaternion.identity);
    SceneManager.MoveGameObjectToScene(enemy.gameObject, arena);
    manager.ServerManager.Spawn(enemy);
}
```

Each client then puts its instance into its own copy of the scene.

## Factories and pooling

A prefab id can also be registered with a factory instead of a prefab. The factory creates and releases the instances on clients, which makes pooling possible:

```csharp
using System.Collections.Generic;
using Fomoxa.Unity;
using Generated;
using UnityEngine;

public sealed class BulletPool : MonoBehaviour
{
    [SerializeField] private NetworkManager manager;
    [SerializeField] private NetworkObject bulletPrefab;

    private readonly Stack<NetworkObject> idle = new Stack<NetworkObject>();

    private void Start()
    {
        manager.Prefabs.Register(FomoxaPrefabs.BulletId, FomoxaPrefabs.BulletFingerprint, Take, Return);
    }

    private NetworkObject Take(Vector3 position, Quaternion rotation)
    {
        NetworkObject bullet = idle.Count > 0 ? idle.Pop() : Instantiate(bulletPrefab);
        bullet.transform.SetPositionAndRotation(position, rotation);
        bullet.gameObject.SetActive(true);
        return bullet;
    }

    private void Return(NetworkObject bullet)
    {
        bullet.gameObject.SetActive(false);
        idle.Push(bullet);
    }
}
```

The client calls `Take` when a spawn of that prefab id arrives and `Return` when the object despawns. The fingerprint constant comes from `FomoxaPrefabs.cs` and must match the prefab the server spawns, and `Take` must return an instance that is not spawned.

The factory only applies on clients. On the server, `Spawn` still takes an instance you created, and `Despawn` destroys it.

Each prefab id can be registered only once, so a factory for a prefab that is also in Collected Prefabs throws `prefab id 0x... is already registered`. In that case, turn Collect Prefabs off and list the other prefabs in the Prefabs field, or register the factory on a manager whose lists do not contain that prefab.

## Limitations

Nested `NetworkObject` components are not supported, and each `NetworkManager` has its own prefab registry. A client cannot spawn objects; it asks the server to do so with an RPC.

For the object being spawned, see [NetworkObject](network-object.md), [ownership](ownership.md) and [observers](observers.md). The [ServerManager reference](../reference/server-manager.md) lists the spawning members, and [editor integration](../unity/editor-integration.md) describes how the Editor assigns ids.
