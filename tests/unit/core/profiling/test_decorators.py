"""Tests for profiling decorators and context managers."""
import pytest
import time


class TestProfilerConstruction:
    """Tests for Profiler direct construction."""

    def test_construction_creates_independent_instances(self):
        """Profiler() should create independent instances."""
        from game.core.profiling import Profiler

        instance1 = Profiler()
        instance2 = Profiler()

        assert instance1 is not instance2

    def test_instance_methods_work(self):
        """Profiler instance should work with method calls."""
        from game.core.profiling import Profiler

        profiler = Profiler()

        assert profiler.active is False
        profiler.start()
        assert profiler.active is True
        profiler.record("test", 0.1)

        assert len(profiler.records) == 1


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
