"""Tests for FleetOperations using StrategySessionFacade.

These tests verify that FleetOperations correctly delegates to the facade
instead of directly accessing session internals.
"""
import pytest
from unittest.mock import Mock, MagicMock, patch
from game.core.hex_math import HexCoord
from game.core.validation import ValidationResult


class TestFleetOperationsInit:
    """Tests for FleetOperations initialization with facade."""

    def test_init_stores_facade_reference(self):
        """FleetOperations stores facade reference on init."""
        from game.ui.screens.strategy_fleet_ops import FleetOperations

        mock_scene = Mock()
        mock_facade = Mock()

        ops = FleetOperations(mock_scene, mock_facade)

        assert ops.facade is mock_facade
        assert ops.scene is mock_scene

    def test_init_without_facade_raises_error(self):
        """FleetOperations requires facade parameter."""
        from game.ui.screens.strategy_fleet_ops import FleetOperations

        mock_scene = Mock()

        with pytest.raises(TypeError):
            FleetOperations(mock_scene)  # Missing facade


class TestFleetOperationsNoSessionProperty:
    """Tests verifying session property is removed."""

    def test_no_session_property(self):
        """FleetOperations should not have session property."""
        from game.ui.screens.strategy_fleet_ops import FleetOperations

        mock_scene = Mock()
        mock_facade = Mock()

        ops = FleetOperations(mock_scene, mock_facade)

        assert not hasattr(ops, 'session')


class TestExecuteMove:
    """Tests for execute_move using facade."""

    def test_execute_move_uses_facade_for_path_preview(self):
        """execute_move calls facade.get_fleet_path_preview."""
        from game.ui.screens.strategy_fleet_ops import FleetOperations

        mock_scene = Mock()
        mock_facade = Mock()
        mock_facade.get_fleet_path_preview.return_value = [HexCoord(1, 0), HexCoord(2, 0)]
        mock_facade.handle_command.return_value = ValidationResult()

        ops = FleetOperations(mock_scene, mock_facade)

        mock_fleet = Mock()
        mock_fleet.id = 101
        target = HexCoord(2, 0)

        result = ops.execute_move(mock_fleet, target)

        mock_facade.get_fleet_path_preview.assert_called_once_with(101, target)

    def test_execute_move_uses_facade_for_command(self):
        """execute_move calls facade.handle_command for IssueMoveCommand."""
        from game.ui.screens.strategy_fleet_ops import FleetOperations
        from game.strategy.engine.commands import IssueMoveCommand

        mock_scene = Mock()
        mock_facade = Mock()
        mock_facade.get_fleet_path_preview.return_value = [HexCoord(1, 0)]
        mock_facade.handle_command.return_value = ValidationResult()

        ops = FleetOperations(mock_scene, mock_facade)

        mock_fleet = Mock()
        mock_fleet.id = 42
        target = HexCoord(1, 0)

        ops.execute_move(mock_fleet, target)

        # Verify handle_command was called
        mock_facade.handle_command.assert_called_once()
        cmd = mock_facade.handle_command.call_args[0][0]
        assert isinstance(cmd, IssueMoveCommand)
        assert cmd.fleet_id == 42
        assert cmd.target_hex == target

    def test_execute_move_returns_error_on_no_path(self):
        """execute_move returns error when no path available."""
        from game.ui.screens.strategy_fleet_ops import FleetOperations

        mock_scene = Mock()
        mock_facade = Mock()
        mock_facade.get_fleet_path_preview.return_value = None

        ops = FleetOperations(mock_scene, mock_facade)

        mock_fleet = Mock()
        mock_fleet.id = 101
        target = HexCoord(100, 100)

        result = ops.execute_move(mock_fleet, target)

        assert result['type'] == 'error'
        assert 'Unreachable' in result['message']

    def test_execute_move_returns_success_on_valid_move(self):
        """execute_move returns success when move succeeds."""
        from game.ui.screens.strategy_fleet_ops import FleetOperations

        mock_scene = Mock()
        mock_facade = Mock()
        mock_facade.get_fleet_path_preview.return_value = [HexCoord(1, 0)]
        mock_facade.handle_command.return_value = ValidationResult()

        ops = FleetOperations(mock_scene, mock_facade)

        mock_fleet = Mock()
        mock_fleet.id = 101

        result = ops.execute_move(mock_fleet, HexCoord(1, 0))

        assert result['type'] == 'success'


