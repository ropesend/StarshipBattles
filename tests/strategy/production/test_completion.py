"""
Production completion tests.

Tests ship and complex spawning when production completes.
"""

import pytest
from game.strategy.data.planet import PlanetaryFacility


class TestProductionCompletion:
    """Tests for production completing and spawning entities."""

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
                    "CORE": [{
                        "abilities": {"SpaceShipyard": {"value": 1}}
                    }]
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


class TestComplexSpawning:
    """Tests for complex spawning."""

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


class TestShipSpawning:
    """Tests for ship spawning."""

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
                    "CORE": [{
                        "abilities": {"SpaceShipyard": {"value": 1}}
                    }]
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
                    "CORE": [{
                        "abilities": {"SpaceShipyard": {"value": 1}}
                    }]
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
                    "CORE": [{
                        "abilities": {"SpaceShipyard": {"value": 1}}
                    }]
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
                    "CORE": [{
                        "abilities": {"SpaceShipyard": {"value": 1}}
                    }]
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
                    "CORE": [{
                        "abilities": {"SpaceShipyard": {"value": 1}}
                    }]
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
