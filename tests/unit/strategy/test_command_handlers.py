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
    # NOTE: BuildShipCommandHandler removed in PROJ-208 (dead code)
    InterceptCommandHandler,
    JoinCommandHandler,
    ColonizeMissionCommandHandler,
    ClearOrdersCommandHandler,
    TransferCommandHandler,
    SplitFleetCommandHandler,
    DeleteOrderCommandHandler,
    ReorderOrderCommandHandler,
    AddToConstructionQueueCommandHandler,
    RemoveFromConstructionQueueCommandHandler,
    ReorderConstructionQueueCommandHandler,
    create_default_registry,
)
from game.core.validation import ValidationResult
from game.strategy.data.fleet import Fleet


class TestCommandHandlerRegistry:
    """Tests for CommandHandlerRegistry class."""

    def test_register_and_dispatch(self):
        """Registry dispatches to registered handler."""
        registry = CommandHandlerRegistry()
        mock_handler = Mock()
        mock_handler.execute.return_value = ValidationResult()

        registry.register('TestCommand', mock_handler)
        mock_session = Mock()
        mock_session.active_empire = Mock(id=0)
        mock_command = Mock()

        result = registry.dispatch('TestCommand', mock_session, mock_command)

        assert result.is_valid
        mock_handler.execute.assert_called_once_with(mock_session, mock_command)

    def test_dispatch_unknown_command_returns_failure(self):
        """Unknown command type returns failure result."""
        registry = CommandHandlerRegistry()
        mock_session = Mock()
        mock_session.active_empire = Mock(id=0)
        mock_command = Mock()

        result = registry.dispatch('UnknownCommand', mock_session, mock_command)

        assert not result.is_valid
        assert "Unknown command type" in result.message

    def test_create_default_registry_has_all_handlers(self):
        """Default registry has all standard handlers registered."""
        registry = create_default_registry()

        expected_commands = [
            'IssueColonizeCommand',
            'IssueMoveCommand',
            # NOTE: IssueBuildShipCommand removed in PROJ-208 (dead code)
            'IssueInterceptCommand',
            'IssueJoinFleetCommand',
            'QueueColonizeMissionCommand',
            'ClearOrdersCommand',
            'IssueTransferCommand',
            # PROJ-208 Fleet Management Commands
            'SplitFleetCommand',
            'DeleteOrderCommand',
            'ReorderOrderCommand',
            # PROJ-208 Phase 2: Construction Queue Commands
            'AddToConstructionQueueCommand',
            'RemoveFromConstructionQueueCommand',
            'ReorderConstructionQueueCommand',
        ]

        for cmd_name in expected_commands:
            assert cmd_name in registry._handlers, f"Missing handler for {cmd_name}"


class TestColonizeCommandHandler:
    """Tests for ColonizeCommandHandler."""

    def test_fleet_not_found(self):
        """Returns failure when fleet not found."""
        handler = ColonizeCommandHandler()
        mock_session = Mock()
        mock_session.active_empire = Mock(id=0)
        mock_session._get_fleet_by_id.return_value = None
        mock_cmd = Mock(fleet_id=999, planet_id=1)

        result = handler.execute(mock_session, mock_cmd)

        assert not result.is_valid
        assert "Fleet not found" in result.message

    def test_valid_colonize_creates_order(self):
        """Valid colonize adds order to fleet."""
        handler = ColonizeCommandHandler()

        mock_fleet = Mock()

        mock_fleet.owner_id = 0
        mock_fleet.id = 1
        mock_fleet.location = HexCoord(0, 0)  # Fleet already at planet location
        mock_fleet.orders = []
        mock_fleet.add_order = Mock()

        mock_planet = Mock()
        mock_planet.id = 10
        mock_planet.populations = []

        mock_session = Mock()

        mock_session.active_empire = Mock(id=0)
        mock_session._get_fleet_by_id.return_value = mock_fleet
        mock_session._get_planet_by_id.return_value = mock_planet
        mock_session.galaxy.get_planet_global_hex.return_value = HexCoord(0, 0)
        mock_session.turn_engine.validate_colonize_order.return_value = ValidationResult()

        mock_cmd = Mock(fleet_id=1, planet_id=10)

        result = handler.execute(mock_session, mock_cmd)

        assert result.is_valid
        # Colonize command only adds COLONIZE (no LOAD_POPULATION)
        assert mock_fleet.add_order.call_count == 1


class TestMoveCommandHandler:
    """Tests for MoveCommandHandler."""

    def test_fleet_not_found(self):
        """Returns failure when fleet not found."""
        handler = MoveCommandHandler()
        mock_session = Mock()
        mock_session.active_empire = Mock(id=0)
        mock_session._get_fleet_by_id.return_value = None
        mock_cmd = Mock(fleet_id=999, target_hex=(0, 0))

        result = handler.execute(mock_session, mock_cmd)

        assert not result.is_valid
        assert "Fleet not found" in result.message

    def test_unreachable_target(self):
        """Returns failure when path not found."""
        handler = MoveCommandHandler()

        mock_fleet = Mock()

        mock_fleet.owner_id = 0
        mock_fleet.location = (0, 0)

        mock_session = Mock()

        mock_session.active_empire = Mock(id=0)
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

        mock_fleet.owner_id = 0
        mock_fleet.location = (0, 0)
        mock_fleet.orders = []
        mock_fleet.add_order = Mock()

        mock_session = Mock()

        mock_session.active_empire = Mock(id=0)
        mock_session._get_fleet_by_id.return_value = mock_fleet
        mock_session.preview_fleet_path.return_value = [(1, 0), (2, 0)]

        mock_cmd = Mock(fleet_id=1, target_hex=(2, 0))

        result = handler.execute(mock_session, mock_cmd)

        assert result.is_valid
        mock_fleet.add_order.assert_called_once()


# NOTE: TestBuildShipCommandHandler removed in PROJ-208 Phase 2 (dead code).
# Use AddToConstructionQueueCommandHandler instead - see TestAddToConstructionQueueCommandHandler.


class TestInterceptCommandHandler:
    """Tests for InterceptCommandHandler."""

    def test_fleet_not_found(self):
        """Returns failure when source fleet not found."""
        handler = InterceptCommandHandler()
        mock_session = Mock()
        mock_session.active_empire = Mock(id=0)
        mock_session._get_fleet_by_id.return_value = None
        mock_cmd = Mock(fleet_id=999, target_fleet_id=2)

        result = handler.execute(mock_session, mock_cmd)

        assert not result.is_valid
        assert "Fleet not found" in result.message

    def test_target_fleet_not_found(self):
        """Returns failure when target fleet not found."""
        handler = InterceptCommandHandler()

        mock_fleet = Mock()

        mock_fleet.owner_id = 0
        mock_fleet.id = 1

        mock_session = Mock()

        mock_session.active_empire = Mock(id=0)
        mock_session._get_fleet_by_id.side_effect = lambda fid: mock_fleet if fid == 1 else None

        mock_cmd = Mock(fleet_id=1, target_fleet_id=999)

        result = handler.execute(mock_session, mock_cmd)

        assert not result.is_valid
        assert "Target fleet not found" in result.message

    def test_valid_intercept_creates_order(self):
        """Valid intercept adds MOVE_TO_FLEET order."""
        handler = InterceptCommandHandler()

        mock_fleet = Mock()

        mock_fleet.owner_id = 0
        mock_fleet.id = 1
        mock_fleet.add_order = Mock()

        mock_target = Mock()
        mock_target.id = 2

        mock_session = Mock()

        mock_session.active_empire = Mock(id=0)
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

        mock_fleet.owner_id = 0
        mock_fleet.id = 1
        mock_fleet.owner_id = 0
        mock_fleet.add_order = Mock()

        mock_target = Mock()
        mock_target.id = 2
        mock_target.owner_id = 0

        mock_session = Mock()

        mock_session.active_empire = Mock(id=0)
        mock_session._get_fleet_by_id.side_effect = lambda fid: mock_fleet if fid == 1 else mock_target

        mock_cmd = Mock(fleet_id=1, target_fleet_id=2)

        result = handler.execute(mock_session, mock_cmd)

        assert result.is_valid
        assert mock_fleet.add_order.call_count == 2


