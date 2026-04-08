# Phase 1: Foundation — Event Types & FleetPursuerTracker

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-222 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** In Progress
**Objective:** Create the FleetPursuerTracker delegate class and add new event types. Pure additive — no existing code modified except event_types.py.

---

## Tasks

### Task 1.1: Add Fleet Event Types [Simple]
**File:** `game/strategy/events/event_types.py`
**Tests:** `pytest tests/unit/strategy/events/test_event_types.py`
- [x] Add `FLEET_JOINED = "fleet_joined"` to EventType enum (after line 19)
- [x] Add `FLEET_JOIN_REDIRECTED = "fleet_join_redirected"` to EventType enum
- [x] Add `FLEET_JOIN_CANCELLED = "fleet_join_cancelled"` to EventType enum
- [x] Add `FLEET_OPERATIONS = "fleet_operations"` to EventCategory enum (after line 29)
- [x] Update test_event_types.py: adjust member count assertions for both enums
- [x] Run tests: `pytest tests/unit/strategy/events/test_event_types.py`

**Notes:** All 17 tests pass. Added FLEET_OPERATIONS before ALL in EventCategory.

### Task 1.2: Create FleetPursuerTracker Delegate [Medium]
**File:** `game/strategy/data/fleet_pursuer_tracker.py` (NEW)
**Tests:** `pytest tests/unit/strategy/fleet/test_fleet_pursuer_tracker.py`
- [x] Create `game/strategy/data/fleet_pursuer_tracker.py` with class FleetPursuerTracker
- [x] Constructor: `__init__(self, fleet: 'Fleet')` — stores `self._fleet = fleet`, creates `self._pursuers: Set['Fleet'] = set()`
- [x] Method: `add_pursuer(fleet: 'Fleet') -> None` — adds fleet to `_pursuers` set
- [x] Method: `remove_pursuer(fleet: 'Fleet') -> None` — discards fleet from `_pursuers` set (no error if missing)
- [x] Property: `pursuers -> FrozenSet['Fleet']` — returns `frozenset(self._pursuers)` for read-only access
- [x] Property: `pursuer_count -> int` — returns `len(self._pursuers)`
- [x] Method: `redirect_pursuers(new_target: 'Fleet') -> List[Tuple['Fleet', 'Fleet']]` — for each pursuer: rewrite all MOVE_TO_FLEET/JOIN_FLEET order targets from `self._fleet` to `new_target`, transfer pursuer to `new_target._pursuer_tracker.add_pursuer()`, return list of (pursuer, old_target) tuples for event logging. Clear `self._pursuers` after transfer.
- [x] Method: `notify_target_destroyed() -> List['Fleet']` — for each pursuer: clear their MOVE_TO_FLEET/JOIN_FLEET orders that target `self._fleet` (use `_remove_orders_targeting_fleet()`), return list of affected pursuers for event logging. Clear `self._pursuers`.
- [x] Private method: `_remove_orders_targeting_fleet(pursuer: 'Fleet') -> None` — removes all orders from pursuer whose target is `self._fleet` and type is MOVE_TO_FLEET or JOIN_FLEET. Iterate in reverse to safely remove by index.
- [x] Use `TYPE_CHECKING` import for Fleet to avoid circular dependency
- [x] Create test file `tests/unit/strategy/fleet/test_fleet_pursuer_tracker.py`
- [x] Test: `test_add_and_remove_pursuer` — add/remove/verify set contents
- [x] Test: `test_add_duplicate_pursuer_is_idempotent` — add same fleet twice, verify count is 1
- [x] Test: `test_redirect_pursuers_rewrites_order_targets` — create 2 pursuers with MOVE_TO_FLEET orders, redirect, verify targets changed
- [x] Test: `test_redirect_pursuers_transfers_to_new_target` — verify pursuers moved to new target's tracker
- [x] Test: `test_redirect_pursuers_clears_source` — verify source tracker is empty after redirect
- [x] Test: `test_notify_target_destroyed_removes_orders` — create pursuers with orders, notify, verify orders removed
- [x] Test: `test_notify_target_destroyed_returns_affected` — verify return value lists affected fleets
- [x] Test: `test_redirect_preserves_non_targeting_orders` — pursuer has orders targeting other fleets, only matching orders are rewritten
- [x] Run tests: `pytest tests/unit/strategy/fleet/test_fleet_pursuer_tracker.py`

**Notes:** Follow delegate pattern from FleetResourceAggregator (simplest existing delegate).

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase
