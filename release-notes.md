# Release notes

## 0.6.0

This release ships these parts together:

| Part | Version | Install |
|---|---|---|
| `com.fomoxa.networking` | 0.6.0 | `https://github.com/fomoxa/com.fomoxa.networking.git#0.6.0` |
| `com.fomoxa.rpc` | 0.1.9; needs `com.fomoxa.networking` 0.6.0 | `https://github.com/fomoxa/com.fomoxa.rpc.git#0.1.9` |
| `com.fomoxa.networking.rapier` | 0.4.0; needs `com.fomoxa.networking` 0.6.0 | `https://github.com/fomoxa/networking-rapier.git?path=com.fomoxa.networking.rapier#0.4.0` |
| `com.fomoxa.networking.steam` | 0.1.4; needs `com.fomoxa.networking` 0.6.0 and Steamworks.NET 2025.165.0 or later | `https://github.com/fomoxa/com.fomoxa.networking.steam.git#0.1.4` |

`Fomoxa.Backend.Templates` 0.1.1 and the directory and gateway at tag `0.2.0` have no new version.

### Upgrading from 0.5.0

Update `com.fomoxa.rpc` to 0.1.9, `com.fomoxa.networking.rapier` to 0.4.0 and `com.fomoxa.networking.steam` to 0.1.4 together with the package. With the 0.6.0 package, `com.fomoxa.rpc` 0.1.8 reports an error when it generates code, Rapier 0.3.0 does not compile, and Steam 0.1.3 throws a version error when the `NetworkManager` creates the transport.

Three of the package's own messages changed: `SceneLoad` names scene instances, and `ObjectSpawn` and `ObjectSceneSpawn` carry the instance an object is in. A new message, `ObjectSceneMove`, moves an object between instances, and transforms of moving objects now travel in a new message, `TransformFrame`, which replaces `TransformUpdate`. The fields of `SceneLoad` no longer match those of 0.5.0, so a 0.5.0 build and a 0.6.0 build refuse each other with `HandshakeFailure.SchemaConflict`. Update the server and every client build at the same time. The first code generation after the update rewrites the generated code of these messages and removes the files of `TransformUpdate`; commit it and build your console servers from it.

Unity in batch mode stops before that generation, because the generated code of 0.5.0 no longer compiles and batch mode exits on compiler errors. If your project is only ever built in batch mode, open it in the Editor once, or run the generation twice:

```
Unity -batchmode -nographics -ignorecompilererrors -quit -projectPath <project> -executeMethod Fomoxa.Unity.Editor.FomoxaHook.GenerateFromMenu
Unity -batchmode -nographics -quit -projectPath <project> -executeMethod Fomoxa.Unity.Editor.FomoxaHook.GenerateFromMenu
```

The first run exits with code 0 although the compilation failed. Your scripts did not compile, so it cannot see your behaviours: it reports the models that come from your scripts as `BREAKING: message removed` and deletes their generated code. The second run compiles cleanly, writes those models back and reports them as `COMPATIBLE: new message`. Commit the result of the second run. The second run creates the generated files of those models again, so their `.meta` files have new GUIDs. Generated code contains no components, so no scene or prefab refers to those GUIDs.

