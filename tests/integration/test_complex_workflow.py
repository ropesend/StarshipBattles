"""
Integration tests for the complete planetary complex workflow.
Tests the end-to-end flow: Design → Queue → Build → Facility
"""

import pytest
import os
import json
import tempfile
from unittest.mock import MagicMock
from game.strategy.data.planet import Planet, PlanetType, PlanetaryFacility
from game.strategy.data.hex_math import HexCoord
from game.strategy.data.empire import Empire
from game.strategy.engine.turn_engine import TurnEngine
from game.strategy.systems.design_library import DesignLibrary


@pytest.fixture
def test_savegame_dir():
    """Create temporary savegame directory with test designs."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create designs directory structure
        # DesignLibrary expects designs in empire-specific subfolder: designs/empire_N/
        # Empire ID 1 is used by empire_with_colony fixture
        designs_dir = os.path.join(tmpdir, "designs", "empire_1")
        os.makedirs(designs_dir, exist_ok=True)

        # Create test complex design with harvester
        complex_design = {
            "name": "Mining Complex Mk1",
            "vehicle_type": "Planetary Complex",
            "vehicle_class": "Planetary Complex (Tier 1)",
            "layers": {
                "internal": [
                    {
                        "id": "metal_harvester",
                        "position": [0, 0],
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

        with open(os.path.join(designs_dir, "mining_complex_mk1.json"), "w") as f:
            json.dump(complex_design, f)

        # Create shipyard complex design
        shipyard_design = {
            "name": "Space Shipyard Mk1",
            "vehicle_type": "Planetary Complex",
            "vehicle_class": "Planetary Complex (Tier 1)",
            "layers": {
                "internal": [
                    {
                        "id": "space_shipyard",
                        "position": [0, 0],
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

        with open(os.path.join(designs_dir, "space_shipyard_mk1.json"), "w") as f:
            json.dump(shipyard_design, f)

        # Create test ship design
        ship_design = {
            "name": "Frigate Mk1",
            "vehicle_type": "Ship",
            "vehicle_class": "Ship (Tier 1)",
            "layers": {
                "internal": []
            }
        }

        with open(os.path.join(designs_dir, "frigate_mk1.json"), "w") as f:
            json.dump(ship_design, f)

        yield tmpdir


@pytest.fixture
def empire_with_colony(test_savegame_dir):
    """Create empire with a colony planet.

    Returns:
        Tuple of (empire, planet, save_path)
    """
    empire = Empire(1, "Test Empire", (255, 0, 0))

    planet = Planet(
        name="Test Colony",
        location=HexCoord(5, 5),
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
        planet_type=PlanetType.CONTINENTAL
    )
    planet.owner_id = empire.id
    planet.id = 100

    empire.colonies.append(planet)

    return empire, planet, test_savegame_dir


def test_design_save_load_complex(test_savegame_dir):
    """Test that complex designs can be saved and loaded."""
    library = DesignLibrary(test_savegame_dir, empire_id=1)

    # Scan designs
    designs = library.scan_designs()

    # Should find our test designs
    assert len(designs) >= 2, "Should find at least 2 designs (complex + shipyard)"

    design_names = [d.name for d in designs]
    assert "Mining Complex Mk1" in design_names
    assert "Space Shipyard Mk1" in design_names

    # Load specific design data
    complex_data = library.load_design_data("mining_complex_mk1")
    assert complex_data is not None
    assert complex_data["name"] == "Mining Complex Mk1"
    assert complex_data["vehicle_type"] == "Planetary Complex"


def test_complex_design_in_build_queue(empire_with_colony):
    """Test that complex designs appear in BuildQueueScreen's category filter."""
    empire, planet, save_path = empire_with_colony

    library = DesignLibrary(save_path, empire_id=1)

    # Simulate _load_designs_by_category("complex")
    all_designs = library.scan_designs()
    complexes = [d for d in all_designs if d.vehicle_type == "Planetary Complex"]

    # Should find both complex designs
    assert len(complexes) == 2
    complex_names = [d.name for d in complexes]
    assert "Mining Complex Mk1" in complex_names
    assert "Space Shipyard Mk1" in complex_names

    # Ships should be filtered out
    ships = [d for d in all_designs if d.vehicle_type == "Ship"]
    assert len(ships) == 1
    assert ships[0].name == "Frigate Mk1"


