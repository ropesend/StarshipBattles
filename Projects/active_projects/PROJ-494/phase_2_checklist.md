# Phase 2: CAT-8 needless complexity (UI)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-494 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Flatten deeply-nested patch chains, oversized helper functions, and excessive mock wiring in UI-family tests. Inherited from PROJ-480 Phase 2.

Line refs are advisory — Phase 0 should have refreshed them. Re-grep before editing.

Within this phase, where a file is ALSO touched by Phase 3 (parametrize) or Phase 4 (fragile/logic), do Phase 2 FIRST so any newly-extracted fixture is available when the parametrize lands.

---

## Tasks

### Task 2.1: test_build_queue_panel_factory.py — fixture setup ratio
**File:** `tests/unit/ui/screens/test_build_queue_panel_factory.py`
**Tests:** `pytest tests/unit/ui/screens/test_build_queue_panel_factory.py`
**Origin:** PROJ-480 T2.3

- [ ] Extract `_build_factory_for_create_all_panels` mock UI configuration (PROJ-480 cited lines 133-168, 30 of 37 LOC are setup) into a reusable fixture.
- [ ] Verify: passes; LOC delta ≈ -30.

**Notes:** Same file is touched by Phase 4 Task 4.6 (T5.3 path-walk → Paths). Do this fixture extraction FIRST.

### Task 2.2: test_detail_panel_rendering.py — 7 patch starts in setup_method
**File:** `tests/unit/ui/test_detail_panel_rendering.py`
**Tests:** `pytest tests/unit/ui/test_detail_panel_rendering.py`
**Origin:** PROJ-480 T2.4

- [ ] Move pygame_gui mocks (PROJ-480 cited lines 16-76 setup_method) to a class-scoped shared fixture; 7 patch starts collapse to 1 fixture.
- [ ] Verify: passes; LOC delta ≈ -50.

### Task 2.3: test_event_log_window.py — _make_strategy_ui 25+ attrs
**File:** `tests/unit/ui/screens/test_event_log_window.py`
**Tests:** `pytest tests/unit/ui/screens/test_event_log_window.py`
**Origin:** PROJ-480 T2.6

- [ ] Convert `_make_strategy_ui` (PROJ-480 cited lines 259-306, manually sets 25+ attrs) into a fixture or factory accepting a field dict.
- [ ] Verify: passes; LOC delta ≈ -30.

### Task 2.4: test_camera.py — 13 triple-nested with patch() blocks
**File:** `tests/unit/ui/test_camera.py`
**Tests:** `pytest tests/unit/ui/test_camera.py`
**Origin:** PROJ-480 T2.7

- [ ] Extract the common patch triplet/quad stack used in 13 `TestCameraUpdateInput` methods (PROJ-480 cited lines 414-613) into a `@pytest.fixture` or use `patch.multiple()`.
- [ ] Verify: passes; LOC delta ≈ -60.

### Task 2.5: test_strategy_detail_formatter.py — 6-level patch nesting
**File:** `tests/unit/ui/screens/test_strategy_detail_formatter.py`
**Tests:** `pytest tests/unit/ui/screens/test_strategy_detail_formatter.py`
**Origin:** PROJ-480 T2.9

- [ ] Replace the 6-level `with patch()` nesting (PROJ-480 cited lines 129-151) with `patch.multiple()` or a fixture parameter.
- [ ] Verify: passes; LOC delta ≈ -15.

### Task 2.6: test_view_model.py (battle_setup) — 6 in-method BattleSetupViewModel imports
**File:** `tests/unit/ui/screens/battle_setup/test_view_model.py`
**Tests:** `pytest tests/unit/ui/screens/battle_setup/test_view_model.py`
**Origin:** PROJ-480 T2.10

- [ ] Add module-level import of `BattleSetupViewModel`; remove 6 in-method imports (PROJ-480 cited lines 14, 28, 35, 48, 61, 75).
- [ ] Verify: passes; LOC delta ≈ -6.

### Task 2.7: test_new_game_setup_extended.py — 7-layer mock setup
**File:** `tests/unit/ui/screens/test_new_game_setup_extended.py`
**Tests:** `pytest tests/unit/ui/screens/test_new_game_setup_extended.py`
**Origin:** PROJ-480 T2.13

- [ ] Flatten the 7-layer mock setup (PROJ-480 cited lines 407-440, 1 context patch + 1 patch.object + 5 side_effect lambdas) into a single fixture.
- [ ] Verify: passes; LOC delta ≈ -25.

### Task 2.8: test_strategy_game_state_manager.py — _make_*_state_manager overlap
**File:** `tests/unit/ui/screens/test_strategy_game_state_manager.py`
**Tests:** `pytest tests/unit/ui/screens/test_strategy_game_state_manager.py`
**Origin:** PROJ-480 T2.14

- [ ] Merge `_make_game_state_manager()` (PROJ-480 cited lines 10-64) and `_make_n_player_state_manager()` (PROJ-480 cited lines 821-870) into one parametrized helper — they share ~80% structure.
- [ ] Verify: passes; LOC delta ≈ -50.

### Task 2.9: test_modifier_impact_grid.py — duplicated pygame init blocks
**File:** `tests/unit/ui/test_modifier_impact_grid.py`
**Tests:** `pytest tests/unit/ui/test_modifier_impact_grid.py`
**Origin:** PROJ-480 T2.15

- [ ] Extract the identical pygame.init + display.set_mode + UIManager setup block (PROJ-480 cited lines 10-18 and 235-244) into a shared fixture.
- [ ] Verify: passes; LOC delta ≈ -10.

