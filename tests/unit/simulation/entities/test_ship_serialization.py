"""
Unit tests for ShipSerializer class.

Tests cover:
- Serialization (to_dict) methods
- Deserialization (from_dict) methods
- Round-trip tests (serialize -> deserialize -> compare)
- Edge cases (empty data, missing fields, invalid data)
- Helper methods (_load_components, _restore_resources, _verify_stats)

PROJ-118 Phase 2: Foundation test coverage.
"""
import pytest
from unittest.mock import MagicMock, patch

from game.core.exceptions import ValidationException
from game.simulation.entities.ship_serialization import ShipSerializer
from game.simulation.entities.ship import Ship
from game.simulation.components.component import create_component
from game.core.constants import LayerType
from game.core.registry import GameRegistries


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture
def registries(fresh_registries):
    """Provide fresh registries for test isolation."""
    return fresh_registries


@pytest.fixture
def basic_ship(registries):
    """Create a basic ship for testing."""
    ship = Ship(
        name="TestShip",
        x=100, y=200,
        color=(255, 128, 64),
        team_id=1,
        ship_class="Escort",
        theme_id="Federation",
        registries=registries
    )
    return ship


@pytest.fixture
def equipped_ship(registries):
    """Create a ship with components in various layers.

    Uses Cruiser class which has CORE, INNER, OUTER, and ARMOR layers.
    """
    ship = Ship(
        name="EquippedShip",
        x=0, y=0,
        color=(100, 200, 50),
        team_id=2,
        ship_class="Cruiser",  # Cruiser has INNER layer
        theme_id="Terran",
        registries=registries
    )
    ship.movement_policy = "brawl_close"
    ship.targeting_policy = "brawler"

    # Add components to different layers
    bridge = create_component('bridge', registries=registries)
    ship.add_component(bridge, LayerType.CORE)

    # Use standard_engine (not 'engine') and fuel_tank for INNER layer
    fuel_tank = create_component('fuel_tank', registries=registries)
    ship.add_component(fuel_tank, LayerType.INNER)

    railgun = create_component('railgun', registries=registries)
    ship.add_component(railgun, LayerType.OUTER)

    armor = create_component('armor_plate', registries=registries)
    ship.add_component(armor, LayerType.ARMOR)

    ship.recalculate_stats()
    return ship


@pytest.fixture
def minimal_ship_dict():
    """Minimal valid ship dictionary for deserialization."""
    return {
        "name": "MinimalShip",
        "ship_class": "Escort",
        "layers": {}
    }


@pytest.fixture
def full_ship_dict():
    """Complete ship dictionary with all fields.

    Uses Cruiser class which supports INNER layer.
    Uses standard_engine instead of 'engine'.
    """
    return {
        "_format_version": "2.0",
        "name": "FullShip",
        "ship_class": "Cruiser",
        "vehicle_type": "Ship",
        "theme_id": "Federation",
        "team_id": 3,
        "color": [128, 64, 255],
        "movement_policy": "kite_medium",
        "targeting_policy": "standard",
        "layers": {
            "CORE": [{"id": "bridge", "modifiers": []}],
            "INNER": [{"id": "fuel_tank", "modifiers": []}],  # fuel_tank instead of engine
            "OUTER": [{"id": "railgun", "modifiers": []}],
        },
        "resources": {
            "fuel": 100.0,
            "energy": 50.0,
            "ammo": 25.0,
        },
        "expected_stats": {}  # Don't validate stats in this fixture
    }


# =============================================================================
# Test: to_dict Serialization
# =============================================================================

