# Red Runner troubleshooting

This page covers problems specific to the Red Runner port. Each section first links to the matching entry of the general [troubleshooting](../../getting-started/troubleshooting.md) page and then lists the checks that apply to this game.

## The client returns to the start screen after Play

The general checks are under [client cannot connect](../../getting-started/troubleshooting.md#client-cannot-connect).

- The server is running, and its log shows `[RedRunner] server listening on UDP port 7777`.
- The address field holds the server's address, and the server uses port 7777, which is the port the client joins. A server started with another `-port` cannot be joined from the start screen, because the start screen always uses `NetworkGame`'s Port field.
- Max Reconnect Retries is 3, so a client that cannot reach the server stops after three retries and the start screen comes back.

## The player does not spawn

The general checks are under [object does not spawn](../../getting-started/troubleshooting.md#object-does-not-spawn), and [spawning](../../core/spawning.md) explains the mechanism.

- If the Console shows `prefab id 0x... of RedRunner(Clone) is not registered`, drag `Generated/FomoxaPrefabList.asset` into Collected Prefabs and `Generated/FomoxaSceneList.asset` into Collected Scenes on the `NetworkManager` in `Play.unity`. In the Editor the package assigns these lists only after `NetworkManager.Awake`, as [step 03](offline-to-online/step-03-player-spawning.md#configure-the-networkmanager) explains.
- `RedRunner.prefab` has a `NetworkObject` and a prefab id. Choose Tools > Fomoxa > Assign Prefab Ids after changing it.
- `NetworkGame` has `RedRunner.prefab` in Player Prefab and the scene's `NetworkManager` in Manager.
- The server log shows `[RedRunner] spawned a player for peer ...`. If it does not, the client never reached `ConnectionState.Started`.

## The level is empty or differs between clients

The general checks are under [state does not update](../../getting-started/troubleshooting.md#state-does-not-update).

- The `Network Level` object has a `NetworkObject` and was saved after adding it, so that it has a scene object id. Scene objects stay inactive until the server spawns them.
- `Generation Settings.asset` has positive Start, Middle and End Blocks Counts, because otherwise `Layout` throws, as described in [step 02](offline-to-online/step-02-shared-level.md#make-the-level-finite).
- Hills, clouds and other background blocks are random on each client by design, and only the foreground comes from the seed.

## Another player's character does not move or slides in its idle pose

The general checks are under [remote objects jitter, lag or do not move](../../getting-started/troubleshooting.md#remote-objects-jitter-lag-or-do-not-move), with background in [NetworkTransform](../../synchronization/transform.md) and [authority](../../concepts/authority.md).

- `RedRunner.prefab` has a `NetworkTransform` with Sync Scale on; without it, the character does not turn.
- Simulate Physics is on in the `RigidbodyPhysics` of the `Network Manager`, and that component is in its Physics field. With it, a body the client does not predict is kinematic and follows its `NetworkTransform`, while without it the client's physics moves the body on its own.
- A character that moves but plays its idle animation needs the kinematic branch in `RedCharacter.LateUpdate`, which computes the speed from the distance moved, as shown in [step 05](offline-to-online/step-05-prediction-and-reconciliation.md#animate-characters-you-do-not-control).

## Your own character feels wrong

The general checks are under [prediction keeps correcting](../../getting-started/troubleshooting.md#prediction-keeps-correcting), with background in [prediction](../../concepts/prediction.md), [ticks and timing](../../concepts/tick.md) and [reconciliation](../../prediction/reconciliation.md).

- Tick Rate is 50, matching the project's fixed timestep of 0.02 seconds.
- `PlayerMotion` includes `RunSmoothVelocity`. Without it, every replay starts the acceleration from a different value and the character drifts after each correction.
- `RedCharacter.Jump` tests the ground with `GroundCheck.Check ()` rather than `IsGrounded`, which is a frame old during a replay.
- If jump sounds or particles play twice, check that `Apply` passes `!context.Replaying` as `effects`.
- In host mode the host's own character is not predicted and never corrects, so test prediction with a separate server.

## A player snaps or slides during a respawn

The mechanisms involved are described in [teleporting](../../synchronization/transform.md#teleporting), [teleporting a PhysicsBody](../../physics/physics-body.md#teleporting) and [reconciliation](../../prediction/reconciliation.md#correction-and-replay).

- If other clients see the character slide from the death point to the start, `NetworkPlayer.Respawn` must call `NetworkTransform.Teleport()` after it moves the body. The generated code must also be up to date with the package, because teleport generations travel in the transform system models.
- If the other clients' animator runs at a huge speed for a moment, `RedCharacter.LateUpdate` must treat a move over `m_TeleportDistance` as a teleport, as shown in [step 08](offline-to-online/step-08-two-clients.md#animate-a-character-that-teleports).
- If the owner's character jumps to the start in one frame, that is the expected correction. The owner predicts the character and takes the respawn as a reconcile mismatch, and since Red Runner does not use the `NetworkTransform` Visual field, the correction is not smoothed.

## The mace is in a different place on each client

`NetworkLevel` must move the followers in `TimeManager.OnPreTick` with `PredictionTick`, not with `Tick`, because on a client `Tick` counts local ticks and is not the server's number. [Ticks and timing](../../concepts/tick.md#three-tick-numbers) explains the three tick numbers.

## A player who left keeps running

The mechanisms involved are described in [client](../../core/client.md#connect-and-disconnect) and [input](../../prediction/input.md#on-the-server).

- If the player quit with Home or by closing the game, the client sends `PeerLeave` and the character should despawn at once. If it does not, regenerate the code with Tools > Fomoxa > Generate so that `PeerLeave` is registered.
- If the client crashed, the server waits for the heartbeat, about 20 seconds with the defaults. The character should still stand still after 10 repeated ticks; if it does not, check the `RepeatedTicks` rule in `NetworkPlayer.Apply` described in [step 08](offline-to-online/step-08-two-clients.md#stop-a-character-whose-player-vanished).

## The address field shows no text

In a player build, the game's font, `Baloo-Regular`, does not fit a default legacy input field. Set Vertical Overflow to Overflow on the field's text and placeholder, as described in [step 03](offline-to-online/step-03-player-spawning.md#add-the-address-field).
