# Phase 1: Behavior/assertion rewrites

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-491 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Replace 15 brittle-assertion patterns deferred by PROJ-479 with behavior-based or kwargs-extraction assertions. Each task addresses one file and verifies via the existing test runner. No production code changes.

**Mechanical pattern:** find the test that asserts on a private call / source-text / AST property, replace with assertion on the observable public-API outcome.

---

## Tasks

### Task 1.1: test_hex_outlines.py — exact float literal asserts
**Source:** PROJ-479 Task 3.10
**File:** `tests/unit/ui/screens/strategy_render/test_hex_outlines.py` (lines 101-106)
**Tests:** `pytest tests/unit/ui/screens/strategy_render/test_hex_outlines.py`

- [x] Replace exact float literal assertions on `renderer._draw_inner_hex.call_args_list` with tolerance-based checks (`math.isclose` per coordinate) OR a property assertion (call count + bounded coordinate range).
- [x] Verify: tests pass.

### Task 1.2: test_profiler_perf.py — inspect.getsource forbidden-string asserts
**Source:** PROJ-479 Task 3.30
**File:** `tests/unit/performance/test_profiler_perf.py` (lines 53-61) — confirmed by audit; PROJ-479's `tests/unit/core/profiling/` path is wrong
**Tests:** `pytest tests/unit/performance/test_profiler_perf.py`

- [x] Replace `inspect.getsource` + "json.dump(" / "json.loads(" substring asserts with `patch('module.json.dump')` + `patch('module.json.loads')` at call site, then assert `not_called()`.
- [x] Verify: tests pass.

### Task 1.3: test_turn_engine_progress_callback.py — kwargs extraction
**Source:** Already done in PROJ-479 Task 3.18 — VERIFY ONLY, no action expected
**File:** `tests/unit/strategy/engine/test_turn_engine_progress_callback.py`
**Tests:** `pytest tests/unit/strategy/engine/test_turn_engine_progress_callback.py`

- [x] Verify the named-arg extraction pattern is still in place (no regression). If regressed, restore.
- [x] Verify: 5 tests pass.

### Task 1.4: test_app_public_api.py — inspect.signature asserts
**Source:** PROJ-479 Task 3.24
**File:** `tests/unit/test_app_public_api.py` (lines 39-47)
**Tests:** `pytest tests/unit/test_app_public_api.py`

- [x] Replace `inspect.signature(Game.__init__)` param-name/default assertions with a behavioral test: call `Game()` with no args, verify no exception.
- [x] Verify: tests pass.

### Task 1.5: test_turn_engine_lazy_properties.py — inspect.getsource + AST asserts
**Source:** PROJ-479 Task 3.21
**File:** `tests/unit/strategy/turn_engine/test_turn_engine_lazy_properties.py` (lines 219-251, 262-288)
**Tests:** `pytest tests/unit/strategy/turn_engine/test_turn_engine_lazy_properties.py`

- [x] Replace `inspect.getsource` source-text containment asserts (219-251) with behavioral test: construct with `battle_resolver=None`, verify ValueError raised.
- [x] Replace AST-parsing import-absence test (262-288) with either:
  - A static-guard test under `tests/static_guards/` (preferred — preserves the architectural intent), OR
  - Convert to a linter rule and delete the test (acceptable if a linter rule already covers it).
- [x] Verify: tests pass.

### Task 1.6: test_order_processor_facade.py — AST attribute counting
**Source:** PROJ-479 Task 3.22
**File:** `tests/unit/strategy/engine/order_handlers/test_order_processor_facade.py` (lines 32-57)
**Tests:** `pytest tests/unit/strategy/engine/order_handlers/test_order_processor_facade.py`

- [x] Replace `ast.Attribute`-counting OrderType reference test with either:
  - Behavioral test: dispatch each OrderType through the facade, assert handler invocation, OR
  - Keep as architectural guard with explicit comment about false-positive risk and accept-with-comment.
