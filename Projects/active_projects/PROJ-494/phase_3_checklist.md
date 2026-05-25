# Phase 3: CAT-10 parametrize (UI)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-494 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Parametrize structurally-identical test clusters in UI-family tests. Inherited from PROJ-480 Phase 3.

---

## Tasks

### Task 3.1: test_build_queue_helpers.py — 6+7 same-pattern tests
- [x] Parametrized 6 format_empire_resources tests + 6 format_resource_cost tests on `(input, expected_substrs, forbidden_substrs, exact)`. Kept 2 structural-property tests separate (pipe separator, missing-resource graceful handling). 40 tests pass.

### Task 3.2: test_fleet_report_window_multi_select.py — 3 null-guard tests
- [x] Parametrized 3 null-guard tests on `(guard_name, apply_guard_lambda)`. 21 tests pass.

### Task 3.3: test_system_selection_window.py — 2 cancel/confirm tests
- [~] **Out of scope.** The 2 cancel/confirm tests have distinct assertions (cancel asserts `kill.assert_called_once`, confirm asserts callback receives system name, no-selection asserts non-crash). Parametrizing them would reduce clarity; each test exercises a fundamentally different concern.

### Task 3.4: test_planet_menu_items.py — 5+ TestPlanetMenuCapabilityMatrix tests
- [x] Parametrized 4 facility→label visibility tests on `(facility_abilities, expected_label, should_be_visible)`. Recover-X tests left distinct (multi-step assertions). 9 tests pass.

### Task 3.5: test_fleet_menu_items.py — 10+ FMS row tests
- [x] Parametrized 9 launch-row visibility tests (LayMines/LaunchFighters/LaunchSatellites × visible-with-ability-and-inventory / hidden-no-ability / hidden-no-inventory) on `(abilities, carried_type, expected_label, should_be_visible)`. Recover-X tests left distinct (multi-step galaxy setup). 33 tests pass.

### Task 3.6: test_strategy_input_handler_core.py — 4 escape-returns tests
- [x] Parametrized 4 ESC-returns-to-SELECT tests on `mode`. 46 tests pass.

### Task 3.7: test_empire_build_queue_window.py — duplicate method name
- [x] Merged 2 same-named `test_toggle_column_hides_visible_column` methods (the second shadowed the first per Python rules) into 1 parametrized `test_toggle_column_hides_any_column` on `column_id`. 129 tests pass.

### Task 3.8: test_design_selector_window.py — 3 ID-sanitization tests
- [x] Parametrized 2 of the 3 ID-sanitization tests on `(design_id, forbidden_chars)`. The third (`test_design_row_layout`) is a basic layout assertion, not a sanitization test, and stays distinct. 39 tests pass.

### Task 3.9: test_strategy_input_handler_hotkeys.py — 3 hotkey clusters
- [x] Parametrized 3 clusters: (1) 4 M/J/C/T mode-activation tests on `(key, expected_mode)`; (2) 3 fleet-keys-ignored-without-fleet tests on `key`; (3) 4 zoom-key tests on `(key, modifiers, camera_method_name)`. 43 tests pass.

### Task 3.10: test_planet_abilities_controller_scanner.py — 2 instance_label tests
- [~] **Out of scope.** The 2 instance_label tests have different setup (multiple components vs singleton) and short bodies. Parametrizing reduces clarity.

### Task 3.11: test_setup_screen.py — 3 hasattr+callable tests
- [x] Parametrized 3 IScene-protocol method-existence tests on method_name. 29 tests pass.

### Task 3.12: test_ship_io.py — 7 round-trip tests
- [x] Extracted shared `_roundtrip_ship(ship, registries, tmp_path)` helper. Parametrized 2 mock-ship-attribute preservation tests on `attr_name`. Other 5 tests build bespoke ships and stay distinct. 54 tests pass.

### Task 3.13: test_fleet_report_filters.py — warp filter + sort cluster
- [x] Parametrized 5 `TestHasWarpCapability` tests on `(mass, warp_tonnage, expected)`. The warp filter and sort tests have heterogeneous setup (different ship configurations) and stay distinct. 66 tests pass.

### Task 3.14: test_battle_screen_simulation.py — 3 clusters
- [x] Speed cluster parametrized into 4 cases; 3 winner-determination tests added as parametrize (Phase 5); input-handler cluster left distinct (each tests a different event-branch with different mocks/setup).

### Task 3.15: test_research_renderer.py — 10 + 7 visibility/margin tests
- [x] Visibility cluster parametrized in Phase 3; 4 directional margin tests parametrized in Phase 5; 3 heterogeneous margin tests (corners/zero/large) kept distinct.

### Task 3.16: test_new_game_setup_controller.py — 2 callback tests
- [x] Parametrized 2 race-callback tests on `(callback_method, player_index, needs_modal_setup)`. 25 tests pass.

### Task 3.17: test_event_log_sidebar.py — verify completion
- [x] Verified PROJ-480 parametrize work is intact — 13 tests pass.

### Task 3.18: test_empire_treasury_panel.py — 4 _format_value tests
- [x] Parametrized 4 `_format_value` tests into 11 cases on `(input_value, expected_output)` (each original test's multiple assertions become individual parametrize cases). 29 tests pass.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked (16 done, 2 marked out-of-scope `[~]`)
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 4 (CAT-11/12)
