# Phase 2: CAT-8 Needless Complexity

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-480 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Flatten ~30 verified CAT-8 needlessly-complex test sites from review `2026-05-20_210550_test-review`. Deeply-nested `with patch()` chains, oversized helper functions, excessive mock wiring. Extract helpers and shared fixtures; use `patch.multiple` to collapse stacks.

---

## Tasks

### Task 2.1: test_workshop_screen.py — repeated mock/lambda definitions
**File:** `tests/unit/ui/screens/test_workshop_screen.py`
**Tests:** `pytest tests/unit/ui/screens/test_workshop_screen.py`

- [ ] _(Subsumed by PROJ-478 Phase 2 deletion of CAT-2 cluster — once those tests are removed, this CAT-8 finding evaporates.)_
- [ ] Verify: re-check after PROJ-478 Phase 2.

### Task 2.2: test_resource_pipeline.py — monolithic integration test
**File:** `tests/integration/resource_system/test_resource_pipeline.py`
**Tests:** `pytest tests/integration/resource_system/test_resource_pipeline.py`

- [ ] Split the 73-line monolithic test (lines 22-95) into focused tests at each logical step (intermediate assertions at lines 48, 80-81 mark the natural split points).
- [ ] Verify: passes; LOC delta ≈ +20 (split adds method overhead but each test independently failable).

### Task 2.3: test_build_queue_panel_factory.py — fixture setup ratio
**File:** `tests/unit/ui/screens/test_build_queue_panel_factory.py`
**Tests:** `pytest tests/unit/ui/screens/test_build_queue_panel_factory.py`

- [ ] Extract `_build_factory_for_create_all_panels` mock UI configuration (lines 133-168, 30 of 37 LOC are setup) into a reusable fixture.
- [ ] Verify: passes; LOC delta ≈ -30.

### Task 2.4: test_detail_panel_rendering.py — 7 patch starts in setup_method
**File:** `tests/unit/ui/test_detail_panel_rendering.py`
**Tests:** `pytest tests/unit/ui/test_detail_panel_rendering.py`

- [ ] Move pygame_gui mocks (lines 16-76 setup_method) to a class-scoped shared fixture; 7 patch starts collapse to 1 fixture.
- [ ] Verify: passes; LOC delta ≈ -50.

### Task 2.5: test_ai_controller_unit.py — 3 nested patches × multiple tests
**File:** `tests/unit/ai/test_ai_controller_unit.py`
**Tests:** `pytest tests/unit/ai/test_ai_controller_unit.py`

- [ ] Extract the 3-nested patch + lambda capture stack (lines 284-325) into a shared context-manager helper.
- [ ] Address the 4-nested patches (lines 367-420) — apply same extraction. _(NEEDS_REWORK: original claim said 5 patches; actual is 4. Severity stays MINOR.)_
- [ ] Refactor TestNavigateTo cluster (lines 623-809, 12 test methods each rebuild AIController with slight variations) — extract `_make_ai_controller(**overrides)` helper.
- [ ] Verify: passes; LOC delta ≈ -80.

### Task 2.6: test_event_log_window.py — _make_strategy_ui 25+ attrs
**File:** `tests/unit/ui/screens/test_event_log_window.py`
**Tests:** `pytest tests/unit/ui/screens/test_event_log_window.py`

- [ ] Convert `_make_strategy_ui` (lines 259-306, manually sets 25+ attrs) into a fixture or factory accepting a field dict.
- [ ] Verify: passes; LOC delta ≈ -30.

### Task 2.7: test_camera.py — 13 triple-nested with patch() blocks
**File:** `tests/unit/ui/test_camera.py`
**Tests:** `pytest tests/unit/ui/test_camera.py`

- [ ] Extract the common patch triplet/quad stack used in 13 TestCameraUpdateInput methods (lines 414-613) into a `@pytest.fixture` or use `patch.multiple()`.
- [ ] Verify: passes; LOC delta ≈ -60.

### Task 2.8: test_ship_stats.py — 43-line setup for 8-line test body
**File:** `tests/unit/simulation/entities/test_ship_stats.py`
**Tests:** `pytest tests/unit/simulation/entities/test_ship_stats.py`

- [ ] Compress the `_TL_ABILITY`/`_VS_ABILITY` SimpleNamespace + `_HangarComponent` class + 9-attribute MagicMock ship setup (lines 12-55) into a fixture; per-test setup drops dramatically.
- [ ] Verify: passes; LOC delta ≈ -30.

### Task 2.9: test_strategy_detail_formatter.py — 6-level patch nesting
**File:** `tests/unit/ui/screens/test_strategy_detail_formatter.py`
**Tests:** `pytest tests/unit/ui/screens/test_strategy_detail_formatter.py`

- [ ] Replace the 6-level `with patch()` nesting at lines 129-151 (is_star_system / is_star / is_planet / is_fleet / is_warp_point / is_sector_environment) with `patch.multiple()` or a fixture parameter.
- [ ] Verify: passes; LOC delta ≈ -15.

