# State

A state model holds data of a `NetworkBehaviour` that the server keeps in sync on every observer, such as health, a score or whether a door is open. The server changes its instance of the model, and at the end of each tick the package sends what changed. Clients receive the new values into their own instance and get a callback with the previous values.

## When to use it

State suits values that clients must always know, including clients that join later. One-off events are better sent as an [RPC](../messaging/rpc.md), and movement is handled by [`NetworkTransform`](transform.md).

## Basic usage

A state model must be on the reliable-ordered channel:

```csharp
using Fomoxa;
using Fomoxa.Networking;

namespace MyGame.Network.Models
{
    [Network]
    [Codec("net")]
    [NetworkChannel("net", Channel.ReliableOrdered)]
    public class Health
    {
        [Network("u16")]
        [Codec("net")]
        public ushort Current { get; set; }

        [Network("u16")]
        [Codec("net")]
        public ushort Max { get; set; }
    }
}
```

The behaviour then registers an instance of it:

```csharp
using Fomoxa.Networking;
using Fomoxa.Unity;
using Generated;
using MyGame.Network.Models;
using UnityEngine;

public sealed class Damageable : NetworkBehaviour
{
    [SerializeField] private ushort maxHealth = 100;

    private readonly Health health = new Health();

    public ushort Current => health.Current;

    private void Awake()
    {
        health.Max = maxHealth;
        health.Current = maxHealth;
    }

    protected override void OnRegisterState(NetworkState state)
    {
        state.Use(HealthNetAdapter.Instance, health, OnHealthChanged);
    }

    public void TakeDamage(ushort amount)
    {
        health.Current = (ushort)Mathf.Max(0, health.Current - amount);
    }

    private void OnHealthChanged(Health previous)
    {
        Debug.Log($"{name}: {previous.Current} -> {health.Current}");
    }
}
```

Call `TakeDamage` on the server, and the clients' `health` changes at the end of that tick, after the network delay.

## How it works

`NetworkState.Use(codec, instance, onChanged)` registers the instance. After the tick's `OnTick` and `OnPostTick` events, the server encodes every state instance, compares the bytes with what it sent last, and sends the state to every observer if they differ.

Because the comparison works on the encoded bytes, any change of a carried property is detected without you having to mark anything dirty. A property the codec does not carry is neither compared nor sent.

## Server behavior

Change the instance on the server only. The server gets no callback for its own changes; `onChanged` runs on clients.

The spawn message contains the state captured at `Spawn`, so set the initial values before calling `Spawn`, for example in `Awake`. A client that joins later receives the state as it was at the last tick.

## Client behavior

The initial state is already in the instance before `OnStartClient` runs, and `onChanged` does not run for it. For every later change, the package decodes the new values into the instance and calls `onChanged` with a separate object holding the previous values, so read the new values from your own instance.

A change made to the instance on a client is not sent, and the next update overwrites it. On a host the instance is shared with the server and is not decoded again, but `onChanged` still runs on the host's client.

## Delta encoding

When the encoded state has the same length as the last one sent, the server computes a delta, which is the XOR of the two encodings with runs of unchanged bytes compressed. If the delta is smaller than the full state, the server sends the delta instead, and clients apply it to the last state they received.

A client that cannot apply a delta, for example because it is out of step, drops it, asks the server for the full state and ignores further deltas until that full state arrives. This recovery is automatic.

Fixed-size fields keep the encoding length stable, which lets deltas apply. A change of length, such as a longer string or a longer array, makes the server send the full state.

## Configuration

| Rule | When broken |
|---|---|
| The model is on the reliable-ordered channel | `HandlerRegistrationException`: `... is not on the reliable-ordered channel; declare the model's codec with [NetworkChannel(..., Channel.ReliableOrdered)]` |
| The model encodes to at least one byte | `HandlerRegistrationException`: `... whose model encodes to no bytes; a state model needs at least one field` |
| One state model per behaviour | `HandlerRegistrationException`: `... uses more than one state model` |
| The model is not also an RPC | `HandlerRegistrationException` when the object spawns |

## Limitations

Each `NetworkBehaviour` has at most one state model, so data that needs more is split across several behaviours. State is sent at most once per tick, which merges all changes made within one tick. Every observer receives the same state, so data meant for a single client goes in a target RPC instead.

State is registered in a [NetworkBehaviour](../core/network-behaviour.md) and declared like any other [model](../messaging/models.md). [NetworkAnimator](animator.md) is built on the same mechanism.
