"""
TestLabScreen - Combat Lab UI main screen.

This module contains the main TestLabScreen class which orchestrates
the Combat Lab interface for viewing and running test scenarios.

PROJ-172: Refactored to MVVM architecture with ViewModel, Renderer, and InputHandler.
"""
import pygame
import pygame_gui
import os

from game.ui.fonts import get_font, FONT_MONO
from game.ui.screens.test_lab import theme
from game.core.config import DisplayConfig
from game.core.string_utils import display_name
WIDTH, HEIGHT = DisplayConfig.DEFAULT_WIDTH, DisplayConfig.DEFAULT_HEIGHT
from game.core.json_utils import load_json
from test_framework.registry import TestRegistry
from test_framework.test_history import TestHistory
from simulation_tests.logging_config import get_logger

# Intra-package imports
from .dialogs import JSONPopup, ConfirmationDialog
from .data_extractor import TestLabDataExtractor, get_test_data_dir
from .validation_manager import TestLabValidationManager
from .panel_manager import TestLabPanelManager
from .test_executor import TestLabExecutor
from .viewmodel import TestLabViewModel
from .renderer import TestLabRenderer
from .screen_input_handler import TestLabInputHandler
from game.ui.screens.builder.event_bus import EventBus

logger = get_logger(__name__)


