# Physics

A console server has no Unity physics. It simulates physics through an `IPhysicsScenes` passed to `StandaloneRuntime.Create`, and the [Rapier backend](../rapier/overview.md) provides one, `RapierScenes`. The Unity clients then use `RapierPhysics`, so both sides run the same Rapier worlds from the same scene files.

## Adding Rapier to the project

The assembly `Fomoxa.Networking.Rapier`, in `Runtime/Rapier` of the `com.fomoxa.networking.rapier` package, does not reference Unity. The console project compiles it like layer 1 and copies the native library next to the executable:

```xml
<PropertyGroup>
  <Rapier Condition="'$(Rapier)' == ''">$(Game)/../networking-rapier/com.fomoxa.networking.rapier</Rapier>
</PropertyGroup>

<ItemGroup>
  <Compile Include="$(Rapier)/Runtime/Rapier/**/*.cs" />
</ItemGroup>

<ItemGroup>
  <None Include="$(Rapier)/Runtime/Plugins/Linux/x86_64/libfomoxa_rapier.so" Link="libfomoxa_rapier.so" CopyToOutputDirectory="PreserveNewest" />
  <None Include="$(Rapier)/Runtime/Plugins/Windows/x86_64/fomoxa_rapier.dll" Link="fomoxa_rapier.dll" CopyToOutputDirectory="PreserveNewest" />
</ItemGroup>
```

Here `$(Rapier)` is a clone of [networking-rapier](https://github.com/fomoxa/networking-rapier) next to the other folders.

## Creating the runtime

```csharp
var physics = new RapierScenes(new Vector3(0f, -9.81f, 0f));
var settings = new NetworkSettings { PhysicsBackend = PhysicsBackend.Rapier };
NetworkRuntime runtime = StandaloneRuntime.Create(
    registry, settings, new UdpTransportFactory(), prefabs, behaviours,
    new SceneFileDirectory(scenesFolder), () => clock.Elapsed, NetworkLog.Console,
    physics, new[] { FomoxaScenes.GameId });
```

`NetworkSettings.PhysicsBackend` must be `Rapier`, because the server tells each client its backend and a client with `RapierPhysics` stops with `PhysicsBackendMismatch` otherwise. Use the gravity of the clients' `RapierPhysics`. Dispose the `RapierScenes` when the program ends, after `ServerManager.StopConnection()`, to free the native worlds.

`RapierScenes` keeps one world per scene id and dimension. The scene file of each boot scene and of each network scene that loads adds its static colliders and layer collision matrices to the worlds of that scene.

## Bodies of entities

When an entity spawns, the console backend asks it for its body and adds that body to the worlds of the entity's `SceneId`:

- A scene object uses the body described in its scene file, which the Editor wrote from its colliders and `Rigidbody` or `Rigidbody2D`.
- A prefab entity overrides `TryGetBody` or `TryGetBody2D` and returns a `BodyDesc` or `BodyDesc2D`. The backend places it at the entity's position and rotation.

After the spawn, `StandaloneEntity.Body` and `Body2D` return the body, and `Position` and `Rotation` read and write it, so the transform sync and game code see the simulated pose. Despawning removes the body.

```csharp
public override bool TryGetBody2D(out BodyDesc2D body)
{
    var collider = new ColliderDesc2D(BodyShape2D.Capsule(0.3f, 0.4f), Vector2.Zero, 0f, ColliderMaterial.Default, 0, false);
    body = new BodyDesc2D(BodyKind.Dynamic, new[] { collider }, Vector2.Zero, 0f, 1f, new BodyMotion2D(BodyLocks2D.Rotation, 1f, 0f, 0f));
    return true;
}
```

The description has to match the one the Unity client builds from the prefab's colliders, or the server and the predicting client simulate different bodies. One way to keep them equal is to export the descriptions from the Editor with `BodyDescriptions.TryDescribe2D` into a file that the console server reads, as the [Red Runner example](../examples/redrunner/rapier-and-console/step-12-level-catalogue.md) does.

## Level geometry and unowned bodies

`RapierScenes` has the same runtime members as `NetworkPhysics`, by scene id instead of `Scene`: `AddStatic(sceneId, colliders)`, `AddStatic2D`, `RemoveStatic`, `AddBody(sceneId, body)`, `AddBody2D`, `RemoveBody` and `RemoveBody2D`. `WorldOf(sceneId)` and `WorldOf2D(sceneId)` return the worlds, whose `Touching` method reads contact sets as described in [Rapier bodies and colliders](../rapier/bodies.md#reading-the-worlds). Build runtime geometry in the same order as the clients do.

The console backend does not run the contact event components, which are Unity components. Server rules that depend on contacts read the contact sets of the worlds.

## Prediction on console clients

A console client created with a `RapierScenes` predicts and rolls back its entities like a Unity client, through `IPhysicsScenes.HistoryOf`, `PlaceProxy` and `EndProxy`.
