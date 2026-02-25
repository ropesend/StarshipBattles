# Phase 4: StrategyScreen Minimal Extraction

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-173 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Minimal extraction from StrategyScreen (823 lines) — move BuildQueueManager (188 lines) and GameStateManager (109 lines) to separate files. StrategyScreen is already well-decomposed with 8 delegates; this phase brings it under 600 lines. Conservative approach — StrategyScreen is NOT a god class, just oversized.

**Note:** This phase is OPTIONAL. If the team decides StrategyScreen is acceptable at 823 lines (already 8 delegates extracted), this phase can be skipped. The swarm agent recommended ACCEPT.

---

## Tasks

### Task 4.1: Extract StrategyBuildQueueManager [Medium]
**File:** `game/ui/screens/strategy_screen.py` (read)
**New File:** `game/ui/screens/strategy_build_queue_manager.py`
**Tests:** `pytest tests/unit/ui/screens/test_strategy_screen.py -v`

- [x] Read `strategy_screen.py` fully, identify build queue methods:
  - [x] `on_build_yard_click()` (lines 413-458, ~46L) — opens BuildQueueScreen for planets
  - [x] `_on_build_queue_close()` (lines 459-492, ~34L) — closure handling + fleet BUILD order
  - [x] `_handle_fleet_build_queue_close(fleet)` (lines 493-514, ~22L) — auto-issue BUILD orders
  - [x] `on_navigate_to_hex_build(hex_coord, source)` (lines 515-568, ~54L) — navigate to hex build
  - [x] `on_fleet_build_click()` (lines 569-613, ~45L) — opens BuildQueueScreen for fleets
- [x] Create `game/ui/screens/strategy_build_queue_manager.py`:
  - [x] `StrategyBuildQueueManager` class
  - [x] Constructor: `__init__(self, screen)` — receives StrategyScreen reference
  - [x] Accesses: `screen.session`, `screen._facade`, `screen.ui`, `screen.selected_object`, `screen.empire_assets`, `screen.input_mapper`, `screen.current_empire`
  - [x] Move all 5 build queue methods
  - [x] Adjust `self.` references to `self._screen.`
  - [x] Does NOT import StrategyScreen at runtime (TYPE_CHECKING only)
- [x] Update `strategy_screen.py`:
  - [x] In `__init__`: `self._build_queue = StrategyBuildQueueManager(self)`
  - [x] `on_build_yard_click()` becomes: `self._build_queue.on_build_yard_click()`
  - [x] `on_fleet_build_click()` becomes: `self._build_queue.on_fleet_build_click()`
  - [x] `on_navigate_to_hex_build()` becomes: `self._build_queue.on_navigate_to_hex_build(...)`
  - [x] Remove all moved methods
- [x] Run tests: `pytest tests/unit/ui/screens/test_strategy_screen.py -v`

**Notes:**

---

### Task 4.2: Extract StrategyGameStateManager [Medium]
**File:** `game/ui/screens/strategy_screen.py` (read)
**New File:** `game/ui/screens/strategy_game_state_manager.py`
**Tests:** `pytest tests/unit/ui/screens/test_strategy_screen.py tests/integration/strategy/test_strategy_scene.py -v`

- [x] Identify turn processing methods:
  - [x] `advance_turn()` (lines 271-289, ~19L) — player turn advancement cycle
  - [x] `_process_full_turn()` (lines 290-334, ~45L) — full turn processing for all empires
  - [x] `_show_scuttle_notifications()` (lines 335-371, ~37L) — maintenance failure notifications
  - [x] `_update_player_label()` (lines 372-376, ~5L) — update UI player indicator
- [x] Create `game/ui/screens/strategy_game_state_manager.py`:
  - [x] `StrategyGameStateManager` class
  - [x] Constructor: `__init__(self, screen)` — receives StrategyScreen reference
  - [x] Accesses: `screen.session`, `screen._facade`, `screen.empires`, `screen.ui`, `screen.current_empire`, `screen._renderer`
  - [x] Move all 4 turn processing methods
  - [x] Adjust `self.` references to `self._screen.`
  - [x] Does NOT import StrategyScreen at runtime (TYPE_CHECKING only)
- [x] Update `strategy_screen.py`:
  - [x] In `__init__`: `self._game_state = StrategyGameStateManager(self)`
  - [x] `advance_turn()` becomes: `self._game_state.advance_turn()`
  - [x] Remove all moved methods
- [x] Run tests: `pytest tests/unit/ui/screens/test_strategy_screen.py tests/integration/strategy/test_strategy_scene.py -v`

**Notes:**

---

### Task 4.3: Verify StrategyScreen coordinator [Simple]
**File:** `game/ui/screens/strategy_screen.py`
**Tests:** `pytest tests/unit/ui/screens/test_strategy_screen.py -v`

- [x] Verify StrategyScreen is now:
  - [x] `__init__()` — creates all delegates (now 10: existing 8 + BuildQueueManager + GameStateManager)
  - [x] Properties — galaxy, empires, player_empire, etc.
  - [x] Lifecycle — `update()`, `draw()`, `handle_resize()`
  - [x] Event routing — `handle_event()`, `handle_click()`, `update_input()` (delegates)
  - [x] Navigation — `center_camera_on()`, `cycle_selection()` (delegates)
  - [x] Colonization — 3 thin methods delegating to ColonizationSystem
  - [x] Selection — `on_ui_selection()` (stays, coordinates multiple delegates)
  - [x] Menu — `on_design_click()`, `on_menu_option()`, save/load (stays, thin)
  - [x] Utilities — pathfinding wrappers, asset loading (stays)
- [x] Verify: StrategyScreen public API unchanged (IScene protocol: draw, update, handle_resize, handle_event)
- [x] Verify: All callers unaffected (app.py, tests)
- [x] Run all strategy tests: `pytest tests/unit/ui/screens/test_strategy_screen.py tests/integration/strategy/test_strategy_scene.py tests/integration/ui/test_strategy_buttons.py -v`
- [x] Verify: StrategyScreen < 600 lines (538 lines)

**Notes:**

---

### Task 4.4: Phase 4 verification [Simple]
**Tests:** `pytest tests/ -n 12`

- [x] Run full test suite: `pytest tests/ -n 12`
- [x] Verify: 12,338 tests pass, 1 skipped, 0 failures
- [x] Verify line counts:
  - [x] `strategy_screen.py` = 538 lines (< 600)
  - [x] `strategy_build_queue_manager.py` = 242 lines
  - [x] `strategy_game_state_manager.py` = 144 lines
- [x] Verify: StrategyScreen public API unchanged
- [x] Verify: New managers do NOT import StrategyScreen at runtime (TYPE_CHECKING only)

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to "Project Complete"
