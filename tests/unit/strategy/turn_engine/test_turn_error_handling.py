"""
Tests for turn engine error handling during tick processing.

PROJ-239 Task 1.1: Verify that sub-engine failures during tick processing
are caught and logged rather than crashing the entire turn.
"""
import logging
from unittest.mock import MagicMock


class TestTickErrorHandling:
    """Tests that sub-engine exceptions during _process_tick are handled gracefully."""

    def test_tick_continues_when_harvesting_engine_raises(
        self, turn_engine, mock_empire, mock_galaxy
    ):
        """If harvesting engine raises, the tick continues and other phases run."""
        mock_empire.fleets = []

        # Make harvesting engine raise
        mock_harvesting = MagicMock()
        mock_harvesting.process_harvesting_tick.side_effect = RuntimeError("harvest boom")
        turn_engine._harvesting_engine = mock_harvesting

        # Inject a mock movement engine to verify later phases still run
        mock_movement = MagicMock()
        mock_movement.collect_movements.return_value = []
        turn_engine._movement_engine = mock_movement

        # Should not raise
        turn_engine.process_turn([mock_empire], mock_galaxy)

        # Movement engine should still have been called (later phase)
        assert mock_movement.collect_movements.call_count > 0

    def test_tick_continues_when_production_engine_raises(
        self, turn_engine, mock_empire, mock_galaxy
    ):
        """If production engine raises, the tick continues."""
        mock_empire.fleets = []

        mock_production = MagicMock()
        mock_production.process_construction_tick.side_effect = RuntimeError("production boom")
        turn_engine._production_engine = mock_production

        mock_movement = MagicMock()
        mock_movement.collect_movements.return_value = []
        turn_engine._movement_engine = mock_movement

        turn_engine.process_turn([mock_empire], mock_galaxy)

        # Movement still called despite production failure
        assert mock_movement.collect_movements.call_count > 0

    def test_tick_continues_when_conflict_engine_raises(
        self, turn_engine, mock_empire, mock_galaxy
    ):
        """If conflict resolution raises, the turn still completes."""
        mock_empire.fleets = []

        mock_conflict = MagicMock()
        mock_conflict.resolve_all_conflicts.side_effect = RuntimeError("combat boom")
        turn_engine._conflict_engine = mock_conflict

        # Should complete without raising
        turn_engine.process_turn([mock_empire], mock_galaxy)

    def test_sub_engine_error_is_logged(
        self, turn_engine, mock_empire, mock_galaxy, caplog
    ):
        """Sub-engine exceptions are logged with details."""
        mock_empire.fleets = []

        mock_harvesting = MagicMock()
        mock_harvesting.process_harvesting_tick.side_effect = RuntimeError("test error msg")
        turn_engine._harvesting_engine = mock_harvesting

        with caplog.at_level(logging.ERROR, logger="game.strategy.engine.turn_engine"):
            turn_engine.process_turn([mock_empire], mock_galaxy)

        # Should have logged the error with phase name
        error_records = [r for r in caplog.records if r.levelno >= logging.ERROR]
        assert len(error_records) > 0, "Expected at least one ERROR log record"
        # The log message contains the phase name
        assert any("harvesting" in r.message for r in error_records), (
            f"Expected error log mentioning 'harvesting', got: {[r.message for r in error_records]}"
        )
        # The exception details are in exc_info (traceback)
        assert any(r.exc_info is not None for r in error_records), (
            "Expected error log records to include exception info"
        )

    def test_population_growth_still_runs_after_tick_errors(
        self, turn_engine, mock_empire, mock_galaxy
    ):
        """Population growth (post-loop) still runs even if ticks had errors."""
        mock_empire.fleets = []

        mock_harvesting = MagicMock()
        mock_harvesting.process_harvesting_tick.side_effect = RuntimeError("boom")
        turn_engine._harvesting_engine = mock_harvesting

        mock_pop = MagicMock()
        turn_engine._population_engine = mock_pop

        turn_engine.process_turn([mock_empire], mock_galaxy)

        mock_pop.process_population_growth.assert_called_once()

    def test_all_100_ticks_run_despite_errors(
        self, turn_engine, mock_empire, mock_galaxy
    ):
        """All 100 ticks execute even if every tick has an error in one phase."""
        mock_empire.fleets = []

        mock_harvesting = MagicMock()
        mock_harvesting.process_harvesting_tick.side_effect = RuntimeError("boom")
        turn_engine._harvesting_engine = mock_harvesting

        mock_movement = MagicMock()
        mock_movement.collect_movements.return_value = []
        turn_engine._movement_engine = mock_movement

        turn_engine.process_turn([mock_empire], mock_galaxy)

        # Movement should have been called 100 times (once per tick)
        assert mock_movement.collect_movements.call_count == 100
