# The project

A console server is an ordinary .NET console project that compiles source files from the package and from the Unity project instead of referencing built assemblies. This page sets one up.

## Folder layout

The project needs three folders on disk: the `com.fomoxa.networking` package, the Unity project, and the console project. The examples on this page keep them side by side:

```text
com.fomoxa.networking/        clone of https://github.com/fomoxa/com.fomoxa.networking
MyGame/                       the Unity project
    Assets/Network/Models/
    Assets/Network/Generated/
    Server~/                  the console project
        MyGame.Server.csproj
        Program.cs
```

A folder whose name ends in `~` is ignored by Unity, so `Server~` inside the Unity project does not get imported and its `bin` and `obj` folders do not disturb the Editor.

## The project file

```xml
<Project Sdk="Microsoft.NET.Sdk">

  <PropertyGroup>
    <OutputType>Exe</OutputType>
    <TargetFramework>net8.0</TargetFramework>
    <LangVersion>9.0</LangVersion>
    <Nullable>disable</Nullable>
    <EnableDefaultCompileItems>false</EnableDefaultCompileItems>
    <Game>..</Game>
    <Core Condition="'$(Core)' == ''">$(Game)/../com.fomoxa.networking</Core>
  </PropertyGroup>

  <ItemGroup>
    <Compile Include="$(Core)/Runtime/Core/**/*.cs" />
    <Compile Include="$(Core)/Standalone~/**/*.cs" />
    <Compile Include="$(Game)/Assets/Network/Models/**/*.cs" />
    <Compile Include="$(Game)/Assets/Network/Generated/**/*.cs" />
    <Compile Include="*.cs" />
  </ItemGroup>

  <ItemGroup>
    <None Include="$(Game)/Assets/Network/Generated/*.fomoxascene" Link="Scenes/%(Filename)%(Extension)" CopyToOutputDirectory="PreserveNewest" />
  </ItemGroup>

  <ItemGroup>
    <Reference Include="Fomoxa.Attributes">
      <HintPath>$(Core)/Runtime/Plugins/Fomoxa.Attributes.dll</HintPath>
    </Reference>
    <Reference Include="Fomoxa.Net">
      <HintPath>$(Core)/Runtime/Plugins/Fomoxa.Net.dll</HintPath>
    </Reference>
    <Reference Include="Fomoxa.Net.WebSockets">
      <HintPath>$(Core)/Runtime/Plugins/Fomoxa.Net.WebSockets.dll</HintPath>
    </Reference>
    <PackageReference Include="BouncyCastle.Cryptography" Version="2.6.2" />
  </ItemGroup>

</Project>
```

| Part | Why |
|---|---|
| `EnableDefaultCompileItems` false | The project lists its sources itself, so it does not pick up the Unity project's scripts |
| `Core` | The folder of the package. The condition lets you pass another one with `-p:Core=<folder>` |
| `Runtime/Core/**` and `Standalone~/**` | Layer 1 and the console backend, as source |
| Models and Generated | Your models and the generated codecs, adapters, `FomoxaPrefabs` and `FomoxaScenes` constants |
| `*.fomoxascene` | The scene files, copied to a `Scenes` folder next to the executable |
| `Fomoxa.Attributes`, `Fomoxa.Net`, `Fomoxa.Net.WebSockets` | The bundled DLLs, referenced from the package |
| `BouncyCastle.Cryptography` | The NuGet package of the BouncyCastle DLL in `Runtime/Plugins`, at the same version; encrypted UDP and client TLS use it |

The generated `FomoxaUnityRegistration.cs` compiles to nothing outside Unity, so the console program calls `FomoxaAdapters.RegisterAll` itself, as the next page shows. Models that use Unity types such as `UnityEngine.Vector3`, and their codecs in `UnityCodecs/`, cannot compile without Unity. Give the models that the console server needs plain fields instead.

## Game code shared with Unity

Code that both the Unity game and the console server run, such as movement rules or a level generator, can live in an assembly of the Unity project whose assembly definition sets `noEngineReferences`. The console project then compiles that folder too:

```xml
<Compile Include="$(Game)/Assets/Scripts/Simulation/**/*.cs" />
```

Such code must not use `UnityEngine` and must be written in C# 9.

## RPCs declared with attributes

The RPC source generator handles `EntityBehaviour` as well as `NetworkBehaviour`. To use `[ServerRpc]` and `[ClientRpc]` in the console project, reference it as an analyzer:

```xml
<ItemGroup>
  <Analyzer Include="$(Core)/Runtime/Core/Generators/Fomoxa.Networking.Generators.dll" />
</ItemGroup>
```

Without it, register the RPCs in `OnRegisterRpcs`, as described in [RPCs](../messaging/rpc.md).

## Building and running

```
dotnet run --project Server~ -c Release
```

With the package elsewhere, pass its folder: `dotnet run --project Server~ -c Release -p:Core=/path/to/com.fomoxa.networking`. Each time the models or scenes change in Unity, let the Editor generate the code and export the scene files, then build the console project again; a server and a client built from different models fail the handshake with `SchemaConflict`.

[The runtime](runtime.md) writes `Program.cs`.
