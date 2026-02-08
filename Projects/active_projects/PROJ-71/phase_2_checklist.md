# Phase 2: Strategy Screen Integration

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-71 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Wire the InputMapper into the strategy layer, replacing all hardcoded key checks and adding tooltip hints.

---

## Tasks

### Task 2.1: Add GameState.KEYBINDINGS [Simple]
**File:** `game/core/constants.py` (line 37, after GALAXY_TEST = 9)
**Tests:** `pytest tests/ --testmon`

- [ ] Add `KEYBINDINGS = 10` to `GameState` IntEnum
- [ ] Verify: No import errors, no test regressions

**Notes:**

---

### Task 2.2: Create and inject InputMapper in app.py [Medium]
**File:** `game/app.py`
**Tests:** `pytest tests/ --testmon`

- [ ] Add import: `from game.core.input_mapper import InputMapper`
- [ ] In `Game.__init__()`, after `set_default_registries()` (~line 109):
  - `self.input_mapper = InputMapper()`
  - `self.input_mapper.load()`
- [ ] Pass `input_mapper=self.input_mapper` to `StrategyScreen()` constructor (lines 128, 232, 285, 333)
- [ ] Refactor `_handle_normal_events()` (line 474): replace hardcoded ALT+X and F9 checks with:
  - `action = self.input_mapper.resolve(event, contexts=["global"])`
  - `if action == InputAction.GLOBAL_EXIT: self.show_exit_dialog = True`
  - `if action == InputAction.GLOBAL_TOGGLE_PROFILER: ...`
- [ ] Add `start_keybindings(on_close)` method for PROJ-72 to call later:
  - Creates `KeybindingsScene` and switches to `GameState.KEYBINDINGS`
- [ ] Verify: Game launches without errors, ALT+X and F9 still work

**Notes:**

---

### Task 2.3: Wire InputMapper through StrategyScreen [Medium]
**File:** `game/ui/screens/strategy_screen.py`
**Tests:** `pytest tests/unit/ui/ --testmon`

- [ ] Add `input_mapper` parameter to `StrategyScreen.__init__()` (line 50), default `None`
- [ ] Store as `self.input_mapper = input_mapper`
- [ ] Pass to `StrategyInputHandler(self, input_mapper)` (line 114)
- [ ] Pass to `StrategyUI(self, screen_width, screen_height, input_mapper)` (line 89)
- [ ] Verify: Strategy screen still creates and functions

**Notes:**

---

### Task 2.4: Refactor StrategyInputHandler to use InputMapper [Medium]
**File:** `game/ui/screens/strategy_input_handler.py`
**Tests:** `pytest tests/unit/ui/ --testmon`

- [ ] Add `input_mapper` parameter to `__init__()` (line 18)
- [ ] Add import: `from game.core.input_actions import InputAction`
- [ ] Refactor `_handle_keydown()` (lines 77-124):
  - Build contexts list: `["strategy", "global"]` + `"fleet"` if `self.scene.selected_fleet`
  - `action = self._mapper.resolve(event, contexts)`
  - Replace each `elif event.key == pygame.K_m:` block with `if action == InputAction.FLEET_MOVE:`
  - Map all actions:
    - `FLEET_MOVE` -> enter MOVE mode
    - `FLEET_JOIN` -> enter JOIN mode
    - `FLEET_COLONIZE` -> enter COLONIZE_TARGET mode
    - `FLEET_TRANSFER` -> open transfer dialog
    - `FLEET_CANCEL_MODE` -> return to SELECT mode
    - `STRATEGY_ZOOM_GALAXY` -> zoom to galaxy
    - `STRATEGY_ZOOM_SYSTEM` -> zoom to system
    - `GLOBAL_SCREENSHOT_FULL` -> take full screenshot
    - `GLOBAL_SCREENSHOT_VIEWPORT` -> take viewport screenshot
    - `STRATEGY_NEXT_TURN` -> advance turn
    - `STRATEGY_OPEN_PLANETS` -> open planet list
    - `STRATEGY_OPEN_DESIGN` -> open design workshop
    - `STRATEGY_OPEN_BUILD_QUEUES` -> open build queue list
    - `STRATEGY_SAVE_GAME` -> save game
    - `STRATEGY_PREV_COLONY` / `STRATEGY_NEXT_COLONY` -> cycle colony
    - `STRATEGY_PREV_FLEET` / `STRATEGY_NEXT_FLEET` -> cycle fleet
    - `FLEET_OPEN_ORDERS` -> open orders window
    - `FLEET_OPEN_FLEET_REPORT` -> open fleet report
    - `FLEET_OPEN_BUILD` -> open fleet build queue
