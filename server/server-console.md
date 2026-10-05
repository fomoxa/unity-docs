# Server console

{% hint style="warning" %}
Not packaged. Version 0.1.0 does not ship a server console, a project template or a supported workflow for one. This page describes what the package's layering allows and what is missing.
{% endhint %}

## What a server console is

A server console is a server written as a plain .NET program that does not load the Unity Engine. Unity clients would connect to it just as they connect to a Unity server.

## What exists

Layer 1 of the package, the `Fomoxa.Unity.Core` assembly in `Runtime/Core`, does not reference Unity; its assembly definition sets `noEngineReferences`, so the compiler rejects any Unity dependency. It contains the server-side parts a console would need:

| Part | Types |
|---|---|
| Sessions and connection events | `ServerSession`, `SessionLimits`, `ConnectionStateArgs` |
| Objects, ownership, observers | `ServerObjects` |
| Network scenes | `ServerScenes` |
| Clock and input buffers | `ServerClock`, `ServerInputs` |
| Transports | `TcpTransportFactory`, `UdpTransportFactory`, `WebSocketTransportFactory`, `MultiTransportFactory` |
| Registry | `FomoxaRegistry`, filled by the generated `FomoxaAdapters.RegisterAll` |
| Physics interfaces | `IPhysicsWorld`, `IPhysicsWorld2D`, `PhysicsHistory` |

The generated code also gives a server without Unity a way to refer to prefabs and scenes, through the constants in `FomoxaPrefabs.cs` and `FomoxaScenes.cs`. The generated `FomoxaAdapters.RegisterAll(registry)` works outside Unity too, and only `FomoxaUnityRegistration.cs` is Unity-specific.

## What is missing

There is no project file or build setup for compiling `Runtime/Core` and the generated code outside Unity, and there is no tick loop. In Unity, `NetworkManager` drives the sessions, the clock, input, state and transforms each tick, and a console would have to do the same.

Objects have no state, transform or RPC routing outside Unity either, because `NetworkObject`, `NetworkBehaviour`, `NetworkTransform` and the state mechanism are Unity components in layer 2. The only physics backend uses Unity's physics, and the `Rapier` backend is not implemented. Beyond the [API index](../reference/api.md), the layer 1 types are not documented.

Until the package supports a server console, run dedicated servers as Unity players in batch mode, as described in [dedicated server](dedicated-server.md). [Architecture](../concepts/architecture.md) and [physics architecture](../physics/architecture.md) explain the layering this page relies on.
