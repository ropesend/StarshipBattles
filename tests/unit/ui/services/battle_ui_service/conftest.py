"""Shared fixtures for BattleUIService tests."""
import pytest
from unittest.mock import Mock

from game.core.math import Vector2


@pytest.fixture
def mock_ship():
    """Create a mock ship with all required attributes."""
    ship = Mock()
    ship.id = "ship_1"
    ship.name = "Test Ship"
    ship.team_id = 0
    ship.position = Vector2(100, 200)
    ship.velocity = Vector2(10, 5)
    # Ship uses 'angle' internally (from PhysicsBody), DTO exposes as 'heading'
    ship.angle = 1.5
    ship.is_alive = True
    ship.is_derelict = False
    ship.hp = 80.0
    ship.max_hp = 100.0
    ship.current_shields = 50.0
    ship.max_shields = 100.0
    ship.current_speed = 30.0
    ship.max_speed = 60.0
    ship.mass = 1000.0
    ship.total_thrust = 500.0
    ship.turn_speed = 0.1
    ship.total_shots_fired = 5
    ship.crew_onboard = 10
    ship.crew_required = 10
    ship.current_target = None
    ship.secondary_targets = []
    ship.max_targets = 1
    ship.ai_strategy = "aggressive"
    ship.source_file = "ships/test.json"
    ship.layers = {}

    # Mock resources using proper public API
    mock_resource = Mock()
    mock_resource.name = "fuel"
    mock_resource.current_value = 50.0
    mock_resource.max_value = 100.0

    ship.resources = Mock()
    ship.resources.get_all_resources.return_value = [mock_resource]

    return ship


@pytest.fixture
def mock_projectile():
    """Create a mock projectile."""
    proj = Mock()
    proj.id = "proj_1"
    proj.position = Vector2(50, 50)
    proj.velocity = Vector2(100, 0)
    proj.color = (255, 200, 50)
    proj.radius = 4.0
    proj.damage = 25.0
    proj.hp = 10.0
    proj.max_hp = 10.0
    proj.status = "active"
    proj.endurance = 5.0
    proj.max_endurance = 10.0
    proj.target = None
    proj.max_speed = 100.0
    return proj


@pytest.fixture
def mock_battle_service(mock_ship):
    """Create mock BattleService with ships."""
    service = Mock()
    engine = Mock()
    engine.ships = [mock_ship]
    engine.projectiles = []
    engine.recent_beams = []
    engine.tick_counter = 100
    engine.is_battle_over.return_value = False
    engine.get_winner.return_value = None
    service.get_engine.return_value = engine
    return service


@pytest.fixture
def mock_battle_service_with_projectile(mock_projectile):
    """Create mock BattleService with a projectile."""
    service = Mock()
    engine = Mock()
    engine.ships = []
    engine.projectiles = [mock_projectile]
    engine.recent_beams = []
    engine.tick_counter = 0
    engine.is_battle_over.return_value = False
    engine.get_winner.return_value = None
    service.get_engine.return_value = engine
    return service


@pytest.fixture
def mock_battle_service_with_beams():
    """Create mock BattleService with beams."""
    service = Mock()
    engine = Mock()
    engine.ships = []
    engine.projectiles = []
    engine.recent_beams = [
        {
            "start": Vector2(0, 0),
            "end": Vector2(100, 100),
            "color": (255, 0, 0)
        }
    ]
    engine.tick_counter = 0
    engine.is_battle_over.return_value = False
    engine.get_winner.return_value = None
    service.get_engine.return_value = engine
    return service
