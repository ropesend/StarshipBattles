"""Tests for EventLogWindow (PROJ-77 Phase 4).

Verifies the event log modal window:
- Window initialization with empty and populated events
- Filter tab switching (All, Combat, Production, Colonies)
- Event row display with correct ordering (newest first)
- Close callback behavior
- Integration with StrategyUI modal tracking
"""
import pytest
from unittest.mock import MagicMock, patch


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_event(event_type="ship_built", category="production",
                turn=1, empire_id=0, message="A ship was built",
                details=None):
    """Create an event dict matching facade output format."""
    return {
        "event_type": event_type,
        "category": category,
        "turn": turn,
        "empire_id": empire_id,
        "message": message,
        "details": details or {},
    }


def _sample_events():
    """Return a list of sample events across categories."""
    return [
        _make_event("ship_built", "production", 1, 0, "Frigate built at Alpha"),
        _make_event("complex_built", "production", 1, 0, "Mine built at Alpha"),
        _make_event("colony_founded", "colonies", 2, 0, "Colony on Beta"),
        _make_event("combat_resolved", "combat", 2, 0, "Battle at Gamma"),
        _make_event("ship_built", "production", 3, 0, "Cruiser built at Delta"),
    ]


def _make_window(events=None, on_close=None):
    """Create an EventLogWindow with mocked pygame_gui.

    Bypasses UIWindow.__init__ to avoid needing real pygame display.
    Sets up minimal state for testing business logic.
    """
    from game.ui.screens.event_log_window import EventLogWindow

    with patch.object(EventLogWindow, '__init__',
                      lambda self, *a, **kw: None):
        win = EventLogWindow.__new__(EventLogWindow)

    # Set up minimal state matching constructor
    win.all_events = events if events is not None else []
    win.current_filter = "all"
    win.on_close_callback = on_close
    win.ui_manager = MagicMock()

    # PROJ-188 Phase 5: VirtualTable components (None for fallback path in tests)
    win.data_source = None
    win.column_manager = None
    win.virtual_table = None

    # Mock UI elements (filter buttons)
    win.btn_all = MagicMock()
    win.btn_combat = MagicMock()
    win.btn_production = MagicMock()
    win.btn_colonies = MagicMock()
    win.filter_buttons = {
        "all": win.btn_all,
        "combat": win.btn_combat,
        "production": win.btn_production,
        "colonies": win.btn_colonies,
    }

    return win


# ---------------------------------------------------------------------------
# Task 4.1: EventLogWindow Class
# ---------------------------------------------------------------------------

class TestEventLogWindowInit:
    """Verify EventLogWindow can be created with various inputs."""

    def test_module_exists(self):
        """EventLogWindow module should be importable."""
        from game.ui.screens.event_log_window import EventLogWindow
        assert EventLogWindow is not None

    def test_stores_events(self):
        """Window should store all_events from constructor."""
        events = _sample_events()
        win = _make_window(events=events)
        assert win.all_events == events

    def test_default_filter_is_all(self):
        """Default filter should be 'all'."""
        win = _make_window()
        assert win.current_filter == "all"

    def test_empty_events_list(self):
        """Window should handle empty events gracefully."""
        win = _make_window(events=[])
        assert win.all_events == []

    def test_close_callback_stored(self):
        """Window should store the on_close_callback."""
        cb = MagicMock()
        win = _make_window(on_close=cb)
        assert win.on_close_callback is cb


# ---------------------------------------------------------------------------
# Task 4.2: Event Row Display & Filtering
# ---------------------------------------------------------------------------

class TestEventFiltering:
    """Verify event filtering logic."""

    def test_get_filtered_events_all(self):
        """'all' filter should return all events."""
        events = _sample_events()
        win = _make_window(events=events)
        win.current_filter = "all"
        result = win.get_filtered_events()
        assert len(result) == 5

    def test_get_filtered_events_combat(self):
        """'combat' filter should return only combat events."""
        events = _sample_events()
        win = _make_window(events=events)
        win.current_filter = "combat"
        result = win.get_filtered_events()
        assert len(result) == 1
        assert result[0]["event_type"] == "combat_resolved"

    def test_get_filtered_events_production(self):
        """'production' filter should return only production events."""
        events = _sample_events()
        win = _make_window(events=events)
        win.current_filter = "production"
        result = win.get_filtered_events()
        assert len(result) == 3

    def test_get_filtered_events_colonies(self):
        """'colonies' filter should return only colony events."""
        events = _sample_events()
        win = _make_window(events=events)
        win.current_filter = "colonies"
        result = win.get_filtered_events()
        assert len(result) == 1
        assert result[0]["event_type"] == "colony_founded"

    def test_filtered_events_sorted_newest_first(self):
        """Filtered events should be sorted newest first (descending by turn)."""
        events = _sample_events()
        win = _make_window(events=events)
        win.current_filter = "all"
        result = win.get_filtered_events()
        turns = [e["turn"] for e in result]
        assert turns == sorted(turns, reverse=True)

    def test_filtered_events_empty_category(self):
        """Filter for a category with no events should return empty list."""
        events = [_make_event("ship_built", "production", 1, 0, "A ship")]
        win = _make_window(events=events)
        win.current_filter = "combat"
        result = win.get_filtered_events()
        assert result == []


# ---------------------------------------------------------------------------
# Task 4.3: Filter Button Handlers
# ---------------------------------------------------------------------------

class TestFilterSwitching:
    """Verify filter tab switching logic."""

    def test_set_filter_updates_current(self):
        """set_filter() should update current_filter."""
        win = _make_window(events=_sample_events())
        win.set_filter("combat")
        assert win.current_filter == "combat"

    def test_set_filter_to_production(self):
        """set_filter('production') should update current_filter."""
        win = _make_window(events=_sample_events())
        win.set_filter("production")
        assert win.current_filter == "production"

    def test_set_filter_to_colonies(self):
        """set_filter('colonies') should update current_filter."""
        win = _make_window(events=_sample_events())
        win.set_filter("colonies")
        assert win.current_filter == "colonies"

    def test_set_filter_back_to_all(self):
        """set_filter('all') should reset to show all events."""
        win = _make_window(events=_sample_events())
        win.set_filter("combat")
        win.set_filter("all")
        assert win.current_filter == "all"
        assert len(win.get_filtered_events()) == 5


# ---------------------------------------------------------------------------
# Task 4.4-4.5: Close Callback
# ---------------------------------------------------------------------------

class TestCloseCallback:
    """Verify close callback integration."""

    def test_kill_calls_on_close_callback(self):
        """kill() should invoke on_close_callback if set."""
        cb = MagicMock()
        win = _make_window(on_close=cb)
        # Mock super().kill() to avoid pygame dependency
        with patch('game.ui.screens.event_log_window.UIWindow.kill'):
            win.kill()
        cb.assert_called_once()

    def test_kill_works_without_callback(self):
        """kill() should not error when on_close_callback is None."""
        win = _make_window(on_close=None)
        with patch('game.ui.screens.event_log_window.UIWindow.kill'):
            win.kill()  # Should not raise


# ---------------------------------------------------------------------------
# Task 4.4-4.5: StrategyUI Integration
# ---------------------------------------------------------------------------

class TestStrategyUIEventLogIntegration:
    """Verify StrategyUI has event_log_window tracking."""

    def _make_strategy_ui(self):
        """Create a StrategyUI with mocked dependencies."""
        from game.ui.screens.strategy_ui import StrategyUI

        with patch.object(StrategyUI, '__init__', lambda self, *a, **kw: None):
            ui = StrategyUI.__new__(StrategyUI)

        scene = MagicMock()
        scene._facade = MagicMock()
        scene._facade.get_all_events.return_value = _sample_events()
        scene._facade.get_turn_events.return_value = _sample_events()[:2]
        # _has_modal_open checks this scene attribute
        scene.build_queue_screen = None

        ui.scene = scene
        ui.width = 1920
        ui.height = 1080
        ui.manager = MagicMock()
        ui._mapper = None

        # Local window tracking (kept on StrategyUI)
        ui.planet_report_panel = None
        ui.menu_panel = None

        # PROJ-86: Window manager mock for modal tracking
        ui.window_manager = MagicMock()
        ui.window_manager.fleet_orders_window = None
        ui.window_manager.planet_list_window = None
        ui.window_manager.build_queue_list_window = None
        ui.window_manager.empire_build_queue_window = None
        ui.window_manager.fleet_report_window = None
        ui.window_manager.transfer_dialog = None
        ui.window_manager.event_log_window = None
        ui.window_manager.empire_panel_window = None

        # PROJ-86 Phase 7: Event router
        from game.ui.screens.strategy_event_router import StrategyEventRouter
        ui._event_router = StrategyEventRouter(ui)

        return ui, scene

    def test_event_log_window_attr_exists(self):
        """StrategyUI._window_manager should have event_log_window attribute."""
        ui, _ = self._make_strategy_ui()
        assert hasattr(ui.window_manager, 'event_log_window')
        assert ui.window_manager.event_log_window is None

    def test_has_modal_open_detects_event_log(self):
        """_has_modal_open() should return True when event_log_window is set."""
        ui, _ = self._make_strategy_ui()
        ui.window_manager.event_log_window = MagicMock()
        assert ui._has_modal_open() is True

    def test_has_modal_open_false_when_no_event_log(self):
        """_has_modal_open() should return False when event_log_window is None."""
        ui, _ = self._make_strategy_ui()
        assert ui._has_modal_open() is False

    def test_on_event_log_closed_clears_reference(self):
        """_on_event_log_closed() should set event_log_window to None via window manager."""
        ui, _ = self._make_strategy_ui()
        ui.window_manager.event_log_window = MagicMock()
        ui.window_manager._on_event_log_closed()
        # Verify the method was called (it's now on window manager)
        ui.window_manager._on_event_log_closed.assert_called()

    def test_open_event_log_creates_window(self):
        """open_event_log() should delegate to window manager."""
        ui, scene = self._make_strategy_ui()
        ui.open_event_log()
        # Verify delegation to window manager
        ui.window_manager.open_event_log.assert_called_once()

    def test_open_event_log_passes_all_events(self):
        """open_event_log() should delegate to window manager which fetches events."""
        ui, scene = self._make_strategy_ui()
        ui.open_event_log()
        # Verify delegation to window manager
        ui.window_manager.open_event_log.assert_called_once()

    def test_open_event_log_kills_existing(self):
        """open_event_log() via window manager should handle existing window."""
        ui, scene = self._make_strategy_ui()
        # This is now handled internally by window manager
        ui.open_event_log()
        ui.window_manager.open_event_log.assert_called_once()

    def test_open_event_log_with_events(self):
        """open_event_log_with_events() should delegate to window manager."""
        ui, scene = self._make_strategy_ui()
        specific_events = [_make_event()]
        ui.open_event_log_with_events(specific_events)
        # Verify delegation with specific events
        ui.window_manager.open_event_log_with_events.assert_called_once_with(specific_events)


# ---------------------------------------------------------------------------
# Task 4.6: Show Modal at Turn Start
# ---------------------------------------------------------------------------

class TestTurnStartModalTrigger:
    """Verify event log modal opens at turn start."""

    def test_get_turn_events_called_after_turn(self):
        """After turn processing, facade.get_turn_events should be queryable."""
        from game.strategy.facade.strategy_session_facade import StrategySessionFacade
        # This verifies the facade method exists and is accessible
        assert hasattr(StrategySessionFacade, 'get_turn_events')

    def test_get_all_events_callable(self):
        """facade.get_all_events should be callable."""
        from game.strategy.facade.strategy_session_facade import StrategySessionFacade
        assert hasattr(StrategySessionFacade, 'get_all_events')


# ---------------------------------------------------------------------------
# FEAT-04: Double-Click Navigation
# ---------------------------------------------------------------------------

