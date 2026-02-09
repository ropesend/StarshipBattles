"""Tests for fleet production processing.

PROJ-67 Phase 3: Fleet space yards can build ships that join the fleet directly.
"""
import pytest
from unittest.mock import MagicMock, patch

from game.strategy.engine.production_engine import ProductionEngine
from game.strategy.data.fleet import Fleet, FleetOrder, OrderType
from game.strategy.data.hex_math import HexCoord


class TestFleetProductionBasics:
    """Test basic fleet production queue processing."""

    def test_fleet_with_build_order_and_queue_gets_turns_decremented(self):
        """Fleet with BUILD order and queue item should have turns decremented."""
        engine = ProductionEngine()

        # Create fleet with space yard
        fleet = Fleet(1, 0, HexCoord(5, 5))
        fleet.construction_queue = [
            {"design_id": "destroyer_1", "type": "ship", "turns_remaining": 5}
        ]
        fleet.orders = [FleetOrder(OrderType.BUILD)]

        # Mock has_space_shipyard to return True
        with patch.object(Fleet, 'has_space_shipyard', new_callable=lambda: property(lambda self: True)):
            empire = MagicMock()
            empire.id = 0
            empire.fleets = [fleet]

            engine.process_fleet_production([empire], None, None)

            assert fleet.construction_queue[0]["turns_remaining"] == 4

    def test_fleet_without_build_order_is_skipped(self):
        """Fleet without BUILD order should not process production."""
        engine = ProductionEngine()

        # Create fleet with MOVE order (not BUILD)
        fleet = Fleet(1, 0, HexCoord(5, 5))
        fleet.construction_queue = [
            {"design_id": "destroyer_1", "type": "ship", "turns_remaining": 5}
        ]
        fleet.orders = [FleetOrder(OrderType.MOVE, HexCoord(10, 10))]

        with patch.object(Fleet, 'has_space_shipyard', new_callable=lambda: property(lambda self: True)):
            empire = MagicMock()
            empire.id = 0
            empire.fleets = [fleet]

            engine.process_fleet_production([empire], None, None)

            # Turns should NOT be decremented
            assert fleet.construction_queue[0]["turns_remaining"] == 5

    def test_fleet_without_shipyard_pauses_production(self):
        """Fleet without shipyard should pause production (no turns decremented)."""
        engine = ProductionEngine()

        fleet = Fleet(1, 0, HexCoord(5, 5))
        fleet.construction_queue = [
            {"design_id": "destroyer_1", "type": "ship", "turns_remaining": 5}
        ]
        fleet.orders = [FleetOrder(OrderType.BUILD)]

        # has_space_shipyard returns False (yard destroyed)
        with patch.object(Fleet, 'has_space_shipyard', new_callable=lambda: property(lambda self: False)):
            empire = MagicMock()
            empire.id = 0
            empire.fleets = [fleet]

            engine.process_fleet_production([empire], None, None)

            # Turns should NOT be decremented
            assert fleet.construction_queue[0]["turns_remaining"] == 5

    def test_fleet_with_empty_queue_is_skipped(self):
        """Fleet with BUILD order but empty queue should be skipped."""
        engine = ProductionEngine()

        fleet = Fleet(1, 0, HexCoord(5, 5))
        fleet.construction_queue = []  # Empty queue
        fleet.orders = [FleetOrder(OrderType.BUILD)]

        with patch.object(Fleet, 'has_space_shipyard', new_callable=lambda: property(lambda self: True)):
            empire = MagicMock()
            empire.id = 0
            empire.fleets = [fleet]

            # Should not raise
            engine.process_fleet_production([empire], None, None)

            # Queue should still be empty
            assert fleet.construction_queue == []


