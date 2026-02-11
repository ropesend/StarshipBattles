# Phase 4: TestLabScreen Test Executor [Complex]

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-86 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Extract test execution methods from TestLabScreen into a new `test_executor.py` module. This is the most complex extraction (~375 lines) due to render callbacks for progress overlays and tight coupling to `game.battle_scene`.

**File:** `game/ui/screens/test_lab/screen.py`
**New File:** `game/ui/screens/test_lab/test_executor.py`
**Tests:** `pytest tests/unit/ui/test_lab_scene/ tests/unit/test_lab/ -x`

---

## Tasks

### Task 4.1: Design render callback interface [Simple]
**File:** N/A (design task)

- [ ] Define the render callback signature: `render_progress(title: str, subtitle: str, detail: str) -> None`
  - `title`: e.g., "Running Test..." or "Running test 3/15"
  - `subtitle`: e.g., test metadata name
  - `detail`: e.g., "Max ticks: 500" or "ID: BEAM360-001"
- [ ] Define the screen draw callback: `draw_current(screen) -> None` -- draws current TestLabScreen state before overlay
- [ ] Decide on additional callbacks needed:
  - `get_battle_engine() -> BattleEngine` -- access to game.battle_scene.engine
  - `ensure_engine_exists() -> None` -- ensures battle engine is created
  - `switch_to_battle(scenario) -> None` -- for visual run mode (sets game state)
  - `get_effective_seed(default_seed) -> int` -- seed from controller.ui_state

**Notes:** The executor must not import or reference `self.game` directly. All game access flows through callbacks/interfaces.

---

### Task 4.2: Create test_executor.py [Complex]
**File:** `game/ui/screens/test_lab/test_executor.py` (new)

- [ ] Create new file `game/ui/screens/test_lab/test_executor.py`
- [ ] Create `class TestLabExecutor` with constructor accepting:
  - `registry` - TestRegistry instance
  - `test_history` - TestHistory instance
  - `controller` - TestLabUIController (for seed mode access)
  - `render_progress` - callback `(title, subtitle, detail) -> None`
  - `draw_and_flip` - callback `() -> None` that draws current screen state and flips display
  - `get_engine` - callback `() -> BattleEngine`
  - `ensure_engine` - callback `() -> None`
  - `switch_to_battle` - callback `(scenario) -> None`
  - `output_log` - list reference for appending log messages
- [ ] Move `_on_run` logic (lines 966-1042) into `TestLabExecutor.run_visual(self, test_id)` method
  - Replace `self.game.battle_scene.*` with `self.get_engine()`, `self.ensure_engine()`, `self.switch_to_battle(scenario)`
- [ ] Move `_on_run_headless` logic (lines 1044-1173) into `TestLabExecutor.run_headless(self, test_id)` method
  - Replace overlay rendering with `self.render_progress(title, subtitle, detail)` + `self.draw_and_flip()`
  - Replace `self.game.battle_scene.engine` with `self.get_engine()`
- [ ] Move `_on_run_all_tests` logic (lines 1175-1188) into `TestLabExecutor.run_all(self, filtered_scenarios)` method
  - Store batch state: `self.batch_tests`, `self.batch_total`, `self.batch_current_index`, `self.batch_running`
- [ ] Move `_run_next_batch_test` logic (lines 1190-1299) into `TestLabExecutor.run_next_batch(self)` method
  - Replace overlay rendering with `self.render_progress(title, subtitle, detail)` + `self.draw_and_flip()`
- [ ] Move `_continue_batch_test` logic (lines 1301-1304) into `TestLabExecutor.continue_batch(self)` method
- [ ] Extract shared headless execution logic from `run_headless` and `run_next_batch` into private `_execute_headless(self, test_id, scenario, engine, seed)` helper to reduce duplication
- [ ] Ensure imports: `time`, `pygame`, `test_framework.runner.TestRunner`, `test_framework.battle_state_capture.BattleStateCapture`, `simulation_tests.logging_config.get_logger`
- [ ] Add docstrings to module and class

**Notes:** The `_on_run` (visual) method switches game state to BATTLE and does NOT run the simulation loop -- it delegates to the battle scene. The headless methods run the simulation inline. Keep this behavioral distinction clear.

