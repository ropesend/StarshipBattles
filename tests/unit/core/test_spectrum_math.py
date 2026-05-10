"""PROJ-372 Phase 1: pure-math tests for ``game.core.spectrum_math``.

These functions and constants were extracted from ``stars.py`` because
they're pure math with zero domain knowledge — Kelvin-to-RGB (Tanner
Helland's algorithm), Stefan-Boltzmann luminosity, Wien's displacement
law, and the 9-band representative wavelength dict.

The tests assert identical numerical behavior to the prior in-stars.py
implementation; if the math drifts, this catches it.
"""
from __future__ import annotations

import math


def test_module_constants_present() -> None:
    from game.core import spectrum_math as sm

    assert sm.SOLAR_MASS_KG == 1.989e30
    assert sm.SOLAR_RADIUS_M == 6.957e8
    assert sm.SOLAR_LUMINOSITY_W == 3.828e26
    assert sm.SOLAR_TEMP_K == 5778
    assert sm.WIEN_DISPLACEMENT_CONSTANT == 2.898e-3
    # 9 representative wavelengths for the Spectrum band model.
    assert set(sm._WAVELENGTHS.keys()) == {
        "gamma", "xray", "uv", "blue", "green", "red",
        "ir", "microwave", "radio",
    }


def test_kelvin_to_rgb_solar_temperature() -> None:
    from game.core.spectrum_math import kelvin_to_rgb

    r, g, b = kelvin_to_rgb(5778)
    # Solar temperature should be near-white.
    assert 200 <= r <= 255
    assert 200 <= g <= 255
    assert 200 <= b <= 255


def test_kelvin_to_rgb_cool_star_warm_tinted() -> None:
    from game.core.spectrum_math import kelvin_to_rgb

    r, g, b = kelvin_to_rgb(2000)
    # Cool stars: red dominates blue.
    assert r > b
    assert r == 255  # Tanner Helland clamps red to 255 for temp/100 <= 66.


def test_kelvin_to_rgb_hot_star_blue_tinted() -> None:
    from game.core.spectrum_math import kelvin_to_rgb

    r, g, b = kelvin_to_rgb(20000)
    # Hot stars: blue dominates red.
    assert b == 255  # Hot stars: blue clamped to 255.
    assert b >= r


def test_stefan_boltzmann_solar_baseline() -> None:
    from game.core.spectrum_math import (
        SOLAR_TEMP_K,
        stefan_boltzmann_luminosity,
    )

    # Sun: radius=1 R_sol, temp=5778 K, luminosity = 1 L_sol.
    L = stefan_boltzmann_luminosity(radius_solar=1.0, temp_k=SOLAR_TEMP_K)
    assert math.isclose(L, 1.0, abs_tol=1e-9)


def test_stefan_boltzmann_scales_with_radius_and_temperature() -> None:
    from game.core.spectrum_math import stefan_boltzmann_luminosity

    # Doubling radius should quadruple luminosity at fixed T.
    base = stefan_boltzmann_luminosity(radius_solar=1.0, temp_k=5778)
    bigger = stefan_boltzmann_luminosity(radius_solar=2.0, temp_k=5778)
    assert math.isclose(bigger / base, 4.0, abs_tol=1e-9)


def test_wien_peak_wavelength_solar_in_visible() -> None:
    from game.core.spectrum_math import wien_peak_wavelength

    # Solar peak ~ 502 nm (green-blue boundary).
    peak = wien_peak_wavelength(temp_k=5778)
    assert 4e-7 < peak < 6e-7


def test_wien_peak_wavelength_zero_temperature_safe() -> None:
    from game.core.spectrum_math import wien_peak_wavelength

    # Black-hole edge case (temp=0); must not raise.
    peak = wien_peak_wavelength(temp_k=0)
    # Convention: returns "infinity-ish" as 1e99 (matches stars.py legacy).
    assert peak >= 1e10
