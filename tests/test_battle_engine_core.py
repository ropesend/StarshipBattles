
import unittest
import math
import pygame
from pygame.math import Vector2
from unittest.mock import MagicMock, patch

# Adjust path to find modules if necessary (assuming running from root)
import sys
import os
# Ensure the root directory is in python path
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root_dir not in sys.path:
    sys.path.append(root_dir)

# Also add the current directory just in case it's run differently
if os.getcwd() not in sys.path:
    sys.path.append(os.getcwd())

try:
    from battle_engine import BattleEngine
    from ship import Ship
    from projectiles import Projectile
    from spatial import SpatialGrid
except ImportError:
    # If running directly from tests folder, might need adjustment
    sys.path.append(os.path.join(os.getcwd(), '..'))
    from battle_engine import BattleEngine
    from ship import Ship
    from projectiles import Projectile
    from spatial import SpatialGrid

class TestBattleEngineCore(unittest.TestCase):
    def setUp(self):
        # Initialize BattleEngine
        self.engine = BattleEngine()
        
        # Create dummy ships
        # Ship(name, x, y, color, team_id, ship_class, theme_id)
        self.ship1 = Ship("TestShip1", 0, 0, (255, 0, 0), team_id=0)
        self.ship2 = Ship("TestShip2", 200, 0, (0, 0, 255), team_id=1)
        
        # Override some ship properties for stable testing
        self.ship1.radius = 20
        self.ship2.radius = 20
        self.ship1.hp_pool = 100 # Adjusting for how Ship handles hp via @property or attributes
        # Ship.hp is a property summing components. We need to mock components or manually set logic if possible.
        # However, Ship.hp is a getter. Setter is not defined?
        # Let's check Ship.hp implementation in ship.py
        # @property def hp(self): return sum(c.current_hp ...)
        # So we cannot set self.ship1.hp = 100 directly if it relies on components.
        # But we can mock the property or add a dummy component.
        
        # Let's add a dummy component to hold HP
        dummy_comp1 = MagicMock()
        dummy_comp1.current_hp = 100
        dummy_comp1.max_hp = 100
        
        dummy_comp2 = MagicMock()
        dummy_comp2.current_hp = 100
        dummy_comp2.max_hp = 100
        
        # Inject into layers
        from components import LayerType
        # We need to ensure layers exist. Ship init does this.
        # But we used mocked objects, so let's just forcefully inject
        
        # Check if ship has layers initialized
        if not self.ship1.layers:
             self.ship1.layers = {LayerType.CORE: {'components': []}}
             
        # Ideally, we use add_component logic or just direct insert for test speed
        # But allow simple access
        # Ship.hp sums from self.layers.values() -> 'components'
        
        # Manually constructing minimal layer structure
        self.ship1.layers = {
            'CORE': {'components': [dummy_comp1]}
        }
        self.ship2.layers = {
            'CORE': {'components': [dummy_comp2]}
        }
        
        self.ship1.is_alive = True
        self.ship2.is_alive = True

        # Manually link references usually handled by start()
        self.engine.ships = [self.ship1, self.ship2]
        
    def test_spatial_grid_integration(self):
        """
        Test engine.update() to verify that ships and projectiles are correctly inserted into the grid every tick.
        Test object removal from the grid when is_alive becomes False.
        """
        # Add a backup ship to Team 0 so the battle doesn't end when ship1 dies
        # If battle ends, engine.update() returns early and doesn't clear the grid
        ship3 = Ship("BackupShip", -100, 0, (0, 255, 0), team_id=0)
        ship3.radius = 20
        ship3.is_alive = True
        self.engine.ships.append(ship3)

        # 1. Verify insertion after update
        self.engine.update()
        
        # Check if ships are in grid
        # query_radius at ship positions should find them
        found_ships_1 = self.engine.grid.query_radius(self.ship1.position, 100)
        self.assertIn(self.ship1, found_ships_1, "Ship1 should be in spatial grid after update")
        
        found_ships_2 = self.engine.grid.query_radius(self.ship2.position, 100)
        self.assertIn(self.ship2, found_ships_2, "Ship2 should be in spatial grid after update")
        
        # 2. Add a projectile and verify insertion
        proj = Projectile(
            owner=self.ship1,
            position=Vector2(50, 50),
            velocity=Vector2(10, 0),
            damage=10,
            range_val=1000,
            endurance=5,
            proj_type='projectile'
        )
        self.engine.projectiles.append(proj)
        
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


    def test_beam_weapon_raycasting(self):
        """
        Unit test _process_beam_attack with hardcoded vectors.
        Verify hit detection math: direct hit, near miss, range limits.
        """
        # Setup source and target
        source_pos = Vector2(0, 0)
        target = self.ship2 # at 200, 0
        target.position = Vector2(200, 0)
        target.radius = 20
        # target.hp is controlled by dummy_comp
        target_comp = target.layers['CORE']['components'][0]
        target_comp.current_hp = 100
        target.is_alive = True
        
        # Mock component for hit chance (always hit)
        mock_component = MagicMock()
        mock_component.calculate_hit_chance.return_value = 1.0
        
        # Case 1: Direct Hit
        attack_hit = {
            'origin': source_pos,
            'direction': Vector2(1, 0), # Directly at target (200, 0)
            'range': 300,
            'target': target,
            'damage': 10,
            'component': mock_component
        }
        
        # Force deterministic random if needed
        with patch('random.random', return_value=0.0): # 0.0 < 1.0 is True
             # We need to mock take_damage primarily because Ship.take_damage might be complex
             # But let's try to let it run. Ship.take_damage logic isn't fully visible in my minimal reading
             # ship.py: 304 s.take_damage(p.damage) in _update_projectiles
             # The method wasn't in the snippet I read of ship.py?
             # Ah, ship.py imports ShipCombatMixin. take_damage likely there.
             # I should check if ShipCombatMixin has take_damage.
             # Assume yes. If not, this will crash. I'll mock take_damage to be safe and verify call.
             with patch.object(target, 'take_damage') as mock_take_damage:
                 self.engine._process_beam_attack(attack_hit)
                 mock_take_damage.assert_called_with(10)
        
        # Case 2: Near Miss (aiming slightly off)
        # Target at (200,0), radius 20. Edge is at y=20.
        # Aim at y=21 (Vector(200, 21).normalize())
        aim_vec = Vector2(200, 21).normalize()
        
        attack_miss = {
            'origin': source_pos,
            'direction': aim_vec,
            'range': 300,
            'target': target,
            'damage': 10,
            'component': mock_component
        }
        
        with patch('random.random', return_value=0.0):
             with patch.object(target, 'take_damage') as mock_take_damage:
                 self.engine._process_beam_attack(attack_miss)
                 mock_take_damage.assert_not_called()
        
        # Case 3: Range Limits
        attack_range = {
            'origin': source_pos,
            'direction': Vector2(1, 0),
            'range': 150, # Short of 180 (dist - radius)
            'target': target,
            'damage': 10,
            'component': mock_component
        }
        
        with patch('random.random', return_value=0.0):
             with patch.object(target, 'take_damage') as mock_take_damage:
                 self.engine._process_beam_attack(attack_range)
                 mock_take_damage.assert_not_called()

    def test_ramming_logic(self):
        """
        test _process_ramming by positioning two ships within collision radius.
        Verify the damage formulas.
        """
        # Setup
        rammer = self.ship1
        target = self.ship2
        
        rammer.ai_strategy = 'kamikaze'
        rammer.current_target = target
        rammer.radius = 10
        target.radius = 10
        
        # Use mocked take_damage to verify logic without relying on Ship mechanics
        # Because we can't easily set HP on Ship (it's a property), we mock the property or attributes
        # But take_damage is what we really want to verify is called with correct values.
        # Logic: 
        # if r.hp < t.hp: r takes hp_r+9999, t takes hp_r*0.5
        
        rammer.position = Vector2(0, 0)
        target.position = Vector2(15, 0) # dist 15 < 20
        
        # Mock HP property
        # Since 'hp' is a property, we can't patch it directly on the instance easily without class patch
        # or wrapping.
        # But we controlled layers. So we can control HP via components.
        
        # Case A: Rammer HP (50) < Target HP (100)
        rammer.layers['CORE']['components'][0].current_hp = 50
        rammer.layers['CORE']['components'][0].max_hp = 50
        target.layers['CORE']['components'][0].current_hp = 100
        target.layers['CORE']['components'][0].max_hp = 100
        
        # Also patch take_damage to avoid side effects and verify values
        with patch.object(rammer, 'take_damage') as mock_rammer_dmg, \
             patch.object(target, 'take_damage') as mock_target_dmg:
                 
            self.engine._process_ramming()
            
            # Rammer dies (hp + 9999) = 50 + 9999
            mock_rammer_dmg.assert_called_with(50 + 9999)
            # Target takes half rammer HP = 25
            mock_target_dmg.assert_called_with(25.0)

        # Case B: Rammer HP (100) > Target HP (50)
        rammer.layers['CORE']['components'][0].current_hp = 100
        target.layers['CORE']['components'][0].current_hp = 50
        
        with patch.object(rammer, 'take_damage') as mock_rammer_dmg, \
             patch.object(target, 'take_damage') as mock_target_dmg:
             
            self.engine._process_ramming()
            
            # Target dies (hp + 9999) = 50 + 9999
            mock_target_dmg.assert_called_with(50 + 9999)
            # Rammer takes half target hp = 25
            mock_rammer_dmg.assert_called_with(25.0)

        # Case C: Mutual destruction (Equal HP)
        rammer.layers['CORE']['components'][0].current_hp = 100
        target.layers['CORE']['components'][0].current_hp = 100
        
        with patch.object(rammer, 'take_damage') as mock_rammer_dmg, \
             patch.object(target, 'take_damage') as mock_target_dmg:
             
            self.engine._process_ramming()
            
            mock_rammer_dmg.assert_called_with(100 + 9999)
            mock_target_dmg.assert_called_with(100 + 9999)

    def test_projectile_interaction(self):
        """
        Test _update_projectiles for:
        Projectile movement.
        Collision with ships.
        Missile interception.
        """
        # 1. Projectile Movement
        p_vel = Vector2(10, 0)
        proj = Projectile(
            owner=self.ship1,
            position=Vector2(0, 0),
            velocity=p_vel,
            damage=10,
            range_val=1000,
            endurance=5,
            proj_type='projectile'
        )
        self.engine.projectiles.append(proj)
        
        self.engine._update_projectiles()
        
        expected_pos = Vector2(10, 0)
        self.assertEqual(proj.position, expected_pos, "Projectile should move by its velocity")
        
        # 2. Collision with Ships
        # Reset
        self.engine.projectiles = []
        target_ship = self.ship2 # Team 1
        target_ship.position = Vector2(100, 0)
        target_ship.velocity = Vector2(0, 0)
        target_ship.radius = 10
        # Set Component HP
        target_ship.layers['CORE']['components'][0].current_hp = 100
        
        proj_hit = Projectile(
            owner=self.ship1, # Team 0
            position=Vector2(95, 0),
            velocity=Vector2(10, 0),
            damage=20,
            range_val=1000,
            endurance=5,
            proj_type='projectile'
        )
        self.engine.projectiles.append(proj_hit)
        
        # Ensure grid is populated
        self.engine.grid.clear()
        self.engine.grid.insert(target_ship)
        
        with patch.object(target_ship, 'take_damage') as mock_take_damage:
            self.engine._update_projectiles()
            
            # Check if hit registered
            self.assertFalse(proj_hit.is_alive, "Projectile should be removed/dead after hit")
            mock_take_damage.assert_called_with(20)
        
        # 3. Missile Interception
        missile = Projectile(
            owner=self.ship1,
            position=Vector2(50, 50),
            velocity=Vector2(10, 0),
            damage=10,
            range_val=1000,
            endurance=5,
            proj_type='missile'
        )
        
        target_missile = Projectile(
            owner=self.ship2,
            position=Vector2(60, 50),
            velocity=Vector2(-10, 0),
            damage=10,
            range_val=1000,
            endurance=5,
            proj_type='missile'
        )
        
        missile.target = target_missile
        
        self.engine.projectiles = [missile, target_missile]
        
        self.engine._update_projectiles()
        
        self.assertFalse(target_missile.is_alive, "Target missile should be destroyed")
        self.assertFalse(missile.is_alive, "Interceptor missile should be destroyed")

if __name__ == '__main__':
    unittest.main()
