"""
Engine Physics Tests (ENG-001 through ENG-004)

Validates engine physics formulas from ship_stats.py:
- max_speed = (thrust * K_SPEED) / mass  where K_SPEED = 25
- acceleration = (thrust * K_THRUST) / mass²  where K_THRUST = 2500
"""
import unittest
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from game.simulation.entities.ship import Ship, LayerType, load_vehicle_classes
from game.simulation.components.component import load_components, create_component
import pytest


# Physics constants from ship_stats.py
K_SPEED = 25
K_THRUST = 2500


@pytest.mark.use_custom_data
class TestEnginePhysics(unittest.TestCase):
    """Test engine physics formulas for speed and acceleration."""
    
    @classmethod
    def setUpClass(cls):
        # pygame.init() removed for session isolation
        load_vehicle_classes("tests/unit/data/test_vehicleclasses.json")
        load_components("tests/unit/data/test_components.json")
    
    @classmethod
    def tearDownClass(cls):
        pass # pygame.quit() removed for session isolation
    
    def _build_engine_ship(self, ship_class, num_engines, mass_sims_1k=0, mass_sims_10k=0):
        """Helper to build a test ship with specified engines and mass simulators."""
        ship = Ship("EngineTest", 0, 0, (0, 255, 0), ship_class=ship_class)
        
        # Add engines
        for _ in range(num_engines):
            ship.add_component(create_component('test_engine_std'), LayerType.CORE)
        
        # Add mass simulators
        for _ in range(mass_sims_1k):
            ship.add_component(create_component('test_mass_sim_1k'), LayerType.CORE)
        for _ in range(mass_sims_10k):
            ship.add_component(create_component('test_mass_sim_10k'), LayerType.CORE)
        
        ship.recalculate_stats()
        return ship
    
    def test_ENG_001_base_speed_accel_calculation(self):
        """ENG-001: Verify base speed/acceleration formulas with minimal mass ship."""
        # Build: 1 engine, minimal mass (TestS_2L: hull 20 + engine 20 = 40 mass)
        ship = self._build_engine_ship("TestS_2L", num_engines=1)
        
        # Expected values
        thrust = 500  # test_engine_std thrust
        mass = 40     # hull(20) + engine(20)
        expected_speed = (thrust * K_SPEED) / mass  # 312.5
        expected_accel = (thrust * K_THRUST) / (mass ** 2)  # 78125
        
        self.assertEqual(ship.total_thrust, thrust)
        self.assertEqual(ship.mass, mass)
        self.assertAlmostEqual(ship.max_speed, expected_speed, places=1,
                               msg=f"max_speed: expected {expected_speed}, got {ship.max_speed}")
        self.assertAlmostEqual(ship.acceleration_rate, expected_accel, places=0,
                               msg=f"acceleration: expected {expected_accel}, got {ship.acceleration_rate}")
    
    def test_ENG_002_speed_decreases_linearly_with_mass(self):
        """ENG-002: Speed decreases linearly with mass (speed ∝ 1/mass)."""
        # Three ships: same thrust (500), different masses
        ship_low = self._build_engine_ship("TestS_2L", num_engines=1)  # 40 mass
        ship_med = self._build_engine_ship("TestS_2L", num_engines=1, mass_sims_1k=2)  # 2040 mass
        ship_high = self._build_engine_ship("TestM_2L", num_engines=1, mass_sims_10k=1)  # 10220 mass
        
        # Verify speed decreases
        self.assertGreater(ship_low.max_speed, ship_med.max_speed,
                           "Low mass ship should be faster than medium")
        self.assertGreater(ship_med.max_speed, ship_high.max_speed,
                           "Medium mass ship should be faster than high")
        
        # Verify linear relationship: speed_ratio == mass_ratio (inverse)
        # ship_low to ship_med
        speed_ratio_1 = ship_low.max_speed / ship_med.max_speed
        mass_ratio_1 = ship_med.mass / ship_low.mass
        self.assertAlmostEqual(speed_ratio_1, mass_ratio_1, places=1,
                               msg=f"Speed ratio {speed_ratio_1} should equal mass ratio {mass_ratio_1}")
        
        # ship_med to ship_high
        speed_ratio_2 = ship_med.max_speed / ship_high.max_speed
        mass_ratio_2 = ship_high.mass / ship_med.mass
        self.assertAlmostEqual(speed_ratio_2, mass_ratio_2, places=1,
                               msg=f"Speed ratio {speed_ratio_2} should equal mass ratio {mass_ratio_2}")
    
    def test_ENG_003_accel_decreases_quadratically_with_mass(self):
        """ENG-003: Acceleration decreases quadratically with mass (accel ∝ 1/mass²)."""
        # Same three ships as ENG-002
        ship_low = self._build_engine_ship("TestS_2L", num_engines=1)  # 40 mass
        ship_med = self._build_engine_ship("TestS_2L", num_engines=1, mass_sims_1k=2)  # 2040 mass
        ship_high = self._build_engine_ship("TestM_2L", num_engines=1, mass_sims_10k=1)  # 10220 mass
        
        # Verify accel decreases
        self.assertGreater(ship_low.acceleration_rate, ship_med.acceleration_rate,
                           "Low mass ship should have higher accel than medium")
        self.assertGreater(ship_med.acceleration_rate, ship_high.acceleration_rate,
                           "Medium mass ship should have higher accel than high")
        
        # Verify quadratic relationship: accel_ratio == mass_ratio²
        # ship_low to ship_med
        accel_ratio_1 = ship_low.acceleration_rate / ship_med.acceleration_rate
        mass_ratio_1_squared = (ship_med.mass / ship_low.mass) ** 2
        self.assertAlmostEqual(accel_ratio_1, mass_ratio_1_squared, places=0,
                               msg=f"Accel ratio {accel_ratio_1} should equal mass ratio² {mass_ratio_1_squared}")
        
        # ship_med to ship_high
        accel_ratio_2 = ship_med.acceleration_rate / ship_high.acceleration_rate
        mass_ratio_2_squared = (ship_high.mass / ship_med.mass) ** 2
        self.assertAlmostEqual(accel_ratio_2, mass_ratio_2_squared, places=0,
                               msg=f"Accel ratio {accel_ratio_2} should equal mass ratio² {mass_ratio_2_squared}")
    
    def test_ENG_004_speed_increases_linearly_with_thrust(self):
        """ENG-004: Speed increases linearly with thrust (at same mass)."""
        # Two ships with different engine counts but same base class
        # Using same class for similar hull mass, comparing thrust effect
        
        # 1 engine: thrust 500
        ship_1x = self._build_engine_ship("TestM_3L", num_engines=1)
        # 3 engines: thrust 1500
        ship_3x = self._build_engine_ship("TestM_3L", num_engines=3)
        
        # Mass difference is small (2 extra engines = 40 mass difference)
        # Focus on verifying thrust increase produces proportional speed increase
        
        # Calculate expected speeds using actual masses
        expected_1x = (500 * K_SPEED) / ship_1x.mass
        expected_3x = (1500 * K_SPEED) / ship_3x.mass
        
        self.assertAlmostEqual(ship_1x.max_speed, expected_1x, places=1)
        self.assertAlmostEqual(ship_3x.max_speed, expected_3x, places=1)
        
        # 3x engines should give approximately 3x speed (slightly less due to engine mass)
        speed_increase_ratio = ship_3x.max_speed / ship_1x.max_speed
        thrust_ratio = 3.0
        # Allow 15% variance due to mass difference from engines
        self.assertAlmostEqual(speed_increase_ratio, thrust_ratio, delta=0.5,
                               msg=f"3x engines should give ~3x speed. Got ratio: {speed_increase_ratio}")


