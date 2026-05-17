"""PROJ-426 — `PostBattleHookBuilder`.

Owns the strategy post-battle hook closure construction lifted from
`spec_compiler.py::_build_strategy_post_battle_hook`. Behavior is
unchanged from the original helper — this extraction is structural only.

The closure built here:
1. Calls `apply_reboard` (when the captured `engine_ref` has been filled
   by the pre-tick reboard setup callback) so mid-battle launched
   fighters land back in friendly bays / overflow into sector
   fighter_groups before the empty-fleet prune.
2. Calls `apply_outcome_to_fleets` to write component HP / removal back
   into `ShipInstance.components`.
3. Drives `TacticalMineResolver.writeback_to_mine_group` for each
   participating mine_group, then prunes any mine_group that ended the
   battle empty.
"""
from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any, Callable, Dict, List, Mapping, Optional, Sequence, Tuple

if TYPE_CHECKING:
    from game.strategy.data.deployed_group import MineGroup
    from game.strategy.data.fleet import Fleet


__all__ = ["PostBattleHookBuilder"]


class PostBattleHookBuilder:
    """Build the strategy post-battle hook closure."""

    def build(
        self,
        fleets: List["Fleet"],
        empires: Mapping[Any, Any],
        *,
        mine_groups: Optional[Sequence["MineGroup"]] = None,
        engine_ref: Optional[List[Any]] = None,
        owner_to_team_id: Optional[Mapping[Any, int]] = None,
    ) -> Callable[[Any], None]:
        """Create the post-battle hook closure for a battle.

        ``owner_to_team_id`` is the canonical owner->team mapping computed
        once by the assembler (`TeamSpecBuilder.compute_owner_to_team_id`).
        Passing the same mapping object here keeps the assembler and the
        post-battle hook in lockstep — the alternative (re-deriving the
        mapping from ``fleets``) is the drift surface flagged by the
        Codex Phase 6 consult.

        For back-compat with callers that pre-date the kwarg (tests that
        construct the hook directly without an assembler), ``None`` falls
        back to re-deriving the mapping from ``fleets`` using the same
        insertion-order rule the assembler uses.
        """
        from game.strategy.combat.post_battle_hook import apply_outcome_to_fleets

        owner_to_fleets: Dict[Any, List["Fleet"]] = {}
        for fleet in fleets:
            owner_to_fleets.setdefault(fleet.owner_id, []).append(fleet)

        if owner_to_team_id is None:
            # Back-compat fallback: re-derive using the same insertion-order
            # rule the assembler applies. Production callers (the assembler)
            # always pass the canonical mapping; this path only fires for
            # legacy direct-construction tests.
            owner_to_team_id = {
                owner_id: team_id
                for team_id, owner_id in enumerate(owner_to_fleets.keys())
            }

        fleets_by_team_id: Dict[int, List["Fleet"]] = {
            owner_to_team_id[owner_id]: list(owner_fleets)
            for owner_id, owner_fleets in owner_to_fleets.items()
            if owner_id in owner_to_team_id
        }
        empires_by_team_id: Dict[int, Any] = {}
        for owner_id, team_id in owner_to_team_id.items():
            empire = empires.get(team_id)
            if empire is None:
                empire = empires.get(owner_id)
            if empire is not None:
                empires_by_team_id[team_id] = empire

        captured_mine_groups: Tuple["MineGroup", ...] = tuple(mine_groups or ())
        captured_engine_ref: List[Any] = (
            engine_ref if engine_ref is not None else []
        )
        captured_owner_to_fleets: Dict[Any, List["Fleet"]] = dict(owner_to_fleets)
        captured_empires_by_owner: Dict[Any, Any] = {}
        for owner_id in owner_to_team_id.keys():
            emp = empires.get(owner_id)
            if emp is not None:
                captured_empires_by_owner[owner_id] = emp

        def _hook(outcome) -> None:
            if captured_engine_ref:
                from game.simulation.systems.fighter_reboard import apply_reboard
                try:
                    apply_reboard(
                        engine=captured_engine_ref[0],
                        participating_fleets_by_owner=captured_owner_to_fleets,
                        empires_by_owner=captured_empires_by_owner,
                    )
                except Exception:  # Intentional broad catch: reboard failures must not break post-battle persistence; log + continue.
                    logging.getLogger(__name__).exception(
                        "fighter_reboard.apply_reboard raised during "
                        "post-battle hook"
                    )

            apply_outcome_to_fleets(
                outcome,
                fleets_by_team_id=fleets_by_team_id,
                empires=empires_by_team_id or None,
            )

            for mg in captured_mine_groups:
                resolver = getattr(mg, "_tactical_resolver", None)
                if resolver is None:
                    continue
                try:
                    resolver.writeback_to_mine_group(mg)
                except Exception:  # Intentional broad catch: writeback failures must not break post-battle persistence.
                    logging.getLogger(__name__).exception(
                        "TacticalMineResolver.writeback_to_mine_group raised "
                        "for mine_group %s; continuing.",
                        getattr(mg, "id", "?"),
                    )
                try:
                    delattr(mg, "_tactical_resolver")
                except AttributeError:
                    pass

            for mg in captured_mine_groups:
                if not _mine_group_has_inventory(mg):
                    # PROJ-431 Phase 2: mine groups live in
                    # ``empire.deployed_groups``, not ``empire.fleets``.
                    for empire in empires_by_team_id.values():
                        deployed = getattr(empire, "deployed_groups", None)
                        if deployed is None:
                            continue
                        if mg in deployed:
                            deployed.remove(mg)
                            break

        return _hook


def _mine_group_has_inventory(mine_group: Any) -> bool:
    """True iff the ``MineGroup`` still has at least one mine."""
    return bool(getattr(mine_group, "mines", None))
