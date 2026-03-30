"""
TestLabInputHandler - Input handling for Combat Lab UI.

Handles mouse clicks, scroll events, and hover state updates for TestLabScreen.
Reads state from ViewModel and controller, calls ViewModel/controller methods to mutate state.

PROJ-172: Extracted from screen.py as part of MVVM decomposition.
"""
import pygame
from typing import Optional, Callable, Dict, Any


class TestLabInputHandler:
    """
    Handles input events for Combat Lab UI.

    Delegates to ViewModel for UI state changes and controller for business logic.
    Does NOT import screen.py (one-way dependency).
    """

    def __init__(
        self,
        viewmodel,
        controller,
        registry,
        callbacks: Dict[str, Callable]
    ):
        """
        Initialize the input handler.

        Args:
            viewmodel: TestLabViewModel for UI state
            controller: TestLabUIController for business logic
            registry: TestRegistry for test data
            callbacks: Dict of callback functions:
                - 'on_run': Run selected test visually
                - 'on_run_headless': Run selected test headless
                - 'on_run_all': Run all filtered tests
                - 'on_update_expected': Handle update expected values
                - 'create_ship_panels': Create ship panels for test
                - 'create_results_panel': Create results panel for test
                - 'prompt_custom_seed': Prompt for custom seed
                - 'continue_batch': Continue batch test execution
        """
        self.viewmodel = viewmodel
        self.controller = controller
        self.registry = registry
        self.callbacks = callbacks

        # Layout dimensions (must match renderer)
        self.category_width = 220
        self.test_list_width = 420
        self.header_height = 80

    def handle_event(
        self,
        event: pygame.event.Event,
        filtered_scenarios: Dict[str, Any],
        categories: list,
        executor
    ) -> bool:
        """
        Handle a pygame event.

        Args:
            event: The pygame event
            filtered_scenarios: Currently filtered scenarios dict
            categories: List of category names
            executor: TestLabExecutor for batch state

        Returns:
            True if event was consumed, False otherwise
        """
        # Handle batch test continuation timer
        if event.type == pygame.USEREVENT + 1:
            self.callbacks['continue_batch']()
            return True

        # Dispatch to dialog, panel, and scroll/mouse handlers
        if self._handle_dialog_events(event):
            return True
        if self._handle_panel_events(event):
            return True

        return self._handle_scroll_and_mouse(event, filtered_scenarios, categories, executor)

    def _handle_dialog_events(self, event: pygame.event.Event) -> bool:
        """
        Handle events for confirmation dialog, JSON popup, and battle state viewer.

        Returns:
            True if the event was consumed by a dialog.
        """
        # Handle confirmation dialog first (if open)
        if self.viewmodel.confirmation_dialog and self.viewmodel.confirmation_dialog.is_open:
            self.viewmodel.confirmation_dialog.handle_event(event)
            if not self.viewmodel.confirmation_dialog.is_open:
                self.viewmodel.close_confirmation_dialog()
            return True  # Don't process other events while dialog is open

        # Handle JSON popup (if open)
        if self.viewmodel.json_popup and self.viewmodel.json_popup.is_open:
            self.viewmodel.json_popup.handle_event(event)
            if not self.viewmodel.json_popup.is_open:
                self.viewmodel.close_json_popup()
            return True  # Don't process other events while popup is open

        return False

    def _handle_panel_events(self, event: pygame.event.Event) -> bool:
        """
        Handle events for tabbed ship panel, ship panels, component panels,
        results panel, and test details panel.

        Returns:
            True if the event was consumed by a panel.
        """
        # Handle ship panel events (scrolling)
        if self.viewmodel.tabbed_ship_panel:
            if self.viewmodel.tabbed_ship_panel.handle_event(event):
                return True
        for panel in self.viewmodel.ship_panels:
            if panel.handle_event(event):
                return True

        # Handle component panel events (scrolling, dropdown clicks)
        for panel in self.viewmodel.component_panels:
            if panel.handle_event(event):
                return True

        # Handle results panel events (scrolling, card selection, clear buttons)
        if self.viewmodel.results_panel:
            if self.viewmodel.results_panel.handle_event(event):
                return True

        # Handle test details panel events (scrolling)
        if self.viewmodel.test_details_panel:
            if self.viewmodel.test_details_panel.handle_event(event):
                return True

        return False

    def _handle_scroll_and_mouse(
        self,
        event: pygame.event.Event,
        filtered_scenarios: Dict[str, Any],
        categories: list,
        executor
    ) -> bool:
        """Handle MOUSEWHEEL, MOUSEMOTION, and MOUSEBUTTONDOWN events."""
        # Handle mouse wheel for test list scrolling
        if event.type == pygame.MOUSEWHEEL:
            mx, my = pygame.mouse.get_pos()
            test_list_panel_rect = self.viewmodel.test_list_panel_rect
            if test_list_panel_rect and test_list_panel_rect.collidepoint(mx, my):
                self.viewmodel.scroll(-event.y * 40)  # 40px per scroll tick
                return True

        # Handle mouse motion for hover effects
        if event.type == pygame.MOUSEMOTION:
            mx, my = event.pos
            self._update_hover_state(mx, my, filtered_scenarios, categories)
            return False  # Don't consume motion events

        # Handle mouse clicks
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            return self._handle_click(mx, my, filtered_scenarios, categories, executor)

        return False

    def _update_hover_state(
        self,
        mx: int,
        my: int,
        filtered_scenarios: Dict[str, Any],
        categories: list
    ) -> None:
        """Update hover state for categories and tests."""
        # Reset hover
        self.controller.ui_state.set_category_hover(None)
        self.controller.ui_state.set_test_hover(None)

        # Check "All Tests" hover
        category_x = 20
        category_y = self.header_height + 20
        all_tests_y = category_y + 40
        all_tests_rect = pygame.Rect(category_x, all_tests_y, 200, 40)
        if all_tests_rect.collidepoint(mx, my):
            self.controller.ui_state.set_category_hover("ALL")
            return

        # Check category hover (starts after "All Tests" button)
        category_start_y = all_tests_y + 50
        for i, category in enumerate(categories):
            rect = pygame.Rect(category_x, category_start_y + i * 50, 200, 40)
            if rect.collidepoint(mx, my):
                self.controller.ui_state.set_category_hover(category)
                return

        # Check test hover (accounting for scroll offset)
        test_list_x = 20 + self.category_width + 20
        test_list_y = self.header_height + 20 + 40  # +40 for header offset

        test_list_panel_rect = self.viewmodel.test_list_panel_rect
        # Check if mouse is within the test list panel visible area
        if test_list_panel_rect and test_list_panel_rect.collidepoint(mx, my):
            sorted_test_ids = sorted(filtered_scenarios.keys())
            scroll_offset = self.viewmodel.scroll_offset

            for i, test_id in enumerate(sorted_test_ids):
                # Calculate item position with scroll offset
                item_y = test_list_y + i * 55 - scroll_offset
                rect = pygame.Rect(test_list_x, item_y, 400, 50)
                if (rect.collidepoint(mx, my) and
                    item_y >= test_list_y - 50 and
                    item_y < test_list_y + (test_list_panel_rect.height - 50)):
                    self.controller.ui_state.set_test_hover(test_id)
                    break

    def _handle_click(
        self,
        mx: int,
        my: int,
        filtered_scenarios: Dict[str, Any],
        categories: list,
        executor
    ) -> bool:
        """Handle click events for categories and tests."""
        if self._check_category_clicks(mx, my, categories):
            return True
        if self._check_tag_filter_clicks(mx, my, executor):
            return True
        if self._check_test_item_click(mx, my, filtered_scenarios):
            return True
        if self._check_action_button_clicks(mx, my):
            return True
        if self._check_seed_mode_clicks(mx, my):
            return True
        return False

    def _check_category_clicks(self, mx: int, my: int, categories: list) -> bool:
        """
        Check clicks on the 'All Tests' button and category list.

        Returns:
            True if a click was handled.
        """
        category_x = 20
        category_y = self.header_height + 20

        # Check header offset (40px for "CATEGORIES" header)
        all_tests_y = category_y + 40
        all_tests_rect = pygame.Rect(category_x, all_tests_y, 200, 40)
        if all_tests_rect.collidepoint(mx, my):
            self.controller.ui_state.select_category(None)
            self.controller.ui_state.select_test(None)
            return True

        # Check category click (starts after "All Tests" button)
        category_start_y = all_tests_y + 50
        for i, category in enumerate(categories):
            rect = pygame.Rect(category_x, category_start_y + i * 50, 200, 40)
            if rect.collidepoint(mx, my):
                selected = self.controller.ui_state.get_selected_category()
                # Toggle category selection
                if selected == category:
                    self.controller.ui_state.select_category(None)  # Deselect - show all
                else:
                    self.controller.ui_state.select_category(category)
                self.controller.ui_state.select_test(None)  # Clear test selection
                return True

        return False

    def _check_tag_filter_clicks(self, mx: int, my: int, executor) -> bool:
        """
        Check clicks on tag filter buttons, clear button, and run all tests button.

        Returns:
            True if a click was handled.
        """
        # Check tag filter clicks
        # Left-click: cycle through states (neutral -> include -> exclude -> neutral)
        for tag, rect in self.viewmodel.tag_filter_rects.items():
            if rect.collidepoint(mx, my):
                self.controller.ui_state.cycle_tag_state(tag)
                return True

        # Check tag filter clear button
        tag_clear_rect = self.viewmodel.tag_clear_rect
        if tag_clear_rect and tag_clear_rect.collidepoint(mx, my):
            self.controller.ui_state.clear_tag_filters()
            return True

        # Check "Run Tests" button click (in test list panel)
        run_all_rect = self.viewmodel.run_all_tests_btn_rect
        if run_all_rect and run_all_rect.collidepoint(mx, my):
            if not executor.batch_running:
                self.callbacks['on_run_all']()
            return True

        return False

    def _check_test_item_click(
        self, mx: int, my: int, filtered_scenarios: Dict[str, Any]
    ) -> bool:
        """
        Check clicks on test items in the scrollable test list.

        Returns:
            True if a click was handled.
        """
        # Check test click (accounting for scroll offset)
        test_list_x = 20 + self.category_width + 20
        test_list_y = self.header_height + 20 + 40  # +40 for header offset

        test_list_panel_rect = self.viewmodel.test_list_panel_rect
        # Only check test clicks if within the test list panel
        if test_list_panel_rect and test_list_panel_rect.collidepoint(mx, my):
            sorted_test_ids = sorted(filtered_scenarios.keys())
            scroll_offset = self.viewmodel.scroll_offset

            for i, test_id in enumerate(sorted_test_ids):
                # Calculate item position with scroll offset
                item_y = test_list_y + i * 55 - scroll_offset
                rect = pygame.Rect(test_list_x, item_y, 400, 50)
                # Check if item is visible and clicked
                if (rect.collidepoint(mx, my) and
                    item_y >= test_list_y - 50 and
                    item_y < test_list_y + (test_list_panel_rect.height - 50)):
                    self.controller.ui_state.select_test(test_id)
                    # Create ship panels for the selected test
                    self.callbacks['create_ship_panels'](test_id)
                    # Create results panel for the selected test
                    self.callbacks['create_results_panel'](test_id)
                    return True

        return False

    def _check_action_button_clicks(self, mx: int, my: int) -> bool:
        """
        Check clicks on Run Test, Run Headless, and Update Expected buttons.

        Returns:
            True if a click was handled.
        """
        # Check Run Test button click (in metadata panel)
        run_test_rect = self.viewmodel.run_test_btn_rect
        if run_test_rect and run_test_rect.collidepoint(mx, my):
            self.callbacks['on_run']()
            return True

        # Check Run Headless button click (in metadata panel)
        run_headless_rect = self.viewmodel.run_headless_btn_rect
        if run_headless_rect and run_headless_rect.collidepoint(mx, my):
            self.callbacks['on_run_headless']()
            return True

        # Check Visual Baseline button click (ComparisonScenario only)
        run_baseline_rect = self.viewmodel.run_baseline_btn_rect
        if run_baseline_rect and run_baseline_rect.collidepoint(mx, my):
            self.callbacks['on_run_visual_baseline']()
            return True

        # Check "Update Expected Values" button click
        if self.viewmodel.update_expected_button_visible:
            update_rect = self.viewmodel.update_expected_button_rect
            if update_rect and update_rect.collidepoint(mx, my):
                self.callbacks['on_update_expected']()
                return True

        return False

    def _check_seed_mode_clicks(self, mx: int, my: int) -> bool:
        """
        Check clicks on seed mode buttons and seed input area.

        Returns:
            True if a click was handled.
        """
        # Check seed mode button clicks
        for mode_id, rect in self.viewmodel.seed_mode_rects.items():
            if rect.collidepoint(mx, my):
                self.controller.ui_state.set_seed_mode(mode_id)
                return True

        # Check seed input click (for custom mode)
        seed_input_rect = self.viewmodel.seed_input_rect
        if seed_input_rect and seed_input_rect.collidepoint(mx, my):
            self.callbacks['prompt_custom_seed']()
            return True

        return False
