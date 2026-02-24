# PROJ-168: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Initial Analysis

### The Duplication
Five files implement the same hex-axial-to-Cartesian conversion:
```python
dq = q - center_q
dr = r - center_r
x = dq + dr * 0.5
y = dr * math.sqrt(3.0) / 2.0
```

One site (region_classifier.py) uses a hardcoded constant `0.8660254037844386` instead of `math.sqrt(3.0) / 2.0`. Both are numerically equivalent.

### Existing Infrastructure
`game/core/hex_math.py` already provides `hex_to_pixel()` which does a *different* conversion — it maps axial coords to flat-topped pixel coordinates with a size scaling factor. The density primitives need a simpler "axial to raw Cartesian" conversion without pixel scaling.

### Call Sites (5 duplications)
1. `spiral_arm.py:55-58` — Standard pattern (dq, dr, x, y)
2. `linear.py:53-55` — Standard pattern
3. `geometric.py:56-58` — Standard pattern
4. `noise.py:93-94` — Variant: incorporates offset and scale inline
5. `region_classifier.py:177-178` — Variant: uses hardcoded constant

## Design Decisions

### Function Placement: `game/core/hex_math.py`
The function belongs in the existing hex math module because:
- It's a pure geometric conversion (no domain logic)
- `hex_math.py` already has `hex_to_pixel()` which does a related conversion
- The density primitives and region classifier are in the strategy layer — they should import from core
- `region_classifier.py` already imports from `game.core.hex_math`

### Function Signature
```python
def hex_axial_to_cartesian(
    q: float, r: float,
    center_q: float = 0.0, center_r: float = 0.0
) -> Tuple[float, float]:
```

**Why float inputs (not int):** The callers pass integer hex coordinates, but making the signature accept float allows future flexibility and matches the center parameters which are float. No type coercion needed.

**Why center parameters with defaults:** 4 of 5 callers compute `dq = q - center; dr = r - center` before the conversion. Including center in the function signature eliminates this repeated boilerplate.

### noise.py Special Case
noise.py's pattern is:
```python
x = (q + offset_q + (r + offset_r) * 0.5) / scale
y = ((r + offset_r) * sqrt(3)/2) / scale
```

This is mathematically equivalent to:
```python
x, y = hex_axial_to_cartesian(q, r, -offset_q, -offset_r)
x /= scale
y /= scale
```

The scale division is a separate concern (noise frequency) and stays at the call site.

## Dependencies & Risks
1. **Numerical precision** — The hardcoded constant `0.8660254037844386` and `math.sqrt(3.0) / 2.0` produce identical IEEE 754 results. No precision change expected. Test validates this.
2. **Performance** — Function call overhead is negligible compared to the density field evaluation these sites do. Each primitive is called thousands of times during galaxy generation, but the conversion is a trivial arithmetic operation.

## Key Patterns to Reuse
- **Test pattern**: `test_hex_math_core.py` uses focused test classes per function with clear docstrings. Follow this pattern.
- **Import pattern**: Density primitives import from `game.strategy.generation.density.primitives.density_primitive`. Region classifier already imports from `game.core.hex_math`.
