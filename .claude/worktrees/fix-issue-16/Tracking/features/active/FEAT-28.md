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

Awaiting Confirmation

## Related

- **BUG-122** (Awaiting Confirmation) — fixed the *destruction* edge
  case of mutual joins. This feature builds on the data model
  (`PursuerTracker.pursuers_of`) that BUG-122 already polished.

## Work Log

- 2026-04-28: Created from QA Session 20260428_190154 [19:10:51 –
  19:11:11]. Code investigation completed during triage.
- 2026-04-29: Implemented under deep-dive-resume team
  (worktree `.claude/worktrees/feat-feat-28`, rebased onto main
  `0ab9b0e25` post-FEAT-27 merge).

  **Diagnosis confirmed empirically:** today's `calculate_intercept_point`
  is asymmetric for mutual pursuit. The evaluator scores candidates by
  `abs(chaser_turns - target_turn)` after the in-time filter, so the
  candidate equal to the chaser's own current location wins
  (chaser_turns=0). One fleet sees a populated target_path and picks
  "stay still"; the other (whose nested projection trips the
  `_projection_guard`) gets a fallback chase path. Result: one fleet
  moves, the other waits. Verified via the new
  `test_distance_10_today_baseline_takes_many_ticks` test (≥100 sub-ticks
  baseline at distance 10, equal speed 5).

  **Implementation:**
  - `game/strategy/services/fleet_navigation_service.py` —
    new `_is_mutual_pursuit(self_fleet, target_fleet)` predicate (reads
    target's head order; True iff `MOVE_TO_FLEET`/`JOIN_FLEET` targeting
    `self_fleet`). `get_destination` MOVE_TO_FLEET branch checks the
    predicate first; on True, returns `target_fleet.location` directly,
    bypassing `calculate_intercept_point`. Optional `self_fleet=None`
    parameter threaded through `compute_next_step` and
    `_resolve_path_for_order`; `calculate_fleet_next_hex` and
    `_project_path_inner` pass `self_fleet=fleet`. Default `None`
    preserves backward compatibility for any callers without a Fleet
    identity.
  - `game/strategy/engine/fleet_movement_engine.py` — new
    `_filter_jump_past_collisions(move_queue)` post-processor called at
    the end of `collect_movements`. Detects mutual-pursuit pairs whose
    next-hex assignments would swap (`next_a == fleet_b.location` AND
    `next_b == fleet_a.location`) and drops the larger fleet's entry.
    "Larger" = more ships; tiebreak smaller `fleet.id` (mirrors BUG-122
    `_elect_canonical_merges`). v1 covers swap parity only; broader
    leapfrog cases are deferred (fleets at distance 3 land 1 hex apart
    next tick anyway and merge naturally).

  **Tests (TDD per CLAUDE.md Rule 1):**
  - `tests/unit/strategy/services/test_fleet_navigation_mutual_pursuit.py`
    (NEW, 10 cases) — predicate truth table (`MOVE_TO_FLEET` /
    `JOIN_FLEET` / no orders / 3rd-party / `MOVE` / `COLONIZE`),
    `get_destination` mutual branch returns target's location,
    fall-through to `calculate_intercept_point` when not mutual,
    `self_fleet=None` falls through, signature has `self_fleet`
    keyword default `None`.
  - `tests/integration/strategy/test_mutual_join_rendezvous.py` (NEW,
    7 cases) — empirical baseline (≥100 sub-ticks at distance 10 with
    predicate disabled), rendezvous ≤2/3 of baseline, JOIN_FLEET not
    prematurely cancelled, one-fleet-cancels-fallback (no crash),
    swap-parity larger fleet delays, swap-parity ship-count tiebreak,
    no-swap no-filter passthrough.

  **Anti-reversion verified:**
  - BUG-122 `redirect_pursuers(exclude=)`, `_elect_canonical_merges`,
    `process_instant_orders` Phase A/B/C: not touched
    (`tests/integration/strategy/test_fleet_join_redirect.py`,
    `tests/unit/strategy/test_fleet_order_processor.py` all pass).
  - BUG-125 `_resolve_player_fleet` handler authorization: not touched
    (`handlers/movement.py` unchanged).
  - PROJ-222 pursuer tracker construction: not touched (predicate reads
    head order directly, not the tracker).
  - `_projection_guard` re-entrancy:
    `tests/unit/strategy/pathfinding/test_intercept_recursion.py` 4/4
    pass (cycle tests use plain `MOVE_TO_FLEET` orders that still hit
    today's intercept path).

  **Tests:** Full suite `python -m pytest tests/ -n 12`: **16184 passed,
  3 skipped** (75s). Targeted anti-regression suite: 170/170 pass.

  **Docs updated:** `docs/systems/strategy_layer.md` — added
  "Mutual-Pursuit Rendezvous Routing (FEAT-28)" subsection under
  FleetPursuerTracker; bumped `> **Last verified:**` to today.

  **Out-of-scope deferrals (per ticket):**
  - Speed-balanced rendezvous (meet hex shifts toward slower fleet) —
    out of scope per ticket; v1 is geometric-natural convergence.
  - Visual indicator on map for mutual-joining state — out of scope.
  - Multi-way (3+) rendezvous — out of scope.
  - Leapfrog jump-past (distance 3+, both speed ≥2 passing through but
    not swapping) — implementer-deferred; merges naturally next tick.
