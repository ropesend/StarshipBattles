"""Integration tests for move order registration pipeline.

PROJ-216 Phase 4: These tests verify that the click-to-order pipeline works
correctly, ensuring that clicks in MOVE mode result in orders being added
to fleet queues via the command handler chain.

These tests complement the click gate tests (Task 4.1) by testing the
command dispatch chain AFTER the click passes through the gate.
"""

import pytest
from unittest.mock import Mock, MagicMock, patch, PropertyMock
from game.core.hex_math import HexCoord
from game.core.validation import ValidationResult


# ===========================================================================
# Task 4.2: Move Order End-to-End Tests
# ===========================================================================

class TestMoveOrderRegistration:
    """Tests for move order registration through the command chain."""

    def test_execute_move_issues_command_via_facade(self):
        """execute_move creates IssueMoveCommand and sends to facade.handle_command."""
        from game.ui.screens.strategy_fleet_ops import FleetOperations
        from game.strategy.engine.commands import IssueMoveCommand

        mock_scene = Mock()
        mock_facade = Mock()
        mock_facade.get_fleet_path_preview.return_value = [HexCoord(1, 0), HexCoord(2, 0)]
        mock_facade.handle_command.return_value = ValidationResult()

        ops = FleetOperations(mock_scene, mock_facade)

        mock_fleet = Mock()
        mock_fleet.id = 42
        target = HexCoord(2, 0)

        result = ops.execute_move(mock_fleet, target)

        # Verify command was sent
        mock_facade.handle_command.assert_called_once()
        cmd = mock_facade.handle_command.call_args[0][0]
        assert isinstance(cmd, IssueMoveCommand)
        assert cmd.fleet_id == 42
        assert cmd.target_hex == HexCoord(2, 0)

    def test_execute_move_returns_fleet_on_success(self):
        """execute_move returns success dict with fleet reference."""
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
        assert result['fleet'] is mock_fleet

    def test_execute_move_returns_error_when_no_path(self):
        """execute_move returns error when path preview returns None."""
        from game.ui.screens.strategy_fleet_ops import FleetOperations

        mock_scene = Mock()
        mock_facade = Mock()
        mock_facade.get_fleet_path_preview.return_value = None

        ops = FleetOperations(mock_scene, mock_facade)

        mock_fleet = Mock()
        mock_fleet.id = 101

        result = ops.execute_move(mock_fleet, HexCoord(100, 100))

        assert result['type'] == 'error'
        assert 'Unreachable' in result['message']
        mock_facade.handle_command.assert_not_called()


