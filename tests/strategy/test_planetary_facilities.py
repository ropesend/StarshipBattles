import unittest
from game.strategy.data.planet import Planet, PlanetType, PlanetaryFacility
from game.strategy.data.hex_math import HexCoord


class TestPlanetaryFacilities(unittest.TestCase):
    """Test planetary facility system."""

    def setUp(self):
        """Create a test planet."""
        self.planet = Planet(
            name="Test Colony",
            location=HexCoord(0, 0),
            orbit_distance=3,
            mass=5.97e24,
            radius=6371000,
            surface_area=5.1e14,
            density=5515,
            surface_gravity=9.81,
            surface_pressure=101325,
            surface_temperature=288,
            surface_water=0.7,
            tectonic_activity=0.1,
            magnetic_field=1.0,
            atmosphere={'N2': 78000.0, 'O2': 21000.0},
            planet_type=PlanetType.TERRESTRIAL
        )
        self.planet.owner_id = 0

    def test_add_facility_to_planet(self):
        """Verify adding a PlanetaryFacility to planet.facilities list."""
        facility = PlanetaryFacility(
            instance_id="test-123",
            design_id="mining_complex_mk1",
            name="Mining Complex",
            design_data={"name": "Mining Complex", "layers": {}}
        )

        self.planet.facilities.append(facility)

        self.assertEqual(len(self.planet.facilities), 1)
        self.assertEqual(self.planet.facilities[0].instance_id, "test-123")
        self.assertEqual(self.planet.facilities[0].name, "Mining Complex")

    def test_facility_has_design_data(self):
        """Verify facility stores full design JSON."""
        design_data = {
            "name": "Resource Harvester",
            "vehicle_class": "Planetary Complex (Tier 1)",
            "layers": {
                "outer": {
                    "components": [
                        {
                            "id": "metal_harvester",
                            "abilities": {
                                "ResourceHarvester": {
                                    "resource_type": "Metals",
                                    "base_harvest_rate": 10.0
                                }
                            }
                        }
                    ]
                }
            }
        }

        facility = PlanetaryFacility(
            instance_id="harvest-001",
            design_id="harvester_complex",
            name="Harvester Complex",
            design_data=design_data
        )

        self.planet.facilities.append(facility)

        stored_data = self.planet.facilities[0].design_data
        self.assertEqual(stored_data["name"], "Resource Harvester")
        self.assertIn("layers", stored_data)
        self.assertIn("outer", stored_data["layers"])

    def test_has_space_shipyard_property(self):
        """Verify has_space_shipyard detects shipyard in facilities."""
        shipyard_data = {
            "name": "Orbital Shipyard",
            "layers": {
                "core": {
                    "components": [
                        {
                            "id": "space_shipyard",
                            "abilities": {
                                "SpaceShipyard": {
                                    "construction_speed_bonus": 1.0,
                                    "max_ship_mass": 100000
                                }
                            }
                        }
                    ]
                }
            }
        }

        facility = PlanetaryFacility(
            instance_id="shipyard-001",
            design_id="orbital_shipyard_mk1",
            name="Orbital Shipyard",
            design_data=shipyard_data,
            is_operational=True
        )

        self.planet.facilities.append(facility)

        self.assertTrue(self.planet.has_space_shipyard)

    def test_has_space_shipyard_false_when_none(self):
        """Verify has_space_shipyard returns False when no shipyard exists."""
        # Add a non-shipyard facility
        harvester_data = {
            "name": "Metal Harvester",
            "layers": {
                "outer": {
                    "components": [
                        {
                            "id": "metal_harvester",
                            "abilities": {
                                "ResourceHarvester": {
                                    "resource_type": "Metals"
                                }
                            }
                        }
                    ]
                }
            }
        }

        facility = PlanetaryFacility(
            instance_id="harvester-001",
            design_id="metal_harvester_complex",
            name="Metal Harvester",
            design_data=harvester_data
        )

        self.planet.facilities.append(facility)

        self.assertFalse(self.planet.has_space_shipyard)

    def test_has_space_shipyard_false_when_not_operational(self):
        """Verify damaged shipyard doesn't count."""
        shipyard_data = {
            "name": "Damaged Shipyard",
            "layers": {
                "core": {
                    "components": [
                        {
                            "id": "space_shipyard",
                            "abilities": {
                                "SpaceShipyard": {
                                    "construction_speed_bonus": 1.0
                                }
                            }
                        }
                    ]
                }
            }
        }

        facility = PlanetaryFacility(
            instance_id="shipyard-damaged",
            design_id="orbital_shipyard_mk1",
            name="Damaged Shipyard",
            design_data=shipyard_data,
            is_operational=False  # Damaged!
        )

        self.planet.facilities.append(facility)

        self.assertFalse(self.planet.has_space_shipyard)

    def test_multiple_facilities(self):
        """Verify multiple facilities can exist on one planet."""
        for i in range(3):
            facility = PlanetaryFacility(
                instance_id=f"facility-{i}",
                design_id=f"complex_{i}",
                name=f"Complex {i}",
                design_data={"name": f"Complex {i}"}
            )
            self.planet.facilities.append(facility)

        self.assertEqual(len(self.planet.facilities), 3)

    def test_facility_defaults(self):
        """Verify PlanetaryFacility defaults are correct."""
        facility = PlanetaryFacility(
            instance_id="test",
            design_id="test_design",
            name="Test Facility",
            design_data={}
        )

        # Default is_operational should be True
        self.assertTrue(facility.is_operational)


if __name__ == '__main__':
    unittest.main()
