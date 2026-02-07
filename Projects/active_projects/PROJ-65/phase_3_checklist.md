# Phase 3: Extract MenuScene & Scene Dispatch

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-65 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Create MenuScene, replace all if/elif chains with `self.active_scene` dispatch, implement scene_callback handler.

---

## Tasks

### Task 3.1: Create MenuScene [Medium]
**File:** `game/ui/screens/menu_scene.py` (new)
**Tests:** `pytest tests/unit/test_app_integration.py --tb=short`

- [ ] Create `MenuScene` class implementing IScene:
  - `__init__(self, width, height, ui_manager, button_callbacks)` — takes button config
  - `handle_event(self, event)` — delegates to `ui_manager.process_events()`, checks button presses
  - `update(self, dt)` — calls `ui_manager.update(dt)`
  - `draw(self, screen)` — fills background, calls `ui_manager.draw_ui(screen)`
  - `handle_resize(self, width, height)` — recreates buttons for new size
- [ ] Move `update_menu_buttons()` logic from Game into MenuScene
- [ ] Move `_draw_menu()` logic from Game into MenuScene.draw()
- [ ] Handle dialog windows (new game setup, load menu, race setup) — these are overlays on the menu
- [ ] Verify: MenuScene satisfies IScene protocol

**Notes:**

### Task 3.2: Replace if/elif Chains with active_scene Dispatch [Complex]
**File:** `game/app.py`
**Tests:** `pytest tests/ --tb=short` (full suite)

- [ ] Add `self.active_scene: IScene` attribute initialized to MenuScene in `__init__`
- [ ] Replace `_forward_event_to_scene()` (lines 515-554) with `self.active_scene.handle_event(event)`
- [ ] Replace resize dispatch in `_handle_resize()` (lines 556-583) with `self.active_scene.handle_resize(w, h)`
- [ ] Replace `_update_and_draw()` (lines 625-693) with `self.active_scene.update(frame_time)` + `self.active_scene.draw(self.screen)`
- [ ] Fold `_handle_click()` (lines 589-597) into scene handle_event
- [ ] Fold `_handle_scroll()` (lines 615-623) into scene handle_event
- [ ] Fold `_handle_keydown()` (line 585-587) into scene handle_event
- [ ] Add `_switch_scene(self, state, scene)` method that sets `self.state` and `self.active_scene`
- [ ] Update all `start_*()` methods to call `_switch_scene()` instead of just setting `self.state`
- [ ] Verify: zero if/elif chains branching on GameState in dispatch methods

**Notes:**

### Task 3.3: Implement scene_callback Handler [Medium]
**File:** `game/app.py`
**Tests:** `pytest tests/unit/test_app_integration.py --tb=short`

- [ ] Define `_handle_scene_action(self, action, **kwargs)` method handling:
  - `"return_to_menu"` → switch to MenuScene
  - `"start_battle"` → switch to BattleScreen with ships
  - `"open_builder"` → switch to DesignWorkshopScreen with context
  - `"return_to_setup"` → switch to BattleSetupScreen
  - `"return_to_test_lab"` → switch to TestLabScreen
  - `"start_test_battle"` → set up battle from test scenario
- [ ] Pass `self._handle_scene_action` as callback to scene constructors
- [ ] Remove all action flag polling from Game (lines 643-680, 711-724)
- [ ] Verify: no direct action flag checks remain in Game class

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] `self.active_scene` dispatch works for all scenes
- [ ] Zero if/elif chains on GameState in app.py dispatch methods
- [ ] Tests pass: `pytest tests/` (full suite)
- [ ] Manual test: app launches, scene transitions work
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase
