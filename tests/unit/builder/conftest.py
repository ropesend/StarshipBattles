"""
Conftest for builder module tests.

Provides fixtures and setup for builder-related tests.

Note: Test isolation (cleanup) is handled by reset_game_state in root conftest.py.
No module-specific autouse fixture is needed here.
"""
from tests.fixtures.paths import data_dir, project_root, unit_test_data_dir  # noqa: F401
from tests.fixtures.common import initialized_ship_data, initialized_ship_data_with_modifiers  # noqa: F401
from tests.fixtures.ships import basic_cruiser_ship, basic_escort_ship  # noqa: F401
