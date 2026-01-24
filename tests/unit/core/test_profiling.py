"""
Comprehensive tests for game/core/profiling.py

This test file focuses on gaps in existing coverage:
- Thread safety
- ProfilerProxy behavior
- Clear method
- Metadata in records
- Edge cases
- Timing accuracy verification
- Report generation aspects
"""
import pytest
import time
import threading
import os
import uuid
from unittest.mock import MagicMock, patch


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture(autouse=True)
def reset_profiler():
    """Reset profiler state before and after each test."""
    from game.core.profiling import Profiler

    Profiler.reset()

    yield

    Profiler.reset()


@pytest.fixture
def profiler():
    """Get a fresh profiler instance."""
    from game.core.profiling import Profiler
    Profiler.reset()
    return Profiler.instance()


@pytest.fixture
def test_file():
    """Create a unique test file and clean up after."""
    filename = f"test_profiling_{uuid.uuid4().hex[:8]}.json"
    yield filename
    if os.path.exists(filename):
        try:
            os.remove(filename)
        except PermissionError:
            pass


# =============================================================================
# Test: Singleton Behavior
# =============================================================================

class TestSingletonBehavior:
    """Tests for Profiler singleton pattern."""

    def test_instance_returns_same_object(self):
        """instance() should always return the same object."""
        from game.core.profiling import Profiler

        p1 = Profiler.instance()
        p2 = Profiler.instance()

        assert p1 is p2

    def test_direct_instantiation_raises_exception(self, profiler):
        """Direct instantiation should raise when singleton exists."""
        from game.core.profiling import Profiler

        with pytest.raises(Exception, match="singleton"):
            Profiler()

    def test_reset_allows_new_instance(self):
        """reset() should allow creating a new instance."""
        from game.core.profiling import Profiler

        p1 = Profiler.instance()
        session_id_1 = p1.session_id

        Profiler.reset()

        p2 = Profiler.instance()
        session_id_2 = p2.session_id

        # New instance has new session ID
        assert session_id_1 != session_id_2

    def test_has_thread_lock(self):
        """Profiler class should have a lock for thread safety."""
        from game.core.profiling import Profiler

        assert hasattr(Profiler, '_lock')
        assert isinstance(Profiler._lock, type(threading.Lock()))


# =============================================================================
# Test: Thread Safety
# =============================================================================

class TestThreadSafety:
    """Tests for thread-safe operations."""

    def test_concurrent_instance_access(self):
        """Multiple threads calling instance() should get same instance."""
        from game.core.profiling import Profiler

        Profiler.reset()
        results = []
        errors = []

        def get_instance():
            try:
                results.append(Profiler.instance())
            except Exception as e:
                errors.append(e)

        threads = [threading.Thread(target=get_instance) for _ in range(10)]

        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(errors) == 0
        assert len(results) == 10

        # All should be same instance
        first = results[0]
        assert all(r is first for r in results)

    def test_concurrent_recording(self, profiler):
        """Multiple threads recording should not corrupt data."""
        profiler.start()

        def record_action(name):
            for _ in range(10):
                profiler.record(name, 0.001)

        threads = [
            threading.Thread(target=record_action, args=(f"action_{i}",))
            for i in range(5)
        ]

        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # Should have 50 records (5 threads x 10 records each)
        assert len(profiler.records) == 50


# =============================================================================
# Test: Clear Method
# =============================================================================

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


# =============================================================================
# Test: ProfilerProxy
# =============================================================================

class TestProfilerProxy:
    """Tests for the ProfilerProxy class."""

    def test_proxy_delegates_getattr(self):
        """PROFILER proxy should delegate attribute access."""
        from game.core.profiling import PROFILER, Profiler

        # Reset to ensure fresh state
        Profiler.reset()

        # Access through proxy
        assert PROFILER.active == False
        PROFILER.start()
        assert PROFILER.active == True

    def test_proxy_delegates_setattr(self):
        """PROFILER proxy should delegate attribute setting."""
        from game.core.profiling import PROFILER, Profiler

        Profiler.reset()
        instance = Profiler.instance()

        PROFILER.active = True
        assert instance.active == True

        PROFILER.active = False
        assert instance.active == False

    def test_proxy_works_with_methods(self):
        """PROFILER proxy should work with method calls."""
        from game.core.profiling import PROFILER, Profiler

        Profiler.reset()

        PROFILER.start()
        PROFILER.record("test", 0.1)

        assert len(PROFILER.records) == 1


# =============================================================================
# Test: Recording with Metadata
# =============================================================================

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


# =============================================================================
# Test: Start/Stop Behavior
# =============================================================================

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


# =============================================================================
# Test: Profile Decorator
# =============================================================================

class TestProfileDecorator:
    """Tests for the profile_action decorator."""

    def test_decorator_records_when_active(self, profiler):
        """Decorated function should record when profiler is active."""
        from game.core.profiling import profile_action

        profiler.start()

        @profile_action("decorated_func")
        def my_func():
            return 42

        result = my_func()

        assert result == 42
        assert len(profiler.records) == 1
        assert profiler.records[0]['name'] == "decorated_func"

    def test_decorator_skips_when_inactive(self, profiler):
        """Decorated function should not record when profiler is inactive."""
        from game.core.profiling import profile_action

        profiler.stop()

        @profile_action("decorated_func")
        def my_func():
            return 42

        result = my_func()

        assert result == 42
        assert len(profiler.records) == 0

    def test_decorator_preserves_function_metadata(self, profiler):
        """Decorator should preserve function name and docstring."""
        from game.core.profiling import profile_action

        @profile_action("test_func")
        def my_documented_function():
            """This is a docstring."""
            pass

        assert my_documented_function.__name__ == "my_documented_function"
        assert my_documented_function.__doc__ == "This is a docstring."

    def test_decorator_passes_arguments(self, profiler):
        """Decorator should pass through arguments."""
        from game.core.profiling import profile_action

        profiler.start()

        @profile_action("add_func")
        def add(a, b, c=0):
            return a + b + c

        result = add(1, 2, c=3)

        assert result == 6

    def test_decorator_handles_exceptions(self, profiler):
        """Decorator should still record when function raises."""
        from game.core.profiling import profile_action

        profiler.start()

        @profile_action("raising_func")
        def raise_error():
            raise ValueError("test error")

        with pytest.raises(ValueError):
            raise_error()

        # Should still have recorded the call
        assert len(profiler.records) == 1


# =============================================================================
# Test: Profile Context Manager
# =============================================================================

class TestProfileContextManager:
    """Tests for the profile_block context manager."""

    def test_context_manager_records_when_active(self, profiler):
        """Context manager should record when profiler is active."""
        from game.core.profiling import profile_block

        profiler.start()

        with profile_block("my_block"):
            x = 1 + 1

        assert len(profiler.records) == 1
        assert profiler.records[0]['name'] == "my_block"

    def test_context_manager_skips_when_inactive(self, profiler):
        """Context manager should not record when profiler is inactive."""
        from game.core.profiling import profile_block

        profiler.stop()

        with profile_block("my_block"):
            x = 1 + 1

        assert len(profiler.records) == 0

    def test_context_manager_measures_time(self, profiler):
        """Context manager should measure elapsed time."""
        from game.core.profiling import profile_block

        profiler.start()

        with profile_block("sleep_block"):
            time.sleep(0.02)  # 20ms

        # Should be at least 15ms (allowing for timer imprecision)
        assert profiler.records[0]['duration_ms'] > 15

    def test_context_manager_handles_exceptions(self, profiler):
        """Context manager should still record when block raises."""
        from game.core.profiling import profile_block

        profiler.start()

        with pytest.raises(ValueError):
            with profile_block("error_block"):
                raise ValueError("test error")

        # Should still have recorded
        assert len(profiler.records) == 1


# =============================================================================
# Test: Save History
# =============================================================================

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


# =============================================================================
# Test: Timing Accuracy
# =============================================================================

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


# =============================================================================
# Test: Edge Cases
# =============================================================================

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


# =============================================================================
# Test: Initialization
# =============================================================================

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
