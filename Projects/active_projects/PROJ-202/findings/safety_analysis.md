# Safety Analysis: `_draw_systems` Function

**File:** `game/ui/screens/strategy_renderer.py`
**Lines:** 306-376
**Cyclomatic Complexity:** Target for reduction (see `complexity_target.md`)

---

## 1. Function Overview

The `_draw_systems` method renders all star systems on the strategy map. It handles:
- Viewport culling (skip off-screen systems)
- Colony markers at low zoom
- Star rendering with color-based asset selection
- Selection highlighting
- Star labels at high zoom
- Delegation to `_draw_system_details` for planets/warp points

---

## 2. Edge Cases and Error Handling Paths

### 2.1 Null/Empty Data Handling
| Condition | Current Handling | Risk Level |
|-----------|------------------|------------|
| `self.galaxy.systems` is empty | Loop doesn't execute - safe | Low |
| `sys.primary_star` is None | Guarded by `if primary:` at line 339 | Low |
| `sys.stars` is empty | Loop doesn't execute when `primary` is falsy | Low |
| `sys.planets` is empty | List comprehension returns `[]` - safe | Low |
| `owned_planets` is empty | `if owned_planets:` guard at line 327 | Low |
| `owner_emp` is None | `if owner_emp:` guard at line 330 | Low |
| `star_img` is None | Fallback to `pygame.draw.circle` at line 367 | **Medium** - fallback path less tested |

### 2.2 Coordinate Edge Cases
| Condition | Current Handling | Risk Level |
|-----------|------------------|------------|
| Camera inverted (tl.x > br.x) | `min()`/`max()` handles this at lines 312-313 | Low |
| System at exact viewport boundary | Margin of 600 pixels provides buffer | Low |
| Zero hex_size | Would cause division issues in other code | Out of scope |

### 2.3 Zoom-Level Transitions
| Zoom Level | Behavior | Critical Threshold |
|------------|----------|-------------------|
| `< 0.5` | Shows colony markers, hides labels | Line 325 |
| `>= 0.5` | Shows star labels, calls `_draw_system_details` | Lines 369, 375-376 |

---

## 3. Invariants That Must Be Preserved

### 3.1 Rendering Order Invariants
1. **Colony markers render before stars** (at low zoom) - visual layering
2. **Selection highlight renders before star image** - ensures visibility
3. **`_draw_system_details` only called at zoom >= 0.5** - performance guard

### 3.2 Data Invariants
1. **`sys.primary_star` returns `sys.stars[0]` or None** - no star duplication
2. **Star color is always a 3-tuple (R, G, B)** - assumed by classification logic
3. **`star.diameter_hexes` is always positive** - used in radius calculation

### 3.3 Coordinate System Invariants
1. **Local star positions are relative to system origin** - `hx + local_pixel_x`
2. **World positions must go through `camera.world_to_screen`** for display
3. **Viewport culling uses world coordinates, not screen coordinates**

### 3.4 Selection State Invariant
1. **`self.scene.selected_object`** comparison uses object identity (`==`)
   - Must compare `sys` (the system), not individual stars
   - Selection highlight only for primary star when system is selected

---

## 4. Risk Areas for Refactoring

### 4.1 HIGH RISK: Star Color Classification Logic (Lines 344-353)

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

**Risks:**
- Order of conditions matters (if-elif chain)
- Thresholds are magic numbers with no documentation
- "Yellow" is implicit default - not explicitly checked
- Condition overlap: `(255, 200, 255)` would match 'white' not 'orange' due to elif order

**Refactoring approach:** Extract to `_classify_star_color(color) -> str` helper.

### 4.2 MEDIUM RISK: Selection Highlight Logic (Line 359)

```python
if self.scene.selected_object == sys and star == primary:
```

**Risks:**
- Dual condition: system must be selected AND star must be primary
- `selected_object` can be various types (Planet, Fleet, StarSystem, WarpPoint)
- Identity comparison could fail if objects are recreated

### 4.3 MEDIUM RISK: Zoom-Conditional Rendering

Multiple zoom checks create implicit state machine:
- Line 325: `zoom < 0.5` - colony markers
- Line 369: `zoom >= 0.5` - star labels
- Line 375: `zoom >= 0.5` - system details

**Risk:** Inconsistent zoom thresholds across refactored code.

### 4.4 LOW RISK: Screen Position Calculation (Line 342)

```python
star_screen_pos = self.camera.world_to_screen(
    pygame.math.Vector2(hx + local_pixel_x, hy + local_pixel_y)
)
```

**Risk:** Inline Vector2 construction could be extracted incorrectly.

---

## 5. Current Test Coverage Analysis

