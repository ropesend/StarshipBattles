"""
Root test configuration for all tests.

Provides session-scoped fixtures for expensive data loading operations.
Also provides test isolation fixtures for singleton cleanup.
"""
import pytest
import pygame
import os

from tests.fixtures.paths import get_data_dir, get_project_root
from game.simulation.entities.ship_loader import initialize_ship_data
from game.simulation.components import load_components, load_modifiers


# Ensure headless pygame for all tests
os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')


# =============================================================================
# Test Isolation Fixtures
# =============================================================================

@pytest.fixture(autouse=True)
def reset_singletons():
    """
    Reset singleton state after each test to prevent data accumulation.

    This is a CRITICAL fixture that prevents the registry accumulation bug
    where data from one test leaks into another. The fixture runs after
    each test (not before) to clean up any modifications.

    See tests/unit/core/test_registry.py::test_data_accumulation_bug_scenario
    for documentation of this issue.
    """
    # Let the test run
    yield

    # After test: Reset singletons to clean state
    # Import here to avoid circular imports at module load time
    from game.core.registry import RegistryManager
    from game.core.logger import Logger
    from game.core.profiling import Profiler

    # Clear registry data (preserves singleton instance but clears contents)
    try:
        registry = RegistryManager._instance
        if registry is not None:
            registry.clear()
    except Exception:
        pass

    # Reset logger event handler
    try:
        from game.core.logger import set_event_handler
        set_event_handler(None)
    except Exception:
        pass

    # Clear profiler records
    try:
        profiler = Profiler._instance
        if profiler is not None:
            profiler.clear()
    except Exception:
        pass


@pytest.fixture(scope="session")
def global_ship_data():
    """
    Load ship data once per test session (session-scoped).

    This is more efficient than loading for each test when the data
    doesn't change. Tests that need clean registry state should use
    the function-scoped 'initialized_ship_data' fixture instead.

    Returns:
        True when data is loaded
    """
    # Initialize pygame once for the session
    if not pygame.get_init():
        pygame.init()

    initialize_ship_data(str(get_project_root()))
    load_components(str(get_data_dir() / "components.json"))
    return True


@pytest.fixture(scope="session")
def global_ship_data_with_modifiers(global_ship_data):
    """
    Load ship data and modifiers once per test session.

    Extends global_ship_data with modifier loading.

    Returns:
        True when data is loaded
    """
    load_modifiers(str(get_data_dir() / "modifiers.json"))
    return True
