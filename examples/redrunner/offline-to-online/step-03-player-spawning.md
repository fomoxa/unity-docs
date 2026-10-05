# Step 03: Player spawning

## Goal

After this step the game starts as a dedicated server, a host or a client. The server spawns one character for each client that joins, owned by that client, and every client sees all of them. The characters only stand at the start of the level until step 04 makes them move.

## Starting point

After step 02 the server and each client build the same level from a seed, but the single character is still an object in `Play.unity`.

## Problem

```
Offline:
Play.unity
  └── RedRunner (the only character)
        ↑ referenced by GameManager, TerrainGenerator, CameraController
RedCharacter.Update reads the keyboard
GameManager pauses with Time.timeScale = 0
```

A scene character exists once in every process, belongs to nobody, and moves with whatever keyboard that process has. Online, the number of characters depends on who is connected, so the server has to create them, and each client has to know which character is its own. An online game also cannot pause, because `Time.timeScale = 0` would stop the server's simulation, and every other player with it, behind one player's pause screen.

## Fomoxa concepts

- [Spawning](../../../core/spawning.md)
- [Ownership](../../../core/ownership.md)
- [Server](../../../core/server.md)
- [Client](../../../core/client.md)
- [Host mode](../../../core/host-mode.md)
- [NetworkTransform](../../../synchronization/transform.md)
- [Physics overview](../../../physics/overview.md)
- [Editor integration](../../../unity/editor-integration.md#prefab-step)

## Design

```
Client                         Server
Start screen: Play               NetworkGame.Start (-server)
  ↓                                ↓
NetworkGame.Join(address)        ServerManager.StartConnection(port)
  ↓ ── connect ──→                 ↓
                                 OnRemoteConnectionState(Started)
                                   ↓
                                 Instantiate RedRunner.prefab
                                 ServerManager.Spawn(player, peerId)
  ↓ ←── spawn ──
NetworkPlayer.OnStartClient
  IsOwner? → NetworkGame.SetLocalPlayer
```

`NetworkGame`, a `MonoBehaviour` next to the `NetworkManager`, holds the game's networking decisions: how to start, where to spawn a player and which player is local. `NetworkPlayer`, a `NetworkBehaviour` on the character prefab, reports the local player. The scene character is deleted, and the prefab `RedRunner.prefab` becomes the network player.

## Files

```
Assets/Prefabs/RedRunner.prefab
Assets/Scenes/Play.unity
Assets/Scripts/RedRunner/Characters/RedCharacter.cs
Assets/Scripts/RedRunner/GameManager.cs
Assets/Scripts/RedRunner/Utilities/CameraController.cs
Assets/Scripts/RedRunner/UI/UIScreen/StartScreen.cs
Assets/Scripts/RedRunner/UI/UIScreen/PauseScreen.cs
Assets/Scripts/RedRunner/Networking/NetworkGame.cs
Assets/Scripts/RedRunner/Networking/NetworkPlayer.cs
Assets/Scripts/RedRunner/Networking/Generated/FomoxaPrefabList.asset
Assets/Scripts/RedRunner/Networking/Generated/FomoxaPrefabs.cs
```

## Implementation

### Make the character a network prefab

Open `Assets/Prefabs/RedRunner.prefab` and add to its root:

1. `NetworkObject`.
2. `NetworkTransform`, with Sync Rotation off (the `Rigidbody2D` freezes rotation) and Sync Scale on (`RedCharacter` faces left or right with `localScale.x`).
3. `NetworkPlayer`, below.

Save the prefab and choose Tools > Fomoxa > Assign Prefab Ids, which gives the prefab an id in `Generated/FomoxaPrefabList.asset`.

Then delete the `RedRunner` object from `Play.unity`. This leaves the Main Character field of Game Manager, the Character field of Terrain Generator and the Followee field of the camera empty.

### Let the game run without a scene character

`GameManager.Start` and `Update` now check `m_MainCharacter` for null. `CameraController.Follow ()` returns early when it has nothing to follow, and it gets an overload that sets the followee:

```csharp
public void Follow ( Transform followee )
{
	m_Followee = followee;
}
```

`GameManager.StopGame` and `ResumeGame` now only set the flag and leave `Time.timeScale` alone:

Before:

```csharp
public void StopGame()
{
    m_GameRunning = false;
    Time.timeScale = 0f;
}
```

After:

```csharp
public void StopGame()
{
    m_GameRunning = false;
}
```

`RedCharacter.Update` no longer reads the keyboard or moves the character, because step 04 sends the input through the network. The guard and punch actions are left out of the online game.

### Configure the NetworkManager

| Field | Value | Why |
|---|---|---|
| Tick Rate | 50 | The project's fixed timestep is 0.02 seconds, so physics steps as often as in the offline game. |
| Simulate Physics | on | The manager steps 2D physics once per tick. On a client, a networked `Rigidbody2D` that the client does not predict becomes kinematic and follows its `NetworkTransform`. |
| Max Reconnect Retries | 3 | The default, -1, retries forever. With 3, a client that cannot reach the server stops and the game returns to the start screen. |
| Collected Prefabs | `Generated/FomoxaPrefabList.asset` | See below. |
| Collected Scenes | `Generated/FomoxaSceneList.asset` | See below. |

The package assigns both lists itself when Unity prepares a scene for Play Mode, but in the Editor that happens after `NetworkManager.Awake` has registered prefabs, and spawning then fails with `prefab id 0x... of RedRunner(Clone) is not registered`. Player builds get the lists during the build. Assigning them in the scene works in both cases.

### Start a server, a host or a client

`NetworkGame.cs` (abridged; the full file is in `Assets/Scripts/RedRunner/Networking`):

```csharp
private void Start()
{
    m_Manager.ServerManager.OnRemoteConnectionState += OnRemoteConnectionState;
    m_Manager.ClientManager.OnClientConnectionState += OnClientConnectionState;
    string[] arguments = Environment.GetCommandLineArgs();
    ushort port = ReadPort(arguments);
    if (Array.IndexOf(arguments, "-server") >= 0)
    {
        Application.targetFrameRate = m_ServerFrameRate;
        StartServer(port);
    }
    else if (Array.IndexOf(arguments, "-host") >= 0)
    {
        Host(port);
    }
}

public void StartServer(ushort port)
{
    m_Manager.ServerManager.StartConnection(port);
    Debug.Log($"[RedRunner] server listening on UDP port {m_Manager.ServerManager.Port}");
}

public void Host(ushort port)
{
    StartServer(port);
    m_Manager.ClientManager.StartConnection("localhost", m_Manager.ServerManager.Port);
}

public void Join(string address, ushort port)
{
    m_Manager.ClientManager.StartConnection(string.IsNullOrWhiteSpace(address) ? "localhost" : address.Trim(), port);
}

public void Leave()
{
    m_Manager.ClientManager.StopConnection();
    if (IsServer)
    {
        m_Manager.ServerManager.StopConnection();
    }
}

private void OnRemoteConnectionState(ConnectionStateArgs args)
{
    if (args.State != ConnectionState.Started)
    {
        return;
    }

    NetworkObject player = Instantiate(m_PlayerPrefab, m_SpawnPoint, Quaternion.identity);
    m_Manager.ServerManager.Spawn(player, args.PeerId);
    Debug.Log($"[RedRunner] spawned a player for peer {args.PeerId} at {m_SpawnPoint}");
}
```

`-server` starts a dedicated server and caps the frame rate at `m_ServerFrameRate` (60), because a batch mode player otherwise runs frames as fast as the CPU allows. `-host` runs a server and a client in one process, and `-port` changes the UDP port from its default of 7777. For the start screen, the class also raises `ClientStateChanged` with each `ConnectionState` of the client.

The server spawns a character with the peer as its owner as soon as the peer reaches `ConnectionState.Started`. By then the level already exists, because `NetworkLevel` builds it when the server starts. When the peer leaves, the package despawns the character, since Despawn With Owner is on by default.

`NetworkPlayer.cs` in this step only reports the local player:

```csharp
public sealed class NetworkPlayer : NetworkBehaviour
{
    private NetworkGame m_Game;

    public override void OnStartClient()
    {
        if (NetworkObject.IsOwner)
        {
            m_Game = FindFirstObjectByType<NetworkGame>();
            m_Game?.SetLocalPlayer(this);
        }
    }

    public override void OnStopClient()
    {
        m_Game?.ClearLocalPlayer(this);
        m_Game = null;
    }
}
```

`NetworkObject.IsOwner` is already valid in `OnStartClient`. The package does not give a client its own peer id, so ownership is how a client finds its local character.

Add `NetworkGame` to the `Network Manager` object, with the `NetworkManager` in Manager and `RedRunner.prefab` in Player Prefab. The default spawn point, (7.24, 12.59), is where the scene character used to stand.

Fomoxa creates the character on every client, assigns the owner and despawns the character when the owner leaves, while the game decides when to spawn, where, and which prefab.

### Add the address field

Under `Canvas/Start Screen`, add a GameObject > UI > Legacy > Input Field named `Address Field`, below the row of small buttons (position 0, -222, size 320 × 48). Set its text to `localhost` and its placeholder to `Server address`. Give both texts the game's font, `Baloo-Regular`, at size 24, centred, with Vertical Overflow set to Overflow, because with Truncate the line height of Baloo hides the text. These layout settings come from commit `7396f92` in step 09; in `1b65628` the field sat elsewhere on the screen and its text did not show.

![The start screen with the address field](../../../.gitbook/assets/redrunner-start-screen.png)

`StartScreen` gets an `AddressField` and a `Network` field. The Play button calls `Network.Join(AddressField.text)` before it opens the in-game screen, and if the client connection stops while the game runs, the start screen comes back. `PauseScreen` gets a `Network` field too, and its Home button calls `Network.Leave()` before `GameManager.Init()`.

## Test

Build a Windows player with `Play.unity` as its only scene and start a server:

```
RedRunner.exe -batchmode -nographics -server -port 7777 -logFile server.log
```

Press Play in the Editor, keep `localhost` in the address field and click Play. Start more clients from the build to see more characters, or start the build with `-host` to try everything in one process.

The port's own checks are `HostCheck`, `JoinCheck` and `PlayerCheck` in `Tools/PortChecks`.

## Expected result

The server log shows the seed, the port and each spawn. The seed line comes from a `Debug.Log` in `NetworkLevel.OnStartServer`, which this step also adds:

```
[RedRunner] level seed 1535992127
[RedRunner] server listening on UDP port 7777
[RedRunner] spawned a player for peer 1 at (7.24, 12.59)
```

Each client builds the level from the server's seed, and its character drops onto the start block. Several characters stand in the same place and pass through each other, because the 2D layer collision matrix already turns off `Characters` against `Characters`. Nobody moves yet.

## Commit

```
Commit: 1b65628
Message: Join a dedicated server, a host or a client from the start screen
```

View [`1b65628`](https://github.com/fomoxa/RedRunner/commit/1b656285a486c6be727309e48d6612a3e483da80) on GitHub, then continue with [step 04: player input](step-04-player-input.md).