- [ ] Fallback: if `input_mapper` is None, preserve current hardcoded behavior (for backward compat during transition)
- [ ] Verify: All strategy hotkeys still work (M, J, C, T, ESC, Shift+G, Shift+S, F12, F11)

**Notes:**

---

### Task 2.5: Add hotkey-triggered button actions [Medium]
**File:** `game/ui/screens/strategy_input_handler.py`
**Tests:** Manual test in-game

- [ ] In `_handle_keydown()`, add dispatch for button-only actions that previously had no hotkey:
  - `STRATEGY_NEXT_TURN` -> `self.scene.advance_turn()`
  - `STRATEGY_OPEN_PLANETS` -> `self.scene.ui.open_planet_list()`
  - `STRATEGY_OPEN_EMPIRE` -> (not implemented yet, skip)
  - `STRATEGY_OPEN_RESEARCH` -> (not implemented yet, skip)
  - `STRATEGY_OPEN_DESIGN` -> `self.scene.on_design_click()`
  - `STRATEGY_OPEN_BUILD_QUEUES` -> `self.scene.ui.open_build_queue_list()`
  - `STRATEGY_SAVE_GAME` -> `self.scene.on_save_game_click()`
  - `STRATEGY_PREV_COLONY` / `NEXT` -> `self.scene.cycle_selection('colony', -1/+1)`
  - `STRATEGY_PREV_FLEET` / `NEXT` -> `self.scene.cycle_selection('fleet', -1/+1)`
  - `FLEET_OPEN_ORDERS` -> `self.scene.ui.open_orders_window(fleet)`
  - `FLEET_OPEN_FLEET_REPORT` -> `self.scene.ui.open_fleet_report_window(fleet)`
  - `FLEET_OPEN_BUILD` -> `self.scene.on_fleet_build_click()`
- [ ] Guard fleet-specific actions with `if self.scene.selected_fleet:` check
- [ ] Verify: Press P to open Planets, Space/Enter to end turn, etc.

**Notes:**

---

### Task 2.6: Add tooltip enrichment to StrategyUI [Medium]
**File:** `game/ui/screens/strategy_ui.py`
**Tests:** Manual test - hover over buttons to see tooltips

- [ ] Add `input_mapper` parameter to `StrategyUI.__init__()` (line 34), store as `self._mapper`
- [ ] Add `_apply_hotkey_tooltips()` method:
  - Map buttons to InputAction values
  - For each button, get display text via `mapper.get_display_text(action)`
  - If non-empty, call `btn.set_tooltip(f"Hotkey: {hint}")` (or equivalent pygame_gui tooltip API)
- [ ] Call `_apply_hotkey_tooltips()` at end of `__init__()` after all buttons are created
- [ ] Map these buttons:
  - `btn_next_turn` -> `STRATEGY_NEXT_TURN`
  - `btn_planets` -> `STRATEGY_OPEN_PLANETS`
  - `btn_empire` -> `STRATEGY_OPEN_EMPIRE`
  - `btn_research` -> `STRATEGY_OPEN_RESEARCH`
  - `btn_design` -> `STRATEGY_OPEN_DESIGN`
  - `btn_build_queues` -> `STRATEGY_OPEN_BUILD_QUEUES`
  - `btn_save_game` -> `STRATEGY_SAVE_GAME`
  - `btn_prev_colony` -> `STRATEGY_PREV_COLONY`
  - `btn_next_colony` -> `STRATEGY_NEXT_COLONY`
  - `btn_prev_fleet` -> `STRATEGY_PREV_FLEET`
  - `btn_next_fleet` -> `STRATEGY_NEXT_FLEET`
  - `btn_colonize` -> `FLEET_COLONIZE`
  - `btn_orders` -> `FLEET_OPEN_ORDERS`
  - `btn_fleet_report` -> `FLEET_OPEN_FLEET_REPORT`
  - `btn_build_yard` -> (new action or reuse strategy.open_build_queues)
  - `btn_build_fleet` -> `FLEET_OPEN_BUILD`
- [ ] Verify: Hover over "End Turn" shows tooltip "Hotkey: Space" (or whatever default is set)

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] All hotkeys work as before (M, J, C, T, ESC, Shift+G, Shift+S, F12, F11)
- [ ] New button hotkeys work (P for Planets, D for Design, etc.)
- [ ] Tooltips display on button hover
- [ ] Full test suite passes (`pytest tests/ -n 12`)
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase
