import unittest
from unittest.mock import MagicMock, patch
import pygame

from game.engine.spatial import SpatialGrid
from game.ui.screens.battle_scene import BattleScene
from game.simulation.entities.ship import Ship, initialize_ship_data
from game.simulation.components.component import load_components

from game.ai.controller import StrategyManager
from tests.fixtures.paths import get_project_root, get_data_dir, get_unit_test_data_dir

class TestBattleSetupLogic(unittest.TestCase):
    """Test SpatialGrid functionality and BattleScene setup logic."""


    def setUp(self):
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
        # Mock window surface if BattleScene needs it for initialization
        # This part was in the user's provided 'Code Edit' but not directly related to the original file's tests.
        # Keeping it commented out as it might be for a different test context.
        # self.setup = BattleSetup() # Original file does not use BattleSetup directly in tests
        # self.setup.window = MagicMock()
        # self.setup.width = 800
        # self.setup.height = 600


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
        self.assertIn(obj1, res)
        self.assertIn(obj2, res)
        self.assertIn(obj3, res)
        self.assertNotIn(obj4, res)

    def test_battle_scene_start_assignment(self):
        """Verify BattleScene.start assigns teams and creates AI controllers."""
        scene = BattleScene(1000, 1000)
        
        ship1 = Ship("T1-1", 0, 0, (255,0,0), team_id=0)
        ship2 = Ship("T2-1", 1000, 1000, (0,0,255), team_id=1)
        
        scene.start([ship1], [ship2])
        
        self.assertEqual(len(scene.ships), 2)
        self.assertEqual(len(scene.ai_controllers), 2)
        
        # Check team assignments (should be forced by start)
        self.assertEqual(ship1.team_id, 0)
        self.assertEqual(ship2.team_id, 1)
        
        # Check AI target teams
        # AIController(ship, grid, enemy_team_id)
        ai1 = next(ai for ai in scene.ai_controllers if ai.ship == ship1)
        ai2 = next(ai for ai in scene.ai_controllers if ai.ship == ship2)
        
        self.assertEqual(ai1.enemy_team_id, 1)
        self.assertEqual(ai2.enemy_team_id, 0)

    def test_battle_scene_clear_state(self):
        """Verify BattleScene clears state between starts."""
        scene = BattleScene(1000, 1000)
        ship1 = Ship("S1", 0, 0, (255,255,255))
        scene.start([ship1], [])
        self.assertEqual(len(scene.ships), 1)
        
        ship2 = Ship("S2", 0, 0, (255,255,255))
        scene.start([ship2], [])
        self.assertEqual(len(scene.ships), 1)
        self.assertEqual(scene.ships[0], ship2)
        self.assertEqual(len(scene.projectiles), 0)

if __name__ == '__main__':
    unittest.main()
