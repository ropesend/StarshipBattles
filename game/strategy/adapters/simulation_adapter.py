"""SimulationBattleResolver - Strategy-to-simulation adapter.

PROJ-11 Phase 4: Interface Contracts.
PROJ-275 Phase 7: signature widened to accept N fleets.

This adapter bridges the strategy layer's `IBattleResolver` interface
to the simulation layer's unified `run_battle(spec) -> BattleOutcome`
entry. It translates fleets into a `BattleSpec` via the strategy spec
compiler, runs the battle, and reports the outcome as a `BattleResult`.

PROJ-269 Phase 6 Tasks 6.5 + 6.11:
  - The legacy `BattleController` + `BattleConfig` + `run_headless`
    path was replaced with `build_strategy_battle_spec` + `run_battle`.
  - Environmental and team modifiers flow through `ModifierStack` entries
    emitted by the compiler (placeholder effects per Phase 5.5 semantics).
  - Fleet updates happen via `PostBattleHook` (attached by the compiler)
    during `run_battle` — callers treat `BattleResult` as a read-only
    report. `FleetBattleAdapter.update_from_battle_results` is deleted.
"""

import logging
from typing import Any, Dict, List, Mapping, Optional, Sequence, TYPE_CHECKING

from game.simulation.battle_runner import run_battle
from game.strategy.interfaces.battle_resolver import BattleResult, IBattleResolver

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

    PROJ-275 Phase 7: native N-fleet support. A 2-fleet call still
    works; 3+ fleets share one battle instead of being decomposed into
    sequential pairs.
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
        fleets: Sequence['Fleet'],
        modifiers: Optional[Mapping[int, Any]] = None,
        seed: Optional[int] = None,
        registries: Optional['GameRegistries'] = None,
        environmental_effects: Optional['EnvironmentalEffects'] = None,
    ) -> BattleResult:
        """Resolve a battle between N fleets via the unified entry.

        Args:
            fleets: Two or more fleets. Position determines team_id —
                `fleets[i]` is assigned to team `i`.
            modifiers: Optional `{team_id: FleetCombatModifiers}` mapping
                of per-team strategic modifiers. Flows into the
                BattleSpec's ModifierStack as per-team entries.
            seed: Optional random seed for deterministic battles.
            registries: Optional GameRegistries for DI. If None, the
                underlying `ShipInstance.to_ship` uses the global
                default registry provider.
            environmental_effects: Optional sector/hex environmental
                effects (storm shield interference). Flows into the
                BattleSpec's ModifierStack as global entries.

        Returns:
            BattleResult with winner, tick count, and per-team survivors.
            Fleet state (ship removal, component HP updates) has already
            been written back by the compiler's post-battle hook when this
            returns.
        """
        fleet_list = list(fleets)
        if len(fleet_list) < 2:
            raise ValueError(
                f"SimulationBattleResolver.resolve_battle requires at least "
                f"2 fleets; got {len(fleet_list)}"
            )

        logger.info(
            f"Simulating {len(fleet_list)}-team battle: "
            + " vs ".join(f"Fleet {f.id}" for f in fleet_list)
        )

        # Per-team combat-capable ship lists, indexed by team_id.
        combat_capable: Dict[int, List[Any]] = {
            tid: [s for s in fleet.ships if s.is_combat_capable()]
            for tid, fleet in enumerate(fleet_list)
        }
        teams_with_ships = [tid for tid, ships in combat_capable.items() if ships]

        # Short-circuits when not enough teams can fight.
        if len(teams_with_ships) == 0:
            logger.warning("No team has any combat-capable ships")
            return BattleResult(
                winner=None, tick_count=0,
                team_survivors={tid: [] for tid in combat_capable},
            )
        if len(teams_with_ships) == 1:
            sole_winner = teams_with_ships[0]
            logger.warning(
                f"Only team {sole_winner} has combat-capable ships; "
                f"declared winner without simulation"
            )
            survivors = {
                tid: (
                    self._instances_to_ships(combat_capable[tid], tid, registries)
                    if tid == sole_winner else []
                )
                for tid in combat_capable
            }
            return BattleResult(
                winner=sole_winner, tick_count=0, team_survivors=survivors
            )

        battle_seed = self._resolve_seed(seed)
        spec = self._build_spec(
            fleet_list,
            seed=battle_seed,
            registries=registries,
            environmental_effects=environmental_effects,
            modifiers=modifiers,
        )
        # PROJ-274: no ship_builder closure needed. The strategy compiler
        # sets `ShipSpec.instance_ref = ship_instance` on each spec; the
        # default InstanceBackedMaterializer (context-registered) reads
        # it via duck typing and calls `instance.to_ship(...)`.
        # `run_battle` invokes the compiler's `PostBattleHook` which
        # writes outcome data back into the ShipInstances and prunes
        # destroyed/retreated ships from the fleets.
        # PROJ-306: pass `registry_provider` explicitly — the Strategy
        # layer is allowed to call `get_default_registry_provider()`;
        # the Simulation layer cannot.
        from game.core.registry import get_default_registry_provider
        outcome = run_battle(
            spec,
            ai_factory=self._ai_factory,
            registry_provider=get_default_registry_provider(),
        )

        winner = self._determine_winner(outcome)
        team_survivors: Dict[int, List[Any]] = {
            tid: self._instances_to_ships(fleet.ships, tid, registries)
            for tid, fleet in enumerate(fleet_list)
        }

        logger.info(
            f"Battle complete: winner={winner}, ticks={outcome.duration_ticks}"
        )
        for tid, survivors in team_survivors.items():
            logger.info(f"  Team {tid} survivors: {len(survivors)}")

        return BattleResult(
            winner=winner,
            tick_count=outcome.duration_ticks,
            team_survivors=team_survivors,
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
        fleets: List['Fleet'],
        *,
        seed: int,
        registries: Optional['GameRegistries'],
        environmental_effects: Optional['EnvironmentalEffects'],
        modifiers: Optional[Mapping[int, Any]],
    ):
        from game.strategy.combat.spec_compiler import build_strategy_battle_spec

        team_modifiers: Optional[Dict[int, Any]] = None
        if modifiers:
            team_modifiers = {tid: mod for tid, mod in modifiers.items() if mod is not None}
            if not team_modifiers:
                team_modifiers = None

        return build_strategy_battle_spec(
            fleets,
            registries=registries,
            seed=seed,
            environmental_effects=environmental_effects,
            team_modifiers=team_modifiers,
        )

    def _determine_winner(self, outcome) -> Optional[int]:
        """Map BattleOutcome team survival → winner team_id (or None).

        A team is considered "still fighting" if it has at least one
        SURVIVED or DERELICT ship. If exactly one team is still
        fighting, it wins. Otherwise returns None (draw / all wiped).
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
