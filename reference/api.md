# API index

This page lists the public types of the package by namespace. Types marked "building block" are public so that layer 1 can be used and tested on its own, and types marked "backend contract" are what a backend other than Unity implements or calls. Game code reaches the same features through the managers and components and normally does not use these types directly.

## Fomoxa.Unity (layer 2, assembly Fomoxa.Unity)

| Type | Kind | Page |
|---|---|---|
| `NetworkManager` | Component | [Reference](network-manager.md) |
| `TransportManager` | Class | [NetworkManager reference](network-manager.md#transportmanager) |
| `NetworkObject` | Component | [Reference](network-object.md) |
| `NetworkBehaviour` | Abstract component | [Reference](network-object.md#networkbehaviour) |
| `NetworkTransform`, `NetworkAnimator` | Components | [Components](components.md) |
| `NetworkCollision`, `NetworkTrigger`, `NetworkCollision2D`, `NetworkTrigger2D`, `IContactQuery`, `IContactQuery2D` | Components, interfaces | [Components](components.md#contact-components) |
| `ObserverRule`, `DistanceRule`, `ObserverRange` | Asset types, component | [Components](components.md#observers) |
| `NetworkAuthenticator` | Abstract component | [Authentication](../connections/authentication.md) |
| `PrefabRegistry`, `SceneRegistry`, `ISceneLoader`, `NetworkScenesExtensions` | Classes, interface, extension methods | [NetworkManager reference](network-manager.md#prefabregistry) |
| `NetworkPrefabList`, `NetworkSceneList` | Generated asset types | [Editor integration](../advanced/editor-integration.md) |
| `NetworkTransport`, `UdpNetworkTransport`, `TcpNetworkTransport`, `WebSocketNetworkTransport`, `MultiNetworkTransport` | Components | [Components](components.md#transports) |
| `NetworkPhysics`, `RigidbodyPhysics` | Components | [Physics API](physics.md#physics-components) |
| `UnityPhysicsWorld`, `UnityPhysicsWorld2D`, `BodyDescriptions` | Physics worlds, helper | [Physics API](physics.md#unity-worlds) |

## Fomoxa.Networking (layer 1, assembly Fomoxa.Networking)

| Type | Kind | Page |
|---|---|---|
| `ServerManager` | Class | [Reference](server-manager.md) |
| `ClientManager` | Class | [Reference](client-manager.md) |
| `TimeManager`, `TimingMode` | Class, enum | [Reference](time-manager.md) |
| `NetworkScenes` | Class | [ServerManager reference](server-manager.md#scenes) |
| `NetworkVisibility` | Enum | [NetworkObject reference](network-object.md) |
| `NetworkRpcs`, `NetworkState`, `NetworkInput`, `InputContext` | Registration types | [Reference](network-object.md#registration-types) |
| `NetworkList<T>`, `NetworkDictionary<TKey, TValue>`, `NetworkSet<T>`, `NetworkCollections`, `NetworkListOperation`, `NetworkDictionaryOperation`, `NetworkSetOperation`, `NetworkListChanged<T>`, `NetworkDictionaryChanged<TKey, TValue>`, `NetworkSetChanged<T>` | Collection types | [Collections](../synchronization/collections.md) |
| `ServerRpcAttribute`, `ClientRpcAttribute`, `NetworkRpcAttribute`, `NetworkChannelAttribute`, `MessageAdapterAttribute` | Attributes | [Attributes](attributes.md) |
| `Channel` | Enum | [Channels](../messaging/channels.md) |
| `FomoxaRegistry`, `RpcMessageIds` | Classes | [Messaging API](messaging.md) |
| `INetworkEntity` | Interface | The type of the values of `Spawned`; `NetworkObject` implements it |
| `IObserverRule`, `ObserverContext`, `DistanceObserverRule` | Interface, classes | The rule behind `ObserverRule` and `DistanceRule` |
| `ObserverGroups` | Class | [ServerManager reference](server-manager.md#observergroups) |
| `IServerAuthenticator`, `IClientAuthenticator`, `ServerAuthentication`, `ClientAuthentication`, `ServerAuthenticationContext`, `ClientAuthenticationContext` | Interfaces, classes | [Authentication](../connections/authentication.md) |
| `EntityBehaviour`, `EntityRecord`, `NetworkRuntime`, `NetworkSettings`, `NetworkBackends`, `NetworkLog`, `ITransformSource`, `ITransformReceiver`, `TransformSample`, `TransformSync`, `TransformSyncSettings` | Backend contract | [Console backend reference](../console-server/reference.md) |

## Fomoxa.Networking.Messaging

| Type | Kind | Page |
|---|---|---|
| `IMessageCodec<T>`, `MessageDecodeException` | Interface, exception | [Messaging API](messaging.md) |
| `MessageDispatcher`, `PayloadHandler`, `ObjectPayloadHandler`, `HandlerRegistrationException`, `MessageChannels` | Classes, delegates | [Messaging API](messaging.md) |
| `AnimatorState`, `InputFrames`, `LocalPeer`, `MessageBundle`, `BundleEntry`, `ObjectSpawn`, `ObjectSceneSpawn`, `ObjectDespawn`, `ObjectOwnerChange`, `PeerLeave`, `ReconcileState`, `ReliableAck`, `SceneLoad`, `SceneLoaded`, `SceneUnload`, `StateDelta`, `StateResync`, `TickPing`, `TickPong`, `TransformUpdate`, `TransformSettle`, `CollectionChanges`, `CollectionContent`, `CollectionContents`, `CollectionResync` | The package's system models | [Messaging API](messaging.md#system-models) |
| `BoolValue`, `I8Value`, `U8Value`, `I16Value`, `U16Value`, `I32Value`, `U32Value`, `I64Value`, `U64Value`, `F32Value`, `F64Value`, `StringValue` | One-field system models that carry primitive collection elements | [Messaging API](messaging.md#system-models) |
| `SceneFile`, `SceneFileObject`, `SceneFilePose`, `SceneFileBody`, `SceneFileBody2D`, `SceneFileCollider`, `SceneFileCollider2D`, `SceneFileMaterial` | System models of the scene file | [Editor integration](../advanced/editor-integration.md#scene-files) |
| `BundleFormat`, `BundleReader`, `BundleWriter`, `ObjectHeader`, `SeqHeader`, `OutgoingEntry`, `OutgoingKind`, `OutgoingQueue`, `QueuedMessage`, `EnqueueResult`, `MessageSender`, `ReliableChannel`, `ReliableVerdict`, `SessionProtocol`, `ZeroRuns` | Building blocks | |

## Fomoxa.Networking.Sessions

| Type | Kind | Page |
|---|---|---|
| `ConnectionState`, `ServerState`, `StopReason`, `SendResult` | Enums | [Errors and stop reasons](errors.md) |
| `ConnectionStateArgs`, `ServerConnectionStateArgs`, `SendDroppedArgs`, `ReceiveDroppedArgs`, `HandlerExceptionArgs` | Event arguments | [Events and callbacks](callbacks.md) |
| `SessionLimits`, `ReconnectPolicy` | Settings | [Configuration](configuration.md) |
| `ClientSession`, `ServerSession`, `ClientReconnector`, `SessionInbox`, `SessionOutbox`, `FlushPolicy`, `SendResults` | Building blocks | |

## Fomoxa.Networking.Objects

| Type | Kind | Page |
|---|---|---|
| `ObjectMismatchKind`, `ObjectMismatchArgs`, `ObjectOwnerChangedArgs`, `ObserverAddedArgs`, `SpawnResult` | Enums, event arguments | [Errors](errors.md), [Callbacks](callbacks.md) |
| `IServerEntityBackend`, `IClientEntityBackend`, `IServerSceneHost`, `ISceneHost`, `SceneFileFormat`, `SceneFileGeometry` | Backend contract | [Console backend reference](../console-server/reference.md) |
| `ServerObjects`, `ClientObjects`, `ServerScenes`, `ObjectTable`, `ObjectRow`, `SpawnedObject`, `SpawnData`, `SpawnSource`, `IObjectSpawner`, `ObjectProtocol`, `StateProtocol`, `CollectionProtocol`, `TransformProtocol`, `SceneProtocol`, `SpawnTransform` | Building blocks | |

## Fomoxa.Networking.Timing and Fomoxa.Networking.Prediction

| Type | Kind | Page |
|---|---|---|
| `IClientPredictionBackend` | Backend contract | [Console backend reference](../console-server/reference.md) |
| `ClientClock`, `InputRejectedArgs`, `ClockEstimator`, `ClockProtocol`, `ClockSettings`, `ServerClock`, `ServerInputs`, `InputProtocol` | Building blocks | [Ticks and timing](../concepts/tick.md) |

## Fomoxa.Networking.Simulation

| Type | Kind | Page |
|---|---|---|
| `PhysicsBody`, `PhysicsBody2D`, `BodyState`, `BodyState2D` | Structs | [Physics API](physics.md) |
| `IPhysicsSimulation`, `IPhysicsWorld`, `IPhysicsWorld2D`, `PhysicsSnapshot`, `PhysicsHistory`, `PhysicsHistories`, `PhysicsBackend` | Interfaces, classes, enum | [Physics API](physics.md) |
| `BodyHandle`, `BodyKind`, `BodyShape`, `BodyShape2D`, `ShapeKind`, `ShapeKind2D`, `ColliderDesc`, `ColliderDesc2D`, `ColliderMaterial`, `CombineRule`, `BodyDesc`, `BodyDesc2D`, `BodyMotion`, `BodyMotion2D`, `BodyLocks`, `BodyLocks2D`, `StaticGroup`, `RayHit`, `RayHit2D` | Data types | [Physics API](physics.md) |
| `IPhysicsWorlds`, `IPhysicsScenes`, `IContactTracker`, `IContactSource<TContact>`, `ContactTracker<TContact>`, `ContactSet<TContact>` | Backend contract | [Physics API](physics.md#backend-contract) |

## Fomoxa.Networking.Transports

| Type | Kind | Page |
|---|---|---|
| `ITransportFactory`, `ITransportConnector`, `ConnectStatus` | Interfaces, enum | [Custom transport](../connections/transports/custom-transport.md) |
| `UdpTransportFactory`, `TcpTransportFactory`, `WebSocketTransportFactory`, `WebSocketSettings`, `MultiTransportFactory` | Factories | [Transports](../connections/transports/README.md) |
| `LoopbackTransport`, `LoopbackListener`, `CompositeListener` | Transports | [Loopback](../connections/transports/loopback.md) |
| `IHostResolver`, `HostResolver`, `ResolveStatus` | Name resolution | [Transports overview](../connections/transports/README.md#non-blocking-operation) |

## Fomoxa.Unity.Editor

| Type | Kind | Page |
|---|---|---|
| `FomoxaSettings` | Asset type | [Editor integration](../advanced/editor-integration.md) |
| `FomoxaUnityTypes`, `FomoxaUnityField`, `FomoxaUnityType` | Unity type layouts | [Custom codecs](../advanced/custom-codecs.md) |
| `FomoxaHook`, `FomoxaGenerator`, `FomoxaPrefabStep`, `FomoxaSceneStep`, `FomoxaSceneFileStep`, `FomoxaSceneFileImporter`, `FomoxaSceneObjectIds`, `FomoxaRpcScanner`, `FomoxaChannelScanner`, `FomoxaPrefabBuild`, `FomoxaRpcBuild` and their data types | Editor steps | [Editor integration](../advanced/editor-integration.md) |

## From the bundled DLLs

| Type | Namespace | Page |
|---|---|---|
| `NetworkAttribute`, `CodecAttribute` (`[Network]`, `[Codec]`) | `Fomoxa` | [Models and codecs](../messaging/models.md) |
| `HandshakeFailure`, `SendStatus`, `Schema`, `FomoxaWire` | `Fomoxa.Net` | [Errors](errors.md) |
| `ITransport`, `IListenerTransport`, `SendOutcome`, `ReceiveOutcome`, `AcceptOutcome`, `TransportKind` | `Fomoxa.Net.Transports` | [Custom transport](../connections/transports/custom-transport.md) |
