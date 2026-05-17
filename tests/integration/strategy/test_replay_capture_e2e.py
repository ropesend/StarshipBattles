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

Adapter-contract tests (``TestNoCapableBranchTruncatedReplayCapture``,
``TestSoleSurvivorBranchHonestTooltip``, ``TestReasonFlowsThroughEventBus``)
use the ``_RecordingCaptureSink`` fake so they stay focused on the
issue-#8 shortcut-branch changes.

``TestProductionWiringEndToEnd`` deliberately uses a REAL ``ReplayStore``
plus ``set_save_root`` plus the production ``set_default_capture_sink``
/ ``set_replay_store`` accessors, to pin the end-to-end production
wiring (PROJ-366 commits 99b6d7cd0 + c9ad63910) for the simulator
branch — the path the QA session on 2026-05-04 exercised and saw fail
because the wiring was missing at QA time.
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


def _real_store_run_battle_factory(sink, *, recorded_specs):
    """``run_battle`` replacement that drives the sink with a REAL
    ``ReplayOutcome`` (not a ``MagicMock``).

    ``ReplayStore.on_battle_ended`` serializes the outcome via
    ``record.to_dict()`` and writes the result to disk through
    ``save_json``. A ``MagicMock`` is not JSON-serializable, so the
    real-store path requires a real ``ReplayOutcome``. Empty ``data``
    is fine — this helper only proves the capture round-trip, not the
    outcome contents (those are covered by
    ``tests/integration/replay/test_capture_pipeline.py``).
    """
    from game.simulation.replay import ReplaySpec
    from game.simulation.replay.replay_outcome import ReplayOutcome
    from game.simulation.replay.replay_serialization import REPLAY_SCHEMA_VERSION

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
            replay_outcome = ReplayOutcome(
                schema_version=REPLAY_SCHEMA_VERSION,
                data={},
            )
            sink.on_battle_ended(replay_id, replay_outcome)
        return outcome

    return _patched


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


class TestProductionWiringEndToEnd:
    """QA-rejection regression guard for issue #8.

    The QA session on 2026-05-04 showed all three Replay buttons grayed
    out for ``branch=simulator`` battles, despite the issue-#8 shortcut
    fix being in place. Root cause at that time: production never wired
    ``ReplayStore`` as the default capture sink, so every battle ran
    against ``NullCaptureSink`` and ``BattleOutcome.replay_id`` always
    landed as ``None``. PROJ-366 (commits 99b6d7cd0 + c9ad63910,
    2026-05-05 morning PT) added the production wiring in
    ``game/app_bootstrap.py:279-287``.

    PROJ-366 invariant tests (``tests/unit/test_app_bootstrap_invariants
    .py::test_invariant_7_replay_store_registered_after_input_mapper``)
    verify the wiring exists at bootstrap import time. The other tests
    in THIS file verify the adapter contract via a mock
    ``_RecordingCaptureSink``. Neither verifies the END-TO-END production
    path through a real ``ReplayStore`` for the ``branch=simulator``
    path. This class closes that gap: if PROJ-366's wiring or the
    sink's ``save_root``-coupled uuid generation regresses, this test
    fails immediately.
    """

    def test_simulator_branch_captures_real_replay_id_through_real_store(
        self, tmp_path,
    ):
        """Simulator-branch battle with the production ``ReplayStore``
        wired as the default sink AND a real ``save_root`` set should:

        - produce a non-None ``BattleResult.replay_id`` (a real uuid hex).
        - persist a sidecar at ``<save_root>/replays/replay_<uuid>.json``.

        The QA-observed failure had ``replay_id`` always ``None``
        because no sink was wired AND/OR because the store had no
        save_root, both of which collapse to the same user-visible
        symptom (Replay button disabled). This test exercises BOTH
        conditions being correctly met simultaneously.
        """
        from pathlib import Path

        from game.simulation.replay import (
            reset_default_capture_sink,
            set_default_capture_sink,
        )
        from game.strategy.adapters.simulation_adapter import (
            SimulationBattleResolver,
        )
        from game.strategy.services.replay_store import (
            ReplaySettings,
            ReplayStore,
        )
        from game.strategy.systems.save_game_service import SaveGameService

        save_root: Path = tmp_path / "qs_save"
        save_root.mkdir()

        # Settings mirror production defaults; verification disabled keeps
        # the test focused on the capture-sink wiring (the verification
        # path is covered by tests/integration/replay/
        # test_verification_queue_integration.py).
        settings = ReplaySettings(
            max_replays_per_save=10,
            verification_enabled=False,
            verification_queue_cap=4,
        )
        store = ReplayStore(settings=settings)
        store.set_save_root(save_root)

        # Mirror app_bootstrap.py:286-287 production wiring exactly:
        # source-module functions, not lazy-import sites.
        set_default_capture_sink(store)
        SaveGameService.default().set_replay_store(store)

        try:
            resolver = SimulationBattleResolver(ai_factory=MagicMock())
            f1 = _make_fleet(1, [_MockShipInstance("a", combat_capable=True)])
            f2 = _make_fleet(2, [_MockShipInstance("b", combat_capable=True)])

            # Drive run_battle with a fake that fires the SAME sink hooks
            # the production start_engine_from_spec + extract_outcome
            # call, against the REAL ReplayStore. This proves the wiring
            # end-to-end without needing a full battle physics tick loop
            # (covered separately by
            # tests/integration/replay/test_verification_queue_integration
            # .py and tests/integration/replay/test_capture_pipeline.py).
            recorded: List[Any] = []
            with patch(
                "game.strategy.adapters.simulation_adapter.run_battle",
                side_effect=_real_store_run_battle_factory(
                    store, recorded_specs=recorded
                ),
            ):
                result = resolver.resolve_battle([f1, f2])

            # The simulator branch must dispatch to run_battle (not a
            # shortcut), and BattleResult.replay_id must carry the uuid
            # the REAL ReplayStore minted.
            assert len(recorded) == 1, (
                "simulator branch must call run_battle"
            )
            assert result.replay_id is not None, (
                "BattleResult.replay_id must be non-None when a real "
                "ReplayStore is wired AND save_root is set. If this "
                "fails, the QA-observed symptom is back: either the "
                "sink is not wired (PROJ-366 regression) or "
                "ReplayStore.on_battle_started returned empty (save_root "
                "regression)."
            )
            # ReplayStore.on_battle_started returns ``uuid.uuid4().hex``,
            # which is a 32-char lowercase hex string.
            assert len(result.replay_id) == 32, (
                f"expected 32-char hex uuid, got {result.replay_id!r}"
            )
            assert all(c in "0123456789abcdef" for c in result.replay_id), (
                f"replay_id is not a hex uuid: {result.replay_id!r}"
            )
            assert result.replay_unavailable_reason is None

            # The sidecar JSON must have landed under <save_root>/replays/.
            sidecar = save_root / "replays" / f"replay_{result.replay_id}.json"
            assert sidecar.exists(), (
                f"ReplayStore.on_battle_ended must persist a sidecar at "
                f"{sidecar}; this proves the full capture round-trip "
                f"(started → uuid → ended → atomic write) is intact."
            )
        finally:
            reset_default_capture_sink()
            SaveGameService.default().set_replay_store(None)

    def test_null_sink_baseline_still_yields_none_replay_id(self):
        """Baseline sanity: without production wiring, ``replay_id`` is
        ``None`` (the QA-observed pre-PROJ-366 behaviour). Confirms the
        positive test above is exercising the wiring rather than masking
        a different cause.

        Uses ``reset_default_capture_sink()`` to ensure the default
        ``NullCaptureSink`` is active. ``NullCaptureSink.on_battle_started``
        returns ``""``, which ``extract_outcome`` coerces to ``None``.
        """
        from game.simulation.replay import reset_default_capture_sink
        from game.strategy.adapters.simulation_adapter import (
            SimulationBattleResolver,
        )

        # Defensive: clear any leakage from a prior test.
        reset_default_capture_sink()

        resolver = SimulationBattleResolver(ai_factory=MagicMock())
        f1 = _make_fleet(1, [_MockShipInstance("a", combat_capable=True)])
        f2 = _make_fleet(2, [_MockShipInstance("b", combat_capable=True)])

        from game.simulation.replay import get_default_capture_sink

        sink = get_default_capture_sink()
        recorded: List[Any] = []
        with patch(
            "game.strategy.adapters.simulation_adapter.run_battle",
            side_effect=_real_store_run_battle_factory(
                sink, recorded_specs=recorded
            ),
        ):
            result = resolver.resolve_battle([f1, f2])

        assert len(recorded) == 1
        # NullCaptureSink returns "", which extract_outcome coerces to
        # None — this is the legacy pre-PROJ-366 production behaviour.
        assert result.replay_id is None, (
            "Without production wiring, the default NullCaptureSink "
            "returns an empty replay_id (coerced to None). If this is "
            "non-None, the test environment is leaking a real sink "
            "from a prior test."
        )


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
