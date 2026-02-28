"""
Tests for command handler registry and individual handlers.

PROJ-87 Phase 5: Tests for the extracted command handler system.
"""
import pytest
from unittest.mock import Mock, MagicMock, patch, PropertyMock

from game.core.hex_math import HexCoord
from game.strategy.engine.command_handlers import (
    CommandHandlerRegistry,
    ColonizeCommandHandler,
    MoveCommandHandler,
    BuildShipCommandHandler,
    InterceptCommandHandler,
    JoinCommandHandler,
    ColonizeMissionCommandHandler,
    ClearOrdersCommandHandler,
    TransferCommandHandler,
    create_default_registry,
)
from game.core.validation import ValidationResult


class TestCommandHandlerRegistry:
    """Tests for CommandHandlerRegistry class."""

    def test_register_and_dispatch(self):
        """Registry dispatches to registered handler."""
        registry = CommandHandlerRegistry()
        mock_handler = Mock()
        mock_handler.execute.return_value = ValidationResult()

        registry.register('TestCommand', mock_handler)
        mock_session = Mock()
        mock_command = Mock()

        result = registry.dispatch('TestCommand', mock_session, mock_command)

        assert result.is_valid
        mock_handler.execute.assert_called_once_with(mock_session, mock_command)

    def test_dispatch_unknown_command_returns_failure(self):
        """Unknown command type returns failure result."""
        registry = CommandHandlerRegistry()
        mock_session = Mock()
        mock_command = Mock()

        result = registry.dispatch('UnknownCommand', mock_session, mock_command)

        assert not result.is_valid
        assert "Unknown command type" in result.message

    def test_create_default_registry_has_all_handlers(self):
        """Default registry has all 8 standard handlers registered."""
        registry = create_default_registry()

        expected_commands = [
            'IssueColonizeCommand',
            'IssueMoveCommand',
            'IssueBuildShipCommand',
            'IssueInterceptCommand',
            'IssueJoinFleetCommand',
            'QueueColonizeMissionCommand',
            'ClearFleetOrdersCommand',
            'IssueTransferCommand',
        ]

        for cmd_name in expected_commands:
            assert cmd_name in registry._handlers, f"Missing handler for {cmd_name}"


class TestColonizeCommandHandler:
    """Tests for ColonizeCommandHandler."""

    def test_fleet_not_found(self):
        """Returns failure when fleet not found."""
        handler = ColonizeCommandHandler()
        mock_session = Mock()
        mock_session._get_fleet_by_id.return_value = None
        mock_cmd = Mock(fleet_id=999, planet_id=1)

        result = handler.execute(mock_session, mock_cmd)

        assert not result.is_valid
        assert "Fleet not found" in result.message

    def test_valid_colonize_creates_order(self):
        """Valid colonize adds order to fleet."""
        handler = ColonizeCommandHandler()

        mock_fleet = Mock()
        mock_fleet.id = 1
        mock_fleet.location = HexCoord(0, 0)  # Fleet already at planet location
        mock_fleet.orders = []
        mock_fleet.add_order = Mock()

        mock_planet = Mock()
        mock_planet.id = 10
        mock_planet.populations = []

        mock_session = Mock()
        mock_session._get_fleet_by_id.return_value = mock_fleet
        mock_session._get_planet_by_id.return_value = mock_planet
        mock_session.galaxy.get_planet_global_hex.return_value = HexCoord(0, 0)
        mock_session.turn_engine.validate_colonize_order.return_value = ValidationResult()
        mock_session._find_colony_at_fleet.return_value = None

        mock_cmd = Mock(fleet_id=1, planet_id=10)

        result = handler.execute(mock_session, mock_cmd)

        assert result.is_valid
        mock_fleet.add_order.assert_called_once()


class TestMoveCommandHandler:
    """Tests for MoveCommandHandler."""

    def test_fleet_not_found(self):
        """Returns failure when fleet not found."""
        handler = MoveCommandHandler()
        mock_session = Mock()
        mock_session._get_fleet_by_id.return_value = None
        mock_cmd = Mock(fleet_id=999, target_hex=(0, 0))

        result = handler.execute(mock_session, mock_cmd)

        assert not result.is_valid
        assert "Fleet not found" in result.message

    def test_unreachable_target(self):
        """Returns failure when path not found."""
        handler = MoveCommandHandler()

        mock_fleet = Mock()
        mock_fleet.location = (0, 0)

        mock_session = Mock()
        mock_session._get_fleet_by_id.return_value = mock_fleet
        mock_session.preview_fleet_path.return_value = None

        mock_cmd = Mock(fleet_id=1, target_hex=(100, 100))

        result = handler.execute(mock_session, mock_cmd)

        assert not result.is_valid
        assert "unreachable" in result.message.lower()

    def test_valid_move_creates_order(self):
        """Valid move adds order and sets path."""
        handler = MoveCommandHandler()

        mock_fleet = Mock()
        mock_fleet.location = (0, 0)
        mock_fleet.orders = []
        mock_fleet.add_order = Mock()

        mock_session = Mock()
        mock_session._get_fleet_by_id.return_value = mock_fleet
        mock_session.preview_fleet_path.return_value = [(1, 0), (2, 0)]

        mock_cmd = Mock(fleet_id=1, target_hex=(2, 0))

        result = handler.execute(mock_session, mock_cmd)

        assert result.is_valid
        mock_fleet.add_order.assert_called_once()


class TestBuildShipCommandHandler:
    """Tests for BuildShipCommandHandler."""

    def test_planet_not_found(self):
        """Returns failure when planet not found."""
        handler = BuildShipCommandHandler()
        mock_session = Mock()
        mock_session._get_planet_by_id.return_value = None
        mock_cmd = Mock(planet_id=999, design_name="Scout")

        result = handler.execute(mock_session, mock_cmd)

        assert not result.is_valid
        assert "Planet not found" in result.message

    def test_valid_build_adds_production(self):
        """Valid build calls add_production on planet."""
        handler = BuildShipCommandHandler()

        mock_planet = Mock()
        mock_planet.add_production = Mock()

        mock_session = Mock()
        mock_session._get_planet_by_id.return_value = mock_planet

        mock_cmd = Mock(planet_id=1, design_name="Scout")

        result = handler.execute(mock_session, mock_cmd)

        assert result.is_valid
        mock_planet.add_production.assert_called_once_with("Scout", 1)


class TestInterceptCommandHandler:
    """Tests for InterceptCommandHandler."""

    def test_fleet_not_found(self):
        """Returns failure when source fleet not found."""
        handler = InterceptCommandHandler()
        mock_session = Mock()
        mock_session._get_fleet_by_id.return_value = None
        mock_cmd = Mock(fleet_id=999, target_fleet_id=2)

        result = handler.execute(mock_session, mock_cmd)

        assert not result.is_valid
        assert "Fleet not found" in result.message

    def test_target_fleet_not_found(self):
        """Returns failure when target fleet not found."""
        handler = InterceptCommandHandler()

        mock_fleet = Mock()
        mock_fleet.id = 1

        mock_session = Mock()
        mock_session._get_fleet_by_id.side_effect = lambda fid: mock_fleet if fid == 1 else None

        mock_cmd = Mock(fleet_id=1, target_fleet_id=999)

        result = handler.execute(mock_session, mock_cmd)

        assert not result.is_valid
        assert "Target fleet not found" in result.message

    def test_valid_intercept_creates_order(self):
        """Valid intercept adds MOVE_TO_FLEET order."""
        handler = InterceptCommandHandler()

        mock_fleet = Mock()
        mock_fleet.id = 1
        mock_fleet.add_order = Mock()

        mock_target = Mock()
        mock_target.id = 2

        mock_session = Mock()
        mock_session._get_fleet_by_id.side_effect = lambda fid: mock_fleet if fid == 1 else mock_target

        mock_cmd = Mock(fleet_id=1, target_fleet_id=2)

        result = handler.execute(mock_session, mock_cmd)

        assert result.is_valid
        mock_fleet.add_order.assert_called_once()


