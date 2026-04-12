"""SimulationBattleResolver - Strategy-to-simulation adapter.

PROJ-11 Phase 4: Interface Contracts.

This adapter bridges the strategy layer's `IBattleResolver` interface
to the simulation layer's unified `run_battle(spec) -> BattleOutcome`
entry. It translates fleets into a `BattleSpec` via the strategy spec
compiler, runs the battle, and reports the outcome as a `BattleResult`.

PROJ-269 Phase 6 Tasks 6.5 + 6.11:
  - The legacy `BattleController` + `BattleConfig` + `run_headless`
    path was replaced with `build_strategy_battle_spec` + `run_battle`.
  - The `_apply_shield_interference` / `_apply_strategic_modifiers`
    ship-mutation side channels are gone — environmental and team
    modifiers now flow through `ModifierStack` entries emitted by the
    compiler (placeholder effects per Phase 5.5 semantics).
  - Fleet updates happen via `PostBattleHook` (attached by the compiler)
    during `run_battle` — callers treat `BattleResult` as a read-only
    report. `FleetBattleAdapter.update_from_battle_results` is deleted.
"""

from typing import Optional, List, Any, TYPE_CHECKING
import logging

from game.simulation.battle_runner import run_battle
from game.strategy.interfaces.battle_resolver import IBattleResolver, BattleResult

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from game.strategy.data.fleet import Fleet
    from game.core.registry import GameRegistries
    from game.strategy.services.area_effect_manager import EnvironmentalEffects
    from game.simulation.interfaces.ai_controller import IAIControllerFactory