class TestToDictSerialization:
    """Tests for ShipSerializer.to_dict() method."""

    def test_to_dict_includes_format_version(self, basic_ship):
        """to_dict should include _format_version field."""
        data = ShipSerializer.to_dict(basic_ship)
        assert "_format_version" in data
        assert data["_format_version"] == "2.0"

    def test_to_dict_serializes_basic_properties(self, basic_ship):
        """to_dict should serialize all basic ship properties."""
        data = ShipSerializer.to_dict(basic_ship)

        assert data["name"] == "TestShip"
        assert data["ship_class"] == "Escort"
        assert data["theme_id"] == "Federation"
        assert data["team_id"] == 1
        assert tuple(data["color"]) == (255, 128, 64)

    def test_to_dict_serializes_vehicle_type(self, basic_ship):
        """to_dict should serialize vehicle_type."""
        data = ShipSerializer.to_dict(basic_ship)
        assert "vehicle_type" in data
        assert data["vehicle_type"] == basic_ship.vehicle_type

    def test_to_dict_serializes_movement_policy(self, equipped_ship):
        """to_dict should serialize movement_policy."""
        data = ShipSerializer.to_dict(equipped_ship)
        assert data["movement_policy"] == "brawl_close"

    def test_to_dict_serializes_layers(self, equipped_ship):
        """to_dict should serialize components in each layer."""
        data = ShipSerializer.to_dict(equipped_ship)

        assert "layers" in data
        assert "CORE" in data["layers"]
        assert "INNER" in data["layers"]
        assert "OUTER" in data["layers"]
        assert "ARMOR" in data["layers"]

    def test_to_dict_excludes_hull_layer(self, basic_ship):
        """to_dict should not serialize the HULL layer explicitly."""
        data = ShipSerializer.to_dict(basic_ship)
        assert "HULL" not in data["layers"]

    def test_to_dict_serializes_resources(self, equipped_ship):
        """to_dict should serialize current resource values."""
        data = ShipSerializer.to_dict(equipped_ship)

        assert "resources" in data
        assert "fuel" in data["resources"]
        assert "energy" in data["resources"]
        assert "ammo" in data["resources"]

    def test_to_dict_serializes_expected_stats(self, equipped_ship):
        """to_dict should serialize expected stats for validation."""
        data = ShipSerializer.to_dict(equipped_ship)

        assert "expected_stats" in data
        expected = data["expected_stats"]

        # Check key stats are present
        assert "max_hp" in expected
        assert "max_fuel" in expected
        assert "max_energy" in expected
        assert "max_ammo" in expected
        assert "max_speed" in expected
        assert "acceleration_rate" in expected
        assert "turn_speed" in expected
        assert "total_thrust" in expected
        assert "mass" in expected
        assert "armor_hp_pool" in expected

    def test_to_dict_component_format(self, equipped_ship):
        """to_dict should serialize components as dicts with id and modifiers."""
        data = ShipSerializer.to_dict(equipped_ship)

        for layer_name, components in data["layers"].items():
            for comp in components:
                assert isinstance(comp, dict)
                assert "id" in comp
                # modifiers should only be present if component has modifiers
                if "modifiers" in comp:
                    assert isinstance(comp["modifiers"], list)

    def test_to_dict_excludes_hull_components(self, basic_ship, registries):
        """to_dict should not include hull_* components in any layer."""
        # Add a component to OUTER layer
        railgun = create_component('railgun', registries=registries)
        basic_ship.add_component(railgun, LayerType.OUTER)

        data = ShipSerializer.to_dict(basic_ship)

        # Check no hull_ components in serialized data
        for layer_name, components in data["layers"].items():
            for comp in components:
                assert not comp["id"].startswith("hull_")


# =============================================================================
# Test: from_dict Deserialization
# =============================================================================

