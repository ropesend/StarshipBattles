"""Tests for facility queue production processing.

PROJ-69 Phase 2: Each shipyard facility processes its own construction_queue
independently, enabling parallel ship construction on planets with multiple
shipyards.
"""
import pytest
from unittest.mock import MagicMock, patch

from game.strategy.data.planet import PlanetaryFacility
from game.strategy.engine.production_engine import ProductionEngine


def _make_shipyard_facility(instance_id: str = "yard_1") -> PlanetaryFacility:
    """Create a shipyard facility with construction_queue support."""
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
        is_operational=True,
    )


def _make_non_shipyard_facility(instance_id: str = "mine_1") -> PlanetaryFacility:
    """Create a non-shipyard facility."""
    return PlanetaryFacility(
        instance_id=instance_id,
        design_id="mining_complex",
        name="Mining Complex",
        design_data={"layers": {"CORE": [{"id": "mining_drill"}]}},
        is_operational=True,
    )


class TestFacilityQueueProcessing:
    """Tests for individual shipyard facility queue processing."""

    def test_facility_queue_decrements_turns(self, mock_empire, mock_planet):
        """Shipyard facility queue item has turns decremented."""
        engine = ProductionEngine()
        yard = _make_shipyard_facility()
        yard.construction_queue = [
            {"design_id": "Scout", "type": "ship", "turns_remaining": 3}
        ]
        mock_planet.facilities = [yard]
        mock_planet.construction_queue = []  # Empty base queue
        mock_empire.colonies = [mock_planet]

        engine.process_production([mock_empire])

        assert yard.construction_queue[0]["turns_remaining"] == 2

    def test_facility_queue_completes_ship(self, mock_empire, mock_planet, mock_galaxy):
        """Ship in facility queue completes and spawns when turns reach zero."""
        engine = ProductionEngine()
        yard = _make_shipyard_facility()
        yard.construction_queue = [
            {"design_id": "Scout", "type": "ship", "turns_remaining": 1}
        ]
        mock_planet.facilities = [yard]
        mock_planet.construction_queue = []
        mock_empire.colonies = [mock_planet]

        with patch.object(engine, '_spawn_ship') as mock_spawn:
            engine.process_production([mock_empire], mock_galaxy)

            mock_spawn.assert_called_once()
            assert len(yard.construction_queue) == 0

    def test_facility_queue_completes_complex(self, mock_empire, mock_planet, mock_galaxy):
        """Complex in facility queue completes and spawns."""
        engine = ProductionEngine()
        yard = _make_shipyard_facility()
        yard.construction_queue = [
            {"design_id": "Factory", "type": "complex", "turns_remaining": 1}
        ]
        mock_planet.facilities = [yard]
        mock_planet.construction_queue = []
        mock_empire.colonies = [mock_planet]

        with patch.object(engine, '_spawn_complex') as mock_spawn:
            engine.process_production([mock_empire], mock_galaxy)

            mock_spawn.assert_called_once()
            assert len(yard.construction_queue) == 0

    def test_non_shipyard_facility_queue_ignored(self, mock_empire, mock_planet):
        """Non-shipyard facility queues are not processed."""
        engine = ProductionEngine()
        mine = _make_non_shipyard_facility()
        mine.construction_queue = [
            {"design_id": "Scout", "type": "ship", "turns_remaining": 3}
        ]
        mock_planet.facilities = [mine]
        mock_planet.construction_queue = []
        mock_empire.colonies = [mock_planet]

        engine.process_production([mock_empire])

        # Should not have decremented
        assert mine.construction_queue[0]["turns_remaining"] == 3

    def test_inoperational_shipyard_facility_queue_ignored(self, mock_empire, mock_planet):
        """Inoperational shipyard facility queues are not processed."""
        engine = ProductionEngine()
        yard = _make_shipyard_facility()
        yard.is_operational = False
        yard.construction_queue = [
            {"design_id": "Scout", "type": "ship", "turns_remaining": 3}
        ]
        mock_planet.facilities = [yard]
        mock_planet.construction_queue = []
        mock_empire.colonies = [mock_planet]

        engine.process_production([mock_empire])

        assert yard.construction_queue[0]["turns_remaining"] == 3

    def test_facility_queue_only_first_item_processed(self, mock_empire, mock_planet):
        """Only the first item in a facility queue is processed per turn."""
        engine = ProductionEngine()
        yard = _make_shipyard_facility()
        yard.construction_queue = [
            {"design_id": "Scout", "type": "ship", "turns_remaining": 3},
            {"design_id": "Cruiser", "type": "ship", "turns_remaining": 5},
        ]
        mock_planet.facilities = [yard]
        mock_planet.construction_queue = []
        mock_empire.colonies = [mock_planet]

        engine.process_production([mock_empire])

        assert yard.construction_queue[0]["turns_remaining"] == 2
        assert yard.construction_queue[1]["turns_remaining"] == 5

    def test_empty_facility_queue_skipped(self, mock_empire, mock_planet):
        """Shipyard facility with empty queue is skipped without error."""
        engine = ProductionEngine()
        yard = _make_shipyard_facility()
        yard.construction_queue = []
        mock_planet.facilities = [yard]
        mock_planet.construction_queue = []
        mock_empire.colonies = [mock_planet]

        # Should not raise
        engine.process_production([mock_empire])


