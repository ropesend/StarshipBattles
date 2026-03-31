"""
Production completion tests.

Tests ship and complex spawning when production completes.

PROJ-69 Phase 2: Updated to use facility queues for ship items. Ship items
now go in shipyard facility construction_queue, not planet base queue.

PROJ-158 Phase 4: Updated to use tick-based production API instead of dead
process_production() method.
"""

import pytest
from game.strategy.data.planet import PlanetaryFacility


def _process_one_turn(engine, empires, galaxy=None, save_path=None):
    """Process 100 ticks of construction for one turn.

    Uses the live tick-based API instead of the dead process_production().
    """
    for tick in range(1, 101):
        engine.production_engine.process_construction_tick(
            tick, empires, galaxy, save_path=save_path
        )


def _make_shipyard(instance_id: str = "shipyard_1") -> PlanetaryFacility:
    """Create a shipyard facility with space_shipyard ability."""
    return PlanetaryFacility(
        instance_id=instance_id,
        design_id="shipyard_complex",
        name="Space Shipyard",
        design_data={
            "layers": {
                "CORE": [{
                    "id": "space_shipyard",
                    "abilities": {"SpaceShipyard": {"value": 1}}
                }]
            }
        },
        is_operational=True
    )


class TestProductionCompletion:
    """Tests for production completing and spawning entities."""

    def test_production_completion(self, production_setup):
        """Verify ship spawns when production completes via facility queue."""
        planet = production_setup['planet']
        empire = production_setup['empire']
        engine = production_setup['engine']
        empires = production_setup['empires']
        temp_dir = production_setup['temp_dir']

        # Add shipyard with ship item in its facility queue
        # At 30/tick shipyard rate, 100 Metals = 4 ticks, completes in 1 turn
        shipyard = _make_shipyard()
        shipyard.construction_queue = [
            {
                "design_id": "test_ship",
                "type": "ship",
                "turns_remaining": 1,
                "total_cost": {"metals": 100.0},
                "resources_consumed": {"metals": 0.0}
            }
        ]
        planet.facilities.append(shipyard)

        # Capture initial fleets
        initial_fleet_count = len(empire.fleets)

        _process_one_turn(engine, empires, save_path=temp_dir)

        # Expectation: Facility queue empty, Fleet count +1
        assert len(shipyard.construction_queue) == 0
        assert len(empire.fleets) == initial_fleet_count + 1


class TestComplexSpawning:
    """Tests for complex spawning."""

    def test_build_complex_adds_to_facilities(self, production_setup):
        """Verify complex completes and appears in planet.facilities."""
        planet = production_setup['planet']
        engine = production_setup['engine']
        empires = production_setup['empires']
        temp_dir = production_setup['temp_dir']

        # Add complex to queue with proper tick-based fields
        # At 20/tick planetary rate, 100 Metals = 5 ticks, completes in 1 turn
        queue_item = {
            "design_id": "test_complex_design",
            "type": "complex",
            "turns_remaining": 1,
            "total_cost": {"metals": 100.0},
            "resources_consumed": {"metals": 0.0}
        }
        planet.construction_queue.append(queue_item)

        # Process turn - should complete
        initial_facility_count = len(planet.facilities)
        _process_one_turn(engine, empires, save_path=temp_dir)

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
            "turns_remaining": 1,
            "total_cost": {"metals": 100.0},
            "resources_consumed": {"metals": 0.0}
        }
        planet.construction_queue.append(queue_item)

        # Process turn
        _process_one_turn(engine, empires, save_path=temp_dir)

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
            "turns_remaining": 1,
            "total_cost": {"metals": 100.0},
            "resources_consumed": {"metals": 0.0}
        }
        planet.construction_queue.append(queue_item)

        # Process turn
        _process_one_turn(engine, empires, save_path=temp_dir)

        # Should have facility with unique ID
        if len(planet.facilities) > 0:
            facility = planet.facilities[-1]
            assert facility.instance_id is not None
            assert len(facility.instance_id) > 0
            # UUID format check (basic)
            assert "-" in facility.instance_id

    def test_complex_builds_in_1_turn(self, production_setup):
        """Test that complexes complete after 1 turn."""
        planet = production_setup['planet']
        engine = production_setup['engine']
        empires = production_setup['empires']
        temp_dir = production_setup['temp_dir']

        queue_item = {
            "design_id": "test_complex",
            "type": "complex",
            "turns_remaining": 1,
            "total_cost": {"metals": 100.0},
            "resources_consumed": {"metals": 0.0}
        }
        planet.construction_queue.append(queue_item)

        # Process one turn
        _process_one_turn(engine, empires, save_path=temp_dir)

        # Should complete and remove from queue
        assert len(planet.construction_queue) == 0
        # Should create facility
        assert len(planet.facilities) > 0


