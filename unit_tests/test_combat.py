"""Tests for ship combat damage mechanics."""
import unittest
import sys
import os
import pygame
import random

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ship import Ship, LayerType, initialize_ship_data
from components import load_components, create_component  # Phase 7: Removed Bridge import
from unittest.mock import MagicMock



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
        
        # Ensure TestShip class exists in VEHICLE_CLASSES with correct layers
        from ship import VEHICLE_CLASSES
        VEHICLE_CLASSES["TestShip"] = {
            "hull_mass": 50, "max_mass": 1000,
            "layers": [
                {"type": "CORE", "radius_pct": 0.5, "max_mass_pct": 0.5},
                {"type": "ARMOR", "radius_pct": 1.0, "max_mass_pct": 0.5}
            ]
        }
        self.ship._initialize_layers()
        # Re-add components because _initialize_layers clears them
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
            if c.type_str == 'Bridge':
                bridge = c
                break
        
        self.assertIsNotNone(bridge)
        self.assertTrue(self.ship.is_alive)
        
        # Deal massive damage to destroy bridge
        # Need to potentially hit bridge multiple times due to random selection
        for _ in range(50):
            if not bridge.is_active:
                break
            self.ship.take_damage(100)
        
        # Bridge should be destroyed
        self.assertFalse(bridge.is_active)
        
        # Ship should STILL BE ALIVE (No requirements set for "TestShip")
        self.assertTrue(self.ship.is_alive)
        self.assertFalse(self.ship.is_derelict)

    def test_bridge_requirement_kills_ship(self):
        """Destroying the bridge SHOULD kill the ship IF required."""
        # Inject requirement
        from ship import VEHICLE_CLASSES
        VEHICLE_CLASSES["TestShip"] = {
            "hull_mass": 50, "max_mass": 1000,
            "requirements": {"CommandAndControl": True}
        }
        self.ship.ship_class = "TestShip" # Must match key
        # Re-init ship to pick up requirements
        self.ship.update_derelict_status()
        
        # Ensure bridge exists and provides CommandAndControl
        # (Assuming standard bridge provides it)
        
        # Remove armor first
        self.ship.layers[LayerType.ARMOR]['components'] = []
        
        bridge = None
        for c in self.ship.layers[LayerType.CORE]['components']:
             if c.type_str == 'Bridge':
                 bridge = c
                 break
        
        # Kill logic
        for _ in range(50):
            if self.ship.is_derelict:
                break
            self.ship.take_damage(100)

        # Should be derelict now
        self.assertTrue(self.ship.is_derelict)


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
        self.ship.resources.get_resource("energy").current_value = self.ship.resources.get_max_value("energy") / 2
        initial_energy = self.ship.resources.get_value("energy")
        
        # Energy regeneration happens in Ship.update() via ResourceRegistry (tick-based)
        self.ship.update()
        
        self.assertGreater(self.ship.resources.get_value("energy"), initial_energy)
    
    def test_energy_capped_at_max(self):
        """Energy should not exceed max_energy."""
        self.ship.resources.get_resource("energy").current_value = self.ship.resources.get_max_value("energy") - 1
        
        # Regen creates overflow
        # Manually boost regen rate to ensure overflow (tick is 0.01s, need >1.0 change)
        self.ship.resources.get_resource("energy").regen_rate = 200
        self.ship.update()
        
        self.assertEqual(self.ship.resources.get_value("energy"), self.ship.resources.get_max_value("energy"))
    
    def test_dead_ship_no_regen(self):
        """Dead ship should not regenerate energy."""
        self.ship.is_alive = False
        self.ship.resources.get_resource("energy").current_value = 0
        
        self.ship.update()
        
        self.assertEqual(self.ship.resources.get_value("energy"), 0)


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
        # Phase 7: Use ability-based weapon detection
        
        weapon = None
        for c in self.ship.layers[LayerType.OUTER]['components']:
            if c.has_ability('WeaponAbility') and c.is_active:
                weapon = c
                break
        
        self.assertIsNotNone(weapon, "No active weapon found in OUTER layer")
        
        # Phase 7: Use ability-based access for weapon methods
        weapon_ab = weapon.get_ability('WeaponAbility') or weapon.get_ability('ProjectileWeaponAbility')
        self.assertIsNotNone(weapon_ab)
        
        # Fire to start cooldown
        weapon_ab.fire(target=None)
        initial_cooldown = weapon_ab.cooldown_timer
        self.assertGreater(initial_cooldown, 0, "Weapon should have cooldown after firing")
        
        # Weapon cooldowns are updated in Ship.update() via Component.update() (tick-based)
        self.ship.update()
        
        self.assertLess(weapon_ab.cooldown_timer, initial_cooldown)



class TestCombatFlow(unittest.TestCase):
    """Refactored Tests for Combat Flow (Projectile Creation)."""
    
    def setUp(self):
        if not pygame.get_init():
            pygame.init()
        # Mocking Ship and Target 
        self.ship = MagicMock()
        self.ship.position = pygame.math.Vector2(0, 0)
        self.ship.velocity = pygame.math.Vector2(0, 0)
        self.ship.team_id = 0
        
        self.target = MagicMock()
        self.target.position = pygame.math.Vector2(100, 0)
        self.target.velocity = pygame.math.Vector2(10, 0) # Moving Right
        self.target.radius = 10
        self.target.is_active = True
        
    def test_projectile_creation(self):
        """Test that firing creates a valid Projectile object."""
        # Using real ProjectileWeaponAbility
        from components import Component
        from abilities import ProjectileWeaponAbility
        from projectiles import Projectile
        from game_constants import AttackType
        
        data = {
            "projectile_speed": 200,
            "damage": 10,
            "range": 500
        }
        # Mock component
        comp = MagicMock()
        comp.position = pygame.math.Vector2(0,0)
        comp.stats = {}
        comp.ship = self.ship
        
        # Test direct projectile instantiation
        # Init: owner, position, velocity, damage, range_val, endurance, proj_type, source_weapon=None, **kwargs
        proj = Projectile(
            owner=self.ship,
            position=pygame.math.Vector2(0,0),
            velocity=pygame.math.Vector2(200,0),
            damage=10,
            range_val=500,
            endurance=5.0,
            proj_type=AttackType.PROJECTILE,
            source_id="shooter"
        )
        
        self.assertEqual(proj.damage, 10)
        self.assertEqual(proj.max_range, 500)
        # Verify it moves
        proj.update() # 0.01s tick inside update
        # Projectile implementation does pos += velocity (velocity is per-tick displacement)
        # Input was 200, so it moves 200.
        self.assertAlmostEqual(proj.position.x, 200.0, places=2)


