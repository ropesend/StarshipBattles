# Structure Analysis: `_draw_systems` (Lines 306-376)

## Overview

The `_draw_systems` function in `strategy_renderer.py` renders all star systems on the galaxy map, including stars, colony markers, labels, and system details. The function spans 71 lines and has a cyclomatic complexity driven by multiple nested conditionals.

---

## Control Flow Structure

### Main Loop Structure
```
for sys in self.galaxy.systems.values():        # Line 315
    [viewport culling check]                     # Line 319
    [colony marker logic - zoom < 0.5]           # Lines 325-336
    [star rendering - if primary exists]         # Lines 339-373
    [system details - zoom >= 0.5]               # Lines 375-376
```

---

## Complexity Contributors (Ranked by Impact)

### 1. Star Color Classification Logic (Lines 344-353) - HIGH COMPLEXITY

**Current Code:**
```python
asset_key = 'yellow'
color = star.color
if color[0] > 200 and color[1] < 100:
    asset_key = 'red'
elif color[2] > 200 and color[0] < 100:
    asset_key = 'blue'
elif color[0] > 200 and color[1] > 200 and color[2] > 200:
    asset_key = 'white'
elif color[0] > 200 and color[1] > 150:
    asset_key = 'orange'
```

**Issues:**
- 5 branches with magic numbers (200, 100, 150)
- Color classification logic is data, not control flow
- Repeated `color[n] > threshold` pattern
- Could be extracted to a pure function or lookup table

**Recommendation:** Extract to `_classify_star_color(rgb_tuple) -> str` or use a declarative mapping.

---

### 2. Nested Colony Marker Logic (Lines 325-336) - MEDIUM-HIGH COMPLEXITY

**Current Code:**
```python
if self.camera.zoom < 0.5:                           # Line 325
    owned_planets = [p for p in sys.planets if p.owner_id is not None]
    if owned_planets:                                 # Line 327
        first_owner_id = owned_planets[0].owner_id
        owner_emp = next((e for e in self.empires if e.id == first_owner_id), None)
        if owner_emp:                                 # Line 330
            # draw marker (6 lines)
```

**Issues:**
- 3 levels of nesting
- Early continue not used (could invert conditions)
- Owner lookup pattern is common elsewhere
- Marker drawing is 6 lines that could be extracted

**Recommendation:**
- Invert to `if self.camera.zoom >= 0.5: continue` OR extract entire block to `_draw_colony_marker_if_needed()`
- Extract owner lookup to shared helper

---

### 3. Star Rendering Block (Lines 339-373) - MEDIUM COMPLEXITY

**Current Code:**
```python
if primary:                                           # Line 339
    for star in sys.stars:                           # Line 340
        [position calculation]                        # Lines 341-342
        [color classification]                        # Lines 344-353 (analyzed above)
        [image loading]                              # Line 355
        [selection highlight]                        # Lines 359-360
        [image or fallback rendering]                # Lines 362-367
        [label rendering - zoom >= 0.5]              # Lines 369-373
```

**Issues:**
- Loop body is 33 lines with multiple responsibilities
- Selection highlight condition: `self.scene.selected_object == sys and star == primary` (Line 359)
- Image-or-fallback rendering is a common pattern (Lines 362-367)
- Label rendering is zoom-gated (Line 369) - duplicate check with Line 375

**Recommendation:**
- Extract star rendering loop body to `_draw_star(screen, star, sys, screen_pos, is_primary)`
- Extract image-or-fallback pattern to utility

---

### 4. Conditional Image vs Fallback Rendering (Lines 362-367)

**Current Code:**
```python
if star_img:
    scaled_img = pygame.transform.smoothscale(star_img, (screen_star_r * 2, screen_star_r * 2))
    dest_rect = scaled_img.get_rect(center=(int(star_screen_pos.x), int(star_screen_pos.y)))
    screen.blit(scaled_img, dest_rect)
else:
    pygame.draw.circle(screen, color, star_screen_pos, screen_star_r)
```

**Issues:**
- Common pattern likely repeated elsewhere in codebase
- 6 lines that obscure the intent ("draw star visually")

