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
        self.reload = 0.1
        self.reload_current = 0
        self.base_accuracy = 1.0
        self.accuracy_falloff = 0
        self.allowed_layers = [LayerType.OUTER]
        self.mass = 10
        self.modifiers = []

    def can_fire(self):
        return True
        
    def fire(self):
        return True
        
    def calculate_hit_chance(self, dist):
        return 1.0

class TestPDC(unittest.TestCase):
    def setUp(self):
        pygame.init()
        self.scene = BattleScene(100, 100)
        
        # Ship with PDC
        self.ship = Ship("Defender", 0, 0, (255,255,255), team_id=0)
        self.ship.current_energy = 1000
        self.ship.max_energy = 1000
        pdc = MockPDC()
        self.ship.layers[LayerType.OUTER]['components'] = [pdc]
        
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
        
        self.scene.ships = [self.ship]
        self.scene.projectiles = [self.missile]
        self.scene.grid.insert(self.ship) # Needed for queries if any
        
    def test_pdc_targets_missile(self):
        # Context must be passed
        context = {'projectiles': self.scene.projectiles, 'grid': self.scene.grid}
        
        # Manual fire check
        # We expect fire_weapons to return a beam attack targeting the missile
        
        # We need to simulate the ship logic calling fire_weapons via update or directly
        # Let's call directly to verify logic
        
        # ship.update() calls fire_weapons() if trigger pulled
        self.ship.comp_trigger_pulled = True
        
        attacks = self.ship.fire_weapons(context)
        
        self.assertTrue(len(attacks) > 0, "PDC should have fired")
        attack = attacks[0]
        self.assertEqual(attack['type'], 'beam')
        self.assertEqual(attack['target'], self.missile)
        
    def test_pdc_ignores_friendly_missile(self):
        self.missile.team_id = 0 # Friendly
        context = {'projectiles': self.scene.projectiles, 'grid': self.scene.grid}
        
        attacks = self.ship.fire_weapons(context)
        self.assertEqual(len(attacks), 0, "PDC should not fire at friendly missile")

if __name__ == '__main__':
    unittest.main()
