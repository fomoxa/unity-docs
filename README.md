# Fomoxa for Unity

Fomoxa for Unity (`com.fomoxa.networking`) is a server-authoritative networking package for Unity games, built on the Fomoxa protocol and its C# runtime, Fomoxa.Net. A game declares its messages as plain C# classes and the package generates their codecs. Components such as `NetworkManager`, `NetworkObject` and `NetworkBehaviour` then take care of connections, spawning, RPCs, state, transforms and client-side prediction.

| | |
|---|---|
| Package | `com.fomoxa.networking` 0.1.0 |
| Unity | 6000.5 or later |
| License | Apache-2.0 |
| Bundled code generator | `fomoxac` v0.2.2, Windows x64 and Linux x64 |

## Where to start

If you are new to the package, read the [introduction](getting-started/introduction.md) first, then follow [installation](getting-started/installation.md) and the three tutorial pages after it, which build a small game with a server, a host and clients. The [concepts](concepts/architecture.md) section explains how the package works underneath: its layers, the tick, authority, replication and prediction.

When you want to add a particular feature, go to the guides under Core, Messaging, Synchronization, Prediction, Physics and Transports, where each page covers one feature with working code. If you are porting an existing game, the [Red Runner example](examples/redrunner/README.md) takes a single-player platformer online in nine steps and shows the real code and commits along the way. To look up a single member, use the [reference](reference/api.md), which lists the public API by type.

## What the package covers

The package connects peers over UDP, TCP or WebSocket. One server can listen on several transports at once, and host mode uses an in-process connection instead of a socket. Network objects are spawned from prefabs or placed in scenes, and each one can have an owner and a visibility that differs per peer.

Clients call the server and the server calls clients through RPCs declared with attributes. Each behaviour can keep a state that is sent with delta encoding, `NetworkTransform` replicates transforms with interpolation and teleport, and `NetworkAnimator` replicates the Animator. Network scenes can be loaded for everyone or only for selected peers.

The package also offers client-side prediction with input, reconciliation and replay, including rollback of Unity 3D and 2D physics. WebGL clients connect through the browser's WebSocket.

The [introduction](getting-started/introduction.md#what-is-not-included) lists what the package does not do.

## Beyond Unity's physics and Unity servers

Two optional parts build on the same package once a game works in Unity. [Rapier physics](rapier/overview.md) is a separate package that replaces Unity's physics with Rapier, so that rollback replays the server's physics exactly. The [console server](console-server/overview.md) runs a game's server as a .NET program without Unity. The rest of this documentation does not depend on either of them, and the second part of the [Red Runner example](examples/redrunner/rapier-and-console/README.md) uses both.
