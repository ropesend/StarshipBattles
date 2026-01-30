"""Shared fixtures for profiling tests."""
import pytest
import os
import uuid


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
