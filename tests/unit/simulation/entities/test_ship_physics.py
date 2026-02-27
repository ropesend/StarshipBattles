"""
Unit tests for ShipPhysicsMixin.

Tests the physics calculations in isolation using a mock host class
to verify behavior without Ship class dependencies.
"""
import pytest
from unittest.mock import Mock, patch

from game.simulation.entities.ship_physics import ShipPhysicsMixin
from game.engine.physics import PhysicsBody
from game.core.math import Vector2
from game.simulation.physics_constants import K_SPEED, K_THRUST


class MockShipWithPhysics(PhysicsBody, ShipPhysicsMixin):
    """
    Minimal mock ship for testing ShipPhysicsMixin in isolation.

    Provides all required attributes that the mixin expects.
    """

    def __init__(self, x=0, y=0, angle=0):
        super().__init__(x, y, angle)
        # Required attributes for ShipPhysicsMixin
        self.current_speed = 0.0
        self.max_speed = 100.0
        self.acceleration_rate = 1.0
        self.turn_speed = 100.0  # Degrees per second
        self.is_thrusting = False
        self.target_speed = 0.0
        self.engine_throttle = 1.0
        self.turn_throttle = 1.0
        # Fuel-related
        self.current_fuel = 100.0
        # Mass for physics calculations
        self.mass = 100.0
        # Total thrust value
        self._total_thrust = 1000.0

    def get_total_ability_value(self, ability_type, operational_only=False):
        """Mock ability lookup - returns thrust value."""
        if ability_type == 'CombatPropulsion':
            return self._total_thrust
        return 0.0


class TestShipPhysicsMixinThrust:
    """Tests for thrust_forward method."""

    def test_thrust_forward_sets_flag(self):
        """thrust_forward() should set is_thrusting to True."""
        ship = MockShipWithPhysics()
        assert ship.is_thrusting is False

        ship.thrust_forward()

        assert ship.is_thrusting is True

    def test_thrust_forward_multiple_calls_stays_true(self):
        """Multiple thrust_forward() calls should keep flag True."""
        ship = MockShipWithPhysics()

        ship.thrust_forward()
        ship.thrust_forward()
        ship.thrust_forward()

        assert ship.is_thrusting is True


class TestShipPhysicsMixinRotation:
    """Tests for rotate method."""

    def test_rotate_left_decreases_angle(self):
        """Rotating left (direction=-1) should decrease angle."""
        ship = MockShipWithPhysics(angle=90)
        initial_angle = ship.angle

        ship.rotate(-1)

        assert ship.angle < initial_angle

    def test_rotate_right_increases_angle(self):
        """Rotating right (direction=+1) should increase angle."""
        ship = MockShipWithPhysics(angle=90)
        initial_angle = ship.angle

        ship.rotate(1)

        assert ship.angle > initial_angle

    def test_rotate_uses_turn_speed(self):
        """Rotation amount should be turn_speed / 100.0 per call."""
        ship = MockShipWithPhysics(angle=0)
        ship.turn_speed = 50.0
        ship.turn_throttle = 1.0

        ship.rotate(1)

        expected = 50.0 / 100.0  # 0.5 degrees
        assert ship.angle == pytest.approx(expected, abs=0.001)

    def test_rotate_respects_turn_throttle(self):
        """Rotation should scale with turn_throttle."""
        ship = MockShipWithPhysics(angle=0)
        ship.turn_speed = 100.0
        ship.turn_throttle = 0.5

        ship.rotate(1)

        expected = (100.0 * 0.5) / 100.0  # 0.5 degrees
        assert ship.angle == pytest.approx(expected, abs=0.001)

    def test_rotate_with_zero_turn_speed(self):
        """Zero turn_speed should result in no rotation."""
        ship = MockShipWithPhysics(angle=45)
        ship.turn_speed = 0.0

        ship.rotate(1)

        assert ship.angle == pytest.approx(45.0, abs=0.001)

    # DELETED: test_rotate_without_turn_throttle_attribute
    # Reason: Duck typing replaced with explicit protocols in PROJ-190.
    # Ships must now have turn_throttle attribute.


