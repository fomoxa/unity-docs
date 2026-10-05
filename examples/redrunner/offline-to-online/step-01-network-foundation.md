# Step 01: Network foundation

## Goal

This step adds `com.fomoxa.unity` to Red Runner, sets up code generation and puts a `NetworkManager` in `Play.unity`. The game still plays as before, because nothing opens a connection yet.

## Starting point

The [offline game](../offline-baseline.md) at upstream commit `2b675b5`, saved with Unity 6000.2.6f2.

## Problem

The package needs Unity 6000.5 or later, and the project is on an older version. The package also generates the codecs for every network message from C# classes, so before any networking code can compile, the project needs a place for those classes and for the generated code. Finally, the build scene list names a scene that does not exist, and the package collects its network scenes from that list.

## Fomoxa concepts

- [Installation](../../../getting-started/installation.md)
- [Models and codecs](../../../messaging/models.md)
- [Editor integration](../../../unity/editor-integration.md)
- [NetworkManager](../../../core/network-manager.md)
- [UDP](../../../transports/udp.md)

## Design

All networking code goes under `Assets/Scripts/RedRunner/Networking`, next to the game's own folders. Models go in `Networking/Models` and generated code in `Networking/Generated`, which makes the generated namespace `Generated`. A single `Network Manager` object at the root of `Play.unity` carries the `NetworkManager` and a `UdpNetworkTransport`.

## Files

```
Packages/manifest.json
Packages/packages-lock.json
ProjectSettings/ProjectVersion.txt
ProjectSettings/EditorBuildSettings.asset
Assets/Scenes/Play.unity
Assets/Scripts/RedRunner/Networking/FomoxaSettings.asset
Assets/Scripts/RedRunner/Networking/Models/.gitkeep
Assets/Scripts/RedRunner/Networking/Generated/
FomoxaSystemModels/
.fomoxa/
fomoxa.toml
```

## Implementation

### Upgrade the project

Open the project with Unity 6000.5 or later and accept the upgrade. Package Manager moves the Unity packages in `Packages/manifest.json` to the versions that ship with your Editor, and `ProjectSettings/ProjectVersion.txt` records the new version; the port used 6000.5.7f1. If you want the upgrade separate from the networking work, commit it on its own.

### Add the package

Open Window > Package Manager, click +, choose Install package from git URL and enter:

```
https://github.com/fomoxa/com.fomoxa.unity.git
```

The package depends on the built-in Physics, Physics 2D and Animation modules, which Red Runner already uses.

### Create the settings asset

1. Create the folders `Assets/Scripts/RedRunner/Networking/Models` and `Assets/Scripts/RedRunner/Networking/Generated`.
2. Right-click `Assets/Scripts/RedRunner/Networking` and choose Create > Fomoxa > Settings.
3. Set Models Folder to `Assets/Scripts/RedRunner/Networking/Models` and Generated Folder to `Assets/Scripts/RedRunner/Networking/Generated`.
4. Add an empty `.gitkeep` file to the models folder. The folder stays empty until step 02, and `fomoxac` stops when a source folder is missing.

After the next compilation the package writes `fomoxa.toml`, `FomoxaSystemModels/`, `.fomoxa/` and the generated folder, each of which [installation](../../../getting-started/installation.md#generate-the-code) describes. Commit all of them.

### Fix the build scene list

Open File > Build Profiles, remove the missing `Assets/Scenes/Gooose.unity` from the Scene List and add `Assets/Scenes/Play.unity`. The package refreshes `Generated/FomoxaSceneList.asset` from this list, as described in [network scenes](../../../core/scenes.md#scene-ids).

### Add the NetworkManager

In `Play.unity`, create an empty root GameObject named `Network Manager` and add:

1. `UdpNetworkTransport`.
2. `NetworkManager`, with the `UdpNetworkTransport` in its Transport field.

Leave the other fields at their defaults for now; step 03 changes the tick rate, turns on physics simulation and fills Collected Prefabs and Collected Scenes. A `NetworkManager` does nothing until code calls `ServerManager.StartConnection` or `ClientManager.StartConnection`, so the game plays as before.

## Test

To test the setup, add a throwaway component to the scene that starts a server on the scene's manager, creates a second manager as a client and connects it:

```csharp
server.ServerManager.StartConnection(0);
var clientObject = new GameObject("Check Client");
clientObject.AddComponent<UdpNetworkTransport>();
NetworkManager client = clientObject.AddComponent<NetworkManager>();
client.ClientManager.StartConnection("127.0.0.1", server.ServerManager.Port);
```

Port 0 lets the operating system choose a free port, which `ServerManager.Port` then reports. The port's own check for this step is `Tools/PortChecks/ConnectionCheck.cs`.

## Expected result

- The Console shows no error that starts with `[Fomoxa]`.
- `Generated/` contains `NetSchema.cs`, `FomoxaAdapters.cs` and an adapter for each system model.
- A few frames after the test starts, `client.ClientManager.State` is `ConnectionState.Started` and `server.ServerManager.PeerCount` is 1.
- Without the test component, the game plays as the offline game did.

## Commit

```
Commit: 8983a5a
Message: Install com.fomoxa.unity and add a NetworkManager to the Play scene
```

View [`8983a5a`](https://github.com/fomoxa/RedRunner/commit/8983a5ae2105e4ce79b8b127c9e5564147707eb1) on GitHub, then continue with [step 02: shared level](step-02-shared-level.md).
