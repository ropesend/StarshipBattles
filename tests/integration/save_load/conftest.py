"""Shared fixtures for save/load tests."""
import pytest
import os
import tempfile
import shutil

from game.strategy.engine.game_session import GameSession
from game.strategy.engine.game_config import GameConfig, PlayerConfig
from game.strategy.data.fleet import Fleet
from game.core.hex_math import HexCoord
from tests.conftest import make_mock_ship_instance


@pytest.fixture
def temp_save_folder():
    """Create a temporary folder for saves and clean up after test."""
    temp_dir = tempfile.mkdtemp(prefix="test_saves_")
    yield temp_dir
    # Cleanup
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)


@pytest.fixture
def minimal_game_session():
    """Create a minimal game session for testing."""
    config = GameConfig()
    config.galaxy_radius = 300
    config.system_count = 2
    config.players = [
        PlayerConfig(name="TestPlayer", is_human=True, color=(0, 100, 200)),
        PlayerConfig(name="TestEnemy", is_human=False, color=(200, 100, 0)),
    ]
    return GameSession(config=config)


@pytest.fixture
def game_session_with_state(minimal_game_session):
    """Create a game session with some game state to preserve."""
    session = minimal_game_session

    # Add some fleets
    fleet1 = Fleet(100, 0, HexCoord(10, 10), speed=15.0)
    fleet1.ships = [make_mock_ship_instance("Scout", 0)]
    session.empires[0].add_fleet(fleet1)

    fleet2 = Fleet(200, 1, HexCoord(20, 20), speed=10.0)
    fleet2.ships = [make_mock_ship_instance("Destroyer", 1)]
    session.empires[1].add_fleet(fleet2)

    # Advance a few turns
    session.process_turn()
    session.process_turn()

    return session
