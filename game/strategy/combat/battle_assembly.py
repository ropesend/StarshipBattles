"""PROJ-426 — typed assembly seam between strategy and simulation.

`StrategyBattleAssembler.assemble(...)` is the canonical orchestrator
for turning fleets on a hex into a battle. It returns a
`StrategyBattleAssembly` bundling:

- `spec: BattleSpec` — the immutable simulation-layer DTO passed to
  `run_battle`.
- `extensions: BattleSpecExtensions` — typed sidecar holding the four
  pieces of strategy-only state (`mine_groups`, `owner_to_team_id`,
  `combat_fleets`, `engine_ref`) that used to be parked on the spec via
  `object.__setattr__(spec, ...)`.
- `pre_tick_setup: PreTickBattleSetupRegistry` — composes the mine +
  reboard setup callbacks into the single `pre_tick_loop_callback`
  `run_battle` accepts.

`StrategyBattleAssembler` also carries a temporary `mine_group_filter`
parameter. PROJ-431 Phase 2 (TD-10 deployable substrate redesign)
simplifies this away once mines, satellites, and fighter groups live
on a unified substrate; do not pre-collapse it here.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Callable, Dict, List, Mapping, Optional, Sequence, Tuple

from game.simulation.battle_spec import BattleSpec
from game.simulation.combat.boundary import UnboundedRegion
from game.simulation.combat.formation import resolve_team_entry_vectors
from game.simulation.combat.telemetry import TelemetryLevel
from game.simulation.systems.battle_end_conditions import (
    TeamEliminatedCondition,
    TickLimitCondition,
)
from game.strategy.combat.post_battle_hook_builder import PostBattleHookBuilder
from game.strategy.combat.pre_tick_setup_registry import PreTickBattleSetupRegistry
from game.strategy.combat.strategy_modifier_stack_builder import (
    StrategyModifierStackBuilder,
)
from game.strategy.combat.team_spec_builder import TeamSpecBuilder

if TYPE_CHECKING:
    from game.core.registry import GameRegistries
    from game.simulation.systems.battle_end_conditions import IEndCondition
    from game.strategy.data.fleet import Fleet


__all__ = [
    "BattleSpecExtensions",
    "StrategyBattleAssembly",
    "StrategyBattleAssembler",
    "build_strategy_battle_assembly",
]


_DEFAULT_ABSOLUTE_MAX_TICKS = 20_000
_MIN_TEAMS = 2
_MAX_TEAMS = 8


def _boundary_to_box(
    boundary: Any,
) -> Optional[Tuple[float, float, float, float]]:
    """Derive an axis-aligned scatter box from a battle boundary.

    Tactical mine scatter takes a `(xmin, ymin, xmax, ymax)` rect.
    `UnboundedRegion` and non-rectangular boundaries fall back to `None`
    so the resolver pulls from the mine_group's stored `mine_positions`.
    """
    if boundary is None:
        return None
    radius = getattr(boundary, "radius", None)
    if radius is not None:
        r = float(radius)
        return (-r, -r, r, r)
    bounds = getattr(boundary, "bounds", None)
    if bounds is not None and len(bounds) == 4:
        return tuple(float(v) for v in bounds)  # type: ignore[return-value]
    return None


def _default_mine_group_filter(
    fleets: Sequence["Fleet"],
) -> Tuple[List["Fleet"], List["Fleet"]]:
    """Partition `fleets` into `(combat_fleets, mine_groups)`.

    Mine-group Fleets carry mines in a synthetic-carrier ShipInstance whose
    `layers` / `components` are empty. They participate in tactical combat
    exclusively via `TacticalMineResolver`, not as ShipSpecs on a team.
    """
    return TeamSpecBuilder().split_mine_groups(fleets)


@dataclass(frozen=True)
class BattleSpecExtensions:
    """Strategy-only sidecar for a `BattleSpec`.

    - `mine_groups`: filtered-out mine_group Fleets for the tactical
      `TacticalMineResolver` wiring.
    - `owner_to_team_id`: empire_id -> team_id mapping used by both the
      mine resolver (for `_owner_team_id`) and the post-battle hook.
    - `combat_fleets`: the fleets that survived the mine-group filter
      and entered team construction. Used by the fighter reboard setup.
    - `engine_ref`: mutable one-slot list inside this otherwise frozen
      dataclass. The pre-tick reboard callback appends the live
      `BattleEngine` to it so the post-battle hook can drive
      `apply_reboard`. The frozen dataclass holds the list reference;
      the list itself is mutable. Do NOT replace the list — append.
    """
    mine_groups: Tuple["Fleet", ...]
    owner_to_team_id: Mapping[Any, int]
    combat_fleets: Tuple["Fleet", ...]
    engine_ref: List[Any]


@dataclass(frozen=True)
class StrategyBattleAssembly:
    """Typed wrapper bundling a battle's three artifacts."""
    spec: BattleSpec
    extensions: BattleSpecExtensions
    pre_tick_setup: PreTickBattleSetupRegistry


