"""Extended tests for Ship class methods."""
import unittest
import sys
import os
import pygame
import math

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ship import Ship, LayerType, initialize_ship_data
from components import load_components, create_component


class TestSolveLead(unittest.TestCase):
    """Test lead calculation for projectile interception."""
    
    @classmethod
    def setUpClass(cls):
        pygame.init()
        initialize_ship_data("C:\\Dev\\Starship Battles")
        load_components("data/components.json")
    
    @classmethod
    def tearDownClass(cls):
        pygame.quit()
    
    def setUp(self):
        self.ship = Ship("Shooter", 0, 0, (255, 255, 255))
        self.ship.add_component(create_component('bridge'), LayerType.CORE)
        self.ship.add_component(create_component('crew_quarters'), LayerType.CORE)
        self.ship.add_component(create_component('life_support'), LayerType.CORE)
        self.ship.recalculate_stats()
    
    def test_solve_lead_stationary_target(self):
        """For a stationary target, lead time should be simple distance / speed."""
        shooter_pos = pygame.math.Vector2(0, 0)
        shooter_vel = pygame.math.Vector2(0, 0)
        target_pos = pygame.math.Vector2(100, 0)
        target_vel = pygame.math.Vector2(0, 0)
        projectile_speed = 10
        
        t = self.ship.solve_lead(shooter_pos, shooter_vel, target_pos, target_vel, projectile_speed)
        
        # Expected time: 100 distance / 10 speed = 10
        self.assertGreater(t, 0)
        expected = 100 / projectile_speed
        self.assertAlmostEqual(t, expected, places=2)
    
    def test_solve_lead_moving_target_perpendicular(self):
        """Target moving perpendicular should require lead."""
        shooter_pos = pygame.math.Vector2(0, 0)
        shooter_vel = pygame.math.Vector2(0, 0)
        target_pos = pygame.math.Vector2(100, 0)
        target_vel = pygame.math.Vector2(0, 5)  # Moving up
        projectile_speed = 20
        
        t = self.ship.solve_lead(shooter_pos, shooter_vel, target_pos, target_vel, projectile_speed)
        
        # Should find a positive intercept time
        self.assertGreater(t, 0)
        
        # Verify the intercept point makes sense
        intercept_pos = target_pos + target_vel * t
        intercept_dist = intercept_pos.length()
        expected_travel_time = intercept_dist / projectile_speed
        self.assertAlmostEqual(t, expected_travel_time, places=2)
    
    def test_solve_lead_no_solution_target_too_fast(self):
        """If target is faster than projectile, may return 0."""
        shooter_pos = pygame.math.Vector2(0, 0)
        shooter_vel = pygame.math.Vector2(0, 0)
        target_pos = pygame.math.Vector2(100, 0)
        target_vel = pygame.math.Vector2(50, 0)  # Moving away very fast
        projectile_speed = 10  # Too slow to catch
        
        t = self.ship.solve_lead(shooter_pos, shooter_vel, target_pos, target_vel, projectile_speed)
        
        # Should return 0 when no solution exists
        self.assertEqual(t, 0)
    
    def test_solve_lead_approaching_target(self):
        """Target approaching should require less lead time."""
        shooter_pos = pygame.math.Vector2(0, 0)
        shooter_vel = pygame.math.Vector2(0, 0)
        target_pos = pygame.math.Vector2(100, 0)
        target_vel = pygame.math.Vector2(-5, 0)  # Moving toward
        projectile_speed = 10
        
        t = self.ship.solve_lead(shooter_pos, shooter_vel, target_pos, target_vel, projectile_speed)
        
        # Should find faster intercept than stationary
        self.assertGreater(t, 0)
        stationary_time = 100 / projectile_speed
        self.assertLess(t, stationary_time)


class TestIsDerelict(unittest.TestCase):
    """Test derelict status calculation."""
    
    @classmethod
    def setUpClass(cls):
        pygame.init()
        initialize_ship_data("C:\\Dev\\Starship Battles")
        load_components("data/components.json")
    
    @classmethod
    def tearDownClass(cls):
        pygame.quit()
    
    def test_healthy_ship_not_derelict(self):
        """Ship with bridge and engines should NOT be derelict."""
        ship = Ship("Healthy", 0, 0, (255, 255, 255))
        ship.add_component(create_component('bridge'), LayerType.CORE)
        ship.add_component(create_component('crew_quarters'), LayerType.CORE)
        ship.add_component(create_component('life_support'), LayerType.CORE)
        ship.add_component(create_component('standard_engine'), LayerType.OUTER)
        ship.recalculate_stats()
        
        self.assertFalse(ship.is_derelict)
    
    def test_no_bridge_is_derelict(self):
        """Ship without bridge should be derelict."""
        ship = Ship("NoBridge", 0, 0, (255, 255, 255))
        ship.add_component(create_component('crew_quarters'), LayerType.CORE)
        ship.add_component(create_component('life_support'), LayerType.CORE)
        ship.add_component(create_component('standard_engine'), LayerType.OUTER)
        ship.recalculate_stats()
        
        self.assertTrue(ship.is_derelict)
    
    def test_no_engine_is_derelict(self):
        """Ship without any propulsion should be derelict."""
        ship = Ship("NoEngine", 0, 0, (255, 255, 255))
        ship.add_component(create_component('bridge'), LayerType.CORE)
        ship.add_component(create_component('crew_quarters'), LayerType.CORE)
        ship.add_component(create_component('life_support'), LayerType.CORE)
        # No engines added
        ship.recalculate_stats()
        
        self.assertTrue(ship.is_derelict)
    
    def test_damaged_bridge_is_derelict(self):
        """Ship with destroyed bridge should be derelict."""
        ship = Ship("DamagedBridge", 0, 0, (255, 255, 255))
        bridge = create_component('bridge')
        ship.add_component(bridge, LayerType.CORE)
        ship.add_component(create_component('crew_quarters'), LayerType.CORE)
        ship.add_component(create_component('life_support'), LayerType.CORE)
        ship.add_component(create_component('standard_engine'), LayerType.OUTER)
        
        # Damage bridge below 50% threshold
        bridge.current_hp = bridge.max_hp * 0.4
        ship.recalculate_stats()
        
        # Bridge should now be inactive
        self.assertFalse(bridge.is_active)
        self.assertTrue(ship.is_derelict)


