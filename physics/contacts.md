# Contact events

Unity raises `OnCollisionEnter`, `OnTriggerEnter` and their exit counterparts from inside each physics step. When a client replays ticks during reconciliation, the same steps run again, and Unity would raise the same events a second time. The package's contact components avoid that by raising enter and exit events once per tick, and after a replay only for what changed.

| Component | Colliders on its GameObject | Reports |
|---|---|---|
| `NetworkCollision` | 3D, non-trigger | Colliders touching them |
| `NetworkTrigger` | 3D, trigger | Colliders inside them |
| `NetworkCollision2D` | 2D, non-trigger | Colliders touching them |
| `NetworkTrigger2D` | 2D, trigger | Colliders inside them |

## Basic usage

Add the component to the GameObject that has the colliders and subscribe to its events:

```csharp
using Fomoxa.Unity;
using UnityEngine;

[RequireComponent(typeof(NetworkTrigger2D))]
public sealed class Pickup : MonoBehaviour
{
    private void OnEnable()
    {
        GetComponent<NetworkTrigger2D>().OnEnter += Collect;
    }

    private void OnDisable()
    {
        GetComponent<NetworkTrigger2D>().OnEnter -= Collect;
    }

    private void Collect(Collider2D other)
    {
        Debug.Log($"{other.name} entered {name}");
    }
}
```

| Member | Meaning |
|---|---|
| `OnEnter` | A collider started touching, or entered the trigger |
| `OnExit` | A collider stopped touching, or left the trigger |
| `Touching` | The colliders touching now, as of the last published tick |

Within one tick, exits are raised before enters. An exception in a handler is logged and does not keep the other handlers from running.

## How it works

When a `NetworkManager` steps the component's physics world, the component ignores Unity's callbacks and instead queries, after each step, which colliders touch its own. `NetworkCollision` and `NetworkTrigger` run overlap queries with the shape of each of their colliders, grown by Additional Size. These queries respect the layer collision matrix and `Physics.IgnoreCollision`, and skip colliders of the same `Rigidbody`. `NetworkCollision2D` and `NetworkTrigger2D` ask Unity's 2D physics for the current contacts of their colliders.

At the end of the tick the result is compared with the previously published set, and the differences are raised as events.

On the owner's client the components also record the touching set of every tick. A replay restores the set of the corrected tick, updates it as the worlds step again and publishes once after the replay. An event that already fired for the original run does not fire again, and a contact that the replay removed fires an exit.

When no `NetworkManager` steps the world, for example with Simulate Physics off, the components simply pass Unity's own callbacks through as `OnEnter` and `OnExit`.

## Configuration

| Field | On | Default | Meaning |
|---|---|---|---|
| Additional Size | `NetworkCollision` | `Physics.defaultContactOffset` × 2 | Distance by which the query shapes are grown, so that resting contacts count as touching |
| Additional Size | `NetworkTrigger` | 0 | Distance by which the query shapes are grown |

## Where events fire

The components raise events on every side that runs them, whether server, client or host. Game rules that affect other players, such as collecting a pickup, should act on the server, while a client uses the events for local effects.

## Limitations

3D queries handle box, sphere and capsule colliders exactly, and fall back to the bounding box for other collider types. The components only see colliders on their own GameObject, gathered when the component is enabled.

Contact components depend on the stepping described in the [physics overview](overview.md) and on the replay described in [rollback with physics](../prediction/rollback.md). The [components reference](../reference/components.md#contact-components) lists their members.
