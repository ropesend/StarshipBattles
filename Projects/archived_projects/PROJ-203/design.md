# PROJ-203: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Initial Analysis

**Target**: `StrategyRenderer._draw_systems` (lines 306-376)
**Current CC**: 29 (Grade E)
**Goal**: Reduce to below CC 20

The function renders all star systems on the strategy map, handling:
- Viewport culling for performance
- Colony markers at low zoom
- Star rendering with color-based asset selection
- Selection highlights
- System detail delegation at high zoom

## Swarm Findings Summary

Combined analysis from 3 parallel review agents in `findings/`.

### Architecture

1. **Single Call Site**: `_draw_systems` is only called from `draw()` method at line 125
2. **Private Method**: Safe to modify interface (underscore prefix)
3. **Side-Effect Only**: No return value, draws to pygame Surface
4. **Read-Only State**: Reads camera, galaxy, empires but makes no mutations

### Key Patterns to Reuse

- **Early Continue Pattern**: `strategy_renderer.py:319-320` - Good viewport culling guard
- **Fallback Pattern**: `strategy_renderer.py:362-367` - Image fallback to circle draw
- **Color Mapping Tests**: `test_star_color_mapping.py` - Comprehensive threshold boundary tests

### Dependencies & Risks

1. **Star Color Evaluation Order** - The if/elif chain (lines 344-353) has overlapping conditions. White check must come before orange check. CRITICAL: Preserve exact order when extracting.

2. **Zoom Threshold Semantics** - Three locations use 0.5:
   - `< 0.5` for colony markers (line 325)
   - `>= 0.5` for labels (line 369)
   - `>= 0.5` for details (line 375)
   Operators must be preserved exactly.

3. **Coordinate Conversion Chain** - hex -> world -> screen conversion must remain consistent. Any extraction must clearly document coordinate space.

4. **Colony Marker Owner Selection** - Uses first owned planet's owner (line 328). Changing this is a behavioral change, not refactoring.

### Opportunities Discovered

- Pure function extraction for color mapping (zero dependencies, easily testable)
- Clear guard clause pattern for colony marker extraction
- Star rendering is self-contained per star (no cross-star dependencies)

## Design Decisions

See [decisions.md](decisions.md) for the full log with rationale.

---

## Extraction Specifications

### Extraction 1: `_get_star_asset_key(color)`

**Source**: Lines 344-354
**Type**: Pure function
**Signature**: `_get_star_asset_key(self, color: tuple) -> str`

Extracts the 5-branch color classification chain. Returns one of: 'yellow', 'red', 'blue', 'white', 'orange'.

**CC Impact**: -4 (removes 4 elif branches from main function)

### Extraction 2: `_draw_colony_marker(screen, sys, world_pos)`

**Source**: Lines 325-336
**Type**: Side-effect method (draws to screen)
**Signature**: `_draw_colony_marker(self, screen, sys, world_pos)`

Extracts the 3-level nested block that draws ownership markers at low zoom. Uses early returns to flatten nesting.

**CC Impact**: -3

### Extraction 3: `_draw_star(screen, star, ...)`

**Source**: Lines 340-373 (per-star portion of loop)
**Type**: Side-effect method (draws to screen)
**Signature**: `_draw_star(self, screen, star, system_center, system_name, is_primary, is_selected_system)`

Extracts individual star rendering including:
- Position calculation (local coordinates)
- Color-to-asset mapping (calls `_get_star_asset_key`)
- Selection highlight
- Image or fallback circle
- Label rendering

**CC Impact**: -6

---

## Expected Outcome

| Metric | Before | After |
|--------|--------|-------|
| Cyclomatic Complexity | 29 | 16-18 |
| Lines in `_draw_systems` | 71 | ~25 |
| Nesting Depth | 4 | 2 |
| New Methods | 0 | 3 |

## Verification Commands

```bash
# Run unit tests
pytest tests/unit/ui/screens/test_strategy_renderer.py -v

# Run star color tests
pytest tests/unit/ui/test_star_color_mapping.py -v

# Measure complexity
radon cc game/ui/screens/strategy_renderer.py -a -s

# Full test suite
pytest tests/ -n 12
```
