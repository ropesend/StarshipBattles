"""Tests for profiling persistence, timing, edge cases, and initialization."""
import pytest
import time
import uuid
import os


class TestSaveHistory:
    """Tests for save_history functionality."""

    def test_save_history_creates_file(self, profiler, test_file):
        """save_history should create the history file."""
        profiler.start()
        profiler.record("action", 0.1)
        profiler.save_history(test_file)

        assert os.path.exists(test_file)

    def test_save_history_empty_records(self, profiler, test_file):
        """save_history with no records should not create file."""
        profiler.start()
        # No records

        profiler.save_history(test_file)

        # File should not be created (no records)
        assert not os.path.exists(test_file)

    def test_save_history_includes_session_id(self, profiler, test_file):
        """save_history should include session_id in saved data."""
        from game.core.json_utils import load_json

        profiler.start()
        profiler.record("action", 0.1)
        profiler.save_history(test_file)

        data = load_json(test_file)
        assert len(data) == 1
        assert data[0]['session_id'] == profiler.session_id

    def test_save_history_includes_timestamp(self, profiler, test_file):
        """save_history should include timestamp in saved data."""
        from game.core.json_utils import load_json

        profiler.start()
        profiler.record("action", 0.1)
        profiler.save_history(test_file)

        data = load_json(test_file)
        assert 'timestamp' in data[0]

    def test_save_history_appends_to_existing(self, profiler, test_file):
        """save_history should append to existing history."""
        from game.core.json_utils import load_json

        profiler.start()
        profiler.record("action1", 0.1)
        profiler.save_history(test_file)

        # Simulate new session
        profiler.clear()
        profiler.record("action2", 0.2)
        profiler.save_history(test_file)

        data = load_json(test_file)
        assert len(data) == 2


class TestTimingAccuracy:
    """Tests for timing measurement accuracy."""

    def test_decorator_uses_perf_counter(self):
        """Decorator should use time.perf_counter for accuracy."""
        import inspect
        from game.core import profiling

        source = inspect.getsource(profiling)
        assert "time.perf_counter()" in source

    def test_context_manager_uses_perf_counter(self):
        """Context manager should use time.perf_counter for accuracy."""
        import inspect
        from game.core import profiling

        source = inspect.getsource(profiling)
        # Both decorator and context manager use perf_counter
        assert source.count("time.perf_counter()") >= 2

    def test_timing_is_reasonably_accurate(self, profiler):
        """Timing should be within reasonable bounds."""
        from game.core.profiling import profile_block

        profiler.start()

        with profile_block("sleep_50ms"):
            time.sleep(0.05)  # 50ms

        duration = profiler.records[0]['duration_ms']

        # Should be between 45ms and 100ms (allowing for scheduler delays)
        assert 45 < duration < 100


class TestEdgeCases:
    """Tests for edge cases."""

    def test_record_zero_duration(self, profiler):
        """record() should handle zero duration."""
        profiler.start()
        profiler.record("instant", 0.0)

        assert profiler.records[0]['duration_ms'] == 0.0

    def test_record_very_small_duration(self, profiler):
        """record() should handle very small durations."""
        profiler.start()
        profiler.record("tiny", 0.000001)  # 1 microsecond

        assert profiler.records[0]['duration_ms'] == pytest.approx(0.001, rel=0.01)

    def test_record_very_large_duration(self, profiler):
        """record() should handle very large durations."""
        profiler.start()
        profiler.record("long", 3600.0)  # 1 hour

        assert profiler.records[0]['duration_ms'] == 3600000.0

    def test_record_negative_duration(self, profiler):
        """record() should handle negative duration (edge case)."""
        profiler.start()
        profiler.record("negative", -0.1)

        # Should still record it
        assert profiler.records[0]['duration_ms'] == -100.0

    def test_empty_action_name(self, profiler):
        """record() should handle empty action name."""
        profiler.start()
        profiler.record("", 0.1)

        assert profiler.records[0]['name'] == ""

    def test_unicode_action_name(self, profiler):
        """record() should handle unicode action names."""
        profiler.start()
        profiler.record("Unicode: \u4e2d\u6587 \U0001F680", 0.1)

        assert profiler.records[0]['name'] == "Unicode: \u4e2d\u6587 \U0001F680"

    def test_none_metadata_converted_to_empty_dict(self, profiler):
        """record() should convert None metadata to empty dict."""
        profiler.start()
        profiler.record("action", 0.1, metadata=None)

        assert profiler.records[0]['metadata'] == {}


class TestInitialization:
    """Tests for Profiler initialization."""

    def test_initial_active_is_false(self, profiler):
        """New profiler should have active=False."""
        assert profiler.active == False

    def test_initial_records_is_empty(self, profiler):
        """New profiler should have empty records."""
        assert profiler.records == []

    def test_initial_start_time_is_none(self, profiler):
        """New profiler should have start_time=None."""
        assert profiler.start_time == None

    def test_session_id_is_uuid(self, profiler):
        """New profiler should have a valid UUID session_id."""
        # Should be a string that can be parsed as UUID
        parsed = uuid.UUID(profiler.session_id)
        assert str(parsed) == profiler.session_id
