"""
Tests for DesignMetadata
"""
import unittest
import tempfile
import os
from datetime import datetime
from unittest.mock import MagicMock
from game.strategy.data.design_metadata import DesignMetadata
from game.core.json_utils import save_json


class TestDesignMetadata(unittest.TestCase):
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

        self.assertEqual(metadata.design_id, "test_ship")
        self.assertEqual(metadata.name, "Test Ship")
        self.assertEqual(metadata.ship_class, "Escort")
        self.assertEqual(metadata.vehicle_type, "Ship")
        self.assertEqual(metadata.mass, 1000.0)
        self.assertEqual(metadata.combat_power, 500.0)
        self.assertEqual(metadata.resource_cost, {"metal": 100, "energy": 50})
        self.assertEqual(metadata.times_built, 3)
        self.assertFalse(metadata.is_obsolete)

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

        self.assertEqual(data["design_id"], "cruiser_mk2")
        self.assertEqual(data["name"], "Cruiser Mk II")
        self.assertEqual(data["ship_class"], "Cruiser")
        self.assertEqual(data["times_built"], 5)
        self.assertTrue(data["is_obsolete"])

    def test_from_design_file(self):
        """Can load metadata from design file"""
        # Create temporary design file
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = os.path.join(tmpdir, "test_design.json")

            design_data = {
                "name": "Test Fighter",
                "ship_class": "Fighter",
                "vehicle_type": "Fighter",
                "mass": 50.0,
                "theme_id": "Rebellion",
                "layers": {
                    "core": {
                        "components": [
                            {
                                "id": "laser_cannon",
                                "category": "weapon",
                                "damage": 100,
                                "rate_of_fire": 2,
                                "cost": {"metal": 10, "energy": 5}
                            }
                        ]
                    }
                },
                "_metadata": {
                    "is_obsolete": False,
                    "times_built": 2
                }
            }

            save_json(filepath, design_data)

            # Load metadata
            metadata = DesignMetadata.from_design_file(filepath, "test_design")

            self.assertEqual(metadata.design_id, "test_design")
            self.assertEqual(metadata.name, "Test Fighter")
            self.assertEqual(metadata.ship_class, "Fighter")
            self.assertEqual(metadata.vehicle_type, "Fighter")
            self.assertEqual(metadata.mass, 50.0)
            self.assertEqual(metadata.times_built, 2)
            self.assertFalse(metadata.is_obsolete)
            # Combat power should be calculated from weapon
            self.assertGreater(metadata.combat_power, 0)

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
            "outer": {
                "components": [weapon, armor]
            }
        }

        # Create metadata
        metadata = DesignMetadata.from_ship(ship, "destroyer_x")

        self.assertEqual(metadata.design_id, "destroyer_x")
        self.assertEqual(metadata.name, "Destroyer X")
        self.assertEqual(metadata.ship_class, "Destroyer")
        self.assertEqual(metadata.mass, 3000.0)
        self.assertEqual(metadata.times_built, 0)  # New design
        self.assertFalse(metadata.is_obsolete)
        # Check resource costs calculated
        self.assertEqual(metadata.resource_cost["metal"], 150)
        self.assertEqual(metadata.resource_cost["energy"], 25)
        # Combat power calculated
        self.assertGreater(metadata.combat_power, 0)

    def test_combat_power_calculation(self):
        """Combat power is calculated correctly"""
        design_data = {
            "layers": {
                "core": {
                    "components": [
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
        }

        power = DesignMetadata._calculate_combat_power(design_data)

        # Expected: (100 * 10) + (2 * 5) + (500 * 0.5) = 1000 + 10 + 250 = 1260
        self.assertEqual(power, 1260.0)

    def test_resource_cost_calculation(self):
        """Resource costs are summed correctly"""
        design_data = {
            "layers": {
                "core": {
                    "components": [
                        {"cost": {"metal": 10, "energy": 5}},
                        {"cost": {"metal": 20, "energy": 10}},
                        {"cost": {"crystals": 5}}
                    ]
                }
            }
        }

        costs = DesignMetadata._calculate_resource_cost(design_data)

        self.assertEqual(costs["metal"], 30)
        self.assertEqual(costs["energy"], 15)
        self.assertEqual(costs["crystals"], 5)

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

        self.assertIn("_metadata", result)
        self.assertTrue(result["_metadata"]["is_obsolete"])
        self.assertEqual(result["_metadata"]["times_built"], 10)


if __name__ == '__main__':
    unittest.main()
