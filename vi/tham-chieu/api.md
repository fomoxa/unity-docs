# Danh mục API

Trang này liệt kê các public type của package theo namespace. Type đánh dấu "building block" là public để tầng 1 có thể được dùng và test riêng. Code game truy cập các tính năng tương ứng qua manager và component, và thường không dùng trực tiếp các type này.

## Fomoxa.Unity (tầng 2, assembly Fomoxa.Unity) <a href="#fomoxaunity-layer-2-assembly-fomoxaunity" id="fomoxaunity-layer-2-assembly-fomoxaunity"></a>

| Type                                                                                                                   | Loại                  | Trang                                                            |
| ---------------------------------------------------------------------------------------------------------------------- | --------------------- | ---------------------------------------------------------------- |
| `NetworkManager`                                                                                                       | Component             | [Tham chiếu](network-manager.md)                                 |
| `ServerManager`                                                                                                        | Class                 | [Tham chiếu](server-manager.md)                                  |
| `ClientManager`                                                                                                        | Class                 | [Tham chiếu](client-manager.md)                                  |
| `TimeManager`, `TimingMode`                                                                                            | Class, enum           | [Tham chiếu](time-manager.md)                                    |
| `TransportManager`                                                                                                     | Class                 | [Tham chiếu NetworkManager](network-manager.md#transportmanager) |
| `NetworkObject`, `NetworkVisibility`                                                                                   | Component, enum       | [Tham chiếu](network-object.md)                                  |
| `NetworkBehaviour`                                                                                                     | Component trừu tượng  | [Tham chiếu](network-object.md#networkbehaviour)                 |
| `NetworkRpcs`, `NetworkState`, `NetworkInput`, `InputContext`                                                          | Type đăng ký          | [Tham chiếu](network-object.md#registration-types)               |
| `NetworkTransform`, `NetworkAnimator`                                                                                  | Component             | [Component](components.md)                                       |
| `NetworkCollision`, `NetworkTrigger`, `NetworkCollision2D`, `NetworkTrigger2D`                                         | Component             | [Component](components.md#contact-components)                    |
| `ObserverRule`, `DistanceRule`, `ObserverRange`                                                                        | Type asset, component | [Component](components.md#observers)                             |
| `PrefabRegistry`, `SceneRegistry`, `ISceneLoader`, `NetworkScenes`                                                     | Class, interface      | [Tham chiếu ServerManager](server-manager.md#scenes)             |
| `NetworkPrefabList`, `NetworkSceneList`                                                                                | Type asset được sinh  | [Tích hợp Editor](../unity/editor-integration.md)                |
| `NetworkTransport`, `UdpNetworkTransport`, `TcpNetworkTransport`, `WebSocketNetworkTransport`, `MultiNetworkTransport` | Component             | [Component](components.md#transports)                            |
| `UnityPhysicsWorld`, `UnityPhysicsWorld2D`                                                                             | Physics backend       | [Physics API](physics.md#unity-backend)                          |

## Fomoxa.Unity (tầng 1, assembly Fomoxa.Unity.Core) <a href="#fomoxaunity-layer-1-assembly-fomoxaunitycore" id="fomoxaunity-layer-1-assembly-fomoxaunitycore"></a>

| Type                                                                                                                    | Loại      | Trang                               |
| ----------------------------------------------------------------------------------------------------------------------- | --------- | ----------------------------------- |
| `ServerRpcAttribute`, `ClientRpcAttribute`, `NetworkRpcAttribute`, `NetworkChannelAttribute`, `MessageAdapterAttribute` | Attribute | [Attribute](attributes.md)          |
| `Channel`                                                                                                               | Enum      | [Channel](../messaging/channels.md) |
| `FomoxaRegistry`, `RpcMessageIds`                                                                                       | Class     | [Messaging API](messaging.md)       |

## Fomoxa.Unity.Messaging <a href="#fomoxaunitymessaging" id="fomoxaunitymessaging"></a>

| Type                                                                                                                                                                                                                                                                                                                                     | Loại                     | Trang                                       |
| ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------ | ------------------------------------------- |
| `IMessageCodec<T>`, `MessageDecodeException`                                                                                                                                                                                                                                                                                             | Interface, exception     | [Messaging API](messaging.md)               |
| `MessageDispatcher`, `PayloadHandler`, `ObjectPayloadHandler`, `HandlerRegistrationException`, `MessageChannels`                                                                                                                                                                                                                         | Class, delegate          | [Messaging API](messaging.md)               |
| `AnimatorState`, `InputFrames`, `LocalPeer`, `MessageBundle`, `BundleEntry`, `ObjectSpawn`, `ObjectSceneSpawn`, `ObjectDespawn`, `ObjectOwnerChange`, `PeerLeave`, `ReconcileState`, `ReliableAck`, `SceneLoad`, `SceneLoaded`, `SceneUnload`, `StateDelta`, `StateResync`, `TickPing`, `TickPong`, `TransformUpdate`, `TransformSettle` | System model của package | [Messaging API](messaging.md#system-models) |
| `BundleFormat`, `BundleReader`, `BundleWriter`, `ObjectHeader`, `SeqHeader`, `OutgoingEntry`, `OutgoingKind`, `OutgoingQueue`, `QueuedMessage`, `EnqueueResult`, `MessageSender`, `ReliableChannel`, `ReliableVerdict`, `SessionProtocol`, `ZeroRuns`                                                                                    | Building block           |                                             |

## Fomoxa.Unity.Sessions <a href="#fomoxaunitysessions" id="fomoxaunitysessions"></a>

| Type                                                                                                                 | Loại           | Trang                             |
| -------------------------------------------------------------------------------------------------------------------- | -------------- | --------------------------------- |
| `ConnectionState`, `ServerState`, `StopReason`, `SendResult`                                                         | Enum           | [Lỗi và lý do dừng](errors.md)    |
| `ConnectionStateArgs`, `ServerConnectionStateArgs`, `SendDroppedArgs`, `ReceiveDroppedArgs`, `HandlerExceptionArgs`  | Tham số event  | [Event và callback](callbacks.md) |
| `SessionLimits`, `ReconnectPolicy`                                                                                   | Thiết lập      | [Cấu hình](configuration.md)      |
| `ClientSession`, `ServerSession`, `ClientReconnector`, `SessionInbox`, `SessionOutbox`, `FlushPolicy`, `SendResults` | Building block |                                   |

## Fomoxa.Unity.Objects <a href="#fomoxaunityobjects" id="fomoxaunityobjects"></a>

| Type                                                                                                                                                                                                                                                 | Loại                | Trang                                         |
| ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------- | --------------------------------------------- |
| `ObjectMismatchKind`, `ObjectMismatchArgs`, `ObjectOwnerChangedArgs`, `ObserverAddedArgs`, `SpawnResult`                                                                                                                                             | Enum, tham số event | [Lỗi](errors.md), [Callback](callbacks.md)    |
| `ServerObjects`, `ClientObjects`, `ServerScenes`, `ObjectTable`, `ObjectRow`, `SpawnedObject`, `SpawnData`, `SpawnSource`, `IObjectSpawner`, `ISceneHost`, `ObjectProtocol`, `StateProtocol`, `TransformProtocol`, `SceneProtocol`, `SpawnTransform` | Building block      | [Server console](../server/server-console.md) |

## Fomoxa.Unity.Timing và Fomoxa.Unity.Prediction <a href="#fomoxaunitytiming-and-fomoxaunityprediction" id="fomoxaunitytiming-and-fomoxaunityprediction"></a>

| Type                                                                                                                                   | Loại           | Trang                                     |
| -------------------------------------------------------------------------------------------------------------------------------------- | -------------- | ----------------------------------------- |
| `ClientClock`, `InputRejectedArgs`, `ClockEstimator`, `ClockProtocol`, `ClockSettings`, `ServerClock`, `ServerInputs`, `InputProtocol` | Building block | [Tick và thời gian](../khai-niem/tick.md) |

## Fomoxa.Unity.Simulation <a href="#fomoxaunitysimulation" id="fomoxaunitysimulation"></a>

| Type                                                                                                                             | Loại                   | Trang                     |
| -------------------------------------------------------------------------------------------------------------------------------- | ---------------------- | ------------------------- |
| `PhysicsBody`, `PhysicsBody2D`, `BodyState`, `BodyState2D`                                                                       | Struct                 | [Physics API](physics.md) |
| `IPhysicsSimulation`, `IPhysicsWorld`, `IPhysicsWorld2D`, `PhysicsSnapshot`, `PhysicsHistory`, `PhysicsBackend`                  | Interface, class, enum | [Physics API](physics.md) |
| `BodyHandle`, `BodyKind`, `BodyShape`, `BodyShape2D`, `ShapeKind`, `ShapeKind2D`, `BodyDesc`, `BodyDesc2D`, `RayHit`, `RayHit2D` | Type dữ liệu           | [Physics API](physics.md) |

## Fomoxa.Unity.Transports <a href="#fomoxaunitytransports" id="fomoxaunitytransports"></a>

| Type                                                                                                                    | Loại            | Trang                                                                  |
| ----------------------------------------------------------------------------------------------------------------------- | --------------- | ---------------------------------------------------------------------- |
| `ITransportFactory`, `ITransportConnector`, `ConnectStatus`                                                             | Interface, enum | [Transport tùy chỉnh](../transport/custom-transport.md)                |
| `UdpTransportFactory`, `TcpTransportFactory`, `WebSocketTransportFactory`, `WebSocketSettings`, `MultiTransportFactory` | Factory         | [Transport](../transport/overview.md)                                  |
| `LoopbackTransport`, `LoopbackListener`, `CompositeListener`                                                            | Transport       | [Loopback](../transport/loopback.md)                                   |
| `IHostResolver`, `HostResolver`, `ResolveStatus`                                                                        | Phân giải tên   | [Tổng quan transport](../transport/overview.md#non-blocking-operation) |

## Fomoxa.Unity.Editor <a href="#fomoxaunityeditor" id="fomoxaunityeditor"></a>

| Type                                                                                                                                                                                                            | Loại                  | Trang                                             |
| --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------- | ------------------------------------------------- |
| `FomoxaSettings`                                                                                                                                                                                                | Type asset            | [Tích hợp Editor](../unity/editor-integration.md) |
| `FomoxaUnityTypes`, `FomoxaUnityField`, `FomoxaUnityType`                                                                                                                                                       | Layout type của Unity | [Codec tùy chỉnh](../nang-cao/custom-codecs.md)   |
| `FomoxaHook`, `FomoxaGenerator`, `FomoxaPrefabStep`, `FomoxaSceneStep`, `FomoxaSceneObjectIds`, `FomoxaRpcScanner`, `FomoxaChannelScanner`, `FomoxaPrefabBuild`, `FomoxaRpcBuild` và các type dữ liệu của chúng | Các bước Editor       | [Tích hợp Editor](../unity/editor-integration.md) |

## Từ các DLL đi kèm <a href="#from-the-bundled-dlls" id="from-the-bundled-dlls"></a>

| Type                                                                                                  | Namespace               | Trang                                                   |
| ----------------------------------------------------------------------------------------------------- | ----------------------- | ------------------------------------------------------- |
| `NetworkAttribute`, `CodecAttribute` (`[Network]`, `[Codec]`)                                         | `Fomoxa`                | [Model và codec](../messaging/models.md)                |
| `HandshakeFailure`, `SendStatus`, `Schema`, `FomoxaWire`                                              | `Fomoxa.Net`            | [Lỗi](errors.md)                                        |
| `ITransport`, `IListenerTransport`, `SendOutcome`, `ReceiveOutcome`, `AcceptOutcome`, `TransportKind` | `Fomoxa.Net.Transports` | [Transport tùy chỉnh](../transport/custom-transport.md) |
