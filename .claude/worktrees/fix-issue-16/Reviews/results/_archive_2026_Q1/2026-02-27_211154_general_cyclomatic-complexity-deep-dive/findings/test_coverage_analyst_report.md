# Test Coverage Analysis Report

**Date:** 2026-02-27
**Scope:** Four highest cyclomatic complexity functions targeted for decomposition
**Analyst:** Test Coverage Analyst (Claude Code)

---

## Summary

- **Total issues found: 18**
- **Critical: 4, Major: 6, Minor: 5, Info: 3**

Coverage is strongest for `calculate_stats` (excellent, 60+ tests) and `load_game` (good, 30+ tests). Coverage is weakest for `_process_queue_tick_dynamic` (moderate, ~15 tests but gaps in edge cases) and `project_path` (moderate, ~15 tests but missing warp order projection paths).

---

## Function 1: `_process_queue_tick_dynamic` (CC=27)

**File:** `game/strategy/engine/production_engine.py:177-351`

### What It Does
Processes one tick of production for a construction queue with dynamic resource consumption. Contains a while-loop consuming tick capacity across queue items with:
- Invalid item removal (line 227)
- Complex-only filter (line 234)
- Fleet complex location check (line 244)
- Total cost initialization fallback (line 253)
- Remaining cost calculation (line 266-270)
- Zero-cost instant completion (line 274)
- Limiting resource determination (line 281-294)
- Zero production rate bailout (line 285-289)
- Tick fraction calculation (line 297-316)
- Affordability check (line 319)
- Resource consumption (line 323-326)
- Turns remaining UI update (line 332-337)
- Completion check with epsilon (line 341-349)

### Test Files Found
| File | Type | Tests Exercising Function |
|------|------|--------------------------|
| `tests/unit/strategy/engine/test_production_refactor.py` | Unit | 2 tests: limiting resource, carry-over capacity |
| `tests/unit/strategy/production_engine/test_tick_consumption.py` | Unit | 16 tests: tick consumption, pause, resume, mid-turn completion |
| `tests/unit/strategy/production_engine/test_resource_costs.py` | Unit | 9 tests: design cost calculation (helper method) |
| `tests/unit/strategy/production_engine/test_spawning.py` | Unit | 8 tests: spawn ship/complex (helper methods) |
| `tests/integration/strategy/production/test_completion.py` | Integration | 10 tests: full turn completion |
| `tests/integration/strategy/production/test_queue.py` | Integration | 5 tests: queue operations |
| `tests/integration/strategy/production/test_fleet_production_e2e.py` | Integration | Fleet production scenarios |

### Tested Code Paths
- Happy path: resource consumption per tick at correct rate
- Carry-over capacity (two items completing in one tick)
- Limiting resource selection (two resources, different amounts)
- Pause on insufficient resources
- Resume after resources added
- Multiple resources consumed together
- Partial resource insufficiency pauses all
- Zero cost item completes immediately
- Mid-turn completion pops item and spawns
- Next item starts after first completes
- Fleet queue processing
- Fleet complex paused when not at planet
- Item stays when partially consumed
- Empty queue no-ops
- Facility (shipyard) queue rate
- Multiple queue items only first processes
- Malformed items without total_cost

### Untested Code Paths (Gaps)
1. **Invalid item removal** (line 226-228): No test verifies that non-dict items in the queue are removed.
2. **Complex-only filter** (line 234-241): The `is_complex_only=True` path filtering out non-complex items is not directly unit tested. Integration tests use it implicitly but never verify the `return` behavior.
3. **Zero production rate bailout** (line 285-289): No test for when `production_rate` has 0 for a required resource type. The function returns, stopping the queue.
4. **Iteration safety limit** (line 221): The `iterations < 10` guard is never triggered in tests.
5. **Epsilon completion check** (line 344): The 0.001 epsilon comparison for floating point completion is not specifically tested.
6. **`resources_consumed` dict initialization path** (line 326): When `item.get('resources_consumed', {})` returns empty dict mid-processing.
7. **`turns_remaining` UI update calculation** (lines 332-337): Never directly asserted.

### Mocking Strategy
- `mock_empire.has_resources.return_value = True` in refactor tests (MagicMock)
- Real `Empire` objects in tick_consumption tests
- `patch.object(engine, '_spawn_complex')` / `'_spawn_ship'` to isolate from spawning
- Integration tests use real TurnEngine with real data objects

