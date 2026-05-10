# Dependency Analysis: `_draw_systems` Method

## Overview

This document analyzes all callers, dependencies, and test coverage for the `StrategyRenderer._draw_systems` method located at `game/ui/screens/strategy_renderer.py:306`.

---

## 1. Callers of `_draw_systems`

### Direct Callers

| Location | Caller | Context |
|----------|--------|---------|
| `strategy_renderer.py:125` | `StrategyRenderer.draw()` | Called unconditionally as part of main render loop |

### Call Pattern

```python
# strategy_renderer.py:108-127 (draw method)
def draw(self, screen):
    """Main draw entry point for the galaxy map."""
    viewport_w = self.screen_width - self.SIDEBAR_WIDTH
    viewport_h = self.screen_height - self.TOP_BAR_HEIGHT
    # ... viewport setup ...

    # Draw Galaxy Elements (Clipped)
    if self.camera.zoom >= 0.4:
        self._draw_grid(screen)

    self._draw_warp_lanes(screen)
    self._draw_systems(screen)  # <-- ALWAYS CALLED
    self._draw_fleets(screen)
    # ...
```

### Parameters Passed

- **`screen`**: A `pygame.Surface` object for drawing
- No other parameters - all data accessed via `self` properties

### Return Value

- **None** - The method is purely side-effectful (draws to screen)
- No callers use a return value

---

## 2. Imports and External Dependencies of `StrategyRenderer`

### Module Imports (strategy_renderer.py)

| Import | Usage |
|--------|-------|
| `pygame` | All rendering (Surface, Rect, draw operations) |
| `game.ui.config.UIConfig` | Sidebar width constant |
| `game.core.hex_math` | `hex_to_pixel`, `pixel_to_hex`, `HexCoord` |
| `game.strategy.data.fleet.OrderType` | Move preview styling |
| `game.strategy.data.planet.PlanetType` | Dyson Sphere detection |
| `game.ui.colors` | All color constants |
| `game.ui.utils` | `scale_and_rotate_image` |
| `game.ui.fonts` | `get_font` |

### Callers of `StrategyRenderer` Class

| Location | Usage |
|----------|-------|
| `strategy_screen.py:35` | `from game.ui.screens.strategy_renderer import StrategyRenderer` |
| `strategy_screen.py:120` | `self._renderer = StrategyRenderer(self)` |

The `StrategyRenderer` is **only** instantiated by `StrategyScreen` and passed `self` as the scene reference.

---

## 3. Interface Stability Analysis

### Can the interface change?

**YES, the interface can change** with the following considerations:

1. **Method is private** (prefixed with `_`)
   - Not part of the public API
   - Only called internally within `StrategyRenderer.draw()`

2. **Single caller site**
   - Only called from one location (`draw()` method, line 125)
   - Easy to update call site if signature changes

3. **No external callers**
   - Not imported or called from other modules
   - Test mocks the method but doesn't call it directly with specific parameters

### Recommended Approach

Since `_draw_systems` is:
- Private (underscore prefix)
- Called only internally
- Only from a single location

**The interface can be freely modified** as long as the single call site in `draw()` is updated accordingly.

---

## 4. Side Effects and State Mutations

### Direct Side Effects

| Effect | Description |
|--------|-------------|
| **Screen Drawing** | Draws stars, system labels, and colony markers to `screen` surface |
| **Camera Access** | Reads `self.camera.zoom`, `screen_to_world()`, `world_to_screen()` |
| **Asset Loading** | Calls `self._asset_manager.load_image()` for star sprites |

### Indirect Side Effects (via delegated methods)

| Method Called | Side Effects |
|---------------|--------------|
| `_draw_system_details()` | Draws planets, warp points, storms, Dyson spheres |
| `_draw_dyson_spheres()` | Draws Dyson sphere planets with owner markers |
| `_draw_storms()` | Draws storm overlays for systems |
| `_draw_planet_sprite()` | Draws planet sprites with colony flags |

### State Mutations

| Mutation | Location | Description |
|----------|----------|-------------|
| `p._temp_screen_pos` | `_draw_system_details:462` | Temporary position on planet objects |
| `p._temp_draw_r` | `_draw_system_details:463` | Temporary radius on planet objects |

