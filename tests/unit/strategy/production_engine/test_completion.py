"""Tests for production completion and shipyard requirements.

PROJ-69 Phase 2: Updated to reflect new queue model where ship items go in
facility queues and base queue handles complexes only. Shipyard requirement
tests updated to test that ship items in base queue are skipped (not paused
based on has_space_shipyard).
"""
import pytest
from unittest.mock import MagicMock, patch

from game.strategy.data.planet import PlanetaryFacility


def _make_shipyard(instance_id: str = "yard_1") -> PlanetaryFacility:
    """Create a shipyard facility for tests."""
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


class TestProductionCompletion:
    """Tests for production completion (turns reach zero)."""

    def test_ship_production_completes_via_facility_queue(self, mock_empire, mock_planet, mock_galaxy):
        """Ship production completes via facility queue when turns reach zero."""
        from game.strategy.engine.production_engine import ProductionEngine

        engine = ProductionEngine()
        yard = _make_shipyard()
        yard.construction_queue = [{"type": "ship", "design_id": "Scout", "turns_remaining": 1}]
        mock_planet.facilities = [yard]
        mock_planet.construction_queue = []
        mock_empire.colonies = [mock_planet]

        with patch.object(engine, '_spawn_ship') as mock_spawn:
            engine.process_production([mock_empire], mock_galaxy)

            mock_spawn.assert_called()
            assert len(yard.construction_queue) == 0

    def test_complex_production_completes(self, mock_empire, mock_planet, mock_galaxy):
        """Complex production completes when turns reach zero."""
        from game.strategy.engine.production_engine import ProductionEngine

        engine = ProductionEngine()
        mock_planet.construction_queue = [{"type": "complex", "design_id": "Factory", "turns_remaining": 1}]
        mock_planet.facilities = []
        mock_empire.colonies = [mock_planet]

        with patch.object(engine, '_spawn_complex') as mock_spawn:
            engine.process_production([mock_empire], mock_galaxy)

            mock_spawn.assert_called()

    def test_default_type_ship_in_facility_queue(self, mock_empire, mock_planet, mock_galaxy):
        """Dict format without 'type' key defaults to ship type in facility queue."""
        from game.strategy.engine.production_engine import ProductionEngine

        engine = ProductionEngine()
        yard = _make_shipyard()
        yard.construction_queue = [{"design_id": "Scout", "turns_remaining": 1}]  # No "type" key
        mock_planet.facilities = [yard]
        mock_planet.construction_queue = []
        mock_empire.colonies = [mock_planet]

        with patch.object(engine, '_spawn_ship') as mock_spawn:
            engine.process_production([mock_empire], mock_galaxy)

            # Should call _spawn_ship (default type)
            mock_spawn.assert_called()


class TestShipyardRequirements:
    """Tests for shipyard requirements on production.

    PROJ-69 Phase 2: Ship/fighter/satellite items in the base queue are
    now skipped entirely (they belong in facility queues). The base queue
    only processes complex items.
    """

    def test_ship_in_base_queue_skipped(self, mock_empire, mock_planet):
        """Ship items in base queue are skipped (belong in facility queue)."""
        from game.strategy.engine.production_engine import ProductionEngine

        engine = ProductionEngine()
        mock_planet.construction_queue = [{"type": "ship", "design_id": "Scout", "turns_remaining": 2}]
        mock_planet.has_space_shipyard = True
        mock_planet.facilities = []
        mock_empire.colonies = [mock_planet]

        engine.process_production([mock_empire])

        # Turns should NOT decrement - ship items skipped in base queue
        assert mock_planet.construction_queue[0]["turns_remaining"] == 2

    def test_fighter_in_base_queue_skipped(self, mock_empire, mock_planet):
        """Fighter items in base queue are skipped."""
        from game.strategy.engine.production_engine import ProductionEngine

        engine = ProductionEngine()
        mock_planet.construction_queue = [{"type": "fighter", "design_id": "Fighter", "turns_remaining": 2}]
        mock_planet.has_space_shipyard = False
        mock_planet.facilities = []
        mock_empire.colonies = [mock_planet]

        engine.process_production([mock_empire])

        assert mock_planet.construction_queue[0]["turns_remaining"] == 2

    def test_satellite_in_base_queue_skipped(self, mock_empire, mock_planet):
        """Satellite items in base queue are skipped."""
        from game.strategy.engine.production_engine import ProductionEngine

        engine = ProductionEngine()
        mock_planet.construction_queue = [{"type": "satellite", "design_id": "Satellite", "turns_remaining": 2}]
        mock_planet.has_space_shipyard = False
        mock_planet.facilities = []
        mock_empire.colonies = [mock_planet]

        engine.process_production([mock_empire])

        assert mock_planet.construction_queue[0]["turns_remaining"] == 2

    def test_complex_production_no_shipyard_needed(self, mock_empire, mock_planet, mock_galaxy):
        """Complexes don't need shipyard - process via base queue."""
        from game.strategy.engine.production_engine import ProductionEngine

        engine = ProductionEngine()
        mock_planet.construction_queue = [{"type": "complex", "design_id": "Factory", "turns_remaining": 1}]
        mock_planet.has_space_shipyard = False
        mock_planet.facilities = []
        mock_empire.colonies = [mock_planet]

        with patch.object(engine, '_spawn_complex') as mock_spawn:
            engine.process_production([mock_empire], mock_galaxy)

            mock_spawn.assert_called()
