import pytest
from unittest.mock import MagicMock, patch
import pygame

from game.engine.spatial import SpatialGrid
from game.ui.screens.battle_scene import BattleScene
from game.simulation.entities.ship import Ship, initialize_ship_data
from game.simulation.components.component import load_components

from game.ai.controller import StrategyManager
from tests.fixtures.paths import get_project_root, get_data_dir, get_unit_test_data_dir


@pytest.fixture(autouse=True)
def setup_game_data():
    """Initialize pygame and game data before each test."""
    pygame.init()
    # Ensure data dir is accessible
    initialize_ship_data(str(get_project_root()))
    load_components(str(get_data_dir() / "components.json"))
    manager = StrategyManager.instance()
    manager.load_data(
         str(get_unit_test_data_dir()),
         targeting_file="test_targeting_policies.json",
         movement_file="test_movement_policies.json",
         strategy_file="test_combat_strategies.json"
    )
    manager._loaded = True


class TestBattleSetupLogic:
    """Test SpatialGrid functionality and BattleScene setup logic."""

    def test_spatial_grid_insertion_query(self):
        """Verify SpatialGrid correctly stores and retrieves objects."""
        grid = SpatialGrid(cell_size=100)

        # Mock object with position
        class MockObj:
            def __init__(self, x, y):
                self.position = pygame.math.Vector2(x, y)

        obj1 = MockObj(50, 50)   # Cell (0,0)
        obj2 = MockObj(150, 50)  # Cell (1,0)
        obj3 = MockObj(50, 150)  # Cell (0,1)
        obj4 = MockObj(500, 500) # Far away

        grid.insert(obj1)
        grid.insert(obj2)
        grid.insert(obj3)
        grid.insert(obj4)

        # Query at (0,0) with radius 10 (should only see obj1)
        # SpatialGrid.query_radius(pos, radius) checks cells around pos.
        # steps = ceil(10 / 100) = 1.
        # Checks cells (0-1 to 0+1, 0-1 to 0+1) = (-1 to 1, -1 to 1).
        # This will find obj1, obj2, obj3.
        res = grid.query_radius(pygame.math.Vector2(50, 50), 10)
        assert obj1 in res
        assert obj2 in res
        assert obj3 in res
        assert obj4 not in res

    def test_battle_scene_start_assignment(self):
        """Verify BattleScene.start assigns teams and creates AI controllers."""
        scene = BattleScene(1000, 1000)

        ship1 = Ship("T1-1", 0, 0, (255,0,0), team_id=0)
        ship2 = Ship("T2-1", 1000, 1000, (0,0,255), team_id=1)

        scene.start([ship1], [ship2])

        assert len(scene.ships) == 2
        assert len(scene.ai_controllers) == 2

        # Check team assignments (should be forced by start)
        assert ship1.team_id == 0
        assert ship2.team_id == 1

        # Check AI target teams
        # AIController(ship, grid, enemy_team_id)
        ai1 = next(ai for ai in scene.ai_controllers if ai.ship == ship1)
        ai2 = next(ai for ai in scene.ai_controllers if ai.ship == ship2)

        assert ai1.enemy_team_id == 1
        assert ai2.enemy_team_id == 0

    def test_battle_scene_clear_state(self):
        """Verify BattleScene clears state between starts."""
        scene = BattleScene(1000, 1000)
        ship1 = Ship("S1", 0, 0, (255,255,255))
        scene.start([ship1], [])
        assert len(scene.ships) == 1

        ship2 = Ship("S2", 0, 0, (255,255,255))
        scene.start([ship2], [])
        assert len(scene.ships) == 1
        assert scene.ships[0] == ship2
        assert len(scene.projectiles) == 0
