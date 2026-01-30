"""
Tests for turn processing structure and phases.

This test file covers:
- Turn processing structure (100 ticks, end-turn orders, production)
- Production processing delegation
- End-turn order execution
"""
import pytest
from unittest.mock import MagicMock, patch

from game.strategy.engine.turn_engine import TurnEngine
from game.strategy.data.fleet import FleetOrder, OrderType
from game.strategy.data.hex_math import HexCoord


# =============================================================================
# Test: Turn Processing Structure
# =============================================================================


class TestTurnProcessing:
    """Tests for process_turn method structure."""

    @patch.object(TurnEngine, '_process_tick')
    @patch.object(TurnEngine, '_process_end_turn_orders')
    @patch.object(TurnEngine, 'process_production')
    def test_process_turn_calls_subticks(self, mock_production, mock_end_turn, mock_tick,
                                         turn_engine, mock_empire, mock_galaxy):
        """process_turn calls _process_tick 100 times."""
        mock_empire.fleets = []

        turn_engine.process_turn([mock_empire], mock_galaxy)

        assert mock_tick.call_count == 100

    @patch.object(TurnEngine, '_process_tick')
    @patch.object(TurnEngine, '_process_end_turn_orders')
    @patch.object(TurnEngine, 'process_production')
    def test_process_turn_processes_end_turn_orders(self, mock_production, mock_end_turn, mock_tick,
                                                     turn_engine, mock_empire, mock_fleet, mock_galaxy):
        """process_turn calls end-turn order processing for each fleet."""
        mock_empire.fleets = [mock_fleet]

        turn_engine.process_turn([mock_empire], mock_galaxy)

        mock_end_turn.assert_called()

    @patch.object(TurnEngine, '_process_tick')
    @patch.object(TurnEngine, '_process_end_turn_orders')
    @patch.object(TurnEngine, 'process_production')
    def test_process_turn_runs_production(self, mock_production, mock_end_turn, mock_tick,
                                          turn_engine, mock_empire, mock_galaxy):
        """process_turn calls production phase."""
        mock_empire.fleets = []

        turn_engine.process_turn([mock_empire], mock_galaxy)

        mock_production.assert_called_once()


# =============================================================================
# Test: Production Processing
# =============================================================================


class TestProductionProcessing:
    """Tests for process_production method."""

    def test_empty_queue_skipped(self, turn_engine, mock_empire, mock_planet):
        """Colonies with empty queues are skipped."""
        mock_planet.construction_queue = []
        mock_empire.colonies = [mock_planet]

        turn_engine.process_production([mock_empire])

        # No errors, nothing built

    def test_production_decrements_turns(self, turn_engine, mock_empire, mock_planet):
        """Production decrements turns remaining."""
        mock_planet.construction_queue = [{"type": "ship", "design_id": "Scout", "turns_remaining": 3}]
        mock_planet.has_space_shipyard = True
        mock_empire.colonies = [mock_planet]

        turn_engine.process_production([mock_empire])

        assert mock_planet.construction_queue[0]["turns_remaining"] == 2

    def test_production_completes_at_zero(self, turn_engine, mock_empire, mock_planet, mock_galaxy):
        """Production completes when turns reach zero."""
        mock_planet.construction_queue = [{"type": "ship", "design_id": "Scout", "turns_remaining": 1}]
        mock_planet.has_space_shipyard = True
        mock_empire.colonies = [mock_planet]

        # PROJ-12: TurnEngine delegates to ProductionEngine, so patch there
        with patch.object(turn_engine.production_engine, '_spawn_ship') as mock_spawn:
            turn_engine.process_production([mock_empire], mock_galaxy)

            mock_spawn.assert_called()
            assert len(mock_planet.construction_queue) == 0

    def test_no_shipyard_pauses_production(self, turn_engine, mock_empire, mock_planet):
        """Ships require shipyard to build."""
        mock_planet.construction_queue = [{"type": "ship", "design_id": "Scout", "turns_remaining": 1}]
        mock_planet.has_space_shipyard = False
        mock_empire.colonies = [mock_planet]

        turn_engine.process_production([mock_empire])

        # Turns should NOT decrement
        assert mock_planet.construction_queue[0]["turns_remaining"] == 1

    def test_complex_production_no_shipyard_needed(self, turn_engine, mock_empire, mock_planet, mock_galaxy):
        """Complexes don't need shipyard."""
        mock_planet.construction_queue = [{"type": "complex", "design_id": "Factory", "turns_remaining": 1}]
        mock_planet.has_space_shipyard = False
        mock_empire.colonies = [mock_planet]

        # PROJ-12: TurnEngine delegates to ProductionEngine, so patch there
        with patch.object(turn_engine.production_engine, '_spawn_complex') as mock_spawn:
            turn_engine.process_production([mock_empire], mock_galaxy)

            mock_spawn.assert_called()


