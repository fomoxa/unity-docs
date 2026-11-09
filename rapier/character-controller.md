# Character controller

The Rapier backend moves a kinematic body the way a character controller does: it slides along walls, climbs steps and slopes up to a limit, snaps to the ground and can push dynamic bodies. It replaces Unity's `CharacterController`, which the backend does not support. The move is part of the simulation, so the server and the predicting client compute it the same way and a replay repeats it.

## Setting up the body

The character is a network object with a kinematic `Rigidbody` or `Rigidbody2D` and exactly one collider that is not a trigger: a box, a sphere or a capsule in 3D, a box, a circle or a capsule in 2D. Trigger colliders on the same body are allowed. The body is not rotated by the move.

## Moving

Call `MoveCharacter` in `apply`, once per tick, with the move you want for this tick:

```csharp
using Fomoxa.Networking;
using Fomoxa.Networking.Rapier;
using Fomoxa.Unity;
using Fomoxa.Unity.Rapier;
using UnityEngine;

public sealed class Walker : NetworkBehaviour
{
    [SerializeField] private NetworkManager manager;
    [SerializeField] private RapierPhysics rapier;
    [SerializeField] private float speed = 4f;
    [SerializeField] private float fallSpeed = 6f;

    private static readonly CharacterSettings2D Settings = default(CharacterSettings2D)
        .WithAutostep(new CharacterAutostep(CharacterLength.Absolute(0.3f), CharacterLength.Absolute(0.2f), true));

    private bool grounded;

    private void Apply(MoveInput input, InputContext context)
    {
        float seconds = (float)manager.TimeManager.TickDelta;
        var desired = new System.Numerics.Vector2(input.X * speed, -fallSpeed) * seconds;
        CharacterMove2D move = rapier.Scenes.MoveCharacter(NetworkObject, NetworkObject.Body2D, desired, seconds, Settings);
        grounded = move.Grounded;
    }
}
```

`MoveInput` stands for the input model of your game, registered in `OnRegisterInput` as in [input](../prediction/input.md); `manager` and `rapier` are the `NetworkManager` and its `RapierPhysics`. The fall here is a constant speed for brevity; a game usually keeps a vertical velocity in its predicted state. The call computes how far the body can go and sets that as its next kinematic position, so the body gets there during the step of the same tick and the `Transform` follows after it. Calling it again before the step computes the move again from the old position and replaces the first one.

The result tells what happened:

| Member | Meaning |
|---|---|
| `Moved` | The movement that was applied, after walls, steps and slopes |
| `Grounded` | The character stands on something at the end of the move |
| `Sliding` | The move went down and the character stands on a slope steeper than `MinSlopeSlideAngle` |

`RapierScenes.MoveCharacter(INetworkEntity owner, PhysicsBody body, Vector3 desired, float seconds, in CharacterSettings settings)` and the `PhysicsBody2D` overload check that `body` belongs to `owner`. A body that no network object owns moves through its world, `rapier.Scenes.WorldOf2D(sceneId).MoveCharacter(body.Handle, desired, seconds, settings)`. Both have overloads with a `QueryFilter` at the end. A console server makes the same calls with its `StandaloneEntity`.

## What the move collides with

- Trigger colliders never block the character.
- The layer collision matrix applies, between the layer of the character's collider and the layers of the others.
- A `QueryFilter` narrows that further with its `LayerMask` and `ExcludeBody`. Its `IncludeTriggers` is not used.
- One-way [platform effectors](effectors.md#platform) let the character through from below and hold it from above.

## Settings

`default(CharacterSettings)` and `CharacterSettings.Default` give Rapier's defaults. Every `With` method returns a copy with one change:

| Setting | Default | Meaning |
|---|---|---|
| `WithUp(up)` | (0, 1, 0) | The up direction, used for slopes, steps and the ground |
| `WithOffset(length)` | 1% of the character's height | A small gap kept between the character and what it touches |
| `WithSlide(bool)` | on | Slide along an obstacle instead of stopping at it |
| `WithAutostep(CharacterAutostep?)` | none | Climb steps up to a maximum height with a minimum width of free floor on top; `CharacterAutostep.Default` is a quarter of the character's height and half of its width, and includes dynamic bodies |
| `WithSlopeAngles(maxClimb, minSlide)` | 45°, 45° | The steepest slope the character climbs, and from which angle it slides down |
| `WithSnapToGround(CharacterLength?)` | 20% of the character's height | Keep the character on the ground when it walks over the top of a slope or down a step; `null` turns it off |
| `WithNormalNudgeFactor(float)` | 0.0001 | How far the character is pushed off a surface to avoid getting stuck |
| `WithPushMass(float)` | 0 | Above 0, dynamic bodies that the move hits get impulses as if the character had this mass |

Angles are in radians. `CharacterLength.Absolute(meters)` is a length in world units and `CharacterLength.Relative(fraction)` a fraction of the character's collider: of its height along the up direction, or of its width across it for the minimum step width. `CharacterSettings2D` has the same members with a `Vector2` up direction.

## Determinism

The same sequence of calls on the same world gives the same result, and a replay after `Load` repeats it bit for bit. The server and a client do not have the same world, because the client places other objects as proxies, so a move can differ between them like any other prediction. The client then corrects on the next reconcile.

A move against kinematic bodies depends on their velocity, which Rapier derives from their next position. A kinematic body that was just created has no velocity until its first step, so a move before that step can differ from the same move after it.