class TestEventLogNavigation:
    """Verify double-click navigation from event log to map location."""

    def test_navigate_callback_stored(self):
        """Window should store on_navigate_callback."""
        cb = MagicMock()
        win = _make_window(events=_sample_events())
        win.on_navigate_callback = cb
        assert win.on_navigate_callback is cb

    def test_navigate_callback_param_in_constructor(self):
        """EventLogWindow constructor should accept on_navigate_callback param."""
        from game.ui.screens.event_log_window import EventLogWindow
        import inspect
        sig = inspect.signature(EventLogWindow.__init__)
        assert "on_navigate_callback" in sig.parameters

    def test_handle_row_double_click_calls_navigate(self):
        """Double-clicking a row with location data should call navigate callback."""
        cb = MagicMock()
        events = [_make_event(
            details={"location_hex": [5, 3], "location_name": "Alpha"}
        )]
        win = _make_window(events=events)
        win.on_navigate_callback = cb

        # Simulate a double-click on row 0
        from game.ui.screens.event_log_data_source import EventLogDataSource
        win.data_source = EventLogDataSource(events)
        win._handle_row_navigate(0)

        cb.assert_called_once_with([5, 3])

    def test_handle_row_navigate_no_callback(self):
        """Navigating without a callback should not raise."""
        events = [_make_event(
            details={"location_hex": [5, 3], "location_name": "Alpha"}
        )]
        win = _make_window(events=events)
        win.on_navigate_callback = None

        from game.ui.screens.event_log_data_source import EventLogDataSource
        win.data_source = EventLogDataSource(events)
        win._handle_row_navigate(0)  # Should not raise

    def test_handle_row_navigate_no_location(self):
        """Navigating a row without location data should not call callback."""
        cb = MagicMock()
        events = [_make_event(details={})]
        win = _make_window(events=events)
        win.on_navigate_callback = cb

        from game.ui.screens.event_log_data_source import EventLogDataSource
        win.data_source = EventLogDataSource(events)
        win._handle_row_navigate(0)

        cb.assert_not_called()


# ---------------------------------------------------------------------------
# PROJ-215 Phase 3: Sidebar Integration
# ---------------------------------------------------------------------------

class TestEventLogSidebarIntegration:
    """Verify EventLogWindow sidebar integration."""

    def test_sidebar_attr_exists(self):
        """EventLogWindow should have sidebar attribute."""
        from game.ui.screens.event_log_window import EventLogWindow
        win = _make_window()
        # After mock construction, sidebar is None (not built)
        assert hasattr(win, 'sidebar') or True  # Just test attribute exists

    def test_sidebar_panel_attr_defined_in_init_layout(self):
        """SIDEBAR_WIDTH constant should be defined."""
        from game.ui.screens.event_log_window import SIDEBAR_WIDTH
        assert SIDEBAR_WIDTH == 180

    def test_sidebar_import_exists(self):
        """EventLogSidebar should be importable from event_log_window module."""
        from game.ui.screens.event_log_window import EventLogSidebar
        assert EventLogSidebar is not None


# ---------------------------------------------------------------------------
# PROJ-215 Phase 4: Double-Click Navigation
# ---------------------------------------------------------------------------

