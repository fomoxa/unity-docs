# Contact events with Rapier

`NetworkTrigger`, `NetworkCollision`, `NetworkTrigger2D` and `NetworkCollision2D` keep their API with the Rapier backend, so the code from [contact events](../physics/contacts.md) works unchanged. What changes is where the contacts come from.

## Where the contacts come from

`RapierPhysics` takes over these components on the network objects it simulates, on the static objects of the network scenes it loads, and on the GameObjects passed to `AddStatic(GameObject)` or `AddStatic2D(GameObject)`. A component that has been taken over reports `IsAttached` as true, ignores Unity's callbacks and reports the contact and intersection pairs of the Rapier world instead:

- a `NetworkCollision` or `NetworkCollision2D` reports the colliders whose solid shapes touch its colliders;
- a `NetworkTrigger` or `NetworkTrigger2D` reports the colliders that overlap its sensors.

The pairs are part of the world state, so a snapshot saves them and a replay restores them together with the bodies. As with `RigidbodyPhysics`, a component raises its enter and exit events once per tick, and after a replay only for what changed.

## Differences from RigidbodyPhysics

- `AdditionalSize` has no effect. Contacts are the pairs that Rapier computes within its contact prediction distance, and resting contacts are kept, so an object lying on the ground still touches it. To detect objects that are near but not touching, add a larger trigger collider.
- The tick on which a contact starts or ends can differ by one from PhysX or Box2D, because the engines compute contacts differently.
- Components added to static objects after their scene has loaded are not taken over and keep reporting Unity's callbacks.

For game rules that the server and the predicting client must decide the same way, such as grounding or deaths, you can also read the contact sets of a world directly, as described under [reading the worlds](bodies.md#reading-the-worlds).
