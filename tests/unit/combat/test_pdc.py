import unittest
import pygame
import math
from game.simulation.entities.ship import Ship, LayerType
from game.simulation.components.component import Component
from game.ui.screens.battle_scene import BattleScene
from game.simulation.entities.projectile import Projectile
from game.core.constants import AttackType

# Mock definitions to avoid loading full game data if possible, 
# or we just rely on class structure.

class MockPDC(Component):
    def __init__(self):
        # Use proper Component initialization with abilities dict
        # This ensures abilities survive recalculate_stats()
        data = {
            'id': 'mock_pdc',
            'name': 'PDC',
            'type': 'BeamWeapon',
            'mass': 10,
            'hp': 10,
            'abilities': {
                'BeamWeaponAbility': {
                    'damage': 10,
                    'range': 1000,
                    'reload': 0.1,
                    'firing_arc': 360,
                    'base_accuracy': 1.0,
                    'accuracy_falloff': 0,
                    'tags': ['pdc']  # Tag-based PDC detection
                }
            }
        }
        super().__init__(data)
        self.cooldown_timer = 0  # Start ready to fire

    def update(self):
        dt = 0.01
        if self.cooldown_timer > 0:
            self.cooldown_timer -= dt

    def can_fire(self):
        return self.is_active and self.cooldown_timer <= 0
        
    def fire(self, target=None):
        if self.can_fire():
            self.cooldown_timer = self.reload_time
            return True
        return False
        
    def calculate_hit_chance(self, dist):
        return 1.0

class TestPDC(unittest.TestCase):
    def setUp(self):
        pygame.init()
        # Initialize vehicle classes and components so registry works
        from game.simulation.entities.ship import initialize_ship_data
        initialize_ship_data()
        from game.simulation.components.component import load_components
        load_components()
        
        self.scene = BattleScene(100, 100)
        
        # Ship with PDC - Use Satellite to avoid engine/crew requirements
        self.ship = Ship("Defender", 0, 0, (255,255,255), team_id=0, ship_class="Satellite (Small)")
        
        # ADD A BRIDGE so it's not derelict
        from game.simulation.components.component import create_component, Component  # Phase 7: Removed Bridge import
        bridge = create_component('satellite_core') # Specific for satellites
        if not bridge:
             bridge = create_component('bridge')
             
        if bridge:
            self.ship.add_component(bridge, LayerType.CORE)
        else:
            # Fallback mock bridge if registry fails - use Component directly
            mock_bridge = Component({
                'id':'bridge', 'name':'Bridge', 'type':'Bridge', 'mass':10, 'hp':10, 
                'allowed_layers':['CORE'], 
                'abilities':{'CommandAndControl':True, 'CrewRequired':0}
            })
            mock_bridge.type_str = "Bridge"
            self.ship.add_component(mock_bridge, LayerType.CORE)

        self.ship.resources.set_max_value('energy', 1000); self.ship.resources.set_value('energy', 1000)
        self.ship.resources.set_max_value('energy', 1000)
        self.pdc = MockPDC()
        self.ship.layers[LayerType.OUTER]['components'] = [self.pdc]
        
        # Enemy Missile
        self.missile = Projectile(
            owner=Ship("Attacker", 1000, 0, (255,0,0), team_id=1), # Enemy team
            position=pygame.math.Vector2(500, 0), # Within 1000 range
            velocity=pygame.math.Vector2(-10, 0), # Incoming
            damage=100,
            range_val=5000,
            endurance=10,
            proj_type='missile',
            hp=5
        )
        self.missile.team_id = 1
        
        self.scene.engine.ships = [self.ship]
        self.scene.engine.projectile_manager.projectiles = [self.missile]
        self.scene.engine.grid.insert(self.ship) # Needed for queries if any
        
    def test_pdc_targets_missile(self):
        # Context must be passed
        context = {'projectiles': self.scene.projectiles, 'grid': self.scene.engine.grid}
        
        # Ensure it is type 'missile' for ship_combat.py check
        self.missile.type = AttackType.MISSILE
        self.missile.is_alive = True
        
        self.ship.recalculate_stats()
        self.ship.resources.set_max_value('energy', 1000); self.ship.resources.set_value('energy', 1000)
        self.ship.resources.set_max_value('energy', 1000)
        # fire_weapons prioritized current_target first, and only looks at secondary if max_targets > 1
        self.ship.current_target = self.missile 
        self.ship.secondary_targets = [self.missile] 
        
        # Diagnostic: Why is it not firing?
        # print(f"DEBUG: Alive={self.ship.is_alive}, Derelict={self.ship.is_derelict}, Energy={self.ship.resources.get_value('energy')}/{self.ship.resources.get_max_value('energy')}, Targets={self.ship.current_target}")
        # print(f"DEBUG: PDC Active={self.pdc.is_active}, CD={self.pdc.cooldown_timer}, Range={self.pdc.range}")

        attacks = self.ship.fire_weapons(context)
        
        self.assertTrue(len(attacks) > 0, "PDC should have fired.")
        attack = attacks[0]
        self.assertEqual(attack['type'], AttackType.BEAM)
        self.assertEqual(attack['target'], self.missile)
        
    def test_pdc_ignores_friendly_missile(self):
        self.missile.team_id = 0 # Friendly
        context = {'projectiles': self.scene.projectiles, 'grid': self.scene.engine.grid}
        self.ship.recalculate_stats()
        self.ship.current_target = self.missile
        self.ship.secondary_targets = [self.missile]
        
        attacks = self.ship.fire_weapons(context)
        self.assertEqual(len(attacks), 0, "PDC should not fire at friendly missile")

if __name__ == '__main__':
    unittest.main()