class TestFromDictDeserialization:
    """Tests for ShipSerializer.from_dict() method."""

    def test_from_dict_requires_registries(self, minimal_ship_dict):
        """from_dict should raise ValidationException if registries is None."""
        with pytest.raises(ValidationException):
            ShipSerializer.from_dict(minimal_ship_dict, registries=None)

    def test_from_dict_creates_ship(self, minimal_ship_dict, registries):
        """from_dict should create a Ship instance."""
        ship = ShipSerializer.from_dict(minimal_ship_dict, registries=registries)

        assert isinstance(ship, Ship)
        assert ship.name == "MinimalShip"

    def test_from_dict_handles_default_values(self, registries):
        """from_dict should use defaults for missing optional fields."""
        data = {"name": "DefaultsShip"}

        ship = ShipSerializer.from_dict(data, registries=registries)

        assert ship.name == "DefaultsShip"
        assert ship.ship_class == "Escort"  # default
        assert ship.theme_id == "Federation"  # default
        assert ship.team_id == 0  # default
        assert ship.movement_policy == "kite_max"  # default

    def test_from_dict_restores_basic_properties(self, full_ship_dict, registries):
        """from_dict should restore all basic ship properties."""
        ship = ShipSerializer.from_dict(full_ship_dict, registries=registries)

        assert ship.name == "FullShip"
        assert ship.ship_class == "Cruiser"
        assert ship.theme_id == "Federation"
        assert ship.team_id == 3
        assert tuple(ship.color) == (128, 64, 255)
        assert ship.movement_policy == "kite_medium"

    def test_from_dict_converts_color_list_to_tuple(self, registries):
        """from_dict should convert color list to tuple."""
        data = {
            "name": "ColorTest",
            "color": [100, 150, 200]
        }

        ship = ShipSerializer.from_dict(data, registries=registries)

        # Color should be a tuple
        assert tuple(ship.color) == (100, 150, 200)

    def test_from_dict_handles_color_tuple(self, registries):
        """from_dict should accept color as tuple."""
        data = {
            "name": "ColorTupleTest",
            "color": (50, 100, 150)
        }

        ship = ShipSerializer.from_dict(data, registries=registries)

        assert tuple(ship.color) == (50, 100, 150)

    def test_from_dict_loads_components(self, full_ship_dict, registries):
        """from_dict should load components into layers."""
        ship = ShipSerializer.from_dict(full_ship_dict, registries=registries)

        # Check components were loaded
        core_ids = [c.id for c in ship.layers[LayerType.CORE].components]
        assert "bridge" in core_ids

        inner_ids = [c.id for c in ship.layers[LayerType.INNER].components]
        assert "fuel_tank" in inner_ids

        outer_ids = [c.id for c in ship.layers[LayerType.OUTER].components]
        assert "railgun" in outer_ids

    def test_from_dict_calls_recalculate_stats(self, minimal_ship_dict, registries):
        """from_dict should call recalculate_stats on the ship."""
        with patch.object(Ship, 'recalculate_stats') as mock_recalc:
            ShipSerializer.from_dict(minimal_ship_dict, registries=registries)
            mock_recalc.assert_called_once()

    def test_from_dict_stores_registries(self, minimal_ship_dict, registries):
        """from_dict should store registries on the created ship."""
        ship = ShipSerializer.from_dict(minimal_ship_dict, registries=registries)

        assert ship._registries is registries


# =============================================================================
# Test: Round-trip (serialize -> deserialize)
# =============================================================================

