# PROJ-73: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Initial Analysis

### Test Baseline
- **Result:** 6630 passed, 1 failed (pre-existing failure in `test_protocols.py`)
- **Pre-existing issue:** `test_mock_with_fleet_spec_satisfies_ifleet` - unrelated to this project

### Warp Point Rendering - Current State
**File:** `game/ui/screens/strategy_renderer.py` lines 454-470

Current implementation:
1. Iterates over `sys.warp_points` for each star system
2. Uses `hash(wp)` as seed for deterministic image selection (3 images available)
3. Scales image based on camera zoom: `size = int(12 * self.camera.zoom)`
4. Applies `smoothscale` then blits with `pygame.BLEND_ADD` (additive glow)
5. **No rotation currently applied**

```python
for i, wp in enumerate(sys.warp_points):
    # ... coordinate conversion ...
    img = self._asset_manager.get_random_from_group('warp_points', 'default', seed_id=hash(wp))
    if img:
        size = int(12 * self.camera.zoom)
        scaled = pygame.transform.smoothscale(img, (size, size))
        dest = scaled.get_rect(center=(int(w_screen.x), int(w_screen.y)))
        screen.blit(scaled, dest, special_flags=pygame.BLEND_ADD)
```

### Warp Point Assets
**Location:** `assets/Images/Stellar Objects/Warp Points/`
- `Warp_Point_1.jpg`, `Warp_Point_2.jpg`, `Warp_Point_3.jpg`
- Also available as `.png` formats
- Loaded via `AssetManager.get_random_from_group()` with deterministic seed

### Animation Infrastructure
**Pattern Reference:** `game/ui/renderer/camera.py` lines 40-53

The codebase uses `update(dt)` pattern for frame-rate independent animation:
```python
def update(self, dt):
    if abs(self.zoom - self.target_zoom) > 0.001:
        self.zoom += (self.target_zoom - self.zoom) * min(1.0, self.zoom_speed * dt)
```

**All UI screens have `update(dt)` methods:**
- `strategy_screen.py` line 176: `def update(self, dt):`
- Currently calls `camera.update(dt)` and `ui.update(dt)`
- **Renderer does NOT have an update method** (gap to fill)

### Rotation Utility
**File:** `game/ui/utils.py` lines 66-94

`scale_and_rotate_image(image, scale_factor, rotation)` already exists:
- Takes rotation in degrees
- Applies scale first, then rotation (correct order)
- Used by ship rendering in `game_renderer.py`

---

## Swarm Findings Summary

### Architecture
- StrategyRenderer is a pure rendering class with no update state
- Receives scene reference in constructor, delegates to scene for all state
- Clean separation: renderer draws, scene manages state
- Adding `_elapsed_time` state to renderer is appropriate for render-only animation

### Key Patterns to Reuse
- **Camera Animation**: `camera.py:40-43` - Exponential interpolation for smooth animation
- **Rotation Utility**: `ui/utils.py:66-94` - `scale_and_rotate_image()` for scale+rotate
- **Hash for Variety**: `strategy_renderer.py:462` - `hash(wp)` for per-object variation

### Dependencies & Risks
1. **Performance** - Rotation is CPU-bound but cheap. With 5-20 warp points visible, impact is negligible
2. **No risks identified** - This is an additive change with no side effects

### Opportunities Discovered
- Could add rotation direction variation: `(hash(wp) % 2) * 2 - 1` as multiplier
- Could add pulsing/oscillation effects in future
- Could make rotation speed configurable

---

## Design Decisions

See [decisions.md](decisions.md) for the full log with rationale.

**Key Decisions:**
1. Rotation speed: 12 deg/sec (full rotation in 30 seconds)
2. Unique offsets via `hash(wp) % 360`
3. Track elapsed time in StrategyRenderer
4. Use existing `scale_and_rotate_image()` utility