### Decomposition Impact
- Tests calling `_process_queue_tick_dynamic` directly (2 tests in refactor) would need updating
- Tests calling `process_construction_tick` (16+ tests) are decoupled through the public API and are resilient
- Helper method tests (`_spawn_ship`, `_spawn_complex`, `_calculate_design_cost`) are already well-isolated
- Extracted methods for resource calculation, completion, and constraint checking would need new targeted tests

---

## Function 2: `calculate_stats` (CC=26)

**File:** `game/strategy/services/ship_stats_calculator.py:87-297`

### What It Does
Calculates all ship statistics from design data and component damage/toggles. Iterates through components, applies modifiers, evaluates formulas, and accumulates stats including HP, mass, resource storage, consumption, strategic movement, warp capability, and cargo storage.

### Test Files Found
| File | Type | Tests |
|------|------|-------|
| `tests/unit/strategy/ship_stats/test_basics.py` | Unit | 11 tests: basics, damage effectiveness, stat aggregation, component ID matching |
| `tests/unit/strategy/ship_stats/test_edge_cases.py` | Unit | 18 tests: constructor validation, formula evaluation, ability helpers, fallback, zero HP, warp effectiveness, has_warp_capability, component toggles, multiple resources, cargo storage |
| `tests/unit/strategy/ship_stats/test_modifiers.py` | Unit | 8 tests: bug documentation, modifier application, scaled batteries |
| `tests/unit/strategy/ship_stats/test_resources.py` | Unit | 13 tests: generic dict accumulators, trigger types, custom resources |
| `tests/unit/strategy/ship_stats/test_toggles.py` | Unit | 8 tests: component toggle functionality |
| `tests/unit/strategy/ship_stats/test_warp.py` | Unit | 13 tests: warp capability, has_warp_capability |

**Total: ~71 tests exercising calculate_stats or its sub-methods**

### Tested Code Paths
- Empty design returns zeros
- Missing components skipped
- Undamaged component full effectiveness
- Below threshold zero effectiveness
- Gradual degradation linear model
- Armor never degrades (by type and by ability marker)
- Mass never degrades
- HP degrades with damage
- Strategic movement aggregation with damage
- Fuel storage aggregation
- Strategic fuel consumption per hex
- Component toggles (on/off, mass still counted)
- Multiple resource types in storage
- Multiple consumption triggers (per_hex, per_turn, warp_jump)
- Custom resource types in all buckets
- Formula evaluation (with context, without context, non-formula strings, None)
- Ability list extraction (None, list, dict, simple value)
- Ability value extraction (missing, numeric, dict with recognized keys)
- Modifier application (capacity_mult, mass_mult, hp_mult)
- Warp requires 100% HP
- Warp tonnage uses largest drive
- One damaged warp drive reduces capability
- Warp resource costs only when warp functional
- Unknown trigger types ignored
- Empty/None resource types handled
- Fallback to expected_stats when no components found
- Cargo storage aggregation with damage degradation
- Constructor validation (registries required)
- Multiple warp drives largest tonnage selection
- has_warp_capability comprehensive checks (mass, tonnage, storage)
- Consumption multiplier from modifiers

### Untested Code Paths (Gaps)
1. **WarpJump as non-dict value** (lines 263-268): The `else` branch handling `warp_data` as a formula string or raw numeric value is not tested. Tests always use `dict` format for WarpJump.
2. **vehicle_classes context resolution** (lines 136-140): The `class_data` lookup from `vehicle_classes` registry for `formula_context` is never tested with actual vehicle class data; tests always use empty `vehicle_classes={}`.
3. **consumption_mult modifier** (line 231): While capacity_mult is tested, consumption_mult is never explicitly tested with a modifier that sets it.

### Mocking Strategy
- Uses `MockComponent` class (lightweight dict-like objects) instead of full registry
- `create_mock_registries()` provides `GameRegistries` with test-specific components/modifiers
- `make_design_data()` helper creates proper layer structure
- No Pygame or file system dependencies
- Tests are all pure unit tests with excellent isolation

### Decomposition Impact
- Tests are highly resilient to decomposition. Most test through the public `calculate_stats()` API.
- Static helper method tests (`get_component_effectiveness`, `_get_warp_effectiveness`, `_evaluate_value`, `_get_ability_list`, `_get_ability_value`, `_get_current_hp`) are already isolated and would move with their methods.
- `_iterate_design_components` is tested implicitly through `calculate_stats`.
- Extracted accumulators (e.g., `_accumulate_resource_storage`, `_accumulate_warp`) would inherit coverage from existing `calculate_stats` tests.
- **Recommendation:** Keep existing tests as regression tests against the public API. Add targeted unit tests for any new extracted methods.

