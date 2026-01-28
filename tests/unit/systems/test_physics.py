import pytest
import pygame
import math

from game.engine.physics import PhysicsBody


@pytest.fixture
def pygame_init():
    """Initialize and cleanup pygame for tests."""
    pygame.init()
    yield
    pygame.quit()
    from game.core.registry import RegistryManager
    RegistryManager.instance().clear()


class TestPhysicsBasics:
    """Test basic PhysicsBody initialization and properties."""

    def test_initialization(self, pygame_init):
        """PhysicsBody should initialize with correct position and angle."""
        body = PhysicsBody(100, 200, 90)
        assert body.position == pygame.math.Vector2(100, 200)
        assert body.angle == 90
        assert body.velocity == pygame.math.Vector2(0, 0)

    def test_default_values(self, pygame_init):
        """PhysicsBody should have sensible defaults."""
        body = PhysicsBody(0, 0)
        assert body.angle == 0
        assert body.mass == 1.0
        assert body.drag > 0


class TestPhysicsMovement:
    """Test PhysicsBody movement and physics update."""

    def test_update_movement(self, pygame_init):
        """Test basic velocity application."""
        body = PhysicsBody(0, 0)
        body.velocity = pygame.math.Vector2(10, 0)
        # PhysicsBody implementation:
        # velocity *= (1 - drag)
        # position += velocity
        # default drag is 0.5

        body.update(1.0)

        # Expected:
        # Start Vel: (10, 0)
        # Dragged Vel: (10, 0) * (1 - 0.5) = (5, 0)
        # Position: (0,0) + (5,0) = (5, 0)

        assert body.position == pygame.math.Vector2(5, 0)
        assert body.velocity == pygame.math.Vector2(5, 0)

    def test_angular_velocity(self, pygame_init):
        """Angular velocity should rotate the body."""
        body = PhysicsBody(0, 0, 0)
        body.angular_velocity = 45
        body.angular_drag = 0  # Disable drag for predictable test

        body.update()

        assert body.angle == 45


class TestPhysicsForces:
    """Test force application and acceleration."""

    def test_apply_force_accelerates(self, pygame_init):
        """apply_force should add to acceleration based on mass."""
        body = PhysicsBody(0, 0)
        body.mass = 2.0
        body.drag = 0  # Disable drag

        force = pygame.math.Vector2(10, 0)
        body.apply_force(force)

        # Acceleration should be force / mass
        expected_accel = pygame.math.Vector2(5, 0)
        assert body.acceleration == expected_accel

    def test_apply_force_accumulates(self, pygame_init):
        """Multiple apply_force calls should accumulate."""
        body = PhysicsBody(0, 0)
        body.mass = 1.0

        body.apply_force(pygame.math.Vector2(5, 0))
        body.apply_force(pygame.math.Vector2(3, 2))

        assert body.acceleration == pygame.math.Vector2(8, 2)

    def test_apply_force_updates_velocity(self, pygame_init):
        """After update, acceleration should affect velocity."""
        body = PhysicsBody(0, 0)
        body.mass = 1.0
        body.drag = 0  # Disable for test

        body.apply_force(pygame.math.Vector2(10, 0))
        body.update()

        # Velocity should have increased by acceleration
        assert body.velocity.x > 0
        # Acceleration should be reset
        assert body.acceleration == pygame.math.Vector2(0, 0)


class TestPhysicsDirection:
    """Test forward vector calculation."""

    def test_forward_vector_angle_0(self, pygame_init):
        """Angle 0 should point right (1, 0)."""
        body = PhysicsBody(0, 0, 0)
        forward = body.forward_vector()

        assert forward.x == pytest.approx(1.0, abs=1e-5)
        assert forward.y == pytest.approx(0.0, abs=1e-5)

    def test_forward_vector_angle_90(self, pygame_init):
        """Angle 90 should point down (0, 1) in screen coords."""
        body = PhysicsBody(0, 0, 90)
        forward = body.forward_vector()

        assert forward.x == pytest.approx(0.0, abs=1e-5)
        assert forward.y == pytest.approx(1.0, abs=1e-5)

    def test_forward_vector_angle_180(self, pygame_init):
        """Angle 180 should point left (-1, 0)."""
        body = PhysicsBody(0, 0, 180)
        forward = body.forward_vector()

        assert forward.x == pytest.approx(-1.0, abs=1e-5)
        assert forward.y == pytest.approx(0.0, abs=1e-5)

    def test_forward_vector_is_unit(self, pygame_init):
        """Forward vector should be unit length."""
        body = PhysicsBody(0, 0, 45)
        forward = body.forward_vector()

        assert forward.length() == pytest.approx(1.0, abs=1e-5)


