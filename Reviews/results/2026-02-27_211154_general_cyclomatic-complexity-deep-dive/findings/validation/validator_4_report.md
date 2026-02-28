# Validation Report: Validator 4

## Summary
- **Findings Reviewed:** 25
- **Confirmed:** 19
- **Downgraded:** 4
- **Rejected:** 2
- **Rejection Rate:** 8%

## Verdicts

#### Finding: DS-012
**Original Severity:** Info
**Verdict:** CONFIRMED
**Reason:** The three proposed extractions (_load_save_metadata, _load_turn_data, _reconstruct_game_session) do correctly map to natural phase boundaries in load_game (lines 112-221). The code structure at lines 124-159, 162-191, and 194-208 aligns with these splits. This is an accurate positive assessment.

#### Finding: DS-013
**Original Severity:** Major
**Verdict:** CONFIRMED
**Reason:** Verified by reading project_path lines 470-499. The proposed `_project_action_order(state, order, moves_left_in_turn, turns_left)` is indeed missing `fleet` (line 473), `component_registry` (line 473), `is_first_order` (line 477), `first_order_progress` (line 478), `moves_per_turn` (line 488), `max_turns` (line 481), and `current_turn` (line 481/487). The finding correctly identifies 9 total parameters needed.

#### Finding: DS-014
**Original Severity:** Major
**Verdict:** CONFIRMED
**Reason:** Lines 481-488 contain a nested while loop consuming action_time ticks across turn boundaries. Lines 557-560 have a conceptually similar pattern for movement cost (decrementing moves_left_in_turn and advancing current_turn). Both are tick-consumption patterns that could share logic. The finding correctly identifies this as a separate concern and CC driver.

#### Finding: DS-015
**Original Severity:** Minor
**Verdict:** CONFIRMED
**Reason:** Lines 526-560 do indeed merge three responsibilities: segment creation (526-539: creating PathSegment), state mutation (542-554: building new NavigationState), and movement cost tracking (557-560: decrementing moves_left_in_turn and advancing turns). The finding correctly identifies these as distinct concerns, though each is individually simple.

#### Finding: DS-016
**Original Severity:** Minor
**Verdict:** CONFIRMED
**Reason:** Lines 451-453 define `first_order_progress` and `is_first_order`, and lines 477-478 use them in a conditional that fires exactly once then sets `is_first_order = False`. This adds two variables and a conditional for a one-shot adjustment. The finding's observation about accidental complexity is valid -- this could be pre-computed before the loop.

#### Finding: DS-017
**Original Severity:** Critical
**Verdict:** DOWNGRADED(Major)
**Reason:** The pattern observation is valid -- production_engine, ship_stats_calculator, and fleet_navigation_service all have main loops with conditional branches containing return/break plus nested inner loops. However, "Critical" overstates the impact. The existing code works correctly, is well-tested, and the proposed extractions (even if imperfect) would still meaningfully reduce per-method CC. The nested-loop pattern is a design-level recommendation, not a defect.

#### Finding: DS-018
**Original Severity:** Info
**Verdict:** CONFIRMED
**Reason:** The recommended ordering (1. load_game, 2. production_engine, 3. project_path, 4. calculate_stats) is a reasonable prioritization based on risk and complexity. load_game's linear exception-handling structure is indeed lowest risk; calculate_stats with its 7+ ability types and WarpJump coupling is indeed highest risk. Sound advice.

#### Finding: TC-001
**Original Severity:** Critical
**Verdict:** DOWNGRADED(Minor)
**Reason:** Line 226-228 indeed removes non-dict items from queue with `queue.pop(0)` and no test explicitly passes a non-dict item to verify this. However, this is a trivial validation guard (3 lines) that exists as defensive coding. The controller always creates dict items. Severity should be Minor -- it is a minor gap in edge case coverage, not a critical deficiency.

#### Finding: TC-002
**Original Severity:** Critical
**Verdict:** CONFIRMED
**Reason:** Lines 285-289 show that when `p_rate_per_turn <= 0` for any required resource, the method returns immediately (stops the queue). Searched all test files and found no test that sets a production rate to 0 for a required resource. This is a meaningful untested code path that could affect gameplay (queue permanently stuck).

#### Finding: TC-003
**Original Severity:** Critical
**Verdict:** DOWNGRADED(Major)
**Reason:** Lines 506-507 show the WARP branch in project_path calls `compute_path_for_warp`. Searched for tests: `test_warp_orders.py` tests `compute_path_for_warp` and `compute_next_step` with WARP orders, and `test_navigation_pure.py` tests warp path computation. However, no test specifically exercises the WARP branch *within* `project_path()` (the projection method). The warp logic is tested in compute_next_step but not through the projection code path. Downgraded from Critical because the underlying warp logic is tested, just not through this specific call site.

#### Finding: TC-004
**Original Severity:** Critical
**Verdict:** CONFIRMED
**Reason:** Lines 263-268 handle the else branch for warp_data when it is not a dict -- treating it as a formula string (startswith "=") or raw numeric. Examined all test files in `tests/unit/strategy/ship_stats/`: every WarpJump test uses `{'max_tonnage': N}` dict format. No test provides warp_data as a plain number or formula string. This branch is entirely untested.

#### Finding: TC-005
**Original Severity:** Major
**Verdict:** CONFIRMED
**Reason:** Lines 234-241 show that when `is_complex_only=True` and vehicle_type is not 'complex', the function returns immediately, stopping the queue. Searched all test files -- no test passes `is_complex_only=True` with a non-complex item. The production tests all use proper vehicle types matching queue type. This is a real test gap.

