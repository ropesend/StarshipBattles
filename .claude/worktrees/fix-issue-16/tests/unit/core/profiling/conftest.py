"""Shared fixtures for profiling tests."""
import pytest
import os
import uuid

from game.core.profiling import Profiler, set_default_profiler


@pytest.fixture(autouse=True)
def reset_profiler():
    """Reset profiler state before and after each test."""
    set_default_profiler(Profiler())
    yield
    set_default_profiler(None)


@pytest.fixture
def profiler():
    """Get a fresh profiler instance."""
    p = Profiler()
    set_default_profiler(p)
    return p


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
