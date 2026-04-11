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

    def __init__(self, ai_factory: 'IAIControllerFactory'):
        """
        Initialize the battle resolver.

        Args:
            ai_factory: AI controller factory (required). Must be injected
                       from a layer that can import game.ai (UI or app layer).
                       PROJ-239: Made required to eliminate AI layer dependency
                       from the strategy layer.
        """
        self._ai_factory = ai_factory

    def resolve_battle(
        self,
        fleet1: 'Fleet',
        fleet2: 'Fleet',
        seed: Optional[int] = None,
        registries: Optional['GameRegistries'] = None,
        environmental_effects: Optional['EnvironmentalEffects'] = None,
        team0_modifiers: Optional['FleetCombatModifiers'] = None,
        team1_modifiers: Optional['FleetCombatModifiers'] = None,
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
        team0_ships = fleet1.battle.to_battle_ships(team_id=0, registries=registries)
        team1_ships = fleet2.battle.to_battle_ships(team_id=1, registries=registries)

        # PROJ-189: Apply storm shield interference before combat
        if environmental_effects is not None and environmental_effects.shield_capacity_mult < 1.0:
            self._apply_shield_interference(team0_ships, environmental_effects.shield_capacity_mult)
            self._apply_shield_interference(team1_ships, environmental_effects.shield_capacity_mult)
            logger.info(f"Storm shield interference applied: {environmental_effects.shield_capacity_mult}")

        # Apply strategic combat modifiers (shield/damage boosters/suppressors)
        if team0_modifiers is not None:
            self._apply_strategic_modifiers(team0_ships, team0_modifiers)
        if team1_modifiers is not None:
            self._apply_strategic_modifiers(team1_ships, team1_modifiers)

        # Handle edge cases
        if not team0_ships and not team1_ships:
            logger.warning("Both fleets have no combat-capable ships")
            return BattleResult(
                winner=None,
                tick_count=0,
                team0_survivors=[],
                team1_survivors=[]
            )

        if not team0_ships:
            logger.warning("Fleet 1 has no combat-capable ships, Fleet 2 wins")
            return BattleResult(
                winner=1,
                tick_count=0,
                team0_survivors=[],
                team1_survivors=self._convert_ships_to_survivors(team1_ships)
            )

        if not team1_ships:
            logger.warning("Fleet 2 has no combat-capable ships, Fleet 1 wins")
            return BattleResult(
                winner=0,
                tick_count=0,
                team0_survivors=self._convert_ships_to_survivors(team0_ships),
                team1_survivors=[]
            )

        # Create battle controller
        # PROJ-239: ai_factory is always injected (required param)
        controller = BattleController(ai_factory=self._ai_factory)

        # Configure battle
        # PROJ-252: Use per-adapter RNG for fallback seed, not module-level random
        if seed is not None:
            battle_seed = seed
        else:
            if not hasattr(self, '_seed_rng'):
                import random as _random_mod
                self._seed_rng = _random_mod.Random()
            battle_seed = self._seed_rng.randint(0, 1000000)
        config = BattleConfig(
            mode=BattleMode.STRATEGY,
            seed=battle_seed,
            headless=True,
            allow_retreat=True,
        )

        controller.configure(config)
        controller.add_ships(team0_ships, 0)
        controller.add_ships(team1_ships, 1)
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
            # Ship always has max_shields and current_shields
            if ship.max_shields > 0:
                # Reduce max shields
                new_max = int(ship.max_shields * shield_mult)
                ship.max_shields = new_max
                # Cap current shields to new max
                ship.current_shields = min(ship.current_shields, new_max)

    def _apply_strategic_modifiers(self, ships: List[Any], modifiers) -> None:
        """Apply strategic combat modifiers to ships pre-battle.

        Args:
            ships: List of Ship objects to modify.
            modifiers: FleetCombatModifiers with shield/damage multipliers and flat bonus.
        """
        if modifiers.flat_shield_bonus > 0:
            bonus = int(modifiers.flat_shield_bonus)
            for ship in ships:
                ship.max_shields += bonus
                ship.current_shields += bonus

        if modifiers.shield_mult != 1.0:
            self._apply_shield_interference(ships, modifiers.shield_mult)

        if modifiers.damage_mult != 1.0:
            for ship in ships:
                ship.damage_output_mult = modifiers.damage_mult
