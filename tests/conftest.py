"""
Test fixtures for Starship Battles test suite.

Provides session-scoped fixtures for expensive data loading operations
and DI-friendly registry fixtures for testing.

Note: Test isolation is handled by reset_game_state in the root conftest.py.
This file provides additional fixtures that build on that foundation.

PROJ-38: Added DI fixtures for GameRegistries:
- session_registries: Session-scoped, loaded once per test session
- fresh_registries: Function-scoped, deep copies for test isolation
- minimal_registries: Empty registries for isolated unit tests

PROJ-48: Consolidated test isolation into root conftest.py reset_game_state fixture.
"""
import pytest
import pygame
import os
import copy
from typing import TYPE_CHECKING

from tests.fixtures.paths import get_data_dir, get_project_root
from game.simulation.entities.ship_loader import initialize_ship_data
from game.simulation.components.component import load_components, load_modifiers
from game.core.registry import get_default_registry_provider

if TYPE_CHECKING:
    from game.core.registry import GameRegistries


# Ensure headless pygame for all tests
os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')


# =============================================================================
# Session-Scoped Data Loading Fixtures
# =============================================================================

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

    # PROJ-211: Pass registry_provider explicitly (no fallback)
    provider = get_default_registry_provider()
    initialize_ship_data(str(get_project_root()), registry_provider=provider)
    load_components(str(get_data_dir() / "components.json"), registry_provider=provider)
    return True


@pytest.fixture(scope="session")
def global_ship_data_with_modifiers(global_ship_data):
    """
    Load ship data and modifiers once per test session.

    Extends global_ship_data with modifier loading.

    Returns:
        True when data is loaded
    """
    # PROJ-211: Pass registry_provider explicitly (no fallback)
    provider = get_default_registry_provider()
    load_modifiers(str(get_data_dir() / "modifiers.json"), registry_provider=provider)
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

    # Load resource catalog once for the session
    from game.core.resources import ResourceCatalog
    resource_catalog = ResourceCatalog.from_json()

    # Create and return GameRegistries instance
    # Note: We use the cache's deep-copied data for the session fixture
    return GameRegistries(
        components=cache.components_data,
        modifiers=cache.modifiers_data,
        vehicle_classes=cache.vehicle_classes_data,
        resources={},  # Resources not yet in cache, use empty dict
        resource_catalog=resource_catalog,
    )


