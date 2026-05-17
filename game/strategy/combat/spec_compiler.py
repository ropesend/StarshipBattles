"""Strategy spec compiler — public facade.

PROJ-426 reduces this module to a thin facade. The canonical orchestrator
is `game.strategy.combat.battle_assembly.StrategyBattleAssembler.assemble`,
which returns a typed `StrategyBattleAssembly` bundling `BattleSpec`,
`BattleSpecExtensions` (strategy-only state), and `PreTickBattleSetupRegistry`.

This module exists to preserve the public import path
`game.strategy.combat.spec_compiler.build_strategy_battle_spec`. New
callers should prefer
`game.strategy.combat.battle_assembly.build_strategy_battle_assembly`
when they need access to the extensions or pre-tick setup registry.

The actual team / modifier / hook / mine / reboard construction lives in:

- `team_spec_builder.TeamSpecBuilder`
- `strategy_modifier_stack_builder.StrategyModifierStackBuilder`
- `post_battle_hook_builder.PostBattleHookBuilder`
- `pre_tick_setup/` (mine + reboard setup builders)
- `battle_assembly.StrategyBattleAssembler` (orchestrator)

`BattleSpec` itself remains a frozen simulation-layer DTO; strategy-only
extension state lives beside it on `BattleSpecExtensions`.
"""
from __future__ import annotations

from typing import TYPE_CHECKING, Any, List, Mapping, Optional

from game.simulation.battle_spec import BattleSpec
from game.strategy.combat.battle_assembly import (
    build_strategy_battle_assembly,
)

if TYPE_CHECKING:
    from game.core.registry import GameRegistries
    from game.simulation.systems.battle_end_conditions import IEndCondition
    from game.strategy.data.fleet import Fleet


# Issue #8: budget for the truncated `run_battle` call invoked by
# `SimulationBattleResolver` when both fleets have ships but neither has
# any combat-capable weapons. 1/10 of the normal strategy ceiling.
_DEFAULT_ABSOLUTE_MAX_TICKS = 20_000
_BRIEF_RUN_TICK_BUDGET = _DEFAULT_ABSOLUTE_MAX_TICKS // 10


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

    Public facade preserved for back-compat. Internally delegates to
    `StrategyBattleAssembler.assemble` and discards the extensions /
    pre-tick registry. Production callers that need access to those
    should use `build_strategy_battle_assembly` directly.

    Args:
        fleets: The fleets clashing on the hex.
        empires: Optional `{team_id|owner_id: Empire}` mapping. The
            post-battle hook uses this to prune destroyed fleets.
        settings: Optional `GameSettings`. Only `combat_boundary_default`
            is consulted; `None` falls back to `UnboundedRegion`.
        registries: Required `GameRegistries` (parity; ship construction
            uses `InstanceBackedMaterializer` end-to-end).
        seed: Optional RNG seed; `None` defaults to 0.
        end_condition: Optional custom end condition. Defaults to
            `TeamEliminatedCondition()`.
        post_battle_hook: Optional explicit hook closure. `None` lets the
            assembler attach the live strategy hook.
        environmental_effects: PROJ-300 sector-effects list.
        team_modifiers: Optional `{team_id: FleetCombatModifiers}`
            mapping translated to per-team ModifierStack entries.
        max_ticks: Issue #8 — when supplied, caps both
            `absolute_max_ticks` and the end condition.
    """
    return build_strategy_battle_assembly(
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
    ).spec


__all__ = ["build_strategy_battle_spec"]