class TestJoinCommandHandlerPursuerTracking:
    """Tests for JoinCommandHandler pursuer registration and validation (PROJ-222)."""

    def _make_session_with_real_fleets(self, fleet, target):
        """Helper: create mock session that returns real Fleet objects."""
        mock_session = Mock()
        mock_session.active_empire = Mock(id=0)
        lookup = {fleet.id: fleet, target.id: target}
        mock_session._get_fleet_by_id.side_effect = lambda fid: lookup.get(fid)
        return mock_session

    def test_join_registers_pursuer(self):
        fleet = Fleet("f1", 0, HexCoord(0, 0))
        target = Fleet("f2", 0, HexCoord(5, 5))
        session = self._make_session_with_real_fleets(fleet, target)
        cmd = Mock(fleet_id="f1", target_fleet_id="f2")

        result = JoinCommandHandler().execute(session, cmd)

        assert result.is_valid
        assert target.pursuer_tracker.pursuer_count == 1
        assert fleet in target.pursuer_tracker.pursuers

    def test_join_self_targeting_rejected(self):
        fleet = Fleet("f1", 0, HexCoord(0, 0))
        session = self._make_session_with_real_fleets(fleet, fleet)
        cmd = Mock(fleet_id="f1", target_fleet_id="f1")

        result = JoinCommandHandler().execute(session, cmd)

        assert not result.is_valid
        assert "itself" in result.message.lower()

    def test_join_cross_empire_rejected(self):
        fleet = Fleet("f1", 0, HexCoord(0, 0))
        target = Fleet("f2", 1, HexCoord(5, 5))  # Different owner
        session = self._make_session_with_real_fleets(fleet, target)
        cmd = Mock(fleet_id="f1", target_fleet_id="f2")

        result = JoinCommandHandler().execute(session, cmd)

        assert not result.is_valid
        assert "empire" in result.message.lower()


class TestInterceptCommandHandlerPursuerTracking:
    """Tests for InterceptCommandHandler pursuer registration and validation (PROJ-222)."""

    def _make_session_with_real_fleets(self, fleet, target):
        mock_session = Mock()
        mock_session.active_empire = Mock(id=0)
        lookup = {fleet.id: fleet, target.id: target}
        mock_session._get_fleet_by_id.side_effect = lambda fid: lookup.get(fid)
        return mock_session

    def test_intercept_registers_pursuer(self):
        fleet = Fleet("f1", 0, HexCoord(0, 0))
        target = Fleet("f2", 0, HexCoord(5, 5))
        session = self._make_session_with_real_fleets(fleet, target)
        cmd = Mock(fleet_id="f1", target_fleet_id="f2")

        result = InterceptCommandHandler().execute(session, cmd)

        assert result.is_valid
        assert target.pursuer_tracker.pursuer_count == 1
        assert fleet in target.pursuer_tracker.pursuers

    def test_intercept_self_targeting_rejected(self):
        fleet = Fleet("f1", 0, HexCoord(0, 0))
        session = self._make_session_with_real_fleets(fleet, fleet)
        cmd = Mock(fleet_id="f1", target_fleet_id="f1")

        result = InterceptCommandHandler().execute(session, cmd)

        assert not result.is_valid
        assert "itself" in result.message.lower()


class TestColonizeMissionCommandHandler:
    """Tests for ColonizeMissionCommandHandler."""

    def test_fleet_not_found(self):
        """Returns failure when fleet not found."""
        handler = ColonizeMissionCommandHandler()
        mock_session = Mock()
        mock_session.active_empire = Mock(id=0)
        mock_session._get_fleet_by_id.return_value = None
        mock_cmd = Mock(fleet_id=999, planet_id=None, target_hex=(0, 0))

        result = handler.execute(mock_session, mock_cmd)

        assert not result.is_valid
        assert "Fleet not found" in result.message

    def test_no_path_found(self):
        """Returns failure when no path to target."""
        handler = ColonizeMissionCommandHandler()

        mock_fleet = Mock()

        mock_fleet.owner_id = 0
        mock_fleet.location = (0, 0)
        mock_fleet.orders = []

        mock_session = Mock()

        mock_session.active_empire = Mock(id=0)
        mock_session._get_fleet_by_id.return_value = mock_fleet
        mock_session._get_planet_by_id.return_value = None

        mock_cmd = Mock(fleet_id=1, planet_id=None, target_hex=(100, 100))

        # PROJ-207: Patch at command_handlers where function is imported
        with patch('game.strategy.engine.handlers.base.find_hybrid_path', return_value=None):
            result = handler.execute(mock_session, mock_cmd)

        assert not result.is_valid
        assert "No path found" in result.message


class TestClearOrdersCommandHandler:
    """Tests for ClearOrdersCommandHandler."""

    def test_fleet_not_found(self):
        """Returns failure when fleet not found."""
        handler = ClearOrdersCommandHandler()
        mock_session = Mock()
        mock_session.active_empire = Mock(id=0)
        mock_session._get_fleet_by_id.return_value = None
        mock_cmd = Mock(fleet_id=999)

        result = handler.execute(mock_session, mock_cmd)

        assert not result.is_valid
        assert "Fleet not found" in result.message

    def test_clears_orders_and_path(self):
        """Valid clear calls fleet.clear_orders() (PROJ-222: uses Fleet API)."""
        handler = ClearOrdersCommandHandler()

        mock_fleet = Mock()

        mock_fleet.owner_id = 0
        mock_fleet.id = 1

        mock_session = Mock()

        mock_session.active_empire = Mock(id=0)
        mock_session._get_fleet_by_id.return_value = mock_fleet

        mock_cmd = Mock(fleet_id=1)

        result = handler.execute(mock_session, mock_cmd)

        assert result.is_valid
        mock_fleet.clear_orders.assert_called_once()