**Recommendation:** Could be a shared utility `draw_scaled_image_or_circle(screen, img, pos, radius, fallback_color)`.

---

### 5. Duplicate Zoom Threshold Checks

**Lines with `zoom >= 0.5` or `zoom < 0.5`:**
- Line 325: `if self.camera.zoom < 0.5:`
- Line 369: `if self.camera.zoom >= 0.5:`
- Line 375: `if self.camera.zoom >= 0.5:`

**Issues:**
- Magic number 0.5 repeated 3 times
- Should be a named constant like `ZOOM_DETAIL_THRESHOLD`
- Lines 369 and 375 both check `zoom >= 0.5` - could be combined

---

## Early Return Opportunities

### Current: Viewport Culling (Line 319)
```python
if not (min_x < world_pos.x < max_x and min_y < world_pos.y < max_y):
    continue
```
This is already an early continue - good.

### Missed Opportunity: No Primary Star (Line 339)
```python
if primary:
    # 34 lines of code
```
Could be:
```python
if not primary:
    if self.camera.zoom >= 0.5:
        self._draw_system_details(screen, sys, world_pos)
    continue
```
This would flatten the main rendering logic by one level.

---

## Repeated Patterns

### 1. World-to-Screen Coordinate Conversion
- Line 322: `screen_pos = self.camera.world_to_screen(world_pos)`
- Line 333: `marker_screen = self.camera.world_to_screen(marker_world)`
- Line 342: `star_screen_pos = self.camera.world_to_screen(...)`

Pattern is unavoidable but positions are computed inline with offsets. Could be cleaner.

### 2. Circle Drawing with Outline
Lines 335-336:
```python
pygame.draw.circle(screen, owner_emp.color, (int(marker_screen.x), int(marker_screen.y)), 5)
pygame.draw.circle(screen, WHITE, (int(marker_screen.x), int(marker_screen.y)), 6, 1)
```
This "filled circle with outline" pattern is likely repeated elsewhere.

### 3. Font Size Selection by Condition (Lines 370-372)
```python
font_size = 12 if star == primary else 10
font = self._get_font(font_size)
text = font.render(star.name if star != primary else sys.name, True, STAR_LABEL)
```
Two ternaries checking `star == primary` - could be combined into a single conditional block.

---

## Data Transformations That Could Be Separated

### 1. Star Color Classification (Lines 344-353)
**Input:** RGB tuple `star.color`
**Output:** Asset key string ('yellow', 'red', 'blue', 'white', 'orange')
**Type:** Pure function - no side effects, no state needed

### 2. Viewport Bounds Calculation (Lines 308-313)
**Input:** Camera, screen dimensions
**Output:** min_x, max_x, min_y, max_y bounds
**Type:** Pure computation - could be `_get_visible_bounds()` returning a named tuple

### 3. Colony Owner Lookup (Lines 326-329)
**Input:** System's planets, list of empires
**Output:** First owner's empire (or None)
**Type:** Query - could be `_get_first_colony_owner(sys) -> Optional[Empire]`

---

## Summary of Refactoring Priorities

| Priority | Issue | Lines | Complexity Reduction |
|----------|-------|-------|---------------------|
| 1 | Extract star color classification | 344-353 | High - removes 5 branches |
| 2 | Extract colony marker drawing | 325-336 | Medium - removes 3 nesting levels |
| 3 | Define ZOOM_DETAIL_THRESHOLD constant | 325, 369, 375 | Low - removes magic numbers |
| 4 | Flatten primary star check with early continue | 339 | Medium - reduces nesting |
| 5 | Extract star rendering to helper method | 340-373 | High - simplifies loop body |

---

## Estimated Complexity Reduction

**Current estimated cyclomatic complexity:** ~12-15 (multiple branches, nested conditions)

**After suggested refactoring:** ~5-7 (main loop + delegation to extracted methods)

The primary wins come from:
1. Moving the star color classification to a lookup or mapping
2. Extracting the colony marker block
3. Extracting star rendering to a dedicated method
