"""
Unit tests for StrategyWindowManager class.

Tests window lifecycle management: opening, closing, and tracking of modal windows.
"""
import pytest
from unittest.mock import Mock, MagicMock, patch
import pygame


# =============================================================================
# Test Fixtures
# =============================================================================

@pytest.fixture
def mock_scene():
    """Create mock scene with required attributes."""
    scene = Mock()
    scene.current_empire = Mock()
    scene.current_empire.id = 1
    scene.galaxy = Mock()
    scene._facade = Mock()
    scene._facade.get_all_events = Mock(return_value=[])
    scene.on_navigate_to_hex_build = Mock()
    return scene


@pytest.fixture
def mock_manager():
    """Create mock pygame_gui manager."""
    return Mock()


@pytest.fixture
def window_manager(mock_scene, mock_manager):
    """Create StrategyWindowManager instance."""
    from game.ui.screens.strategy_window_manager import StrategyWindowManager

    return StrategyWindowManager(
        scene=mock_scene,
        manager=mock_manager,
        width=1920,
        height=1080,
        input_mapper=None,
        asset_resolver=None,
    )


# =============================================================================
# Initialization Tests
# =============================================================================

class TestStrategyWindowManagerInit:
    """Tests for StrategyWindowManager initialization."""

    def test_init_sets_all_windows_to_none(self, window_manager):
        """Test initialization sets all window references to None."""
        assert window_manager.planet_list_window is None
        assert window_manager.build_queue_list_window is None
        assert window_manager.empire_build_queue_window is None
        assert window_manager.event_log_window is None
        assert window_manager.fleet_orders_window is None
        assert window_manager.fleet_report_window is None
        assert window_manager.transfer_dialog is None
        assert window_manager.empire_panel_window is None

    def test_init_stores_references(self, mock_scene, mock_manager):
        """Test initialization stores scene and manager references."""
        from game.ui.screens.strategy_window_manager import StrategyWindowManager

        wm = StrategyWindowManager(mock_scene, mock_manager, 1920, 1080)

        assert wm.scene is mock_scene
        assert wm.manager is mock_manager
        assert wm.width == 1920
        assert wm.height == 1080

    def test_init_empty_callbacks_dict(self, window_manager):
        """Test initialization creates empty callbacks dict."""
        assert window_manager.ui_callbacks == {}

    def test_init_confirmation_dialog_attributes(self, window_manager):
        """BUG-97: Confirmation dialog attributes must be initialized to None."""
        assert window_manager._pending_confirmation_dialog is None
        assert window_manager._pending_confirmation_callback is None


# =============================================================================
# Handle Resize Tests
# =============================================================================

class TestHandleResize:
    """Tests for handle_resize method."""

    def test_handle_resize_updates_dimensions(self, window_manager):
        """Test handle_resize updates stored dimensions."""
        window_manager.handle_resize(2560, 1440)

        assert window_manager.width == 2560
        assert window_manager.height == 1440


# =============================================================================
# Planet List Window Tests
# =============================================================================

class TestPlanetListWindow:
    """Tests for planet list window management."""

    @patch('game.ui.screens.strategy_windows.list_windows.PlanetListWindow')
    def test_open_planet_list_creates_window(self, mock_window_class, window_manager):
        """Test open_planet_list creates PlanetListWindow."""
        window_manager.open_planet_list()

        mock_window_class.assert_called_once()
        assert window_manager.planet_list_window is not None

    @patch('game.ui.screens.strategy_windows.list_windows.PlanetListWindow')
    def test_open_planet_list_passes_correct_params(self, mock_window_class, window_manager):
        """Test open_planet_list passes correct parameters."""
        window_manager.open_planet_list()

        call_args = mock_window_class.call_args
        # Check rect is passed (first positional arg)
        rect = call_args[0][0]
        assert isinstance(rect, pygame.Rect)
        # Check manager is passed (second positional arg)
        assert call_args[0][1] is window_manager.manager
        # Check galaxy is passed (third positional arg)
        assert call_args[0][2] is window_manager.scene.galaxy
        # Check empire is passed (fourth positional arg)
        assert call_args[0][3] is window_manager.scene.current_empire

    def test_on_planet_list_closed_clears_reference(self, window_manager):
        """Test _on_planet_list_closed clears window reference."""
        window_manager.planet_list_window = Mock()

        window_manager._on_planet_list_closed()

        assert window_manager.planet_list_window is None