class TestJoinCommandHandler:
    """Tests for JoinCommandHandler."""

    def test_valid_join_creates_two_orders(self):
        """Valid join adds MOVE_TO_FLEET and JOIN_FLEET orders."""
        handler = JoinCommandHandler()

        mock_fleet = Mock()
        mock_fleet.id = 1
        mock_fleet.add_order = Mock()

        mock_target = Mock()
        mock_target.id = 2

        mock_session = Mock()
        mock_session._get_fleet_by_id.side_effect = lambda fid: mock_fleet if fid == 1 else mock_target

        mock_cmd = Mock(fleet_id=1, target_fleet_id=2)

        result = handler.execute(mock_session, mock_cmd)

        assert result.is_valid
        assert mock_fleet.add_order.call_count == 2


class TestColonizeMissionCommandHandler:
    """Tests for ColonizeMissionCommandHandler."""

    def test_fleet_not_found(self):
        """Returns failure when fleet not found."""
        handler = ColonizeMissionCommandHandler()
        mock_session = Mock()
        mock_session._get_fleet_by_id.return_value = None
        mock_cmd = Mock(fleet_id=999, planet_id=None, target_hex=(0, 0))

        result = handler.execute(mock_session, mock_cmd)

        assert not result.is_valid
        assert "Fleet not found" in result.message

    def test_no_path_found(self):
        """Returns failure when no path to target."""
        handler = ColonizeMissionCommandHandler()

        mock_fleet = Mock()
        mock_fleet.location = (0, 0)
        mock_fleet.orders = []

        mock_session = Mock()
        mock_session._get_fleet_by_id.return_value = mock_fleet
        mock_session._get_planet_by_id.return_value = None

        mock_cmd = Mock(fleet_id=1, planet_id=None, target_hex=(100, 100))

        with patch('game.strategy.data.pathfinding.find_hybrid_path', return_value=None):
            result = handler.execute(mock_session, mock_cmd)

        assert not result.is_valid
        assert "No path found" in result.message


class TestClearOrdersCommandHandler:
    """Tests for ClearOrdersCommandHandler."""

    def test_fleet_not_found(self):
        """Returns failure when fleet not found."""
        handler = ClearOrdersCommandHandler()
        mock_session = Mock()
        mock_session._get_fleet_by_id.return_value = None
        mock_cmd = Mock(fleet_id=999)

        result = handler.execute(mock_session, mock_cmd)

        assert not result.is_valid
        assert "Fleet not found" in result.message

    def test_clears_orders_and_path(self):
        """Valid clear resets orders and path lists."""
        handler = ClearOrdersCommandHandler()

        mock_fleet = Mock()
        mock_fleet.id = 1
        mock_fleet.orders = ['order1', 'order2']
        mock_fleet.path = ['hex1', 'hex2']

        mock_session = Mock()
        mock_session._get_fleet_by_id.return_value = mock_fleet

        mock_cmd = Mock(fleet_id=1)

        result = handler.execute(mock_session, mock_cmd)

        assert result.is_valid
        assert mock_fleet.orders == []
        assert mock_fleet.path == []