class TestRoundTrip:
    """Tests for serialize/deserialize round-trip consistency."""

    def test_roundtrip_preserves_name(self, basic_ship, registries):
        """Round-trip should preserve ship name."""
        data = ShipSerializer.to_dict(basic_ship)
        restored = ShipSerializer.from_dict(data, registries=registries)

        assert restored.name == basic_ship.name

    def test_roundtrip_preserves_ship_class(self, basic_ship, registries):
        """Round-trip should preserve ship class."""
        data = ShipSerializer.to_dict(basic_ship)
        restored = ShipSerializer.from_dict(data, registries=registries)

        assert restored.ship_class == basic_ship.ship_class

    def test_roundtrip_preserves_theme_id(self, basic_ship, registries):
        """Round-trip should preserve theme_id."""
        data = ShipSerializer.to_dict(basic_ship)
        restored = ShipSerializer.from_dict(data, registries=registries)

        assert restored.theme_id == basic_ship.theme_id

    def test_roundtrip_preserves_team_id(self, basic_ship, registries):
        """Round-trip should preserve team_id."""
        data = ShipSerializer.to_dict(basic_ship)
        restored = ShipSerializer.from_dict(data, registries=registries)

        assert restored.team_id == basic_ship.team_id

    def test_roundtrip_preserves_color(self, basic_ship, registries):
        """Round-trip should preserve color."""
        data = ShipSerializer.to_dict(basic_ship)
        restored = ShipSerializer.from_dict(data, registries=registries)

        assert tuple(restored.color) == tuple(basic_ship.color)

    def test_roundtrip_preserves_movement_policy(self, equipped_ship, registries):
        """Round-trip should preserve movement_policy."""
        data = ShipSerializer.to_dict(equipped_ship)
        restored = ShipSerializer.from_dict(data, registries=registries)

        assert restored.movement_policy == equipped_ship.movement_policy

    def test_roundtrip_preserves_component_count(self, equipped_ship, registries):
        """Round-trip should preserve component counts in each layer."""
        original_counts = {}
        # Only check layers that exist on this ship
        for layer_type in equipped_ship.layers.keys():
            if layer_type == LayerType.HULL:
                continue  # Skip HULL as it's auto-equipped
            original_counts[layer_type] = len(equipped_ship.layers[layer_type].components)

        data = ShipSerializer.to_dict(equipped_ship)
        restored = ShipSerializer.from_dict(data, registries=registries)

        for layer_type, expected_count in original_counts.items():
            actual_count = len(restored.layers[layer_type].components)
            assert actual_count == expected_count, f"Layer {layer_type.name}: expected {expected_count}, got {actual_count}"

    def test_roundtrip_preserves_component_ids(self, equipped_ship, registries):
        """Round-trip should preserve component IDs."""
        original_ids = {}
        # Only check layers that exist on this ship
        for layer_type in equipped_ship.layers.keys():
            if layer_type == LayerType.HULL:
                continue  # Skip HULL as it's auto-equipped
            original_ids[layer_type] = [c.id for c in equipped_ship.layers[layer_type].components]

        data = ShipSerializer.to_dict(equipped_ship)
        restored = ShipSerializer.from_dict(data, registries=registries)

        for layer_type, expected_ids in original_ids.items():
            actual_ids = [c.id for c in restored.layers[layer_type].components]
            assert actual_ids == expected_ids

    def test_roundtrip_preserves_hull(self, basic_ship, registries):
        """Round-trip should preserve hull (auto-equipped based on ship_class)."""
        original_hull_id = basic_ship.layers[LayerType.HULL].components[0].id

        data = ShipSerializer.to_dict(basic_ship)
        restored = ShipSerializer.from_dict(data, registries=registries)

        assert len(restored.layers[LayerType.HULL].components) == 1
        assert restored.layers[LayerType.HULL].components[0].id == original_hull_id

    def test_roundtrip_preserves_stats(self, equipped_ship, registries):
        """Round-trip should produce consistent calculated stats."""
        data = ShipSerializer.to_dict(equipped_ship)
        restored = ShipSerializer.from_dict(data, registries=registries)

        assert restored.max_hp == equipped_ship.max_hp
        assert restored.mass == pytest.approx(equipped_ship.mass, abs=0.1)
        assert restored.max_speed == pytest.approx(equipped_ship.max_speed, abs=0.1)


# =============================================================================
# Test: Edge Cases
# =============================================================================

class TestEdgeCases:
    """Tests for edge cases and error handling."""

    def test_from_dict_empty_layers(self, registries):
        """from_dict should handle empty layers dict."""
        data = {
            "name": "EmptyLayersShip",
            "layers": {}
        }

        ship = ShipSerializer.from_dict(data, registries=registries)

        assert ship is not None
        assert ship.name == "EmptyLayersShip"

    def test_from_dict_no_layers_key(self, registries):
        """from_dict should handle missing layers key."""
        data = {"name": "NoLayersShip"}

        ship = ShipSerializer.from_dict(data, registries=registries)

        assert ship is not None
        assert ship.name == "NoLayersShip"

    def test_from_dict_unknown_layer_type(self, registries):
        """from_dict should skip unknown layer types."""
        data = {
            "name": "UnknownLayerShip",
            "layers": {
                "UNKNOWN_LAYER": [{"id": "bridge", "modifiers": []}]
            }
        }

        # Should not raise - just skips unknown layer
        ship = ShipSerializer.from_dict(data, registries=registries)
        assert ship is not None

    def test_from_dict_unknown_component_id(self, registries):
        """from_dict should skip unknown component IDs."""
        data = {
            "name": "UnknownComponentShip",
            "layers": {
                "CORE": [{"id": "nonexistent_component", "modifiers": []}]
            }
        }

        # Should not raise - just skips unknown component
        ship = ShipSerializer.from_dict(data, registries=registries)

        # Check that no component was added
        core_ids = [c.id for c in ship.layers[LayerType.CORE].components]
        assert "nonexistent_component" not in core_ids

    def test_from_dict_invalid_component_entry_raises(self, registries):
        """from_dict should raise ValueError for non-dict component entry."""
        data = {
            "name": "InvalidEntryShip",
            "layers": {
                "CORE": ["bridge"]  # Should be dict, not string
            }
        }

        with pytest.raises(ValidationException):
            ShipSerializer.from_dict(data, registries=registries)

    def test_from_dict_empty_resources(self, registries):
        """from_dict should handle empty resources dict."""
        data = {
            "name": "EmptyResourcesShip",
            "resources": {}
        }

        ship = ShipSerializer.from_dict(data, registries=registries)
        assert ship is not None

    def test_from_dict_missing_resources(self, registries):
        """from_dict should handle missing resources key."""
        data = {"name": "NoResourcesShip"}

        ship = ShipSerializer.from_dict(data, registries=registries)
        assert ship is not None

    def test_from_dict_null_resource_value(self, registries):
        """from_dict should handle null resource values."""
        data = {
            "name": "NullResourceShip",
            "resources": {
                "fuel": None,
                "energy": 50.0,
                "ammo": None
            }
        }

        ship = ShipSerializer.from_dict(data, registries=registries)
        assert ship is not None

    def test_from_dict_empty_expected_stats(self, registries):
        """from_dict should handle empty expected_stats dict."""
        data = {
            "name": "EmptyStatsShip",
            "expected_stats": {}
        }

        ship = ShipSerializer.from_dict(data, registries=registries)
        assert ship is not None

    def test_from_dict_missing_name_uses_default(self, registries):
        """from_dict should use 'Unnamed' for missing name."""
        data = {}

        ship = ShipSerializer.from_dict(data, registries=registries)

        assert ship.name == "Unnamed"


