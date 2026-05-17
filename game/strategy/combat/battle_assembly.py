"""PROJ-426 + PROJ-431 — typed assembly seam between strategy and simulation.

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

PROJ-431 Phase 2: the temporary `mine_group_filter` parameter is
DELETED. Mines now live on `empire.deployed_groups` as typed
:class:`MineGroup` instances and arrive at the assembler through the
``empires`` mapping (the same map the post-battle hook already
consults). Combat fleets and mine groups are now structurally
distinct collections — no string-discriminator partitioning step.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Dict, List, Mapping, Optional, Sequence, Tuple

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
from game.strategy.data.deployed_group import MineGroup

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


def _collect_mine_groups_at_hex(
    combat_fleets: Sequence["Fleet"],
    empires: Mapping[Any, Any],
) -> List[MineGroup]:
    """Collect MineGroups co-located with any combat fleet.

    PROJ-431 Phase 2: mines no longer live in ``empire.fleets``; they
    live in ``empire.deployed_groups``. The assembler walks the union
    of empires referenced by ``combat_fleets`` (resolved via the
    ``empires`` mapping) and pulls every :class:`MineGroup` at a hex
    one of the combat fleets occupies.
    """
    if not combat_fleets:
        return []
    target_hexes = {f.location for f in combat_fleets}
    seen_empire_ids: set = set()
    seen_group_ids: set = set()
    collected: List[MineGroup] = []
    for empire in empires.values():
        # Dedupe empires by ``id(...)`` rather than via ``set(...)`` so
        # callers that pass un-hashable ``SimpleNamespace`` stubs work.
        if id(empire) in seen_empire_ids:
            continue
        seen_empire_ids.add(id(empire))
        deployed = getattr(empire, "deployed_groups", None) or ()
        for group in deployed:
            if not isinstance(group, MineGroup):
                continue
            if group.location not in target_hexes:
                continue
            if id(group) in seen_group_ids:
                continue
            seen_group_ids.add(id(group))
            collected.append(group)
    return collected


@dataclass(frozen=True)
class BattleSpecExtensions:
    """Strategy-only sidecar for a `BattleSpec`.

    - `mine_groups`: typed :class:`MineGroup` instances co-located with
      the battle, wired into ``TacticalMineResolver`` setup.
    - `owner_to_team_id`: empire_id -> team_id mapping used by both the
      mine resolver (for `_owner_team_id`) and the post-battle hook.
    - `combat_fleets`: the fleets that entered team construction. Used
      by the fighter reboard setup.
    - `engine_ref`: mutable one-slot list inside this otherwise frozen
      dataclass. The pre-tick reboard callback appends the live
      `BattleEngine` to it so the post-battle hook can drive
      `apply_reboard`. The frozen dataclass holds the list reference;
      the list itself is mutable. Do NOT replace the list — append.
    """
    mine_groups: Tuple[MineGroup, ...]
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

    PROJ-431 Phase 2: the temporary ``mine_group_filter`` parameter is
    DELETED. Mines live on ``empire.deployed_groups`` as typed
    :class:`MineGroup` instances and are gathered from the ``empires``
    mapping directly — no partition step on ``fleets``.
    """

    def __init__(self) -> None:
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
        del registries  # parity; ship construction uses InstanceBackedMaterializer.

        if empires is None:
            empires = {}

        # PROJ-431 Phase 2: every entry in ``fleets`` is a real combat
        # fleet. Mines arrive as typed ``MineGroup``s on
        # ``empire.deployed_groups`` and are collected separately.
        combat_fleets = list(fleets)
        mine_groups = _collect_mine_groups_at_hex(combat_fleets, empires)

        # Single source of truth for owner-order and owner->team mapping.
        # `PostBattleHookBuilder` and `BattleSpecExtensions.owner_to_team_id`
        # both receive the SAME dict object — never re-derive locally.
        fleets_by_owner, owner_order = self._team_builder.group_fleets_by_owner(
            combat_fleets
        )

        num_teams = len(owner_order)
        if num_teams < _MIN_TEAMS or num_teams > _MAX_TEAMS:
            raise ValueError(
                f"StrategyBattleAssembler.assemble: requires "
                f"{_MIN_TEAMS}..{_MAX_TEAMS} unique combat-fleet owners; "
                f"got {num_teams} from {len(combat_fleets)} combat fleets "
                f"({len(mine_groups)} MineGroups)"
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
                owner_to_team_id=empire_to_team_id,
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
            # Identity, NOT a copy: the same dict instance is captured by
            # PostBattleHookBuilder above so the two stay in lockstep.
            owner_to_team_id=empire_to_team_id,
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
