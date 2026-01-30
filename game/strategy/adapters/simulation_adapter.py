"""
SimulationBattleResolver - Adapts simulation layer to IBattleResolver interface.

PROJ-11 Phase 4: Interface Contracts.

This adapter bridges the strategy layer's IBattleResolver interface
to the simulation layer's BattleController. It handles:
- Converting fleets to battle ships
- Running headless battles
- Converting simulation results back to strategy-layer format
"""

from typing import Optional, List, Any, TYPE_CHECKING
import random

from game.core.logger import log_info, log_warning, log_debug
from game.strategy.interfaces.battle_resolver import IBattleResolver, BattleResult

if TYPE_CHECKING:
    from game.strategy.data.fleet import Fleet
    from game.core.registry import GameRegistries


# Import simulation layer components
from game.simulation.battle_controller import (
    BattleController, BattleConfig, BattleMode
)
from game.simulation.services.battle_service import BattleService


class SimulationBattleResolver(IBattleResolver):
    """
    IBattleResolver implementation using the full battle simulation.

    Uses BattleController to run headless battles and converts
    the results to strategy-layer BattleResult objects.
    """

    def resolve_battle(
        self,
        fleet1: 'Fleet',
        fleet2: 'Fleet',
        seed: Optional[int] = None,
        registries: Optional['GameRegistries'] = None
    ) -> BattleResult:
        """
        Resolve a battle between two fleets using the battle simulation.

        Args:
            fleet1: First fleet (assigned to team 0)
            fleet2: Second fleet (assigned to team 1)
            seed: Optional random seed for deterministic battles
            registries: Optional GameRegistries for DI. If None, uses global fallback
                        (transitional - will be required in Phase 6).

        Returns:
            BattleResult containing winner, tick count, and survivors
        """
        log_info(f"Simulating battle: Fleet {fleet1.id} vs Fleet {fleet2.id}")

        # Convert fleets to battle ships
        team1_ships = fleet1.to_battle_ships(team_id=0, registries=registries)
        team2_ships = fleet2.to_battle_ships(team_id=1, registries=registries)

        # Handle edge cases
        if not team1_ships and not team2_ships:
            log_warning("Both fleets have no combat-capable ships")
            return BattleResult(
                winner=None,
                tick_count=0,
                team0_survivors=[],
                team1_survivors=[]
            )

        if not team1_ships:
            log_warning("Fleet 1 has no combat-capable ships, Fleet 2 wins")
            return BattleResult(
                winner=1,
                tick_count=0,
                team0_survivors=[],
                team1_survivors=self._convert_ships_to_survivors(team2_ships)
            )

        if not team2_ships:
            log_warning("Fleet 2 has no combat-capable ships, Fleet 1 wins")
            return BattleResult(
                winner=0,
                tick_count=0,
                team0_survivors=self._convert_ships_to_survivors(team1_ships),
                team1_survivors=[]
            )

        # Create battle controller
        controller = BattleController(BattleService())

        # Configure battle
        battle_seed = seed if seed is not None else random.randint(0, 1000000)
        config = BattleConfig(
            mode=BattleMode.STRATEGY,
            seed=battle_seed,
            headless=True,
            allow_retreat=True,
            source_fleets=(fleet1, fleet2),
        )

        controller.configure(config)
        controller.add_ships(team1_ships, 0)
        controller.add_ships(team2_ships, 1)
        controller.start()

        # Run headless battle
        results = controller.run_headless()

        log_info(f"Battle complete: winner={results.winner}, ticks={results.tick_count}")

        # Convert survivors
        team0_survivors = []
        team1_survivors = []

        for ship_state in results.surviving_ships:
            ship = ship_state.to_ship()
            if ship_state.team_id == 0:
                team0_survivors.append(ship)
            else:
                team1_survivors.append(ship)

        log_info(f"  Team 0 survivors: {len(team0_survivors)}")
        log_info(f"  Team 1 survivors: {len(team1_survivors)}")

        return BattleResult(
            winner=results.winner,
            tick_count=results.tick_count,
            team0_survivors=team0_survivors,
            team1_survivors=team1_survivors
        )

    def _convert_ships_to_survivors(self, ships: List[Any]) -> List[Any]:
        """
        Convert battle ship objects to survivor format.

        Used for edge cases where battle doesn't actually run.
        """
        # For ships that never entered battle, just return them as-is
        # They're already in the format we need
        return list(ships)
