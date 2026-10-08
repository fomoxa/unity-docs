# Architecture

The package is built in layers, and each layer only uses the layers below it. Layer 1, the Core, does not know about Unity. Layer 2 connects it to Unity.

```text
Your game: MonoBehaviours, NetworkBehaviours, models
    ↓
Layer 2: Fomoxa.Unity                Unity integration
    ↓
Layer 1: Fomoxa.Networking           the Core: engine-independent networking
    ↓
Fomoxa.Net                           Fomoxa protocol: framing, handshake, heartbeat
    ↓
Transport                            UDP, TCP, WebSocket, in-process loopback
    ↓
Network
```

Both ends of a connection have the same stack:

```text
Unity client                              Server
Game code                                 Game code
    ↓                                         ↑
Layer 2: Fomoxa.Unity                     Layer 2: Fomoxa.Unity
    ↓                                         ↑
Layer 1: Fomoxa.Networking                Layer 1: Fomoxa.Networking
    ↓                                         ↑
Fomoxa.Net and transport  ─── network ──→ Fomoxa.Net and transport
```

Messages from the server to the client pass through the same layers in the opposite direction.

## Assemblies

| Assembly | Folder | References UnityEngine | Contents |
|---|---|---|---|
| `Fomoxa.Net` | `Runtime/Plugins/Fomoxa.Net.dll` | No | The Fomoxa protocol runtime: frames, handshake, heartbeat, `Schema`, TCP and UDP transports |
| `Fomoxa.Attributes` | `Runtime/Plugins/Fomoxa.Attributes.dll` | No | `[Network]` and `[Codec]`, in namespace `Fomoxa` |
| `Fomoxa.Networking` | `Runtime/Core` | No | Layer 1, plus the RPC source generator in `Runtime/Core/Generators` |
| `Fomoxa.Unity` | `Runtime/Unity` | Yes | Layer 2 |
| `Fomoxa.Unity.Editor` | `Editor` | Yes, Editor only | Code generation hook, prefab and scene id steps, scene files, build checks |

## Layer 1: Fomoxa.Networking

Layer 1 holds everything that can work without Unity. Its assembly definition sets `noEngineReferences`, so the compiler rejects any use of `UnityEngine` inside it. Vectors and quaternions in its API are `System.Numerics` types.

| Area | Namespace | What it does |
|---|---|---|
| Managers | `Fomoxa.Networking` | `ServerManager`, `ClientManager` and `TimeManager`, the order of work in one tick, `FomoxaRegistry`, the RPC and channel attributes, and the registration types `NetworkRpcs`, `NetworkState` and `NetworkInput` |
| Messaging | `Fomoxa.Networking.Messaging` | Message ids, `IMessageCodec<T>`, message bundles, the reliable-ordered channel, the dispatcher that routes a message id to a handler, delta encoding, the package's system models |
| Sessions | `Fomoxa.Networking.Sessions` | Client and server sessions: connection states, send queues and their limits, flushing, reconnection, connection events |
| Objects | `Fomoxa.Networking.Objects` | The object table, spawn, despawn and owner messages, observer sets, network scenes per peer |
| Timing | `Fomoxa.Networking.Timing` | The client's estimate of the server tick and of the prediction tick, ping and pong |
| Prediction | `Fomoxa.Networking.Prediction` | The server's input buffers per object and peer, and the client's prediction, reconciliation and replay |
| Simulation | `Fomoxa.Networking.Simulation` | The physics interfaces `IPhysicsSimulation`, `IPhysicsWorld` and `IPhysicsWorld2D`, `PhysicsBody`, `PhysicsHistory` and contact tracking |
| Transports | `Fomoxa.Networking.Transports` | `ITransportFactory`, non-blocking connectors, the WebSocket protocol, loopback, combined listeners |

Spawning, ownership, RPC and state routing, observer decisions and the decision of when to send a transform are all made in layer 1. A `NetworkBehaviour` forwards its callbacks and registrations to a layer 1 behaviour, so the rules are the same whatever drives them.

Layer 1 writes its warnings and errors through a `NetworkLog` that layer 2 gives it, and layer 2 sends them to the Unity Console.

## Layer 2: Fomoxa.Unity

Layer 2 connects layer 1 to Unity's GameObjects, scenes, player loop and physics. `NetworkManager` reads its Inspector fields, builds layer 1 from them and runs it from Unity's player loop. `TransportManager`, `NetworkObject` and `NetworkBehaviour` are in this layer too, and so are the `NetworkTransform` and `NetworkAnimator` components.

The prefab and scene registries, scene loading and the observer rule assets live in layer 2 as well, and so do the `RigidbodyPhysics` component with the `Rigidbody` and `Rigidbody2D` worlds, the contact event components and the transport components, including the browser WebSocket for WebGL.

## Generated code

The game's own code works together with code that the package generates in the project:

```text
Models (your classes with [Network] and [Codec])
    ↓ fomoxac
Codecs (<Model><Codec>Codec) and NetSchema
    ↓ package Editor step
Adapters (<Model><Codec>Adapter : IMessageCodec<T>), FomoxaAdapters.RegisterAll, FomoxaUnityRegistration
    ↓ at startup
FomoxaRegistry.Default
    ↓ in Awake
NetworkManager
```

The package's own messages, such as spawn and transform messages, are models too. The package copies them into the project's `FomoxaSystemModels` folder and generates them together with yours, so every message the game sends belongs to one schema, which the client and the server compare during the handshake. [Editor integration](../unity/editor-integration.md) lists every generated file.

## Why the split

Layer 1 does not depend on Unity, so it can be compiled and tested outside Unity. Physics follows the same split: game code uses the interfaces and `PhysicsBody` from layer 1, and the Unity worlds implement them in layer 2, as [physics architecture](../physics/architecture.md) explains.

The [networking model](networking-model.md) and [ticks and timing](tick.md) pages build on this one, and the [API index](../reference/api.md) lists the public API by type.