class TestFleetShipSpawning:
    """Test ship spawning for fleet production."""

    def test_completed_ship_joins_building_fleet(self):
        """When ship completes, it should join the building fleet."""
        engine = ProductionEngine()

        fleet = Fleet(1, 0, HexCoord(5, 5))
        fleet.construction_queue = [
            {"design_id": "destroyer_1", "type": "ship", "turns_remaining": 1}  # Completes this turn
        ]
        fleet.orders = [FleetOrder(OrderType.BUILD)]

        # Track ships added to fleet
        original_ship_count = len(fleet.ships)

        with patch.object(Fleet, 'has_space_shipyard', new_callable=lambda: property(lambda self: True)):
            empire = MagicMock()
            empire.id = 0
            empire.fleets = [fleet]

            # Mock the DesignLibrary
            mock_design = {
                "name": "Destroyer",
                "layers": {},
                "hull": {"id": "hull_medium"}
            }

            with patch('game.strategy.engine.production_engine.DesignLibrary') as MockLib:
                mock_lib_instance = MagicMock()
                mock_lib_instance.load_design_data.return_value = mock_design
                mock_lib_instance.increment_built_count = MagicMock()
                MockLib.return_value = mock_lib_instance

                engine.process_fleet_production([empire], None, "/fake/save/path")

        # Ship should be added to fleet
        assert len(fleet.ships) == original_ship_count + 1
        # Queue should be empty
        assert len(fleet.construction_queue) == 0

    def test_design_times_built_incremented(self):
        """Design's times_built counter should increment on completion."""
        engine = ProductionEngine()

        fleet = Fleet(1, 0, HexCoord(5, 5))
        fleet.construction_queue = [
            {"design_id": "destroyer_1", "type": "ship", "turns_remaining": 1}
        ]
        fleet.orders = [FleetOrder(OrderType.BUILD)]

        with patch.object(Fleet, 'has_space_shipyard', new_callable=lambda: property(lambda self: True)):
            empire = MagicMock()
            empire.id = 0
            empire.fleets = [fleet]

            mock_design = {"name": "Destroyer", "layers": {}, "hull": {"id": "hull_medium"}}

            with patch('game.strategy.engine.production_engine.DesignLibrary') as MockLib:
                mock_lib_instance = MagicMock()
                mock_lib_instance.load_design_data.return_value = mock_design
                MockLib.return_value = mock_lib_instance

                engine.process_fleet_production([empire], None, "/fake/save/path")

                # increment_built_count should be called
                mock_lib_instance.increment_built_count.assert_called_once_with("destroyer_1")


class TestFleetComplexSpawning:
    """Test complex spawning for fleet production."""

    def test_complex_spawns_to_planet_when_fleet_at_planet_hex(self):
        """Complex should spawn on planet when fleet is at planet hex."""
        engine = ProductionEngine()

        fleet = Fleet(1, 0, HexCoord(5, 5))
        fleet.construction_queue = [
            {"design_id": "factory_1", "type": "complex", "turns_remaining": 1}
        ]
        fleet.orders = [FleetOrder(OrderType.BUILD)]

        # Mock planet at same hex
        mock_planet = MagicMock()
        mock_planet.facilities = []
        mock_planet.name = "Test Planet"

        mock_galaxy = MagicMock()
        mock_galaxy.get_planets_at_global_hex.return_value = [mock_planet]

        with patch.object(Fleet, 'has_space_shipyard', new_callable=lambda: property(lambda self: True)):
            empire = MagicMock()
            empire.id = 0
            empire.fleets = [fleet]

            mock_design = {"name": "Factory", "layers": {}}

            with patch('game.strategy.engine.production_engine.DesignLibrary') as MockLib:
                mock_lib_instance = MagicMock()
                mock_lib_instance.load_design_data.return_value = mock_design
                MockLib.return_value = mock_lib_instance

                engine.process_fleet_production([empire], mock_galaxy, "/fake/save/path")

        # Complex should be added to planet
        assert len(mock_planet.facilities) == 1
        # Queue should be empty
        assert len(fleet.construction_queue) == 0

    def test_complex_paused_when_fleet_not_at_planet(self):
        """Complex production pauses when fleet is not at planet hex (PROJ-67 Phase 6)."""
        engine = ProductionEngine()

        fleet = Fleet(1, 0, HexCoord(5, 5))
        fleet.construction_queue = [
            {"design_id": "factory_1", "type": "complex", "turns_remaining": 1}
        ]
        fleet.orders = [FleetOrder(OrderType.BUILD)]

        # No planet at fleet's hex
        mock_galaxy = MagicMock()
        mock_galaxy.get_planets_at_global_hex.return_value = []

        with patch.object(Fleet, 'has_space_shipyard', new_callable=lambda: property(lambda self: True)):
            empire = MagicMock()
            empire.id = 0
            empire.fleets = [fleet]

            # Should not raise, just pause production
            engine.process_fleet_production([empire], mock_galaxy, "/fake/save/path")

        # Queue item should still be in queue (paused, not removed)
        assert len(fleet.construction_queue) == 1
        # Turns should not have been decremented
        assert fleet.construction_queue[0]["turns_remaining"] == 1