---

## Function 3: `load_game` (CC=26)

**File:** `game/strategy/systems/save_game_service.py:112-221`

### What It Does
Loads game state from a save folder. Handles path resolution, folder validation, metadata loading, version checking, turn file loading, game state validation, and GameSession reconstruction. Contains extensive error handling with specific exception types.

### Test Files Found
| File | Type | Tests |
|------|------|-------|
| `tests/unit/strategy/save_game_service/test_save_load_ops.py` | Unit | 9 tests: folder structure, versions, load operations, metadata |
| `tests/unit/strategy/save_game_service/test_error_handling.py` | Unit | 13 tests: error logging, user-friendly errors, exception handling |
| `tests/integration/save_load/test_save_edge_cases.py` | Integration | 13 tests: corrupted saves, version compatibility, save management, game continuity |
| `tests/integration/save_load/test_load_restoration.py` | Integration | 11 tests: state round-trip preservation |
| `tests/integration/save_load/test_resupply_persistence.py` | Integration | Resource persistence tests |
| `tests/integration/strategy/production/test_fleet_save_load.py` | Integration | Fleet production save/load |

**Total: ~46+ tests exercising load_game or related save/load flow**

### Tested Code Paths
- Load returns valid GameSession
- Load restores turn number, empires, galaxy, config, fleets, colonies
- Load defaults to latest turn
- Load specific turn by number
- Load sets save_path on session
- Corrupt metadata JSON returns error
- Missing metadata file returns error
- Missing turns folder returns error
- Corrupt turn file JSON returns error
- Missing turn file returns error
- Missing required game state fields
- Incompatible version rejected
- Permission denied errors handled
- User-friendly error messages (no raw exceptions exposed)
- Error logging with context
- Nonexistent save path returns error
- RuntimeError from GameSession.from_dict handled
- Multiple save/load cycles preserve state
- Can process turns after load
- Can save after load
- Human player IDs preserved
- Planet IDs preserved

### Untested Code Paths (Gaps)
1. **Relative path resolution** (line 125-126): No test passes a relative path to `load_game` to verify `os.path.join(Paths.SAVES_DIR, save_path)` logic.
2. **Missing metadata keys validation** (lines 151-154): While tested indirectly through corrupted save tests, no test specifically verifies the "Missing metadata fields: X, Y" message with specific missing keys.
3. **Outer PermissionError catch** (line 213-215): The outer `except PermissionError` at line 213 (which catches errors not in the inner blocks) is never triggered in tests.
4. **Outer broad exception catch** (lines 219-221): The final fallback `except (KeyError, TypeError, ...)` block for unexpected errors during the load process flow is not directly triggered.
5. **OSError from load_json_required for metadata** (line 147-148): The `OSError` path for metadata reading is not tested.
6. **OSError from load_json_required for turn file** (line 184-185): The `OSError` path for turn file reading is not tested.

### Mocking Strategy
- Uses `tempfile.mkdtemp()` for real filesystem operations (good practice)
- `patch.object(paths_module.Paths, 'SAVES_DIR', saves_dir)` redirects to temp dir
- `MockGameSession` class for save operations
- `patch('game.strategy.engine.game_session.GameSession.from_dict')` to inject errors
- Integration tests use real `GameSession` objects
- `patch('os.makedirs', side_effect=PermissionError)` for permission tests
- `patch('shutil.rmtree', side_effect=PermissionError)` for delete tests

### Decomposition Impact
- Tests are well-structured and mostly test through the public `load_game()` API.
- Error handling is the most complex part -- extracted error handling methods would be testable in isolation.
- Metadata validation, version checking, and turn file loading could each become separate methods with dedicated tests.
- The deeply nested try/except blocks create the complexity -- decomposition into `_load_metadata`, `_load_turn_data`, `_reconstruct_session` would each get their own test suite.
- **Recommendation:** Existing tests provide excellent regression coverage. During decomposition, preserve all existing tests as-is and add focused unit tests for each extracted method.

---

## Function 4: `project_path` (CC=22)

**File:** `game/strategy/services/fleet_navigation_service.py:413-562`

