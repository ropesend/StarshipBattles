"""
Shared fixtures for ShipComponentManager tests.

PROJ-48: Extracted from test_ship_component_manager.py during test file splitting.
"""

import pytest


@pytest.fixture
def weapon_component():
    """Create a weapon component (laser cannon)."""
    from tests.fixtures.components import create_weapon
    return create_weapon()


@pytest.fixture
def engine_component():
    """Create an engine component (standard engine)."""
    from tests.fixtures.components import create_engine
    return create_engine()


@pytest.fixture
def basic_ship():
    """Create a basic ship with bridge and engine."""
    from tests.fixtures.ships import create_test_ship
    return create_test_ship(
        name="BasicShip",
        add_bridge=True,
        add_engine=True
    )


@pytest.fixture
def armed_ship():
    """Create an armed ship for testing."""
    from tests.fixtures.ships import create_test_ship
    return create_test_ship(
        name="ArmedShip",
        add_bridge=True,
        add_engine=True,
        add_weapons=2,
    )
