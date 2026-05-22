"""Empire query slice (PROJ-309 sub-phase 3.7)."""

from __future__ import annotations

from typing import TYPE_CHECKING, List, Optional

from game.core.hex_math import HexCoord
from game.strategy.facade.dto import (
    BuildQueueSourceDTO,
    ColonySummary,
    EmpireInfo,
    FleetSummary,
)

if TYPE_CHECKING:
    from game.strategy.data.empire import Empire
    from game.strategy.facade.slices._facade_state import FacadeSessionState


class EmpireSlice:
    """Empire-scoped reads + build-queue collectors."""

    __slots__ = ("_state",)

    def __init__(self, state: "FacadeSessionState") -> None:
        self._state = state

    # ------------------------------------------------------------------
    # ID helper (forwarded for legacy tests)
    # ------------------------------------------------------------------

    def get_empire_by_id(self, empire_id: int) -> Optional["Empire"]:
        """Internal helper to get an empire by ID via linear scan."""
        return self._state.get_empire_by_id(empire_id)

    # ------------------------------------------------------------------
    # Public reads
    # ------------------------------------------------------------------

    def get_all_empires(self) -> List[EmpireInfo]:
        """Get information about all empires."""
        return [
            EmpireInfo.from_empire(empire)
            for empire in self._state.session.empires
        ]

    def get_empire(self, empire_id: int) -> Optional[EmpireInfo]:
        """Get empire information by ID."""
        empire = self._state.get_empire_by_id(empire_id)
        if empire is None:
            return None
        return EmpireInfo.from_empire(empire)

    def get_empire_colonies(self, empire_id: int) -> List[ColonySummary]:
        """Get colony summaries for an empire."""
        empire = self._state.get_empire_by_id(empire_id)
        if empire is None:
            return []
        return [ColonySummary.from_planet(planet) for planet in empire.colonies]

    def get_empire_fleets(self, empire_id: int) -> List[FleetSummary]:
        """Get fleet summaries for an empire."""
        empire = self._state.get_empire_by_id(empire_id)
        if empire is None:
            return []
        return [FleetSummary.from_fleet(fleet) for fleet in empire.fleets]

    def get_empire_build_queues(self, empire_id: int) -> List[BuildQueueSourceDTO]:
        """Get all build queue sources for an empire."""
        from game.strategy.data.build_queue_source import (
            collect_all_build_queues_for_empire,
        )

        empire = self._state.get_empire_by_id(empire_id)
        if empire is None:
            return []
        sources = collect_all_build_queues_for_empire(
            empire, registries=self._state.session.registries
        )
        return [self._project_build_queue_source(source) for source in sources]

    def get_hex_build_queues(
        self, empire_id: int, hex_coord: HexCoord
    ) -> List[BuildQueueSourceDTO]:
        """Get all build queue sources at a hex for a specific empire."""
        from game.strategy.data.build_queue_source import collect_build_queues_at_hex

        empire = self._state.get_empire_by_id(empire_id)
        if empire is None:
            return []
        sources = collect_build_queues_at_hex(
            hex_coord,
            self._state.session.galaxy,
            empire,
            registries=self._state.session.registries,
        )
        return [self._project_build_queue_source(source) for source in sources]

    # ------------------------------------------------------------------
    # Build-queue projection (PROJ-472 Phase 1B)
    # ------------------------------------------------------------------

    def _project_build_queue_source(self, source: object) -> BuildQueueSourceDTO:
        """Project a domain ``BuildQueueSource`` to a ``BuildQueueSourceDTO``.

        Resolves the owner-derived SCALARS (``owner_global_hex`` /
        ``owner_system_name``) against the galaxy here, where galaxy access
        exists, so the frozen DTO never holds the live owner entity. The UI
        consumes only the resolved scalars.
        """
        owner_global_hex, owner_system_name = self._resolve_owner_scalars(source)
        return BuildQueueSourceDTO.from_domain(
            source,
            owner_global_hex=owner_global_hex,
            owner_system_name=owner_system_name,
        )

    def _resolve_owner_scalars(
        self, source: object
    ) -> tuple[Optional[HexCoord], Optional[str]]:
        """Resolve (owner_global_hex, owner_system_name) for a build queue source.

        Fleet sources: hex is the fleet's live ``location``; system name is
        the system at that hex. Planet sources: hex is
        ``system.global_location + planet.location``; system name is the
        owning system's name. Returns ``(None, None)`` when no galaxy is
        available or the owner cannot be located.
        """
        owner = getattr(source, "owner_entity", None)
        if owner is None:
            return None, None
        galaxy = getattr(self._state.session, "galaxy", None)
        context_type = getattr(source, "context_type", None)

        if context_type == "fleet":
            location = getattr(owner, "location", None)
            system_name = None
            if galaxy is not None and location is not None:
                system = galaxy.get_system_at_location(location)
                if system is not None:
                    system_name = system.name
            return location, system_name

        if context_type == "planet":
            if galaxy is None:
                return None, None
            system = galaxy.get_system_of_planet(owner)
            if system is None:
                return None, None
            owner_location = getattr(owner, "location", None)
            global_hex = (
                system.global_location + owner_location
                if owner_location is not None
                else None
            )
            return global_hex, system.name

        return None, None
