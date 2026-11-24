# State

State is data of a `NetworkBehaviour` that the server keeps in sync on every observer, such as health, a score or whether a door is open. You mark fields with `[NetworkState]`, the server changes them, and at the end of each tick the package sends what changed. Clients receive the new values into the same fields and can get a callback with the previous value.

## When to use it

State suits values that clients must always know, including clients that join later. One-off events are better sent as an [RPC](../messaging/rpc.md), and movement is handled by [`NetworkTransform`](transform.md). Data that grows and shrinks, such as an inventory, fits a [collection](collections.md) better: an array in a state field is sent in full whenever it changes length.

## Basic usage

```csharp
using Fomoxa.Networking;
using Fomoxa.Unity;
using UnityEngine;

public sealed partial class Damageable : NetworkBehaviour
{
    [SerializeField] private ushort maxHealth = 100;

    [NetworkState(OnChanged = nameof(OnHealthChanged))]
    private ushort health;

    [NetworkState]
    private ushort max;

    public ushort Current => health;

    private void Awake()
    {
        max = maxHealth;
        health = maxHealth;
    }

    public void TakeDamage(ushort amount)
    {
        health = (ushort)Mathf.Max(0, health - amount);
    }

    private void OnHealthChanged(ushort previous, ushort current)
    {
        Debug.Log($"{name}: {previous} -> {current} of {max}");
    }
}
```

Call `TakeDamage` on the server, and the clients' `health` changes at the end of that tick, after the network delay.

The class must be `partial`, and so must every class that contains it, because a source generator in the package writes the code that copies the fields.

## State fields

