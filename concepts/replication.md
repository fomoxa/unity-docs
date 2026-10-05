# Replication

Replication is how the server's objects and their data reach the clients. Everything is sent from the server, and each client receives only the objects it observes.

## What a client receives about an object

| Event on the server | Message to observers | Channel |
|---|---|---|
| `ServerManager.Spawn` | A spawn message: object id, prefab id or scene object id, prefab fingerprint, owner, position, rotation and scale, the initial state of every behaviour, and the network scene | Reliable ordered |
| A state model changes | The new state, as a full copy or as a delta | Reliable ordered |
| A `NetworkTransform` moves | A transform update with the tick | Unreliable |
| A `NetworkTransform` stops, spawns or teleports | A settle message with the final transform | Reliable ordered |
| `NetworkAnimator` parameters change | The animator state, through the state mechanism | Reliable ordered |
| An RPC to observers | The RPC | The RPC's channel |
| `ServerManager.ChangeOwner` | An owner change | Reliable ordered |
| `ServerManager.Despawn`, or the client stops observing | A despawn | Reliable ordered |

Reliable messages arrive in the order the server sent them, so a client always has the object before any of its state changes and never gets a state change after the despawn. Unreliable messages for an object the client does not have are ignored.

## Spawning on the client

When a spawn arrives, the client goes through three steps.

1. It looks up the prefab by prefab id, or the scene object by scene object id, and compares the fingerprint, which describes the list of `NetworkBehaviour` types. A missing or different prefab stops the client with `PrefabMismatch`.
2. It instantiates the prefab at the spawn's position and rotation and sets its scale, or activates the scene object and places it.
3. It calls the registration callbacks of every `NetworkBehaviour`, applies the initial states and then calls `OnStartClient`.

On a host, the client does not create a second instance and uses the server's instead, as described in [host mode](../core/host-mode.md).

## Clients that join late

A client that connects after objects were spawned gets a spawn message for every object it observes as soon as it reaches `Started`. That message carries the object's current transform and the last state the server captured, so the late client starts from the present values and not from those of the original spawn.

## Observers decide who receives

For each object the server keeps the set of peers that observe it. A peer that enters the set receives a spawn, a peer that leaves it receives a despawn, and state, transforms and RPCs to observers go only to the peers in the set. The owner of an object always observes it, unless the object is in a network scene the owner has not loaded. [Observers](../core/observers.md) explains how the set is built.

## What is not replicated

Only what the package's components and your models send is replicated. Other components, the fields of ordinary MonoBehaviours, child objects created at run time and materials stay local, so put any data that clients need into a [state model](../synchronization/state.md) or send it with an [RPC](../messaging/rpc.md).

A `NetworkObject` may have `NetworkBehaviour` components on its children, including `NetworkTransform`, and each `NetworkTransform` replicates the local position, rotation and scale of the GameObject it sits on.

The guides on [spawning](../core/spawning.md), [state](../synchronization/state.md) and [NetworkTransform](../synchronization/transform.md) cover each kind of message in detail, and [authority](authority.md) explains why everything flows from the server.