The server can now hold several instances of one scene asset, and every scene call except loading names an instance, a `NetworkScene`, see [instances](objects/scenes.md#instances). Scene ids still name the asset, and the load calls still take them. Replace the scene calls as follows:

| 0.5.0 | 0.6.0 |
|---|---|
| `ServerManager.Scenes.LoadGlobal(sceneIds)`, which returned nothing | The same call, which returns the `NetworkScene` of each instance |
| `UnloadGlobal(sceneIds)` | `UnloadGlobal(scenes)`, with the instances that `LoadGlobal` returned |
| `LoadForPeers(sceneId, peerIds)`, which added peers to a scene that was already loaded | `Load(sceneId, peerIds)`, which creates a new instance every time and returns it. `AddPeers(scene, peerIds)` gives an existing instance to more peers |
| `UnloadForPeers(sceneId, peerIds)` | `RemovePeers(scene, peerIds)` |
| `Unload(sceneId)` | `Unload(scene)` |
| `Global`, `Contains`, `IsGlobal`, `HasLoaded`, `PeersOf`, `OnLoaded` and `OnLoadFailed` with scene ids | The same members with `NetworkScene`. `SceneIdOf(scene)` returns the scene id of an instance, and `InstancesOf(sceneId)` the instances of an asset |
| `ServerManager.Scenes.TryGetScene(sceneId, out Scene scene)` | `TryGetScene(networkScene, out Scene scene)`, on `ServerManager.Scenes` and on the new `ClientManager.Scenes` |
| `ISceneLoader.Load(loaded, failed)` | `Load(SceneLoadRequest request, Action<float> progress, Action<Scene> loaded, Action<Exception> failed)`. Load with `request.Physics` and pass `loaded` the `Scene` of this load, see [custom loaders](objects/scenes.md#custom-loaders) |
| `ObjectMismatchArgs.SceneId` | `ObjectMismatchArgs.Scene` |
| Console server: `StandaloneEntity.SceneId` | `StandaloneEntity.Scene` |

Every instance is loaded with `ScenePhysics.Shared` unless you pass `ScenePhysics.Own`, and a scene asset can have only one `Shared` instance at a time, so a second `Shared` instance of the same asset throws `ArgumentException`. Load rooms of one map with `Own`, see [physics of an instance](objects/scenes.md#physics-of-an-instance).

Code that implements the package's contracts itself changes as well. A scene host takes the `NetworkScene`, its `ScenePhysics` and a progress callback in `TryLoad`, and the `NetworkScene` in `Unload`. `IServerEntityBackend.SceneIdOf` became `SceneOf`, which returns a `NetworkScene`, and `IServerEntityBackend` and `IClientEntityBackend` have a new `MoveToScene`. A physics backend implements `IPhysicsScenes` with `NetworkScene` arguments (`LoadScene(scene, file)`, `UnloadScene(scene)`, `AddStatic`, `AddBody`) and the new abstract `NetworkPhysics.MoveBodies`. With Rapier, `RapierScenes.WorldOf` and `WorldOf2D` take a `NetworkScene`; `TryGetNetworkScene(gameObject.scene, out NetworkScene scene)` on `ServerManager.Scenes` or `ClientManager.Scenes` finds it from a Unity scene.

### Added

- Several instances of one scene asset at the same time, for example one per match, each reaching only the peers that loaded it. See [network scenes](objects/scenes.md#instances).
- `ScenePhysics.Own` gives an instance its own 3D and 2D physics worlds, so rooms of one map do not collide. The Rapier backend gives every instance its own Rapier worlds. See [physics of an instance](objects/scenes.md#physics-of-an-instance).
- `ServerManager.MoveToScene` moves a spawned object to another instance, and its behaviours get `OnSceneChangedServer` and `OnSceneChangedClient`. See [moving an object to another instance](objects/scenes.md#move-an-object-to-another-instance).
- `ClientManager.Scenes` with load events and `OnLoadProgress`, `TryGetNetworkScene` on both sides, and the server events `OnUnloaded` and `OnPeerLoaded`. See [server events and queries](objects/scenes.md#server-events-and-queries).
- [Multiple rooms on one server](deploy/multiple-rooms.md) builds a lobby and rooms on one headless server and shows how to measure what a room costs.

### Bandwidth

- A `NetworkTransform` sends the updates of one tick to a client in one message and rounds them: position and scale to 0.01 units, rotation to within about 0.2 degrees. An axis beyond ±327.67 is sent as an exact `float`, and the settle message keeps exact values. An update with position and rotation takes 17 bytes instead of 51 when the position is within that range. See [how it works](synchronization/transform.md#how-it-works).

### Fixed

- The package lists `com.unity.modules.imgui` among its dependencies. `NetworkStatsDisplay` uses IMGUI, and a project without that module could not compile the package.

## 0.5.0

This release ships these parts together:

| Part | Version | Install |
|---|---|---|
| `com.fomoxa.networking` | 0.5.0 | `https://github.com/fomoxa/com.fomoxa.networking.git#0.5.0` |
| `com.fomoxa.rpc` | 0.1.8; needs `com.fomoxa.networking` 0.5.0 | `https://github.com/fomoxa/com.fomoxa.rpc.git#0.1.8` |
| `com.fomoxa.networking.rapier` | 0.3.0; needs `com.fomoxa.networking` 0.5.0 | `https://github.com/fomoxa/networking-rapier.git?path=com.fomoxa.networking.rapier#0.3.0` |
| `com.fomoxa.networking.steam` | 0.1.3; needs `com.fomoxa.networking` 0.5.0 and Steamworks.NET 2025.165.0 or later | `https://github.com/fomoxa/com.fomoxa.networking.steam.git#0.1.3` |

`Fomoxa.Backend.Templates` 0.1.1 and the directory and gateway at tag `0.2.0` have no new version.

### Upgrading from 0.4.0

Update `com.fomoxa.rpc` to 0.1.8, `com.fomoxa.networking.rapier` to 0.3.0 and `com.fomoxa.networking.steam` to 0.1.3 together with the package. With the 0.5.0 package, `com.fomoxa.rpc` 0.1.7 reports an error when it generates code, Rapier 0.2.6 does not compile, and Steam 0.1.2 throws a version error when the `NetworkManager` creates the transport.

The package has a new message of its own, `TransformAuthority`. The handshake accepts a message that only one side knows, so 0.4.0 and 0.5.0 builds of a game whose own models did not change still connect to each other. Owner Authority needs 0.5.0 on both sides. The first code generation after the update adds the new message to `FomoxaAdapters.cs`, adds `MessageModels` to the `src` list of `fomoxa.toml` and creates the `MessageModels` folder in the Generated Folder, with a `.gitkeep` file. Commit these files and build your console servers from them. A console server built with the old generated code stops as it starts, with `no TransformAuthority codec is registered`.

Game code in Unity now handles physics with UnityEngine types. `NetworkObject.Body` and the related properties return new types, so code that uses them with `System.Numerics` vectors no longer compiles. Replace it as follows:

| 0.4.0 | 0.5.0 |
|---|---|
| `NetworkObject.Body` and `Body2D`, of type `PhysicsBody` and `PhysicsBody2D` | [`NetworkBody` and `NetworkBody2D`](physics/physics-body.md), with `Vector3`, `Quaternion` and `Vector2` |
| `NetworkObject.Bodies` and `Bodies2D`, lists of `PhysicsBody` and `PhysicsBody2D` | Lists of `NetworkBody` and `NetworkBody2D` |
| `BodyState` and `BodyState2D` from `body.State` | `NetworkBodyState` and `NetworkBodyState2D` |
| `Raycast`, `ShapeCast` and `Overlap` with `System.Numerics` values, returning `RayHit` and `RayHit2D` | The same calls with Unity values, returning `NetworkRayHit` and `NetworkRayHit2D`, see [physics queries](physics/queries.md) |
| `BodyShape.Box` and `BodyShape2D.Box` with a `System.Numerics` vector | `NetworkShapes.Box` and `NetworkShapes.Box2D` |
| Rapier: `MoveCharacter`, `CreateJoint` and `AddEffector` with a `PhysicsBody` or `PhysicsBody2D` | The same calls with a `NetworkBody` or `NetworkBody2D` and Unity vectors, see [character controller](rapier/character-controller.md) and [effectors](rapier/effectors.md) |
| Rapier: the `JointDesc` constructor, `JointDesc.Rope` and `JointDesc.Spring` with `System.Numerics` values | `NetworkJoints.Create`, `Rope` and `Spring`, and `Create2D`, `Rope2D` and `Spring2D`, see [joints](rapier/joints.md) |

`body.Core` returns the `PhysicsBody` inside a `NetworkBody` for code that you share with a console server, and `new NetworkBody(physicsBody)` goes the other way. The methods of `IPhysicsWorld` and `IPhysicsWorld2D` keep their `System.Numerics` types, and so does a console server.

A physics backend written outside the package has new members to implement: `SetKind` on `IPhysicsWorld` and `IPhysicsWorld2D`, and `BodyOf(Transform)` and `Body2DOf(Transform)` on `NetworkPhysics`. Code that constructs a `TransformProtocol` itself passes the codec of `TransformAuthority` as the new `authorityCodec` argument; `TransformProtocol.From(registry)` did not change.

Authenticators that register hand-written models, like the `JoinRequest` of the earlier authentication page, keep working, because `server.On` and `context.Send` did not change. Declaring their messages as methods, described below, is optional.

### Added

- A `NetworkTransform` with Owner Authority turned on takes its pose from the owner's client. The server interpolates the owner's samples, writes them into the object and forwards them to the other clients, and `OwnerSampleFilter` lets it reject a sample, for example one that moves too far. See [letting the owner decide](synchronization/transform.md#letting-the-owner-decide). An object whose behaviours predict cannot use it.
- [Raw messages](messaging/messages.md) can be declared as `[ServerMessage]` and `[ClientMessage]` methods of a `NetworkMessageBehaviour`, and the generator writes their send methods. Without the component, `ClientManager.Send<T>`, `ServerManager.Send<T>` and `ServerManager.Broadcast<T>` send a model with its codec, `MessageDispatcher.Register<T>` hands the handler a decoded model, and `MessageDispatcher.Unregister` removes a handler.
- An authenticator declares its messages the same way, with [`[ServerAuthenticationMessage]` and `[ClientAuthenticationMessage]`](connections/authentication.md#declare-messages) methods.
- `NetworkObject.NetworkManager` and `NetworkBehaviour.NetworkManager` return the manager that spawned the object, and `ServerManager.StartedPeers` lists the peers that have started.
- `ServerManager.OnInputRejected` and `OnServerRpcRejected` report input and server RPCs that the server dropped because the sender does not own the object, see [message events](reference/callbacks.md#message-events). The warning that the server logged for them in 0.4.0 now appears only while nothing is subscribed.
- `PrefabRegistry.SetFactory` gives a prefab that is already in the list a factory, whether it runs before or after `NetworkManager.Awake`. See [factories and pooling](objects/spawning.md#factories-and-pooling).

## 0.4.0

This release ships these parts together:

| Part | Version | Install |
|---|---|---|
| `com.fomoxa.networking` | 0.4.0 | `https://github.com/fomoxa/com.fomoxa.networking.git#0.4.0` |
| `com.fomoxa.rpc` | 0.1.7; needs `com.fomoxa.networking` 0.4.0 | `https://github.com/fomoxa/com.fomoxa.rpc.git#0.1.7` |
| `com.fomoxa.networking.rapier` | 0.2.6; needs `com.fomoxa.networking` 0.4.0 | `https://github.com/fomoxa/networking-rapier.git?path=com.fomoxa.networking.rapier#0.2.6` |
| `com.fomoxa.networking.steam` | 0.1.2; needs `com.fomoxa.networking` 0.4.0 and Steamworks.NET 2025.165.0 or later | `https://github.com/fomoxa/com.fomoxa.networking.steam.git#0.1.2` |

`Fomoxa.Backend.Templates` 0.1.1 and the directory and gateway at tag `0.2.0` have no new version.

### Upgrading from 0.3.5

Update `com.fomoxa.rpc` to 0.1.7, `com.fomoxa.networking.rapier` to 0.2.6 and `com.fomoxa.networking.steam` to 0.1.2 together with the package. With the 0.4.0 package, `com.fomoxa.rpc` 0.1.6 reports an error when it generates code, Rapier 0.2.5 throws a version error when it creates its worlds, and Steam 0.1.1 throws one when the `NetworkManager` creates the transport.

A `NetworkBehaviour` now declares its state and input as fields and its RPC arguments as parameters, and the package generates the models. Code that registers models on a `NetworkBehaviour` no longer compiles. Replace it as follows:

| 0.3.5 | 0.4.0 |
|---|---|
| `OnRegisterState` with `state.Use(adapter, instance, onChanged)` | [`[NetworkState]` fields](synchronization/state.md), with `OnChanged` naming the callback |
| `state.Use(..., onlyWhenDirty: true)` | `[NetworkStateModel(OnlyWhenDirty = true)]` on the class |
| `state.Use(index, collection, ...)` | A [collection field](synchronization/collections.md) with `[NetworkState(Index = n)]` |
| `OnRegisterInput` with `input.Use(adapter, gather, apply)` | [`[NetworkInput]` fields](prediction/input.md), `OnGatherInput` and `OnApplyInput` |
| `input.Reconcile(adapter, capture, restore, matches)` | [`[NetworkReconcile]` fields](prediction/reconciliation.md), `OnCaptureState` and `OnRestoreState`; `Tolerance` on the attribute takes the place of `matches` |
| `OnRegisterRpcs` and `[NetworkRpc]` methods | `[ServerRpc]` and `[ClientRpc]` methods |
| `SendServerRpc(adapter, model)`, `SendObserversRpc(adapter, model)`, `SendTargetRpc(peerId, adapter, model)` | The generated [send methods](messaging/rpc.md#sending), such as `SendFireServerRpc(direction, weapon)` |

An RPC whose only parameter is a model now sends a generated model that holds it, on `ReliableOrdered` unless the attribute names another channel. In 0.3.5 it sent the model itself, on the model's `[NetworkChannel]`.

The Editor writes the generated models to the `StateModels` and `RpcModels` subfolders of the Generated Folder and blocks Play mode and player builds while one is missing or out of date.

The protocol and the package's own messages did not change, but your game's messages change with the generated models. Update the server and the clients of your game together, because a build made with 0.3.5 may not connect to one made with 0.4.0. A [console server](console-server/runtime.md) still registers models on `EntityBehaviour` as in 0.3.5; if it shares a behaviour with Unity clients, it uses the models that the Editor generates.

### Declaring with fields

- A state field can be any type that has a wire type, including a model. Collections are fields too, so one behaviour can hold state fields and collections side by side.
- An RPC takes any number of parameters. The generator writes a typed send method for each RPC, and sending by name takes the values as one argument or a tuple: `SendServerRpc(nameof(Fire), (direction, weapon))`.
- When the package generates a model whose fields changed, the Console shows a `[Fomoxa]` warning with a verdict. `COMPATIBLE` means older builds of the game still connect, and `BREAKING` means they do not. [Changing the fields](synchronization/state.md#changing-the-fields) lists which changes keep older builds connected.

## 0.3.5

This release ships these parts together:

| Part | Version | Install |
|---|---|---|
| `com.fomoxa.networking` | 0.3.5 | `https://github.com/fomoxa/com.fomoxa.networking.git#0.3.5` |
| `com.fomoxa.rpc` | 0.1.6; needs `com.fomoxa.networking` 0.3.5 | `https://github.com/fomoxa/com.fomoxa.rpc.git#0.1.6` |
| `com.fomoxa.networking.rapier` | 0.2.5; needs `com.fomoxa.networking` 0.3.5 | `https://github.com/fomoxa/networking-rapier.git?path=com.fomoxa.networking.rapier#0.2.5` |
| `com.fomoxa.networking.steam` | 0.1.1; needs `com.fomoxa.networking` 0.3.5 and Steamworks.NET 2025.165.0 or later | `https://github.com/fomoxa/com.fomoxa.networking.steam.git#0.1.1` |

`Fomoxa.Backend.Templates` 0.1.1 and the directory and gateway at tag `0.2.0` have no new version.

### Upgrading from 0.3.4

Update `com.fomoxa.rpc` to 0.1.6, `com.fomoxa.networking.rapier` to 0.2.5 and `com.fomoxa.networking.steam` to 0.1.1 together with the package. With the 0.3.5 package, `com.fomoxa.rpc` 0.1.5 reports an error when it generates code, Rapier 0.2.4 throws a version error when it creates its worlds, and Steam 0.1.0 throws one when the `NetworkManager` creates the transport.

The wire protocol, the fingerprints, the scene file format and the generated code did not change, so 0.3.4 and 0.3.5 peers connect to each other and you do not need to generate code again.

`HandlerExceptionArgs` is now a class instead of a struct, with the same constructor and properties. Your source code compiles without changes, but an assembly compiled against 0.3.4 has to be compiled again.

In the Editor and in Development builds, the server now logs a warning when a state registered with `onlyWhenDirty: true` changes and `SetStateDirty()` is not called. Set State Mark Warning Seconds on the `NetworkManager` to 0 to turn the check off.

### Errors

- A subscriber to `ServerManager.OnHandlerException` can set `HandlerExceptionArgs.Disconnect` to `false` to keep the client connected after a server message handler threw. The server then delivers the rest of the bundle and the messages after it.
- In the Editor and in Development builds, the server warns once per object when a state registered with `onlyWhenDirty: true` has differed from what it last sent for State Mark Warning Seconds (2 by default) without a call to `SetStateDirty()`. A console server turns the check on with `NetworkSettings.StateMarkWarning`.
- The new [Errors](concepts/error-handling.md) page lists which failures end a connection, which only drop a message, and why.

### com.fomoxa.rpc 0.1.6

- When the server rejects the credential in `ConnectOptions.Credential`, `ConnectException.Status` now carries the decoded detail if the authentication method declares its type.
- A transport can implement `IPeerAddress` to give `RpcServer` the address of the peer it accepted, for example when it reads the client's address from a proxy. A `TcpTransport` still gives the address of its socket.

## com.fomoxa.networking.steam 0.1.0

A new package adds a Steam transport. The other parts have no new version.

| Part | Version | Install |
|---|---|---|
| `com.fomoxa.networking.steam` | 0.1.0; needs `com.fomoxa.networking` 0.3.4 and Steamworks.NET 2025.165.0 or later | `https://github.com/fomoxa/com.fomoxa.networking.steam.git#0.1.0` |

`SteamNetworkTransport` connects players by SteamID through Steam. When two computers cannot reach each other directly, Steam sends the traffic through Valve's relay network, so a player can host from behind NAT without opening a port. It runs in Windows, Linux and macOS standalone builds with the Steam client, and has no dedicated or console server. The transport does not start Steam: your game starts it and runs its callbacks every frame. [Steam](connections/transports/steam.md) explains the setup.

## 0.3.4

This release ships these parts together:

| Part | Version | Install |
|---|---|---|
| `com.fomoxa.networking` | 0.3.4 | `https://github.com/fomoxa/com.fomoxa.networking.git#0.3.4` |
| `com.fomoxa.rpc` | 0.1.5; needs `com.fomoxa.networking` 0.3.4 | `https://github.com/fomoxa/com.fomoxa.rpc.git#0.1.5` |
| `com.fomoxa.networking.rapier` | 0.2.4; needs `com.fomoxa.networking` 0.3.4 | `https://github.com/fomoxa/networking-rapier.git?path=com.fomoxa.networking.rapier#0.2.4` |

`Fomoxa.Backend.Templates` 0.1.1 and the directory and gateway at tag `0.2.0` have no new version.

### Upgrading from 0.3.3

Update `com.fomoxa.rpc` to 0.1.5 and `com.fomoxa.networking.rapier` to 0.2.4 together with the package. With the 0.3.4 package, `com.fomoxa.rpc` 0.1.4 reports an error when it generates code, and Rapier 0.2.3 throws a version error when it creates its worlds.

The wire protocol, the fingerprints and the scene file format did not change, so 0.3.3 and 0.3.4 peers connect to each other.

`IClientPredictionBackend.EndCorrection` now takes the tick of the corrected state: `EndCorrection(INetworkEntity entity, uint tick)`. Only a backend for another engine implements this interface, and the Unity and console backends in the package already do.

The next code generation rewrites `FomoxaAdapters.cs`, which now records the name of every message. Commit the regenerated file. Code generated by 0.3.3 still compiles, and `FomoxaRegistry.NameOf` returns null until you regenerate.

### Debug tools

- Collect Statistics on the `NetworkManager` turns on traffic counters for bundles and for each message, in `ClientManager.Statistics` and `ServerManager.Statistics`, with message names from `FomoxaRegistry.NameOf`.
- `NetworkStatsDisplay` shows connection, traffic, tick and prediction numbers in a corner of the Game view.
- `SimulatedNetworkTransport` adds latency, jitter, packet loss, duplicates and reordering to another transport in the Editor and in Development builds, and `SimulatedTransportFactory` does the same on a console server.
- `NetworkTransform.OnCorrected` and `LastCorrection` report how far each prediction correction moves the object, and Draw Corrections shows the jumps in the Scene view.
- `ServerManager.DroppedInputs` counts the dropped inputs of every client.

[Debugging](advanced/debugging.md) and [network simulation](connections/transports/simulated.md) explain them.

## 0.3.3

This release ships these parts together:

| Part | Version | Install |
|---|---|---|
| `com.fomoxa.networking` | 0.3.3 | `https://github.com/fomoxa/com.fomoxa.networking.git#0.3.3` |
| `com.fomoxa.rpc` | 0.1.4; needs `com.fomoxa.networking` 0.3.3 | `https://github.com/fomoxa/com.fomoxa.rpc.git#0.1.4` |
| `com.fomoxa.networking.rapier` | 0.2.3; needs `com.fomoxa.networking` 0.3.3 | `https://github.com/fomoxa/networking-rapier.git?path=com.fomoxa.networking.rapier#0.2.3` |
| `Fomoxa.Backend.Templates` | 0.1.1 | `dotnet new install Fomoxa.Backend.Templates::0.1.1` |

The directory and gateway at tag `0.2.0` have no new version.

### Upgrading from 0.3.2

Update `com.fomoxa.rpc` to 0.1.4 and `com.fomoxa.networking.rapier` to 0.2.3 together with the package. With the 0.3.3 package, `com.fomoxa.rpc` 0.1.3 reports an error when it generates code, and Rapier 0.2.2 throws a version error when it creates its worlds.

The next code generation rewrites every generated file, because each one records the `fomoxac` version and now carries a `// <auto-generated/>` line. Commit the regenerated folder. The wire protocol, the fingerprints, the API and the scene file format did not change, so 0.3.2 and 0.3.3 peers connect to each other.

### fomoxac 0.2.3

The package bundles `fomoxac` 0.2.3 for Windows x64, Linux x64 and macOS, the same version as the backend template, the gateway and the directory. Generated C# files are marked as generated code, so a project with nullable reference types and warnings as errors compiles them without warnings.

### Backend template 0.1.1

The template now bundles `fomoxac` for macOS too, so a backend built on macOS generates its codecs. A backend made from 0.1.0 can copy `tools/fomoxac/osx/` from the new package and add the `OSX` line to its `.csproj`.

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