class TestTransferCommandHandler:
    """Tests for TransferCommandHandler."""

    def test_fleet_not_found(self):
        """Returns failure when fleet not found."""
        handler = TransferCommandHandler()
        mock_session = Mock()
        mock_session.active_empire = Mock(id=0)
        mock_session._get_fleet_by_id.return_value = None
        mock_cmd = Mock(fleet_id=999)

        result = handler.execute(mock_session, mock_cmd)

        assert not result.is_valid
        assert "Fleet not found" in result.message

    def test_fleet_owner_not_found(self):
        """Returns failure when fleet owner empire not found.

        BUG-125: aligning active_empire with the fleet's owner_id passes
        the authorization gate; the owner-empire-lookup failure is then
        the next branch reached.
        """
        handler = TransferCommandHandler()

        mock_fleet = Mock()
        mock_fleet.owner_id = 99
        mock_fleet.id = 1
        mock_fleet.ships = []
        mock_fleet.location = (0, 0)

        mock_session = Mock()
        # active_empire matches fleet owner so auth passes; empires list
        # is empty so the owner-not-found branch fires.
        mock_session.active_empire = Mock(id=99)
        mock_session._get_fleet_by_id.return_value = mock_fleet
        mock_session.empires = []

        mock_cmd = Mock(fleet_id=1)

        result = handler.execute(mock_session, mock_cmd)

        assert not result.is_valid
        assert "Fleet owner not found" in result.message

    def test_planet_not_found(self):
        """Returns failure when planet not found."""
        handler = TransferCommandHandler()

        mock_fleet = Mock()

        mock_fleet.owner_id = 0
        mock_fleet.id = 1
        mock_fleet.ships = []
        mock_fleet.location = (0, 0)
        mock_fleet.owner_id = 0  # Valid owner_id

        mock_empire = Mock()
        mock_empire.fleets = [mock_fleet]

        mock_session = Mock()

        mock_session.active_empire = Mock(id=0)
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

        mock_fleet.owner_id = 0
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

        mock_session.active_empire = Mock(id=0)
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
        mock_fleet.owner_id = 0
        mock_fleet.id = 1

        mock_session = Mock()

        mock_session.active_empire = Mock(id=0)
        mock_session._get_fleet_by_id.return_value = mock_fleet

        fleet = handler._resolve_fleet_required(mock_session, 1)

        assert fleet is mock_fleet

    def test_resolve_fleet_required_raises_when_not_found(self):
        """_resolve_fleet_required raises ValueError when fleet not found."""
        from game.strategy.engine.command_handlers import BaseCommandHandler

        handler = BaseCommandHandler()
        mock_session = Mock()
        mock_session.active_empire = Mock(id=0)
        mock_session._get_fleet_by_id.return_value = None

        with pytest.raises(ValueError) as exc_info:
            handler._resolve_fleet_required(mock_session, 999)

        assert "Fleet not found" in str(exc_info.value)

    def test_resolve_fleet_required_validates_ownership(self):
        """_resolve_fleet_required raises when owner_id doesn't match."""
        from game.strategy.engine.command_handlers import BaseCommandHandler

        handler = BaseCommandHandler()
        mock_fleet = Mock()
        mock_fleet.owner_id = 0
        mock_fleet.id = 1
        mock_fleet.owner_id = 0

        mock_session = Mock()

        mock_session.active_empire = Mock(id=0)
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

        mock_session.active_empire = Mock(id=0)
        mock_session._get_planet_by_id.return_value = mock_planet

        planet = handler._resolve_planet_optional(mock_session, 10)

        assert planet is mock_planet

    def test_resolve_planet_optional_returns_none_when_not_found_and_not_required(self):
        """_resolve_planet_optional returns None when not found and required=False."""
        from game.strategy.engine.command_handlers import BaseCommandHandler

        handler = BaseCommandHandler()
        mock_session = Mock()
        mock_session.active_empire = Mock(id=0)
        mock_session._get_planet_by_id.return_value = None

        planet = handler._resolve_planet_optional(mock_session, 999, required=False)

        assert planet is None

    def test_resolve_planet_optional_raises_when_not_found_and_required(self):
        """_resolve_planet_optional raises ValueError when not found and required=True."""
        from game.strategy.engine.command_handlers import BaseCommandHandler

        handler = BaseCommandHandler()
        mock_session = Mock()
        mock_session.active_empire = Mock(id=0)
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

        mock_fleet.owner_id = 0
        mock_fleet.location = HexCoord(5, 5)
        mock_fleet.orders = []
        mock_fleet.add_order = Mock()

        mock_session = Mock()

        mock_session.active_empire = Mock(id=0)

        result = add_move_order_if_needed(mock_session, mock_fleet, HexCoord(5, 5))

        assert result.is_valid
        mock_fleet.add_order.assert_not_called()

    def test_add_move_order_if_needed_adds_move_when_not_at_target(self):
        """add_move_order_if_needed adds MOVE order when fleet not at target."""
        from game.strategy.engine.command_handlers import add_move_order_if_needed
        from game.strategy.data.order_types import OrderType

        mock_fleet = Mock()

        mock_fleet.owner_id = 0
        mock_fleet.location = HexCoord(0, 0)
        mock_fleet.orders = []
        mock_fleet.add_order = Mock()

        mock_session = Mock()

        mock_session.active_empire = Mock(id=0)
        mock_session.galaxy = Mock()

        target = HexCoord(5, 5)

        with patch('game.strategy.engine.handlers.base.find_hybrid_path') as mock_path:
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

        mock_fleet.owner_id = 0
        mock_fleet.location = HexCoord(0, 0)
        mock_fleet.orders = []

        mock_session = Mock()

        mock_session.active_empire = Mock(id=0)
        mock_session.galaxy = Mock()

        with patch('game.strategy.engine.handlers.base.find_hybrid_path') as mock_path:
            mock_path.return_value = None
            result = add_move_order_if_needed(mock_session, mock_fleet, HexCoord(100, 100))

        assert not result.is_valid
        assert "No path found" in result.message


# =============================================================================
# PROJ-208 Fleet Management Command Handler Tests
# =============================================================================

