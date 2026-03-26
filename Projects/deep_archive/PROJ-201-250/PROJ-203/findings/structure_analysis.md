# Structure Analysis: `_draw_systems` Method

**File:** `game/ui/screens/strategy_renderer.py`
**Lines:** 306-376
**Cyclomatic Complexity:** High (multiple nested conditionals)

---

## Overview

The `_draw_systems` method renders star systems on the strategy map. It iterates through all systems, applies viewport culling, and renders stars with their visual properties. The method handles multiple zoom-dependent rendering paths.

---

## Control Flow Structure

### Primary Loop (Line 315)
```python
for sys in self.galaxy.systems.values():
```
The entire method body is wrapped in this loop, which iterates over all star systems.

### Key Branch Points

| Line | Condition | Purpose |
|------|-----------|---------|
| 319 | Viewport bounds check | Culling (early continue) |
| 325 | `self.camera.zoom < 0.5` | Colony marker at low zoom |
| 327 | `owned_planets` truthy | Colony ownership check |
| 329-330 | Empire lookup + check | Owner existence validation |
| 339 | `primary` truthy | Star rendering guard |
| 346-353 | Color RGB chain | Asset key determination |
| 359 | Selection + primary check | Selection highlight |
| 362 | `star_img` truthy | Image vs fallback circle |
| 369 | `self.camera.zoom >= 0.5` | Label rendering threshold |
| 375 | `self.camera.zoom >= 0.5` | Detail rendering threshold |

---

## Complexity Contributors

### 1. Nested Colony Marker Block (Lines 325-336)

**Current structure:**
```python
if self.camera.zoom < 0.5:                    # Level 1
    owned_planets = [p for p in sys.planets if p.owner_id is not None]
    if owned_planets:                          # Level 2
        first_owner_id = owned_planets[0].owner_id
        owner_emp = next((e for e in self.empires if e.id == first_owner_id), None)
        if owner_emp:                          # Level 3
            # ... 5 lines of drawing code
```

**Issues:**
- Three levels of nesting
- List comprehension followed by conditional check (could be combined)
- Empire lookup is repeated pattern (appears elsewhere in codebase)

**Simplification opportunity:** Extract to `_draw_colony_marker(screen, sys, world_pos)` helper.

---

### 2. Star Color-to-Asset Mapping (Lines 344-353)

**Current structure:**
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
- Pure data transformation embedded in rendering logic
- Magic numbers (200, 100, 150) without named constants
- If/elif chain is a code smell for data lookup

**Simplification opportunity:** Extract to pure function `_color_to_asset_key(color) -> str` or use a lookup table.

---

### 3. Star Rendering Block (Lines 340-373)

**Current structure:**
```python
for star in sys.stars:                         # Level 1 (within system loop)
    # position calculation...
    # color-to-asset mapping (if/elif chain)
    # star image loading
    # radius calculation

    if self.scene.selected_object == sys and star == primary:  # Level 2
        # selection highlight

    if star_img:                               # Level 2
        # scale and blit
    else:
        # fallback circle

    if self.camera.zoom >= 0.5:                # Level 2
        # font size conditional (ternary)
        # label rendering
```

**Issues:**
- Multiple independent concerns interleaved
- Mixing data preparation with rendering
- The `star == primary` check appears twice (lines 359, 370, 372)

**Simplification opportunities:**
- Separate position/size calculation from drawing
- Extract star label rendering to helper
- Cache `is_primary = star == primary` to avoid repeated comparison

---

### 4. Repeated Zoom Threshold Checks

**Observations:**
- Line 325: `self.camera.zoom < 0.5` (colony marker)
- Line 369: `self.camera.zoom >= 0.5` (labels)
- Line 375: `self.camera.zoom >= 0.5` (details)

**Issue:** The zoom threshold (0.5) is a magic number repeated three times.

**Simplification opportunity:** Define `DETAIL_ZOOM_THRESHOLD = 0.5` constant, or compute `is_detailed_view = self.camera.zoom >= 0.5` once at method start.

---

## Early Returns and Continue Statements

### Existing Early Continue (Line 319-320)
```python
if not (min_x < world_pos.x < max_x and min_y < world_pos.y < max_y):
    continue
```
**Status:** Good use of early continue for viewport culling.

### Missing Early Continue Opportunities

**Line 339:** The `if primary:` guard wraps 35 lines of code. However, this is unlikely to be false (systems typically have a primary star), so this is acceptable as-is.

---

## Repeated Patterns

### 1. World-to-Screen Coordinate Conversion
Appears multiple times:
- Line 322: `screen_pos = self.camera.world_to_screen(world_pos)`
- Line 333: `marker_screen = self.camera.world_to_screen(marker_world)`
- Line 342: `star_screen_pos = self.camera.world_to_screen(...)`

**Not an issue:** These are different positions, conversion is necessary.

### 2. hex_to_pixel Calls
- Line 316: System location
- Line 341: Star location within system

**Not an issue:** Different coordinate spaces.

### 3. Integer Conversion for Drawing
- Line 335: `(int(marker_screen.x), int(marker_screen.y))`
- Line 364: `(int(star_screen_pos.x), int(star_screen_pos.y))`

**Minor issue:** Could use a helper `to_int_tuple(vec)` for consistency.

---

## Data Transformations That Could Be Separated

### 1. Color-to-Asset Key Mapping (Lines 344-353)
**Extract as:** `_star_color_to_asset_key(color: tuple) -> str`

### 2. Star Radius Calculation (Line 357)
```python
screen_star_r = max(3, int(star.diameter_hexes * self.hex_size * self.camera.zoom))
```
**Extract as:** `_calculate_star_screen_radius(star, hex_size, zoom) -> int`

### 3. Owner Empire Lookup (Lines 328-329)
```python
first_owner_id = owned_planets[0].owner_id
owner_emp = next((e for e in self.empires if e.id == first_owner_id), None)
```
**Extract as:** `_get_system_owner_empire(sys) -> Optional[Empire]`

---

## Summary of Refactoring Opportunities

| Priority | Lines | Issue | Suggested Fix |
|----------|-------|-------|---------------|
| High | 344-353 | Color mapping if/elif chain | Extract to pure function or lookup table |
| High | 325-336 | 3-level nesting for colony marker | Extract to helper method |
| Medium | 340-373 | Mixed concerns in star loop | Separate data prep from rendering |
| Medium | 325,369,375 | Magic zoom threshold | Define constant |
| Low | 359,370,372 | Repeated `star == primary` | Cache in local variable |
| Low | 335,364 | Int conversion pattern | Optional helper |

---

## Recommended Extraction Order

1. **`_color_to_asset_key(color)`** - Pure function, zero dependencies, easy to test
2. **`_draw_colony_marker(screen, sys, world_pos)`** - Isolates nested block
3. **`_draw_star(screen, star, star_screen_pos, is_primary, is_selected)`** - Largest complexity reduction
4. **Zoom threshold constant** - Simple rename refactor

This order minimizes risk by starting with the simplest, most isolated changes.