@pytest.fixture
def fresh_registries(session_registries) -> 'GameRegistries':
    """
    Function-scoped GameRegistries with deep-copied production data.

    PROJ-38: This fixture provides a fresh copy of registries for each test.
    Use this when your test needs real component/modifier data with isolation.

    PROJ-50: Primary fixture for strict DI tests. Pass to constructors:
        - Component(data, registries=fresh_registries)
        - Ship(..., registries=fresh_registries)
        - create_component(id, registries=fresh_registries)

    The deep copy ensures modifications don't affect other tests or the
    session-scoped cache.

    Usage:
        def test_with_real_data(fresh_registries):
            ship = Ship("Test", 0, 0, (255,255,255), registries=fresh_registries)
            comp = create_component("laser_cannon", registries=fresh_registries)

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
        resources=copy.deepcopy(session_registries.resources),
        resource_catalog=session_registries.resource_catalog,  # Immutable, shared
    )


@pytest.fixture
def minimal_registries() -> 'GameRegistries':
    """
    Empty GameRegistries for isolated unit tests.

    PROJ-38: This fixture provides completely empty registries for tests
    that need full control over their test data. Add only what your test needs.

    Usage:
        def test_something(minimal_registries):
            # Start with empty registries
            minimal_registries.components["my_comp"] = {...}
            component = Component(data, registries=minimal_registries)

    Returns:
        GameRegistries: Empty container with empty dictionaries
    """
    from game.core.registry import GameRegistries

    return GameRegistries(
        components={},
        modifiers={},
        vehicle_classes={},
        resources={},
    )


@pytest.fixture
def mock_registries(minimal_registries) -> 'GameRegistries':
    """
    Alias for minimal_registries - empty GameRegistries for mocking.

    PROJ-50: Added for clarity when writing DI-focused tests.
    Use this when you want to emphasize you're mocking registry data.

    Usage:
        def test_with_mocked_data(mock_registries):
            mock_registries.components["test_comp"] = {"id": "test_comp", ...}
            component = Component(data, registries=mock_registries)

    Returns:
        GameRegistries: Empty container (same as minimal_registries)
    """
    return minimal_registries


@pytest.fixture
def stable_component_registries(session_registries) -> 'GameRegistries':
    # Production data is considered mod-able balance. Logic/modifier regression
    # tests must not break when data/components.json is rebalanced, so this
    # fixture overlays stable test values for components whose balance has
    # historically drifted. Other components (modifiers, engines, etc.) are
    # inherited unchanged from the session registries.
    from pathlib import Path
    from game.core.registry import GameRegistries
    from game.simulation.components.component_loader import load_components_data

    registries = GameRegistries(
        components=copy.deepcopy(session_registries.components),
        modifiers=copy.deepcopy(session_registries.modifiers),
        vehicle_classes=copy.deepcopy(session_registries.vehicle_classes),
        resources=copy.deepcopy(session_registries.resources),
        resource_catalog=session_registries.resource_catalog,
    )

    fixture_path = Path(__file__).parent / "fixtures" / "test_components.json"
    test_components = load_components_data(str(fixture_path), registries=registries)
    registries.components.update(test_components)

    return registries


# =============================================================================
# PROJ-48: Assertion Helper Functions
# =============================================================================

def assert_success(success: bool, message: str = "") -> None:
    """
    Assert that an operation succeeded with context message.

    PROJ-48: Use this helper for save/load operations that return (success, message) tuples.
    Provides better error messages than bare `assert success`.

    Args:
        success: The success boolean to check
        message: Error message from the operation (displayed on failure)

    Raises:
        AssertionError: If success is False

    Example:
        success, message = SaveGameService.save_game(session, "TestGame")
        assert_success(success, message)
    """
    assert success, f"Operation failed: {message}"


def assert_list_length(items, expected_length: int, description: str = "") -> None:
    """
    Assert list length with context.

    PROJ-48: Use this helper for assertions about list/collection lengths.
    Provides better error messages than bare `assert len(items) == N`.

    Args:
        items: The list/collection to check
        expected_length: Expected number of items
        description: Description of what the list contains (for error message)

    Raises:
        AssertionError: If length doesn't match

    Example:
        assert_list_length(events, 1, "events after selection")
    """
    assert len(items) == expected_length, \
        f"{description}: Expected {expected_length} items, got {len(items)}"


# =============================================================================
# PROJ-40: Shared Test Helpers
# =============================================================================

def make_mock_ship_instance(name="Test Ship", owner_id=0, registries=None):
    """
    Create a mock ShipInstance for testing.

    PROJ-40/NEW-INT-003: Consolidated from multiple integration test files.
    Use this helper instead of defining local versions in test files.

    PROJ-211: Now accepts optional registries parameter. If provided, enables
    get_calculated_stats() calls. Required for tests that call process_turn()
    or Fleet.add_ship() since those trigger stats calculations.

    Args:
        name: Ship name (also used as design_id)
        owner_id: Owner empire ID
        registries: Optional GameRegistries for stats calculation

    Returns:
        ShipInstance: A mock ship instance for testing
    """
    from game.strategy.data.ship_instance import ShipInstance

    ship = ShipInstance(
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
    if registries is not None:
        ship._registries = registries
    return ship


@pytest.fixture
def ship_factory(fresh_registries):
    """
    Factory fixture for creating ShipInstance with proper DI.

    PROJ-211: Provides a factory function that creates ShipInstance objects
    with registries properly injected. Use this in tests that need to call
    ShipInstance.create() or access get_calculated_stats().

    Usage:
        def test_something(ship_factory):
            ship = ship_factory(design_data={'name': 'Destroyer', ...})
            # Ship has registries, so get_calculated_stats() works

    Returns:
        Callable that creates ShipInstance with registries
    """
    from game.strategy.data.ship_instance import ShipInstance

    def _create_ship(
        design_data: dict,
        owner_id: int = 0,
        name: str = None,
        design_id: str = None,
        empire = None,
    ) -> ShipInstance:
        ship = ShipInstance.create(
            design_data=design_data,
            owner_id=owner_id,
            name=name,
            design_id=design_id,
            empire=empire,
            registries=fresh_registries,
        )
        # Pre-cache stats from expected_stats for test designs without real
        # component layers. This avoids running the stat calculator on
        # empty designs and lets tests control the exact stat values.
        expected = design_data.get('expected_stats')
        if expected and not any(design_data.get('layers', {}).values()):
            ship._cached_stats = expected
            # Re-initialize consumable_levels from the expected storage
            storage = expected.get('resource_storage', {})
            ship.consumable_levels = {name: float(val) for name, val in storage.items()}
        return ship

    return _create_ship


def make_colony_ship_for_planet(planet, owner_id=0, name="Colony Ship", registries=None):
    """
    Create a colony ship that can colonize a specific planet.

    Phase 3: Drop pods are carried items in ship.carried_items.
    Ship is reusable after colonization.

    Args:
        planet: The Planet object to create a colony ship for
        owner_id: Owner empire ID
        name: Ship name
        registries: Optional GameRegistries for DI compliance

    Returns:
        ShipInstance: A colony ship with a drop pod in carried_items
    """
    from game.strategy.data.ship_instance import ShipInstance

    planet_type_str = planet.planet_type.name

    ship = ShipInstance(
        instance_id=f"colony-{name.lower().replace(' ', '-')}-{id(name)}",
        design_id=f"{planet_type_str}_colony_ship",
        name=name,
        owner_id=owner_id,
        design_data={
            'name': name,
            'vehicle_type': 'Ship',
            'stats': {'mass': 100},
            'expected_stats': {'speed': 10.0},
            'layers': {
                'HULL': [{'id': 'colony_pod_bay'}]
            }
        },
    )
    # Load drop pod as carried item
    ship.carried_items.append({
        "vehicle_type": "drop_pod",
        "design_id": f"{planet_type_str.lower()}_drop_pod",
        "name": f"Drop Pod ({planet_type_str})",
        "design_data": {"layers": {"CORE": []}},
        "mass": 500,
    })
    if registries is not None:
        ship.set_registries(registries)
    return ship


# --------------------------------------------------------------------------- #
# Race construction helper (PROJ-283 Phase 4)                                  #
# --------------------------------------------------------------------------- #


def make_test_race(
    *,
    preferences_overrides=None,
    base_reproduction_rate=0.03,
    base_happiness=0.5,
    name="Test Race",
    flag_id="flag_test",
    portrait_id="portrait_test",
    theme_id="Federation",
    **aptitude_overrides,
):
    """Construct a valid `RaceConfig` from `FACTOR_REGISTRY` defaults.

    Reduces boilerplate in tests that need a working race object without
    caring about the specific environmental preferences. The default
    construction returns a race that scores ~1.0 habitability on an
    Earth-like planet (every preference at registry default).

    Args:
        preferences_overrides: Optional `Dict[str, EnvironmentalPreference]`
            applied on top of the registry defaults. Useful for
            tightening tolerance on a specific axis or shifting a
            setpoint for a single test.
        base_reproduction_rate: Override for `RaceConfig.base_reproduction_rate`.
        base_happiness: Override for `RaceConfig.base_happiness`.
        name, flag_id, portrait_id, theme_id: Identity fields required by
            `RaceConfig.validate()`. Defaults satisfy validation so tests
            don't need to duplicate the boilerplate.
        **aptitude_overrides: Any `aptitude_*` keyword propagated to the
            `RaceConfig` constructor (e.g. `aptitude_strength=80`).

    Returns:
        A constructed `RaceConfig` with `preferences` backfilled from
        `FACTOR_REGISTRY` defaults via `__post_init__`. Caller-supplied
        overrides win over defaults (already the constructor's behaviour).
    """
    from game.strategy.data.race_config import RaceConfig

    return RaceConfig(
        name=name,
        flag_id=flag_id,
        portrait_id=portrait_id,
        theme_id=theme_id,
        preferences=preferences_overrides or {},
        base_reproduction_rate=base_reproduction_rate,
        base_happiness=base_happiness,
        **aptitude_overrides,
    )