### What It Does
Projects fleet movement over multiple turns for UI visualization. Simulates future movement based on orders, speed, and warp capability. Handles action orders with timing delays (PROJ-187), chained movement orders, warp detection, and turn boundary calculations.

### Test Files Found
| File | Type | Tests |
|------|------|-------|
| `tests/unit/strategy/fleet_navigation/test_projection.py` | Unit | 8 tests: segment production, max_turns, warp detection, turn numbers, as_dicts |
| `tests/unit/strategy/fleet_navigation/test_service_edge_cases.py` | Unit | 15 tests: data structures, edge cases, zero speed, no orders, mutation bridge |
| `tests/unit/strategy/services/test_fleet_navigation_action_timing.py` | Unit | 7 tests: action timing delays (colonize, stellerate, in-progress, instant) |
| `tests/integration/strategy/test_fleet_navigation_consistency.py` | Integration | 9 tests: projection-execution consistency |

**Total: ~39 tests exercising project_path or related navigation methods**

### Tested Code Paths
- Produces correct PathSegment objects
- Respects max_turns limit
- Warp jump detection (hex_distance > 1)
- Correct turn number calculation based on speed
- Returns empty for fleet without orders or path
- Zero speed returns empty
- Negative speed returns empty
- project_path_as_dicts returns list of dicts
- Action timing delays (COLONIZE with action_time=1)
- Multi-tick action delays (STELLERATE_STAR action_time=5)
- In-progress action with execution_progress
- Instant action (action_time=0)
- Multiple actions accumulate delay
- Long action respects max_turns
- Projection matches execution (MOVE order)
- Multi-turn projection matches execution
- Warp projection matches execution
- Intercept projection matches execution
- Chained orders projection matches execution
- Already-at-destination consistency
- Fractional speed consistency
- Non-movement orders (COLONIZE) not projected as movement

### Untested Code Paths (Gaps)
1. **WARP order projection via compute_path_for_warp** (lines 506-507): The `if order.type == OrderType.WARP` branch in the path calculation section is never tested directly. All tests use MOVE orders. The WARP order type has specialized path computation that is not covered by projection tests.
2. **Max iterations safety limit** (lines 461-463): The `if iterations > max_steps` guard with logger.warning is never triggered in tests.
3. **Pathfinding failure mid-projection** (lines 510-511): The `if not new_path: break` after calling `compute_path` inside the projection loop is not tested. This handles cases where pathfinding returns empty for a chained order.
4. **is_first_order flag tracking** (lines 498, 520): The transition from first order to subsequent orders and how `first_order_progress` is applied only once is implicitly tested but not directly verified.
5. **Fleet with pre-existing path but no orders** (line 459): The `while (state.path or state.orders)` condition when `state.path` has items but `state.orders` is empty is not tested.

### Mocking Strategy
- Uses real `Fleet` objects with `can_use_warp = MagicMock(return_value=False)`
- `patch('game.strategy.services.fleet_navigation_service.find_hybrid_path')` for pathfinding
- `patch('game.strategy.services.action_time_resolver.ActionTimeResolver.resolve_action_time')` for action timing
- Integration tests use real `TurnEngine`, `Empire`, and `Fleet` objects
- `MagicMock()` for galaxy in most unit tests

### Decomposition Impact
- Tests call `project_path()` through the public API -- resilient to internal refactoring.
- The while-loop body has clear phases: action order handling, path computation, step execution, turn tracking.
- Extracted methods like `_handle_action_order_projection`, `_compute_order_path`, `_execute_projection_step` would each need tests.
- Integration consistency tests are the most valuable -- they verify the contract between projection and execution.
- Action timing tests (`test_fleet_navigation_action_timing.py`) heavily mock internals and would need updating if ActionTimeResolver integration changes.
- **Recommendation:** Preserve all consistency tests as regression tests. Add unit tests for extracted projection sub-methods.

---

## Findings

### TC-001
#### CRITICAL: No Tests for Invalid Queue Items in Production
**ID:** TC-001
**Location:** `game/strategy/engine/production_engine.py:226-228`
**Issue:** The `_process_queue_tick_dynamic` method removes non-dict items from the queue (line 227: `queue.pop(0)`), but no test verifies this behavior. If decomposition changes this path, the bug could go unnoticed.
**Impact:** Invalid items in the queue could cause silent failures or crashes if this guard is accidentally removed during refactoring.
**Recommendation:** Add a test with a non-dict item (e.g., a string or None) in the queue, verifying it is removed and processing continues.
**Effort:** Simple

