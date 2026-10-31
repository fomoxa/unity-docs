# Release notes

## 0.2.0

This release ships these parts together:

| Part | Version | Install |
|---|---|---|
| `com.fomoxa.networking` | 0.2.0 | `https://github.com/fomoxa/com.fomoxa.networking.git#0.2.0` |
| `com.fomoxa.rpc` | 0.1.0, first release; needs `com.fomoxa.networking` 0.2.0 | `https://github.com/fomoxa/com.fomoxa.rpc.git#0.1.0` |
| `com.fomoxa.networking.rapier` | 0.1.1; needs `com.fomoxa.networking` 0.2.0 | `https://github.com/fomoxa/networking-rapier.git?path=com.fomoxa.networking.rapier#0.1.1` |
| `Fomoxa.Backend.Templates` | 0.1.0, first release | `dotnet new install Fomoxa.Backend.Templates::0.1.0` |
| `fomoxa-directory`, `fomoxa-gateway` | 0.2.0, first release, as source | [fomoxa/gateway](https://github.com/fomoxa/gateway) at tag `0.2.0`; build with Cargo |

### Upgrading from 0.1.0

A 0.2.0 server does not accept a 0.1.0 client, and a 0.2.0 client cannot join a 0.1.0 server. The package added system models, so the handshake sees a different schema, and every UDP datagram now carries a session id. Update the server and every client build at the same time.

- Update `com.fomoxa.networking.rapier` to 0.1.1 together with the package. Version 0.1.0 of the Rapier backend reports a version error with the 0.2.0 package.
- The package now ships `BouncyCastle.Cryptography.dll` and `Fomoxa.Net.WebSockets.dll` in `Runtime/Plugins`. If your project has its own copy of either assembly, remove it.
- A console server compiles `Standalone~` from the package, so rebuild it from the 0.2.0 package.
- A client that the server closes with a notice no longer reconnects. The server sends the notice on `Kick`, on a [server transfer](connections/transfer.md), and when a server handler throws; in 0.1.0 a handler exception dropped the connection and the client reconnected. The client stops with `StopReason.ServerClosed`, or `Transferred` after a transfer. The [ClientManager reference](reference/client-manager.md) lists every reason the client does not retry after.
- Objects that no peer observes no longer send state or transform updates. A peer that starts observing one still receives its current state.

### Connections

- [Authentication](connections/authentication.md): a peer passes a new `Authenticating` state before `Started`. `IServerAuthenticator` and `IClientAuthenticator`, or the `NetworkAuthenticator` component, exchange messages with the client, accept it or reject it with a reason, and can check asynchronously with a cancellation token.
- `ServerManager.Kick(peerId)` tells the client why it is being closed and flushes what is queued first, within Close Timeout Seconds. See [server](connections/server.md#peers).
- [Server transfer](connections/transfer.md): `ServerManager.Transfer` sends a client to another server with a ticket. The client connects there by itself and raises `OnTransferring`. `TransferTickets` issues and checks HMAC-SHA256 tickets with an expiry and a one-time nonce.
- [Encrypted UDP](connections/transports/encrypted-udp.md), off by default: `EncryptedUdpNetworkTransport` encrypts every datagram with keys made per connection. Your login service issues grants with `ConnectTokens`, and the client passes one to `StartConnection(address, port, connection)`.
- [Client TLS](connections/transports/tls.md), off by default: native clients connect over TLS on TCP and with `wss://` on WebSocket. The package checks certificates against the Mozilla roots it ships. A rejected certificate stops the client with `StopReason.TlsRejected`.
- [Encrypted WebSocket](connections/transports/encrypted-websocket.md): the encrypted UDP datagrams carried over WebSocket, so WebGL clients reach the same pods through a gateway.
- An encrypted UDP listener can run [behind a gateway](connections/transports/encrypted-udp.md#behind-a-gateway). `ServerManager.ArrivedOverWebSocket(peerId)` tells which way a peer came in.

### Messages and synchronization

- Reliable messages larger than one bundle are split and joined again, up to 1 MiB. A larger send returns `SendResult.TooLargeForReassembly`. See [channels](messaging/channels.md#message-size).
- [Collections](synchronization/collections.md): `NetworkList<T>`, `NetworkDictionary<TKey, TValue>` and `NetworkSet<T>` send the operations made on them. A client that misses operations asks for the whole collection again.
- [State](synchronization/state.md#marking-changes) can be sent only when you mark it changed, with `state.Use(..., onlyWhenDirty: true)` and `SetStateDirty()`.
- [Observers](objects/observers.md): `ServerManager.Groups` keeps groups of peers for an observer rule, and a rule whose answer changes only when the game changes something can turn off the periodic recalculation with `RebuildsPeriodically`.
- A transform is read only when its source reports a change: `IPhysicsMotion` for physics backends, and `SyncTransform(sync, receiver)` for entities of the console server.

### Performance

The server does less work per tick. It looks up observers in hash sets, visits only objects that have input, and skips objects nobody observes. The Fomoxa.Net runtime looks up peers by id in a hash table.

### Fomoxa.Net

The package ships a temporary build of Fomoxa.Net 0.1.3 with one fix: a TCP or WebSocket send no longer blocks under Unity's Mono on Windows when the socket's send buffer is full. [Installation](getting-started/installation.md) explains the parts that work around Mono, and a later version for Unity on CoreCLR drops them.

### fRPC: `com.fomoxa.rpc` 0.1.0

The new package adds fRPC services to a Unity project. You declare a service as a C# interface, and its client calls the backend over TCP, or over WebSocket in WebGL. The package also holds the pod side of the directory, `DirectoryPod`: it registers a game server with the directory, takes rooms, reports load, and tells the game when the pod is drained so the game can move its rooms. See its [README](https://github.com/fomoxa/com.fomoxa.rpc).

### Cluster

The [cluster](deploy/cluster.md) page shows how the new parts fit together. A game backend made from the `fomoxa-backend` template logs players in and asks the directory for a room. The directory places rooms on pods and issues grants, the gateway gives the pods one public UDP address and a WebSocket endpoint, and a drained pod moves its players to another pod.

The directory and the gateway are released as source only. There are no prebuilt binaries or container images yet.

### Rapier backend 0.1.1

- Reports the bodies that moved in each step through `IPhysicsMotion`, so `NetworkTransform` reads only those.
- On Linux the native library needs glibc 2.34 or later.
