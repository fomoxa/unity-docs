# Documentation TODO

This file collects the questions that the documentation could not settle from the package's code. It is not listed in `SUMMARY.md`.

## Unclear API

### Local peer id on a client
Question: Should a client be able to read its own peer id? `ClientObjects.LocalPeerId` exists but `ClientManager.Objects` is internal.
Why it matters: Games that compare `NetworkObject.OwnerId` with "me" have to use `IsOwner` instead. Documented as "the client does not expose its own peer id".
Source examined: `Runtime/Core/ClientManager.cs`, `Runtime/Core/Objects/ClientObjects.cs`.

### UDP listener limits in Fomoxa.Net
Question: Does the bundled `Fomoxa.Net.dll` limit the number of UDP peers per listener (the `csharp` source has `PeerCeiling = 1024` and a per-peer queue of 64 datagrams)?
Why it matters: A real server capacity limit that the UDP page does not mention, because the bundled DLL was not inspected.
Source examined: `Runtime/Plugins/Fomoxa.Net.dll` (binary only).

### Factories for collected prefabs
Question: Is the intended way to register a pooling factory for a prefab that the Editor collects to turn Collect Prefabs off?
Why it matters: `PrefabRegistry.Register(prefabId, ...)` throws when the prefab is already registered from Collected Prefabs. Documented as a limitation in `core/spawning.md`.
Source examined: `Runtime/Unity/PrefabRegistry.cs`, `Runtime/Unity/NetworkManager.cs`.

## Missing implementation

### Lockstep, match replay, deterministic RNG, state hashing
Current state: Not present in the code.
Documentation impact: Listed as not included; no pages.

### Samples
Current state: The package has no `Samples~` folder.
Documentation impact: The tutorial and the guides carry their own code instead of pointing at samples. The Red Runner example points at a separate game repository instead.

### Red Runner checks without WSL
Current state: The port's automated checks (`Tools/PortChecks`) run through `Tools/unity-windows.sh`, which drives a Windows Editor from WSL.
Documentation impact: The example describes what each check verifies and gives manual tests instead of the commands.

## Conflicting information

### Requested structure and Unity packages
Source: The documentation task asks for a `docs/` folder.
Existing docs: A `docs/` folder inside a Unity package is imported by Unity and needs `.meta` files; installs from Git would warn about every file.
Resolution: The documentation is kept in its own repository, outside the package, so Unity never imports it.

### Terms in the documentation task
Source: The task names `PhysicsWorld`, `PhysicsWorld3D` and `PhysicsWorld2D`.
Existing docs: The code names them `IPhysicsWorld` and `IPhysicsWorld2D`, both extending `IPhysicsSimulation`.
Resolution: The documentation uses the names in the code.

### Stale reconcile states
Source: `InputSlot.HoldPending` keeps the newest pending state, but after it has been handled, an older state that arrives late is held and handled again. Its tick is usually no longer in the history, so it counts as a mismatch and causes a correction from an older server state.
Existing docs: `prediction/reconciliation.md` says a state for a tick without a prediction counts as a mismatch, and does not describe this case.
Resolution: Not resolved; needs a decision on whether late states should be ignored.
