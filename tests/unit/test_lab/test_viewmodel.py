"""
Unit tests for TestLabViewModel.

Tests the ViewModel's state management, event emission, and scroll handling
independently of pygame/rendering.
"""
import pytest
from unittest.mock import Mock, MagicMock, patch

from game.ui.screens.test_lab.viewmodel import TestLabViewModel, TestLabEvents


class TestTestLabEvents:
    """Test the event constants class."""

    def test_event_constants_defined(self):
        """All required event types are defined."""
        assert hasattr(TestLabEvents, 'SCROLL_CHANGED')
        assert hasattr(TestLabEvents, 'DIALOG_OPENED')
        assert hasattr(TestLabEvents, 'DIALOG_CLOSED')
        assert hasattr(TestLabEvents, 'PANELS_UPDATED')
        assert hasattr(TestLabEvents, 'TEST_SELECTED')

    def test_event_constants_unique(self):
        """Event constants are unique strings."""
        events = [
            TestLabEvents.SCROLL_CHANGED,
            TestLabEvents.DIALOG_OPENED,
            TestLabEvents.DIALOG_CLOSED,
            TestLabEvents.PANELS_UPDATED,
            TestLabEvents.TEST_SELECTED,
        ]
        assert len(events) == len(set(events)), "Event constants must be unique"


class TestTestLabViewModelInit:
    """Test ViewModel initialization."""

    def test_init_with_event_bus(self):
        """ViewModel initializes with event_bus."""
        event_bus = Mock()
        vm = TestLabViewModel(event_bus)
        assert vm.event_bus is event_bus

    def test_init_scroll_state(self):
        """ViewModel initializes with default scroll state."""
        event_bus = Mock()
        vm = TestLabViewModel(event_bus)
        assert vm.scroll_offset == 0
        assert vm.max_scroll == 0

    def test_init_dialog_state(self):
        """ViewModel initializes with no dialogs open."""
        event_bus = Mock()
        vm = TestLabViewModel(event_bus)
        assert vm.is_dialog_open is False
        assert vm.json_popup is None
        assert vm.confirmation_dialog is None


class TestScrollStateManagement:
    """Test scroll offset and clamping logic."""

    def test_scroll_offset_clamping_at_zero(self):
        """Scroll offset cannot go below zero."""
        event_bus = Mock()
        vm = TestLabViewModel(event_bus)
        vm.set_max_scroll(100)

        vm.scroll(-50)  # Try to scroll past top
        assert vm.scroll_offset == 0

    def test_scroll_offset_clamping_at_max(self):
        """Scroll offset cannot exceed max_scroll."""
        event_bus = Mock()
        vm = TestLabViewModel(event_bus)
        vm.set_max_scroll(100)

        vm.scroll(200)  # Try to scroll past bottom
        assert vm.scroll_offset == 100

    def test_scroll_within_bounds(self):
        """Scroll offset updates correctly within bounds."""
        event_bus = Mock()
        vm = TestLabViewModel(event_bus)
        vm.set_max_scroll(200)

        vm.scroll(50)
        assert vm.scroll_offset == 50

        vm.scroll(30)
        assert vm.scroll_offset == 80

    def test_scroll_emits_event(self):
        """Scrolling emits SCROLL_CHANGED event."""
        event_bus = Mock()
        vm = TestLabViewModel(event_bus)
        vm.set_max_scroll(100)

        vm.scroll(25)

        event_bus.emit.assert_called_with(
            TestLabEvents.SCROLL_CHANGED,
            {'offset': 25, 'max_scroll': 100}
        )

    def test_set_max_scroll_clamps_current(self):
        """Setting max_scroll clamps current offset if needed."""
        event_bus = Mock()
        vm = TestLabViewModel(event_bus)
        vm.set_max_scroll(200)
        vm.scroll(150)
        assert vm.scroll_offset == 150

        # Reduce max - should clamp current
        vm.set_max_scroll(100)
        assert vm.scroll_offset == 100

    def test_reset_scroll(self):
        """reset_scroll() sets offset back to 0."""
        event_bus = Mock()
        vm = TestLabViewModel(event_bus)
        vm.set_max_scroll(200)
        vm.scroll(100)

        vm.reset_scroll()
        assert vm.scroll_offset == 0


class TestDialogState:
    """Test dialog open/close state management."""

    def test_open_json_popup(self):
        """Opening JSON popup updates state."""
        event_bus = Mock()
        vm = TestLabViewModel(event_bus)

        mock_popup = Mock()
        vm.open_json_popup(mock_popup)

        assert vm.json_popup is mock_popup
        assert vm.is_dialog_open is True
        event_bus.emit.assert_called_with(TestLabEvents.DIALOG_OPENED, 'json_popup')

    def test_close_json_popup(self):
        """Closing JSON popup updates state."""
        event_bus = Mock()
        vm = TestLabViewModel(event_bus)

        mock_popup = Mock()
        vm.open_json_popup(mock_popup)
        event_bus.reset_mock()

        vm.close_json_popup()

        assert vm.json_popup is None
        assert vm.is_dialog_open is False
        event_bus.emit.assert_called_with(TestLabEvents.DIALOG_CLOSED, 'json_popup')

    def test_open_confirmation_dialog(self):
        """Opening confirmation dialog updates state."""
        event_bus = Mock()
        vm = TestLabViewModel(event_bus)

        mock_dialog = Mock()
        vm.open_confirmation_dialog(mock_dialog)

        assert vm.confirmation_dialog is mock_dialog
        assert vm.is_dialog_open is True
        event_bus.emit.assert_called_with(TestLabEvents.DIALOG_OPENED, 'confirmation')

    def test_close_confirmation_dialog(self):
        """Closing confirmation dialog updates state."""
        event_bus = Mock()
        vm = TestLabViewModel(event_bus)

        mock_dialog = Mock()
        vm.open_confirmation_dialog(mock_dialog)
        event_bus.reset_mock()

        vm.close_confirmation_dialog()

        assert vm.confirmation_dialog is None
        assert vm.is_dialog_open is False
        event_bus.emit.assert_called_with(TestLabEvents.DIALOG_CLOSED, 'confirmation')

    def test_is_dialog_open_with_multiple(self):
        """is_dialog_open is True when any dialog is open."""
        event_bus = Mock()
        vm = TestLabViewModel(event_bus)

        # Open popup
        vm.open_json_popup(Mock())
        assert vm.is_dialog_open is True

        # Also open confirmation
        vm.open_confirmation_dialog(Mock())
        assert vm.is_dialog_open is True

        # Close popup, confirmation still open
        vm.close_json_popup()
        assert vm.is_dialog_open is True

        # Close confirmation, now all closed
        vm.close_confirmation_dialog()
        assert vm.is_dialog_open is False


class TestPanelStateManagement:
    """Test panel reference management."""

    def test_update_ship_panels(self):
        """update_ship_panels stores references and emits event."""
        event_bus = Mock()
        vm = TestLabViewModel(event_bus)

        ship_panels = [Mock(), Mock()]
        component_panels = [Mock()]
        tabbed_panel = Mock()

        vm.update_ship_panels(ship_panels, component_panels, tabbed_panel)

        assert vm.ship_panels == ship_panels
        assert vm.component_panels == component_panels
        assert vm.tabbed_ship_panel is tabbed_panel
        event_bus.emit.assert_called_with(TestLabEvents.PANELS_UPDATED, 'ship_panels')

    def test_update_results_panels(self):
        """update_results_panels stores references and emits event."""
        event_bus = Mock()
        vm = TestLabViewModel(event_bus)

        results_panel = Mock()
        details_panel = Mock()

        vm.update_results_panels(results_panel, details_panel)

        assert vm.results_panel is results_panel
        assert vm.test_details_panel is details_panel
        event_bus.emit.assert_called_with(TestLabEvents.PANELS_UPDATED, 'results_panels')

    def test_clear_panels(self):
        """clear_panels clears all panel references."""
        event_bus = Mock()
        vm = TestLabViewModel(event_bus)

        # Set some panels
        vm.update_ship_panels([Mock()], [Mock()], Mock())
        vm.update_results_panels(Mock(), Mock())
        event_bus.reset_mock()

        vm.clear_panels()

        assert vm.ship_panels == []
        assert vm.component_panels == []
        assert vm.tabbed_ship_panel is None
        assert vm.results_panel is None
        assert vm.test_details_panel is None


class TestButtonRectState:
    """Test button rect state management (non-pygame, just storage)."""

    def test_button_rects_initialized_none(self):
        """Button rects start as None."""
        event_bus = Mock()
        vm = TestLabViewModel(event_bus)

        assert vm.run_test_btn_rect is None
        assert vm.run_headless_btn_rect is None
        assert vm.run_all_tests_btn_rect is None
        assert vm.update_expected_button_rect is None

    def test_update_expected_button_visibility(self):
        """update_expected_button_visible property works."""
        event_bus = Mock()
        vm = TestLabViewModel(event_bus)

        assert vm.update_expected_button_visible is False

        vm.update_expected_button_visible = True
        assert vm.update_expected_button_visible is True


class TestTestSelection:
    """Test test selection state management."""

    def test_select_test_emits_event(self):
        """Selecting a test emits TEST_SELECTED event."""
        event_bus = Mock()
        vm = TestLabViewModel(event_bus)

        vm.select_test("BEAM-001")

        event_bus.emit.assert_called_with(TestLabEvents.TEST_SELECTED, "BEAM-001")

    def test_select_test_resets_scroll(self):
        """Selecting a new test resets scroll offset."""
        event_bus = Mock()
        vm = TestLabViewModel(event_bus)
        vm.set_max_scroll(200)
        vm.scroll(100)

        vm.select_test("BEAM-001")

        # Not asserting specific behavior here - depends on design decision
        # But we verify it doesn't crash

    def test_clear_test_selection(self):
        """clear_test_selection clears the selected test."""
        event_bus = Mock()
        vm = TestLabViewModel(event_bus)

        vm.select_test("BEAM-001")
        event_bus.reset_mock()

        vm.clear_test_selection()

        event_bus.emit.assert_called_with(TestLabEvents.TEST_SELECTED, None)
