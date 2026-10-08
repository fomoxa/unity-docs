# Installation

This page adds the package to a Unity project and sets up code generation. When you finish, the project compiles together with the generated code and is ready for the [first project](first-project.md) tutorial.

## Requirements

The package needs Unity 6000.5 or later, running in a Windows x64 or Linux x64 Editor. The `fomoxac` code generator is bundled for these two platforms only, so in the macOS Editor generation stops with `the fomoxac binary for this editor platform is missing`.

The package also depends on the built-in Physics, Physics 2D and Animation modules. Because it declares them as dependencies, Package Manager enables them for you.

## Add the package

### From a Git URL

In Unity, open Window > Package Manager, click the + button, choose Install package from git URL and enter:

```
https://github.com/fomoxa/com.fomoxa.networking.git
```

To pin a version, add a branch, tag or commit after `#`, for example `https://github.com/fomoxa/com.fomoxa.networking.git#<tag>`.

### From a local folder

To work against a local copy, choose Install package from disk in the same menu and select the package's `package.json`, and Package Manager adds a `file:` entry to `Packages/manifest.json`. You can also write that entry yourself. A path relative to the project's `Packages` folder works on every machine that has the same folder layout:

```json
"com.fomoxa.networking": "file:../../com.fomoxa.networking"
```

## Create the settings asset

The package reads the location of your models, and the folder it writes generated code to, from a `FomoxaSettings` asset.

1. Create a folder for models, for example `Assets/Network/Models`, and one for generated code, for example `Assets/Network/Generated`.
2. Right-click a folder in the Project window and choose Create > Fomoxa > Settings.
3. In the new asset, set Models Folder to `Assets/Network/Models` and Generated Folder to `Assets/Network/Generated`. The defaults are `Assets/Models` and `Assets/Generated`.

Keep exactly one `FomoxaSettings` asset in the project. If there are two, the package logs `more than one FomoxaSettings asset exists; keep exactly one` and generates nothing.

The models folder must exist before the first generation even while it is empty, because `fomoxac` stops when a source folder is missing. Git does not keep empty folders, so put an empty `.gitkeep` file in it; Unity ignores files whose names start with a dot.

## Generate the code

The package generates code after every script compilation, and you can also run it by hand with Tools > Fomoxa > Generate. Each generation writes these files:

| Path | Contents |
|---|---|
| `fomoxa.toml` | The `fomoxac` configuration, written from the settings asset. Edit the asset, not this file. |
| `FomoxaSystemModels/` | The package's own models, copied out of the package so that `fomoxac` can read them. The folder is outside `Assets`, so Unity does not compile it. |
| `.fomoxa/` | The schema files that `fomoxac` writes. |
| Generated Folder | A codec and an adapter for every model, `NetSchema.cs`, `FomoxaAdapters.cs`, `FomoxaUnityRegistration.cs`, the prefab list and constants, the scene list and constants, a scene file for each network scene, and the `RpcModels` and `UnityCodecs` subfolders. |

Commit all of them so that a fresh clone compiles before the generator has run.

You never call registration code yourself. `FomoxaUnityRegistration.cs` registers the generated schema and codecs when the player or Play Mode starts, and a `NetworkManager` picks them up from there.

## Check the result

After Unity finishes compiling, the Console should show no error starting with `[Fomoxa]`, and the Generated Folder should contain `NetSchema.cs`, `FomoxaAdapters.cs` and adapters such as `MessageBundleNetAdapter.cs`. If generation failed, see [troubleshooting](troubleshooting.md#code-generation-fails).

The generated code lives in a namespace named after the last folder of the Generated Folder path. For `Assets/Network/Generated` that namespace is `Generated`, which is why the examples in this documentation start with `using Generated;`.

Continue with [your first project](first-project.md).