class StrategyBattleAssembler:
    """Orchestrator that compiles fleets into a `StrategyBattleAssembly`.

    The `mine_group_filter` parameter is the explicit temporary handoff
    to PROJ-431 Phase 2: that project's deployable substrate redesign
    simplifies the filter away once mines/satellites/fighters live on a
    unified substrate. Do not pre-collapse it here.
    """

    def __init__(
        self,
        *,
        mine_group_filter: Optional[
            Callable[[Sequence["Fleet"]], Tuple[List["Fleet"], List["Fleet"]]]
        ] = None,
    ) -> None:
        self._mine_group_filter = mine_group_filter or _default_mine_group_filter
        self._team_builder = TeamSpecBuilder()
        self._modifier_builder = StrategyModifierStackBuilder()
        self._hook_builder = PostBattleHookBuilder()

    def assemble(
        self,
        fleets: List["Fleet"],
        *,
        empires: Optional[Mapping[Any, Any]] = None,
        settings: Any = None,
        registries: "GameRegistries",
        seed: Optional[int] = None,
        end_condition: Optional["IEndCondition"] = None,
        post_battle_hook: Optional[Any] = None,
        environmental_effects: Any = None,
        team_modifiers: Optional[Mapping[int, Any]] = None,
        max_ticks: Optional[int] = None,
    ) -> StrategyBattleAssembly:
        _ = registries  # parity; ship construction uses InstanceBackedMaterializer.

        if empires is None:
            empires = {}

        combat_fleets, mine_groups = self._mine_group_filter(fleets)

        fleets_by_owner: Dict[Any, List["Fleet"]] = {}
        for fleet in combat_fleets:
            fleets_by_owner.setdefault(fleet.owner_id, []).append(fleet)
        owner_order: List[Any] = list(fleets_by_owner.keys())

        num_teams = len(owner_order)
        if num_teams < _MIN_TEAMS or num_teams > _MAX_TEAMS:
            raise ValueError(
                f"StrategyBattleAssembler.assemble: requires "
                f"{_MIN_TEAMS}..{_MAX_TEAMS} unique combat-fleet owners; "
                f"got {num_teams} from {len(combat_fleets)} combat fleets "
                f"({len(mine_groups)} mine_groups)"
            )

        entry_vectors = resolve_team_entry_vectors(team_count=num_teams)
        teams = [
            self._team_builder.team_spec_for_fleet_group(
                list(fleets_by_owner[owner_id]),
                team_id=team_id,
                entry_vector=entry_vectors[team_id],
            )
            for team_id, owner_id in enumerate(owner_order)
        ]

        empire_to_team_id: Dict[Any, int] = {
            owner_id: team_id for team_id, owner_id in enumerate(owner_order)
        }
        modifier_stack = self._modifier_builder.build(
            team_count=len(teams),
            environmental_effects=environmental_effects,
            team_modifiers=team_modifiers,
            empire_to_team_id=empire_to_team_id,
        )

        boundary = None
        if settings is not None:
            boundary = getattr(settings, "combat_boundary_default", None)
        if boundary is None:
            boundary = UnboundedRegion()

        if max_ticks is not None:
            effective_end_condition: "IEndCondition" = TickLimitCondition(
                max_ticks=max_ticks
            )
            effective_absolute_max_ticks = max_ticks
        else:
            effective_end_condition = (
                end_condition if end_condition is not None
                else TeamEliminatedCondition()
            )
            effective_absolute_max_ticks = _DEFAULT_ABSOLUTE_MAX_TICKS

        # Shared engine_ref: post-battle hook captures it; pre-tick reboard
        # setup appends the live BattleEngine to slot 0; same list lives on
        # `BattleSpecExtensions.engine_ref` so the adapter / tests can read.
        engine_ref: List[Any] = []
        effective_hook = post_battle_hook
        if effective_hook is None:
            effective_hook = self._hook_builder.build(
                combat_fleets, empires,
                mine_groups=mine_groups, engine_ref=engine_ref,
            )

        spec = BattleSpec(
            seed=seed if seed is not None else 0,
            telemetry_level=TelemetryLevel.NORMAL,
            boundary=boundary,
            end_condition=effective_end_condition,
            absolute_max_ticks=effective_absolute_max_ticks,
            teams=tuple(teams),
            modifier_stack=modifier_stack,
            post_battle_hook=effective_hook,
        )

        # Populate the pre-tick setup registry with the mine and reboard
        # setups. `composed_callback()` will return None when both setups
        # are absent (e.g., synthetic test fleets).
        registry = PreTickBattleSetupRegistry()
        if combat_fleets:
            from game.strategy.combat.pre_tick_setup import (
                build_fighter_reboard_setup,
            )
            reboard_setup = build_fighter_reboard_setup(
                combat_fleets, engine_ref=engine_ref,
            )
            if reboard_setup is not None:
                registry.register("reboard", reboard_setup)
        if mine_groups:
            from game.strategy.combat.pre_tick_setup import (
                build_mine_resolver_setup,
            )
            mine_setup = build_mine_resolver_setup(
                mine_groups, empire_to_team_id,
                battle_boundary=_boundary_to_box(boundary),
            )
            if mine_setup is not None:
                registry.register("mine", mine_setup)

        extensions = BattleSpecExtensions(
            mine_groups=tuple(mine_groups),
            owner_to_team_id=dict(empire_to_team_id),
            combat_fleets=tuple(combat_fleets),
            engine_ref=engine_ref,
        )

        return StrategyBattleAssembly(
            spec=spec,
            extensions=extensions,
            pre_tick_setup=registry,
        )


def build_strategy_battle_assembly(
    fleets: List["Fleet"],
    *,
    empires: Optional[Mapping[Any, Any]] = None,
    settings: Any = None,
    registries: "GameRegistries",
    seed: Optional[int] = None,
    end_condition: Optional["IEndCondition"] = None,
    post_battle_hook: Optional[Any] = None,
    environmental_effects: Any = None,
    team_modifiers: Optional[Mapping[int, Any]] = None,
    max_ticks: Optional[int] = None,
) -> StrategyBattleAssembly:
    """Public functional entry — instantiate a default assembler and assemble."""
    return StrategyBattleAssembler().assemble(
        fleets,
        empires=empires,
        settings=settings,
        registries=registries,
        seed=seed,
        end_condition=end_condition,
        post_battle_hook=post_battle_hook,
        environmental_effects=environmental_effects,
        team_modifiers=team_modifiers,
        max_ticks=max_ticks,
    )
