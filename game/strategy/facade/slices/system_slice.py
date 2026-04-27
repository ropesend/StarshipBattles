"""System / star / storm query slice (PROJ-309 sub-phase 3.7)."""

from __future__ import annotations

from typing import TYPE_CHECKING, List, Optional

from game.core.hex_math import HexCoord
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
            for system in self._state.session.galaxy.systems.values()
        ]

    def get_all_stars(self) -> List[StarInfo]:
        """Get information about all stars in the galaxy.

        Returns enriched StarInfo DTOs with system context (system name,
        global location, planet count, companion star count).

        PROJ-254: cached per turn — galaxy structure doesn't change mid-turn.
        """
        state = self._state
        current_turn = getattr(state.session, "turn_number", 0)
        if (
            state.all_stars_cache is not None
            and state.all_stars_cache_turn == current_turn
        ):
            return state.all_stars_cache

        results: List[StarInfo] = []
        for system in state.session.galaxy.systems.values():
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
        system = self._state.session.galaxy.get_system_at_location(hex_coord)
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
        system = self._state.session.galaxy.get_system_at_location(hex_coord)
        if system:
            return SystemInfo.from_star_system(system)

        # 2. Proximity check
        from game.core.hex_math import hex_distance
        closest_system = None
        min_dist = max_dist + 1

        for sys in self._state.session.galaxy.systems.values():
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

        Uses AreaEffectManager to query the galaxy's zone spatial index
        for storms at the given hex.
        """
        from game.strategy.services.area_effect_manager import AreaEffectManager

        manager = AreaEffectManager()
        effects = manager.get_effects_at_global_hex(
            self._state.session.galaxy, hex_coord
        )
        return effects.storm_names if effects.in_storm else []
