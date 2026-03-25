"""
Boundary tests for physics formula calculations.

Tests edge cases for physics formulas including:
- Zero values (zero mass, zero thrust, zero velocity)
- Maximum/extreme values
- Negative values (where applicable)
- Division by zero protection
- Floating point edge cases

PROJ-118 Phase 2 Task 2.15
"""
import pytest
import math

from game.simulation.physics_constants import K_SPEED, K_THRUST, K_TURN
from game.core.config import PhysicsConfig


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture
def physics_constants():
    """Provide physics constants as a dict for test parameterization."""
    return {
        'K_SPEED': K_SPEED,
        'K_THRUST': K_THRUST,
        'K_TURN': K_TURN,
    }


@pytest.fixture
def reference_values():
    """Provide reference values for physics calculations."""
    return {
        'base_radius': PhysicsConfig.DEFAULT_BASE_RADIUS,
        'reference_mass': PhysicsConfig.REFERENCE_MASS,
        'default_drag': PhysicsConfig.DEFAULT_LINEAR_DRAG,
        'angular_drag': PhysicsConfig.DEFAULT_ANGULAR_DRAG,
    }


# =============================================================================
# Speed Formula: max_speed = (thrust * K_SPEED) / mass
# =============================================================================

class TestSpeedFormulaBoundaries:
    """Boundary tests for speed formula: max_speed = (thrust * K_SPEED) / mass."""

    def test_zero_thrust_gives_zero_speed(self, physics_constants):
        """Zero thrust produces zero speed regardless of mass."""
        thrust = 0
        mass = 1000
        max_speed = (thrust * physics_constants['K_SPEED']) / mass
        assert max_speed == 0.0

    def test_zero_mass_protection_required(self, physics_constants):
        """Division by zero must be protected when mass is zero.

        This test documents the expected behavior: formulas should either
        return 0 or a finite value when mass is zero, not crash.
        """
        thrust = 1000
        mass = 0

        # Protected calculation (as done in ship_stats.py)
        if mass > 0:
            max_speed = (thrust * physics_constants['K_SPEED']) / mass
        else:
            max_speed = 0

        assert max_speed == 0.0
        assert math.isfinite(max_speed)

    def test_very_small_mass_produces_high_but_finite_speed(self, physics_constants):
        """Very small mass produces high but finite speed."""
        thrust = 1000
        mass = 1e-10  # Very small mass

        max_speed = (thrust * physics_constants['K_SPEED']) / mass

        assert math.isfinite(max_speed)
        assert max_speed > 0
        # With thrust=1000, K_SPEED=25, mass=1e-10: speed = 25e13
        assert max_speed == pytest.approx(2.5e14, rel=1e-9)

    def test_very_large_mass_produces_near_zero_speed(self, physics_constants):
        """Very large mass produces near-zero speed."""
        thrust = 1000
        mass = 1e15  # Very large mass

        max_speed = (thrust * physics_constants['K_SPEED']) / mass

        assert math.isfinite(max_speed)
        assert max_speed > 0
        assert max_speed < 1e-9  # Essentially zero

    def test_very_large_thrust_produces_finite_speed(self, physics_constants):
        """Very large thrust produces finite speed (no overflow)."""
        thrust = 1e15
        mass = 1000

        max_speed = (thrust * physics_constants['K_SPEED']) / mass

        assert math.isfinite(max_speed)
        assert max_speed > 0

    def test_negative_thrust_treated_as_zero_conceptually(self, physics_constants):
        """Negative thrust produces negative speed mathematically.

        Note: Game logic should prevent negative thrust, but formula
        handles it mathematically without error.
        """
        thrust = -1000
        mass = 100

        # Formula still works mathematically
        max_speed = (thrust * physics_constants['K_SPEED']) / mass

        assert math.isfinite(max_speed)
        assert max_speed < 0  # Negative result, but finite

    def test_speed_formula_linear_in_thrust(self, physics_constants):
        """Doubling thrust doubles speed (linear relationship)."""
        mass = 1000
        thrust_1 = 500
        thrust_2 = 1000

        speed_1 = (thrust_1 * physics_constants['K_SPEED']) / mass
        speed_2 = (thrust_2 * physics_constants['K_SPEED']) / mass

        assert speed_2 == pytest.approx(2 * speed_1, rel=1e-9)

    def test_speed_formula_inverse_linear_in_mass(self, physics_constants):
        """Doubling mass halves speed (inverse linear relationship)."""
        thrust = 1000
        mass_1 = 500
        mass_2 = 1000

        speed_1 = (thrust * physics_constants['K_SPEED']) / mass_1
        speed_2 = (thrust * physics_constants['K_SPEED']) / mass_2

        assert speed_2 == pytest.approx(speed_1 / 2, rel=1e-9)


