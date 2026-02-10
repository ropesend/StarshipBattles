"""Shared fixtures for battle controller tests."""
import pytest
from unittest.mock import Mock

from game.simulation.battle_config import BattleConfig, BattleMode
from game.simulation.services.battle_service import BattleResult


@pytest.fixture
def mock_service():
    """Create a mock BattleService."""
    service = Mock()
    service.create_battle.return_value = BattleResult(success=True)
    service.add_ship.return_value = BattleResult(success=True)
    service.start_battle.return_value = BattleResult(success=True)
    service.update.return_value = BattleResult(success=True)
    service.is_battle_over.return_value = False
    service.get_winner.return_value = None
    service.get_all_ships.return_value = []
    service.get_alive_ships.return_value = []
    service.get_engine.return_value = Mock(tick_counter=0, ships=[], projectiles=[])
    return service


@pytest.fixture
def controller(mock_service):
    """Create a BattleController with mock service."""
    from game.simulation.battle_controller import BattleController
    return BattleController(service=mock_service)


@pytest.fixture
def mock_ship():
    """Create a mock Ship object."""
    ship = Mock()
    ship.name = "Test Ship"
    ship.is_alive = True
    ship.team_id = 0
    ship.x = 50000
    ship.y = 50000
    ship.ship_class = "frigate"
    ship.theme_id = "default"
    ship.color = (255, 0, 0)
    ship.hp = 100
    ship.max_hp = 100
    return ship


@pytest.fixture
def basic_config():
    """Create a basic BattleConfig."""
    return BattleConfig(
        mode=BattleMode.MANUAL,
        seed=12345,
        max_ticks=10000,
    )
