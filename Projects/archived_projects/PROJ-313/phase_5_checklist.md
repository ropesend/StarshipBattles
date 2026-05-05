# Phase 5: Migrate Registrar-Callback-Only Windows (5 windows)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-313 5`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Migrate the 5 windows that already follow the BUG-121 Registrar Close-Callback pattern (Pattern #30). Each migration replaces the manual `kill()` override and registrar `_on_closed` with the structural base class — net deletion of code, no new behaviour.

**Per-window pattern:** same as Phase 4 (subclass, drop kill override, drop on_close_callback param, drop registrar _on_closed, drop slot field, drop router clauses).

---

## Tasks

### Task 5.1: Migrate `PlanetListWindow` [Medium]
**File:** `game/ui/screens/planet_list_window.py`
**Registrar:** `game/ui/screens/strategy_windows/list_windows.py` (`PlanetListRegistrar._on_closed` at line 67 per audit)
**Spawn site:** `list_windows.py:52`
**Tests:** `pytest tests/unit/ui/screens/test_planet_list_window.py tests/unit/ui/screens/test_planet_list_components.py`

- [x] Subclass `StrategyModalWindow`
- [x] Forward `window_manager` keyword
- [x] Delete `kill()` override at line 681
- [x] Delete `on_close_callback` param from `__init__`
- [x] Delete `PlanetListRegistrar._on_closed`
- [x] Delete slot field, router clauses
- [x] Run targeted tests — pass
- [x] Run full sharded — 15893 preserved
**Notes:**

### Task 5.2: Migrate `StarListWindow` [Medium]
**File:** `game/ui/screens/star_list_window.py`
**Registrar:** `game/ui/screens/strategy_windows/list_windows.py` (`StarListRegistrar._on_closed` at line 99)
**Spawn site:** `list_windows.py:90`
**Tests:** `pytest tests/unit/ui/screens/test_star_list_window.py`

- [x] Same migration steps
- [x] Delete `kill()` override at line 452
- [x] Run targeted tests — pass
- [x] Run full sharded — 15893 preserved
**Notes:**

### Task 5.3: Migrate `BuildQueueListWindow` [Medium]
**File:** `game/ui/screens/build_queue_list_window.py`
**Registrar:** `game/ui/screens/strategy_windows/build_queue_windows.py` (`_on_closed` at line 43)
**Spawn site:** `build_queue_windows.py:34`
**Tests:** `pytest tests/unit/ui/screens/test_build_queue_list_window.py`

- [x] Same migration steps
- [x] Delete `kill()` override at line 123
- [x] Run targeted tests — pass
- [x] Run full sharded — 15893 preserved
**Notes:**

### Task 5.4: Migrate `FleetReportWindow` [Medium]
**File:** `game/ui/screens/fleet_report_window.py`
**Registrar:** `game/ui/screens/strategy_windows/fleet_report_ctrl.py` (`_on_closed` at line 62)
**Spawn site:** `fleet_report_ctrl.py:52`
**Tests:** `pytest tests/unit/ui/screens/test_fleet_report_window.py`

- [x] Same migration steps
- [x] Delete `kill()` override at line 360
- [x] Run targeted tests — pass
- [x] Run full sharded — 15893 preserved
**Notes:**

### Task 5.5: Migrate `PlanetAbilitiesWindow` [Medium]
**File:** `game/ui/screens/planet_abilities_window.py`
**Registrar:** `game/ui/screens/strategy_windows/planet_abilities_ctrl.py` (`_on_closed` at line 55)
**Spawn site:** `planet_abilities_ctrl.py:44`
**Tests:** `pytest tests/unit/ui/screens/test_planet_abilities_window_lifecycle.py tests/unit/ui/screens/test_strategy_input_handler_hotkeys.py`

- [x] Same migration steps
- [x] Delete `kill()` override at line 100-103 (the BUG-121 reference implementation — its job is now done by the base class)
- [x] **CARE:** The BUG-121 regression test `test_strategy_input_handler_hotkeys.py::test_scroll_after_close` must continue to pass — confirm it still works with the new structural mechanism.
- [x] Run targeted tests — pass
- [x] Run full sharded — 15893 preserved
**Notes:** This is the window that motivated Pattern #30 in the first place. After migration, Pattern #30 is fully retired (see Phase 8 doc updates).

### Task 5.6: Phase verification [Simple]
**Tests:** `python Tools/test_sharded/test_sharded.py`

- [x] All 5 windows migrated
- [x] Router scans shrunk by 5 clauses each
- [x] At this point, the OLD slot-based system has only `settings_window` left (intentional non-modal); plus any remaining branches in `_handle_window_close` for Phase 6/7 windows
- [x] Full sharded suite still 15893 passing
- [x] Manual smoke: open Planet List → Planet Abilities → close both. Open Star List, close. Open Build Queue, close. Open Fleet Report, close. Verify `has_modal_open()` returns False after each.
- [x] BUG-121 regression smoke: open Planet Abilities, close via `[X]`, immediately try mouse-wheel zoom on the strategy map — confirm it works.
**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 6 (Promote move_choice_window)
