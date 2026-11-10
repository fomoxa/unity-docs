# Release notes

## 0.3.2

This release ships these parts together:

| Part | Version | Install |
|---|---|---|
| `com.fomoxa.networking` | 0.3.2 | `https://github.com/fomoxa/com.fomoxa.networking.git#0.3.2` |
| `com.fomoxa.rpc` | 0.1.3; needs `com.fomoxa.networking` 0.3.2 | `https://github.com/fomoxa/com.fomoxa.rpc.git#0.1.3` |
| `com.fomoxa.networking.rapier` | 0.2.2; needs `com.fomoxa.networking` 0.3.2 | `https://github.com/fomoxa/networking-rapier.git?path=com.fomoxa.networking.rapier#0.2.2` |

`Fomoxa.Backend.Templates` 0.1.0 and the directory and gateway at tag `0.2.0` have no new version.

### Upgrading from 0.3.1

Update `com.fomoxa.rpc` to 0.1.3 and `com.fomoxa.networking.rapier` to 0.2.2 together with the package. With the 0.3.2 package, `com.fomoxa.rpc` 0.1.2 reports an error when it generates code, and Rapier 0.2.1 throws a version error when it creates its worlds.

The API, the wire protocol, the handshake schema and the scene file format did not change, so 0.3.1 and 0.3.2 peers connect to each other, and generated code and exported scene files need no change.

### Code generation on macOS

The package now bundles `fomoxac` for the macOS Editor, next to the Windows x64 and Linux x64 builds. It is one binary for Apple silicon and Intel and needs macOS 11 or later. All three are `fomoxac` v0.2.2, so they generate the same code.

## 0.3.1

This release ships these parts together:

| Part | Version | Install |
|---|---|---|
| `com.fomoxa.networking` | 0.3.1 | `https://github.com/fomoxa/com.fomoxa.networking.git#0.3.1` |
| `com.fomoxa.rpc` | 0.1.2; needs `com.fomoxa.networking` 0.3.1 | `https://github.com/fomoxa/com.fomoxa.rpc.git#0.1.2` |
| `com.fomoxa.networking.rapier` | 0.2.1; needs `com.fomoxa.networking` 0.3.1 | `https://github.com/fomoxa/networking-rapier.git?path=com.fomoxa.networking.rapier#0.2.1` |

`Fomoxa.Backend.Templates` 0.1.0 and the directory and gateway at tag `0.2.0` have no new version.

### Upgrading from 0.3.0

Update the server before the clients, or at the same time. Over UDP, encrypted UDP and WebSocket, a 0.3.1 client sends the handshake of a schema with 63 messages or more in several packets. A 0.3.0 server drops those packets, and the client stops with `HandshakeFailed` and `Timeout`. The count includes the package's own messages. A 0.3.0 client can still join a 0.3.1 server, and TCP and TLS connections did not change.

- Update `com.fomoxa.rpc` to 0.1.2 and `com.fomoxa.networking.rapier` to 0.2.1 together with the package. With the 0.3.1 package, `com.fomoxa.rpc` 0.1.1 reports an error when it generates code, and Rapier 0.2.0 throws a version error when it creates its worlds.
- A console server compiles `Standalone~` and references `Runtime/Plugins/Fomoxa.Net.dll` from the package, so rebuild it from the 0.3.1 package.

The API, the handshake schema and the scene file format are the same as in 0.3.0, so generated code and exported scene files need no change.

### Large handshakes

