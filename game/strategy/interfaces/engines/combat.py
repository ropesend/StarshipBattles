"""Combat / environmental-hazard engine ABCs.

PROJ-422 (TD-09): extracted verbatim from the former
`game/strategy/interfaces/engines.py` monolith. Symbol-preserving;
the public import paths remain
`game.strategy.interfaces.engines.IConflictEngine` and
`game.strategy.interfaces.engines.IEnvironmentalHazardEngine` via the
package `__init__.py` re-export seam.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from game.strategy.data.galaxy import Galaxy
    from game.strategy.engine.conflict_resolution_engine import ConflictResult


__all__ = ['IConflictEngine', 'IEnvironmentalHazardEngine']


class IConflictEngine(ABC):
    """
    Abstract interface for combat conflict resolution.

    Implementations handle:
    - Detection of multi-empire conflicts at hexes
    - Battle resolution via IBattleResolver interface
    - Tracking combat results

    Example usage:
        engine = ConflictResolutionEngine(battle_resolver)
        result = engine.resolve_all_conflicts(empires)
    """

    @abstractmethod
    def resolve_all_conflicts(
        self,
        empires: List,
        galaxy: Optional['Galaxy'] = None,
        *,
        tick: Optional[int] = None,
        moved_fleet_ids: Optional[set] = None,
    ) -> 'ConflictResult':
        """
        Resolve all conflicts between empires.

        Args:
            empires: List of Empire objects to check for conflicts
            galaxy: Optional Galaxy for environmental effect lookup (PROJ-189).
                   When provided, storm effects are applied to combat.
            tick: PROJ-320 — current strategic sub-tick (1..TICKS_PER_TURN).
                When provided, combat is dispatched per-fleet on movement-
                opportunity ticks via `_should_trigger_combat_for_fleet`.
                When None, no combat fires (defensive: predicate cannot
                evaluate `tick % interval`). Production callers always pass
                this; legacy tests that omit it get a no-op behaviour and
                must opt in by supplying the tick to exercise the engine.
            moved_fleet_ids: PROJ-320 — set of fleet ids whose location
                actually changed during this tick's Phase 3
                (`FleetMovementEngine.apply_movements`). Combat is skipped
                for any fleet in this set on this tick (the fleet exercised
                its movement opportunity by leaving the hex). Defaults to
                an empty set when omitted.

        Returns:
            ConflictResult with combat statistics
        """
        pass


class IEnvironmentalHazardEngine(ABC):
    """
    Abstract interface for environmental hazard processing.

    PROJ-189: Storms Environmental Hazards.

    Implementations handle:
    - Processing storm effects (damage, fuel drain) each tick
    - Querying ability_iterator / SystemEffectsCollector at fleet locations for environmental effects
    - Applying damage and fuel drain to ships in storm hexes
    - Tracking environmental events for logging/UI

    Example usage:
        engine = EnvironmentalHazardEngine()
        events = engine.process_environmental_tick(tick, empires, galaxy)
    """

    @abstractmethod
    def process_environmental_tick(
        self,
        tick: int,
        empires: List,
        galaxy: Any
    ) -> List:
        """
        Process environmental effects for one tick.

        For each fleet in each empire, queries storm effects at the
        fleet's location and applies damage and fuel drain if in storm.

        Args:
            tick: Current tick number (1-100)
            empires: List of Empire objects to process
            galaxy: Galaxy object for spatial queries

        Returns:
            List of EnvironmentalEvent records for affected fleets
        """
        pass