# =============================================================================
# Test: _load_components Helper
# =============================================================================

class TestLoadComponents:
    """Tests for ShipSerializer._load_components() helper."""

    def test_load_components_adds_to_correct_layer(self, basic_ship, registries):
        """_load_components should add components to correct layers."""
        data = {
            "layers": {
                "CORE": [{"id": "bridge", "modifiers": []}],
                "OUTER": [{"id": "railgun", "modifiers": []}]
            }
        }

        ShipSerializer._load_components(basic_ship, data, registries)

        core_ids = [c.id for c in basic_ship.layers[LayerType.CORE].components]
        assert "bridge" in core_ids

        outer_ids = [c.id for c in basic_ship.layers[LayerType.OUTER].components]
        assert "railgun" in outer_ids

    def test_load_components_applies_modifiers(self, basic_ship, registries):
        """_load_components should apply modifiers to components."""
        data = {
            "layers": {
                "CORE": [{"id": "bridge", "modifiers": [{"id": "simple_size_mount", "value": 1.5}]}]
            }
        }

        ShipSerializer._load_components(basic_ship, data, registries)

        bridges = [c for c in basic_ship.layers[LayerType.CORE].components if c.id == "bridge"]
        assert len(bridges) == 1

        bridge = bridges[0]
        modifier = bridge.get_modifier("simple_size_mount")
        assert modifier is not None
        assert modifier.value == 1.5

    def test_load_components_skips_unknown_modifiers(self, basic_ship, registries):
        """_load_components should skip unknown modifier IDs with warning."""
        data = {
            "layers": {
                "CORE": [{"id": "bridge", "modifiers": [{"id": "nonexistent_modifier", "value": 1.0}]}]
            }
        }

        # Should not raise - just logs warning
        ShipSerializer._load_components(basic_ship, data, registries)

    def test_load_components_sets_registries_on_component(self, basic_ship, registries):
        """_load_components should set registries on created components."""
        data = {
            "layers": {
                "CORE": [{"id": "bridge", "modifiers": []}]
            }
        }

        ShipSerializer._load_components(basic_ship, data, registries)

        bridges = [c for c in basic_ship.layers[LayerType.CORE].components if c.id == "bridge"]
        assert bridges[0]._registries is registries

    def test_load_components_handles_empty_modifiers_list(self, basic_ship, registries):
        """_load_components should handle empty modifiers list."""
        data = {
            "layers": {
                "CORE": [{"id": "bridge", "modifiers": []}]
            }
        }

        ShipSerializer._load_components(basic_ship, data, registries)

        bridges = [c for c in basic_ship.layers[LayerType.CORE].components if c.id == "bridge"]
        assert len(bridges) == 1

    def test_load_components_handles_no_modifiers_key(self, basic_ship, registries):
        """_load_components should handle missing modifiers key."""
        data = {
            "layers": {
                "CORE": [{"id": "bridge"}]  # No modifiers key
            }
        }

        ShipSerializer._load_components(basic_ship, data, registries)

        bridges = [c for c in basic_ship.layers[LayerType.CORE].components if c.id == "bridge"]
        assert len(bridges) == 1


