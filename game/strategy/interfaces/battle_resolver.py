"""
IBattleResolver interface and BattleResult DTO.

PROJ-11 Phase 4: Interface contract for battle resolution.
PROJ-275 Phase 7: signature widened from (fleet1, fleet2) to
(fleets: Sequence[Fleet]) for native N-team support. The legacy
sequential 2-fleet decomposition in `ConflictResolutionEngine` is
gone — strategy resolves N>=2 fleets at one sector in a single battle.

This interface allows the strategy layer to depend on an abstraction
rather than the concrete simulation implementation.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Mapping, Optional, Sequence, TYPE_CHECKING

from game.core.protocols import IPostBattleShip

if TYPE_CHECKING:
    from game.strategy.data.fleet import Fleet
    from game.core.registry import GameRegistries


@dataclass
class BattleResult:
    """N-team battle outcome reported up to the strategy layer.

    `winner` is the surviving team's id, or `None` for a draw (≥2 teams
    still have ships). `team_survivors` carries the post-battle survivors
    keyed by team_id, with one entry per team that participated — empty
    list means total loss.

    PROJ-275 Phase 7: replaced the legacy `team0_survivors` /
    `team1_survivors` pair (2-team only) with the dict form so any
    number of teams can be reported.

    FEAT-26: `replay_id` carries the captured replay's uuid string from
    `BattleOutcome.replay_id`. None when no real replay was written
    (a sole-survivor shortcut, or a simulator run with no capture sink).
    The strategy `ConflictResolutionEngine` reads this to attach the
    replay reference to the `COMBAT_RESOLVED` event.

    Issue #8: `replay_unavailable_reason` is a UI-friendly identifier
    explaining WHY `replay_id` is None. Reserved values:
      * "sole_survivor" — only one team had any ships at battle start
      * "no_ships" — neither fleet had any ships to materialize
    The Event Log button uses this string to show an honest tooltip
    instead of falling back to the generic "older save" wording. None
    when `replay_id` is set, or for legacy events from saves predating
    this field.
    """
    winner: Optional[int]
    tick_count: int
    team_survivors: Dict[int, List[IPostBattleShip]] = field(default_factory=dict)
    replay_id: Optional[str] = None
    replay_unavailable_reason: Optional[str] = None


class IBattleResolver(ABC):
    """
    Abstract interface for battle resolution.

    Implementations handle the actual combat simulation between any
    number of fleets (>=2). The strategy layer uses this interface to
    remain decoupled from specific simulation implementations.

    Example usage:
        resolver = SimulationBattleResolver(ai_factory=...)
        result = resolver.resolve_battle([fleet_a, fleet_b, fleet_c], seed=42)
        if result.winner is not None:
            print(f"Team {result.winner} won with "
                  f"{len(result.team_survivors[result.winner])} survivors")
    """

    @abstractmethod
    def resolve_battle(
        self,
        fleets: Sequence['Fleet'],
        modifiers: Optional[Mapping[int, Any]] = None,
        seed: Optional[int] = None,
        registries: Optional['GameRegistries'] = None,
        environmental_effects: Any = None,  # PROJ-300: now a sector-effects list
        empires: Optional[Mapping[int, Any]] = None,
    ) -> BattleResult:
        """
        Resolve a battle between N fleets.

        Args:
            fleets: Two or more fleets to fight. Position in the sequence
                determines team_id (fleets[i] → team i).
            modifiers: Optional mapping `{team_id: FleetCombatModifiers}`
                with per-team strategic modifiers.
            seed: Optional random seed for deterministic battles.
            registries: Optional GameRegistries for DI (PROJ-50).
            environmental_effects: PROJ-300 sector-effects list from
                `collect_sector_effects` (or None). The spec compiler
                emits one ModifierEntry per active provider so overlapping
                storms multiply.
            empires: BUG-126 — optional `{team_id: Empire}` mapping
                threaded into the spec compiler's `PostBattleHook` so
                fleets that end the battle with zero ships are removed
                from their empire's `fleets` list. Production callers
                must pass this; tests with mock resolvers may omit it.

        Returns:
            BattleResult with winner, tick count, and per-team survivors.
        """
        pass
