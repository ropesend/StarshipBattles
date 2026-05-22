"""System / star / storm query slice (PROJ-309 sub-phase 3.7)."""

from __future__ import annotations

from typing import TYPE_CHECKING, List, Optional

from game.core.hex_math import HexCoord
from game.core.protocols import is_storm
from game.strategy.facade.dto import StarInfo, SystemInfo

if TYPE_CHECKING:
    from game.strategy.facade.slices._facade_state import FacadeSessionState


class SystemSlice:
    """System / star / storm / map reads."""

    __slots__ = ("_state",)

    def __init__(self, state: "FacadeSessionState") -> None:
        self._state = state

    # ------------------------------------------------------------------
    # System reads
    # ------------------------------------------------------------------

    def get_all_systems(self) -> List[SystemInfo]:
        """Get information about all star systems."""
        return [
            SystemInfo.from_star_system(system)
            for system in self._state._session.galaxy.systems.values()
        ]

    def get_all_stars(self) -> List[StarInfo]:
        """Get information about all stars in the galaxy.

        Returns enriched StarInfo DTOs with system context (system name,
        global location, planet count, companion star count).

        PROJ-254: cached per turn — galaxy structure doesn't change mid-turn.
        """
        state = self._state
        current_turn = getattr(state._session, "turn_number", 0)
        if (
            state.all_stars_cache is not None
            and state.all_stars_cache_turn == current_turn
        ):
            return state.all_stars_cache

        results: List[StarInfo] = []
        for system in state._session.galaxy.systems.values():
            for star in system.stars:
                results.append(StarInfo.from_star(
                    star,
                    system_name=system.name,
                    system_global_location=system.global_location,
                    planet_count=len(system.planets),
                    total_star_count=len(system.stars),
                ))
        state.all_stars_cache = results
        state.all_stars_cache_turn = current_turn
        return results

    def get_system_at_hex(self, hex_coord: HexCoord) -> Optional[SystemInfo]:
        """Get the system at a specific hex coordinate.

        ``hex_coord`` may be the system's global center or any hex inside it.
        """
        system = self._state._session.galaxy.get_system_at_location(hex_coord)
        if system is None:
            return None
        return SystemInfo.from_star_system(system)

    def get_system_by_name(self, name: str) -> Optional[SystemInfo]:
        """Get the system with the given name (O(1) name-map lookup).

        PROJ-477 Phase 2: summary read surface for cold callers; delegates to
        ``galaxy.get_system_by_name`` (``galaxy.py:130``). Returns ``None`` for
        an unknown name.
        """
        system = self._state._session.galaxy.get_system_by_name(name)
        if system is None:
            return None
        return SystemInfo.from_star_system(system)

    def get_system_of_object(self, obj: object) -> Optional[SystemInfo]:
        """Get the system containing an object with a global location.

        PROJ-477 Phase 2: summary read surface for cold callers; delegates to
        ``galaxy.get_system_of_object`` (``galaxy.py:134``). Returns ``None``
        when the object resolves to no system. Callers that need the LIVE
        ``StarSystem`` (e.g. to iterate its ``.planets``) use the scene-owned
        ``StrategyWorldAccess.system_for_object`` instead (POST-FLESH B2).
        """
        system = self._state._session.galaxy.get_system_of_object(obj)
        if system is None:
            return None
        return SystemInfo.from_star_system(system)

    def get_system_at_map_hex(
        self, hex_coord: HexCoord, radius: int = 50
    ) -> Optional[SystemInfo]:
        """Get the system OWNING a map hex, using pathfinder system-radius
        semantics (default 50).

        PROJ-477 Phase 2: this is the system-ownership query (delegating to
        ``GalaxyPathfindingService.get_system_at_hex(hex, radius)`` via
        ``galaxy._pathfinder``, ``galaxy_pathfinding_service.py:113``). It is
        DISTINCT from ``near_hex(max_dist=8)`` — different ownership semantics
        (design.md risk 2 / decisions.md). Do NOT alias the two.

        Callers that need the LIVE ``StarSystem`` (to read ``.planets`` /
        ``.warp_points``) use ``StrategyWorldAccess.system_at_map_hex`` instead
        (POST-FLESH B2); this summary surface is for summary-only callers.
        """
        system = self._state._session.galaxy._pathfinder.get_system_at_hex(
            hex_coord, radius
        )
        if system is None:
            return None
        return SystemInfo.from_star_system(system)

    def get_system_containing_fleet(self, fleet_id: int) -> Optional[SystemInfo]:
        """Get the system containing (or closest to) the fleet.

        Handles cases where the fleet is in empty space within a system's
        logic bounds but not at a specific system object.
        """
        fleet = self._state.get_fleet_by_id(fleet_id)
        if fleet is None:
            return None

        return self.get_system_near_hex(fleet.location)

    def get_system_near_hex(
        self, hex_coord: HexCoord, max_dist: int = 8
    ) -> Optional[SystemInfo]:
        """Get the system at or near the given hex coordinate.

        Useful for resolving clicks that might be slightly off a system's
        strict location, or for finding the enclosing system when an entity
        is in 'empty space' within a system.
        """
        # 1. Try strict lookup first
        system = self._state._session.galaxy.get_system_at_location(hex_coord)
        if system:
            return SystemInfo.from_star_system(system)

        # 2. Proximity check
        from game.core.hex_math import hex_distance
        closest_system = None
        min_dist = max_dist + 1

        for sys in self._state._session.galaxy.systems.values():
            dist = hex_distance(sys.global_location, hex_coord)
            if dist < min_dist:
                min_dist = dist
                closest_system = sys

        if closest_system:
            return SystemInfo.from_star_system(closest_system)

        return None

    # ------------------------------------------------------------------
    # Storm reads (PROJ-215 Phase 5)
    # ------------------------------------------------------------------

    def get_storm_names_at_hex(self, hex_coord: HexCoord) -> List[str]:
        """Get storm names affecting a global hex coordinate.

        PROJ-300 Phase 7: AreaEffectManager removed; queries the galaxy's
        zone spatial index directly for Storm instances at the hex.

        PROJ-470 TG-003: uses the ``is_storm`` TypeGuard instead of
        ``isinstance(zone, Storm)``. The guard requires BOTH ``storm_type``
        and ``abilities``; ``storm_type`` is unique to ``Storm`` across the
        strategy layer, so the guard is exactly equivalent to the isinstance
        check for the zone domain (stars/storms/planets) while conforming to
        the Pattern #2 Protocol+TypeGuard convention. Characterization test:
        ``test_get_storm_names_at_hex_excludes_abilities_carrying_non_storm``.
        """
        galaxy = self._state._session.galaxy
        get_zones = getattr(galaxy, 'get_zones_at_global_hex', None)
        if get_zones is None:
            return []
        zones = get_zones(hex_coord) or []
        return [zone.name for zone in zones if is_storm(zone)]
