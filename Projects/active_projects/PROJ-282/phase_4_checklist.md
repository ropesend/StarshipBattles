# Phase 4: Extract BattleSetupRenderer (panel construction)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-282 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Extract the three `_build_*_panel` methods (~447 lines of panel construction) into focused per-panel renderer modules under `game/ui/screens/battle_setup/panels/` plus a top-level `BattleSetupRenderer` orchestrator.

**Prerequisite:** Phase 3 complete — ViewModel exists; panels can read view-state from it.

---

## Tasks

### Task 4.1: Create `battle_setup/panels/` package [Simple]
**Files:** `game/ui/screens/battle_setup/panels/__init__.py` (NEW), `game/ui/screens/battle_setup/__init__.py` (update)
**Tests:** `pytest tests/unit/ui/screens/` — imports still work

- [ ] Create empty `panels/__init__.py`
- [ ] Update `battle_setup/__init__.py` to re-export panels if needed
- [ ] Note: `battle_setup/spec_compiler.py` already exists here and stays unchanged

**Notes:**

### Task 4.2: Extract `left_panel.py` [Medium]
**File:** `game/ui/screens/battle_setup/panels/left_panel.py` (NEW)
**Tests:** `pytest tests/unit/ui/screens/battle_setup/panels/test_left_panel.py` (NEW)

- [ ] Read `FleetBattleSetupScreen._build_left_panel` end-to-end
- [ ] Create `LeftPanelRenderer` class (or function, whichever fits) that takes `state: BattleSetupState`, `view_model: BattleSetupViewModel`, and pygame_gui manager arguments
- [ ] Port the left panel build logic verbatim (fleet/complex selection widgets)
- [ ] Add unit tests: smoke-test construction without pygame (use test helpers that short-circuit UI element creation if possible, otherwise mark as integration)

**Notes:**

### Task 4.3: Extract `center_panel.py` [Medium]
**File:** `game/ui/screens/battle_setup/panels/center_panel.py` (NEW)
**Tests:** `pytest tests/unit/ui/screens/battle_setup/panels/test_center_panel.py`

- [ ] Same pattern as Task 4.2 for the center (fleet hierarchy tree) panel
- [ ] Port `_build_center_panel` logic

**Notes:**

### Task 4.4: Extract `right_panel.py` [Medium]
**File:** `game/ui/screens/battle_setup/panels/right_panel.py` (NEW)
**Tests:** `pytest tests/unit/ui/screens/battle_setup/panels/test_right_panel.py`

- [ ] Same pattern as Task 4.2 for the right (design library) panel
- [ ] Port `_build_right_panel` logic
- [ ] Be careful: there's also a `right_panel.py` at [game/ui/screens/builder/right_panel.py](../../../game/ui/screens/builder/right_panel.py) — different file, same name. Avoid import confusion.

**Notes:**

### Task 4.5: Create `BattleSetupRenderer` orchestrator [Medium]
**File:** `game/ui/screens/battle_setup/renderer.py` (NEW)
**Tests:** `pytest tests/unit/ui/screens/battle_setup/test_renderer.py` (NEW)

- [ ] Class holds references to the 3 panel renderers
- [ ] Owns layout calculation (panel widths/positions for 2560×1600+ display)
- [ ] Provides a `rebuild_all(state, view_model)` method called by the screen on state changes
- [ ] Smoke test: construct + rebuild without errors

**Notes:**

### Task 4.6: Migrate screen to use BattleSetupRenderer [Medium]
**File:** `game/ui/screens/battle_setup_screen.py`
**Tests:** `pytest tests/unit/ui/screens/`

- [ ] Replace `_build_left_panel` / `_build_center_panel` / `_build_right_panel` calls with `self.renderer.rebuild_all(...)`
- [ ] Delete the 3 old `_build_*_panel` methods from the screen
- [ ] Screen line count drops by ~447 lines
- [ ] Existing tests still pass

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] `game/ui/screens/battle_setup/panels/{left,center,right}_panel.py` each exist
- [ ] `game/ui/screens/battle_setup/renderer.py` orchestrates them
- [ ] Screen's `_build_*_panel` methods DELETED
- [ ] `wc -l game/ui/screens/battle_setup_screen.py` shows ~450 fewer lines than at Phase 1 start
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 5 (extract InputHandler)
