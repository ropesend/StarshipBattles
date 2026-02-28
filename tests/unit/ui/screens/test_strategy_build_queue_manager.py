"""Tests for StrategyBuildQueueManager (PROJ-173 Phase 4).

Tests the extracted build queue management functionality.
"""

import pytest
from unittest.mock import MagicMock, patch


def _make_build_queue_manager():
    """Create a StrategyBuildQueueManager with mocked screen dependency."""
    from game.ui.screens.strategy_build_queue_manager import StrategyBuildQueueManager

    # Create mock screen
    mock_screen = MagicMock()
    mock_screen.session = MagicMock()
    mock_screen.session.galaxy = MagicMock()
    mock_screen.facade = MagicMock()  # PROJ-212: facade for command dispatch
    mock_screen.ui = MagicMock()
    mock_screen.ui.manager = MagicMock()
    mock_screen.selected_object = None
    mock_screen.build_queue_screen = None
    mock_screen.input_mapper = MagicMock()

    # Setup empire mocking
    empire = MagicMock()
    empire.id = 0
    mock_screen.session.empires = [empire]
    mock_screen.session.human_player_ids = [0]
    mock_screen.current_player_index = 0

    # Property mock for current_empire
    type(mock_screen).current_empire = property(lambda s: empire)

    manager = StrategyBuildQueueManager(mock_screen)

    return manager, mock_screen


class TestBuildQueueManagerInit:
    """Test StrategyBuildQueueManager initialization."""

    def test_init_stores_screen_reference(self):
        """Manager should store reference to parent screen."""
        manager, screen = _make_build_queue_manager()
        assert manager._screen is screen


class TestOnBuildYardClick:
    """Test on_build_yard_click() method."""

    def test_ignores_when_build_queue_already_open(self):
        """Should do nothing if build queue is already open."""
        manager, screen = _make_build_queue_manager()
        screen.build_queue_screen = MagicMock()

        manager.on_build_yard_click()

        screen.ui.hide_ui.assert_not_called()

    def test_ignores_when_no_selected_object(self):
        """Should do nothing when no object is selected."""
        manager, screen = _make_build_queue_manager()
        screen.selected_object = None

        manager.on_build_yard_click()

        screen.ui.hide_ui.assert_not_called()

    def test_ignores_non_planet_selection(self):
        """Should do nothing when selected object is not a Planet."""
        manager, screen = _make_build_queue_manager()
        screen.selected_object = MagicMock()  # Generic mock, not a Planet

        manager.on_build_yard_click()

        screen.ui.hide_ui.assert_not_called()

    def test_opens_build_queue_for_owned_planet(self):
        """Should open build queue for player-owned planet."""
        manager, screen = _make_build_queue_manager()

        # Create a properly mocked Planet
        from game.strategy.data.planet import Planet
        mock_planet = MagicMock(spec=Planet)
        mock_planet.owner_id = 0  # Same as player empire
        mock_planet.name = "Test Planet"
        screen.selected_object = mock_planet
        screen._get_object_asset = MagicMock(return_value=None)
        screen.session.galaxy.get_system_of_planet.return_value = None

        # PROJ-208: is_planet uses Protocol isinstance, need to patch it for mocks
        with patch('game.ui.screens.strategy_build_queue_manager.BuildQueueScreen') as MockBQS, \
             patch('game.ui.screens.strategy_build_queue_manager.DesignLibrary'), \
             patch('game.ui.screens.strategy_build_queue_manager.DesignLoaderAdapter'), \
             patch('game.ui.screens.strategy_build_queue_manager.is_planet', return_value=True):
            manager.on_build_yard_click()

        MockBQS.assert_called_once()
        screen.ui.hide_ui.assert_called_once()


class TestOnBuildQueueClose:
    """Test _on_build_queue_close() method."""

    def test_clears_build_queue_screen(self):
        """Should set build_queue_screen to None."""
        manager, screen = _make_build_queue_manager()
        screen.build_queue_screen = MagicMock()
        screen.build_queue_screen.queue_sources = []
        screen.selected_object = None

        manager._on_build_queue_close()

        assert screen.build_queue_screen is None

    def test_shows_ui(self):
        """Should call ui.show_ui()."""
        manager, screen = _make_build_queue_manager()
        screen.build_queue_screen = MagicMock()
        screen.build_queue_screen.queue_sources = []
        screen.selected_object = None

        manager._on_build_queue_close()

        screen.ui.show_ui.assert_called_once()

    def test_refreshes_selected_object(self):
        """Should refresh display for selected object."""
        manager, screen = _make_build_queue_manager()
        screen.build_queue_screen = MagicMock()
        screen.build_queue_screen.queue_sources = []
        screen.selected_object = MagicMock()
        screen._get_object_asset = MagicMock(return_value=None)

        manager._on_build_queue_close()

        screen.ui.show_detailed_report.assert_called_once()


class TestHandleFleetBuildQueueClose:
    """Test _handle_fleet_build_queue_close() method.

    PROJ-207 Phase 4: Tests now verify command dispatch instead of direct fleet manipulation.
    """

    def test_dispatches_build_command_when_queue_has_items(self):
        """Should dispatch IssueBuildOrderCommand when construction queue is not empty."""
        from game.strategy.engine.commands import IssueBuildOrderCommand
        manager, screen = _make_build_queue_manager()

        fleet = MagicMock()
        fleet.id = 42
        fleet.construction_queue = [MagicMock()]  # Non-empty queue
        fleet.orders = []

        manager._handle_fleet_build_queue_close(fleet)

        # Should have dispatched IssueBuildOrderCommand
        screen.facade.handle_command.assert_called_once()
        cmd = screen.facade.handle_command.call_args[0][0]
        assert isinstance(cmd, IssueBuildOrderCommand)
        assert cmd.fleet_id == 42

    def test_does_not_dispatch_build_command_if_fleet_already_has_build_order(self):
        """Should not dispatch command if fleet already has BUILD order."""
        from game.strategy.data.order_types import OrderType
        manager, screen = _make_build_queue_manager()

        fleet = MagicMock()
        fleet.id = 42
        fleet.construction_queue = [MagicMock()]
        existing_build_order = MagicMock()
        existing_build_order.type = OrderType.BUILD
        fleet.orders = [existing_build_order]

        manager._handle_fleet_build_queue_close(fleet)

        # Should NOT dispatch command
        screen.facade.handle_command.assert_not_called()

    def test_dispatches_remove_command_when_queue_empty(self):
        """Should dispatch RemoveBuildOrderCommand when construction queue is empty."""
        from game.strategy.engine.commands import RemoveBuildOrderCommand
        manager, screen = _make_build_queue_manager()

        fleet = MagicMock()
        fleet.id = 99
        fleet.construction_queue = []  # Empty queue
        fleet.orders = []

        manager._handle_fleet_build_queue_close(fleet)

        # Should have dispatched RemoveBuildOrderCommand
        screen.facade.handle_command.assert_called_once()
        cmd = screen.facade.handle_command.call_args[0][0]
        assert isinstance(cmd, RemoveBuildOrderCommand)
        assert cmd.fleet_id == 99


class TestOnFleetBuildClick:
    """Test on_fleet_build_click() method."""

    def test_ignores_when_build_queue_already_open(self):
        """Should do nothing if build queue is already open."""
        manager, screen = _make_build_queue_manager()
        screen.build_queue_screen = MagicMock()

        manager.on_fleet_build_click()

        screen.ui.hide_ui.assert_not_called()

    def test_ignores_non_fleet_selection(self):
        """Should do nothing when selected object is not a Fleet."""
        manager, screen = _make_build_queue_manager()
        screen.selected_object = MagicMock()  # Generic mock

        manager.on_fleet_build_click()

        screen.ui.hide_ui.assert_not_called()

    def test_opens_build_queue_for_fleet_with_shipyard(self):
        """Should open build queue for fleet with space shipyard."""
        manager, screen = _make_build_queue_manager()

        from game.strategy.data.fleet import Fleet
        mock_fleet = MagicMock(spec=Fleet)
        mock_fleet.owner_id = 0
        mock_fleet.has_space_shipyard = True
        mock_fleet.location = MagicMock()
        mock_fleet.id = 1
        screen.selected_object = mock_fleet
        screen._get_object_asset = MagicMock(return_value=None)

        # PROJ-208: is_fleet uses Protocol isinstance, need to patch it for mocks
        with patch('game.ui.screens.strategy_build_queue_manager.BuildQueueScreen') as MockBQS, \
             patch('game.ui.screens.strategy_build_queue_manager.DesignLibrary'), \
             patch('game.ui.screens.strategy_build_queue_manager.DesignLoaderAdapter'), \
             patch('game.ui.screens.strategy_build_queue_manager.is_fleet', return_value=True):
            manager.on_fleet_build_click()

        MockBQS.assert_called_once()
        screen.ui.hide_ui.assert_called_once()


class TestOnNavigateToHexBuild:
    """Test on_navigate_to_hex_build() method."""

    def test_ignores_when_build_queue_already_open(self):
        """Should do nothing if build queue is already open."""
        manager, screen = _make_build_queue_manager()
        screen.build_queue_screen = MagicMock()

        mock_hex = MagicMock()
        mock_source = MagicMock()

        manager.on_navigate_to_hex_build(mock_hex, mock_source)

        screen.ui.hide_ui.assert_not_called()

    def test_ignores_source_with_no_entity(self):
        """Should do nothing if source has no owner_entity."""
        manager, screen = _make_build_queue_manager()

        mock_hex = MagicMock()
        mock_source = MagicMock()
        mock_source.owner_entity = None

        manager.on_navigate_to_hex_build(mock_hex, mock_source)

        screen.ui.hide_ui.assert_not_called()

    def test_opens_build_queue_for_valid_source(self):
        """Should open build queue for valid hex and source."""
        manager, screen = _make_build_queue_manager()
        screen._get_object_asset = MagicMock(return_value=None)

        mock_hex = MagicMock()
        mock_source = MagicMock()
        mock_source.owner_entity = MagicMock()
        mock_source.display_name = "Test Planet"

        with patch('game.ui.screens.strategy_build_queue_manager.BuildQueueScreen') as MockBQS, \
             patch('game.ui.screens.strategy_build_queue_manager.DesignLibrary'), \
             patch('game.ui.screens.strategy_build_queue_manager.DesignLoaderAdapter'):
            manager.on_navigate_to_hex_build(mock_hex, mock_source)

        MockBQS.assert_called_once()
        screen.ui.close_empire_build_queue_window.assert_called_once()
        screen.ui.hide_ui.assert_called_once()
