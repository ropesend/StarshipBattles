"""
Engine Physics Tests (ENG-001 through ENG-005)

Validates engine physics formulas from ship_stats.py:
- max_speed = (thrust * K_SPEED) / mass  where K_SPEED = 25
- acceleration = (thrust * K_THRUST) / mass²  where K_THRUST = 2500
"""
import pytest
import os
import json
import math

from game.simulation.entities.ship import Ship

# Physics constants (must match ship_stats.py)
K_SPEED = 25
K_THRUST = 2500


@pytest.mark.simulation
class TestEnginePhysics:
    """Test engine physics formulas."""
    
    @pytest.fixture(autouse=True)
    def setup(self, isolated_registry, ships_dir):
        """Use isolated registry and store ships_dir."""
        self.ships_dir = ships_dir
    
    def _load_ship(self, filename: str) -> Ship:
        """Load ship from JSON and calculate stats."""
        path = os.path.join(self.ships_dir, filename)
        with open(path, 'r') as f:
            data = json.load(f)
        ship = Ship.from_dict(data)
        ship.recalculate_stats()
        return ship
    
    def test_ENG_001_base_speed_calculation(self):
        """
        ENG-001: Verify base speed formula with low mass ship.
        
        Ship: Test_Engine_1x_LowMass (1 engine, no ballast)
        Formula: max_speed = (thrust * K_SPEED) / mass
        """
        ship = self._load_ship('Test_Engine_1x_LowMass.json')
        
        # Get actual values
        thrust = ship.total_thrust
        mass = ship.mass
        
        # Calculate expected (thrust * 25 / mass)
        expected_speed = (thrust * K_SPEED) / mass
        expected_accel = (thrust * K_THRUST) / (mass ** 2)
        
        # Verify speed formula
        assert abs(ship.max_speed - expected_speed) < 0.1, \
            f"max_speed: expected {expected_speed:.2f}, got {ship.max_speed:.2f}"
        
        # Verify acceleration formula
        assert abs(ship.acceleration_rate - expected_accel) < 0.1, \
            f"acceleration: expected {expected_accel:.2f}, got {ship.acceleration_rate:.2f}"
    
    def test_ENG_002_speed_decreases_linearly_with_mass(self):
        """
        ENG-002: Speed decreases linearly with mass (speed ∝ 1/mass).
        
        Compare ships with same engine but different mass values.
        If mass doubles, speed should halve.
        """
        low_mass = self._load_ship('Test_Engine_1x_LowMass.json')
        med_mass = self._load_ship('Test_Engine_1x_MedMass.json')
        high_mass = self._load_ship('Test_Engine_1x_HighMass.json')
        
        # All should have same thrust (1 engine)
        assert low_mass.total_thrust == med_mass.total_thrust == high_mass.total_thrust, \
            "Test ships should have identical thrust"
        
        # Verify speed ratio matches inverse mass ratio
        # low_mass.max_speed / med_mass.max_speed should equal med_mass.mass / low_mass.mass
        ratio_low_med = low_mass.max_speed / med_mass.max_speed
        expected_ratio_low_med = med_mass.mass / low_mass.mass
        
        assert abs(ratio_low_med - expected_ratio_low_med) < 0.05, \
            f"Speed ratio low/med: expected {expected_ratio_low_med:.2f}, got {ratio_low_med:.2f}"
        
        # Verify high mass ship is slower
        assert high_mass.max_speed < med_mass.max_speed < low_mass.max_speed, \
            "Higher mass ships should have lower max speed"
    
    def test_ENG_003_accel_decreases_quadratically_with_mass(self):
        """
        ENG-003: Acceleration decreases quadratically with mass (accel ∝ 1/mass²).
        
        If mass doubles, acceleration should quarter.
        """
        low_mass = self._load_ship('Test_Engine_1x_LowMass.json')
        med_mass = self._load_ship('Test_Engine_1x_MedMass.json')
        
        # Verify acceleration ratio matches inverse square mass ratio
        ratio = low_mass.acceleration_rate / med_mass.acceleration_rate
        mass_factor = med_mass.mass / low_mass.mass
        expected_ratio = mass_factor ** 2  # Quadratic relationship
        
        assert abs(ratio - expected_ratio) / expected_ratio < 0.05, \
            f"Accel ratio: expected {expected_ratio:.2f}, got {ratio:.2f}"
    
    def test_ENG_004_speed_increases_linearly_with_thrust(self):
        """
        ENG-004: Speed increases linearly with thrust (at similar mass).
        
        3x the engines should give approximately 3x the speed.
        """
        one_engine = self._load_ship('Test_Engine_1x_LowMass.json')
        three_engine = self._load_ship('Test_Engine_3x_LowMass.json')
        
        # Verify thrust ratio
        thrust_ratio = three_engine.total_thrust / one_engine.total_thrust
        assert abs(thrust_ratio - 3.0) < 0.1, \
            f"Expected 3x thrust, got {thrust_ratio:.1f}x"
        
        # Speed should also scale roughly 3x (adjusted for mass difference)
        # Since mass may differ slightly, calculate expected speed
        expected_speed_ratio = (three_engine.total_thrust / three_engine.mass) / \
                               (one_engine.total_thrust / one_engine.mass)
        actual_speed_ratio = three_engine.max_speed / one_engine.max_speed
        
        assert abs(actual_speed_ratio - expected_speed_ratio) / expected_speed_ratio < 0.05, \
            f"Speed ratio: expected {expected_speed_ratio:.2f}, got {actual_speed_ratio:.2f}"
    
    def test_ENG_005_formula_verification_multiple_configs(self):
        """
        ENG-005: Verify formulas hold for various ship configurations.
        
        Tests that the physics engine correctly implements:
        - max_speed = (thrust * K_SPEED) / mass
        - acceleration = (thrust * K_THRUST) / mass²
        """
        test_ships = [
            'Test_Engine_1x_LowMass.json',
            'Test_Engine_1x_MedMass.json',
            'Test_Engine_1x_HighMass.json',
            'Test_Engine_3x_LowMass.json',
            'Test_Engine_3x_HighMass.json',
        ]
        
        for ship_file in test_ships:
            ship = self._load_ship(ship_file)
            
            expected_speed = (ship.total_thrust * K_SPEED) / ship.mass
            expected_accel = (ship.total_thrust * K_THRUST) / (ship.mass ** 2)
            
            # Allow 1% tolerance
            assert abs(ship.max_speed - expected_speed) / expected_speed < 0.01, \
                f"{ship_file}: max_speed expected {expected_speed:.4f}, got {ship.max_speed:.4f}"
            
            assert abs(ship.acceleration_rate - expected_accel) / expected_accel < 0.01, \
                f"{ship_file}: acceleration expected {expected_accel:.4f}, got {ship.acceleration_rate:.4f}"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