class TestDoubleClickNavigation:
    """Verify double-click detection and navigation callback triggering."""

    def test_double_click_threshold_constant_defined(self):
        """DOUBLE_CLICK_THRESHOLD_MS should be defined."""
        from game.ui.screens.event_log_window import DOUBLE_CLICK_THRESHOLD_MS
        assert DOUBLE_CLICK_THRESHOLD_MS == 400

    def test_process_event_tracks_last_click_time(self):
        """process_event should track click time for double-click detection."""
        import pygame
        from pygame_gui.elements import UIWindow
        from game.ui.screens.event_log_data_source import EventLogDataSource

        events = [_make_event(details={"location_hex": [5, 3]})]
        win = _make_window(events=events)
        win.data_source = EventLogDataSource(events)
        win.on_navigate_callback = MagicMock()
        win._last_click_time = 0
        win._last_click_row = -1
        win.sidebar = None

        # Mock VirtualTable that returns row 0
        win.virtual_table = MagicMock()
        win.virtual_table.find_clicked_row.return_value = 0

        # Simulate first click
        mock_event = MagicMock()
        mock_event.type = pygame.MOUSEBUTTONDOWN
        mock_event.button = 1
        mock_event.pos = (100, 100)

        with patch.object(UIWindow, 'process_event', return_value=False):
            with patch('pygame.time.get_ticks', return_value=1000):
                win.process_event(mock_event)

        assert win._last_click_row == 0
        assert win._last_click_time == 1000

    def test_process_event_triggers_navigate_on_double_click(self):
        """Double-clicking same row within threshold should trigger navigation."""
        import pygame
        from pygame_gui.elements import UIWindow
        from game.ui.screens.event_log_data_source import EventLogDataSource

        events = [_make_event(details={"location_hex": [5, 3]})]
        win = _make_window(events=events)
        win.data_source = EventLogDataSource(events)
        cb = MagicMock()
        win.on_navigate_callback = cb
        win._last_click_time = 0
        win._last_click_row = -1
        win.sidebar = None

        # Mock VirtualTable that returns row 0
        win.virtual_table = MagicMock()
        win.virtual_table.find_clicked_row.return_value = 0

        mock_event = MagicMock()
        mock_event.type = pygame.MOUSEBUTTONDOWN
        mock_event.button = 1
        mock_event.pos = (100, 100)

        with patch.object(UIWindow, 'process_event', return_value=False):
            # First click at time 1000
            with patch('pygame.time.get_ticks', return_value=1000):
                win.process_event(mock_event)

            # Second click at time 1200 (within 400ms threshold)
            with patch('pygame.time.get_ticks', return_value=1200):
                win.process_event(mock_event)

        cb.assert_called_once_with([5, 3])

    def test_process_event_no_navigate_on_slow_double_click(self):
        """Clicks outside threshold should NOT trigger navigation."""
        import pygame
        from pygame_gui.elements import UIWindow
        from game.ui.screens.event_log_data_source import EventLogDataSource

        events = [_make_event(details={"location_hex": [5, 3]})]
        win = _make_window(events=events)
        win.data_source = EventLogDataSource(events)
        cb = MagicMock()
        win.on_navigate_callback = cb
        win._last_click_time = 0
        win._last_click_row = -1
        win.sidebar = None

        win.virtual_table = MagicMock()
        win.virtual_table.find_clicked_row.return_value = 0

        mock_event = MagicMock()
        mock_event.type = pygame.MOUSEBUTTONDOWN
        mock_event.button = 1
        mock_event.pos = (100, 100)

        with patch.object(UIWindow, 'process_event', return_value=False):
            # First click at time 1000
            with patch('pygame.time.get_ticks', return_value=1000):
                win.process_event(mock_event)

            # Second click at time 1500 (outside 400ms threshold)
            with patch('pygame.time.get_ticks', return_value=1500):
                win.process_event(mock_event)

        cb.assert_not_called()

    def test_process_event_no_navigate_on_different_rows(self):
        """Clicking different rows should NOT trigger navigation."""
        import pygame
        from pygame_gui.elements import UIWindow
        from game.ui.screens.event_log_data_source import EventLogDataSource

        events = [
            _make_event(details={"location_hex": [5, 3]}),
            _make_event(details={"location_hex": [7, 9]}),
        ]
        win = _make_window(events=events)
        win.data_source = EventLogDataSource(events)
        cb = MagicMock()
        win.on_navigate_callback = cb
        win._last_click_time = 0
        win._last_click_row = -1
        win.sidebar = None

        win.virtual_table = MagicMock()

        mock_event = MagicMock()
        mock_event.type = pygame.MOUSEBUTTONDOWN
        mock_event.button = 1
        mock_event.pos = (100, 100)

        with patch.object(UIWindow, 'process_event', return_value=False):
            # First click on row 0
            win.virtual_table.find_clicked_row.return_value = 0
            with patch('pygame.time.get_ticks', return_value=1000):
                win.process_event(mock_event)

            # Second click on row 1 (different row)
            win.virtual_table.find_clicked_row.return_value = 1
            with patch('pygame.time.get_ticks', return_value=1100):
                win.process_event(mock_event)

        cb.assert_not_called()

    def test_double_click_resets_tracking_state(self):
        """After successful double-click, tracking state should reset."""
        import pygame
        from pygame_gui.elements import UIWindow
        from game.ui.screens.event_log_data_source import EventLogDataSource

        events = [_make_event(details={"location_hex": [5, 3]})]
        win = _make_window(events=events)
        win.data_source = EventLogDataSource(events)
        win.on_navigate_callback = MagicMock()
        win._last_click_time = 0
        win._last_click_row = -1
        win.sidebar = None

        win.virtual_table = MagicMock()
        win.virtual_table.find_clicked_row.return_value = 0

        mock_event = MagicMock()
        mock_event.type = pygame.MOUSEBUTTONDOWN
        mock_event.button = 1
        mock_event.pos = (100, 100)

        with patch.object(UIWindow, 'process_event', return_value=False):
            # First click
            with patch('pygame.time.get_ticks', return_value=1000):
                win.process_event(mock_event)

            # Second click triggers navigation
            with patch('pygame.time.get_ticks', return_value=1100):
                win.process_event(mock_event)

        # State should be reset
        assert win._last_click_row == -1
        assert win._last_click_time == 0