# =============================================================================
# Test: End-Turn Order Processing
# =============================================================================


class TestEndTurnOrders:
    """Tests for _process_end_turn_orders method."""

    def test_no_order_returns_false(self, turn_engine, mock_fleet, mock_empire, mock_galaxy):
        """Fleet with no order returns False."""
        mock_fleet.get_current_order.return_value = None

        result = turn_engine._process_end_turn_orders(mock_fleet, mock_empire, mock_galaxy)

        assert result is False

    def test_colonize_order_executes(self, turn_engine, mock_fleet, mock_empire, mock_galaxy, mock_planet):
        """COLONIZE order transfers planet ownership."""
        order = FleetOrder(OrderType.COLONIZE, mock_planet)
        mock_fleet.get_current_order.return_value = order
        mock_fleet.location = mock_planet.location
        mock_galaxy.get_planets_at_global_hex.return_value = [mock_planet]

        result = turn_engine._process_end_turn_orders(mock_fleet, mock_empire, mock_galaxy)

        assert result is True
        mock_empire.add_colony.assert_called_with(mock_planet)
        mock_empire.remove_fleet.assert_called_with(mock_fleet)

    def test_colonize_any_finds_planet(self, turn_engine, mock_fleet, mock_empire, mock_galaxy, mock_planet):
        """COLONIZE with None target finds valid planet."""
        order = FleetOrder(OrderType.COLONIZE, None)  # "Any"
        mock_fleet.get_current_order.return_value = order
        mock_fleet.location = mock_planet.location
        mock_galaxy.get_planets_at_global_hex.return_value = [mock_planet]

        result = turn_engine._process_end_turn_orders(mock_fleet, mock_empire, mock_galaxy)

        assert result is True
        mock_empire.add_colony.assert_called_with(mock_planet)

    def test_colonize_invalid_pops_order(self, turn_engine, mock_fleet, mock_empire, mock_galaxy):
        """Invalid COLONIZE pops order and returns False."""
        order = FleetOrder(OrderType.COLONIZE, None)
        mock_fleet.get_current_order.return_value = order
        mock_galaxy.get_planets_at_global_hex.return_value = []  # No planets

        result = turn_engine._process_end_turn_orders(mock_fleet, mock_empire, mock_galaxy)

        assert result is False
        mock_fleet.pop_order.assert_called()

    def test_join_fleet_at_location(self, turn_engine, mock_fleet, mock_empire, mock_galaxy):
        """JOIN_FLEET merges when at same location."""
        target_fleet = MagicMock()
        target_fleet.location = HexCoord(0, 0)

        order = FleetOrder(OrderType.JOIN_FLEET, target_fleet)
        mock_fleet.get_current_order.return_value = order
        mock_fleet.location = HexCoord(0, 0)
        mock_fleet.merge_with = MagicMock()

        result = turn_engine._process_end_turn_orders(mock_fleet, mock_empire, mock_galaxy)

        assert result is True
        mock_fleet.merge_with.assert_called_with(target_fleet)
        mock_empire.remove_fleet.assert_called_with(mock_fleet)

    def test_join_fleet_wrong_location(self, turn_engine, mock_fleet, mock_empire, mock_galaxy):
        """JOIN_FLEET fails when not at target location."""
        target_fleet = MagicMock()
        target_fleet.location = HexCoord(100, 100)

        order = FleetOrder(OrderType.JOIN_FLEET, target_fleet)
        mock_fleet.get_current_order.return_value = order
        mock_fleet.location = HexCoord(0, 0)  # Different location

        result = turn_engine._process_end_turn_orders(mock_fleet, mock_empire, mock_galaxy)

        assert result is False
        mock_fleet.pop_order.assert_called()

    def test_join_fleet_invalid_target(self, turn_engine, mock_fleet, mock_empire, mock_galaxy):
        """JOIN_FLEET with invalid target pops order."""
        order = FleetOrder(OrderType.JOIN_FLEET, None)
        mock_fleet.get_current_order.return_value = order

        result = turn_engine._process_end_turn_orders(mock_fleet, mock_empire, mock_galaxy)

        assert result is False
        mock_fleet.pop_order.assert_called()
