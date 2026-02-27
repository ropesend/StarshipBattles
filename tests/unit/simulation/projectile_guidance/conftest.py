"""
Shared fixtures for projectile guidance tests.
"""
import pytest
import pygame
from unittest.mock import MagicMock

from game.simulation.entities.projectile import Projectile


@pytest.fixture(scope="module", autouse=True)
def init_pygame():
    """Initialize pygame for vector operations."""
    pygame.init()
    yield
    pygame.quit()


@pytest.fixture
def mock_owner():
    """Create a minimal owner mock with required protocol attributes."""
    owner = MagicMock(spec=[])  # Empty spec prevents auto-creating attributes
    owner.team_id = 0
    owner.is_alive = True
    owner.position = pygame.math.Vector2(0, 0)
    # combat_engine with solve_lead (required for projectile guidance)
    owner.combat_engine = MagicMock()
    owner.combat_engine.solve_lead = MagicMock(return_value=0)  # Default: no lead
    return owner


@pytest.fixture
def mock_target():
    """Create a minimal target mock."""
    target = MagicMock()
    target.is_alive = True
    target.position = pygame.math.Vector2(1000, 0)
    target.velocity = pygame.math.Vector2(0, 0)
    return target


@pytest.fixture
def guided_missile(mock_owner, mock_target):
    """Create a standard guided missile for testing."""
    return Projectile(
        owner=mock_owner,
        position=pygame.math.Vector2(0, 0),
        velocity=pygame.math.Vector2(100, 0),  # Moving right
        damage=50,
        range_val=5000,
        endurance=10.0,
        proj_type='missile',
        turn_rate=90,  # 90 deg/sec
        max_speed=100,
        target=mock_target,
        hp=5
    )