### Task 2.10: test_fleet_report_filters.py — 98-line make_mock_ship factory
**File:** `tests/unit/ui/screens/test_fleet_report_filters.py`
**Tests:** `pytest tests/unit/ui/screens/test_fleet_report_filters.py`
**Origin:** PROJ-480 T2.16

- [ ] Move `make_mock_ship()` (12 params, ~102 LOC at PROJ-480-cited lines 12-113) to a shared fixture in `tests/fixtures/ship_mocks.py`.
- [ ] Verify: passes; LOC delta ≈ -90.

**Notes:** Same file is touched by Phase 3 Task 3.13 (T3.30 warp filter + sort cluster). Do this fixture extraction FIRST so the parametrize body uses the new fixture.

### Task 2.11: test_race_summary_panel.py — _refresh_with_mocked_uilabel
**File:** `tests/unit/ui/test_race_summary_panel.py`
**Tests:** `pytest tests/unit/ui/test_race_summary_panel.py`
**Origin:** PROJ-480 T2.17

- [ ] Extract nested patches in `_refresh_with_mocked_uilabel` (PROJ-480 cited lines 363-414, 4 patch.object + 12+ attr wirings) into a shared fixture factory accepting a field dict.
- [ ] _(coordination note: also touches Phase 3 of PROJ-479 for CAT-6 __new__ rewrite. Sequence: do PROJ-479 Phase 3 first if possible.)_
- [ ] Verify: passes; LOC delta ≈ -40.

### Task 2.12: test_bug_04_display.py — 15 patches with 4-level nesting
**File:** `tests/repro_issues/test_bug_04_display.py`
**Tests:** `pytest tests/repro_issues/test_bug_04_display.py`
**Origin:** PROJ-480 T2.18

- [ ] Move the 15-patch / 4-level-nested setup (PROJ-480 cited lines 45-105) to a conftest pytest fixture.
- [ ] Verify: passes; LOC delta ≈ -40.

### Task 2.13: test_design_selector_window.py — 6-deep nested patch stack ×3
**File:** `tests/unit/ui/screens/test_design_selector_window.py`
**Tests:** `pytest tests/unit/ui/screens/test_design_selector_window.py`
**Origin:** PROJ-480 T2.19

- [ ] Extract the 6-deep nested patch stack duplicated across 3 tests (PROJ-480 cited lines 490-540) into a shared context-manager helper.
- [ ] Verify: passes; LOC delta ≈ -40.

**Notes:** Same file is touched by Phase 3 Task 3.10 (T3.19 ID-sanitization helper). Do Task 2.13 FIRST.

### Task 2.14: test_empire_treasury_panel.py — identical 4-decorator stack ×16
**File:** `tests/unit/ui/panels/test_empire_treasury_panel.py`
**Tests:** `pytest tests/unit/ui/panels/test_empire_treasury_panel.py`
**Origin:** PROJ-480 T2.20

- [ ] Apply the 4-decorator stack via pytest fixture parametrization or class-scope, rather than repeating on all 16 methods (PROJ-480 cited lines 238-631).
- [ ] Verify: passes; LOC delta ≈ -40.

**Notes:** Same file is touched by Phase 3 Task 3.18 (T3.45 _format_value parametrize). Do Task 2.14 FIRST.

### Task 2.15: test_strategy_screen.py — 7-patch init test
**File:** `tests/unit/ui/screens/test_strategy_screen.py`
**Tests:** `pytest tests/unit/ui/screens/test_strategy_screen.py`
**Origin:** PROJ-480 T2.21

- [ ] Use `patch.multiple` to collapse the 7-patch with-block in `test_init_with_injected_composition_wires_slots` (PROJ-480 cited lines 198-216, test body lines 134-252). _(severity downgraded to MINOR — patch count reflects constructor DI count, not test design flaw.)_
- [ ] Verify: passes; LOC delta ≈ -15.

### Task 2.16: test_structure_visibility.py — 8-patch with-statement
**File:** `tests/unit/ui/test_structure_visibility.py`
**Tests:** `pytest tests/unit/ui/test_structure_visibility.py`
**Origin:** PROJ-480 T2.22

- [ ] Use `patch.multiple` for each of the 2 module groups in `setup_mocks` (PROJ-480 cited lines 29-36, 4 patches each).
- [ ] Verify: passes; LOC delta ≈ -10.

### Task 2.17: test_strategy_screen_selection.py — 4 patch.object × 6 methods
**File:** `tests/unit/ui/screens/test_strategy_screen_selection.py`
**Tests:** `pytest tests/unit/ui/screens/test_strategy_screen_selection.py`
**Origin:** PROJ-480 T2.28

- [ ] Extract `patcher_selection` fixture returning dict of 4 patchers; yield `patchers.start()` so tests reference via fixture instead of inline (PROJ-480 cited lines 48-122).
- [ ] Verify: passes; LOC delta ≈ -30.

### Task 2.18: test_build_queue_formatting.py — 60-line MockSession class
**File:** `tests/integration/ui/test_build_queue_formatting.py` (retargeted from PROJ-480's `tests/unit/ui/screens/test_build_queue_formatting.py`)
**Tests:** `pytest tests/integration/ui/test_build_queue_formatting.py`
**Origin:** PROJ-480 T2.30

- [ ] Move MockSession (Codex spot-check 2026-05-23 confirmed still at `:28-88`, with nested `_EconomyNS`/`_SessionMetaNS` + 9 methods) to `tests/integration/ui/conftest.py` for reuse.
- [ ] Verify: passes; LOC delta ≈ -60.

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 3 (CAT-10 parametrize)