class TestLabScreen:
    """
    Combat Lab UI - Enhanced with TestRegistry and rich metadata display.

    Implements IScene protocol for standardized scene handling.

    PROJ-172: Refactored to MVVM architecture:
    - TestLabViewModel: Manages all mutable UI state
    - TestLabRenderer: Handles all drawing operations
    - TestLabInputHandler: Handles input events

    This screen class is now a thin coordinator that:
    - Initializes components
    - Provides IScene protocol interface
    - Delegates to MVVM components
    """

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

        # MVVM Components
        self._event_bus = EventBus()
        self._viewmodel = TestLabViewModel(self._event_bus)
        self._renderer = TestLabRenderer()
        self._input_handler = TestLabInputHandler(
            viewmodel=self._viewmodel,
            controller=self.controller,
            registry=self.registry,
            callbacks={
                'on_run': self._on_run,
                'on_run_headless': self._on_run_headless,
                'on_run_visual_baseline': self._on_run_visual_baseline,
                'on_run_all': self._on_run_all_tests,
                'on_update_expected': self._handle_update_expected_values,
                'create_ship_panels': self._create_ship_panels,
                'create_results_panel': self._create_results_panel,
                'prompt_custom_seed': self._prompt_for_custom_seed,
                'continue_batch': self._continue_batch_test,
            }
        )

        # Battle state viewer (for viewing initial/final JSON states)
        from game.ui.screens.battle_state_viewer import BattleStateViewer
        self.battle_state_viewer = BattleStateViewer(WIDTH, HEIGHT)

        self._create_ui()

    # ─────────────────────────────────────────────────────────────────
    # Property delegates to controller.ui_state (backward compatibility)
    # ─────────────────────────────────────────────────────────────────

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

    # ─────────────────────────────────────────────────────────────────
    # ViewModel panel accessors (backward compatibility)
    # ─────────────────────────────────────────────────────────────────

    @property
    def ship_panels(self):
        return self._viewmodel.ship_panels

    @property
    def component_panels(self):
        return self._viewmodel.component_panels

    @property
    def tabbed_ship_panel(self):
        return self._viewmodel.tabbed_ship_panel

    @property
    def results_panel(self):
        return self._viewmodel.results_panel

    @property
    def test_details_panel(self):
        return self._viewmodel.test_details_panel

    @property
    def json_popup(self):
        return self._viewmodel.json_popup

    @property
    def confirmation_dialog(self):
        return self._viewmodel.confirmation_dialog

    # ─────────────────────────────────────────────────────────────────
    # Delegate methods
    # ─────────────────────────────────────────────────────────────────

    def _extract_ships_from_scenario(self, test_id):
        """Extract ship information from test scenario metadata."""
        return self._data_extractor.extract_ships(test_id)

    def _validate_all_scenarios(self):
        """Validate all test scenarios against component/ship data files."""
        self._validation_manager.validate_all()

    def _build_validation_context_from_files(self, test_id, metadata):
        """Build validation context from ship and component JSON files."""
        return self._validation_manager.build_context_from_files(test_id, metadata)

    def _load_component_data(self, component_id):
        """Load component JSON from components.json by ID."""
        return self._data_extractor.load_component(component_id)

    def _handle_update_expected_values(self):
        """Handle click on Update Expected Values button."""
        dialog = self._validation_manager.handle_update_expected_values(
            self.selected_test_id, self.ui_manager,
            self.game.screen.get_width(), self.game.screen.get_height()
        )
        if dialog:
            self._viewmodel.open_confirmation_dialog(dialog)

    def _apply_metadata_updates(self, changes):
        """Apply metadata updates to the test scenario file."""
        self._validation_manager.apply_metadata_updates(changes, self.selected_test_id)

    def _create_ship_panels(self, test_id):
        """Create ship panels and component panels for the selected test."""
        panels = self._panel_manager.create_ship_panels(test_id, self)
        ship_panels, component_panels, tabbed_panel = panels
        self._viewmodel.update_ship_panels(ship_panels, component_panels, tabbed_panel)

    def _create_results_panel(self, test_id):
        """Create results panel for selected test."""
        callbacks = {
            'on_view_battle_states': self._on_view_battle_states,
            'on_use_seed': self._on_use_seed_from_run,
            'on_copy_results': self._on_copy_results,
        }
        panels = self._panel_manager.create_results_panel(
            test_id, self._viewmodel.ship_panels, self._viewmodel.tabbed_ship_panel, callbacks
        )
        results_panel, details_panel = panels
        self._viewmodel.update_results_panels(results_panel, details_panel)

    def _create_ui(self):
        """Create UI buttons."""
        self.btn_back, callbacks = self._panel_manager.create_ui_buttons(
            self.ui_manager, self._on_back
        )
        self._button_callbacks.update(callbacks)

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

                logger.debug(f"Storing visual test results for {self.selected_test_id}")
                self.registry.update_last_run_results(self.selected_test_id, scenario.results)

                # Add to persistent test history
                self.test_history.add_run(self.selected_test_id, scenario.results)

                # Refresh results panel if it exists
                if self._viewmodel.results_panel:
                    self._viewmodel.results_panel.set_test(self.selected_test_id)

        # Clear battle scene test state
        if hasattr(self.game.battle_scene, 'test_completed'):
            self.game.battle_scene.test_completed = False
        if hasattr(self.game.battle_scene, 'test_scenario'):
            self.game.battle_scene.test_scenario = None

        self.selected_test_id = None
        logger.debug("Test selection cleared")

    def _on_back(self):
        """Return to main menu via scene_callback (PROJ-65 pattern)."""
        if self.scene_callback:
            self.scene_callback("return_to_menu")

    # ─────────────────────────────────────────────────────────────────
    # Executor callback helpers
    # ─────────────────────────────────────────────────────────────────

    def _render_progress(self, title, subtitle, detail):
        """Render a progress overlay for headless test execution."""
        overlay = pygame.Surface((600, 200))
        overlay.fill(theme.BG_OVERLAY)
        pygame.draw.rect(overlay, theme.BORDER_ACTIVE, overlay.get_rect(), 3)

        header_font = get_font(24, FONT_MONO)
        body_font = get_font(18, FONT_MONO)
        small_font = get_font(14, FONT_MONO)

        title_text = header_font.render(title, True, theme.TEXT_WHITE)
        sub_text = body_font.render(subtitle, True, theme.TEXT_MUTED)
        detail_text = small_font.render(detail, True, theme.TEXT_DIM)

        overlay.blit(title_text, (300 - title_text.get_width()//2, 50))
        overlay.blit(sub_text, (300 - sub_text.get_width()//2, 90))
        overlay.blit(detail_text, (300 - detail_text.get_width()//2, 130))

        screen_center_x = self.game.screen.get_width() // 2
        screen_center_y = self.game.screen.get_height() // 2
        self.game.screen.blit(overlay, (screen_center_x - 300, screen_center_y - 100))

    def _draw_and_flip(self):
        """Draw current screen state with progress overlay and flip display."""
        self.game.screen.fill(theme.BG_PRIMARY)
        self.draw(self.game.screen)
        pygame.display.flip()

    def _get_engine(self):
        """Get the battle engine from battle scene."""
        return self.game.battle_scene.engine

    def _ensure_engine(self):
        """Ensure battle engine exists (create if needed)."""
        if self.game.battle_scene.engine is None:
            from game.ai.ai_factory import AIControllerFactory
            self.game.battle_scene._battle_service.create_battle(
                ai_factory=AIControllerFactory()
            )

    def _switch_to_battle(self, scenario):
        """Configure battle via controller and request scene transition.

        Uses the unified controller flow: creates BattleConfig, configures
        a BattleController, runs scenario.setup(), then hands the controller
        to BattleScreen.start_battle().
        """
        from game.simulation.battle_config import BattleConfig, BattleMode, ReturnDestination
        from game.simulation.battle_controller import BattleController
        from game.ai.ai_factory import AIControllerFactory

        config = BattleConfig(
            mode=BattleMode.TEST,
            start_paused=True,
            return_destination=ReturnDestination.TEST_LAB,
            show_results=True,
            test_scenario=scenario,
        )
        controller = BattleController(ai_factory=AIControllerFactory())
        controller.configure(config)

        # Scenario sets up ships, positions, AI strategies, and starts engine
        scenario.setup(controller.service.get_engine())
        controller._is_started = True  # Engine already started by scenario.setup()

        self.game.battle_scene.start_battle(controller)

        if self.scene_callback:
            self.scene_callback("start_test_battle", scenario=scenario)

    def _on_view_battle_states(self, run_record, run_number):
        """Open the battle state viewer for a test run."""
        from test_framework.battle_state_capture import load_battle_state_json

        initial_json = None
        final_json = None

        if run_record.initial_state_file:
            initial_json = load_battle_state_json(run_record.initial_state_file)
        if run_record.final_state_file:
            final_json = load_battle_state_json(run_record.final_state_file)

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
        """Copy the seed from a test run to the custom seed control."""
        self.controller.ui_state.set_custom_seed(seed)
        self.output_log.append(f"Seed set to: {seed}")

    def _on_copy_results(self, run_record, run_number):
        """Copy test results to clipboard."""
        lines = []
        lines.append(f"Test: {self.selected_test_id}")
        lines.append(f"Run #{run_number} - {run_record.get_formatted_timestamp()}")
        lines.append(f"Status: {'PASSED' if run_record.passed else 'FAILED'}")
        if run_record.seed is not None:
            lines.append(f"Seed: {run_record.seed}")
        lines.append("")

        lines.append("=== Test Metrics ===")
        for key, value in run_record.metrics.items():
            if key not in ['validation_results', 'validation_summary']:
                if isinstance(value, float):
                    value_str = f"{value:.4f}"
                else:
                    value_str = str(value)
                display_key = display_name(key)
                lines.append(f"  {display_key}: {value_str}")
        lines.append("")

        if run_record.validation_results:
            lines.append("=== Validation Results ===")
            for vr in run_record.validation_results:
                status = vr['status']
                name = vr['name']
                symbol = "V" if status == 'PASS' else "X"
                lines.append(f"{symbol} {name}: {status}")

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

    def _on_run_visual_baseline(self):
        """Run the baseline battle of a ComparisonScenario visually."""
        self._executor.run_visual_baseline(self.selected_test_id)

    def _on_run_headless(self):
        """Run the selected test scenario in headless mode (fast, no visuals)."""
        self.headless_running = True
        self._executor.run_headless(self.selected_test_id)
        self.headless_running = False
        # Refresh results panel if it exists
        if self._viewmodel.results_panel:
            self._viewmodel.results_panel.set_test(self.selected_test_id)

    def _on_run_all_tests(self):
        """Run all visible tests headlessly in sequence."""
        self._executor.run_all(self._get_filtered_scenarios())

    def _continue_batch_test(self):
        """Continue batch execution (called from event handler)."""
        self._executor.continue_batch()

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

    # ─────────────────────────────────────────────────────────────────
    # IScene Protocol
    # ─────────────────────────────────────────────────────────────────

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
            if event.type == pygame_gui.UI_BUTTON_PRESSED and hasattr(event, 'ui_element'):
                callback = self._button_callbacks.get(event.ui_element)
                if callback:
                    callback()
                    continue

            # Delegate to input handler
            filtered_scenarios = self._get_filtered_scenarios()
            self._input_handler.handle_event(
                event, filtered_scenarios, self.categories, self._executor
            )

    def update(self, dt: float = 0):
        """Update UI state (IScene protocol)."""
        # Update tabbed ship panel (hover states)
        if self._viewmodel.tabbed_ship_panel:
            self._viewmodel.tabbed_ship_panel.update()

        # Update ship panels (hover states)
        for panel in self._viewmodel.ship_panels:
            panel.update()

        # Update component panels (hover states)
        for panel in self._viewmodel.component_panels:
            panel.update()

        # Update results panel (hover states for buttons/cards)
        if self._viewmodel.results_panel:
            self._viewmodel.results_panel.update()

    def draw(self, screen):
        """Draw the Combat Lab UI."""
        # Delegate to renderer
        self._renderer.draw(
            surface=screen,
            viewmodel=self._viewmodel,
            controller=self.controller,
            registry=self.registry,
            categories=self.categories,
            filtered_scenarios=self._get_filtered_scenarios(),
            executor=self._executor,
            ui_manager=self.ui_manager
        )

        # Battle state viewer (drawn on top of everything)
        if self.battle_state_viewer and self.battle_state_viewer.visible:
            self.battle_state_viewer.draw(screen)

    # ─────────────────────────────────────────────────────────────────
    # Backward compatibility methods (kept for external callers)
    # ─────────────────────────────────────────────────────────────────

    def _show_ships_json(self, test_id):
        """Show JSON for all ships used in the test."""
        if test_id is None:
            return

        scenario_info = self.registry.get_by_id(test_id)
        if not scenario_info:
            return

        ships_data = {}
        metadata = scenario_info['metadata']

        ship_files = []
        for condition in metadata.conditions:
            if '.json' in condition and ('Attacker:' in condition or 'Target:' in condition):
                parts = condition.split(':')
                if len(parts) > 1:
                    filename = parts[1].strip()
                    ship_files.append(filename)

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

        popup = JSONPopup(f"Ships JSON - {test_id}", ships_data, WIDTH, HEIGHT, self.ui_manager)
        self._viewmodel.open_json_popup(popup)

    def _show_components_json(self):
        """Show JSON for all components in the test data."""
        components_path = os.path.join(get_test_data_dir(), 'components.json')

        components_data = load_json(components_path)
        if components_data is not None:
            popup = JSONPopup("Components JSON", components_data, WIDTH, HEIGHT, self.ui_manager)
        else:
            popup = JSONPopup(
                "Components JSON",
                {"error": "components.json not found or invalid"},
                WIDTH, HEIGHT, self.ui_manager
            )
        self._viewmodel.open_json_popup(popup)
