"""
Conftest for builder module tests.

Provides fixtures and setup for builder-related tests.
"""
import pytest
import pygame

from tests.fixtures.paths import data_dir, project_root, unit_test_data_dir  # noqa: F401
from tests.fixtures.common import initialized_ship_data, initialized_ship_data_with_modifiers  # noqa: F401
from tests.fixtures.ships import basic_cruiser_ship, basic_escort_ship  # noqa: F401
from game.core.registry import RegistryManager


@pytest.fixture(autouse=True)
def builder_test_setup():
    """Auto-setup for builder tests: initialize pygame and clean up after."""
    if not pygame.get_init():
        pygame.init()
    yield
    RegistryManager.instance().clear()