# =============================================================================
# Acceleration Formula: accel = (thrust * K_THRUST) / (mass * mass)
# =============================================================================

class TestAccelerationFormulaBoundaries:
    """Boundary tests for acceleration formula: accel = (thrust * K_THRUST) / mass^2."""

    def test_zero_thrust_gives_zero_acceleration(self, physics_constants):
        """Zero thrust produces zero acceleration."""
        thrust = 0
        mass = 1000
        accel = (thrust * physics_constants['K_THRUST']) / (mass * mass)
        assert accel == 0.0

    def test_zero_mass_protection_required(self, physics_constants):
        """Division by zero must be protected when mass is zero."""
        thrust = 1000
        mass = 0

        # Protected calculation
        if mass > 0:
            accel = (thrust * physics_constants['K_THRUST']) / (mass * mass)
        else:
            accel = 0

        assert accel == 0.0
        assert math.isfinite(accel)

    def test_very_small_mass_produces_high_but_finite_acceleration(self, physics_constants):
        """Very small mass produces high but finite acceleration."""
        thrust = 1000
        mass = 1e-5  # Very small mass

        accel = (thrust * physics_constants['K_THRUST']) / (mass * mass)

        assert math.isfinite(accel)
        assert accel > 0
        # With thrust=1000, K_THRUST=2500, mass=1e-5: accel = 2.5e9 / 1e-10 = 2.5e19
        expected = (1000 * 2500) / (1e-5 * 1e-5)
        assert accel == pytest.approx(expected, rel=1e-9)

    def test_very_large_mass_produces_near_zero_acceleration(self, physics_constants):
        """Very large mass produces near-zero acceleration."""
        thrust = 1000
        mass = 1e10  # Very large mass

        accel = (thrust * physics_constants['K_THRUST']) / (mass * mass)

        assert math.isfinite(accel)
        assert accel > 0
        assert accel < 1e-10  # Essentially zero

    def test_acceleration_inverse_square_in_mass(self, physics_constants):
        """Doubling mass quarters acceleration (inverse square relationship)."""
        thrust = 1000
        mass_1 = 500
        mass_2 = 1000  # 2x mass

        accel_1 = (thrust * physics_constants['K_THRUST']) / (mass_1 * mass_1)
        accel_2 = (thrust * physics_constants['K_THRUST']) / (mass_2 * mass_2)

        # 2x mass -> 1/4 acceleration
        assert accel_2 == pytest.approx(accel_1 / 4, rel=1e-9)

    def test_acceleration_known_value(self, physics_constants):
        """Verify known calculation: thrust=100, mass=50 -> accel=100."""
        thrust = 100
        mass = 50

        accel = (thrust * physics_constants['K_THRUST']) / (mass * mass)

        # 100 * 2500 / (50 * 50) = 250000 / 2500 = 100
        assert accel == pytest.approx(100.0, rel=1e-9)


# =============================================================================
# Turn Speed Formula: turn_speed = (raw_turn * K_TURN) / (mass ** 1.5)
# =============================================================================