#### Finding: TC-006
**Original Severity:** Major
**Verdict:** CONFIRMED
**Reason:** Lines 125-126 show that `if not os.path.isabs(save_path)`, the path is joined with `Paths.SAVES_DIR`. Examined all load_game test calls in `test_save_load_ops.py` and `test_error_handling.py` -- every test passes an absolute path (either from save_game return or manually constructed with tmpdir). No test passes a relative path to exercise the join logic.

#### Finding: TC-007
**Original Severity:** Major
**Verdict:** CONFIRMED
**Reason:** Lines 213-221 contain outer PermissionError, OSError, and broad exception catch blocks. Reviewed all tests in `test_error_handling.py`: tests trigger inner exception handlers (corrupt JSON, missing turn file, RuntimeError from from_dict) but all inner handlers catch and return before the outer handlers can fire. No test triggers the outer catch blocks. This aligns with DS-010's finding that they are redundant.

#### Finding: TC-008
**Original Severity:** Major
**Verdict:** CONFIRMED
**Reason:** Lines 510-511 in project_path show `if not new_path: break` -- when compute_path returns empty for a chained order, projection stops. Searched all test files for fleet navigation; the consistency tests in `test_fleet_navigation_consistency.py` test chained orders but always with valid pre-set paths. No test creates a scenario where pathfinding fails mid-chain during projection.

#### Finding: TC-009
**Original Severity:** Major
**Verdict:** DOWNGRADED(Minor)
**Reason:** Line 220-221 shows `iterations < 10` as a safety guard in the main while loop. No test triggers this guard -- all tests use realistic queue sizes (1-2 items). However, this is a safety limit designed to prevent infinite loops, not a business logic path. Testing it would require crafting a pathological scenario (e.g., zero-cost items that loop). Minor gap in coverage of a defensive guard, not a major test gap.

#### Finding: TC-010
**Original Severity:** Major
**Verdict:** CONFIRMED
**Reason:** Lines 136-140 show that `vehicle_classes` is used to look up `ship_class_mass` for the formula context. The conftest at `tests/unit/strategy/ship_stats/conftest.py` line 19 shows `vehicle_classes={}` is always passed. No test provides actual vehicle class data (e.g., `{'Cruiser': {'max_mass': 16000}}`) to verify the formula context is built correctly from real class data.

#### Finding: TC-011
**Original Severity:** Minor
**Verdict:** CONFIRMED
**Reason:** Line 344 shows `consumed < total - 0.001` as the epsilon completion check. While tests verify completion behavior (items are completed or not), no test specifically targets the epsilon boundary -- e.g., testing that an item with consumed=99.9995 and total=100.0 is considered complete. This is a minor gap in boundary testing.

#### Finding: TC-012
**Original Severity:** Minor
**Verdict:** CONFIRMED
**Reason:** Lines 332-337 update `item['turns_remaining']` for UI display. Searched for assertions on `turns_remaining` in the production test files -- `test_tick_consumption.py` and `test_production_refactor.py` never assert the value of `turns_remaining` after processing. The field is set but never verified.

#### Finding: TC-013
**Original Severity:** Minor
**Verdict:** CONFIRMED
**Reason:** Line 231 shows `consumption_mult = multipliers.get('consumption_mult', 1.0)` and line 238 applies it to resource consumption amounts. While `consumption_mult` is tested extensively in the simulation layer (`test_resource_consumption.py`), the strategy layer's `ShipStatsCalculator` never tests it with an actual modifier that produces a non-1.0 consumption_mult value. The modifier tests in `test_modifiers.py` test capacity_mult, mass_mult, and hp_mult but not consumption_mult.

#### Finding: TC-014
**Original Severity:** Minor
**Verdict:** CONFIRMED
**Reason:** Lines 461-463 show the max_steps safety limit (`iterations > max_steps`). This defensive guard is never triggered in any test because all test scenarios use small, bounded paths. This is a minor gap consistent with TC-009's pattern of untested safety guards.

#### Finding: TC-015
**Original Severity:** Minor
**Verdict:** CONFIRMED
**Reason:** Line 459 shows `while (state.path or state.orders)`. The case where `state.path` has items but `state.orders` is empty is not directly tested. While `test_service_edge_cases.py` and `test_projection.py` reference path-without-orders scenarios in file names, I found no test that explicitly creates a NavigationState/Fleet with a non-empty path and empty orders list to verify projection behavior.

#### Finding: TC-016
**Original Severity:** Info
**Verdict:** CONFIRMED
**Reason:** The `tests/unit/strategy/ship_stats/` directory contains 6 focused files (test_basics.py, test_warp.py, test_resources.py, test_modifiers.py, test_toggles.py, test_edge_cases.py) with a shared conftest.py. This is well-organized, with clear separation of concerns across test files.

#### Finding: TC-017
**Original Severity:** Info
**Verdict:** CONFIRMED
**Reason:** The `tests/unit/strategy/save_game_service/` tests use `tempfile.mkdtemp()` for real filesystem operations, patching `Paths.SAVES_DIR` to point to temporary directories. This is verified in every fixture across both `test_save_load_ops.py` and `test_error_handling.py`. This is a sound testing approach.

#### Finding: TC-018
**Original Severity:** Info
**Verdict:** CONFIRMED
**Reason:** `tests/integration/strategy/test_fleet_navigation_consistency.py` contains a `TestProjectionMatchesExecution` class that verifies UI projections match actual TurnEngine execution. Tests cover simple moves, multi-turn journeys, warp moves, intercepts, chained orders, and edge cases. This is a strong safety net for the unified navigation service.

#### Finding: TC-002 (duplicate entry removed -- already covered above)

