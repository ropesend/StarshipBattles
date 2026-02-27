# Dependency Analysis: `_draw_systems`

**File:** `C:\Dev\Starship Battles\game\ui\screens\strategy_renderer.py`
**Function:** `StrategyRenderer._draw_systems`
**Lines:** 306-376 (71 lines)
**Cyclomatic Complexity:** 29 (Grade E)

---

## 1. Callers of `_draw_systems`

### Direct Callers

| Location | Caller | Call Site | Context |
|----------|--------|-----------|---------|
| `strategy_renderer.py:125` | `StrategyRenderer.draw()` | `self._draw_systems(screen)` | Main draw orchestrator |

### Call Chain
```
StrategyScreen.draw()
    └── StrategyRenderer.draw()           # line 108-143
            └── self._draw_systems(screen)  # line 125
```

**Only one caller exists:** The `draw()` method in the same class calls `_draw_systems` as part of the rendering pipeline:

```python
def draw(self, screen):
    """Main draw entry point for the galaxy map."""
    # ... viewport setup ...

    if self.camera.zoom >= 0.4:
        self._draw_grid(screen)

    self._draw_warp_lanes(screen)
    self._draw_systems(screen)      # <-- THE CALL
    self._draw_fleets(screen)

    # ... rest of draw ...
```

---

## 2. Parameters and Return Values

### Parameters
| Parameter | Type | Purpose |
|-----------|------|---------|
| `self` | `StrategyRenderer` | Instance providing access to scene, camera, galaxy, etc. |
| `screen` | `pygame.Surface` | The pygame surface to draw on |

### Return Value
- **None** - The function is purely side-effectful (draws to screen)

### Usage Pattern
The call is unconditional (no zoom threshold check for the call itself), though internal rendering has zoom-dependent behavior.

---

## 3. Interface Stability Analysis

### Can the Interface Change?

**YES - The interface can change** with these caveats:

1. **Private method (`_` prefix):** This is an internal implementation detail of `StrategyRenderer`. It is not part of the public API.

2. **Single caller:** Only `draw()` calls this method, and both are in the same class. Any signature change requires updating only one call site.

3. **No external consumers:** No external code imports or calls this method directly.

4. **Test implications:** Tests exist but use mocking:
   - `test_strategy_renderer.py` mocks `_draw_systems` to test `draw()` orchestration
   - Direct tests call `renderer._draw_systems(screen)` but only test edge cases (empty galaxy, culling)

### Recommended Approach
If refactoring splits functionality into helper methods, the interface can change freely. If extracting to separate classes/modules, consider:
- Keep internal helpers private
- Maintain the single `_draw_systems(screen)` entry point for minimal disruption

---

## 4. Side Effects and State Mutations

### Direct Side Effects

| Side Effect | Description |
|-------------|-------------|
| **Screen drawing** | Draws circles, images, and text to pygame surface via `pygame.draw.*` and `screen.blit()` |
| **Asset loading** | Loads star images via `self._asset_manager.load_image('stars', asset_key)` (cached) |
| **Font rendering** | Creates text surfaces via `font.render()` |
| **Image transformation** | Scales images via `pygame.transform.smoothscale()` |

### State Read (Not Mutated)

| State | Access Pattern |
|-------|----------------|
| `self.camera` | Reads `.zoom`, `.screen_to_world()`, `.world_to_screen()` |
| `self.galaxy.systems` | Iterates over systems dictionary |
| `self.empires` | Reads to find planet owners |
| `self.scene.selected_object` | Reads to draw selection highlight |
| `self.hex_size` | Reads for coordinate calculations |
| `self.screen_width`, `self.screen_height` | Reads for viewport bounds |

### State NOT Mutated
- No instance variables are modified
- No galaxy/system/planet state is changed
- Camera state is read-only
- This is a pure rendering function (read state, draw output)

### Sub-Method Calls
When `zoom >= 0.5`, calls:
```python
self._draw_system_details(screen, sys, world_pos)
```
Which in turn calls:
- `self._draw_storms()`
- `self._draw_dyson_spheres()`
- `self._draw_planet_sprite()` (via planet iteration)
- `self._draw_warp_point()`

---

## 5. Test Coverage

