# Phase 3: Simplify Control Flow

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-202 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Simplify remaining control flow in `_draw_systems` and extracted helpers.

**Target file:** `game/ui/screens/strategy_renderer.py`

---

## Tasks

### Task 3.1: Review Refactored _draw_systems [Simple]
**File:** `game/ui/screens/strategy_renderer.py`
**Tests:** `pytest tests/unit/ui/screens/test_strategy_renderer_draw_systems.py -v`

Verify the main function is now clean and simple.

- [ ] Read current `_draw_systems` method
- [ ] Verify structure matches:
```python
def _draw_systems(self, screen):
    """Draw all star systems with stars, planets, and warp points."""
    # Viewport bounds calculation
    tl = self.camera.screen_to_world((0, 0))
    br = self.camera.screen_to_world((self.screen_width, self.screen_height))
    margin = 600
    min_x, max_x = min(tl.x, br.x) - margin, max(tl.x, br.x) + margin
    min_y, max_y = min(tl.y, br.y) - margin, max(tl.y, br.y) + margin

    for sys in self.galaxy.systems.values():
        hx, hy = hex_to_pixel(sys.global_location, self.hex_size)
        world_pos = pygame.math.Vector2(hx, hy)

        # Viewport culling
        if not (min_x < world_pos.x < max_x and min_y < world_pos.y < max_y):
            continue

        screen_pos = self.camera.world_to_screen(world_pos)

        # Colony marker (zoomed out only)
        self._draw_colony_marker_if_zoomed_out(screen, sys, world_pos)

        # Stars
        self._draw_system_stars(screen, sys, hx, hy)

        # System details (planets, warp points - zoomed in only)
        if self.camera.zoom >= ZOOM_DETAIL_THRESHOLD:
            self._draw_system_details(screen, sys, world_pos)
```
- [ ] Count decision points (should be ~3-4: loop, culling, zoom check)
- [ ] Verify: Structure is clean

**Notes:** If structure differs, document deviations.

---

### Task 3.2: Document Star Color Thresholds [Simple]
**File:** `game/ui/screens/strategy_renderer.py`

Add documentation for the magic number thresholds in `_classify_star_color`.

- [ ] Add docstring explanation for color thresholds:
```python
@staticmethod
def _classify_star_color(color: tuple) -> str:
    """Classify star RGB color to asset key.

    Color classification thresholds:
    - Red: R > 200, G < 100 (high red, low green)
    - Blue: B > 200, R < 100 (high blue, low red)
    - White: R > 200, G > 200, B > 200 (all channels high)
    - Orange: R > 200, G > 150 (high red, medium green)
    - Yellow: default (anything else)

    Args:
        color: RGB tuple (r, g, b) with values 0-255

    Returns:
        Asset key string: 'red', 'blue', 'white', 'orange', or 'yellow'
    """
```
- [ ] Verify: Docstring is accurate and complete

**Notes:** The thresholds are intentional design choices, not arbitrary.

---

### Task 3.3: Consider Color Classification Constants [Optional]
**File:** `game/ui/screens/strategy_renderer.py`

Optionally extract threshold magic numbers to constants.

- [ ] Evaluate: Are constants like `STAR_COLOR_HIGH_THRESHOLD = 200` helpful?
- [ ] Decision: Add constants OR document decision to keep inline
- [ ] If adding constants:
  - `STAR_COLOR_HIGH = 200`
  - `STAR_COLOR_LOW = 100`
  - `STAR_COLOR_MEDIUM = 150`
- [ ] Update `_classify_star_color` to use constants (if decided yes)

**Notes:** This is optional - inline values with good documentation may be clearer.

---

### Task 3.4: Run Final Complexity Check [Simple]
**Tests:** `radon cc game/ui/screens/strategy_renderer.py -s -a`

- [ ] Run radon: `radon cc game/ui/screens/strategy_renderer.py -s -a`
- [ ] Record final CC for `_draw_systems`: ____ (target: < 10)
- [ ] Record final CC for `_classify_star_color`: ____ (target: < 6)
- [ ] Record final CC for `_draw_colony_marker_if_zoomed_out`: ____ (target: < 6)
- [ ] Record final CC for `_draw_system_stars`: ____ (target: < 12)
- [ ] Verify: All extracted methods have CC < 15

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Code is clean and well-documented
- [ ] All tests pass
- [ ] Commit: `[PROJ-202] Phase 3: Simplify control flow and document`
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 4
