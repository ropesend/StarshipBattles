# Safety Analysis: _draw_systems (CC 29)

## Function Overview

**File:** `game/ui/screens/strategy_renderer.py`
**Function:** `StrategyRenderer._draw_systems(self, screen)` (lines 306-376)
**Cyclomatic Complexity:** 29 (Grade E)
**Length:** ~71 lines

### Purpose
Draws all star systems on the strategy map, including:
- Viewport culling for performance
- Colony markers at low zoom
- Star rendering with color-based asset selection
- Selection highlights
- System detail delegation at high zoom

---

## 1. Edge Cases and Error Handling Paths

### 1.1 Viewport Culling (lines 308-320)
```python
tl = self.camera.screen_to_world((0, 0))
br = self.camera.screen_to_world((self.screen_width, self.screen_height))

margin = 600
min_x, max_x = min(tl.x, br.x) - margin, max(tl.x, br.x) + margin
min_y, max_y = min(tl.y, br.y) - margin, max(tl.y, br.y) + margin

for sys in self.galaxy.systems.values():
    # ...
    if not (min_x < world_pos.x < max_x and min_y < world_pos.y < max_y):
        continue
```
**Edge Cases:**
- Camera at extreme positions (very large x/y values)
- Negative camera positions
- Zero-sized viewport
- Empty galaxy (no systems)

**Risk Level:** LOW - Standard culling logic, well-understood behavior.

### 1.2 Empty Galaxy (line 315)
The loop `for sys in self.galaxy.systems.values()` handles empty galaxy gracefully by simply not iterating.

**Existing Test:**
```python
def test_draw_systems_empty_galaxy(self, renderer, mock_scene):
    """_draw_systems should handle empty galaxy."""
    screen = MagicMock()
    mock_scene.galaxy.systems = {}
    renderer._draw_systems(screen)  # Should not raise
```

### 1.3 Colony Marker at Low Zoom (lines 324-336)
```python
if self.camera.zoom < 0.5:
    owned_planets = [p for p in sys.planets if p.owner_id is not None]
    if owned_planets:
        first_owner_id = owned_planets[0].owner_id
        owner_emp = next((e for e in self.empires if e.id == first_owner_id), None)
        if owner_emp:
            # Draw marker...
```
**Edge Cases:**
- System with no planets
- System with planets but none owned
- Owned planet but empire not in empires list (orphaned owner_id)
- Multiple owners - only first owner's color used

**Risk Level:** MEDIUM - The `next(..., None)` fallback is safe, but behavior with orphaned owner_id is silent (no visual feedback).

### 1.4 Primary Star Check (line 338-339)
```python
primary = sys.primary_star
if primary:
```
**Edge Cases:**
- System with no stars (`primary_star` returns `None`)
- System with empty stars list

**Existing Test:**
```python
def test_draw_systems_culls_offscreen(self, renderer, mock_scene):
    mock_system.primary_star = None
    mock_system.stars = []
```

**Risk Level:** LOW - Properly guarded.

### 1.5 Star Color Classification (lines 344-354)
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
**Edge Cases:**
- Colors at exact threshold boundaries (200, 100, 150)
- None color (would crash)
- Short tuple (less than 3 elements)

**Existing Tests:** `test_star_color_mapping.py` has extensive threshold boundary tests.

**Risk Level:** MEDIUM - The `star.color` access assumes a valid 3-tuple. No explicit None check.

### 1.6 Star Image Fallback (lines 362-367)
```python
if star_img:
    scaled_img = pygame.transform.smoothscale(star_img, (screen_star_r * 2, screen_star_r * 2))
    dest_rect = scaled_img.get_rect(center=(...))
    screen.blit(scaled_img, dest_rect)
else:
    pygame.draw.circle(screen, color, star_screen_pos, screen_star_r)
```
**Edge Cases:**
- Asset manager returns None
- `screen_star_r` is 0 or negative (guarded by `max(3, ...)` on line 357)

**Risk Level:** LOW - Fallback properly implemented.

### 1.7 Selection Highlight (lines 359-360)
```python
if self.scene.selected_object == sys and star == primary:
    pygame.draw.circle(screen, WHITE, star_screen_pos, screen_star_r + 4, 1)
```
**Edge Cases:**
- `selected_object` is None
- `selected_object` is a different type (Planet, Fleet, etc.)

**Risk Level:** LOW - Direct equality comparison handles mismatched types.

