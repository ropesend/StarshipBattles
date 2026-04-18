# Phase 6: Extract BattleSetupController (mutation + launch)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-282 6`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Extract mutation operations (fleet/TF/squadron CRUD, complex toggles, side add/remove, save/load, battle launch) from `FleetBattleSetupScreen` into a `BattleSetupController` class. The Controller is the only code that mutates `BattleSetupState`.

**Prerequisite:** Phase 5 complete — InputHandler exists and calls Controller methods. Phase 6 replaces the Controller stub with the real implementation.

---

## Tasks

### Task 6.1: Inventory mutation operations to extract [Simple]
**Tests:** N/A (research)

Inventoried from the Phase 1 audit's [delegate_map.md](../../../.agent_reports/PROJ-282-audit/delegate_map.md) + a read of the current screen:

- [x] Fleet CRUD: `add_fleet`, `remove_fleet` (screen had inline code in `_handle_button`; Controller gives them named methods)
- [x] Ship CRUD: `add_ship_from_design(design_index)`, `remove_ship(ship_index)`
- [x] TaskForce CRUD: `add_task_force`, `duplicate_task_force(tf_index)`, `delete_task_force(tf_index)` — ship-cloning stays inline on controller for now; Phase 7 pulls into `FleetHierarchyEditor`
- [x] Squadron CRUD: `add_squadron`, `duplicate_squadron(tf_index, sq_index)`, `delete_squadron(tf_index, sq_index)` — ditto
- [x] Policies: `set_fleet_battle_role(role_name)`, `set_ship_policy(key, display_name, options_list)`, `set_selected_policy(axis, display_name)`
- [x] Complex toggles: `toggle_complex(side_id, scope, design_id)` + `get_complex_toggle(...)`
- [x] Side management: `set_active_side(side_id)` — add/remove side UI deferred to a future phase (audit flagged; not mandated by Phase 6 checklist)
- [x] End-condition settings (moved off screen entirely — FIXES a latent Phase 3 dead-code bug where these fields were inside the `@available_designs.setter` and reset on every scan): `toggle_end_destroyed`, `toggle_end_derelict`, `toggle_end_mass_ratio`, `set_tick_limit_from_text(text)`
- [x] Save/load: `save_setup()`, `load_setup()` + test-friendly `_save_to_path(filepath)` / `_load_from_path(filepath)` hooks
- [x] Battle launch: `start_battle(headless)` — guard, `_sync_complex_toggles_to_state`, `_build_end_condition`, `build_manual_battle_spec`, fire `scene_callback`
- [x] Lifecycle: `start(preserve_teams)`, `scan_designs()` — screen's `start()` is now a one-line delegate
- [x] Scene navigation: `return_to_menu()` — fires the registered scene_callback