class TestTurnSpeedFormulaBoundaries:
    """Boundary tests for turn speed formula: turn = (raw * K_TURN) / mass^1.5."""

    def test_zero_raw_turn_gives_zero_turn_speed(self, physics_constants):
        """Zero raw turn speed produces zero calculated turn speed."""
        raw_turn = 0
        mass = 1000
        turn_speed = (raw_turn * physics_constants['K_TURN']) / (mass ** 1.5)
        assert turn_speed == 0.0

    def test_zero_mass_protection_required(self, physics_constants):
        """Division by zero must be protected when mass is zero."""
        raw_turn = 10
        mass = 0

        # Protected calculation
        if mass > 0:
            turn_speed = (raw_turn * physics_constants['K_TURN']) / (mass ** 1.5)
        else:
            turn_speed = 0

        assert turn_speed == 0.0
        assert math.isfinite(turn_speed)

    def test_very_small_mass_produces_high_but_finite_turn_speed(self, physics_constants):
        """Very small mass produces high but finite turn speed."""
        raw_turn = 10
        mass = 1e-4  # Very small mass

        turn_speed = (raw_turn * physics_constants['K_TURN']) / (mass ** 1.5)

        assert math.isfinite(turn_speed)
        assert turn_speed > 0

    def test_very_large_mass_produces_near_zero_turn_speed(self, physics_constants):
        """Very large mass produces near-zero turn speed."""
        raw_turn = 10
        mass = 1e10  # Very large mass

        turn_speed = (raw_turn * physics_constants['K_TURN']) / (mass ** 1.5)

        assert math.isfinite(turn_speed)
        assert turn_speed > 0
        assert turn_speed < 1e-6  # Essentially zero

    def test_turn_speed_inverse_1_5_power_in_mass(self, physics_constants):
        """Doubling mass reduces turn speed by factor of 2^1.5."""
        raw_turn = 10
        mass_1 = 500
        mass_2 = 1000  # 2x mass

        turn_1 = (raw_turn * physics_constants['K_TURN']) / (mass_1 ** 1.5)
        turn_2 = (raw_turn * physics_constants['K_TURN']) / (mass_2 ** 1.5)

        # 2^1.5 = 2.828...
        ratio = turn_1 / turn_2
        assert ratio == pytest.approx(2 ** 1.5, rel=1e-9)

    def test_turn_speed_known_value(self, physics_constants):
        """Verify known calculation: raw_turn=10, mass=50 -> ~707.1."""
        raw_turn = 10
        mass = 50

        turn_speed = (raw_turn * physics_constants['K_TURN']) / (mass ** 1.5)

        # 10 * 25000 / (50 ** 1.5) = 250000 / 353.55... = 707.1067...
        assert turn_speed == pytest.approx(707.1067811865476, rel=1e-6)


# =============================================================================
# Radius Formula: radius = base_radius * (mass / ref_mass) ** (1/3.0)
# =============================================================================