class TestExecuteIntercept:
    """Tests for execute_intercept using facade."""

    def test_execute_intercept_uses_facade_command(self):
        """execute_intercept calls facade.handle_command with IssueInterceptCommand."""
        from game.ui.screens.strategy_fleet_ops import FleetOperations
        from game.strategy.engine.commands import IssueInterceptCommand

        mock_scene = Mock()
        mock_facade = Mock()
        mock_facade.handle_command.return_value = ValidationResult()

        ops = FleetOperations(mock_scene, mock_facade)

        mock_fleet = Mock()
        mock_fleet.id = 10
        mock_target = Mock()
        mock_target.id = 20

        ops.execute_intercept(mock_fleet, mock_target)

        mock_facade.handle_command.assert_called_once()
        cmd = mock_facade.handle_command.call_args[0][0]
        assert isinstance(cmd, IssueInterceptCommand)
        assert cmd.fleet_id == 10
        assert cmd.target_fleet_id == 20

    def test_execute_intercept_returns_success(self):
        """execute_intercept returns success on valid intercept."""
        from game.ui.screens.strategy_fleet_ops import FleetOperations

        mock_scene = Mock()
        mock_facade = Mock()
        mock_facade.handle_command.return_value = ValidationResult()

        ops = FleetOperations(mock_scene, mock_facade)

        mock_fleet = Mock()
        mock_fleet.id = 10
        mock_target = Mock()
        mock_target.id = 20

        result = ops.execute_intercept(mock_fleet, mock_target)

        assert result['type'] == 'success'


class TestHandleJoinDesignation:
    """Tests for handle_join_designation using facade."""

    def test_join_uses_facade_command(self):
        """handle_join_designation calls facade.handle_command with IssueJoinFleetCommand."""
        from game.ui.screens.strategy_fleet_ops import FleetOperations
        from game.strategy.engine.commands import IssueJoinFleetCommand

        mock_scene = Mock()
        mock_scene.camera.screen_to_world.return_value = Mock(x=0, y=0)
        mock_scene.hex_size = 60

        mock_facade = Mock()
        mock_facade.handle_command.return_value = ValidationResult()

        ops = FleetOperations(mock_scene, mock_facade)

        # Mock get_fleet_at_hex to return a target fleet
        mock_target = Mock()
        mock_target.id = 50
        mock_target.owner_id = 1

        mock_selected = Mock()
        mock_selected.id = 40
        mock_selected.owner_id = 1

        ops.get_fleet_at_hex = Mock(return_value=mock_target)

        result = ops.handle_join_designation(100, 100, mock_selected)

        mock_facade.handle_command.assert_called_once()
        cmd = mock_facade.handle_command.call_args[0][0]
        assert isinstance(cmd, IssueJoinFleetCommand)
        assert cmd.fleet_id == 40
        assert cmd.target_fleet_id == 50

    def test_join_returns_none_for_no_target_fleet(self):
        """handle_join_designation returns None when no fleet at target."""
        from game.ui.screens.strategy_fleet_ops import FleetOperations

        mock_scene = Mock()
        mock_scene.camera.screen_to_world.return_value = Mock(x=0, y=0)
        mock_scene.hex_size = 60

        mock_facade = Mock()

        ops = FleetOperations(mock_scene, mock_facade)
        ops.get_fleet_at_hex = Mock(return_value=None)

        mock_selected = Mock()
        mock_selected.id = 40

        result = ops.handle_join_designation(100, 100, mock_selected)

        assert result is None
        mock_facade.handle_command.assert_not_called()

    def test_join_returns_none_for_self(self):
        """handle_join_designation returns None when targeting self."""
        from game.ui.screens.strategy_fleet_ops import FleetOperations

        mock_scene = Mock()
        mock_scene.camera.screen_to_world.return_value = Mock(x=0, y=0)
        mock_scene.hex_size = 60

        mock_facade = Mock()

        ops = FleetOperations(mock_scene, mock_facade)

        mock_selected = Mock()
        mock_selected.id = 40
        ops.get_fleet_at_hex = Mock(return_value=mock_selected)  # Same fleet

        result = ops.handle_join_designation(100, 100, mock_selected)

        assert result is None

    def test_join_returns_none_for_enemy_fleet(self):
        """handle_join_designation returns None for enemy fleet."""
        from game.ui.screens.strategy_fleet_ops import FleetOperations

        mock_scene = Mock()
        mock_scene.camera.screen_to_world.return_value = Mock(x=0, y=0)
        mock_scene.hex_size = 60

        mock_facade = Mock()

        ops = FleetOperations(mock_scene, mock_facade)

        mock_target = Mock()
        mock_target.id = 50
        mock_target.owner_id = 2  # Different owner

        mock_selected = Mock()
        mock_selected.id = 40
        mock_selected.owner_id = 1

        ops.get_fleet_at_hex = Mock(return_value=mock_target)

        result = ops.handle_join_designation(100, 100, mock_selected)

        assert result is None
