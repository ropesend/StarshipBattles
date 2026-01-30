"""Tests for Profiler recording, clear, and start/stop behavior."""
import pytest
import time


class TestClearMethod:
    """Tests for the clear() method."""

    def test_clear_empties_records(self, profiler):
        """clear() should remove all records."""
        profiler.start()
        profiler.record("action1", 0.1)
        profiler.record("action2", 0.2)

        assert len(profiler.records) == 2

        profiler.clear()

        assert len(profiler.records) == 0

    def test_clear_generates_new_session_id(self, profiler):
        """clear() should generate a new session ID."""
        old_session_id = profiler.session_id

        profiler.clear()

        assert profiler.session_id != old_session_id

    def test_clear_preserves_active_state(self, profiler):
        """clear() should preserve active state."""
        profiler.start()
        assert profiler.active == True

        profiler.clear()

        assert profiler.active == True


class TestRecordingMetadata:
    """Tests for recording with metadata."""

    def test_record_stores_metadata(self, profiler):
        """record() should store metadata in the entry."""
        profiler.start()
        profiler.record("action", 0.1, metadata={"key": "value", "count": 42})

        assert len(profiler.records) == 1
        assert profiler.records[0]['metadata'] == {"key": "value", "count": 42}

    def test_record_default_metadata_is_empty_dict(self, profiler):
        """record() without metadata should have empty dict."""
        profiler.start()
        profiler.record("action", 0.1)

        assert profiler.records[0]['metadata'] == {}

    def test_record_stores_timestamp(self, profiler):
        """record() should store a timestamp."""
        profiler.start()

        before = time.time()
        profiler.record("action", 0.1)
        after = time.time()

        timestamp = profiler.records[0]['timestamp']
        assert before <= timestamp <= after

    def test_record_converts_duration_to_ms(self, profiler):
        """record() should convert duration from seconds to milliseconds."""
        profiler.start()
        profiler.record("action", 0.5)  # 0.5 seconds

        assert profiler.records[0]['duration_ms'] == 500.0

    def test_record_stores_name(self, profiler):
        """record() should store the action name."""
        profiler.start()
        profiler.record("my_action_name", 0.1)

        assert profiler.records[0]['name'] == "my_action_name"


class TestStartStopBehavior:
    """Tests for start/stop state management."""

    def test_start_sets_active_true(self, profiler):
        """start() should set active to True."""
        assert profiler.active == False

        profiler.start()

        assert profiler.active == True

    def test_stop_sets_active_false(self, profiler):
        """stop() should set active to False."""
        profiler.start()
        assert profiler.active == True

        profiler.stop()

        assert profiler.active == False

    def test_toggle_switches_state(self, profiler):
        """toggle() should switch between active states."""
        assert profiler.active == False

        result1 = profiler.toggle()
        assert result1 == True
        assert profiler.active == True

        result2 = profiler.toggle()
        assert result2 == False
        assert profiler.active == False

    def test_is_active_returns_current_state(self, profiler):
        """is_active() should return current active state."""
        assert profiler.is_active() == False

        profiler.start()
        assert profiler.is_active() == True

        profiler.stop()
        assert profiler.is_active() == False

    def test_start_sets_start_time(self, profiler):
        """start() should set start_time."""
        before = time.time()
        profiler.start()
        after = time.time()

        assert profiler.start_time is not None
        assert before <= profiler.start_time <= after
