"""PROJ-426 Phase 3 — mine resolver pre-tick setup builder.

Lifted from `spec_compiler.py::build_mine_resolver_setup` (PROJ-FMS-B
audit Fix 2). Behavior unchanged.
"""
from __future__ import annotations

from typing import TYPE_CHECKING, Any, Callable, Dict, Mapping, Optional, Sequence, Tuple

if TYPE_CHECKING:
    from game.strategy.data.deployed_group import MineGroup


__all__ = ["build_mine_resolver_setup"]


def build_mine_resolver_setup(
    mine_groups: Sequence["MineGroup"],
    owner_to_team_id: Mapping[Any, int],
    *,
    battle_boundary: Optional[Tuple[float, float, float, float]] = None,
) -> Optional[Callable[[Any], None]]:
    """Build a `pre_tick_loop_callback` that wires mine resolvers.

    Returns a closure that, given the constructed `BattleEngine`,
    constructs a `TacticalMineResolver` per `MineGroup`, seeds its
    `_owner_team_id` from `owner_to_team_id`, attaches it to
    `engine.mine_resolvers`, and parks a back-reference on each
    `MineGroup` (`_tactical_resolver`) so the post-battle hook can call
    `writeback_to_mine_group` cleanly.

    Returns `None` when there are no `mine_groups`.
    """
    if not mine_groups:
        return None

    # Local import keeps the strategy-side module free of simulation-systems
    # dependencies at import time.
    from game.simulation.systems.tactical_mine_resolver import (
        TacticalMineResolver,
    )

    captured_groups: Tuple["MineGroup", ...] = tuple(mine_groups)
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
