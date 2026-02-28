# Phase 3: Decompose FleetNavigationService.project_path (CC=22 → ~10)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-209 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Extract action order projection and tick consumption into focused helpers
**Risk Level:** MEDIUM — immutable NavigationState helps, but action_time handling is tricky
**File:** `game/strategy/services/fleet_navigation_service.py`
**Existing Tests:** ~39 tests (unit + integration consistency)

## Review Findings Addressed
- CX-003: 5 Mutable Variables Through Nested Loops (Critical)
- CQ-025: Mixed Abstraction Levels in Main Loop (Major)
- CQ-026: NavigationState Reconstruction Repeated 4 Times (Major)
- CX-009: Action Order Handling Block is 32% of Complexity (Major)
- DS-013: `_project_action_order` Signature Incomplete (Major)
- DS-014: Inner While Loop for action_time Is Separate Concern (Major)
- AR-05: Fake Fleet Object in compute_path (Major)
- TC-003: WARP Order Type Not Tested (Major, downgraded from Critical)
- TC-008: Pathfinding Failure Mid-Projection Not Tested (Major)

---

## Tasks

### Task 3.1: Fill Test Gaps Before Decomposing [Medium]
- [ ] TC-003: Add test with `FleetOrder(OrderType.WARP, warp_point_hex)` verifying projection computes correct path via `compute_path_for_warp`
- [ ] TC-008: Add test with two MOVE orders where second destination has no path (mock `find_hybrid_path` returns None for second call), verify projection stops gracefully
- [ ] Run: `pytest tests/unit/strategy/fleet_navigation/ tests/integration/strategy/test_fleet_navigation_consistency.py -v`
- [ ] Verify all new + existing tests pass

### Task 3.2: Pre-Adjust First-Order Progress [Simple]
Eliminate the `is_first_order` / `first_order_progress` flag pattern (CX-011, DS-016, CQ-027).

- [ ] Before the main loop, check if first order is an action order with `execution_progress > 0`
- [ ] If so, pre-compute the adjusted `action_time` or `moves_left_in_turn` upfront
- [ ] Remove `is_first_order` and `first_order_progress` variables from loop body
- [ ] Verify: all tests still pass (especially consistency tests)

### Task 3.3: Extract `_consume_ticks` Pure Helper [Simple]
Lines 481-488 and 558-560: unified turn-boundary crossing logic (DS-014).

- [ ] Create `@staticmethod _consume_ticks(moves_left, current_turn, moves_per_turn, max_turns, ticks) -> Tuple[int, int]`
- [ ] Returns `(new_moves_left, new_current_turn)`
- [ ] Replace both turn-advancement locations (action order inner loop AND movement cost) with calls to this helper
- [ ] Add targeted unit tests for `_consume_ticks` (boundary cases: exact turn boundary, multi-turn consumption, exceeds max_turns)
- [ ] Verify: all tests still pass

### Task 3.4: Extract `_project_action_order` [Medium]
Lines 470-499: action order handling block (32% of CC).

- [ ] Create `_project_action_order(self, state, order, moves_left, current_turn, moves_per_turn, max_turns, fleet, component_registry) -> Tuple[NavigationState, int, int]`
- [ ] Returns `(new_state, new_moves_left, new_current_turn)`
- [ ] Uses `_consume_ticks` internally for tick consumption loop
- [ ] Estimated CC: ~5
- [ ] Add targeted unit tests
- [ ] Verify: all tests still pass

### Task 3.5: Extract `_resolve_path_for_order` [Simple]
Lines 501-519: destination lookup + warp vs normal path computation.

- [ ] Create `_resolve_path_for_order(self, state, order, galaxy) -> Optional[NavigationState]`
- [ ] Returns updated state with computed path, or None if no valid path
- [ ] Handles WARP vs MOVE branching internally
- [ ] Estimated CC: ~4
- [ ] Verify: all tests still pass

### Task 3.6: Use `dataclasses.replace()` for NavigationState (CQ-026) [Simple]
- [ ] Replace all 3 manual NavigationState constructions in `project_path` with `dataclasses.replace(state, location=..., path=..., orders=...)`
- [ ] Also apply in `compute_next_step` if applicable
- [ ] Verify: all tests still pass

### Task 3.7: Simplify `project_path` Orchestrator [Medium]
- [ ] Main loop calls: resolve order → action or movement → advance step
- [ ] Verify orchestrator CC <= 10
- [ ] Run full test suite: `pytest tests/ -n 12`
- [ ] Verify: all 7353+ tests pass, 0 failures

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] `project_path` orchestrator CC <= 10
- [ ] All extracted helpers CC <= 6
- [ ] WARP projection tested (TC-003)
- [ ] Consistency tests still pass
- [ ] All tests pass (full suite)
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 4