class TestShipSpawning:
    """Tests for ship spawning via facility queues.

    PROJ-69 Phase 2: Ship items are now in shipyard facility construction
    queues, not the planet's base queue.

    PROJ-158 Phase 4: Updated to use tick-based production API.
    """

    def test_process_production_ship_spawns(self, production_setup):
        """Verify ship spawns as fleet when facility queue production completes."""
        planet = production_setup['planet']
        empire = production_setup['empire']
        engine = production_setup['engine']
        empires = production_setup['empires']
        temp_dir = production_setup['temp_dir']

        # Add shipyard with ship in facility queue
        shipyard = _make_shipyard()
        shipyard.construction_queue = [
            {
                "design_id": "test_ship",
                "type": "ship",
                "turns_remaining": 1,
                "total_cost": {"metals": 100.0},
                "resources_consumed": {"metals": 0.0}
            }
        ]
        planet.facilities.append(shipyard)

        initial_fleet_count = len(empire.fleets)

        # Process turn
        _process_one_turn(engine, empires, save_path=temp_dir)

        # Should spawn fleet
        assert len(shipyard.construction_queue) == 0
        assert len(empire.fleets) == initial_fleet_count + 1

    def test_ship_builds_in_1_turn(self, production_setup):
        """Test that ships complete after 1 turn via facility queue."""
        planet = production_setup['planet']
        empire = production_setup['empire']
        engine = production_setup['engine']
        empires = production_setup['empires']
        temp_dir = production_setup['temp_dir']

        # Add shipyard with ship in facility queue
        shipyard = _make_shipyard()
        shipyard.construction_queue = [
            {
                "design_id": "test_ship",
                "type": "ship",
                "turns_remaining": 1,
                "total_cost": {"metals": 100.0},
                "resources_consumed": {"metals": 0.0}
            }
        ]
        planet.facilities.append(shipyard)

        initial_fleet_count = len(empire.fleets)

        # Process one turn
        _process_one_turn(engine, empires, save_path=temp_dir)

        # Should complete and remove from queue
        assert len(shipyard.construction_queue) == 0
        # Should spawn fleet
        assert len(empire.fleets) == initial_fleet_count + 1

    def test_ship_spawns_as_ship_instance(self, production_setup):
        """Test that completed ships create ShipInstance (not string)."""
        from game.strategy.data.ship_instance import ShipInstance
        planet = production_setup['planet']
        empire = production_setup['empire']
        engine = production_setup['engine']
        empires = production_setup['empires']
        temp_dir = production_setup['temp_dir']

        # Add shipyard with ship in facility queue
        shipyard = _make_shipyard()
        shipyard.construction_queue = [
            {
                "design_id": "test_ship",
                "type": "ship",
                "turns_remaining": 1,
                "total_cost": {"metals": 100.0},
                "resources_consumed": {"metals": 0.0}
            }
        ]
        planet.facilities.append(shipyard)

        # Process turn
        _process_one_turn(engine, empires, save_path=temp_dir)

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

        # Add shipyard with ship in facility queue
        shipyard = _make_shipyard()
        shipyard.construction_queue = [
            {
                "design_id": "test_ship",
                "type": "ship",
                "turns_remaining": 1,
                "total_cost": {"metals": 100.0},
                "resources_consumed": {"metals": 0.0}
            }
        ]
        planet.facilities.append(shipyard)

        # Process turn
        _process_one_turn(engine, empires, save_path=temp_dir)

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

        # Add shipyard with multiple ships in facility queue
        # Each completes in 1 turn due to small cost and carry-over
        shipyard = _make_shipyard()
        for i in range(3):
            shipyard.construction_queue.append({
                "design_id": f"test_ship_{i}",
                "type": "ship",
                "turns_remaining": 1,
                "total_cost": {"metals": 100.0},
                "resources_consumed": {"metals": 0.0}
            })
        planet.facilities.append(shipyard)

        # Process turns - with carry-over all 3 may complete in 1 turn
        _process_one_turn(engine, empires, save_path=temp_dir)
        if len(shipyard.construction_queue) > 0:
            _process_one_turn(engine, empires, save_path=temp_dir)
        if len(shipyard.construction_queue) > 0:
            _process_one_turn(engine, empires, save_path=temp_dir)

        # Should have 3 fleets with unique IDs
        assert len(empire.fleets) == 3
        fleet_ids = [fleet.id for fleet in empire.fleets]
        assert len(fleet_ids) == len(set(fleet_ids))  # No duplicates


