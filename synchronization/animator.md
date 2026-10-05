# NetworkAnimator

`NetworkAnimator` replicates an `Animator` from the server to every observer. It sends the parameters, the triggers, the speed and the weights of the layers, and when an observer first sees the object, also the state each layer is in.

## When to use it

Use it when the server drives the animation, for example for characters that the server moves. If each client can derive the animation from data it already has, such as the velocity of an interpolated transform, setting the parameters locally is cheaper because it costs no bandwidth.

## Basic usage

1. Add `NetworkAnimator` to the GameObject that has the `Animator`. The component requires an `Animator` and adds one if it is missing.
2. On the server, set parameters on the `Animator` as usual.
3. Fire triggers through `NetworkAnimator.SetTrigger`, not `Animator.SetTrigger`:

```csharp
GetComponent<NetworkAnimator>().SetTrigger("Jump");
```

## How it works

`NetworkAnimator` is a `NetworkBehaviour` whose state model, `AnimatorState`, goes through the [state](state.md) mechanism. After every tick the server reads the `Animator`:

| Data | Read with |
|---|---|
| Float parameters | `GetFloat`, rounded to a multiple of Float Step |
| Int and bool parameters | `GetInteger`, `GetBool` |
| Triggers | A counter per trigger, increased by `NetworkAnimator.SetTrigger` |
| Speed | `Animator.speed` |
| Layer weights | `GetLayerWeight` for every layer after the first |
| Layer states | `GetCurrentAnimatorStateInfo(layer).fullPathHash` |

If anything changed, the server sends the new state. Rounding the floats keeps tiny changes from producing a message every tick.

## Client behavior

On every update the client sets the parameters, the speed and the layer weights, and fires each trigger as many times as its counter advanced. When the object first appears on the client, the client also plays each layer's current state, so that a late observer does not start from the entry state. Layer states are applied only at that moment; afterwards the client's own `Animator` moves between states driven by the replicated parameters.

## Matching controllers

The server and the client must use the same Animator Controller layout, meaning the same parameters in the same order with the same types, and the same number of layers. The component computes a layout hash and sends it with the state, and when the hashes differ, the client does not apply the state and logs this once:

`Fomoxa: <name> received Animator state with layout 0x..., but its Animator has layout 0x...; the Animator controllers differ between server and client, so the state is not applied`

## Configuration

| Field | Default | Meaning |
|---|---|---|
| Animator | the component on the same GameObject | The `Animator` to replicate |
| Float Step | 0.01 | Floats are rounded to multiples of this; 0 sends them unrounded |

## Limitations

Animation flows from the server to clients only. Triggers must go through `NetworkAnimator.SetTrigger`, which throws `ArgumentException` for a name that is not a trigger parameter of the controller, because a direct call to `Animator.SetTrigger` on the server is not replicated. Layer states are applied when the object appears, not continuously. On a host the server's `Animator` is the one shown, and nothing is applied a second time.

`NetworkAnimator` relies on [state](state.md), and the [components reference](../reference/components.md#networkanimator) lists its members.
