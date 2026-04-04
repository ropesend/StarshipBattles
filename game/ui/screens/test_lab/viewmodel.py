"""
TestLabViewModel - ViewModel for Combat Lab UI state management.

Manages all mutable UI state for the TestLabScreen, emitting events when state changes.
Views subscribe to events and update themselves accordingly.

This ViewModel does NOT import pygame - it's purely for state management.

PROJ-172: Extracted from screen.py as part of MVVM decomposition.
"""
from typing import List, Optional, Any


class TestLabEvents:
    """Event type constants for TestLabViewModel."""

    SCROLL_CHANGED = "test_lab.scroll_changed"
    DIALOG_OPENED = "test_lab.dialog_opened"
    DIALOG_CLOSED = "test_lab.dialog_closed"
    PANELS_UPDATED = "test_lab.panels_updated"
    TEST_SELECTED = "test_lab.test_selected"


class TestLabViewModel:
    """
    Central ViewModel for Combat Lab UI state.

    Holds all mutable UI state and emits events via EventBus when state changes.
    Views subscribe to events and update themselves accordingly.

    Events emitted:
        - SCROLL_CHANGED: When test list scroll position changes
        - DIALOG_OPENED: When a dialog (JSON popup, confirmation) opens
        - DIALOG_CLOSED: When a dialog closes
        - PANELS_UPDATED: When ship/component/results panels change
        - TEST_SELECTED: When a test is selected/deselected

    Note: This ViewModel does NOT manage business logic state like selected_category,
    selected_test_id, tag filters - those are managed by TestLabUIController's ui_state.
    This ViewModel only manages UI-specific state like scroll positions, dialog refs, etc.
    """

    def __init__(self, event_bus):
        """
        Initialize the TestLabViewModel.

        Args:
            event_bus: EventBus instance for emitting state change notifications
        """
        self.event_bus = event_bus

        # Scroll state for test list
        self._scroll_offset: int = 0
        self._max_scroll: int = 0

        # Dialog state
        self._json_popup: Optional[Any] = None
        self._confirmation_dialog: Optional[Any] = None

        # Panel references (for drawing/event handling)
        self._ship_panels: List[Any] = []
        self._component_panels: List[Any] = []
        self._tabbed_ship_panel: Optional[Any] = None
        self._results_panel: Optional[Any] = None
        self._test_details_panel: Optional[Any] = None

        # Button rects (set by renderer, used by input handler)
        self._run_test_btn_rect: Optional[Any] = None
        self._run_headless_btn_rect: Optional[Any] = None
        self._run_baseline_btn_rect: Optional[Any] = None
        self._run_all_tests_btn_rect: Optional[Any] = None
        self._update_expected_button_rect: Optional[Any] = None
        self._update_expected_button_visible: bool = False

        # Category tree rects (set by renderer, used by input handler)
        self.group_header_rects: dict = {}  # group_name -> pygame.Rect
        self.category_rects: dict = {}      # category_name -> pygame.Rect

        # Tag filter rects (set by renderer)
        self._tag_filter_rects: dict = {}
        self._tag_clear_rect: Optional[Any] = None

        # Seed control rects (set by renderer)
        self._seed_mode_rects: dict = {}
        self._seed_input_rect: Optional[Any] = None

        # Test list panel rect (for scroll detection)
        self._test_list_panel_rect: Optional[Any] = None

    # ─────────────────────────────────────────────────────────────────
    # Scroll State
    # ─────────────────────────────────────────────────────────────────

    @property
    def scroll_offset(self) -> int:
        """Current scroll offset for test list panel."""
        return self._scroll_offset

    @property
    def max_scroll(self) -> int:
        """Maximum scroll offset for test list panel."""
        return self._max_scroll

    def set_max_scroll(self, value: int) -> None:
        """
        Set the maximum scroll value.

        Clamps current offset if it exceeds new max.

        Args:
            value: New maximum scroll value
        """
        self._max_scroll = max(0, value)
        # Clamp current offset if needed
        if self._scroll_offset > self._max_scroll:
            self._scroll_offset = self._max_scroll

    def scroll(self, delta: int) -> None:
        """
        Adjust scroll offset by delta, clamping to valid range.

        Args:
            delta: Amount to scroll (positive = down, negative = up)
        """
        new_offset = self._scroll_offset + delta
        new_offset = max(0, min(new_offset, self._max_scroll))

        if new_offset != self._scroll_offset:
            self._scroll_offset = new_offset
            self.event_bus.emit(
                TestLabEvents.SCROLL_CHANGED,
                {'offset': self._scroll_offset, 'max_scroll': self._max_scroll}
            )

    def reset_scroll(self) -> None:
        """Reset scroll offset to 0."""
        if self._scroll_offset != 0:
            self._scroll_offset = 0
            self.event_bus.emit(
                TestLabEvents.SCROLL_CHANGED,
                {'offset': 0, 'max_scroll': self._max_scroll}
            )

    # ─────────────────────────────────────────────────────────────────
    # Dialog State
    # ─────────────────────────────────────────────────────────────────

    @property
    def json_popup(self) -> Optional[Any]:
        """Current JSON popup dialog reference, or None."""
        return self._json_popup

    @property
    def confirmation_dialog(self) -> Optional[Any]:
        """Current confirmation dialog reference, or None."""
        return self._confirmation_dialog

    @property
    def is_dialog_open(self) -> bool:
        """Whether any dialog is currently open."""
        return self._json_popup is not None or self._confirmation_dialog is not None

    def open_json_popup(self, popup) -> None:
        """
        Open a JSON popup dialog.

        Args:
            popup: The popup dialog instance
        """
        self._json_popup = popup
        self.event_bus.emit(TestLabEvents.DIALOG_OPENED, 'json_popup')

    def close_json_popup(self) -> None:
        """Close the JSON popup dialog."""
        if self._json_popup is not None:
            self._json_popup = None
            self.event_bus.emit(TestLabEvents.DIALOG_CLOSED, 'json_popup')

    def open_confirmation_dialog(self, dialog) -> None:
        """
        Open a confirmation dialog.

        Args:
            dialog: The confirmation dialog instance
        """
        self._confirmation_dialog = dialog
        self.event_bus.emit(TestLabEvents.DIALOG_OPENED, 'confirmation')

    def close_confirmation_dialog(self) -> None:
        """Close the confirmation dialog."""
        if self._confirmation_dialog is not None:
            self._confirmation_dialog = None
            self.event_bus.emit(TestLabEvents.DIALOG_CLOSED, 'confirmation')

    # ─────────────────────────────────────────────────────────────────
    # Panel State
    # ─────────────────────────────────────────────────────────────────

    @property
    def ship_panels(self) -> List[Any]:
        """List of ship JSON panels."""
        return self._ship_panels

    @property
    def component_panels(self) -> List[Any]:
        """List of component JSON panels."""
        return self._component_panels

    @property
    def tabbed_ship_panel(self) -> Optional[Any]:
        """Tabbed ship panel (for 3+ ships), or None."""
        return self._tabbed_ship_panel

    @property
    def results_panel(self) -> Optional[Any]:
        """Test results panel reference, or None."""
        return self._results_panel

    @property
    def test_details_panel(self) -> Optional[Any]:
        """Test run details panel reference, or None."""
        return self._test_details_panel

    def update_ship_panels(
        self,
        ship_panels: List[Any],
        component_panels: List[Any],
        tabbed_panel: Optional[Any]
    ) -> None:
        """
        Update ship and component panel references.

        Args:
            ship_panels: List of ship JSON panels
            component_panels: List of component JSON panels
            tabbed_panel: Tabbed ship panel (or None if <3 ships)
        """
        self._ship_panels = ship_panels
        self._component_panels = component_panels
        self._tabbed_ship_panel = tabbed_panel
        self.event_bus.emit(TestLabEvents.PANELS_UPDATED, 'ship_panels')

    def update_results_panels(
        self,
        results_panel: Optional[Any],
        details_panel: Optional[Any]
    ) -> None:
        """
        Update results panel references.

        Args:
            results_panel: Test results panel
            details_panel: Test run details panel
        """
        self._results_panel = results_panel
        self._test_details_panel = details_panel
        self.event_bus.emit(TestLabEvents.PANELS_UPDATED, 'results_panels')

    def clear_panels(self) -> None:
        """Clear all panel references."""
        self._ship_panels = []
        self._component_panels = []
        self._tabbed_ship_panel = None
        self._results_panel = None
        self._test_details_panel = None

    # ─────────────────────────────────────────────────────────────────
    # Button Rect State (set by renderer, read by input handler)
    # ─────────────────────────────────────────────────────────────────

    @property
    def run_test_btn_rect(self) -> Optional[Any]:
        """Rect for Visual Run button."""
        return self._run_test_btn_rect

    @run_test_btn_rect.setter
    def run_test_btn_rect(self, value) -> None:
        self._run_test_btn_rect = value

    @property
    def run_headless_btn_rect(self) -> Optional[Any]:
        """Rect for Headless Run button."""
        return self._run_headless_btn_rect

    @run_headless_btn_rect.setter
    def run_headless_btn_rect(self, value) -> None:
        self._run_headless_btn_rect = value

    @property
    def run_baseline_btn_rect(self) -> Optional[Any]:
        """Rect for Visual Baseline button (ComparisonScenario only)."""
        return self._run_baseline_btn_rect

    @run_baseline_btn_rect.setter
    def run_baseline_btn_rect(self, value) -> None:
        self._run_baseline_btn_rect = value

    @property
    def run_all_tests_btn_rect(self) -> Optional[Any]:
        """Rect for Run All Tests button."""
        return self._run_all_tests_btn_rect

    @run_all_tests_btn_rect.setter
    def run_all_tests_btn_rect(self, value) -> None:
        self._run_all_tests_btn_rect = value

    @property
    def update_expected_button_rect(self) -> Optional[Any]:
        """Rect for Update Expected Values button."""
        return self._update_expected_button_rect

    @update_expected_button_rect.setter
    def update_expected_button_rect(self, value) -> None:
        self._update_expected_button_rect = value

    @property
    def update_expected_button_visible(self) -> bool:
        """Whether Update Expected Values button is visible."""
        return self._update_expected_button_visible

    @update_expected_button_visible.setter
    def update_expected_button_visible(self, value: bool) -> None:
        self._update_expected_button_visible = value

    @property
    def tag_filter_rects(self) -> dict:
        """Dict of tag -> rect for tag filter buttons."""
        return self._tag_filter_rects

    @tag_filter_rects.setter
    def tag_filter_rects(self, value: dict) -> None:
        self._tag_filter_rects = value

    @property
    def tag_clear_rect(self) -> Optional[Any]:
        """Rect for tag clear button."""
        return self._tag_clear_rect

    @tag_clear_rect.setter
    def tag_clear_rect(self, value) -> None:
        self._tag_clear_rect = value

    @property
    def seed_mode_rects(self) -> dict:
        """Dict of mode_id -> rect for seed mode buttons."""
        return self._seed_mode_rects

    @seed_mode_rects.setter
    def seed_mode_rects(self, value: dict) -> None:
        self._seed_mode_rects = value

    @property
    def seed_input_rect(self) -> Optional[Any]:
        """Rect for seed input area."""
        return self._seed_input_rect

    @seed_input_rect.setter
    def seed_input_rect(self, value) -> None:
        self._seed_input_rect = value

    @property
    def test_list_panel_rect(self) -> Optional[Any]:
        """Rect for test list panel (scroll detection)."""
        return self._test_list_panel_rect

    @test_list_panel_rect.setter
    def test_list_panel_rect(self, value) -> None:
        self._test_list_panel_rect = value

    # ─────────────────────────────────────────────────────────────────
    # Test Selection (coordinating with panels)
    # ─────────────────────────────────────────────────────────────────

    def select_test(self, test_id: str) -> None:
        """
        Handle test selection - resets scroll and emits event.

        Note: The actual selected_test_id is stored in TestLabUIController.ui_state.
        This method is called to notify the ViewModel that selection changed.

        Args:
            test_id: The selected test ID
        """
        # Don't reset scroll here - let the screen handle scroll behavior
        self.event_bus.emit(TestLabEvents.TEST_SELECTED, test_id)

    def clear_test_selection(self) -> None:
        """Clear test selection notification."""
        self.event_bus.emit(TestLabEvents.TEST_SELECTED, None)
