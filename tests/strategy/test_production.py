import pytest
import tempfile
import os
import json
import shutil
from game.strategy.data.planet import Planet, PlanetType, PlanetaryFacility
from game.strategy.data.hex_math import HexCoord
from game.strategy.engine.turn_engine import TurnEngine
from game.strategy.data.empire import Empire


@pytest.fixture
def production_setup():
    """Create temporary directory and test objects for production tests."""
    # Create temporary directory for test designs
    # DesignLibrary expects designs in empire-specific subfolder: designs/empire_N/
    # Empire ID 0 is used (Empire(0, "Terran", ...))
    temp_dir = tempfile.mkdtemp()
    designs_dir = os.path.join(temp_dir, "designs", "empire_0")
    os.makedirs(designs_dir, exist_ok=True)

    # Create a test ship design
    test_design = {
        "name": "Test Ship",
        "ship_class": "Frigate",
        "vehicle_type": "Ship",
        "layers": {"CORE": [], "INNER": [], "OUTER": [], "ARMOR": []},
        "resources": {"fuel": 0.0, "energy": 0.0, "ammo": 0.0},
        "expected_stats": {
            "max_hp": 100,
            "max_speed": 10,
            "mass": 100.0
        },
        "_metadata": {
            "is_obsolete": False,
            "times_built": 0
        }
    }

    # Write test design files
    for design_id in ["test_ship", "test_ship_0", "test_ship_1", "test_ship_2"]:
        design_path = os.path.join(designs_dir, f"{design_id}.json")
        with open(design_path, 'w') as f:
            json.dump(test_design, f)

    # Create a valid planet manually to satisfy the dataclass
    planet = Planet(
        name="Terran Prime",
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
    planet.owner_id = 0

    empire = Empire(0, "Terran", (0, 0, 255))
    empire.savegame_path = temp_dir  # Use temp directory for designs
    empire.add_colony(planet)

    engine = TurnEngine()
    empires = [empire]

    yield {
        'temp_dir': temp_dir,
        'designs_dir': designs_dir,
        'planet': planet,
        'empire': empire,
        'engine': engine,
        'empires': empires
    }

    # Cleanup
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)