### Task 2.10: test_view_model.py — 6 in-method BattleSetupViewModel imports
**File:** `tests/unit/ui/screens/battle_setup/test_view_model.py`
**Tests:** `pytest tests/unit/ui/screens/battle_setup/test_view_model.py`

- [ ] Add module-level import of `BattleSetupViewModel`; remove 6 in-method imports (lines 14, 28, 35, 48, 61, 75).
- [ ] Verify: passes; LOC delta ≈ -6.

### Task 2.11: test_container.py — 5 trivial wrapper functions
**File:** `tests/unit/strategy/test_container.py`
**Tests:** `pytest tests/unit/strategy/test_container.py`

- [ ] Inline or use constants for the 5 single-line wrapper functions at lines 38-63 (`_any_policy`, `_metals`, `_energy`, `_human`, `_fighter`). Wrapper-of-stateless-constructor adds noise.
- [ ] Verify: passes; LOC delta ≈ -15.

### Task 2.12: test_resupply_engine.py — 9 module-level mock factories
**File:** `tests/unit/strategy/engine/test_resupply_engine.py`
**Tests:** `pytest tests/unit/strategy/engine/test_resupply_engine.py`

- [ ] Move the 9 module-level mock factory helpers (lines 20-101, 306-379) to `tests/unit/strategy/engine/conftest.py`.
- [ ] _(coordination note: tied to DUP-005 / HLP-006 sweep in PROJ-479 Phase 5/6.)_
- [ ] Verify: passes; LOC delta ≈ -50.

### Task 2.13: test_new_game_setup_extended.py — 7-layer mock setup
**File:** `tests/unit/ui/screens/test_new_game_setup_extended.py`
**Tests:** `pytest tests/unit/ui/screens/test_new_game_setup_extended.py`

- [ ] Flatten the 7-layer mock setup (lines 407-440, 1 context patch + 1 patch.object + 5 side_effect lambdas) into a single fixture.
- [ ] Verify: passes; LOC delta ≈ -25.

### Task 2.14: test_strategy_game_state_manager.py — _make_*_state_manager overlap
**File:** `tests/unit/ui/screens/test_strategy_game_state_manager.py`
**Tests:** `pytest tests/unit/ui/screens/test_strategy_game_state_manager.py`

- [ ] Merge `_make_game_state_manager()` (lines 10-64) and `_make_n_player_state_manager()` (lines 821-870) into one parametrized helper — they share ~80% structure (StrategyGameStateManager wiring, screen mocks, etc.).
- [ ] Verify: passes; LOC delta ≈ -50.

### Task 2.15: test_modifier_impact_grid.py — duplicated pygame init blocks
**File:** `tests/unit/ui/test_modifier_impact_grid.py`
**Tests:** `pytest tests/unit/ui/test_modifier_impact_grid.py`

- [ ] Extract the identical pygame.init + display.set_mode + UIManager setup block (lines 10-18 and 235-244) into a shared fixture.
- [ ] Verify: passes; LOC delta ≈ -10.

### Task 2.16: test_fleet_report_filters.py — 98-line make_mock_ship factory
**File:** `tests/unit/ui/screens/test_fleet_report_filters.py`
**Tests:** `pytest tests/unit/ui/screens/test_fleet_report_filters.py`

- [ ] Move `make_mock_ship()` (12 params, 98 LOC at lines 12-109) to a shared fixture in `tests/fixtures/ship_mocks.py`.
- [ ] Verify: passes; LOC delta ≈ -90 (or shared between files).

### Task 2.17: test_race_summary_panel.py — _refresh_with_mocked_uilabel
**File:** `tests/unit/ui/test_race_summary_panel.py`
**Tests:** `pytest tests/unit/ui/test_race_summary_panel.py`

- [ ] Extract nested patches in `_refresh_with_mocked_uilabel` (lines 363-414, 4 patch.object + 12+ attr wirings) into a shared fixture factory accepting a field dict.
- [ ] _(coordination note: also touches Phase 3 of PROJ-479 for CAT-6 __new__ rewrite. Sequence: do PROJ-479 Phase 3 first if possible.)_
- [ ] Verify: passes; LOC delta ≈ -40.

### Task 2.18: test_bug_04_display.py — 15 patches with 4-level nesting
**File:** `tests/repro_issues/test_bug_04_display.py`
**Tests:** `pytest tests/repro_issues/test_bug_04_display.py`

- [ ] Move the 15-patch / 4-level-nested setup (lines 45-105) to a conftest pytest fixture.
- [ ] Verify: passes; LOC delta ≈ -40.

### Task 2.19: test_design_selector_window.py — 6-deep nested patch stack ×3
**File:** `tests/unit/ui/screens/test_design_selector_window.py`
**Tests:** `pytest tests/unit/ui/screens/test_design_selector_window.py`

- [ ] Extract the 6-deep nested patch stack duplicated across 3 tests (lines 490-540) into a shared context-manager helper.
- [ ] Verify: passes; LOC delta ≈ -40.