In 0.3.0 the handshake went out in one packet that grew by 14 bytes for each message of the schema. Over plain UDP it passed 1200 bytes at 84 messages, sooner with encryption, and a network that drops IP fragments dropped it, so the client could not connect over that network. The package now ships Fomoxa.Net 0.1.4, which splits a handshake longer than 900 bytes into parts, one per packet. With encryption, each datagram stays within 1200 bytes for tickets of up to 249 bytes. As in 0.2.0, the package's build of Fomoxa.Net carries the fix for sends under Unity's Mono (see [Fomoxa.Net](#fomoxanet) under 0.2.0).

## 0.3.0

This release ships these parts together:

| Part | Version | Install |
|---|---|---|
| `com.fomoxa.networking` | 0.3.0 | `https://github.com/fomoxa/com.fomoxa.networking.git#0.3.0` |
| `com.fomoxa.rpc` | 0.1.1; needs `com.fomoxa.networking` 0.3.0 | `https://github.com/fomoxa/com.fomoxa.rpc.git#0.1.1` |
| `com.fomoxa.networking.rapier` | 0.2.0; needs `com.fomoxa.networking` 0.3.0 | `https://github.com/fomoxa/networking-rapier.git?path=com.fomoxa.networking.rapier#0.2.0` |

`Fomoxa.Backend.Templates` 0.1.0 and the directory and gateway at tag `0.2.0` have no new version.

### Upgrading from 0.2.0

A 0.3.0 server does not accept a 0.2.0 client, and a 0.2.0 client cannot join a 0.3.0 server. The package's scene file models gained fields, so the handshake sees a different schema. Update the server and every client build at the same time.

- Update `com.fomoxa.rpc` to 0.1.1 and `com.fomoxa.networking.rapier` to 0.2.0 together with the package. With the 0.3.0 package, `com.fomoxa.rpc` 0.1.0 reports an error when it generates code, and Rapier 0.1.1 throws a version error when it creates its worlds.
- The package rejects scene files written by 0.2.0. Export them again with Tools > Fomoxa > Export Network Scene Files and copy the new files to your console servers. Before a player build, the package rewrites the files it cannot read.
- Data that your game encoded with the package's scene file models can fail to decode with `MessageDecodeException`, for example a level catalogue that holds an array of `SceneFileCollider2D` values. Encode it again.
- A console server compiles `Standalone~` from the package, so rebuild it from the 0.3.0 package.
- Under `RigidbodyPhysics`, `Raycast` without a filter and `Overlap` with a radius now use `QueryFilter.All`. They consider every layer, Ignore Raycast included, and hit triggers, and a query that starts inside a collider hits it at distance 0. Pass a [`QueryFilter`](physics/queries.md#filters) to leave layers or triggers out.
- In 0.2.0 a remote client placed only the body on the GameObject of a network object as a proxy. Bodies on child GameObjects now follow the rules of [several bodies](physics/overview.md#several-bodies): a child body whose GameObject has a `NetworkTransform` is a proxy too, and the client simulates a child body without one. A `Rigidbody2D` with Simulated turned off is not a body.

### Physics

- [Physics queries](physics/queries.md): every query takes a `QueryFilter` with a layer mask, a body to skip and whether triggers count. Worlds add `ShapeCast` and `Overlap` with a shape, and `NetworkPhysics.WorldsOf` returns the worlds of a scene.
- [PhysicsBody](physics/physics-body.md) adds `AddTorque`, `AddTorqueImpulse`, `AddForceAtPoint` and `AddImpulseAtPoint`. [Continuous collision](physics/physics-body.md#continuous-collision) is set through `BodyMotion.ContinuousCollision`, which `BodyDescriptions` takes from the Collision Detection field.
- `PhysicsBody.GetContactPoints` lists where two bodies touch after the last step, and [`NetworkCollision.GetContactPoints`](physics/contacts.md#contact-points) lists the points of a collision event. Through `PhysicsBody`, `RigidbodyPhysics` returns no points for 3D bodies.
- `NetworkObject.Bodies` and `Bodies2D` list the [bodies](physics/overview.md#several-bodies) of a ragdoll or a vehicle, and a `NetworkTransform` on a child GameObject with a body syncs that body.

### Console servers and scene files

- An entity declares child bodies with `GetChildBodies` and `GetChildBodies2D`, and sends their poses with `SyncTransform(sync, ChildBody.Of(index), receiver)`. See [several bodies](console-server/physics.md#several-bodies).
- Scene files carry the child bodies of scene objects, the body each behaviour sits on and the 2D effectors of static colliders. The `BehaviourSite` overload of `StandaloneBehaviours.Register` tells a behaviour which body its GameObject carries. See [scene files](advanced/editor-integration.md#scene-files).

### Rapier backend 0.2.0

- Besides Windows x64 and Linux x64, the package now has native libraries for Windows arm64, Linux arm64, macOS, Android `arm64-v8a` and `armeabi-v7a`, iOS and Web. A build workflow compares their hashes with a reference list, and Windows players under Mono and IL2CPP, Web players and Android players give the same hashes. See [platforms](rapier/setup.md#platforms) and [checked platforms](rapier/determinism.md#checked-platforms).
- The queries, forces, torques, continuous collision, contact points and several bodies listed above work with the same API as under `RigidbodyPhysics`, and Rapier returns contact points for 3D bodies too.
- [Joints](rapier/joints.md) from Unity's joint components and from code.
- `MoveCharacter`, a [character controller](rapier/character-controller.md) for kinematic bodies.
- The five 2D [effectors](rapier/effectors.md) of Unity.

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