class TestSplitFleetCommandHandler:
    """Tests for SplitFleetCommandHandler (PROJ-208 Phase 1)."""

    def test_fleet_not_found(self):
        """Returns failure when source fleet not found."""
        handler = SplitFleetCommandHandler()
        mock_session = Mock()
        mock_session.active_empire = Mock(id=0)
        mock_session._get_fleet_by_id.return_value = None
        mock_cmd = Mock(fleet_id=999, ship_instance_ids=['ship-1'])

        result = handler.execute(mock_session, mock_cmd)

        assert not result.is_valid
        assert "Fleet not found" in result.message

    def test_no_ships_specified(self):
        """Returns failure when no ships specified for split."""
        handler = SplitFleetCommandHandler()

        mock_fleet = Mock()

        mock_fleet.owner_id = 0
        mock_fleet.id = 1
        mock_fleet.ships = []

        mock_session = Mock()

        mock_session.active_empire = Mock(id=0)
        mock_session._get_fleet_by_id.return_value = mock_fleet

        mock_cmd = Mock(fleet_id=1, ship_instance_ids=[])

        result = handler.execute(mock_session, mock_cmd)

        assert not result.is_valid
        assert "No ships specified" in result.message

    def test_ship_not_in_fleet(self):
        """Returns failure when specified ship not found in fleet."""
        handler = SplitFleetCommandHandler()

        mock_ship = Mock()
        mock_ship.instance_id = 'ship-existing'

        mock_fleet = Mock()

        mock_fleet.owner_id = 0
        mock_fleet.id = 1
        mock_fleet.ships = [mock_ship]

        mock_session = Mock()

        mock_session.active_empire = Mock(id=0)
        mock_session._get_fleet_by_id.return_value = mock_fleet

        mock_cmd = Mock(fleet_id=1, ship_instance_ids=['ship-nonexistent'])

        result = handler.execute(mock_session, mock_cmd)

        assert not result.is_valid
        assert "not found in fleet" in result.message

    def test_cannot_remove_all_ships(self):
        """Returns failure when trying to remove all ships from fleet."""
        handler = SplitFleetCommandHandler()

        mock_ship1 = Mock()
        mock_ship1.instance_id = 'ship-1'
        mock_ship2 = Mock()
        mock_ship2.instance_id = 'ship-2'

        mock_fleet = Mock()

        mock_fleet.owner_id = 0
        mock_fleet.id = 1
        mock_fleet.ships = [mock_ship1, mock_ship2]

        mock_session = Mock()

        mock_session.active_empire = Mock(id=0)
        mock_session._get_fleet_by_id.return_value = mock_fleet

        mock_cmd = Mock(fleet_id=1, ship_instance_ids=['ship-1', 'ship-2'])

        result = handler.execute(mock_session, mock_cmd)

        assert not result.is_valid
        assert "At least one ship must remain" in result.message

    def test_fleet_owner_not_found(self):
        """Returns failure when fleet owner empire not found.

        BUG-125: align active_empire with fleet owner so auth passes;
        empires list is empty so the owner-not-found branch fires.
        """
        handler = SplitFleetCommandHandler()

        mock_ship1 = Mock()
        mock_ship1.instance_id = 'ship-1'
        mock_ship2 = Mock()
        mock_ship2.instance_id = 'ship-2'

        mock_fleet = Mock()
        mock_fleet.owner_id = 99
        mock_fleet.id = 1
        mock_fleet.ships = [mock_ship1, mock_ship2]

        mock_session = Mock()
        mock_session.active_empire = Mock(id=99)
        mock_session._get_fleet_by_id.return_value = mock_fleet
        mock_session.empires = []  # No empires

        mock_cmd = Mock(fleet_id=1, ship_instance_ids=['ship-1'])

        result = handler.execute(mock_session, mock_cmd)

        assert not result.is_valid
        assert "Fleet owner not found" in result.message

    def test_valid_split_creates_new_fleet(self):
        """Valid split removes ships and creates new fleet."""
        handler = SplitFleetCommandHandler()

        mock_ship1 = Mock()
        mock_ship1.instance_id = 'ship-1'
        mock_ship2 = Mock()
        mock_ship2.instance_id = 'ship-2'

        mock_fleet = Mock()

        mock_fleet.owner_id = 0
        mock_fleet.id = 1
        mock_fleet.ships = [mock_ship1, mock_ship2]
        mock_fleet.owner_id = 0
        mock_fleet.location = HexCoord(5, 5)
        mock_fleet._component_registry = None
        mock_fleet.remove_ship = Mock()

        mock_empire = Mock()
        mock_empire.get_next_fleet_id.return_value = 100
        mock_empire.add_fleet = Mock()

        mock_session = Mock()

        mock_session.active_empire = Mock(id=0)
        mock_session._get_fleet_by_id.return_value = mock_fleet
        mock_session.empires = [mock_empire]

        mock_cmd = Mock(fleet_id=1, ship_instance_ids=['ship-1'])

        # Patch Fleet class in the data module where it's imported from
        with patch('game.strategy.data.fleet.Fleet') as MockFleet:
            mock_new_fleet = Mock()
            mock_new_fleet.add_ship = Mock()
            MockFleet.return_value = mock_new_fleet

            result = handler.execute(mock_session, mock_cmd)

        assert result.is_valid
        mock_fleet.remove_ship.assert_called_once_with(mock_ship1)
        mock_new_fleet.add_ship.assert_called_once_with(mock_ship1)
        mock_empire.add_fleet.assert_called_once_with(mock_new_fleet)


class TestDeleteOrderCommandHandler:
    """Tests for DeleteOrderCommandHandler (PROJ-208 Phase 1)."""

    def test_fleet_not_found(self):
        """Returns failure when fleet not found."""
        handler = DeleteOrderCommandHandler()
        mock_session = Mock()
        mock_session.active_empire = Mock(id=0)
        mock_session._get_fleet_by_id.return_value = None
        mock_cmd = Mock(fleet_id=999, order_index=0)

        result = handler.execute(mock_session, mock_cmd)

        assert not result.is_valid
        assert "Fleet not found" in result.message

    def test_invalid_order_index_negative(self):
        """Returns failure for negative order index."""
        handler = DeleteOrderCommandHandler()

        mock_fleet = Mock()

        mock_fleet.owner_id = 0
        mock_fleet.id = 1
        mock_fleet.orders = [Mock(), Mock()]

        mock_session = Mock()

        mock_session.active_empire = Mock(id=0)
        mock_session._get_fleet_by_id.return_value = mock_fleet

        mock_cmd = Mock(fleet_id=1, order_index=-1)

        result = handler.execute(mock_session, mock_cmd)

        assert not result.is_valid
        assert "Invalid order index" in result.message

    def test_invalid_order_index_too_high(self):
        """Returns failure when order index exceeds queue length."""
        handler = DeleteOrderCommandHandler()

        mock_fleet = Mock()

        mock_fleet.owner_id = 0
        mock_fleet.id = 1
        mock_fleet.orders = [Mock(), Mock()]

        mock_session = Mock()

        mock_session.active_empire = Mock(id=0)
        mock_session._get_fleet_by_id.return_value = mock_fleet

        mock_cmd = Mock(fleet_id=1, order_index=5)

        result = handler.execute(mock_session, mock_cmd)

        assert not result.is_valid
        assert "Invalid order index" in result.message

    def test_delete_active_order_clears_path(self):
        """Deleting order calls fleet.remove_order_at() (PROJ-222: uses Fleet API)."""
        handler = DeleteOrderCommandHandler()

        mock_fleet = Mock()

        mock_fleet.owner_id = 0
        mock_fleet.id = 1
        mock_fleet.orders = [Mock(), Mock()]

        mock_session = Mock()

        mock_session.active_empire = Mock(id=0)
        mock_session._get_fleet_by_id.return_value = mock_fleet

        mock_cmd = Mock(fleet_id=1, order_index=0)

        result = handler.execute(mock_session, mock_cmd)

        assert result.is_valid
        mock_fleet.remove_order_at.assert_called_once_with(0)

    def test_delete_non_active_order_preserves_path(self):
        """Deleting non-active order calls fleet.remove_order_at() with correct index."""
        handler = DeleteOrderCommandHandler()

        mock_fleet = Mock()

        mock_fleet.owner_id = 0
        mock_fleet.id = 1
        mock_fleet.orders = [Mock(), Mock()]

        mock_session = Mock()

        mock_session.active_empire = Mock(id=0)
        mock_session._get_fleet_by_id.return_value = mock_fleet

        mock_cmd = Mock(fleet_id=1, order_index=1)

        result = handler.execute(mock_session, mock_cmd)

        assert result.is_valid
        mock_fleet.remove_order_at.assert_called_once_with(1)


