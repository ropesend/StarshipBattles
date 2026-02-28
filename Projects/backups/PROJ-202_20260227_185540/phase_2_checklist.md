# Phase 2: Extract Helpers

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-202 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Extract helper methods to reduce cyclomatic complexity while preserving behavior.

**Target file:** `game/ui/screens/strategy_renderer.py`

---

## Tasks

### Task 2.1: Add Zoom Threshold Constant [Simple]
**File:** `game/ui/screens/strategy_renderer.py`
**Tests:** `pytest tests/unit/ui/screens/test_strategy_renderer.py -v`

Replace magic number 0.5 with named constant.

- [ ] Add constant at module level (line ~33): `ZOOM_DETAIL_THRESHOLD = 0.5`
- [ ] Replace line 325: `self.camera.zoom < 0.5` -> `self.camera.zoom < ZOOM_DETAIL_THRESHOLD`
- [ ] Replace line 369: `self.camera.zoom >= 0.5` -> `self.camera.zoom >= ZOOM_DETAIL_THRESHOLD`
- [ ] Replace line 375: `self.camera.zoom >= 0.5` -> `self.camera.zoom >= ZOOM_DETAIL_THRESHOLD`
- [ ] Run tests: `pytest tests/unit/ui/screens/test_strategy_renderer.py -v`
- [ ] Verify: All tests pass

**Notes:** Pure refactor - no behavioral change.

---

### Task 2.2: Extract Star Color Classification [Medium]
**File:** `game/ui/screens/strategy_renderer.py`
**Tests:** `pytest tests/unit/ui/screens/test_strategy_renderer_draw_systems.py::TestStarColorClassification -v`

Extract color-to-asset-key logic (lines 344-353) to a static/class method.

- [ ] Add new method after `_get_font()` (around line 66):
```python
@staticmethod
def _classify_star_color(color: tuple) -> str:
    """Classify star RGB color to asset key.

    Args:
        color: RGB tuple (r, g, b)

    Returns:
        Asset key string: 'red', 'blue', 'white', 'orange', or 'yellow'
    """
    r, g, b = color
    if r > 200 and g < 100:
        return 'red'
    elif b > 200 and r < 100:
        return 'blue'
    elif r > 200 and g > 200 and b > 200:
        return 'white'
    elif r > 200 and g > 150:
        return 'orange'
    return 'yellow'
```
- [ ] Replace lines 344-353 in `_draw_systems` with: `asset_key = self._classify_star_color(star.color)`
- [ ] Run tests: `pytest tests/unit/ui/screens/test_strategy_renderer_draw_systems.py::TestStarColorClassification -v`
- [ ] Verify: All color classification tests pass

**Notes:** This is a pure function extraction - highest confidence, lowest risk.

---

### Task 2.3: Extract Colony Marker Rendering [Medium]
**File:** `game/ui/screens/strategy_renderer.py`
**Tests:** `pytest tests/unit/ui/screens/test_strategy_renderer_draw_systems.py::TestColonyMarkerRendering -v`

Extract colony marker logic (lines 325-336) to a helper method.

- [ ] Add new method after `_classify_star_color()`:
```python
def _draw_colony_marker_if_zoomed_out(self, screen, sys, world_pos):
    """Draw colony ownership marker when zoomed out.

    Only draws if zoom < ZOOM_DETAIL_THRESHOLD and system has owned planets.
    """
    if self.camera.zoom >= ZOOM_DETAIL_THRESHOLD:
        return

    owned_planets = [p for p in sys.planets if p.owner_id is not None]
    if not owned_planets:
        return

    first_owner_id = owned_planets[0].owner_id
    owner_emp = next((e for e in self.empires if e.id == first_owner_id), None)
    if not owner_emp:
        return

    offset_world = pygame.math.Vector2(-0.75 * self.hex_size, -0.75 * self.hex_size)
    marker_world = world_pos + offset_world
    marker_screen = self.camera.world_to_screen(marker_world)

    pygame.draw.circle(screen, owner_emp.color, (int(marker_screen.x), int(marker_screen.y)), 5)
    pygame.draw.circle(screen, WHITE, (int(marker_screen.x), int(marker_screen.y)), 6, 1)
```
- [ ] Replace lines 325-336 in `_draw_systems` with: `self._draw_colony_marker_if_zoomed_out(screen, sys, world_pos)`
- [ ] Run tests: `pytest tests/unit/ui/screens/test_strategy_renderer_draw_systems.py::TestColonyMarkerRendering -v`
- [ ] Verify: All colony marker tests pass