class TestFleetProductionEdgeCases:
    """Test edge cases for fleet production."""

    def test_multiple_fleets_processed(self):
        """Multiple fleets should all be processed."""
        engine = ProductionEngine()

        fleet1 = Fleet(1, 0, HexCoord(5, 5))
        fleet1.construction_queue = [
            {"design_id": "ship_a", "type": "ship", "turns_remaining": 5}
        ]
        fleet1.orders = [FleetOrder(OrderType.BUILD)]

        fleet2 = Fleet(2, 0, HexCoord(10, 10))
        fleet2.construction_queue = [
            {"design_id": "ship_b", "type": "ship", "turns_remaining": 3}
        ]
        fleet2.orders = [FleetOrder(OrderType.BUILD)]

        with patch.object(Fleet, 'has_space_shipyard', new_callable=lambda: property(lambda self: True)):
            empire = MagicMock()
            empire.id = 0
            empire.fleets = [fleet1, fleet2]

            engine.process_fleet_production([empire], None, None)

        # Both should be decremented
        assert fleet1.construction_queue[0]["turns_remaining"] == 4
        assert fleet2.construction_queue[0]["turns_remaining"] == 2

    def test_multiple_empires_processed(self):
        """Multiple empires' fleets should all be processed."""
        engine = ProductionEngine()

        fleet1 = Fleet(1, 0, HexCoord(5, 5))
        fleet1.construction_queue = [
            {"design_id": "ship_a", "type": "ship", "turns_remaining": 5}
        ]
        fleet1.orders = [FleetOrder(OrderType.BUILD)]

        fleet2 = Fleet(2, 1, HexCoord(10, 10))
        fleet2.construction_queue = [
            {"design_id": "ship_b", "type": "ship", "turns_remaining": 3}
        ]
        fleet2.orders = [FleetOrder(OrderType.BUILD)]

        with patch.object(Fleet, 'has_space_shipyard', new_callable=lambda: property(lambda self: True)):
            empire1 = MagicMock()
            empire1.id = 0
            empire1.fleets = [fleet1]

            empire2 = MagicMock()
            empire2.id = 1
            empire2.fleets = [fleet2]

            engine.process_fleet_production([empire1, empire2], None, None)

        # Both should be decremented
        assert fleet1.construction_queue[0]["turns_remaining"] == 4
        assert fleet2.construction_queue[0]["turns_remaining"] == 2

    def test_fighter_and_satellite_types_work(self):
        """Fighter and satellite vehicle types should process correctly."""
        engine = ProductionEngine()

        fleet = Fleet(1, 0, HexCoord(5, 5))
        fleet.construction_queue = [
            {"design_id": "fighter_1", "type": "fighter", "turns_remaining": 2}
        ]
        fleet.orders = [FleetOrder(OrderType.BUILD)]

        with patch.object(Fleet, 'has_space_shipyard', new_callable=lambda: property(lambda self: True)):
            empire = MagicMock()
            empire.id = 0
            empire.fleets = [fleet]

            engine.process_fleet_production([empire], None, None)

        assert fleet.construction_queue[0]["turns_remaining"] == 1

    def test_production_resumes_when_new_yard_ship_joins_fleet(self):
        """Production resumes when a new yard ship joins the fleet."""
        engine = ProductionEngine()

        fleet = Fleet(1, 0, HexCoord(5, 5))
        fleet.construction_queue = [
            {"design_id": "destroyer_1", "type": "ship", "turns_remaining": 5}
        ]
        fleet.orders = [FleetOrder(OrderType.BUILD)]

        empire = MagicMock()
        empire.id = 0
        empire.fleets = [fleet]

        # First turn: no shipyard - production paused
        with patch.object(Fleet, 'has_space_shipyard', new_callable=lambda: property(lambda self: False)):
            engine.process_fleet_production([empire], None, None)
            assert fleet.construction_queue[0]["turns_remaining"] == 5  # Not decremented

        # Second turn: yard ship joined - production resumes
        with patch.object(Fleet, 'has_space_shipyard', new_callable=lambda: property(lambda self: True)):
            engine.process_fleet_production([empire], None, None)
            assert fleet.construction_queue[0]["turns_remaining"] == 4  # Decremented