class TestReorderOrderCommandHandler:
    """Tests for ReorderOrderCommandHandler (PROJ-208 Phase 1)."""

    def test_fleet_not_found(self):
        """Returns failure when fleet not found."""
        handler = ReorderOrderCommandHandler()
        mock_session = Mock()
        mock_session.active_empire = Mock(id=0)
        mock_session._get_fleet_by_id.return_value = None
        mock_cmd = Mock(fleet_id=999, order_index=0, direction=1)

        result = handler.execute(mock_session, mock_cmd)

        assert not result.is_valid
        assert "Fleet not found" in result.message

    def test_invalid_order_index(self):
        """Returns failure for invalid order index."""
        handler = ReorderOrderCommandHandler()

        mock_fleet = Mock()

        mock_fleet.owner_id = 0
        mock_fleet.id = 1
        mock_fleet.orders = [Mock(), Mock()]

        mock_session = Mock()

        mock_session.active_empire = Mock(id=0)
        mock_session._get_fleet_by_id.return_value = mock_fleet

        mock_cmd = Mock(fleet_id=1, order_index=5, direction=1)

        result = handler.execute(mock_session, mock_cmd)

        assert not result.is_valid
        assert "Invalid order index" in result.message

    def test_invalid_direction(self):
        """Returns failure for invalid direction."""
        handler = ReorderOrderCommandHandler()

        mock_fleet = Mock()

        mock_fleet.owner_id = 0
        mock_fleet.id = 1
        mock_fleet.orders = [Mock(), Mock()]

        mock_session = Mock()

        mock_session.active_empire = Mock(id=0)
        mock_session._get_fleet_by_id.return_value = mock_fleet

        mock_cmd = Mock(fleet_id=1, order_index=0, direction=2)  # Invalid

        result = handler.execute(mock_session, mock_cmd)

        assert not result.is_valid
        assert "Invalid direction" in result.message

    def test_cannot_move_first_order_up(self):
        """Returns failure when trying to move first order up."""
        handler = ReorderOrderCommandHandler()

        mock_fleet = Mock()

        mock_fleet.owner_id = 0
        mock_fleet.id = 1
        mock_fleet.orders = [Mock(), Mock()]

        mock_session = Mock()

        mock_session.active_empire = Mock(id=0)
        mock_session._get_fleet_by_id.return_value = mock_fleet

        mock_cmd = Mock(fleet_id=1, order_index=0, direction=-1)

        result = handler.execute(mock_session, mock_cmd)

        assert not result.is_valid
        assert "Cannot move order" in result.message

    def test_cannot_move_last_order_down(self):
        """Returns failure when trying to move last order down."""
        handler = ReorderOrderCommandHandler()

        mock_fleet = Mock()

        mock_fleet.owner_id = 0
        mock_fleet.id = 1
        mock_fleet.orders = [Mock(), Mock()]

        mock_session = Mock()

        mock_session.active_empire = Mock(id=0)
        mock_session._get_fleet_by_id.return_value = mock_fleet

        mock_cmd = Mock(fleet_id=1, order_index=1, direction=1)

        result = handler.execute(mock_session, mock_cmd)

        assert not result.is_valid
        assert "Cannot move order" in result.message

    def test_move_order_down_swaps_positions(self):
        """Moving order down swaps with next order."""
        handler = ReorderOrderCommandHandler()

        mock_order1 = Mock(name='order1')
        mock_order2 = Mock(name='order2')
        mock_order3 = Mock(name='order3')

        mock_fleet = Mock()

        mock_fleet.owner_id = 0
        mock_fleet.id = 1
        mock_fleet.orders = [mock_order1, mock_order2, mock_order3]
        mock_fleet.path = []

        mock_session = Mock()

        mock_session.active_empire = Mock(id=0)
        mock_session._get_fleet_by_id.return_value = mock_fleet

        mock_cmd = Mock(fleet_id=1, order_index=1, direction=1)

        result = handler.execute(mock_session, mock_cmd)

        assert result.is_valid
        assert mock_fleet.orders == [mock_order1, mock_order3, mock_order2]

    def test_move_order_up_swaps_positions(self):
        """Moving order up swaps with previous order."""
        handler = ReorderOrderCommandHandler()

        mock_order1 = Mock(name='order1')
        mock_order2 = Mock(name='order2')
        mock_order3 = Mock(name='order3')

        mock_fleet = Mock()

        mock_fleet.owner_id = 0
        mock_fleet.id = 1
        mock_fleet.orders = [mock_order1, mock_order2, mock_order3]
        mock_fleet.path = []

        mock_session = Mock()

        mock_session.active_empire = Mock(id=0)
        mock_session._get_fleet_by_id.return_value = mock_fleet

        mock_cmd = Mock(fleet_id=1, order_index=2, direction=-1)

        result = handler.execute(mock_session, mock_cmd)

        assert result.is_valid
        assert mock_fleet.orders == [mock_order1, mock_order3, mock_order2]

    def test_reorder_affecting_active_order_clears_path(self):
        """Reordering that affects active order (index 0) clears path."""
        handler = ReorderOrderCommandHandler()

        mock_order1 = Mock(name='order1')
        mock_order2 = Mock(name='order2')

        mock_fleet = Mock()

        mock_fleet.owner_id = 0
        mock_fleet.id = 1
        mock_fleet.orders = [mock_order1, mock_order2]
        mock_fleet.path = [HexCoord(1, 0), HexCoord(2, 0)]

        mock_session = Mock()

        mock_session.active_empire = Mock(id=0)
        mock_session._get_fleet_by_id.return_value = mock_fleet

        # Move order 0 down to 1
        mock_cmd = Mock(fleet_id=1, order_index=0, direction=1)

        result = handler.execute(mock_session, mock_cmd)

        assert result.is_valid
        assert mock_fleet.path == []
        assert mock_fleet.orders == [mock_order2, mock_order1]

    def test_reorder_not_affecting_active_order_preserves_path(self):
        """Reordering not affecting active order preserves path."""
        handler = ReorderOrderCommandHandler()

        mock_order1 = Mock(name='order1')
        mock_order2 = Mock(name='order2')
        mock_order3 = Mock(name='order3')

        mock_fleet = Mock()

        mock_fleet.owner_id = 0
        mock_fleet.id = 1
        mock_fleet.orders = [mock_order1, mock_order2, mock_order3]
        original_path = [HexCoord(1, 0), HexCoord(2, 0)]
        mock_fleet.path = original_path.copy()

        mock_session = Mock()

        mock_session.active_empire = Mock(id=0)
        mock_session._get_fleet_by_id.return_value = mock_fleet

        # Move order 1 down to 2 (doesn't affect order 0)
        mock_cmd = Mock(fleet_id=1, order_index=1, direction=1)

        result = handler.execute(mock_session, mock_cmd)

        assert result.is_valid
        assert mock_fleet.path == original_path
        assert mock_fleet.orders == [mock_order1, mock_order3, mock_order2]


