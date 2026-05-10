"""Shared factory for mock `Planet` objects in tests.

PROJ-322 Task 6.7 (HLP-004): consolidates the duplicated `_make_planet`
helpers that materialized across multiple strategy-test modules.

The factory builds a `MagicMock(spec=Planet)` populated with the full
`IPlanet` protocol surface (PROJ-193). Tests that only need a couple of
attributes can still pass them as kwargs; everything else is filled in
with sensible defaults (no facilities, no populations, single-tile
radius, neutral atmosphere).

Usage
-----

::

    from tests.fixtures.mock_planet import make_mock_planet

    planet = make_mock_planet(name="Eden", owner_id=0)
    # Customize one field without re-listing the entire IPlanet surface:
    planet = make_mock_planet(planet_type=MyPlanetType.CONTINENTAL, max_population=10000)
"""

from __future__ import annotations

from typing import Any
from unittest.mock import MagicMock

from game.core.hex_math import HexCoord


def make_mock_planet(
    *,
    name: str = "Test Planet",
    owner_id: int | None = None,
    location: Any | None = None,
    planet_type: Any | None = None,
    deposits: dict | None = None,
    planet_id: int = 1,
    populations: list | None = None,
    max_population: int = 1000,
    facilities: list | None = None,
    atmosphere: dict | None = None,
    surface_gravity: float = 9.8,
    surface_temperature: float = 300.0,
    orbit_distance: int = 1,
    radius_hexes: int = 0,
    image_id: str = "",
) -> Any:
    """Build a MagicMock(spec=Planet) with the full IPlanet surface.

    All keyword arguments are optional; defaults match the historical
    `_make_planet` helpers across `tests/unit/strategy/validation/` and
    related modules.

    Returns
    -------
    A `MagicMock(spec=Planet)` instance with every IPlanet protocol
    attribute pre-populated. Tests can mutate the returned mock freely.
    """

    from game.strategy.data.planet import Planet

    planet = MagicMock(spec=Planet)
    planet.name = name
    planet.owner_id = owner_id
    planet.location = location if location is not None else HexCoord(0, 0)
    planet.planet_type = planet_type
    planet.deposits = dict(deposits) if deposits is not None else {}
    # PROJ-193: Required IPlanet properties.
    planet.id = planet_id
    planet.populations = list(populations) if populations is not None else []
    planet.max_population = max_population
    planet.facilities = list(facilities) if facilities is not None else []
    planet.atmosphere = dict(atmosphere) if atmosphere is not None else {}
    planet.surface_gravity = surface_gravity
    planet.surface_temperature = surface_temperature
    planet.orbit_distance = orbit_distance
    planet.radius_hexes = radius_hexes
    planet.image_id = image_id
    return planet


__all__ = ["make_mock_planet"]