### Test Files
| File | Purpose |
|------|---------|
| `tests/unit/ui/screens/test_strategy_renderer.py` | Core renderer tests |
| `tests/unit/ui/screens/test_strategy_renderer_animation.py` | Animation/rotation tests |

### Direct Tests for `_draw_systems`

**`test_strategy_renderer.py::TestDrawSystems`** (lines 388-412):

1. **`test_draw_systems_empty_galaxy`**
   - Tests: Empty galaxy handling (no systems)
   - Asserts: No exception raised

2. **`test_draw_systems_culls_offscreen`**
   - Tests: Systems outside viewport are culled
   - Setup: Creates mock system at coordinates (10000, 10000)
   - Asserts: No exception raised (implicit culling test)

### Indirect Tests (via `draw()`)

**`test_strategy_renderer.py::TestDrawMethod`** (lines 183-297):

- `test_draw_calls_draw_systems` (line 229): Verifies `draw()` calls `_draw_systems` exactly once

### Coverage Gaps

| Gap | Impact | Recommendation |
|-----|--------|----------------|
| No test for star rendering logic | Star color mapping untested | Add parameterized tests for color->asset_key mapping |
| No test for colony marker drawing | Zoom < 0.5 behavior untested | Add tests for colony marker visibility |
| No test for selection highlight | Selected system highlight untested | Add test for `selected_object` handling |
| No test for star label rendering | Text positioning untested | Add visual regression or position tests |
| No integration test with real galaxy | Mock-only coverage | Consider integration test with minimal real galaxy |

### Test Quality Assessment

| Aspect | Rating | Notes |
|--------|--------|-------|
| **Edge cases** | Good | Empty galaxy and culling tested |
| **Happy path** | Poor | No test verifies actual drawing calls |
| **Integration** | None | All tests use mocks |
| **Visual correctness** | None | No visual regression tests |

---

## 6. Complexity Breakdown

The CC of 29 comes from these decision points in `_draw_systems`:

| Line Range | Logic | Estimated CC Contribution |
|------------|-------|---------------------------|
| 315-320 | System loop + viewport culling | 3 |
| 325-336 | Colony marker (zoom < 0.5, owned planets, owner exists) | 5 |
| 339-367 | Star rendering (primary exists, loop, color conditions, image exists) | 12 |
| 369-373 | Label rendering (zoom check, primary check) | 3 |
| 375-376 | System details delegation | 1 |

**Primary complexity drivers:**
1. Star color-to-asset-key mapping (5 color conditions)
2. Nested conditionals for ownership/selection state
3. Multiple zoom threshold checks

---

## 7. Refactoring Implications

### Safe Extraction Candidates

1. **Colony marker rendering** (lines 324-336)
   - Self-contained block
   - Clear inputs: `sys`, `world_pos`, `screen`
   - Can become `_draw_colony_marker(screen, sys, world_pos)`

2. **Star color mapping** (lines 344-353)
   - Pure function candidate
   - Input: `star.color` (RGB tuple)
   - Output: `asset_key` string
   - Can become `_get_star_asset_key(color) -> str`

3. **Individual star rendering** (lines 340-373)
   - Loop body is substantial
   - Can become `_draw_star(screen, star, sys, hx, hy)`

### Preserving Behavior

- Viewport culling MUST be preserved (performance critical)
- Zoom thresholds (0.5 for details/labels) are intentional
- Draw order matters: colony markers before stars, stars before labels

### Recommended Extraction Order

1. Extract `_get_star_asset_key(color)` - zero risk, pure function
2. Extract `_draw_colony_marker(screen, sys, world_pos)` - self-contained
3. Extract `_draw_star(screen, star, sys, hx, hy)` - largest reduction

Expected CC reduction: 29 -> ~7-10 in main function

---

## 8. Summary

| Aspect | Finding |
|--------|---------|
| **Callers** | Single caller: `draw()` at line 125 |
| **Interface** | Can change freely (private method, single internal caller) |
| **Side effects** | Drawing only - no state mutation |
| **Test coverage** | Basic edge cases tested, no happy path validation |
| **Refactoring risk** | LOW - well-isolated, no external dependencies |
| **CC reduction potential** | HIGH - clear extraction candidates exist |
