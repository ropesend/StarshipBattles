"""
Tests for DesignMetadata
"""
import tempfile
import os
from unittest.mock import MagicMock
from game.strategy.data.design_metadata import DesignMetadata
from game.core.json_utils import save_json
from game.simulation.entities.layer_data import LayerData


class TestDesignMetadata:
    """Tests for DesignMetadata class"""

    def test_create_metadata_from_dict(self):
        """Can create metadata from dictionary"""
        data = {
            "design_id": "test_ship",
            "name": "Test Ship",
            "ship_class": "Escort",
            "vehicle_type": "Ship",
            "mass": 1000.0,
            "combat_power": 500.0,
            "resource_cost": {"metal": 100, "energy": 50},
            "created_date": "2026-01-17T10:00:00",
            "last_modified": "2026-01-17T12:00:00",
            "is_obsolete": False,
            "times_built": 3,
            "theme_id": "Federation"
        }

        metadata = DesignMetadata.from_dict(data)

        assert metadata.design_id == "test_ship"
        assert metadata.name == "Test Ship"
        assert metadata.ship_class == "Escort"
        assert metadata.vehicle_type == "Ship"
        assert metadata.mass == 1000.0
        assert metadata.combat_power == 500.0
        assert metadata.resource_cost == {"metal": 100, "energy": 50}
        assert metadata.times_built == 3
        assert metadata.is_obsolete is False

    def test_to_dict_serialization(self):
        """Can serialize metadata to dictionary"""
        metadata = DesignMetadata(
            design_id="cruiser_mk2",
            name="Cruiser Mk II",
            ship_class="Cruiser",
            vehicle_type="Ship",
            mass=5000.0,
            combat_power=2000.0,
            resource_cost={"metal": 500, "energy": 200},
            created_date="2026-01-17T10:00:00",
            last_modified="2026-01-17T12:00:00",
            is_obsolete=True,
            times_built=5,
            theme_id="Empire"
        )

        data = metadata.to_dict()

        assert data["design_id"] == "cruiser_mk2"
        assert data["name"] == "Cruiser Mk II"
        assert data["ship_class"] == "Cruiser"
        assert data["times_built"] == 5
        assert data["is_obsolete"] is True

    def test_from_design_file(self):
        """Can load metadata from design file"""
        # Create temporary design file
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = os.path.join(tmpdir, "test_design.json")

            design_data = {
                "name": "Test Fighter",
                "ship_class": "Fighter",
                "vehicle_type": "Fighter",
                "theme_id": "Rebellion",
                "layers": {
                    "core": [
                        {
                            "id": "laser_cannon",
                            "category": "weapon",
                            "damage": 100,
                            "rate_of_fire": 2,
                            "cost": {"metal": 10, "energy": 5}
                        }
                    ]
                },
                "expected_stats": {
                    "mass": 50.0
                },
                "_metadata": {
                    "is_obsolete": False,
                    "times_built": 2
                }
            }

            save_json(filepath, design_data)

            # Load metadata
            metadata = DesignMetadata.from_design_file(filepath, "test_design")

            assert metadata.design_id == "test_design"
            assert metadata.name == "Test Fighter"
            assert metadata.ship_class == "Fighter"
            assert metadata.vehicle_type == "Fighter"
            assert metadata.mass == 50.0
            assert metadata.times_built == 2
            assert metadata.is_obsolete is False
            # Combat power should be calculated from weapon
            assert metadata.combat_power > 0

    def test_from_ship_instance(self):
        """Can create metadata from Ship instance"""
        # Mock ship
        ship = MagicMock()
        ship.name = "Destroyer X"
        ship.ship_class = "Destroyer"
        ship.vehicle_type = "Ship"
        ship.mass = 3000.0
        ship.theme_id = "Alliance"

        # Mock layers with components
        weapon = MagicMock()
        weapon.category = "weapon"
        weapon.damage = 200
        weapon.rate_of_fire = 1
        weapon.cost = {"metal": 50, "energy": 25}

        armor = MagicMock()
        armor.category = "armor"
        armor.hp = 1000
        armor.cost = {"metal": 100}

        ship.layers = {
            "outer": LayerData(components=[weapon, armor])
        }

        # Create metadata
        metadata = DesignMetadata.from_ship(ship, "destroyer_x")

        assert metadata.design_id == "destroyer_x"
        assert metadata.name == "Destroyer X"
        assert metadata.ship_class == "Destroyer"
        assert metadata.mass == 3000.0
        assert metadata.times_built == 0  # New design
        assert metadata.is_obsolete is False
        # Check resource costs calculated
        assert metadata.resource_cost["metal"] == 150
        assert metadata.resource_cost["energy"] == 25
        # Combat power calculated
        assert metadata.combat_power > 0

    def test_combat_power_calculation(self):
        """Combat power is calculated correctly"""
        design_data = {
            "layers": {
                "core": [
                    {
                        "category": "weapon",
                        "damage": 100,
                        "rate_of_fire": 2
                    },
                    {
                        "category": "armor",
                        "hp": 500
                    }
                ]
            }
        }

        power = DesignMetadata._calculate_combat_power(design_data)

        # Expected: (100 * 10) + (2 * 5) + (500 * 0.5) = 1000 + 10 + 250 = 1260
        assert power == 1260.0

    def test_resource_cost_calculation(self):
        """Resource costs are summed correctly"""
        design_data = {
            "layers": {
                "core": [
                    {"cost": {"metal": 10, "energy": 5}},
                    {"cost": {"metal": 20, "energy": 10}},
                    {"cost": {"crystals": 5}}
                ]
            }
        }

        costs = DesignMetadata._calculate_resource_cost(design_data)

        assert costs["metal"] == 30
        assert costs["energy"] == 15
        assert costs["crystals"] == 5

    def test_embed_metadata_in_ship_data(self):
        """Can embed metadata into ship data dict"""
        metadata = DesignMetadata(
            design_id="test",
            name="Test",
            ship_class="Escort",
            vehicle_type="Ship",
            mass=1000.0,
            combat_power=500.0,
            is_obsolete=True,
            times_built=10,
            created_date="2026-01-17T10:00:00",
            last_modified="2026-01-17T12:00:00"
        )

        ship_data = {"name": "Test", "ship_class": "Escort"}
        result = metadata.embed_in_ship_data(ship_data)

        assert "_metadata" in result
        assert result["_metadata"]["is_obsolete"] is True
        assert result["_metadata"]["times_built"] == 10


