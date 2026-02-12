"""
Unit tests for Profiler edge cases.

Tests save_history error paths, profile_action decorator,
and profile_block context manager behavior.
"""
import pytest
from unittest.mock import patch, MagicMock

from game.core.profiling import (
    Profiler,
    profile_action,
    profile_block,
)


@pytest.fixture(autouse=True)
def reset_profiler():
    """Reset Profiler singleton before/after each test."""
    Profiler.reset()
    yield
    Profiler.reset()


class TestSaveHistoryErrorPaths:
    """Tests for save_history edge cases."""

    def test_save_history_no_records_skips(self):
        """Empty records results in no file write."""
        profiler = Profiler.instance()
        profiler.records = []

        with patch("game.core.profiling.save_json") as mock_save:
            profiler.save_history("dummy.json")
            # save_json should NOT be called when no records
            mock_save.assert_not_called()

    def test_save_history_io_error(self):
        """When save_json returns False, error is logged."""
        profiler = Profiler.instance()
        profiler.records = [{"name": "test", "duration_ms": 10.0}]

        with patch("game.core.profiling.load_json", return_value=[]):
            with patch("game.core.profiling.save_json", return_value=False):
                with patch("game.core.profiling.log_error") as mock_log_error:
                    profiler.save_history("dummy.json")
                    mock_log_error.assert_called_once()
                    assert "Failed to save" in mock_log_error.call_args[0][0]

    def test_save_history_appends_to_existing(self):
        """Existing history gets new session appended."""
        profiler = Profiler.instance()
        profiler.records = [{"name": "new_record", "duration_ms": 5.0}]
        profiler.session_id = "new-session-id"

        existing_history = [
            {"session_id": "old-session", "records": [{"name": "old"}]}
        ]

        with patch("game.core.profiling.load_json", return_value=existing_history):
            with patch("game.core.profiling.save_json", return_value=True) as mock_save:
                profiler.save_history("dummy.json")

                # Verify save_json was called with combined history
                mock_save.assert_called_once()
                saved_data = mock_save.call_args[0][1]
                assert len(saved_data) == 2  # Old + new session
                assert saved_data[0]["session_id"] == "old-session"
                assert saved_data[1]["session_id"] == "new-session-id"


class TestProfileActionDecorator:
    """Tests for profile_action decorator."""

    def test_profile_action_inactive_no_record(self):
        """When profiler is inactive, function runs without recording."""
        profiler = Profiler.instance()
        profiler.active = False
        initial_records = len(profiler.records)

        @profile_action("test_func")
        def my_func():
            return 42

        result = my_func()

        assert result == 42
        assert len(profiler.records) == initial_records  # No new records

    def test_profile_action_active_records(self):
        """When profiler is active, a record is created."""
        profiler = Profiler.instance()
        profiler.start()
        profiler.records = []

        @profile_action("test_func")
        def my_func():
            return "result"

        result = my_func()

        assert result == "result"
        assert len(profiler.records) == 1
        assert profiler.records[0]["name"] == "test_func"

    def test_profile_action_exception_still_records(self):
        """If function raises, duration is still recorded."""
        profiler = Profiler.instance()
        profiler.start()
        profiler.records = []

        @profile_action("failing_func")
        def failing_func():
            raise ValueError("Test error")

        with pytest.raises(ValueError):
            failing_func()

        # Record should still be created
        assert len(profiler.records) == 1
        assert profiler.records[0]["name"] == "failing_func"
        assert profiler.records[0]["duration_ms"] >= 0


class TestProfileBlockContextManager:
    """Tests for profile_block context manager."""

    def test_profile_block_inactive_no_record(self):
        """When profiler is inactive, no recording happens."""
        profiler = Profiler.instance()
        profiler.active = False
        profiler.records = []

        with profile_block("test_block"):
            x = 1 + 1

        assert len(profiler.records) == 0

    def test_profile_block_active_records(self):
        """When profiler is active, block is recorded."""
        profiler = Profiler.instance()
        profiler.start()
        profiler.records = []

        with profile_block("test_block"):
            x = 1 + 1

        assert len(profiler.records) == 1
        assert profiler.records[0]["name"] == "test_block"

    def test_profile_block_exception_still_records(self):
        """If block raises, duration is still recorded."""
        profiler = Profiler.instance()
        profiler.start()
        profiler.records = []

        with pytest.raises(RuntimeError):
            with profile_block("failing_block"):
                raise RuntimeError("Block error")

        # Record should still be created
        assert len(profiler.records) == 1
        assert profiler.records[0]["name"] == "failing_block"
