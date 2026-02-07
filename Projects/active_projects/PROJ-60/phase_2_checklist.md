# Phase 2: Extract Galaxy Mode Module

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-60 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Extract all galaxy-mode-specific code from `screen.py` into `galaxy_mode.py`, creating a `GalaxyModeHelper` class.

---

## Tasks

### Task 2.1: Create `galaxy_mode.py` with `GalaxyModeHelper` class [Medium]
**File:** `game/ui/screens/galaxy_test/galaxy_mode.py`
**Source lines from screen.py (originally galaxy_test_screen.py):**
- `_create_galaxy_ui()` (lines 159-313, ~155 lines)
- `_generate_galaxy()` (lines 456-542, ~86 lines)
- `_draw_galaxy()` (lines 897-924, ~27 lines)
- `_draw_warp_lanes()` (lines 926-964, ~38 lines)
- `_center_camera_on_galaxy()` (lines 662-692, ~30 lines)

- [ ] Create `galaxy_mode.py` with class `GalaxyModeHelper`:
  ```python
  class GalaxyModeHelper:
      def __init__(self, screen):
          self.screen = screen  # Access camera, ui_manager, canvas dims
          self.galaxy = None
          self.generation_time = 0.0
          self.system_count = 100
          self.galaxy_radius = 4000
          self.galaxy_type = "spiral"
          self.galaxy_seed = None
  ```
- [ ] Move `_create_galaxy_ui()` -> `GalaxyModeHelper.create_ui()` (returns list of UI elements)
  - Update references: `self.screen_width` -> `self.screen.screen_width`, `self.canvas_width` -> `self.screen.canvas_width`, etc.
  - `self.ui_manager` -> `self.screen.ui_manager`
  - Store button/slider/label references on `self` (e.g., `self.system_count_slider`, `self.btn_generate`, etc.)
- [ ] Move `_generate_galaxy()` -> `GalaxyModeHelper.generate()`
  - Galaxy state (`self.galaxy`, `self.generation_time`, etc.) lives on the helper
  - Camera access: `self.screen.camera`
- [ ] Move `_draw_galaxy()` -> `GalaxyModeHelper.draw(screen_surface)`
- [ ] Move `_draw_warp_lanes()` -> `GalaxyModeHelper._draw_warp_lanes(screen_surface)` (private helper)
- [ ] Move `_center_camera_on_galaxy()` -> `GalaxyModeHelper._center_camera()`
- [ ] Add `update_slider_displays()` method (extract from `update()` lines 865-871)
- [ ] Add imports: `SIDEBAR_WIDTH, HEX_SIZE, PLANET_TYPE_COLORS` from constants, plus all strategy/generation imports

**Notes:**

### Task 2.2: Update `screen.py` to Use `GalaxyModeHelper` [Medium]
**File:** `game/ui/screens/galaxy_test/screen.py`
**Tests:** `pytest tests/ -x -q --tb=short`

- [ ] Add import: `from game.ui.screens.galaxy_test.galaxy_mode import GalaxyModeHelper`
- [ ] In `__init__`: create `self.galaxy_helper = GalaxyModeHelper(self)`
- [ ] In `_go_to_galaxy_mode()`: call `self._ui_elements = self.galaxy_helper.create_ui()` instead of `self._create_galaxy_ui()`
- [ ] In `draw()`: replace `self._draw_galaxy(screen)` with `self.galaxy_helper.draw(screen)`
- [ ] In `_handle_button_click()`: replace `self._generate_galaxy()` with `self.galaxy_helper.generate()`
  - Update button check: `getattr(self, 'btn_generate', None)` -> `getattr(self.galaxy_helper, 'btn_generate', None)`
- [ ] In `update()`: replace slider display logic with `self.galaxy_helper.update_slider_displays()`
- [ ] Remove all moved methods from `screen.py`:
  - `_create_galaxy_ui()`
  - `_generate_galaxy()`
  - `_draw_galaxy()`
  - `_draw_warp_lanes()`
  - `_center_camera_on_galaxy()`
- [ ] Remove galaxy-specific imports that are no longer needed in screen.py (placement strategies, density map, etc.)
- [ ] Remove galaxy-specific state from `__init__` (`self.galaxy`, `self.generation_time`, `self.system_count`, `self.galaxy_radius`, `self.galaxy_type`, `self.galaxy_seed`)
- [ ] Run `pytest tests/ -x -q --tb=short` - all tests pass
- [ ] Verify: `python -c "from game.ui.screens.galaxy_test import GalaxyTestScreen; print('OK')"`
- [ ] Count lines in screen.py: should be ~900-950 lines (down from ~1130 after Phase 1)

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] `galaxy_mode.py` exists with `GalaxyModeHelper` class
- [ ] `screen.py` delegates all galaxy operations to helper
- [ ] No galaxy-specific state/methods remain in screen.py
- [ ] All tests passing
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase
