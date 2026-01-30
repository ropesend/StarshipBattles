"""
Conftest for systems module tests.

Provides fixtures and setup for systems-related tests.

Note: Test isolation (cleanup) is handled by reset_game_state in root conftest.py.
Pygame initialization is handled by enforce_headless in root conftest.py.
"""
from tests.fixtures.paths import data_dir, project_root  # noqa: F401
from tests.fixtures.common import initialized_ship_data, initialized_ship_data_with_modifiers  # noqa: F401
from tests.fixtures.ships import basic_cruiser_ship, basic_escort_ship  # noqa: F401