class TestComplexPauseWhenFleetNotAtPlanet:
    """Tests for complex production pausing when fleet moves away from planet (PROJ-67 Phase 6)."""

    def test_complex_pauses_when_fleet_not_at_planet(self):
        """Complex production pauses when fleet is not at a planet hex."""
        engine = ProductionEngine()

        fleet = Fleet(1, 0, HexCoord(5, 5))
        fleet.construction_queue = [
            {"design_id": "factory_1", "type": "complex", "turns_remaining": 5}
        ]
        fleet.orders = [FleetOrder(OrderType.BUILD)]

        # Galaxy with no planet at fleet's location
        mock_galaxy = MagicMock()
        mock_galaxy.get_planets_at_global_hex.return_value = []

        with patch.object(Fleet, 'has_space_shipyard', new_callable=lambda: property(lambda self: True)):
            empire = MagicMock()
            empire.id = 0
            empire.fleets = [fleet]

            engine.process_fleet_production([empire], mock_galaxy, None)

        # Turns should NOT be decremented
        assert fleet.construction_queue[0]["turns_remaining"] == 5

    def test_ship_items_continue_even_when_not_at_planet(self):
        """Ship production continues even when fleet is not at a planet."""
        engine = ProductionEngine()

        fleet = Fleet(1, 0, HexCoord(5, 5))
        fleet.construction_queue = [
            {"design_id": "destroyer_1", "type": "ship", "turns_remaining": 5}
        ]
        fleet.orders = [FleetOrder(OrderType.BUILD)]

        # Galaxy with no planet at fleet's location
        mock_galaxy = MagicMock()
        mock_galaxy.get_planets_at_global_hex.return_value = []

        with patch.object(Fleet, 'has_space_shipyard', new_callable=lambda: property(lambda self: True)):
            empire = MagicMock()
            empire.id = 0
            empire.fleets = [fleet]

            engine.process_fleet_production([empire], mock_galaxy, None)

        # Turns SHOULD be decremented for ships
        assert fleet.construction_queue[0]["turns_remaining"] == 4

    def test_complex_resumes_when_fleet_returns_to_planet(self):
        """Complex production resumes when fleet returns to planet hex."""
        engine = ProductionEngine()

        fleet = Fleet(1, 0, HexCoord(5, 5))
        fleet.construction_queue = [
            {"design_id": "factory_1", "type": "complex", "turns_remaining": 5}
        ]
        fleet.orders = [FleetOrder(OrderType.BUILD)]

        mock_galaxy = MagicMock()
        empire = MagicMock()
        empire.id = 0
        empire.fleets = [fleet]

        # First turn: not at planet - paused
        mock_galaxy.get_planets_at_global_hex.return_value = []
        with patch.object(Fleet, 'has_space_shipyard', new_callable=lambda: property(lambda self: True)):
            engine.process_fleet_production([empire], mock_galaxy, None)
            assert fleet.construction_queue[0]["turns_remaining"] == 5

        # Second turn: at planet - resumes
        mock_planet = MagicMock()
        mock_galaxy.get_planets_at_global_hex.return_value = [mock_planet]
        with patch.object(Fleet, 'has_space_shipyard', new_callable=lambda: property(lambda self: True)):
            engine.process_fleet_production([empire], mock_galaxy, None)
            assert fleet.construction_queue[0]["turns_remaining"] == 4

    def test_complex_pauses_when_no_galaxy_provided(self):
        """Complex production pauses when no galaxy is provided."""
        engine = ProductionEngine()

        fleet = Fleet(1, 0, HexCoord(5, 5))
        fleet.construction_queue = [
            {"design_id": "factory_1", "type": "complex", "turns_remaining": 5}
        ]
        fleet.orders = [FleetOrder(OrderType.BUILD)]

        with patch.object(Fleet, 'has_space_shipyard', new_callable=lambda: property(lambda self: True)):
            empire = MagicMock()
            empire.id = 0
            empire.fleets = [fleet]

            engine.process_fleet_production([empire], None, None)  # No galaxy

        # Turns should NOT be decremented
        assert fleet.construction_queue[0]["turns_remaining"] == 5