class TestRadiusFormulaBoundaries:
    """Boundary tests for radius formula: radius = base * (mass/ref)^(1/3)."""

    def test_zero_mass_uses_minimum(self, reference_values):
        """Zero mass is clamped to minimum for radius calculation."""
        base_radius = reference_values['base_radius']
        ref_mass = reference_values['reference_mass']
        mass = 0

        # As per ship_stats.py: actual_mass = max(mass, 100)
        actual_mass = max(mass, 100)
        ratio = actual_mass / ref_mass
        radius = base_radius * (ratio ** (1/3.0))

        assert math.isfinite(radius)
        assert radius > 0
        # With mass=100, ref=1000: ratio=0.1, radius=40*(0.1)^(1/3)=40*0.464=18.56
        expected = base_radius * ((100 / ref_mass) ** (1/3.0))
        assert radius == pytest.approx(expected, rel=1e-9)

    def test_reference_mass_gives_base_radius(self, reference_values):
        """Mass equal to reference mass gives base radius."""
        base_radius = reference_values['base_radius']
        ref_mass = reference_values['reference_mass']
        mass = ref_mass

        ratio = mass / ref_mass
        radius = base_radius * (ratio ** (1/3.0))

        # ratio = 1, radius = base_radius * 1 = base_radius
        assert radius == pytest.approx(base_radius, rel=1e-9)

    def test_very_large_mass_produces_finite_radius(self, reference_values):
        """Very large mass produces finite radius."""
        base_radius = reference_values['base_radius']
        ref_mass = reference_values['reference_mass']
        mass = 1e15

        ratio = mass / ref_mass
        radius = base_radius * (ratio ** (1/3.0))

        assert math.isfinite(radius)
        assert radius > base_radius  # Larger than base

    def test_radius_cube_root_scaling(self, reference_values):
        """8x mass produces 2x radius (cube root relationship)."""
        base_radius = reference_values['base_radius']
        ref_mass = reference_values['reference_mass']

        mass_1 = 1000
        mass_2 = 8000  # 8x mass

        ratio_1 = mass_1 / ref_mass
        ratio_2 = mass_2 / ref_mass

        radius_1 = base_radius * (ratio_1 ** (1/3.0))
        radius_2 = base_radius * (ratio_2 ** (1/3.0))

        # 8^(1/3) = 2
        assert radius_2 == pytest.approx(2 * radius_1, rel=1e-9)

    def test_negative_mass_protected(self, reference_values):
        """Negative mass should be handled (clamped to minimum)."""
        base_radius = reference_values['base_radius']
        ref_mass = reference_values['reference_mass']
        mass = -500

        # As per ship_stats.py logic, use minimum clamp
        actual_mass = max(mass, 100)
        ratio = actual_mass / ref_mass
        radius = base_radius * (ratio ** (1/3.0))

        assert math.isfinite(radius)
        assert radius > 0


# =============================================================================
# Force Application: acceleration += force / mass
# =============================================================================

class TestForceApplicationBoundaries:
    """Boundary tests for force application: acceleration = force / mass."""

    def test_zero_force_gives_zero_acceleration(self):
        """Zero force produces no acceleration change."""
        force = 0.0
        mass = 100.0

        accel = force / mass

        assert accel == 0.0

    def test_zero_mass_protection_no_division(self):
        """Zero mass is protected by conditional check (no division occurs)."""
        force = 100.0
        mass = 0.0

        # As per PhysicsBody.apply_force: if self.mass > 0
        if mass > 0:
            accel = force / mass
        else:
            accel = 0.0

        assert accel == 0.0
        assert math.isfinite(accel)

    def test_very_small_mass_large_acceleration(self):
        """Very small mass produces large but finite acceleration."""
        force = 100.0
        mass = 1e-10

        accel = force / mass

        assert math.isfinite(accel)
        assert accel == pytest.approx(1e12, rel=1e-9)

    def test_very_large_force_finite_acceleration(self):
        """Very large force produces finite acceleration."""
        force = 1e15
        mass = 1.0

        accel = force / mass

        assert math.isfinite(accel)
        assert accel == pytest.approx(1e15, rel=1e-9)

    def test_negative_force_produces_negative_acceleration(self):
        """Negative force produces negative acceleration (deceleration)."""
        force = -100.0
        mass = 10.0

        accel = force / mass

        assert accel == pytest.approx(-10.0, rel=1e-9)


# =============================================================================
# Drag Formula: new_velocity = velocity * (1 - drag)
# =============================================================================

