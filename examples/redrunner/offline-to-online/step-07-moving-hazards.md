# Step 07: Moving hazards

## Goal

After this step the mace and the saws that ride a track stand at the same place on the server and on every client at the same tick, without their positions being sent over the network.

## Starting point

After step 06 the server decides deaths, but path followers still move in `PathFollower.Update` with `Time.deltaTime`.

## Problem

```
Offline:
PathFollower.Update (every frame)
  ↓
Smart: a character within range? start
gameRunning false? stop
  ↓
move toward the next point with Time.deltaTime
```

Online, that gives every process its own mace. The dedicated server never calls `GameManager.StartGame`, so `gameRunning` stays false and its mace never moves. Each client's mace starts when that client's own character comes near, which happens at a different time in every process.

Since step 06 the server's mace is the one that kills, so a player could be crushed on screen by a mace that was somewhere else on the server, or die on the server to a mace the client showed elsewhere.

## Fomoxa concepts

- [Ticks and timing](../../../concepts/tick.md)
- [Tick events](../../../concepts/tick.md#tick-events)
- [Three tick numbers](../../../concepts/tick.md#three-tick-numbers)
- [Deterministic simulation](../../../concepts/deterministic-simulation.md)

## Design

The movement of a follower does not depend on any player, so it can be computed from the tick number alone:

```
BuildCycle(tickDelta): run the path rules once, tick by tick,
                       until the follower is back at its first point
  ↓
cycle = [position after tick 0, 1, 2, … N-1]
  ↓
position(tick) = cycle[tick % N]
```

`NetworkLevel` moves every follower before each tick, using the tick the process is simulating. On the server that is the server's tick. On a client it is the prediction tick, the tick the client is predicting, which is the same number the server uses when it applies that tick's input. The mace therefore stands where it will stand on the server when the local character reaches it.

Nothing is replicated. The server and the clients compute the same position because they run the same code on the same tick number, and only the server's collision kills.

## Files

```
Assets/Scripts/RedRunner/Utilities/PathFollower.cs
Assets/Scripts/RedRunner/Networking/NetworkLevel.cs
Assets/Scripts/RedRunner/Enemies/Mace.cs
```

## Implementation

### Turn the path into a cycle

`PathFollower.BuildCycle (float tickDelta)` runs the movement types of the path points (MoveTowards, Lerp, SmoothDamp, Acceleration) with the tick length instead of the frame time. It starts at the first point, runs until the follower arrives at the first point again, and stores the position after every tick. To make the cycle close exactly, three details differ from the frame version: on arrival the follower snaps to the point and its smoothing velocity resets, it holds still while it waits at a point, and Acceleration gains speed once per tick. The loop stops after 600 seconds of ticks, a limit only a path that never returns would reach.

### Place the follower for a tick

```csharp
public virtual Vector3 PositionAt (uint tick)
{
	return m_Cycle [(int)(tick % (uint)m_Cycle.Count)];
}
```

```csharp
public virtual void FollowTick (uint tick, float tickDelta)
{
	if (m_PathDefinition == null) {
		return;
	}
	if (m_Cycle == null || m_CycleTickDelta != tickDelta) {
		BuildCycle (tickDelta);
	}
	Vector3 position = PositionAt (tick);
	m_Velocity = (PositionAt (tick - 1) - position) / tickDelta;
	if (!m_Driven) {
		m_Driven = true;
		StopAllCoroutines ();
		m_Rigidbody2D = GetComponent<Rigidbody2D> ();
		transform.position = position;
		if (m_Rigidbody2D != null) {
			m_Rigidbody2D.position = position;
		}
	} else if (m_Rigidbody2D != null) {
		m_Rigidbody2D.MovePosition (position);
	} else {
		transform.position = position;
	}
}
```

The mace has a kinematic `Rigidbody2D`, and `MovePosition` moves it during the next physics step, so a character it hits is pushed the way a moving body pushes. `Velocity` keeps the sign the mace's collision code expects (previous position minus current), so the mace still decides from its direction whether it slams. Once `FollowTick` has run, `Update` returns at its first line, and the range check, the `Stopped` flag and the frame movement no longer apply.

### Drive the followers from the level

`NetworkLevel` knows when the level exists, so it drives the followers. After it builds the blocks, it collects their followers and subscribes to `TimeManager.OnPreTick`, which runs before the package steps physics:

```csharp
private void Build()
{
    if (m_State.Seed == 0 || m_Generator.IsBuilt)
    {
        return;
    }

    m_Generator.Build((int)m_State.Seed);
    m_Followers = FindObjectsByType<PathFollower>(FindObjectsSortMode.None);
    m_Game.Manager.TimeManager.OnPreTick += MoveFollowers;
}

private void MoveFollowers()
{
    TimeManager time = m_Game.Manager.TimeManager;
    uint tick = time.PredictionTick;
    float tickDelta = (float)time.TickDelta;
    foreach (PathFollower follower in m_Followers)
    {
        follower.FollowTick(tick, tickDelta);
    }
}
```

On the server and in host mode, `TimeManager.PredictionTick` equals the server's tick. `NetworkLevel` finds `NetworkGame` in `Awake` and unsubscribes in `OnDestroy`.

When a client replays ticks to correct its character, the followers stay at the position of the current tick. A replay covers only a few ticks, so the difference is small, and the server still decides whether the mace killed anyone.

Fomoxa provides the tick number, the tick length and the moment before each tick, and the game turns them into a position.

## Test

Join a server and watch a mace without going near it.

The port's own check is `Tools/PortChecks/PathCheck.cs`, run with the server argument `-log-paths`. On the server, `PathLog` logs the position of the level's first moving follower every 10 ticks. The client logs the same for 10 seconds, and the check compares the two logs at the ticks that both contain.

## Expected result

- The mace moves even when no character is near.
- Every client shows it at the same point of its swing.

In one run of `PathCheck` the mace was at the same position on both sides at 49 ticks, with a cycle of 436 ticks (8.7 seconds at 50 ticks per second).

## Commit

```
Commit: f277dad
Message: Move maces and track saws on a cycle of server ticks
```

View [`f277dad`](https://github.com/fomoxa/RedRunner/commit/f277dad4cc29eccef696158280185c9117a270ae) on GitHub, then continue with [step 08: two clients](step-08-two-clients.md).
