# Multiple rooms on one server

A [dedicated server](dedicated-server.md) can host several matches of the same map in one process. Each match runs in its own instance of the map scene, and each instance has its own physics worlds, so players and objects in one room never collide with those in another and clients only receive the objects of their own room. This page builds that setup: a lobby that every client loads, rooms that the server opens for groups of players, and the move from the lobby into a room. The last section shows how to measure what a room costs on your own hardware.

## What a room is

A room is a [network scene instance](../objects/scenes.md#instances) of the map, loaded only for the peers that play in it:

- `ServerManager.Scenes.Load(mapId, peers, ScenePhysics.Own)` creates a new instance every time, even when the map already has one, and returns its `NetworkScene`.
- `ScenePhysics.Own` gives the instance its own 3D and 2D physics worlds. Two rooms of one map loaded with the default, `Shared`, would overlap in the default world, so a map can have only one `Shared` instance at a time.
- Objects in the instance, including objects the server spawns into it, only reach the peers that have loaded it.

The lobby is a global instance, loaded with `LoadGlobal`, which every client loads when it connects. Players spawn there and move into a room when the room is ready.

## Open a room and move the players in

Moving a player into a room only sends a scene move when the player's client has already loaded the room. A client that is still loading gets a despawn instead, then a new spawn once it reports the load, and its object starts again from `OnStartClient`. The class below therefore loads the room, waits until the server and every peer of the room have finished loading, and only then moves the players:

```csharp
using System.Collections.Generic;
using Fomoxa.Networking;
using Fomoxa.Unity;

public sealed class RoomHost
{
    private readonly NetworkManager manager;
    private readonly uint mapId;
    private readonly Dictionary<NetworkScene, PendingRoom> pending = new Dictionary<NetworkScene, PendingRoom>();

    public RoomHost(NetworkManager manager, uint mapId)
    {
        this.manager = manager;
        this.mapId = mapId;
        manager.ServerManager.Scenes.OnLoaded += OnLoaded;
        manager.ServerManager.Scenes.OnPeerLoaded += OnPeerLoaded;
    }

    public NetworkScene Open(IReadOnlyList<ulong> peers, IReadOnlyList<NetworkObject> players)
    {
        NetworkScene room = manager.ServerManager.Scenes.Load(mapId, peers, ScenePhysics.Own);
        pending.Add(room, new PendingRoom(peers, players));
        return room;
    }

    private void OnLoaded(NetworkScene room)
    {
        if (pending.TryGetValue(room, out PendingRoom waiting))
        {
            waiting.ServerLoaded = true;
            TryMoveIn(room, waiting);
        }
    }

    private void OnPeerLoaded(ulong peerId, NetworkScene room)
    {
        if (pending.TryGetValue(room, out PendingRoom waiting))
        {
            waiting.LoadedPeers.Add(peerId);
            TryMoveIn(room, waiting);
        }
    }

    private void TryMoveIn(NetworkScene room, PendingRoom waiting)
    {
        if (!waiting.ServerLoaded || waiting.LoadedPeers.Count < waiting.Peers.Count)
        {
            return;
        }

        pending.Remove(room);
        foreach (NetworkObject player in waiting.Players)
        {
            manager.ServerManager.MoveToScene(player, room);
        }
    }

    private sealed class PendingRoom
    {
        public PendingRoom(IReadOnlyList<ulong> peers, IReadOnlyList<NetworkObject> players)
        {
            Peers = peers;
            Players = players;
        }

        public IReadOnlyList<ulong> Peers { get; }

        public IReadOnlyList<NetworkObject> Players { get; }

        public HashSet<ulong> LoadedPeers { get; } = new HashSet<ulong>();

        public bool ServerLoaded { get; set; }
    }
}
```

`mapId` is the scene id of the map, for example `FomoxaScenes.ArenaId` or `manager.Scenes.IdOf("Assets/Scenes/Arena.unity")`. Create the `RoomHost` once the server has started, and pass `Open` the peers of the match and the player objects they own, which the server spawned in the lobby. `Load` skips peers that are not started, so drop a peer that disconnects from your own list before you call `Open`, and handle a disconnect during the load in your matchmaking code, because the room above would wait for that peer forever.

The move keeps each body's position and velocity. Rooms of one map usually start players at fixed spawn points, so place each player after its move through its body, which works with both physics backends:

```csharp
NetworkBody body = player.Body;
NetworkBodyState state = body.State;
state.Position = spawnPoint;
state.Velocity = Vector3.zero;
body.State = state;
```

Read `player.Body` after `MoveToScene`, because the move builds the bodies again in the room's world. An owner that predicts its player stops predicting when the move arrives and starts again from the first state the server sends from the room, as [moving an object](../objects/scenes.md#move-an-object-to-another-instance) describes.

## Fill the room

Objects that belong to the match, such as pickups or crates, are spawned into the room by moving them into its Unity scene before `Spawn`, as in [spawning into a network scene](../objects/spawning.md#spawning-into-a-network-scene). Do this in the `OnLoaded` handler of the room or later, because `TryGetScene` only finds the Unity scene once the server has loaded it.

## Physics queries in a room

A raycast or overlap only sees the colliders of one world. Ask the physics component for the worlds of the room's scene, as shown in [reaching a world](../physics/queries.md#reaching-a-world), and query those. The static `Physics.Raycast` and `Physics2D.Raycast` only see the default world, which holds the lobby and the scene the game started with, but no room loaded with `Own`.

## Choosing a physics backend

Both backends keep rooms apart:

| Backend | Rooms | What the server steps every tick |
|---|---|---|
| `RigidbodyPhysics` with Simulate Physics on | Each `Own` instance has its own PhysX and Box2D worlds | Every world of every loaded scene, the rooms included |
| `RapierPhysics` | Each instance has its own Rapier worlds, whichever `ScenePhysics` it was loaded with | The Rapier worlds; the manager also steps the Unity worlds of `Own` instances, which only hold physics outside network objects |

With Rapier, export the [scene files](../rapier/setup.md#export-the-scene-files) of the lobby and the map, because Rapier reads a room's static geometry from them.

## Closing a room

`ServerManager.Scenes.Unload(room)` despawns every object in the room, including the players, unloads the room on its peers and then on the server. To keep the players for the next match, move them back to the lobby with `MoveToScene(player, lobby)` before you unload the room. An instance stays loaded on the server when its last peer leaves, so unload rooms whose match has ended; otherwise their worlds keep being stepped.

## Measure your server

The cost of a room depends on the map, the number of bodies and the machine, so measure your own build. Run the server player as in production, with `-batchmode -nographics`, load the number of rooms you want to compare, give each room the objects a real match has, and let it run for a few hundred ticks before you start measuring.

### Tick time

With the Tick timing mode, every tick that is due in a frame runs inside the manager's first step of Unity's player loop, at the very start of `EarlyUpdate` (see [when it runs](../connections/network-manager.md#when-it-runs)). The class below adds a step before and after it and adds up the time between them. At the end of each frame that ran ticks, it divides the time gathered since the previous such frame by the number of ticks and records one value per tick. Create it after the manager is enabled, for example in `Start`, so that the manager's step is already first:

```csharp
using System;
using System.Collections.Generic;
using System.Diagnostics;
using Fomoxa.Networking;
using UnityEngine.LowLevel;
using UnityEngine.PlayerLoop;

public sealed class TickTimer : IDisposable
{
    private readonly TimeManager time;
    private readonly Stopwatch stopwatch = new Stopwatch();
    private readonly List<double> milliseconds = new List<double>();
    private double pending;
    private int ticksThisFrame;

    public TickTimer(TimeManager time)
    {
        this.time = time;
        time.OnPreTick += CountTick;
        PlayerLoopSystem root = PlayerLoop.GetCurrentPlayerLoop();
        for (int index = 0; index < root.subSystemList.Length; index++)
        {
            ref PlayerLoopSystem phase = ref root.subSystemList[index];
            if (phase.type == typeof(EarlyUpdate))
            {
                var systems = new List<PlayerLoopSystem>(phase.subSystemList);
                systems.Insert(1, new PlayerLoopSystem { type = typeof(TickTimer), updateDelegate = End });
                systems.Insert(0, new PlayerLoopSystem { type = typeof(TickTimer), updateDelegate = stopwatch.Restart });
                phase.subSystemList = systems.ToArray();
            }
            else if (phase.type == typeof(PostLateUpdate))
            {
                var systems = new List<PlayerLoopSystem>(phase.subSystemList);
                systems.Add(new PlayerLoopSystem { type = typeof(TickTimer), updateDelegate = Record });
                phase.subSystemList = systems.ToArray();
            }
        }

        PlayerLoop.SetPlayerLoop(root);
    }

    public IReadOnlyList<double> Milliseconds => milliseconds;

    public void Dispose()
    {
        time.OnPreTick -= CountTick;
        PlayerLoopSystem root = PlayerLoop.GetCurrentPlayerLoop();
        for (int index = 0; index < root.subSystemList.Length; index++)
        {
            ref PlayerLoopSystem phase = ref root.subSystemList[index];
            if (phase.subSystemList != null)
            {
                phase.subSystemList = Array.FindAll(phase.subSystemList, system => system.type != typeof(TickTimer));
            }
        }

        PlayerLoop.SetPlayerLoop(root);
    }

    private void CountTick() => ticksThisFrame++;

    private void End()
    {
        stopwatch.Stop();
        pending += stopwatch.Elapsed.TotalMilliseconds;
    }

    private void Record()
    {
        if (ticksThisFrame == 0)
        {
            return;
        }

        for (int tick = 0; tick < ticksThisFrame; tick++)
        {
            milliseconds.Add(pending / ticksThisFrame);
        }

        pending = 0;
        ticksThisFrame = 0;
    }
}
```

Report the mean, the median, the 95th percentile and the maximum of `Milliseconds`, not only the mean, because a slow tick is what players notice. At 60 ticks per second a tick has 16.7 ms, and the server also needs time for the rest of each frame.

### Memory

Read the memory after the measurement, with the rooms still loaded:

| Value | Read with | Covers |
|---|---|---|
| Managed heap | `GC.GetTotalMemory(false)` | C# objects of the game and the package |
| Unity reserved memory | `Profiler.GetTotalReservedMemoryLong()` (`UnityEngine.Profiling`) | Memory that Unity's allocators hold, scenes and physics included |
| Working set | `Process.WorkingSet64`, or the operating system's tools | The whole process |

In Windows players with the Mono scripting backend `Process.WorkingSet64` can report 0. Read the working set from Task Manager, or call `K32GetProcessMemoryInfo` from `kernel32.dll`, in that case.

### Comparing runs

Run each count of rooms in a fresh process, and with both backends if you are choosing between them. The difference between two counts is the cost of the added rooms, which is easier to compare across machines than the totals.

## Limits

All rooms of a process share Unity's main thread: the server steps every room's worlds and runs every room's game code one after the other, so a slow room delays the ticks of all rooms. Run more processes when one is no longer enough, as described in [cluster](cluster.md). A process that loads the same map many times also holds a copy of the map's scene objects per room.