### TC-002
#### CRITICAL: No Tests for Zero Production Rate in Production Engine
**ID:** TC-002
**Location:** `game/strategy/engine/production_engine.py:285-289`
**Issue:** When `production_rate` has 0 for a required resource, the function returns immediately (stops the queue). No test covers this path. This is a realistic scenario if a facility type has no rate defined for a resource.
**Impact:** During decomposition, this critical bailout logic could be lost, leading to division-by-zero errors or infinite loops.
**Recommendation:** Add a test where `production_rate` has a required resource set to 0, verifying the queue stops processing without error.
**Effort:** Simple

### TC-003
#### CRITICAL: WARP Order Type Not Tested in project_path
**ID:** TC-003
**Location:** `game/strategy/services/fleet_navigation_service.py:506-507`
**Issue:** The `project_path` method has a special branch for `OrderType.WARP` that calls `compute_path_for_warp` instead of `compute_path`. No test exercises this branch. All projection tests use `OrderType.MOVE`.
**Impact:** Warp order projection could break silently during decomposition. This is particularly concerning because warp orders have specialized path computation (path to warp point + exit hex).
**Recommendation:** Add a test with a `FleetOrder(OrderType.WARP, warp_point_hex)` verifying the projection computes the correct path through the warp point.
**Effort:** Medium

### TC-004
#### CRITICAL: WarpJump Non-Dict Value Branch Untested in calculate_stats
**ID:** TC-004
**Location:** `game/strategy/services/ship_stats_calculator.py:263-268`
**Issue:** The `else` branch for handling `warp_data` when it is NOT a dict (formula string or raw numeric) is never tested. All tests use `{'max_tonnage': N}` format. If warp data can be `"=ship_class_mass"` or just `5000`, this path is dead-code-risky.
**Impact:** If this path exists for real component data, it would break silently during decomposition.
**Recommendation:** Add tests with `WarpJump` ability data as: (a) a formula string `"=ship_class_mass"`, (b) a raw integer `5000`. Verify tonnage is calculated correctly.
**Effort:** Simple

### TC-005
#### MAJOR: Complex-Only Filter Path Not Directly Tested
**ID:** TC-005
**Location:** `game/strategy/engine/production_engine.py:234-241`
**Issue:** When `is_complex_only=True` and a non-complex item is encountered, the function returns immediately. This is used by the base queue to prevent ship items from being processed there. No unit test directly verifies this `return` behavior.
**Impact:** If decomposition accidentally changes this to `continue` instead of `return`, ships could be processed in the wrong queue.
**Recommendation:** Add a test with `is_complex_only=True` and a ship item in the queue, verifying the function returns without processing it.
**Effort:** Simple

### TC-006
#### MAJOR: Relative Path Resolution Not Tested in load_game
**ID:** TC-006
**Location:** `game/strategy/systems/save_game_service.py:125-126`
**Issue:** `load_game` has logic to resolve relative paths by joining with `Paths.SAVES_DIR`. No test passes a relative path name (e.g., `"my_save"` instead of `"C:/saves/my_save"`) to verify this resolution.
**Impact:** If the path resolution logic is extracted during decomposition, the behavior could change without detection.
**Recommendation:** Add a test passing `load_game("my_save_name")` with `SAVES_DIR` patched, verifying the correct absolute path is used.
**Effort:** Simple

### TC-007
#### MAJOR: Outer Exception Handlers in load_game Never Triggered
**ID:** TC-007
**Location:** `game/strategy/systems/save_game_service.py:213-221`
**Issue:** The outer `except PermissionError` (line 213) and the broad `except (KeyError, TypeError, ...)` (line 219) handlers are fallback catches that are never triggered by any test. These exist to catch errors that escape the inner try/except blocks.
**Impact:** These handlers produce user-facing error messages. If decomposition restructures the exception handling, these messages could be lost or wrong.
**Recommendation:** Create tests that trigger errors before the inner try blocks are entered (e.g., `os.path.isabs` raising an error) to verify the outer handlers work.
**Effort:** Medium