# =============================================================================
# Build Queue List Window Tests
# =============================================================================

class TestBuildQueueListWindow:
    """Tests for build queue list window management."""

    @patch('game.ui.screens.strategy_windows.build_queue_windows.BuildQueueListWindow')
    def test_open_build_queue_list_creates_window(self, mock_window_class, window_manager):
        """Test open_build_queue_list creates BuildQueueListWindow."""
        window_manager.open_build_queue_list()

        mock_window_class.assert_called_once()
        assert window_manager.build_queue_list_window is not None

    @patch('game.ui.screens.strategy_windows.build_queue_windows.BuildQueueListWindow')
    def test_open_build_queue_list_kills_existing(self, mock_window_class, window_manager):
        """Test open_build_queue_list kills existing window first."""
        existing = Mock()
        window_manager.build_queue_list_window = existing

        window_manager.open_build_queue_list()

        existing.kill.assert_called_once()

    def test_on_build_queue_list_closed_clears_reference(self, window_manager):
        """Test _on_build_queue_list_closed clears window reference."""
        window_manager.build_queue_list_window = Mock()

        window_manager._on_build_queue_list_closed()

        assert window_manager.build_queue_list_window is None


# =============================================================================
# Empire Build Queue Window Tests
# =============================================================================

class TestEmpireBuildQueueWindow:
    """Tests for empire build queue window management."""

    @patch('game.ui.screens.strategy_windows.build_queue_windows.EmpireBuildQueueWindow')
    def test_open_empire_build_queue_creates_window(self, mock_window_class, window_manager):
        """Test open_empire_build_queue_window creates window."""
        window_manager.open_empire_build_queue_window()

        mock_window_class.assert_called_once()
        assert window_manager.empire_build_queue_window is not None

    @patch('game.ui.screens.strategy_windows.build_queue_windows.EmpireBuildQueueWindow')
    def test_open_empire_build_queue_kills_existing(self, mock_window_class, window_manager):
        """Test open_empire_build_queue_window kills existing first."""
        existing = Mock()
        window_manager.empire_build_queue_window = existing

        window_manager.open_empire_build_queue_window()

        existing.kill.assert_called_once()

    def test_on_empire_build_queue_closed_clears_reference(self, window_manager):
        """Test callback clears window reference."""
        window_manager.empire_build_queue_window = Mock()

        window_manager._on_empire_build_queue_closed()

        assert window_manager.empire_build_queue_window is None


# =============================================================================
# Event Log Window Tests
# =============================================================================

class TestEventLogWindow:
    """Tests for event log window management."""

    @patch('game.ui.screens.strategy_windows.event_log_window_ctrl.EventLogWindow')
    def test_open_event_log_creates_window(self, mock_window_class, window_manager):
        """Test open_event_log creates EventLogWindow."""
        window_manager.open_event_log()

        mock_window_class.assert_called_once()
        assert window_manager.event_log_window is not None

    @patch('game.ui.screens.strategy_windows.event_log_window_ctrl.EventLogWindow')
    def test_open_event_log_kills_existing(self, mock_window_class, window_manager):
        """Test open_event_log kills existing window first."""
        existing = Mock()
        window_manager.event_log_window = existing

        window_manager.open_event_log()

        existing.kill.assert_called_once()

    @patch('game.ui.screens.strategy_windows.event_log_window_ctrl.EventLogWindow')
    def test_open_event_log_with_events(self, mock_window_class, window_manager):
        """Test open_event_log_with_events passes specific events."""
        events = [{'type': 'test', 'message': 'Hello'}]

        window_manager.open_event_log_with_events(events)

        call_args = mock_window_class.call_args
        assert call_args[0][2] == events  # Third positional arg is events

    def test_on_event_log_closed_clears_reference(self, window_manager):
        """Test callback clears window reference."""
        window_manager.event_log_window = Mock()

        window_manager._on_event_log_closed()

        assert window_manager.event_log_window is None


