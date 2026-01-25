"""Tests for ShipPhysicsMixin movement mechanics."""
import pytest
import pygame

from game.simulation.entities.ship import Ship, LayerType
from game.simulation.entities.ship_loader import initialize_ship_data
from game.simulation.components import load_components, create_component
from game.core.registry import RegistryManager
from tests.fixtures.paths import get_project_root, get_data_dir


@pytest.fixture
def ship_with_engine():
    """Create a ship with engine and fuel for thrust tests."""
    pygame.init()
    initialize_ship_data(str(get_project_root()))
    load_components(str(get_data_dir() / "components.json"))
    ship = Ship("TestShip", 0, 0, (255, 255, 255), ship_class="Escort")
    ship.add_component(create_component('bridge'), LayerType.CORE)
    ship.add_component(create_component('crew_quarters'), LayerType.CORE)
    ship.add_component(create_component('life_support'), LayerType.CORE)
    ship.add_component(create_component('standard_engine'), LayerType.OUTER)
    ship.add_component(create_component('fuel_tank'), LayerType.CORE)
    ship.recalculate_stats()
    yield ship
    RegistryManager.instance().clear()
    if pygame.get_init():
        pygame.quit()


@pytest.fixture
def ship_with_thruster():
    """Create a ship with thruster for rotation tests."""
    pygame.init()
    initialize_ship_data(str(get_project_root()))
    load_components(str(get_data_dir() / "components.json"))
    ship = Ship("TestShip", 0, 0, (255, 255, 255), ship_class="Escort")
    ship.add_component(create_component('bridge'), LayerType.CORE)
    ship.add_component(create_component('crew_quarters'), LayerType.CORE)
    ship.add_component(create_component('life_support'), LayerType.CORE)
    ship.add_component(create_component('standard_engine'), LayerType.OUTER)
    ship.add_component(create_component('thruster'), LayerType.OUTER)
    ship.recalculate_stats()
    yield ship
    RegistryManager.instance().clear()
    if pygame.get_init():
        pygame.quit()


class TestShipPhysicsThrust:
    """Test thrust and fuel consumption."""

    def test_thrust_forward_sets_flag(self, ship_with_engine):
        """Thrusting should set is_thrusting flag."""
        ship = ship_with_engine
        ship.is_thrusting = False
        initial_fuel = ship.resources.get_value("fuel")

        ship.thrust_forward()

        # Should have set thrusting flag if we have fuel
        if initial_fuel > 0:
            assert ship.is_thrusting is True

    def test_thrust_forward_consumes_fuel(self, ship_with_engine):
        """Thrusting implies active engine, which consumes fuel (now constant)."""
        ship = ship_with_engine
        initial_fuel = ship.resources.get_value("fuel")
        assert initial_fuel > 0, "Ship needs fuel for this test"

        # In the new model, engines consume fuel CONSTANTLY if they are active components.
        # Calling update() should trigger consumption regardless of thrust command if engine is ON.

        ship.update()  # This runs Component.update() which consumes fuel (constant trigger)

        # Should have consumed some fuel
        assert ship.resources.get_value("fuel") < initial_fuel

    def test_thrust_no_fuel_no_thrust(self, ship_with_engine):
        """Ship without fuel should not be able to sustain thrust."""
        ship = ship_with_engine
        ship.resources.get_resource("fuel").current_value = 0

        # Run update to trigger fuel starvation check on engine
        # This marks engine as non-operational via ResourceConsumption ability
        ship.update()

        # Now attempt to thrust - engine should be non-operational
        ship.thrust_forward()
        ship.update_physics_movement()  # Calculate movement based on thrust state

        # Speed should be 0 or very low because engine is non-operational
        # With no operational engines, thrust_force is 0, so no acceleration
        assert ship.current_speed < 1.0

    def test_update_physics_accelerates_when_thrusting(self, ship_with_engine):
        """Speed should increase toward max when thrusting."""
        ship = ship_with_engine
        initial_speed = ship.current_speed
        assert initial_speed == 0

        # Thrust and update
        ship.thrust_forward()
        ship.update_physics_movement()

        # Speed should have increased
        assert ship.current_speed > initial_speed

    def test_update_physics_decelerates_when_not_thrusting(self, ship_with_engine):
        """Speed should decrease when not thrusting."""
        ship = ship_with_engine
        # Give ship some speed first
        ship.current_speed = 10

        # Don't thrust
        ship.is_thrusting = False
        ship.update_physics_movement()

        # Speed should decrease toward 0
        assert ship.current_speed < 10


class TestShipPhysicsRotation:
    """Test ship rotation mechanics."""

    def test_rotate_left(self, ship_with_thruster):
        """Rotating left (direction=-1) should decrease angle."""
        ship = ship_with_thruster
        initial_angle = ship.angle

        ship.rotate(-1)

        # Allow for modular wrapping
        angle_change = ship.angle - initial_angle
        if angle_change > 180:
            angle_change -= 360

        assert angle_change < 0

    def test_rotate_right(self, ship_with_thruster):
        """Rotating right (direction=+1) should increase angle."""
        ship = ship_with_thruster
        initial_angle = ship.angle

        ship.rotate(1)

        # Allow for modular wrapping
        angle_change = ship.angle - initial_angle
        if angle_change < -180:
            angle_change += 360

        assert angle_change > 0

    def test_rotation_respects_turn_speed(self, ship_with_thruster):
        """Rotation amount should depend on turn_speed stat."""
        ship = ship_with_thruster
        # Ship with thrusters should have turn_speed > 0
        assert ship.turn_speed > 0

        # Rotation amount should be related to turn_speed
        initial_angle = ship.angle
        ship.rotate(1)
        rotation = ship.angle - initial_angle

        # Expected: turn_speed / 100.0 per rotate call
        expected_rotation = ship.turn_speed / 100.0
        assert rotation == pytest.approx(expected_rotation, abs=0.001)


class TestShipPhysicsMovement:
    """Test ship position updates."""

    def test_position_updates_with_velocity(self, ship_with_engine):
        """Position should update based on velocity."""
        ship = ship_with_engine
        initial_pos = pygame.math.Vector2(ship.position)

        # Thrust first to set speed, then update to move
        ship.thrust_forward()  # Sets is_thrusting flag
        ship.update_physics_movement()  # Accelerates and moves

        # Position should have changed since we're now moving
        assert tuple(ship.position) != tuple(initial_pos)

    def test_velocity_matches_heading(self, ship_with_engine):
        """Velocity should match ship heading direction."""
        ship = ship_with_engine
        ship.angle = 90  # Facing down (in screen coords)
        ship.current_speed = 10

        ship.update_physics_movement()

        # Velocity should primarily be in Y direction (down)
        assert abs(ship.velocity.y) > abs(ship.velocity.x)
