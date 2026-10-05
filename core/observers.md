# Observers

An observer of an object is a client that receives it. For each spawned object the server keeps the set of peers that observe it. A peer that enters the set receives the object's spawn, a peer that leaves it receives a despawn, and state, transform updates and RPCs to observers go only to the peers in the set.

Limiting observers saves bandwidth and keeps information away from clients that should not have it, such as enemies behind a wall or the units of other teams.

## Who observes an object

For each started peer and each object, the server decides in three steps.

1. An object in a network scene is only observed by peers that have loaded that scene.
2. The owner observes its own objects.
3. For everyone else, the object's Visibility field decides. With `Everyone`, every peer observes the object, and with `OwnerOnly`, only the owner does. With `Rule`, the default, the `ObserverRule` of the `NetworkManager` decides, and if there is no rule, every peer observes the object.

## ObserverRule

An observer rule is a `ScriptableObject` that answers whether a given peer observes a given object:

```csharp
using Fomoxa.Unity;
using UnityEngine;

[CreateAssetMenu(menuName = "Game/Team Rule")]
public sealed class TeamRule : ObserverRule
{
    public override bool Observes(NetworkObject networkObject, ulong peerId)
    {
        Team team = networkObject.GetComponent<Team>();
        return team == null || team.IsVisibleTo(peerId);
    }
}
```

`Team` here stands for a component of your own. Create an asset of the rule and assign it to the Observer Rule field of the `NetworkManager`.

`Observes` runs on the server only. It must not spawn, despawn, change owners or rebuild observers, and those calls throw while the server is deciding. If `Observes` throws, the exception is logged and the answer counts as "does not observe".

## DistanceRule

`DistanceRule` is the rule that comes with the package, and you create one with Assets > Create > Fomoxa > Distance Rule. A peer observes an object when the object is within Radius (50 units by default) of any object the peer owns, measured between the world positions of the transforms. An `ObserverRange` component on an object replaces Radius for that object, for example to give a tall building a larger radius.

A peer that owns no object observes nothing through this rule, so spawn the peer's player before you expect it to see the world. As soon as a peer gets its first owned object, the server rebuilds that peer's observers.

## When observers are recalculated

Because positions keep changing, the server recalculates observers continuously. Each tick it handles a share of the objects, so that every object is recalculated once every Observer Interval ticks (15 by default), which at 30 ticks per second means twice per second.

When something the rule depends on changes, you can recalculate immediately instead of waiting:

| Method | Recalculates |
|---|---|
| `ServerManager.RebuildObservers(networkObject)` | One object for every peer. Returns false when the object is not spawned by this server. |
| `ServerManager.RebuildObserversOfPeer(peerId)` | Every object for one peer |
| `ServerManager.RebuildObservers()` | Every object for every peer |

`ServerManager.IsObserver(networkObject, peerId)` tells whether a peer currently observes an object.

## Host mode

The host's client is a peer like any other and only observes what the rule allows. Objects it does not observe still exist in the host's process because the server needs them, but the package hides their renderers, as described in [host mode](host-mode.md).

The Visibility field is set on the [NetworkObject](network-object.md), [network scenes](scenes.md) explains the scene step of the decision, and the [ServerManager reference](../reference/server-manager.md) lists the observer members.