# =============================================================================
# PROJ-215 Phase 4: Event Log Navigation Tests
# =============================================================================

class TestEventLogNavigation:
    """Tests for event log navigation callback."""

    def test_on_event_log_navigate_closes_window(self, window_manager):
        """Test navigation callback closes the event log window."""
        mock_window = Mock()
        window_manager.event_log_window = mock_window

        window_manager._on_event_log_navigate([5, 3])

        mock_window.kill.assert_called_once()

    def test_on_event_log_navigate_centers_camera(self, window_manager):
        """Test navigation callback centers camera on hex."""
        # Set up scene with camera navigator
        mock_camera_nav = Mock()
        window_manager.scene._camera_nav = mock_camera_nav

        window_manager._on_event_log_navigate([5, 3])

        mock_camera_nav.center_on_hex.assert_called_once()
        # Verify HexCoord was created with correct values
        call_arg = mock_camera_nav.center_on_hex.call_args[0][0]
        assert call_arg.q == 5
        assert call_arg.r == 3

    def test_on_event_log_navigate_handles_no_camera_nav(self, window_manager):
        """Test navigation doesn't crash if scene lacks _camera_nav."""
        # Remove _camera_nav from scene
        if hasattr(window_manager.scene, '_camera_nav'):
            delattr(window_manager.scene, '_camera_nav')

        # Should not raise
        window_manager._on_event_log_navigate([5, 3])

    def test_on_event_log_navigate_handles_no_window(self, window_manager):
        """Test navigation doesn't crash if event_log_window is None."""
        window_manager.event_log_window = None
        mock_camera_nav = Mock()
        window_manager.scene._camera_nav = mock_camera_nav

        # Should not raise
        window_manager._on_event_log_navigate([5, 3])

        # Camera should still be moved
        mock_camera_nav.center_on_hex.assert_called_once()

    @patch('game.ui.screens.strategy_windows.event_log_window_ctrl.EventLogWindow')
    def test_open_event_log_passes_navigate_callback(self, mock_window_class, window_manager):
        """Test open_event_log passes navigation callback to window.

        PROJ-309 sub-phase 3.10: the navigate callback now lives on the
        EventLogRegistrar; the composer's ``_on_event_log_navigate`` method
        delegates to it. The contract is that the callback passed to
        EventLogWindow drives the registrar's _on_navigate behavior.
        """
        window_manager.open_event_log()

        call_kwargs = mock_window_class.call_args[1]
        assert 'on_navigate_callback' in call_kwargs
        # The bound method object lives on the registrar now.
        assert call_kwargs['on_navigate_callback'] == window_manager._event_log._on_navigate


# =============================================================================
# Empire Panel Window Tests
# =============================================================================

class TestEmpirePanelWindow:
    """Tests for empire panel window management."""

    @patch('game.ui.screens.strategy_windows.empire_panel_ctrl.EmpirePanelWindow')
    def test_open_empire_panel_creates_window(self, mock_window_class, window_manager):
        """Test open_empire_panel creates EmpirePanelWindow."""
        window_manager.open_empire_panel()

        mock_window_class.assert_called_once()
        assert window_manager.empire_panel_window is not None

    @patch('game.ui.screens.strategy_windows.empire_panel_ctrl.EmpirePanelWindow')
    def test_open_empire_panel_kills_existing(self, mock_window_class, window_manager):
        """Test open_empire_panel kills existing window first."""
        existing = Mock()
        window_manager.empire_panel_window = existing

        window_manager.open_empire_panel()

        existing.kill.assert_called_once()

    def test_on_empire_panel_closed_clears_reference(self, window_manager):
        """Test callback clears window reference."""
        window_manager.empire_panel_window = Mock()

        window_manager._on_empire_panel_closed()

        assert window_manager.empire_panel_window is None