def test_full_build_workflow(empire_with_colony):
    """Test complete workflow: Design → Queue → Build → Facility."""
    empire, planet, save_path = empire_with_colony
    engine = TurnEngine()

    # Initial state: no facilities
    assert len(planet.facilities) == 0

    # Add complex to build queue
    planet.add_production("mining_complex_mk1", turns=2, vehicle_type="complex")
    assert len(planet.construction_queue) == 1

    # Process turn 1 - should decrement turns
    engine.process_production([empire], save_path=save_path)
    assert len(planet.construction_queue) == 1
    item = planet.construction_queue[0]
    assert item["turns_remaining"] == 1
    assert len(planet.facilities) == 0  # Not complete yet

    # Process turn 2 - should complete and spawn facility
    engine.process_production([empire], save_path=save_path)
    assert len(planet.construction_queue) == 0  # Queue empty
    assert len(planet.facilities) == 1  # Facility built

    # Verify facility
    facility = planet.facilities[0]
    assert isinstance(facility, PlanetaryFacility)
    assert facility.design_id == "mining_complex_mk1"
    assert facility.is_operational is True
    assert facility.instance_id is not None
    assert len(facility.instance_id) > 0


def test_shipyard_enables_ship_building(empire_with_colony):
    """Test that building a shipyard complex enables ship construction."""
    empire, planet, save_path = empire_with_colony
    engine = TurnEngine()

    # Initial state: no shipyard
    assert planet.has_space_shipyard is False

    # Build shipyard complex first
    planet.add_production("space_shipyard_mk1", turns=1, vehicle_type="complex")

    # Process turn - shipyard completes
    engine.process_production([empire], save_path=save_path)

    # Verify shipyard built and detected
    assert len(planet.facilities) == 1
    facility = planet.facilities[0]
    assert facility.design_id == "space_shipyard_mk1"

    # Planet should now have shipyard
    assert planet.has_space_shipyard is True

    # Now add ship to queue (shipyard exists)
    planet.add_production("frigate_mk1", turns=3, vehicle_type="ship")

    # Process remaining turns for ship
    initial_fleet_count = len(empire.fleets)
    engine.process_production([empire], save_path=save_path)  # Turn 1
    engine.process_production([empire], save_path=save_path)  # Turn 2
    engine.process_production([empire], save_path=save_path)  # Turn 3 - completes

    # Ship should spawn as fleet
    assert len(empire.fleets) == initial_fleet_count + 1
    new_fleet = empire.fleets[-1]
    assert any(ship.design_id == "frigate_mk1" for ship in new_fleet.ships)


def test_multiple_complexes_on_planet(empire_with_colony):
    """Test building multiple complexes on one planet."""
    empire, planet, save_path = empire_with_colony
    engine = TurnEngine()

    # Queue 3 complexes
    planet.add_production("mining_complex_mk1", turns=1, vehicle_type="complex")
    planet.add_production("space_shipyard_mk1", turns=1, vehicle_type="complex")
    planet.add_production("mining_complex_mk1", turns=1, vehicle_type="complex")

    assert len(planet.construction_queue) == 3

    # Process 3 turns
    engine.process_production([empire], save_path=save_path)  # Complex 1
    assert len(planet.facilities) == 1

    engine.process_production([empire], save_path=save_path)  # Complex 2
    assert len(planet.facilities) == 2

    engine.process_production([empire], save_path=save_path)  # Complex 3
    assert len(planet.facilities) == 3

    # Verify all facilities
    assert len(planet.construction_queue) == 0
    assert len(planet.facilities) == 3

    # Check unique instance IDs
    instance_ids = [f.instance_id for f in planet.facilities]
    assert len(set(instance_ids)) == 3  # All unique

    # Check design IDs
    design_ids = [f.design_id for f in planet.facilities]
    assert design_ids.count("mining_complex_mk1") == 2
    assert design_ids.count("space_shipyard_mk1") == 1


def test_shipyard_detection_with_multiple_facilities(empire_with_colony):
    """Test that has_space_shipyard works with multiple facilities."""
    empire, planet, save_path = empire_with_colony
    engine = TurnEngine()

    # Build 2 mining complexes (no shipyard)
    planet.add_production("mining_complex_mk1", turns=1, vehicle_type="complex")
    planet.add_production("mining_complex_mk1", turns=1, vehicle_type="complex")

    engine.process_production([empire], save_path=save_path)
    engine.process_production([empire], save_path=save_path)

    assert len(planet.facilities) == 2
    assert planet.has_space_shipyard is False

    # Build shipyard
    planet.add_production("space_shipyard_mk1", turns=1, vehicle_type="complex")
    engine.process_production([empire], save_path=save_path)

    assert len(planet.facilities) == 3
    assert planet.has_space_shipyard is True


def test_non_operational_shipyard_not_detected(empire_with_colony):
    """Test that damaged/non-operational shipyard doesn't enable ship building."""
    empire, planet, save_path = empire_with_colony
    engine = TurnEngine()

    # Build shipyard
    planet.add_production("space_shipyard_mk1", turns=1, vehicle_type="complex")
    engine.process_production([empire], save_path=save_path)

    assert planet.has_space_shipyard is True

    # Damage shipyard
    planet.facilities[0].is_operational = False

    # Should no longer detect shipyard
    assert planet.has_space_shipyard is False
