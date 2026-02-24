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
                with patch("game.core.profiling.logger") as mock_logger:
                    profiler.save_history("dummy.json")
                    mock_logger.error.assert_called_once()
                    assert "Failed to save" in mock_logger.error.call_args[0][0]

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


# =============================================================================
# TCG-FND-009: Additional Profiler Edge Cases
# =============================================================================

class TestSaveHistoryWithCustomFilename:
    """Tests for save_history with custom filename."""

    def test_save_history_custom_filename(self):
        """save_history accepts custom filename."""
        profiler = Profiler.instance()
        profiler.records = [{"name": "test", "duration_ms": 5.0}]

        with patch("game.core.profiling.load_json", return_value=[]):
            with patch("game.core.profiling.save_json", return_value=True) as mock_save:
                profiler.save_history("custom_history.json")

        mock_save.assert_called_once()
        filename_arg = mock_save.call_args[0][0]
        assert filename_arg == "custom_history.json"

    def test_save_history_default_filename(self):
        """save_history uses Paths.PROFILING_HISTORY by default."""
        profiler = Profiler.instance()
        profiler.records = [{"name": "test", "duration_ms": 5.0}]

        with patch("game.core.profiling.load_json", return_value=[]):
            with patch("game.core.profiling.save_json", return_value=True) as mock_save:
                with patch("game.core.profiling.Paths") as mock_paths:
                    mock_paths.PROFILING_HISTORY = "default_path.json"
                    profiler.save_history()

        mock_save.assert_called_once()
        filename_arg = mock_save.call_args[0][0]
        assert filename_arg == "default_path.json"


class TestProfilerRecordMethod:
    """Tests for Profiler.record() method."""

    def test_record_when_inactive_does_nothing(self):
        """record() does nothing when profiler is inactive."""
        profiler = Profiler.instance()
        profiler.active = False
        profiler.records = []

        profiler.record("test_action", 0.5)

        assert len(profiler.records) == 0

    def test_record_when_active_adds_entry(self):
        """record() adds entry when profiler is active."""
        profiler = Profiler.instance()
        profiler.active = True
        profiler.records = []

        profiler.record("test_action", 0.5, metadata={"extra": "info"})

        assert len(profiler.records) == 1
        assert profiler.records[0]["name"] == "test_action"
        assert profiler.records[0]["duration_ms"] == 500.0  # Converted to ms
        assert profiler.records[0]["metadata"]["extra"] == "info"

    def test_record_with_no_metadata(self):
        """record() uses empty dict for metadata if not provided."""
        profiler = Profiler.instance()
        profiler.active = True
        profiler.records = []

        profiler.record("test_action", 0.1)

        assert profiler.records[0]["metadata"] == {}


class TestProfilerToggle:
    """Tests for Profiler.toggle() method."""

    def test_toggle_starts_when_inactive(self):
        """toggle() starts profiler when inactive."""
        profiler = Profiler.instance()
        profiler.active = False

        result = profiler.toggle()

        assert profiler.active is True
        assert result is True

    def test_toggle_stops_when_active(self):
        """toggle() stops profiler when active."""
        profiler = Profiler.instance()
        profiler.start()

        result = profiler.toggle()

        assert profiler.active is False
        assert result is False


class TestProfilerClear:
    """Tests for Profiler.clear() method."""

    def test_clear_resets_records(self):
        """clear() empties records list."""
        profiler = Profiler.instance()
        profiler.records = [{"name": "test"}]

        profiler.clear()

        assert profiler.records == []

    def test_clear_generates_new_session_id(self):
        """clear() generates new session ID."""
        profiler = Profiler.instance()
        old_session = profiler.session_id

        profiler.clear()

        assert profiler.session_id != old_session


class TestProfileActionDecoratorWithArgs:
    """Additional decorator tests."""

    def test_profile_action_preserves_function_args(self):
        """Decorator preserves function arguments."""
        profiler = Profiler.instance()
        profiler.start()
        profiler.records = []

        @profile_action("add_func")
        def add(a, b):
            return a + b

        result = add(5, 3)

        assert result == 8
        assert len(profiler.records) == 1

    def test_profile_action_preserves_kwargs(self):
        """Decorator preserves keyword arguments."""
        profiler = Profiler.instance()
        profiler.start()
        profiler.records = []

        @profile_action("greet_func")
        def greet(name, greeting="Hello"):
            return f"{greeting}, {name}!"

        result = greet("World", greeting="Hi")

        assert result == "Hi, World!"
        assert len(profiler.records) == 1

    def test_profile_action_preserves_function_name(self):
        """Decorator preserves function __name__."""
        @profile_action("original_func")
        def original_func():
            pass

        assert original_func.__name__ == "original_func"


class TestProfileBlockNested:
    """Tests for nested profile blocks."""

    def test_nested_profile_blocks(self):
        """Nested profile blocks all record."""
        profiler = Profiler.instance()
        profiler.start()
        profiler.records = []

        with profile_block("outer"):
            with profile_block("inner"):
                x = 1 + 1

        # Both blocks should be recorded
        assert len(profiler.records) == 2
        names = [r["name"] for r in profiler.records]
        assert "inner" in names
        assert "outer" in names

    def test_profile_block_mixed_with_decorator(self):
        """Profile block and decorator can be mixed."""
        profiler = Profiler.instance()
        profiler.start()
        profiler.records = []

        @profile_action("decorated")
        def decorated_func():
            with profile_block("block_inside"):
                return 42

        result = decorated_func()

        assert result == 42
        assert len(profiler.records) == 2
