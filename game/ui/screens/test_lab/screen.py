"""
TestLabScreen - Combat Lab UI main screen.

This module contains the main TestLabScreen class which orchestrates
the Combat Lab interface for viewing and running test scenarios.

PROJ-172: Refactored to MVVM architecture with ViewModel, Renderer, and InputHandler.

This screen follows the MVVM pattern documented in
`docs/03_CONVENTIONS.md § 2.4 UI Screen Line Budget`. Target: keep the
class under 300 lines — delegate logic to ViewModel / Renderer /
InputHandler / Controller. FleetBattleSetupScreen is the sibling exemplar.
"""
from __future__ import annotations

from typing import Any, Callable, TYPE_CHECKING
import pygame
import pygame_gui

from game.ui.pygame_gui_patch import StarshipUIManager

if TYPE_CHECKING:
    from game.ui.screens.battle_screen import BattleScreen
import os

from game.ui.fonts import get_font, FONT_MONO
from game.ui.screens.test_lab import theme
from game.core.config import DisplayConfig
from game.core.string_utils import display_name
WIDTH, HEIGHT = DisplayConfig.DEFAULT_WIDTH, DisplayConfig.DEFAULT_HEIGHT
from game.core.json_utils import load_json
from combat_lab.registry import TestRegistry
from combat_lab.test_history import TestHistory
from combat_lab.logging_config import get_logger