class TestTransferCommandHandler:
    """Tests for TransferCommandHandler."""

    def test_fleet_not_found(self):
        """Returns failure when fleet not found."""
        handler = TransferCommandHandler()
        mock_session = Mock()
        mock_session._get_fleet_by_id.return_value = None
        mock_cmd = Mock(fleet_id=999)

        result = handler.execute(mock_session, mock_cmd)

        assert not result.is_valid
        assert "Fleet not found" in result.message

    def test_fleet_owner_not_found(self):
        """Returns failure when fleet owner empire not found."""
        handler = TransferCommandHandler()

        mock_fleet = Mock()
        mock_fleet.id = 1
        mock_fleet.ships = []
        mock_fleet.location = (0, 0)
        mock_fleet.owner_id = 99  # Invalid owner_id

        mock_empire = Mock()
        mock_empire.fleets = []  # Fleet not in any empire

        mock_session = Mock()
        mock_session._get_fleet_by_id.return_value = mock_fleet
        mock_session.empires = [mock_empire]

        mock_cmd = Mock(fleet_id=1)

        result = handler.execute(mock_session, mock_cmd)

        assert not result.is_valid
        assert "Fleet owner not found" in result.message

    def test_planet_not_found(self):
        """Returns failure when planet not found."""
        handler = TransferCommandHandler()

        mock_fleet = Mock()
        mock_fleet.id = 1
        mock_fleet.ships = []
        mock_fleet.location = (0, 0)
        mock_fleet.owner_id = 0  # Valid owner_id

        mock_empire = Mock()
        mock_empire.fleets = [mock_fleet]

        mock_session = Mock()
        mock_session._get_fleet_by_id.return_value = mock_fleet
        mock_session.empires = [mock_empire]
        mock_session._get_planet_by_id.return_value = None

        mock_cmd = Mock(fleet_id=1, planet_id=999)

        result = handler.execute(mock_session, mock_cmd)

        assert not result.is_valid
        assert "Planet not found" in result.message

    def test_valid_transfer_creates_order(self):
        """Valid transfer validates and adds TRANSFER order."""
        handler = TransferCommandHandler()

        mock_fleet = Mock()
        mock_fleet.id = 1
        mock_fleet.ships = []
        mock_fleet.location = HexCoord(0, 0)  # Fleet already at planet location
        mock_fleet.orders = []
        mock_fleet.add_order = Mock()
        mock_fleet.owner_id = 0  # Valid owner_id

        mock_empire = Mock()
        mock_empire.fleets = [mock_fleet]

        mock_planet = Mock()
        mock_planet.id = 10
        mock_planet.name = "TestPlanet"
        mock_planet.owner_id = 0
        mock_planet.total_population = 1000

        mock_session = Mock()
        mock_session._get_fleet_by_id.return_value = mock_fleet
        mock_session.empires = [mock_empire]
        mock_session._get_planet_by_id.return_value = mock_planet
        mock_session.galaxy = Mock()
        mock_session.galaxy.get_planet_global_hex.return_value = HexCoord(0, 0)

        mock_cmd = Mock(
            fleet_id=1,
            planet_id=10,
            cargo_type='fuel',
            direction='load',
            amount=100,
            species_id=None
        )

        with patch('game.strategy.validation.TransferValidator') as mock_validator:
            mock_validator.validate.return_value = ValidationResult()
            result = handler.execute(mock_session, mock_cmd)

        assert result.is_valid
        mock_fleet.add_order.assert_called_once()


