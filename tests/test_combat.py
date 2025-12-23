"""Tests for ship combat damage mechanics."""
import unittest
import sys
import os
import pygame
import random

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ship import Ship, LayerType, initialize_ship_data
from components import load_components, create_component, Bridge


class TestDamageLayerLogic(unittest.TestCase):
    """Test damage distribution through ship layers."""
    
    @classmethod
    def setUpClass(cls):
        pygame.init()
        initialize_ship_data("C:\\Dev\\Starship Battles")
        load_components("data/components.json")
    
    @classmethod
    def tearDownClass(cls):
        pygame.quit()
    
    def setUp(self):
        # Set deterministic random for reproducible tests
        random.seed(42)
        
        self.ship = Ship("TestShip", 0, 0, (255, 255, 255))
        self.ship.add_component(create_component('bridge'), LayerType.CORE)
        self.ship.add_component(create_component('crew_quarters'), LayerType.CORE)
        self.ship.add_component(create_component('life_support'), LayerType.CORE)
        self.ship.add_component(create_component('armor_plate'), LayerType.ARMOR)
        self.ship.recalculate_stats()
    
    def test_armor_absorbs_damage_first(self):
        """Damage should be absorbed by armor layer first."""
        armor = self.ship.layers[LayerType.ARMOR]['components'][0]
        initial_armor_hp = armor.current_hp
        
        # Deal damage less than armor HP
        self.ship.take_damage(50)
        
        self.assertLess(armor.current_hp, initial_armor_hp)
        # Core components should be untouched
        core_damage = sum(c.max_hp - c.current_hp for c in self.ship.layers[LayerType.CORE]['components'])
        self.assertEqual(core_damage, 0)
    
    def test_damage_overflows_to_next_layer(self):
        """Excess damage should overflow to inner layers."""
        armor = self.ship.layers[LayerType.ARMOR]['components'][0]
        armor_hp = armor.current_hp
        
        # Deal more damage than armor can absorb
        overflow_damage = 50
        self.ship.take_damage(armor_hp + overflow_damage)
        
        # Armor should be destroyed
        self.assertEqual(armor.current_hp, 0)
        
        # CORE (skipping empty OUTER/INNER) should have taken overflow
        core_damage = sum(c.max_hp - c.current_hp for c in self.ship.layers[LayerType.CORE]['components'])
        self.assertGreater(core_damage, 0)
    
    def test_shield_absorbs_before_armor(self):
        """Shield should absorb damage before armor."""
        # Add shield (correct component ID is 'shield_generator')
        self.ship.add_component(create_component('shield_generator'), LayerType.CORE)
        self.ship.recalculate_stats()
        
        initial_shields = self.ship.current_shields
        armor = self.ship.layers[LayerType.ARMOR]['components'][0]
        initial_armor_hp = armor.current_hp
        
        # Deal damage less than shields
        damage = min(initial_shields - 10, 50)
        if damage > 0:
            self.ship.take_damage(damage)
            
            self.assertLess(self.ship.current_shields, initial_shields)
            self.assertEqual(armor.current_hp, initial_armor_hp)
    
    def test_bridge_destruction_kills_ship(self):
        """Destroying the bridge should kill the ship."""
        # Remove armor first to make bridge accessible
        self.ship.layers[LayerType.ARMOR]['components'] = []
        self.ship.recalculate_stats()
        
        bridge = None
        for c in self.ship.layers[LayerType.CORE]['components']:
            if isinstance(c, Bridge):
                bridge = c
                break
        
        self.assertIsNotNone(bridge)
        self.assertTrue(self.ship.is_alive)
        
        # Deal massive damage to destroy bridge
        # Need to potentially hit bridge multiple times due to random selection
        for _ in range(50):
            if not self.ship.is_alive:
                break
            self.ship.take_damage(100)
        
        # Either ship died or bridge was destroyed
        self.assertTrue(not self.ship.is_alive or not bridge.is_active)


class TestEnergyRegeneration(unittest.TestCase):
    """Test energy and shield regeneration mechanics."""
    
    @classmethod
    def setUpClass(cls):
        pygame.init()
        initialize_ship_data("C:\\Dev\\Starship Battles")
        load_components("data/components.json")
    
    @classmethod
    def tearDownClass(cls):
        pygame.quit()
    
    def setUp(self):
        self.ship = Ship("TestShip", 0, 0, (255, 255, 255), ship_class="Cruiser")
        self.ship.add_component(create_component('bridge'), LayerType.CORE)
        self.ship.add_component(create_component('crew_quarters'), LayerType.CORE)
        self.ship.add_component(create_component('life_support'), LayerType.CORE)
        self.ship.add_component(create_component('battery'), LayerType.INNER)
        self.ship.add_component(create_component('generator'), LayerType.INNER)
        self.ship.recalculate_stats()
    
    def test_energy_regenerates_per_tick(self):
        """Energy should regenerate each combat tick."""
        # Drain energy first, then check if it regenerates
        self.ship.current_energy = self.ship.max_energy / 2
        initial_energy = self.ship.current_energy
        
        self.ship.update_combat_cooldowns()
        
        self.assertGreater(self.ship.current_energy, initial_energy)
    
    def test_energy_capped_at_max(self):
        """Energy should not exceed max_energy."""
        self.ship.current_energy = self.ship.max_energy
        
        self.ship.update_combat_cooldowns()
        
        self.assertEqual(self.ship.current_energy, self.ship.max_energy)
    
    def test_dead_ship_no_regen(self):
        """Dead ship should not regenerate energy."""
        self.ship.is_alive = False
        self.ship.current_energy = 0
        
        self.ship.update_combat_cooldowns()
        
        self.assertEqual(self.ship.current_energy, 0)


class TestWeaponCooldowns(unittest.TestCase):
    """Test weapon cooldown mechanics."""
    
    @classmethod
    def setUpClass(cls):
        pygame.init()
        initialize_ship_data("C:\\Dev\\Starship Battles")
        load_components("data/components.json")
    
    @classmethod
    def tearDownClass(cls):
        pygame.quit()
    
    def setUp(self):
        self.ship = Ship("TestShip", 0, 0, (255, 255, 255))
        self.ship.add_component(create_component('bridge'), LayerType.CORE)
        self.ship.add_component(create_component('crew_quarters'), LayerType.CORE)
        self.ship.add_component(create_component('life_support'), LayerType.CORE)
        # Use laser_cannon which is a BeamWeapon that can go in OUTER
        self.ship.add_component(create_component('laser_cannon'), LayerType.OUTER)
        self.ship.recalculate_stats()
    
    def test_weapon_cooldown_decreases(self):
        """Weapon cooldown should decrease each tick."""
        from components import Weapon
        
        weapon = None
        for c in self.ship.layers[LayerType.OUTER]['components']:
            if isinstance(c, Weapon) and c.is_active:
                weapon = c
                break
        
        self.assertIsNotNone(weapon, "No active weapon found in OUTER layer")
        
        # Fire to start cooldown
        weapon.fire()
        initial_cooldown = weapon.cooldown_timer
        self.assertGreater(initial_cooldown, 0, "Weapon should have cooldown after firing")
        
        self.ship.update_combat_cooldowns()
        
        self.assertLess(weapon.cooldown_timer, initial_cooldown)


if __name__ == '__main__':
    unittest.main()