### Task 2.20: test_empire_treasury_panel.py — identical 4-decorator stack ×16
**File:** `tests/unit/ui/panels/test_empire_treasury_panel.py`
**Tests:** `pytest tests/unit/ui/panels/test_empire_treasury_panel.py`

- [ ] Apply the 4-decorator stack via pytest fixture parametrization or class-scope, rather than repeating on all 16 methods (lines 238-631).
- [ ] Verify: passes; LOC delta ≈ -40.

### Task 2.21: test_strategy_screen.py — 7-patch init test
**File:** `tests/unit/ui/screens/test_strategy_screen.py`
**Tests:** `pytest tests/unit/ui/screens/test_strategy_screen.py`

- [ ] Use `patch.multiple` to collapse the 7-patch with-block in `test_init_with_injected_composition_wires_slots` (lines 178-231). _(NEEDS_REWORK: severity downgraded to MINOR — patch count reflects constructor DI count, not test design flaw.)_
- [ ] Verify: passes; LOC delta ≈ -15.

### Task 2.22: test_structure_visibility.py — 8-patch with-statement
**File:** `tests/unit/ui/test_structure_visibility.py`
**Tests:** `pytest tests/unit/ui/test_structure_visibility.py`

- [ ] Use `patch.multiple` for each of the 2 module groups in `setup_mocks` (lines 29-36, 4 patches each).
- [ ] Verify: passes; LOC delta ≈ -10.

### Task 2.23: test_fleet_navigation_action_timing.py — 5 double-patch tests
**File:** `tests/unit/strategy/services/test_fleet_navigation_action_timing.py`
**Tests:** `pytest tests/unit/strategy/services/test_fleet_navigation_action_timing.py`

- [ ] Extract the 2-level nested `with patch(find_hybrid_path)` pattern (lines 66-308, 5 test methods) into a helper context manager. PROJ-323 Task 2.14 acknowledged the intent.
- [ ] Verify: passes; LOC delta ≈ -30.

### Task 2.24: test_app_public_api.py — 29-name parametrize
**File:** `tests/unit/test_app_public_api.py`
**Tests:** `pytest tests/unit/test_app_public_api.py`

- [ ] _(verification: VERIFIED but already-optimally parametrized. No action required — task retained for traceability.)_

### Task 2.25: test_app_public_api.py — inspect.signature
**File:** `tests/unit/test_app_public_api.py`
**Tests:** `pytest tests/unit/test_app_public_api.py`

- [ ] _(coordination note: addressed via Task 3.24 in PROJ-479 Phase 3 CAT-6.)_

### Task 2.26: test_scenarios.py fixture — 88-line shared fixture
**File:** `tests/fixtures/test_scenarios.py`
**Tests:** `pytest tests/fixtures/`

- [ ] _(verification: VERIFIED but acceptable as a shared fixture utility. No action required.)_

### Task 2.27: test_renderer.py — bypass + isinstance smoke
**File:** `tests/unit/ui/screens/battle_setup/test_renderer.py`
**Tests:** `pytest tests/unit/ui/screens/battle_setup/test_renderer.py`

- [ ] _(verification: VERIFIED but accepted as low-value contract guard per review's own recommendation. No action required.)_

### Task 2.28: test_strategy_screen_selection.py — 4 patch.object × 6 methods
**File:** `tests/unit/ui/screens/test_strategy_screen_selection.py`
**Tests:** `pytest tests/unit/ui/screens/test_strategy_screen_selection.py`

- [ ] Extract `patcher_selection` fixture returning dict of 4 patchers; yield `patchers.start()` so tests reference via fixture instead of inline (lines 33-104).
- [ ] Verify: passes; LOC delta ≈ -30.

### Task 2.29: test_tech_preset_loader.py — identical patch wrapper
**File:** `tests/unit/strategy/data/test_tech_preset_loader.py`
**Tests:** `pytest tests/unit/strategy/data/test_tech_preset_loader.py`

- [ ] Move the identical `with patch('TECH_PRESETS_DIR', str(temp_presets_dir))` wrapper (every test in 5+ class methods) to a `@pytest.fixture(autouse=True)` in the class.
- [ ] Verify: passes; LOC delta ≈ -25.

### Task 2.30: test_build_queue_formatting.py — 60-line MockSession class
**File:** `tests/unit/ui/screens/test_build_queue_formatting.py`
**Tests:** `pytest tests/unit/ui/screens/test_build_queue_formatting.py`

- [ ] Move MockSession (lines 28-88, with nested `_EconomyNS`/`_SessionMetaNS` + 9 methods) to `tests/integration/ui/conftest.py` for reuse.
- [ ] Verify: passes; LOC delta ≈ -60.

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase (Phase 3 — CAT-10 Parametrize)

_Source review: `Reviews/results/2026-05-20_210550_test-review/`. See [findings/source_review.md](findings/source_review.md) for the link._
