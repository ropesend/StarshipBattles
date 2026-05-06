"""Pure-math spectral helpers.

PROJ-372 extracted these from ``game/strategy/data/stars.py`` because
they are physics / math primitives with zero domain knowledge —
``core/`` is the architectural home (mirrors PROJ-257's placement of
``FormulaEvaluator`` here).

Used today by:
- ``game/strategy/generation/star_generator.py`` (PROJ-372 Phase 1)

Future spectral consumers should import from this module rather than
from ``stars.py``.
"""
from __future__ import annotations

import math
from typing import Tuple


__all__ = [
    "SOLAR_MASS_KG",
    "SOLAR_RADIUS_M",
    "SOLAR_LUMINOSITY_W",
    "SOLAR_TEMP_K",
    "WIEN_DISPLACEMENT_CONSTANT",
    "kelvin_to_rgb",
    "stefan_boltzmann_luminosity",
    "wien_peak_wavelength",
]


# Solar reference constants
SOLAR_MASS_KG = 1.989e30
SOLAR_RADIUS_M = 6.957e8
SOLAR_LUMINOSITY_W = 3.828e26
SOLAR_TEMP_K = 5778

# Kelvin-to-RGB approximation coefficients (Tanner Helland's algorithm).
# Source: tannerhelland.com/2012/09/18/convert-temperature-rgb-algorithm-code
_KELVIN_RED_COEFF = 329.698727446
_KELVIN_RED_EXP = -0.1332047592
_KELVIN_GREEN_LOW_COEFF = 99.4708025861
_KELVIN_GREEN_LOW_OFFSET = -161.1195681661
_KELVIN_GREEN_HIGH_COEFF = 288.1221695283
_KELVIN_GREEN_HIGH_EXP = -0.0755148492
_KELVIN_BLUE_COEFF = 138.5177312231
_KELVIN_BLUE_OFFSET = -305.0447927307
_KELVIN_WARM_COOL_BOUNDARY = 66   # temp/100 dividing warm and cool formulas
_KELVIN_BLUE_FLOOR = 19           # temp/100 below which blue channel = 0

# Wien's displacement law constant (meters * Kelvin)
WIEN_DISPLACEMENT_CONSTANT = 2.898e-3

# Spectrum-band intensity model parameters (used by StarGenerator).
_SPECTRUM_SIGMA = 0.5             # log-gaussian width for Planck approximation
_SPECTRUM_JITTER_RANGE = (0.9, 1.1)

# Representative wavelengths (meters) for 9-band spectrum model.
_WAVELENGTHS = {
    "gamma": 1e-12, "xray": 1e-9, "uv": 1e-7,
    "blue": 4.5e-7, "green": 5.5e-7, "red": 6.5e-7,
    "ir": 1e-5, "microwave": 1e-2, "radio": 10,
}

# Hex-radius mapping coefficients (solar radii -> hex radius 1-6).
# Used by StarGenerator._map_solar_radius_to_hex_radius. Decision D6
# keeps the mapping function in star_generator.py (game design choice),
# but the constants are pure-math thresholds and may live here.
_HEX_RADIUS_LOG_COEFF = 1.73
_HEX_RADIUS_LOG_OFFSET = 0.8
_HEX_RADIUS_MIN = 1
_HEX_RADIUS_MAX = 6


def kelvin_to_rgb(temp_k: float) -> Tuple[int, int, int]:
    """Approximate sRGB triple for a black-body temperature in Kelvin.

    Tanner Helland's algorithm — well-known piecewise-fit approximation
    that produces visually-plausible star colors.

    Args:
        temp_k: Black-body temperature in Kelvin.

    Returns:
        ``(r, g, b)`` triple of ints in [0, 255].
    """
    temp = temp_k / 100

    # Red channel
    if temp <= _KELVIN_WARM_COOL_BOUNDARY:
        r = 255
    else:
        r = temp - 60
        r = _KELVIN_RED_COEFF * (r ** _KELVIN_RED_EXP)
        if r < 0:
            r = 0
        if r > 255:
            r = 255

    # Green channel
    if temp <= _KELVIN_WARM_COOL_BOUNDARY:
        g = temp
        g = _KELVIN_GREEN_LOW_COEFF * math.log(g) + _KELVIN_GREEN_LOW_OFFSET
        if g < 0:
            g = 0
        if g > 255:
            g = 255
    else:
        g = temp - 60
        g = _KELVIN_GREEN_HIGH_COEFF * (g ** _KELVIN_GREEN_HIGH_EXP)
        if g < 0:
            g = 0
        if g > 255:
            g = 255

    # Blue channel
    if temp >= _KELVIN_WARM_COOL_BOUNDARY:
        b = 255
    else:
        if temp <= _KELVIN_BLUE_FLOOR:
            b = 0
        else:
            b = temp - 10
            b = _KELVIN_BLUE_COEFF * math.log(b) + _KELVIN_BLUE_OFFSET
            if b < 0:
                b = 0
            if b > 255:
                b = 255

    return (int(r), int(g), int(b))


def stefan_boltzmann_luminosity(radius_solar: float, temp_k: float) -> float:
    """Solar-relative luminosity from radius (in R_sun) and temperature (K).

    L / L_sun = (R / R_sun)^2 * (T / T_sun)^4

    Used by Stefan-Boltzmann star types (RED_GIANT, BROWN_DWARF,
    WHITE_DWARF) where temperature and radius are independent inputs.
    """
    return (radius_solar ** 2) * ((temp_k / SOLAR_TEMP_K) ** 4)


def wien_peak_wavelength(temp_k: float) -> float:
    """Peak emission wavelength (meters) via Wien's displacement law.

    lambda_peak = b / T, where b = WIEN_DISPLACEMENT_CONSTANT.

    For ``temp_k == 0`` (black-hole edge case) returns 1e99 to match
    legacy ``stars.py`` behavior — the caller short-circuits to zero
    intensity in that case.
    """
    if temp_k <= 0:
        return 1e99
    return WIEN_DISPLACEMENT_CONSTANT / temp_k
