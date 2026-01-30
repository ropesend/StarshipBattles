"""
Shared fixtures for collision edge case tests.
"""
import pytest
from unittest.mock import MagicMock
from pygame.math import Vector2

from game.simulation.projectile_manager import ProjectileManager
from game.engine.collision import CollisionSystem


@pytest.fixture
def projectile_manager():
    """Create a ProjectileManager instance."""
    return ProjectileManager()


@pytest.fixture
def collision_system():
    """Create a CollisionSystem instance."""
    return CollisionSystem()


@pytest.fixture
def mock_grid():
    """Create a mock spatial grid."""
    grid = MagicMock()
    grid.query_radius.return_value = []
    return grid


@pytest.fixture
def mock_target_ship():
    """Create a mock target ship for collision tests."""
    ship = MagicMock()
    ship.position = Vector2(100, 0)
    ship.velocity = Vector2(0, 0)
    ship.radius = 20
    ship.is_alive = True
    ship.team_id = 1
    return ship


@pytest.fixture
def mock_projectile():
    """Create a mock projectile."""
    proj = MagicMock()
    proj.position = Vector2(0, 0)
    proj.velocity = Vector2(10, 0)
    proj.radius = 2
    proj.damage = 10
    proj.is_alive = True
    proj.team_id = 0
    proj.type = 'projectile'
    proj.source_weapon = None
    proj.distance_traveled = 0
    proj.target = None
    proj.status = 'active'
    return proj
