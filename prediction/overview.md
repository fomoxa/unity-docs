# Prediction overview

Client-side prediction lets the owner of an object apply its own input at once instead of waiting a round trip for the server. The server applies the same input when it arrives and sends back its result, and the client corrects itself if the results differ. [Prediction](../concepts/prediction.md) explains the idea, and this page builds a predicted character step by step.

## Requirements

The `NetworkManager` must use Timing Mode Tick, and the object needs a `NetworkBehaviour` that registers an input model and a reconcile model in `OnRegisterInput`. The object also needs an owner, because only the owning client predicts and the server accepts the object's input only from the owner.

## A predicted character

The character needs two models. The first carries the input of one tick:

```csharp
using Fomoxa;

namespace MyGame.Network.Models
{
    [Network]
    [Codec("net")]
    public class MoveInput
    {
        [Network("f32")]
        [Codec("net")]
        public float X { get; set; }

        [Network("f32")]
        [Codec("net")]
        public float Z { get; set; }
    }
}
```

The second holds the state that the client compares with the server's after each tick:

```csharp
using Fomoxa;
using UnityEngine;

namespace MyGame.Network.Models
{
    [Network]
    [Codec("net")]
    public class MoveState
    {
        [Network("Vector3")]
        [Codec("net")]
        public Vector3 Position { get; set; }
    }
}
```

Neither model needs `[NetworkChannel]`, because the package carries input and reconcile states inside its own messages.

The behaviour ties them together:

```csharp
using Fomoxa.Unity;
using Generated;
using MyGame.Network.Models;
using UnityEngine;

public sealed class PredictedMover : NetworkBehaviour
{
    private const float Tolerance = 0.01f;

    [SerializeField] private float speed = 5f;

    private NetworkManager manager;

    private void Awake()
    {
        manager = FindFirstObjectByType<NetworkManager>();
    }

    protected override void OnRegisterInput(NetworkInput input)
    {
        input.Use(MoveInputNetAdapter.Instance, Gather, Apply);
        input.Reconcile(MoveStateNetAdapter.Instance, Capture, Restore, Matches);
    }

    private void Gather(MoveInput input)
    {
        input.X = Input.GetAxisRaw("Horizontal");
        input.Z = Input.GetAxisRaw("Vertical");
    }

    private void Apply(MoveInput input, InputContext context)
    {
        Vector3 direction = Vector3.ClampMagnitude(new Vector3(input.X, 0f, input.Z), 1f);
        transform.position += direction * speed * (float)manager.TimeManager.TickDelta;
    }

    private void Capture(MoveState state)
    {
        state.Position = transform.position;
    }

    private void Restore(MoveState state)
    {
        transform.position = state.Position;
    }

    private static bool Matches(MoveState server, MoveState predicted) =>
        Vector3.Distance(server.Position, predicted.Position) <= Tolerance;
}
```

The example reads the legacy Input Manager; with the Input System package, read your input action in `Gather` instead.

Put `NetworkObject`, `NetworkTransform` and `PredictedMover` on the player prefab, and spawn it with the player's peer id as its owner.

## What happens each tick

| Who | What |
|---|---|
| Owner's client | Calls `Gather` for its prediction tick and sends the input together with the previous inputs. Once it predicts, it also calls `Apply` with that input and records the state from `Capture`. It starts predicting when the first state from the server arrives. |
| Server | When its tick reaches the input's tick, calls `Apply` with it, then `Capture`, and sends the captured state to the owner. |
| Owner's client | When the server's state for a tick arrives, compares it with its record of that tick using `Matches`. On a mismatch it calls `Restore` with the server's state and calls `Apply` again for every later tick it has input for. |
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