### TC-008
#### MAJOR: No Test for Pathfinding Failure Mid-Projection
**ID:** TC-008
**Location:** `game/strategy/services/fleet_navigation_service.py:510-511`
**Issue:** When `project_path` processes a chained order and `compute_path` returns an empty path, the projection breaks out of the loop. No test verifies this behavior with a second order that has no valid path.
**Impact:** If the `break` is changed to `continue` during decomposition, the projection could enter an infinite loop.
**Recommendation:** Add a test with two MOVE orders where the second destination has no path (mock `find_hybrid_path` to return None for the second call). Verify projection stops gracefully.
**Effort:** Medium

### TC-009
#### MAJOR: Production Engine Iteration Safety Limit Never Tested
**ID:** TC-009
**Location:** `game/strategy/engine/production_engine.py:220-221`
**Issue:** The `iterations < 10` guard prevents infinite loops in `_process_queue_tick_dynamic`. It is never triggered in any test. If this guard is removed during decomposition, an infinite loop could occur with zero-cost items that fail to spawn.
**Impact:** Production loops in runtime could hang the game if this guard is lost.
**Recommendation:** Create a test with an edge case that would loop (e.g., items that complete but fail to pop from queue due to a mock), verifying the 10-iteration limit stops processing.
**Effort:** Medium

### TC-010
#### MAJOR: vehicle_classes Context Never Tested in calculate_stats
**ID:** TC-010
**Location:** `game/strategy/services/ship_stats_calculator.py:136-140`
**Issue:** The `formula_context` is built from `vehicle_classes` registry data (`ship_class_mass`), but all tests use `vehicle_classes={}`. No test verifies that a formula like `"=ship_class_mass"` uses the correct value from the vehicle class registry.
**Impact:** During decomposition, the formula context construction could be separated from stat calculation, and the vehicle_classes integration could break.
**Recommendation:** Add a test with a non-empty `vehicle_classes` dict and a component ability using a formula referencing `ship_class_mass`.
**Effort:** Simple

### TC-011
#### MINOR: Epsilon Completion Check Not Specifically Tested
**ID:** TC-011
**Location:** `game/strategy/engine/production_engine.py:344`
**Issue:** The completion check uses `consumed < total - 0.001` as an epsilon for floating-point comparison. No test specifically exercises the boundary around this epsilon.
**Impact:** Low risk, but floating-point precision issues in production could cause items to never complete or complete prematurely.
**Recommendation:** Add a test where `resources_consumed` is within 0.001 of `total_cost`, verifying the item is considered complete.
**Effort:** Simple

### TC-012
#### MINOR: turns_remaining UI Update Never Asserted
**ID:** TC-012
**Location:** `game/strategy/engine/production_engine.py:332-337`
**Issue:** The `turns_remaining` field is updated each tick for UI display, but no test asserts its value. Tests check resource consumption and queue state, but not the estimated time.
**Impact:** UI could show wrong estimated time without any test catching it.
**Recommendation:** Add assertions for `item['turns_remaining']` in existing tick consumption tests.
**Effort:** Simple

### TC-013
#### MINOR: consumption_mult Modifier Not Tested in calculate_stats
**ID:** TC-013
**Location:** `game/strategy/services/ship_stats_calculator.py:231`
**Issue:** While `capacity_mult` is tested with battery modifiers, `consumption_mult` (which scales ResourceConsumption amounts) is never tested with an actual modifier.
**Impact:** Consumption scaling could silently break during decomposition.
**Recommendation:** Add a test with a modifier that sets `consumption_mult`, verifying consumption values are scaled.
**Effort:** Simple

### TC-014
#### MINOR: Max Iterations Safety in project_path Never Triggered
**ID:** TC-014
**Location:** `game/strategy/services/fleet_navigation_service.py:461-463`
**Issue:** The `max_steps = max_turns * moves_per_turn + 100` safety limit is never triggered in tests.
**Impact:** Low risk, but removing this guard during decomposition could lead to infinite loops.
**Recommendation:** Consider adding a test that would exceed the iteration limit (e.g., pathfinding that returns oscillating paths).
**Effort:** Medium

### TC-015
#### MINOR: Fleet with Path But No Orders Not Tested
**ID:** TC-015
**Location:** `game/strategy/services/fleet_navigation_service.py:459`
**Issue:** The `while (state.path or state.orders)` condition allows processing when `state.path` has items but `state.orders` is empty. This edge case is not tested -- a fleet with a leftover path but no orders.
**Impact:** This could consume the path without producing meaningful segments. Low risk but surprising behavior.
**Recommendation:** Add a test with `fleet.path = [HexCoord(1,0)]` and `fleet.orders = []`, verifying the path segments are still generated.
**Effort:** Simple

