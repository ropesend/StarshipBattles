import pytest
import pygame
import math

from game.simulation.entities.ship import Ship, LayerType
from game.simulation.entities.ship_loader import initialize_ship_data
from game.simulation.components import load_components, create_component
from game.core.registry import RegistryManager
from tests.fixtures.paths import get_project_root, get_data_dir


@pytest.fixture
def ship_data():
    """Initialize ship data and load components, clean up pygame and registry after test."""
    initialize_ship_data(str(get_project_root()))
    load_components(str(get_data_dir() / "components.json"))
    yield
    pygame.quit()
    RegistryManager.instance().clear()


@pytest.fixture
def fully_equipped_ship(ship_data):
    """Create a fully equipped Cruiser ship for testing movement."""
    # Use Cruiser class which has INNER layer (Capital_Standard config)
    ship = Ship("TestShip", 100, 100, (255, 255, 255), ship_class="Cruiser")
    # Basic setup - need crew infrastructure for components to be active
    # Core: Bridge (requires crew to function)
    ship.add_component(create_component('bridge'), LayerType.CORE)
    # Core: Generator
    ship.add_component(create_component('generator'), LayerType.CORE)

    # INNER: Multiple crew quarters and life support (Cruiser needs more crew than Escort)
    for _ in range(3):
        ship.add_component(create_component('crew_quarters'), LayerType.INNER)
        ship.add_component(create_component('life_support'), LayerType.INNER)

    # Inner: Fuel Tank
    ship.add_component(create_component('fuel_tank'), LayerType.INNER)
    # Outer: Engine (requires crew to be active)
    ship.add_component(create_component('standard_engine'), LayerType.OUTER)

    # Initial recalc
    ship.recalculate_stats()

    # Verify stats populated - engine should be active with crew support
    assert ship.total_thrust > 0, \
        f"Engine should have thrust. Crew: {ship.crew_onboard}, Required: {ship.crew_required}"
    assert ship.resources.get_max_value("fuel") > 0
    ship.resources.get_resource("fuel").current_value = ship.resources.get_max_value("fuel")

    return ship


class TestArcadeMovement:

    def test_stats(self, fully_equipped_ship):
        """Physics validation using tick-based INVERSE MASS SCALING model."""
        ship = fully_equipped_ship
        # Acceleration = (Thrust * K_THRUST) / (Mass^2)
        # Max Speed = (Thrust * K_SPEED) / Mass
        # Constants scaled for dt=1.0 per tick
        K_THRUST = 2500   # Tick-based constant
        K_SPEED = 25      # Tick-based constant

        expected_accel = (ship.total_thrust * K_THRUST) / (ship.mass ** 2)
        assert ship.acceleration_rate == pytest.approx(expected_accel, abs=0.01)

        # Max Speed
        expected_max_speed = (ship.total_thrust * K_SPEED) / ship.mass
        assert ship.max_speed == pytest.approx(expected_max_speed, abs=0.01)

    def test_thrust_increases_speed(self, fully_equipped_ship):
        """Thrusting should increase speed and consume fuel."""
        ship = fully_equipped_ship
        initial_speed = ship.current_speed
        assert initial_speed == 0

        ship.thrust_forward()
        ship.update()  # Full update triggers component fuel consumption

        # Speed should increase by acceleration_rate (flag-based physics)
        assert ship.current_speed > 0

        # Fuel consumed via engine's ResourceConsumption ability
        assert ship.resources.get_value("fuel") < ship.resources.get_max_value("fuel")

    def test_movement_direction(self, fully_equipped_ship):
        """Ship should move in the direction it's facing."""
        ship = fully_equipped_ship
        ship.current_speed = 100
        ship.angle = 0  # Right (1, 0)

        initial_pos = pygame.math.Vector2(ship.position)

        ship.update()

        # Should move 100 units right (minus drag decay on speed, but position uses velocity calculated from speed)
        # Wait, update applies drag to speed!
        # self.current_speed *= (1 - self.drag * dt)
        # Then velocity = forward * speed
        # Pos += velocity * dt

        # So actual movement will be slightly less if drag is high
        # But direction should be purely X axis
        new_pos = ship.position
        diff = new_pos - initial_pos

        assert diff.x > 50  # Moved right
        assert diff.y == pytest.approx(0, abs=0.00001)  # Minimal Y movement

        # Test Rotation
        ship.angle = 90  # Down (0, 1) if pygame coord (y down)
        # Rotate logic check:
        # ship.rotate not called here, manual angle set

        initial_pos = pygame.math.Vector2(ship.position)
        ship.current_speed = 100  # Reset speed
        ship.update()

        diff = ship.position - initial_pos
        assert diff.x == pytest.approx(0, abs=1.0)
        assert diff.y > 50  # Moved down

    def test_max_speed_cap(self, fully_equipped_ship):
        """Speed above max should decelerate toward max_speed when thrusting."""
        ship = fully_equipped_ship
        initial_over_speed = ship.max_speed + 1000
        ship.current_speed = initial_over_speed

        # Thrusting sets target_speed = max_speed, so ship decelerates toward it
        ship.thrust_forward()
        ship.update_physics_movement()

        # Speed should have decreased (moving toward max_speed)
        assert ship.current_speed < initial_over_speed, \
            "Speed should decrease when above max_speed and thrusting"

        # Run multiple updates to reach max_speed
        for _ in range(3000):  # Enough iterations to converge
            ship.thrust_forward()
            ship.update_physics_movement()

        # After many updates, should be at or very close to max_speed
        assert ship.current_speed == pytest.approx(ship.max_speed, abs=0.1), \
            "Speed should converge to max_speed when thrusting"
