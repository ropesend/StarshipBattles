"""
PROJ-332 — Characterization tests for `TurnEngine.process_turn` snapshot
integration with `TurnStateSnapshot`.

Pins:
- `TurnStateSnapshot.capture` is invoked iff `session` is provided.
- On `EnginePhaseError`, `snapshot.restore(session)` is invoked iff a
  snapshot was captured AND a session is set.
- On `EnginePhaseError`, `snapshot.dump_crash_snapshot(save_path, ...)`
  is invoked iff a snapshot was captured AND `save_path` is set.
- D-008 OBSERVATION: if `TurnStateSnapshot.capture` itself raises, the
  exception is swallowed (logged at ERROR), and the turn proceeds with
  `snapshot is None`. Pinning as observed; no production fix proposed.

Discipline: pure characterization — no production refactors.
"""
from __future__ import annotations

import logging
from unittest.mock import MagicMock, patch

import pytest

from game.core.exceptions import EnginePhaseError
from game.strategy.engine.turn_engine import TurnEngine


def _make_engine_with_failing_harvester(fresh_registries):
    """Build a TurnEngine whose harvesting engine raises in tick 1.

    Used to force the EnginePhaseError code path inside `process_turn`.
    """
    engine = TurnEngine(registries=fresh_registries, ai_factory=MagicMock())
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
        engine = TurnEngine(registries=fresh_registries, ai_factory=MagicMock())
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
        engine_b = TurnEngine(registries=fresh_registries, ai_factory=MagicMock())
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

    def test_snapshot_capture_failure_is_swallowed_and_turn_continues_with_snapshot_none(
        self, fresh_registries, mock_empire, mock_galaxy, caplog
    ):
        """D-008 OBSERVATION: if `TurnStateSnapshot.capture` raises, the
        broad `except Exception` swallows it, logs at ERROR, and the turn
        proceeds with snapshot=None.

        Verified by:
        - process_turn does not propagate the capture exception.
        - On a subsequent EnginePhaseError, neither restore nor
          dump_crash_snapshot is called (because snapshot is None).
        - An ERROR log entry mentions the snapshot capture failure.
        """
        mock_empire.fleets = []
        engine = _make_engine_with_failing_harvester(fresh_registries)
        session = MagicMock()
        session.turn_number = 1

        # capture raises — its return value is unused; the snapshot var
        # stays None for the rest of the turn.
        with patch(
            'game.strategy.engine.turn_state_snapshot.TurnStateSnapshot.capture',
            side_effect=RuntimeError("snapshot capture failed"),
        ):
            with caplog.at_level(
                logging.ERROR, logger="game.strategy.engine.turn_engine"
            ):
                with pytest.raises(EnginePhaseError):
                    engine.process_turn(
                        [mock_empire],
                        mock_galaxy,
                        save_path="/tmp/proj332-fake-save",
                        session=session,
                    )

        # The capture failure is logged but not raised.
        assert any(
            "Failed to capture pre-turn snapshot" in record.getMessage()
            for record in caplog.records
            if record.levelno >= logging.ERROR
        )