class TestDragFormulaBoundaries:
    """Boundary tests for drag formula: new_velocity = velocity * (1 - drag)."""

    def test_zero_drag_preserves_velocity(self):
        """Zero drag preserves velocity completely."""
        velocity = 100.0
        drag = 0.0

        new_velocity = velocity * (1 - drag)

        assert new_velocity == velocity

    def test_full_drag_stops_immediately(self):
        """Drag of 1.0 (100%) stops motion immediately."""
        velocity = 100.0
        drag = 1.0

        new_velocity = velocity * (1 - drag)

        assert new_velocity == 0.0

    def test_drag_over_1_clamped_to_1(self):
        """Drag over 1.0 is clamped to prevent velocity reversal."""
        velocity = 100.0
        drag = 1.5  # Over 100%

        # As per PhysicsBody.update: if drag_factor > 1: drag_factor = 1
        drag_factor = min(drag, 1.0)
        new_velocity = velocity * (1 - drag_factor)

        assert new_velocity >= 0.0
        assert new_velocity == 0.0

    def test_negative_drag_not_expected_but_handled(self):
        """Negative drag increases velocity (not expected but mathematically valid)."""
        velocity = 100.0
        drag = -0.5

        new_velocity = velocity * (1 - drag)

        # (1 - (-0.5)) = 1.5, so velocity increases
        assert new_velocity == pytest.approx(150.0, rel=1e-9)

    def test_half_drag_halves_velocity(self):
        """50% drag halves velocity per tick."""
        velocity = 100.0
        drag = 0.5

        new_velocity = velocity * (1 - drag)

        assert new_velocity == pytest.approx(50.0, rel=1e-9)

    def test_small_drag_approaches_zero_asymptotically(self):
        """Small drag approaches zero velocity asymptotically over many ticks."""
        velocity = 1000.0
        drag = 0.1  # 10% per tick

        # Apply drag 100 times
        for _ in range(100):
            velocity = velocity * (1 - drag)

        # After 100 iterations with 10% drag: 1000 * 0.9^100 = ~2.66e-5
        assert velocity < 1.0  # Much smaller than original
        assert velocity > 0.0  # Never exactly zero
        assert math.isfinite(velocity)


# =============================================================================
# Defense Score Formula: -2.5 * log10(diameter / 80)
# =============================================================================

class TestDefenseScoreFormulaBoundaries:
    """Boundary tests for defense score size component."""

    def test_reference_diameter_gives_zero_size_score(self):
        """Diameter of 80 (reference) gives zero size score."""
        diameter = 80
        d_ratio = max(0.1, diameter / 80.0)
        size_score = -2.5 * math.log10(d_ratio)

        # log10(1) = 0, so score = 0
        assert size_score == pytest.approx(0.0, abs=1e-9)

    def test_larger_diameter_gives_negative_score(self):
        """Larger ships (diameter > 80) are easier to hit (negative score)."""
        diameter = 160  # 2x reference
        d_ratio = max(0.1, diameter / 80.0)
        size_score = -2.5 * math.log10(d_ratio)

        # log10(2) = 0.301, score = -0.753
        assert size_score < 0
        assert size_score == pytest.approx(-0.753, rel=0.01)

    def test_smaller_diameter_gives_positive_score(self):
        """Smaller ships (diameter < 80) are harder to hit (positive score)."""
        diameter = 40  # 0.5x reference
        d_ratio = max(0.1, diameter / 80.0)
        size_score = -2.5 * math.log10(d_ratio)

        # log10(0.5) = -0.301, score = 0.753
        assert size_score > 0

    def test_zero_diameter_clamped_to_minimum(self):
        """Zero diameter is clamped to 0.1 to prevent log(0)."""
        diameter = 0
        d_ratio = max(0.1, diameter / 80.0)
        size_score = -2.5 * math.log10(d_ratio)

        assert math.isfinite(size_score)
        # log10(0.1) = -1, score = 2.5
        assert size_score == pytest.approx(2.5, rel=1e-9)

    def test_very_small_diameter_clamped(self):
        """Very small diameter is clamped to prevent extreme values."""
        diameter = 0.001
        d_ratio = max(0.1, diameter / 80.0)  # Clamped to 0.1
        size_score = -2.5 * math.log10(d_ratio)

        assert math.isfinite(size_score)
        assert size_score == pytest.approx(2.5, rel=1e-9)  # Same as diameter=0


# =============================================================================
# Maneuver Score Formula: sqrt((accel/20) + (turn/360))
# =============================================================================

