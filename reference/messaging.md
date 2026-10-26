# Messaging API reference

This page lists the messaging types. The guides on [models and codecs](../messaging/models.md), [raw messages](../messaging/messages.md) and [channels](../messaging/channels.md) explain how they are used.

## IMessageCodec<T>

`public interface IMessageCodec<T>` in `Fomoxa.Networking.Messaging` is implemented by every generated adapter.

| Member | Description |
|---|---|
| `uint MessageId { get; }` | The message id of the model and codec |
| `ReadOnlyMemory<byte> Encode(T value)` | Encodes a value. The memory is reused by the next call on the same adapter. |
| `void Decode(ReadOnlyMemory<byte> payload, ref T value)` | Decodes into an instance; leaves properties the codec does not carry unchanged. Throws `MessageDecodeException`. |

Each generated adapter is a `public sealed class <Model><Codec>Adapter : IMessageCodec<Model>` with a `public static readonly <Model><Codec>Adapter Instance`, marked `[MessageAdapter("<codec>")]`.

## FomoxaRegistry

`public sealed class FomoxaRegistry` in `Fomoxa.Networking`.

| Member | Description |
|---|---|
| `static FomoxaRegistry Default` | The registry the generated registration fills when the player starts, and that `NetworkManager` uses by default |
| `Schema Schema` | The generated schema |
| `MessageChannels Channels` | The channel of every reliable message id |
| `RpcMessageIds Rpcs` | Message ids of parameterless RPCs |
| `void SetSchema(Schema schema)` | Sets the schema |
| `void SetCodec<T>(IMessageCodec<T> codec)` | Registers a codec for a type |
| `IMessageCodec<T> Codec<T>()` | The codec registered for a type, or null |

The generated `FomoxaAdapters.RegisterAll(FomoxaRegistry registry)` fills a registry with the schema, the system codecs, the declared channels and the RPC ids.

## RpcMessageIds

`public sealed class RpcMessageIds` in `Fomoxa.Networking`.

| Member | Description |
|---|---|
| `int Count` | Declared RPCs |
| `void Set(string type, string method, uint messageId)` | Declares the message id of a parameterless RPC by full type name and method name |
| `bool TryGet(Type type, string method, out uint messageId)` | Finds the id for a type or its base types |

## MessageChannels

`public sealed class MessageChannels` in `Fomoxa.Networking.Messaging`.

| Member | Description |
|---|---|
| `void Set(uint messageId, Channel channel)` | Sets a message id's channel |
| `Channel Of(uint messageId)` | The channel; `Unreliable` when not set |
| `bool IsReliable(uint messageId)` | Whether the id is reliable |
| `int ReliableCount` | Reliable ids |

## MessageDispatcher

`public sealed class MessageDispatcher` in `Fomoxa.Networking.Messaging`. Each `ServerManager` and each `ClientManager` has one.

| Member | Description |
|---|---|
| `void Register(uint messageId, PayloadHandler handler)` | Registers a handler for a plain message |
| `void RegisterObject(uint messageId, ObjectPayloadHandler handler)` | Registers a handler for an object message |
| `bool IsObjectMessage(uint messageId)` | Whether an object handler is registered |
| `bool Dispatch(ulong peerId, uint messageId, ReadOnlyMemory<byte> data)` | Calls the handler; false when none. Used by the sessions. |
| `int HandlerCount` | Registered handlers |

The handlers are these delegates:

```csharp
public delegate void PayloadHandler(ulong peerId, ReadOnlyMemory<byte> payload);
public delegate void ObjectPayloadHandler(ulong peerId, uint objectId, byte behaviourIndex, ReadOnlyMemory<byte> body);
```

`Register` and `RegisterObject` throw `HandlerRegistrationException` for an id that is not in the schema or already has a handler.

## Exceptions

| Exception | Namespace | Thrown when |
|---|---|---|
| `MessageDecodeException` | `Fomoxa.Networking.Messaging` | An adapter cannot decode a payload |
| `HandlerRegistrationException` | `Fomoxa.Networking.Messaging` | A handler, RPC, state, collection or input registration is invalid |

## System models

The package's own models live in `Fomoxa.Networking.Messaging`. They are generated together with your models and are part of every schema, but game code does not send them.

| Model | Purpose | Channel |
|---|---|---|
| `MessageBundle`, `BundleEntry` | Several messages in one frame | Unreliable |
| `ReliableAck` | Acknowledgement of reliable messages | Unreliable |
| `PeerLeave` | A client leaving | Unreliable |
| `LocalPeer` | The client's peer id, the tick rate and the physics backend | Reliable ordered |
| `PeerTransfer` | The server a client is moved to, its ticket, and its grant for [encrypted UDP](../connections/transports/encrypted-udp.md#server-transfers) | Reliable ordered |
| `TransferTicket` | The content of a ticket from `TransferTickets` | Not sent on its own |
| `ConnectToken`, `ConnectTokenSecret`, `ConnectionGrant` | A token from `ConnectTokens`, its sealed part, and the grant that carries it with the session keys | Not sent on its own |
| `ObjectSpawn`, `ObjectSceneSpawn`, `ObjectDespawn`, `ObjectOwnerChange` | Object lifecycle | Reliable ordered |
| `StateDelta`, `StateResync` | State deltas, and a client's request for a full state | Reliable ordered |
| `CollectionChanges` | The operations called on one collection in one tick | Reliable ordered |
| `CollectionContent`, `CollectionResync` | The full content of one collection, and a client's request for it | Reliable ordered |
| `CollectionContents` | The collections of one behaviour inside a spawn message | Not sent on its own |
| `BoolValue`, `I8Value`, `U8Value`, `I16Value`, `U16Value`, `I32Value`, `U32Value`, `I64Value`, `U64Value`, `F32Value`, `F64Value`, `StringValue` | A primitive collection element | Not sent on its own |
| `TransformUpdate` | Transform while moving | Unreliable |
| `TransformSettle` | Final transform | Reliable ordered |
| `AnimatorState` | `NetworkAnimator` state | Reliable ordered |
| `SceneLoad`, `SceneUnload`, `SceneLoaded` | Network scenes | Reliable ordered |
| `TickPing`, `TickPong` | Clock synchronization | Unreliable |
| `InputFrames` | Input of a predicted object | Unreliable |
| `ReconcileState` | The server's state for reconciliation | Unreliable |

The [attributes](attributes.md), [events and callbacks](callbacks.md) and [errors](errors.md) references cover the related types.
