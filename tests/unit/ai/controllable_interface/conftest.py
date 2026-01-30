"""
Shared fixtures for IControllable interface tests.
"""
import pytest
from unittest.mock import MagicMock
from pygame.math import Vector2


@pytest.fixture
def mock_ship():
    """Create a mock ship with typical attributes."""
    ship = MagicMock()
    ship.position = Vector2(100, 200)
    ship.velocity = Vector2(10, 5)
    ship.angle = 45.0
    ship.team_id = 1
    ship.is_alive = True
    ship.max_speed = 100.0
    ship.max_weapon_range = 500.0
    ship.radius = 40.0
    ship.turn_speed = 180.0
    ship.acceleration_rate = 50.0
    ship.current_speed = 50.0
    ship.turn_throttle = 1.0
    ship.engine_throttle = 1.0
    ship.comp_trigger_pulled = False
    ship.current_target = None
    ship.secondary_targets = []
    ship.formation_members = []
    ship.formation_master = None
    ship.in_formation = False
    ship.formation_offset = None
    ship.vehicle_type = 'Ship'
    ship.ai_strategy = 'standard_ranged'
    ship.max_targets = 1
    ship.is_thrusting = False
    ship.is_derelict = False
    return ship
