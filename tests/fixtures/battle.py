"""
Shared battle engine fixtures for tests.

This module provides reusable battle engine fixtures that can be used across all tests,
eliminating boilerplate battle setup code and ensuring consistent test setups.

Usage in tests:
    def test_something(battle_engine):
        # battle_engine is automatically provided by pytest
        assert battle_engine.ships == []

    def test_with_factory():
        # Or use factory directly for custom setup
        from tests.fixtures.battle import create_battle_engine
        engine = create_battle_engine(enable_logging=True)

Available fixtures:
    - battle_engine: Clean BattleEngine with no ships
    - battle_engine_with_ships: BattleEngine with two opposing ships
    - mock_battle_engine: Mock battle engine for unit tests
    - mock_battle_scene: Mock battle scene with engine
"""
import pytest
from unittest.mock import Mock

from game.simulation.systems.battle_engine import BattleEngine, BattleLogger
from tests.fixtures.ships import create_test_ship


# =============================================================================
# Factory Functions
# =============================================================================

def create_battle_engine(enable_logging: bool = False, log_filename: str = "test_battle_log.txt") -> BattleEngine:
    """
    Create a battle engine for testing.

    Args:
        enable_logging: If True, enable battle logging (default: False)
        log_filename: Filename for battle log if logging enabled

    Returns:
        Configured BattleEngine instance
    """
    logger = BattleLogger(filename=log_filename, enabled=enable_logging)
    return BattleEngine(logger=logger)


def create_battle_engine_with_ships(
    team1_count: int = 1,
    team2_count: int = 1,
    enable_logging: bool = False,
) -> BattleEngine:
    """
    Create a battle engine with ships already added.

    Args:
        team1_count: Number of ships for team 0
        team2_count: Number of ships for team 1
        enable_logging: If True, enable battle logging

    Returns:
        BattleEngine with ships configured
    """
    engine = create_battle_engine(enable_logging=enable_logging)

    # Create team 1 ships (left side)
    team1_ships = []
    for i in range(team1_count):
        ship = create_test_ship(
            name=f"Team1Ship{i}",
            x=100 + (i * 50),
            y=400,
            team_id=0,
            add_bridge=True,
            add_engine=True,
            add_weapons=1,
        )
        team1_ships.append(ship)

    # Create team 2 ships (right side)
    team2_ships = []
    for i in range(team2_count):
        ship = create_test_ship(
            name=f"Team2Ship{i}",
            x=700 + (i * 50),
            y=400,
            team_id=1,
            add_bridge=True,
            add_engine=True,
            add_weapons=1,
        )
        team2_ships.append(ship)

    # Start the battle
    engine.start(team1_ships, team2_ships)

    return engine


def create_mock_battle_engine() -> Mock:
    """
    Create a mock battle engine for unit tests.

    Returns a Mock object with common BattleEngine attributes/methods stubbed.

    Returns:
        Mock object mimicking BattleEngine interface
    """
    engine = Mock()
    engine.tick_counter = 0
    engine.ships = []
    engine.projectiles = []
    engine.recent_beams = []
    engine.winner = None
    engine.update = Mock()
    engine.is_battle_over = Mock(return_value=False)
    engine.start = Mock()
    engine.grid = Mock()
    engine.collision_system = Mock()
    engine.projectile_manager = Mock()
    return engine


def create_mock_battle_scene(engine: Mock = None) -> Mock:
    """
    Create a mock battle scene for unit tests.

    Args:
        engine: Mock battle engine to use (creates new one if None)

    Returns:
        Mock object mimicking BattleScene interface
    """
    if engine is None:
        engine = create_mock_battle_engine()

    scene = Mock()
    scene.engine = engine
    scene.headless_mode = False
    scene.sim_paused = True
    scene.test_mode = False
    scene.test_scenario = None
    scene.test_tick_count = 0
    scene.test_completed = False
    scene.action_return_to_test_lab = False
    scene.camera = Mock()
    scene.camera.fit_objects = Mock()
    return scene


# =============================================================================
# Pytest Fixtures
# =============================================================================

@pytest.fixture
def battle_engine():
    """
    Create a clean battle engine with no ships.

    Returns a BattleEngine instance with logging disabled.
    """
    return create_battle_engine()


@pytest.fixture
def battle_engine_with_ships():
    """
    Create a battle engine with two opposing ships.

    Returns a BattleEngine with one ship per team, ready for combat simulation.
    """
    return create_battle_engine_with_ships()


@pytest.fixture
def mock_battle_engine():
    """
    Create a mock battle engine for unit tests.

    Returns a Mock object with common BattleEngine methods stubbed.
    Useful for testing code that depends on BattleEngine without
    needing full simulation.
    """
    return create_mock_battle_engine()


@pytest.fixture
def mock_battle_scene(mock_battle_engine):
    """
    Create a mock battle scene with engine.

    Returns a Mock object with common BattleScene attributes set.
    The engine attribute is set to the mock_battle_engine fixture.
    """
    return create_mock_battle_scene(engine=mock_battle_engine)
