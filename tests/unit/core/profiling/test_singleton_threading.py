"""Tests for Profiler singleton pattern and thread safety."""
import pytest
import threading


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
