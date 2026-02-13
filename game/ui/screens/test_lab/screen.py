"""
TestLabScreen - Combat Lab UI main screen.

This module contains the main TestLabScreen class which orchestrates
the Combat Lab interface for viewing and running test scenarios.
"""
import pygame
import pygame_gui
import os
import sys

from game.ui.colors import FONT_MAIN
from game.core.config import DisplayConfig
WIDTH, HEIGHT = DisplayConfig.DEFAULT_WIDTH, DisplayConfig.DEFAULT_HEIGHT
from game.core.json_utils import load_json
from test_framework.registry import TestRegistry
from test_framework.test_history import TestHistory
from simulation_tests.logging_config import get_logger

# Intra-package imports
from .dialogs import JSONPopup, ConfirmationDialog
from .json_viewer import ScrollableJSONViewer
from .test_run_card import TestRunCard
from .data_extractor import TestLabDataExtractor, get_test_data_dir
from .validation_manager import TestLabValidationManager
from .panel_manager import TestLabPanelManager
from .test_executor import TestLabExecutor

logger = get_logger(__name__)


class TestLabScreen:
    """
    Combat Lab UI - Enhanced with TestRegistry and rich metadata display.

    Implements IScene protocol for standardized scene handling.

    Layout:
    - Left: Category sidebar (220px wide)
    - Center: Test list (420px wide)
    - Right: Metadata panel (540px wide)
    """

    # Color scheme
    BG_COLOR = (20, 20, 25)
    PANEL_BG = (25, 25, 30)
    BORDER_COLOR = (80, 80, 90)
    TEXT_COLOR = (220, 220, 220)
    HEADER_COLOR = (100, 200, 255)
    SELECTED_COLOR = (0, 100, 200)
    HOVER_COLOR = (150, 150, 150)
    CATEGORY_BG = (35, 35, 40)

    def __init__(self, game, scene_callback=None):
        """Initialize test lab screen.

        Args:
            game: Game instance providing screen, battle_scene, and state management.
            scene_callback: Callback function for scene transitions.
                           Called with (action, **kwargs) where action is:
                           - "start_test_battle": Start visual test battle with scenario kwarg
                           - "return_to_menu": Return to main menu
        """
        self.game = game
        self.scene_callback = scene_callback
        self.screen_width = game.screen.get_width() if hasattr(game, 'screen') else WIDTH
        self.screen_height = game.screen.get_height() if hasattr(game, 'screen') else HEIGHT

        # pygame_gui UIManager for buttons
        self.ui_manager = pygame_gui.UIManager((self.screen_width, self.screen_height))
        self._button_callbacks = {}  # Maps UIButton -> callback function

        # Fonts
        self.title_font = pygame.font.SysFont(FONT_MAIN, 48)
        self.header_font = pygame.font.SysFont(FONT_MAIN, 24)
        self.body_font = pygame.font.SysFont(FONT_MAIN, 18)
        self.small_font = pygame.font.SysFont(FONT_MAIN, 14)

        # Initialize controller (handles all business logic)
        from test_framework.services.test_lab_controller import TestLabUIController
        self.registry = TestRegistry()
        self.test_history = TestHistory()
        self.controller = TestLabUIController(game, self.registry, self.test_history)

        # Data extraction helper (ships, components from test scenarios)
        self._data_extractor = TestLabDataExtractor(self.registry)

        # Validation manager (static validation, expected value updates)
        self._validation_manager = TestLabValidationManager(
            self.registry, self._data_extractor, lambda: self.all_scenarios
        )

        # Panel manager (factory for ship, component, results panels)
        layout = {
            'header_height': 80,
            'category_width': 220,
            'test_list_width': 420,
            'metadata_width': 540,
        }
        self._panel_manager = TestLabPanelManager(
            self._data_extractor, self.test_history, layout
        )

        # Test executor (handles visual, headless, and batch test runs)
        self._executor = TestLabExecutor(
            registry=self.registry,
            test_history=self.test_history,
            controller=self.controller,
            render_progress=self._render_progress,
            draw_and_flip=self._draw_and_flip,
            get_engine=self._get_engine,
            ensure_engine=self._ensure_engine,
            switch_to_battle=self._switch_to_battle,
            output_log=self.output_log,
        )

        # Get categories for sidebar
        self.categories = self.registry.get_categories()

        # Layout dimensions
        self.category_width = 220
        self.test_list_width = 420
        self.metadata_width = 540
        self.header_height = 80

        # Scrolling state for test list panel
        self.test_list_scroll_offset = 0
        self.test_list_max_scroll = 0
        self.test_list_panel_rect = None  # Set in _draw_test_list for scroll event handling

        # Batch test execution state (delegated to executor, but need btn rect)
        self.run_all_tests_btn_rect = None

        # UI components
        self.json_popup = None  # For displaying JSON data
        self.confirmation_dialog = None  # For confirming metadata updates
        self.ship_panels = []  # Ship JSON panels
        self.tabbed_ship_panel = None  # Tabbed ship panel (for 3+ ships)
        self.component_panels = []  # Component JSON panels
        self.results_panel = None  # Test run history panel
        self.test_details_panel = None  # Test run details panel

        # Update Expected Values button state
        self.update_expected_button_rect = None
        self.update_expected_button_visible = False

        # Battle state viewer (for viewing initial/final JSON states)
        from game.ui.screens.battle_state_viewer import BattleStateViewer
        self.battle_state_viewer = BattleStateViewer(WIDTH, HEIGHT)

        self._create_ui()


    @property
    def selected_category(self):
        return self.controller.ui_state.get_selected_category()

    @selected_category.setter
    def selected_category(self, value):
        self.controller.ui_state.select_category(value)

    @property
    def selected_test_id(self):
        return self.controller.ui_state.get_selected_test_id()

    @selected_test_id.setter
    def selected_test_id(self, value):
        self.controller.ui_state.select_test(value)

    @property
    def category_hover(self):
        return self.controller.ui_state.get_category_hover()

    @category_hover.setter
    def category_hover(self, value):
        self.controller.ui_state.set_category_hover(value)

    @property
    def test_hover(self):
        return self.controller.ui_state.get_test_hover()

    @test_hover.setter
    def test_hover(self, value):
        self.controller.ui_state.set_test_hover(value)

    @property
    def headless_running(self):
        return self.controller.ui_state.is_headless_running()

    @headless_running.setter
    def headless_running(self, value):
        self.controller.ui_state.set_headless_running(value)

    @property
    def output_log(self):
        return self.controller.output_log

    @property
    def all_scenarios(self):
        return self.controller.all_scenarios

    @property
    def batch_running(self):
        """Delegate batch_running to executor."""
        return self._executor.batch_running

    @property
    def batch_current_index(self):
        """Delegate batch_current_index to executor."""
        return self._executor.batch_current_index

    @property
    def batch_total(self):
        """Delegate batch_total to executor."""
        return self._executor.batch_total

    def _extract_ships_from_scenario(self, test_id):
        """
        Extract ship information from test scenario metadata.

        Delegates to TestLabDataExtractor.extract_ships().
        """
        return self._data_extractor.extract_ships(test_id)

    def _validate_all_scenarios(self):
        """
        Validate all test scenarios against component/ship data files.

        Delegates to TestLabValidationManager.validate_all().
        """
        self._validation_manager.validate_all()

    def _build_validation_context_from_files(self, test_id, metadata):
        """
        Build validation context from ship and component JSON files.

        Delegates to TestLabValidationManager.build_context_from_files().
        """
        return self._validation_manager.build_context_from_files(test_id, metadata)

    def _load_component_data(self, component_id):
        """
        Load component JSON from components.json by ID.

        Delegates to TestLabDataExtractor.load_component().
        """
        return self._data_extractor.load_component(component_id)

    @property
    def components_cache(self):
        """Access component cache from data extractor.

        Provides public access to the components cache for backward compatibility.
        """
        return self._data_extractor.get_components_cache()

    def _handle_update_expected_values(self):
        """
        Handle click on Update Expected Values button.

        Delegates to TestLabValidationManager.handle_update_expected_values().
        """
        self.confirmation_dialog = self._validation_manager.handle_update_expected_values(
            self.selected_test_id, self.ui_manager,
            self.game.screen.get_width(), self.game.screen.get_height()
        )

    def _apply_metadata_updates(self, changes):
        """
        Apply metadata updates to the test scenario file.

        Delegates to TestLabValidationManager.apply_metadata_updates().
        """
        self._validation_manager.apply_metadata_updates(changes, self.selected_test_id)

    def _create_ship_panels(self, test_id):
        """
        Create ship panels and component panels for the selected test.

        Uses TabbedShipPanel when there are 3+ ships, individual ShipPanels otherwise.

        Args:
            test_id: Test ID (e.g., "BEAM360-001")
        """
        panels = self._panel_manager.create_ship_panels(test_id, self)
        self.ship_panels, self.component_panels, self.tabbed_ship_panel = panels

    def _create_results_panel(self, test_id):
        """
        Create results panel for selected test.

        Positions panel to the right of ship panels, using remaining 4K display space.

        Args:
            test_id: Test ID (e.g., "BEAM360-001")
        """
        callbacks = {
            'on_view_battle_states': self._on_view_battle_states,
            'on_use_seed': self._on_use_seed_from_run,
            'on_copy_results': self._on_copy_results,
        }
        panels = self._panel_manager.create_results_panel(
            test_id, self.ship_panels, self.tabbed_ship_panel, callbacks
        )
        self.results_panel, self.test_details_panel = panels

    def _create_ui(self):
        """Create UI buttons."""
        # Delegate button creation to panel manager
        self.btn_back, callbacks = self._panel_manager.create_ui_buttons(
            self.ui_manager, self._on_back
        )
        self._button_callbacks.update(callbacks)

        # Run Test and Run Headless buttons are now drawn in _draw_metadata_panel()
        self.run_test_btn_rect = None
        self.run_headless_btn_rect = None

        # Tag filter button rects (populated in _draw_tag_filters)
        self.tag_filter_rects = {}  # tag -> pygame.Rect
        self.tag_exclude_rects = {}  # tag -> pygame.Rect for exclude buttons

        # Seed control rects (populated in _draw_seed_controls)
        self.seed_mode_rects = {}  # mode -> pygame.Rect
        self.seed_input_rect = None
        self.copy_seed_rect = None

    def _get_filtered_scenarios(self):
        """Get scenarios filtered by selected category and tags."""
        # Start with category filter
        if self.selected_category is None:
            scenarios = self.all_scenarios
        else:
            scenarios = self.registry.get_by_category(self.selected_category)

        # Apply tag filters
        active_tags = self.controller.ui_state.get_active_tag_filters()
        excluded_tags = self.controller.ui_state.get_excluded_tags()

        if not active_tags and not excluded_tags:
            return scenarios

        filtered = {}
        for test_id, info in scenarios.items():
            metadata = info['metadata']
            test_tags = set(metadata.tags)

            # Check excluded tags first (any excluded tag means skip)
            if excluded_tags and any(tag in test_tags for tag in excluded_tags):
                continue

            # Check active tags (all must be present if any are set)
            if active_tags and not all(tag in test_tags for tag in active_tags):
                continue

            filtered[test_id] = info

        return filtered

    def reset_selection(self):
        """Clear test selection (called when returning from battle)."""
        # Store results from completed visual test before clearing
        if self.selected_test_id and hasattr(self.game.battle_scene, 'test_scenario'):
            scenario = self.game.battle_scene.test_scenario
            # Only capture results if test actually completed (not if user exited early)
            if scenario and self.game.battle_scene.test_completed:
                # Ensure results dict exists
                if not hasattr(scenario, 'results') or scenario.results is None:
                    scenario.results = {}

                # Ensure essential fields are populated
                if 'passed' not in scenario.results:
                    scenario.results['passed'] = getattr(scenario, 'passed', False)
                if 'ticks_run' not in scenario.results:
                    scenario.results['ticks_run'] = self.game.battle_scene.test_tick_count

                logger.debug(f"Storing visual test results for {self.selected_test_id}, keys: {list(scenario.results.keys())}")
                self.registry.update_last_run_results(self.selected_test_id, scenario.results)

                # Add to persistent test history
                self.test_history.add_run(self.selected_test_id, scenario.results)

                # Refresh results panel if it exists
                if self.results_panel:
                    self.results_panel.set_test(self.selected_test_id)
            else:
                logger.debug(f"No results to store - scenario={scenario}, test_completed={self.game.battle_scene.test_completed if scenario else 'N/A'}")

        # Clear battle scene test state
        if hasattr(self.game.battle_scene, 'test_completed'):
            self.game.battle_scene.test_completed = False
        if hasattr(self.game.battle_scene, 'test_scenario'):
            self.game.battle_scene.test_scenario = None

        self.selected_test_id = None
        logger.debug(f"Test selection cleared")

    def _on_back(self):
        """Return to main menu."""
        from game.core.constants import GameState
        self.game.state = GameState.MENU
        if hasattr(self.game, 'menu_screen') and hasattr(self.game.menu_screen, 'create_particles'):
            self.game.menu_screen.create_particles()

    # --- Executor callback helpers ---

    def _render_progress(self, title, subtitle, detail):
        """Render a progress overlay for headless test execution."""
        overlay = pygame.Surface((600, 200))
        overlay.fill((40, 40, 45))
        pygame.draw.rect(overlay, (100, 100, 120), overlay.get_rect(), 3)

        title_text = self.header_font.render(title, True, (255, 255, 255))
        sub_text = self.body_font.render(subtitle, True, (200, 200, 200))
        detail_text = self.small_font.render(detail, True, (150, 150, 150))

        overlay.blit(title_text, (300 - title_text.get_width()//2, 50))
        overlay.blit(sub_text, (300 - sub_text.get_width()//2, 90))
        overlay.blit(detail_text, (300 - detail_text.get_width()//2, 130))

        screen_center_x = self.game.screen.get_width() // 2
        screen_center_y = self.game.screen.get_height() // 2
        self.game.screen.blit(overlay, (screen_center_x - 300, screen_center_y - 100))

    def _draw_and_flip(self):
        """Draw current screen state with progress overlay and flip display."""
        self.game.screen.fill((20, 20, 25))
        self.draw(self.game.screen)
        pygame.display.flip()

    def _get_engine(self):
        """Get the battle engine from battle scene."""
        return self.game.battle_scene.engine

    def _ensure_engine(self):
        """Ensure battle engine exists (create if needed)."""
        if self.game.battle_scene.engine is None:
            # PROJ-126: Use battle_scene's AI factory
            self.game.battle_scene._battle_service.create_battle(
                ai_factory=self.game.battle_scene._ai_factory
            )

    def _switch_to_battle(self, scenario):
        """Configure battle scene for visual test mode and switch to battle state."""
        engine = self.game.battle_scene.engine

        # Clear and setup engine
        engine.start([], [])
        scenario.setup(engine)

        # Configure battle scene for test mode
        logger.debug(f" Configuring battle scene for test mode")
        logger.debug(f" BEFORE: test_mode={self.game.battle_scene.test_mode}")
        self.game.battle_scene.headless_mode = False
        self.game.battle_scene.sim_paused = True  # Start paused
        self.game.battle_scene.test_mode = True   # Enable test mode
        self.game.battle_scene.test_scenario = scenario  # Pass scenario for update() calls
        self.game.battle_scene.test_tick_count = 0  # Reset tick counter
        self.game.battle_scene.test_completed = False  # Reset completed flag
        logger.debug(f" AFTER: test_mode={self.game.battle_scene.test_mode}")
        logger.debug(f" Battle scene configured (paused=True, test_mode=True, scenario={scenario.metadata.test_id})")

        # Fit camera to ships
        ships = engine.ships
        logger.debug(f" Ships in engine: {len(ships) if ships else 0}")
        if ships:
            for i, ship in enumerate(ships):
                logger.debug(f"   Ship {i}: {ship.name if hasattr(ship, 'name') else 'unknown'} at {ship.position}, alive={ship.is_alive}")
            self.game.battle_scene.camera.fit_objects(ships)
            # Also sync target_zoom to prevent animation overriding the fit
            self.game.battle_scene.camera.target_zoom = self.game.battle_scene.camera.zoom
            logger.debug(f" Camera fitted: pos={self.game.battle_scene.camera.position}, zoom={self.game.battle_scene.camera.zoom}")
        else:
            logger.warning(" No ships in engine after scenario setup!")

        # Switch to battle state
        from game.core.constants import GameState
        logger.debug(f" Switching to BATTLE state")
        self.game.state = GameState.BATTLE

    def _on_view_battle_states(self, run_record, run_number):
        """
        Open the battle state viewer for a test run.

        Args:
            run_record: TestRunRecord with state file paths
            run_number: Display number for the run
        """
        from test_framework.battle_state_capture import load_battle_state_json

        initial_json = None
        final_json = None

        # Load initial state JSON
        if run_record.initial_state_file:
            initial_json = load_battle_state_json(run_record.initial_state_file)
            if initial_json is None:
                logger.warning(f"Could not load initial state from: {run_record.initial_state_file}")

        # Load final state JSON
        if run_record.final_state_file:
            final_json = load_battle_state_json(run_record.final_state_file)
            if final_json is None:
                logger.warning(f"Could not load final state from: {run_record.final_state_file}")

        if initial_json or final_json:
            self.battle_state_viewer.show(
                initial_json=initial_json,
                final_json=final_json,
                test_id=self.selected_test_id,
                run_number=run_number
            )
        else:
            self.output_log.append("ERROR: Could not load battle state files")

    def _on_use_seed_from_run(self, seed):
        """
        Copy the seed from a test run to the custom seed control.

        Args:
            seed: The seed value to use
        """
        self.controller.ui_state.set_custom_seed(seed)
        self.output_log.append(f"Seed set to: {seed}")

    def _on_copy_results(self, run_record, run_number):
        """
        Copy test results to clipboard.

        Args:
            run_record: TestRunRecord with test results
            run_number: Display number for the run
        """
        # Build a text representation of the test results
        lines = []
        lines.append(f"Test: {self.selected_test_id}")
        lines.append(f"Run #{run_number} - {run_record.get_formatted_timestamp()}")
        lines.append(f"Status: {'PASSED' if run_record.passed else 'FAILED'}")
        if run_record.seed is not None:
            lines.append(f"Seed: {run_record.seed}")
        lines.append("")

        # Metrics
        lines.append("=== Test Metrics ===")
        for key, value in run_record.metrics.items():
            if key not in ['validation_results', 'validation_summary']:
                if isinstance(value, float):
                    value_str = f"{value:.4f}"
                else:
                    value_str = str(value)
                display_key = key.replace('_', ' ').title()
                lines.append(f"  {display_key}: {value_str}")
        lines.append("")

        # Validation Results
        if run_record.validation_results:
            lines.append("=== Validation Results ===")
            for vr in run_record.validation_results:
                status = vr['status']
                name = vr['name']
                expected = vr.get('expected')
                actual = vr.get('actual')
                p_value = vr.get('p_value')

                symbol = "V" if status == 'PASS' else "X"
                lines.append(f"{symbol} {name}: {status}")
                if expected is not None:
                    lines.append(f"    Expected: {expected}")
                if actual is not None:
                    lines.append(f"    Actual: {actual}")
                if p_value is not None:
                    lines.append(f"    p-value: {p_value:.6f}")
                lines.append("")

        # Copy to clipboard using pygame's scrap module
        try:
            result_text = "\n".join(lines)
            pygame.scrap.init()
            pygame.scrap.put(pygame.SCRAP_TEXT, result_text.encode('utf-8'))
            self.output_log.append("Test results copied to clipboard")
        except pygame.error as e:
            self.output_log.append(f"Failed to copy to clipboard: {e}")

    def _on_run(self):
        """Run the selected test scenario visually in Combat Lab."""
        self._executor.run_visual(self.selected_test_id)

    def _on_run_headless(self):
        """Run the selected test scenario in headless mode (fast, no visuals)."""
        self.headless_running = True
        self._executor.run_headless(self.selected_test_id)
        self.headless_running = False
        # Refresh results panel if it exists
        if self.results_panel:
            self.results_panel.set_test(self.selected_test_id)

    def _on_run_all_tests(self):
        """Run all visible tests headlessly in sequence."""
        self._executor.run_all(self._get_filtered_scenarios())

    def _run_next_batch_test(self):
        """Run the next test in the batch sequence."""
        self._executor.run_next_batch()

    def _continue_batch_test(self):
        """Continue batch execution (called from event handler)."""
        self._executor.continue_batch()

    def handle_event(self, event):
        """Handle a single pygame event (IScene protocol)."""
        self.handle_input([event])

    def handle_resize(self, width: int, height: int):
        """Handle window resize (IScene protocol)."""
        self.screen_width = width
        self.screen_height = height
        self.ui_manager.set_window_resolution((width, height))
        self._create_ui()

    def handle_input(self, events):
        """Handle user input for category selection, test selection, and buttons."""
        for event in events:
            # Process pygame_gui events first
            self.ui_manager.process_events(event)

            # Handle pygame_gui button presses
            # Note: Check hasattr because USEREVENT+1 == UI_BUTTON_PRESSED (both 32866)
            if event.type == pygame_gui.UI_BUTTON_PRESSED and hasattr(event, 'ui_element'):
                callback = self._button_callbacks.get(event.ui_element)
                if callback:
                    callback()
                    continue  # Event consumed by button

            # Handle batch test continuation timer
            if event.type == pygame.USEREVENT + 1:
                self._continue_batch_test()
                continue

            # Dispatch to dialog, panel, and scroll/mouse handlers
            if self._handle_dialog_events(event):
                continue
            if self._handle_panel_events(event):
                continue
            self._handle_scroll_and_mouse(event)

    def _handle_dialog_events(self, event):
        """Handle events for confirmation dialog, JSON popup, and battle state viewer.

        Returns:
            True if the event was consumed by a dialog.
        """
        # Handle confirmation dialog first (if open)
        if self.confirmation_dialog and self.confirmation_dialog.is_open:
            self.confirmation_dialog.handle_event(event)
            if not self.confirmation_dialog.is_open:
                self.confirmation_dialog = None
            return True  # Don't process other events while dialog is open

        # Handle JSON popup (if open)
        if self.json_popup and self.json_popup.is_open:
            self.json_popup.handle_event(event)
            if not self.json_popup.is_open:
                self.json_popup = None
            return True  # Don't process other events while popup is open

        # Handle battle state viewer (if open)
        if self.battle_state_viewer and self.battle_state_viewer.visible:
            self.battle_state_viewer.handle_event(event)
            return True  # Don't process other events while viewer is open

        return False

    def _handle_panel_events(self, event):
        """Handle events for tabbed ship panel, ship panels, component panels,
        results panel, and test details panel.

        Returns:
            True if the event was consumed by a panel.
        """
        # Handle ship panel events (scrolling)
        if self.tabbed_ship_panel:
            if self.tabbed_ship_panel.handle_event(event):
                return True  # Event consumed by tabbed panel
        for panel in self.ship_panels:
            if panel.handle_event(event):
                return True  # Event consumed by panel

        # Handle component panel events (scrolling, dropdown clicks)
        for panel in self.component_panels:
            if panel.handle_event(event):
                return True  # Event consumed by panel

        # Handle results panel events (scrolling, card selection, clear buttons)
        if self.results_panel:
            if self.results_panel.handle_event(event):
                return True  # Event consumed by panel

        # Handle test details panel events (scrolling)
        if self.test_details_panel:
            if self.test_details_panel.handle_event(event):
                return True  # Event consumed by panel

        return False

    def _handle_scroll_and_mouse(self, event):
        """Handle MOUSEWHEEL, MOUSEMOTION, and MOUSEBUTTONDOWN events."""
        # Handle mouse wheel for test list scrolling
        if event.type == pygame.MOUSEWHEEL:
            mx, my = pygame.mouse.get_pos()
            if self.test_list_panel_rect and self.test_list_panel_rect.collidepoint(mx, my):
                self.test_list_scroll_offset -= event.y * 40  # 40px per scroll tick
                self.test_list_scroll_offset = max(0, min(self.test_list_scroll_offset, self.test_list_max_scroll))
                return  # Event consumed

        # Handle mouse motion for hover effects
        if event.type == pygame.MOUSEMOTION:
            mx, my = event.pos
            self._update_hover_state(mx, my)

        # Handle mouse clicks
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            self._handle_click(mx, my)

    def _update_hover_state(self, mx, my):
        """Update hover state for categories and tests."""
        # Reset hover
        self.category_hover = None
        self.test_hover = None

        # Check "All Tests" hover
        category_x = 20
        category_y = self.header_height + 20
        all_tests_y = category_y + 40
        all_tests_rect = pygame.Rect(category_x, all_tests_y, 200, 40)
        if all_tests_rect.collidepoint(mx, my):
            self.category_hover = "ALL"
            return

        # Check category hover (starts after "All Tests" button)
        category_start_y = all_tests_y + 50
        for i, category in enumerate(self.categories):
            rect = pygame.Rect(category_x, category_start_y + i * 50, 200, 40)
            if rect.collidepoint(mx, my):
                self.category_hover = category
                return

        # Check test hover (accounting for scroll offset)
        test_list_x = 20 + self.category_width + 20
        test_list_y = self.header_height + 20 + 40  # +40 for header offset

        # Check if mouse is within the test list panel visible area
        if self.test_list_panel_rect and self.test_list_panel_rect.collidepoint(mx, my):
            filtered_scenarios = self._get_filtered_scenarios()
            sorted_test_ids = sorted(filtered_scenarios.keys())

            for i, test_id in enumerate(sorted_test_ids):
                # Calculate item position with scroll offset
                item_y = test_list_y + i * 55 - self.test_list_scroll_offset
                rect = pygame.Rect(test_list_x, item_y, 400, 50)
                if rect.collidepoint(mx, my) and item_y >= test_list_y - 50 and item_y < test_list_y + (self.test_list_panel_rect.height - 50):
                    self.test_hover = test_id
                    break

    def _handle_click(self, mx, my):
        """Handle click events for categories and tests."""
        if self._check_category_clicks(mx, my):
            return
        if self._check_tag_filter_clicks(mx, my):
            return
        if self._check_test_item_click(mx, my):
            return
        if self._check_action_button_clicks(mx, my):
            return
        self._check_seed_mode_clicks(mx, my)

    def _check_category_clicks(self, mx, my):
        """Check clicks on the 'All Tests' button and category list.

        Returns:
            True if a click was handled.
        """
        category_x = 20
        category_y = self.header_height + 20

        # Check header offset (40px for "CATEGORIES" header)
        all_tests_y = category_y + 40
        all_tests_rect = pygame.Rect(category_x, all_tests_y, 200, 40)
        if all_tests_rect.collidepoint(mx, my):
            self.selected_category = None
            self.selected_test_id = None
            return True

        # Check category click (starts after "All Tests" button)
        category_start_y = all_tests_y + 50
        for i, category in enumerate(self.categories):
            rect = pygame.Rect(category_x, category_start_y + i * 50, 200, 40)
            if rect.collidepoint(mx, my):
                # Toggle category selection
                if self.selected_category == category:
                    self.selected_category = None  # Deselect - show all
                else:
                    self.selected_category = category
                self.selected_test_id = None  # Clear test selection
                return True

        return False

    def _check_tag_filter_clicks(self, mx, my):
        """Check clicks on tag filter buttons, clear button, and run all tests button.

        Returns:
            True if a click was handled.
        """
        # Check tag filter clicks
        # Left-click: cycle through states (neutral -> include -> exclude -> neutral)
        for tag, rect in self.tag_filter_rects.items():
            if rect.collidepoint(mx, my):
                self.controller.ui_state.cycle_tag_state(tag)
                return True

        # Check tag filter clear button
        if hasattr(self, 'tag_clear_rect') and self.tag_clear_rect:
            if self.tag_clear_rect.collidepoint(mx, my):
                self.controller.ui_state.clear_tag_filters()
                return True

        # Check "Run Tests" button click (in test list panel)
        if self.run_all_tests_btn_rect and self.run_all_tests_btn_rect.collidepoint(mx, my):
            if not self.batch_running:
                self._on_run_all_tests()
            return True

        return False

    def _check_test_item_click(self, mx, my):
        """Check clicks on test items in the scrollable test list.

        Returns:
            True if a click was handled.
        """
        # Check test click (accounting for scroll offset)
        test_list_x = 20 + self.category_width + 20
        test_list_y = self.header_height + 20 + 40  # +40 for header offset

        # Only check test clicks if within the test list panel
        if self.test_list_panel_rect and self.test_list_panel_rect.collidepoint(mx, my):
            filtered_scenarios = self._get_filtered_scenarios()
            sorted_test_ids = sorted(filtered_scenarios.keys())

            for i, test_id in enumerate(sorted_test_ids):
                # Calculate item position with scroll offset
                item_y = test_list_y + i * 55 - self.test_list_scroll_offset
                rect = pygame.Rect(test_list_x, item_y, 400, 50)
                # Check if item is visible and clicked
                if rect.collidepoint(mx, my) and item_y >= test_list_y - 50 and item_y < test_list_y + (self.test_list_panel_rect.height - 50):
                    self.selected_test_id = test_id
                    # Create ship panels for the selected test
                    self._create_ship_panels(test_id)
                    # Create results panel for the selected test
                    self._create_results_panel(test_id)
                    return True

        return False

    def _check_action_button_clicks(self, mx, my):
        """Check clicks on Run Test, Run Headless, and Update Expected buttons.

        Returns:
            True if a click was handled.
        """
        # Check Run Test button click (in metadata panel)
        if self.run_test_btn_rect and self.run_test_btn_rect.collidepoint(mx, my):
            self._on_run()
            return True

        # Check Run Headless button click (in metadata panel)
        if self.run_headless_btn_rect and self.run_headless_btn_rect.collidepoint(mx, my):
            self._on_run_headless()
            return True

        # Check "Update Expected Values" button click
        if self.update_expected_button_visible and self.update_expected_button_rect:
            if self.update_expected_button_rect.collidepoint(mx, my):
                self._handle_update_expected_values()
                return True

        return False

    def _check_seed_mode_clicks(self, mx, my):
        """Check clicks on seed mode buttons and seed input area.

        Returns:
            True if a click was handled.
        """
        # Check seed mode button clicks
        for mode_id, rect in self.seed_mode_rects.items():
            if rect.collidepoint(mx, my):
                self.controller.ui_state.set_seed_mode(mode_id)
                return True

        # Check seed input click (for custom mode)
        if self.seed_input_rect and self.seed_input_rect.collidepoint(mx, my):
            self._prompt_for_custom_seed()
            return True

        return False

    def _prompt_for_custom_seed(self):
        """Prompt user to enter a custom seed value."""
        import tkinter as tk
        from tkinter import simpledialog

        # Create a hidden root window
        root = tk.Tk()
        root.withdraw()

        # Get current custom seed for default value
        current_seed = self.controller.ui_state.get_custom_seed()
        default_val = str(current_seed) if current_seed is not None else ""

        # Show input dialog
        result = simpledialog.askstring(
            "Custom Seed",
            "Enter seed value (integer):",
            initialvalue=default_val,
            parent=root
        )

        root.destroy()

        # Process result
        if result is not None:
            try:
                seed_value = int(result.strip())
                self.controller.ui_state.set_custom_seed(seed_value)
                self.output_log.append(f"Custom seed set to: {seed_value}")
            except ValueError:
                self.output_log.append(f"Invalid seed value: {result}")

    def update(self, dt: float = 0):
        """Update UI state (IScene protocol).

        Args:
            dt: Time since last frame in seconds (unused by this screen)
        """
        # Update tabbed ship panel (hover states)
        if self.tabbed_ship_panel:
            self.tabbed_ship_panel.update()

        # Update ship panels (hover states)
        for panel in self.ship_panels:
            panel.update()

        # Update component panels (hover states)
        for panel in self.component_panels:
            panel.update()

        # Update results panel (hover states for buttons/cards)
        if self.results_panel:
            self.results_panel.update()

    def draw(self, screen):
        """Draw the Combat Lab UI with category sidebar, test list, and metadata panel."""
        screen.fill(self.BG_COLOR)

        # Header
        self._draw_header(screen)

        # Three-column layout
        self._draw_category_sidebar(screen)
        self._draw_test_list(screen)
        self._draw_metadata_panel(screen)

        # Ship panels (drawn after metadata panel)
        if self.tabbed_ship_panel:
            self.tabbed_ship_panel.draw(screen)
        for panel in self.ship_panels:
            panel.draw(screen)

        # Component panels (drawn after ship panels)
        for panel in self.component_panels:
            panel.draw(screen)

        # Results panel (drawn after component panels)
        if self.results_panel:
            self.results_panel.draw(screen)

        # Test details panel (drawn after results panel)
        if self.test_details_panel:
            self.test_details_panel.draw(screen)

        # Output log
        self._draw_output_log(screen)

        # Update and draw pygame_gui UIManager (for UIButtons)
        # Use a fixed time_delta since we don't have access to clock here
        self.ui_manager.update(1.0 / 60.0)  # Assume 60 FPS
        self.ui_manager.draw_ui(screen)

        # JSON popup (drawn last, on top of everything)
        if self.json_popup and self.json_popup.is_open:
            self.json_popup.draw(screen)

        # Confirmation dialog (drawn last, on top of everything including popups)
        if self.confirmation_dialog and self.confirmation_dialog.is_open:
            self.confirmation_dialog.draw(screen)

        # Battle state viewer (drawn on top of everything)
        if self.battle_state_viewer and self.battle_state_viewer.visible:
            self.battle_state_viewer.draw(screen)

    def _draw_header(self, screen):
        """Draw the header with title and global seed controls."""
        title = self.title_font.render("COMBAT LAB - TEST VIEWER", True, self.HEADER_COLOR)
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 20))

        # Draw seed controls on the right side of header
        self._draw_header_seed_controls(screen)

    def _draw_header_seed_controls(self, screen):
        """Draw global seed controls in the header area (upper right)."""
        mx, my = pygame.mouse.get_pos()

        # Position in upper right
        x = WIDTH - 450
        y = 15

        # Seed label
        seed_label = self.body_font.render("Seed Mode:", True, (180, 180, 180))
        screen.blit(seed_label, (x, y))

        # Seed mode buttons
        mode_x = x + 100
        btn_height = 24
        btn_spacing = 8

        current_mode = self.controller.ui_state.get_seed_mode()
        self.seed_mode_rects = {}

        modes = [
            ("random", "Random", 65),
            ("metadata", "Fixed", 55),
            ("custom", "Custom", 60)
        ]

        for mode_id, mode_label, btn_width in modes:
            rect = pygame.Rect(mode_x, y - 2, btn_width, btn_height)
            self.seed_mode_rects[mode_id] = rect

            is_active = current_mode == mode_id
            is_hovered = rect.collidepoint(mx, my)

            if is_active:
                bg_color = (40, 80, 120)
                border_color = (80, 140, 200)
                text_color = (200, 220, 255)
            elif is_hovered:
                bg_color = (50, 50, 60)
                border_color = (100, 100, 110)
                text_color = self.TEXT_COLOR
            else:
                bg_color = self.CATEGORY_BG
                border_color = self.BORDER_COLOR
                text_color = (150, 150, 150)

            pygame.draw.rect(screen, bg_color, rect, border_radius=3)
            pygame.draw.rect(screen, border_color, rect, 1, border_radius=3)

            mode_text = self.small_font.render(mode_label, True, text_color)
            text_x = rect.x + (btn_width - mode_text.get_width()) // 2
            screen.blit(mode_text, (text_x, rect.y + 4))

            mode_x += btn_width + btn_spacing

        # Show current seed value / input area
        seed_x = mode_x + 10
        custom_seed = self.controller.ui_state.get_custom_seed()

        if current_mode == "random":
            seed_text = "(new each run)"
            seed_color = (100, 100, 100)
        elif current_mode == "metadata":
            # Show the metadata seed if we have a selected test
            if self.selected_test_id:
                scenario_info = self.registry.get_by_id(self.selected_test_id)
                if scenario_info:
                    seed_text = f"= {scenario_info['metadata'].seed}"
                else:
                    seed_text = "(select test)"
            else:
                seed_text = "(select test)"
            seed_color = (100, 140, 100)
        else:  # custom
            if custom_seed is not None:
                seed_text = f"= {custom_seed}"
                seed_color = (100, 180, 255)
            else:
                seed_text = "[click to enter]"
                seed_color = (180, 140, 100)

        # Draw seed value/input area as clickable region for custom mode
        seed_surf = self.small_font.render(seed_text, True, seed_color)
        seed_rect = pygame.Rect(seed_x, y, max(seed_surf.get_width() + 10, 120), btn_height)

        if current_mode == "custom":
            # Make it look clickable
            is_hovered = seed_rect.collidepoint(mx, my)
            if is_hovered:
                pygame.draw.rect(screen, (40, 50, 60), seed_rect, border_radius=3)
            pygame.draw.rect(screen, (80, 100, 120), seed_rect, 1, border_radius=3)
            self.seed_input_rect = seed_rect
        else:
            self.seed_input_rect = None

        screen.blit(seed_surf, (seed_x + 5, y + 4))

    def _draw_category_sidebar(self, screen):
        """Draw the category selection sidebar."""
        x = 20
        y = self.header_height + 20

        # Draw panel background
        panel_rect = pygame.Rect(x - 10, y - 10, self.category_width, HEIGHT - y - 100)
        pygame.draw.rect(screen, self.PANEL_BG, panel_rect, border_radius=5)
        pygame.draw.rect(screen, self.BORDER_COLOR, panel_rect, 2, border_radius=5)

        # Header
        header_text = self.header_font.render("CATEGORIES", True, self.HEADER_COLOR)
        screen.blit(header_text, (x, y - 5))
        y += 40

        # "All Tests" option
        all_rect = pygame.Rect(x, y, 200, 40)
        if self.selected_category is None:
            color = self.SELECTED_COLOR
        elif self.category_hover == "ALL":
            color = (50, 50, 60)
        else:
            color = self.CATEGORY_BG

        pygame.draw.rect(screen, color, all_rect, border_radius=3)
        pygame.draw.rect(screen, self.BORDER_COLOR, all_rect, 1, border_radius=3)

        all_text = self.body_font.render(f"All Tests ({len(self.all_scenarios)})", True, self.TEXT_COLOR)
        screen.blit(all_text, (all_rect.x + 10, all_rect.y + 10))
        y += 50

        # Check hover for "All Tests"
        mx, my = pygame.mouse.get_pos()
        if all_rect.collidepoint(mx, my):
            self.category_hover = "ALL"

        # Category buttons
        for i, category in enumerate(self.categories):
            rect = pygame.Rect(x, y + i * 50, 200, 40)

            # Determine color
            if self.selected_category == category:
                color = self.SELECTED_COLOR
            elif self.category_hover == category:
                color = (50, 50, 60)
            else:
                color = self.CATEGORY_BG

            pygame.draw.rect(screen, color, rect, border_radius=3)
            pygame.draw.rect(screen, self.BORDER_COLOR, rect, 1, border_radius=3)

            # Count tests in category
            count = len(self.registry.get_by_category(category))
            text = self.body_font.render(f"{category} ({count})", True, self.TEXT_COLOR)
            screen.blit(text, (rect.x + 10, rect.y + 10))

        # Draw tag filter section below categories
        tag_section_y = y + len(self.categories) * 50 + 20
        self._draw_tag_filters(screen, x, tag_section_y)

    def _draw_tag_filters(self, screen, x, y):
        """Draw tag filter buttons for quick filtering."""
        # Header
        header_text = self.small_font.render("TAG FILTERS", True, self.HEADER_COLOR)
        screen.blit(header_text, (x, y))
        y += 25

        # Get all unique tags from registry
        all_tags = self.registry.get_all_tags()

        # Prioritize common filter tags at the top
        priority_tags = ['high-tick', 'precision', 'quick']
        sorted_tags = [t for t in priority_tags if t in all_tags]
        sorted_tags += [t for t in sorted(all_tags) if t not in priority_tags]

        # Limit display to avoid overcrowding
        display_tags = sorted_tags[:8]  # Show top 8 tags

        self.tag_filter_rects = {}
        mx, my = pygame.mouse.get_pos()

        for i, tag in enumerate(display_tags):
            # Create tag button
            btn_width = 95
            btn_height = 24
            col = i % 2
            row = i // 2
            btn_x = x + col * (btn_width + 5)
            btn_y = y + row * (btn_height + 4)

            rect = pygame.Rect(btn_x, btn_y, btn_width, btn_height)
            self.tag_filter_rects[tag] = rect

            # Determine state and color
            is_active = self.controller.ui_state.is_tag_active(tag)
            is_excluded = self.controller.ui_state.is_tag_excluded(tag)
            is_hovered = rect.collidepoint(mx, my)

            if is_excluded:
                bg_color = (100, 40, 40)  # Red for excluded
                border_color = (180, 80, 80)
                text_color = (255, 150, 150)
                prefix = "X "
            elif is_active:
                bg_color = (40, 80, 40)  # Green for active
                border_color = (80, 150, 80)
                text_color = (150, 255, 150)
                prefix = "V "
            elif is_hovered:
                bg_color = (50, 50, 60)
                border_color = (100, 100, 110)
                text_color = self.TEXT_COLOR
                prefix = ""
            else:
                bg_color = self.CATEGORY_BG
                border_color = self.BORDER_COLOR
                text_color = (180, 180, 180)
                prefix = ""

            pygame.draw.rect(screen, bg_color, rect, border_radius=3)
            pygame.draw.rect(screen, border_color, rect, 1, border_radius=3)

            # Truncate tag text if needed
            display_tag = prefix + tag
            if len(display_tag) > 12:
                display_tag = display_tag[:11] + "..."
            tag_text = self.small_font.render(display_tag, True, text_color)
            screen.blit(tag_text, (rect.x + 4, rect.y + 4))

        # Show filter count if active
        active_count = len(self.controller.ui_state.get_active_tag_filters())
        excluded_count = len(self.controller.ui_state.get_excluded_tags())
        if active_count > 0 or excluded_count > 0:
            filter_y = y + ((len(display_tags) + 1) // 2) * 28 + 5
            if active_count > 0 and excluded_count > 0:
                filter_text = f"+{active_count} / -{excluded_count}"
            elif active_count > 0:
                filter_text = f"+{active_count} tags"
            else:
                filter_text = f"-{excluded_count} tags"

            # Clear filters button
            clear_rect = pygame.Rect(x, filter_y, 80, 20)
            is_clear_hovered = clear_rect.collidepoint(mx, my)
            clear_bg = (80, 60, 60) if is_clear_hovered else (60, 50, 50)
            pygame.draw.rect(screen, clear_bg, clear_rect, border_radius=3)
            pygame.draw.rect(screen, (120, 80, 80), clear_rect, 1, border_radius=3)
            clear_text = self.small_font.render("Clear", True, (255, 180, 180))
            screen.blit(clear_text, (clear_rect.x + 22, clear_rect.y + 3))

            # Store for click handling
            self.tag_clear_rect = clear_rect

            # Filter count display
            count_text = self.small_font.render(filter_text, True, (150, 150, 150))
            screen.blit(count_text, (x + 90, filter_y + 3))
        else:
            self.tag_clear_rect = None

    def _draw_test_list(self, screen):
        """Draw the test list panel with scrolling support."""
        x = 20 + self.category_width + 20
        y = self.header_height + 20

        # Draw panel background
        panel_rect = pygame.Rect(x - 10, y - 10, self.test_list_width, HEIGHT - y - 100)
        self.test_list_panel_rect = panel_rect  # Store for scroll event handling
        pygame.draw.rect(screen, self.PANEL_BG, panel_rect, border_radius=5)
        pygame.draw.rect(screen, self.BORDER_COLOR, panel_rect, 2, border_radius=5)

        # Header - always say "TESTS" for consistency
        header_text = self.header_font.render("TESTS", True, self.HEADER_COLOR)
        screen.blit(header_text, (x, y - 5))
        y += 40

        # Get filtered scenarios
        filtered_scenarios = self._get_filtered_scenarios()
        sorted_test_ids = sorted(filtered_scenarios.keys())

        # Draw "Run Tests" button
        mouse_pos = pygame.mouse.get_pos()
        btn_width = 120
        btn_height = 32
        self.run_all_tests_btn_rect = pygame.Rect(x + self.test_list_width - btn_width - 30, y - 35, btn_width, btn_height)

        if self.batch_running:
            # Show progress during batch execution
            progress_text = f"{self.batch_current_index + 1}/{self.batch_total}"
            btn_color = (80, 80, 50)
            btn_border = (150, 150, 80)
            text_color = (255, 255, 150)
        else:
            btn_hover = self.run_all_tests_btn_rect.collidepoint(mouse_pos)
            btn_color = (60, 80, 60) if btn_hover else (40, 60, 40)
            btn_border = (80, 120, 80)
            progress_text = "Run Tests"
            text_color = (150, 200, 150)

        pygame.draw.rect(screen, btn_color, self.run_all_tests_btn_rect, border_radius=4)
        pygame.draw.rect(screen, btn_border, self.run_all_tests_btn_rect, 1, border_radius=4)
        btn_text = self.small_font.render(progress_text, True, text_color)
        text_rect = btn_text.get_rect(center=self.run_all_tests_btn_rect.center)
        screen.blit(btn_text, text_rect)

        if not sorted_test_ids:
            no_tests_text = self.body_font.render("No tests available", True, (150, 150, 150))
            screen.blit(no_tests_text, (x + 20, y + 20))
            return

        # Calculate scrolling dimensions
        item_height = 55
        content_height = len(sorted_test_ids) * item_height
        visible_height = panel_rect.height - 50  # Space for header
        self.test_list_max_scroll = max(0, content_height - visible_height)

        # Clamp scroll offset
        self.test_list_scroll_offset = max(0, min(self.test_list_scroll_offset, self.test_list_max_scroll))

        # Set clipping region for test items
        clip_rect = pygame.Rect(panel_rect.x, y, panel_rect.width, visible_height)
        screen.set_clip(clip_rect)

        # Draw test items with scroll offset
        for i, test_id in enumerate(sorted_test_ids):
            item_y = y + i * item_height - self.test_list_scroll_offset

            # Skip items outside visible area for performance
            if item_y + 50 < y or item_y > y + visible_height:
                continue

            scenario_info = filtered_scenarios[test_id]
            metadata = scenario_info['metadata']

            rect = pygame.Rect(x, item_y, 400, 50)

            # Determine color
            if self.selected_test_id == test_id:
                color = self.SELECTED_COLOR
            elif self.test_hover == test_id:
                color = (40, 40, 50)
            else:
                color = (30, 30, 35)

            pygame.draw.rect(screen, color, rect, border_radius=3)
            pygame.draw.rect(screen, self.BORDER_COLOR, rect, 1, border_radius=3)

            # Validation status flag (if available)
            flag_x = rect.x + rect.width - 30
            flag_y = rect.y + rect.height // 2  # Vertically centered
            self._draw_validation_flag(screen, flag_x, flag_y, scenario_info)

            # Test ID
            id_text = self.body_font.render(test_id, True, self.HEADER_COLOR)
            screen.blit(id_text, (rect.x + 10, rect.y + 5))

            # Test name
            name_text = self.small_font.render(metadata.name, True, self.TEXT_COLOR)
            screen.blit(name_text, (rect.x + 10, rect.y + 28))

        # Reset clipping
        screen.set_clip(None)

        # Draw scrollbar if needed
        if self.test_list_max_scroll > 0:
            self._draw_test_list_scrollbar(screen, panel_rect, y, visible_height)

    def _draw_test_list_scrollbar(self, screen, panel_rect, content_y, visible_height):
        """Draw scrollbar for the test list panel."""
        scrollbar_width = 8
        scrollbar_x = panel_rect.x + panel_rect.width - scrollbar_width - 5
        scrollbar_y = content_y
        scrollbar_height = visible_height

        # Draw track
        track_rect = pygame.Rect(scrollbar_x, scrollbar_y, scrollbar_width, scrollbar_height)
        pygame.draw.rect(screen, (40, 40, 50), track_rect, border_radius=4)

        # Calculate thumb size and position
        content_height = self.test_list_max_scroll + visible_height
        thumb_height = max(30, int(visible_height * visible_height / content_height))
        scroll_ratio = self.test_list_scroll_offset / self.test_list_max_scroll if self.test_list_max_scroll > 0 else 0
        thumb_y = scrollbar_y + int(scroll_ratio * (scrollbar_height - thumb_height))

        # Draw thumb
        thumb_rect = pygame.Rect(scrollbar_x, thumb_y, scrollbar_width, thumb_height)
        pygame.draw.rect(screen, (100, 100, 120), thumb_rect, border_radius=4)

    def _draw_metadata_panel(self, screen):
        """Draw the metadata panel showing rich test information."""
        x = 20 + self.category_width + 20 + self.test_list_width + 20
        y = self.header_height + 20

        # Draw panel background
        panel_rect = pygame.Rect(x - 10, y - 10, self.metadata_width, HEIGHT - y - 100)
        pygame.draw.rect(screen, self.PANEL_BG, panel_rect, border_radius=5)
        pygame.draw.rect(screen, self.BORDER_COLOR, panel_rect, 2, border_radius=5)

        # Header with run buttons
        header_text = self.header_font.render("TEST DETAILS", True, self.HEADER_COLOR)
        screen.blit(header_text, (x, y - 5))

        # Run buttons to the right of header (only if a test is selected)
        if self.selected_test_id is not None:
            mouse_pos = pygame.mouse.get_pos()
            btn_height = 26
            btn_spacing = 10
            header_btn_y = y - 8

            # Visual Run button (green)
            visual_btn_width = 90
            visual_btn_x = x + self.metadata_width - 220
            self.run_test_btn_rect = pygame.Rect(visual_btn_x, header_btn_y, visual_btn_width, btn_height)
            run_test_hover = self.run_test_btn_rect.collidepoint(mouse_pos)
            run_test_color = (70, 100, 70) if run_test_hover else (50, 80, 50)
            pygame.draw.rect(screen, run_test_color, self.run_test_btn_rect, border_radius=4)
            pygame.draw.rect(screen, (100, 150, 100), self.run_test_btn_rect, 1, border_radius=4)
            run_text = self.small_font.render("Visual Run", True, (200, 255, 200))
            text_rect = run_text.get_rect(center=self.run_test_btn_rect.center)
            screen.blit(run_text, text_rect)

            # Headless Run button (blue)
            headless_btn_width = 100
            headless_btn_x = visual_btn_x + visual_btn_width + btn_spacing
            self.run_headless_btn_rect = pygame.Rect(headless_btn_x, header_btn_y, headless_btn_width, btn_height)
            run_headless_hover = self.run_headless_btn_rect.collidepoint(mouse_pos)
            run_headless_color = (70, 70, 100) if run_headless_hover else (50, 50, 80)
            pygame.draw.rect(screen, run_headless_color, self.run_headless_btn_rect, border_radius=4)
            pygame.draw.rect(screen, (100, 100, 150), self.run_headless_btn_rect, 1, border_radius=4)
            headless_text = self.small_font.render("Headless Run", True, (200, 200, 255))
            text_rect = headless_text.get_rect(center=self.run_headless_btn_rect.center)
            screen.blit(headless_text, text_rect)

        y += 40

        if self.selected_test_id is None:
            hint_text = self.body_font.render("Select a test to view details", True, (150, 150, 150))
            screen.blit(hint_text, (x + 20, y + 20))
            return

        # Get selected test metadata
        scenario_info = self.registry.get_by_id(self.selected_test_id)
        if scenario_info is None:
            return

        metadata = scenario_info['metadata']

        # Test ID
        y = self._draw_section(screen, x, y, "Test ID", metadata.test_id, self.HEADER_COLOR)
        y += 10

        # Category
        category_text = f"{metadata.category} > {metadata.subcategory}"
        y = self._draw_section(screen, x, y, "Category", category_text, (200, 150, 100))
        y += 10

        # Summary
        y = self._draw_section_wrapped(screen, x, y, "Summary", metadata.summary, (100, 200, 150))
        y += 15

        # Get validation results if available
        validation_results = None
        if 'last_run_results' in scenario_info and scenario_info['last_run_results']:
            validation_results = scenario_info['last_run_results'].get('validation_results', None)

        # Conditions (with validation indicators)
        y = self._draw_bullet_list(screen, x, y, "Conditions", metadata.conditions, (150, 200, 255), validation_results)
        y += 15

        # Edge Cases
        y = self._draw_bullet_list(screen, x, y, "Edge Cases", metadata.edge_cases, (255, 200, 100))
        y += 15

        # Expected Outcome
        y = self._draw_section_wrapped(screen, x, y, "Expected Outcome", metadata.expected_outcome, (100, 255, 150))
        y += 15

        # Pass Criteria
        y = self._draw_section_wrapped(screen, x, y, "Pass Criteria", metadata.pass_criteria, (255, 150, 150))
        y += 15

        # Validation Results (from static validation or test run)
        if 'last_run_results' in scenario_info and scenario_info['last_run_results']:
            results = scenario_info['last_run_results']
            if 'validation_results' in results:
                y += 20
                y = self._draw_validation_section(screen, x, y, results)

        y += 20

        # Metadata footer - just show max ticks (seed controls are now in header)
        ticks_text = f"Max Ticks: {metadata.max_ticks}    |    Test Seed: {metadata.seed}"
        ticks_surf = self.small_font.render(ticks_text, True, (120, 120, 120))
        screen.blit(ticks_surf, (x, y))

    def _draw_section(self, screen, x, y, label, text, color):
        """Draw a single-line metadata section."""
        # Label
        label_surf = self.body_font.render(f"{label}:", True, color)
        screen.blit(label_surf, (x, y))
        y += 25

        # Text
        text_surf = self.small_font.render(text, True, self.TEXT_COLOR)
        screen.blit(text_surf, (x + 10, y))
        y += 22

        return y

    def _draw_section_wrapped(self, screen, x, y, label, text, color):
        """Draw a metadata section with text wrapping."""
        # Label
        label_surf = self.body_font.render(f"{label}:", True, color)
        screen.blit(label_surf, (x, y))
        y += 25

        # Wrapped text
        y = self._draw_wrapped_text(screen, text, x + 10, y, self.metadata_width - 40, self.TEXT_COLOR)
        y += 5

        return y

    def _draw_bullet_list(self, screen, x, y, label, items, color, validation_results=None):
        """Draw a bullet list section with optional validation indicators."""
        # Label
        label_surf = self.body_font.render(f"{label}:", True, color)
        screen.blit(label_surf, (x, y))
        y += 25

        # Items
        if not items:
            none_surf = self.small_font.render("None", True, (120, 120, 120))
            screen.blit(none_surf, (x + 20, y))
            y += 22
        else:
            for item in items:
                bullet_surf = self.small_font.render(f"* {item}", True, self.TEXT_COLOR)
                screen.blit(bullet_surf, (x + 10, y))

                # Check if this item is verified by validation results
                if validation_results and self._is_condition_verified(item, validation_results):
                    # Draw green "V" on right edge
                    v_surf = self.body_font.render("V", True, (80, 255, 120))  # Green
                    v_x = x + self.metadata_width - 40  # Right edge with padding
                    screen.blit(v_surf, (v_x, y - 2))

                y += 22

        return y

    def _is_condition_verified(self, condition_text, validation_results):
        """
        Check if a condition is verified by a passing validation.

        Args:
            condition_text: Text like "Beam Damage: 5 per hit"
            validation_results: List of validation result dicts

        Returns:
            True if condition matches a PASS validation
        """
        # Map condition text patterns to validation rule names
        mappings = {
            # Beam weapon mappings
            'Beam Damage': 'Beam Weapon Damage',
            'Base Accuracy': 'Base Accuracy',
            'Accuracy Falloff': 'Accuracy Falloff',
            'Weapon Max Range': 'Weapon Range',
            'Distance': None,  # Distance is test setup, not component property
            'Net Score': None,  # Calculated value, complex validation
            'Test Duration': None,  # Test parameter, not validated
            'Test duration': None,  # Test parameter, not validated

            # Propulsion test mappings
            'Engine thrust': 'Engine Thrust',
            'Ship mass': 'Ship Mass',
            'Expected max_speed': 'Max Speed (Formula)',
            'Expected acceleration_rate': 'Acceleration Rate (Formula)',
            'Initial velocity': 'Initial Velocity',
            'Initial angle': 'Initial Angle',
            'Total thrust': 'Total Thrust',
            'turn_speed': 'Turn Speed',
            'Turn speed': 'Turn Speed (Formula)',
            'raw_turn_rate': 'Raw Turn Rate',
            'Expected turn_speed': 'Turn Speed (Formula)',
            'No engine component': 'Total Thrust (Should be 0)',
            'No thruster component': None,  # Not directly validated
            'thrust = 0': 'Total Thrust (Should be 0)',
            'Expected: No movement': 'Distance Traveled',
            'Expected: Rotation but no translation': 'Final Velocity',
        }

        # Check direct validations
        for pattern, validation_name in mappings.items():
            if validation_name and pattern in condition_text:
                # Find matching validation result
                for vr in validation_results:
                    if vr['name'] == validation_name and vr['status'] == 'PASS':
                        return True

        # Special case: Range Penalty (calculated from distance x accuracy_falloff)
        if 'Range Penalty' in condition_text:
            # Extract values from condition text like "Range Penalty: 50 * 0.002 = 0.1"
            try:
                import re
                # Match pattern: "Range Penalty: {distance} * {falloff} = {result}"
                match = re.search(r'Range Penalty:\s*(\d+\.?\d*)\s*\*\s*(\d+\.?\d*)\s*=\s*(\d+\.?\d*)', condition_text)
                if match:
                    distance_stated = float(match.group(1))
                    falloff_stated = float(match.group(2))
                    penalty_stated = float(match.group(3))

                    # Check if falloff is verified
                    falloff_verified = False
                    falloff_actual = None
                    for vr in validation_results:
                        if vr['name'] == 'Accuracy Falloff' and vr['status'] == 'PASS':
                            falloff_verified = True
                            falloff_actual = vr['actual']
                            break

                    if falloff_verified and falloff_actual is not None:
                        # Verify the calculation is correct
                        calculated_penalty = distance_stated * falloff_actual
                        if abs(calculated_penalty - penalty_stated) < 0.0001:  # Float comparison with tolerance
                            return True
            except (ValueError, TypeError):
                pass  # If parsing fails, don't show V

        return False

    def _draw_wrapped_text(self, screen, text, x, y, max_width, color):
        """Draw text with word wrapping."""
        words = text.split(' ')
        lines = []
        current_line = []

        for word in words:
            test_line = ' '.join(current_line + [word])
            test_surf = self.small_font.render(test_line, True, color)

            if test_surf.get_width() <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]

        if current_line:
            lines.append(' '.join(current_line))

        # Draw lines
        for line in lines:
            line_surf = self.small_font.render(line, True, color)
            screen.blit(line_surf, (x, y))
            y += 20

        return y

    def _draw_validation_section(self, screen, x, y, results):
        """Draw validation results section with color-coded status."""
        # Section header
        header_surf = self.body_font.render("Validation Results:", True, (255, 200, 100))
        screen.blit(header_surf, (x, y))
        y += 25

        validation_results = results.get('validation_results', [])
        validation_summary = results.get('validation_summary', {})

        if not validation_results:
            no_val_surf = self.small_font.render("No validation rules defined", True, (120, 120, 120))
            screen.blit(no_val_surf, (x + 10, y))
            return y + 22

        # Summary counts
        pass_count = validation_summary.get('pass', 0)
        fail_count = validation_summary.get('fail', 0)
        warn_count = validation_summary.get('warn', 0)

        # Determine overall status color
        if fail_count > 0:
            summary_color = (255, 80, 80)  # Red
            status_symbol = "X"
        elif warn_count > 0:
            summary_color = (255, 200, 80)  # Yellow/Orange
            status_symbol = "!"
        else:
            summary_color = (80, 255, 120)  # Green
            status_symbol = "V"

        # Summary line
        summary_text = f"{status_symbol} {pass_count} Pass, {fail_count} Fail, {warn_count} Warn"
        summary_surf = self.small_font.render(summary_text, True, summary_color)
        screen.blit(summary_surf, (x + 10, y))
        y += 25

        # Individual validation results
        for vr in validation_results:
            status = vr['status']
            name = vr['name']
            expected = vr['expected']
            actual = vr['actual']
            p_value = vr.get('p_value')

            # Status color
            if status == 'PASS':
                status_color = (80, 255, 120)
                symbol = "V"
            elif status == 'FAIL':
                status_color = (255, 80, 80)
                symbol = "X"
            elif status == 'WARN':
                status_color = (255, 200, 80)
                symbol = "!"
            else:
                status_color = (120, 120, 200)
                symbol = "i"

            # Validation name with symbol
            name_surf = self.small_font.render(f"{symbol} {name}", True, status_color)
            screen.blit(name_surf, (x + 10, y))
            y += 20

            # Expected vs Actual
            if expected is not None and actual is not None:
                # Format as percentage if between 0 and 1
                if isinstance(expected, (int, float)) and 0 <= expected <= 1:
                    exp_str = f"{expected:.2%}"
                else:
                    exp_str = str(expected)

                if isinstance(actual, (int, float)) and 0 <= actual <= 1:
                    act_str = f"{actual:.2%}"
                else:
                    act_str = str(actual)

                exp_act_text = f"Expected: {exp_str} | Actual: {act_str}"
                exp_act_surf = self.small_font.render(exp_act_text, True, (180, 180, 180))
                screen.blit(exp_act_surf, (x + 25, y))
                y += 18

            # P-value (for statistical tests - TOST interpretation)
            if p_value is not None:
                p_text = f"p-value: {p_value:.4f}"
                if p_value < 0.05:
                    p_color = (100, 255, 150)  # Green - proven equivalent (PASS)
                else:
                    p_color = (255, 100, 100)  # Red - not proven equivalent (FAIL)

                p_surf = self.small_font.render(p_text, True, p_color)
                screen.blit(p_surf, (x + 25, y))
                y += 18

            y += 5  # Space between validation items

        # Add "Update Expected Values" button if there are failures
        if fail_count > 0:
            y += 10
            button_width = 200
            button_height = 35
            button_x = x + 10
            button_y = y

            # Store button rect for click detection
            self.update_expected_button_rect = pygame.Rect(button_x, button_y, button_width, button_height)
            self.update_expected_button_visible = True

            # Draw button
            button_color = (60, 120, 200)  # Blue
            button_hover_color = (80, 140, 220)

            # Check if mouse is over button
            mouse_pos = pygame.mouse.get_pos()
            is_hover = self.update_expected_button_rect.collidepoint(mouse_pos)
            current_color = button_hover_color if is_hover else button_color

            # Draw button background
            pygame.draw.rect(screen, current_color, self.update_expected_button_rect)
            pygame.draw.rect(screen, (100, 140, 200), self.update_expected_button_rect, 2)

            # Draw button text
            button_text = "Update Expected Values"
            button_surf = self.small_font.render(button_text, True, (255, 255, 255))
            text_x = button_x + (button_width - button_surf.get_width()) // 2
            text_y = button_y + (button_height - button_surf.get_height()) // 2
            screen.blit(button_surf, (text_x, text_y))

            y += button_height + 10
        else:
            self.update_expected_button_visible = False

        return y

    def _draw_validation_flag(self, screen, x, y, scenario_info):
        """
        Draw a colored flag/circle indicating validation status.

        Green circle = All validations passed
        Yellow circle = Warnings present
        Red circle = Failures present
        Gray circle = No validation data (test not run yet)
        """
        radius = 10

        # Check for validation results
        last_run_results = scenario_info.get('last_run_results')

        if not last_run_results or 'validation_results' not in last_run_results:
            # No validation data - gray circle
            color = (100, 100, 100)
            symbol = None
        else:
            validation_summary = last_run_results.get('validation_summary', {})
            fail_count = validation_summary.get('fail', 0)
            warn_count = validation_summary.get('warn', 0)

            if fail_count > 0:
                # Failures - red circle with X
                color = (255, 80, 80)
                symbol = "X"
            elif warn_count > 0:
                # Warnings - yellow circle with !
                color = (255, 200, 80)
                symbol = "!"
            else:
                # All passed - green circle with checkmark
                color = (80, 255, 120)
                symbol = "V"

        # Draw circle
        pygame.draw.circle(screen, color, (x, y), radius)
        pygame.draw.circle(screen, (0, 0, 0), (x, y), radius, 2)  # Black outline

        # Draw symbol if present
        if symbol:
            symbol_surf = self.small_font.render(symbol, True, (0, 0, 0))
            symbol_rect = symbol_surf.get_rect(center=(x, y))
            screen.blit(symbol_surf, symbol_rect)

    def _show_ships_json(self, test_id):
        """Show JSON for all ships used in the test."""
        if test_id is None:
            return

        scenario_info = self.registry.get_by_id(test_id)
        if not scenario_info:
            return

        # Load ship JSON files from test data
        ships_data = {}

        # Get ship filenames from test scenario
        # This is a simplified approach - we'll try to find ship files mentioned in conditions
        metadata = scenario_info['metadata']

        # Extract ship filenames from conditions
        ship_files = []
        for condition in metadata.conditions:
            if '.json' in condition and ('Attacker:' in condition or 'Target:' in condition):
                parts = condition.split(':')
                if len(parts) > 1:
                    filename = parts[1].strip()
                    ship_files.append(filename)

        # Load ship JSON files
        data_dir = os.path.join(get_test_data_dir(), 'ships')

        for ship_file in ship_files:
            ship_path = os.path.join(data_dir, ship_file)
            ship_data = load_json(ship_path)
            if ship_data is not None:
                ships_data[ship_file] = ship_data
            elif os.path.exists(ship_path):
                ships_data[ship_file] = "Error loading ship file"

        if not ships_data:
            ships_data = {"error": "No ship files found for this test"}

        self.json_popup = JSONPopup(f"Ships JSON - {test_id}", ships_data, WIDTH, HEIGHT, self.ui_manager)

    def _show_components_json(self):
        """Show JSON for all components in the test data."""
        # Load components.json from test data
        components_path = os.path.join(get_test_data_dir(), 'components.json')

        components_data = load_json(components_path)
        if components_data is not None:
            self.json_popup = JSONPopup("Components JSON", components_data, WIDTH, HEIGHT, self.ui_manager)
        else:
            self.json_popup = JSONPopup("Components JSON", {"error": "components.json not found or invalid"}, WIDTH, HEIGHT, self.ui_manager)

    def _draw_output_log(self, screen):
        """Draw the output log at the bottom."""
        y = HEIGHT - 90
        for i, msg in enumerate(self.output_log[-3:]):
            color = (255, 100, 100) if "ERROR" in msg else (150, 150, 150)
            txt = self.small_font.render(msg, True, color)
            screen.blit(txt, (20, y + i * 20))
