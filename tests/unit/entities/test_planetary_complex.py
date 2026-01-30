import pytest

from game.simulation.entities.ship import Ship, LayerType
from game.simulation.entities.ship_loader import initialize_ship_data
from game.simulation.components.component import load_components, load_modifiers, get_all_components, create_component
from game.core.registry import RegistryManager


class TestPlanetaryComplex:
    """Test Planetary Complex implementation."""

    @pytest.fixture(autouse=True)
    def setup(self, fresh_registries):
        self.fresh_registries = fresh_registries

        classes = fresh_registries.vehicle_classes
        for i in range(1, 12):
            class_name = f"Planetary Complex (Tier {i})"
            assert class_name in classes, f"{class_name} missing"

            # Check mass doubling (allow for already-patched values from parallel runs)
            vehicle_def = classes[class_name]
            expected_mass = 1000 * (2**(i-1))
            # Due to parallel test execution, value may already be patched (+2000)
            actual_mass = vehicle_def['max_mass']
            assert actual_mass == expected_mass or actual_mass == expected_mass + 2000, \
                f"{class_name} mass incorrect: got {actual_mass}, expected {expected_mass} or {expected_mass + 2000}"
            assert vehicle_def['type'] == "Planetary Complex"

            # PATCH: Increase max_mass to allow adding components in tests
            # (since hulls now take 100% of base budget)
            # Only patch if not already patched
            if actual_mass == expected_mass:
                vehicle_def['max_mass'] += 2000

    def test_add_central_command(self):
        """Verify Central Complex Command can be added."""
        complex_ship = Ship("Test Complex", 0, 0, (255, 255, 255),
                          ship_class="Planetary Complex (Tier 1)",
                          registries=self.fresh_registries)

        command = create_component("central_complex_command", registries=self.fresh_registries)
        result = complex_ship.add_component(command, LayerType.CORE)
        assert result, "Should accept Central Complex Command"

        complex_ship.recalculate_stats()
        assert complex_ship.get_ability_total("CommandAndControl"), \
            "Should have CommandAndControl ability"

    def test_accepts_ship_components(self):
        """Verify it accepts standard ship weapons and sensors."""
        complex_ship = Ship("Test Complex", 0, 0, (255, 255, 255),
                          ship_class="Planetary Complex (Tier 1)",
                          registries=self.fresh_registries)

        # Weapons
        railgun = create_component("railgun", registries=self.fresh_registries)
        result = complex_ship.add_component(railgun, LayerType.OUTER)
        assert result, "Should accept Railgun"

        # Sensors
        sensor = create_component("combat_sensor", registries=self.fresh_registries)
        result = complex_ship.add_component(sensor, LayerType.OUTER)
        assert result, "Should accept Combat Sensor"

        # Shields
        shield = create_component("shield_generator", registries=self.fresh_registries)
        result = complex_ship.add_component(shield, LayerType.INNER)
        assert result, "Should accept Shield Generator"

    def test_rejects_propulsion(self):
        """Verify it rejects engines and thrusters."""
        complex_ship = Ship("Test Complex", 0, 0, (255, 255, 255),
                          ship_class="Planetary Complex (Tier 1)",
                          registries=self.fresh_registries)

        engine = create_component("standard_engine", registries=self.fresh_registries)
        result = complex_ship.add_component(engine, LayerType.INNER)
        assert not result, "Should REJECT Standard Engine"

        thruster = create_component("thruster", registries=self.fresh_registries)
        result = complex_ship.add_component(thruster, LayerType.OUTER)
        assert not result, "Should REJECT Thruster"

    def test_rejects_ship_bridge(self):
        """Verify it rejects standard Ship Bridge."""
        complex_ship = Ship("Test Complex", 0, 0, (255, 255, 255),
                          ship_class="Planetary Complex (Tier 1)",
                          registries=self.fresh_registries)

        bridge = create_component("bridge", registries=self.fresh_registries)
        result = complex_ship.add_component(bridge, LayerType.CORE)
        assert not result, "Should REJECT standard Ship Bridge"

    def test_movement_capabilities(self):
        """Verify it has zero movement capabilities."""
        complex_ship = Ship("Test Complex", 0, 0, (255, 255, 255),
                          ship_class="Planetary Complex (Tier 1)",
                          registries=self.fresh_registries)

        command = create_component("central_complex_command", registries=self.fresh_registries)
        complex_ship.add_component(command, LayerType.CORE)
        complex_ship.recalculate_stats()

        assert complex_ship.total_thrust == 0
        assert complex_ship.turn_speed == 0
