# Phase 3: CAT-10 parametrize (UI)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-494 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Parametrize structurally-identical test clusters in UI-family tests. Inherited from PROJ-480 Phase 3.

Line refs advisory — Phase 0 should have refreshed them. Re-grep before editing.

---

## Tasks

### Task 3.1: test_build_queue_helpers.py — 6+7 same-pattern tests
**File:** `tests/unit/ui/screens/test_build_queue_helpers.py`
**Tests:** `pytest tests/unit/ui/screens/test_build_queue_helpers.py`
**Origin:** PROJ-480 T3.1

- [ ] Parametrize the 6 `format_empire_resources` tests (PROJ-480 cited lines 42-115) and the 7 `format_resource_cost` tests (PROJ-480 cited lines 118-181).
- [ ] Verify: passes; LOC delta ≈ -100.

### Task 3.2: test_fleet_report_window_multi_select.py — 3 null-guard tests
**File:** `tests/unit/ui/screens/test_fleet_report_window_multi_select.py`
**Tests:** `pytest tests/unit/ui/screens/test_fleet_report_window_multi_select.py`
**Origin:** PROJ-480 T3.2

- [ ] Parametrize the 3 null-guard tests (PROJ-480 cited lines 241-265).
- [ ] Verify: passes; LOC delta ≈ -15.

### Task 3.3: test_system_selection_window.py — 2 cancel/confirm tests
**File:** `tests/unit/ui/screens/test_system_selection_window.py`
**Tests:** `pytest tests/unit/ui/screens/test_system_selection_window.py`
**Origin:** PROJ-480 T3.12

- [ ] Parametrize the 2 cancel/confirm tests with identical setup (PROJ-480 cited lines 12-232).
- [ ] Verify: passes; LOC delta ≈ -20.

### Task 3.4: test_planet_menu_items.py — 5+ TestPlanetMenuCapabilityMatrix tests
**File:** `tests/unit/ui/screens/test_planet_menu_items.py`
**Tests:** `pytest tests/unit/ui/screens/test_planet_menu_items.py`
**Origin:** PROJ-480 T3.13

- [ ] Parametrize 5+ TestPlanetMenuCapabilityMatrix tests (PROJ-480 cited lines 141-203).
- [ ] Verify: passes; LOC delta ≈ -50.

### Task 3.5: test_fleet_menu_items.py — 10+ FMS row tests
**File:** `tests/unit/ui/screens/test_fleet_menu_items.py`
**Tests:** `pytest tests/unit/ui/screens/test_fleet_menu_items.py`
**Origin:** PROJ-480 T3.14

- [ ] Parametrize the 10+ FMS row tests (PROJ-480 cited lines 409-624) on `(ability, label, condition)`. Uses existing module-level `_make_fleet` / `_make_galaxy` / `_mapper` helpers (T1.3 already-done dependency).
- [ ] Verify: passes; LOC delta ≈ -150.

### Task 3.6: test_strategy_input_handler_core.py — 4 escape-returns-to-select tests
**File:** `tests/unit/ui/screens/test_strategy_input_handler_core.py`
**Tests:** `pytest tests/unit/ui/screens/test_strategy_input_handler_core.py`
**Origin:** PROJ-480 T3.15

- [ ] Parametrize the 4 escape-returns-to-select tests on `mode` ∈ ["MOVE", "JOIN", "COLONIZE_TARGET", "TRANSFER"] (PROJ-480 cited lines 128-169).
- [ ] Verify: passes; LOC delta ≈ -25.

### Task 3.7: test_empire_build_queue_window.py — duplicate method name
**File:** `tests/unit/ui/screens/test_empire_build_queue_window.py`
**Tests:** `pytest tests/unit/ui/screens/test_empire_build_queue_window.py`
**Origin:** PROJ-480 T3.16

- [ ] Parametrize `test_toggle_column_hides_visible_column` (PROJ-480 cited lines 653-672, 2 defs — first is shadowed by second per Python rules) on `column_id` ∈ ["location", "build_rate"]; rename to `test_toggle_column_hides_any_column`.
- [ ] Verify: passes; LOC delta ≈ -10.

### Task 3.8: test_design_selector_window.py — 3 ID-sanitization tests
**File:** `tests/unit/ui/screens/test_design_selector_window.py`
**Tests:** `pytest tests/unit/ui/screens/test_design_selector_window.py`
**Origin:** PROJ-480 T3.19

- [ ] Extract `_assert_design_row_with_id(design_id, forbidden_chars)` helper for the 3 ID-sanitization tests (PROJ-480 cited lines 482-498, 500-523, 525-546). Runs AFTER Phase 2 Task 2.13 (T2.19 patch-stack extraction).
- [ ] Verify: passes; LOC delta ≈ -25.

### Task 3.9: test_strategy_input_handler_hotkeys.py — 3 hotkey clusters
**File:** `tests/unit/ui/screens/test_strategy_input_handler_hotkeys.py`
**Tests:** `pytest tests/unit/ui/screens/test_strategy_input_handler_hotkeys.py`
**Origin:** PROJ-480 T3.21

- [ ] Parametrize the M/J/C/T mode-activation cluster (4 tests, PROJ-480 cited lines 70-101).
- [ ] Parametrize the 4 zoom tests (PROJ-480 cited lines 181-208) on `(key, modifiers, camera_method)`.
- [ ] Parametrize the action tests (PROJ-480 cited lines 214-317, ~14 tests) into 2 sub-clusters: simple-action + fleet-dependent.
- [ ] Verify: passes; LOC delta ≈ -100.

### Task 3.10: test_planet_abilities_controller_scanner.py — 2 instance_label tests
**File:** `tests/unit/ui/screens/test_planet_abilities_controller_scanner.py`
**Tests:** `pytest tests/unit/ui/screens/test_planet_abilities_controller_scanner.py`
**Origin:** PROJ-480 T3.22

- [ ] Parametrize the 2 instance_label tests (PROJ-480 cited lines 121-153).
- [ ] Verify: passes; LOC delta ≈ -15.

### Task 3.11: test_setup_screen.py — 3 handle_event/update/draw hasattr tests
**File:** `tests/unit/ui/screens/test_setup_screen.py`
**Tests:** `pytest tests/unit/ui/screens/test_setup_screen.py`
**Origin:** PROJ-480 T3.23

- [ ] Parametrize the 3 hasattr+callable tests (PROJ-480 cited lines 389-408) on method name.
- [ ] Verify: passes; LOC delta ≈ -15.

### Task 3.12: test_ship_io.py — 7 round-trip tests
**File:** `tests/unit/ui/services/test_ship_io.py`
**Tests:** `pytest tests/unit/ui/services/test_ship_io.py`
**Origin:** PROJ-480 T3.26

- [ ] _(coordination note: addressed via DUP-003 in PROJ-479 Phase 5 Task 5.3. After that, parametrize remaining IO-specific properties locally; PROJ-480 cited lines 395-541.)_
- [ ] Verify: passes; LOC delta ≈ -75.

### Task 3.13: test_fleet_report_filters.py — warp filter + sort cluster
**File:** `tests/unit/ui/screens/test_fleet_report_filters.py`
**Tests:** `pytest tests/unit/ui/screens/test_fleet_report_filters.py`
**Origin:** PROJ-480 T3.30

- [ ] Parametrize the 3 warp filter tests (PROJ-480 cited lines 392-452) and 8+ sort tests (PROJ-480 cited lines 455-635). Runs AFTER Phase 2 Task 2.10 (T2.16 make_mock_ship shared fixture).
- [ ] Verify: passes; LOC delta ≈ -100.

### Task 3.14: test_battle_screen_simulation.py — 3 clusters
**File:** `tests/unit/ui/test_battle_screen_simulation.py` (retargeted from PROJ-480's `tests/unit/ui/screens/test_battle_screen_simulation.py`)
**Tests:** `pytest tests/unit/ui/test_battle_screen_simulation.py`
**Origin:** PROJ-480 T3.36

- [ ] Parametrize the 4 speed-multiplier-key tests (PROJ-480 cited lines 262-320).
- [ ] Parametrize the 3 battle-over tests (PROJ-480 cited lines 175-222).
- [ ] Parametrize the 3 input-handler tests (PROJ-480 cited lines 444-492).
- [ ] Verify: passes; LOC delta ≈ -60.

### Task 3.15: test_research_renderer.py — 10 + 7 visibility/margin tests
**File:** `tests/unit/research/test_research_renderer.py` (retargeted from PROJ-480's `tests/unit/ui/screens/test_research_renderer.py`)
**Tests:** `pytest tests/unit/research/test_research_renderer.py`
**Origin:** PROJ-480 T3.37

- [ ] Parametrize the 10 visibility tests (PROJ-480 cited lines 112-169; Codex spot-check 2026-05-23 saw cluster at `:174-239`) on `(pos, expected)`.
- [ ] Parametrize the 7 margin tests on `(pos, margin, expected)`.
- [ ] Verify: passes; LOC delta ≈ -100.

### Task 3.16: test_new_game_setup_controller.py — 2 callback tests
**File:** `tests/unit/ui/screens/test_new_game_setup_controller.py`
**Tests:** `pytest tests/unit/ui/screens/test_new_game_setup_controller.py`
**Origin:** PROJ-480 T3.38

- [ ] Parametrize the 2 tests (PROJ-480 cited lines 174-196) on `(callback_method, player_index, needs_modal_setup)`.
- [ ] Verify: passes; LOC delta ≈ -15.

### Task 3.17: test_event_log_sidebar.py — verify completion of 4 attribute tests
**File:** `tests/unit/ui/screens/test_event_log_sidebar.py`
**Tests:** `pytest tests/unit/ui/screens/test_event_log_sidebar.py`
**Origin:** PROJ-480 T3.41 (PARTIAL — PROJ-480 box left unchecked)

- [ ] Confirm the parametrize done in PROJ-480 (3 parametrized cases + 1 separate `test_stores_callback`) still passes — PROJ-480's plan checkbox was left unchecked under "Verify: passes; LOC delta ≈ -15." Run `pytest`, re-tick if green.
- [ ] If anything is still wrong, complete the parametrize.

### Task 3.18: test_empire_treasury_panel.py — 4 _format_value tests
**File:** `tests/unit/ui/panels/test_empire_treasury_panel.py`
**Tests:** `pytest tests/unit/ui/panels/test_empire_treasury_panel.py`
**Origin:** PROJ-480 T3.45

- [ ] Parametrize the 4 _format_value tests (PROJ-480 cited lines 235-284) on `(input_value, expected_output)`. Runs AFTER Phase 2 Task 2.14 (T2.20 4-decorator → class fixture).
- [ ] Verify: passes; LOC delta ≈ -15.

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 4 (CAT-11/12)
