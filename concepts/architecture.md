# Architecture

The package is built in layers, and each layer only uses the layers below it. Layer 2 is the lowest layer that knows about Unity.

```text
Your game: MonoBehaviours, NetworkBehaviours, models
    ↓
Layer 2: Fomoxa.Unity                Unity integration
    ↓
Layer 1: Fomoxa.Unity.Core           engine-independent networking
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
Layer 1: Fomoxa.Unity.Core                Layer 1: Fomoxa.Unity.Core
    ↓                                         ↑
Fomoxa.Net and transport  ─── network ──→ Fomoxa.Net and transport
```

Messages from the server to the client pass through the same layers in the opposite direction.

## Assemblies

| Assembly | Folder | References UnityEngine | Contents |
|---|---|---|---|
| `Fomoxa.Net` | `Runtime/Plugins/Fomoxa.Net.dll` | No | The Fomoxa protocol runtime: frames, handshake, heartbeat, `Schema`, TCP and UDP transports |
| `Fomoxa.Attributes` | `Runtime/Plugins/Fomoxa.Attributes.dll` | No | `[Network]` and `[Codec]`, in namespace `Fomoxa` |
| `Fomoxa.Unity.Core` | `Runtime/Core` | No | Layer 1 |
| `Fomoxa.Unity` | `Runtime/Unity` | Yes | Layer 2, plus the RPC source generator in `Runtime/Unity/Generators` |
| `Fomoxa.Unity.Editor` | `Editor` | Yes, Editor only | Code generation hook, prefab and scene id steps, build checks |

## Layer 1: Fomoxa.Unity.Core

Layer 1 holds everything that can work without Unity. Its assembly definition sets `noEngineReferences`, so the compiler rejects any use of `UnityEngine` inside it.

| Area | Namespace | What it does |
|---|---|---|
| Messaging | `Fomoxa.Unity.Messaging` | Message ids, `IMessageCodec<T>`, message bundles, the reliable-ordered channel, the dispatcher that routes a message id to a handler, delta encoding, the package's system models |
| Sessions | `Fomoxa.Unity.Sessions` | Client and server sessions: connection states, send queues and their limits, flushing, reconnection, connection events |
| Objects | `Fomoxa.Unity.Objects` | The object table, spawn, despawn and owner messages, observer sets, network scenes per peer |
| Timing | `Fomoxa.Unity.Timing` | The client's estimate of the server tick and of the prediction tick, ping and pong |
| Prediction | `Fomoxa.Unity.Prediction` | The server's input buffers per object and peer |
| Simulation | `Fomoxa.Unity.Simulation` | The physics interfaces `IPhysicsSimulation`, `IPhysicsWorld` and `IPhysicsWorld2D`, `PhysicsBody`, and `PhysicsHistory` |
| Transports | `Fomoxa.Unity.Transports` | `ITransportFactory`, non-blocking connectors, the WebSocket protocol, loopback, combined listeners |
| Registry | `Fomoxa.Unity` | `FomoxaRegistry`, which holds the schema, the codecs, the channels and the RPC ids; the RPC and channel attributes |

Layer 1 never logs. It reports what happens through events, and layer 2 turns those events into Unity log messages.

## Layer 2: Fomoxa.Unity

Layer 2 connects layer 1 to Unity's GameObjects, scenes, player loop and physics. It contains `NetworkManager` with its player loop entries, together with `ServerManager`, `ClientManager`, `TimeManager` and `TransportManager`. It also contains `NetworkObject` and `NetworkBehaviour` with the registration of RPCs, state and input, prediction and replay, and the `NetworkTransform` and `NetworkAnimator` components.

The prefab and scene registries, scene loading and the observer rules live in layer 2 as well, and so do the `Rigidbody` and `Rigidbody2D` physics backends, the contact event components and the transport components, including the browser WebSocket for WebGL.

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

Because layer 1 does not depend on Unity, it can be compiled and tested on its own, and a server written as a plain .NET program could use it. The package does not ship such a server; [server console](../server/server-console.md) describes what exists today. Physics follows the same split, with game code using the interfaces and `PhysicsBody` from layer 1 and the Unity backends implementing them in layer 2, as [physics architecture](../physics/architecture.md) explains.

The [networking model](networking-model.md) and [ticks and timing](tick.md) pages build on this one, and the [API index](../reference/api.md) lists the public API by type.
