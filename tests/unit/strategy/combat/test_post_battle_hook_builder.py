"""PROJ-426 Phase 2 — tests for `PostBattleHookBuilder`.

Pins the closure-construction contract; deeper writeback behavior is
still covered by `test_post_battle_hook.py`.
"""
from __future__ import annotations

from unittest.mock import MagicMock

from game.strategy.combat.post_battle_hook_builder import PostBattleHookBuilder


def test_build_hook_returns_callable():
    """`PostBattleHookBuilder.build` returns a single-arg callable."""
    builder = PostBattleHookBuilder()
    fleet = MagicMock()
    fleet.id = 1
    fleet.owner_id = 10
    fleet.ships = []

    hook = builder.build([fleet], empires={})
    assert callable(hook)


def test_build_hook_with_empty_inputs_returns_no_op_safe_closure():
    """The closure must not raise when invoked with a minimal outcome."""
    builder = PostBattleHookBuilder()
    hook = builder.build([], empires={})

    outcome = MagicMock()
    outcome.teams = []
    # Should not raise — captured mine_groups is empty + no engine_ref means
    # neither reboard nor writeback iterates over anything meaningful.
    hook(outcome)


def test_build_hook_threads_mine_groups_and_engine_ref():
    """The closure must actually exercise the captured mine_groups and
    engine_ref when invoked — pinning observable behavior, not just the
    fact that ``build`` returns a callable."""
    builder = PostBattleHookBuilder()
    fleet = MagicMock()
    fleet.id = 1
    fleet.owner_id = 10
    fleet.ships = []

    # Mine group with a tactical resolver — the closure should call its
    # writeback_to_mine_group then delattr the resolver. Use real attributes
    # rather than MagicMock auto-attrs so delattr is observable.
    class _StubMineGroup:
        def __init__(self) -> None:
            self.id = 99
            self.owner_id = 10
            self.ships: list = []
            self.mines = ["m1"]  # has inventory -> should NOT be pruned
            self._tactical_resolver = MagicMock()

    mine_group = _StubMineGroup()

    # Empty engine_ref => the reboard branch must be skipped (no engine to
    # call apply_reboard on). Verify this by ensuring the closure does not
    # raise even though apply_reboard would fail on an empty list.
    engine_ref: list = []

    # Empire stub so the mine_group prune step has somewhere to look — but
    # since the mine_group still has inventory, it must remain in
    # deployed_groups after the hook runs.
    empire = MagicMock()
    empire.deployed_groups = [mine_group]

    hook = builder.build(
        [fleet],
        empires={10: empire},
        mine_groups=[mine_group],
        engine_ref=engine_ref,
    )

    outcome = MagicMock()
    outcome.teams = []

    # Behavioral checks: invoking the hook must drive writeback on the
    # mine_group resolver and must drop the captured resolver reference.
    resolver_mock = mine_group._tactical_resolver
    hook(outcome)

    resolver_mock.writeback_to_mine_group.assert_called_once_with(mine_group)
    assert not hasattr(mine_group, "_tactical_resolver"), (
        "Hook should delattr _tactical_resolver after writeback."
    )
    # Mine group still has inventory => empire.deployed_groups untouched.
    assert mine_group in empire.deployed_groups
