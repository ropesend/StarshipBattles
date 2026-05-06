"""``PlanetQueryService`` — pure-function queries over a ``Planet``.

PROJ-372 Phase 2. Hosts the four logic-bearing query/calc methods that
used to live on ``Planet`` itself:

- ``active_abilities`` — derive ability_name -> True from facility
  component_states.
- ``is_ability_active`` — single-key check on the above.
- ``occupied_hexes`` — multi-hex zone footprint (PROJ-139).
- ``can_build_type`` — vehicle-type build eligibility.

All methods are static. Tests can construct minimal planets and call
them without instantiating the service. The Planet facade's 1-line
delegations preserve the public API; external callers may continue to
call ``planet.active_abilities`` etc. as before.
"""
from __future__ import annotations

from typing import TYPE_CHECKING, Dict, FrozenSet

from game.core.hex_math import HexCoord, hex_circle_filled

if TYPE_CHECKING:
    from game.strategy.data.planet import Planet


__all__ = ["PlanetQueryService"]


class PlanetQueryService:
    """Static queries over a ``Planet`` data class.

    All methods take ``Planet`` (or duck-typed planet-like) as their
    first arg and return a derived value. They never mutate the
    planet.
    """

    @staticmethod
    def active_abilities(planet: "Planet") -> Dict[str, bool]:
        """Map ability_name -> True for every facility component in 'active' phase.

        Single source of truth — there is no separately-stored field;
        the dict is derived on every call from ``planet.facilities``.
        """
        result: Dict[str, bool] = {}
        for facility in planet.facilities:
            for _key, state_data in facility.component_states.items():
                if isinstance(state_data, dict) and state_data.get("phase") == "active":
                    ability_name = state_data.get("ability_name", "")
                    if ability_name:
                        result[ability_name] = True
        return result

    @staticmethod
    def is_ability_active(planet: "Planet", ability_key: str) -> bool:
        """True iff ``ability_key`` is present in ``active_abilities``."""
        return PlanetQueryService.active_abilities(planet).get(ability_key, False)

    @staticmethod
    def occupied_hexes(planet: "Planet") -> FrozenSet[HexCoord]:
        """Return all hexes occupied by this planet (PROJ-139 IZoneOccupant).

        Single-hex planet: returns ``frozenset({planet.location})``.
        Multi-hex object (Dyson Sphere): returns the filled hex circle.
        """
        if planet.radius_hexes > 0:
            return hex_circle_filled(planet.location, max(0, planet.radius_hexes - 1))
        return frozenset({planet.location})

    @staticmethod
    def can_build_type(planet: "Planet", vehicle_type: str) -> bool:
        """True iff this planet can build the given vehicle type.

        Complexes can always be built. Ships, fighters, and satellites
        require a space shipyard. Anything else returns False.
        """
        vehicle_lower = vehicle_type.lower()
        if vehicle_lower == "complex":
            return True
        if vehicle_lower in ("ship", "fighter", "satellite"):
            return planet.has_space_shipyard
        return False
