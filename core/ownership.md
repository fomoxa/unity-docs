# Ownership

Every spawned object has an owner, which is either the peer id of one client or 0 when the server owns the object. The owner is the client the object belongs to, typically the player whose character it is. Ownership does not move authority to that client, as [authority](../concepts/authority.md) explains.

## What the owner gets

The owner may call the object's server RPCs, while other clients may only call those declared with `RequireOwnership = false`. If the object has an input model, the owner predicts it, and the server accepts input for the object only from the owner.

The owner also always observes the object, whatever the observer rule says, as long as it has loaded the object's network scene. With a [`DistanceRule`](observers.md#distancerule), the objects a peer owns are the points from which it observes everything else.

## Setting the owner

You give the owner when spawning:

```csharp
manager.ServerManager.Spawn(player, peerId);
```

To change it later, call `ChangeOwner` on the server:

```csharp
bool changed = manager.ServerManager.ChangeOwner(car, driverPeerId);
```

`ChangeOwner` returns false when this server did not spawn the object or when the new owner is not a connected peer in the `Started` state. Passing 0 gives the object to the server.

After a change, the server calls `OnOwnerChangedServer(previousOwnerId)` and every observing client calls `OnOwnerChangedClient(previousOwnerId)`. The new owner starts observing the object if it was not already, and a previous owner that no longer passes the observer rule stops observing it.

A change of owner also resets prediction. The server discards the input it buffered for the object, the previous owner stops predicting it, and the new owner starts predicting once the server has sent it the first state.

## Reading the owner

| Member | Where | Meaning |
|---|---|---|
| `NetworkObject.OwnerId` | Server and clients | The owner's peer id, 0 for the server |
| `NetworkObject.IsOwner` | Clients | True on the owner's client, including a host's client |

## When the owner disconnects

By default the server despawns every object owned by a peer that disconnects. To keep the object instead, turn off Despawn With Owner on the `NetworkObject` or set `DespawnWithOwner = false` from code. The object then becomes owned by the server, and `OnOwnerChangedServer` runs with the old owner as `previousOwnerId`.

```csharp
public override void OnOwnerChangedServer(ulong previousOwnerId)
{
    if (NetworkObject.OwnerId == 0)
    {
        Debug.Log($"{name} lost its owner {previousOwnerId} and stays in the world");
    }
}
```

Ownership is a property of the [NetworkObject](network-object.md), and the [RPC](../messaging/rpc.md) and [input](../prediction/input.md) guides describe the ownership checks in more detail.
