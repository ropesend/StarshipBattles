# Phase 4: StrategyScreen Minimal Extraction

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-173 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Minimal extraction from StrategyScreen (823 lines) — move BuildQueueManager (188 lines) and GameStateManager (109 lines) to separate files. StrategyScreen is already well-decomposed with 8 delegates; this phase brings it under 600 lines. Conservative approach — StrategyScreen is NOT a god class, just oversized.

**Note:** This phase is OPTIONAL. If the team decides StrategyScreen is acceptable at 823 lines (already 8 delegates extracted), this phase can be skipped. The swarm agent recommended ACCEPT.

---

## Tasks

### Task 4.1: Extract StrategyBuildQueueManager [Medium]
**File:** `game/ui/screens/strategy_screen.py` (read)
**New File:** `game/ui/screens/strategy_build_queue_manager.py`
**Tests:** `pytest tests/unit/ui/screens/test_strategy_screen.py -v`

- [ ] Read `strategy_screen.py` fully, identify build queue methods:
  - [ ] `on_build_yard_click()` (lines 413-458, ~46L) — opens BuildQueueScreen for planets
  - [ ] `_on_build_queue_close()` (lines 459-492, ~34L) — closure handling + fleet BUILD order
  - [ ] `_handle_fleet_build_queue_close(fleet)` (lines 493-514, ~22L) — auto-issue BUILD orders
  - [ ] `on_navigate_to_hex_build(hex_coord, source)` (lines 515-568, ~54L) — navigate to hex build
  - [ ] `on_fleet_build_click()` (lines 569-613, ~45L) — opens BuildQueueScreen for fleets
- [ ] Create `game/ui/screens/strategy_build_queue_manager.py`:
  - [ ] `StrategyBuildQueueManager` class
  - [ ] Constructor: `__init__(self, screen)` — receives StrategyScreen reference
  - [ ] Accesses: `screen.session`, `screen._facade`, `screen.ui`, `screen.selected_object`, `screen.empire_assets`, `screen.input_mapper`, `screen.current_empire`
  - [ ] Move all 5 build queue methods
  - [ ] Adjust `self.` references to `self._screen.`
  - [ ] Does NOT import StrategyScreen at runtime (TYPE_CHECKING only)
- [ ] Update `strategy_screen.py`:
  - [ ] In `__init__`: `self._build_queue = StrategyBuildQueueManager(self)`
  - [ ] `on_build_yard_click()` becomes: `self._build_queue.on_build_yard_click()`
  - [ ] `on_fleet_build_click()` becomes: `self._build_queue.on_fleet_build_click()`
  - [ ] `on_navigate_to_hex_build()` becomes: `self._build_queue.on_navigate_to_hex_build(...)`
  - [ ] Remove all moved methods
- [ ] Run tests: `pytest tests/unit/ui/screens/test_strategy_screen.py -v`

**Notes:**

---

### Task 4.2: Extract StrategyGameStateManager [Medium]
**File:** `game/ui/screens/strategy_screen.py` (read)
**New File:** `game/ui/screens/strategy_game_state_manager.py`
**Tests:** `pytest tests/unit/ui/screens/test_strategy_screen.py tests/integration/strategy/test_strategy_scene.py -v`

- [ ] Identify turn processing methods:
  - [ ] `advance_turn()` (lines 271-289, ~19L) — player turn advancement cycle
  - [ ] `_process_full_turn()` (lines 290-334, ~45L) — full turn processing for all empires
  - [ ] `_show_scuttle_notifications()` (lines 335-371, ~37L) — maintenance failure notifications
  - [ ] `_update_player_label()` (lines 372-376, ~5L) — update UI player indicator
- [ ] Create `game/ui/screens/strategy_game_state_manager.py`:
  - [ ] `StrategyGameStateManager` class
  - [ ] Constructor: `__init__(self, screen)` — receives StrategyScreen reference
  - [ ] Accesses: `screen.session`, `screen._facade`, `screen.empires`, `screen.ui`, `screen.current_empire`, `screen._renderer`
  - [ ] Move all 4 turn processing methods
  - [ ] Adjust `self.` references to `self._screen.`
  - [ ] Does NOT import StrategyScreen at runtime (TYPE_CHECKING only)
- [ ] Update `strategy_screen.py`:
  - [ ] In `__init__`: `self._game_state = StrategyGameStateManager(self)`
  - [ ] `advance_turn()` becomes: `self._game_state.advance_turn()`
  - [ ] Remove all moved methods
- [ ] Run tests: `pytest tests/unit/ui/screens/test_strategy_screen.py tests/integration/strategy/test_strategy_scene.py -v`

**Notes:**

---

### Task 4.3: Verify StrategyScreen coordinator [Simple]
**File:** `game/ui/screens/strategy_screen.py`
**Tests:** `pytest tests/unit/ui/screens/test_strategy_screen.py -v`

- [ ] Verify StrategyScreen is now:
  - [ ] `__init__()` — creates all delegates (now 10: existing 8 + BuildQueueManager + GameStateManager)
  - [ ] Properties — galaxy, empires, player_empire, etc.
  - [ ] Lifecycle — `update()`, `draw()`, `handle_resize()`
  - [ ] Event routing — `handle_event()`, `handle_click()`, `update_input()` (delegates)
  - [ ] Navigation — `center_camera_on()`, `cycle_selection()` (delegates)
  - [ ] Colonization — 3 thin methods delegating to ColonizationSystem
  - [ ] Selection — `on_ui_selection()` (stays, coordinates multiple delegates)
  - [ ] Menu — `on_design_click()`, `on_menu_option()`, save/load (stays, thin)
  - [ ] Utilities — pathfinding wrappers, asset loading (stays)
- [ ] Verify: StrategyScreen public API unchanged (IScene protocol: draw, update, handle_resize, handle_event)
- [ ] Verify: All callers unaffected (app.py, tests)
- [ ] Run all strategy tests: `pytest tests/unit/ui/screens/test_strategy_screen.py tests/integration/strategy/test_strategy_scene.py tests/integration/ui/test_strategy_buttons.py -v`
- [ ] Verify: StrategyScreen < 600 lines

**Notes:**

---

### Task 4.4: Phase 4 verification [Simple]
**Tests:** `pytest tests/ -n 12`

- [ ] Run full test suite: `pytest tests/ -n 12`
- [ ] Verify: 12,023+ tests pass, 0 failures
- [ ] Verify line counts:
  - [ ] `strategy_screen.py` < 600 lines
  - [ ] `strategy_build_queue_manager.py` exists (~188 lines)
  - [ ] `strategy_game_state_manager.py` exists (~109 lines)
- [ ] Verify: StrategyScreen public API unchanged
- [ ] Verify: New managers do NOT import StrategyScreen at runtime

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to "Project Complete"