class TestBaseCommandHandler:
    """Tests for BaseCommandHandler resolution helpers."""

    def test_resolve_fleet_required_returns_fleet_when_found(self):
        """_resolve_fleet_required returns fleet when found."""
        from game.strategy.engine.command_handlers import BaseCommandHandler

        handler = BaseCommandHandler()
        mock_fleet = Mock()
        mock_fleet.id = 1

        mock_session = Mock()
        mock_session._get_fleet_by_id.return_value = mock_fleet

        fleet = handler._resolve_fleet_required(mock_session, 1)

        assert fleet is mock_fleet

    def test_resolve_fleet_required_raises_when_not_found(self):
        """_resolve_fleet_required raises ValueError when fleet not found."""
        from game.strategy.engine.command_handlers import BaseCommandHandler

        handler = BaseCommandHandler()
        mock_session = Mock()
        mock_session._get_fleet_by_id.return_value = None

        with pytest.raises(ValueError) as exc_info:
            handler._resolve_fleet_required(mock_session, 999)

        assert "Fleet not found" in str(exc_info.value)

    def test_resolve_fleet_required_validates_ownership(self):
        """_resolve_fleet_required raises when owner_id doesn't match."""
        from game.strategy.engine.command_handlers import BaseCommandHandler

        handler = BaseCommandHandler()
        mock_fleet = Mock()
        mock_fleet.id = 1
        mock_fleet.owner_id = 0

        mock_session = Mock()
        mock_session._get_fleet_by_id.return_value = mock_fleet

        with pytest.raises(ValueError) as exc_info:
            handler._resolve_fleet_required(mock_session, 1, empire_id=99)

        assert "does not belong" in str(exc_info.value)

    def test_resolve_planet_optional_returns_planet_when_found(self):
        """_resolve_planet_optional returns planet when found."""
        from game.strategy.engine.command_handlers import BaseCommandHandler

        handler = BaseCommandHandler()
        mock_planet = Mock()
        mock_planet.id = 10

        mock_session = Mock()
        mock_session._get_planet_by_id.return_value = mock_planet

        planet = handler._resolve_planet_optional(mock_session, 10)

        assert planet is mock_planet

    def test_resolve_planet_optional_returns_none_when_not_found_and_not_required(self):
        """_resolve_planet_optional returns None when not found and required=False."""
        from game.strategy.engine.command_handlers import BaseCommandHandler

        handler = BaseCommandHandler()
        mock_session = Mock()
        mock_session._get_planet_by_id.return_value = None

        planet = handler._resolve_planet_optional(mock_session, 999, required=False)

        assert planet is None

    def test_resolve_planet_optional_raises_when_not_found_and_required(self):
        """_resolve_planet_optional raises ValueError when not found and required=True."""
        from game.strategy.engine.command_handlers import BaseCommandHandler

        handler = BaseCommandHandler()
        mock_session = Mock()
        mock_session._get_planet_by_id.return_value = None

        with pytest.raises(ValueError) as exc_info:
            handler._resolve_planet_optional(mock_session, 999, required=True)

        assert "Planet not found" in str(exc_info.value)


class TestCommandHelpers:
    """Tests for command handler helper functions."""

    def test_add_move_order_if_needed_no_move_when_at_target(self):
        """add_move_order_if_needed does not add move when fleet at target."""
        from game.strategy.engine.command_handlers import add_move_order_if_needed

        mock_fleet = Mock()
        mock_fleet.location = HexCoord(5, 5)
        mock_fleet.orders = []
        mock_fleet.add_order = Mock()

        mock_session = Mock()

        result = add_move_order_if_needed(mock_session, mock_fleet, HexCoord(5, 5))

        assert result.is_valid
        mock_fleet.add_order.assert_not_called()

    def test_add_move_order_if_needed_adds_move_when_not_at_target(self):
        """add_move_order_if_needed adds MOVE order when fleet not at target."""
        from game.strategy.engine.command_handlers import add_move_order_if_needed
        from game.strategy.data.fleet import OrderType

        mock_fleet = Mock()
        mock_fleet.location = HexCoord(0, 0)
        mock_fleet.orders = []
        mock_fleet.add_order = Mock()

        mock_session = Mock()
        mock_session.galaxy = Mock()

        target = HexCoord(5, 5)

        with patch('game.strategy.engine.command_handlers.find_hybrid_path') as mock_path:
            mock_path.return_value = [HexCoord(1, 0), HexCoord(2, 0), HexCoord(5, 5)]
            result = add_move_order_if_needed(mock_session, mock_fleet, target)

        assert result.is_valid
        mock_fleet.add_order.assert_called_once()
        call_args = mock_fleet.add_order.call_args[0][0]
        assert call_args.type == OrderType.MOVE
        assert call_args.target == target

    def test_add_move_order_if_needed_returns_error_when_no_path(self):
        """add_move_order_if_needed returns error when no path found."""
        from game.strategy.engine.command_handlers import add_move_order_if_needed

        mock_fleet = Mock()
        mock_fleet.location = HexCoord(0, 0)
        mock_fleet.orders = []

        mock_session = Mock()
        mock_session.galaxy = Mock()

        with patch('game.strategy.engine.command_handlers.find_hybrid_path') as mock_path:
            mock_path.return_value = None
            result = add_move_order_if_needed(mock_session, mock_fleet, HexCoord(100, 100))

        assert not result.is_valid
        assert "No path found" in result.message
