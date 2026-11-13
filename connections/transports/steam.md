# Steam

`SteamNetworkTransport` connects players through Steam. A client finds the host by its SteamID instead of an IP address, and Steam carries the traffic. When the two computers cannot reach each other directly, the traffic goes through Valve's relay network. A player can therefore host a game from a home network behind NAT without opening a port.

The transport is in its own package, `com.fomoxa.networking.steam`, and calls Steam through [Steamworks.NET](https://github.com/rlabrecque/Steamworks.NET). The package does not ship Steam's libraries. You install Steamworks.NET yourself.

## Requirements

- `com.fomoxa.networking` 0.3.4. The package is built for that one version and checks it, as described in [Versions](#versions).
- Steamworks.NET 2025.165.0 or later, installed as a Unity package.
- A Windows, Linux or macOS standalone build target. On WebGL, Android, iOS and other targets, the component is not compiled.
- The Steam client running and signed in on every computer, with each player on their own Steam account.
- A Steam AppID. During development you can use 480, Valve's test app Spacewar.

## Install

1. Install `com.fomoxa.networking` as described in [installation](../../getting-started/installation.md).
2. In Package Manager, choose **Install package from git URL** and add Steamworks.NET:

```
https://github.com/rlabrecque/Steamworks.NET.git?path=/com.rlabrecque.steamworks.net#2025.165.0
```

3. Add this package the same way:

```
https://github.com/fomoxa/com.fomoxa.networking.steam.git#0.1.0
```

`SteamNetworkTransport` lives in the `Fomoxa.Unity.Steam` assembly. Unity compiles that assembly only when Steamworks.NET is installed and the build target is Windows, Linux or macOS. Without Steamworks.NET, the project still compiles, and the component is missing from the **Add Component** menu.

## Start Steam in your game

The transport does not start Steam. Your game initializes the Steam API before it starts a server or a client, runs Steam's callbacks every frame, and shuts Steam down when it exits, as in this component:

```csharp
using Steamworks;
using UnityEngine;

public sealed class SteamSession : MonoBehaviour
{
    private bool started;

    private void Awake()
    {
        ESteamAPIInitResult result = SteamAPI.InitEx(out string error);
        if (result != ESteamAPIInitResult.k_ESteamAPIInitResult_OK)
        {
            Debug.LogError($"Steam did not start ({result}): {error}");
            return;
        }

        started = true;
        Debug.Log($"Steam ID {SteamUser.GetSteamID().m_SteamID}");
    }

    private void Update()
    {
        if (started)
        {
            SteamAPI.RunCallbacks();
        }
    }

    private void OnDestroy()
    {
        if (started)
        {
            started = false;
            SteamAPI.Shutdown();
        }
    }
}
```

Put it in the same scene as the `NetworkManager`, and start the server or client after `Awake`, for example in `Start` or from a button. The transport learns that a connection has opened or closed from Steam's callbacks. If nothing calls `SteamAPI.RunCallbacks()`, connections never finish opening.

### The AppID file

When Steam did not launch the game, `SteamAPI.InitEx` reads the AppID from a file named `steam_appid.txt` in the working directory. In the Editor that is the project's root folder. In a build it is the folder of the executable. For development, the file holds one line:

```text
480
```

Steamworks.NET writes this file to the project's root folder from an Editor script, but the script can run after the first Play has already started Steam, and that Play then fails with `No appID found`. Steamworks.NET also does not copy the file next to a build. Create the file in the project's root folder yourself, and copy it next to your builds, by hand or with a post-build step. A game that Steam launches gets its AppID from Steam and does not read the file.

## Set up the NetworkManager

1. Add `SteamNetworkTransport` to a GameObject. It has no fields.
2. Assign it to the **Transport** field of the `NetworkManager`.

## Host and join

The server listens on a Steam virtual port, a number that only has meaning inside Steam. `ServerManager.StartConnection(port)` opens a Steam listen socket on that virtual port, and `ServerManager.Port` reports the same number. Nothing opens on the computer's UDP or TCP ports.

A client passes the host's SteamID64 as the address, written as a decimal number, together with the same virtual port:

```csharp
networkManager.ClientManager.StartConnection("76561198000000001", 7777);
```

The host reads its SteamID64 with `SteamUser.GetSteamID().m_SteamID`. The package does not include lobbies, invites or matchmaking, so your game decides how players pass the SteamID to each other, for example with Steam lobbies or friend invites from Steamworks.NET.

A player who hosts uses [host mode](../host-mode.md): `ServerManager.StartConnection(port)`, then `ClientManager.StartConnection` with any address. The host's own client always connects through the in-process [loopback](loopback.md), so it never goes through Steam.

A connection to an address that is not a SteamID64 fails at once with `TransportError`, as when a UDP server cannot be reached. Steam also refuses a connection to the game's own SteamID, so a second copy of the game on the same Steam account cannot join the first one. To test with two players, use two Steam accounts on two computers.

## Connection data

On the server, `ServerAuthenticationContext.ConnectionData` holds the client's SteamID as 8 bytes, little-endian. Read it in your [authenticator](../authentication.md):

```csharp
ulong steamId = BinaryPrimitives.ReadUInt64LittleEndian(context.ConnectionData.Span);
```

`BinaryPrimitives` is in `System.Buffers.Binary`. Steam authenticates both ends of the connection with certificates it issues, so a client cannot present another account's SteamID. The package has no authenticator of its own. Bans, friends-only games and similar rules are up to your game. For the host's own client, `ConnectionData` is empty.

## Behavior

| | Steam |
|---|---|
| Connection model | A Steam networking connection, then the Fomoxa handshake |
| Reliability of the transport | None used; every bundle goes as an unreliable Steam message, and the package runs its own reliability |
| Frame budget for bundles | 1200 bytes |
| Addressing | SteamID64 and virtual port |
| Server listens on | A Steam virtual port |
| Encryption | Steam encrypts every connection |
| Route | Chosen by Steam: direct when the two computers can reach each other, otherwise through Valve's relay network |

The package always uses Steam's default routing. RTT and traffic in [`NetworkStatsDisplay`](../../advanced/debugging.md) include the relay when Steam uses one.

## Limitations

- Only a game running with the Steam client can host. The package does not use Steam's game server API, so there is no dedicated server build and no [console server](../../console-server/overview.md) over Steam.
- One process has one SteamID and cannot connect to itself.
- No lobbies, invites or matchmaking.

## Troubleshooting

### `Steam is not initialized`

`ServerManager.StartConnection` or `ClientManager.StartConnection` throws:

```text
Steam is not initialized: call SteamAPI.Init() and run SteamAPI.RunCallbacks() every frame before starting a Steam connection
```

Steam has not started, or failed to start. Look for the error from `SteamAPI.InitEx` in the log. The usual causes are that the Steam client is not running, or that `steam_appid.txt` is missing from the working directory.

### The client stays in `Starting`

The client has asked Steam for a connection and Steam has not answered. Steam gives up on an attempt after about 10 seconds. The client then stops with `TransportError` and starts again after Reconnect Interval Seconds, as [reconnection](../client.md#reconnection) describes, so to a player it stays in `Starting`.

Over the relay, an attempt sometimes times out and the next one connects. That needs no fix. When every attempt fails, check these, in order:

1. Both games call `SteamAPI.RunCallbacks()` every frame.
2. Steam is online on both computers. `SteamAPI.InitEx` succeeds and the SteamID is known even when the Steam client cannot reach Steam's servers, but connecting needs those servers. If the Steam client shows Offline, keeps connecting, or shows error -101, fix the network first.
3. The address is the host's SteamID64, and the virtual port is the one the host listens on.
4. Run In Background is on in the host's build. A host whose window is in the background does not answer; see [troubleshooting](../../getting-started/troubleshooting.md#the-game-stops-while-its-window-is-in-the-background).

To see what Steam is doing, log its connection changes and messages in your game. Steamworks.NET calls every callback registered for an event, so this does not take events away from the transport:

```csharp
using System.Text;
using Steamworks;
using UnityEngine;

public sealed class SteamNetworkingLog : MonoBehaviour
{
    private Callback<SteamNetConnectionStatusChangedCallback_t> statusChanged;
    private FSteamNetworkingSocketsDebugOutput output;

    private void Start()
    {
        statusChanged = Callback<SteamNetConnectionStatusChangedCallback_t>.Create(LogStatus);
        output = LogMessage;
        SteamNetworkingUtils.SetDebugOutputFunction(ESteamNetworkingSocketsDebugOutputType.k_ESteamNetworkingSocketsDebugOutputType_Msg, output);
    }

    private void OnDestroy()
    {
        statusChanged?.Dispose();
    }

    private static void LogStatus(SteamNetConnectionStatusChangedCallback_t status)
    {
        Debug.Log($"Steam connection {status.m_eOldState} -> {status.m_info.m_eState}: {status.m_info.m_szEndDebug}");
    }

    private static void LogMessage(ESteamNetworkingSocketsDebugOutputType type, StringBuilder message)
    {
        Debug.Log($"Steam networking {type}: {message}");
    }
}
```

Put it in the same scene as `SteamSession`. `SteamSession` starts Steam in `Awake`, which runs before any `Start`. A computer that cannot reach Steam's servers logs `We're not logged into Steam`.

### Steam logs `recv queue overflow` or `Did you forget to call CloseConnection()`

Both warnings come from Steam's own messages, which the `SteamNetworkingLog` component above prints:

```text
recv queue overflow 1000 messages already queued.
We are in state 4 and have been waiting 20.0s to be cleaned up.  Did you forget to call CloseConnection()?
```

The first means that the game stopped reading a connection. Steam keeps 1000 unread messages for each connection and drops the ones after that. The second means that a connection ended at least 20 seconds earlier and the game has not closed it. The transport closes a connection when Steam's callback reports that it ended, and Steam runs callbacks only inside `SteamAPI.RunCallbacks()`. The state number is 4 when the other side closed the connection and 5 when Steam found a problem on this side.

Both usually mean that the game stopped running for a while, most often because its window was in the background with Run In Background off. See [troubleshooting](../../getting-started/troubleshooting.md#the-game-stops-while-its-window-is-in-the-background).

## Versions

The package is built for one version of `com.fomoxa.networking`, which `SteamPackage.CoreVersion` holds. When the `NetworkManager` creates the transport in `Awake` and the project has another version, the transport throws `InvalidOperationException`:

```text
com.fomoxa.networking.steam needs com.fomoxa.networking 0.3.4; the project has 0.3.5
```

Install the version of this package that the [release notes](../../release-notes.md) list for your version of `com.fomoxa.networking`.