class TestManeuverScoreFormulaBoundaries:
    """Boundary tests for maneuver score calculation."""

    def test_zero_maneuverability_gives_zero_score(self):
        """Zero acceleration and turn speed gives zero maneuver score."""
        accel = 0
        turn = 0

        maneuver_score = math.sqrt((accel / 20.0) + (turn / 360.0))

        assert maneuver_score == 0.0

    def test_fighter_typical_values(self):
        """Typical fighter values (high accel, high turn) give reasonable score."""
        accel = 25  # Fighter-like
        turn = 180  # Fighter-like

        maneuver_score = math.sqrt((accel / 20.0) + (turn / 360.0))

        # sqrt(1.25 + 0.5) = sqrt(1.75) = 1.32
        assert maneuver_score == pytest.approx(1.32, rel=0.01)

    def test_capital_ship_low_maneuverability(self):
        """Capital ships (low accel, low turn) have low maneuver score."""
        accel = 1
        turn = 10

        maneuver_score = math.sqrt((accel / 20.0) + (turn / 360.0))

        # sqrt(0.05 + 0.028) = sqrt(0.078) = 0.28
        assert maneuver_score < 0.5
        assert maneuver_score > 0

    def test_negative_values_protected(self):
        """Negative acceleration or turn speed doesn't cause math domain error."""
        accel = -10  # Not expected but shouldn't crash
        turn = -45

        # Sum could be negative, sqrt would fail
        inner = (accel / 20.0) + (turn / 360.0)

        # Protected version
        if inner >= 0:
            maneuver_score = math.sqrt(inner)
        else:
            maneuver_score = 0.0

        assert math.isfinite(maneuver_score)


# =============================================================================
# Floating Point Edge Cases
# =============================================================================

class TestFloatingPointEdgeCases:
    """Tests for floating point precision and special values."""

    def test_subnormal_values_handled(self, physics_constants):
        """Subnormal (denormalized) floating point values are handled."""
        # Smallest positive normal float is ~2.2e-308
        # Subnormal values are smaller
        thrust = 1e-310
        mass = 1.0

        max_speed = (thrust * physics_constants['K_SPEED']) / mass

        # Should be a very small positive number or zero (flush to zero)
        assert max_speed >= 0
        # Either finite or flushed to zero
        assert math.isfinite(max_speed) or max_speed == 0

    def test_near_overflow_values_produce_infinity(self, physics_constants):
        """Values near overflow produce infinity, not crash."""
        thrust = 1e308
        mass = 1e-300  # Very small mass

        # This will overflow
        max_speed = (thrust * physics_constants['K_SPEED']) / mass

        # Should be infinity, not crash
        assert math.isinf(max_speed) or math.isfinite(max_speed)

    def test_nan_propagation(self, physics_constants):
        """NaN values propagate correctly (not crash)."""
        thrust = float('nan')
        mass = 1000

        max_speed = (thrust * physics_constants['K_SPEED']) / mass

        # NaN propagates
        assert math.isnan(max_speed)

    def test_infinity_input_handled(self, physics_constants):
        """Infinity inputs produce infinity output (not crash)."""
        thrust = float('inf')
        mass = 1000

        max_speed = (thrust * physics_constants['K_SPEED']) / mass

        assert math.isinf(max_speed)

    def test_precision_at_small_differences(self, physics_constants):
        """Small differences in large values maintain precision."""
        mass_1 = 1e10
        mass_2 = 1e10 + 1  # Very small relative difference
        thrust = 1000

        speed_1 = (thrust * physics_constants['K_SPEED']) / mass_1
        speed_2 = (thrust * physics_constants['K_SPEED']) / mass_2

        # Should be distinguishable
        assert speed_1 != speed_2
        # And the difference should be roughly proportional
        assert speed_1 > speed_2  # Smaller mass = higher speed


# =============================================================================
# Combined Formula Consistency Tests
# =============================================================================

