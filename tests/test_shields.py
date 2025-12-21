import unittest
from ship import Ship, LayerType
from components import Shield, ShieldRegenerator
import pygame

class TestShields(unittest.TestCase):
    def setUp(self):
        # Minimal init
        pygame.init()
        self.ship = Ship("TestShip", 0, 0, (255,0,0))
        self.ship.ship_class = "Escort"
        self.ship.max_mass_budget = 1000
        
        # Shield Proj: 100 Capacity
        self.shield_data = {
            'id': 's1', 'name': 'Shield', 'type': 'Shield', 
            'mass': 10, 'hp': 10, 'allowed_layers': ['CORE'], 'abilities': {'ShieldProjection': 100}
        }
        self.shield = Shield(self.shield_data)
        
        # Shield Regen: 60/sec (1/tick) for math simplicity, Cost 30/sec (0.5/tick)
        self.regen_data = {
            'id': 'r1', 'name': 'Regen', 'type': 'ShieldRegenerator', 
            'mass': 10, 'hp':10, 'allowed_layers': ['CORE'], 
            'abilities': {'ShieldRegeneration': 60.0, 'EnergyConsumption': 30.0}
        }
        self.regenerator = ShieldRegenerator(self.regen_data)
        
        self.ship.add_component(self.shield, LayerType.CORE)
        self.ship.add_component(self.regenerator, LayerType.CORE)
        
        self.ship.max_energy = 1000
        self.ship.current_energy = 1000
        self.ship.recalculate_stats() 

    def tearDown(self):
        pygame.quit()

    def test_stats_init(self):
        self.assertEqual(self.ship.max_shields, 100)
        self.assertEqual(self.ship.shield_regen_rate, 60.0)
        self.assertEqual(self.ship.shield_regen_cost, 30.0)
        self.assertEqual(self.ship.current_shields, 100)

    def test_damage_absorption(self):
        # 50 damage -> all absorbed
        self.ship.take_damage(50)
        self.assertEqual(self.ship.current_shields, 50)
        self.assertEqual(self.shield.current_hp, self.shield.max_hp)
        
        # 60 damage -> 50 absorbed, 10 bleed through
        self.ship.take_damage(60)
        self.assertEqual(self.ship.current_shields, 0)
        # Check component damage
        hp_loss = (self.shield.max_hp - self.shield.current_hp) + (self.regenerator.max_hp - self.regenerator.current_hp)
        self.assertEqual(hp_loss, 10)

    def test_regeneration(self):
        self.ship.current_shields = 0
        self.ship.current_energy = 100
        
        # Update 1 tick (dt=1.0)
        # Rate 60/s -> 1 per tick
        # Cost 30/s -> 0.5 per tick
        self.ship.update_combat_cooldowns(1.0)
        
        self.assertAlmostEqual(self.ship.current_shields, 1.0)
        # If bug exists (deducting full cost 30.0), energy will be 70
        # If fixed (deducting scaled cost 0.5), energy will be 99.5
        self.assertAlmostEqual(self.ship.current_energy, 99.5)
        
    def test_regen_capped(self):
        self.ship.current_shields = 99
        self.ship.update_combat_cooldowns(1.0)
        self.assertEqual(self.ship.current_shields, 100)

    def test_energy_starvation(self):
        self.ship.current_shields = 0
        self.ship.current_energy = 0
        self.ship.update_combat_cooldowns(1.0)
        self.assertEqual(self.ship.current_shields, 0)
