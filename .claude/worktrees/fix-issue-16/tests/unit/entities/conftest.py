"""
Conftest for entities module tests.

Provides fixtures and setup for entity-related tests.

Note: Test isolation (cleanup) is handled by reset_game_state in root conftest.py.
Pygame initialization is handled by enforce_headless in root conftest.py.
"""
from tests.fixtures.paths import data_dir, project_root, unit_test_data_dir  # noqa: F401
from tests.fixtures.common import initialized_ship_data, initialized_ship_data_with_modifiers  # noqa: F401
from tests.fixtures.ships import basic_cruiser_ship  # noqa: F401


# Alias intentionally kept - used by 9+ tests in entity and simulation test suites
basic_ship = basic_cruiser_ship