# =============================================================================
# PROJ-208 Phase 2: Construction Queue Command Handler Tests
# =============================================================================

class TestAddToConstructionQueueCommandHandler:
    """Tests for AddToConstructionQueueCommandHandler (PROJ-208 Phase 2)."""

    def test_planet_not_found(self):
        """Returns failure when planet not found."""
        handler = AddToConstructionQueueCommandHandler()
        mock_session = Mock()
        mock_session.active_empire = Mock(id=0)
        mock_session._get_planet_by_id.return_value = None
        mock_cmd = Mock(
            entity_id=999,
            entity_type="planet",
            design_id="scout",
            category="ship",
            index=None,
            target_planet_id=None,
            queue_id=None  # PROJ-208: Required for _resolve_queue
        )

        result = handler.execute(mock_session, mock_cmd)

        assert not result.is_valid
        assert "Planet not found" in result.message

    def test_fleet_not_found(self):
        """Returns failure when fleet not found."""
        handler = AddToConstructionQueueCommandHandler()
        mock_session = Mock()
        mock_session.active_empire = Mock(id=0)
        mock_session._get_fleet_by_id.return_value = None
        mock_cmd = Mock(
            entity_id=999,
            entity_type="fleet",
            design_id="scout",
            category="ship",
            index=None,
            target_planet_id=None,
            queue_id=None  # PROJ-208: Required for _resolve_queue
        )

        result = handler.execute(mock_session, mock_cmd)

        assert not result.is_valid
        assert "Fleet not found" in result.message

    def test_invalid_entity_type(self):
        """Returns failure for invalid entity type."""
        handler = AddToConstructionQueueCommandHandler()
        mock_session = Mock()
        mock_session.active_empire = Mock(id=0)
        mock_cmd = Mock(
            entity_id=1,
            entity_type="invalid",
            design_id="scout",
            category="ship",
            index=None,
            target_planet_id=None,
            queue_id=None  # PROJ-208: Required for _resolve_queue
        )

        result = handler.execute(mock_session, mock_cmd)

        assert not result.is_valid
        assert "not found" in result.message.lower()

    def test_invalid_index_negative(self):
        """Returns failure for negative index."""
        handler = AddToConstructionQueueCommandHandler()

        mock_planet = Mock()
        mock_planet.construction_queue = []
        mock_planet.facilities = []  # PROJ-208: Required for _resolve_queue

        mock_session = Mock()

        mock_session.active_empire = Mock(id=0)
        mock_session._get_planet_by_id.return_value = mock_planet

        mock_cmd = Mock(
            entity_id=1,
            entity_type="planet",
            design_id="scout",
            category="ship",
            index=-1,
            target_planet_id=None,
            queue_id=None  # PROJ-208: Required for _resolve_queue
        )

        result = handler.execute(mock_session, mock_cmd)

        assert not result.is_valid
        assert "Invalid queue index" in result.message

    def test_invalid_index_too_high(self):
        """Returns failure for index beyond queue length."""
        handler = AddToConstructionQueueCommandHandler()

        mock_planet = Mock()
        mock_planet.construction_queue = [{"design_id": "existing"}]
        mock_planet.facilities = []  # PROJ-208: Required for _resolve_queue

        mock_session = Mock()

        mock_session.active_empire = Mock(id=0)
        mock_session._get_planet_by_id.return_value = mock_planet

        mock_cmd = Mock(
            entity_id=1,
            entity_type="planet",
            design_id="scout",
            category="ship",
            index=5,
            target_planet_id=None,
            queue_id=None  # PROJ-208: Required for _resolve_queue
        )

        result = handler.execute(mock_session, mock_cmd)

        assert not result.is_valid
        assert "Invalid queue index" in result.message

    def test_append_to_planet_queue(self):
        """Successfully appends item to planet construction queue."""
        handler = AddToConstructionQueueCommandHandler()

        mock_planet = Mock()
        mock_planet.construction_queue = []
        mock_planet.facilities = []  # PROJ-208: Required for _resolve_queue

        mock_session = Mock()

        mock_session.active_empire = Mock(id=0)
        mock_session._get_planet_by_id.return_value = mock_planet

        mock_cmd = Mock(
            entity_id=1,
            entity_type="planet",
            design_id="scout",
            category="ship",
            index=None,
            target_planet_id=None,
            queue_id=None  # PROJ-208: Required for _resolve_queue
        )

        result = handler.execute(mock_session, mock_cmd)

        assert result.is_valid
        assert len(mock_planet.construction_queue) == 1
        assert mock_planet.construction_queue[0]["design_id"] == "scout"
        assert mock_planet.construction_queue[0]["type"] == "ship"

    def test_insert_at_index(self):
        """Successfully inserts item at specified index."""
        handler = AddToConstructionQueueCommandHandler()

        existing_item = {"design_id": "cruiser", "type": "ship"}
        mock_planet = Mock()
        mock_planet.construction_queue = [existing_item]
        mock_planet.facilities = []  # PROJ-208: Required for _resolve_queue

        mock_session = Mock()

        mock_session.active_empire = Mock(id=0)
        mock_session._get_planet_by_id.return_value = mock_planet

        mock_cmd = Mock(
            entity_id=1,
            entity_type="planet",
            design_id="scout",
            category="ship",
            index=0,
            target_planet_id=None,
            queue_id=None  # PROJ-208: Required for _resolve_queue
        )

        result = handler.execute(mock_session, mock_cmd)

        assert result.is_valid
        assert len(mock_planet.construction_queue) == 2
        assert mock_planet.construction_queue[0]["design_id"] == "scout"
        assert mock_planet.construction_queue[1]["design_id"] == "cruiser"

    def test_adds_target_planet_id_for_complex(self):
        """Adds target_planet_id to queue item when specified."""
        handler = AddToConstructionQueueCommandHandler()

        mock_fleet = Mock()

        mock_fleet.owner_id = 0
        mock_fleet.construction_queue = []
        mock_fleet.facilities = []  # PROJ-208: Required for _resolve_queue

        mock_session = Mock()

        mock_session.active_empire = Mock(id=0)
        mock_session._get_fleet_by_id.return_value = mock_fleet

        mock_cmd = Mock(
            entity_id=1,
            entity_type="fleet",
            design_id="research_lab",
            category="complex",
            index=None,
            target_planet_id=42,
            queue_id=None  # PROJ-208: Required for _resolve_queue
        )

        result = handler.execute(mock_session, mock_cmd)

        assert result.is_valid
        assert mock_fleet.construction_queue[0]["target_planet_id"] == 42

    def test_queue_item_has_required_fields(self):
        """Queue item has all required fields."""
        handler = AddToConstructionQueueCommandHandler()

        mock_planet = Mock()
        mock_planet.construction_queue = []
        mock_planet.facilities = []  # PROJ-208: Required for _resolve_queue

        mock_session = Mock()

        mock_session.active_empire = Mock(id=0)
        mock_session._get_planet_by_id.return_value = mock_planet

        mock_cmd = Mock(
            entity_id=1,
            entity_type="planet",
            design_id="scout",
            category="ship",
            index=None,
            target_planet_id=None,
            queue_id=None  # PROJ-208: Required for _resolve_queue
        )

        result = handler.execute(mock_session, mock_cmd)

        assert result.is_valid
        item = mock_planet.construction_queue[0]
        assert "design_id" in item
        assert "type" in item
        assert "turns_remaining" in item
        assert "total_cost" in item
        assert "resources_consumed" in item


    def test_turns_remaining_precalculated_from_production_rate(self):
        """BUG-96: turns_remaining should be pre-calculated via build_queue_source
        utilities, not hardcoded to 1.0."""
        handler = AddToConstructionQueueCommandHandler()

        mock_planet = Mock()
        mock_planet.construction_queue = []
        mock_planet.facilities = []

        mock_session = Mock()

        mock_session.active_empire = Mock(id=0)
        mock_session._get_planet_by_id.return_value = mock_planet

        mock_cmd = Mock(
            entity_id=1,
            entity_type="planet",
            design_id="scout",
            category="ship",
            index=None,
            target_planet_id=None,
            queue_id=None
        )

        # Mock _load_design_cost to return known costs
        total_cost = {"metals": 3000.0, "electronics": 500.0}
        handler._load_design_cost = Mock(return_value=total_cost)

        # Patch the shared utilities that the handler delegates to
        with patch(
            'game.strategy.data.build_queue_source.get_production_rate_for_queue',
            return_value={"metals": 1000.0, "electronics": 1000.0}
        ) as mock_rate, patch(
            'game.strategy.data.build_queue_source.estimate_build_turns',
            return_value=3.0
        ) as mock_estimate:
            result = handler.execute(mock_session, mock_cmd)

        assert result.is_valid
        item = mock_planet.construction_queue[0]
        assert item["turns_remaining"] == 3.0
        mock_rate.assert_called_once_with(mock_planet, None)
        mock_estimate.assert_called_once_with(total_cost, {"metals": 1000.0, "electronics": 1000.0})


