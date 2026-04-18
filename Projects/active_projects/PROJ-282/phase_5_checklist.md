# Phase 5: Extract BattleSetupInputHandler

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-282 5`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Extract event-dispatch logic from the screen's `handle_event` method (~120 lines with `hasattr(element, '_fleet_index')` style dispatch) into a `BattleSetupInputHandler` class. The handler translates pygame_gui events into Controller method calls — no direct mutation.

**Prerequisite:** Phase 4 complete — Renderer exists. Phase 6 (Controller) will follow; the handler's method calls will route to Controller methods that Phase 6 creates.

---

## Tasks

### Task 5.1: Write tests for BattleSetupInputHandler [Medium]
**File:** `tests/unit/ui/screens/battle_setup/test_input_handler.py` (NEW)
**Tests:** `pytest tests/unit/ui/screens/battle_setup/test_input_handler.py`

- [x] Test: handler takes `screen` (a Mock in tests) in constructor
- [x] Test: `UI_BUTTON_PRESSED` on a fleet-create button calls `screen._*` mutation methods (fleet/ship/design/TF/SQ/complex/named-button branches)
- [x] Test: `UI_DROP_DOWN_MENU_CHANGED` on all 6 dropdowns dispatches to the expected screen method
- [x] Test: selection-only button clicks (fleet/ship/TF/SQ) write to `screen.view_model.*` directly; mutation buttons call `screen._*` methods
- [x] Test: unknown event types + unrecognized buttons are a no-op (no crash)
- [x] Test: every event family from the screen's existing handle_event is covered

**Notes:** 26 tests total in [test_input_handler.py](../../../tests/unit/ui/screens/battle_setup/test_input_handler.py). Used `SimpleNamespace(type=..., ui_element=...)` for synthetic events — real pygame_gui events are heavy to construct. Started red (26 fails), green after Task 5.2 implementation. **Deviation from checklist wording:** the handler takes `screen` not `(view_model, controller)` — because the Controller hasn't been extracted yet (Phase 6's job), the screen is the Controller's stand-in. The decision is documented in decisions.md and revisited in Phase 6.

### Task 5.2: Implement `BattleSetupInputHandler` [Medium]
**File:** `game/ui/screens/battle_setup/input_handler.py` (NEW)
**Tests:** `pytest tests/unit/ui/screens/battle_setup/test_input_handler.py`

- [x] Ported dispatch logic from `FleetBattleSetupScreen._handle_button` (105 LOC) + `_handle_dropdown` (17 LOC)
- [x] Kept the `hasattr(element, '_tag')` dispatch pattern — it's the simplest correct dispatch for pygame_gui elements carrying custom tags set by panel builders
- [x] Selection-only changes write to `screen.view_model.*`; mutations call `screen._*` methods (Phase 6 retargets these to `controller.*`)
- [x] Return value is implicit (None) — screen doesn't need the "consumed" signal; tests verify no-op for unknown events

**Notes:** 172 LOC module including docstrings and 2 dispatch methods. Slightly over the ~150 LOC target from [migration_plan.md](../../../.agent_reports/PROJ-282-audit/migration_plan.md); the overage is pure docstring content.

### Task 5.3: Migrate screen to use BattleSetupInputHandler [Medium]
**File:** `game/ui/screens/battle_setup_screen.py`
**Tests:** `pytest tests/unit/ui/screens/`

- [x] `__init__` now creates `self.input_handler = BattleSetupInputHandler(self)`
- [x] Screen's `handle_event` body trimmed to: process pygame_gui events on the UIManager, then `self.input_handler.handle_event(event)`
- [x] Deleted `_handle_button` (105 LOC) and `_handle_dropdown` (17 LOC) from the screen
- [x] Dropped now-unused `import pygame_gui` from the screen
- [x] Regression: 2146 tests pass (UI screens + integration UI)

**Notes:** Screen went 801 → 680 LOC (−121). The `_set_ship_policy` / `_set_selected_policy` / `_set_fleet_battle_role` mutation helpers stayed on the screen — the handler calls them. Phase 6 will move them to the Controller. Also kept `_rebuild_ui` / `_scan_designs` / save-load / start-battle / TF-SQ CRUD on the screen for Phase 6 extraction.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] `game/ui/screens/battle_setup/input_handler.py` exists with full dispatch logic
- [x] Screen's `handle_event` is a 2-line delegation (UIManager event-processing + `self.input_handler.handle_event(event)`)
- [x] Tests verify handler calls screen mutation methods (Phase 6 retargets to Controller)
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 6 (extract Controller)
