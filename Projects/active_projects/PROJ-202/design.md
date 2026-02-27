# PROJ-202: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Initial Analysis

Target function: `StrategyRenderer._draw_systems()` at `game/ui/screens/strategy_renderer.py:306-376`
- Cyclomatic Complexity: 29 (Grade E)
- Length: 71 lines
- Purpose: Renders star systems on the galaxy map including stars, colony markers, labels, and selection highlights

## Swarm Findings Summary

Combined analysis from 3 parallel review agents examining structure, dependencies, and safety.

### Architecture

**Call Chain:**
```
StrategyScreen.draw()
    └── StrategyRenderer.draw()           # line 108
            └── self._draw_systems(screen)  # line 125
                    └── self._draw_system_details()  # line 376 (zoom >= 0.5)
```

**Data Flow:**
- Reads: `self.camera`, `self.galaxy.systems`, `self.empires`, `self.scene.selected_object`
- Writes: pygame screen surface (drawing calls only)
- No state mutations - pure rendering function

**Complexity Distribution:**
| Component | Lines | CC Contribution |
|-----------|-------|-----------------|
| System loop + culling | 315-320 | 3 |
| Colony marker (nested) | 325-336 | 5 |
| Star color classification | 344-353 | 5 |
| Star rendering | 339-367 | 7 |
| Label + detail delegation | 369-376 | 4 |

### Key Patterns to Reuse

- **Viewport Culling**: `strategy_renderer.py:308-320` - Calculate world bounds and skip off-screen systems
- **World-to-Screen Conversion**: `camera.world_to_screen(world_pos)` - Standard coordinate transform
- **Image-or-Fallback Rendering**: `strategy_renderer.py:362-367` - Try image, fallback to primitive

### Dependencies & Risks

1. **Star Color Classification Order** - The if-elif chain at lines 344-353 is order-dependent. "White" must come before "orange" to avoid misclassification of high RGB values. Mitigation: Preserve exact condition order in extracted function.

2. **Selection Highlight Logic** - Line 359 requires both `selected_object == sys` AND `star == primary`. Easy to break by extracting incorrectly. Mitigation: Keep this logic inline within star rendering helper.

3. **Zoom Thresholds** - Magic number 0.5 appears 3 times with consistent meaning. Mitigation: Extract to named constant `ZOOM_DETAIL_THRESHOLD`.

4. **No Test Coverage for Color Classification** - Most risky code path has zero tests. Mitigation: Phase 1 adds comprehensive tests BEFORE any refactoring.

### Opportunities Discovered

- **Pure Function Extraction**: `_classify_star_color(color)` is a pure function with no dependencies - ideal extraction candidate
- **Guard Clause Simplification**: Colony marker logic has 3 nested ifs that can become 3 early returns
- **Potential Future Consolidation**: `_draw_system_details` (CC 24) and `_draw_storms` (CC 23) in same file could benefit from similar treatment in future projects

## Design Decisions

### Extraction Strategy

1. **`_classify_star_color(color: tuple) -> str`**
   - Static method (no self needed)
   - Pure function - easiest to test, zero risk
   - Reduces CC by 5

2. **`_draw_colony_marker_if_zoomed_out(screen, sys, world_pos)`**
   - Instance method (needs self.camera, self.empires, self.hex_size)
   - Uses early returns to flatten nested conditionals
   - Reduces CC by 4-5

3. **`_draw_system_stars(screen, sys, hx, hy)`**
   - Instance method (needs self.camera, self.scene, self.hex_size, etc.)
   - Contains star loop, color classification call, image/fallback, labels
   - Reduces CC by 10-12

### Expected Final State

**`_draw_systems` after refactoring (~10 lines):**
```python
def _draw_systems(self, screen):
    # Viewport bounds
    # ...
    for sys in self.galaxy.systems.values():
        # Culling check (1 branch)
        if not in_viewport: continue

        # Delegate to helpers
        self._draw_colony_marker_if_zoomed_out(screen, sys, world_pos)
        self._draw_system_stars(screen, sys, hx, hy)

        if self.camera.zoom >= ZOOM_DETAIL_THRESHOLD:  # 1 branch
            self._draw_system_details(screen, sys, world_pos)
```

**Expected CC: 4-6** (down from 29)

See [decisions.md](decisions.md) for the full log with rationale.
