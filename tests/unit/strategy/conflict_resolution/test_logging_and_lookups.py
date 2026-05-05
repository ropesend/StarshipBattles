"""PROJ-331 Phase 3: characterization tests for ConflictResolutionEngine
private helpers and short-circuits.

Pins observed behavior of:
- `_validate_tick_inputs` (raises ValidationException on None location).
- `resolve_all_conflicts` short-circuit when `tick=None`.
- `_log_combat_result` event-payload extraction (no event_bus, storm
  names dedupe, min owner_id, replay_unavailable_reason plumbing).
- `_lookup_environmental_effects` empty-galaxy paths.
- `_collect_team_modifiers` exception-swallow path (D-007 / OBSERVATION-A).
- Multi-fleet ordering determinism in `_resolve_combat_at_hex`.
- Sole-survivor / single-empire shortcuts.

Per D-008: no new fixtures; per-test synthetic MagicMocks build the
empires/fleets/galaxy. Behavior is what production CURRENTLY does
(broad-catch swallow is intentional per OBSERVATION-A inline comment).
"""
from __future__ import annotations

import logging
from unittest.mock import MagicMock, patch

import pytest

from game.core.event_logging import EventBus
from game.core.exceptions import ValidationException
from game.core.hex_math import HexCoord
from game.strategy.engine.conflict_resolution_engine import (
    ConflictResolutionEngine,
    ConflictResult,
)
from game.strategy.events import EventType
from game.strategy.interfaces.battle_resolver import BattleResult


def _empire(empire_id):
    emp = MagicMock()
    emp.id = empire_id
    emp.fleets = []
    emp.remove_fleet = MagicMock()
    return emp


_DEFAULT_LOC = object()  # sentinel — distinguishes "not passed" from "explicit None"


def _fleet(fleet_id, owner_id, *, location=_DEFAULT_LOC, speed=5, ships=None):
    f = MagicMock()
    f.id = fleet_id
    f.owner_id = owner_id
    if location is _DEFAULT_LOC:
        f.location = HexCoord(0, 0)
    else:
        f.location = location
    f.speed = speed
    f.ships = list(ships) if ships is not None else [MagicMock()]
    return f


def _capture_calls():
    calls = []

    def _fake(event_type, **kwargs):
        calls.append((event_type, kwargs))

    return calls, EventBus(_fake)


def _make_engine(*, resolver=None, event_bus=None):
    engine = ConflictResolutionEngine(
        battle_resolver=resolver or MagicMock(),
        event_bus=event_bus,
    )
    engine._empires = []
    engine._combats_resolved = 0
    engine._fleets_destroyed = []
    return engine


# ---------------------------------------------------------------------------
# _validate_tick_inputs
# ---------------------------------------------------------------------------


class TestValidateTickInputs:
    def test_validate_tick_inputs_raises_validation_exception_when_fleet_has_none_location(self):
        engine = _make_engine()
        emp = _empire(0)
        bad_fleet = _fleet(7, owner_id=0, location=None)
        emp.fleets = [bad_fleet]

        with pytest.raises(ValidationException) as exc_info:
            engine.resolve_all_conflicts([emp], tick=20)

        ctx = exc_info.value.context or {}
        assert ctx.get("empire_id") == 0
        assert ctx.get("fleet_id") == 7

    def test_validate_tick_inputs_passes_when_all_fleets_have_locations(self):
        engine = _make_engine()
        emp = _empire(0)
        emp.fleets = [_fleet(7, owner_id=0, location=HexCoord(1, 1))]

        # No raise; returns ConflictResult.
        result = engine.resolve_all_conflicts([emp], tick=20)
        assert isinstance(result, ConflictResult)


# ---------------------------------------------------------------------------
# resolve_all_conflicts tick=None short-circuit
# ---------------------------------------------------------------------------


class TestResolveAllConflictsTickNone:
    def test_resolve_all_conflicts_returns_zero_combats_when_tick_is_none(self):
        engine = _make_engine()
        # Patch _resolve_conflicts so we can confirm it's NOT called.
        with patch.object(engine, "_resolve_conflicts") as mock_resolve:
            result = engine.resolve_all_conflicts([], tick=None)

        assert result.combats_resolved == 0
        assert result.fleets_destroyed == []
        mock_resolve.assert_not_called()


# ---------------------------------------------------------------------------
# _log_combat_result + _resolve_combat_at_hex behavior
# ---------------------------------------------------------------------------


def _two_fleet_occupants(*, owner_a=0, owner_b=1, fleet_a_id=1, fleet_b_id=2,
                          location=None):
    loc = location or HexCoord(0, 0)
    emp_a = _empire(owner_a)
    emp_b = _empire(owner_b)
    f_a = _fleet(fleet_a_id, owner_id=owner_a, location=loc)
    f_b = _fleet(fleet_b_id, owner_id=owner_b, location=loc)
    return emp_a, emp_b, f_a, f_b


class TestLogCombatResult:
    def test_log_combat_result_skips_emission_when_event_bus_is_none(self):
        """Engine with `event_bus=None`: no AttributeError; no emission."""
        # Resolver returns a normal BattleResult.
        resolver = MagicMock()
        resolver.resolve_battle.return_value = BattleResult(
            winner=0, tick_count=10,
            team_survivors={0: [MagicMock()], 1: []},
        )
        engine = _make_engine(resolver=resolver, event_bus=None)

        emp_a, emp_b, f_a, f_b = _two_fleet_occupants()
        # Should not raise.
        engine._resolve_combat_at_hex([(emp_a, f_a), (emp_b, f_b)])

    def test_log_combat_result_extracts_unique_storm_names_from_sector_effects(self):
        resolver = MagicMock()
        resolver.resolve_battle.return_value = BattleResult(
            winner=0, tick_count=10,
            team_survivors={0: [MagicMock()], 1: []},
        )
        calls, bus = _capture_calls()
        engine = _make_engine(resolver=resolver, event_bus=bus)

        emp_a, emp_b, f_a, f_b = _two_fleet_occupants()

        environmental_effects = [
            {"providers": [
                {"source_kind": "storm", "source_label": "Ion Storm"},
            ]},
            {"providers": [
                {"source_kind": "storm", "source_label": "Ion Storm"},
                {"source_kind": "storm", "source_label": "Plasma"},
            ]},
        ]
        engine._log_combat_result(
            [f_a, f_b],
            surviving_fleet_ids=[f_a.id],
            destroyed_fleet_ids=[f_b.id],
            location=HexCoord(0, 0),
            environmental_effects=environmental_effects,
        )

        assert len(calls) == 1
        _, kw = calls[0]
        # Deduped, in encounter order: ["Ion Storm", "Plasma"].
        assert kw["storm_names"] == ["Ion Storm", "Plasma"]

    def test_log_combat_result_uses_min_owner_id_as_empire_id(self):
        calls, bus = _capture_calls()
        engine = _make_engine(event_bus=bus)
        f_a = _fleet(1, owner_id=5)
        f_b = _fleet(2, owner_id=2)

        engine._log_combat_result(
            [f_a, f_b],
            surviving_fleet_ids=[],
            destroyed_fleet_ids=[],
            location=HexCoord(0, 0),
        )
        assert len(calls) == 1
        _, kw = calls[0]
        # min(5, 2) = 2.
        assert kw["empire_id"] == 2

    def test_log_combat_result_threads_replay_unavailable_reason_from_battle_result(self):
        """Resolver-supplied `replay_unavailable_reason` flows into event payload."""
        resolver = MagicMock()
        resolver.resolve_battle.return_value = BattleResult(
            winner=None, tick_count=0,
            team_survivors={0: [MagicMock()], 1: [MagicMock()]},
            replay_id=None,
            replay_unavailable_reason="sole_survivor",
        )
        calls, bus = _capture_calls()
        engine = _make_engine(resolver=resolver, event_bus=bus)

        emp_a, emp_b, f_a, f_b = _two_fleet_occupants()
        engine._resolve_combat_at_hex([(emp_a, f_a), (emp_b, f_b)])

        assert len(calls) == 1
        etype, kw = calls[0]
        assert etype == EventType.COMBAT_RESOLVED
        assert kw["replay_unavailable_reason"] == "sole_survivor"


# ---------------------------------------------------------------------------
# _lookup_environmental_effects
# ---------------------------------------------------------------------------


class TestLookupEnvironmentalEffects:
    def test_lookup_environmental_effects_returns_none_when_galaxy_is_none(self):
        engine = _make_engine()
        engine._galaxy = None
        assert engine._lookup_environmental_effects(HexCoord(1, 2)) is None

    def test_lookup_environmental_effects_returns_none_when_galaxy_lacks_get_system_at_location(self):
        engine = _make_engine()
        # spec=[] means the mock has no attributes — `getattr(..., None)` returns None.
        engine._galaxy = MagicMock(spec=[])
        assert engine._lookup_environmental_effects(HexCoord(1, 2)) is None


# ---------------------------------------------------------------------------
# _collect_team_modifiers exception swallow
# ---------------------------------------------------------------------------


class TestCollectTeamModifiersExceptionSwallow:
    def test_collect_team_modifiers_returns_none_and_logs_when_collector_raises(
        self, caplog,
    ):
        """OBSERVATION-A: broad except in `_collect_team_modifiers` swallows
        collector failures and returns None. Pin this behavior."""
        engine = _make_engine()
        engine._galaxy = MagicMock()
        emp = _empire(0)
        emp.fleets = [_fleet(1, owner_id=0)]
        engine._empires = [emp]

        f1 = _fleet(1, owner_id=0)
        f2 = _fleet(2, owner_id=1)
        fleets_by_empire = {0: [f1], 1: [f2]}
        empire_order = [0, 1]

        # PROJ-353 Tier-7 (T2.3): patch BOTH the source module AND the engine
        # module's namespace so the test is stable regardless of whether
        # production keeps the deferred `from ... import collect_combat_modifiers`
        # inside `_collect_team_modifiers` or hoists it to a module-level
        # import. The current production code uses a deferred import, so
        # patching only the source module would also work today, but a
        # future refactor lifting the import would silently make the source-
        # module patch a no-op (the engine's local binding would shadow it).
        # `create=True` on the engine-module patch tolerates the binding not
        # yet existing.
        with patch(
            "game.strategy.services.combat_modifier_collector.collect_combat_modifiers",
            side_effect=RuntimeError("boom"),
        ), patch(
            "game.strategy.engine.conflict_resolution_engine.collect_combat_modifiers",
            side_effect=RuntimeError("boom"),
            create=True,
        ):
            with caplog.at_level(logging.WARNING):
                result = engine._collect_team_modifiers(fleets_by_empire, empire_order)

        assert result is None
        # Warning logged (broad-catch contract).
        assert any(
            "Failed to collect combat modifiers" in rec.message
            for rec in caplog.records
        )


# ---------------------------------------------------------------------------
# Multi-fleet ordering determinism
# ---------------------------------------------------------------------------


class TestResolveCombatAtHexOrdering:
    def test_resolve_combat_at_hex_orders_fleets_by_empire_id_then_fleet_id(self):
        """D-006: pin the (empire_id, fleet_id) iteration order seen by the resolver."""
        captured: list[list] = []

        def _resolve(fleets, **_kw):
            captured.append(list(fleets))
            return BattleResult(
                winner=None, tick_count=0,
                team_survivors={i: [] for i in range(len(list(fleets)))},
            )

        resolver = MagicMock()
        resolver.resolve_battle.side_effect = _resolve
        engine = _make_engine(resolver=resolver)

        loc = HexCoord(0, 0)
        emp5 = _empire(5)
        emp2 = _empire(2)
        # Fleet ids are intentionally out-of-order.
        f5_99 = _fleet(99, owner_id=5, location=loc)
        f5_3 = _fleet(3, owner_id=5, location=loc)
        f2_99 = _fleet(99, owner_id=2, location=loc)
        f2_3 = _fleet(3, owner_id=2, location=loc)
        emp5.fleets = [f5_99, f5_3]
        emp2.fleets = [f2_99, f2_3]

        occupants = [
            (emp5, f5_99), (emp5, f5_3),
            (emp2, f2_99), (emp2, f2_3),
        ]
        engine._resolve_combat_at_hex(occupants)

        assert len(captured) == 1
        ordered = captured[0]
        # Expected: emp2/fleet3, emp2/fleet99, emp5/fleet3, emp5/fleet99.
        assert [(f.owner_id, f.id) for f in ordered] == [
            (2, 3), (2, 99), (5, 3), (5, 99),
        ]


# ---------------------------------------------------------------------------
# Sole-survivor / single-empire shortcuts
# ---------------------------------------------------------------------------


class TestResolveCombatAtHexShortCircuits:
    def test_resolve_combat_at_hex_skips_when_no_fleet_has_any_ships(self, caplog):
        """All occupant fleets have empty ships=[]: resolver NOT called; INFO logged."""
        resolver = MagicMock()
        engine = _make_engine(resolver=resolver)
        loc = HexCoord(0, 0)
        emp_a, emp_b, f_a, f_b = _two_fleet_occupants(location=loc)
        f_a.ships = []
        f_b.ships = []

        with caplog.at_level(logging.INFO):
            engine._resolve_combat_at_hex([(emp_a, f_a), (emp_b, f_b)])

        resolver.resolve_battle.assert_not_called()
        assert any(
            "no participating fleet has any ships" in rec.message
            for rec in caplog.records
        )

    def test_resolve_combat_at_hex_returns_when_only_one_empire_present(self):
        """Single-empire occupants: resolver NOT called (early return)."""
        resolver = MagicMock()
        engine = _make_engine(resolver=resolver)
        loc = HexCoord(0, 0)
        emp = _empire(0)
        f1 = _fleet(1, owner_id=0, location=loc)
        f2 = _fleet(2, owner_id=0, location=loc)
        emp.fleets = [f1, f2]

        engine._resolve_combat_at_hex([(emp, f1), (emp, f2)])
        resolver.resolve_battle.assert_not_called()
