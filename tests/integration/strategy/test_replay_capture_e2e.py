"""End-to-end replay capture wiring for ``SimulationBattleResolver``.

Issue #8 redirects the design of the two shortcut branches in
``simulation_adapter.py``:

* ``no_capable_ships`` — both fleets have ships but no team has any
  combat-capable weapon. Replaces the old ``return BattleResult(...)``
  shortcut with a brief, truncated ``run_battle`` (1/10 of the normal
  tick budget) so the existing replay-capture pipeline records a real
  (if short) replay. The Event Log Replay button becomes clickable for
  these events.
* ``sole_survivor`` — one team has 0 ships at battle start. Stays a
  shortcut; ``BattleResult.replay_id`` stays ``None`` because there
  was no battle to replay. The new ``replay_unavailable_reason`` field
  carries a tooltip-friendly string so the UI can show an honest
  reason instead of the generic "older save" wording.

This file pins the round-trip wiring between
``SimulationBattleResolver`` → ``IReplayCaptureSink`` (the bridge that
``ReplayStore`` implements in production) → ``BattleResult.replay_id``.
The actual sink-to-disk path is covered by
``tests/integration/replay/test_replay_store.py``; here we use a
fake sink that records the calls so the test stays focused on the
adapter contract issue #8 changes.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple
from unittest.mock import MagicMock, patch


# ---------------------------------------------------------------------------
# Fakes
# ---------------------------------------------------------------------------


class _RecordingCaptureSink:
    """Minimal ``IReplayCaptureSink`` that records calls.

    Returns a deterministic uuid string from ``on_battle_started`` so
    tests can assert exact round-trip equality.
    """

    def __init__(self, replay_id: str = "fake-replay-uuid-001"):
        self._replay_id = replay_id
        self.started_calls: List[Tuple[Any, Any]] = []
        self.ended_calls: List[Tuple[str, Any]] = []

    def on_battle_started(self, replay_spec, *, context) -> str:
        self.started_calls.append((replay_spec, context))
        return self._replay_id

    def on_battle_ended(self, replay_id: str, outcome) -> None:
        self.ended_calls.append((replay_id, outcome))


class _MockShipInstance:
    """Stand-in that satisfies the adapter's call shape and the strategy
    spec compiler's attribute reads (used by ``no_capable`` tests where
    the ships have no weapons but are otherwise valid)."""

    def __init__(
        self,
        instance_id: str = "i",
        *,
        combat_capable: bool = True,
    ):
        self.instance_id = instance_id
        self.design_id = f"design-{instance_id}"
        self.design_data = {"theme_id": "Federation"}
        self.name = f"Ship-{instance_id}"
        self.components = {}
        self._combat_capable = combat_capable

    def is_combat_capable(self) -> bool:
        return self._combat_capable

    def to_ship(self, pos, team_id=0, registries=None):  # noqa: D401
        ship = MagicMock()
        ship.instance_id = self.instance_id
        return ship


def _make_fleet(fleet_id: int, ships: List[_MockShipInstance]):
    """Mock fleet that satisfies the compiler's attribute reads."""
    from game.core.hex_math import HexCoord

    fleet = MagicMock()
    fleet.id = fleet_id
    fleet.ships = ships
    fleet.task_forces = []
    fleet.location = HexCoord(0, 0)
    fleet.owner_id = fleet_id
    return fleet


def _make_outcome(
    *,
    replay_id: Optional[str],
    winner_team_id: Optional[int] = 0,
    duration: int = 200,
):
    """Build a minimal ``BattleOutcome`` stand-in that the adapter's
    ``_determine_winner`` understands."""
    from game.simulation.battle_outcome import ShipStatus

    outcome = MagicMock()
    outcome.duration_ticks = duration
    outcome.replay_id = replay_id

    teams = []
    for tid in (0, 1):
        team = MagicMock()
        team.team_id = tid
        ship = MagicMock()
        ship.status = (
            ShipStatus.SURVIVED if tid == winner_team_id else ShipStatus.DESTROYED
        )
        team.ships = [ship]
        teams.append(team)
    outcome.teams = tuple(teams)
    return outcome


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _patched_run_battle_factory(sink, *, recorded_specs):
    """Build a ``run_battle`` replacement that simulates the production
    capture wiring inside ``start_engine_from_spec``.

    Production path: ``run_battle`` calls ``sink.on_battle_started`` →
    stashes the returned uuid on the engine → ``extract_outcome`` reads
    it back → ``sink.on_battle_ended`` fires → outcome carries the uuid.

    Our fake collapses all of that: when a ``capture_context`` is
    supplied, we drive both halves of the sink contract directly so the
    captured ``replay_id`` flows back through ``BattleOutcome``.
    """
    from game.simulation.replay import ReplaySpec

    def _patched(spec, **kwargs):
        recorded_specs.append(spec)
        capture_context = kwargs.get("capture_context")
        replay_id: Optional[str] = None
        if capture_context is not None:
            replay_spec = ReplaySpec.from_battle_spec(
                spec,
                ship_instance_lookup=capture_context.ship_instance_lookup,
            )
            replay_id = sink.on_battle_started(replay_spec, context=capture_context)

        outcome = _make_outcome(
            replay_id=replay_id or None,
            winner_team_id=0,
            duration=spec.absolute_max_ticks,
        )
        if replay_id:
            sink.on_battle_ended(replay_id, MagicMock())
        return outcome

    return _patched


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestNoCapableBranchTruncatedReplayCapture:
    """Issue #8: the ``no_capable_ships`` branch now runs a truncated
    ``run_battle`` and produces a real ``replay_id``."""

    def test_no_capable_with_ships_runs_truncated_simulator(self):
        """Both fleets have ships but no combat-capable ones — used to
        be a shortcut, now runs the simulator at the brief tick budget
        so the replay captures."""
        from game.strategy.adapters.simulation_adapter import (
            SimulationBattleResolver,
        )
        from game.simulation.replay import set_default_capture_sink, reset_default_capture_sink

        sink = _RecordingCaptureSink()
        set_default_capture_sink(sink)
        try:
            resolver = SimulationBattleResolver(ai_factory=MagicMock())
            f1 = _make_fleet(1, [_MockShipInstance("a", combat_capable=False)])
            f2 = _make_fleet(2, [_MockShipInstance("b", combat_capable=False)])

            recorded: List[Any] = []
            with patch(
                "game.strategy.adapters.simulation_adapter.run_battle",
                side_effect=_patched_run_battle_factory(
                    sink, recorded_specs=recorded
                ),
            ):
                result = resolver.resolve_battle([f1, f2])

            assert len(recorded) == 1, (
                "no_capable branch with non-empty fleets must invoke run_battle"
            )
            spec_used = recorded[0]

            from game.strategy.combat.spec_compiler import _BRIEF_RUN_TICK_BUDGET

            assert spec_used.absolute_max_ticks == _BRIEF_RUN_TICK_BUDGET, (
                "Truncated run must cap at _BRIEF_RUN_TICK_BUDGET"
            )

            assert result.replay_id == "fake-replay-uuid-001", (
                "BattleResult.replay_id must carry the captured uuid"
            )
            assert result.replay_unavailable_reason is None
            assert len(sink.started_calls) == 1
            assert len(sink.ended_calls) == 1
        finally:
            reset_default_capture_sink()

    def test_no_capable_truncated_run_uses_tick_limit_end_condition(self):
        """The truncated spec must ALSO swap end_condition for
        ``TickLimitCondition`` so a no-weapons battle terminates at the
        cap instead of running to the safety ceiling
        (``TeamEliminatedCondition`` would never fire — neither team
        can be eliminated)."""
        from game.strategy.adapters.simulation_adapter import (
            SimulationBattleResolver,
        )
        from game.simulation.systems.battle_end_conditions import (
            TickLimitCondition,
        )

        resolver = SimulationBattleResolver(ai_factory=MagicMock())
        f1 = _make_fleet(1, [_MockShipInstance("a", combat_capable=False)])
        f2 = _make_fleet(2, [_MockShipInstance("b", combat_capable=False)])

        recorded: List[Any] = []

        def _capture(spec, **kwargs):
            recorded.append(spec)
            return _make_outcome(replay_id="x", winner_team_id=None, duration=2000)

        with patch(
            "game.strategy.adapters.simulation_adapter.run_battle",
            side_effect=_capture,
        ):
            resolver.resolve_battle([f1, f2])

        spec_used = recorded[0]
        assert isinstance(spec_used.end_condition, TickLimitCondition), (
            "Truncated run must use TickLimitCondition; "
            "TeamEliminatedCondition would tick until the safety ceiling."
        )

    def test_no_ships_at_all_keeps_shortcut_with_reason(self):
        """Defensive edge case: both fleets are completely empty
        (``fleet.ships == []``). The simulator has nothing to render,
        so we keep the shortcut and surface an honest reason."""
        from game.strategy.adapters.simulation_adapter import (
            SimulationBattleResolver,
        )

        resolver = SimulationBattleResolver(ai_factory=MagicMock())
        f1 = _make_fleet(1, [])
        f2 = _make_fleet(2, [])

        with patch(
            "game.strategy.adapters.simulation_adapter.run_battle"
        ) as mock_run:
            result = resolver.resolve_battle([f1, f2])

        mock_run.assert_not_called()
        assert result.replay_id is None
        assert result.replay_unavailable_reason == "no_ships"


class TestSoleSurvivorBranchHonestTooltip:
    """Issue #8: the ``sole_survivor`` branch keeps the shortcut and
    keeps ``replay_id=None``, but populates ``replay_unavailable_reason``
    so the UI can show an honest tooltip."""

    def test_sole_survivor_returns_none_replay_with_reason(self):
        from game.strategy.adapters.simulation_adapter import (
            SimulationBattleResolver,
        )

        resolver = SimulationBattleResolver(ai_factory=MagicMock())
        f1 = _make_fleet(1, [_MockShipInstance("a", combat_capable=True)])
        f2 = _make_fleet(2, [])

        with patch(
            "game.strategy.adapters.simulation_adapter.run_battle"
        ) as mock_run:
            result = resolver.resolve_battle([f1, f2])

        mock_run.assert_not_called()
        assert result.replay_id is None
        assert result.replay_unavailable_reason == "sole_survivor"
        assert result.winner == 0


class TestReasonFlowsThroughEventBus:
    """Issue #8: ``replay_unavailable_reason`` must thread from
    ``BattleResult`` → ``ConflictResolutionEngine._log_combat_result``
    → ``EventBus.log_event(...)`` → ``Event.details``."""

    def _make_engine_with_resolver(self, resolver, event_handler):
        from game.core.event_logging import EventBus
        from game.strategy.engine.conflict_resolution_engine import (
            ConflictResolutionEngine,
        )

        engine = ConflictResolutionEngine(battle_resolver=resolver)
        engine._event_bus = EventBus(event_handler)
        return engine

    def test_sole_survivor_reason_lands_in_event_details(self):
        from game.core.hex_math import HexCoord
        from game.strategy.interfaces.battle_resolver import (
            BattleResult,
            IBattleResolver,
        )

        captured: List[Tuple[Any, Dict[str, Any]]] = []

        def handler(event_type, **kwargs):
            captured.append((event_type, kwargs))

        class _StubResolver(IBattleResolver):
            def resolve_battle(self, fleets, **kwargs):
                # Mimic the sole_survivor adapter return value.
                return BattleResult(
                    winner=0,
                    tick_count=0,
                    team_survivors={0: list(fleets[0].ships), 1: []},
                    replay_id=None,
                    replay_unavailable_reason="sole_survivor",
                )

        emp1 = MagicMock()
        emp1.id = 1
        emp2 = MagicMock()
        emp2.id = 2
        f1 = MagicMock()
        f1.id = 11
        f1.owner_id = 1
        f1.ships = [MagicMock()]
        f1.location = HexCoord(0, 0)
        f2 = MagicMock()
        f2.id = 22
        f2.owner_id = 2
        f2.ships = []
        f2.location = HexCoord(0, 0)

        engine = self._make_engine_with_resolver(_StubResolver(), handler)
        engine._empires = [emp1, emp2]
        engine._resolve_combat_at_hex([(emp1, f1), (emp2, f2)])

        assert len(captured) == 1
        _, kw = captured[0]
        assert kw["replay_id"] is None
        assert kw["replay_unavailable_reason"] == "sole_survivor"