class TestClickDispatcherRoutesMove:
    """Tests for ClickModeDispatcher routing in MOVE mode."""

    def _create_click_dispatcher(self):
        """Create a ClickModeDispatcher with mocked dependencies.

        Returns:
            Tuple of (dispatcher, handler_mock, scene_mock).
        """
        from game.ui.screens.strategy_click_dispatcher import ClickModeDispatcher

        handler = MagicMock()
        handler.input_mode = 'SELECT'

        scene = MagicMock()
        scene.selected_fleet = MagicMock()
        scene.selected_fleet.id = 42
        scene._fleet_ops = MagicMock()
        scene._fleet_ops.handle_move_designation.return_value = {
            'type': 'success',
            'fleet': scene.selected_fleet
        }

        handler.scene = scene

        # Create dispatcher
        dispatcher = ClickModeDispatcher(handler)

        # Add fleet router mock
        handler._fleet_router = MagicMock()

        return dispatcher, handler, scene

    def test_move_mode_left_click_calls_handle_move_designation(self):
        """Left click in MOVE mode calls fleet_ops.handle_move_designation."""
        dispatcher, handler, scene = self._create_click_dispatcher()

        # Set MOVE mode
        handler.input_mode = 'MOVE'

        result = dispatcher.dispatch_click(500, 400, 1)  # Left click

        assert result is True
        scene._fleet_ops.handle_move_designation.assert_called_once_with(
            500, 400, scene.selected_fleet
        )

    def test_move_mode_success_calls_finish_move_action(self):
        """Successful move designation calls _fleet_router.finish_move_action."""
        dispatcher, handler, scene = self._create_click_dispatcher()

        handler.input_mode = 'MOVE'
        scene._fleet_ops.handle_move_designation.return_value = {
            'type': 'success',
            'fleet': scene.selected_fleet
        }

        dispatcher.dispatch_click(500, 400, 1)

        handler._fleet_router.finish_move_action.assert_called_once_with(
            scene.selected_fleet
        )

    def test_move_mode_right_click_cancels(self):
        """Right click in MOVE mode cancels and returns to SELECT mode."""
        dispatcher, handler, scene = self._create_click_dispatcher()

        handler.input_mode = 'MOVE'

        result = dispatcher.dispatch_click(500, 400, 3)  # Right click

        assert result is True
        assert handler.input_mode == 'SELECT'

    def test_move_mode_error_result_returns_to_select(self):
        """Move designation error returns to SELECT mode."""
        dispatcher, handler, scene = self._create_click_dispatcher()

        handler.input_mode = 'MOVE'
        scene._fleet_ops.handle_move_designation.return_value = {
            'type': 'error',
            'message': 'Cannot move there'
        }

        dispatcher.dispatch_click(500, 400, 1)

        assert handler.input_mode == 'SELECT'

    def test_move_mode_choice_result_prompts_user(self):
        """Move designation with target fleet prompts for move vs intercept choice."""
        dispatcher, handler, scene = self._create_click_dispatcher()

        handler.input_mode = 'MOVE'
        target_fleet = MagicMock()
        scene._fleet_ops.handle_move_designation.return_value = {
            'type': 'choice',
            'target_hex': HexCoord(5, 5),
            'target_fleet': target_fleet
        }

        dispatcher.dispatch_click(500, 400, 1)

        # Should prompt for move choice
        scene.ui.prompt_move_choice.assert_called_once()
        args = scene.ui.prompt_move_choice.call_args[0]
        assert args[0] is target_fleet
        assert args[1] == HexCoord(5, 5)
        # args[2] and args[3] are the on_move and on_intercept callbacks


class TestSelectModeQuickMove:
    """Tests for quick move (right-click) in SELECT mode."""

    def _create_click_dispatcher(self):
        """Create a ClickModeDispatcher with mocked dependencies."""
        from game.ui.screens.strategy_click_dispatcher import ClickModeDispatcher

        handler = MagicMock()
        handler.input_mode = 'SELECT'

        scene = MagicMock()
        scene.selected_fleet = MagicMock()
        scene.selected_fleet.id = 42
        scene._fleet_ops = MagicMock()
        scene._fleet_ops.handle_move_designation.return_value = {
            'type': 'success',
            'fleet': scene.selected_fleet
        }

        handler.scene = scene
        handler._fleet_router = MagicMock()

        dispatcher = ClickModeDispatcher(handler)

        return dispatcher, handler, scene

    def test_select_mode_right_click_with_fleet_issues_move(self):
        """Right click in SELECT mode with selected fleet triggers move."""
        dispatcher, handler, scene = self._create_click_dispatcher()

        handler.input_mode = 'SELECT'

        result = dispatcher.dispatch_click(500, 400, 3)  # Right click

        assert result is True
        scene._fleet_ops.handle_move_designation.assert_called_once_with(
            500, 400, scene.selected_fleet
        )

    def test_select_mode_right_click_without_fleet_does_nothing(self):
        """Right click in SELECT mode without selected fleet does nothing."""
        dispatcher, handler, scene = self._create_click_dispatcher()

        handler.input_mode = 'SELECT'
        scene.selected_fleet = None

        result = dispatcher.dispatch_click(500, 400, 3)

        # Returns False since no fleet selected
        assert result is False
        scene._fleet_ops.handle_move_designation.assert_not_called()


