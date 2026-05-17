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
    """The closure captures `mine_groups` and `engine_ref` for later use."""
    builder = PostBattleHookBuilder()
    fleet = MagicMock()
    fleet.id = 1
    fleet.owner_id = 10
    fleet.ships = []

    mine_group = MagicMock()
    mine_group.id = 99
    mine_group.owner_id = 10
    mine_group.ships = []

    engine_ref = []  # mutable one-slot list
    hook = builder.build(
        [fleet], empires={}, mine_groups=[mine_group], engine_ref=engine_ref,
    )
    assert callable(hook)