# =============================================================================
# Fleet Orders Window Tests
# =============================================================================

class TestFleetOrdersWindow:
    """Tests for fleet orders window management."""

    @patch('game.ui.screens.orders_window.OrdersWindow')
    def test_open_orders_window_creates_window(self, mock_window_class, window_manager):
        """Test open_orders_window creates OrdersWindow."""
        fleet = Mock()

        window_manager.open_orders_window(fleet)

        mock_window_class.assert_called_once()

    @patch('game.ui.screens.orders_window.OrdersWindow')
    def test_open_orders_window_kills_existing(self, mock_window_class, window_manager):
        """Test open_orders_window kills existing window first."""
        existing = Mock()
        window_manager.fleet_orders_window = existing
        fleet = Mock()

        window_manager.open_orders_window(fleet)

        existing.kill.assert_called_once()

    @patch('game.ui.screens.orders_window.OrdersWindow')
    def test_open_orders_window_passes_fleet(self, mock_window_class, window_manager):
        """Test open_orders_window passes fleet to window."""
        fleet = Mock()
        fleet.id = "F-001"

        window_manager.open_orders_window(fleet)

        call_args = mock_window_class.call_args
        assert call_args[0][2] is fleet  # Third positional arg


# =============================================================================
# Fleet Report Window Tests
# =============================================================================

class TestFleetReportWindow:
    """Tests for fleet report window management."""

    @patch('game.ui.screens.strategy_windows.fleet_report_ctrl.FleetReportWindow')
    def test_open_fleet_report_creates_window(self, mock_window_class, window_manager):
        """Test open_fleet_report_window creates FleetReportWindow."""
        fleet = Mock()

        window_manager.open_fleet_report_window(fleet)

        mock_window_class.assert_called_once()
        assert window_manager.fleet_report_window is not None

    @patch('game.ui.screens.strategy_windows.fleet_report_ctrl.FleetReportWindow')
    def test_open_fleet_report_kills_existing(self, mock_window_class, window_manager):
        """Test open_fleet_report_window kills existing first."""
        existing = Mock()
        window_manager.fleet_report_window = existing
        fleet = Mock()

        window_manager.open_fleet_report_window(fleet)

        existing.kill.assert_called_once()

    def test_on_fleet_report_closed_clears_reference(self, window_manager):
        """Test callback clears window reference."""
        window_manager.fleet_report_window = Mock()

        window_manager._on_fleet_report_closed()

        assert window_manager.fleet_report_window is None


# =============================================================================
# Transfer Dialog Tests
# =============================================================================

class TestTransferDialog:
    """Tests for transfer dialog management."""

    def test_open_transfer_dialog_creates_dialog(self, window_manager):
        """Test open_transfer_dialog creates TransferDialog."""
        fleet = Mock()
        hex_coord = (10, 20)

        # Patch where TransferDialog is imported inside the method
        with patch('game.ui.screens.transfer_dialog.TransferDialog') as mock_dialog_class:
            window_manager.open_transfer_dialog(fleet, hex_coord)

            mock_dialog_class.assert_called_once()
            assert window_manager.transfer_dialog is not None

    def test_open_transfer_dialog_kills_existing(self, window_manager):
        """Test open_transfer_dialog kills existing dialog first."""
        existing = Mock()
        window_manager.transfer_dialog = existing
        fleet = Mock()

        with patch('game.ui.screens.transfer_dialog.TransferDialog'):
            window_manager.open_transfer_dialog(fleet, (10, 20))

        existing.kill.assert_called_once()


# =============================================================================
# Cargo Quick Dialog Tests
# =============================================================================

