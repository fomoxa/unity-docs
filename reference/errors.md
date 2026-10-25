# Errors and stop reasons reference

## StopReason

`Fomoxa.Networking.Sessions.StopReason` appears in `ConnectionStateArgs.Reason` when a connection stops.

| Value | Meaning | Client retries |
|---|---|---|
| `None` | The connection has not stopped | |
| `LocalStop` | This side called `StopConnection`, `Disconnect` or `Kick` | No |
| `PeerClosed` | The other side closed the connection, or the client sent a leave message | Yes |
| `TransportError` | The transport failed: refused connection, unresolved host, socket error | Yes |
| `Timeout` | The heartbeat probe was not answered in time | Yes |
| `HandshakeFailed` | The Fomoxa handshake failed; see `Failure` | Only for `Timeout` |
| `HandlerException` | A message handler on this side threw. When a server handler throws on a client's message, the server's peer stops with this reason and the client stops with `ServerClosed` | No |
| `PrefabMismatch` | The client cannot spawn an object: unknown or different prefab or scene object, or a network scene that does not load | No |
| `ObjectMismatch` | The client received an object message it cannot apply | No |
| `PhysicsBackendMismatch` | The client and the server use different physics backends | No |
| `InvalidFragment` | The other side sent fragments of a large reliable message that do not fit together | No |
| `ServerClosed` | The server closed the connection on purpose and sent its reason, which is in `CloseReason` | No |
| `UnauthenticatedMessage` | While the connection was `Authenticating`, the other side sent a message that the [authentication](../connections/authentication.md#messages-outside-the-authentication) does not allow | No |
| `AuthenticationFailed` | On the server: the authenticator rejected the peer. The client stops with `ServerClosed` | |
| `AuthenticationTimeout` | On the server: the peer was not accepted within Authentication Timeout Seconds. The client stops with `ServerClosed` | |

## SessionCloseReason

`Fomoxa.Networking.Sessions.SessionCloseReason` appears in `ConnectionStateArgs.CloseReason` when a client stops with `ServerClosed`. The server sends it just before it closes the connection.

| Value | Meaning |
|---|---|
| `Unspecified` (0) | No reason was given. The package itself never sends this value |
| `HandlerException` (1) | A message handler on the server threw while handling this client's message |
| `Kicked` (2) | The server called `ServerManager.Kick` |
| `AuthenticationFailed` (3) | The server's authenticator rejected the client |
| `AuthenticationTimeout` (4) | The client was not accepted within the server's Authentication Timeout Seconds |

A newer server may send a value this list does not have. The client keeps the value as it arrived, and it still does not retry.

## HandshakeFailure

`Fomoxa.Net.HandshakeFailure` appears in `ConnectionStateArgs.Failure`.

| Value | Meaning |
|---|---|
| `VersionMismatch` | The two sides speak different Fomoxa protocol versions |
| `SchemaConflict` | The two sides were built from different models |
| `Corrupt` | The handshake data could not be read |
| `Timeout` | The handshake did not finish within Handshake Timeout Seconds |

## ObjectMismatchKind

`Fomoxa.Networking.Objects.ObjectMismatchKind` appears in `ObjectMismatchArgs.Kind`. The first four kinds and `UnknownScene` stop the client with `PrefabMismatch`, and the others with `ObjectMismatch`.

| Value | Meaning |
|---|---|
| `UnknownPrefab` | No registered prefab has the spawn's prefab id |
| `IncompatiblePrefab` | The prefab's `NetworkBehaviour` list differs from the server's |
| `UnknownSceneObject` | No scene object has the spawn's scene object id |
| `IncompatibleSceneObject` | The scene object's `NetworkBehaviour` list differs from the server's |
| `UnknownScene` | A network scene could not be loaded |
| `DuplicateObject` | A spawn for an object id the client already has |
| `UnknownObject` | A message for an object id the client does not have, where one is required |
| `InvalidSpawn` | A spawn the client cannot apply, such as a state that does not decode or a scene the client has not loaded |
| `InvalidMessage` | An object or scene message that does not decode |

## SendResult

`Fomoxa.Networking.Sessions.SendResult` is returned by the send methods.

| Value | Meaning |
|---|---|
| `Queued` | The message is in the send queue |
| `Full` | The queue holds Message Capacity messages |
| `BytesFull` | The queue holds too many bytes for this message |
| `TooLargeForQueue` | The message is larger than Byte Capacity |
| `TooLargeForReassembly` | A `ReliableOrdered` message that has to be split for the transport is larger than 1 MiB |
| `TooLarge` | The message is larger than the protocol allows |
| `NotConnected` | No connection, or no such peer. From an authentication context: that authentication has ended |
| `NotObserver` | A target RPC to a peer that does not observe the object |

## SendStatus

`Fomoxa.Net.SendStatus` appears in `SendDroppedArgs.Reason`, where `TooLarge` means the transport could not send the message and it was dropped.

## Exceptions

| Exception | Thrown by | Cause |
|---|---|---|
| `InvalidOperationException` | `NetworkManager.Awake` | The generated registration did not run |
| `InvalidOperationException` | `StartConnection` | Already running |
| `InvalidOperationException` | `ServerManager.Authenticator`, `ClientManager.Authenticator` | Set while that side is running |
| `InvalidOperationException` | `Send`, `Accept`, `Reject` of an authentication context | The authentication was already accepted |
| `InvalidOperationException` | `Spawn`, scene methods | The server is not started |
| `InvalidOperationException` | Send RPC methods | The object is not spawned on the sending side, or a parameterless RPC has no generated model |
| `ArgumentException` | `Spawn` | Prefab asset, already spawned, unregistered prefab id, invalid scene object, owner not started |
| `ArgumentException` | `PrefabRegistry.Register`, `SceneRegistry.Register` | Id 0, id registered to something else, invalid prefab hierarchy |
| `HandlerRegistrationException` | Registration hooks, `MessageDispatcher.Register` | Invalid state, input or RPC registration; id not in the schema; duplicate handler |
| `PlatformNotSupportedException` | Transports, `ServerManager.StartConnection` | UDP or TCP in a browser; a server in a browser |
| `NotSupportedException` | Desktop WebSocket client | A `wss://` URL |
| `MessageDecodeException` | Adapters | A payload that does not decode |

## Run-time log messages

| Message | Meaning |
|---|---|
| `Fomoxa dropped message 0x... (N bytes) to peer N: <reason>` | A queued message could not be sent |
| `Fomoxa dropped N received bytes from peer N: a message bundle, or a model in it, could not be read` | A received bundle could not be read |
| `Fomoxa dropped server RPC 0x... to object N from peer N, which does not own the object` | A server RPC with `RequireOwnership` from a non-owner |
| `Fomoxa dropped input to object N from peer N, which does not own the object` | Input from a non-owner |
| `Fomoxa stopped the client: object mismatch <kind>, object N, prefab 0x..., scene object 0x...` | `OnObjectMismatch` without a subscriber |
| `Fomoxa: object N (prefab 0x...) was destroyed on the client without a despawn from the server` | A spawned GameObject was destroyed on a client |
| `Fomoxa: <name> received Animator state with layout 0x..., but its Animator has layout 0x...` | The Animator controllers differ between server and client |

Editor messages start with `[Fomoxa]` and are covered in [troubleshooting](../getting-started/troubleshooting.md#code-generation-fails) and [editor integration](../advanced/editor-integration.md).

[Troubleshooting](../getting-started/troubleshooting.md) goes from symptoms to these values, and [events and callbacks](callbacks.md) lists the events that carry them.
