# Phase 2: Wire Up Strategy UI

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-72 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Replace Save Game button with Menu button, add panel toggle logic and event handling

---

## Tasks

### Task 2.1: Replace Save Game button with Menu button [Simple]
**File:** `game/ui/screens/strategy_ui.py`
**Tests:** `pytest tests/ --testmon`

- [x] Add `self.menu_panel = None` to `__init__` (near line 43, alongside other window tracking)
- [x] Replace `self.btn_save_game` with `self.btn_menu` (lines 241-247):
  ```python
  # Menu Button (replaces Save Game - options now in dropdown)
  self.btn_menu = pygame_gui.elements.UIButton(
      relative_rect=pygame.Rect(main_start_x + 5*(btn_w+gap), 5, btn_w, 40),
      text="Menu",
      manager=self.manager,
      container=self.top_bar
  )
  ```
- [x] Verify: No references to `btn_save_game` remain in the file

### Task 2.2: Add panel management methods [Simple]
**File:** `game/ui/screens/strategy_ui.py`

- [x] Add import at top: `from game.ui.screens.strategy_menu_panel import StrategyMenuPanel`
- [x] Add `toggle_menu_panel(self)` method:
  - If `self.menu_panel` exists, call `close_menu_panel()`
  - Else call `open_menu_panel()`
- [x] Add `open_menu_panel(self)` method:
  - Get Menu button absolute rect via `self.btn_menu.get_abs_rect()`
  - Create panel rect positioned below button: `pygame.Rect(btn_rect.x, btn_rect.bottom + 2, 220, 245)`
  - Create `StrategyMenuPanel(panel_rect, self.manager, self._on_menu_option_selected)`
  - Store in `self.menu_panel`
- [x] Add `close_menu_panel(self)` method:
  - If `self.menu_panel`: call `.kill()`, set to `None`
- [x] Add `_on_menu_option_selected(self, option)` method:
  - Call `close_menu_panel()`
  - Call `self.scene.on_menu_option(option)`

### Task 2.3: Update event handling [Medium]
**File:** `game/ui/screens/strategy_ui.py` (handle_event method)

- [x] In the `UI_BUTTON_PRESSED` handler block:
  - Replace the `btn_save_game` check with `btn_menu` → `toggle_menu_panel()`
  - Delete the old `btn_save_game` handler lines
- [x] Add click-outside detection BEFORE the `UI_BUTTON_PRESSED` block
- [x] Add Escape key handling (early in handle_event, before other key checks)
- [x] Update `_has_modal_open()` to include `self.menu_panel`

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase
