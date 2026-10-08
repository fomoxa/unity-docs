# Raw messages

RPCs are tied to a spawned object, and raw messages are not. With raw messages, the server and the client send a model by its message id, and a handler registered for that id handles it. They suit game-wide messages such as chat, match events or lobby data.

## When to use them

Use a raw message when the message has no natural object, when it must work before any object is spawned, or when you want to handle it once per connection rather than once per object.

Raw messages bypass observers and ownership checks. The server sends them to whichever peers you choose, and the handler receives the sender's peer id, so validate everything a client sends.

## Basic usage

Start with the model:

```csharp
using Fomoxa;
using Fomoxa.Networking;

namespace MyGame.Network.Models
{
    [Network]
    [Codec("net")]
    [NetworkChannel("net", Channel.ReliableOrdered)]
    public class ChatLine
    {
        [Network("string")]
        [Codec("net")]
        public string Text { get; set; }
    }
}
```

The following component relays chat through the server:

```csharp
using System;
using Fomoxa.Networking;
using Fomoxa.Networking.Sessions;
using Fomoxa.Unity;
using Generated;
using MyGame.Network.Models;
using UnityEngine;

public sealed class Chat : MonoBehaviour
{
    private const int MaxLength = 200;

    [SerializeField] private NetworkManager manager;

    private readonly ChatLine received = new ChatLine();

    private static ChatLineNetAdapter Codec => ChatLineNetAdapter.Instance;

    private void Start()
    {
        manager.ServerManager.Dispatcher.Register(Codec.MessageId, OnServerReceived);
        manager.ClientManager.Dispatcher.Register(Codec.MessageId, OnClientReceived);
    }

    public SendResult Say(string text) =>
        manager.ClientManager.Send(Codec.MessageId, Codec.Encode(new ChatLine { Text = text }).Span);

    private void OnServerReceived(ulong peerId, ReadOnlyMemory<byte> payload)
    {
        ChatLine line = received;
        Codec.Decode(payload, ref line);
        if (string.IsNullOrWhiteSpace(line.Text) || line.Text.Length > MaxLength)
        {
            return;
        }

        line.Text = $"{peerId}: {line.Text}";
        manager.ServerManager.Broadcast(Codec.MessageId, Codec.Encode(line).Span);
    }

    private void OnClientReceived(ulong peerId, ReadOnlyMemory<byte> payload)
    {
        ChatLine line = received;
        Codec.Decode(payload, ref line);
        Debug.Log(line.Text);
    }
}
```

## Sending

| Method | Sends to |
|---|---|
| `ClientManager.Send(messageId, payload)` | The server |
| `ServerManager.Send(peerId, messageId, payload)` | One peer |
| `ServerManager.Broadcast(messageId, payload)` | Every peer in the `Started` state; returns how many it was queued for |

The payload is copied into the send queue during the call, and the message travels on the model's channel. `Send` returns a `SendResult`, where `NotConnected` means the connection or the peer does not exist.

`ClientManager.SendToObject` and `ServerManager.SendToObject` send a message addressed to one behaviour of one object, the way RPCs do. RPCs are built on top of them, and game code should prefer RPCs.

## Receiving

`ServerManager.Dispatcher` and `ClientManager.Dispatcher` are separate, so register a handler on each side that should receive the message:

```csharp
manager.ServerManager.Dispatcher.Register(messageId, (peerId, payload) => { });
```

The message id must be in the generated schema, and each id can have only one handler per dispatcher. Otherwise `Register` throws `HandlerRegistrationException` with `message id 0x... is not declared in the schema` or `already has a handler`. Register after the `NetworkManager` has run `Awake`, for example in `Start`, and before the messages arrive.

On a client, `peerId` is always 0. `payload` is only valid during the call, so decode or copy it before returning. A handler that throws disconnects the peer on the server, or stops the client, with `StopReason.HandlerException`, whereas a `MessageDecodeException` from `Decode` only drops the message.

Raw messages are [models](models.md) on their [channel](channels.md), just like [RPCs](rpc.md). The [messaging API](../reference/messaging.md) lists the dispatcher and send members.