**Note:** These are temporary attributes added to planet objects during rendering. This is a code smell but does not affect external state.

### Read-Only Access

The method reads but does not modify:
- `self.galaxy.systems` (dict of star systems)
- `self.camera` (position, zoom)
- `self.empires` (list of empires for colony colors)
- `self.scene.selected_object` (for selection highlighting)
- `self.hex_size` (coordinate conversion)

---

## 5. Test Coverage

### Test File Location

`tests/unit/ui/screens/test_strategy_renderer.py`

### Test Classes Covering `_draw_systems`

| Test Class | Coverage |
|------------|----------|
| `TestDrawSystems` | Direct tests for `_draw_systems` |
| `TestDrawMethod` | Tests that `draw()` calls `_draw_systems` |

### Specific Test Cases

#### Direct Tests (TestDrawSystems class, lines 388-412)

```python
def test_draw_systems_empty_galaxy(self, renderer, mock_scene):
    """_draw_systems should handle empty galaxy."""
    screen = MagicMock()
    mock_scene.galaxy.systems = {}
    renderer._draw_systems(screen)  # Should not raise

def test_draw_systems_culls_offscreen(self, renderer, mock_scene):
    """_draw_systems should cull systems outside viewport."""
    # Creates a system far outside viewport (q=10000, r=10000)
    # Verifies no exceptions raised
```

#### Integration Tests (TestDrawMethod class, line 229)

```python
def test_draw_calls_draw_systems(self, renderer, mock_scene):
    """draw() should call _draw_systems."""
    screen = MagicMock()
    self._mock_draw_methods(renderer)
    with patch('pygame.draw.rect'):
        renderer.draw(screen)
    renderer._draw_systems.assert_called_once()
```

### Test Coverage Summary

| Aspect | Coverage |
|--------|----------|
| Empty galaxy handling | Covered |
| Off-screen culling | Covered |
| Integration with `draw()` | Covered |
| Star rendering | Not directly tested |
| Colony markers | Not directly tested |
| System labels | Not directly tested |
| Detailed rendering (`_draw_system_details`) | Not directly tested |

### Test Strategy for Refactoring

1. **Existing tests will verify no regressions** at the integration level
2. **Mock-level tests** verify call relationships
3. **New helper methods** extracted from `_draw_systems` should have their own tests
4. The existing test pattern uses `MagicMock` for dependencies, allowing safe refactoring

---

## 6. Method Complexity Breakdown

The `_draw_systems` method (lines 306-376) contains:

### Complexity Contributors

| Pattern | Count | Description |
|---------|-------|-------------|
| `for` loops | 2 | Galaxy systems iteration, stars iteration |
| `if` conditions | 11+ | Viewport culling, zoom checks, color detection, selection |
| Nested conditions | Several | Star color detection, label visibility |

### Extractable Units

Based on the code structure, these are candidates for extraction:

1. **Viewport culling** (lines 308-313) - Calculate visible bounds
2. **Colony marker rendering** (lines 324-336) - Zoomed-out colony indicators
3. **Star asset key resolution** (lines 344-354) - Color-to-asset mapping
4. **Star rendering** (lines 338-373) - Individual star sprite + label
5. **System label rendering** (lines 369-373) - Font and positioning

---

## 7. Summary

### Key Findings

| Aspect | Finding |
|--------|---------|
| **Callers** | Single internal caller (`draw()` method) |
| **Interface** | Private method, can be freely modified |
| **Parameters** | Single `screen` parameter (pygame Surface) |
| **Return value** | None (side-effect only) |
| **Side effects** | Screen drawing only |
| **State mutations** | Temporary `_temp_*` attributes on planets (via helper) |
| **Test coverage** | Integration-level coverage, no direct visual tests |

### Refactoring Safety

**Safe to refactor** - The method is:
- Private (underscore prefix)
- Single call site
- No return value dependencies
- Covered by integration tests
- Read-only access to game state (no mutations)

### Recommended Approach

1. Extract helper methods for complex conditional blocks
2. Keep the same signature (`def _draw_systems(self, screen)`)
3. New helpers should follow the `_draw_*` naming convention
4. Add unit tests for extracted helpers
5. Run existing test suite to verify no regressions
