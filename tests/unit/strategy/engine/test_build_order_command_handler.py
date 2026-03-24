"""Tests for BuildOrderCommandHandler, IssueBuildOrderCommand, and helper functions.

PROJ-207 Phase 4: Tests for routing BUILD orders through command pipeline.
CP-002 - Build orders should use command pipeline instead of direct FleetOrder creation.
CP-003 - Shared auto-load population helper.
"""
import pytest
from unittest.mock import Mock, MagicMock

from game.strategy.engine.commands import IssueBuildOrderCommand, CommandType
from game.strategy.engine.command_handlers import (
    BuildOrderCommandHandler,
    create_auto_load_population_order
)
from game.strategy.data.order_types import FleetOrder, OrderType


class TestIssueBuildOrderCommand:
    """Tests for IssueBuildOrderCommand dataclass."""

    def test_create_build_order_command(self):
        """IssueBuildOrderCommand should store fleet_id."""
        cmd = IssueBuildOrderCommand(fleet_id=10)
        assert cmd.fleet_id == 10
        assert cmd.type == CommandType.ISSUE_ORDER

    def test_command_name(self):
        """Command name property should return class name."""
        cmd = IssueBuildOrderCommand(fleet_id=1)
        assert cmd.name == "IssueBuildOrderCommand"

    def test_commands_with_same_fleet_are_equal(self):
        """Commands with same fleet_id should be equal."""
        cmd1 = IssueBuildOrderCommand(fleet_id=5)
        cmd2 = IssueBuildOrderCommand(fleet_id=5)
        assert cmd1 == cmd2

    def test_commands_with_different_fleet_are_not_equal(self):
        """Commands with different fleet_id should not be equal."""
        cmd1 = IssueBuildOrderCommand(fleet_id=5)
        cmd2 = IssueBuildOrderCommand(fleet_id=6)
        assert cmd1 != cmd2


class TestBuildOrderCommandHandler:
    """Tests for BuildOrderCommandHandler."""

    def test_handler_creates_build_order(self):
        """Handler should create BUILD order and insert at position 0."""
        # Setup
        handler = BuildOrderCommandHandler()
        session = Mock()
        mock_fleet = Mock()
        mock_fleet.orders = []
        session._get_fleet_by_id.return_value = mock_fleet

        cmd = IssueBuildOrderCommand(fleet_id=10)

        # Execute
        result = handler.execute(session, cmd)

        # Verify
        assert result.is_valid
        assert len(mock_fleet.orders) == 1
        assert mock_fleet.orders[0].type == OrderType.BUILD
        assert mock_fleet.path == []  # Path should be cleared

    def test_handler_inserts_at_position_0(self):
        """BUILD order should be inserted at position 0 (front of queue)."""
        handler = BuildOrderCommandHandler()
        session = Mock()

        # Fleet already has a MOVE order
        existing_order = FleetOrder(OrderType.MOVE, target=Mock())
        mock_fleet = Mock()
        mock_fleet.orders = [existing_order]
        session._get_fleet_by_id.return_value = mock_fleet

        cmd = IssueBuildOrderCommand(fleet_id=10)

        result = handler.execute(session, cmd)

        assert result.is_valid
        assert len(mock_fleet.orders) == 2
        assert mock_fleet.orders[0].type == OrderType.BUILD
        assert mock_fleet.orders[1].type == OrderType.MOVE

    def test_handler_clears_path(self):
        """Handler should clear fleet.path when adding BUILD order."""
        handler = BuildOrderCommandHandler()
        session = Mock()
        mock_fleet = Mock()
        mock_fleet.orders = []
        mock_fleet.path = [Mock(), Mock(), Mock()]  # Existing path
        session._get_fleet_by_id.return_value = mock_fleet

        cmd = IssueBuildOrderCommand(fleet_id=10)

        result = handler.execute(session, cmd)

        assert result.is_valid
        assert mock_fleet.path == []

    def test_handler_returns_error_if_fleet_not_found(self):
        """Handler should return error if fleet doesn't exist."""
        handler = BuildOrderCommandHandler()
        session = Mock()
        session._get_fleet_by_id.return_value = None

        cmd = IssueBuildOrderCommand(fleet_id=999)

        result = handler.execute(session, cmd)

        assert not result.is_valid
        assert "Fleet not found" in result.errors[0]


class TestRemoveBuildOrderCommand:
    """Tests for RemoveBuildOrderCommand and handler."""

    def test_remove_build_order_command_creation(self):
        """RemoveBuildOrderCommand should store fleet_id."""
        from game.strategy.engine.commands import RemoveBuildOrderCommand
        cmd = RemoveBuildOrderCommand(fleet_id=15)
        assert cmd.fleet_id == 15
        assert cmd.type == CommandType.ISSUE_ORDER

    def test_handler_removes_build_orders(self):
        """Handler should call fleet.remove_orders_by_type(BUILD) (PROJ-222: uses Fleet API)."""
        from game.strategy.engine.commands import RemoveBuildOrderCommand
        from game.strategy.engine.command_handlers import RemoveBuildOrderCommandHandler

        handler = RemoveBuildOrderCommandHandler()
        session = Mock()

        mock_fleet = Mock()
        session._get_fleet_by_id.return_value = mock_fleet

        cmd = RemoveBuildOrderCommand(fleet_id=15)

        result = handler.execute(session, cmd)

        assert result.is_valid
        mock_fleet.remove_orders_by_type.assert_called_once_with(OrderType.BUILD)

    def test_handler_does_nothing_if_no_build_order(self):
        """Handler should succeed even if no BUILD order exists."""
        from game.strategy.engine.commands import RemoveBuildOrderCommand
        from game.strategy.engine.command_handlers import RemoveBuildOrderCommandHandler

        handler = RemoveBuildOrderCommandHandler()
        session = Mock()

        # Fleet with only MOVE order
        move_order = FleetOrder(OrderType.MOVE, target=Mock())
        mock_fleet = Mock()
        mock_fleet.orders = [move_order]
        session._get_fleet_by_id.return_value = mock_fleet

        cmd = RemoveBuildOrderCommand(fleet_id=15)

        result = handler.execute(session, cmd)

        assert result.is_valid
        assert len(mock_fleet.orders) == 1
        assert mock_fleet.orders[0].type == OrderType.MOVE


class TestBuildOrderHandlerRegistration:
    """Tests for handler registration in create_default_registry()."""

    def test_build_order_handler_registered(self):
        """BuildOrderCommandHandler should be registered."""
        from game.strategy.engine.command_handlers import create_default_registry

        registry = create_default_registry()

        # Should have handler registered
        assert 'IssueBuildOrderCommand' in registry._handlers
        assert isinstance(registry._handlers['IssueBuildOrderCommand'], BuildOrderCommandHandler)

    def test_remove_build_order_handler_registered(self):
        """RemoveBuildOrderCommandHandler should be registered."""
        from game.strategy.engine.command_handlers import (
            create_default_registry,
            RemoveBuildOrderCommandHandler
        )

        registry = create_default_registry()

        assert 'RemoveBuildOrderCommand' in registry._handlers
        assert isinstance(registry._handlers['RemoveBuildOrderCommand'], RemoveBuildOrderCommandHandler)


class TestCreateAutoLoadPopulationOrder:
    """Tests for create_auto_load_population_order helper (BUG-70 rework)."""

    def test_creates_generic_load_order(self):
        """Should create a generic LOAD_POPULATION order with no planet_id."""
        order = create_auto_load_population_order()

        assert order is not None
        assert order.type == OrderType.LOAD_POPULATION
        assert order.target['direction'] == 'load'
        assert order.target['cargo_type'] == 'passengers'
        assert order.target['amount'] == 0
        assert 'planet_id' not in order.target
        assert 'species_id' not in order.target

    def test_always_returns_order(self):
        """Should always return an order (never None). Colony resolved at execution time."""
        order = create_auto_load_population_order()
        assert order is not None
