# Phase 1: Create Menu Panel Component

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-72 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Create the StrategyMenuPanel dropdown component

---

## Tasks

### Task 1.1: Create StrategyMenuPanel class [Simple]
**New File:** `game/ui/screens/strategy_menu_panel.py`
**Tests:** `pytest tests/ --testmon`

- [x] Create file `game/ui/screens/strategy_menu_panel.py`
- [x] Import `pygame`, `pygame_gui`, `pygame_gui.elements`
- [x] Create `StrategyMenuPanel` class subclassing `pygame_gui.elements.UIPanel`
- [x] Constructor signature: `__init__(self, relative_rect, manager, on_option_callback)`
  - Call `super().__init__(relative_rect, starting_height=2, manager=manager)` (starting_height=2 ensures panel renders above top_bar)
  - Store `on_option_callback`
  - Create 6 UIButton instances inside the panel container
- [x] Button layout: each 200x35, vertically stacked with 5px gaps, 10px padding
  - Button 1: "Save Game" → option `"save_game"`
  - Button 2: "Load Game" → option `"load_game"`
  - Button 3: "Settings" → option `"settings"`
  - Button 4: "Controls" → option `"controls"`
  - Button 5: "Quit to Menu" → option `"quit_to_menu"`
  - Button 6: "Quit Game" → option `"quit_game"`
- [x] Store buttons in `self._option_buttons` dict mapping `UIButton` → `option_name`
- [x] Add `process_event(self, event)` method:
  ```python
  def process_event(self, event):
      if event.type == pygame_gui.UI_BUTTON_PRESSED:
          option = self._option_buttons.get(event.ui_element)
          if option:
              self.on_option_callback(option)
              return True
      return super().process_event(event)
  ```
- [x] Panel total size: 220w x (6*35 + 7*5) = 220w x 245h
- [x] Verify: File parses without errors (`python -c "from game.ui.screens.strategy_menu_panel import StrategyMenuPanel"`)

**Notes:**
- Added module-level named constants for all layout values and button definitions
- Created `_create_buttons()` helper for clean separation
- Added `get_option_buttons()` accessor for testing
- 19 unit tests in `tests/unit/ui/screens/test_strategy_menu_panel.py`

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase
