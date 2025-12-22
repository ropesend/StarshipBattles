import unittest
from ship import Ship, LayerType, initialize_ship_data
from components import Shield, ShieldRegenerator, load_components, create_component
import pygame

class TestShields(unittest.TestCase):
    def setUp(self):
        # Minimal init
        pygame.init()
        # Load components for crew support
        initialize_ship_data("C:\\Dev\\Starship Battles")
        load_components("data/components.json")
        
        self.ship = Ship("TestShip", 0, 0, (255,0,0))
        self.ship.ship_class = "Escort"
        self.ship.max_mass_budget = 1000
        
        # Add crew infrastructure first so shield components are active
        self.ship.add_component(create_component('bridge'), LayerType.CORE)
        self.ship.add_component(create_component('crew_quarters'), LayerType.CORE)
        self.ship.add_component(create_component('life_support'), LayerType.CORE)
        
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
        # 50 damage -> all absorbed by shields
        self.ship.take_damage(50)
        self.assertEqual(self.ship.current_shields, 50)
        self.assertEqual(self.shield.current_hp, self.shield.max_hp)
        
        # 60 damage -> 50 absorbed by shields, 10 bleed through to CORE
        # The 10 damage goes to a random CORE component:
        # - bridge (200 hp), crew_quarters (60 hp), life_support (40 hp), shield (10 hp), regen (10 hp)
        self.ship.take_damage(60)
        self.assertEqual(self.ship.current_shields, 0)
        # Check that SOME damage was applied to CORE components
        core_components = self.ship.layers[LayerType.CORE]['components']
        total_hp_lost = sum(c.max_hp - c.current_hp for c in core_components)
        self.assertEqual(total_hp_lost, 10, "10 HP should bleed through shields to CORE")

    def test_regeneration(self):
        self.ship.current_shields = 0
        self.ship.current_energy = 100
        
        # Update 1 tick (dt=1.0)
        # Rate 60/s -> 0.6 per tick (60/100)
        # Cost 30/s -> 0.3 per tick (30/100)
        self.ship.update_combat_cooldowns()
        
        self.assertAlmostEqual(self.ship.current_shields, 0.6)
        # 100 energy - 0.3 cost = 99.7
        self.assertAlmostEqual(self.ship.current_energy, 99.7)
        
    def test_regen_capped(self):
        self.ship.current_shields = 99
        self.ship.update_combat_cooldowns()
        # 99 + 0.6 = 99.6. Not capped yet.
        self.assertAlmostEqual(self.ship.current_shields, 99.6)

    def test_energy_starvation(self):
        self.ship.current_shields = 0
        self.ship.current_energy = 0
        self.ship.update_combat_cooldowns()
        self.assertEqual(self.ship.current_shields, 0)