### 1.8 Zoom-Based Detail Delegation (lines 375-376)
```python
if self.camera.zoom >= 0.5:
    self._draw_system_details(screen, sys, world_pos)
```
**Edge Cases:**
- Zoom exactly at 0.5 (included)
- Zoom just below 0.5 (excluded)

**Risk Level:** LOW - Simple threshold, well-defined behavior.

---

## 2. Invariants That Must Be Preserved

### 2.1 Rendering Order
1. Systems must be rendered BEFORE the zoom check delegates to details
2. Colony markers ONLY at low zoom (< 0.5)
3. Star labels ONLY at high zoom (>= 0.5)
4. Selection highlight drawn BEFORE star image

### 2.2 Visual Consistency
- **Star color mapping must remain deterministic** - Same RGB always maps to same asset key
- **Colony marker uses first owned planet's owner** - Changing this breaks visual expectations
- **Margin of 600 for culling** - Reducing this may cause pop-in artifacts

### 2.3 Coordinate System
- `hex_to_pixel()` with `self.hex_size` must be consistent throughout
- `world_to_screen()` conversion required before any screen drawing
- Local star coordinates are RELATIVE to system center

### 2.4 Performance Invariants
- Culling must happen BEFORE any expensive operations (asset loading, transforms)
- Empty galaxy must be O(1), not O(n)

---

## 3. Risk Areas Where Refactoring Could Introduce Bugs

### 3.1 HIGH RISK: Star Color Classification Logic
**Location:** Lines 344-354

The color classification uses magic numbers (100, 150, 200) with specific inequality operators (`>` vs `>=`). The evaluation ORDER matters because conditions overlap:
- White (220, 220, 220) also matches Orange condition
- The if/elif chain must preserve exact order

**Refactoring Risk:**
- Extracting to helper method: SAFE if conditions preserved exactly
- Converting to dict lookup: HIGH RISK - loses evaluation order
- Using match/case: HIGH RISK - may change semantics

**Mitigation:** The `test_star_color_mapping.py` tests are comprehensive and cover boundary cases. Run these after any refactor.

### 3.2 MEDIUM RISK: Colony Marker Owner Resolution
**Location:** Lines 326-336

```python
first_owner_id = owned_planets[0].owner_id
owner_emp = next((e for e in self.empires if e.id == first_owner_id), None)
```

**Refactoring Risk:**
- Changing `owned_planets[0]` to any other selection changes visual behavior
- The `next(..., None)` pattern must remain to handle orphaned owner_ids

**Mitigation:** Add test coverage before refactoring (see Section 4).

### 3.3 MEDIUM RISK: World/Screen Coordinate Mixing
**Location:** Throughout function

The function constantly converts between:
- Hex coordinates (`sys.global_location`, `star.location`)
- World pixel coordinates (`world_pos`, `hx + local_pixel_x`)
- Screen pixel coordinates (`screen_pos`, `star_screen_pos`)

**Refactoring Risk:**
- Extracting coordinate conversion could swap world/screen accidentally
- Moving code could break the chain of conversions

**Mitigation:** Any extracted helper must clearly document whether it returns world or screen coordinates.

### 3.4 LOW RISK: Zoom Threshold Consistency
**Location:** Lines 325, 369, 375

Multiple zoom thresholds used:
- `< 0.5` for colony markers
- `>= 0.5` for labels and details

**Refactoring Risk:** Creating a "zoom level" enum or constant could accidentally change threshold semantics.

**Mitigation:** If extracting thresholds, ensure exact values and operators are preserved.

---

## 4. Missing Test Coverage That Should Be Added BEFORE Refactoring

### 4.1 CRITICAL: Colony Marker Edge Cases
**Current Coverage:** None found in test files

**Tests Needed:**
```python
def test_draw_systems_colony_marker_at_low_zoom():
    """Colony marker should appear when zoom < 0.5 and planet owned."""

def test_draw_systems_no_colony_marker_at_high_zoom():
    """Colony marker should NOT appear when zoom >= 0.5."""

def test_draw_systems_colony_marker_uses_first_owner():
    """When multiple planets owned by different empires, use first owner's color."""

def test_draw_systems_colony_marker_orphaned_owner():
    """When planet.owner_id not in empires list, skip marker gracefully."""
```

### 4.2 CRITICAL: Star Rendering Edge Cases
**Current Coverage:** Partial (color mapping tested separately, not integrated)

