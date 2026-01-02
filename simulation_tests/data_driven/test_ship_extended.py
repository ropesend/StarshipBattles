"""Extended tests for Ship class methods."""
import unittest
import sys
import os
import pygame
import math

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from ship import Ship, LayerType, initialize_ship_data, load_vehicle_classes
from components import load_components, create_component


class TestSolveLead(unittest.TestCase):
    """Test lead calculation for projectile interception."""
    
    @classmethod
    def setUpClass(cls):
        pygame.init()
        load_vehicle_classes("unit_tests/data/test_vehicleclasses.json")
        load_components("unit_tests/data/test_components.json")
    
    @classmethod
    def tearDownClass(cls):
        pygame.quit()
    
    def setUp(self):
        self.ship = Ship("Shooter", 0, 0, (255, 255, 255))
        self.ship.add_component(create_component('test_bridge_basic'), LayerType.CORE)
        self.ship.add_component(create_component('test_crew_quarters'), LayerType.CORE)
        self.ship.add_component(create_component('test_life_support'), LayerType.CORE)
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


class TestToHitProfile(unittest.TestCase):
    """Test defensive to-hit profile calculation (Defense Score)."""
    
    @classmethod
    def setUpClass(cls):
        pygame.init()
        load_vehicle_classes("unit_tests/data/test_vehicleclasses.json")
        load_components("unit_tests/data/test_components.json")
    
    @classmethod
    def tearDownClass(cls):
        pygame.quit()
    
    def test_to_hit_profile_exists(self):
        """Ship should have a to_hit_profile attribute after recalculate_stats."""
        ship = Ship("TestShip", 0, 0, (255, 255, 255))
        ship.add_component(create_component('test_bridge_basic'), LayerType.CORE)
        ship.add_component(create_component('test_crew_quarters'), LayerType.CORE)
        ship.add_component(create_component('test_life_support'), LayerType.CORE)
        ship.add_component(create_component('test_engine_std'), LayerType.OUTER)
        ship.recalculate_stats()
        
        self.assertTrue(hasattr(ship, 'to_hit_profile'))
        # Can be float or int
        self.assertIsInstance(ship.to_hit_profile, (float, int))
        
    def test_larger_ship_easier_to_hit(self):
        """Larger ships should have LOWER Defense Score (Easier to Hit)."""
        # Small ship - TestShip_S_2L (Max Mass 2000)
        small = Ship("Small", 0, 0, (255, 255, 255), ship_class="TestShip_S_2L")
        small.add_component(create_component('test_bridge_basic'), LayerType.CORE)
        small.add_component(create_component('test_crew_quarters'), LayerType.CORE)
        small.add_component(create_component('test_life_support'), LayerType.CORE)
        small.add_component(create_component('test_engine_std'), LayerType.CORE)
        small.recalculate_stats()
        
        # Large ship - TestShip_L_4L (Max Mass 10000)
        large = Ship("Large", 0, 0, (255, 255, 255), ship_class="TestShip_L_4L")
        large.add_component(create_component('test_bridge_basic'), LayerType.CORE)
        large.add_component(create_component('test_crew_quarters'), LayerType.CORE)
        large.add_component(create_component('test_life_support'), LayerType.CORE)
        large.add_component(create_component('test_engine_std'), LayerType.OUTER)
        # Add massive bulk
        for _ in range(20):
             # Adding heavy structure/armor to increase mass/radius
             large.add_component(create_component('test_armor_std'), LayerType.ARMOR)
             
        large.recalculate_stats()
        
        # Logic: Defense Score = SizeScore + ManueverScore
        # Large Size = Negative Score. Small Size = Less Negative/Positive.
        # So Large Ship Score < Small Ship Score
        self.assertLess(large.to_hit_profile, small.to_hit_profile)
    
    def test_baseline_offense_exists(self):
        """Ship should have baseline_to_hit_offense attribute."""
        ship = Ship("TestShip", 0, 0, (255, 255, 255))
        ship.add_component(create_component('test_bridge_basic'), LayerType.CORE)
        ship.add_component(create_component('test_crew_quarters'), LayerType.CORE)
        ship.add_component(create_component('test_life_support'), LayerType.CORE)
        ship.recalculate_stats()
        
        self.assertTrue(hasattr(ship, 'baseline_to_hit_offense'))
        self.assertIsInstance(ship.baseline_to_hit_offense, (float, int))


class TestMaxWeaponRange(unittest.TestCase):
    """Test max weapon range property."""
    
    @classmethod
    def setUpClass(cls):
        pygame.init()
        load_vehicle_classes("unit_tests/data/test_vehicleclasses.json")
        load_components("unit_tests/data/test_components.json")
    
    @classmethod
    def tearDownClass(cls):
        pygame.quit()
    
    def test_max_weapon_range_no_weapons(self):
        """Ship with no weapons should have 0 max range."""
        ship = Ship("Unarmed", 0, 0, (255, 255, 255))
        ship.add_component(create_component('test_bridge_basic'), LayerType.CORE)
        ship.add_component(create_component('test_crew_quarters'), LayerType.CORE)
        ship.add_component(create_component('test_life_support'), LayerType.CORE)
        ship.recalculate_stats()
        
        self.assertEqual(ship.max_weapon_range, 0)
    
    def test_max_weapon_range_single_weapon(self):
        """Ship with one weapon should return that weapon's range."""
        ship = Ship("Armed", 0, 0, (255, 255, 255))
        ship.add_component(create_component('test_bridge_basic'), LayerType.CORE)
        ship.add_component(create_component('test_crew_quarters'), LayerType.CORE)
        ship.add_component(create_component('test_life_support'), LayerType.CORE)
        railgun = create_component('test_weapon_proj_fixed')
        ship.add_component(railgun, LayerType.OUTER)
        ship.recalculate_stats()
        
        self.assertEqual(ship.max_weapon_range, railgun.range)
    
    def test_max_weapon_range_multiple_weapons(self):
        """Ship with multiple weapons should return longest range."""
        ship = Ship("HeavilyArmed", 0, 0, (255, 255, 255))
        ship.add_component(create_component('test_bridge_basic'), LayerType.CORE)
        ship.add_component(create_component('test_crew_quarters'), LayerType.CORE)
        ship.add_component(create_component('test_life_support'), LayerType.CORE)
        
        # Add different weapons
        railgun = create_component('test_weapon_proj_fixed')
        laser = create_component('test_weapon_beam_std')
        ship.add_component(railgun, LayerType.OUTER)
        ship.add_component(laser, LayerType.OUTER)
        ship.recalculate_stats()
        
        expected_max = max(railgun.range, laser.range)
        self.assertEqual(ship.max_weapon_range, expected_max)


if __name__ == '__main__':
    unittest.main()

