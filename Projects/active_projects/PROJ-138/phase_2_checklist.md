# Phase 2: Wire into StrategyUI

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-138 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Wire SystemSelectionWindow into the StrategyWindowManager and StrategyUI delegation chain so the existing `_show_system_picker()` call discovers and uses it.

---

## Tasks

### Task 2.1: Add open_system_selection to StrategyWindowManager [Simple]
**File:** `game/ui/screens/strategy_window_manager.py`
**Tests:** `pytest tests/unit/ui/screens/test_strategy_window_manager.py -v`

- [ ] Add import at top (line ~22): `from game.ui.screens.system_selection_window import SystemSelectionWindow`
- [ ] Add new method after `prompt_planet_selection` (after line 396):
  ```python
  def open_system_selection(self, systems, current_system, on_selected: Callable) -> None:
      """Open a modal window to select a star system.

      Args:
          systems: List of StarSystem objects to choose from.
          current_system: Current StarSystem (for distance display).
          on_selected: Callback called with selected system name string.
      """
      width = 450
      height = 500
      x = (self.width - width) / 2
      y = (self.height - height) / 2
      rect = pygame.Rect(x, y, width, height)
      SystemSelectionWindow(rect, self.manager, systems, current_system, on_selected)
  ```
- [ ] Verify: No stored reference needed (fire-and-forget like prompt_planet_selection)

**Notes:**

### Task 2.2: Add show_system_picker delegate to StrategyUI [Simple]
**File:** `game/ui/screens/strategy_ui.py`
**Tests:** `pytest tests/unit/ui/screens/test_strategy_superweapons.py -v` (existing tests use `hasattr` mock)

- [ ] Add delegate method after `prompt_planet_selection` (after line 341):
  ```python
  def show_system_picker(self, systems, current_system, on_selected):
      """Open a modal window to select a star system for warp point creation."""
      self.window_manager.open_system_selection(systems, current_system, on_selected)
  ```
- [ ] Verify: Method signature matches what `strategy_superweapons.py:388` expects: `show_system_picker(systems, current_system, on_selected)`

**Notes:**

### Task 2.3: Add window manager tests [Simple]
**File:** `tests/unit/ui/screens/test_strategy_window_manager.py`
**Tests:** `pytest tests/unit/ui/screens/test_strategy_window_manager.py -v`

- [ ] Add test class `TestSystemSelectionPrompt` after `TestPlanetSelectionPrompt` (after line ~447):
  ```python
  class TestSystemSelectionPrompt:
      """Tests for system selection prompt."""

      @patch('game.ui.screens.strategy_window_manager.SystemSelectionWindow')
      def test_open_system_selection_creates_window(self, mock_window_class, window_manager):
          """Test open_system_selection creates selection window."""
          systems = [Mock(), Mock()]
          current_system = Mock()
          callback = Mock()
          window_manager.open_system_selection(systems, current_system, callback)
          mock_window_class.assert_called_once()

      @patch('game.ui.screens.strategy_window_manager.SystemSelectionWindow')
      def test_open_system_selection_passes_args(self, mock_window_class, window_manager):
          """Test open_system_selection passes systems, current_system, and callback."""
          systems = [Mock(), Mock()]
          current_system = Mock()
          callback = Mock()
          window_manager.open_system_selection(systems, current_system, callback)
          call_args = mock_window_class.call_args
          assert call_args[0][2] == systems
          assert call_args[0][3] == current_system
          assert call_args[0][4] is callback
  ```
- [ ] Run: `pytest tests/unit/ui/screens/test_strategy_window_manager.py -v` — all pass

**Notes:**

### Task 2.4: Run regression and full test suite [Simple]
**Tests:** Full suite
- [ ] Run: `pytest tests/unit/ui/test_superweapon_operations.py tests/unit/ui/screens/test_strategy_superweapons.py -v` — existing tests still pass
- [ ] Run: `pytest tests/ -n 12` — full suite passes (baseline: 11,906)

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to indicate project complete
