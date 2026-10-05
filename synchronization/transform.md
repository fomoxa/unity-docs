# NetworkTransform

`NetworkTransform` sends the server's transform of a GameObject to every observer and moves the client's copy smoothly between the received values. It is a `NetworkBehaviour`, so it sits on a `NetworkObject` or on one of its children.

## When to use it

Add it to objects that the server moves, such as other players' characters, projectiles and moving platforms. An object that its owner predicts needs one too, so that the other clients see it move, although the owner itself ignores it while predicting.

## Basic usage

1. Add `NetworkTransform` to the prefab, on the GameObject whose transform should be replicated.
2. Choose which parts to sync. Position and rotation are on by default, scale is off.
3. Move the object on the server.

No code is needed beyond moving the object.

## How it works

The server samples the local position, rotation and scale after every tick.

```text
server tick   ... 10    11    12    13    14    15 ...
moving             ●─────●─────●─────●
transform update   U     U     U     U          unreliable, carries tick 10, 11, 12, 13
stopped                                    S    reliable settle with the final values
```

While the object moves, the server sends an update for each tick in which a synced part moved more than its threshold. These updates are unreliable and carry the tick. When the object stops, the server sends one settle message on the reliable channel with the exact final values, so a lost update can never leave an object resting in the wrong place. A client also gets a settle with the current values when the object spawns and whenever it starts observing the object.

An update contains only the parts that changed, and the client never applies a part it has not received yet.

## Server behavior

The server only reads the transform, so you can move it any way you like, whether from code, from physics or from an animation.

## Client behavior

Clients keep a short list of received snapshots and show the object Interpolation Ticks (2 by default) behind the newest one, interpolating position and scale linearly and rotation spherically. A settle replaces the list and puts the object at its values at once.

The client applies the values to the local position, rotation and scale, so the object must have the same parent on the server and on the clients for the values to mean the same thing.

## Interpolation

Interpolation shows remote objects slightly in the past, so that there is always a next snapshot to move towards. More Interpolation Ticks give smoother movement on a lossy network at the cost of more delay, while fewer give less delay but more visible stutter when updates are lost.

Unlike [prediction](../concepts/prediction.md), interpolation does not use input and makes no guess about where the object will be.

## Prediction

While the owner's client predicts an object, it ignores that object's transform updates and lets its own simulation move it. Other clients interpolate the object as usual.

A correction can make the predicted object jump. To hide the jump, put the object's visible parts on a child GameObject and assign that child to the Visual field. After each correction the package keeps the child where it was on screen and moves it back to its resting place over Smoothing Time seconds (0.1 by default), or snaps it there at once if Smoothing Time is 0.

## Teleporting

Call `Teleport()` on the server after moving the object to its new place:

```csharp
transform.position = respawnPoint;
GetComponent<NetworkTransform>().Teleport();
```

Clients then jump to the new values instead of interpolating across the distance, and ignore updates from before the teleport that arrive late. `Teleport()` does nothing on a client or before the object has spawned.

For an object with a physics body, set the body's position as well, as described in [PhysicsBody](../physics/physics-body.md#teleporting).

## Configuration

| Field | Default | Meaning |
|---|---|---|
| Sync Position | on | Replicate the local position |
| Sync Rotation | on | Replicate the local rotation |
| Sync Scale | off | Replicate the local scale |
| Position Threshold | 0.01 | Distance a position must move before an update includes it |
| Rotation Threshold | 0.1 | Angle in degrees a rotation must turn before an update includes it |
| Scale Threshold | 0.01 | Change a scale must make before an update includes it |
| Interpolation Ticks | 2 | How many ticks behind the newest snapshot clients show the object |
| Visual | none | A child transform that is smoothed after prediction corrections |
| Smoothing Time | 0.1 | Seconds over which the Visual returns to its rest position |

`Visual` and `SmoothingTime` can also be set from code, while the sync flags and `InterpolationTicks` are read-only there.

## Limitations

Transforms flow from the server to clients only, and a client can move a networked object for others only through RPCs or input. Values are replicated in local space, and re-parenting a replicated object at run time is not replicated. Thresholds apply per update, so movement smaller than a threshold is only sent once the object stops. On a host, the server's transform is shown as it is, without interpolation for the host's own view.

[Replication](../concepts/replication.md) explains how transform messages fit with the other messages, the [prediction overview](../prediction/overview.md) shows `NetworkTransform` on a predicted character, and the [components reference](../reference/components.md#networktransform) lists its members.
