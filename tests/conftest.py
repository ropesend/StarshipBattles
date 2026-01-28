"""
Root test configuration for all tests.

Provides session-scoped fixtures for expensive data loading operations.
Also provides test isolation fixtures for singleton cleanup.

PROJ-38: Added DI fixtures for GameRegistries:
- session_registries: Session-scoped, loaded once per test session
- fresh_registries: Function-scoped, deep copies for test isolation
- minimal_registries: Empty registries for isolated unit tests
"""
import pytest
import pygame
import os
import copy
from typing import TYPE_CHECKING

from tests.fixtures.paths import get_data_dir, get_project_root
from game.simulation.entities.ship_loader import initialize_ship_data
from game.simulation.components.component import load_components, load_modifiers

if TYPE_CHECKING:
    from game.core.registry import GameRegistries


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


# =============================================================================
# PROJ-38: DI Registry Fixtures
# =============================================================================

@pytest.fixture(scope="session")
def session_registries() -> 'GameRegistries':
    """
    Session-scoped GameRegistries loaded once per test session.

    PROJ-38: This fixture provides a GameRegistries instance that is loaded
    once at the start of the test session and reused for all tests. For tests
    that need isolated/mutable registries, use fresh_registries instead.

    The fixture uses SessionRegistryCache to load data once and cache it.

    Returns:
        GameRegistries: Immutable container with all game registries
    """
    from game.core.registry import GameRegistries
    from tests.infrastructure.session_cache import SessionRegistryCache

    # Load data once via session cache
    cache = SessionRegistryCache.instance()
    cache.load_all_data()

    # Create and return GameRegistries instance
    # Note: We use the cache's deep-copied data for the session fixture
    return GameRegistries(
        components=cache.components_data,
        modifiers=cache.modifiers_data,
        vehicle_classes=cache.vehicle_classes_data,
        resources={}  # Resources not yet in cache, use empty dict
    )


@pytest.fixture
def fresh_registries(session_registries) -> 'GameRegistries':
    """
    Function-scoped GameRegistries with deep-copied data.

    PROJ-38: This fixture provides a fresh copy of registries for each test.
    Use this when your test modifies registry data and needs isolation.

    The deep copy ensures modifications don't affect other tests or the
    session-scoped cache.

    Args:
        session_registries: The session-scoped registries to copy from

    Returns:
        GameRegistries: Fresh copy with deep-copied dictionaries
    """
    from game.core.registry import GameRegistries

    return GameRegistries(
        components=copy.deepcopy(session_registries.components),
        modifiers=copy.deepcopy(session_registries.modifiers),
        vehicle_classes=copy.deepcopy(session_registries.vehicle_classes),
        resources=copy.deepcopy(session_registries.resources)
    )


@pytest.fixture
def minimal_registries() -> 'GameRegistries':
    """
    Empty GameRegistries for isolated unit tests.

    PROJ-38: This fixture provides completely empty registries for tests
    that need full control over their test data. Add only what your test needs.

    Returns:
        GameRegistries: Empty container with empty dictionaries
    """
    from game.core.registry import GameRegistries

    return GameRegistries(
        components={},
        modifiers={},
        vehicle_classes={},
        resources={}
    )


# =============================================================================
# PROJ-40: Shared Test Helpers
# =============================================================================

def make_mock_ship_instance(name="Test Ship", owner_id=0):
    """
    Create a mock ShipInstance for testing.

    PROJ-40/NEW-INT-003: Consolidated from multiple integration test files.
    Use this helper instead of defining local versions in test files.

    Args:
        name: Ship name (also used as design_id)
        owner_id: Owner empire ID

    Returns:
        ShipInstance: A mock ship instance for testing
    """
    from game.strategy.data.ship_instance import ShipInstance

    return ShipInstance(
        instance_id=f"test-{name.lower().replace(' ', '-')}-{id(name)}",
        design_id=name,
        name=name,
        owner_id=owner_id,
        design_data={
            'name': name,
            'vehicle_type': 'Ship',
            'stats': {'mass': 100}
        },
    )
