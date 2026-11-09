# Determinism

Rapier gives the same result for the same world and the same sequence of operations. The backend keeps its own part of that promise: one pinned Rapier version, the `enhanced-determinism` feature, worlds built in the same order on every machine, and snapshots that hold the whole world. Game code has to keep the operations the same.

## What game code must do

- Change bodies only in prediction callbacks (`apply`, `restore`) and tick events, in a fixed order, from the input and the tick number. Forces, impulses and state writes are operations on the world, and a different order gives a different result.
- Keep library math out of values that reach the simulation. `Mathf.Sin`, `MathF.Cos` and other library functions can differ in the last bit between Mono, IL2CPP and .NET. Use tables, integer arithmetic or values that come from the input.
- Do not read time, frame-dependent values or random generators seeded from the clock in simulation code. A generator seeded from a value that the server sends, with its own arithmetic, gives the same sequence everywhere.
- Build runtime geometry in the same order on every peer. `AddStatic` and `AddBody` numbering and the order of bodies in the world follow the order of the calls, and so do joints and effectors created from code.

`System.Random` is not guaranteed to give the same sequence under Mono and .NET, so it is not suitable for a level that a Unity client and a console server both build from a seed.

## Checking a run

`RapierWorld.StateHash` and `RapierWorld2D.StateHash` hash the id, kind, position, rotation and velocities of every body of a world. Joints, effectors and contacts are not hashed directly, but they change the hash through the bodies they move. Comparing the hashes of the same tick on two machines, or on the server and a client, shows whether the two simulations are still the same. The package itself does not send or compare hashes.

## What is still approximate

Prediction still corrects when the server's input differs from the client's prediction, for example when another player's input arrives late or a remote body moves differently than the proxy showed. Determinism removes the corrections that the physics engine caused. Corrections caused by information the client did not have remain.

## Checked platforms

The native library runs one fixed scenario, with bodies, queries, forces, contacts, joints, character moves and effectors, and its hashes are compared with a reference list on every platform where the build workflow can run it: Windows, Linux and macOS on x64 and arm64, the iOS simulator, Android on an x86-64 emulator, and Web on Node. A Unity player project runs the same scenario through the C# API, and gives the same hashes in these players:

| Player | Scripting backend |
|---|---|
| Windows x64 | Mono and IL2CPP |
| Web | IL2CPP, in Microsoft Edge |
| Android `arm64-v8a` and `armeabi-v7a` | IL2CPP, on a phone |

Players on Linux, macOS and iOS have not been run with this check. The Windows arm64 player has only been built.
