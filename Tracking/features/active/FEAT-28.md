# FEAT-28: Mutual JOIN orders should make both fleets move toward each other

## Description

When two fleets are mutually assigned to join each other (Fleet A has
`JOIN_FLEET → B`, Fleet B has `JOIN_FLEET → A`), today only one fleet
moves while the other sits still. The user wants both fleets to start
heading toward each other (a meet-in-the-middle rendezvous) so the
merge happens in roughly half the time.

User commentary at QA Session 20260428_190154 [19:10:51 – 19:11:11]:
> "A fleet knows what fleets are trying to join it and it knows what
> fleets it's trying to join. If two fleets are assigned to join each
> other, then that should just automatically get them to start heading
> towards each other."

## Code investigation findings

`JoinCommandHandler.handle()`
([`game/strategy/engine/handlers/movement.py:159-165`](../../../game/strategy/engine/handlers/movement.py#L159-L165))
generates a `MOVE_TO_FLEET` order followed by a `JOIN_FLEET` order
when a player issues "join". The `MOVE_TO_FLEET` does the chasing and
the `JOIN_FLEET` performs the merge once co-located.

**Today's behaviour** — when mutual joins are issued:
- A's queue: `[MOVE_TO_FLEET → B, JOIN_FLEET → B]`
- B's queue: `[MOVE_TO_FLEET → A, JOIN_FLEET → A]`
- Both fleets independently pathfind to the *other's current location*
  via `FleetNavigationService.calculate_fleet_next_hex()`. If both
  call this on the same tick, both move — but each is moving toward
  the other's previous-tick location, not a midpoint. The chase
  converges, but slowly and with no symmetric / coordinated routing.

**Pursuer tracking** is at
[`game/strategy/data/fleet_pursuer_tracker.py`](../../../game/strategy/data/fleet_pursuer_tracker.py)
— `PursuerTracker` maintains `pursuers_of(fleet)` and is queried by
`redirect_pursuers(new_target, exclude=...)` (BUG-122 fix). The data
needed to detect mutual-join — "is B in A's pursuer list AND A in B's
pursuer list?" — is already tracked.

**No rendezvous / midpoint logic exists.**
`calculate_intercept_point()` at
[`game/strategy/data/pathfinding.py:434-463`](../../../game/strategy/data/pathfinding.py#L434-L463)
solves "where can the chaser arrive given the target's projected
path?" but assumes the target is non-cooperating. There is no
"both-moving, find the meet hex" helper.

## Required changes

### Detection
- During order processing, before `MOVE_TO_FLEET` movement resolves,
  check if `target.get_current_order().target == self`. If so, this
  is a mutual-join pair.
- Detection lives close to `OrderProcessor` movement-phase or
  `FleetNavigationService.calculate_fleet_next_hex()` so the
  symmetric routing applies on every tick of the chase, not just at
  order-issue time.

### Routing
- New helper `calculate_rendezvous_hex(fleet_a, fleet_b)` in
  `pathfinding.py`: returns the hex closest to the geometric midpoint
  between A and B that respects warp lane / movement-cost constraints.
- Both fleets pathfind to the rendezvous hex, not to each other's
  current position.
- Reseed each tick (in case warp routing makes the optimal midpoint
  shift) — recompute `calculate_rendezvous_hex` per tick.

### Edge cases to test
- A and B at adjacent hexes — rendezvous should be one of the two
  current hexes (no oscillation).
- A and B in different star systems — rendezvous goes through the
  shared warp point; one of them may need to traverse more hexes if
  the warp lane is asymmetric, but neither should sit idle.
- A is mutual-join with B; B is also mutual-join with C (chain) — A's
  routing target must remain the "B" rendezvous; B's must pick one of
  A or C (existing pursuer-priority rules apply).
- A loses its `JOIN_FLEET` order while moving — fall back to
  single-mover chase (revert to today's behaviour).
- A and B have very different speeds — slow fleet still moves; fast
  fleet covers more ground. Rendezvous hex should *not* be the
  geometric midpoint when speeds are unequal — it should bias toward
  the slow fleet so both arrive on the same tick. Decide during
  implementation whether this matters for game feel; geometric
  midpoint is acceptable as v1.

### Tests (TDD-first per CLAUDE.md Rule 1)
- `tests/integration/strategy/test_mutual_join_rendezvous.py` — new
  file:
  - Equal-speed A and B at hex distance 10 should meet at hex 5 from
    each starting position.
  - Distance halved compared to today (where A moves all 10, B sits
    still).
  - Rendezvous still works after one fleet's `JOIN_FLEET` is
    cancelled mid-chase.

## Acceptance

- Two fleets with mutual `JOIN_FLEET` orders begin moving toward each
  other on the next tick after the orders are issued.
- The merge completes in roughly half the ticks of the current
  asymmetric chase (for equal-speed fleets at small distances).
- Cancelling one fleet's order reverts to single-mover chase
  behaviour without crashes.

## Out of scope

- Visual indicator on the map that "this fleet is mutually joining" —
  could be a follow-up cosmetic ticket.
- Multi-way (3+ fleet) rendezvous at a single point.
- Speed-balanced rendezvous (where rendezvous hex shifts toward the
  slower fleet so both arrive simultaneously). Geometric midpoint is
  the v1 contract; speed-balanced is a follow-up.

## Priority

Medium — quality-of-life improvement that meaningfully reduces
"waiting for fleets to converge" friction during play. Not blocking
gameplay, but the asymmetric chase feels wrong once you know both
sides have the same intent.

## Status

In-Progress

## Related

- **BUG-122** (Awaiting Confirmation) — fixed the *destruction* edge
  case of mutual joins. This feature builds on the data model
  (`PursuerTracker.pursuers_of`) that BUG-122 already polished.

## Work Log

- 2026-04-28: Created from QA Session 20260428_190154 [19:10:51 –
  19:11:11]. Code investigation completed during triage.
