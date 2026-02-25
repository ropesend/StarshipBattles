"""
IBattleResolver interface and BattleResult DTO.

PROJ-11 Phase 4: Interface contract for battle resolution.
This interface allows the strategy layer to depend on an abstraction
rather than the concrete simulation implementation.

The interface enables:
- Unit testing with mock resolvers
- Alternative battle resolution strategies
- Clean separation between strategy and simulation layers
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional, TYPE_CHECKING

from game.core.protocols import IPostBattleShip

if TYPE_CHECKING:
    from game.strategy.data.fleet import Fleet
    from game.core.registry import GameRegistries
    from game.strategy.services.area_effect_manager import EnvironmentalEffects


@dataclass
class BattleResult:
    """
    Data transfer object for battle results.

    This is a strategy-layer representation of battle outcomes,
    decoupled from simulation-layer internals.

    PROJ-90: Uses IPostBattleShip protocol for survivors typing.

    Attributes:
        winner: Team that won (0 or 1), or None for a draw
        tick_count: Number of simulation ticks the battle took
        team0_survivors: List of surviving ships for team 0
        team1_survivors: List of surviving ships for team 1
    """
    winner: Optional[int]
    tick_count: int
    team0_survivors: List[IPostBattleShip]
    team1_survivors: List[IPostBattleShip]


class IBattleResolver(ABC):
    """
    Abstract interface for battle resolution.

    Implementations handle the actual combat simulation between two fleets.
    The strategy layer uses this interface to remain decoupled from
    specific simulation implementations.

    Example usage:
        resolver = SimulationBattleResolver()  # or MockBattleResolver for tests
        result = resolver.resolve_battle(fleet1, fleet2, seed=42)
        if result.winner == 0:
            winner = fleet1
        elif result.winner == 1:
            winner = fleet2
        else:
            # Handle draw
            pass
    """

    @abstractmethod
    def resolve_battle(
        self,
        fleet1: 'Fleet',
        fleet2: 'Fleet',
        seed: Optional[int] = None,
        registries: Optional['GameRegistries'] = None,
        environmental_effects: Optional['EnvironmentalEffects'] = None
    ) -> BattleResult:
        """
        Resolve a battle between two fleets.

        Args:
            fleet1: First fleet (assigned to team 0)
            fleet2: Second fleet (assigned to team 1)
            seed: Optional random seed for deterministic battles
            registries: Optional GameRegistries for DI (PROJ-50)
            environmental_effects: Optional environmental effects from storms (PROJ-189).
                                   If provided with shield_capacity_mult < 1.0, ships
                                   will have reduced shield capacity during combat.

        Returns:
            BattleResult containing winner, tick count, and survivors
        """
        pass