**Notes:** Screen kept backward-compat property shims for `tick_limit`, `end_all_destroyed`, `end_all_derelict`, `end_mass_ratio`, `mass_ratio_threshold`, and `_get_toggle` (the renderer's `left_panel.py` reads these via `screen.*`). Phase 8 drops the shims when the renderer can switch to reading via `screen.controller.*` or is itself slimmed.

### Task 6.2: Write tests for BattleSetupController [Complex]
**File:** `tests/unit/ui/screens/battle_setup/test_controller.py` (NEW)
**Tests:** `pytest tests/unit/ui/screens/battle_setup/test_controller.py`

- [x] One test per mutation method (31 tests total, use real `BattleSetupState` + `BattleSetupViewModel`, no UI mocks)
- [x] Test: `start_battle(headless=False)` fires callback with `"start_battle"` + spec; `headless=True` fires `"start_headless"`
- [x] Test: save/load round-trip via `_save_to_path` / `_load_from_path` — includes legacy `_complex_toggles` top-level key migration
- [x] Test: `remove_fleet` preserves the one-fleet minimum
- [x] Test: `TestSyncComplexTogglesIsNTeamSafe` regression — method iterates all sides (moved from screen-level tests that were deleted after extraction)
- [x] Test: end-condition toggle methods flip booleans + fire `on_change`; `set_tick_limit_from_text` parses/clamps/ignores correctly
- [x] Test: complex toggle flips state field; twice returns to off

**Notes:** Added `TestConstructorDefaults` + `TestLifecycle` + `TestFleetCRUD` + `TestSideDropdown` + `TestEndConditionToggles` + `TestComplexToggle` + `TestTaskForceCRUD` + `TestSquadronCRUD` + `TestSyncComplexTogglesIsNTeamSafe` + `TestBuildEndCondition` + `TestStartBattle` + `TestReturnToMenu` + `TestSaveLoadLegacyMigration` classes. 31 tests, all started red, green after Task 6.3.

### Task 6.3: Implement `BattleSetupController` [Complex]
**File:** `game/ui/screens/battle_setup/controller.py` (NEW — 458 LOC)
**Tests:** `pytest tests/unit/ui/screens/battle_setup/test_controller.py`

- [x] Constructor: `BattleSetupController(state, view_model, *, scene_callback=None, on_change=None)`. `scene_callback` fired by `start_battle` / `return_to_menu`. `on_change` fired after each mutation — screen passes `self._rebuild_ui` so the pygame_gui tree refreshes.
- [x] All 15 mutation methods + 4 end-condition toggles + `scan_designs` + `start(preserve_teams)` + `return_to_menu` + save/load.
- [x] TF/SQ CRUD: inline ship-cloning via `_clone_ship` static helper. Phase 7 moves into `FleetHierarchyEditor`.
- [x] `start_battle`: guard check (both sides need ships) → `_sync_complex_toggles_to_state` → `_build_end_condition` → `build_manual_battle_spec` → `scene_callback(action, spec=...)`.
- [x] Save/load: tkinter.filedialog wrapped in `save_setup` / `load_setup`; test-friendly `_save_to_path` / `_load_from_path` hooks do the actual I/O + legacy migration.
- [x] Controller is pygame-free. Tkinter is stdlib; fine to import.

**Notes:** Design decision (logged in [decisions.md 2026-04-18](decisions.md) "Phase 6 Controller: on_change callback + scene_callback"): controller fires `on_change()` after mutations instead of holding a reference to the screen or rebuilding pygame_gui itself. Keeps the controller testable without pygame. The screen hands `self._rebuild_ui` at construction time.

### Task 6.4: Wire Controller into InputHandler + Screen [Medium]
**Files:** `game/ui/screens/battle_setup/input_handler.py`, `game/ui/screens/battle_setup_screen.py`
**Tests:** `pytest tests/unit/ui/screens/`

- [x] Input handler retargeted — every `screen._*` mutation call became `screen.controller.*`. Selection-only updates (fleet/ship/TF/SQ button clicks) stay on `screen.view_model.*` directly since they're pure view state.
- [x] `_push_tick_limit_to_controller()` helper on the handler reads the tick-limit text entry before `start_battle` so the typed value flows to the controller.
- [x] Updated `test_input_handler.py` (Phase 5's 26 tests): mocked `screen.controller = MagicMock()`; assertions moved from `screen._add_ship_from_design.assert_called_once_with(7)` to `screen.controller.add_ship_from_design.assert_called_once_with(7)`. 4 tests added for add_fleet, remove_fleet, add_tf, add_sq, end_derelict, end_mass. Total: 30 tests.
- [x] Screen's `__init__` instantiates `self.controller = BattleSetupController(state, view_model, scene_callback=..., on_change=self._rebuild_ui)`.
- [x] Screen's `start()` is now a one-line delegate: `self.controller.start(preserve_teams=preserve_teams)`.
- [x] Added property shims on screen for `tick_limit`, `end_all_destroyed`, `end_all_derelict`, `end_mass_ratio`, `mass_ratio_threshold`, and `_get_toggle` — preserves the renderer's read access patterns during the transition.
- [x] Deleted 15 mutation methods (`_set_ship_policy`, `_set_selected_policy`, `_get_active_fleet`, `_add_task_force`, `_add_squadron`, `_duplicate_task_force`, `_delete_task_force`, `_duplicate_squadron`, `_delete_squadron`, `_set_fleet_battle_role`, `_add_ship_from_design`, `_remove_ship`, `_start_battle`, `_build_end_condition`, `_sync_complex_toggles_to_state`, `_save_setup`, `_load_setup`, `_scan_designs`) + the legacy end-condition field initializers + the `_toggle_dict_for` / `_set_toggle` helpers + the unused `os` import.
- [x] **FIXED Phase 3 dead-code bug:** end-condition settings (`tick_limit = 100000`, `end_all_destroyed = True`, etc.) were assigned inside the `@available_designs.setter` (unreachable from `__init__`, re-run on every scan). These attrs moved to the controller; the stray `setter`-body code is gone.
- [x] Screen line count dropped from **680 → 287** (−393 LOC). Plan target was "~260 line drop"; we went further because the dead-code setter block + the `_scan_designs` method also went.
- [x] Deleted the 2 screen-level `TestSyncComplexTogglesToStateIsNTeamSafe` tests in `test_battle_setup_state.py` — same coverage now lives in `test_controller.py::TestSyncComplexTogglesIsNTeamSafe` with real controller instances (no bypass-init needed).

**Notes:** 3563 tests pass after Phase 6 — up from 3470 at end of Phase 5 (+31 controller tests +4 input_handler tests −2 duplicated state tests). Screen is now 287 LOC: IScene protocol + property shims + `_rebuild_ui` / `start` delegates + state/view_model/renderer/input_handler/controller attributes. Phase 8 will further slim once module-level constant tables relocate to `battle_setup/constants.py`.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] `game/ui/screens/battle_setup/controller.py` exists with full mutation logic (458 LOC)
- [x] Screen no longer contains fleet/TF/squadron/toggle/launch/save mutation code
- [x] `wc -l game/ui/screens/battle_setup_screen.py` = 287 (was 680 at end of Phase 5; −393 LOC, exceeding the ~260 plan target)
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 7 (FleetHierarchyEditor)