class TestToHitProfile(unittest.TestCase):
    """Test defensive to-hit profile calculation."""
    
    @classmethod
    def setUpClass(cls):
        pygame.init()
        initialize_ship_data("C:\\Dev\\Starship Battles")
        load_components("data/components.json")
    
    @classmethod
    def tearDownClass(cls):
        pygame.quit()
    
    def test_to_hit_profile_exists(self):
        """Ship should have a to_hit_profile attribute after recalculate_stats."""
        ship = Ship("TestShip", 0, 0, (255, 255, 255))
        ship.add_component(create_component('bridge'), LayerType.CORE)
        ship.add_component(create_component('crew_quarters'), LayerType.CORE)
        ship.add_component(create_component('life_support'), LayerType.CORE)
        ship.add_component(create_component('standard_engine'), LayerType.OUTER)
        ship.recalculate_stats()
        
        self.assertTrue(hasattr(ship, 'to_hit_profile'))
        self.assertIsInstance(ship.to_hit_profile, float)
        self.assertGreater(ship.to_hit_profile, 0)
    
    def test_larger_ship_higher_profile(self):
        """Larger ships should have higher to-hit profile (easier to hit)."""
        # Small ship
        small = Ship("Small", 0, 0, (255, 255, 255), ship_class="Escort")
        small.add_component(create_component('bridge'), LayerType.CORE)
        small.add_component(create_component('crew_quarters'), LayerType.CORE)
        small.add_component(create_component('life_support'), LayerType.CORE)
        small.add_component(create_component('standard_engine'), LayerType.OUTER)
        small.recalculate_stats()
        
        # Large ship with more mass
        large = Ship("Large", 0, 0, (255, 255, 255), ship_class="Battleship")
        large.add_component(create_component('bridge'), LayerType.CORE)
        large.add_component(create_component('crew_quarters'), LayerType.CORE)
        large.add_component(create_component('life_support'), LayerType.CORE)
        large.add_component(create_component('standard_engine'), LayerType.OUTER)
        # Add more mass to increase size
        for _ in range(10):
            large.add_component(create_component('armor_plate'), LayerType.ARMOR)
        large.recalculate_stats()
        
        # Larger ship should be easier to hit
        self.assertGreater(large.to_hit_profile, small.to_hit_profile)
    
    def test_baseline_offense_exists(self):
        """Ship should have baseline_to_hit_offense attribute."""
        ship = Ship("TestShip", 0, 0, (255, 255, 255))
        ship.add_component(create_component('bridge'), LayerType.CORE)
        ship.add_component(create_component('crew_quarters'), LayerType.CORE)
        ship.add_component(create_component('life_support'), LayerType.CORE)
        ship.recalculate_stats()
        
        self.assertTrue(hasattr(ship, 'baseline_to_hit_offense'))
        self.assertIsInstance(ship.baseline_to_hit_offense, float)


class TestMaxWeaponRange(unittest.TestCase):
    """Test max weapon range property."""
    
    @classmethod
    def setUpClass(cls):
        pygame.init()
        initialize_ship_data("C:\\Dev\\Starship Battles")
        load_components("data/components.json")
    
    @classmethod
    def tearDownClass(cls):
        pygame.quit()
    
    def test_max_weapon_range_no_weapons(self):
        """Ship with no weapons should have 0 max range."""
        ship = Ship("Unarmed", 0, 0, (255, 255, 255))
        ship.add_component(create_component('bridge'), LayerType.CORE)
        ship.add_component(create_component('crew_quarters'), LayerType.CORE)
        ship.add_component(create_component('life_support'), LayerType.CORE)
        ship.recalculate_stats()
        
        self.assertEqual(ship.max_weapon_range, 0)
    
    def test_max_weapon_range_single_weapon(self):
        """Ship with one weapon should return that weapon's range."""
        ship = Ship("Armed", 0, 0, (255, 255, 255))
        ship.add_component(create_component('bridge'), LayerType.CORE)
        ship.add_component(create_component('crew_quarters'), LayerType.CORE)
        ship.add_component(create_component('life_support'), LayerType.CORE)
        railgun = create_component('railgun')
        ship.add_component(railgun, LayerType.OUTER)
        ship.recalculate_stats()
        
        self.assertEqual(ship.max_weapon_range, railgun.range)
    
    def test_max_weapon_range_multiple_weapons(self):
        """Ship with multiple weapons should return longest range."""
        ship = Ship("HeavilyArmed", 0, 0, (255, 255, 255))
        ship.add_component(create_component('bridge'), LayerType.CORE)
        ship.add_component(create_component('crew_quarters'), LayerType.CORE)
        ship.add_component(create_component('life_support'), LayerType.CORE)
        
        # Add different weapons
        railgun = create_component('railgun')
        laser = create_component('laser_cannon')
        ship.add_component(railgun, LayerType.OUTER)
        ship.add_component(laser, LayerType.OUTER)
        ship.recalculate_stats()
        
        expected_max = max(railgun.range, laser.range)
        self.assertEqual(ship.max_weapon_range, expected_max)


if __name__ == '__main__':
    unittest.main()
