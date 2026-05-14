"""
Integration tests for the complete planetary complex workflow.
Tests the end-to-end flow: Design → Queue → Build → Facility
"""

import pytest
import os
import json
import tempfile
from unittest.mock import MagicMock
from game.strategy.data.planet import Planet, PlanetType
from game.strategy.data.planetary_facility import PlanetaryFacility
from game.core.hex_math import HexCoord
from game.strategy.data.empire import Empire
from game.strategy.engine.turn_engine import TurnEngine
from tests.fixtures.turn_engine import build_test_turn_engine
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
                                "resource_type": "metals",
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
    # Give planet local stockpile for production
    planet.stockpile = {
        "metals": 100000.0,
        "organics": 100000.0,
        "radioactives": 100000.0,
        "Energy": 100000.0
    }
    planet.max_stockpile = {
        "metals": 200000.0,
        "organics": 200000.0,
        "radioactives": 200000.0,
        "Energy": 200000.0
    }

    empire.colonies.append(planet)

    # Add PlanetaryYard facility so base construction queue is processed
    yard = PlanetaryFacility(
        instance_id="yard_starter",
        design_id="colony_hub",
        name="Colony Hub",
        design_data={
            "layers": {
                "CORE": [{"id": "yard", "abilities": {"PlanetaryYard": True}}]
            }
        },
        is_operational=True,
    )
    planet.facilities.append(yard)

    return empire, planet, test_savegame_dir


def _process_one_turn(engine, empires, galaxy=None, save_path=None):
    """Process 100 ticks of construction for one turn.

    Uses the live tick-based API instead of the dead process_production().
    """
    for tick in range(1, 101):
        engine.production_engine.process_construction_tick(
            tick, empires, galaxy, save_path=save_path
        )


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
    result = library.load_design_data("mining_complex_mk1")
    assert result.success
    assert result.data["name"] == "Mining Complex Mk1"
    assert result.data["vehicle_type"] == "Planetary Complex"


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


def test_full_build_workflow(empire_with_colony, fresh_registries):
    """Test complete workflow: Design → Queue → Build → Facility."""
    empire, planet, save_path = empire_with_colony
    engine = build_test_turn_engine(fresh_registries)

    # Initial state: only the starter PlanetaryYard facility
    initial_facility_count = len(planet.facilities)
    assert initial_facility_count == 1

    # Add complex with proper tick-based fields
    # At 20 Metals/tick (planetary_yard rate), 4000 Metals = 200 ticks = 2 turns
    queue_item = {
        "design_id": "mining_complex_mk1",
        "type": "complex",
        "turns_remaining": 2,
        "total_cost": {"metals": 4000.0},
        "resources_consumed": {"metals": 0.0}
    }
    planet.construction_queue.append(queue_item)
    assert len(planet.construction_queue) == 1

    # Process turn 1 - item should still be in queue with partial progress
    _process_one_turn(engine, [empire], save_path=save_path)
    assert len(planet.construction_queue) == 1
    item = planet.construction_queue[0]
    # After 100 ticks at 20/tick = 2000 Metals consumed
    assert item["resources_consumed"]["metals"] > 0
    assert len(planet.facilities) == initial_facility_count  # Not complete yet

    # Process turn 2 - should complete and spawn facility
    _process_one_turn(engine, [empire], save_path=save_path)
    assert len(planet.construction_queue) == 0  # Queue empty
    assert len(planet.facilities) == initial_facility_count + 1  # Facility built

    # Verify the newly built facility (last one added)
    facility = planet.facilities[-1]
    assert isinstance(facility, PlanetaryFacility)
    assert facility.design_id == "mining_complex_mk1"
    assert facility.is_operational is True
    assert facility.instance_id is not None
    assert len(facility.instance_id) > 0


def test_shipyard_enables_ship_building(empire_with_colony, fresh_registries):
    """Test that building a shipyard complex enables ship construction."""
    empire, planet, save_path = empire_with_colony
    engine = build_test_turn_engine(fresh_registries)

    # Initial state: no shipyard
    assert planet.has_space_shipyard is False

    # Build shipyard complex - 100 Metals = 5 ticks at 20/tick, completes in 1 turn
    shipyard_item = {
        "design_id": "space_shipyard_mk1",
        "type": "complex",
        "turns_remaining": 1,
        "total_cost": {"metals": 100.0},
        "resources_consumed": {"metals": 0.0}
    }
    planet.construction_queue.append(shipyard_item)

    # Process turn - shipyard completes
    _process_one_turn(engine, [empire], save_path=save_path)

    # Verify shipyard built and detected (starter yard + new shipyard)
    assert len(planet.facilities) == 2
    facility = planet.facilities[-1]
    assert facility.design_id == "space_shipyard_mk1"

    # Planet should now have shipyard
    assert planet.has_space_shipyard is True

    # PROJ-69 Phase 2: Ship items now go in facility queues, not base queue
    # Add ship to the shipyard facility's construction queue
    # At 30/tick shipyard rate, 9000 Metals = 300 ticks = 3 turns
    facility.construction_queue.append({
        "design_id": "frigate_mk1",
        "type": "ship",
        "turns_remaining": 3,
        "total_cost": {"metals": 9000.0},
        "resources_consumed": {"metals": 0.0}
    })

    # Process remaining turns for ship
    initial_fleet_count = len(empire.fleets)
    _process_one_turn(engine, [empire], save_path=save_path)  # Turn 1
    _process_one_turn(engine, [empire], save_path=save_path)  # Turn 2
    _process_one_turn(engine, [empire], save_path=save_path)  # Turn 3 - completes

    # Ship should spawn as fleet
    assert len(empire.fleets) == initial_fleet_count + 1
    new_fleet = empire.fleets[-1]
    assert any(ship.design_id == "frigate_mk1" for ship in new_fleet.ships)


