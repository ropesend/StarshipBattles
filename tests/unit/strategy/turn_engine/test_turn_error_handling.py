"""
Tests for turn engine error handling during tick processing.

PROJ-251: Rewritten from "continue on failure" to "halt and raise EnginePhaseError".
Sub-engine failures now halt the turn immediately and raise EnginePhaseError.
"""
import logging
from unittest.mock import MagicMock

import pytest
from game.core.exceptions import EnginePhaseError


class TestTickErrorHandling:
    """Tests that sub-engine exceptions halt the turn with EnginePhaseError."""

    def test_turn_halts_when_harvesting_engine_raises(
        self, turn_engine, mock_empire, mock_galaxy
    ):
        """PROJ-251: If harvesting engine raises, turn halts with EnginePhaseError."""
        mock_empire.fleets = []

        mock_harvesting = MagicMock()
        mock_harvesting.process_harvesting_tick.side_effect = RuntimeError("harvest boom")
        turn_engine._harvesting_engine = mock_harvesting

        with pytest.raises(EnginePhaseError) as exc_info:
            turn_engine.process_turn([mock_empire], mock_galaxy)

        assert exc_info.value.context["phase_name"] == "harvesting"
        assert "harvest boom" in exc_info.value.context["original_error"]

    def test_turn_halts_when_production_engine_raises(
        self, turn_engine, mock_empire, mock_galaxy
    ):
        """PROJ-251: If production engine raises, turn halts with EnginePhaseError."""
        mock_empire.fleets = []

        mock_production = MagicMock()
        mock_production.process_construction_tick.side_effect = RuntimeError("production boom")
        turn_engine._production_engine = mock_production

        with pytest.raises(EnginePhaseError) as exc_info:
            turn_engine.process_turn([mock_empire], mock_galaxy)

        assert exc_info.value.context["phase_name"] == "production"

    def test_turn_halts_when_conflict_engine_raises(
        self, turn_engine, mock_empire, mock_galaxy
    ):
        """PROJ-251: If conflict resolution raises, turn halts with EnginePhaseError."""
        mock_empire.fleets = []

        mock_conflict = MagicMock()
        mock_conflict.resolve_all_conflicts.side_effect = RuntimeError("combat boom")
        turn_engine._conflict_engine = mock_conflict

        with pytest.raises(EnginePhaseError):
            turn_engine.process_turn([mock_empire], mock_galaxy)

    def test_sub_engine_error_is_logged(
        self, turn_engine, mock_empire, mock_galaxy, caplog
    ):
        """Sub-engine exceptions are still logged with details before raising."""
        mock_empire.fleets = []

        mock_harvesting = MagicMock()
        mock_harvesting.process_harvesting_tick.side_effect = RuntimeError("test error msg")
        turn_engine._harvesting_engine = mock_harvesting

        with caplog.at_level(logging.ERROR, logger="game.strategy.engine.turn_engine"):
            with pytest.raises(EnginePhaseError):
                turn_engine.process_turn([mock_empire], mock_galaxy)

        error_records = [r for r in caplog.records if r.levelno >= logging.ERROR]
        assert len(error_records) > 0, "Expected at least one ERROR log record"
        assert any("harvesting" in r.message for r in error_records)

    def test_later_phases_not_called_after_failure(
        self, turn_engine, mock_empire, mock_galaxy
    ):
        """PROJ-251: Later phases are NOT called after a phase failure."""
        mock_empire.fleets = []

        # Make harvesting fail
        mock_harvesting = MagicMock()
        mock_harvesting.process_harvesting_tick.side_effect = RuntimeError("boom")
        turn_engine._harvesting_engine = mock_harvesting

        # Track movement calls
        mock_movement = MagicMock()
        mock_movement.collect_movements.return_value = []
        turn_engine._movement_engine = mock_movement

        with pytest.raises(EnginePhaseError):
            turn_engine.process_turn([mock_empire], mock_galaxy)

        # Movement should NOT have been called (harvesting is earlier)
        assert mock_movement.collect_movements.call_count == 0

    def test_engine_phase_error_has_tick_context(
        self, turn_engine, mock_empire, mock_galaxy
    ):
        """EnginePhaseError includes tick number in context."""
        mock_empire.fleets = []

        mock_harvesting = MagicMock()
        mock_harvesting.process_harvesting_tick.side_effect = RuntimeError("boom")
        turn_engine._harvesting_engine = mock_harvesting

        with pytest.raises(EnginePhaseError) as exc_info:
            turn_engine.process_turn([mock_empire], mock_galaxy)

        # First tick should be 1
        assert exc_info.value.context["tick"] == 1

    def test_engine_phase_error_chains_original_exception(
        self, turn_engine, mock_empire, mock_galaxy
    ):
        """EnginePhaseError.__cause__ is the original exception."""
        mock_empire.fleets = []

        original = RuntimeError("original error")
        mock_harvesting = MagicMock()
        mock_harvesting.process_harvesting_tick.side_effect = original
        turn_engine._harvesting_engine = mock_harvesting

        with pytest.raises(EnginePhaseError) as exc_info:
            turn_engine.process_turn([mock_empire], mock_galaxy)

        assert exc_info.value.__cause__ is original

    def test_normal_turn_completes_without_error(
        self, turn_engine, mock_empire, mock_galaxy
    ):
        """A normal turn (no failures) completes without raising."""
        mock_empire.fleets = []
        # Should not raise
        turn_engine.process_turn([mock_empire], mock_galaxy)
