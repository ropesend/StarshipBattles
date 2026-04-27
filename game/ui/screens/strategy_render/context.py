"""RenderContext + hex-radius math helper (PROJ-309 sub-phase 3.2).

The frozen ``RenderContext`` value-class threads per-frame derived state
through the layer functions. The composer (``StrategyRenderer``) builds it
once per frame; each layer reads it without writing back.

``hex_radius_to_screen`` is the BUG-94 power-curve scaling helper, shared
by stars, Dyson Spheres, and other multi-hex objects.
"""
from __future__ import annotations

import math


def hex_radius_to_screen(radius_hexes: float, hex_size: float, zoom: float) -> int:
    """Convert a hex-space radius to screen pixels using non-linear scaling.

    Uses a power curve anchored so that radius-2 matches the linear sqrt(3)
    formula exactly, while larger radii grow faster (reaching further into
    outer hex rings) and radius-1 grows slower (not overflowing center hex).

    BUG-94: linear sqrt(3) scaling is correct for radius-2 but undershoots
    large radii and overshoots radius-1.
    """
    if radius_hexes <= 0:
        return 3
    # Reference: radius-2 at hex_size=10, zoom=1 -> 34px
    # Exponent > 1 makes large radii grow faster, small radii slower
    _EXPONENT = 1.2
    # Base unit: screen distance for 1 hex ring
    hex_spacing = math.sqrt(3) * hex_size * zoom
    # Anchor at radius_hexes=2: result == 2 * hex_spacing (preserves current correct size)
    # General: result = 2 * hex_spacing * (radius_hexes / 2) ^ exponent
    return max(3, int(2 * hex_spacing * (radius_hexes / 2) ** _EXPONENT))
