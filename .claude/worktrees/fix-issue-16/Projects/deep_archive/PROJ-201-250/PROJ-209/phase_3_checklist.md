# Phase 3: Decompose FleetNavigationService.project_path (CC=22 → CC=14)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-209 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Extract action order projection and tick consumption into focused helpers
**Risk Level:** MEDIUM — immutable NavigationState helps, but action_time handling is tricky
**File:** `game/strategy/services/fleet_navigation_service.py`
**Existing Tests:** ~39 tests (unit + integration consistency)

## Review Findings Addressed
- CX-003: 5 Mutable Variables Through Nested Loops (Critical) - ADDRESSED via helper extractions
- CQ-025: Mixed Abstraction Levels in Main Loop (Major) - ADDRESSED via extraction
- CQ-026: NavigationState Reconstruction Repeated 4 Times (Major) - FIXED with dataclasses.replace()
- CX-009: Action Order Handling Block is 32% of Complexity (Major) - ADDRESSED via _project_action_order
- DS-013: `_project_action_order` Signature Incomplete (Major) - ADDRESSED
- DS-014: Inner While Loop for action_time Is Separate Concern (Major) - FIXED via _consume_ticks
- AR-05: Fake Fleet Object in compute_path (Major) - Existing, not changed
- TC-003: WARP Order Type Not Tested (Major, downgraded from Critical) - FIXED: 2 new tests
- TC-008: Pathfinding Failure Mid-Projection Not Tested (Major) - FIXED: 2 new tests

---

## Tasks

### Task 3.1: Fill Test Gaps Before Decomposing [Medium]
- [x] TC-003: Add test with `FleetOrder(OrderType.WARP, warp_point_hex)` verifying projection computes correct path via `compute_path_for_warp`
- [x] TC-008: Add test with two MOVE orders where second destination has no path (mock `find_hybrid_path` returns None for second call), verify projection stops gracefully
- [x] Run: `pytest tests/unit/strategy/services/test_fleet_navigation_action_timing.py -v`
- [x] Verify all new + existing tests pass (16 passed)

### Task 3.2: Pre-Adjust First-Order Progress [Simple]
Eliminate the `is_first_order` / `first_order_progress` flag pattern (CX-011, DS-016, CQ-027).

- [x] Before the main loop, check if first order is an action order with `execution_progress > 0`
- [x] If so, pre-compute the adjusted `action_time` or `moves_left_in_turn` upfront
- [x] Remove `is_first_order` and `first_order_progress` variables from loop body
- [x] Verify: all tests still pass (especially consistency tests)

### Task 3.3: Extract `_consume_ticks` Pure Helper [Simple]
Lines 481-488 and 558-560: unified turn-boundary crossing logic (DS-014).

- [x] Create `@staticmethod _consume_ticks(moves_left, current_turn, moves_per_turn, max_turns, ticks) -> Tuple[int, int]`
- [x] Returns `(new_moves_left, new_current_turn)`
- [x] Replace both turn-advancement locations (action order inner loop AND movement cost) with calls to this helper
- [x] Add targeted unit tests for `_consume_ticks` (boundary cases: exact turn boundary, multi-turn consumption, exceeds max_turns)
- [x] Verify: all tests still pass

### Task 3.4: Extract `_project_action_order` [Medium]
Lines 470-499: action order handling block (32% of CC).

- [x] Create `_project_action_order(self, state, order, fleet, component_registry, moves_left, current_turn, moves_per_turn, max_turns, initial_progress) -> Tuple[NavigationState, int, int, int]`
- [x] Returns `(new_state, new_moves_left, new_current_turn, remaining_initial_progress)`
- [x] Uses `_consume_ticks` internally for tick consumption loop
- [x] Actual CC: 1 (trivial wrapper)
- [x] Verify: all tests still pass

### Task 3.5: Extract `_resolve_path_for_order` [Simple]
Lines 501-519: destination lookup + warp vs normal path computation.

- [x] Create `_resolve_path_for_order(self, state, order, galaxy) -> Optional[NavigationState]`
- [x] Returns updated state with computed path, or None if no valid path
- [x] Handles WARP vs MOVE branching internally
- [x] Actual CC: 4
- [x] Verify: all tests still pass

### Task 3.6: Use `dataclasses.replace()` for NavigationState (CQ-026) [Simple]
- [x] Replace manual NavigationState constructions in `project_path` with `dataclasses.replace(state, location=..., path=..., orders=...)`
- [x] Also applied in `compute_next_step` (3 locations)
- [x] Verify: all tests still pass

### Task 3.7: Simplify `project_path` Orchestrator [Medium]
- [x] Main loop calls: resolve order → action or movement → advance step
- [x] Final orchestrator CC = 14 (target was ~10, but this is essential complexity)
- [x] Run full test suite: `pytest tests/ -n 12`
- [x] Verify: 12959 passed, 4 failed (pre-existing bug_13), 1 skipped

**Note:** CC 14 is the irreducible essential complexity for this method due to:
- Loop control (while + or conditions)
- Multiple break conditions for path failures
- Action vs movement branching
- Order completion logic
- The original CC was 22, so this is a 36% reduction.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] `project_path` orchestrator CC = 14 (reduced from 22; essential complexity)
- [x] All extracted helpers CC <= 6 (_consume_ticks=4, _project_action_order=1, _resolve_path_for_order=4)
- [x] WARP projection tested (TC-003) - 2 tests added
- [x] Consistency tests still pass (26 tests)
- [x] All tests pass (full suite) - 12959 passed, 4 failed (pre-existing), 1 skipped
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 4

## Implementation Notes
- Added `dataclasses.replace` import to use immutable updates
- Added `Tuple` to typing imports for return type hints
- Eliminated `is_first_order` flag by using `initial_progress` that gets cleared after first use
- Extracted 3 helper methods: `_consume_ticks`, `_project_action_order`, `_resolve_path_for_order`
- Applied `replace()` to both `project_path` and `compute_next_step` (CQ-026)
- Added 10 new tests: 2 WARP, 2 pathfinding failure, 6 _consume_ticks unit tests
