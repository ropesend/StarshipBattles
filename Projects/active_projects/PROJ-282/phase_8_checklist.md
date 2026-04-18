# Phase 8: Slim FleetBattleSetupScreen to a thin scene shell

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-282 8`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** After Phases 3-7 extracted ViewModel, Renderer, InputHandler, Controller, FleetHierarchyEditor, the screen has no responsibility left except being the IScene shell. Move the screen into `game/ui/screens/battle_setup/screen.py` as a thin coordinator (~150 lines target).

**Prerequisite:** Phases 2-7 complete — all domain logic extracted into delegates.

---

## Tasks

### Task 8.1: Create new screen module [Medium]
**File:** `game/ui/screens/battle_setup/screen.py` (NEW)
**Tests:** `pytest tests/unit/ui/screens/`

- [ ] Create `FleetBattleSetupScreen(IScene)` class in the new location
- [ ] `__init__`: instantiate `BattleSetupState`, `BattleSetupViewModel`, `BattleSetupController`, `BattleSetupRenderer`, `BattleSetupInputHandler` — wire them together
- [ ] Implement IScene methods:
  - `handle_event(event)`: delegate to `self.input_handler.handle(event)`
  - `update(dt)`: call `self.renderer.update(dt)` if needed
  - `draw(screen)`: call `self.renderer.draw(screen)`
  - `handle_resize(w, h)`: call `self.renderer.handle_resize(w, h)`
- [ ] Line count target: ≤ 150 lines (hard target per audit)

**Notes:** Follow the exact shape of [game/ui/screens/test_lab/screen.py](../../../game/ui/screens/test_lab/screen.py).

### Task 8.2: Update package exports [Simple]
**File:** `game/ui/screens/battle_setup/__init__.py`, `game/ui/screens/__init__.py`
**Tests:** `pytest tests/unit/ui/screens/`

- [ ] `battle_setup/__init__.py` re-exports `FleetBattleSetupScreen` (and optionally `BattleSetupState`, `BattleSetupSide`)
- [ ] `game/ui/screens/__init__.py` maintains the `BattleSetupScreen = FleetBattleSetupScreen` alias so existing imports still work
- [ ] Verify `from game.ui.screens import BattleSetupScreen` still resolves

**Notes:**

### Task 8.3: Delete old `battle_setup_screen.py` [Medium]
**File:** `game/ui/screens/battle_setup_screen.py` (DELETE)
**Tests:** `pytest tests/unit/ui/` + integration tests

- [ ] Grep repo-wide for imports from `game.ui.screens.battle_setup_screen` — update each to `game.ui.screens.battle_setup.screen` (or rely on the re-export alias)
- [ ] Delete the file
- [ ] Run full PROJ-282 scope regression

**Notes:** `game.ui.screens.battle_setup_state` is a DIFFERENT file (holds `BattleSetupState` / `BattleSetupSide`). Be careful not to delete it.

### Task 8.4: Verify line counts [Simple]
**Tests:** N/A (verification)

- [ ] `wc -l game/ui/screens/battle_setup/screen.py` — should be ≤ 150 lines
- [ ] `wc -l game/ui/screens/battle_setup/renderer.py game/ui/screens/battle_setup/view_model.py game/ui/screens/battle_setup/input_handler.py game/ui/screens/battle_setup/controller.py game/ui/screens/battle_setup/fleet_hierarchy_editor.py` — each ≤ 300 lines
- [ ] `wc -l game/ui/screens/battle_setup/panels/*.py` — each ≤ 300 lines
- [ ] Record sizes in a comment on this checklist for the record

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Old `game/ui/screens/battle_setup_screen.py` DELETED
- [ ] New `game/ui/screens/battle_setup/screen.py` ≤ 150 lines
- [ ] All delegate files ≤ 300 lines
- [ ] Full PROJ-282 scope regression passes
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 9 (docs)