# =============================================================================
# Test: _restore_resources Helper
# =============================================================================

class TestRestoreResources:
    """Tests for ShipSerializer._restore_resources() helper."""

    def test_restore_resources_sets_values(self, equipped_ship):
        """_restore_resources should set resource values from saved data."""
        # Get max values
        max_fuel = equipped_ship.resources.get_max_value("fuel")
        max_energy = equipped_ship.resources.get_max_value("energy")

        saved = {
            "fuel": min(50.0, max_fuel) if max_fuel > 0 else 0,
            "energy": min(75.0, max_energy) if max_energy > 0 else 0,
        }

        ShipSerializer._restore_resources(equipped_ship, saved)

        if max_fuel > 0:
            assert equipped_ship.resources.get_value("fuel") == pytest.approx(saved["fuel"], abs=0.1)
        if max_energy > 0:
            assert equipped_ship.resources.get_value("energy") == pytest.approx(saved["energy"], abs=0.1)

    def test_restore_resources_handles_empty_dict(self, basic_ship):
        """_restore_resources should handle empty saved resources dict."""
        # Should not raise
        ShipSerializer._restore_resources(basic_ship, {})

    def test_restore_resources_handles_none_dict(self, basic_ship):
        """_restore_resources should handle None saved resources."""
        # Should not raise (returns early)
        ShipSerializer._restore_resources(basic_ship, None)

    def test_restore_resources_skips_none_values(self, equipped_ship):
        """_restore_resources should skip None resource values."""
        saved = {
            "fuel": None,
            "energy": None,
        }

        # Should not raise
        ShipSerializer._restore_resources(equipped_ship, saved)


# =============================================================================
# Test: _verify_stats Helper
# =============================================================================

class TestVerifyStats:
    """Tests for ShipSerializer._verify_stats() helper."""

    def test_verify_stats_no_mismatches_when_stats_match(self, equipped_ship):
        """_verify_stats should find no mismatches when stats match."""
        # Get actual stats
        expected = {
            "max_hp": equipped_ship.max_hp,
            "mass": equipped_ship.mass,
            "max_speed": equipped_ship.max_speed,
        }

        ShipSerializer._verify_stats(equipped_ship, expected)

        assert equipped_ship._loading_warnings == []

    def test_verify_stats_detects_mismatch(self, equipped_ship):
        """_verify_stats should detect stat mismatches."""
        # Create expected stats that don't match
        expected = {
            "max_hp": equipped_ship.max_hp + 1000,  # Wrong HP
        }

        ShipSerializer._verify_stats(equipped_ship, expected)

        assert len(equipped_ship._loading_warnings) > 0
        assert any("max_hp" in w for w in equipped_ship._loading_warnings)

    def test_verify_stats_handles_empty_expected(self, basic_ship):
        """_verify_stats should handle empty expected stats dict."""
        ShipSerializer._verify_stats(basic_ship, {})

        # Should set _loading_warnings to empty list
        assert basic_ship._loading_warnings == []

    def test_verify_stats_handles_none_expected(self, basic_ship):
        """_verify_stats should handle None expected stats."""
        # Should return early without setting _loading_warnings
        ShipSerializer._verify_stats(basic_ship, None)

    def test_verify_stats_uses_tolerance(self, equipped_ship):
        """_verify_stats should use tolerance for floating-point comparisons."""
        # Get actual stats and add small delta within tolerance
        expected = {
            "max_speed": equipped_ship.max_speed + 0.05,  # Within 0.1 tolerance
        }

        ShipSerializer._verify_stats(equipped_ship, expected)

        # Should not report mismatch for small differences within tolerance
        speed_warnings = [w for w in equipped_ship._loading_warnings if "max_speed" in w]
        assert len(speed_warnings) == 0