class TestRemoveFromConstructionQueueCommandHandler:
    """Tests for RemoveFromConstructionQueueCommandHandler (PROJ-208 Phase 2)."""

    def test_planet_not_found(self):
        """Returns failure when planet not found."""
        handler = RemoveFromConstructionQueueCommandHandler()
        mock_session = Mock()
        mock_session.active_empire = Mock(id=0)
        mock_session._get_planet_by_id.return_value = None
        mock_cmd = Mock(entity_id=999, entity_type="planet", item_index=0, queue_id=None)

        result = handler.execute(mock_session, mock_cmd)

        assert not result.is_valid
        assert "Planet not found" in result.message

    def test_fleet_not_found(self):
        """Returns failure when fleet not found."""
        handler = RemoveFromConstructionQueueCommandHandler()
        mock_session = Mock()
        mock_session.active_empire = Mock(id=0)
        mock_session._get_fleet_by_id.return_value = None
        mock_cmd = Mock(entity_id=999, entity_type="fleet", item_index=0, queue_id=None)

        result = handler.execute(mock_session, mock_cmd)

        assert not result.is_valid
        assert "Fleet not found" in result.message

    def test_invalid_index_negative(self):
        """Returns failure for negative index."""
        handler = RemoveFromConstructionQueueCommandHandler()

        mock_planet = Mock()
        mock_planet.construction_queue = [{"design_id": "scout"}]

        mock_session = Mock()

        mock_session.active_empire = Mock(id=0)
        mock_session._get_planet_by_id.return_value = mock_planet

        mock_cmd = Mock(entity_id=1, entity_type="planet", item_index=-1, queue_id=None)

        result = handler.execute(mock_session, mock_cmd)

        assert not result.is_valid
        assert "Invalid queue index" in result.message

    def test_invalid_index_too_high(self):
        """Returns failure for index beyond queue length."""
        handler = RemoveFromConstructionQueueCommandHandler()

        mock_planet = Mock()
        mock_planet.construction_queue = [{"design_id": "scout"}]

        mock_session = Mock()

        mock_session.active_empire = Mock(id=0)
        mock_session._get_planet_by_id.return_value = mock_planet

        mock_cmd = Mock(entity_id=1, entity_type="planet", item_index=5, queue_id=None)

        result = handler.execute(mock_session, mock_cmd)

        assert not result.is_valid
        assert "Invalid queue index" in result.message

    def test_removes_item_from_queue(self):
        """Successfully removes item from queue."""
        handler = RemoveFromConstructionQueueCommandHandler()

        item1 = {"design_id": "scout"}
        item2 = {"design_id": "cruiser"}
        mock_planet = Mock()
        mock_planet.construction_queue = [item1, item2]

        mock_session = Mock()

        mock_session.active_empire = Mock(id=0)
        mock_session._get_planet_by_id.return_value = mock_planet

        mock_cmd = Mock(entity_id=1, entity_type="planet", item_index=0, queue_id=None)

        result = handler.execute(mock_session, mock_cmd)

        assert result.is_valid
        assert len(mock_planet.construction_queue) == 1
        assert mock_planet.construction_queue[0] == item2

    def test_removes_from_fleet_queue(self):
        """Successfully removes item from fleet queue."""
        handler = RemoveFromConstructionQueueCommandHandler()

        item1 = {"design_id": "fighter"}
        mock_fleet = Mock()
        mock_fleet.owner_id = 0
        mock_fleet.construction_queue = [item1]

        mock_session = Mock()

        mock_session.active_empire = Mock(id=0)
        mock_session._get_fleet_by_id.return_value = mock_fleet

        mock_cmd = Mock(entity_id=1, entity_type="fleet", item_index=0, queue_id=None)

        result = handler.execute(mock_session, mock_cmd)

        assert result.is_valid
        assert len(mock_fleet.construction_queue) == 0

    def test_removes_from_facility_queue(self):
        """Successfully removes item from a facility queue (BUG-103)."""
        handler = RemoveFromConstructionQueueCommandHandler()

        # Planet base queue (should be untouched)
        base_item = {"design_id": "complex_a"}
        mock_planet = Mock()
        mock_planet.construction_queue = [base_item]
        mock_planet.id = 1

        # Facility queue (target)
        fac_item1 = {"design_id": "scout"}
        fac_item2 = {"design_id": "cruiser"}
        mock_facility = Mock()
        mock_facility.instance_id = "fac-uuid-001"
        mock_facility.construction_queue = [fac_item1, fac_item2]
        mock_planet.facilities = [mock_facility]

        mock_session = Mock()

        mock_session.active_empire = Mock(id=0)
        mock_session._get_planet_by_id.return_value = mock_planet

        mock_cmd = Mock(
            entity_id=1, entity_type="planet",
            item_index=0, queue_id="fac-uuid-001",
        )

        result = handler.execute(mock_session, mock_cmd)

        assert result.is_valid
        assert len(mock_facility.construction_queue) == 1
        assert mock_facility.construction_queue[0] == fac_item2
        # Base queue unchanged
        assert mock_planet.construction_queue == [base_item]

    def test_removes_from_base_queue_with_queue_id(self):
        """Removes from base queue when queue_id matches base pattern (BUG-103)."""
        handler = RemoveFromConstructionQueueCommandHandler()

        base_item = {"design_id": "complex_a"}
        mock_planet = Mock()
        mock_planet.construction_queue = [base_item]
        mock_planet.id = 42
        mock_planet.facilities = []

        mock_session = Mock()

        mock_session.active_empire = Mock(id=0)
        mock_session._get_planet_by_id.return_value = mock_planet

        mock_cmd = Mock(
            entity_id=42, entity_type="planet",
            item_index=0, queue_id="planet_42_base",
        )

        result = handler.execute(mock_session, mock_cmd)

        assert result.is_valid
        assert len(mock_planet.construction_queue) == 0

    def test_facility_queue_invalid_index(self):
        """Returns failure for invalid index on facility queue (BUG-103)."""
        handler = RemoveFromConstructionQueueCommandHandler()

        mock_planet = Mock()
        mock_planet.construction_queue = []
        mock_planet.id = 1

        mock_facility = Mock()
        mock_facility.instance_id = "fac-uuid-001"
        mock_facility.construction_queue = [{"design_id": "scout"}]
        mock_planet.facilities = [mock_facility]

        mock_session = Mock()

        mock_session.active_empire = Mock(id=0)
        mock_session._get_planet_by_id.return_value = mock_planet

        mock_cmd = Mock(
            entity_id=1, entity_type="planet",
            item_index=5, queue_id="fac-uuid-001",
        )

        result = handler.execute(mock_session, mock_cmd)

        assert not result.is_valid
        assert "Invalid queue index" in result.message


