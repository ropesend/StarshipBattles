"""
Shared fixtures for planet atmosphere tests.
"""

import pytest

from game.strategy.data.planet_physics import (
    MASS_EARTH, MASS_JUPITER, MASS_MARS
)


@pytest.fixture
def earth_like_params():
    """Parameters for an Earth-like planet."""
    return {
        "mass": MASS_EARTH,
        "escape_vel": 11186.0,  # m/s
        "base_temp": 255.0,  # K (blackbody temp)
        "flux_wm2": 1361.0,  # W/m^2 (solar constant)
    }


@pytest.fixture
def gas_giant_params():
    """Parameters for a Jupiter-like gas giant."""
    return {
        "mass": MASS_JUPITER,
        "escape_vel": 59500.0,  # m/s
        "base_temp": 110.0,  # K
        "flux_wm2": 50.0,  # W/m^2
    }


@pytest.fixture
def small_body_params():
    """Parameters for a small body like the Moon."""
    return {
        "mass": 7.34e22,  # Moon mass
        "escape_vel": 2380.0,  # m/s
        "base_temp": 270.0,  # K
        "flux_wm2": 1361.0,  # W/m^2
    }


@pytest.fixture
def hot_small_body_params():
    """Parameters for a hot Mercury-like body."""
    return {
        "mass": 3.30e23,  # Mercury mass
        "escape_vel": 4250.0,  # m/s
        "base_temp": 700.0,  # K (high temp)
        "flux_wm2": 9000.0,  # W/m^2
    }
