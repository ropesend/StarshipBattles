"""
Shared fixtures for ShipComponentManager tests.

PROJ-48: Extracted from test_ship_component_manager.py during test file splitting.
PROJ-50: Updated to use fresh_registries for strict DI.
"""

import pytest


@pytest.fixture
def weapon_component(fresh_registries):
    """Create a weapon component (laser cannon)."""
    from tests.fixtures.components import create_weapon
    return create_weapon(registries=fresh_registries)


@pytest.fixture
def engine_component(fresh_registries):
    """Create an engine component (standard engine)."""
    from tests.fixtures.components import create_engine
    return create_engine(registries=fresh_registries)


@pytest.fixture
def basic_ship(fresh_registries):
    """Create a basic ship with bridge and engine."""
    from tests.fixtures.ships import create_test_ship
    return create_test_ship(
        name="BasicShip",
        add_bridge=True,
        add_engine=True,
        registries=fresh_registries
    )


@pytest.fixture
def armed_ship(fresh_registries):
    """Create an armed ship for testing."""
    from tests.fixtures.ships import create_test_ship
    return create_test_ship(
        name="ArmedShip",
        add_bridge=True,
        add_engine=True,
        add_weapons=2,
        registries=fresh_registries
    )
