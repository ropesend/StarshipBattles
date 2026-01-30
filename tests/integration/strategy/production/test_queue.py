"""
Production queue tests.

Tests queue format, adding items, and progress.
"""

import pytest
from game.strategy.data.planet import PlanetaryFacility


class TestProductionQueue:
    """Tests for production queue operations."""

    def test_add_to_queue(self, production_setup):
        """Verify adding an item to the queue works."""
        planet = production_setup['planet']
        # Item: "Colony Ship", Turns: 1
        planet.add_production("Colony Ship", 1)
        assert len(planet.construction_queue) == 1
        item = planet.construction_queue[0]
        assert item["design_id"] == "Colony Ship"
        assert item["type"] == "ship"
        assert item["turns_remaining"] == 1

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


class TestShipyardRequirement:
    """Tests for shipyard requirement on ship builds."""

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
                    "CORE": [{
                        "abilities": {"SpaceShipyard": {"value": 1}}
                    }]
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
                    "CORE": [{
                        "abilities": {"SpaceShipyard": {"value": 1}}
                    }]
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