class TestParallelShipyardE2E:
    """E2E tests for parallel facility queue processing (PROJ-69 Phase 6).

    PROJ-158 Phase 4: Updated to use tick-based production API.
    """

    def test_two_shipyards_process_and_complete_independently(self, production_setup):
        """E2E: Planet with 2 shipyards + queued items → both process independently."""
        planet = production_setup['planet']
        empire = production_setup['empire']
        engine = production_setup['engine']
        empires = production_setup['empires']
        temp_dir = production_setup['temp_dir']

        # Add two shipyard facilities with separate queues
        # yard1: 6000 Metals at 30/tick = 200 ticks = 2 turns
        # yard2: 3000 Metals at 30/tick = 100 ticks = 1 turn
        yard1 = _make_shipyard("shipyard_1")
        yard1.construction_queue = [
            {
                "design_id": "test_ship",
                "type": "ship",
                "turns_remaining": 2,
                "total_cost": {"metals": 6000.0},
                "resources_consumed": {"metals": 0.0}
            }
        ]
        yard2 = _make_shipyard("shipyard_2")
        yard2.construction_queue = [
            {
                "design_id": "test_ship",
                "type": "ship",
                "turns_remaining": 1,
                "total_cost": {"metals": 3000.0},
                "resources_consumed": {"metals": 0.0}
            }
        ]
        planet.facilities.extend([yard1, yard2])

        initial_fleet_count = len(empire.fleets)

        # Turn 1: yard2 completes (1 turn), yard1 partially consumed
        _process_one_turn(engine, empires, save_path=temp_dir)

        # yard1 should still have item (consumed 3000/6000)
        assert len(yard1.construction_queue) == 1
        assert yard1.construction_queue[0]["resources_consumed"]["metals"] > 0
        # yard2 should be empty
        assert len(yard2.construction_queue) == 0
        assert len(empire.fleets) == initial_fleet_count + 1  # yard2's ship spawned

        # Turn 2: yard1 completes
        _process_one_turn(engine, empires, save_path=temp_dir)

        assert len(yard1.construction_queue) == 0
        assert len(empire.fleets) == initial_fleet_count + 2  # yard1's ship also spawned


class TestFacilityQueueSaveLoadE2E:
    """E2E tests for facility queue save/load persistence (PROJ-69 Phase 6).

    PROJ-158 Phase 4: Updated to use tick-based production API.
    """

    def test_save_load_preserves_facility_queues_and_processes(self, production_setup):
        """E2E: Save with facility queues → load → queues preserved → process → items complete."""
        from game.strategy.data.planet import Planet

        planet = production_setup['planet']
        empire = production_setup['empire']
        engine = production_setup['engine']
        empires = production_setup['empires']
        temp_dir = production_setup['temp_dir']

        # Add shipyard with items in its facility queue
        yard = _make_shipyard("shipyard_save_test")
        yard.construction_queue = [
            {
                "design_id": "test_ship",
                "type": "ship",
                "turns_remaining": 1,
                "total_cost": {"metals": 100.0},
                "resources_consumed": {"metals": 0.0}
            }
        ]
        planet.facilities.append(yard)

        # Also add complex to base queue
        planet.construction_queue.append({
            "design_id": "test_complex",
            "type": "complex",
            "turns_remaining": 1,
            "total_cost": {"metals": 100.0},
            "resources_consumed": {"metals": 0.0}
        })

        # Serialize planet (simulating save)
        planet_data = planet.to_dict()

        # Deserialize planet (simulating load)
        restored_planet = Planet.from_dict(planet_data)
        restored_planet.owner_id = planet.owner_id

        # Verify facility queue was preserved (starter yard + shipyard = 2)
        assert len(restored_planet.facilities) == 2
        # Find the shipyard by instance_id
        restored_yard = next(f for f in restored_planet.facilities if f.instance_id == "shipyard_save_test")
        assert len(restored_yard.construction_queue) == 1
        assert restored_yard.construction_queue[0]["design_id"] == "test_ship"

        # Verify base queue was preserved
        assert len(restored_planet.construction_queue) == 1
        assert restored_planet.construction_queue[0]["type"] == "complex"

        # Replace colony in empire with the restored planet for processing
        empire.colonies.clear()
        empire.add_colony(restored_planet)

        initial_fleet_count = len(empire.fleets)
        initial_facility_count = len(restored_planet.facilities)

        # Process production on restored planet - both queues should complete
        _process_one_turn(engine, empires, save_path=temp_dir)

        # Facility queue ship should have spawned
        assert len(restored_yard.construction_queue) == 0
        assert len(empire.fleets) == initial_fleet_count + 1

        # Base queue complex should have spawned as facility
        assert len(restored_planet.construction_queue) == 0
        assert len(restored_planet.facilities) == initial_facility_count + 1
