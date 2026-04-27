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
        return [BuildQueueSourceDTO.from_domain(source) for source in sources]

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
        return [BuildQueueSourceDTO.from_domain(source) for source in sources]
