# Setup

This page installs the Rapier backend into a project that already uses `com.fomoxa.networking` and switches its `NetworkManager` over to it.

## Install the package

A Unity package cannot declare a dependency on a Git package, so `com.fomoxa.networking` is not listed in this package's dependencies, and you install both. In Window > Package Manager, click +, choose Install package from git URL and enter each URL in turn:

```
https://github.com/fomoxa/com.fomoxa.networking.git
https://github.com/fomoxa/networking-rapier.git?path=com.fomoxa.networking.rapier
```

The backend checks the version of `com.fomoxa.networking` when it creates its worlds and throws `com.fomoxa.networking.rapier needs com.fomoxa.networking 0.1.0; the project has ...` if the project has another one.

The package carries the native library for Windows x64 and Linux x64 under `Runtime/Plugins`, and Unity copies the right one into player builds.

## Add RapierPhysics

1. Select the GameObject of the `NetworkManager`.
2. Add the `RapierPhysics` component. It must sit on the same GameObject as the `NetworkManager`; otherwise the manager throws `RapierPhysics belongs on the GameObject of the NetworkManager that uses it` when it starts.
3. Set Gravity if your game needs something other than (0, -9.81, 0). 2D worlds use its X and Y.
4. Drag the component into the Physics field of the `NetworkManager`.
5. Remove the `RigidbodyPhysics` component if there is one.

Do the same for every `NetworkManager` that runs a server or a client of the game. `RapierPhysics` always simulates, so it has no Simulate Physics field.

## Export the scene files

Rapier reads the static geometry of a scene from the scene file that the package writes into the Generated Folder, `<scene id>.fomoxascene`. The Editor writes it when you save a network scene, before every player build, and on Tools > Fomoxa > Export Network Scene Files, as described in [Editor integration](../unity/editor-integration.md#scene-files). Commit the files with the rest of the generated code.

Only network scenes have worlds. A scene must be in the Build Profiles scene list, so that it has a scene id in `FomoxaSceneList.asset`, and the `NetworkManager` must have that list in Collected Scenes. A loaded network scene without a scene file is simulated without static geometry, and the backend warns `scene 0x... has no scene file; Rapier simulates it without static geometry. Export the network scene files`.

## Check the result

Enter Play Mode as a host. The Console should show no warning about missing scene files, and a network object with a `Rigidbody2D` or `Rigidbody` should fall and land on the scene's static colliders. Its `Rigidbody` shows as kinematic in the Inspector while the manager runs, because Rapier moves the object and writes its pose back to the `Transform`.

A client that still uses `RigidbodyPhysics` connects and then stops with `PhysicsBackendMismatch`, which confirms that the server runs Rapier.

[Bodies and colliders](bodies.md) lists what the backend can represent.