@pytest.mark.use_custom_data
class TestEnginePhysicsFormulas(unittest.TestCase):
    """Direct formula validation tests - dynamically calculates expected values."""
    
    @classmethod
    def setUpClass(cls):
        # pygame.init() removed for session isolation
        load_vehicle_classes("unit_tests/data/test_vehicleclasses.json")
        load_components("unit_tests/data/test_components.json")
    
    @classmethod
    def tearDownClass(cls):
        pass # pygame.quit() removed for session isolation
    
    def _build_and_verify(self, ship_class, engines, mass_1k=0, mass_10k=0):
        """Build ship and verify formulas match calculated values."""
        ship = Ship("FormulaTest", 0, 0, (255, 255, 255), ship_class=ship_class)
        for _ in range(engines):
            ship.add_component(create_component('test_engine_std'), LayerType.CORE)
        for _ in range(mass_1k):
            ship.add_component(create_component('test_mass_sim_1k'), LayerType.CORE)
        for _ in range(mass_10k):
            ship.add_component(create_component('test_mass_sim_10k'), LayerType.CORE)
        ship.recalculate_stats()
        return ship
    
    def test_formula_max_speed(self):
        """Verify max_speed = (thrust * 25) / mass for various configurations."""
        test_cases = [
            # (ship_class, engines, mass_1k, mass_10k)
            ("TestS_2L", 1, 0, 0),     # Minimal
            ("TestS_2L", 1, 1, 0),     # Medium mass
            ("TestM_2L", 1, 0, 1),     # High mass
            ("TestM_3L", 3, 0, 0),     # Multiple engines
        ]
        
        for ship_class, engines, m1k, m10k in test_cases:
            with self.subTest(ship_class=ship_class, engines=engines, m1k=m1k, m10k=m10k):
                ship = self._build_and_verify(ship_class, engines, m1k, m10k)
                
                # Calculate expected speed using actual mass
                expected_speed = (ship.total_thrust * K_SPEED) / ship.mass
                self.assertAlmostEqual(ship.max_speed, expected_speed, places=5,
                    msg=f"max_speed formula mismatch: got {ship.max_speed}, expected {expected_speed}")
    
    def test_formula_acceleration(self):
        """Verify acceleration = (thrust * 2500) / mass² for various configurations."""
        test_cases = [
            # (ship_class, engines, mass_1k, mass_10k)
            ("TestS_2L", 1, 0, 0),
            ("TestS_2L", 1, 1, 0),
            ("TestM_2L", 1, 0, 1),
            ("TestM_3L", 3, 0, 0),
        ]
        
        for ship_class, engines, m1k, m10k in test_cases:
            with self.subTest(ship_class=ship_class, engines=engines, m1k=m1k, m10k=m10k):
                ship = self._build_and_verify(ship_class, engines, m1k, m10k)
                
                # Calculate expected accel using actual mass
                expected_accel = (ship.total_thrust * K_THRUST) / (ship.mass ** 2)
                self.assertAlmostEqual(ship.acceleration_rate, expected_accel, places=5,
                    msg=f"acceleration formula mismatch: got {ship.acceleration_rate}, expected {expected_accel}")


if __name__ == '__main__':
    unittest.main()