class TestCargoQuickDialog:
    """Tests for cargo quick dialog."""

    def test_open_cargo_quick_dialog_creates_dialog(self, window_manager):
        """Test open_cargo_quick_dialog creates dialog."""
        fleet = Mock()
        hex_coord = (10, 20)

        with patch('game.ui.screens.cargo_quick_dialog.CargoQuickDialog') as mock_dialog_class:
            window_manager.open_cargo_quick_dialog(fleet, hex_coord, 'unload')

            mock_dialog_class.assert_called_once()

    def test_open_cargo_quick_dialog_passes_direction(self, window_manager):
        """Test open_cargo_quick_dialog passes direction parameter."""
        fleet = Mock()

        with patch('game.ui.screens.cargo_quick_dialog.CargoQuickDialog') as mock_dialog_class:
            window_manager.open_cargo_quick_dialog(fleet, (5, 5), 'load')

            call_kwargs = mock_dialog_class.call_args[1]
            assert call_kwargs['direction'] == 'load'


# =============================================================================
# Planet Selection Prompt Tests
# =============================================================================

class TestPlanetSelectionPrompt:
    """Tests for planet selection prompt."""

    @patch('game.ui.screens.strategy_windows.selection_prompts.PlanetSelectionWindow')
    def test_prompt_planet_selection_creates_window(self, mock_window_class, window_manager):
        """Test prompt_planet_selection creates selection window."""
        planets = [Mock(), Mock()]
        callback = Mock()

        window_manager.prompt_planet_selection(planets, callback)

        mock_window_class.assert_called_once()

    @patch('game.ui.screens.strategy_windows.selection_prompts.PlanetSelectionWindow')
    def test_prompt_planet_selection_passes_planets_and_callback(self, mock_window_class, window_manager):
        """Test prompt_planet_selection passes planets and callback."""
        planets = [Mock(name="P1"), Mock(name="P2")]
        callback = Mock()

        window_manager.prompt_planet_selection(planets, callback)

        call_args = mock_window_class.call_args
        assert call_args[0][2] == planets  # Third positional arg
        assert call_args[0][3] is callback  # Fourth positional arg


# =============================================================================
# System Selection Prompt Tests (PROJ-138)
# =============================================================================

class TestSystemSelectionPrompt:
    """Tests for system selection prompt."""

    @patch('game.ui.screens.strategy_windows.selection_prompts.SystemSelectionWindow')
    def test_open_system_selection_creates_window(self, mock_window_class, window_manager):
        """Test open_system_selection creates selection window."""
        systems = [Mock(), Mock()]
        current_system = Mock()
        callback = Mock()

        window_manager.open_system_selection(systems, current_system, callback)

        mock_window_class.assert_called_once()

    @patch('game.ui.screens.strategy_windows.selection_prompts.SystemSelectionWindow')
    def test_open_system_selection_passes_args(self, mock_window_class, window_manager):
        """Test open_system_selection passes systems, current_system, and callback."""
        systems = [Mock(), Mock()]
        current_system = Mock()
        callback = Mock()

        window_manager.open_system_selection(systems, current_system, callback)

        call_args = mock_window_class.call_args
        assert call_args[0][2] == systems
        assert call_args[0][3] == current_system
        assert call_args[0][4] is callback


# =============================================================================
# Move Choice Prompt Tests
# =============================================================================

