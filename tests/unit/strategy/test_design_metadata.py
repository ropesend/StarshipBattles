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