### TC-016
#### INFO: calculate_stats Has Excellent Test Organization
**ID:** TC-016
**Location:** `tests/unit/strategy/ship_stats/`
**Issue:** The test suite for `calculate_stats` is split across 6 focused files (basics, edge_cases, modifiers, resources, toggles, warp) with a shared conftest providing `MockComponent` and helper utilities. This is exemplary test organization.
**Impact:** Positive -- this pattern should be replicated for other functions during decomposition.
**Recommendation:** Use this as the template for test organization of other decomposed functions.
**Effort:** N/A

### TC-017
#### INFO: load_game Tests Use Real Filesystem (Good Practice)
**ID:** TC-017
**Location:** `tests/unit/strategy/save_game_service/`, `tests/integration/save_load/`
**Issue:** Save/load tests use `tempfile.mkdtemp()` and real filesystem operations rather than mocking the filesystem. This provides high confidence in actual behavior.
**Impact:** Positive -- tests catch real filesystem issues that mocking would miss.
**Recommendation:** Maintain this approach during decomposition. Extracted methods that interact with the filesystem should also use real temp directories.
**Effort:** N/A

### TC-018
#### INFO: Integration Consistency Tests Provide Strong Safety Net
**ID:** TC-018
**Location:** `tests/integration/strategy/test_fleet_navigation_consistency.py`
**Issue:** The consistency tests verify that `project_path` produces the same results as actual `TurnEngine` execution. This is an excellent pattern that catches projection-execution drift.
**Impact:** Positive -- these tests provide the strongest guarantee during decomposition.
**Recommendation:** Do NOT modify these tests during decomposition. They are the ultimate regression safety net.
**Effort:** N/A

---

## Top 5 Priority Issues

1. **TC-002 (CRITICAL):** Zero production rate bailout untested -- could cause division-by-zero if lost during decomposition. Simple fix.

2. **TC-003 (CRITICAL):** WARP order type in `project_path` completely untested -- an entire code branch has zero coverage. Medium effort but high impact.

3. **TC-001 (CRITICAL):** Invalid queue item removal untested -- silent data corruption risk. Simple fix.

4. **TC-004 (CRITICAL):** WarpJump non-dict value branch untested -- potential dead code or live bug. Simple fix.

5. **TC-005 (MAJOR):** Complex-only filter not directly tested -- wrong queue processing could cause gameplay bugs. Simple fix.

---

## Decomposition Test Strategy Recommendations

### For `_process_queue_tick_dynamic` (CC=27)
- **Preserve:** All 16+ tick consumption tests through `process_construction_tick` public API
- **Add before decomposition:** Tests for TC-001, TC-002, TC-005, TC-009, TC-011
- **Strategy:** Extract constraint checking, resource calculation, and completion logic into separate methods. Each gets targeted unit tests. The while-loop orchestration stays in the main method but becomes simpler.
- **Risk:** 2 tests call `_process_queue_tick_dynamic` directly -- these need updating.

### For `calculate_stats` (CC=26)
- **Preserve:** All 71 tests as-is. They test through the public API.
- **Add before decomposition:** Tests for TC-004, TC-010, TC-013
- **Strategy:** Extract ability accumulation into `_accumulate_resource_storage`, `_accumulate_movement`, `_accumulate_warp`, etc. Each inherits coverage from existing integration-style tests. Add focused tests for extracted methods.
- **Risk:** Very low. Tests are well-isolated and API-stable.

### For `load_game` (CC=26)
- **Preserve:** All 46+ tests as-is. Excellent coverage of error paths.
- **Add before decomposition:** Tests for TC-006, TC-007
- **Strategy:** Extract `_load_metadata`, `_load_turn_data`, `_reconstruct_session`. Error handling tests map naturally to each extracted method. Outer exception handlers become simpler.
- **Risk:** Low. Tests use real filesystem and are behavior-focused.

### For `project_path` (CC=22)
- **Preserve:** All 39 tests, especially the 9 consistency tests.
- **Add before decomposition:** Tests for TC-003, TC-008, TC-014
- **Strategy:** Extract action order handling and path computation into separate methods. The main loop becomes a coordinator. Consistency tests validate the contract.
- **Risk:** Medium. Action timing tests use heavy mocking. WARP order path has zero coverage.
