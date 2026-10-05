# Your first server

This page adds a launcher to the scene from [your first project](first-project.md). The launcher starts a server, a host or a client, and the server spawns a `Player` for every client that connects. Here you only test the server; [your first client](first-client.md) connects clients to it.

## 1. Write the launcher

Create `Assets/Network/Launcher.cs`:

```csharp
using System;
using Fomoxa.Unity;
using Fomoxa.Unity.Sessions;
using UnityEngine;

namespace MyGame.Network
{
    public sealed class Launcher : MonoBehaviour
    {
        [SerializeField] private NetworkManager manager;
        [SerializeField] private NetworkObject playerPrefab;
        [SerializeField] private ushort port = 7777;

        private string address = "127.0.0.1";

        private void Start()
        {
            manager.ServerManager.OnRemoteConnectionState += OnRemoteConnectionState;
            manager.ClientManager.OnClientConnectionState += OnClientConnectionState;
            if (Array.IndexOf(Environment.GetCommandLineArgs(), "-server") >= 0)
            {
                StartServer();
            }
        }

        private void OnDestroy()
        {
            if (manager != null && manager.ServerManager != null)
            {
                manager.ServerManager.OnRemoteConnectionState -= OnRemoteConnectionState;
                manager.ClientManager.OnClientConnectionState -= OnClientConnectionState;
            }
        }

        private void OnGUI()
        {
            bool serverRunning = manager.ServerManager.State != ServerState.Stopped;
            bool clientRunning = manager.ClientManager.State != ConnectionState.Stopped;
            if (serverRunning || clientRunning)
            {
                GUILayout.Label($"server: {manager.ServerManager.State}, peers: {manager.ServerManager.PeerCount}, client: {manager.ClientManager.State}");
                if (GUILayout.Button("Stop"))
                {
                    manager.ClientManager.StopConnection();
                    manager.ServerManager.StopConnection();
                }

                return;
            }

            address = GUILayout.TextField(address);
            if (GUILayout.Button("Server"))
            {
                StartServer();
            }

            if (GUILayout.Button("Host"))
            {
                StartServer();
                manager.ClientManager.StartConnection(address, manager.ServerManager.Port);
            }

            if (GUILayout.Button("Client"))
            {
                manager.ClientManager.StartConnection(address, port);
            }
        }

        private void StartServer()
        {
            manager.ServerManager.StartConnection(port);
            Debug.Log($"server listening on port {manager.ServerManager.Port}");
        }

        private void OnRemoteConnectionState(ConnectionStateArgs args)
        {
            Debug.Log($"peer {args.PeerId}: {args.State} {args.Reason}");
            if (args.State != ConnectionState.Started)
            {
                return;
            }

            var position = new Vector3(args.PeerId * 2f, 0f, 0f);
            NetworkObject player = Instantiate(playerPrefab, position, Quaternion.identity);
            manager.ServerManager.Spawn(player, args.PeerId);
        }

        private void OnClientConnectionState(ConnectionStateArgs args)
        {
            Debug.Log($"client: {args.State} {args.Reason}");
        }
    }
}
```

## 2. How the server part works

`ServerManager.StartConnection(port)` opens the transport's listener on that port. Port 0 asks the operating system for a free port, and `ServerManager.Port` always reports the port actually in use.

`ServerManager.OnRemoteConnectionState` reports every change in a client connection. Each client has a peer id, `args.PeerId`, and moves through three states: `Starting` while the transport has connected and the Fomoxa handshake runs, `Started` once the handshake has succeeded and messages can flow, and finally `Stopped`.

When a client reaches `Started`, the launcher instantiates the prefab and calls `ServerManager.Spawn(player, args.PeerId)`. Spawning assigns an object id, makes the peer the owner and sends the object to every client that observes it. The object passed in must be an instance in a scene rather than the prefab asset, and its prefab must be registered with the `NetworkManager`, which the Collected Prefabs list took care of on the previous page.

A `NetworkObject` despawns with its owner by default, so when the client leaves, the package despawns its player, and a despawn on the server destroys the instance. `ServerManager.StopConnection()` disconnects every client and despawns every object.

## 3. Add the launcher to the scene

1. Select `Network Manager` and add the `Launcher` component.
2. Drag the `NetworkManager` component into its Manager field and the `Player` prefab into Player Prefab.
3. Save the scene.

## 4. Test the server

Enter Play Mode and click Server. The Console should show `server listening on port 7777`, and the label should read `server: Started, peers: 0, client: Stopped`. Click Stop and leave Play Mode.

If `StartConnection` throws a `SocketException` instead, the port could not be opened, for example because another process is using UDP port 7777. Change the Port field of the launcher and try again.

## 5. Run a dedicated server

A dedicated server is a player build started without graphics, and the launcher starts a server whenever the command line contains `-server`.

1. Open File > Build Profiles, select your desktop platform and build the player, for example to `Builds/MyGame.exe` on Windows.
2. Start it from a terminal:

```
MyGame.exe -batchmode -nographics -server -logFile server.log
```

`server.log` should contain `server listening on port 7777`. Keep the process running for the next page, and stop it with your operating system's process tools when you are done. [Dedicated server](../server/dedicated-server.md) covers frame rate, ports and other details.

Continue with [your first client](first-client.md).
