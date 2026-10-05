# Troubleshooting

This page is organized by symptom. Each entry goes through the checks in order and quotes the exact message the package logs or throws, so you can search the page for the text you see. For the full list of stop reasons and mismatch kinds, see [errors and stop reasons](../reference/errors.md).

## Code generation fails

Generation errors appear in the Console with the prefix `[Fomoxa]`.

| Message | Cause and fix |
|---|---|
| `the fomoxac binary for this editor platform is missing` | The Editor runs on a platform without a bundled `fomoxac`. Only Windows x64 and Linux x64 are bundled. |
| `no FomoxaSettings asset; create one with Assets > Create > Fomoxa > Settings` | Create the settings asset, see [installation](installation.md#create-the-settings-asset). |
| `more than one FomoxaSettings asset exists; keep exactly one` | Delete the extra asset. |
| `the FomoxaSettings asset needs both a models folder and a generated folder` | Fill both fields of the settings asset. |
| `fomoxac generate exited with ...` | `fomoxac` rejected a model or a path. The rest of the message is `fomoxac`'s own output. A missing models folder is a common cause; create the folder. |
| `... was not written by com.fomoxa.unity; remove it ...` | A file the package manages, such as `fomoxa.toml` or a file in `FomoxaSystemModels`, was written by someone else. Remove it and generate again. |
| `the field type ... is neither a model nor a Unity type com.fomoxa.unity knows` | A model field uses a type that has no codec. See [custom codecs](../advanced/custom-codecs.md). |

## NetworkManager throws when the scene starts

The exception reads `no Fomoxa schema is registered; FomoxaAdapters.RegisterAll has not run`, or `no ... codec is registered; FomoxaAdapters.RegisterAll has not run`.

1. Check that the Generated Folder contains `FomoxaAdapters.cs` and `FomoxaUnityRegistration.cs`, and run Tools > Fomoxa > Generate if it does not.
2. Check that the project compiles. The registration runs from generated code, so a compile error anywhere else prevents it.
3. If you assign `NetworkManager.Registry` yourself, call the generated `FomoxaAdapters.RegisterAll(registry)` on that registry first.

## Client cannot connect

The client's `OnClientConnectionState` reports `Stopped` with a `Reason`, and `WillRetry` tells whether the client will try again. Work through these checks in order.

1. The server is running, that is, its `ServerManager.State` is `Started`.
2. The client uses the server machine's address. `127.0.0.1` only reaches a server on the same machine.
3. The client's port is the one the server reports in `ServerManager.Port`.
4. Both sides use the same transport. A UDP client cannot reach a TCP or WebSocket listener, and a server with a [`MultiNetworkTransport`](../transports/multi-transport.md) listens on a separate port for each transport.
5. The firewall lets the transport's protocol, UDP or TCP, through on the server's port.
6. If the `Reason` is `HandshakeFailed`, it comes with a `Failure` that narrows the cause down.
   - `SchemaConflict` means the client and the server were built from different models. Generate code once and build both from the same project state.
   - `VersionMismatch` means the two sides speak different Fomoxa protocol versions, for example because they were built with different versions of the package.
   - `Timeout` means the handshake did not finish within Handshake Timeout Seconds. Over UDP an unreachable server can also show up this way, because UDP has no connection step before the handshake.
7. A `Reason` of `TransportError` means the transport itself failed, for example on a refused TCP connection or a host name that does not resolve. The logs say which.

The client does not retry after `LocalStop`, `HandlerException`, `PrefabMismatch`, `ObjectMismatch`, `PhysicsBackendMismatch`, or a `HandshakeFailed` other than `Timeout`. A `PhysicsBackendMismatch` means the Physics Backend field differs between the server's and the client's `NetworkManager`.

## Client connects, then stops with PrefabMismatch or ObjectMismatch

In this case the client logs `Fomoxa stopped the client: object mismatch <kind>, object <id>, prefab 0x..., scene object 0x...`, and the kind tells you what to check.

| Kind | Check |
|---|---|
| `UnknownPrefab` | The client has no prefab with that prefab id. Assign Collected Prefabs on the client's `NetworkManager`, and build client and server from the same project state. |
| `IncompatiblePrefab` | The prefab exists but its list of `NetworkBehaviour` components differs between server and client. Rebuild both. |
| `UnknownSceneObject` | The client's scene has no object with that scene object id. Save the scene after adding a `NetworkObject` to it, and rebuild. |
| `IncompatibleSceneObject` | The scene object's `NetworkBehaviour` list differs between the builds. |
| `UnknownScene` | The client could not load a network scene the server asked for. Check the scene is in the build and in Collected Scenes. |
| `InvalidSpawn`, `InvalidMessage`, `DuplicateObject`, `UnknownObject` | The client received an object message it could not apply, such as initial state that does not decode. Check that both sides run the same build. |

## Object does not spawn

Start on the server.

1. The code calls `ServerManager.Spawn` only after the server has started; before that, the call throws `the server is not started`.
2. The argument is an instance in a scene. Passing the prefab asset throws `<name> is a prefab asset; spawn an instance of it`.
3. The prefab is registered. `prefab id 0x... of <name> is not registered` means it is in neither Collected Prefabs nor the Prefabs list of the `NetworkManager`; see step 5 of [your first project](first-project.md).
4. The prefab has a prefab id. A prefab with Prefab Id 0 cannot be registered, so run Tools > Fomoxa > Assign Prefab Ids.
5. The owner is a connected client. `owner <id> is not a started peer` means it is not; pass 0 for an object without an owner.

If the server spawns the object but a client does not show it, continue on the client.

1. The client only receives objects it observes. Check the object's Visibility field, the Observer Rule of the `NetworkManager`, and `ServerManager.IsObserver(networkObject, peerId)`. With a [`DistanceRule`](../core/observers.md#distancerule), a peer that owns no object observes nothing except what it owns.
2. An object in a network scene only reaches peers that have loaded that scene.
3. If the client stopped with a mismatch, see the previous section.

## RPC does nothing

1. If the server logs `Fomoxa dropped server RPC 0x... to object <id> from peer <id>, which does not own the object`, the caller is not the owner. Call the RPC from the owner's client, or set `RequireOwnership = false`.
2. `<name> is not spawned on the server` or `on the client` means the object is not spawned on the side that sends.
3. `<Type>.<Method> has no generated parameterless RPC model; mark the method with [NetworkRpc] and run Tools > Fomoxa > Generate` means the generated model is missing. Let the generation finish, then try again.
4. Compile errors `FOMOXA001` to `FOMOXA010` describe a wrong RPC declaration; see [RPCs](../messaging/rpc.md#compile-errors).
5. An RPC with a model uses the model's channel, which is unreliable unless the model declares `[NetworkChannel(..., Channel.ReliableOrdered)]`, and an unreliable RPC can be lost.
6. `SendTargetRpc` returns `SendResult.NotObserver` when the target peer does not observe the object.

## State does not update

1. Only the server sends state. A change made on a client stays local and is overwritten by the next change from the server.
2. Registration errors are thrown as `HandlerRegistrationException` when the object spawns. The causes are a state model that is not on the reliable-ordered channel, a state model that encodes to no bytes, or a behaviour that registers more than one state model.
3. `onChanged` runs only for changes after the spawn. The initial value is already in place in `OnStartClient`, and it does not trigger the callback.

## Remote objects jitter, lag or do not move

1. The prefab needs a `NetworkTransform`.
2. Movements below the position, rotation or scale threshold are not sent until the object stops.
3. Clients show remote objects Interpolation Ticks behind the newest position. Lower the value for less delay, or raise it for smoother movement over a lossy network.
4. A dynamic `Rigidbody` or `Rigidbody2D` on a client keeps simulating unless Simulate Physics is on. With it on, the client turns the bodies it does not predict into kinematic bodies that follow `NetworkTransform`; see [physics](../physics/overview.md).

## Prediction keeps correcting

Each time the client corrects a prediction, it calls `OnReconciled` and increments `NetworkBehaviour.ReconcileCount`. If the count keeps growing while the player does nothing special, the client and the server are computing different results.

1. `apply` must move by `TimeManager.TickDelta`, never by `Time.deltaTime`.
2. Per-frame input, such as a button press, must be stored in `Update` and read in `gather`, so that a short press is not lost.
3. `apply` must read only the input, the behaviour's own state and the tick length. Reading other objects, frame time or unseeded random numbers makes the two sides differ.
4. With physics, Simulate Physics must be on so that the package steps and rolls back physics per tick. Even then, rollback of Unity physics is approximate; see [rollback](../prediction/rollback.md).
5. The reconcile model must contain everything `apply` depends on. A value that carries over between ticks, such as a damping velocity, belongs in it.
6. Without a `matches` function, the package compares the encoded bytes exactly, so float noise counts as a mismatch. Pass a `matches` function with tolerances.

Input that the server could not use also causes corrections. Input that arrives too late or too far ahead is dropped, the server repeats the last input for that tick, and `ServerManager.DroppedInputsOf(peerId)` counts these cases.

The message `<Type> registers an input model, but its NetworkManager uses the Variable timing mode; prediction needs the Tick timing mode` means the Timing Mode field must be set to Tick.

## Warnings about dropped messages

`Fomoxa dropped message 0x... (N bytes) to peer <id>: TooLarge` means a single message did not fit the transport. `Fomoxa dropped N received bytes from peer <id>: a message bundle, or a model in it, could not be read` means a received bundle failed to decode. Both warnings are logged by default and can be turned off with Log Send Dropped and Log Receive Dropped, and [debugging](../advanced/debugging.md) shows how to subscribe to the same events.

## WebGL build fails to connect

`UdpNetworkTransport cannot run in a browser` or `TcpNetworkTransport cannot run in a browser` means the build uses the wrong transport: a WebGL build needs a `WebSocketNetworkTransport`, alone or inside a `MultiNetworkTransport`. `a server cannot listen in a browser; WebGL builds are clients only` means the build tried to start a server or a host, which a WebGL build cannot do. See [WebGL](../unity/webgl.md).
