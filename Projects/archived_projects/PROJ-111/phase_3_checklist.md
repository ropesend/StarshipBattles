# Phase 3: Battle Layer (Screens & Panels)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-111 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Add unit tests for battle-related screens and panels: BattleScreen (extending existing), BattlePanels (extending existing), BattleSetupScreen (new), and MenuScene (new).
**Findings covered:** TCG-UI1-001, TCG-UI1-008, TCG-UI1-009, TCG-UI1-010
**Estimated tests:** ~100-130

---

## Task 3.1: BattleScreen Extended Coverage [Complex]
**Finding:** TCG-UI1-001
**Source:** `game/ui/screens/battle_screen.py` (672 lines, 30+ methods)
**Tests:** `tests/unit/ui/test_battle_screen.py` + `tests/unit/ui/test_battle_screen_extended.py` (existing, extend)
**Mocks:** Patch BattleUI; use fresh_registries for real Ship objects

Existing tests (7) cover: init, battle_over, tick update, projectile registration/cleanup, ui_service. Missing:

**Simulation lifecycle:**
- [x] Test `start()` with empty ship lists -> still initializes (0 ships)
- [x] Test `start()` with headless=True vs headless=False mode differences
- [x] Test `start()` assigns correct team_id to team1 (0) and team2 (1) ships
- [x] Test `start()` creates BattleService and BattleUIService
- [x] Test pause/unpause via `sim_paused` toggle
- [x] Test speed multiplier changes (0.5x, 2x, 4x) affect tick accumulation

**Win/loss detection:**
- [x] Test `get_winner()` returns 1 when team 0 ships all dead
- [x] Test `get_winner()` returns 0 when team 1 ships all dead
- [x] Test `is_battle_over()` with both teams having dead ships but not all dead
- [x] Test draw condition (all ships dead simultaneously)

**Event handling:**
- [x] Test `handle_event()` with keyboard events (mock event routing)
- [x] Test `handle_event()` with mouse scroll (zoom)
- [x] Test `handle_event()` forwards to BattleUI

**BattleController integration:**
- [x] Test `start_from_controller()` if method exists (PROJ-104 unified battle mode)
- [x] Test `start()` with `BattleConfig` parameter

**Tick mechanics:**
- [x] Test accumulator doesn't exceed max cap (prevents spiral-of-death)
- [x] Test multiple ticks per frame with large dt value

- [x] Verify: `pytest tests/unit/ui/test_battle_screen.py tests/unit/ui/test_battle_screen_extended.py -v`

**Notes:** Use existing `setup_scene_and_ships` fixture pattern. Patch BattleUI to avoid UI overhead.

---

## Task 3.2: Battle Panels Extended Coverage [Medium]
**Finding:** TCG-UI1-008
**Source:** `game/ui/panels/battle_panels.py` (566 lines)
**Tests:** `tests/unit/ui/test_battle_panels.py` (existing, extend)
**Mocks:** Mock pygame via sys.modules; MockRect helper; mock ship DTOs

Existing tests (8+) cover: expansion toggle, scroll offset, seeker state, coordinate logic, DTO integration. Missing:

**ShipStatsPanel:**
- [x] Test `_get_ships()` with ui_service available returns DTO list
- [x] Test `_get_ships()` with ui_service None falls back to scene.ships
- [x] Test `_get_ships()` with ui_service.get_ships() raising exception falls back
- [x] Test multiple team display (3+ teams if supported)
- [x] Test empty ship list (no ships in battle)
- [x] Test expanded ship details rendering (component list, weapon stats)

**SeekerMonitorPanel:**
- [x] Test `add_seeker()` with multiple seekers of different statuses
- [x] Test `clear_inactive()` removes only non-active seekers
- [x] Test scroll state with many seekers (overflow handling)
- [x] Test seeker expansion shows velocity/damage details

**BattleControlPanel:**
- [x] Test `handle_click()` with no rects set (draw not called yet) -> returns False
- [x] Test speed control buttons if present
- [x] Test pause toggle button if present

- [x] Verify: `pytest tests/unit/ui/test_battle_panels.py -v`

---

## Task 3.3: MenuScene Tests [Simple]
**Finding:** TCG-UI1-009
**Source:** `game/ui/screens/menu_scene.py` (105 lines)
**Tests:** `tests/unit/ui/screens/test_menu_scene.py` (NEW)
**Mocks:** Mock pygame_gui.UIManager and UIButton

- [x] Create `tests/unit/ui/screens/test_menu_scene.py`
- [x] Test initialization creates correct number of buttons from config
- [x] Test button_config with 3 buttons (New Game, Load, Settings)
- [x] Test button click dispatches to correct callback
- [x] Test `handle_event()` passes events to UIManager
- [x] Test `update()` calls UIManager.update()
- [x] Test `draw()` fills background and calls UIManager.draw_ui()
- [x] Test empty button_config (0 buttons) initializes without error
- [x] Test button_config with single button
- [x] Verify: `pytest tests/unit/ui/screens/test_menu_scene.py -v`

**Notes:** MenuScene uses `pygame_gui.UIManager` and `UIButton`. Use bypass-init or create minimal UIManager with headless display.

---

## Task 3.4: BattleSetupScreen Tests [Medium]
**Finding:** TCG-UI1-010
**Source:** `game/ui/screens/setup_screen.py` (382 lines)
**Tests:** `tests/unit/ui/screens/test_setup_screen.py` (NEW)
**Mocks:** Bypass-init pattern; mock ShipFactory, StrategyManager; mock scene_callback

- [x] Create `tests/unit/ui/screens/test_setup_screen.py`
- [x] Test initialization sets up empty team lists
- [x] Test `_add_ship_to_team()` adds ship to correct team
- [x] Test `_remove_ship_from_team()` removes ship
- [x] Test `_clear_team()` empties team list
- [x] Test AI strategy selection stores strategy name per team
- [x] Test scene_callback invoked with "start_battle" action
- [x] Test scene_callback invoked with "start_headless" action
- [x] Test scene_callback invoked with "return_to_menu" action
- [x] Test ship loading from JSON file (mock `load_json_required`)
- [x] Test save/load battle setup (mock file I/O via `setup_data_io`)
- [x] Test formation application to team ships
- [x] Verify: `pytest tests/unit/ui/screens/test_setup_screen.py -v`

**Notes:** Uses tkinter for file dialogs. Tests must avoid triggering tkinter by mocking `filedialog` calls. Use bypass-init pattern since `__init__` creates pygame surfaces.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] All new tests passing: `pytest tests/unit/ui/test_battle_screen.py tests/unit/ui/test_battle_screen_extended.py tests/unit/ui/test_battle_panels.py tests/unit/ui/screens/test_menu_scene.py tests/unit/ui/screens/test_setup_screen.py -v`
- [x] No regressions: `pytest tests/ -n 12` (9150 passed)
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase
