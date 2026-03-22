"""Tests for FEAT-07: 'W' hotkey for explicit warp orders on strategy map.

Tests cover:
- W key triggers WARP_TARGET mode when fleet is selected and warp-capable
- W key silently ignored when no fleet selected
- W key silently ignored when fleet cannot warp
- ESC cancels WARP_TARGET mode
- WARP_TARGET click dispatches IssueWarpCommand via facade
- Right-click in WARP_TARGET cancels to SELECT
"""
import pytest
from unittest.mock import MagicMock, patch

import pygame

from game.core.input_actions import InputAction


class MockScene:
    """Mock scene for testing input handler."""

    def __init__(self):
        self.selected_fleet = MagicMock()
        self.ui = MagicMock()
        self._superweapons = MagicMock()
        self._fleet_ops = MagicMock()
        self._colonization = MagicMock()
        self.camera = MagicMock()
        self._camera_nav = MagicMock()
        self.facade = MagicMock()
        self.hex_size = 30
        self.galaxy = MagicMock()
        self.on_ui_selection = MagicMock()


class MockInputMapper:
    """Mock input mapper that returns a fixed action."""

    def __init__(self, action_to_return):
        self._action = action_to_return

    def resolve(self, event, contexts):
        return self._action


class TestWarpHotkeyModeActivation:
    """Tests for W key -> WARP_TARGET mode transitions."""

    @pytest.fixture
    def handler(self):
        from game.ui.screens.strategy_input_handler import StrategyInputHandler
        scene = MockScene()
        handler = StrategyInputHandler(scene, input_mapper=None)
        return handler

    def test_w_sets_warp_target_mode(self, handler):
        """FLEET_WARP sets WARP_TARGET mode when fleet is selected."""
        mapper = MockInputMapper(InputAction.FLEET_WARP)
        handler._mapper = mapper
        handler.scene.selected_fleet = MagicMock()
        # Fleet is warp-capable (default mock behavior - hasattr returns True,
        # capabilities.can_use_warp() returns truthy MagicMock)

        event = MagicMock()
        handler._handle_keydown_mapped(event)

        assert handler.input_mode == 'WARP_TARGET'

    def test_w_ignored_without_fleet(self, handler):
        """FLEET_WARP does nothing when no fleet selected."""
        mapper = MockInputMapper(InputAction.FLEET_WARP)
        handler._mapper = mapper
        handler.scene.selected_fleet = None

        event = MagicMock()
        handler._handle_keydown_mapped(event)

        assert handler.input_mode == 'SELECT'

    def test_w_ignored_when_fleet_cannot_warp(self, handler):
        """FLEET_WARP silently ignored when fleet cannot use warp."""
        mapper = MockInputMapper(InputAction.FLEET_WARP)
        handler._mapper = mapper
        fleet = MagicMock()
        fleet.capabilities.can_use_warp.return_value = False
        handler.scene.selected_fleet = fleet

        event = MagicMock()
        handler._handle_keydown_mapped(event)

        assert handler.input_mode == 'SELECT'

    def test_escape_cancels_warp_target_mode(self, handler):
        """ESC returns to SELECT from WARP_TARGET mode."""
        mapper = MockInputMapper(InputAction.FLEET_CANCEL_MODE)
        handler._mapper = mapper
        handler.input_mode = 'WARP_TARGET'

        event = MagicMock()
        handler._handle_keydown_mapped(event)

        assert handler.input_mode == 'SELECT'


class TestWarpHotkeyViaRealMapper:
    """Tests using the real InputMapper with default keybindings."""

    @pytest.fixture
    def mapper(self):
        from game.ui.services.input_mapper import InputMapper
        from game.core.paths import Paths
        m = InputMapper()
        m.load(Paths.DEFAULT_KEYBINDINGS_FILE)
        return m

    @pytest.fixture
    def mock_scene(self):
        scene = MagicMock()
        scene.ui = MagicMock()
        scene.ui.manager = MagicMock()
        scene.ui.window_manager = MagicMock()
        scene.ui.window_manager.planet_list_window = None
        scene.selected_fleet = None
        scene.build_queue_screen = None
        scene._camera_nav = MagicMock()
        return scene

    def _keydown(self, key, mod=0):
        return pygame.event.Event(pygame.KEYDOWN, {'key': key, 'mod': mod})

    def test_w_key_triggers_warp_mode(self, mock_scene, mapper):
        """Pressing W sets input mode to WARP_TARGET when warp-capable fleet selected."""
        from game.ui.screens.strategy_input_handler import StrategyInputHandler
        handler = StrategyInputHandler(mock_scene, input_mapper=mapper)
        fleet = MagicMock()
        fleet.capabilities.can_use_warp.return_value = True
        mock_scene.selected_fleet = fleet

        handler.handle_event(self._keydown(pygame.K_w))

        assert handler.input_mode == 'WARP_TARGET'

    def test_w_key_ignored_without_fleet(self, mock_scene, mapper):
        """Pressing W does nothing when no fleet selected."""
        from game.ui.screens.strategy_input_handler import StrategyInputHandler
        handler = StrategyInputHandler(mock_scene, input_mapper=mapper)
        mock_scene.selected_fleet = None

        handler.handle_event(self._keydown(pygame.K_w))

        assert handler.input_mode == 'SELECT'

    def test_w_key_ignored_when_fleet_cannot_warp(self, mock_scene, mapper):
        """Pressing W does nothing when fleet cannot warp."""
        from game.ui.screens.strategy_input_handler import StrategyInputHandler
        handler = StrategyInputHandler(mock_scene, input_mapper=mapper)
        fleet = MagicMock()
        fleet.capabilities.can_use_warp.return_value = False
        mock_scene.selected_fleet = fleet

        handler.handle_event(self._keydown(pygame.K_w))

        assert handler.input_mode == 'SELECT'


class TestWarpClickDispatching:
    """Tests for WARP_TARGET click handling."""

    @pytest.fixture
    def handler(self):
        from game.ui.screens.strategy_input_handler import StrategyInputHandler
        scene = MockScene()
        scene.ui.handle_click = MagicMock(return_value=False)
        # Mock camera.screen_to_world to return a proper Vector2-like object
        world_pos = MagicMock()
        world_pos.x = 100.0
        world_pos.y = 200.0
        scene.camera.screen_to_world = MagicMock(return_value=world_pos)
        scene.camera.zoom = 0.3  # Low zoom so _resolve_click_target skips planet hit-testing
        handler = StrategyInputHandler(scene, input_mapper=None)
        # Mock _get_system_at_hex to return None (no system context)
        scene._get_system_at_hex = MagicMock(return_value=None)
        return handler

    def test_warp_left_click_issues_command_on_success(self, handler):
        """Left click in WARP_TARGET mode issues IssueWarpCommand via facade."""
        handler.input_mode = 'WARP_TARGET'
        fleet = MagicMock()
        fleet.id = 42
        handler.scene.selected_fleet = fleet
        handler.scene.facade.handle_command = MagicMock(
            return_value=MagicMock(is_valid=True)
        )

        result = handler.handle_click(100, 200, 1)

        assert result is True
        # Command was issued
        handler.scene.facade.handle_command.assert_called_once()
        cmd = handler.scene.facade.handle_command.call_args[0][0]
        assert cmd.fleet_id == 42
        # Returns to SELECT mode on success
        assert handler.input_mode == 'SELECT'

    def test_warp_left_click_stays_in_mode_on_failure(self, handler):
        """Left click in WARP_TARGET stays in mode on command failure."""
        handler.input_mode = 'WARP_TARGET'
        fleet = MagicMock()
        fleet.id = 42
        handler.scene.selected_fleet = fleet
        handler.scene.facade.handle_command = MagicMock(
            return_value=MagicMock(is_valid=False, error_message="No warp point here")
        )

        result = handler.handle_click(100, 200, 1)

        assert result is True
        # Stays in WARP_TARGET mode on failure (user can try clicking again)
        assert handler.input_mode == 'WARP_TARGET'

    def test_warp_right_click_cancels(self, handler):
        """Right click in WARP_TARGET mode cancels to SELECT."""
        handler.input_mode = 'WARP_TARGET'

        result = handler.handle_click(100, 200, 3)

        assert result is True
        assert handler.input_mode == 'SELECT'
