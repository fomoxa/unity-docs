# ClientManager reference

`public sealed class ClientManager` in `Fomoxa.Networking` has no public constructor; you reach it through `NetworkManager.ClientManager`. The [client](../connections/client.md) guide explains how to use it.

## Connection

| Member | Description |
|---|---|
| `void StartConnection(string address, ushort port)` | Connects to a server. When the same manager runs a server, connects through the in-process connection and ignores both arguments. Throws `InvalidOperationException` when already running. |
| `void StopConnection()` | Sends a leave message, closes the connection, despawns the client's objects and cancels pending retries |
| `ConnectionState State` | `Stopped`, `Starting`, `Authenticating` or `Started` |
| `IClientAuthenticator Authenticator` | The client side of the [authentication](../connections/authentication.md). Get and set; setting it while the client is running throws `InvalidOperationException`. |
| `TimeSpan Rtt` | Smoothed round-trip time to the server; zero for a host's client and before the first clock answer |

## Objects and prediction

| Member | Description |
|---|---|
| `IReadOnlyDictionary<uint, INetworkEntity> Spawned` | Objects spawned on this client, by object id; each value is a `NetworkObject` in Unity |
| `bool IsReplaying` | True while the client replays input during reconciliation |

## Messages

| Member | Description |
|---|---|
| `SendResult Send(uint messageId, ReadOnlySpan<byte> payload)` | Queues a message for the server; `NotConnected` while stopped. Before `Started`, the message waits in the queue. |
| `SendResult SendToObject(uint messageId, uint objectId, byte behaviourIndex, ReadOnlySpan<byte> body)` | Queues an object message for the server |
| `MessageDispatcher Dispatcher` | Handlers for incoming messages |

## Events

| Event | Argument |
|---|---|
| `OnClientConnectionState` | `ConnectionStateArgs`, including `WillRetry` |
| `OnSendDropped` | `SendDroppedArgs` |
| `OnReceiveDropped` | `ReceiveDroppedArgs` |
| `OnHandlerException` | `HandlerExceptionArgs`; logged when nobody subscribes |
| `OnObjectMismatch` | `ObjectMismatchArgs`; logged when nobody subscribes |

[Events and callbacks](callbacks.md) describes the event arguments.

## Reconnection

Reconnection is configured on the `NetworkManager` with Max Reconnect Retries and Reconnect Interval Seconds. The client does not retry after `LocalStop`, `HandlerException`, `PrefabMismatch`, `ObjectMismatch`, `PhysicsBackendMismatch`, `InvalidFragment`, `ServerClosed`, or a `HandshakeFailed` other than `Timeout`, and never retries a host's in-process connection.

The related types are [NetworkManager](network-manager.md), [ServerManager](server-manager.md) and [TimeManager](time-manager.md).