class TestFleetComplexTargetPlanet:
    """PROJ-79 Phase 4: Tests for target_planet_id in fleet complex spawning."""

    def test_complex_spawns_on_target_planet_when_specified(self):
        """Complex should spawn on target_planet_id if specified."""
        engine = ProductionEngine()

        fleet = Fleet(1, 0, HexCoord(5, 5))
        fleet.construction_queue = [
            {
                "design_id": "factory_1",
                "type": "complex",
                "turns_remaining": 1,
                "target_planet_id": 20,  # Specific target
            }
        ]
        fleet.orders = [FleetOrder(OrderType.BUILD)]

        # Two planets at hex
        mock_planet1 = MagicMock()
        mock_planet1.id = 10
        mock_planet1.facilities = []
        mock_planet1.name = "Planet A"

        mock_planet2 = MagicMock()
        mock_planet2.id = 20
        mock_planet2.facilities = []
        mock_planet2.name = "Planet B"

        mock_galaxy = MagicMock()
        mock_galaxy.get_planets_at_global_hex.return_value = [mock_planet1, mock_planet2]

        with patch.object(Fleet, 'has_space_shipyard', new_callable=lambda: property(lambda self: True)):
            empire = MagicMock()
            empire.id = 0
            empire.fleets = [fleet]

            mock_design = {"name": "Factory", "layers": {}}

            with patch('game.strategy.engine.production_engine.DesignLibrary') as MockLib:
                mock_lib_instance = MagicMock()
                mock_lib_instance.load_design_data.return_value = mock_design
                MockLib.return_value = mock_lib_instance

                engine.process_fleet_production([empire], mock_galaxy, "/fake/save/path")

        # Complex should be on planet2 (target_planet_id=20), not planet1
        assert len(mock_planet1.facilities) == 0
        assert len(mock_planet2.facilities) == 1

    def test_complex_falls_back_to_first_planet_when_target_not_found(self):
        """Complex should fall back to first planet if target_planet_id not at hex."""
        engine = ProductionEngine()

        fleet = Fleet(1, 0, HexCoord(5, 5))
        fleet.construction_queue = [
            {
                "design_id": "factory_1",
                "type": "complex",
                "turns_remaining": 1,
                "target_planet_id": 999,  # Not at hex
            }
        ]
        fleet.orders = [FleetOrder(OrderType.BUILD)]

        # Only planet1 at hex
        mock_planet1 = MagicMock()
        mock_planet1.id = 10
        mock_planet1.facilities = []
        mock_planet1.name = "Planet A"

        mock_galaxy = MagicMock()
        mock_galaxy.get_planets_at_global_hex.return_value = [mock_planet1]

        with patch.object(Fleet, 'has_space_shipyard', new_callable=lambda: property(lambda self: True)):
            empire = MagicMock()
            empire.id = 0
            empire.fleets = [fleet]

            mock_design = {"name": "Factory", "layers": {}}

            with patch('game.strategy.engine.production_engine.DesignLibrary') as MockLib:
                mock_lib_instance = MagicMock()
                mock_lib_instance.load_design_data.return_value = mock_design
                MockLib.return_value = mock_lib_instance

                engine.process_fleet_production([empire], mock_galaxy, "/fake/save/path")

        # Complex should fall back to planet1
        assert len(mock_planet1.facilities) == 1

    def test_complex_uses_first_planet_when_no_target_specified(self):
        """Complex should use first planet when target_planet_id not specified (legacy)."""
        engine = ProductionEngine()

        fleet = Fleet(1, 0, HexCoord(5, 5))
        fleet.construction_queue = [
            {
                "design_id": "factory_1",
                "type": "complex",
                "turns_remaining": 1,
                # No target_planet_id - legacy behavior
            }
        ]
        fleet.orders = [FleetOrder(OrderType.BUILD)]

        mock_planet1 = MagicMock()
        mock_planet1.id = 10
        mock_planet1.facilities = []
        mock_planet1.name = "Planet A"

        mock_planet2 = MagicMock()
        mock_planet2.id = 20
        mock_planet2.facilities = []
        mock_planet2.name = "Planet B"

        mock_galaxy = MagicMock()
        mock_galaxy.get_planets_at_global_hex.return_value = [mock_planet1, mock_planet2]

        with patch.object(Fleet, 'has_space_shipyard', new_callable=lambda: property(lambda self: True)):
            empire = MagicMock()
            empire.id = 0
            empire.fleets = [fleet]

            mock_design = {"name": "Factory", "layers": {}}

            with patch('game.strategy.engine.production_engine.DesignLibrary') as MockLib:
                mock_lib_instance = MagicMock()
                mock_lib_instance.load_design_data.return_value = mock_design
                MockLib.return_value = mock_lib_instance

                engine.process_fleet_production([empire], mock_galaxy, "/fake/save/path")

        # Complex should be on planet1 (first in list)
        assert len(mock_planet1.facilities) == 1
        assert len(mock_planet2.facilities) == 0
