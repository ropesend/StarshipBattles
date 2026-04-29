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

from __future__ import annotations

import logging
from typing import Any, Dict, List, Mapping, Optional, Sequence, Tuple, TYPE_CHECKING

from game.simulation.battle_runner import run_battle
from game.strategy.interfaces.battle_resolver import BattleResult, IBattleResolver

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from game.simulation.battle_spec import BattleSpec
    from game.strategy.data.fleet import Fleet
    from game.core.registry import GameRegistries
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
        environmental_effects: Any = None,  # PROJ-300: now a sector-effects list
        empires: Optional[Mapping[int, Any]] = None,
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
            empires: BUG-126 — optional `{team_id: Empire}` mapping
                threaded into the spec compiler's `PostBattleHook` so
                empty fleets are pruned from their empire's `fleets`
                list post-battle.

        Returns:
            BattleResult with winner, tick count, and per-team survivors.
            Fleet state (ship removal, component HP updates) has already
            been written back by the compiler's post-battle hook when this
            returns.

        BUG-126: branch decisions are logged at INFO level
        (`branch=shortcut_no_capable | shortcut_sole_survivor |
        simulator`) so operators can grep `battle.log` for which path
        each strategy battle took.
        """
        fleet_list = list(fleets)
        if len(fleet_list) < 2:
            raise ValueError(
                f"SimulationBattleResolver.resolve_battle requires at least "
                f"2 fleets; got {len(fleet_list)}"
            )

        # Per-team combat-capable ship lists, indexed by team_id.
        combat_capable: Dict[int, List[Any]] = {
            tid: [s for s in fleet.ships if s.is_combat_capable()]
            for tid, fleet in enumerate(fleet_list)
        }
        teams_with_ships = [tid for tid, ships in combat_capable.items() if ships]

        # Short-circuits when not enough teams can fight.
        if len(teams_with_ships) == 0:
            logger.info(
                "Strategy battle resolved branch=shortcut_no_capable "
                "fleets=[%s]: no team has any combat-capable ships",
                ", ".join(f"Fleet {f.id}" for f in fleet_list),
            )
            return BattleResult(
                winner=None, tick_count=0,
                team_survivors={tid: [] for tid in combat_capable},
            )
        if len(teams_with_ships) == 1:
            sole_winner = teams_with_ships[0]
            logger.info(
                "Strategy battle resolved branch=shortcut_sole_survivor "
                "fleets=[%s] sole_team=%d: declared winner without simulation",
                ", ".join(f"Fleet {f.id}" for f in fleet_list),
                sole_winner,
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

        logger.info(
            "Strategy battle resolved branch=simulator "
            "fleets=[%s]: dispatching %d-team battle to run_battle",
            ", ".join(f"Fleet {f.id}" for f in fleet_list),
            len(fleet_list),
        )

        battle_seed = self._resolve_seed(seed)
        spec = self._build_spec(
            fleet_list,
            seed=battle_seed,
            registries=registries,
            environmental_effects=environmental_effects,
            modifiers=modifiers,
            empires=empires,
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

        # PROJ-312: build the replay capture context. ship_instance_lookup
        # serializes the strategy ShipInstance via ShipInstanceSerializer
        # so the captured ReplaySpec can re-materialize independently of
        # current strategy state. Phase 4's ReplayStore consumes this; if
        # no sink is registered, the context is harmless overhead.
        capture_context = self._build_capture_context(
            fleet_list, registries=registries
        )
        outcome = run_battle(
            spec,
            ai_factory=self._ai_factory,
            registry_provider=get_default_registry_provider(),
            capture_context=capture_context,
        )

        winner = self._determine_winner(outcome)
        team_survivors: Dict[int, List[Any]] = {
            tid: self._instances_to_ships(fleet.ships, tid, registries)
            for tid, fleet in enumerate(fleet_list)
        }

        # BUG-126: log per-team post-battle ship counts on a single
        # line so `battle.log` carries a complete snapshot of every
        # strategy battle. The strategy layer ignores `winner` (kept
        # for IBattleResolver-contract reasons / Combat Lab UI), so
        # log it as informational only.
        survivor_summary = ", ".join(
            f"team {tid}={len(survivors)}"
            for tid, survivors in team_survivors.items()
        )
        logger.info(
            "Strategy battle complete: ticks=%d simulator_winner=%s "
            "survivors[%s]",
            outcome.duration_ticks, winner, survivor_summary,
        )

        return BattleResult(
            winner=winner,
            tick_count=outcome.duration_ticks,
            team_survivors=team_survivors,
            # FEAT-26: thread the captured replay id up to the strategy layer
            # so `ConflictResolutionEngine` can attach it to the
            # `COMBAT_RESOLVED` event for the Event Log Replay button.
            replay_id=outcome.replay_id,
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
        environmental_effects: Any,  # PROJ-300: now a sector-effects list
        modifiers: Optional[Mapping[int, Any]],
        empires: Optional[Mapping[int, Any]] = None,
    ) -> BattleSpec:
        from game.strategy.combat.spec_compiler import build_strategy_battle_spec

        team_modifiers: Optional[Dict[int, Any]] = None
        if modifiers:
            team_modifiers = {tid: mod for tid, mod in modifiers.items() if mod is not None}
            if not team_modifiers:
                team_modifiers = None

        return build_strategy_battle_spec(
            fleets,
            empires=empires,
            registries=registries,
            seed=seed,
            environmental_effects=environmental_effects,
            team_modifiers=team_modifiers,
        )

    def _build_capture_context(
        self,
        fleets: List['Fleet'],
        *,
        registries: Optional['GameRegistries'],
    ) -> Any:
        """Build a ``ReplayCaptureContext`` for this strategy battle.

        PROJ-312: the context carries metadata + a ``ship_instance_lookup``
        callable that serializes each ``ShipInstance`` via
        ``ShipInstanceSerializer.to_dict`` so the captured ``ReplaySpec``
        can re-materialize independently of current strategy state.

        Sector / turn / empire metadata is filled in opportunistically
        from the fleet inputs; missing values are left as ``None`` /
        empty tuples (Phase 4 enriches further when integrating with the
        save lifecycle).
        """
        from datetime import datetime, timezone

        from game.simulation.replay import (
            ReplayCaptureContext,
            compute_components_registry_hash,
        )
        from game.strategy.data.ship_instance_serializer import (
            ShipInstanceSerializer,
        )

        # Empire participation by team order; tolerate fleets without an
        # empire association (orphan/AI-only).
        empires: List[str] = []
        for fleet in fleets:
            owner = getattr(fleet, "owner", None) or getattr(fleet, "empire", None)
            name = getattr(owner, "name", None) if owner is not None else None
            if name is None:
                name = getattr(fleet, "owner_name", None) or "Unknown"
            empires.append(str(name))

        # Sector — every fleet at the same hex by IBattleResolver invariant.
        sector_coords: Optional[Tuple[int, int]] = None
        sector_name: Optional[str] = None
        if fleets:
            location = getattr(fleets[0], "location", None)
            if location is not None:
                q = getattr(location, "q", None)
                r = getattr(location, "r", None)
                if q is not None and r is not None:
                    sector_coords = (int(q), int(r))
                    sector_name = f"({q}, {r})"

        # Components-registry hash — fed by Phase 6 drift-warning UI.
        components_hash = (
            compute_components_registry_hash(registries)
            if registries is not None
            else "sha256:unknown"
        )

        # ship_instance_lookup serializes the strategy ShipInstance referenced
        # by ShipSpec.instance_ref. Returns None when no instance is attached
        # (synthetic / Combat Lab / Battle Setup fixtures).
        def _lookup(ship_spec):  # type: ignore[no-redef]
            instance = getattr(ship_spec, "instance_ref", None)
            if instance is None:
                return None
            try:
                return ShipInstanceSerializer.to_dict(instance)
            except Exception:  # Intentional broad catch: capture must not crash a battle
                return None

        return ReplayCaptureContext(
            sector_name=sector_name,
            sector_coords=sector_coords,
            turn_number=None,  # Phase 4 wires the GameSession turn number
            participating_empires=tuple(empires),
            components_registry_hash=components_hash,
            captured_at=datetime.now(timezone.utc).isoformat(),
            ship_instance_lookup=_lookup,
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