# Intra-package imports
from .dialogs import JSONPopup
from .data_extractor import TestLabDataExtractor, get_test_data_dir
from .panel_manager import TestLabPanelManager
from .test_executor import TestLabExecutor
from .viewmodel import TestLabViewModel
from .renderer import TestLabRenderer
from .screen_actions import TestLabScreenActions
from .screen_input_handler import TestLabInputHandler
from game.ui.screens.builder.event_bus import WorkshopEventBus

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

    def __init__(
        self,
        screen_width: int,
        screen_height: int,
        battle_scene: "BattleScreen",
        scene_callback: Callable[..., None] | None = None,
    ) -> None:
        """Initialize test lab screen.

        Args:
            screen_width: Display width in pixels.
            screen_height: Display height in pixels.
            battle_scene: BattleScreen instance used for engine access during
                test execution and as the visual-mode battle target.
            scene_callback: Callback function for scene transitions.
                Called with (action, **kwargs) where action is:
                - "start_test_battle": Start visual test battle with scenario kwarg
                - "return_to_menu": Return to main menu
        """
        self.battle_scene = battle_scene
        self.scene_callback = scene_callback
        self.screen_width = screen_width
        self.screen_height = screen_height

        # pygame_gui UIManager for buttons
        self.ui_manager = StarshipUIManager((self.screen_width, self.screen_height))
        self._button_callbacks = {}  # Maps UIButton -> callback function

        # Initialize controller (handles all business logic)
        from combat_lab.services.test_lab_controller import TestLabUIController
        self.registry = TestRegistry()
        self.test_history = TestHistory()
        self.controller = TestLabUIController(self.registry, self.test_history)

        # Data extraction helper (ships, components from test scenarios)
        self._data_extractor = TestLabDataExtractor(self.registry)

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


        # PROJ-457 Phase 3: test execution + result viewers extracted to
        # TestLabScreenActions. Instantiated here so `_executor` /
        # `_input_handler` callback dicts below can point at its methods.
        self._actions = TestLabScreenActions(self)

        # Test executor (handles visual, headless, and batch test runs)
        self._executor = TestLabExecutor(
            registry=self.registry,
            test_history=self.test_history,
            controller=self.controller,
            render_progress=self._actions._render_progress,
            draw_and_flip=self._actions._draw_and_flip,
            get_engine=self._actions._get_engine,
            ensure_engine=self._actions._ensure_engine,
            switch_to_battle=self._actions._switch_to_battle,
            output_log=self.output_log,
        )

        # Get categories for sidebar
        self.categories = self.registry.get_categories()

        # MVVM Components
        self._event_bus = WorkshopEventBus()
        self._viewmodel = TestLabViewModel(self._event_bus)
        self._renderer = TestLabRenderer()
        self._input_handler = TestLabInputHandler(
            viewmodel=self._viewmodel,
            controller=self.controller,
            registry=self.registry,
            callbacks={
                'on_run': self._actions._on_run,
                'on_run_headless': self._actions._on_run_headless,
                'on_run_visual_baseline': self._actions._on_run_visual_baseline,
                'on_run_all': self._actions._on_run_all_tests,
                'create_ship_panels': self._create_ship_panels,
                'create_results_panel': self._create_results_panel,
                'prompt_custom_seed': self._actions._prompt_for_custom_seed,
                'continue_batch': self._actions._continue_batch_test,
            }
        )

        # Battle state viewer (for viewing initial/final JSON states)
        from game.ui.screens.battle_state_viewer import BattleStateViewer
        self.battle_state_viewer = BattleStateViewer(self.screen_width, self.screen_height)

        self._create_ui()

    # ─────────────────────────────────────────────────────────────────
    # Property delegates to controller.ui_state (backward compatibility)
    # ─────────────────────────────────────────────────────────────────

    @property
    def selected_category(self) -> Any:
        return self.controller.ui_state.get_selected_category()

    @selected_category.setter
    def selected_category(self, value) -> None:
        self.controller.ui_state.select_category(value)

    @property
    def selected_test_id(self) -> Any:
        return self.controller.ui_state.get_selected_test_id()

    @selected_test_id.setter
    def selected_test_id(self, value) -> None:
        self.controller.ui_state.select_test(value)

    @property
    def category_hover(self) -> Any:
        return self.controller.ui_state.get_category_hover()

    @category_hover.setter
    def category_hover(self, value) -> None:
        self.controller.ui_state.set_category_hover(value)

    @property
    def test_hover(self) -> Any:
        return self.controller.ui_state.get_test_hover()

    @test_hover.setter
    def test_hover(self, value) -> None:
        self.controller.ui_state.set_test_hover(value)

    @property
    def headless_running(self) -> Any:
        return self.controller.ui_state.is_headless_running()

    @headless_running.setter
    def headless_running(self, value) -> None:
        self.controller.ui_state.set_headless_running(value)

    @property
    def output_log(self) -> Any:
        return self.controller.output_log

    @property
    def all_scenarios(self) -> Any:
        return self.controller.all_scenarios

    @property
    def batch_running(self) -> Any:
        """Delegate batch_running to executor."""
        return self._executor.batch_running

    @property
    def batch_current_index(self) -> Any:
        """Delegate batch_current_index to executor."""
        return self._executor.batch_current_index

    @property
    def batch_total(self) -> Any:
        """Delegate batch_total to executor."""
        return self._executor.batch_total

    # ─────────────────────────────────────────────────────────────────
    # ViewModel panel accessors (backward compatibility)
    # ─────────────────────────────────────────────────────────────────

    @property
    def ship_panels(self) -> Any:
        return self._viewmodel.ship_panels

    @property
    def component_panels(self) -> Any:
        return self._viewmodel.component_panels

    @property
    def tabbed_ship_panel(self) -> Any:
        return self._viewmodel.tabbed_ship_panel

    @property
    def results_panel(self) -> Any:
        return self._viewmodel.results_panel

    @property
    def test_details_panel(self) -> Any:
        return self._viewmodel.test_details_panel

    @property
    def json_popup(self) -> Any:
        return self._viewmodel.json_popup

    @property
    def confirmation_dialog(self) -> Any:
        return self._viewmodel.confirmation_dialog

    # ─────────────────────────────────────────────────────────────────
    # Delegate methods
    # ─────────────────────────────────────────────────────────────────

    def _extract_ships_from_scenario(self, test_id) -> Any:
        """Extract ship information from test scenario metadata."""
        return self._data_extractor.extract_ships(test_id)

    def _load_component_data(self, component_id) -> Any:
        """Load component JSON from components.json by ID."""
        return self._data_extractor.load_component(component_id)

    def _create_ship_panels(self, test_id) -> None:
        """Create ship panels and component panels for the selected test."""
        panels = self._panel_manager.create_ship_panels(test_id, self)
        ship_panels, component_panels, tabbed_panel = panels
        self._viewmodel.update_ship_panels(ship_panels, component_panels, tabbed_panel)

    def _create_results_panel(self, test_id) -> None:
        """Create results panel for selected test."""
        callbacks = {
            'on_view_battle_states': self._actions._on_view_battle_states,
            'on_use_seed': self._actions._on_use_seed_from_run,
            'on_copy_results': self._actions._on_copy_results,
        }
        panels = self._panel_manager.create_results_panel(
            test_id, self._viewmodel.ship_panels, self._viewmodel.tabbed_ship_panel, callbacks
        )
        results_panel, details_panel = panels
        self._viewmodel.update_results_panels(results_panel, details_panel)

    def _create_ui(self) -> None:
        """Create UI buttons."""
        self.btn_back, callbacks = self._panel_manager.create_ui_buttons(
            self.ui_manager, self._on_back
        )
        self._button_callbacks.update(callbacks)

    def _get_filtered_scenarios(self) -> Any:
        """Get scenarios filtered by selected category/group and tags."""
        # Start with category or group filter
        selected_group = self.controller.ui_state.get_selected_group()
        if self.selected_category is not None:
            scenarios = self.registry.get_by_category(self.selected_category)
        elif selected_group is not None:
            scenarios = self.registry.get_by_group(selected_group)
        else:
            scenarios = self.all_scenarios

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

    def reset_selection(self) -> None:
        """Preserve test selection on return from battle.

        Called when returning from a Combat Lab visual run. The
        ``self.battle_scene.test_scenario`` capture path was retired in
        PROJ-397 (the dead-var sweep) — visual-run results are now
        recorded directly by the test framework in `_run_single_tick`,
        not lifted off the BattleScreen here. This method now only
        preserves the selected_test_id so the row stays highlighted.
        """
        logger.debug(f"Returned from battle, test selection preserved: {self.selected_test_id}")

    def _on_back(self) -> None:
        """Return to main menu via scene_callback (PROJ-65 pattern)."""
        if self.scene_callback:
            self.scene_callback("return_to_menu")
    def handle_event(self, event) -> None:
        """Handle a single pygame event (IScene protocol)."""
        self.handle_input([event])

    def handle_resize(self, width: int, height: int) -> None:
        """Handle window resize (IScene protocol)."""
        self.screen_width = width
        self.screen_height = height
        self.ui_manager.set_window_resolution((width, height))
        self.battle_state_viewer.handle_resize(width, height)
        self._create_ui()

    def handle_input(self, events) -> None:
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

    def update(self, dt: float = 0) -> None:
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

    def draw(self, screen) -> None:
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
