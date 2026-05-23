"""
Unit tests for physics_constants.py.

Tests the physics constants and validates the documented formulas
produce expected results.
"""
import pytest

from game.simulation.physics_constants import (
    K_SPEED, K_THRUST, K_TURN,
    FORMULA_MAX_SPEED, FORMULA_ACCELERATION, FORMULA_TURN_SPEED
)


class TestPhysicsConstants:
    """Tests for physics constants values."""

    def test_k_speed_is_positive_int(self):
        """K_SPEED is a positive integer."""
        assert isinstance(K_SPEED, int)
        assert K_SPEED > 0

    def test_k_thrust_is_positive_int(self):
        """K_THRUST is a positive integer."""
        assert isinstance(K_THRUST, int)
        assert K_THRUST > 0

    def test_k_turn_is_positive_int(self):
        """K_TURN is a positive integer."""
        assert isinstance(K_TURN, int)
        assert K_TURN > 0


class TestSpeedFormula:
    """Tests for speed calculation formula."""

    def test_speed_formula_known_values(self):
        """Verify speed formula: (100 thrust * 25) / 50 mass = 50 speed."""
        thrust = 100
        mass = 50
        expected_speed = (thrust * K_SPEED) / mass
        assert expected_speed == 50.0

    def test_speed_inverse_mass_scaling(self):
        """Double mass halves speed."""
        thrust = 100
        mass_light = 50
        mass_heavy = 100

        speed_light = (thrust * K_SPEED) / mass_light
        speed_heavy = (thrust * K_SPEED) / mass_heavy

        assert speed_heavy == speed_light / 2


class TestAccelerationFormula:
    """Tests for acceleration calculation formula."""

    def test_acceleration_formula_known_values(self):
        """Verify accel formula: (100 thrust * 2500) / (50^2) = 100 accel."""
        thrust = 100
        mass = 50
        expected_accel = (thrust * K_THRUST) / (mass ** 2)
        assert expected_accel == 100.0


class TestTurnFormula:
    """Tests for turn speed calculation formula."""

    def test_turn_formula_known_values(self):
        """Verify turn formula produces expected result."""
        raw_turn = 10
        mass = 50
        # Formula: turn_speed = (raw_turn_speed * K_TURN) / (mass ** 1.5)
        expected_turn = (raw_turn * K_TURN) / (mass ** 1.5)
        # 10 * 25000 / (50 ** 1.5) = 250000 / 353.55... = ~707.1
        assert abs(expected_turn - 707.1067811865476) < 0.001

    def test_turn_heavier_ships_turn_slower(self):
        """Higher mass results in lower turn speed."""
        raw_turn = 10
        mass_light = 50
        mass_heavy = 100

        turn_light = (raw_turn * K_TURN) / (mass_light ** 1.5)
        turn_heavy = (raw_turn * K_TURN) / (mass_heavy ** 1.5)

        assert turn_heavy < turn_light


class TestFormulaDocumentation:
    """Tests that formula documentation strings exist."""

    # PROJ-480 Task 1.4: parametrize the 3 docstring-substring assertions.
    # Each formula has its own non-overlapping set of required substrings;
    # they are kept distinct so a missing substring fails its own param case.
    @pytest.mark.parametrize(
        "formula, expected_substrings",
        [
            (FORMULA_MAX_SPEED, ("max_speed", "K_SPEED", "mass")),
            (FORMULA_ACCELERATION, ("acceleration", "K_THRUST")),
            (FORMULA_TURN_SPEED, ("turn_speed", "K_TURN")),
        ],
        ids=["max_speed", "acceleration", "turn_speed"],
    )
    def test_formula_documented(self, formula, expected_substrings):
        for substring in expected_substrings:
            assert substring in formula, (
                f"Expected '{substring}' in formula docstring"
            )
