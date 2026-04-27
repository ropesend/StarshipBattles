# Phase 11: N-Side UI support (Add Side / Remove Side buttons)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-282 11`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Surface the state-layer N-team support (PROJ-275's `BattleSetupState.add_side()` / `remove_side()` + MIN_SIDES=2 / MAX_SIDES=8 bounds) through the Battle Setup UI. Today the user can only set up 2-team battles; the state + spec compiler support 2..8, but there's no UI to drive it.

**Prerequisite:** Phases 1-9 complete. Scheduled **before** Phase 10 (manual smoke) — Phase 10 tasks 10.3 (3-side setup) and 10.4 (8-side max) depend on this UI.

**Context for why this was flagged late:** Phase 1's audit [n_team_paths.md](../../../.agent_reports/PROJ-282-audit/n_team_paths.md) explicitly called out the missing UI. The subsequent per-phase checklists focused on structural decomposition (ViewModel, Renderer, InputHandler, Controller, FleetHierarchyEditor, thin-shell, docs convention) and never scheduled the Add/Remove Side buttons as a concrete task. Adding it now as Phase 11 is cleaner than retro-fitting into Phase 4 or Phase 6 after they shipped.

---

## Scope

**In:**
- New `Controller.add_side()` and `Controller.remove_side(index)` methods delegating to `BattleSetupState.add_side()` / `remove_side(index)`
- New "Add Side" and "Remove Side" buttons in the left panel (near the existing side dropdown)
- Side dropdown populated dynamically from `state.sides` count (not hardcoded to 2)
- Button enable/disable respects `MIN_SIDES=2` / `MAX_SIDES=8` bounds
- InputHandler dispatches the new button events to controller
- Tests for: controller methods, handler dispatch, dropdown dynamic population

**Out:**
- Cosmetic / aesthetic polish on the side selector (tab strip vs dropdown vs cycle-buttons — see [n_team_paths.md](../../../.agent_reports/PROJ-282-audit/n_team_paths.md) "Decision point"). Stick with the existing dropdown pattern.
- Renaming "Left" / "Right" side labels for N>2. Flagged as low-priority UX polish.
- Strategy-mode N-team flows — PROJ-275 handles that separately.

---

## Tasks

### Task 11.1: Add `Controller.add_side()` / `remove_side()` [Simple]
**File:** `game/ui/screens/battle_setup/controller.py`
**Tests:** `tests/unit/ui/screens/battle_setup/test_controller.py` — `TestAddRemoveSide` class, 11 tests

- [x] Write test: `controller.add_side()` appends a new `BattleSetupSide`; `state.sides` count grows by 1
- [x] Write test: `controller.add_side()` switches `view_model.active_side` to the new side
- [x] Write test: `controller.add_side()` at MAX_SIDES (8) is a no-op + emits a warning via the module logger
- [x] Write test: `controller.add_side()` fires `on_change`
- [x] Write test: `controller.remove_side(index)` removes the side at `index`; subsequent `team_id`s renumber contiguously
- [x] Write test: `controller.remove_side(index)` at MIN_SIDES (2) is a no-op (no raise, no `on_change` fire)
- [x] Write test: `controller.remove_side(index)` of the active side clamps `view_model.active_side` to the last valid index
- [x] Write test: `controller.remove_side(index)` of a side BEFORE active shifts `view_model.active_side` down by 1 (tracks the same side)
- [x] Write test: `controller.remove_side(out_of_range)` is a no-op
- [x] Implement `add_side()` — calls `state.add_side()`, catches `ValueError` at cap, moves active_side to new last side, clears selection, fires `on_change`
- [x] Implement `remove_side(index)` — range-checks + calls `state.remove_side(index)`, catches `ValueError` at floor, reconciles `view_model.active_side` (clamp on same-side-removal, shift-down on before-active-removal), clears selection, fires `on_change`
- [x] Run `pytest tests/unit/ui/screens/battle_setup/test_controller.py::TestAddRemoveSide` — 11/11 pass

**Notes:** `state.add_side()` / `remove_side()` existed; controller wrappers add view-model reconciliation + bounds-tolerance (no raise at MIN/MAX so the UI button's disabled state isn't the only safety net).