A state field is an instance field that is not `readonly`, and it may be private. Its type decides how it travels, as for [RPC parameters](../messaging/rpc.md#parameter-types): primitives, the package's Unity types and `[Network]` models are recognized, and `[NetworkState("...")]` gives any field a wire type, as in `[NetworkState("f16")] private float speed;`.

`OnChanged` names a method of the same class with the signature `void M(T previous, T current)`, where `T` is the field's type. After an update arrives, the package first writes every field, then calls the callbacks of the fields whose value changed, so a callback can read the other fields' new values. A primitive, Unity type or `string` counts as changed when it is not equal to the previous value, and a model when its encoding differs. When the field holds a model, `previous` is only valid during the callback, because the next update is decoded into the same instance.

## The generated model

The package gathers the state fields of a class into one model, which it generates in the `StateModels` subfolder of the Generated Folder. The model is named after the class followed by `State`, `DamageableState` in the example, and has one field per state field, named after the field with an upper-case first letter. Give it another name with `[NetworkStateModel("...")]` on the class.

When you add, remove or change a state field, the package generates the model after the next compilation and Unity compiles again. Entering Play mode and building a player are blocked as long as a generated model is missing or out of date, with a message that ends in `run Tools > Fomoxa > Generate and commit the generated files`.

### Changing the fields

The model carries the fields by position, from the base class down, in declaration order. Fomoxa lets two builds work together when their field lists differ only at the end, so where you make a change decides whether an older build of the game still connects:

| Change | An older build |
|---|---|
| Add a field after the last state field of the class | Still connects. It ignores the new field, and a newer client of an older server reads zero, `false` or an empty value in it |
| Remove the last state field | Still connects |
| Insert a field before another one, reorder fields, change a field's type or rename it | Cannot connect |
| Add a field to a base class | Cannot connect, because the fields of the base class come first |
| Rename the class | Does not work with the new build, unless `[NetworkStateModel("...")]` keeps the model name |

When the package generates a changed model, the Console shows a `[Fomoxa]` warning with the model's name, the fields that changed and a verdict. `COMPATIBLE: append-only field (1 appended at the end)` means older builds still connect. A verdict that starts with `BREAKING:`, such as `BREAKING: field inserted; every field after it moved`, means you must ship a new server and new clients together.

A class derived from a behaviour with state fields has its own model, which holds the fields of the whole chain from the base class down, in declaration order. A base class compiled in another assembly must also be compiled with the package's generator.

## How it works

<figure><img src="../.gitbook/assets/diagrams/state-sync.svg" alt="On the server, every tick: your code changes health, the server encodes the state after OnTick and OnPostTick and compares the bytes with the state it sent last time. If they are the same, nothing is sent. If they differ, the server sends the full state or a delta, whichever is smaller, reliable and ordered. Each observing client decodes it into your fields and calls OnChanged with the previous and current value. A delta the client cannot apply is dropped, the client sends StateResync and the server answers with the full state."><figcaption><p>The server sends state only when its encoded bytes change.</p></figcaption></figure>

After the tick's `OnTick` and `OnPostTick` events, the server copies the state fields of every behaviour into its model, encodes it, compares the bytes with what it sent last, and sends the state to every observer if they differ.

Because the comparison works on the encoded bytes, any change of a state field is detected without you having to mark anything dirty. A field without `[NetworkState]` is neither compared nor sent. A behaviour can instead choose to [mark its changes](#marking-changes).

## Marking changes

Encoding every state every tick costs server time, even for behaviours whose state rarely changes. A behaviour with a large state that stays the same most of the time can set `OnlyWhenDirty` on the class:

```csharp
using Fomoxa.Networking;
using Fomoxa.Unity;

[NetworkStateModel(OnlyWhenDirty = true)]
public sealed partial class Scoreboard : NetworkBehaviour
{
    [NetworkState]
    private uint red;

    [NetworkState]
    private uint blue;

    public void Score(uint redPoints, uint bluePoints)
    {
        red += redPoints;
        blue += bluePoints;
        SetStateDirty();
    }
}
```

The server then encodes and compares that state only in a tick after the behaviour called `SetStateDirty()`, so call it on the server after each change. A change made without `SetStateDirty()` is not sent. In the Editor and in Development builds, the server logs a warning when such a change has gone unsent for State Mark Warning Seconds on the `NetworkManager`, 2 by default; [debugging](../advanced/debugging.md#forgotten-state-marks) describes the check. Clients keep the last state sent, and a client that starts observing later receives that same state in its spawn message. The state captured at `Spawn` needs no call. Without `OnlyWhenDirty`, which is the default, `SetStateDirty()` does nothing and the server compares the state every tick.

## Server behavior

Change the fields on the server only. The server gets no callback for its own changes; `OnChanged` runs on clients.

The spawn message contains the state captured at `Spawn`, so set the initial values before calling `Spawn`, for example in `Awake`. A client that joins later receives the state as it was at the last tick.

## Client behavior

The initial state is already in the fields before `OnStartClient` runs, and `OnChanged` does not run for it. For every later change, the package writes the new values into the fields and calls `OnChanged` for the fields that changed.

A change made to a state field on a client is not sent, and the next update overwrites it. On a host the fields are shared with the server and are not written again, but `OnChanged` still runs on the host's client, with `current` holding the field's value.

## Delta encoding

When the encoded state has the same length as the last one sent, the server computes a delta, which is the XOR of the two encodings with runs of unchanged bytes compressed. If the delta is smaller than the full state, the server sends the delta instead, and clients apply it to the last state they received.

A client that cannot apply a delta, for example because it is out of step, drops it, asks the server for the full state and ignores further deltas until that full state arrives. This recovery is automatic.

Fixed-size fields keep the encoding length stable, which lets deltas apply. A change of length, such as a longer string or a longer array, makes the server send the full state.

## Errors

The source generator reports these compile errors:

| Id | Meaning |
|---|---|
| `FOMOXA012` | A state field is `static`, `const` or `readonly` |
| `FOMOXA013` | `OnChanged` does not name a method `void M(T previous, T current)` of the class |
| `FOMOXA014` | The class, or a class containing it, is not `partial` |
| `FOMOXA018` | A field carries more than one of `[NetworkState]`, `[NetworkInput]`, `[NetworkReconcile]` |

Generating the model reports, in the Console, a field whose type has no wire type, a field outside a `NetworkBehaviour`, two fields that give the same model field, and two classes that give the same model name.

## Limitations

All the state fields of a behaviour form one model, so data that needs more than one goes into several behaviours or into [collections](collections.md) next to the state fields. State is sent at most once per tick, which merges all changes made within one tick. Every observer receives the same state, so data meant for a single client goes in a target RPC instead.

State is declared in a [NetworkBehaviour](../objects/network-behaviour.md), and a field can hold a [model](../messaging/models.md). A [console server](../console-server/runtime.md) uses the generated model to send the same state; name the model with `[NetworkStateModel("...")]` when the behaviour is shared with one. [NetworkAnimator](animator.md) is built on the same mechanism.