class SimulationBattleResolver(IBattleResolver):
    """IBattleResolver implementation using the unified `run_battle` entry.

    Each call compiles the fleets into a `BattleSpec` (via
    `build_strategy_battle_spec`), runs the battle through `run_battle`,
    and maps the `BattleOutcome` back to a `BattleResult`. The compiler
    attaches a `PostBattleHook` (`apply_outcome_to_fleets`) that writes
    outcome data back into `ShipInstance.components` and prunes the
    fleets — callers do not need to apply fleet updates separately.

    PROJ-147: Supports dependency injection of AI factory to maintain
    layer separation (strategy cannot import AI directly).
    """

    def __init__(self, ai_factory: 'IAIControllerFactory'):
        """Initialize the battle resolver.

        Args:
            ai_factory: AI controller factory (required). Must be
                injected from a layer that can import `game.ai`
                (UI or app layer).
        """
        self._ai_factory = ai_factory

    def resolve_battle(
        self,
        fleet1: 'Fleet',
        fleet2: 'Fleet',
        seed: Optional[int] = None,
        registries: Optional['GameRegistries'] = None,
        environmental_effects: Optional['EnvironmentalEffects'] = None,
        team0_modifiers: Optional[Any] = None,
        team1_modifiers: Optional[Any] = None,
    ) -> BattleResult:
        """Resolve a battle between two fleets via the unified entry.

        Args:
            fleet1: First fleet (assigned to team 0).
            fleet2: Second fleet (assigned to team 1).
            seed: Optional random seed for deterministic battles.
            registries: Optional GameRegistries for DI. If None, the
                underlying `ShipInstance.to_ship` uses the global
                default registry provider.
            environmental_effects: Optional sector/hex environmental
                effects (storm shield interference). Flows into the
                BattleSpec's ModifierStack as global entries.
            team0_modifiers / team1_modifiers: Optional
                `FleetCombatModifiers` carrying per-team strategic
                modifiers. Flow into the BattleSpec's ModifierStack as
                per-team entries.

        Returns:
            BattleResult with winner, tick count, and survivors. Fleet
            state (ship removal, component HP updates) has already been
            written back by the compiler's post-battle hook when this
            returns.
        """
        logger.info(f"Simulating battle: Fleet {fleet1.id} vs Fleet {fleet2.id}")

        team0_combat = [s for s in fleet1.ships if s.is_combat_capable()]
        team1_combat = [s for s in fleet2.ships if s.is_combat_capable()]

        if not team0_combat and not team1_combat:
            logger.warning("Both fleets have no combat-capable ships")
            return BattleResult(
                winner=None, tick_count=0,
                team0_survivors=[], team1_survivors=[],
            )
        if not team0_combat:
            logger.warning("Fleet 1 has no combat-capable ships, Fleet 2 wins")
            return BattleResult(
                winner=1, tick_count=0,
                team0_survivors=[],
                team1_survivors=self._instances_to_ships(team1_combat, 1, registries),
            )
        if not team1_combat:
            logger.warning("Fleet 2 has no combat-capable ships, Fleet 1 wins")
            return BattleResult(
                winner=0, tick_count=0,
                team0_survivors=self._instances_to_ships(team0_combat, 0, registries),
                team1_survivors=[],
            )

        battle_seed = self._resolve_seed(seed)

        spec = self._build_spec(
            fleet1, fleet2,
            seed=battle_seed,
            registries=registries,
            environmental_effects=environmental_effects,
            team0_modifiers=team0_modifiers,
            team1_modifiers=team1_modifiers,
        )
        ship_builder = self._make_ship_builder(fleet1, fleet2, registries)

        # `run_battle` invokes the compiler's `PostBattleHook` which
        # writes outcome data back into the ShipInstances and prunes
        # destroyed/retreated ships from the fleets.
        outcome = run_battle(
            spec,
            ai_factory=self._ai_factory,
            ship_builder=ship_builder,
        )

        winner = self._determine_winner(outcome)
        team0_survivors = self._instances_to_ships(fleet1.ships, 0, registries)
        team1_survivors = self._instances_to_ships(fleet2.ships, 1, registries)

        logger.info(
            f"Battle complete: winner={winner}, "
            f"ticks={outcome.duration_ticks}"
        )
        logger.info(f"  Team 0 survivors: {len(team0_survivors)}")
        logger.info(f"  Team 1 survivors: {len(team1_survivors)}")

        return BattleResult(
            winner=winner,
            tick_count=outcome.duration_ticks,
            team0_survivors=team0_survivors,
            team1_survivors=team1_survivors,
        )

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _resolve_seed(self, seed: Optional[int]) -> int:
        if seed is not None:
            return seed
        if not hasattr(self, '_seed_rng'):
            import random as _random_mod
            self._seed_rng = _random_mod.Random()
        return self._seed_rng.randint(0, 1000000)

    def _build_spec(
        self,
        fleet1: 'Fleet',
        fleet2: 'Fleet',
        *,
        seed: int,
        registries: Optional['GameRegistries'],
        environmental_effects: Optional['EnvironmentalEffects'],
        team0_modifiers: Optional[Any],
        team1_modifiers: Optional[Any],
    ):
        from game.strategy.combat.spec_compiler import build_strategy_battle_spec

        team_modifiers: dict = {}
        if team0_modifiers is not None:
            team_modifiers[0] = team0_modifiers
        if team1_modifiers is not None:
            team_modifiers[1] = team1_modifiers

        return build_strategy_battle_spec(
            [fleet1, fleet2],
            registries=registries,
            seed=seed,
            environmental_effects=environmental_effects,
            team_modifiers=team_modifiers if team_modifiers else None,
        )

    def _make_ship_builder(
        self,
        fleet1: 'Fleet',
        fleet2: 'Fleet',
        registries: Optional['GameRegistries'],
    ):
        """Build a ship_builder closure that materializes Ships from
        ShipInstances, keyed by instance_id.

        The compiler emits `ShipSpec.instance_id = ship_instance.instance_id`
        — the builder looks up the original ShipInstance and calls its
        `to_ship(pos, team_id, registries)` method. Position and team_id
        are overwritten by `run_battle` (spec pose + `controller.add_ships`).
        """
        lookup = {}
        for fleet in (fleet1, fleet2):
            for instance in fleet.ships:
                lookup[instance.instance_id] = instance

        def ship_builder(ship_spec):
            instance = lookup.get(ship_spec.instance_id)
            if instance is None:
                raise ValueError(
                    f"No ShipInstance in source fleets for "
                    f"instance_id={ship_spec.instance_id!r}"
                )
            return instance.to_ship(
                (0.0, 0.0), team_id=0, registries=registries,
            )

        return ship_builder

    def _determine_winner(self, outcome) -> Optional[int]:
        """Map BattleOutcome team survival → winner team_id (or None).

        A team is considered "still fighting" if it has at least one
        SURVIVED or DERELICT ship. If exactly one team is still
        fighting, it wins. Otherwise returns None (draw / both sides
        wiped).
        """
        from game.simulation.battle_outcome import ShipStatus

        alive_teams: List[int] = []
        for team in outcome.teams:
            if any(
                s.status in (ShipStatus.SURVIVED, ShipStatus.DERELICT)
                for s in team.ships
            ):
                alive_teams.append(team.team_id)
        if len(alive_teams) == 1:
            return alive_teams[0]
        return None

    def _instances_to_ships(
        self,
        instances: List[Any],
        team_id: int,
        registries: Optional['GameRegistries'],
    ) -> List[Any]:
        """Convert ShipInstances back to Ship objects for the BattleResult.

        Post-battle-hook has already updated the ShipInstances
        (component HP, removal of destroyed ships). `to_ship` reads the
        updated component state so the returned Ships reflect the
        post-battle fleet.
        """
        return [
            inst.to_ship((0.0, 0.0), team_id=team_id, registries=registries)
            for inst in instances
        ]