---

### Task 4.3: Update screen.py to delegate to test_executor [Medium]
**File:** `game/ui/screens/test_lab/screen.py`

- [ ] Add import: `from .test_executor import TestLabExecutor`
- [ ] Implement `_render_progress` helper on TestLabScreen:
  ```python
  def _render_progress(self, title, subtitle, detail):
      overlay = pygame.Surface((600, 200))
      overlay.fill((40, 40, 45))
      pygame.draw.rect(overlay, (100, 100, 120), overlay.get_rect(), 3)
      title_text = self.header_font.render(title, True, (255, 255, 255))
      sub_text = self.body_font.render(subtitle, True, (200, 200, 200))
      detail_text = self.small_font.render(detail, True, (150, 150, 150))
      overlay.blit(title_text, (300 - title_text.get_width()//2, 50))
      overlay.blit(sub_text, (300 - sub_text.get_width()//2, 90))
      overlay.blit(detail_text, (300 - detail_text.get_width()//2, 130))
      cx = self.game.screen.get_width() // 2
      cy = self.game.screen.get_height() // 2
      self.game.screen.blit(overlay, (cx - 300, cy - 100))
  ```
- [ ] Implement `_draw_and_flip` helper:
  ```python
  def _draw_and_flip(self):
      self.game.screen.fill((20, 20, 25))
      self.draw(self.game.screen)
      self._render_progress("", "", "")  # Will be overwritten by executor
      pygame.display.flip()
  ```
- [ ] Implement engine access callbacks:
  - `_get_engine()`: returns `self.game.battle_scene.engine`
  - `_ensure_engine()`: calls `self.game.battle_scene._battle_service.create_battle()` if engine is None
  - `_switch_to_battle(scenario)`: configures battle_scene for visual test mode and switches game state
- [ ] In `TestLabScreen.__init__`, create executor:
  ```python
  self._executor = TestLabExecutor(
      registry=self.registry,
      test_history=self.test_history,
      controller=self.controller,
      render_progress=self._render_progress,
      draw_and_flip=self._draw_and_flip,
      get_engine=self._get_engine,
      ensure_engine=self._ensure_engine,
      switch_to_battle=self._switch_to_battle,
      output_log=self.output_log,
  )
  ```
- [ ] Replace `_on_run` body with: `self._executor.run_visual(self.selected_test_id)`
- [ ] Replace `_on_run_headless` body with:
  ```python
  self.headless_running = True
  self._executor.run_headless(self.selected_test_id)
  self.headless_running = False
  if self.results_panel:
      self.results_panel.set_test(self.selected_test_id)
  ```
- [ ] Replace `_on_run_all_tests` body with: `self._executor.run_all(self._get_filtered_scenarios())`
- [ ] Replace `_run_next_batch_test` body with: `self._executor.run_next_batch()`
- [ ] Replace `_continue_batch_test` body with: `self._executor.continue_batch()`
- [ ] Update `batch_running` property to delegate: check `self._executor.batch_running` if it exists
- [ ] Remove now-unused imports: `time`, `TestRunner` (if only used by execution methods)

**Notes:** The `headless_running` flag and `batch_running` flag are read by the rendering methods. Ensure these are still accessible -- either keep them as properties on the screen that delegate to the executor, or have the executor set them via callbacks.

---

### Task 4.4: Run tests and verify [Simple]
**Tests:** `pytest tests/unit/ui/test_lab_scene/ tests/unit/test_lab/ -x`

- [ ] Run targeted tests for TestLabScreen
- [ ] Run full test suite: `pytest tests/ -n 12`
- [ ] Verify no import errors
- [ ] Verify line count of `screen.py` decreased by ~250+ lines (accounting for new callback helpers)
- [ ] Verify `_render_progress` and `_draw_and_flip` work correctly by checking overlay drawing logic matches original
- [ ] Fix any failures discovered

**Notes:** This is the most complex phase. Take extra care with the render callback wiring -- the progress overlay must appear during headless runs.

---

## Phase Completion Checklist
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to Complete
- [x] Update plan.md phase table row to Complete
- [x] Update plan.md Current State to point to next phase
