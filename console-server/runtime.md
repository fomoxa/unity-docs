# The runtime

This page writes a console server for the game from [your first project](../getting-started/tutorial/project-setup.md): a capsule per player, a `PlayerStats` state with a jump counter, and a parameterless `Jump` RPC. Unity clients built from that tutorial connect to it unchanged.

## Entities and behaviours

On the console, a network object is a `StandaloneEntity`, and its networked logic lives in `EntityBehaviour` classes. `EntityBehaviour` has the callbacks and registrations of `NetworkBehaviour`: `OnStartServer`, `OnStopServer`, `OnStartClient`, `OnStopClient`, the owner change callbacks, `OnRegisterRpcs`, `OnRegisterState`, `OnRegisterInput`, `OnReconciled`, the `SendServerRpc`, `SendObserversRpc` and `SendTargetRpc` methods, and `IsPredicting`, `IsReplaying` and `ReconcileCount`.

The `Player` prefab of the tutorial has a `NetworkTransform` and a `Player` behaviour, in that order. The console entity has one behaviour for each, in the same order:

```csharp
using System.Numerics;
using Fomoxa.Networking;
using Fomoxa.Networking.Standalone;
using Generated;
using MyGame.Network.Models;

namespace MyGame.Network
{
    public sealed class PlayerEntity : StandaloneEntity
    {
        public PlayerEntity()
            : this(new PlayerTransform(), new Player())
        {
        }

        private PlayerEntity(PlayerTransform transform, Player player)
            : base(FomoxaPrefabs.PlayerId, new EntityBehaviour[] { transform, player })
        {
            transform.Entity = this;
            player.Entity = this;
        }
    }

    public sealed class PlayerTransform : EntityBehaviour, ITransformSource, ITransformReceiver
    {
        public PlayerTransform()
        {
            SyncTransform(new TransformSync(new TransformSyncSettings(true, true, false, 0.01f, 0.1f, 0.01f)), this, this);
        }

        public StandaloneEntity Entity { get; set; }

        public void ReadLocal(out Vector3 localPosition, out Quaternion localRotation, out Vector3 localScale)
        {
            localPosition = Entity.Position;
            localRotation = Entity.Rotation;
            localScale = Entity.Scale;
        }

        public void ResetReceive()
        {
        }

        public void Receive(in TransformSample sample)
        {
        }
    }

    public sealed class Player : EntityBehaviour
    {
        private readonly PlayerStats stats = new PlayerStats();

        public StandaloneEntity Entity { get; set; }

        protected override void OnRegisterState(NetworkState state)
        {
            state.Use(PlayerStatsNetAdapter.Instance, stats);
        }

        protected override void OnRegisterRpcs(NetworkRpcs rpc)
        {
            rpc.OnServer(nameof(Jump), peerId => Jump());
        }

        private void Jump()
        {
            Entity.Position += Vector3.UnitY;
            stats.Jumps++;
        }
    }
}
```

`PlayerTransform` takes the place of `NetworkTransform`. `SyncTransform` gives the behaviour a `TransformSync`, and the server reads the entity's pose through `ITransformSource.ReadLocal` at the end of every tick and sends what changed, with the same rules as `NetworkTransform`. Use the settings of the prefab's `NetworkTransform`: sync position, rotation and scale, then the three thresholds. `ITransformReceiver` is called on a console client; a server leaves it empty. `TransformSync.Teleport()` does what `NetworkTransform.Teleport()` does.

`EntityBehaviour` has no reference to its entity, so the entity passes itself to its behaviours, as above.

### Prefabs

The client checks a spawn by its prefab id and fingerprint, then gives the message of behaviour index *n* to the *n*-th `NetworkBehaviour` of its prefab. A console entity therefore has to match the prefab:

- the prefab id and the fingerprint come from the generated `FomoxaPrefabs` constants;
- the behaviours are in the order of the prefab's `NetworkBehaviour` components, which is the order the Inspector shows, children after their parent;
- each behaviour registers the same state, input and RPC models as its Unity counterpart.

A parameterless RPC is found by the full name of the behaviour's type and the method name, as the generated `RpcModels` registered them. Give the console behaviour the same namespace and class name as the Unity one, as `MyGame.Network.Player` above, or use RPCs with a model, which are matched by the model alone.

## Program

```csharp
using System;
using System.Diagnostics;
using System.IO;
using System.Numerics;
using System.Threading;
using Fomoxa.Networking;
using Fomoxa.Networking.Sessions;
using Fomoxa.Networking.Standalone;
using Fomoxa.Networking.Transports;
using Generated;
using MyGame.Network;

namespace MyGame.Server
{
    public static class Program
    {
        public static void Main()
        {
            var registry = new FomoxaRegistry();
            FomoxaAdapters.RegisterAll(registry);

            var prefabs = new StandalonePrefabs();
            prefabs.Register(FomoxaPrefabs.PlayerId, FomoxaPrefabs.PlayerFingerprint, () => new PlayerEntity());

            var clock = Stopwatch.StartNew();
            NetworkRuntime runtime = StandaloneRuntime.Create(
                registry,
                new NetworkSettings(),
                new UdpTransportFactory(),
                prefabs,
                new StandaloneBehaviours(),
                new SceneFileDirectory(Path.Combine(AppContext.BaseDirectory, "Scenes")),
                () => clock.Elapsed,
                NetworkLog.Console);

            runtime.ServerManager.OnRemoteConnectionState += args =>
            {
                if (args.State == ConnectionState.Started)
                {
                    var player = new PlayerEntity { Position = new Vector3(args.PeerId * 2f, 0f, 0f) };
                    runtime.ServerManager.Spawn(player, args.PeerId);
                }
            };

            runtime.ServerManager.StartConnection(7777);
            Console.WriteLine($"server listening on port {runtime.ServerManager.Port}");

            TimeSpan last = clock.Elapsed;
            while (true)
            {
                TimeSpan now = clock.Elapsed;
                runtime.BeginFrame(now, (now - last).TotalSeconds);
                runtime.EndFrame();
                last = now;
                Thread.Sleep(1);
            }
        }
    }
}
```

Run it with `dotnet run --project Server~ -c Release`, start a client from the Unity tutorial, and click Jump: the capsule moves up and the counter grows, exactly as with the Unity server.

## StandaloneRuntime.Create

```csharp
public static NetworkRuntime Create(
    FomoxaRegistry registry,
    NetworkSettings settings,
    ITransportFactory transport,
    StandalonePrefabs prefabs,
    StandaloneBehaviours behaviours,
    ISceneFiles scenes,
    Func<TimeSpan> clock,
    NetworkLog log,
    IPhysicsScenes physics = null,
    IReadOnlyList<uint> bootScenes = null)
```

| Parameter | Meaning |
|---|---|
| `registry` | A `FomoxaRegistry` filled by the generated `FomoxaAdapters.RegisterAll` |
| `settings` | The values that the `NetworkManager` Inspector holds in Unity: tick rate, timing mode, queue sizes, timeouts, prediction settings and the physics backend. Use the same tick rate as the clients expect. |
| `transport` | `UdpTransportFactory`, `TcpTransportFactory`, `WebSocketTransportFactory`, or a `MultiTransportFactory` that listens on several of them |
| `prefabs` | The prefab ids the runtime can spawn, each with its fingerprint and a factory |
| `behaviours` | Factories for the behaviours of scene objects, by the full name of their Unity type |
| `scenes` | Where scene files come from. `SceneFileDirectory(folder)` reads `<scene id>.fomoxascene` from a folder. |
| `clock` | A monotonic clock |
| `log` | Where warnings and errors go. `NetworkLog.Console` writes them to standard error; `new NetworkLog(exception, warning, error)` sends them elsewhere. |
| `physics` | An `IPhysicsScenes`, or null for a server without physics; see [physics](physics.md) |
| `bootScenes` | Scene ids whose scene objects exist from the start, as described below |

The result is a `NetworkRuntime`, which holds the `ServerManager`, `ClientManager` and `TimeManager` that Unity code reaches through `NetworkManager`. Everything on the [server](../connections/server.md) and [client](../connections/client.md) pages applies to them, except what involves Unity objects.

## The frame loop

`NetworkRuntime` does nothing on its own. Call `BeginFrame(now, elapsedSeconds)` and then `EndFrame()` once per frame of your loop. `BeginFrame` runs every tick that is due, in the order described in [ticks and timing](../concepts/tick.md#order-of-one-tick), and `EndFrame` sends what the Variable timing mode queued. Calling them out of order, or from inside a tick event, throws.

The loop above sleeps between frames so that the process does not spin. Each frame runs every tick that is due, up to `NetworkSettings.MaxTicksPerFrame`, so a sleep longer than one tick does not slow the game down as long as it stays below that many ticks.

## Spawning

`ServerManager.Spawn(entity, ownerId)` spawns a `StandaloneEntity` the same way it spawns a `NetworkObject` in Unity. Set `Position`, `Rotation`, `Scale`, `SceneId`, `DespawnWithOwner` and `Visibility` before the call, because the spawn message carries them. `Despawn` and `ChangeOwner` work as in Unity. The server rejects an entity that is not a `StandaloneEntity`, and a prefab id that is not registered with `StandalonePrefabs`.

`SceneId` places the entity in a network scene, which limits its observers to the peers that loaded that scene, and selects its physics worlds.

## Scene objects and boot scenes

A scene object is described by the scene file of its scene: its scene object id, its fingerprint, its pose, the full type names of its behaviours and its body. The console backend builds a `StandaloneEntity` for it with the behaviours that `StandaloneBehaviours` creates for those type names:

```csharp
var behaviours = new StandaloneBehaviours();
behaviours.Register("MyGame.Network.Door", () => new Door());
```

A type name without a factory throws `behaviour type ... is not registered with StandaloneBehaviours` when the scene loads.

A network scene that the server loads with `ServerManager.Scenes` reads its file when it loads. The scene that clients open before they connect, such as the game scene of the tutorial, is not loaded through the network. Pass its scene id in `bootScenes` when it has scene objects or physics geometry: the backend reads its file in `Create`, spawns its scene objects when the server starts, and loads its geometry into the physics worlds. Clients match those objects against the scene they already have open, as with a Unity server. Entities of a boot scene set `SceneId` to that scene's id so that they share its physics worlds, and the server still sends them as objects outside any network scene.

The [physics](physics.md) page adds a physics backend, and the [reference](reference.md) lists the console types and the backend contract.
