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
import logging
import random

from game.strategy.interfaces.battle_resolver import IBattleResolver, BattleResult

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from game.strategy.data.fleet import Fleet
    from game.core.registry import GameRegistries
    from game.strategy.services.area_effect_manager import EnvironmentalEffects


# Import simulation layer components
from game.simulation.battle_controller import BattleController
from game.simulation.battle_config import BattleConfig, BattleMode
from game.simulation.services.battle_service import BattleService

if TYPE_CHECKING:
    from game.simulation.interfaces.ai_controller import IAIControllerFactory


class SimulationBattleResolver(IBattleResolver):
    """
    IBattleResolver implementation using the full battle simulation.

    Uses BattleController to run headless battles and converts
    the results to strategy-layer BattleResult objects.

    PROJ-147: Supports dependency injection of AI factory to maintain
    layer separation (strategy should not import directly from AI layer).
    """

    def __init__(self, ai_factory: Optional['IAIControllerFactory'] = None):
        """
        Initialize the battle resolver.

        Args:
            ai_factory: Optional AI controller factory. If None, creates
                       AIControllerFactory from game.ai (late import to
                       avoid module-level AI layer dependency).
        """
        self._ai_factory = ai_factory

    def resolve_battle(
        self,
        fleet1: 'Fleet',
        fleet2: 'Fleet',
        seed: Optional[int] = None,
        registries: Optional['GameRegistries'] = None,
        environmental_effects: Optional['EnvironmentalEffects'] = None
    ) -> BattleResult:
        """
        Resolve a battle between two fleets using the battle simulation.

        Args:
            fleet1: First fleet (assigned to team 0)
            fleet2: Second fleet (assigned to team 1)
            seed: Optional random seed for deterministic battles
            registries: Optional GameRegistries for DI. If None, uses global provider.
            environmental_effects: Optional environmental effects from storms (PROJ-189).
                                   If provided with shield_capacity_mult < 1.0, ships
                                   will have reduced shield capacity during combat.

        Returns:
            BattleResult containing winner, tick count, and survivors
        """
        logger.info(f"Simulating battle: Fleet {fleet1.id} vs Fleet {fleet2.id}")

        # Convert fleets to battle ships
        team1_ships = fleet1.to_battle_ships(team_id=0, registries=registries)
        team2_ships = fleet2.to_battle_ships(team_id=1, registries=registries)

        # PROJ-189: Apply storm shield interference before combat
        if environmental_effects is not None and environmental_effects.shield_capacity_mult < 1.0:
            self._apply_shield_interference(team1_ships, environmental_effects.shield_capacity_mult)
            self._apply_shield_interference(team2_ships, environmental_effects.shield_capacity_mult)
            logger.info(f"Storm shield interference applied: {environmental_effects.shield_capacity_mult}")

        # Handle edge cases
        if not team1_ships and not team2_ships:
            logger.warning("Both fleets have no combat-capable ships")
            return BattleResult(
                winner=None,
                tick_count=0,
                team0_survivors=[],
                team1_survivors=[]
            )

        if not team1_ships:
            logger.warning("Fleet 1 has no combat-capable ships, Fleet 2 wins")
            return BattleResult(
                winner=1,
                tick_count=0,
                team0_survivors=[],
                team1_survivors=self._convert_ships_to_survivors(team2_ships)
            )

        if not team2_ships:
            logger.warning("Fleet 2 has no combat-capable ships, Fleet 1 wins")
            return BattleResult(
                winner=0,
                tick_count=0,
                team0_survivors=self._convert_ships_to_survivors(team1_ships),
                team1_survivors=[]
            )

        # Create battle controller
        # PROJ-147: Use injected factory or create via late import
        # Late import maintains layer separation at module level while
        # still allowing default behavior when no factory is injected
        ai_factory = self._ai_factory
        if ai_factory is None:
            from game.ai.ai_factory import AIControllerFactory
            ai_factory = AIControllerFactory()
        controller = BattleController(ai_factory=ai_factory)

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

        logger.info(f"Battle complete: winner={results.winner}, ticks={results.tick_count}")

        # Convert survivors
        # PROJ-50: Pass registries for strict DI compliance
        team0_survivors = []
        team1_survivors = []

        for ship_state in results.surviving_ships:
            ship = ship_state.to_ship(registries=registries)
            if ship_state.team_id == 0:
                team0_survivors.append(ship)
            else:
                team1_survivors.append(ship)

        logger.info(f"  Team 0 survivors: {len(team0_survivors)}")
        logger.info(f"  Team 1 survivors: {len(team1_survivors)}")

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

    def _apply_shield_interference(self, ships: List[Any], shield_mult: float) -> None:
        """
        Apply storm shield interference to ships.

        PROJ-189: Reduces max_shields and caps current_shields accordingly.
        This affects shields for the duration of the battle.

        Args:
            ships: List of Ship objects to modify
            shield_mult: Multiplier for shield capacity (0.0 to 1.0)
        """
        for ship in ships:
            if hasattr(ship, 'max_shields') and ship.max_shields > 0:
                # Reduce max shields
                new_max = int(ship.max_shields * shield_mult)
                ship.max_shields = new_max

                # Cap current shields to new max
                if hasattr(ship, 'current_shields'):
                    ship.current_shields = min(ship.current_shields, new_max)
