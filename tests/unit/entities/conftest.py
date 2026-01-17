"""
Conftest for entities module tests.

Provides fixtures and setup for entity-related tests.
"""
import pytest
import pygame

from tests.fixtures.paths import data_dir, project_root, unit_test_data_dir  # noqa: F401
from tests.fixtures.common import initialized_ship_data, initialized_ship_data_with_modifiers  # noqa: F401
from tests.fixtures.ships import basic_cruiser_ship  # noqa: F401
from game.core.registry import RegistryManager


@pytest.fixture(autouse=True)
def entities_test_setup():
    """Auto-setup for entities tests: initialize pygame and clean up after."""
    if not pygame.get_init():
        pygame.init()
    yield
    RegistryManager.instance().clear()


# Alias for backward compatibility with existing tests
basic_ship = basic_cruiser_ship