class TestUpdatePhysicsMovementThrusting:
    """Tests for update_physics_movement when thrusting."""

    def test_accelerates_when_thrusting(self):
        """Speed should increase when thrusting with operational engines."""
        ship = MockShipWithPhysics()
        ship.current_speed = 0.0
        ship.is_thrusting = True
        ship._total_thrust = 1000.0
        ship.mass = 100.0

        ship.update_physics_movement()

        assert ship.current_speed > 0.0

    def test_acceleration_formula(self):
        """Verify acceleration follows: (thrust * K_THRUST) / mass^2."""
        ship = MockShipWithPhysics()
        ship.current_speed = 0.0
        ship.is_thrusting = True
        ship._total_thrust = 1000.0
        ship.mass = 100.0
        ship.engine_throttle = 1.0

        expected_accel = (ship._total_thrust * K_THRUST) / (ship.mass * ship.mass)
        expected_max_speed = (ship._total_thrust * K_SPEED) / ship.mass
        # At throttle 1.0, target is max_speed
        # Since we start at 0, diff > step, so we get +step

        ship.update_physics_movement()

        assert ship.current_speed == pytest.approx(expected_accel, abs=0.001)

    def test_max_speed_formula(self):
        """Verify max speed follows: (thrust * K_SPEED) / mass."""
        ship = MockShipWithPhysics()
        ship._total_thrust = 1000.0
        ship.mass = 100.0
        ship.engine_throttle = 1.0

        expected_max_speed = (ship._total_thrust * K_SPEED) / ship.mass

        # Run many updates to reach max speed
        for _ in range(1000):
            ship.is_thrusting = True
            ship.update_physics_movement()

        assert ship.current_speed == pytest.approx(expected_max_speed, abs=0.01)

    def test_throttle_affects_target_speed(self):
        """Engine throttle should scale target speed."""
        ship = MockShipWithPhysics()
        ship._total_thrust = 1000.0
        ship.mass = 100.0
        ship.engine_throttle = 0.5

        expected_max_speed = (ship._total_thrust * K_SPEED) / ship.mass
        expected_target = expected_max_speed * 0.5

        # Run many updates to reach target speed
        for _ in range(1000):
            ship.is_thrusting = True
            ship.update_physics_movement()

        assert ship.current_speed == pytest.approx(expected_target, abs=0.01)

    # DELETED: test_missing_engine_throttle_defaults_to_one
    # Reason: Duck typing replaced with explicit protocols in PROJ-190.
    # Ships must now have engine_throttle attribute.

    def test_zero_thrust_no_acceleration(self):
        """Zero thrust should result in no acceleration."""
        ship = MockShipWithPhysics()
        ship.current_speed = 0.0
        ship.is_thrusting = True
        ship._total_thrust = 0.0
        ship.mass = 100.0

        ship.update_physics_movement()

        assert ship.current_speed == 0.0

    def test_zero_mass_no_division_error(self):
        """Zero mass should not cause division by zero."""
        ship = MockShipWithPhysics()
        ship.current_speed = 0.0
        ship.is_thrusting = True
        ship._total_thrust = 1000.0
        ship.mass = 0.0

        # Should not raise exception
        ship.update_physics_movement()

        # Speed unchanged when mass is 0
        assert ship.current_speed == 0.0

    def test_thrusting_flag_reset_after_update(self):
        """is_thrusting should be reset to False after update."""
        ship = MockShipWithPhysics()
        ship.is_thrusting = True

        ship.update_physics_movement()

        assert ship.is_thrusting is False

    def test_speed_steps_toward_target_gradually(self):
        """Speed should approach target in steps, not jump instantly."""
        ship = MockShipWithPhysics()
        ship.current_speed = 0.0
        ship._total_thrust = 10000.0  # Higher thrust for more visible difference
        ship.mass = 1000.0  # Higher mass to slow down acceleration

        expected_max_speed = (ship._total_thrust * K_SPEED) / ship.mass
        expected_accel = (ship._total_thrust * K_THRUST) / (ship.mass * ship.mass)

        ship.is_thrusting = True
        ship.update_physics_movement()

        # After one tick, speed should be acceleration step (not at max yet)
        assert ship.current_speed < expected_max_speed
        assert ship.current_speed == pytest.approx(expected_accel, abs=0.001)

    def test_reaches_exact_target_when_close(self):
        """When diff <= step, speed should snap to target exactly."""
        ship = MockShipWithPhysics()
        ship._total_thrust = 1000.0
        ship.mass = 100.0
        ship.engine_throttle = 1.0

        expected_max_speed = (ship._total_thrust * K_SPEED) / ship.mass
        expected_accel = (ship._total_thrust * K_THRUST) / (ship.mass * ship.mass)

        # Set speed just below target by less than one step
        ship.current_speed = expected_max_speed - (expected_accel * 0.5)
        ship.is_thrusting = True

        ship.update_physics_movement()

        assert ship.current_speed == pytest.approx(expected_max_speed, abs=0.001)


