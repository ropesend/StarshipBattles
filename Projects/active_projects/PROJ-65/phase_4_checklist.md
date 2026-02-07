# Phase 4: Cleanup & Tests

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-65 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Delete dead code, update tests, verify everything works end-to-end.

---

## Tasks

### Task 4.1: Delete Dead Code [Simple]
**Files:** `game/app.py`, `game/battle_coordinator.py`, `game/ui/screens/battle_input_handler.py`
**Tests:** `pytest tests/ --tb=short`

- [ ] Delete `game/battle_coordinator.py` (all logic moved to BattleScreen in Phase 2)
- [ ] Delete or gut `game/ui/screens/battle_input_handler.py` (logic moved to BattleScreen)
- [ ] Remove now-unused imports from `game/app.py` (battle_coordinator, BattleInputHandler)
- [ ] Remove `_draw_menu()`, `update_menu_buttons()` from Game (moved to MenuScene)
- [ ] Remove `_update_battle_setup()`, `_update_battle()` from Game (logic now in scenes)
- [ ] Remove `_handle_battle_actions()`, `_handle_click()`, `_handle_scroll()`, `_handle_keydown()` from Game
- [ ] Remove all `hasattr` guards for scenes
- [ ] Verify: no dead imports or unreachable methods in app.py

**Notes:**

### Task 4.2: Update Tests [Medium]
**Files:** `tests/unit/test_app_integration.py`, `tests/unit/systems/test_main_integration.py`
**Tests:** `pytest tests/unit/test_app_integration.py tests/unit/systems/test_main_integration.py --tb=short`

- [ ] Update `test_main_integration.py` to work with new Game.__init__ signature (args parameter)
- [ ] Update `test_app_integration.py` for any changed method signatures
- [ ] Add test: verify IScene protocol is satisfied by all scene classes (isinstance checks)
- [ ] Add test: verify `_switch_scene()` updates `self.active_scene` correctly
- [ ] Add test: verify `scene_callback` dispatches correctly for key actions

**Notes:**

### Task 4.3: Final Verification [Simple]
**Tests:** `pytest tests/` (full suite)

- [ ] Run full test suite — expect 6225+ passed (same as baseline)
- [ ] Manually verify app launches: `python -m game.app`
- [ ] Verify scene transitions: Menu → Builder → Menu
- [ ] Verify scene transitions: Menu → Battle Setup → Battle → Menu
- [ ] Verify scene transitions: Menu → Strategy (quickstart) → Builder → Strategy
- [ ] Verify resize works in each scene
- [ ] Count lines in `game/app.py` — target: <300 lines (down from 759)
- [ ] Verify no remaining if/elif chains branching on GameState in app.py
- [ ] `grep -r "global WIDTH\|global HEIGHT" game/` returns zero results

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Full test suite passes: `pytest tests/`
- [ ] app.py line count < 300
- [ ] Zero if/elif chains on GameState
- [ ] Zero global WIDTH/HEIGHT
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State: "Project complete, ready for audit"