- [x] Verify: tests pass.

### Task 1.7: test_fleet_aura_cache.py — module-private function patch
**Source:** PROJ-479 Task 3.15
**File:** `tests/unit/simulation/combat/test_fleet_aura_cache.py` (lines 83-88)
**Tests:** `pytest tests/unit/simulation/combat/test_fleet_aura_cache.py`

- [x] Replace `_aggregate_ability_groups` private-function patch + call-count assertion with behavioral assertion on aggregation output (real groups, real input, assert grouped result equals expected dict/list).
- [x] Verify: tests pass.

### Task 1.8: test_order_processor_fleet_merge.py — internal recalc patch
**Source:** PROJ-479 Task 3.9
**File:** `tests/unit/strategy/engine/test_order_processor_fleet_merge.py` (lines 31-62)
**Tests:** `pytest tests/unit/strategy/engine/test_order_processor_fleet_merge.py`

- [x] Replace `trigger_speed_recalculation` patch with behavior-based assertion on merged fleet speed: set ship speeds explicitly, run merge, assert merged fleet speed == min(speeds).
- [x] Verify: tests pass.

### Task 1.9: test_ship_component_manager.py — private cache invalidation calls
**Source:** PROJ-479 Task 3.5
**File:** `tests/unit/builder/test_ship_component_manager.py` (lines 441, 444-445)
**Tests:** `pytest tests/unit/builder/test_ship_component_manager.py`

- [x] Replace direct `_invalidate_components_cache` call + `_components_dirty` / `_weapons_cache_dirty` reads with public Ship API: `add_component` / `remove_component` then verify via `get_all_components()` / `get_weapon_components_cached()` returning the expected updated set.
- [x] Verify: tests pass.

### Task 1.10: test_characterization.py — private passthrough
**Source:** PROJ-479 Task 3.12
**File:** `tests/unit/strategy/consumable_management_engine/test_characterization.py` (lines 92-101)
**Tests:** `pytest tests/unit/strategy/consumable_management_engine/test_characterization.py`

- [x] Remove the `_auto_disable_components_for_resource` mock; call the real method with real component definitions; assert correct disabling behavior on the public API surface.
- [x] Verify: tests pass.

### Task 1.11: test_strategy_input_handler_core.py — private _click_dispatch mocks
**Source:** PROJ-479 Task 3.4
**File:** `tests/unit/ui/screens/test_strategy_input_handler_core.py` (lines 186-704)
**Tests:** `pytest tests/unit/ui/screens/test_strategy_input_handler_core.py`

- [x] Replace `handler._click_dispatch._handle_picking = MagicMock()` pattern with `handle_click()` then observable outcomes (mode changes, callbacks). Large file — work in 3-4 batches by test class.
- [x] Verify: tests pass after each batch.

### Task 1.12: test_build_queue_panel_factory.py — blanket @fast_panel assertion
**Source:** PROJ-479 Task 3.1
**File:** `tests/unit/ui/screens/test_build_queue_panel_factory.py` (lines 170-206)
**Tests:** `pytest tests/unit/ui/screens/test_build_queue_panel_factory.py`

- [x] Replace blanket "every UIPanel uses @fast_panel" assertion with targeted per-logical-panel-group assertions OR a soft-warn that doesn't fail.
- [x] Verify: tests pass.

### Task 1.13: test_invalid_operation_handling.py — MagicMock-only modifier path
**Source:** PROJ-479 Task 3.2
**File:** `tests/unit/modifiers/test_invalid_operation_handling.py` (lines 38-58)
**Tests:** `pytest tests/unit/modifiers/test_invalid_operation_handling.py`

- [x] Replace MagicMock fleets/effects with real `Modifier` objects exercising the real path.
- [x] Verify: tests pass.

