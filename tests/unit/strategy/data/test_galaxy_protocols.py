"""PROJ-372 Phase 0: structural conformance tests for galaxy_protocols.

We assert that the existing `Planet` and `Galaxy` data classes satisfy
the newly-introduced read protocols without any changes. This locks the
"facade preserves the surface" invariant — if a future refactor breaks
one of these protocol shapes accidentally, this test catches it.
"""
from __future__ import annotations

from typing import Optional

import pytest

from game.strategy.data.galaxy_protocols import (
    IGalaxySpatialQuery,
    IGalaxySystemGraph,
    IHabitabilityCalculator,
    IStagingYardHolder,
    IStockpileHolder,
)


def _make_minimal_planet():
    from game.core.hex_math import HexCoord
    from game.strategy.data.planet import Planet, PlanetType

    return Planet(
        name="Test",
        location=HexCoord(0, 0),
        orbit_distance=1,
        mass=1.0,
        radius=1.0,
        surface_area=1.0,
        density=1.0,
        surface_gravity=1.0,
        surface_pressure=0.0,
        surface_temperature=288.0,
        surface_water=0.0,
        tectonic_activity=0.0,
        magnetic_field=0.0,
        planet_type=PlanetType.BARREN,
    )


def test_planet_satisfies_istockpile_holder() -> None:
    planet = _make_minimal_planet()
    assert isinstance(planet, IStockpileHolder)


def test_planet_satisfies_istaging_yard_holder() -> None:
    planet = _make_minimal_planet()
    assert isinstance(planet, IStagingYardHolder)


def test_galaxy_satisfies_igalaxy_system_graph() -> None:
    from game.strategy.data.galaxy import Galaxy

    galaxy = Galaxy(radius=10)
    assert isinstance(galaxy, IGalaxySystemGraph)


def test_galaxy_satisfies_igalaxy_spatial_query() -> None:
    from game.strategy.data.galaxy import Galaxy

    galaxy = Galaxy(radius=10)
    assert isinstance(galaxy, IGalaxySpatialQuery)


def test_ihabitability_calculator_protocol_is_runtime_checkable() -> None:
    """A simple stub implementation should `isinstance` against the protocol."""

    class _StubCalc:
        def get_cached(self, planet, race_registry, turn: int) -> float:
            return 1.0

    assert isinstance(_StubCalc(), IHabitabilityCalculator)


def test_non_implementer_does_not_satisfy_ihabitability_calculator() -> None:
    class _NotACalc:
        pass

    assert not isinstance(_NotACalc(), IHabitabilityCalculator)