class TestDesignMetadataFromDict:
    """Tests for DesignMetadata.from_dict edge cases."""

    def test_from_dict_missing_optional_fields(self):
        """from_dict handles missing optional fields with defaults."""
        data = {
            "design_id": "minimal_ship",
            "name": "Minimal",
        }

        metadata = DesignMetadata.from_dict(data)

        assert metadata.design_id == "minimal_ship"
        assert metadata.name == "Minimal"
        assert metadata.ship_class == "Unknown"
        assert metadata.vehicle_type == "Ship"
        assert metadata.mass == 0.0
        assert metadata.combat_power == 0.0
        assert metadata.resource_cost == {}
        assert metadata.is_obsolete is False
        assert metadata.times_built == 0

    def test_from_dict_sprite_preview_none(self):
        """from_dict handles None sprite_preview."""
        data = {
            "design_id": "test",
            "name": "Test",
            "sprite_preview": None
        }

        metadata = DesignMetadata.from_dict(data)

        assert metadata.sprite_preview is None

    def test_from_dict_empty_resource_cost(self):
        """from_dict handles empty resource_cost."""
        data = {
            "design_id": "test",
            "name": "Test",
            "resource_cost": {}
        }

        metadata = DesignMetadata.from_dict(data)

        assert metadata.resource_cost == {}


