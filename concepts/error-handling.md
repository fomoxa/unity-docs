# Errors

The package treats a failure according to where it comes from: data that cannot be read, your own code throwing, or the two sides disagreeing about objects. This page lists what the package does in each case and why, so that you know which errors end a connection and which only drop a message.

## Overview

| Failure | What the package does | Why | What your game does |
|---|---|---|---|
| A received bundle cannot be read | Drops the whole frame and raises `OnReceiveDropped` | The bundle is checked before any of its messages is delivered, so nothing in it has run yet | Nothing; a log warning shows it by default |
| A model in a bundle cannot be decoded | Drops that message only, raises `OnReceiveDropped`, keeps the connection | The data is damaged, but the messages before it have already run, so the rest of the bundle still goes through | Nothing |
| A message is addressed to an object the receiver does not have | Drops the message, keeps the connection | Messages on different channels can arrive after the object was despawned; this is normal | Nothing |
| A message handler on the server throws, such as a server RPC | Raises `OnHandlerException`, then closes that peer's connection with `HandlerException`. The server and other peers keep running | The handler may have left your game state half changed, and a client whose data breaks a server handler should not keep sending it | Validate client data; set `Disconnect` to `false` when you know the exception is harmless |
| A message handler on the client throws | Raises `OnHandlerException`, stops the client with `HandlerException`, no retry | The client state may be wrong, and retrying would hit the same handler again | Fix the handler, or call `StartConnection` yourself |
| The authenticator, a spawn data source or an object factory throws | Raises `OnHandlerException`, then closes the peer's connection; `Disconnect` is ignored | A peer must not be let in after its authentication failed, and a client that misses an object fails later in a place that is hard to trace | Fix the code that threw |
| The server sends a spawn, despawn or owner change the client cannot apply, or a prefab or scene the client does not have | Raises `OnObjectMismatch`, stops the client with `ObjectMismatch` or `PrefabMismatch`, no retry | These messages travel in order on the reliable channel, so this only happens when the two builds differ or the sender has a bug; reconnecting gives the same result | Ship matching builds; report the error |
| A callback that runs inside a tick throws: `OnStopServer`, `OnStopClient`, `OnStartServer` of a scene object, `OnApplyInput`, an `ObserverRule` | Logs the exception and goes on with the other objects | The callback belongs to no single peer, and stopping the tick would break every connection | Fix the callback |

The [errors reference](../reference/errors.md) lists every stop reason, close reason and mismatch kind, and [reconnection](../connections/client.md#reconnection) lists which ones the client retries.

## Exceptions in server handlers

By default a server handler that throws disconnects the peer whose message it was handling. The peer stops with `StopReason.HandlerException`, and the client stops with `ServerClosed` and a `CloseReason` of `HandlerException`, so it does not reconnect into the same error. If nothing subscribes to `OnHandlerException`, the package logs the exception.

A subscriber can keep the peer. `HandlerExceptionArgs.Disconnect` starts as `true`; set it to `false` and the server keeps the connection and delivers the rest of the bundle and every later message as usual:

```csharp
using System;
using Fomoxa.Networking.Sessions;
using Fomoxa.Unity;
using UnityEngine;

public sealed class InvalidRequestException : Exception
{
    public InvalidRequestException(string message) : base(message)
    {
    }
}

public sealed class HandlerErrors : MonoBehaviour
{
    [SerializeField] private NetworkManager manager;

    private void OnEnable() => manager.ServerManager.OnHandlerException += Decide;

    private void OnDisable() => manager.ServerManager.OnHandlerException -= Decide;

    private static void Decide(HandlerExceptionArgs args)
    {
        Debug.LogException(args.Exception);
        if (args.Exception is InvalidRequestException)
        {
            args.Disconnect = false;
        }
    }
}
```

The event is raised as soon as the handler throws, before the next message of the bundle, so the decision applies to the rest of that bundle. Every subscriber sees the same arguments; a later subscriber sees what an earlier one set. Keep the peer only when you know your game state is still correct, for example when the exception comes from your own input checks.

`Disconnect` only matters for message handlers on the server, such as server RPCs and [raw messages](../messaging/messages.md). The server always disconnects the peer when the authenticator, a spawn data source or an object factory throws, and a client always stops when one of its handlers throws.

## Validate client data in server handlers

A server RPC runs with arguments a client chose, and in a server-authoritative game that client may send anything. Check every argument before you use it, and when a request is bad, return from the handler without throwing. The example uses a model that names an item:

```csharp
using Fomoxa;

namespace MyGame.Network.Models
{
    [Network]
    [Codec("net")]
    public class ItemRequest
    {
        [Network("u32")]
        [Codec("net")]
        public uint ItemId { get; set; }
    }
}
```

The server keeps a count for each item the player holds and checks the request against it:

```csharp
using System.Collections.Generic;
using Fomoxa.Networking;
using Fomoxa.Unity;
using MyGame.Network.Models;

public sealed partial class Inventory : NetworkBehaviour
{
    private readonly Dictionary<uint, int> counts = new Dictionary<uint, int>();

    [ServerRpc]
    private void UseItem(ulong peerId, ItemRequest request)
    {
        if (!counts.TryGetValue(request.ItemId, out int count) || count == 0)
        {
            return;
        }

        counts[request.ItemId] = count - 1;
    }
}
```

Indexing the dictionary with `counts[request.ItemId]` before the check would throw `KeyNotFoundException` for an id the client made up, and that exception would disconnect the client.

The package already drops messages for objects that do not exist and messages that do not decode, so a handler only sees well-formed models for live objects, but the values inside them are whatever the client sent.

## Related pages

- [Server](../connections/server.md) and [client](../connections/client.md) connection events
- [RPCs](../messaging/rpc.md#errors-in-handlers)
- [Authentication](../connections/authentication.md)
- [Debugging](../advanced/debugging.md)
