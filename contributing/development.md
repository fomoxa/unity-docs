# Development

This page describes the layout of the package and how to run its tests from a Unity project. The documentation itself is not part of the package and is kept in a separate repository.

## Package layout

| Folder | Contents |
|---|---|
| `Runtime/Core` | Layer 1, assembly `Fomoxa.Unity.Core`; no Unity references |
| `Runtime/Core/SystemModels` | The package's own models, copied into projects for code generation |
| `Runtime/Unity` | Layer 2, assembly `Fomoxa.Unity`, and `FomoxaWebSocket.jslib` |
| `Runtime/Unity/Generators` | The RPC source generator, built as a DLL |
| `Runtime/Plugins` | `Fomoxa.Net.dll` and `Fomoxa.Attributes.dll` |
| `Editor` | Assembly `Fomoxa.Unity.Editor`: code generation, ids, build checks |
| `Tests/Core`, `Tests/Unity`, `Tests/Fixtures` | Test assemblies, compiled only when the project includes the package's tests |
| `Tools~/fomoxac` | The `fomoxac` binaries; Unity does not import folders ending in `~` |

## Running the tests

The test assemblies use the `UNITY_INCLUDE_TESTS` define, so Unity only compiles them when the project lists the package as testable. To do that, add this to the project's `Packages/manifest.json`:

```json
"testables": [
  "com.fomoxa.unity"
]
```

Then open Window > General > Test Runner and run the EditMode tests. The tests in `Fomoxa.Unity.Core.Tests` cover layer 1, while those in `Fomoxa.Unity.Tests` create `NetworkManager` components, transports and physics scenes in the Editor.

## Code style

The package code has no comments and relies on names to carry the meaning. Match the style of the file you change.

[Architecture](../concepts/architecture.md) explains how the layers in this layout fit together, and [documentation](documentation.md) covers working on these pages.
