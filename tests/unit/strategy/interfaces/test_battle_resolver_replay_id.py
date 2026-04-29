"""FEAT-26 — `BattleResult.replay_id` field for cross-layer plumbing.

The strategy layer's `BattleResult` carries the replay id from
`BattleOutcome.replay_id` so `ConflictResolutionEngine` can attach it
to the `COMBAT_RESOLVED` event.
"""
from __future__ import annotations

from game.strategy.interfaces.battle_resolver import BattleResult


def test_battle_result_has_replay_id_field_default_none() -> None:
    result = BattleResult(winner=0, tick_count=10)
    assert hasattr(result, "replay_id")
    assert result.replay_id is None


def test_battle_result_replay_id_round_trips_string() -> None:
    result = BattleResult(winner=0, tick_count=10, replay_id="captured-uuid")
    assert result.replay_id == "captured-uuid"
