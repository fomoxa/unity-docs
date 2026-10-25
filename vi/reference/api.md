# Danh mục API

Trang này liệt kê các public type của package theo namespace. Type đánh dấu "building block" là public để tầng 1 có thể được dùng và test riêng, còn type đánh dấu "backend contract" là thứ một backend khác Unity hiện thực hoặc gọi tới. Code game truy cập các tính năng tương ứng qua manager và component, và thường không dùng trực tiếp các type này.

## Fomoxa.Unity (tầng 2, assembly Fomoxa.Unity) <a href="#fomoxaunity-layer-2-assembly-fomoxaunity" id="fomoxaunity-layer-2-assembly-fomoxaunity"></a>

| Type | Loại | Trang |
|---|---|---|
| `NetworkManager` | Component | [Tham chiếu](network-manager.md) |
| `TransportManager` | Class | [Tham chiếu NetworkManager](network-manager.md#transportmanager) |
| `NetworkObject` | Component | [Tham chiếu](network-object.md) |
| `NetworkBehaviour` | Component trừu tượng | [Tham chiếu](network-object.md#networkbehaviour) |
| `NetworkTransform`, `NetworkAnimator` | Component | [Component](components.md) |
| `NetworkCollision`, `NetworkTrigger`, `NetworkCollision2D`, `NetworkTrigger2D`, `IContactQuery`, `IContactQuery2D` | Component, interface | [Component](components.md#contact-components) |
| `ObserverRule`, `DistanceRule`, `ObserverRange` | Type asset, component | [Component](components.md#observers) |
| `NetworkAuthenticator` | Component trừu tượng | [Xác thực](../connections/authentication.md) |
| `PrefabRegistry`, `SceneRegistry`, `ISceneLoader`, `NetworkScenesExtensions` | Class, interface, extension method | [Tham chiếu NetworkManager](network-manager.md#prefabregistry) |
| `NetworkPrefabList`, `NetworkSceneList` | Type asset được sinh | [Tích hợp Editor](../advanced/editor-integration.md) |
| `NetworkTransport`, `UdpNetworkTransport`, `TcpNetworkTransport`, `WebSocketNetworkTransport`, `MultiNetworkTransport` | Component | [Component](components.md#transports) |
| `NetworkPhysics`, `RigidbodyPhysics` | Component | [Physics API](physics.md#physics-components) |
| `UnityPhysicsWorld`, `UnityPhysicsWorld2D`, `BodyDescriptions` | Physics world, helper | [Physics API](physics.md#unity-worlds) |

## Fomoxa.Networking (tầng 1, assembly Fomoxa.Networking) <a href="#fomoxanetworking-layer-1-assembly-fomoxanetworking" id="fomoxanetworking-layer-1-assembly-fomoxanetworking"></a>

| Type | Loại | Trang |
|---|---|---|
| `ServerManager` | Class | [Tham chiếu](server-manager.md) |
| `ClientManager` | Class | [Tham chiếu](client-manager.md) |
| `TimeManager`, `TimingMode` | Class, enum | [Tham chiếu](time-manager.md) |
| `NetworkScenes` | Class | [Tham chiếu ServerManager](server-manager.md#scenes) |
| `NetworkVisibility` | Enum | [Tham chiếu NetworkObject](network-object.md) |
| `NetworkRpcs`, `NetworkState`, `NetworkInput`, `InputContext` | Type đăng ký | [Tham chiếu](network-object.md#registration-types) |
| `ServerRpcAttribute`, `ClientRpcAttribute`, `NetworkRpcAttribute`, `NetworkChannelAttribute`, `MessageAdapterAttribute` | Attribute | [Attribute](attributes.md) |
| `Channel` | Enum | [Channel](../messaging/channels.md) |
| `FomoxaRegistry`, `RpcMessageIds` | Class | [Messaging API](messaging.md) |
| `INetworkEntity` | Interface | Type của các giá trị trong `Spawned`; `NetworkObject` hiện thực nó |
| `IObserverRule`, `ObserverContext`, `DistanceObserverRule` | Interface, class | Rule nằm sau `ObserverRule` và `DistanceRule` |
| `ObserverGroups` | Class | [Tham chiếu ServerManager](server-manager.md#observergroups) |
| `IServerAuthenticator`, `IClientAuthenticator`, `ServerAuthentication`, `ClientAuthentication`, `ServerAuthenticationContext`, `ClientAuthenticationContext` | Interface, class | [Xác thực](../connections/authentication.md) |
| `EntityBehaviour`, `EntityRecord`, `NetworkRuntime`, `NetworkSettings`, `NetworkBackends`, `NetworkLog`, `ITransformSource`, `ITransformReceiver`, `TransformSample`, `TransformSync`, `TransformSyncSettings` | Backend contract | [Tham chiếu backend console](../console-server/reference.md) |

## Fomoxa.Networking.Messaging <a href="#fomoxanetworkingmessaging" id="fomoxanetworkingmessaging"></a>

| Type | Loại | Trang |
|---|---|---|
| `IMessageCodec<T>`, `MessageDecodeException` | Interface, exception | [Messaging API](messaging.md) |
| `MessageDispatcher`, `PayloadHandler`, `ObjectPayloadHandler`, `HandlerRegistrationException`, `MessageChannels` | Class, delegate | [Messaging API](messaging.md) |
| `AnimatorState`, `InputFrames`, `LocalPeer`, `MessageBundle`, `BundleEntry`, `ObjectSpawn`, `ObjectSceneSpawn`, `ObjectDespawn`, `ObjectOwnerChange`, `PeerLeave`, `ReconcileState`, `ReliableAck`, `SceneLoad`, `SceneLoaded`, `SceneUnload`, `StateDelta`, `StateResync`, `TickPing`, `TickPong`, `TransformUpdate`, `TransformSettle` | System model của package | [Messaging API](messaging.md#system-models) |
| `SceneFile`, `SceneFileObject`, `SceneFilePose`, `SceneFileBody`, `SceneFileBody2D`, `SceneFileCollider`, `SceneFileCollider2D`, `SceneFileMaterial` | System model của scene file | [Tích hợp Editor](../advanced/editor-integration.md#scene-files) |
| `BundleFormat`, `BundleReader`, `BundleWriter`, `ObjectHeader`, `SeqHeader`, `OutgoingEntry`, `OutgoingKind`, `OutgoingQueue`, `QueuedMessage`, `EnqueueResult`, `MessageSender`, `ReliableChannel`, `ReliableVerdict`, `SessionProtocol`, `ZeroRuns` | Building block | |

## Fomoxa.Networking.Sessions <a href="#fomoxanetworkingsessions" id="fomoxanetworkingsessions"></a>

| Type | Loại | Trang |
|---|---|---|
| `ConnectionState`, `ServerState`, `StopReason`, `SendResult` | Enum | [Lỗi và lý do dừng](errors.md) |
| `ConnectionStateArgs`, `ServerConnectionStateArgs`, `SendDroppedArgs`, `ReceiveDroppedArgs`, `HandlerExceptionArgs` | Tham số event | [Event và callback](callbacks.md) |
| `SessionLimits`, `ReconnectPolicy` | Thiết lập | [Cấu hình](configuration.md) |
| `ClientSession`, `ServerSession`, `ClientReconnector`, `SessionInbox`, `SessionOutbox`, `FlushPolicy`, `SendResults` | Building block | |

## Fomoxa.Networking.Objects <a href="#fomoxanetworkingobjects" id="fomoxanetworkingobjects"></a>

| Type | Loại | Trang |
|---|---|---|
| `ObjectMismatchKind`, `ObjectMismatchArgs`, `ObjectOwnerChangedArgs`, `ObserverAddedArgs`, `SpawnResult` | Enum, tham số event | [Lỗi](errors.md), [Callback](callbacks.md) |
| `IServerEntityBackend`, `IClientEntityBackend`, `IServerSceneHost`, `ISceneHost`, `SceneFileFormat`, `SceneFileGeometry` | Backend contract | [Tham chiếu backend console](../console-server/reference.md) |
| `ServerObjects`, `ClientObjects`, `ServerScenes`, `ObjectTable`, `ObjectRow`, `SpawnedObject`, `SpawnData`, `SpawnSource`, `IObjectSpawner`, `ObjectProtocol`, `StateProtocol`, `TransformProtocol`, `SceneProtocol`, `SpawnTransform` | Building block | |

## Fomoxa.Networking.Timing và Fomoxa.Networking.Prediction <a href="#fomoxanetworkingtiming-and-fomoxanetworkingprediction" id="fomoxanetworkingtiming-and-fomoxanetworkingprediction"></a>

| Type | Loại | Trang |
|---|---|---|
| `IClientPredictionBackend` | Backend contract | [Tham chiếu backend console](../console-server/reference.md) |
| `ClientClock`, `InputRejectedArgs`, `ClockEstimator`, `ClockProtocol`, `ClockSettings`, `ServerClock`, `ServerInputs`, `InputProtocol` | Building block | [Tick và thời gian](../concepts/tick.md) |

## Fomoxa.Networking.Simulation <a href="#fomoxanetworkingsimulation" id="fomoxanetworkingsimulation"></a>

| Type | Loại | Trang |
|---|---|---|
| `PhysicsBody`, `PhysicsBody2D`, `BodyState`, `BodyState2D` | Struct | [Physics API](physics.md) |
| `IPhysicsSimulation`, `IPhysicsWorld`, `IPhysicsWorld2D`, `PhysicsSnapshot`, `PhysicsHistory`, `PhysicsHistories`, `PhysicsBackend` | Interface, class, enum | [Physics API](physics.md) |
| `BodyHandle`, `BodyKind`, `BodyShape`, `BodyShape2D`, `ShapeKind`, `ShapeKind2D`, `ColliderDesc`, `ColliderDesc2D`, `ColliderMaterial`, `CombineRule`, `BodyDesc`, `BodyDesc2D`, `BodyMotion`, `BodyMotion2D`, `BodyLocks`, `BodyLocks2D`, `StaticGroup`, `RayHit`, `RayHit2D` | Type dữ liệu | [Physics API](physics.md) |
| `IPhysicsWorlds`, `IPhysicsScenes`, `IContactTracker`, `IContactSource<TContact>`, `ContactTracker<TContact>`, `ContactSet<TContact>` | Backend contract | [Physics API](physics.md#backend-contract) |

## Fomoxa.Networking.Transports <a href="#fomoxanetworkingtransports" id="fomoxanetworkingtransports"></a>

| Type | Loại | Trang |
|---|---|---|
| `ITransportFactory`, `ITransportConnector`, `ConnectStatus` | Interface, enum | [Transport tùy chỉnh](../connections/transports/custom-transport.md) |
| `UdpTransportFactory`, `TcpTransportFactory`, `WebSocketTransportFactory`, `WebSocketSettings`, `MultiTransportFactory` | Factory | [Transport](../connections/transports/README.md) |
| `LoopbackTransport`, `LoopbackListener`, `CompositeListener` | Transport | [Loopback](../connections/transports/loopback.md) |
| `IHostResolver`, `HostResolver`, `ResolveStatus` | Phân giải tên | [Tổng quan transport](../connections/transports/README.md#non-blocking-operation) |

## Fomoxa.Unity.Editor <a href="#fomoxaunityeditor" id="fomoxaunityeditor"></a>

| Type | Loại | Trang |
|---|---|---|
| `FomoxaSettings` | Type asset | [Tích hợp Editor](../advanced/editor-integration.md) |
| `FomoxaUnityTypes`, `FomoxaUnityField`, `FomoxaUnityType` | Layout type của Unity | [Codec tùy chỉnh](../advanced/custom-codecs.md) |
| `FomoxaHook`, `FomoxaGenerator`, `FomoxaPrefabStep`, `FomoxaSceneStep`, `FomoxaSceneFileStep`, `FomoxaSceneFileImporter`, `FomoxaSceneObjectIds`, `FomoxaRpcScanner`, `FomoxaChannelScanner`, `FomoxaPrefabBuild`, `FomoxaRpcBuild` and their data types | Các bước Editor | [Tích hợp Editor](../advanced/editor-integration.md) |

## Từ các DLL đi kèm <a href="#from-the-bundled-dlls" id="from-the-bundled-dlls"></a>

| Type | Namespace | Trang |
|---|---|---|
| `NetworkAttribute`, `CodecAttribute` (`[Network]`, `[Codec]`) | `Fomoxa` | [Model và codec](../messaging/models.md) |
| `HandshakeFailure`, `SendStatus`, `Schema`, `FomoxaWire` | `Fomoxa.Net` | [Lỗi](errors.md) |
| `ITransport`, `IListenerTransport`, `SendOutcome`, `ReceiveOutcome`, `AcceptOutcome`, `TransportKind` | `Fomoxa.Net.Transports` | [Transport tùy chỉnh](../connections/transports/custom-transport.md) |
