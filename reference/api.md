# API index

This page lists the public types of the package by namespace. Types marked "building block" are public so that layer 1 can be used and tested on its own. Game code reaches the same features through the managers and components and normally does not use these types directly.

## Fomoxa.Unity (layer 2, assembly Fomoxa.Unity)

| Type | Kind | Page |
|---|---|---|
| `NetworkManager` | Component | [Reference](network-manager.md) |
| `ServerManager` | Class | [Reference](server-manager.md) |
| `ClientManager` | Class | [Reference](client-manager.md) |
| `TimeManager`, `TimingMode` | Class, enum | [Reference](time-manager.md) |
| `TransportManager` | Class | [NetworkManager reference](network-manager.md#transportmanager) |
| `NetworkObject`, `NetworkVisibility` | Component, enum | [Reference](network-object.md) |
| `NetworkBehaviour` | Abstract component | [Reference](network-object.md#networkbehaviour) |
| `NetworkRpcs`, `NetworkState`, `NetworkInput`, `InputContext` | Registration types | [Reference](network-object.md#registration-types) |
| `NetworkTransform`, `NetworkAnimator` | Components | [Components](components.md) |
| `NetworkCollision`, `NetworkTrigger`, `NetworkCollision2D`, `NetworkTrigger2D` | Components | [Components](components.md#contact-components) |
| `ObserverRule`, `DistanceRule`, `ObserverRange` | Asset types, component | [Components](components.md#observers) |
| `PrefabRegistry`, `SceneRegistry`, `ISceneLoader`, `NetworkScenes` | Classes, interface | [ServerManager reference](server-manager.md#scenes) |
| `NetworkPrefabList`, `NetworkSceneList` | Generated asset types | [Editor integration](../unity/editor-integration.md) |
| `NetworkTransport`, `UdpNetworkTransport`, `TcpNetworkTransport`, `WebSocketNetworkTransport`, `MultiNetworkTransport` | Components | [Components](components.md#transports) |
| `UnityPhysicsWorld`, `UnityPhysicsWorld2D` | Physics backend | [Physics API](physics.md#unity-backend) |

## Fomoxa.Unity (layer 1, assembly Fomoxa.Unity.Core)

| Type | Kind | Page |
|---|---|---|
| `ServerRpcAttribute`, `ClientRpcAttribute`, `NetworkRpcAttribute`, `NetworkChannelAttribute`, `MessageAdapterAttribute` | Attributes | [Attributes](attributes.md) |
| `Channel` | Enum | [Channels](../messaging/channels.md) |
| `FomoxaRegistry`, `RpcMessageIds` | Classes | [Messaging API](messaging.md) |

## Fomoxa.Unity.Messaging

| Type | Kind | Page |
|---|---|---|
| `IMessageCodec<T>`, `MessageDecodeException` | Interface, exception | [Messaging API](messaging.md) |
| `MessageDispatcher`, `PayloadHandler`, `ObjectPayloadHandler`, `HandlerRegistrationException`, `MessageChannels` | Classes, delegates | [Messaging API](messaging.md) |
| `AnimatorState`, `InputFrames`, `LocalPeer`, `MessageBundle`, `BundleEntry`, `ObjectSpawn`, `ObjectSceneSpawn`, `ObjectDespawn`, `ObjectOwnerChange`, `PeerLeave`, `ReconcileState`, `ReliableAck`, `SceneLoad`, `SceneLoaded`, `SceneUnload`, `StateDelta`, `StateResync`, `TickPing`, `TickPong`, `TransformUpdate`, `TransformSettle` | The package's system models | [Messaging API](messaging.md#system-models) |
| `BundleFormat`, `BundleReader`, `BundleWriter`, `ObjectHeader`, `SeqHeader`, `OutgoingEntry`, `OutgoingKind`, `OutgoingQueue`, `QueuedMessage`, `EnqueueResult`, `MessageSender`, `ReliableChannel`, `ReliableVerdict`, `SessionProtocol`, `ZeroRuns` | Building blocks | |

## Fomoxa.Unity.Sessions

| Type | Kind | Page |
|---|---|---|
| `ConnectionState`, `ServerState`, `StopReason`, `SendResult` | Enums | [Errors and stop reasons](errors.md) |
| `ConnectionStateArgs`, `ServerConnectionStateArgs`, `SendDroppedArgs`, `ReceiveDroppedArgs`, `HandlerExceptionArgs` | Event arguments | [Events and callbacks](callbacks.md) |
| `SessionLimits`, `ReconnectPolicy` | Settings | [Configuration](configuration.md) |
| `ClientSession`, `ServerSession`, `ClientReconnector`, `SessionInbox`, `SessionOutbox`, `FlushPolicy`, `SendResults` | Building blocks | |

## Fomoxa.Unity.Objects

| Type | Kind | Page |
|---|---|---|
| `ObjectMismatchKind`, `ObjectMismatchArgs`, `ObjectOwnerChangedArgs`, `ObserverAddedArgs`, `SpawnResult` | Enums, event arguments | [Errors](errors.md), [Callbacks](callbacks.md) |
| `ServerObjects`, `ClientObjects`, `ServerScenes`, `ObjectTable`, `ObjectRow`, `SpawnedObject`, `SpawnData`, `SpawnSource`, `IObjectSpawner`, `ISceneHost`, `ObjectProtocol`, `StateProtocol`, `TransformProtocol`, `SceneProtocol`, `SpawnTransform` | Building blocks | [Server console](../server/server-console.md) |

## Fomoxa.Unity.Timing and Fomoxa.Unity.Prediction

| Type | Kind | Page |
|---|---|---|
| `ClientClock`, `InputRejectedArgs`, `ClockEstimator`, `ClockProtocol`, `ClockSettings`, `ServerClock`, `ServerInputs`, `InputProtocol` | Building blocks | [Ticks and timing](../concepts/tick.md) |

## Fomoxa.Unity.Simulation

| Type | Kind | Page |
|---|---|---|
| `PhysicsBody`, `PhysicsBody2D`, `BodyState`, `BodyState2D` | Structs | [Physics API](physics.md) |
| `IPhysicsSimulation`, `IPhysicsWorld`, `IPhysicsWorld2D`, `PhysicsSnapshot`, `PhysicsHistory`, `PhysicsBackend` | Interfaces, classes, enum | [Physics API](physics.md) |
| `BodyHandle`, `BodyKind`, `BodyShape`, `BodyShape2D`, `ShapeKind`, `ShapeKind2D`, `BodyDesc`, `BodyDesc2D`, `RayHit`, `RayHit2D` | Data types | [Physics API](physics.md) |

## Fomoxa.Unity.Transports

| Type | Kind | Page |
|---|---|---|
| `ITransportFactory`, `ITransportConnector`, `ConnectStatus` | Interfaces, enum | [Custom transport](../transports/custom-transport.md) |
| `UdpTransportFactory`, `TcpTransportFactory`, `WebSocketTransportFactory`, `WebSocketSettings`, `MultiTransportFactory` | Factories | [Transports](../transports/overview.md) |
| `LoopbackTransport`, `LoopbackListener`, `CompositeListener` | Transports | [Loopback](../transports/loopback.md) |
| `IHostResolver`, `HostResolver`, `ResolveStatus` | Name resolution | [Transports overview](../transports/overview.md#non-blocking-operation) |

## Fomoxa.Unity.Editor

| Type | Kind | Page |
|---|---|---|
| `FomoxaSettings` | Asset type | [Editor integration](../unity/editor-integration.md) |
| `FomoxaUnityTypes`, `FomoxaUnityField`, `FomoxaUnityType` | Unity type layouts | [Custom codecs](../advanced/custom-codecs.md) |
| `FomoxaHook`, `FomoxaGenerator`, `FomoxaPrefabStep`, `FomoxaSceneStep`, `FomoxaSceneObjectIds`, `FomoxaRpcScanner`, `FomoxaChannelScanner`, `FomoxaPrefabBuild`, `FomoxaRpcBuild` and their data types | Editor steps | [Editor integration](../unity/editor-integration.md) |

## From the bundled DLLs

| Type | Namespace | Page |
|---|---|---|
| `NetworkAttribute`, `CodecAttribute` (`[Network]`, `[Codec]`) | `Fomoxa` | [Models and codecs](../messaging/models.md) |
| `HandshakeFailure`, `SendStatus`, `Schema`, `FomoxaWire` | `Fomoxa.Net` | [Errors](errors.md) |
| `ITransport`, `IListenerTransport`, `SendOutcome`, `ReceiveOutcome`, `AcceptOutcome`, `TransportKind` | `Fomoxa.Net.Transports` | [Custom transport](../transports/custom-transport.md) |
