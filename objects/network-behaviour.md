# NetworkBehaviour

`NetworkBehaviour` is the base class for networked scripts. It is a `MonoBehaviour` that belongs to the `NetworkObject` on its own GameObject or on one of its parents, and it gives your script lifecycle callbacks for the server and the client. RPCs, state and input are declared on it with attributes.

## Basic usage

```csharp
using Fomoxa.Networking;
using Fomoxa.Unity;
using UnityEngine;

public sealed partial class Door : NetworkBehaviour
{
    public override void OnStartServer()
    {
        Debug.Log($"door {NetworkObject.ObjectId} spawned on the server");
    }

    public override void OnStartClient()
    {
        Debug.Log($"door {NetworkObject.ObjectId} appeared on this client");
    }

    [ServerRpc(RequireOwnership = false)]
    private void Knock(ulong peerId)
    {
        Debug.Log($"peer {peerId} knocked");
        SendPlayKnockObserversRpc();
    }

    [ClientRpc]
    private void PlayKnock()
    {
        GetComponent<AudioSource>().Play();
    }

    public void RequestKnock() => SendKnockServerRpc();
}
```

A class that declares RPCs, state or input must be `partial`, and so must every class that contains it, because the package generates the code that registers them and the RPCs' send methods.

## Lifecycle callbacks

Override these callbacks to react to the object's network lifecycle:

| Callback | Runs |
|---|---|
| `OnStartServer()` | On the server, after the object spawned |
| `OnStopServer()` | On the server, before the object despawns |
| `OnStartClient()` | On a client, after the object appeared and its initial state was applied |
| `OnStopClient()` | On a client, before the object disappears |
| `OnOwnerChangedServer(ulong previousOwnerId)` | On the server, after the owner changed |
| `OnOwnerChangedClient(ulong previousOwnerId)` | On every observing client, after the owner changed |
| `OnSceneChangedServer(NetworkScene previous, NetworkScene current)` | On the server, after the object [moved](scenes.md#move-an-object-to-another-instance) to another instance |
| `OnSceneChangedClient(NetworkScene previous, NetworkScene current)` | On every client that observes the object in both instances, after the move arrived |
| `OnHostVisibility(bool visible)` | On a host, when its client stops or starts observing the object; see [host mode](../connections/host-mode.md) |
| `OnReconciled(uint tick)` | On the owner's client, after a correction from the server's state at `tick`; see [reconciliation](../prediction/reconciliation.md) |

[Lifecycle](../concepts/lifecycle.md) shows the order in which they run.

## Declarations

| Declare | With | Guide |
|---|---|---|
| RPCs | `[ServerRpc]` and `[ClientRpc]` on methods | [RPCs](../messaging/rpc.md) |
| State | `[NetworkState]` on fields | [State](../synchronization/state.md) |
| Collections | `[NetworkState(Index = n)]` on `readonly` collection fields | [Collections](../synchronization/collections.md) |
| Input and predicted state | `[NetworkInput]` and `[NetworkReconcile]` on fields | [Input](../prediction/input.md), [reconciliation](../prediction/reconciliation.md) |

The package registers these once per component instance, the first time its object spawns on the server or on a client, before `OnStartServer` or `OnStartClient`.

A behaviour with `[NetworkInput]` fields overrides the methods that fill and read them:

| Method | Runs |
|---|---|
| `OnGatherInput()` | On the owner's client, once per tick; write the input fields here |
| `OnApplyInput(InputContext context)` | On the server and on the predicting client, after the input fields were written; simulate from them here |
| `OnCaptureState()` | Before the `[NetworkReconcile]` fields are copied; optional |
| `OnRestoreState()` | After the `[NetworkReconcile]` fields were restored from the server; optional |

## Sending RPCs

For each RPC the package generates `protected` send methods, named after the RPC:

| Method | Side | Sends to | Returns |
|---|---|---|---|
| `Send<Method>ServerRpc(...)` | Client | The server | `SendResult` |
| `Send<Method>ObserversRpc(...)` | Server | Every observer of the object | Number of peers it was queued for |
| `Send<Method>TargetRpc(peerId, ...)` | Server | One observer | `SendResult`, `NotObserver` when the peer does not observe |

They call `SendServerRpc`, `SendObserversRpc` and `SendTargetRpc`, which take the RPC's name and are `protected` as well; [RPCs](../messaging/rpc.md#sending-by-name) describes them. When the object is not spawned on the sending side, the send methods throw `InvalidOperationException` with `<name> is not spawned on the server` or `on the client`.

## Properties

| Property | Meaning |
|---|---|
| `NetworkObject` | The object this behaviour belongs to. Null until the object spawns for the first time. |
| `BehaviourIndex` | The behaviour's position in `NetworkObject.Behaviours` |
| `IsPredicting` | True on the owner's client while it predicts this behaviour |
| `IsReplaying` | True on a client while it replays input during reconciliation |
| `ReconcileCount` | Corrections of this behaviour since it was created |

## Limitations

A behaviour has one state model, made of all its state fields, up to 256 [collections](../synchronization/collections.md) and one input model; an object that needs more uses several behaviours. Because registration runs once per component instance, a scene object that is despawned and spawned again keeps its first registration.

The behaviour belongs to a [NetworkObject](network-object.md). The guides on [RPCs](../messaging/rpc.md), [state](../synchronization/state.md) and [input](../prediction/input.md) explain each declaration, and the [NetworkBehaviour reference](../reference/network-object.md#networkbehaviour) lists every member.
