"""Strategy spec compiler — fleets on a hex → BattleSpec.

PROJ-426: this module preserves the public import path
`game.strategy.combat.spec_compiler.build_strategy_battle_spec`. The
actual team / modifier / hook / mine / reboard construction lives in:

- `team_spec_builder.TeamSpecBuilder`
- `strategy_modifier_stack_builder.StrategyModifierStackBuilder`
- `post_battle_hook_builder.PostBattleHookBuilder`
- `pre_tick_setup/` (mine + reboard setup builders)
- `battle_assembly.StrategyBattleAssembler` (orchestrator)

Strategy-only state (`mine_groups`, `owner_to_team_id`, `combat_fleets`,
`engine_ref`) lives on `BattleSpecExtensions` inside
`StrategyBattleAssembly`. `BattleSpec` itself remains a frozen
simulation-layer DTO. The `_compile_spec_with_state` internal helper
surfaces the intermediate state for the assembler.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Dict, List, Mapping, Optional, Tuple

from game.simulation.battle_spec import BattleSpec
from game.simulation.combat.boundary import UnboundedRegion
from game.simulation.combat.formation import resolve_team_entry_vectors
from game.simulation.combat.telemetry import TelemetryLevel
from game.simulation.systems.battle_end_conditions import (
    TeamEliminatedCondition,
    TickLimitCondition,
)
from game.strategy.combat.post_battle_hook_builder import PostBattleHookBuilder
from game.strategy.combat.strategy_modifier_stack_builder import (
    StrategyModifierStackBuilder,
)
from game.strategy.combat.team_spec_builder import TeamSpecBuilder

if TYPE_CHECKING:
    from game.core.registry import GameRegistries
    from game.simulation.systems.battle_end_conditions import IEndCondition
    from game.strategy.data.fleet import Fleet


_DEFAULT_ABSOLUTE_MAX_TICKS = 20_000

# Issue #8: budget for the truncated `run_battle` call invoked by
# `SimulationBattleResolver` when both fleets have ships but neither has
# any combat-capable weapons. 1/10 of the normal strategy ceiling.
_BRIEF_RUN_TICK_BUDGET = _DEFAULT_ABSOLUTE_MAX_TICKS // 10


_MIN_TEAMS = 2
_MAX_TEAMS = 8


@dataclass(frozen=True)
class _SpecCompilationState:
    """Internal intermediate state surfaced by `_compile_spec_with_state`.

    `StrategyBattleAssembler` consumes this to populate
    `BattleSpecExtensions` without reaching back into the now-deleted
    `object.__setattr__(spec, ...)` side-channels. The fields here are
    the same four pieces of state that used to live as private attrs
    on `BattleSpec`; capturing them in a typed tuple keeps the
    extension surface explicit.
    """
    combat_fleets: Tuple["Fleet", ...]
    mine_groups: Tuple["Fleet", ...]
    owner_to_team_id: Dict[Any, int]
    engine_ref: List[Any]


def build_strategy_battle_spec(
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
) -> BattleSpec:
    """Public entry point — compile fleets into a `BattleSpec`."""
    spec, _state = _compile_spec_with_state(
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
    return spec


def _compile_spec_with_state(
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
) -> Tuple[BattleSpec, "_SpecCompilationState"]:
    """Compile fleets-on-hex + environment into a `BattleSpec`.

    See `Projects/active_projects/PROJ-426/design.md` for the full
    pipeline and `BattleSpecExtensions` typed-replacement plan for the
    four side-channels still written below.

    Args:
        fleets: The fleets clashing on the hex.
        empires: Optional mapping of team_id -> empire.
        settings: Optional GameSettings. Only `combat_boundary_default`
            is consulted; None falls back to `UnboundedRegion`.
        registries: GameRegistries (required for signature parity).
        seed: Optional RNG seed. `None` defaults to 0.
        end_condition: Optional custom end condition. Defaults to
            `TeamEliminatedCondition()`.
        environmental_effects: Optional `EnvironmentalEffects` object.
        team_modifiers: Optional mapping `{team_id: FleetCombatModifiers}`.
        max_ticks: Issue #8 — when supplied, overrides BOTH
            `absolute_max_ticks` AND replaces the default
            `TeamEliminatedCondition` with `TickLimitCondition(max_ticks=max_ticks)`.
    """
    _ = registries  # parity; ship construction uses InstanceBackedMaterializer.

    if empires is None:
        empires = {}

    team_builder = TeamSpecBuilder()
    modifier_builder = StrategyModifierStackBuilder()
    hook_builder = PostBattleHookBuilder()

    # PROJ-FMS-B audit Fix 2: mine_groups participate as battlefield
    # hazards via `TacticalMineResolver`, not as ShipSpecs on a team.
    combat_fleets, mine_groups = team_builder.split_mine_groups(fleets)

    # PROJ-320 Phase 3: group fleets by `owner_id` so allied fleets share
    # a team. Insertion order is canonical (Python 3.7+).
    fleets_by_owner: Dict[Any, List["Fleet"]] = {}
    for fleet in combat_fleets:
        fleets_by_owner.setdefault(fleet.owner_id, []).append(fleet)
    owner_order: List[Any] = list(fleets_by_owner.keys())

    num_teams = len(owner_order)
    if num_teams < _MIN_TEAMS or num_teams > _MAX_TEAMS:
        raise ValueError(
            f"build_strategy_battle_spec: requires {_MIN_TEAMS}..{_MAX_TEAMS} "
            f"unique combat-fleet owners; got {num_teams} from "
            f"{len(combat_fleets)} combat fleets ({len(mine_groups)} mine_groups)"
        )

    entry_vectors = resolve_team_entry_vectors(team_count=num_teams)

    teams = [
        team_builder.team_spec_for_fleet_group(
            list(fleets_by_owner[owner_id]),
            team_id=team_id,
            entry_vector=entry_vectors[team_id],
        )
        for team_id, owner_id in enumerate(owner_order)
    ]

    # PROJ-343 T1.3-combat: empire_id -> team_id mapping for ownerful
    # sector effects.
    empire_to_team_id: Dict[Any, int] = {
        owner_id: team_id for team_id, owner_id in enumerate(owner_order)
    }
    modifier_stack = modifier_builder.build(
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
            end_condition if end_condition is not None else TeamEliminatedCondition()
        )
        effective_absolute_max_ticks = _DEFAULT_ABSOLUTE_MAX_TICKS

    # PROJ-FMS-C Phase 3: shared engine ref list (mutable one-slot
    # container parked on the spec via a side-channel below).
    engine_ref: List[Any] = []
    effective_hook = post_battle_hook
    if effective_hook is None:
        effective_hook = hook_builder.build(
            combat_fleets, empires,
            mine_groups=mine_groups, engine_ref=engine_ref,
        )

    # PROJ-426 Phase 4: side-channels deleted. Strategy-only state
    # (mine_groups, owner_to_team_id, combat_fleets, engine_ref) now
    # surfaces via `_SpecCompilationState` for the assembler to thread
    # onto `BattleSpecExtensions` inside `StrategyBattleAssembly`.
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
    state = _SpecCompilationState(
        combat_fleets=tuple(combat_fleets),
        mine_groups=tuple(mine_groups),
        owner_to_team_id=dict(empire_to_team_id),
        engine_ref=engine_ref,
    )
    return spec, state


__all__ = ["build_strategy_battle_spec"]
