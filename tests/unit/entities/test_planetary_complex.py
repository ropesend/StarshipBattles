import pytest

from game.simulation.entities.ship import Ship, LayerType
from game.simulation.entities.ship_loader import initialize_ship_data
from game.simulation.components import load_components, load_modifiers, get_all_components
from game.core.registry import RegistryManager


class TestPlanetaryComplex:
    """Test Planetary Complex implementation."""

    @pytest.fixture(autouse=True)
    def setup(self):
        initialize_ship_data()
        load_components()
        load_modifiers()

        classes = RegistryManager.instance().vehicle_classes
        for i in range(1, 12):
            class_name = f"Planetary Complex (Tier {i})"
            assert class_name in classes, f"{class_name} missing"

            # Check mass doubling
            vehicle_def = classes[class_name]
            expected_mass = 1000 * (2**(i-1))
            assert vehicle_def['max_mass'] == expected_mass, f"{class_name} mass incorrect"
            assert vehicle_def['type'] == "Planetary Complex"

            # PATCH: Increase max_mass to allow adding components in tests
            # (since hulls now take 100% of base budget)
            vehicle_def['max_mass'] += 2000

        yield

        # Teardown
        RegistryManager.instance().clear()

    def test_add_central_command(self):
        """Verify Central Complex Command can be added."""
        complex_ship = Ship("Test Complex", 0, 0, (255, 255, 255),
                          ship_class="Planetary Complex (Tier 1)")

        comps = RegistryManager.instance().components
        command = comps["central_complex_command"].clone()
        result = complex_ship.add_component(command, LayerType.CORE)
        assert result, "Should accept Central Complex Command"

        complex_ship.recalculate_stats()
        assert complex_ship.get_ability_total("CommandAndControl"), \
            "Should have CommandAndControl ability"

    def test_accepts_ship_components(self):
        """Verify it accepts standard ship weapons and sensors."""
        complex_ship = Ship("Test Complex", 0, 0, (255, 255, 255),
                          ship_class="Planetary Complex (Tier 1)")

        # Weapons
        comps = RegistryManager.instance().components
        railgun = comps["railgun"].clone()
        result = complex_ship.add_component(railgun, LayerType.OUTER)
        assert result, "Should accept Railgun"

        # Sensors
        sensor = comps["combat_sensor"].clone()
        result = complex_ship.add_component(sensor, LayerType.OUTER)
        assert result, "Should accept Combat Sensor"

        # Shields
        shield = comps["shield_generator"].clone()
        result = complex_ship.add_component(shield, LayerType.INNER)
        assert result, "Should accept Shield Generator"

    def test_rejects_propulsion(self):
        """Verify it rejects engines and thrusters."""
        complex_ship = Ship("Test Complex", 0, 0, (255, 255, 255),
                          ship_class="Planetary Complex (Tier 1)")

        comps = RegistryManager.instance().components
        engine = comps["standard_engine"].clone()
        result = complex_ship.add_component(engine, LayerType.INNER)
        assert not result, "Should REJECT Standard Engine"

        thruster = comps["thruster"].clone()
        result = complex_ship.add_component(thruster, LayerType.OUTER)
        assert not result, "Should REJECT Thruster"

    def test_rejects_ship_bridge(self):
        """Verify it rejects standard Ship Bridge."""
        complex_ship = Ship("Test Complex", 0, 0, (255, 255, 255),
                          ship_class="Planetary Complex (Tier 1)")

        comps = RegistryManager.instance().components
        bridge = comps["bridge"].clone()
        result = complex_ship.add_component(bridge, LayerType.CORE)
        assert not result, "Should REJECT standard Ship Bridge"

    def test_movement_capabilities(self):
        """Verify it has zero movement capabilities."""
        complex_ship = Ship("Test Complex", 0, 0, (255, 255, 255),
                          ship_class="Planetary Complex (Tier 1)")

        comps = RegistryManager.instance().components
        command = comps["central_complex_command"].clone()
        complex_ship.add_component(command, LayerType.CORE)
        complex_ship.recalculate_stats()

        assert complex_ship.total_thrust == 0
        assert complex_ship.turn_speed == 0
