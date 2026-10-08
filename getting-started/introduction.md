# Introduction

Fomoxa for Unity adds multiplayer networking to a Unity project. One process runs as the server and owns the game state. Clients connect to it, send their requests and input, and show what the server sends back. A host is a process that runs the server and a client together.

## How a game uses the package

A typical game goes through four steps.

1. It declares its network messages as C# classes called models, marked with `[Network]` and `[Codec]`. The package runs the `fomoxac` compiler on them and generates a codec for each one.
2. It puts a `NetworkManager` in a scene and picks a transport for it, such as `UdpNetworkTransport`.
3. It adds a `NetworkObject` to every prefab that exists on the network, and writes `NetworkBehaviour` scripts for the networked logic of those prefabs.
4. It starts a server, a client or a host from code, and the server spawns objects for the clients.

Once objects are spawned, a `NetworkBehaviour` can call RPCs and register a state model that the server keeps in sync. Adding a `NetworkTransform` replicates the object's position, and registering an input model lets the client predict its own character.

## Main types

| Type | Role |
|---|---|
| [`NetworkManager`](../core/network-manager.md) | The component that runs networking for a scene: configuration, tick loop, server and client |
| [`ServerManager`](../core/server.md) | Starts and stops the server, spawns and despawns objects, changes owners |
| [`ClientManager`](../core/client.md) | Connects to a server, reconnects, exposes the client's spawned objects |
| [`NetworkObject`](../core/network-object.md) | Marks a GameObject as a network object with an object id and an owner |
| [`NetworkBehaviour`](../core/network-behaviour.md) | Base class for networked scripts: lifecycle callbacks, RPCs, state and input |
| [`NetworkTransform`](../synchronization/transform.md) | Replicates position, rotation and scale from the server |
| [`NetworkAnimator`](../synchronization/animator.md) | Replicates Animator parameters, triggers and layer states |
| [`NetworkTransport`](../transports/overview.md) | Base class of the transport components: UDP, TCP, WebSocket, multiple |

## Feature status

| Feature | Status |
|---|---|
| UDP, TCP and WebSocket transports, multiple transports on one server | Available |
| Host mode over an in-process connection | Available |
| Spawning, scene objects, ownership, observers | Available |
| RPCs with and without a model, declared by attribute or registered by hand | Available |
| State with delta encoding, `NetworkTransform`, `NetworkAnimator` | Available |
| Network scenes | Available |
| Client-side prediction, reconciliation and replay | Available |
| Rollback of Unity physics (`Rigidbody` and `Rigidbody2D`) | Available, approximate (see [rollback](../prediction/rollback.md)) |
| WebGL client | Available |
| `fomoxac` binary for macOS | Not bundled; code generation fails in the macOS Editor |

## What is not included

The package has no lockstep simulation and cannot record or replay a whole match. It also has no deterministic random number generator and no state hashing.

Matchmaking, relay servers, lobbies and NAT traversal are outside the package as well, and so are encryption and authentication of connections. A WebSocket client in a browser can still reach a server over TLS through a proxy, as described in [WebSocket](../transports/websocket.md).

Continue with [installation](installation.md).
