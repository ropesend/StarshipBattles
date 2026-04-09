"""Tests for Profiler instance management and thread safety.

PROJ-258: Profiler migrated from SingletonMeta to DI via ApplicationContext.
"""
import pytest
import threading


class TestInstanceManagement:
    """Tests for Profiler instance behavior."""

    def test_direct_construction_creates_independent_instances(self):
        """Each Profiler() call creates a new independent instance."""
        from game.core.profiling import Profiler

        p1 = Profiler()
        p2 = Profiler()
        assert p1 is not p2

    def test_each_instance_has_unique_session_id(self):
        """Each new Profiler has a unique session_id."""
        from game.core.profiling import Profiler

        p1 = Profiler()
        p2 = Profiler()
        assert p1.session_id != p2.session_id


class TestThreadSafety:
    """Tests for thread-safe operations."""

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
