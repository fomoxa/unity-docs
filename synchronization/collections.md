# Collections

A collection is a list, a dictionary or a set held by a `NetworkBehaviour` and kept in sync by the server on every observer. The server sends only the operations you call on it, such as an add or a removal. Each client applies them in the same order and gets a callback for each one.

## When to use it

Use a collection for data that grows and shrinks: an inventory, the players in a room, a scoreboard. A [state model](state.md) with an `Array` field is sent in full when the array changes length, so adding one item to a list of 500 sends all 500. A collection sends the one item.

Values that change together and keep their size, such as health or a position in a match, stay in a state model, which is cheaper for them.

## Basic usage

An element is either a model or a primitive type. A model element is declared like any other model. It needs no channel, because it never travels as a message of its own:

```csharp
using Fomoxa;

namespace MyGame.Network.Models
{
    [Network]
    [Codec("net")]
    public class Item
    {
        [Network("u32")]
        [Codec("net")]
        public uint Id { get; set; }

        [Network("u16")]
        [Codec("net")]
        public ushort Count { get; set; }
    }
}
```

The behaviour keeps its collections and registers each one in `OnRegisterState`, under an index of your choice:

```csharp
using System.Collections.Generic;
using Fomoxa.Networking;
using Fomoxa.Unity;
using Generated;
using MyGame.Network.Models;
using UnityEngine;

public sealed class Inventory : NetworkBehaviour
{
    private readonly NetworkList<Item> items = new NetworkList<Item>();
    private readonly NetworkDictionary<string, int> scores = new NetworkDictionary<string, int>();
    private readonly NetworkSet<ulong> visitors = new NetworkSet<ulong>();

    public IReadOnlyList<Item> Items => items;

    protected override void OnRegisterState(NetworkState state)
    {
        state.Use(0, items, ItemNetAdapter.Instance, OnItemsChanged);
        state.Use(1, scores);
        state.Use(2, visitors);
    }

    public void Pick(uint id)
    {
        items.Add(new Item { Id = id, Count = 1 });
    }

    public void UseOne(int index)
    {
        items.Modify(index, item => item.Count--);
    }

    private void OnItemsChanged(NetworkListOperation operation, int index, Item oldItem, Item newItem)
    {
        Debug.Log($"{name}: {operation} at {index}");
    }
}
```

Call `Pick` and `UseOne` on the server. At the end of that tick each observer receives the operations, applies them to its own `items` and calls `OnItemsChanged` once per operation.

## Registering a collection

`state.Use(index, collection, ...)` registers a collection. The index is a `byte` you choose. Calls can come in any order and indexes can skip numbers; the package handles collections in increasing index order. The same index used twice in one behaviour, or one collection instance registered twice, throws `HandlerRegistrationException`.

The index travels with every operation, so the client must register the same index with the same kind of collection and the same element type. If the spawn message shows a different set of indexes, kinds or element types, the client stops with `ObjectMismatch` (`InvalidSpawn`).

A behaviour can register collections next to its [state model](state.md), or without one.

## Element types

| Element | Registration |
|---|---|
| A model (`[Network]`, `[Codec("net")]`) | Pass its adapter: `state.Use(0, items, ItemNetAdapter.Instance)` |
| `bool`, `sbyte`, `byte`, `short`, `ushort`, `int`, `uint`, `long`, `ulong`, `float`, `double`, `string` | No adapter: `state.Use(1, scores)` |

Dictionary values can be models or primitive types. Dictionary keys and set elements must be primitive types, which compare by value. A model registered without its adapter, or a model used as a key or set element, throws `HandlerRegistrationException` with a message that names the type.

## Operations

The three types follow `List<T>`, `Dictionary<TKey, TValue>` and `HashSet<T>`, and implement `IReadOnlyList<T>`, `IReadOnlyDictionary<TKey, TValue>` and `IReadOnlyCollection<T>`, so `foreach`, LINQ and methods that take those interfaces work on them.

| Type | Operations |
|---|---|
| `NetworkList<T>` | `Add`, `Insert`, `list[index] = value`, `RemoveAt`, `Remove(item)`, `Clear`, `Dirty(index)`, `Modify(index, ...)` |
| `NetworkDictionary<TKey, TValue>` | `Add` (throws `ArgumentException` if the key exists), `dictionary[key] = value`, `Remove(key)`, `Clear`, `Dirty(key)`, `Modify(key, ...)`; reading with `ContainsKey`, `TryGetValue`, `Keys`, `Values` |
| `NetworkSet<T>` | `Add`, `Remove`, `Clear`, `Contains` |

Each call that changes the collection sends one operation, with these exceptions:

- `Remove(item)` on a list removes the first element equal to `item`, compared with `Equals`, which for a model means the same instance. It is sent as a removal at that index.
- `Remove` on a dictionary or a set returns `false` and sends nothing when the key or element is not there. `Add` on a set returns `false` and sends nothing when the element is already there.
- Setting an element to the value it already has still sends the operation. The server does not compare values.

A `null` element, value or key throws `ArgumentNullException` at the call, because a model or a `string` on the wire cannot be null.

## Changing an element in place

