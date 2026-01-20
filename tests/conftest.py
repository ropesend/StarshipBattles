"""
Root test configuration for all tests.

Provides session-scoped fixtures for expensive data loading operations.
"""
import pytest
import pygame
import os

from tests.fixtures.paths import get_data_dir, get_project_root
from game.simulation.entities.ship import initialize_ship_data
from game.simulation.components.component import load_components, load_modifiers


# Ensure headless pygame for all tests
os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')


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

    initialize_ship_data(str(get_project_root()))
    load_components(str(get_data_dir() / "components.json"))
    return True


@pytest.fixture(scope="session")
def global_ship_data_with_modifiers(global_ship_data):
    """
    Load ship data and modifiers once per test session.

    Extends global_ship_data with modifier loading.

    Returns:
        True when data is loaded
    """
    load_modifiers(str(get_data_dir() / "modifiers.json"))
    return True
