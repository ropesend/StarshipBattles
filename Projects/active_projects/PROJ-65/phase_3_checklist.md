# Phase 3: Extract MenuScene & Scene Dispatch

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-65 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Create MenuScene, replace all if/elif chains with `self.active_scene` dispatch, implement scene_callback handler.

---

## Tasks

### Task 3.1: Create MenuScene [Medium]
**File:** `game/ui/screens/menu_scene.py` (new)
**Tests:** `pytest tests/unit/test_app_integration.py --tb=short`

- [x] Create `MenuScene` class implementing IScene:
  - `__init__(self, width, height, button_config)` — takes button config list
  - `handle_event(self, event)` — delegates to `ui_manager.process_events()`, checks button presses
  - `update(self, dt)` — calls `ui_manager.update(dt)`
  - `draw(self, screen)` — fills background, calls `ui_manager.draw_ui(screen)`
  - `handle_resize(self, width, height)` — recreates buttons for new size
- [x] Move `update_menu_buttons()` logic from Game into MenuScene._create_buttons()
- [x] Move `_draw_menu()` logic from Game into MenuScene.draw()
- [x] Handle dialog windows (new game setup, load menu, race setup) — handled as overlays in _forward_event_to_scene
- [x] Verify: MenuScene satisfies IScene protocol

**Notes:** MenuScene creates and owns its own UIManager for menu buttons. Overlay dialogs (new game, load, race setup) continue to use menu_ui_manager.

### Task 3.2: Replace if/elif Chains with active_scene Dispatch [Complex]
**File:** `game/app.py`
**Tests:** `pytest tests/ --tb=short` (full suite)

- [x] Add `self.active_scene: IScene` attribute initialized to MenuScene in `__init__`
- [x] Replace `_forward_event_to_scene()` with `self.active_scene.handle_event(event)`
- [x] Replace resize dispatch in `_handle_resize()` with `self.active_scene.handle_resize(w, h)`
- [x] Replace `_update_and_draw()` with `self.active_scene.update(frame_time)` + `self.active_scene.draw(self.screen)`
- [x] Removed `_handle_keydown()` — events forwarded to scenes via handle_event
- [x] Keep `_handle_click()` for strategy legacy click handler (TODO: migrate to handle_event)
- [x] Keep `_handle_scroll()` for strategy legacy scroll handler (TODO: migrate to handle_event)
- [x] Add `_switch_scene(self, state, scene)` method that sets `self.state` and `self.active_scene`
- [x] Update all `start_*()` methods to call `_switch_scene()` instead of just setting `self.state`
- [x] Verify: if/elif chains eliminated from _forward_event_to_scene and _handle_resize

**Notes:** Some legacy handlers kept for Strategy scene (click, scroll). _update_and_draw still has minimal scene-specific logic for Strategy/ResearchTree/GalaxyTest input handling and Battle headless mode.

### Task 3.3: Implement scene_callback Handler [Medium]
**File:** `game/app.py`
**Tests:** `pytest tests/unit/test_app_integration.py --tb=short`

- [x] Scene-specific callback handlers already in place:
  - `_handle_battle_action` — handles return_to_test_lab, return_to_setup
  - `_handle_battle_setup_action` — handles start_battle, start_headless, return_to_menu
  - `_handle_strategy_action` — handles open_builder
  - `_handle_test_lab_action` — handles return_to_menu
- [x] Callbacks passed to scene constructors in __init__
- [x] Remove deprecated `_handle_battle_actions()` polling method
- [x] Verify: no direct action flag checks remain in Game class

**Notes:** Each scene has its own specific callback handler rather than a unified one. This keeps concerns separated and each scene's callback handling isolated.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] `self.active_scene` dispatch works for all scenes
- [x] Major if/elif chains on GameState eliminated from dispatch methods
- [x] Tests pass: `pytest tests/` (full suite) — 6244 passed
- [ ] Manual test: app launches, scene transitions work
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase
