"""
PROJ-332 — Characterization tests for `TurnEngine.process_turn` snapshot
integration with `TurnStateSnapshot`.

Pins:
- `TurnStateSnapshot.capture` is invoked iff `session` is provided.
- On `EnginePhaseError`, `snapshot.restore(session)` is invoked iff a
  snapshot was captured AND a session is set.
- On `EnginePhaseError`, `snapshot.dump_crash_snapshot(save_path, ...)`
  is invoked iff a snapshot was captured AND `save_path` is set.
- PROJ-343 T1.2-snapshot: if `TurnStateSnapshot.capture` raises, the
  failure is now re-raised so callers know the turn aborted before any
  engine ran. The dedicated assertion lives in
  `test_turn_snapshot_capture_failure.py`. The prior D-008 OBSERVATION
  (silent swallow with `snapshot=None`) was retracted as a real defect.

Discipline: pure characterization — no production refactors.
"""
from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from game.core.exceptions import EnginePhaseError
from game.strategy.engine.turn_engine import TurnEngine
from tests.fixtures.turn_engine import build_test_turn_engine


def _make_engine_with_failing_harvester(fresh_registries):
    """Build a TurnEngine whose harvesting engine raises in tick 1.

    Used to force the EnginePhaseError code path inside `process_turn`.
    """
    engine = build_test_turn_engine(fresh_registries, ai_factory=MagicMock())
    failing_harvester = MagicMock()
    failing_harvester.process_harvesting_tick.side_effect = RuntimeError("boom")
    engine._harvesting_engine = failing_harvester
    return engine


class TestSnapshotIntegration:
    """Pin the snapshot capture/restore/crash-dump call boundaries."""

    def test_process_turn_captures_snapshot_when_session_provided_and_skips_when_none(
        self, fresh_registries, mock_empire, mock_galaxy
    ):
        """`TurnStateSnapshot.capture` is called iff `session` is provided."""
        mock_empire.fleets = []

        # Case 1: session provided → capture called.
        engine = build_test_turn_engine(fresh_registries, ai_factory=MagicMock())
        session = MagicMock()
        session.turn_number = 5

        with patch(
            'game.strategy.engine.turn_state_snapshot.TurnStateSnapshot.capture'
        ) as mock_capture:
            mock_capture.return_value = MagicMock()
            engine.process_turn([mock_empire], mock_galaxy, session=session)

        assert mock_capture.call_count == 1
        # Capture sees the session.turn_number / empires / galaxy positionally
        # or by keyword — pin via kwargs lookup that's tolerant of either.
        call = mock_capture.call_args
        passed = {**call.kwargs}
        if call.args:
            # capture(turn_number, empires, galaxy) — positional spelling.
            for value, key in zip(call.args, ("turn_number", "empires", "galaxy")):
                passed.setdefault(key, value)
        assert passed.get("turn_number") == 5

        # Case 2: no session → capture not called.
        engine_b = build_test_turn_engine(fresh_registries, ai_factory=MagicMock())
        with patch(
            'game.strategy.engine.turn_state_snapshot.TurnStateSnapshot.capture'
        ) as mock_capture_b:
            engine_b.process_turn([mock_empire], mock_galaxy, session=None)

        assert mock_capture_b.call_count == 0

    def test_engine_phase_error_triggers_snapshot_restore_when_snapshot_and_session_set(
        self, fresh_registries, mock_empire, mock_galaxy
    ):
        """`snapshot.restore(session)` runs once when a phase fails AND
        both snapshot and session are set."""
        mock_empire.fleets = []
        engine = _make_engine_with_failing_harvester(fresh_registries)
        session = MagicMock()
        session.turn_number = 1

        fake_snapshot = MagicMock()

        with patch(
            'game.strategy.engine.turn_state_snapshot.TurnStateSnapshot.capture',
            return_value=fake_snapshot,
        ):
            with pytest.raises(EnginePhaseError):
                engine.process_turn([mock_empire], mock_galaxy, session=session)

        fake_snapshot.restore.assert_called_once_with(session)

    def test_engine_phase_error_triggers_dump_crash_snapshot_when_snapshot_and_save_path_set(
        self, fresh_registries, mock_empire, mock_galaxy
    ):
        """`snapshot.dump_crash_snapshot(save_path, context)` runs once when
        a phase fails AND both snapshot and save_path are set."""
        mock_empire.fleets = []
        engine = _make_engine_with_failing_harvester(fresh_registries)
        session = MagicMock()
        session.turn_number = 1

        fake_snapshot = MagicMock()

        with patch(
            'game.strategy.engine.turn_state_snapshot.TurnStateSnapshot.capture',
            return_value=fake_snapshot,
        ):
            with pytest.raises(EnginePhaseError):
                engine.process_turn(
                    [mock_empire],
                    mock_galaxy,
                    save_path="/tmp/proj332-fake-save",
                    session=session,
                )

        fake_snapshot.dump_crash_snapshot.assert_called_once()
        # First positional arg is the save_path.
        dump_call = fake_snapshot.dump_crash_snapshot.call_args
        assert dump_call.args[0] == "/tmp/proj332-fake-save"

    # Note: the prior D-008 pinning test
    # (`test_snapshot_capture_failure_is_swallowed_and_turn_continues_with_snapshot_none`)
    # was deleted by PROJ-343 T1.2-snapshot. The new contract — capture
    # failure surfaces via re-raise — is pinned in
    # `test_turn_snapshot_capture_failure.py`.


class TestEnginePhaseErrorContextEnrichment:
    """PROJ-381 Phase 3 (B-2): EnginePhaseError context must include
    turn_number and save_path so crash dumps and the UI dialog can
    correlate the failure to the saved turn."""

    def test_phase_error_context_includes_turn_number_and_save_path(
        self, fresh_registries, mock_empire, mock_galaxy
    ):
        mock_empire.fleets = []
        engine = _make_engine_with_failing_harvester(fresh_registries)
        session = MagicMock()
        session.turn_number = 17

        with patch(
            'game.strategy.engine.turn_state_snapshot.TurnStateSnapshot.capture',
            return_value=MagicMock(),
        ):
            with pytest.raises(EnginePhaseError) as exc_info:
                engine.process_turn(
                    [mock_empire],
                    mock_galaxy,
                    save_path="/tmp/proj381-b2-fake",
                    session=session,
                )

        ctx = exc_info.value.context or {}
        assert ctx.get("turn_number") == 17
        assert ctx.get("save_path") == "/tmp/proj381-b2-fake"
        # Pre-existing keys must still be present.
        assert ctx.get("phase_name") is not None
        assert "tick" in ctx
