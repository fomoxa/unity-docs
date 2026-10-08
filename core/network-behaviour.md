# NetworkBehaviour

`NetworkBehaviour` is the base class for networked scripts. It is a `MonoBehaviour` that belongs to the `NetworkObject` on its own GameObject or on one of its parents, and it gives your script lifecycle callbacks for the server and the client along with the places to register RPCs, state and input.

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
        SendObserversRpc(nameof(PlayKnock));
    }

    [ClientRpc]
    private void PlayKnock()
    {
        GetComponent<AudioSource>().Play();
    }

    public void RequestKnock() => SendServerRpc(nameof(Knock));
}
```

A class that declares RPCs with attributes must be `partial`, and so must every class that contains it, because the package generates the code that registers those RPCs.

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
| `OnHostVisibility(bool visible)` | On a host, when its client stops or starts observing the object; see [host mode](host-mode.md) |
| `OnReconciled(uint tick)` | On the owner's client, after a correction from the server's state at `tick`; see [reconciliation](../prediction/reconciliation.md) |

[Lifecycle](../concepts/lifecycle.md) shows the order in which they run.

## Registration hooks

The package calls these hooks once per component instance, the first time its object spawns on the server or on a client, before `OnStartServer` or `OnStartClient`:

| Hook | Register here | Guide |
|---|---|---|
| `OnRegisterRpcs(NetworkRpcs rpc)` | RPC handlers written by hand | [RPCs](../messaging/rpc.md#registering-by-hand) |
| `OnRegisterState(NetworkState state)` | The behaviour's state model | [State](../synchronization/state.md) |
| `OnRegisterInput(NetworkInput input)` | The behaviour's input model and reconcile model | [Input](../prediction/input.md) |

## Sending RPCs

| Method | Side | Sends to | Returns |
|---|---|---|---|
| `SendServerRpc<T>(codec, value)` | Client | The server | `SendResult` |
| `SendServerRpc(rpcName)` | Client | The server | `SendResult` |
| `SendObserversRpc<T>(codec, value)` | Server | Every observer of the object | Number of peers it was queued for |
| `SendObserversRpc(rpcName)` | Server | Every observer of the object | Number of peers |
| `SendTargetRpc<T>(peerId, codec, value)` | Server | One observer | `SendResult`, `NotObserver` when the peer does not observe |
| `SendTargetRpc(peerId, rpcName)` | Server | One observer | `SendResult` |

These methods are `protected`. When the object is not spawned on the sending side, they throw `InvalidOperationException` with `<name> is not spawned on the server` or `on the client`.

## Properties

| Property | Meaning |
|---|---|
| `NetworkObject` | The object this behaviour belongs to. Null until the object spawns for the first time. |
| `BehaviourIndex` | The behaviour's position in `NetworkObject.Behaviours` |
| `IsPredicting` | True on the owner's client while it predicts this behaviour |
| `IsReplaying` | True on a client while it replays input during reconciliation |
| `ReconcileCount` | Corrections of this behaviour since it was created |

## Limitations

A behaviour can register one state model and one input model; an object that needs more uses several behaviours. On each side a message id belongs to one behaviour type, so using the same model as a server RPC of two behaviour types, or as both an RPC and a state model, throws `HandlerRegistrationException` when the second object spawns. Because the registration hooks run once per component instance, a scene object that is despawned and spawned again keeps its first registration.

The behaviour belongs to a [NetworkObject](network-object.md). The guides on [RPCs](../messaging/rpc.md), [state](../synchronization/state.md) and [input](../prediction/input.md) explain what to register in each hook, and the [NetworkBehaviour reference](../reference/network-object.md#networkbehaviour) lists every member.