**Tests Needed:**
```python
def test_draw_systems_star_with_none_image():
    """When asset manager returns None, fallback circle should be drawn."""

def test_draw_systems_star_screen_radius_minimum():
    """Star radius should never be less than 3 pixels."""

def test_draw_systems_star_selection_highlight():
    """Selected system's primary star should have white outline."""
```

### 4.3 HIGH: Viewport Culling
**Current Coverage:** Basic test exists but doesn't verify culling correctness

**Tests Needed:**
```python
def test_draw_systems_culls_far_offscreen_system():
    """Systems > 600 units outside viewport should not be rendered."""

def test_draw_systems_renders_near_edge_system():
    """Systems within 600 units of viewport edge should be rendered."""

def test_draw_systems_margin_prevents_popin():
    """Verify 600 margin is sufficient for largest star diameter."""
```

### 4.4 MEDIUM: System Detail Delegation
**Current Coverage:** None for the conditional delegation

**Tests Needed:**
```python
def test_draw_systems_delegates_to_draw_system_details_at_high_zoom():
    """_draw_system_details should be called when zoom >= 0.5."""

def test_draw_systems_skips_details_at_low_zoom():
    """_draw_system_details should NOT be called when zoom < 0.5."""
```

---

## 5. Refactorability Assessment

### 5.1 Complexity Breakdown
The CC of 29 comes from:
- 1 for function entry
- 1 for galaxy systems loop
- 1 for viewport culling condition
- 1 for zoom < 0.5 condition (colony marker)
- 1 for owned_planets check
- 1 for owner_emp check
- 1 for primary star check
- 1 for stars loop
- 5 for color classification chain (5 conditions)
- 1 for selection highlight condition
- 1 for star_img check
- 1 for zoom >= 0.5 (labels)
- 1 for star == primary label condition
- 1 for zoom >= 0.5 (details)
- Plus nested conditions contributing to complexity

### 5.2 Recommended Extraction Strategy

**Phase 1: Extract Star Color Classification (SAFE)**
```python
def _get_star_asset_key(self, star_color: tuple) -> str:
    """Map star RGB color to asset key."""
    r, g, b = star_color
    if r > 200 and g < 100:
        return 'red'
    if b > 200 and r < 100:
        return 'blue'
    if r > 200 and g > 200 and b > 200:
        return 'white'
    if r > 200 and g > 150:
        return 'orange'
    return 'yellow'
```
**Expected CC Reduction:** -4 (removes 5 conditions from main function)

**Phase 2: Extract Colony Marker Drawing (SAFE)**
```python
def _draw_colony_marker_if_needed(self, screen, sys, world_pos):
    """Draw colony ownership marker at low zoom levels."""
    if self.camera.zoom >= 0.5:
        return
    owned_planets = [p for p in sys.planets if p.owner_id is not None]
    if not owned_planets:
        return
    # ... marker drawing logic
```
**Expected CC Reduction:** -3

**Phase 3: Extract Single Star Rendering (MODERATE RISK)**
```python
def _draw_star(self, screen, star, system_world_pos, is_primary, is_selected):
    """Render a single star with selection highlight and label."""
```
**Expected CC Reduction:** -5 to -7

### 5.3 Final Verdict

| Aspect | Assessment |
|--------|------------|
| **Is refactorable?** | YES |
| **Recommended approach** | Extract helper methods in phases |
| **Expected final CC** | 10-15 (acceptable) |
| **Pre-requisites** | Add missing tests from Section 4 |
| **Risk level** | MEDIUM - requires careful test verification |

### 5.4 Should This Be Skipped?

**NO** - This function is a good candidate for refactoring because:
1. Clear, extractable sub-responsibilities
2. Existing test infrastructure for critical paths (star colors)
3. No irreducible complexity (all branches are separable)
4. Visual output makes regression detection possible

However, refactoring should be DEFERRED until:
- [ ] Missing tests from Section 4 are added
- [ ] Tests pass on current implementation
- [ ] Each extraction phase is verified before next

---

## 6. Summary of Recommendations

### Before Refactoring
1. Add colony marker tests (4 tests)
2. Add star rendering edge case tests (3 tests)
3. Add viewport culling verification tests (3 tests)
4. Add detail delegation tests (2 tests)

### During Refactoring
1. Extract star color classification first (lowest risk)
2. Run full test suite after each extraction
3. Verify visual output manually for each phase
4. Keep extracted methods private (`_` prefix)

### After Refactoring
1. Verify final CC is below 20
2. Run full test suite
3. Visual smoke test at multiple zoom levels
4. Document any threshold values in constants
