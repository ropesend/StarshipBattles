import unittest
import unittest.mock
import pygame
import sys
import os
import math

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ship import Ship, initialize_ship_data
from components import Component, LayerType, COMPONENT_REGISTRY, Weapon, load_components
from ai import AIController, COMBAT_STRATEGIES
from spatial import SpatialGrid
from projectiles import Projectile
from game_constants import AttackType

class TestMultitarget(unittest.TestCase):
    def setUp(self):
        # Initialize pygame for vectors
        pygame.init()
        initialize_ship_data()
        load_components()
        self.grid = SpatialGrid(2000)
        self.ship = Ship("TestShip", 1000, 1000, (255, 0, 0), team_id=0, ship_class="Cruiser")
        self.ai = AIController(self.ship, self.grid, enemy_team_id=1)
        self.ship.ai_controller = self.ai
        
        # Add Infrastructure to avoid derelict status and allow components to work
        # 1. Bridge (required for non-derelict)
        if 'bridge' in COMPONENT_REGISTRY:
            bridge = COMPONENT_REGISTRY['bridge'].clone()
            self.ship.add_component(bridge, LayerType.CORE)
        
        # 2. Engine (required for non-derelict on Ships)
        if 'standard_engine' in COMPONENT_REGISTRY:
            engine = COMPONENT_REGISTRY['standard_engine'].clone()
            self.ship.add_component(engine, LayerType.INNER)
            
        # 3. Generator
        if 'generator' in COMPONENT_REGISTRY:
            gen = COMPONENT_REGISTRY['generator'].clone()
            self.ship.add_component(gen, LayerType.CORE)
        
        # 4. Battery (for energy storage - required for beam weapons)
        if 'battery' in COMPONENT_REGISTRY:
            bat = COMPONENT_REGISTRY['battery'].clone()
            self.ship.add_component(bat, LayerType.INNER)
            
        # 4. Crew Quarters (Need enough for Multi-tracker + weapons + bridge)
        if 'crew_quarters' in COMPONENT_REGISTRY:
            cq1 = COMPONENT_REGISTRY['crew_quarters'].clone()
            self.ship.add_component(cq1, LayerType.INNER)
            cq2 = COMPONENT_REGISTRY['crew_quarters'].clone()
            self.ship.add_component(cq2, LayerType.INNER)
            cq3 = COMPONENT_REGISTRY['crew_quarters'].clone()
            self.ship.add_component(cq3, LayerType.INNER)
        
        # 5. Life Support
        if 'life_support' in COMPONENT_REGISTRY:
            ls = COMPONENT_REGISTRY['life_support'].clone()
            self.ship.add_component(ls, LayerType.INNER)
            ls2 = COMPONENT_REGISTRY['life_support'].clone()
            self.ship.add_component(ls2, LayerType.INNER)
        
        self.ship.recalculate_stats()
        
    def test_multiplex_tracking_stats(self):
        # Add Multiplex Tracking
        if 'multiplex_tracking' not in COMPONENT_REGISTRY:
            return # Skip if not defined
            
        comp = COMPONENT_REGISTRY['multiplex_tracking'].clone()
        self.ship.add_component(comp, LayerType.OUTER)
        self.ship.recalculate_stats()
        
        self.assertEqual(self.ship.max_targets, 10)
        
    def test_secondary_target_acquisition(self):
        if 'multiplex_tracking' not in COMPONENT_REGISTRY:
            return

        # Add Multiplex
        comp = COMPONENT_REGISTRY['multiplex_tracking'].clone()
        self.ship.add_component(comp, LayerType.OUTER)
        self.ship.recalculate_stats()
        
        # Create Enemies
        e1 = Ship("Enemy1", 1100, 1000, (255, 0, 0), team_id=1) # Dist 100
        e2 = Ship("Enemy2", 1200, 1000, (255, 0, 0), team_id=1) # Dist 200
        e3 = Ship("Enemy3", 1300, 1000, (255, 0, 0), team_id=1) # Dist 300
        
        self.grid.insert(e1)
        self.grid.insert(e2)
        self.grid.insert(e3)
        
        # Update AI
        self.ai.update()
        
        # Depending on strategy (default 'nearest'), closest should be primary
        self.assertEqual(self.ship.current_target, e1)
        self.assertIn(e2, self.ship.secondary_targets)
        self.assertIn(e3, self.ship.secondary_targets)
        
    def test_pdc_missile_logic(self):
        if 'multiplex_tracking' not in COMPONENT_REGISTRY:
            return
            
        # Add Multiplex
        comp = COMPONENT_REGISTRY['multiplex_tracking'].clone()
        res = self.ship.add_component(comp, LayerType.OUTER)
        # self.assertTrue(res.is_valid if hasattr(res, 'is_valid') else res) # Handle boolean return
        if not res:
            self.fail("Multiplex add failed")
        
        # Add PDC: Facing 0 (Right), Arc 45
        pdc = COMPONENT_REGISTRY['point_defence_cannon'].clone()
        pdc.facing_angle = 0
        pdc.firing_arc = 45
        pdc.range = 800
        res = self.ship.add_component(pdc, LayerType.OUTER)
        if not res:
            self.fail("PDC add failed")
        
        self.ship.recalculate_stats()
        
        # Scenario 1: Missile in Front (In Arc)
        # 1200, 1000 is 200 units to RIGHT of 1000,1000. Angle 0.
        m1 = Projectile(None, pygame.math.Vector2(1200, 1000), pygame.math.Vector2(0,0), 10, 1000, 5, AttackType.MISSILE)
        m1.team_id = 1
        
        # Scenario 2: Missile Behind (Out of Arc)
        # 800, 1000 is 200 units to LEFT of 1000,1000. Angle 180.
        m2 = Projectile(None, pygame.math.Vector2(800, 1000), pygame.math.Vector2(0,0), 10, 1000, 5, AttackType.MISSILE)
        m2.team_id = 1
        
        # Add to grid so AI can find them
        self.grid.insert(m1)
        self.grid.insert(m2)
        
        # Inject Strategy
        with unittest.mock.patch.dict(COMBAT_STRATEGIES, {
            'test_strat': {'targeting_priority': ['missiles_in_pdc_arc', 'nearest']}
        }):
            self.ship.ai_strategy = 'test_strat'
            
            # Force AI update to use this strategy
            # AIController.find_secondary_targets uses self.ship.ai_strategy to lookup
            sec = self.ai.find_secondary_targets()
        
        # Diagnostic print
        # print([t for t in sec])
        
        # M1 should be prioritized because it is in PDC arc
        self.assertIn(m1, sec)
        # M2 should NOT be in list (hard filter)
        self.assertNotIn(m2, sec)
        
        # Verify Firing
        # Manually set secondary targets as AI update would
        self.ship.secondary_targets = sec
        context = {'projectiles': [m1, m2]}
        
        # Ensure ship has resources to fire
        self.ship.current_energy = self.ship.max_energy
        
        # Ensure PDC is not on cooldown
        pdc.cooldown_timer = 0
        
        fired = self.ship.fire_weapons(context)
        
        # Should fire 1 shot
        self.assertTrue(len(fired) > 0, "PDC should have fired at missile")
        
        # Check target of first shot
        shot = fired[0]
        # Handle dict or object return
        target = shot.target if hasattr(shot, 'target') else shot.get('target')
        self.assertEqual(target, m1)

if __name__ == '__main__':
    unittest.main()
