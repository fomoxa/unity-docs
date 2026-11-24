# Prediction overview

Client-side prediction lets the owner of an object apply its own input at once instead of waiting a round trip for the server. The server applies the same input when it arrives and sends back its result, and the client corrects itself if the results differ. [Prediction](../concepts/prediction.md) explains the idea, and this page builds a predicted character step by step.

## Requirements

The `NetworkManager` must use Timing Mode Tick, and the object needs a `NetworkBehaviour` with `[NetworkInput]` fields and `[NetworkReconcile]` fields. The object also needs an owner, because only the owning client predicts and the server accepts the object's input only from the owner.

## A predicted character

The behaviour keeps the input of one tick in `[NetworkInput]` fields, and the state that the client compares with the server's after each tick in `[NetworkReconcile]` fields:

```csharp
using Fomoxa.Networking;
using Fomoxa.Unity;
using UnityEngine;

public sealed partial class PredictedMover : NetworkBehaviour
{
    [SerializeField] private float speed = 5f;

    [NetworkInput]
    private float x;

    [NetworkInput]
    private float z;

    [NetworkReconcile(Tolerance = 0.01f)]
    private Vector3 position;

    private NetworkManager manager;

    private void Awake()
    {
        manager = FindAnyObjectByType<NetworkManager>();
    }

    protected override void OnGatherInput()
    {
        x = Input.GetAxisRaw("Horizontal");
        z = Input.GetAxisRaw("Vertical");
    }

    protected override void OnApplyInput(InputContext context)
    {
        Vector3 direction = Vector3.ClampMagnitude(new Vector3(x, 0f, z), 1f);
        transform.position += direction * speed * (float)manager.TimeManager.TickDelta;
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

The class must be `partial`. The package gathers the input fields into a model named `PredictedMoverInput` and the reconcile fields into `PredictedMoverReconcile`, both in the `StateModels` subfolder of the Generated Folder, and carries them inside its own messages. `Tolerance` lets each component of `position` differ by up to 0.01 before the client corrects itself.

The example reads the legacy Input Manager; with the Input System package, read your input action in `OnGatherInput` instead.

Put `NetworkObject`, `NetworkTransform` and `PredictedMover` on the player prefab, and spawn it with the player's peer id as its owner.

## What happens each tick

| Who | What |
|---|---|
| Owner's client | Calls `OnGatherInput` for its prediction tick, copies the input fields and sends them together with the previous inputs. Once it predicts, it also calls `OnApplyInput` and records the reconcile fields after `OnCaptureState`. It starts predicting when the first state from the server arrives. |
| Server | When its tick reaches the input's tick, writes that input into the input fields and calls `OnApplyInput`, then `OnCaptureState`, and sends the reconcile fields to the owner. |
| Owner's client | When the server's state for a tick arrives, compares it with its record of that tick, field by field within `Tolerance`. On a mismatch it writes the server's state into the reconcile fields, calls `OnRestoreState`, and calls `OnApplyInput` again for every later tick it has input for. |
| Other clients | Do nothing with input. They see the object through `NetworkTransform`. |

## Expected result

- The owner's character moves in the same frame the key is pressed.
- Other clients see it move, slightly in the past.
- `ReconcileCount` of the owner's `PredictedMover` stays near 0 while the character moves freely.

## Where to go next

| Topic | Page |
|---|---|
| Gathering, sending, repeating and dropping input | [Input](input.md) |
| Capture, restore, compare and replay | [Reconciliation](reconciliation.md) |
| Characters that move with physics | [Rollback with physics](rollback.md) |
| Smoothing corrections on screen | [NetworkTransform](../synchronization/transform.md#prediction) |

## Host mode

The host does not predict its own objects. The server gathers and applies the host's input directly in the same tick, so there is nothing to correct, while remote clients of a host predict normally.