Changing a field of a model element does not send anything on its own. Call `Dirty` on the server afterwards, and the element is sent again as a `Set`:

```csharp
items[index].Count = 5;
items.Dirty(index);
```

`Modify` does both steps:

```csharp
items.Modify(index, item => item.Count--);
```

To pass a value without capturing it in the lambda, so that the call does not allocate, use the overload that takes a state argument:

```csharp
items.Modify(index, amount, (item, value) => item.Count -= value);
```

The element is marked even when the action throws, and the exception then propagates. `Modify` exists only for model elements; a primitive element is replaced with an assignment. Both `Dirty` and `Modify` throw like a read when the index is out of range or the key is missing.

The element is encoded when you call the operation. A field changed later in the same tick without another `Dirty` is not sent.

## Callbacks

Each collection takes one optional callback, called on clients after the operation is applied:

| Type | Callback |
|---|---|
| `NetworkList<T>` | `(NetworkListOperation operation, int index, T oldItem, T newItem)` |
| `NetworkDictionary<TKey, TValue>` | `(NetworkDictionaryOperation operation, TKey key, TValue oldValue, TValue newValue)` |
| `NetworkSet<T>` | `(NetworkSetOperation operation, T oldItem, T newItem)` |

| Operation | Index or key | Old value | New value |
|---|---|---|---|
| `Add`, `Insert` | Where the element went | `default` | The element |
| `Set` | The element's index or key | The element before | The element after |
| `RemoveAt`, `Remove` | Where the element was | The removed element | `default` |
| `Clear` | `-1`, or `default` key | `default` | `default` |
| `Reset` | `-1`, or `default` key | `default` | `default` |

A set's callback has no index or key. `Dirty` and `Modify` arrive as `Set`. Assigning to a dictionary key arrives as `Add` when the key is new and as `Set` when it already existed. `Clear` and `Reset` run once, after the collection has been emptied or replaced. `Reset` means the client received the whole collection again after it [fell out of step](#recovery); read the collection itself to rebuild anything that depends on it.

The content that arrives with the spawn message does not trigger callbacks. It is already in place when `OnStartClient` runs.

## How it works

Between two sends the server records each operation in the order you call it. After the tick's `OnTick` and `OnPostTick` events, at the same point where [state](state.md) is sent, the server sends one message per collection that has operations, to every observer. Within one behaviour the state model goes first, then the collections in increasing index order, so a collection callback already sees the new state.

`Clear` drops the operations recorded since the last send, because clients only need the empty collection. Operations made while the object has no observers are dropped as well; an observer that arrives later gets the whole collection in its spawn message.

The server numbers every operation. A client that starts observing between two sends receives the current content in its spawn message, including operations that the server has not sent yet. When those operations arrive, the client sees from their numbers that it already has them and skips them.

## Server behavior

Change collections on the server only. The server gets no callbacks for its own changes.

A collection can be filled before `Spawn`, for example in `Awake`. Nothing is sent for those changes, and the content travels in the spawn message. The same holds after the server despawns the object: changes are allowed and not sent, and the next `Spawn` carries the content.

## Client behavior

On a client, every call that changes a spawned collection throws `InvalidOperationException`, including `Dirty` and `Modify`. A local change would shift the indexes that later operations from the server refer to. Read the collection freely; the package applies the server's operations itself.

A client-side instance changed before its spawn message is applied loses that change, because the content in the spawn message replaces it.

## Host mode

On a host the collection is shared with the server, so the host's client does not apply operations to it. To report the previous value in callbacks, the host's client keeps its own copy of each collection and applies the operations to that copy.

## Recovery

A client that cannot apply an operation, for example an index past the end, a missing key or bytes it cannot decode, marks that collection out of step. It ignores further operations for it, asks the server for its full content, and replaces the collection when the content arrives. The callback then runs once with `Reset`. Other collections and the state model are not affected. When the message itself cannot be read, the client cannot tell which collection it was for, so every collection of that behaviour recovers this way.

## Configuration

| Rule | When broken |
|---|---|
| Each index is used once per behaviour | `HandlerRegistrationException`: `... uses collection index 1 twice` |
| Each collection instance is registered once | `HandlerRegistrationException`: `... uses as collection 2 an instance that is already collection 1 of a behaviour` |
| A model element comes with its adapter; keys and set elements are primitive types | `HandlerRegistrationException`: `... which is not a primitive type; a model needs its codec, and keys and set elements must be primitive` |
| Only the server changes a spawned collection | `InvalidOperationException`: `... cannot change collection 0 on a client; only the server changes a collection` |
| No `null` elements, values or keys | `ArgumentNullException` |
| Both sides register the same indexes, kinds and element types | The client stops with `ObjectMismatch` (`InvalidSpawn`) |

## Limitations

Only the server changes a collection. A behaviour has at most 256 collections, one per `byte` index. The whole collection travels in the spawn message, so a very large collection makes every spawn of its object large. The order in which a dictionary or a set is enumerated is not guaranteed to match between the server and a client.

Collections are registered in a [NetworkBehaviour](../objects/network-behaviour.md), and model elements are declared like any other [model](../messaging/models.md).