### Task 1.14: test_order_types_characterization.py — module-level monkeypatch
**Source:** PROJ-479 Task 3.29
**File:** `tests/unit/strategy/data/test_order_types_characterization.py` (lines 49-57)
**Tests:** `pytest tests/unit/strategy/data/test_order_types_characterization.py`

- [x] Replace module-level Planet/Fleet monkeypatch with a per-test factory returning stubbed instances. Enables per-test customization.
- [x] Verify: tests pass.

### Task 1.15: test_battle_panels_extended.py — sys.modules patch + importlib.reload
**Source:** PROJ-479 Task 3.31
**File:** `tests/unit/ui/test_battle_panels_extended.py` (lines 36-69)
**Tests:** `pytest tests/unit/ui/test_battle_panels_extended.py`

- [x] Factor `patch.dict(sys.modules, {'pygame': mock_pygame})` + `importlib.reload(battle_panels)` into a module-level context-manager fixture. Document the reload hazard in the fixture docstring. Add session-end teardown that re-imports the production module to prevent leakage.
- [x] Verify: tests pass.

### Task 1.16: test_strategy_screen.py — 6 mock-only delegation tests
**Source:** PROJ-479 Task 3.33
**File:** `tests/unit/ui/screens/test_strategy_screen.py` (lines 433-482)
**Tests:** `pytest tests/unit/ui/screens/test_strategy_screen.py`

- [x] Replace 6 `TestScreenLifecycle` tests asserting only mock method calls with integration-level tests asserting observable state changes. May require moving to `tests/integration/ui/`.
- [x] Verify: tests pass.

### Task 1.17: test_strategy_game_state_manager.py — patch.object on private methods
**Source:** PROJ-479 Task 3.20 (first bullet only — second bullet handled in Phase 4)
**File:** `tests/unit/ui/screens/test_strategy_game_state_manager.py` (lines 521-648)
**Tests:** `pytest tests/unit/ui/screens/test_strategy_game_state_manager.py`

- [x] Replace `patch.object(manager, ...)` on `_apply_turn_start_state` / `_sync_active_empire` / `_capture_outgoing_player_state` with behavioral assertions on the public turn-advance path (observe pre/post state of empire / fleet / UI).
- [x] Verify: tests pass.

### Task 1.18: test_transfer_handler_fleet_to_fleet.py — closure stubs
**Source:** PROJ-479 Task 3.3 — ENTRY CHECK REQUIRED
**File:** `tests/unit/strategy/engine/test_transfer_handler_fleet_to_fleet.py` (lines 44-109)
**Tests:** `pytest tests/unit/strategy/engine/test_transfer_handler_fleet_to_fleet.py`

- [x] **Entry check:** verify a minimal GameSession constructor exists (or is constructable from existing fixtures). If it doesn't exist, mark task BLOCKED and propose moving to PROJ-493 in plan.md Current State.
- [x] If tractable: replace MagicMock + lambda `add_order` + closure `_get_fleet_by_id` with a real `Fleet` and minimal `GameSession`. _BLOCKED — see test docstring; routing to PROJ-493 once a ``minimal_game_session`` fixture exists._
- [x] Verify: tests pass.

### Task 1.19: test_transfer_drop_pod.py — del planet.ships/.orders hack
**Source:** PROJ-479 Task 3.8
**File:** `tests/unit/strategy/validation/test_transfer_drop_pod.py` (lines 22-23 per PROJ-479; verify on entry — PROJ-479 cited `engine/` path but actual is `validation/`)
**Tests:** `pytest tests/unit/strategy/validation/test_transfer_drop_pod.py`

- [x] Replace `del planet.ships` / `del planet.orders` hack with `MagicMock(spec=Planet)` whose spec excludes those attributes, or use a proper duck-typed stub.
- [x] Verify: tests pass.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked (or marked BLOCKED with handoff)
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 2

_Source: PROJ-479 Phase 3 deferred tasks. See [findings/source_review.md](findings/source_review.md)._
