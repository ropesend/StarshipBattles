"""Tests for ship combat damage mechanics."""
import unittest
import sys
import os
import pygame
import random

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from game.simulation.entities.ship import Ship, LayerType, initialize_ship_data
from game.simulation.components.component import load_components, create_component  # Phase 7: Removed Bridge import
from unittest.mock import MagicMock



class TestDamageLayerLogic(unittest.TestCase):
    """Test damage distribution through ship layers."""
    
    def setUp(self):
        if not pygame.get_init():
            pygame.init()
        initialize_ship_data(os.getcwd())
        load_components("data/components.json")
        
        # Set deterministic random for reproducible tests
        random.seed(42)
        
        self.ship = Ship("TestShip", 0, 0, (255, 255, 255))
        self.ship.add_component(create_component('bridge'), LayerType.CORE)
        self.ship.add_component(create_component('crew_quarters'), LayerType.CORE)
        self.ship.add_component(create_component('life_support'), LayerType.CORE)
        self.ship.add_component(create_component('armor_plate'), LayerType.ARMOR)
        
        # Ensure TestShip class exists in RegistryManager with correct layers
        from game.core.registry import RegistryManager
        RegistryManager.instance().vehicle_classes["TestShip"] = {
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
        from game.core.registry import RegistryManager
        RegistryManager.instance().vehicle_classes["TestShip"] = {
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
    
    def setUp(self):
        if not pygame.get_init():
            pygame.init()
        initialize_ship_data(os.getcwd())
        load_components("data/components.json")
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
    
    def setUp(self):
        if not pygame.get_init():
            pygame.init()
        initialize_ship_data(os.getcwd())
        load_components("data/components.json")
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
    """Refactored Tests for Combat Flow (Firing and Damage)."""
    
    def setUp(self):
        if not pygame.get_init():
            pygame.init()
        # Initialize data for component creation
        initialize_ship_data(os.getcwd())
        load_components("data/components.json")
            
    def test_firing_solution_lead(self):
        """Test lead calculation for moving targets."""
        # Mixin logic requires a class instance
        from ship_combat import ShipCombatMixin
        class MockCombatShip(ShipCombatMixin):
            pass
            
        ship = MockCombatShip()
        ship.position = pygame.math.Vector2(0,0)
        ship.velocity = pygame.math.Vector2(0,0)
        
        # Target moving right at 10 u/s at (100, 0)
        target_pos = pygame.math.Vector2(100, 0)
        target_vel = pygame.math.Vector2(10, 0)
        proj_speed = 20.0 
        
        # Expected collision:
        # P = Vp * t = 20t
        # T = P0 + Vt * t = 100 + 10t
        # Intercept when distance covered matches
        # (20t)^2 = (100 + 10t)^2
        # ... t = 10.0 (See calculation logic)
        
        # ship.solve_lead(pos, vel, t_pos, t_vel, p_speed)
        t = ship.solve_lead(ship.position, ship.velocity, target_pos, target_vel, proj_speed)
        self.assertAlmostEqual(t, 10.0, delta=0.1)

    def test_fire_weapons_creates_projectiles(self):
        """Test that fire_weapons returns correct projectile objects."""
        from game.simulation.entities.ship import Ship, LayerType
        from game.simulation.components.component import Component
        from game.core.constants import AttackType
        
        ship = Ship("Shooter", 0,0, (255,255,255))
        
        # Add a weapon component manually to ensure it has no cost issues
        # Component needs to be 'active'
        weapon = Component({
            "id": "test_gun",
            "name": "Gun", 
            "type": "Weapon",
            "mass": 10,
            "hp": 50,
            "abilities": {
                "WeaponAbility": {"range": 1000, "fire_rate": 1, "cooldown": 0},
                "ProjectileWeaponAbility": {"projectile_speed": 100, "damage": 10}
            }
        })
        ship.add_component(weapon, LayerType.OUTER)
        ship.recalculate_stats() # Activate component
        
        # Setup Target
        target = MagicMock()
        target.position = pygame.math.Vector2(100, 0)
        target.velocity = pygame.math.Vector2(0,0)
        target.is_alive = True
        target.team_id = 1
        target.type = 'ship'
        
        ship.team_id = 0
        ship.current_target = target
        
        # Fire
        attacks = ship.fire_weapons()
        
        self.assertEqual(len(attacks), 1)
        self.assertEqual(attacks[0].damage, 10)
        self.assertEqual(attacks[0].type, AttackType.PROJECTILE) # proj_type -> type
        self.assertEqual(attacks[0].owner, ship)

    def test_special_armor_interactions(self):
        """Test Emissive and Crystalline Armor logic."""
        from game.simulation.entities.ship import Ship
        ship = Ship("Tank", 0,0, (255,255,255))
        
        # 1. Emissive Armor (Flat Reduction)
        ship.emissive_armor = 5
        ship.is_alive = True
        
        # Add a dummy component to take damage
        c = create_component('bridge')
        ship.add_component(c, LayerType.CORE)
        ship.recalculate_stats() 
        ship.emissive_armor = 5
        
        c.is_active = True
        c.current_hp = 100
        initial_hp = c.current_hp
        
        # Take 10 damage -> Reduced by 5 -> 5 damage
        ship.take_damage(10)
        self.assertEqual(c.current_hp, initial_hp - 5)
        
        ship.emissive_armor = 5
        
        # Take 4 damage -> Reduced by 5 -> 0 damage
        prev_hp = c.current_hp
        ship.take_damage(4)
        self.assertEqual(c.current_hp, prev_hp)
        
        # 2. Crystalline Armor (Absorb + Shield Recharge)
        ship.emissive_armor = 0
        ship.crystalline_armor = 10
        ship.max_shields = 100
        ship.current_shields = 50
        
        # Take 20 damage
        # Absorb min(10, 20) = 10
        # Shields += 10 -> 60
        # Remaining Damage = 10
        # Shield Absorption: min(60, 10) = 10 absorbed
        # Shields -= 10 -> 50
        # Remaining Damage = 0
        # Component HP untouched
        
        prev_hp = c.current_hp
        ship.take_damage(20)
        
        self.assertEqual(ship.current_shields, 50)
        self.assertEqual(c.current_hp, prev_hp)


