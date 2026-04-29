"""FEAT-26 — `replay_id` is threaded into the COMBAT_RESOLVED event.

`ConflictResolutionEngine._resolve_combat_at_hex` reads the
`BattleResult.replay_id` returned by the battle resolver and forwards
it through `_log_combat_result -> event_bus.log_event(... replay_id=...)`.

`Event.details=kwargs` (in `GameSession._create_event_handler`) carries
the kwarg into save serialization automatically, so older saves load
fine: events without the key resolve to `details.get("replay_id") -> None`.
"""
from __future__ import annotations

from unittest.mock import MagicMock

from game.core.event_logging import EventBus
from game.strategy.events import EventType
from game.strategy.interfaces.battle_resolver import BattleResult


def _capture_calls():
    calls = []

    def _fake(event_type, **kwargs):
        calls.append((event_type, kwargs))

    return calls, EventBus(_fake)


def _make_engine(mock_resolver, bus):
    from game.strategy.engine.conflict_resolution_engine import (
        ConflictResolutionEngine,
    )

    engine = ConflictResolutionEngine(battle_resolver=mock_resolver, event_bus=bus)
    engine._empires = []
    engine._combats_resolved = 0
    engine._fleets_destroyed = []
    return engine


def _make_fleet_pair():
    from game.core.hex_math import HexCoord
    from game.strategy.data.fleet import Fleet

    emp1 = MagicMock(); emp1.id = 0; emp1.remove_fleet = MagicMock()
    emp2 = MagicMock(); emp2.id = 1; emp2.remove_fleet = MagicMock()
    f1 = MagicMock(spec=Fleet); f1.id = 1; f1.owner_id = 0
    f1.location = HexCoord(2, 3); f1.ships = [MagicMock()]
    f2 = MagicMock(spec=Fleet); f2.id = 2; f2.owner_id = 1
    f2.location = HexCoord(2, 3); f2.ships = [MagicMock()]
    return (emp1, f1), (emp2, f2)


def test_combat_resolved_event_carries_replay_id_from_battle_result() -> None:
    """The resolver's BattleResult.replay_id reaches event details."""
    mock_resolver = MagicMock()
    result = BattleResult(
        winner=0,
        tick_count=10,
        team_survivors={0: [MagicMock()], 1: []},
        replay_id="captured-replay-uuid",
    )

    def _resolve_battle(fleets, **_kw):
        list(fleets)[1].ships = []  # mimic post-battle hook wiping team 1
        return result

    mock_resolver.resolve_battle.side_effect = _resolve_battle

    calls, bus = _capture_calls()
    engine = _make_engine(mock_resolver, bus)
    occupants = list(_make_fleet_pair())

    engine._resolve_combat_at_hex(occupants)

    assert len(calls) == 1
    etype, kw = calls[0]
    assert etype == EventType.COMBAT_RESOLVED
    assert kw["replay_id"] == "captured-replay-uuid"


def test_combat_resolved_event_carries_replay_id_none_when_resolver_returns_none() -> None:
    """When the resolver returns BattleResult(replay_id=None), the
    event payload is `replay_id=None` (not omitted)."""
    mock_resolver = MagicMock()
    result = BattleResult(
        winner=None,
        tick_count=10,
        team_survivors={0: [MagicMock()], 1: [MagicMock()]},
        replay_id=None,
    )
    mock_resolver.resolve_battle.return_value = result

    calls, bus = _capture_calls()
    engine = _make_engine(mock_resolver, bus)
    engine._resolve_combat_at_hex(list(_make_fleet_pair()))

    assert len(calls) == 1
    _, kw = calls[0]
    assert "replay_id" in kw
    assert kw["replay_id"] is None