class TestUpdatePhysicsMovementCoasting:
    """Tests for update_physics_movement when not thrusting (coasting/decelerating)."""

    def test_decelerates_when_not_thrusting(self):
        """Speed should decrease when not thrusting."""
        ship = MockShipWithPhysics()
        ship.current_speed = 50.0
        ship.is_thrusting = False
        ship.acceleration_rate = 5.0

        ship.update_physics_movement()

        assert ship.current_speed < 50.0

    def test_deceleration_uses_acceleration_rate(self):
        """Deceleration step should equal acceleration_rate."""
        ship = MockShipWithPhysics()
        ship.current_speed = 50.0
        ship.is_thrusting = False
        ship.acceleration_rate = 5.0

        ship.update_physics_movement()

        assert ship.current_speed == pytest.approx(45.0, abs=0.001)

    def test_stops_at_zero_speed(self):
        """Speed should stop at zero, not go negative."""
        ship = MockShipWithPhysics()
        ship.current_speed = 3.0
        ship.is_thrusting = False
        ship.acceleration_rate = 5.0  # Step larger than remaining speed

        ship.update_physics_movement()

        assert ship.current_speed == 0.0

    def test_sets_target_speed_zero_when_coasting(self):
        """target_speed should be set to 0 when coasting."""
        ship = MockShipWithPhysics()
        ship.current_speed = 50.0
        ship.target_speed = 50.0
        ship.is_thrusting = False

        ship.update_physics_movement()

        assert ship.target_speed == 0.0

    def test_coasting_from_zero_stays_at_zero(self):
        """Ship at rest should stay at rest when not thrusting."""
        ship = MockShipWithPhysics()
        ship.current_speed = 0.0
        ship.is_thrusting = False
        ship.acceleration_rate = 5.0

        ship.update_physics_movement()

        assert ship.current_speed == 0.0


