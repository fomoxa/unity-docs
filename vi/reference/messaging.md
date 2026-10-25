# Tham chiếu Messaging API

Trang này liệt kê các type về messaging. Các hướng dẫn [model và codec](../messaging/models.md), [raw message](../messaging/messages.md) và [channel](../messaging/channels.md) giải thích cách dùng chúng.

## IMessageCodec<T> <a href="#imessagecodect" id="imessagecodect"></a>

`public interface IMessageCodec<T>` trong `Fomoxa.Networking.Messaging` được mọi adapter sinh ra hiện thực.

| Member | Mô tả |
|---|---|
| `uint MessageId { get; }` | Message id của model và codec |
| `ReadOnlyMemory<byte> Encode(T value)` | Encode một giá trị. Vùng nhớ được dùng lại ở lần gọi tiếp theo trên cùng adapter. |
| `void Decode(ReadOnlyMemory<byte> payload, ref T value)` | Decode vào một instance; giữ nguyên các property mà codec không mang. Ném `MessageDecodeException`. |

Mỗi adapter được sinh là một `public sealed class <Model><Codec>Adapter : IMessageCodec<Model>` với một `public static readonly <Model><Codec>Adapter Instance`, đánh dấu `[MessageAdapter("<codec>")]`.

## FomoxaRegistry <a href="#fomoxaregistry" id="fomoxaregistry"></a>

`public sealed class FomoxaRegistry` trong `Fomoxa.Networking`.

| Member | Mô tả |
|---|---|
| `static FomoxaRegistry Default` | Registry mà phần đăng ký sinh ra điền vào khi player khởi động, và `NetworkManager` dùng theo mặc định |
| `Schema Schema` | Schema được sinh |
| `MessageChannels Channels` | Channel của mọi message id reliable |
| `RpcMessageIds Rpcs` | Message id của các RPC không tham số |
| `void SetSchema(Schema schema)` | Đặt schema |
| `void SetCodec<T>(IMessageCodec<T> codec)` | Đăng ký codec cho một type |
| `IMessageCodec<T> Codec<T>()` | Codec đã đăng ký cho một type, hoặc null |

`FomoxaAdapters.RegisterAll(FomoxaRegistry registry)` được sinh điền vào registry schema, các system codec, các channel đã khai báo và các RPC id.

## RpcMessageIds <a href="#rpcmessageids" id="rpcmessageids"></a>

`public sealed class RpcMessageIds` trong `Fomoxa.Networking`.

| Member | Mô tả |
|---|---|
| `int Count` | Số RPC đã khai báo |
| `void Set(string type, string method, uint messageId)` | Khai báo message id của một RPC không tham số theo tên type đầy đủ và tên method |
| `bool TryGet(Type type, string method, out uint messageId)` | Tìm id cho một type hoặc các base type của nó |

## MessageChannels <a href="#messagechannels" id="messagechannels"></a>

`public sealed class MessageChannels` trong `Fomoxa.Networking.Messaging`.

| Member | Mô tả |
|---|---|
| `void Set(uint messageId, Channel channel)` | Đặt channel của một message id |
| `Channel Of(uint messageId)` | Channel; `Unreliable` khi chưa đặt |
| `bool IsReliable(uint messageId)` | Id có reliable hay không |
| `int ReliableCount` | Số id reliable |

## MessageDispatcher <a href="#messagedispatcher" id="messagedispatcher"></a>

`public sealed class MessageDispatcher` trong `Fomoxa.Networking.Messaging`. Mỗi `ServerManager` và mỗi `ClientManager` có một dispatcher.

| Member | Mô tả |
|---|---|
| `void Register(uint messageId, PayloadHandler handler)` | Đăng ký handler cho plain message |
| `void RegisterObject(uint messageId, ObjectPayloadHandler handler)` | Đăng ký handler cho object message |
| `bool IsObjectMessage(uint messageId)` | Đã có object handler được đăng ký hay chưa |
| `bool Dispatch(ulong peerId, uint messageId, ReadOnlyMemory<byte> data)` | Gọi handler; false khi không có. Được các session dùng. |
| `int HandlerCount` | Số handler đã đăng ký |

Các handler là những delegate sau:

```csharp
public delegate void PayloadHandler(ulong peerId, ReadOnlyMemory<byte> payload);
public delegate void ObjectPayloadHandler(ulong peerId, uint objectId, byte behaviourIndex, ReadOnlyMemory<byte> body);
```

`Register` và `RegisterObject` ném `HandlerRegistrationException` với id không có trong schema hoặc đã có handler.

## Exception <a href="#exceptions" id="exceptions"></a>

| Exception | Namespace | Ném khi |
|---|---|---|
| `MessageDecodeException` | `Fomoxa.Networking.Messaging` | Adapter không decode được payload |
| `HandlerRegistrationException` | `Fomoxa.Networking.Messaging` | Việc đăng ký handler, RPC, state, collection hoặc input không hợp lệ |

## System model <a href="#system-models" id="system-models"></a>

Các model của chính package nằm trong `Fomoxa.Networking.Messaging`. Chúng được sinh cùng model của bạn và là một phần của mọi schema, nhưng code game không gửi chúng.

| Model | Mục đích | Channel |
|---|---|---|
| `MessageBundle`, `BundleEntry` | Nhiều message trong một frame | Unreliable |
| `ReliableAck` | Acknowledgement cho message reliable | Unreliable |
| `PeerLeave` | Một client rời đi | Unreliable |
| `LocalPeer` | Peer id của client, tick rate và physics backend | Reliable ordered |
| `ObjectSpawn`, `ObjectSceneSpawn`, `ObjectDespawn`, `ObjectOwnerChange` | Vòng đời object | Reliable ordered |
| `StateDelta`, `StateResync` | Delta của state, và yêu cầu state đầy đủ từ client | Reliable ordered |
| `CollectionChanges` | Các thao tác gọi trên một collection trong một tick | Reliable ordered |
| `CollectionContent`, `CollectionResync` | Toàn bộ nội dung của một collection, và yêu cầu nội dung đó từ client | Reliable ordered |
| `CollectionContents` | Các collection của một behaviour bên trong message spawn | Không gửi riêng |
| `BoolValue`, `I8Value`, `U8Value`, `I16Value`, `U16Value`, `I32Value`, `U32Value`, `I64Value`, `U64Value`, `F32Value`, `F64Value`, `StringValue` | Một phần tử collection kiểu nguyên thuỷ | Không gửi riêng |
| `TransformUpdate` | Transform khi đang di chuyển | Unreliable |
| `TransformSettle` | Transform cuối cùng | Reliable ordered |
| `AnimatorState` | State của `NetworkAnimator` | Reliable ordered |
| `SceneLoad`, `SceneUnload`, `SceneLoaded` | Network scene | Reliable ordered |
| `TickPing`, `TickPong` | Đồng bộ đồng hồ | Unreliable |
| `InputFrames` | Input của một object được dự đoán | Unreliable |
| `ReconcileState` | State của server cho reconciliation | Unreliable |

Các tham chiếu [attribute](attributes.md), [event và callback](callbacks.md) và [lỗi](errors.md) nói về các type liên quan.