# =============================================================================
# Test: Modifier Serialization
# =============================================================================

class TestModifierSerialization:
    """Tests for component modifier serialization/deserialization."""

    def test_modifier_roundtrip(self, registries):
        """Modifiers should survive round-trip serialization."""
        ship = Ship(
            name="ModifierTest",
            x=0, y=0,
            color=(255, 255, 255),
            registries=registries
        )

        # Add component with modifier
        bridge = create_component('bridge', registries=registries)
        bridge.add_modifier('simple_size_mount', 2.0)
        ship.add_component(bridge, LayerType.CORE)

        # Round-trip
        data = ShipSerializer.to_dict(ship)
        restored = ShipSerializer.from_dict(data, registries=registries)

        # Find bridge in restored ship
        restored_bridges = [c for c in restored.layers[LayerType.CORE].components if c.id == "bridge"]
        assert len(restored_bridges) == 1

        # Check modifier preserved
        modifier = restored_bridges[0].get_modifier('simple_size_mount')
        assert modifier is not None
        assert modifier.value == 2.0

    def test_multiple_modifiers_preserved(self, registries):
        """Multiple modifiers on same component should be preserved through round-trip."""
        ship = Ship(
            name="MultiModTest",
            x=0, y=0,
            color=(255, 255, 255),
            registries=registries
        )

        bridge = create_component('bridge', registries=registries)

        # Add a modifier before adding to ship
        bridge.add_modifier('simple_size_mount', 1.5)

        ship.add_component(bridge, LayerType.CORE)

        # Get the modifier count AFTER adding to ship (which may add additional modifiers)
        original_modifiers = ship.layers[LayerType.CORE].components[0].modifiers
        original_count = len(original_modifiers)
        original_modifier_ids = {m.definition.id for m in original_modifiers}

        # Round-trip
        data = ShipSerializer.to_dict(ship)
        restored = ShipSerializer.from_dict(data, registries=registries)

        restored_bridges = [c for c in restored.layers[LayerType.CORE].components if c.id == "bridge"]
        assert len(restored_bridges) == 1

        # Verify same number of modifiers
        assert len(restored_bridges[0].modifiers) == original_count

        # Verify the specific modifier we added is present
        restored_modifier_ids = {m.definition.id for m in restored_bridges[0].modifiers}
        assert 'simple_size_mount' in restored_modifier_ids
        assert original_modifier_ids == restored_modifier_ids


# =============================================================================
# Test: Multiple Components Per Layer
# =============================================================================

class TestMultipleComponents:
    """Tests for handling multiple components in a single layer."""

    def test_multiple_same_components_preserved(self, registries):
        """Multiple instances of same component type should be preserved."""
        ship = Ship(
            name="MultiCompTest",
            x=0, y=0,
            color=(255, 255, 255),
            registries=registries
        )

        # Add 3 railguns
        for _ in range(3):
            railgun = create_component('railgun', registries=registries)
            ship.add_component(railgun, LayerType.OUTER)

        original_count = len([c for c in ship.layers[LayerType.OUTER].components if c.id == 'railgun'])

        # Round-trip
        data = ShipSerializer.to_dict(ship)
        restored = ShipSerializer.from_dict(data, registries=registries)

        restored_count = len([c for c in restored.layers[LayerType.OUTER].components if c.id == 'railgun'])
        assert restored_count == original_count

    def test_different_components_in_same_layer(self, registries):
        """Different component types in same layer should all be preserved."""
        ship = Ship(
            name="MixedCompTest",
            x=0, y=0,
            color=(255, 255, 255),
            ship_class="Cruiser",  # Cruiser has INNER layer
            registries=registries
        )

        # Add different components to INNER layer
        fuel_tank = create_component('fuel_tank', registries=registries)
        ship.add_component(fuel_tank, LayerType.INNER)

        generator = create_component('generator', registries=registries)
        ship.add_component(generator, LayerType.INNER)

        # Round-trip
        data = ShipSerializer.to_dict(ship)
        restored = ShipSerializer.from_dict(data, registries=registries)

        inner_ids = [c.id for c in restored.layers[LayerType.INNER].components]
        assert 'fuel_tank' in inner_ids
        assert 'generator' in inner_ids