### Task 11.2: Add Add/Remove Side buttons to left panel [Medium]
**File:** `game/ui/screens/battle_setup/panels/left_panel.py`
**Tests:** N/A (UI build code — covered by InputHandler tests + Phase 10 smoke)

- [x] Located the existing side-dropdown build block (was hardcoded 2-entry)
- [x] Replaced hardcoded options with dynamic `[f"Side {i}" for i in range(len(state.sides))]` — drops the `"(Left)"` / `"(Right)"` suffixes that lose meaning for N>2
- [x] Defensive: clamps `active_side` into range when building the default-selected text — safeguards against stale view_model state
- [x] Added `screen._add_side_btn` `UIButton` — labeled "Add Side" when `< MAX_SIDES`, `"Add Side (max 8)"` at cap; calls `.disable()` at cap
- [x] Added `screen._remove_side_btn` `UIButton` — labeled "Remove Side" when `> MIN_SIDES`, `"Remove (min 2)"` at floor; calls `.disable()` at floor
- [x] Also fixed a Phase 8 import-relocation miss: `battle_setup_screen` → `battle_setup.constants` for the complex-tables import

**Notes:** pygame_gui's `UIButton.disable()` visually greys the button + blocks click events. No InputHandler-side guard needed; the disabled button never dispatches.

### Task 11.3: Wire InputHandler dispatch [Simple]
**File:** `game/ui/screens/battle_setup/input_handler.py`
**Tests:** `tests/unit/ui/screens/battle_setup/test_input_handler.py`

- [x] Added `elif` branches for `screen._add_side_btn` → `controller.add_side()` and `screen._remove_side_btn` → `controller.remove_side(screen.view_model.active_side)` in `_handle_button`
- [x] Updated the dropdown parser: `int(event.text.split()[-1])` with fallback to 0 on parse failure (handles malformed text defensively)
- [x] Updated `_make_handler_with_mock_screen()` to include `_add_side_btn` + `_remove_side_btn` sentinels
- [x] Added 4 new tests: `test_add_side_button_calls_controller_add_side`, `test_remove_side_button_calls_controller_remove_active`, `test_side_dropdown_handles_n_gt_2`, `test_side_dropdown_fallback_on_malformed_text`
- [x] Updated the existing `test_side_dropdown_calls_controller_set_active_side_to_1` and `test_side_dropdown_back_to_0` — event text is now `"Side N"` (no more `"(Right)"` / `"(Left)"` suffix)
- [x] Run `pytest tests/unit/ui/screens/battle_setup/test_input_handler.py` — 34/34 pass

**Notes:** The 30 Phase 5+6 tests still pass unchanged. 4 new tests added; 2 existing tests updated to match the new dropdown format.

### Task 11.4: Verify spec compiler still happy [Simple]
**Tests:** `tests/integration/ui/test_battle_setup_three_sides.py` + new controller-level N-team launch test

- [x] Existing `test_battle_setup_three_sides.py` — 4 integration tests pass (state → spec compiler path unchanged)
- [x] Added `TestNTeamBattleLaunch::test_five_team_battle_compiles_and_fires_callback` in `test_controller.py` — grows to 5 sides via `controller.add_side()`, puts ships on each, calls `start_battle(headless=False)`, patches the spec compiler to avoid full materialization, asserts `build_manual_battle_spec` called + scene_callback fired with `"start_battle"`
- [x] PROJ-282 scope regression: **3561 tests pass** (tests/unit/ui/ + tests/integration/ui/). Up from 3545 at end of Phase 9 — gained 16 new Phase 11 tests (11 controller + 4 input_handler + 1 N-team integration).

**Notes:** No spec compiler changes were needed. The compiler already handled N teams per PROJ-275; Phase 11 just ships the UI surface to drive it.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] `BattleSetupController` has `add_side` + `remove_side` methods with MIN/MAX bounds handling + view-model reconciliation
- [x] Left panel has Add-Side + Remove-Side buttons wired through the InputHandler; buttons auto-disable at MIN/MAX
- [x] Side dropdown populates dynamically from `state.sides` count; drops "(Left)" / "(Right)" suffixes
- [x] PROJ-282 scope regression passes (3561 tests, +16 Phase 11)
- [x] Phase 10 smoke tasks 10.3 (3-side) and 10.4 (8-side max) are now unblocked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 10 (manual smoke)
