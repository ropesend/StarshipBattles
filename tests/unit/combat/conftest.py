"""
Conftest for combat module tests.

Provides fixtures and setup for combat-related tests.
"""
import pytest

from tests.fixtures.paths import data_dir, project_root, unit_test_data_dir  # noqa: F401
from tests.fixtures.common import initialized_ship_data, initialized_ship_data_with_modifiers  # noqa: F401
from tests.fixtures.ai import strategy_manager_with_test_data  # noqa: F401
from tests.fixtures.ships import basic_cruiser_ship, armed_ship  # noqa: F401


@pytest.fixture(autouse=True)
def combat_test_setup():
    """Auto-setup for combat tests. Cleanup handled by root conftest."""
    yield


# Aliases for backward compatibility with existing tests
basic_combat_ship = basic_cruiser_ship
armed_combat_ship = armed_ship