class TestUpdatePhysicsMovementPosition:
    """Tests for position updates in update_physics_movement."""

    def test_position_updates_with_velocity(self):
        """Position should update by velocity each tick."""
        ship = MockShipWithPhysics(x=0, y=0, angle=0)
        ship.current_speed = 10.0
        ship.is_thrusting = False
        ship.acceleration_rate = 0.0  # No deceleration for this test

        ship.update_physics_movement()

        # At angle 0, forward is (1, 0), so position should move in +X
        assert ship.position.x > 0
        assert ship.position.y == pytest.approx(0.0, abs=0.001)

    def test_velocity_set_from_speed_and_heading(self):
        """Velocity should be forward_vector * current_speed after update."""
        ship = MockShipWithPhysics(x=0, y=0, angle=0)
        ship.current_speed = 10.0
        ship.acceleration_rate = 0.0  # No deceleration to keep speed constant

        ship.update_physics_movement()

        # Velocity should match current_speed in the forward direction
        assert ship.velocity.x == pytest.approx(10.0, abs=0.01)
        assert ship.velocity.y == pytest.approx(0.0, abs=0.01)

    def test_velocity_follows_heading_at_90_degrees(self):
        """At angle=90, velocity should point in +Y direction."""
        ship = MockShipWithPhysics(x=0, y=0, angle=90)
        ship.current_speed = 10.0
        ship.acceleration_rate = 0.0  # No deceleration to keep speed constant

        ship.update_physics_movement()

        assert ship.velocity.x == pytest.approx(0.0, abs=0.01)
        assert ship.velocity.y == pytest.approx(10.0, abs=0.01)

    def test_velocity_follows_heading_at_180_degrees(self):
        """At angle=180, velocity should point in -X direction."""
        ship = MockShipWithPhysics(x=0, y=0, angle=180)
        ship.current_speed = 10.0
        ship.acceleration_rate = 0.0  # No deceleration to keep speed constant

        ship.update_physics_movement()

        assert ship.velocity.x == pytest.approx(-10.0, abs=0.01)
        assert ship.velocity.y == pytest.approx(0.0, abs=0.01)

    def test_velocity_follows_heading_at_270_degrees(self):
        """At angle=270, velocity should point in -Y direction."""
        ship = MockShipWithPhysics(x=0, y=0, angle=270)
        ship.current_speed = 10.0
        ship.acceleration_rate = 0.0  # No deceleration to keep speed constant

        ship.update_physics_movement()

        assert ship.velocity.x == pytest.approx(0.0, abs=0.01)
        assert ship.velocity.y == pytest.approx(-10.0, abs=0.01)

    def test_position_accumulates_over_multiple_updates(self):
        """Position should accumulate from multiple updates."""
        ship = MockShipWithPhysics(x=0, y=0, angle=0)
        ship.current_speed = 5.0
        ship.acceleration_rate = 0.0  # No deceleration

        for _ in range(10):
            ship.update_physics_movement()

        # After 10 updates at speed 5 heading right
        assert ship.position.x == pytest.approx(50.0, abs=0.1)


class TestUpdatePhysicsMovementRotation:
    """Tests for rotation updates in update_physics_movement."""

    def test_angle_updates_from_angular_velocity(self):
        """Angle should update by angular_velocity each tick."""
        ship = MockShipWithPhysics(angle=0)
        ship.angular_velocity = 10.0

        ship.update_physics_movement()

        assert ship.angle == pytest.approx(10.0, abs=0.001)

    def test_angular_velocity_reset_after_update(self):
        """angular_velocity should be reset to 0 after update."""
        ship = MockShipWithPhysics()
        ship.angular_velocity = 10.0

        ship.update_physics_movement()

        assert ship.angular_velocity == 0.0

    def test_angle_wraps_at_360(self):
        """Angle should wrap around at 360 degrees."""
        ship = MockShipWithPhysics(angle=350)
        ship.angular_velocity = 20.0

        ship.update_physics_movement()

        # 350 + 20 = 370 -> 10 (modulo 360)
        assert ship.angle == pytest.approx(10.0, abs=0.001)

    def test_angle_wraps_from_zero(self):
        """Angle at 0 with negative velocity should wrap to high angle."""
        ship = MockShipWithPhysics(angle=5)
        ship.angular_velocity = -10.0

        ship.update_physics_movement()

        # 5 - 10 = -5 -> 355 (modulo 360)
        assert ship.angle == pytest.approx(355.0, abs=0.001)

    def test_large_angular_velocity_wraps_correctly(self):
        """Large angular velocity should still wrap correctly."""
        ship = MockShipWithPhysics(angle=0)
        ship.angular_velocity = 720.0  # Two full rotations

        ship.update_physics_movement()

        assert ship.angle == pytest.approx(0.0, abs=0.001)