class TestModeDispatchTable:
    """Tests that all input modes are routed correctly."""

    def _create_dispatcher_in_mode(self, mode):
        """Create dispatcher configured for a specific input mode."""
        from game.ui.screens.strategy_click_dispatcher import ClickModeDispatcher

        handler = MagicMock()
        handler.input_mode = mode

        scene = MagicMock()
        scene.selected_fleet = MagicMock()
        scene.camera = MagicMock()
        scene.hex_size = 60

        # Set up all mode handlers to return a result
        scene._fleet_ops.handle_move_designation.return_value = {'type': 'success', 'fleet': scene.selected_fleet}
        scene._fleet_ops.handle_join_designation.return_value = {'type': 'success', 'fleet': scene.selected_fleet}
        scene._colonization.handle_colonize_designation.return_value = {'type': 'success'}
        scene._superweapons.handle_implode_planet_designation.return_value = True
        scene._superweapons.handle_stellerate_star_designation.return_value = True
        scene._superweapons.handle_open_warp_designation.return_value = True
        scene._superweapons.handle_close_warp_designation.return_value = True
        scene._superweapons.handle_dyson_sphere_designation.return_value = True

        handler.scene = scene
        handler._fleet_router = MagicMock()

        dispatcher = ClickModeDispatcher(handler)

        return dispatcher, handler, scene

    def test_join_mode_routes_to_fleet_ops(self):
        """JOIN mode routes to fleet_ops.handle_join_designation."""
        dispatcher, handler, scene = self._create_dispatcher_in_mode('JOIN')

        dispatcher.dispatch_click(500, 400, 1)

        scene._fleet_ops.handle_join_designation.assert_called_once()

    def test_colonize_mode_routes_to_colonization(self):
        """COLONIZE_TARGET mode routes to colonization.handle_colonize_designation."""
        dispatcher, handler, scene = self._create_dispatcher_in_mode('COLONIZE_TARGET')

        dispatcher.dispatch_click(500, 400, 1)

        scene._colonization.handle_colonize_designation.assert_called_once()

    def test_implode_planet_mode_routes_to_superweapons(self):
        """IMPLODE_PLANET_TARGET mode routes to superweapons handler."""
        dispatcher, handler, scene = self._create_dispatcher_in_mode('IMPLODE_PLANET_TARGET')

        dispatcher.dispatch_click(500, 400, 1)

        scene._superweapons.handle_implode_planet_designation.assert_called_once()

    def test_stellerate_star_mode_routes_to_superweapons(self):
        """STELLERATE_STAR_TARGET mode routes to superweapons handler."""
        dispatcher, handler, scene = self._create_dispatcher_in_mode('STELLERATE_STAR_TARGET')

        dispatcher.dispatch_click(500, 400, 1)

        scene._superweapons.handle_stellerate_star_designation.assert_called_once()

    def test_all_modes_have_handlers(self):
        """All registered modes have corresponding handlers."""
        from game.ui.screens.strategy_click_dispatcher import ClickModeDispatcher

        handler = MagicMock()
        dispatcher = ClickModeDispatcher(handler)

        expected_modes = [
            'MOVE', 'JOIN', 'COLONIZE_TARGET', 'TRANSFER',
            'DROP_CARGO', 'LOAD_CARGO', 'IMPLODE_PLANET_TARGET',
            'STELLERATE_STAR_TARGET', 'OPEN_WARP_TARGET', 'CLOSE_WARP_TARGET',
            'DYSON_SPHERE_TARGET', 'SELECT'
        ]

        for mode in expected_modes:
            assert mode in dispatcher._mode_handlers, f"Missing handler for {mode}"

    def test_unknown_mode_returns_false(self):
        """Unknown input mode returns False (not handled)."""
        dispatcher, handler, scene = self._create_dispatcher_in_mode('UNKNOWN_MODE')

        result = dispatcher.dispatch_click(500, 400, 1)

        assert result is False
