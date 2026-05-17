"""Strategy spec compiler — fleets on a hex → BattleSpec.

PROJ-426: post extraction, this module is a thinning facade. The actual
team / modifier / hook / mine / reboard construction lives in:

- `team_spec_builder.TeamSpecBuilder`
- `strategy_modifier_stack_builder.StrategyModifierStackBuilder`
- `post_battle_hook_builder.PostBattleHookBuilder`
- `pre_tick_setup/` (Phase 3 lands the mine + reboard setups here)
- `battle_assembly.StrategyBattleAssembler` (orchestrator)

This file preserves the public import path
`game.strategy.combat.spec_compiler.build_strategy_battle_spec` and —
through Phase 3 — still writes the four `object.__setattr__(spec, ...)`
side-channels so the adapter can read them. Phase 4 removes those writes
and Phase 5 shrinks this file to the orchestration-only target
(<= 120 LOC).

PROJ-FMS-B / PROJ-FMS-C history: the side-channels carry `_mine_groups`,
`_owner_to_team_id`, `_engine_ref`, and `_combat_fleets` — see
`Projects/active_projects/PROJ-426/design.md` for the typed-replacement
plan via `BattleSpecExtensions`.
"""
from __future__ import annotations

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
    # PROJ-426 Phase 1-3 compat: the four side-channels remain written
    # so the adapter (until Phase 4) can read them. PROJ-426 Phase 4
    # deletes these four writes and the adapter consumes
    # `BattleSpecExtensions` via `StrategyBattleAssembly` instead.
    object.__setattr__(spec, "_mine_groups", tuple(mine_groups))
    object.__setattr__(spec, "_owner_to_team_id", dict(empire_to_team_id))
    object.__setattr__(spec, "_engine_ref", engine_ref)
    object.__setattr__(spec, "_combat_fleets", tuple(combat_fleets))
    return spec


def build_fighter_reboard_setup(
    participating_fleets: Sequence["Fleet"],
    *,
    engine_ref: Optional[List[Any]] = None,
) -> Optional[Callable[[Any], None]]:
    """Build a ``pre_tick_loop_callback`` that installs a reboard tracker.

    PROJ-FMS-C Phase 3 — kept here temporarily during the Phase 2 split.
    Phase 3 moves the implementation under
    `game/strategy/combat/pre_tick_setup/reboard_setup.py` and removes
    this function from `spec_compiler.py`.
    """
    if not participating_fleets:
        return None

    from game.simulation.systems.fighter_reboard import ReboardTracker

    captured_engine_ref = engine_ref

    def _setup(engine: Any) -> None:
        tracker = ReboardTracker(battle_id=id(engine))
        try:
            setattr(engine, "reboard_tracker", tracker)
        except (AttributeError, TypeError):
            pass
        if captured_engine_ref is not None:
            captured_engine_ref.append(engine)

    return _setup


def build_mine_resolver_setup(
    mine_groups: Sequence["Fleet"],
    owner_to_team_id: Mapping[Any, int],
    *,
    battle_boundary: Optional[Tuple[float, float, float, float]] = None,
) -> Optional[Callable[[Any], None]]:
    """Build a ``pre_tick_loop_callback`` that wires mine resolvers.

    PROJ-FMS-B audit Fix 2 — kept here temporarily during the Phase 2
    split. Phase 3 moves the implementation under
    `game/strategy/combat/pre_tick_setup/mine_setup.py` and removes
    this function from `spec_compiler.py`.
    """
    if not mine_groups:
        return None

    from game.simulation.systems.tactical_mine_resolver import (
        TacticalMineResolver,
    )

    captured_groups: Tuple["Fleet", ...] = tuple(mine_groups)
    captured_owner_map: Dict[Any, int] = dict(owner_to_team_id)
    captured_boundary = battle_boundary

    def _setup(engine: Any) -> None:
        for mg in captured_groups:
            owner_id = getattr(mg, "owner_id", None)
            if owner_id not in captured_owner_map:
                continue
            resolver = TacticalMineResolver.from_mine_group(
                mg, battle_boundary=captured_boundary,
            )
            resolver._owner_team_id = captured_owner_map[owner_id]
            engine.mine_resolvers.append(resolver)
            try:
                setattr(mg, "_tactical_resolver", resolver)
            except (AttributeError, TypeError):
                pass

    return _setup


__all__ = [
    "build_strategy_battle_spec",
    "build_mine_resolver_setup",
    "build_fighter_reboard_setup",
]
