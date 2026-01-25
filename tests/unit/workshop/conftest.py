"""
Conftest for builder module tests.

Provides fixtures and setup for builder-related tests.
"""
import pytest

from tests.fixtures.paths import data_dir, project_root, unit_test_data_dir  # noqa: F401
from tests.fixtures.common import initialized_ship_data, initialized_ship_data_with_modifiers  # noqa: F401
from tests.fixtures.ships import basic_cruiser_ship, basic_escort_ship  # noqa: F401


@pytest.fixture(autouse=True)
def builder_test_setup():
    """Auto-setup for builder tests. Cleanup handled by root conftest."""
    yield