class TestAbilityDrivenPhysics:
    """Refactored Tests for Ability-Driven Physics."""

    @pytest.fixture
    def mock_ship(self, pygame_init):
        """Create a mock ship for ability-driven physics tests."""
        from game.simulation.entities.ship_physics import ShipPhysicsMixin
        from game.engine.physics import PhysicsBody

        class MockShip(PhysicsBody, ShipPhysicsMixin):
            def __init__(self):
                super().__init__(0, 0)
                self.mass = 1000
                self.drag = 0.5
                self.turn_speed = 90
                self.acceleration_rate = 100
                self.max_speed = 500
                self.current_speed = 0
                self.is_active = True
                self.is_thrusting = False
                self.engine_throttle = 1.0
                self.turn_throttle = 1.0
                self.stats = {}
                self._mock_thrust = 100000

            def get_total_ability_value(self, name, operational_only=True):
                if name == 'CombatPropulsion':
                    return self._mock_thrust
                return 0

        return MockShip()

    def test_ability_driven_thrust(self, mock_ship):
        """Test that physics uses stats derived from CombatPropulsion abilities."""
        mock_ship.angle = 0  # Facing Right
        mock_ship._mock_thrust = 200000  # High thrust

        # Apply Thrust using Mixin method
        mock_ship.thrust_forward()
        mock_ship.update_physics_movement()

        # Velocity should be > 0
        assert mock_ship.current_speed > 0
        assert mock_ship.velocity.x > 0

    def test_mass_dampening(self, mock_ship):
        """Test that higher mass reduces effective response."""
        import pygame

        # Baseline
        mock_ship.mass = 100
        mock_ship._mock_thrust = 100000
        mock_ship.current_speed = 0
        mock_ship.thrust_forward()
        mock_ship.update_physics_movement()
        fast_speed = mock_ship.current_speed

        # High Mass
        mock_ship.mass = 10000
        mock_ship.current_speed = 0
        mock_ship.velocity = pygame.math.Vector2(0, 0)
        mock_ship.thrust_forward()
        mock_ship.update_physics_movement()
        slow_speed = mock_ship.current_speed

        assert fast_speed > slow_speed


class TestPhysicsConstantsConsolidation:
    """Test that physics constants are centralized - PHYS-01 regression test."""

    def test_stats_uses_physics_constants_module(self, pygame_init):
        """Verify stats.py imports K_SPEED, K_THRUST, K_TURN from physics_constants.py."""
        from game.simulation import physics_constants
        import game.simulation.systems.stats as stats_module

        # Verify the constants are imported into stats module (not defined locally)
        # If the fix is correct, stats_module should reference physics_constants values
        assert hasattr(stats_module, 'K_SPEED'), "stats module should import K_SPEED"
        assert hasattr(stats_module, 'K_THRUST'), "stats module should import K_THRUST"
        assert hasattr(stats_module, 'K_TURN'), "stats module should import K_TURN"

        # Verify values match physics_constants (single source of truth)
        assert stats_module.K_SPEED == physics_constants.K_SPEED
        assert stats_module.K_THRUST == physics_constants.K_THRUST
        assert stats_module.K_TURN == physics_constants.K_TURN

    def test_physics_constants_values(self, pygame_init):
        """Verify physics_constants has expected values (documentation check)."""
        from game.simulation import physics_constants

        # These are the canonical values per physics_constants.py
        assert physics_constants.K_SPEED == 25
        assert physics_constants.K_THRUST == 2500
        assert physics_constants.K_TURN == 25000