class TestPhysicsEdgeCases:
    """Edge case tests for ShipPhysicsMixin."""

    def test_very_small_mass(self):
        """Very small mass should result in reaching max speed quickly."""
        ship = MockShipWithPhysics()
        ship.current_speed = 0.0
        ship.is_thrusting = True
        ship._total_thrust = 100.0
        ship.mass = 0.1  # Very small mass

        ship.update_physics_movement()

        # With small mass, acceleration is huge, so ship reaches max speed in one tick
        # Max speed = (thrust * K_SPEED) / mass = (100 * 25) / 0.1 = 25000
        expected_max_speed = (100.0 * K_SPEED) / 0.1
        assert ship.current_speed == pytest.approx(expected_max_speed, abs=0.1)

    def test_very_large_mass(self):
        """Very large mass should result in low acceleration."""
        ship = MockShipWithPhysics()
        ship.current_speed = 0.0
        ship.is_thrusting = True
        ship._total_thrust = 1000.0
        ship.mass = 10000.0  # Very large mass

        ship.update_physics_movement()

        # With large mass, acceleration should be very small
        expected_accel = (1000.0 * K_THRUST) / (10000.0 * 10000.0)
        assert ship.current_speed == pytest.approx(expected_accel, abs=0.0001)

    def test_throttle_at_zero(self):
        """Zero throttle should result in target speed of zero."""
        ship = MockShipWithPhysics()
        ship.current_speed = 50.0
        ship.is_thrusting = True
        ship._total_thrust = 1000.0
        ship.mass = 100.0
        ship.engine_throttle = 0.0

        # Run several updates
        for _ in range(100):
            ship.is_thrusting = True
            ship.update_physics_movement()

        # Should decelerate toward zero target
        assert ship.current_speed == pytest.approx(0.0, abs=0.1)

    def test_throttle_over_one(self):
        """Throttle > 1.0 should result in target speed above normal max."""
        ship = MockShipWithPhysics()
        ship._total_thrust = 1000.0
        ship.mass = 100.0
        ship.engine_throttle = 1.5  # 150% throttle

        expected_max_speed = (ship._total_thrust * K_SPEED) / ship.mass
        expected_target = expected_max_speed * 1.5

        # Run many updates to reach target speed
        for _ in range(2000):
            ship.is_thrusting = True
            ship.update_physics_movement()

        assert ship.current_speed == pytest.approx(expected_target, abs=0.1)

    def test_negative_current_speed_handled(self):
        """Negative current_speed should decelerate toward zero normally."""
        ship = MockShipWithPhysics()
        ship.current_speed = -10.0  # Somehow negative
        ship.is_thrusting = False
        ship.acceleration_rate = 5.0

        ship.update_physics_movement()

        # Should step toward zero (add step since diff is positive)
        assert ship.current_speed == pytest.approx(-5.0, abs=0.001)


class TestMixinIntegrationWithPhysicsBody:
    """Tests for correct integration with PhysicsBody base class."""

    def test_inherits_position_from_physics_body(self):
        """MockShip should have position from PhysicsBody."""
        ship = MockShipWithPhysics(x=100, y=200)

        assert ship.position.x == 100
        assert ship.position.y == 200

    def test_inherits_velocity_from_physics_body(self):
        """MockShip should have velocity from PhysicsBody."""
        ship = MockShipWithPhysics()

        assert hasattr(ship, 'velocity')
        assert ship.velocity.x == 0
        assert ship.velocity.y == 0

    def test_inherits_forward_vector_from_physics_body(self):
        """MockShip should have forward_vector from PhysicsBody."""
        ship = MockShipWithPhysics(angle=0)

        forward = ship.forward_vector()

        assert forward.x == pytest.approx(1.0, abs=0.001)
        assert forward.y == pytest.approx(0.0, abs=0.001)

    def test_forward_vector_rotates_with_angle(self):
        """forward_vector should change based on ship angle."""
        ship = MockShipWithPhysics(angle=90)

        forward = ship.forward_vector()

        assert forward.x == pytest.approx(0.0, abs=0.001)
        assert forward.y == pytest.approx(1.0, abs=0.001)
