"""PROJ-426 — typed assembly seam between strategy and simulation.

Replaces the four `object.__setattr__(spec, ...)` side-channels that the
spec compiler used to bolt onto the frozen `BattleSpec`. The strategy-only
state (mine_groups, owner→team map, combat_fleets, engine_ref) now lives
on a typed `BattleSpecExtensions` dataclass wrapped inside a
`StrategyBattleAssembly` alongside the immutable `BattleSpec` and the
`PreTickBattleSetupRegistry` that owns the pre-tick setup callbacks.

Phase 1 (this file's introduction) adds the DTOs and the
`build_strategy_battle_assembly(...)` orchestrator as a compat layer:
the compiler still writes the side-channels and this orchestrator reads
them back. Phase 4 deletes the side-channel writes and this orchestrator
becomes the only path for the four extension fields.

`StrategyBattleAssembler` also carries a temporary `mine_group_filter`
parameter. PROJ-431 Phase 2 (TD-10 deployable substrate redesign)
simplifies this away once mines, satellites, and fighter groups live
on a unified substrate; do not pre-collapse it here.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Callable, List, Mapping, Optional, Sequence, Tuple

if TYPE_CHECKING:
    from game.core.registry import GameRegistries
    from game.simulation.battle_spec import BattleSpec
    from game.simulation.systems.battle_end_conditions import IEndCondition
    from game.strategy.data.fleet import Fleet

from game.strategy.combat.pre_tick_setup_registry import PreTickBattleSetupRegistry


__all__ = [
    "BattleSpecExtensions",
    "StrategyBattleAssembly",
    "StrategyBattleAssembler",
    "build_strategy_battle_assembly",
]


# Default mine-group filter — partitions fleets into (combat_fleets, mine_groups).
# Lives here as a module-level default so `StrategyBattleAssembler` can carry
# it as a parameter (the temporary handoff to PROJ-431 Phase 2). Once that
# project's deployable substrate redesign lands, the filter is no longer
# needed and the parameter collapses away.
def _boundary_to_box(
    boundary: Any,
) -> Optional[Tuple[float, float, float, float]]:
    """Derive an axis-aligned scatter box from a battle boundary.

    Mirrors the helper currently on `SimulationBattleResolver`: tactical
    mine scatter takes a `(xmin, ymin, xmax, ymax)` rect. `UnboundedRegion`
    and non-rectangular boundaries fall back to `None` so the resolver
    pulls from the mine_group's stored `mine_positions`.
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
    """Partition ``fleets`` into ``(combat_fleets, mine_groups)``.

    Mine-group Fleets carry mines in a synthetic-carrier ShipInstance whose
    `layers` / `components` are empty. They participate in tactical combat
    exclusively via `TacticalMineResolver`, not as ShipSpecs on a team.
    """
    combat: List["Fleet"] = []
    mine_groups: List["Fleet"] = []
    for fleet in fleets:
        if getattr(fleet, "group_kind", "fleet") == "mine_group":
            mine_groups.append(fleet)
        else:
            combat.append(fleet)
    return combat, mine_groups


@dataclass(frozen=True)
class BattleSpecExtensions:
    """Strategy-only sidecar for a `BattleSpec`.

    Holds the data the spec compiler used to stash via
    `object.__setattr__(spec, "_<field>", value)`. Lives beside the spec
    so `BattleSpec` itself remains a frozen simulation-layer DTO.

    - `mine_groups`: filtered-out mine_group Fleets for the tactical
      `TacticalMineResolver` wiring.
    - `owner_to_team_id`: empire_id → team_id mapping used by both the
      mine resolver (for `_owner_team_id`) and the post-battle hook.
    - `combat_fleets`: the fleets that survived `_default_mine_group_filter`
      and entered team construction. Used by the fighter reboard setup.
    - `engine_ref`: mutable one-slot list inside this otherwise frozen
      dataclass. The pre-tick callback fills slot 0 with the live
      `BattleEngine` so the post-battle hook can drive `apply_reboard`.
      The frozen dataclass holds the list reference; the list itself is
      mutable. Do NOT replace the list — append to it.
    """
    mine_groups: Tuple["Fleet", ...]
    owner_to_team_id: Mapping[Any, int]
    combat_fleets: Tuple["Fleet", ...]
    engine_ref: List[Any]


@dataclass(frozen=True)
class StrategyBattleAssembly:
    """Typed wrapper bundling a battle's three artifacts.

    - `spec`: the immutable `BattleSpec` passed to `run_battle`.
    - `extensions`: the strategy-only sidecar `BattleSpecExtensions`.
    - `pre_tick_setup`: the `PreTickBattleSetupRegistry` owning ordered
      `(engine, spec) -> None` callbacks composed into the single
      `pre_tick_loop_callback` that `run_battle` accepts.
    """
    spec: "BattleSpec"
    extensions: BattleSpecExtensions
    pre_tick_setup: PreTickBattleSetupRegistry


class StrategyBattleAssembler:
    """Orchestrator that compiles fleets into a `StrategyBattleAssembly`.

    Phase 1: a thin wrapper over `build_strategy_battle_spec(...)` that
    reads the four side-channels back off the produced spec to populate
    the extensions. Phase 2-3 grow this into the canonical assembly
    pipeline (delegating to `TeamSpecBuilder`, `StrategyModifierStackBuilder`,
    `PostBattleHookBuilder`, and the `pre_tick_setup` package). Phase 4
    flips the spec/extensions ownership — extensions are populated
    directly without reading the soon-to-be-deleted side-channels.

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
        # Local import keeps the strategy-combat package free of any import
        # cycle with `spec_compiler.py`.
        from game.strategy.combat.spec_compiler import _compile_spec_with_state

        spec, state = _compile_spec_with_state(
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

        # PROJ-426 Phase 4: extensions populated directly from the
        # compiler's typed intermediate state (`_SpecCompilationState`).
        # The post-battle hook captured `state.engine_ref`, so reusing
        # that exact list reference here is essential — the pre-tick
        # reboard setup will append to it and the hook will read it.
        combat_fleets = state.combat_fleets
        mine_groups = state.mine_groups
        owner_to_team_id = state.owner_to_team_id
        engine_ref = state.engine_ref

        # Phase 3: populate the pre-tick setup registry with the mine and
        # reboard setups. The registry composes them into the single
        # `pre_tick_loop_callback` that `run_battle` accepts.
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
            battle_boundary = _boundary_to_box(spec.boundary)
            mine_setup = build_mine_resolver_setup(
                mine_groups, owner_to_team_id,
                battle_boundary=battle_boundary,
            )
            if mine_setup is not None:
                registry.register("mine", mine_setup)

        extensions = BattleSpecExtensions(
            mine_groups=tuple(mine_groups),
            owner_to_team_id=dict(owner_to_team_id),
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
    """Public functional entry point for building a `StrategyBattleAssembly`.

    Mirrors the signature of `build_strategy_battle_spec(...)`. Instantiates
    a default `StrategyBattleAssembler` and delegates to `assemble(...)`.
    Production callers (e.g., `SimulationBattleResolver`) hit this path
    once Phase 4 lands; until then, the existing `build_strategy_battle_spec`
    entry point coexists.
    """
    assembler = StrategyBattleAssembler()
    return assembler.assemble(
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