class TestMoveChoicePrompt:
    """Tests for move choice prompt."""

    @patch('game.ui.screens.strategy_windows.move_choice_dialog.MoveChoiceWindow')
    @patch('game.ui.screens.strategy_windows.move_choice_dialog.pygame_gui.elements.UIButton')
    @patch('game.ui.screens.strategy_windows.move_choice_dialog.pygame_gui.elements.UILabel')
    def test_prompt_move_choice_creates_window(self, mock_label, mock_button, mock_window, window_manager):
        """Test prompt_move_choice creates choice window.

        PROJ-313 Phase 6: window construction routes through the
        MoveChoiceWindow(StrategyModalWindow) subclass, not raw pygame_gui.
        """
        fleet = Mock()
        target_hex = (10, 20)
        on_sector = Mock()
        on_intercept = Mock()

        window_manager.prompt_move_choice(fleet, target_hex, on_sector, on_intercept)

        mock_window.assert_called_once()
        # Two buttons should be created
        assert mock_button.call_count == 2

    @patch('game.ui.screens.strategy_windows.move_choice_dialog.MoveChoiceWindow')
    @patch('game.ui.screens.strategy_windows.move_choice_dialog.pygame_gui.elements.UIButton')
    @patch('game.ui.screens.strategy_windows.move_choice_dialog.pygame_gui.elements.UILabel')
    def test_prompt_move_choice_registers_callbacks(self, mock_label, mock_button, mock_window, window_manager):
        """Test prompt_move_choice registers callbacks in ui_callbacks.

        PROJ-313 Phase 6: window construction routes through MoveChoiceWindow.
        """
        # Each UIButton() call returns a unique mock
        mock_button.side_effect = [Mock(name='btn1'), Mock(name='btn2')]

        fleet = Mock()
        on_sector = Mock()
        on_intercept = Mock()

        window_manager.prompt_move_choice(fleet, (10, 20), on_sector, on_intercept)

        # Two callbacks should be registered (one for each button)
        assert len(window_manager.ui_callbacks) == 2


# =============================================================================
# Process UI Callbacks Tests
# =============================================================================

class TestProcessUICallbacks:
    """Tests for process_ui_callbacks method."""

    def test_process_ui_callbacks_executes_registered(self, window_manager):
        """Test process_ui_callbacks executes registered callback."""
        import pygame_gui

        button = Mock()
        callback = Mock()
        window_manager.ui_callbacks[button] = callback

        event = Mock()
        event.type = pygame_gui.UI_BUTTON_PRESSED
        event.ui_element = button

        result = window_manager.process_ui_callbacks(event)

        assert result is True
        callback.assert_called_once()
        assert button not in window_manager.ui_callbacks  # Removed after execution

    def test_process_ui_callbacks_returns_false_for_unknown(self, window_manager):
        """Test process_ui_callbacks returns False for unregistered button."""
        import pygame_gui

        unknown_button = Mock()

        event = Mock()
        event.type = pygame_gui.UI_BUTTON_PRESSED
        event.ui_element = unknown_button

        result = window_manager.process_ui_callbacks(event)

        assert result is False

    def test_process_ui_callbacks_ignores_non_button_events(self, window_manager):
        """Test process_ui_callbacks ignores non-button-press events."""
        event = Mock()
        event.type = 12345  # Some other event type

        result = window_manager.process_ui_callbacks(event)

        assert result is False


# =============================================================================
# Confirmation Dialog Tests (BUG-97)
# =============================================================================

class TestConfirmationDialog:
    """Tests for confirmation dialog management."""

    def test_process_confirmation_event_no_dialog_shown(self, window_manager):
        """BUG-97: process_confirmation_event must not crash when no dialog has been shown."""
        import pygame_gui

        event = Mock()
        event.type = pygame_gui.UI_CONFIRMATION_DIALOG_CONFIRMED
        event.ui_element = Mock()

        # Must not raise AttributeError
        result = window_manager.process_confirmation_event(event)

        assert result is False


# =============================================================================
# Multiple Windows Tests
# =============================================================================

class TestMultipleWindows:
    """Tests for handling multiple windows simultaneously."""

    @patch('game.ui.screens.strategy_windows.list_windows.PlanetListWindow')
    @patch('game.ui.screens.strategy_windows.fleet_report_ctrl.FleetReportWindow')
    @patch('game.ui.screens.strategy_windows.event_log_window_ctrl.EventLogWindow')
    def test_open_multiple_windows(self, mock_event, mock_fleet, mock_planet, window_manager):
        """Test opening multiple windows simultaneously."""
        window_manager.open_planet_list()
        window_manager.open_fleet_report_window(Mock())
        window_manager.open_event_log()

        assert window_manager.planet_list_window is not None
        assert window_manager.fleet_report_window is not None
        assert window_manager.event_log_window is not None