### 5.1 Existing Tests (from `test_strategy_renderer.py`)

| Test | Coverage |
|------|----------|
| `test_draw_systems_empty_galaxy` | Empty galaxy handling |
| `test_draw_systems_culls_offscreen` | Viewport culling |
| `test_draw_calls_draw_systems` | Method called from `draw()` |

### 5.2 MISSING Test Coverage (Must Add Before Refactoring)

#### Critical Missing Tests:

1. **Star color classification**
   - Red star: `color = (255, 50, 50)` -> `asset_key = 'red'`
   - Blue star: `color = (50, 50, 255)` -> `asset_key = 'blue'`
   - White star: `color = (255, 255, 255)` -> `asset_key = 'white'`
   - Orange star: `color = (255, 180, 50)` -> `asset_key = 'orange'`
   - Yellow star (default): `color = (255, 255, 100)` -> `asset_key = 'yellow'`
   - Edge case: `color = (210, 160, 50)` -> verify classification

2. **Colony marker rendering at low zoom**
   - System with owned planet, zoom < 0.5 -> marker drawn
   - System with owned planet, zoom >= 0.5 -> no marker
   - System with no owned planets -> no marker regardless of zoom

3. **Selection highlight**
   - Selected system with primary star -> highlight on primary
   - Selected system with multiple stars -> only primary highlighted
   - Selected planet (not system) -> no star highlight

4. **Star label rendering**
   - Primary star shows system name, not star name
   - Secondary stars show their own names
   - Labels only at zoom >= 0.5

5. **Fallback rendering when image missing**
   - `star_img` returns None -> circle drawn with `star.color`

6. **System with no primary star**
   - `sys.stars = []` -> no star rendering, still safe

7. **Multiple stars in system**
   - All stars rendered, each with correct position

---

## 6. Refactorability Assessment

### Is This Function Truly Refactorable?

**YES** - This function is refactorable. It is NOT an irreducibly complex rendering state machine.

### Justification:

1. **Clear decomposition points:**
   - Viewport culling (lines 308-320) - pure calculation
   - Colony marker rendering (lines 324-336) - self-contained
   - Star color classification (lines 344-353) - pure function candidate
   - Star rendering (lines 340-367) - could be `_render_star()`
   - Label rendering (lines 369-373) - could be combined with star rendering

2. **No genuine state machine:**
   - The zoom checks are simple conditionals, not state transitions
   - No accumulating state between iterations
   - Each system is rendered independently

3. **Testable units exist:**
   - Star color classification is pure (input RGB -> output asset key)
   - Viewport culling is pure (camera state + position -> boolean)

### Recommended Decomposition:

```
_draw_systems()
    |
    +-- _is_system_in_viewport(sys, min_x, max_x, min_y, max_y) -> bool
    |
    +-- _draw_colony_marker(screen, sys, world_pos)  [zoom < 0.5]
    |
    +-- _draw_system_stars(screen, sys, world_pos)
    |       |
    |       +-- _classify_star_color(color) -> str
    |       |
    |       +-- _draw_star(screen, star, screen_pos, is_primary, is_selected)
    |
    +-- _draw_system_details()  [existing, zoom >= 0.5]
```

---

## 7. Pre-Refactoring Checklist

- [ ] Add unit tests for star color classification (all 5 color categories)
- [ ] Add unit tests for colony marker visibility logic
- [ ] Add unit tests for star selection highlight logic
- [ ] Add integration test for multi-star system rendering
- [ ] Add test for fallback rendering when asset missing
- [ ] Verify zoom threshold constants are defined, not magic numbers
- [ ] Document color classification thresholds

---

## 8. Recommended Test File Structure

Create new test file: `tests/unit/ui/screens/test_strategy_renderer_draw_systems.py`

```python
class TestStarColorClassification:
    """Tests for star color -> asset key mapping."""
    pass

class TestColonyMarkerRendering:
    """Tests for colony marker visibility at different zoom levels."""
    pass

class TestStarSelectionHighlight:
    """Tests for selection highlight logic."""
    pass

class TestViewportCulling:
    """Tests for system viewport culling."""
    pass

class TestFallbackRendering:
    """Tests for fallback when assets missing."""
    pass
```

---

## 9. Summary

| Aspect | Assessment |
|--------|------------|
| Refactorability | **YES** - decomposable into smaller functions |
| Primary Risk | Star color classification logic (if-elif order) |
| Test Coverage Gap | **SIGNIFICANT** - color classification untested |
| Blocking Issues | None - can proceed after adding tests |
| Estimated Complexity Reduction | CC 14 -> CC 4-6 (with helper extractions) |