**Notes:** Uses early returns to flatten nested conditionals.

---

### Task 2.4: Extract Star Rendering Loop [Complex]
**File:** `game/ui/screens/strategy_renderer.py`
**Tests:** `pytest tests/unit/ui/screens/test_strategy_renderer_draw_systems.py -v`

Extract star rendering loop body (lines 340-373) to a helper method.

- [ ] Add new method after `_draw_colony_marker_if_zoomed_out()`:
```python
def _draw_system_stars(self, screen, sys, hx, hy):
    """Draw all stars in a system with labels and selection highlight.

    Args:
        screen: Pygame surface to draw on
        sys: StarSystem to render
        hx, hy: System hex center in world pixels
    """
    primary = sys.primary_star
    if not primary:
        return

    for star in sys.stars:
        local_pixel_x, local_pixel_y = hex_to_pixel(star.location, self.hex_size)
        star_screen_pos = self.camera.world_to_screen(
            pygame.math.Vector2(hx + local_pixel_x, hy + local_pixel_y)
        )

        asset_key = self._classify_star_color(star.color)
        star_img = self._asset_manager.load_image('stars', asset_key)

        screen_star_r = max(3, int(star.diameter_hexes * self.hex_size * self.camera.zoom))

        # Selection highlight (only on primary star when system selected)
        if self.scene.selected_object == sys and star == primary:
            pygame.draw.circle(screen, WHITE, star_screen_pos, screen_star_r + 4, 1)

        # Render star image or fallback circle
        if star_img:
            scaled_img = pygame.transform.smoothscale(star_img, (screen_star_r * 2, screen_star_r * 2))
            dest_rect = scaled_img.get_rect(center=(int(star_screen_pos.x), int(star_screen_pos.y)))
            screen.blit(scaled_img, dest_rect)
        else:
            pygame.draw.circle(screen, star.color, star_screen_pos, screen_star_r)

        # Star label (only at high zoom)
        if self.camera.zoom >= ZOOM_DETAIL_THRESHOLD:
            font_size = 12 if star == primary else 10
            font = self._get_font(font_size)
            text = font.render(star.name if star != primary else sys.name, True, STAR_LABEL)
            screen.blit(text, (star_screen_pos.x + 10, star_screen_pos.y))
```
- [ ] Replace lines 338-373 in `_draw_systems` with: `self._draw_system_stars(screen, sys, hx, hy)`
- [ ] Run tests: `pytest tests/unit/ui/screens/test_strategy_renderer_draw_systems.py -v`
- [ ] Verify: All tests pass

**Notes:** This is the largest extraction and reduces the main function CC significantly.

---

### Task 2.5: Verify Complexity Reduction [Simple]
**Tests:** `radon cc game/ui/screens/strategy_renderer.py -s -a`

- [ ] Run radon: `radon cc game/ui/screens/strategy_renderer.py -s -a`
- [ ] Check `_draw_systems` CC is now <= 10 (was 29)
- [ ] Check extracted methods have reasonable CC (< 10 each)
- [ ] Run full test suite: `pytest tests/ -n 12`
- [ ] Verify: All tests pass

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] `_draw_systems` CC reduced to <= 10
- [ ] All tests pass
- [ ] Commit: `[PROJ-202] Phase 2: Extract helpers from _draw_systems`
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 3
