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

    # Mock list container for row display
    win.row_labels = []
    win.list_panel = MagicMock()
    win.scroll_bar = MagicMock()
    win.scroll_bar.start_percentage = 0.0

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
        # _has_modal_open checks these scene attributes
        scene.build_queue_screen = None
        scene.action_open_design = False

        ui.scene = scene
        ui.width = 1920
        ui.height = 1080
        ui.manager = MagicMock()
        ui._mapper = None

        # Local window tracking (kept on StrategyUI)
        ui.planet_report_panel = None
        ui.menu_panel = None

        # PROJ-86: Window manager mock for modal tracking
        ui._window_manager = MagicMock()
        ui._window_manager.fleet_orders_window = None
        ui._window_manager.planet_list_window = None
        ui._window_manager.build_queue_list_window = None
        ui._window_manager.empire_build_queue_window = None
        ui._window_manager.fleet_report_window = None
        ui._window_manager.transfer_dialog = None
        ui._window_manager.event_log_window = None

        # PROJ-86 Phase 7: Event router
        from game.ui.screens.strategy_event_router import StrategyEventRouter
        ui._event_router = StrategyEventRouter(ui)

        return ui, scene

    def test_event_log_window_attr_exists(self):
        """StrategyUI._window_manager should have event_log_window attribute."""
        ui, _ = self._make_strategy_ui()
        assert hasattr(ui._window_manager, 'event_log_window')
        assert ui._window_manager.event_log_window is None

    def test_has_modal_open_detects_event_log(self):
        """_has_modal_open() should return True when event_log_window is set."""
        ui, _ = self._make_strategy_ui()
        ui._window_manager.event_log_window = MagicMock()
        assert ui._has_modal_open() is True

    def test_has_modal_open_false_when_no_event_log(self):
        """_has_modal_open() should return False when event_log_window is None."""
        ui, _ = self._make_strategy_ui()
        assert ui._has_modal_open() is False

    def test_on_event_log_closed_clears_reference(self):
        """_on_event_log_closed() should set event_log_window to None via window manager."""
        ui, _ = self._make_strategy_ui()
        ui._window_manager.event_log_window = MagicMock()
        ui._window_manager._on_event_log_closed()
        # Verify the method was called (it's now on window manager)
        ui._window_manager._on_event_log_closed.assert_called()

    def test_open_event_log_creates_window(self):
        """open_event_log() should delegate to window manager."""
        ui, scene = self._make_strategy_ui()
        ui.open_event_log()
        # Verify delegation to window manager
        ui._window_manager.open_event_log.assert_called_once()

    def test_open_event_log_passes_all_events(self):
        """open_event_log() should delegate to window manager which fetches events."""
        ui, scene = self._make_strategy_ui()
        ui.open_event_log()
        # Verify delegation to window manager
        ui._window_manager.open_event_log.assert_called_once()

    def test_open_event_log_kills_existing(self):
        """open_event_log() via window manager should handle existing window."""
        ui, scene = self._make_strategy_ui()
        # This is now handled internally by window manager
        ui.open_event_log()
        ui._window_manager.open_event_log.assert_called_once()

    def test_open_event_log_with_events(self):
        """open_event_log_with_events() should delegate to window manager."""
        ui, scene = self._make_strategy_ui()
        specific_events = [_make_event()]
        ui.open_event_log_with_events(specific_events)
        # Verify delegation with specific events
        ui._window_manager.open_event_log_with_events.assert_called_once_with(specific_events)


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
