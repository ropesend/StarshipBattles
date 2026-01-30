"""
Shared fixtures for target evaluator tests.
"""
import pytest
import pygame
from unittest.mock import MagicMock


@pytest.fixture(autouse=True)
def pygame_init():
    """Initialize pygame for Vector2 usage."""
    pygame.init()
    yield
    pygame.quit()


@pytest.fixture
def ship():
    """Create a mock ship for testing."""
    s = MagicMock()
    s.position = pygame.math.Vector2(0, 0)
    s.angle = 0
    s.team_id = 0
    s.get_components_by_ability = MagicMock(return_value=[])
    return s


@pytest.fixture
def target():
    """Create a mock target for testing."""
    t = MagicMock()
    t.position = pygame.math.Vector2(100, 0)
    t.mass = 1000
    t.velocity = pygame.math.Vector2(10, 0)
    t.type = 'ship'
    return t


@pytest.fixture
def target_with_hp():
    """Create a target with HP components."""
    t = MagicMock()
    t.position = pygame.math.Vector2(100, 0)
    t.mass = 1000
    t.velocity = pygame.math.Vector2(0, 0)
    t.type = 'ship'

    comp = MagicMock()
    comp.max_hp = 100
    comp.current_hp = 50
    t.get_all_components = MagicMock(return_value=[comp])

    return t
