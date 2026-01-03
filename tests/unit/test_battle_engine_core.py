
import unittest
import math
import pygame
from pygame.math import Vector2
from unittest.mock import MagicMock, patch

# Adjust path to find modules if necessary (assuming running from root)
import sys
import os
# Ensure the root directory is in python path
root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if root_dir not in sys.path:
    sys.path.append(root_dir)

# Also add the current directory just in case it's run differently
if os.getcwd() not in sys.path:
    sys.path.append(os.getcwd())

try:
    from game.simulation.systems.battle_engine import BattleEngine
    from game.simulation.entities.ship import Ship
    from game.simulation.entities.projectile import Projectile
    from game.engine.spatial import SpatialGrid
    from game.core.constants import AttackType
except ImportError:
    # If running directly from tests folder, might need adjustment
    sys.path.append(os.path.join(os.getcwd(), '..'))
    from game.simulation.systems.battle_engine import BattleEngine
    from game.simulation.entities.ship import Ship
    from game.simulation.entities.projectile import Projectile
    from game.engine.spatial import SpatialGrid
    from game.core.constants import AttackType

class TestBattleEngineCore(unittest.TestCase):
    def setUp(self):
        # Initialize BattleEngine with mocked logger
        self.mock_logger = MagicMock()
        self.engine = BattleEngine(logger=self.mock_logger)
        
        # Create dummy ships
        self.ship1 = Ship("TestShip1", 0, 0, (255, 0, 0), team_id=0)
        self.ship2 = Ship("TestShip2", 200, 0, (0, 0, 255), team_id=1)
        
        # Override some ship properties for stable testing
        self.ship1.radius = 20
        self.ship2.radius = 20
        
        # Add dummy components for HP
        dummy_comp1 = MagicMock()
        dummy_comp1.current_hp = 100
        dummy_comp1.max_hp = 100
        
        dummy_comp2 = MagicMock()
        dummy_comp2.current_hp = 100
        dummy_comp2.max_hp = 100
        
        # Manually constructing minimal layer structure
        self.ship1.layers = {
            'CORE': {'components': [dummy_comp1]}
        }
        self.ship2.layers = {
            'CORE': {'components': [dummy_comp2]}
        }
        
        self.ship1.is_alive = True
        self.ship2.is_alive = True

        self.engine.ships = [self.ship1, self.ship2]
        
    def test_spatial_grid_integration(self):
        """
        Test engine.update() to verify that ships and projectiles are correctly inserted into the grid every tick.
        Test object removal from the grid when is_alive becomes False.
        """
        # Add a backup ship to Team 0
        ship3 = Ship("BackupShip", -100, 0, (0, 255, 0), team_id=0)
        ship3.radius = 20
        ship3.is_alive = True
        self.engine.ships.append(ship3)

        # 1. Verify insertion after update
        self.engine.update()
        
        found_ships_1 = self.engine.grid.query_radius(self.ship1.position, 100)
        self.assertIn(self.ship1, found_ships_1, "Ship1 should be in spatial grid after update")
        
        found_ships_2 = self.engine.grid.query_radius(self.ship2.position, 100)
        self.assertIn(self.ship2, found_ships_2, "Ship2 should be in spatial grid after update")
        
        # 2. Add a projectile and verify insertion (Integration check)
        # Using mock projectile to simplify
        proj = MagicMock()
        proj.position = Vector2(50, 50)
        proj.velocity = Vector2(10, 0)
        proj.is_alive = True
        proj.type = AttackType.PROJECTILE # Ensure clean Enum usage
        
        # Add via manager or engine method?
        # Engine update expects projectiles in manager
        self.engine.projectile_manager.add_projectile(proj)
        
        self.engine.update()
        found_objs = self.engine.grid.query_radius(Vector2(50, 50), 100)
        self.assertIn(proj, found_objs, "Projectile should be in spatial grid after update")

        # 3. Test removal when dead
        self.ship1.is_alive = False
        proj.is_alive = False
        
        self.engine.update()
        
        found_objs_dead_ship = self.engine.grid.query_radius(self.ship1.position, 100)
        self.assertNotIn(self.ship1, found_objs_dead_ship, "Dead ship should NOT be in spatial grid")
        
        found_objs_dead_proj = self.engine.grid.query_radius(Vector2(50, 50) + proj.velocity, 100)
        self.assertNotIn(proj, found_objs_dead_proj, "Dead projectile should NOT be in spatial grid")

    def test_system_delegation(self):
        """
        Verify that BattleEngine delegates tasks to subsystems.
        """
        # Patch systems to verify calls
        with patch.object(self.engine.collision_system, 'process_ramming') as mock_ram, \
             patch.object(self.engine.projectile_manager, 'update') as mock_proj_update, \
             patch.object(self.engine.collision_system, 'process_beam_attack') as mock_beam:
            
            # 1. Run update - checks ramming and projectile update
            self.engine.update()
            
            mock_ram.assert_called()
            mock_proj_update.assert_called()
            
            # 2. Check Beam Attack delegation
            # Simulate a ship firing a beam during update
            beam_attack = {'type': AttackType.BEAM, 'damage': 10}
            
            self.ship1.comp_trigger_pulled = True
            with patch.object(self.ship1, 'fire_weapons', return_value=[beam_attack]):
                self.engine.update()
            
            mock_beam.assert_called()

if __name__ == '__main__':
    unittest.main()
