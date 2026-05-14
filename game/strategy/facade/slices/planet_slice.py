"""Planet query slice (PROJ-309 sub-phase 3.7).

Owns planet-shaped reads. The lazy `_planet_index` lives on
`FacadeSessionState` so multiple slices (planet + economy validation) share
the same cache.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, List, Optional

from game.core.hex_math import HexCoord
from game.core.validation import ValidationResult
from game.strategy.facade.dto import PlanetInfo

if TYPE_CHECKING:
    from game.strategy.data.planet import Planet
    from game.strategy.facade.slices._facade_state import FacadeSessionState


class PlanetSlice:
    """Planet reads + planet-shaped validation."""

    __slots__ = ("_state",)

    def __init__(self, state: "FacadeSessionState") -> None:
        self._state = state

    # ------------------------------------------------------------------
    # ID helpers (forwarded for tests asserting on the cached lookup)
    # ------------------------------------------------------------------

    def build_planet_index(self) -> dict:
        """Build planet-id -> Planet lookup dict (PROJ-254)."""
        return self._state.build_planet_index()

    def get_planet_by_id(self, planet_id: int) -> Optional["Planet"]:
        """Internal helper to get a planet by ID using index (PROJ-254)."""
        return self._state.get_planet_by_id(planet_id)

    # ------------------------------------------------------------------
    # Public reads
    # ------------------------------------------------------------------

    def get_planet(self, planet_id: int) -> Optional[PlanetInfo]:
        """Get planet information by ID."""
        planet = self._state.get_planet_by_id(planet_id)
        if planet is None:
            return None
        return PlanetInfo.from_planet(planet)

    def get_planets_at_hex(self, hex_coord: HexCoord) -> List[PlanetInfo]:
        """Get planets whose global position exactly matches the given hex coordinate.

        Only returns planets at the specific hex — not all planets in the
        system. A planet's global position is
        ``system.global_location + planet.location``. Uses radius search to
        resolve which system owns the hex when a strict lookup misses (e.g.
        clicking an inner hex that isn't the system center).
        """
        # 1. Try strict lookup first (fast & correct for exact hits)
        system = self._state.session.galaxy.get_system_at_location(hex_coord)

        # 2. If strict failed, try radius/ownership lookup (robust for area clicks)
        if system is None:
            from game.strategy.services.galaxy_pathfinding_service import (
                GalaxyPathfindingService,
            )
            system = GalaxyPathfindingService(
                self._state.session.galaxy,
            ).get_system_at_hex(hex_coord, radius=50)

        if system is None:
            return []

        target_planets = []
        for p in system.planets:
            p_global = system.global_location + p.location
            if p_global == hex_coord:
                target_planets.append(p)

        return [PlanetInfo.from_planet(planet) for planet in target_planets]

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------

    def can_colonize(
        self, fleet_id: int, planet_id: Optional[int]
    ) -> ValidationResult:
        """Check if a fleet can colonize a planet (without executing).

        Cross-domain query: needs both fleet AND planet lookup. Both go
        through `FacadeSessionState`, so this slice never reaches into
        `FleetSlice`.
        """
        fleet = self._state.get_fleet_by_id(fleet_id)
        if fleet is None:
            return ValidationResult.error("Fleet not found.")

        planet = None
        if planet_id is not None:
            planet = self._state.get_planet_by_id(planet_id)
            if planet is None:
                return ValidationResult.error("Planet not found.")

        return self._state.session.turn_engine.validate_colonize_order(
            self._state.session.galaxy, fleet, planet
        )