class TestReorderConstructionQueueCommandHandler:
    """Tests for ReorderConstructionQueueCommandHandler (PROJ-208 Phase 2)."""

    def test_planet_not_found(self):
        """Returns failure when planet not found."""
        handler = ReorderConstructionQueueCommandHandler()
        mock_session = Mock()
        mock_session.active_empire = Mock(id=0)
        mock_session._get_planet_by_id.return_value = None
        mock_cmd = Mock(entity_id=999, entity_type="planet", from_index=0, to_index=1, queue_id=None)

        result = handler.execute(mock_session, mock_cmd)

        assert not result.is_valid
        assert "Planet not found" in result.message

    def test_invalid_from_index(self):
        """Returns failure for invalid from_index."""
        handler = ReorderConstructionQueueCommandHandler()

        mock_planet = Mock()
        mock_planet.construction_queue = [{"design_id": "scout"}, {"design_id": "cruiser"}]

        mock_session = Mock()

        mock_session.active_empire = Mock(id=0)
        mock_session._get_planet_by_id.return_value = mock_planet

        mock_cmd = Mock(entity_id=1, entity_type="planet", from_index=5, to_index=0, queue_id=None)

        result = handler.execute(mock_session, mock_cmd)

        assert not result.is_valid
        assert "Invalid from_index" in result.message

    def test_invalid_to_index(self):
        """Returns failure for invalid to_index."""
        handler = ReorderConstructionQueueCommandHandler()

        mock_planet = Mock()
        mock_planet.construction_queue = [{"design_id": "scout"}, {"design_id": "cruiser"}]

        mock_session = Mock()

        mock_session.active_empire = Mock(id=0)
        mock_session._get_planet_by_id.return_value = mock_planet

        mock_cmd = Mock(entity_id=1, entity_type="planet", from_index=0, to_index=5, queue_id=None)

        result = handler.execute(mock_session, mock_cmd)

        assert not result.is_valid
        assert "Invalid to_index" in result.message

    def test_reorders_item_forward(self):
        """Successfully moves item forward in queue."""
        handler = ReorderConstructionQueueCommandHandler()

        item1 = {"design_id": "scout"}
        item2 = {"design_id": "cruiser"}
        item3 = {"design_id": "battleship"}
        mock_planet = Mock()
        mock_planet.construction_queue = [item1, item2, item3]

        mock_session = Mock()

        mock_session.active_empire = Mock(id=0)
        mock_session._get_planet_by_id.return_value = mock_planet

        # Move item at index 0 to index 2
        mock_cmd = Mock(entity_id=1, entity_type="planet", from_index=0, to_index=2, queue_id=None)

        result = handler.execute(mock_session, mock_cmd)

        assert result.is_valid
        # After pop(0) and insert(2): [item2, item3] -> insert(2, item1) -> [item2, item3, item1]
        assert mock_planet.construction_queue == [item2, item3, item1]

    def test_reorders_item_backward(self):
        """Successfully moves item backward in queue."""
        handler = ReorderConstructionQueueCommandHandler()

        item1 = {"design_id": "scout"}
        item2 = {"design_id": "cruiser"}
        item3 = {"design_id": "battleship"}
        mock_planet = Mock()
        mock_planet.construction_queue = [item1, item2, item3]

        mock_session = Mock()

        mock_session.active_empire = Mock(id=0)
        mock_session._get_planet_by_id.return_value = mock_planet

        # Move item at index 2 to index 0
        mock_cmd = Mock(entity_id=1, entity_type="planet", from_index=2, to_index=0, queue_id=None)

        result = handler.execute(mock_session, mock_cmd)

        assert result.is_valid
        # After pop(2) and insert(0): [item1, item2] -> insert(0, item3) -> [item3, item1, item2]
        assert mock_planet.construction_queue == [item3, item1, item2]

    def test_reorders_fleet_queue(self):
        """Successfully reorders fleet construction queue."""
        handler = ReorderConstructionQueueCommandHandler()

        item1 = {"design_id": "fighter"}
        item2 = {"design_id": "bomber"}
        mock_fleet = Mock()
        mock_fleet.owner_id = 0
        mock_fleet.construction_queue = [item1, item2]

        mock_session = Mock()

        mock_session.active_empire = Mock(id=0)
        mock_session._get_fleet_by_id.return_value = mock_fleet

        mock_cmd = Mock(entity_id=1, entity_type="fleet", from_index=1, to_index=0, queue_id=None)

        result = handler.execute(mock_session, mock_cmd)

        assert result.is_valid
        assert mock_fleet.construction_queue == [item2, item1]

    def test_reorders_facility_queue(self):
        """Successfully reorders items in a facility queue (BUG-103)."""
        handler = ReorderConstructionQueueCommandHandler()

        # Planet base queue (should be untouched)
        base_item = {"design_id": "complex_a"}
        mock_planet = Mock()
        mock_planet.construction_queue = [base_item]
        mock_planet.id = 1

        # Facility queue (target)
        fac_item1 = {"design_id": "scout"}
        fac_item2 = {"design_id": "cruiser"}
        mock_facility = Mock()
        mock_facility.instance_id = "fac-uuid-001"
        mock_facility.construction_queue = [fac_item1, fac_item2]
        mock_planet.facilities = [mock_facility]

        mock_session = Mock()

        mock_session.active_empire = Mock(id=0)
        mock_session._get_planet_by_id.return_value = mock_planet

        mock_cmd = Mock(
            entity_id=1, entity_type="planet",
            from_index=1, to_index=0,
            queue_id="fac-uuid-001",
        )

        result = handler.execute(mock_session, mock_cmd)

        assert result.is_valid
        assert mock_facility.construction_queue == [fac_item2, fac_item1]
        # Base queue unchanged
        assert mock_planet.construction_queue == [base_item]
