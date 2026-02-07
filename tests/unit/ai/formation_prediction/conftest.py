"""
Shared fixtures for formation prediction tests.
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
def mock_controller():
    """Create a mock AI controller."""
    controller = MagicMock()
    controller.navigate_to = MagicMock()
    return controller


@pytest.fixture
def mock_ship():
    """Create a mock ship for formation testing."""
    ship = MagicMock()
    ship.position = pygame.math.Vector2(100, 100)
    ship.angle = 0
    ship.radius = 25
    ship.max_speed = 500
    ship.turn_speed = 90
    ship.turn_throttle = 1.0
    ship.engine_throttle = 1.0
    ship.acceleration_rate = 100
    ship.formation.active = True
    ship.formation.offset = pygame.math.Vector2(50, 50)
    ship.formation.rotation_mode = 'relative'
    ship.formation.master = None

    # Interface method mocks - use lambdas to dynamically return current values
    ship.get_position.side_effect = lambda: ship.position
    ship.get_rotation.side_effect = lambda: ship.angle
    ship.get_radius.return_value = ship.radius
    ship.get_max_speed.side_effect = lambda: ship.max_speed
    ship.get_turn_speed.side_effect = lambda: ship.turn_speed
    ship.get_acceleration_rate.return_value = ship.acceleration_rate
    ship.get_formation_offset.side_effect = lambda: ship.formation.offset
    ship.get_formation_rotation_mode.side_effect = lambda: ship.formation.rotation_mode
    ship.get_formation_master.side_effect = lambda: ship.formation.master

    # Interface method setters should update attributes for assertion checking
    def set_in_formation(value):
        ship.formation.active = value
    ship.set_in_formation.side_effect = set_in_formation

    def set_throttle(value):
        ship.engine_throttle = value
    ship.set_throttle.side_effect = set_throttle

    def set_rotation(value):
        ship.angle = value
        ship.get_rotation.side_effect = lambda: ship.angle
    ship.set_rotation.side_effect = set_rotation

    def adjust_position(delta):
        ship.position = ship.position + delta
    ship.adjust_position.side_effect = adjust_position

    return ship


@pytest.fixture
def mock_master():
    """Create a mock formation master ship."""
    master = MagicMock()
    master.position = pygame.math.Vector2(0, 0)
    master.angle = 0
    master.is_alive = True
    master.is_derelict = False
    master.velocity = pygame.math.Vector2(10, 0)
    master.current_speed = 10
    master.is_thrusting = True
    master.max_speed = 500
    master.engine_throttle = 1.0
    return master


@pytest.fixture
def formation_behavior(mock_controller, mock_ship, mock_master):
    """Create a FormationBehavior with mocked components."""
    from game.ai.behaviors import FormationBehavior

    mock_ship.formation.master = mock_master
    mock_ship.get_formation_master.return_value = mock_master
    mock_controller.ship = mock_ship

    behavior = FormationBehavior(mock_controller)
    return behavior