def test_multiple_complexes_on_planet(empire_with_colony, fresh_registries):
    """Test building multiple complexes on one planet."""
    empire, planet, save_path = empire_with_colony
    engine = build_test_turn_engine(fresh_registries)

    # Queue 3 complexes - each 100 Metals = completes in 5 ticks (well within 1 turn)
    # But base queue processes 1 item at a time, so each needs its own turn
    planet.construction_queue.extend([
        {
            "design_id": "mining_complex_mk1",
            "type": "complex",
            "turns_remaining": 1,
            "total_cost": {"metals": 100.0},
            "resources_consumed": {"metals": 0.0}
        },
        {
            "design_id": "space_shipyard_mk1",
            "type": "complex",
            "turns_remaining": 1,
            "total_cost": {"metals": 100.0},
            "resources_consumed": {"metals": 0.0}
        },
        {
            "design_id": "mining_complex_mk1",
            "type": "complex",
            "turns_remaining": 1,
            "total_cost": {"metals": 100.0},
            "resources_consumed": {"metals": 0.0}
        }
    ])

    assert len(planet.construction_queue) == 3

    # Process turns - with carry-over capacity, all 3 items complete in 1 turn
    # (100 Metals each at 20/tick = 5 ticks each = 15 ticks total, well under 100)
    _process_one_turn(engine, [empire], save_path=save_path)
    assert len(planet.facilities) >= 2  # Starter yard + at least 1 new

    # Continue if needed
    if len(planet.construction_queue) > 0:
        _process_one_turn(engine, [empire], save_path=save_path)
    if len(planet.construction_queue) > 0:
        _process_one_turn(engine, [empire], save_path=save_path)

    # Verify all facilities (starter yard + 3 built = 4)
    assert len(planet.construction_queue) == 0
    assert len(planet.facilities) == 4

    # Check unique instance IDs
    instance_ids = [f.instance_id for f in planet.facilities]
    assert len(set(instance_ids)) == 4  # All unique

    # Check design IDs of built facilities (excluding starter yard)
    design_ids = [f.design_id for f in planet.facilities]
    assert design_ids.count("mining_complex_mk1") == 2
    assert design_ids.count("space_shipyard_mk1") == 1


def test_shipyard_detection_with_multiple_facilities(empire_with_colony, fresh_registries):
    """Test that has_space_shipyard works with multiple facilities."""
    empire, planet, save_path = empire_with_colony
    engine = build_test_turn_engine(fresh_registries)

    # Build 2 mining complexes (no shipyard) - small cost, completes quickly
    planet.construction_queue.extend([
        {
            "design_id": "mining_complex_mk1",
            "type": "complex",
            "turns_remaining": 1,
            "total_cost": {"metals": 100.0},
            "resources_consumed": {"metals": 0.0}
        },
        {
            "design_id": "mining_complex_mk1",
            "type": "complex",
            "turns_remaining": 1,
            "total_cost": {"metals": 100.0},
            "resources_consumed": {"metals": 0.0}
        }
    ])

    # Process turn - both complete due to carry-over
    _process_one_turn(engine, [empire], save_path=save_path)

    # Starter yard + 2 mining = 3
    assert len(planet.facilities) == 3
    assert planet.has_space_shipyard is False

    # Build shipyard
    planet.construction_queue.append({
        "design_id": "space_shipyard_mk1",
        "type": "complex",
        "turns_remaining": 1,
        "total_cost": {"metals": 100.0},
        "resources_consumed": {"metals": 0.0}
    })
    _process_one_turn(engine, [empire], save_path=save_path)

    # Starter yard + 2 mining + 1 shipyard = 4
    assert len(planet.facilities) == 4
    assert planet.has_space_shipyard is True


def test_non_operational_shipyard_not_detected(empire_with_colony, fresh_registries):
    """Test that damaged/non-operational shipyard doesn't enable ship building."""
    empire, planet, save_path = empire_with_colony
    engine = build_test_turn_engine(fresh_registries)

    # Build shipyard
    planet.construction_queue.append({
        "design_id": "space_shipyard_mk1",
        "type": "complex",
        "turns_remaining": 1,
        "total_cost": {"metals": 100.0},
        "resources_consumed": {"metals": 0.0}
    })
    _process_one_turn(engine, [empire], save_path=save_path)

    assert planet.has_space_shipyard is True

    # Damage the shipyard (last facility added)
    planet.facilities[-1].is_operational = False

    # Should no longer detect shipyard
    assert planet.has_space_shipyard is False
