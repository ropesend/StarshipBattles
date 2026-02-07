# Phase 3: Extract System Mode Module

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-60 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Extract all system-mode-specific code from `screen.py` into `system_mode.py`, creating a `SystemModeHelper` class.

---

## Tasks

### Task 3.1: Create `system_mode.py` with `SystemModeHelper` class [Medium]
**File:** `game/ui/screens/galaxy_test/system_mode.py`
**Source lines from screen.py (originally galaxy_test_screen.py):**
- `_create_system_ui()` (lines 315-441, ~127 lines)
- `_get_blueprint_options()` (lines 443-454, ~12 lines)
- `_generate_system()` (lines 544-624, ~80 lines)
- `_draw_system()` (lines 966-1053, ~88 lines)
- `_center_camera_on_system()` (lines 626-660, ~35 lines)
- `_handle_system_click()` (lines 694-731, ~37 lines)
- `_update_inspector_panel()` (lines 733-753, ~20 lines)
- `_format_star_info()` (lines 755-774, ~20 lines)
- `_format_planet_info()` (lines 776-832, ~56 lines)
- `_get_classification_reason()` (lines 834-852, ~19 lines)

- [ ] Create `system_mode.py` with class `SystemModeHelper`:
  ```python
  class SystemModeHelper:
      def __init__(self, screen):
          self.screen = screen
          self.test_system = None
          self.system_seed = None
          self.selected_blueprint = "random"
          self.selected_object = None
  ```
- [ ] Move `_create_system_ui()` -> `SystemModeHelper.create_ui()` (returns list of UI elements)
  - Update references: `self.screen_width` -> `self.screen.screen_width`, etc.
  - `self.ui_manager` -> `self.screen.ui_manager`
  - Store UI element references on `self` (e.g., `self.blueprint_dropdown`, `self.btn_generate_system`, etc.)
- [ ] Move `_get_blueprint_options()` -> `SystemModeHelper._get_blueprint_options()` (private helper)
- [ ] Move `_generate_system()` -> `SystemModeHelper.generate()`
  - System state lives on the helper
- [ ] Move `_draw_system()` -> `SystemModeHelper.draw(screen_surface)`
- [ ] Move `_center_camera_on_system()` -> `SystemModeHelper._center_camera()`
- [ ] Move `_handle_system_click()` -> `SystemModeHelper.handle_click(mx, my)`
- [ ] Move inspector methods -> `SystemModeHelper._update_inspector_panel()`, `_format_star_info()`, `_format_planet_info()`, `_get_classification_reason()`
- [ ] Add imports: `PLANET_TYPE_COLORS, HEX_SIZE, SIDEBAR_WIDTH` from constants, plus all strategy/planet imports

**Notes:**

### Task 3.2: Update `screen.py` to Use `SystemModeHelper` [Medium]
**File:** `game/ui/screens/galaxy_test/screen.py`
**Tests:** `pytest tests/ -x -q --tb=short`

- [ ] Add import: `from game.ui.screens.galaxy_test.system_mode import SystemModeHelper`
- [ ] In `__init__`: create `self.system_helper = SystemModeHelper(self)`
- [ ] In `_go_to_system_mode()`: call `self._ui_elements = self.system_helper.create_ui()` instead of `self._create_system_ui()`
- [ ] In `draw()`: replace `self._draw_system(screen)` with `self.system_helper.draw(screen)`
- [ ] In `_handle_button_click()`: replace `self._generate_system()` with `self.system_helper.generate()`
  - Update button check: `getattr(self, 'btn_generate_system', None)` -> `getattr(self.system_helper, 'btn_generate_system', None)`
- [ ] In `handle_event()`: replace `self._handle_system_click(mx, my)` with `self.system_helper.handle_click(mx, my)`
- [ ] Remove all moved methods from `screen.py`:
  - `_create_system_ui()`, `_get_blueprint_options()`, `_generate_system()`
  - `_draw_system()`, `_center_camera_on_system()`, `_handle_system_click()`
  - `_update_inspector_panel()`, `_format_star_info()`, `_format_planet_info()`, `_get_classification_reason()`
- [ ] Remove system-specific imports no longer needed (Star, Planet, planet_physics, etc.)
- [ ] Remove system-specific state from `__init__` (`self.test_system`, `self.system_seed`, `self.selected_blueprint`, `self.selected_object`)
- [ ] Run `pytest tests/ -x -q --tb=short` - all tests pass
- [ ] Verify: `python -c "from game.ui.screens.galaxy_test import GalaxyTestScreen; print('OK')"`
- [ ] Count lines in screen.py: should be ~400-500 lines

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] `system_mode.py` exists with `SystemModeHelper` class
- [ ] `screen.py` delegates all system operations to helper
- [ ] No system-specific state/methods remain in screen.py
- [ ] `screen.py` is under 500 lines
- [ ] All tests passing
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase
