import unittest
import pygame
import math
from ship import Ship, LayerType
from components import Component, Weapon, SeekerWeapon, BeamWeapon
from battle import BattleScene
from projectiles import Projectile

# Mock definitions to avoid loading full game data if possible, 
# or we just rely on class structure.

class MockPDC(BeamWeapon):
    def __init__(self):
        # Mimic Point Defence Cannon
        self.name = "PDC"
        self.range = 1000
        self.damage = 10
        self.energy_cost = 0
        self.current_hp = 10
        self.max_hp = 10
        self.is_active = True
        self.abilities = {'PointDefense': True}
        self.firing_arc = 360 # Omni
        self.facing_angle = 0
        self.reload_time = 0.1
        self.cooldown_timer = 0
        self.base_accuracy = 1.0
        self.accuracy_falloff = 0
        self.allowed_layers = [LayerType.OUTER]
        self.type_str = "BeamWeapon"
        self.major_classification = "Weapons"
        self.mass = 10
        self.base_mass = 10
        self.max_hp = 10
        self.base_max_hp = 10
        self.abilities = {'PointDefense': True}
        self.base_abilities = {'PointDefense': True}
        self.modifiers = []
        self.shots_fired = 0
        self.shots_hit = 0
        self.data = {
            'damage': 10,
            'range': 1000,
            'cost': 0,
            'thrust_force': 0,
            'turn_speed': 0,
            'energy_generation': 0,
            'capacity': 0,
            'firing_arc': 360,
            'reload': 0.1
        }

    def update(self):
        dt = 0.01
        if self.cooldown_timer > 0:
            self.cooldown_timer -= dt

    def can_fire(self):
        return self.is_active and self.cooldown_timer <= 0
        
    def fire(self):
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
        from ship import initialize_ship_data
        initialize_ship_data()
        from components import load_components
        load_components()
        
        self.scene = BattleScene(100, 100)
        
        # Ship with PDC - Use Satellite to avoid engine/crew requirements
        self.ship = Ship("Defender", 0, 0, (255,255,255), team_id=0, ship_class="Satellite (Small)")
        
        # ADD A BRIDGE so it's not derelict
        from components import create_component, Bridge
        bridge = create_component('satellite_core') # Specific for satellites
        if not bridge:
             bridge = create_component('bridge')
             
        if bridge:
            self.ship.add_component(bridge, LayerType.CORE)
        else:
            # Fallback mock bridge if registry fails
            mock_bridge = Bridge({
                'id':'bridge', 'name':'Bridge', 'type':'Bridge', 'mass':10, 'hp':10, 
                'allowed_layers':['CORE'], 
                'abilities':{'CommandAndControl':True, 'CrewRequired':0}
            })
            mock_bridge.type_str = "Bridge"
            self.ship.add_component(mock_bridge, LayerType.CORE)

        self.ship.current_energy = 1000
        self.ship.max_energy = 1000
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
        self.scene.engine.projectiles = [self.missile]
        self.scene.engine.grid.insert(self.ship) # Needed for queries if any
        
    def test_pdc_targets_missile(self):
        # Context must be passed
        context = {'projectiles': self.scene.projectiles, 'grid': self.scene.engine.grid}
        
        # Ensure it is type 'missile' for ship_combat.py check
        self.missile.type = 'missile'
        self.missile.is_alive = True
        
        self.ship.recalculate_stats()
        self.ship.current_energy = 1000
        self.ship.max_energy = 1000
        # fire_weapons prioritized current_target first, and only looks at secondary if max_targets > 1
        self.ship.current_target = self.missile 
        self.ship.secondary_targets = [self.missile] 
        
        # Diagnostic: Why is it not firing?
        # print(f"DEBUG: Alive={self.ship.is_alive}, Derelict={self.ship.is_derelict}, Energy={self.ship.current_energy}/{self.ship.max_energy}, Targets={self.ship.current_target}")
        # print(f"DEBUG: PDC Active={self.pdc.is_active}, CD={self.pdc.cooldown_timer}, Range={self.pdc.range}")

        attacks = self.ship.fire_weapons(context)
        
        self.assertTrue(len(attacks) > 0, f"PDC should have fired. Ship Derelict: {self.ship.is_derelict}")
        attack = attacks[0]
        self.assertEqual(attack['type'], 'beam')
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
