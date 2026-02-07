# Phase 2: Standardize Scene Interfaces

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-65 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Make all 8 scene classes conform to the IScene protocol (handle_event, update(dt), draw, handle_resize).

---

## Tasks

### Task 2.1: Standardize BattleSetupScreen [Medium]
**File:** `game/ui/screens/setup_screen.py`
**Tests:** `pytest tests/ -k "setup" --tb=short`

- [ ] Add `handle_event(self, event)` method — move per-event logic from current `update(events, screen_size)`
- [ ] Change `update(self, events, screen_size)` → `update(self, dt)` — remove event processing (now in handle_event)
- [ ] Store screen_size internally via `handle_resize(self, width, height)` instead of per-call
- [ ] Add `handle_resize(self, width, height)` method storing `self.screen_width, self.screen_height`
- [ ] Update app.py call site (line 542): `self.battle_setup.update([event], self.screen.get_size())` → `self.battle_setup.handle_event(event)`
- [ ] Update app.py call site (line 709): `_update_battle_setup` calls `self.battle_setup.update(frame_time)`
- [ ] Replace action flag polling with callback: add `scene_callback` param to constructor, call it instead of setting `action_start_battle`, `action_return_to_menu`, etc.
- [ ] Verify: BattleSetupScreen satisfies IScene protocol

**Notes:**

### Task 2.2: Standardize BattleScreen — Internalize Coordinator [Complex]
**File:** `game/ui/screens/battle_screen.py`, `game/battle_coordinator.py`
**Tests:** `pytest tests/unit/ui/test_battle_screen.py tests/unit/ui/test_battle_screen_extended.py --tb=short`

- [ ] Move `_battle_accumulator` from Game into `BattleScreen.__init__` as `self._accumulator`
- [ ] Move `update_battle_headless()` logic from `battle_coordinator.py` into `BattleScreen._update_headless()`
- [ ] Move `update_battle_visual()` logic from `battle_coordinator.py` into `BattleScreen._update_visual(dt)`
- [ ] Move `update_tick_rate()` logic into BattleScreen
- [ ] Move `draw_battle_hud()` into `BattleScreen.draw()` — pass font as constructor arg or use stored font
- [ ] Change `update(self, events)` → `update(self, dt)` — move event-related visual updates
- [ ] Add `handle_event(self, event)` method for per-event input handling
- [ ] Move BattleInputHandler keyboard logic into BattleScreen.handle_event() (speed controls, overlay toggle, pause)
- [ ] Replace action flags (`action_return_to_setup`, `action_return_to_test_lab`) with `scene_callback`
- [ ] Delete `game/battle_coordinator.py` after all logic moved
- [ ] Delete or gut `game/ui/screens/battle_input_handler.py`
- [ ] Verify: BattleScreen satisfies IScene protocol

**Notes:**

### Task 2.3: Standardize StrategyScreen [Medium]
**File:** `game/ui/screens/strategy_screen.py`
**Tests:** `pytest tests/ -k "strategy" --tb=short`

- [ ] Merge `update_input(dt, events)` into `handle_event(event)` — events processed per-event
- [ ] Replace `action_open_design` flag + `workshop_context_data` with `scene_callback("open_builder", context=...)`
- [ ] Keep `handle_click(mx, my, button)` and `handle_scroll(y, h)` — called from handle_event internally
- [ ] Verify: `handle_event`, `update(dt)`, `draw(screen)`, `handle_resize(w,h)` all match IScene

**Notes:**

### Task 2.4: Standardize TestLabScreen [Medium]
**File:** `game/ui/screens/test_lab_screen.py`
**Tests:** `pytest tests/unit/test_lab/ --tb=short`

- [ ] Replace `__init__(self, game)` with `__init__(self, width, height, scene_callback)`
- [ ] Replace `self.game.screen.get_size()` calls with stored `self.screen_width, self.screen_height`
- [ ] Replace `self.game.battle_scene` access with `scene_callback("start_test_battle", scenario=scenario)`
- [ ] Replace `self.game.state = GameState.BATTLE` with `scene_callback("start_battle", ...)`
- [ ] Rename `handle_input(self, events)` → add `handle_event(self, event)` (single event)
- [ ] Change `update(self)` → `update(self, dt)` (accept dt even if unused)
- [ ] Add `handle_resize(self, width, height)` — call `_create_ui()` inside it
- [ ] Update app.py construction (line 134) to pass `(self.width, self.height, callback)`
- [ ] Verify: TestLabScreen satisfies IScene protocol

**Notes:**

### Task 2.5: Standardize DesignWorkshopScreen [Simple]
**File:** `game/ui/screens/workshop_screen.py`
**Tests:** `pytest tests/unit/builder/ --tb=short`

- [ ] Add `handle_resize(self, width, height)` method if missing
- [ ] Verify `handle_event(event)`, `update(dt)`, `draw(screen)` signatures match IScene
- [ ] Remove `hasattr(self.builder_scene, 'handle_resize')` guard in app.py (line 570)

**Notes:**

### Task 2.6: Standardize ResearchTreeScene & GalaxyTestScreen [Simple]
**Files:** `game/research/ui/research_scene.py`, `game/ui/screens/galaxy_test_screen.py`
**Tests:** `pytest tests/ -k "research or galaxy" --tb=short`

- [ ] Both have `handle_event`, `update(dt)`, `draw(screen)`, `handle_resize(w,h)` — verify match IScene
- [ ] Merge `handle_input(dt, events)` into `update(dt)` (camera/input logic) — events come via handle_event individually
- [ ] Remove `hasattr` guards in app.py (lines 550-554, 579-583, 685-693)
- [ ] Verify both satisfy IScene protocol

**Notes:**

### Task 2.7: Verify FormationEditorScreen [Simple]
**File:** `Tools/formation_editor.py`
**Tests:** `pytest tests/ -k "formation" --tb=short`

- [ ] Verify `handle_event(event)`, `update(dt)`, `draw(screen)`, `handle_resize(w,h)` all match IScene
- [ ] Already standard — minimal/no changes expected

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] All 8 scene classes satisfy IScene protocol
- [ ] Tests pass: `pytest tests/ --testmon`
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase
