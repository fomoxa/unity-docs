# Dedicated server

A dedicated server is a build of your game that runs only the server, without a player and usually without graphics. It comes from the same Unity project and the same scenes as the client, and is simply started in a way that makes your code call `ServerManager.StartConnection` instead of `ClientManager.StartConnection`.

## Starting the server from the command line

The package does not read command-line arguments, so your code decides how a build becomes a server:

```csharp
using System;
using Fomoxa.Networking;
using Fomoxa.Unity;
using UnityEngine;

public sealed class ServerBootstrap : MonoBehaviour
{
    [SerializeField] private NetworkManager manager;
    [SerializeField] private ushort defaultPort = 7777;
    [SerializeField] private int serverFrameRate = 60;

    private void Start()
    {
        string[] arguments = Environment.GetCommandLineArgs();
        if (Array.IndexOf(arguments, "-server") < 0)
        {
            return;
        }

        Application.targetFrameRate = serverFrameRate;
        manager.ServerManager.StartConnection(ReadPort(arguments));
        Debug.Log($"server listening on port {manager.ServerManager.Port}");
    }

    private ushort ReadPort(string[] arguments)
    {
        int index = Array.IndexOf(arguments, "-port");
        return index >= 0 && index + 1 < arguments.Length && ushort.TryParse(arguments[index + 1], out ushort port)
            ? port
            : defaultPort;
    }
}
```

Build a player and start it without graphics:

```
MyGame.exe -batchmode -nographics -server -port 7777 -logFile server.log
```

`-batchmode` and `-nographics` are Unity's options for running without a window and without a graphics device, and `-logFile` writes the Unity log, including the package's warnings, to a file.

## Frame rate and ticks

Ticks run inside Unity's frames. Each frame runs every tick that is due, up to Max Ticks Per Frame (3 by default), and drops the rest. Keep the server's frame rate at least as high as its tick rate so that every tick runs in its own frame, and cap it with `Application.targetFrameRate` so that the server does not use more CPU than it needs.

## Headless behavior

The server needs the same prefabs, scenes and generated code as the clients, because spawns are checked by prefab id and fingerprint and the handshake compares schemas. Build the server and the clients from the same project state.

Renderers, audio and UI do nothing useful on a dedicated server, but the package does not turn them off. Leave them in, or strip them in your own build process.

## Stopping

When the application quits normally, the `NetworkManager` stops its connections, but a process that is killed gets no chance to. Either way, clients see their connection stop, with `PeerClosed` if the server's close reaches them or with `Timeout` after the heartbeat timeout, and then try to reconnect according to their settings.

The [server](../connections/server.md) page covers the `ServerManager` itself, and [deployment](deployment.md) covers what the host machine and its network need. Part 2 of the tutorial, [start a server](../getting-started/tutorial/server.md#5-run-a-dedicated-server), builds and runs one.
