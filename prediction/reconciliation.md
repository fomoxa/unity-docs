# Reconciliation

Reconciliation is how the owner's client corrects its prediction. After applying an input, the server captures the object's state and sends it to the owner together with the tick. The client compares it with the state it predicted for the same tick, and if the two differ, it restores the server's state and replays its input for every later tick.

## Declaring

The state to compare goes in `[NetworkReconcile]` fields, next to the [input fields](input.md):

```csharp
using Fomoxa.Networking;
using Fomoxa.Unity;
using UnityEngine;

public sealed partial class Glider : NetworkBehaviour
{
    [NetworkInput]
    private float thrust;

    [NetworkReconcile(Tolerance = 0.01f)]
    private Vector3 position;

    [NetworkReconcile(Tolerance = 0.01f)]
    private float speed;

    protected override void OnGatherInput()
    {
        thrust = Input.GetAxisRaw("Vertical");
    }

    protected override void OnApplyInput(InputContext context)
    {
        speed = Mathf.Max(0f, speed + thrust * 0.1f);
        transform.position += transform.forward * speed * 0.02f;
    }

    protected override void OnCaptureState()
    {
        position = transform.position;
    }

    protected override void OnRestoreState()
    {
        transform.position = position;
    }
}
```

The package gathers the reconcile fields into a model named after the class followed by `Reconcile`, `GliderReconcile` here, next to the input model. Give it another name with `[NetworkReconcileModel("...")]` on the class. Changing its fields follows the rules of [state](../synchronization/state.md#changing-the-fields). A class with `[NetworkReconcile]` fields needs at least one `[NetworkInput]` field, and a field carries either attribute, not both.

| Method | Runs | Does |
|---|---|---|
| `OnCaptureState()` | After each applied input on the server; after each predicted or replayed tick on the client. The package copies the fields after it returns | Copies state that lives outside the fields, such as a transform or a physics body, into them |
| `OnRestoreState()` | On the client, when a correction starts, after the package wrote the server's state into the fields | Copies the fields back to the transform or body |

Both are optional. A field that `OnApplyInput` changes directly, such as `speed` above, needs neither.

## What goes in the reconcile fields

The reconcile fields must hold everything that `OnApplyInput` reads and changes and that carries over from one tick to the next, such as a position, a velocity, a cooldown timer or a damping velocity. If something is missing, a replay starts from a different value than the server did, and the next comparison fails again.

## Comparing

Without any `Tolerance`, the package compares the encoded bytes of the two states, so any difference counts as a mismatch, including floating-point noise in the last bit. Once a field has a `Tolerance`, the package compares field by field, and the prediction matches when every field does:

| Field | Matches when |
|---|---|
| `float`, `double` with `Tolerance = t` | The values differ by at most `t` |
| `Vector2`, `Vector3`, `Vector4` with `Tolerance = t` | Each component differs by at most `t` |
| `Quaternion` with `Tolerance = t` | The angle between the two is at most `t` degrees |
| A model, without `Tolerance` | Its encoding is the same |
| Any other field without `Tolerance` | The values are equal |

`Tolerance` on any other type is a compile error, `FOMOXA020`.

## Correction and replay

<figure><img src="../.gitbook/assets/diagrams/reconcile-replay.svg" alt="The client has predicted ticks 10 to 14 and is at tick 14 when the server state for tick 11 arrives. The states for tick 11 do not match. The client restores the server state of tick 11 and replays ticks 12, 13 and 14. Each replayed tick calls OnApplyInput with context.Replaying set to true, then OnCaptureState. Afterwards OnReconciled(11) runs and ReconcileCount goes up by one."><figcaption><p>A correction at tick 11 while the client is already at tick 14.</p></figcaption></figure>

The client keeps the inputs and states of the last Prediction History ticks (64 by default). A replay covers the ticks from the corrected one up to the newest predicted tick, using the inputs the client recorded, and after the correction the package calls `OnReconciled(tick)` on the behaviour and increases its `ReconcileCount`.

When several states arrive between two ticks, the client handles only the newest one. A state for a tick that the client has no prediction for counts as a mismatch.

During a replay, `NetworkBehaviour.IsReplaying` and `ClientManager.IsReplaying` are true, and so is `InputContext.Replaying` in `OnApplyInput`.

## Starting and stopping prediction

The owner's client starts predicting when the first reconcile state arrives from the server, and until then it only sends input.

When the object loses its owner or changes owner, the previous owner stops predicting it, clears its history and goes back to following `NetworkTransform`. The new owner starts predicting once the server has sent it a state.

## How often the server sends

The server sends the state every Reconcile Interval ticks (1 by default), for ticks in which it applied an input. A higher interval saves bandwidth, and corrections become less frequent but larger.

## Showing corrections smoothly

A correction moves the object at once. To hide that, assign a child holding the visible parts to the Visual field of the object's `NetworkTransform`. The package then keeps that child where it was on screen and blends it back over Smoothing Time, as described in [NetworkTransform](../synchronization/transform.md#prediction).

## Diagnosing frequent corrections

`ReconcileCount` should stay low as long as nothing unexpected happens. When it keeps growing, the usual causes are:

- `OnApplyInput` uses `Time.deltaTime` instead of `TimeManager.TickDelta`.
- `OnApplyInput` reads data that differs between server and client, such as other objects or unseeded random numbers.
- The reconcile fields miss state that carries over between ticks.
- `Tolerance` is missing or too small.
- Input arrives late at the server and is repeated, which `ServerManager.DroppedInputsOf` shows.

[Deterministic simulation](../concepts/deterministic-simulation.md) explains why each of these makes the two sides differ.

To see how far each correction moves the object, subscribe to `NetworkTransform.OnCorrected` or turn on Draw Corrections, as described in [debugging](../advanced/debugging.md#prediction-corrections). [Network simulation](../connections/transports/simulated.md) adds latency and loss in the Editor, so corrections show up before you test on a real network.

## With physics

When the object moves with a `Rigidbody` or `Rigidbody2D` and physics simulation is on, a correction also rolls the physics worlds back, as described in [rollback with physics](rollback.md).

Reconciliation builds on [input](input.md), and the [prediction overview](overview.md) shows both in a complete character. [NetworkBehaviour](../objects/network-behaviour.md) lists `OnReconciled` and the other callbacks.