class TestDesignMetadataFromDesignFile:
    """Tests for DesignMetadata.from_design_file edge cases."""

    def test_from_design_file_missing_optional_fields(self):
        """from_design_file handles missing optional fields."""
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = os.path.join(tmpdir, "minimal.json")
            design_data = {
                "name": "Minimal Design"
                # No ship_class, vehicle_type, layers, expected_stats
            }
            save_json(filepath, design_data)

            metadata = DesignMetadata.from_design_file(filepath, "minimal")

            assert metadata.name == "Minimal Design"
            assert metadata.ship_class == "Unknown"
            assert metadata.vehicle_type == "Ship"
            assert metadata.mass == 0.0
            assert metadata.combat_power == 0.0

    def test_from_design_file_no_expected_stats(self):
        """from_design_file handles missing expected_stats."""
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = os.path.join(tmpdir, "no_stats.json")
            design_data = {
                "name": "No Stats Ship",
                "ship_class": "Frigate"
            }
            save_json(filepath, design_data)

            metadata = DesignMetadata.from_design_file(filepath, "no_stats")

            assert metadata.mass == 0.0

    def test_from_design_file_no_metadata_section(self):
        """from_design_file handles missing _metadata section."""
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = os.path.join(tmpdir, "no_meta.json")
            design_data = {
                "name": "No Meta Ship",
                "ship_class": "Escort"
            }
            save_json(filepath, design_data)

            metadata = DesignMetadata.from_design_file(filepath, "no_meta")

            assert metadata.is_obsolete is False
            assert metadata.times_built == 0

    def test_from_design_file_empty_layers(self):
        """from_design_file handles empty layers dict."""
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = os.path.join(tmpdir, "empty_layers.json")
            design_data = {
                "name": "Empty Layers",
                "layers": {}
            }
            save_json(filepath, design_data)

            metadata = DesignMetadata.from_design_file(filepath, "empty_layers")

            assert metadata.combat_power == 0.0
            assert metadata.resource_cost == {}


class TestDesignMetadataFromShip:
    """Tests for DesignMetadata.from_ship edge cases."""

    def test_from_ship_missing_vehicle_type(self):
        """from_ship handles ship without vehicle_type attribute."""
        ship = MagicMock(spec=['name', 'ship_class', 'mass', 'layers'])
        ship.name = "Legacy Ship"
        ship.ship_class = "Destroyer"
        ship.mass = 2000.0
        ship.layers = {}

        metadata = DesignMetadata.from_ship(ship, "legacy_ship")

        assert metadata.vehicle_type == "Ship"

    def test_from_ship_missing_theme_id(self):
        """from_ship handles ship without theme_id attribute."""
        ship = MagicMock(spec=['name', 'ship_class', 'mass', 'layers'])
        ship.name = "No Theme Ship"
        ship.ship_class = "Frigate"
        ship.mass = 1500.0
        ship.layers = {}

        metadata = DesignMetadata.from_ship(ship, "no_theme")

        assert metadata.theme_id == ""

    def test_from_ship_empty_layers(self):
        """from_ship handles empty layers."""
        ship = MagicMock()
        ship.name = "Empty Ship"
        ship.ship_class = "Escort"
        ship.mass = 500.0
        ship.layers = {}

        metadata = DesignMetadata.from_ship(ship, "empty")

        assert metadata.combat_power == 0.0
        assert metadata.resource_cost == {}

    def test_from_ship_component_without_cost(self):
        """from_ship handles components without cost attribute."""
        ship = MagicMock()
        ship.name = "No Cost Ship"
        ship.ship_class = "Fighter"
        ship.mass = 100.0
        ship.vehicle_type = "Fighter"
        ship.theme_id = "Test"

        # Component without cost
        comp = MagicMock(spec=['category'])
        comp.category = "engine"

        ship.layers = {
            "core": LayerData(components=[comp])
        }

        metadata = DesignMetadata.from_ship(ship, "no_cost")

        # Should not crash, just skip the component
        assert metadata.resource_cost == {}

    def test_from_ship_integer_cost(self):
        """from_ship handles integer cost (single value) on components."""
        ship = MagicMock()
        ship.name = "Int Cost Ship"
        ship.ship_class = "Escort"
        ship.mass = 800.0
        ship.vehicle_type = "Ship"
        ship.theme_id = ""

        comp = MagicMock()
        comp.category = "engine"
        comp.cost = 50  # Integer, not dict

        ship.layers = {
            "core": LayerData(components=[comp])
        }

        metadata = DesignMetadata.from_ship(ship, "int_cost")

        assert metadata.resource_cost.get("minerals", 0) == 50