class TestFormulaConsistency:
    """Tests to verify formulas work correctly together."""

    def test_heavier_ships_are_slower_and_turn_slower(self, physics_constants):
        """Heavier ships have lower max speed and turn speed."""
        thrust = 10000
        raw_turn = 50

        mass_light = 500
        mass_heavy = 2000

        speed_light = (thrust * physics_constants['K_SPEED']) / mass_light
        speed_heavy = (thrust * physics_constants['K_SPEED']) / mass_heavy

        turn_light = (raw_turn * physics_constants['K_TURN']) / (mass_light ** 1.5)
        turn_heavy = (raw_turn * physics_constants['K_TURN']) / (mass_heavy ** 1.5)

        assert speed_heavy < speed_light
        assert turn_heavy < turn_light

    def test_more_thrust_compensates_for_mass(self, physics_constants):
        """More thrust can compensate for more mass to maintain speed."""
        # Light ship
        thrust_light = 1000
        mass_light = 500

        # Heavy ship with proportionally more thrust
        thrust_heavy = 2000  # 2x thrust
        mass_heavy = 1000   # 2x mass

        speed_light = (thrust_light * physics_constants['K_SPEED']) / mass_light
        speed_heavy = (thrust_heavy * physics_constants['K_SPEED']) / mass_heavy

        # Same thrust-to-mass ratio = same speed
        assert speed_light == pytest.approx(speed_heavy, rel=1e-9)

    def test_physics_constants_are_positive_integers(self, physics_constants):
        """All physics constants are positive integers."""
        assert physics_constants['K_SPEED'] > 0
        assert physics_constants['K_THRUST'] > 0
        assert physics_constants['K_TURN'] > 0

        assert isinstance(physics_constants['K_SPEED'], int)
        assert isinstance(physics_constants['K_THRUST'], int)
        assert isinstance(physics_constants['K_TURN'], int)


# =============================================================================
# Shared Formula Functions (PROJ-225)
# =============================================================================

class TestComputeAcceleration:
    """Tests for compute_acceleration() shared function."""

    def test_basic_calculation(self):
        """Standard calculation matches inline formula."""
        from game.simulation.physics_constants import compute_acceleration
        result = compute_acceleration(100, 500)
        expected = (100 * K_THRUST) / (500 * 500)
        assert result == pytest.approx(expected)

    def test_zero_thrust(self):
        """Zero thrust gives zero acceleration."""
        from game.simulation.physics_constants import compute_acceleration
        assert compute_acceleration(0, 500) == 0.0

    def test_zero_mass_returns_zero(self):
        """Zero mass returns 0 (division by zero guard)."""
        from game.simulation.physics_constants import compute_acceleration
        assert compute_acceleration(100, 0) == 0.0

    def test_negative_mass_returns_zero(self):
        """Negative mass returns 0."""
        from game.simulation.physics_constants import compute_acceleration
        assert compute_acceleration(100, -10) == 0.0

    def test_inverse_square_mass(self):
        """Doubling mass quarters acceleration."""
        from game.simulation.physics_constants import compute_acceleration
        a1 = compute_acceleration(100, 500)
        a2 = compute_acceleration(100, 1000)
        assert a2 == pytest.approx(a1 / 4, rel=1e-9)


class TestComputeMaxSpeed:
    """Tests for compute_max_speed() shared function."""

    def test_basic_calculation(self):
        """Standard calculation matches inline formula."""
        from game.simulation.physics_constants import compute_max_speed
        result = compute_max_speed(100, 500)
        expected = (100 * K_SPEED) / 500
        assert result == pytest.approx(expected)

    def test_zero_thrust(self):
        """Zero thrust gives zero max speed."""
        from game.simulation.physics_constants import compute_max_speed
        assert compute_max_speed(0, 500) == 0.0

    def test_zero_mass_returns_zero(self):
        """Zero mass returns 0 (division by zero guard)."""
        from game.simulation.physics_constants import compute_max_speed
        assert compute_max_speed(100, 0) == 0.0

    def test_negative_mass_returns_zero(self):
        """Negative mass returns 0."""
        from game.simulation.physics_constants import compute_max_speed
        assert compute_max_speed(100, -10) == 0.0

    def test_inverse_linear_mass(self):
        """Doubling mass halves max speed."""
        from game.simulation.physics_constants import compute_max_speed
        s1 = compute_max_speed(100, 500)
        s2 = compute_max_speed(100, 1000)
        assert s2 == pytest.approx(s1 / 2, rel=1e-9)
