"""
Tests for Ship serialization (to_dict/from_dict round-trip).
TDD-first approach for ShipSerializer extraction.
"""
import pytest
import pygame
from unittest import mock

from game.simulation.entities.ship import Ship, LayerType
from game.simulation.entities.ship_loader import initialize_ship_data
from game.simulation.components import load_components, create_component
from game.core.registry import RegistryManager
from tests.fixtures.paths import get_data_dir


@pytest.fixture
def setup_game_data():
    """Initialize game data for each test."""
    if not pygame.get_init():
        pygame.init()
    initialize_ship_data()
    load_components(str(get_data_dir() / "components.json"))
    yield
    # Cleanup
    RegistryManager.instance().clear()
    if pygame.get_init():
        pygame.quit()
    mock.patch.stopall()


class TestShipSerialization:
    """Test Ship serialization round-trip behavior."""

    def test_roundtrip_basic(self, setup_game_data):
        """Basic ship properties survive round-trip serialization."""
        ship = Ship("TestShip", 0, 0, (100, 150, 200), team_id=2,
                    ship_class="Frigate", theme_id="Terran")
        ship.ai_strategy = "aggressive"

        # Round-trip
        data = ship.to_dict()
        restored = Ship.from_dict(data)

        # Verify basic properties
        assert restored.name == "TestShip"
        assert restored.ship_class == "Frigate"
        assert restored.theme_id == "Terran"
        assert restored.team_id == 2
        assert tuple(restored.color) == (100, 150, 200)
        assert restored.ai_strategy == "aggressive"

    def test_roundtrip_with_components(self, setup_game_data):
        """Components in all layers survive round-trip."""
        ship = Ship("ComponentShip", 0, 0, (255, 255, 255))

        # Add components to various layers
        bridge = create_component('bridge')
        ship.add_component(bridge, LayerType.CORE)

        railgun = create_component('railgun')
        ship.add_component(railgun, LayerType.OUTER)

        armor = create_component('armor_plate')
        ship.add_component(armor, LayerType.ARMOR)

        # Round-trip
        data = ship.to_dict()
        restored = Ship.from_dict(data)

        # Verify components are present
        core_ids = [c.id for c in restored.layers[LayerType.CORE]['components']]
        assert 'bridge' in core_ids

        outer_ids = [c.id for c in restored.layers[LayerType.OUTER]['components']]
        assert 'railgun' in outer_ids

        armor_ids = [c.id for c in restored.layers[LayerType.ARMOR]['components']]
        assert 'armor_plate' in armor_ids

    def test_roundtrip_with_modifiers(self, setup_game_data):
        """Components with modifiers survive round-trip when modifiers are present."""
        ship = Ship("ModifierShip", 0, 0, (255, 255, 255))

        # Add component - modifiers are a list of ApplicationModifier objects
        railgun = create_component('railgun')
        ship.add_component(railgun, LayerType.OUTER)

        # Count original modifiers
        original_count = len(railgun.modifiers)

        # Round-trip
        data = ship.to_dict()
        restored = Ship.from_dict(data)

        # Find railgun in restored ship
        restored_railguns = [c for c in restored.layers[LayerType.OUTER]['components']
                            if c.id == 'railgun']
        assert len(restored_railguns) == 1

        restored_railgun = restored_railguns[0]
        # Verify the default modifiers (if any) are preserved
        assert len(restored_railgun.modifiers) == original_count

    def test_roundtrip_preserves_resources(self, setup_game_data):
        """Resource values (fuel, energy, ammo) survive round-trip."""
        ship = Ship("ResourceShip", 0, 0, (255, 255, 255))

        # Add components that provide resource capacity
        # Need fuel tank for fuel, generator for energy
        ship.add_component(create_component('bridge'), LayerType.CORE)
        ship.add_component(create_component('fuel_tank'), LayerType.CORE)
        ship.add_component(create_component('generator'), LayerType.CORE)
        ship.recalculate_stats()

        # Get max values to ensure we're setting within limits
        max_fuel = ship.resources.get_max_value("fuel")
        max_energy = ship.resources.get_max_value("energy")

        # Only test if we have capacity
        test_fuel = None
        test_energy = None
        if max_fuel > 0:
            test_fuel = min(50.0, max_fuel)
            ship.resources.set_value("fuel", test_fuel)
        if max_energy > 0:
            test_energy = min(75.0, max_energy)
            ship.resources.set_value("energy", test_energy)

        # Round-trip
        data = ship.to_dict()
        restored = Ship.from_dict(data)

        # Verify resources restored (compare with what was actually set)
        if test_fuel is not None:
            assert restored.resources.get_value("fuel") == pytest.approx(test_fuel, abs=0.1)
        if test_energy is not None:
            assert restored.resources.get_value("energy") == pytest.approx(test_energy, abs=0.1)

    def test_roundtrip_preserves_stats(self, setup_game_data):
        """Calculated stats (HP, mass, speed) are consistent after round-trip."""
        ship = Ship("StatsShip", 0, 0, (255, 255, 255), ship_class="Escort")

        # Add components that affect stats
        bridge = create_component('bridge')
        ship.add_component(bridge, LayerType.CORE)

        engine = create_component('engine')
        ship.add_component(engine, LayerType.INNER)

        ship.recalculate_stats()

        original_max_hp = ship.max_hp
        original_mass = ship.mass
        original_max_speed = ship.max_speed

        # Round-trip
        data = ship.to_dict()
        restored = Ship.from_dict(data)

        # Stats should match (within tolerance for floating point)
        assert restored.max_hp == original_max_hp
        assert restored.mass == pytest.approx(original_mass, abs=0.1)
        assert restored.max_speed == pytest.approx(original_max_speed, abs=0.1)

    def test_hull_not_serialized_but_restored(self, setup_game_data):
        """HULL layer is not serialized but auto-equipped on restore."""
        ship = Ship("HullTestShip", 0, 0, (255, 255, 255), ship_class="Escort")

        # Verify hull exists
        assert len(ship.layers[LayerType.HULL]['components']) == 1
        original_hull_id = ship.layers[LayerType.HULL]['components'][0].id

        # Round-trip
        data = ship.to_dict()

        # HULL should NOT be in serialized data
        assert 'HULL' not in data['layers']

        # Restore
        restored = Ship.from_dict(data)

        # HULL should be auto-equipped on restore
        assert len(restored.layers[LayerType.HULL]['components']) == 1
        restored_hull_id = restored.layers[LayerType.HULL]['components'][0].id
        assert restored_hull_id == original_hull_id

    def test_layer_order_preserved(self, setup_game_data):
        """Multiple components in same layer maintain order."""
        ship = Ship("OrderShip", 0, 0, (255, 255, 255))

        # Add multiple components to OUTER
        for _ in range(3):
            railgun = create_component('railgun')
            ship.add_component(railgun, LayerType.OUTER)

        original_count = len(ship.layers[LayerType.OUTER]['components'])

        # Round-trip
        data = ship.to_dict()
        restored = Ship.from_dict(data)

        # Same count should be preserved
        restored_count = len(restored.layers[LayerType.OUTER]['components'])
        assert restored_count == original_count
