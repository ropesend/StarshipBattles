"""Tests for SingletonMeta metaclass.

Tests for the shared singleton metaclass that provides thread-safe singleton
behavior for multiple classes across the codebase.
"""
import pytest
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed


class TestSingletonMetaBasics:
    """Tests for basic singleton behavior."""

    def test_instance_returns_same_object_on_repeated_calls(self):
        """instance() returns same object on repeated calls."""
        from game.core.singleton import SingletonMeta

        class MySingleton(metaclass=SingletonMeta):
            pass

        instance1 = MySingleton.instance()
        instance2 = MySingleton.instance()
        instance3 = MySingleton.instance()

        assert instance1 is instance2
        assert instance2 is instance3

    def test_instance_calls_init_exactly_once(self):
        """instance() calls __init__ exactly once."""
        from game.core.singleton import SingletonMeta

        init_count = []

        class InitCounter(metaclass=SingletonMeta):
            def __init__(self):
                init_count.append(1)

        InitCounter.instance()
        InitCounter.instance()
        InitCounter.instance()

        assert len(init_count) == 1

    def test_reset_causes_new_object_creation(self):
        """reset() causes next instance() to create new object."""
        from game.core.singleton import SingletonMeta

        class Resettable(metaclass=SingletonMeta):
            pass

        instance1 = Resettable.instance()
        instance1_id = id(instance1)

        Resettable.reset()

        instance2 = Resettable.instance()
        instance2_id = id(instance2)

        assert instance1_id != instance2_id

    def test_reset_causes_init_to_run_again(self):
        """reset() causes __init__ to run again on next instance()."""
        from game.core.singleton import SingletonMeta

        init_count = []

        class ResetInitCounter(metaclass=SingletonMeta):
            def __init__(self):
                init_count.append(1)

        ResetInitCounter.instance()
        assert len(init_count) == 1

        ResetInitCounter.reset()
        ResetInitCounter.instance()
        assert len(init_count) == 2


class TestSingletonMetaIndependence:
    """Tests for multiple singleton classes being independent."""

    def test_different_singleton_classes_have_independent_instances(self):
        """Two different singleton classes have independent instances."""
        from game.core.singleton import SingletonMeta

        class SingletonA(metaclass=SingletonMeta):
            def __init__(self):
                self.name = "A"

        class SingletonB(metaclass=SingletonMeta):
            def __init__(self):
                self.name = "B"

        instance_a = SingletonA.instance()
        instance_b = SingletonB.instance()

        assert instance_a is not instance_b
        assert instance_a.name == "A"
        assert instance_b.name == "B"

    def test_different_singleton_classes_have_independent_reset(self):
        """Two different singleton classes have independent reset behavior."""
        from game.core.singleton import SingletonMeta

        class SingletonX(metaclass=SingletonMeta):
            pass

        class SingletonY(metaclass=SingletonMeta):
            pass

        instance_x1 = SingletonX.instance()
        instance_y1 = SingletonY.instance()

        # Reset only X
        SingletonX.reset()

        instance_x2 = SingletonX.instance()
        instance_y2 = SingletonY.instance()

        # X should be new, Y should be same
        assert instance_x1 is not instance_x2
        assert instance_y1 is instance_y2


class TestSingletonMetaThreadSafety:
    """Tests for thread safety of singleton operations."""

    def test_concurrent_instance_calls_return_same_object(self):
        """Thread safety - concurrent instance() calls return same object."""
        from game.core.singleton import SingletonMeta

        class ThreadSafeSingleton(metaclass=SingletonMeta):
            def __init__(self):
                self.created_at = threading.current_thread().name

        results = []
        errors = []

        def get_instance():
            try:
                instance = ThreadSafeSingleton.instance()
                results.append(instance)
            except Exception as e:
                errors.append(e)

        # Use 20 threads to increase contention
        with ThreadPoolExecutor(max_workers=20) as executor:
            futures = [executor.submit(get_instance) for _ in range(50)]
            for f in as_completed(futures):
                pass  # Wait for all to complete

        assert len(errors) == 0, f"Errors occurred: {errors}"
        assert len(results) == 50
        assert all(r is results[0] for r in results)

    def test_concurrent_reset_and_instance_dont_crash(self):
        """Thread safety - concurrent reset() + instance() don't crash."""
        from game.core.singleton import SingletonMeta

        class ConcurrentResetSingleton(metaclass=SingletonMeta):
            def __init__(self):
                self.value = 0

        errors = []

        def do_reset():
            try:
                ConcurrentResetSingleton.reset()
            except Exception as e:
                errors.append(e)

        def do_instance():
            try:
                ConcurrentResetSingleton.instance()
            except Exception as e:
                errors.append(e)

        # Mix reset and instance calls
        with ThreadPoolExecutor(max_workers=20) as executor:
            futures = []
            for i in range(100):
                if i % 5 == 0:
                    futures.append(executor.submit(do_reset))
                else:
                    futures.append(executor.submit(do_instance))
            for f in as_completed(futures):
                pass

        assert len(errors) == 0, f"Errors occurred: {errors}"


