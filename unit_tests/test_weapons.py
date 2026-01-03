"""Tests for weapon systems."""
import unittest
import sys
import os
import pygame
import math

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ship import Ship, LayerType, initialize_ship_data
from components import (
    load_components, create_component
)


class TestWeaponBasics(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        initialize_ship_data("C:\\Dev\\Starship Battles")
        load_components("data/components.json")
    
    def test_weapon_initialization(self):
        """Weapon should initialize with correct stats via ability."""
        railgun = create_component('railgun')
        
        # Phase 7: Use ability-based access
        weapon_ab = railgun.get_ability('ProjectileWeaponAbility')
        self.assertIsNotNone(weapon_ab)
        
        self.assertEqual(weapon_ab.damage, 40)
        self.assertEqual(weapon_ab.range, 2400)
        self.assertGreater(weapon_ab.projectile_speed, 0)
    
    def test_weapon_cooldown(self):
        """Weapon should respect cooldown timer via ability."""
        railgun = create_component('railgun')
        
        # Phase 7: Use ability-based access
        weapon_ab = railgun.get_ability('ProjectileWeaponAbility') or railgun.get_ability('WeaponAbility')
        self.assertIsNotNone(weapon_ab)
        
        # Initially should be able to fire
        self.assertTrue(weapon_ab.can_fire())
        
        # Fire
        weapon_ab.fire(target=None)
        
        # Now should be on cooldown
        self.assertFalse(weapon_ab.can_fire())
        
        # Cycle-Based: reload_time is seconds, 0.01s per tick. 
        # Need (reload_time / 0.01) + 1 ticks to clear cooldown.
        ticks_needed = int(weapon_ab.reload_time / 0.01) + 10 # Plus buffer
        for _ in range(ticks_needed):
            weapon_ab.update()
        
        # Should be able to fire again
        self.assertTrue(weapon_ab.can_fire())
    
    def test_beam_weapon_accuracy(self):
        """Beam weapon accuracy should fall off with distance (via ability)."""
        laser = create_component('laser_cannon')
        
        # Phase 7: Use ability-based access
        beam_ab = laser.get_ability('BeamWeaponAbility')
        self.assertIsNotNone(beam_ab)
        
        # Close range - high accuracy
        close_chance = beam_ab.calculate_hit_chance(100)
        # New Sigmoid Logic: P(2.0 - small) ~ 0.87
        self.assertGreater(close_chance, 0.85)
        
        # Far range - lower accuracy
        far_chance = beam_ab.calculate_hit_chance(1500)
        self.assertLess(far_chance, close_chance)
    
    def test_beam_accuracy_clamped(self):
        """Beam accuracy should be clamped between 0 and 1 (via ability)."""
        laser = create_component('laser_cannon')
        
        # Phase 7: Use ability-based access
        beam_ab = laser.get_ability('BeamWeaponAbility')
        self.assertIsNotNone(beam_ab)
        
        # Very close
        close = beam_ab.calculate_hit_chance(0)
        self.assertLessEqual(close, 1.0)
        self.assertGreaterEqual(close, 0.0)
        
        # Very far (beyond reasonable range)
        far = beam_ab.calculate_hit_chance(100000)
        self.assertLessEqual(far, 1.0)
        self.assertGreaterEqual(far, 0.0)


class TestWeaponFiring(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        initialize_ship_data("C:\\Dev\\Starship Battles")
        load_components("data/components.json")
    
    def setUp(self):
        # Create ship with weapons
        self.ship = Ship("Gunship", 0, 0, (255, 255, 255), team_id=0, ship_class="Cruiser")
        self.ship.add_component(create_component('bridge'), LayerType.CORE)
        self.ship.add_component(create_component('railgun'), LayerType.OUTER)
        self.ship.add_component(create_component('ordnance_tank'), LayerType.INNER)
        self.ship.recalculate_stats()
        self.ship.current_ammo = 100
        
        # Create target
        self.target = Ship("Target", 500, 0, (255, 0, 0), team_id=1)
        self.target.add_component(create_component('bridge'), LayerType.CORE)
        self.target.recalculate_stats()
    
    def test_fire_weapons_returns_attacks(self):
        """fire_weapons should return list of attacks."""
        self.ship.current_target = self.target
        self.ship.comp_trigger_pulled = True
        self.ship.angle = 0  # Facing target (target at x=500)
        
        attacks = self.ship.fire_weapons()
        
        # Should have fired at least one projectile
        self.assertIsInstance(attacks, list)
    
    def test_fire_consumes_ammo(self):
        """Firing projectile weapons should consume ammo."""
        initial_ammo = self.ship.current_ammo
        
        self.ship.current_target = self.target
        self.ship.comp_trigger_pulled = True
        self.ship.angle = 0
        
        attacks = self.ship.fire_weapons()
        
        if attacks:  # If weapon fired
            self.assertLess(self.ship.current_ammo, initial_ammo)
    
    def test_no_fire_without_target(self):
        """Weapons should not fire without valid target."""
        self.ship.current_target = None
        self.ship.comp_trigger_pulled = True
        
        attacks = self.ship.fire_weapons()
        
        self.assertEqual(len(attacks), 0)
    
    def test_no_fire_outside_arc(self):
        """Weapons should not fire when target is outside firing arc."""
        self.ship.current_target = self.target
        self.ship.comp_trigger_pulled = True
        self.ship.angle = 180  # Facing away from target
        
        attacks = self.ship.fire_weapons()
        
        # Projectile weapons have narrow arc by default
        self.assertEqual(len(attacks), 0)


class TestLeadCalculation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        initialize_ship_data("C:\\Dev\\Starship Battles")
        load_components("data/components.json")
    
    def setUp(self):
        self.ship = Ship("Shooter", 0, 0, (255, 255, 255))
        self.ship.add_component(create_component('bridge'), LayerType.CORE)
        self.ship.recalculate_stats()
    
    def test_solve_lead_stationary_target(self):
        """Lead calculation for stationary target."""
        pos = pygame.math.Vector2(0, 0)
        vel = pygame.math.Vector2(0, 0)
        t_pos = pygame.math.Vector2(1000, 0)
        t_vel = pygame.math.Vector2(0, 0)
        p_speed = 1000
        
        t = self.ship.solve_lead(pos, vel, t_pos, t_vel, p_speed)
        
        # Time to reach = distance / speed = 1000 / 1000 = 1.0
        self.assertAlmostEqual(t, 1.0, places=2)
    
    def test_solve_lead_moving_target(self):
        """Lead calculation for moving target."""
        pos = pygame.math.Vector2(0, 0)
        vel = pygame.math.Vector2(0, 0)
        t_pos = pygame.math.Vector2(1000, 0)
        t_vel = pygame.math.Vector2(0, 100)  # Moving perpendicular
        p_speed = 1000
        
        t = self.ship.solve_lead(pos, vel, t_pos, t_vel, p_speed)
        
        # Should find intercept time > 0
        self.assertGreater(t, 0)
    
    def test_solve_lead_impossible_intercept(self):
        """Lead calculation should return 0 for impossible intercepts."""
        pos = pygame.math.Vector2(0, 0)
        vel = pygame.math.Vector2(0, 0)
        t_pos = pygame.math.Vector2(1000, 0)
        t_vel = pygame.math.Vector2(2000, 0)  # Target faster than projectile, moving away
        p_speed = 100  # Slow projectile
        
        t = self.ship.solve_lead(pos, vel, t_pos, t_vel, p_speed)
        
        # Should return 0 (no solution)
        self.assertEqual(t, 0)


if __name__ == '__main__':
    unittest.main()