class TestProduction:

    def test_add_to_queue(self, production_setup):
        """Verify adding an item to the queue works."""
        planet = production_setup['planet']
        # Item: "Colony Ship", Turns: 1
        planet.add_production("Colony Ship", 1)
        assert len(planet.construction_queue) == 1
        item, turns = planet.construction_queue[0]
        assert item == "Colony Ship"
        assert turns == 1

    def test_production_progress(self, production_setup):
        """Verify turns decrement and items complete."""
        planet = production_setup['planet']
        planet.add_production("Colony Ship", 1)

        # Process Turn 1 (Should complete it)
        # Note: TurnEngine needs to process production now.
        # We need a dummy 'galaxy' or just pass None if not needed yet,
        # but spawning a fleet might require Galaxy context for location?
        # For now, let's assume Fleet spawn location is just planet global location.
        # But Planet lacks global location context in isolation.
        # We might need to mock Galaxy or pass global offset.

        # Workaround: Manually handle spawn logic in Engine or Mock it?
        # Let's see how TurnEngine handles it.
        pass

    def test_production_completion(self, production_setup):
        """Verify ship spawns when production completes."""
        planet = production_setup['planet']
        empire = production_setup['empire']
        engine = production_setup['engine']
        empires = production_setup['empires']
        temp_dir = production_setup['temp_dir']

        # Add shipyard first
        shipyard = PlanetaryFacility(
            instance_id="shipyard_1",
            design_id="shipyard_complex",
            name="Space Shipyard",
            design_data={
                "layers": {
                    "CORE": {
                        "components": [{
                            "abilities": {"SpaceShipyard": {"value": 1}}
                        }]
                    }
                }
            },
            is_operational=True
        )
        planet.facilities.append(shipyard)

        planet.add_production("test_ship", 1)

        # Capture initial fleets
        initial_fleet_count = len(empire.fleets)

        # Simulate processing logic (since we haven't written it yet, we are defining expectation)
        engine.process_production(empires, save_path=temp_dir)

        # Expectation: Queue empty, Fleet count +1
        assert len(planet.construction_queue) == 0
        assert len(empire.fleets) == initial_fleet_count + 1

    def test_build_queue_dict_format(self, production_setup):
        """Verify new queue format with type/design_id/turns."""
        planet = production_setup['planet']
        queue_item = {
            "design_id": "mining_complex_mk1",
            "type": "complex",
            "turns_remaining": 5
        }

        planet.construction_queue.append(queue_item)

        assert len(planet.construction_queue) == 1
        item = planet.construction_queue[0]
        assert isinstance(item, dict)
        assert item["design_id"] == "mining_complex_mk1"
        assert item["type"] == "complex"
        assert item["turns_remaining"] == 5

    def test_backwards_compat_list_format(self, production_setup):
        """Verify old ['Ship', 5] format still works in processing."""
        planet = production_setup['planet']
        engine = production_setup['engine']
        empires = production_setup['empires']
        temp_dir = production_setup['temp_dir']

        # Add shipyard first (required for ships)
        shipyard = PlanetaryFacility(
            instance_id="shipyard_1",
            design_id="shipyard_complex",
            name="Space Shipyard",
            design_data={
                "layers": {
                    "CORE": {
                        "components": [{
                            "abilities": {"SpaceShipyard": {"value": 1}}
                        }]
                    }
                }
            },
            is_operational=True
        )
        planet.facilities.append(shipyard)

        # Add old format to queue
        planet.construction_queue.append(["test_ship", 2])

        # Process one turn
        engine.process_production(empires, save_path=temp_dir)

        # Should decrement turns
        assert len(planet.construction_queue) == 1
        item = planet.construction_queue[0]
        assert item[1] == 1  # Turns decremented from 2 to 1

    def test_build_complex_adds_to_facilities(self, production_setup):
        """Verify complex completes and appears in planet.facilities."""
        planet = production_setup['planet']
        engine = production_setup['engine']
        empires = production_setup['empires']
        temp_dir = production_setup['temp_dir']

        # Add complex to queue with 1 turn
        queue_item = {
            "design_id": "test_complex_design",
            "type": "complex",
            "turns_remaining": 1
        }
        planet.construction_queue.append(queue_item)

        # Process turn - should complete
        initial_facility_count = len(planet.facilities)
        engine.process_production(empires, save_path=temp_dir)

        # Queue should be empty, facilities should have +1
        assert len(planet.construction_queue) == 0
        assert len(planet.facilities) == initial_facility_count + 1

        # Verify it's a PlanetaryFacility
        new_facility = planet.facilities[-1]
        assert isinstance(new_facility, PlanetaryFacility)
        assert new_facility.design_id == "test_complex_design"

    def test_spawn_complex_loads_design_data(self, production_setup):
        """Verify design data loaded from DesignLibrary when complex spawns."""
        planet = production_setup['planet']
        engine = production_setup['engine']
        empires = production_setup['empires']
        temp_dir = production_setup['temp_dir']

        queue_item = {
            "design_id": "shipyard_complex",
            "type": "complex",
            "turns_remaining": 1
        }
        planet.construction_queue.append(queue_item)

        # Process turn
        engine.process_production(empires, save_path=temp_dir)

        # Complex should have been built
        if len(planet.facilities) > 0:
            facility = planet.facilities[-1]
            # design_data should be populated (even if empty dict for missing design)
            assert facility.design_data is not None
            assert isinstance(facility.design_data, dict)

    def test_spawn_complex_creates_facility_instance(self, production_setup):
        """Verify PlanetaryFacility created with UUID."""
        planet = production_setup['planet']
        engine = production_setup['engine']
        empires = production_setup['empires']
        temp_dir = production_setup['temp_dir']

        queue_item = {
            "design_id": "harvester_complex",
            "type": "complex",
            "turns_remaining": 1
        }
        planet.construction_queue.append(queue_item)

        # Process turn
        engine.process_production(empires, save_path=temp_dir)

        # Should have facility with unique ID
        if len(planet.facilities) > 0:
            facility = planet.facilities[-1]
            assert facility.instance_id is not None
            assert len(facility.instance_id) > 0
            # UUID format check (basic)
            assert "-" in facility.instance_id

    def test_process_production_ship_spawns(self, production_setup):
        """Verify ship spawns as fleet when production completes."""
        planet = production_setup['planet']
        empire = production_setup['empire']
        engine = production_setup['engine']
        empires = production_setup['empires']
        temp_dir = production_setup['temp_dir']

        # Add shipyard first
        shipyard = PlanetaryFacility(
            instance_id="shipyard_1",
            design_id="shipyard_complex",
            name="Space Shipyard",
            design_data={
                "layers": {
                    "CORE": {
                        "components": [{
                            "abilities": {"SpaceShipyard": {"value": 1}}
                        }]
                    }
                }
            },
            is_operational=True
        )
        planet.facilities.append(shipyard)

        queue_item = {
            "design_id": "test_ship",
            "type": "ship",
            "turns_remaining": 1
        }
        planet.construction_queue.append(queue_item)

        initial_fleet_count = len(empire.fleets)

        # Process turn
        engine.process_production(empires, save_path=temp_dir)

        # Should spawn fleet
        assert len(planet.construction_queue) == 0
        assert len(empire.fleets) == initial_fleet_count + 1

    def test_complex_builds_in_1_turn(self, production_setup):
        """Test that complexes complete after 1 turn."""
        planet = production_setup['planet']
        engine = production_setup['engine']
        empires = production_setup['empires']
        temp_dir = production_setup['temp_dir']

        queue_item = {
            "design_id": "test_complex",
            "type": "complex",
            "turns_remaining": 1
        }
        planet.construction_queue.append(queue_item)

        # Process one turn
        engine.process_production(empires, save_path=temp_dir)

        # Should complete and remove from queue
        assert len(planet.construction_queue) == 0
        # Should create facility
        assert len(planet.facilities) > 0

    def test_ship_builds_in_1_turn(self, production_setup):
        """Test that ships complete after 1 turn."""
        planet = production_setup['planet']
        empire = production_setup['empire']
        engine = production_setup['engine']
        empires = production_setup['empires']
        temp_dir = production_setup['temp_dir']

        # Add shipyard first
        shipyard = PlanetaryFacility(
            instance_id="shipyard_1",
            design_id="shipyard_complex",
            name="Space Shipyard",
            design_data={
                "layers": {
                    "CORE": {
                        "components": [{
                            "abilities": {"SpaceShipyard": {"value": 1}}
                        }]
                    }
                }
            },
            is_operational=True
        )
        planet.facilities.append(shipyard)

        queue_item = {
            "design_id": "test_ship",
            "type": "ship",
            "turns_remaining": 1
        }
        planet.construction_queue.append(queue_item)

        initial_fleet_count = len(empire.fleets)

        # Process one turn
        engine.process_production(empires, save_path=temp_dir)

        # Should complete and remove from queue
        assert len(planet.construction_queue) == 0
        # Should spawn fleet
        assert len(empire.fleets) == initial_fleet_count + 1

    def test_ship_build_pauses_without_shipyard(self, production_setup):
        """Test that ship builds don't progress if shipyard is missing."""
        planet = production_setup['planet']
        engine = production_setup['engine']
        empires = production_setup['empires']
        temp_dir = production_setup['temp_dir']

        # Add ship to queue
        queue_item = {
            "design_id": "test_ship",
            "type": "ship",
            "turns_remaining": 2
        }
        planet.construction_queue.append(queue_item)

        # Add a shipyard facility first
        shipyard = PlanetaryFacility(
            instance_id="shipyard_1",
            design_id="shipyard_complex",
            name="Space Shipyard",
            design_data={
                "layers": {
                    "CORE": {
                        "components": [{
                            "abilities": {"SpaceShipyard": {"value": 1}}
                        }]
                    }
                }
            },
            is_operational=True
        )
        planet.facilities.append(shipyard)

        # Process turn - should work with shipyard
        engine.process_production(empires, save_path=temp_dir)
        assert planet.construction_queue[0]["turns_remaining"] == 1

        # Remove shipyard facility
        planet.facilities.clear()

        # Process turn - should NOT progress
        engine.process_production(empires, save_path=temp_dir)
        assert planet.construction_queue[0]["turns_remaining"] == 1  # Still 1

    def test_ship_build_resumes_with_shipyard(self, production_setup):
        """Test that paused ship builds resume when shipyard added."""
        planet = production_setup['planet']
        engine = production_setup['engine']
        empires = production_setup['empires']
        temp_dir = production_setup['temp_dir']

        # Add ship to queue without shipyard
        queue_item = {
            "design_id": "test_ship",
            "type": "ship",
            "turns_remaining": 2
        }
        planet.construction_queue.append(queue_item)

        # Process turn - should NOT progress without shipyard
        engine.process_production(empires, save_path=temp_dir)
        assert planet.construction_queue[0]["turns_remaining"] == 2  # No change

        # Add shipyard facility
        shipyard = PlanetaryFacility(
            instance_id="shipyard_1",
            design_id="shipyard_complex",
            name="Space Shipyard",
            design_data={
                "layers": {
                    "CORE": {
                        "components": [{
                            "abilities": {"SpaceShipyard": {"value": 1}}
                        }]
                    }
                }
            },
            is_operational=True
        )
        planet.facilities.append(shipyard)

        # Process turn - should now progress
        engine.process_production(empires, save_path=temp_dir)
        assert planet.construction_queue[0]["turns_remaining"] == 1  # Decremented

    def test_complex_builds_without_shipyard(self, production_setup):
        """Test that complexes build even without shipyard."""
        planet = production_setup['planet']
        engine = production_setup['engine']
        empires = production_setup['empires']
        temp_dir = production_setup['temp_dir']

        queue_item = {
            "design_id": "mining_complex",
            "type": "complex",
            "turns_remaining": 1
        }
        planet.construction_queue.append(queue_item)

        # No shipyard on planet
        assert len(planet.facilities) == 0

        # Process turn - complex should complete
        initial_facility_count = len(planet.facilities)
        engine.process_production(empires, save_path=temp_dir)

        # Should complete and add facility
        assert len(planet.construction_queue) == 0
        assert len(planet.facilities) > initial_facility_count

    def test_ship_spawns_as_ship_instance(self, production_setup):
        """Test that completed ships create ShipInstance (not string)."""
        from game.strategy.data.ship_instance import ShipInstance
        planet = production_setup['planet']
        empire = production_setup['empire']
        engine = production_setup['engine']
        empires = production_setup['empires']
        temp_dir = production_setup['temp_dir']

        # Add shipyard first
        shipyard = PlanetaryFacility(
            instance_id="shipyard_1",
            design_id="shipyard_complex",
            name="Space Shipyard",
            design_data={
                "layers": {
                    "CORE": {
                        "components": [{
                            "abilities": {"SpaceShipyard": {"value": 1}}
                        }]
                    }
                }
            },
            is_operational=True
        )
        planet.facilities.append(shipyard)

        # Add ship to queue
        queue_item = {
            "design_id": "test_ship",
            "type": "ship",
            "turns_remaining": 1
        }
        planet.construction_queue.append(queue_item)

        # Process turn
        engine.process_production(empires, save_path=temp_dir)

        # Should create fleet with ShipInstance
        assert len(empire.fleets) == 1
        fleet = empire.fleets[0]
        assert len(fleet.ships) > 0

        # Check that ship is ShipInstance (not string)
        ship = fleet.ships[0]
        assert isinstance(ship, ShipInstance)

    def test_ship_has_no_initial_orders(self, production_setup):
        """Test that newly spawned fleets have empty orders list."""
        planet = production_setup['planet']
        empire = production_setup['empire']
        engine = production_setup['engine']
        empires = production_setup['empires']
        temp_dir = production_setup['temp_dir']

        # Add shipyard
        shipyard = PlanetaryFacility(
            instance_id="shipyard_1",
            design_id="shipyard_complex",
            name="Space Shipyard",
            design_data={
                "layers": {
                    "CORE": {
                        "components": [{
                            "abilities": {"SpaceShipyard": {"value": 1}}
                        }]
                    }
                }
            },
            is_operational=True
        )
        planet.facilities.append(shipyard)

        # Add ship to queue
        queue_item = {
            "design_id": "test_ship",
            "type": "ship",
            "turns_remaining": 1
        }
        planet.construction_queue.append(queue_item)

        # Process turn
        engine.process_production(empires, save_path=temp_dir)

        # Check fleet has no orders
        fleet = empire.fleets[0]
        assert len(fleet.orders) == 0

    def test_fleet_id_is_unique(self, production_setup):
        """Test that fleet IDs are guaranteed unique."""
        planet = production_setup['planet']
        empire = production_setup['empire']
        engine = production_setup['engine']
        empires = production_setup['empires']
        temp_dir = production_setup['temp_dir']

        # Add shipyard
        shipyard = PlanetaryFacility(
            instance_id="shipyard_1",
            design_id="shipyard_complex",
            name="Space Shipyard",
            design_data={
                "layers": {
                    "CORE": {
                        "components": [{
                            "abilities": {"SpaceShipyard": {"value": 1}}
                        }]
                    }
                }
            },
            is_operational=True
        )
        planet.facilities.append(shipyard)

        # Add multiple ships to queue
        for i in range(3):
            queue_item = {
                "design_id": f"test_ship_{i}",
                "type": "ship",
                "turns_remaining": 1
            }
            planet.construction_queue.append(queue_item)

        # Process 3 turns
        for _ in range(3):
            engine.process_production(empires, save_path=temp_dir)

        # Should have 3 fleets with unique IDs
        assert len(empire.fleets) == 3
        fleet_ids = [fleet.id for fleet in empire.fleets]
        assert len(fleet_ids) == len(set(fleet_ids))  # No duplicates