class TestSingletonMetaSubclassFeatures:
    """Tests for subclass-specific features."""

    def test_subclass_with_clear_method_works(self):
        """Subclass with clear() method works (preserves instance, clears data)."""
        from game.core.singleton import SingletonMeta

        class ClearableSingleton(metaclass=SingletonMeta):
            def __init__(self):
                self.data = {"key": "value"}

            def clear(self):
                """Clear data without resetting instance."""
                self.data = {}

        instance1 = ClearableSingleton.instance()
        assert instance1.data == {"key": "value"}

        instance1.clear()
        assert instance1.data == {}

        # Same instance
        instance2 = ClearableSingleton.instance()
        assert instance1 is instance2
        assert instance2.data == {}

    def test_init_with_custom_initialization(self):
        """__init__ with custom args works correctly."""
        from game.core.singleton import SingletonMeta

        class CustomInitSingleton(metaclass=SingletonMeta):
            def __init__(self):
                self.data = {}
                self.initialized = True

        instance = CustomInitSingleton.instance()
        assert instance.data == {}
        assert instance.initialized is True


class TestSingletonMetaDirectConstruction:
    """Tests for direct construction behavior."""

    def test_direct_construction_returns_singleton(self):
        """Direct construction (e.g., MyClass()) returns singleton."""
        from game.core.singleton import SingletonMeta

        class DirectConstructSingleton(metaclass=SingletonMeta):
            pass

        # Direct construction should behave like instance()
        direct1 = DirectConstructSingleton()
        direct2 = DirectConstructSingleton()
        via_instance = DirectConstructSingleton.instance()

        assert direct1 is direct2
        assert direct1 is via_instance

    def test_direct_construction_init_runs_once(self):
        """Direct construction calls __init__ only once."""
        from game.core.singleton import SingletonMeta

        init_count = []

        class DirectInitCounter(metaclass=SingletonMeta):
            def __init__(self):
                init_count.append(1)

        DirectInitCounter()
        DirectInitCounter()
        DirectInitCounter()

        assert len(init_count) == 1


class TestSingletonMetaEdgeCases:
    """Tests for edge cases."""

    def test_singleton_with_complex_init(self):
        """Singleton with complex initialization works."""
        from game.core.singleton import SingletonMeta

        class ComplexSingleton(metaclass=SingletonMeta):
            def __init__(self):
                self.list_data = []
                self.dict_data = {}
                self.counter = 0

            def increment(self):
                self.counter += 1

        instance = ComplexSingleton.instance()
        instance.list_data.append(1)
        instance.dict_data["key"] = "value"
        instance.increment()

        # Same instance should have same state
        instance2 = ComplexSingleton.instance()
        assert instance2.list_data == [1]
        assert instance2.dict_data == {"key": "value"}
        assert instance2.counter == 1

    def test_multiple_singletons_created_rapidly(self):
        """Multiple different singleton classes can be created rapidly."""
        from game.core.singleton import SingletonMeta

        # Create 10 different singleton classes
        singletons = []
        for i in range(10):
            cls = type(f"RapidSingleton{i}", (), {"__init__": lambda self, i=i: setattr(self, "index", i)})
            cls = SingletonMeta(cls.__name__, cls.__bases__, dict(cls.__dict__))
            singletons.append(cls)

        # Each should be independent
        instances = [s.instance() for s in singletons]
        for i, inst in enumerate(instances):
            assert inst.index == i

        # All different objects
        ids = [id(inst) for inst in instances]
        assert len(set(ids)) == 10
