"""
Tests for PROP-005: Mass Affects Turn Rate scenario.

TDD tests for verifying that:
- PROP-005 scenario exists and has correct metadata
- Two ships have same thruster but different masses
- High mass ship has lower turn_speed than low mass ship
- Turn speed ratio matches (mass_high/mass_low)^1.5 exactly
"""
import pytest
from game.simulation.physics_constants import K_TURN


# =============================================================================
# EXPECTED PHYSICS VALUES FOR PROP-005
# =============================================================================
PROP005_RAW_TURN_RATE = 5.0  # test_thruster_std
PROP005_LOW_MASS = 400  # hull_test_s
PROP005_HIGH_MASS = 3000  # hull_test_m(1000) + 2×mass_sim_1k(1000) = 3000

# Calculate expected turn speeds using formula: turn_speed = (raw * K_TURN) / mass^1.5
PROP005_LOW_TURN_SPEED = (PROP005_RAW_TURN_RATE * K_TURN) / (PROP005_LOW_MASS ** 1.5)
PROP005_HIGH_TURN_SPEED = (PROP005_RAW_TURN_RATE * K_TURN) / (PROP005_HIGH_MASS ** 1.5)

# Expected ratio: low_turn_speed / high_turn_speed = (high_mass/low_mass)^1.5
PROP005_EXPECTED_RATIO = (PROP005_HIGH_MASS / PROP005_LOW_MASS) ** 1.5


class TestPROP005ScenarioExists:
    """Tests that PROP-005 scenario exists and is properly configured."""

    def test_prop005_class_exists(self):
        """PROP-005 scenario class should exist."""
        from combat_lab.scenarios.propulsion_scenarios import PropMassAffectsTurnRateScenario
        assert PropMassAffectsTurnRateScenario is not None

    def test_prop005_has_correct_test_id(self):
        """PROP-005 should have test_id='PROP-005'."""
        from combat_lab.scenarios.propulsion_scenarios import PropMassAffectsTurnRateScenario
        scenario = PropMassAffectsTurnRateScenario()
        assert scenario.metadata.test_id == "PROP-005"

    def test_prop005_is_in_propulsion_category(self):
        """PROP-005 should be in Propulsion category."""
        from combat_lab.scenarios.propulsion_scenarios import PropMassAffectsTurnRateScenario
        scenario = PropMassAffectsTurnRateScenario()
        assert scenario.metadata.category == "Propulsion"

class TestPROP005ShipConfiguration:
    """Tests for PROP-005 ship configuration."""

    def test_prop005_uses_low_mass_ship(self):
        """PROP-005 should load a low mass ship (400)."""
        from combat_lab.scenarios.propulsion_scenarios import (
            PropMassAffectsTurnRateScenario,
            PROP005_LOW_MASS
        )
        assert PROP005_LOW_MASS == 400

    def test_prop005_uses_high_mass_ship(self):
        """PROP-005 should load a high mass ship (3000)."""
        from combat_lab.scenarios.propulsion_scenarios import (
            PropMassAffectsTurnRateScenario,
            PROP005_HIGH_MASS
        )
        assert PROP005_HIGH_MASS == 3000

    def test_prop005_ships_have_same_raw_turn_rate(self):
        """Both ships must use test_thruster_std (raw_turn_rate=5.0)."""
        from combat_lab.scenarios.propulsion_scenarios import PROP005_RAW_TURN_RATE
        assert PROP005_RAW_TURN_RATE == 5.0


class TestPROP005PhysicsCalculations:
    """Tests for PROP-005 expected physics values."""

    def test_low_mass_expected_turn_speed(self):
        """Expected turn_speed for low mass ship should match formula."""
        from combat_lab.scenarios.propulsion_scenarios import PROP005_LOW_TURN_SPEED
        # turn_speed = (5.0 * 25000) / 400^1.5 = 125000 / 8000 = 15.625
        expected = (5.0 * 25000) / (400 ** 1.5)
        assert abs(PROP005_LOW_TURN_SPEED - expected) < 0.001
        assert abs(PROP005_LOW_TURN_SPEED - 15.625) < 0.001

    def test_high_mass_expected_turn_speed(self):
        """Expected turn_speed for high mass ship should match formula."""
        from combat_lab.scenarios.propulsion_scenarios import PROP005_HIGH_TURN_SPEED
        # turn_speed = (5.0 * 25000) / 3000^1.5
        # 3000^1.5 = 3000 * sqrt(3000) = 3000 * 54.772 = 164316.77
        # turn_speed = 125000 / 164316.77 = 0.7608
        expected = (5.0 * 25000) / (3000 ** 1.5)
        assert abs(PROP005_HIGH_TURN_SPEED - expected) < 0.001

    def test_high_mass_turn_speed_less_than_low_mass(self):
        """Heavier ships should have lower turn_speed."""
        from combat_lab.scenarios.propulsion_scenarios import (
            PROP005_LOW_TURN_SPEED, PROP005_HIGH_TURN_SPEED
        )
        assert PROP005_HIGH_TURN_SPEED < PROP005_LOW_TURN_SPEED

    def test_expected_ratio_is_correct(self):
        """Expected turn speed ratio should equal (high_mass/low_mass)^1.5."""
        from combat_lab.scenarios.propulsion_scenarios import PROP005_EXPECTED_RATIO
        # (3000/400)^1.5 = 7.5^1.5 = 7.5 * sqrt(7.5) = 7.5 * 2.7386 = 20.54
        expected = (3000 / 400) ** 1.5
        assert abs(PROP005_EXPECTED_RATIO - expected) < 0.01

    def test_ratio_relates_turn_speeds_correctly(self):
        """Ratio should equal low_turn_speed / high_turn_speed."""
        from combat_lab.scenarios.propulsion_scenarios import (
            PROP005_LOW_TURN_SPEED, PROP005_HIGH_TURN_SPEED, PROP005_EXPECTED_RATIO
        )
        actual_ratio = PROP005_LOW_TURN_SPEED / PROP005_HIGH_TURN_SPEED
        assert abs(actual_ratio - PROP005_EXPECTED_RATIO) < 0.01


class TestPROP005ResultsStorage:
    """Tests for PROP-005 results storage."""

    def test_scenario_has_validate_method(self):
        """Scenario should implement validate() for the new validation system."""
        from combat_lab.scenarios.propulsion_scenarios import PropMassAffectsTurnRateScenario
        scenario = PropMassAffectsTurnRateScenario()
        assert hasattr(scenario, 'validate')
        # validate() is defined on the class, not just inherited as NotImplementedError
        assert 'validate' in type(scenario).__dict__


class TestPROP005TestShipExists:
    """Tests that required test ship files exist."""

    def test_low_mass_ship_file_exists(self):
        """Test_Thruster_Simple.json should exist for low mass ship."""
        import os
        ship_path = os.path.join(
            os.path.dirname(__file__),
            '..', '..', '..', '..', 'combat_lab', 'data', 'ships',
            'Test_Thruster_Simple.json'
        )
        ship_path = os.path.normpath(ship_path)
        assert os.path.exists(ship_path), f"Ship file not found: {ship_path}"

    def test_high_mass_ship_file_exists(self):
        """Test_Thruster_HighMass.json should exist for high mass ship."""
        import os
        ship_path = os.path.join(
            os.path.dirname(__file__),
            '..', '..', '..', '..', 'combat_lab', 'data', 'ships',
            'Test_Thruster_HighMass.json'
        )
        ship_path = os.path.normpath(ship_path)
        assert os.path.exists(ship_path), f"Ship file not found: {ship_path}"