class TestParallelFacilityProcessing:
    """Tests for multiple shipyard facilities processing simultaneously."""

    def test_two_shipyards_process_simultaneously(self, mock_empire, mock_planet):
        """Two shipyard facilities both process their queues each turn."""
        engine = ProductionEngine()
        yard1 = _make_shipyard_facility("yard_1")
        yard1.construction_queue = [
            {"design_id": "Scout", "type": "ship", "turns_remaining": 3}
        ]
        yard2 = _make_shipyard_facility("yard_2")
        yard2.construction_queue = [
            {"design_id": "Cruiser", "type": "ship", "turns_remaining": 5}
        ]
        mock_planet.facilities = [yard1, yard2]
        mock_planet.construction_queue = []
        mock_empire.colonies = [mock_planet]

        engine.process_production([mock_empire])

        assert yard1.construction_queue[0]["turns_remaining"] == 2
        assert yard2.construction_queue[0]["turns_remaining"] == 4

    def test_two_shipyards_both_complete_same_turn(self, mock_empire, mock_planet, mock_galaxy):
        """Two shipyards can both complete items on the same turn."""
        engine = ProductionEngine()
        yard1 = _make_shipyard_facility("yard_1")
        yard1.construction_queue = [
            {"design_id": "Scout", "type": "ship", "turns_remaining": 1}
        ]
        yard2 = _make_shipyard_facility("yard_2")
        yard2.construction_queue = [
            {"design_id": "Cruiser", "type": "ship", "turns_remaining": 1}
        ]
        mock_planet.facilities = [yard1, yard2]
        mock_planet.construction_queue = []
        mock_empire.colonies = [mock_planet]

        with patch.object(engine, '_spawn_ship') as mock_spawn:
            engine.process_production([mock_empire], mock_galaxy)

            assert mock_spawn.call_count == 2
            assert len(yard1.construction_queue) == 0
            assert len(yard2.construction_queue) == 0

    def test_base_queue_and_facility_queue_both_process(self, mock_empire, mock_planet, mock_galaxy):
        """Base queue (complex) and facility queue (ship) both process same turn."""
        engine = ProductionEngine()
        yard = _make_shipyard_facility()
        yard.construction_queue = [
            {"design_id": "Scout", "type": "ship", "turns_remaining": 3}
        ]
        mock_planet.facilities = [yard]
        mock_planet.construction_queue = [
            {"design_id": "Factory", "type": "complex", "turns_remaining": 2}
        ]
        mock_empire.colonies = [mock_planet]

        engine.process_production([mock_empire])

        # Both should decrement
        assert mock_planet.construction_queue[0]["turns_remaining"] == 1
        assert yard.construction_queue[0]["turns_remaining"] == 2


class TestBaseQueueRestrictions:
    """Tests for base queue being restricted to complexes only."""

    def test_base_queue_processes_complex(self, mock_empire, mock_planet, mock_galaxy):
        """Base queue still processes complex items normally."""
        engine = ProductionEngine()
        mock_planet.construction_queue = [
            {"design_id": "Factory", "type": "complex", "turns_remaining": 1}
        ]
        mock_planet.facilities = []
        mock_empire.colonies = [mock_planet]

        with patch.object(engine, '_spawn_complex') as mock_spawn:
            engine.process_production([mock_empire], mock_galaxy)

            mock_spawn.assert_called_once()
            assert len(mock_planet.construction_queue) == 0

    def test_base_queue_skips_ship_type(self, mock_empire, mock_planet):
        """Base queue ignores ship-type items (they belong in facility queues)."""
        engine = ProductionEngine()
        mock_planet.construction_queue = [
            {"design_id": "Scout", "type": "ship", "turns_remaining": 3}
        ]
        mock_planet.has_space_shipyard = True
        mock_planet.facilities = []
        mock_empire.colonies = [mock_planet]

        engine.process_production([mock_empire])

        # Should NOT decrement - ship items don't process in base queue
        assert mock_planet.construction_queue[0]["turns_remaining"] == 3

    def test_base_queue_skips_fighter_type(self, mock_empire, mock_planet):
        """Base queue ignores fighter-type items."""
        engine = ProductionEngine()
        mock_planet.construction_queue = [
            {"design_id": "Fighter", "type": "fighter", "turns_remaining": 3}
        ]
        mock_planet.has_space_shipyard = True
        mock_planet.facilities = []
        mock_empire.colonies = [mock_planet]

        engine.process_production([mock_empire])

        assert mock_planet.construction_queue[0]["turns_remaining"] == 3

    def test_base_queue_skips_satellite_type(self, mock_empire, mock_planet):
        """Base queue ignores satellite-type items."""
        engine = ProductionEngine()
        mock_planet.construction_queue = [
            {"design_id": "Satellite", "type": "satellite", "turns_remaining": 3}
        ]
        mock_planet.has_space_shipyard = True
        mock_planet.facilities = []
        mock_empire.colonies = [mock_planet]

        engine.process_production([mock_empire])

        assert mock_planet.construction_queue[0]["turns_remaining"] == 3

    def test_base_queue_skips_default_type_ship(self, mock_empire, mock_planet):
        """Base queue ignores items with no type key (default 'ship')."""
        engine = ProductionEngine()
        mock_planet.construction_queue = [
            {"design_id": "Scout", "turns_remaining": 3}  # No type = default "ship"
        ]
        mock_planet.has_space_shipyard = True
        mock_planet.facilities = []
        mock_empire.colonies = [mock_planet]

        engine.process_production([mock_empire])

        assert mock_planet.construction_queue[0]["turns_remaining"] == 3