class TestDesignMetadataCombatPower:
    """Tests for combat power calculation edge cases."""

    def test_calculate_combat_power_empty_layers(self):
        """Combat power is 0 for empty layers."""
        design_data = {"layers": {}}

        power = DesignMetadata._calculate_combat_power(design_data)

        assert power == 0.0

    def test_calculate_combat_power_no_layers_key(self):
        """Combat power is 0 when layers key missing."""
        design_data = {}

        power = DesignMetadata._calculate_combat_power(design_data)

        assert power == 0.0

    def test_calculate_combat_power_non_combat_components(self):
        """Combat power ignores non-combat components."""
        design_data = {
            "layers": {
                "core": [
                    {"category": "engine", "thrust": 100},
                    {"category": "sensor", "range": 50}
                ]
            }
        }

        power = DesignMetadata._calculate_combat_power(design_data)

        assert power == 0.0

    def test_calculate_combat_power_missing_damage(self):
        """Combat power handles weapon without damage field."""
        design_data = {
            "layers": {
                "core": [
                    {"category": "weapon", "rate_of_fire": 3}
                ]
            }
        }

        power = DesignMetadata._calculate_combat_power(design_data)

        # Only rate_of_fire contributes: 3 * 5 = 15
        assert power == 15.0


class TestDesignMetadataResourceCost:
    """Tests for resource cost calculation edge cases."""

    def test_calculate_resource_cost_no_cost_field(self):
        """Resource cost skips components without cost field."""
        design_data = {
            "layers": {
                "core": [
                    {"id": "engine_1"},
                    {"id": "sensor_1"}
                ]
            }
        }

        costs = DesignMetadata._calculate_resource_cost(design_data)

        assert costs == {}

    def test_calculate_resource_cost_empty_cost(self):
        """Resource cost handles empty cost dict."""
        design_data = {
            "layers": {
                "core": [
                    {"id": "test", "cost": {}}
                ]
            }
        }

        costs = DesignMetadata._calculate_resource_cost(design_data)

        assert costs == {}


class TestDesignMetadataSerialization:
    """Tests for to_dict serialization edge cases."""

    def test_to_dict_all_fields(self):
        """to_dict includes all fields."""
        metadata = DesignMetadata(
            design_id="full_test",
            name="Full Test",
            ship_class="Cruiser",
            vehicle_type="Ship",
            mass=5000.0,
            combat_power=2500.0,
            resource_cost={"metal": 500},
            created_date="2026-01-01T00:00:00",
            last_modified="2026-01-02T00:00:00",
            is_obsolete=True,
            times_built=25,
            theme_id="Empire",
            sprite_preview="some_path"
        )

        data = metadata.to_dict()

        assert data["design_id"] == "full_test"
        assert data["sprite_preview"] == "some_path"
        assert data["is_obsolete"] is True
        assert data["times_built"] == 25

    def test_to_dict_sprite_preview_none(self):
        """to_dict correctly serializes None sprite_preview."""
        metadata = DesignMetadata(
            design_id="no_preview",
            name="No Preview",
            ship_class="Escort",
            vehicle_type="Ship",
            mass=100.0,
            combat_power=50.0
        )

        data = metadata.to_dict()

        assert data["sprite_preview"] is None
