"""Strategy UI event routing and handling.

This module contains the StrategyEventRouter class that handles all event
routing for the StrategyUI, including button presses, window management,
and click handling.

PROJ-86: God Class Decomposition - UI Tier
"""
from __future__ import annotations

from typing import TYPE_CHECKING

import pygame
import pygame_gui

from game.core.logger import log_debug
from game.core.protocols import is_fleet

if TYPE_CHECKING:
    from game.ui.screens.strategy_ui import StrategyUI


class StrategyEventRouter:
    """Routes and handles events for the StrategyUI.

    Extracted from StrategyUI to reduce god class size. Handles:
    - pygame_gui UI_BUTTON_PRESSED events
    - Menu panel open/close via Escape and click-outside
    - Window close events
    - Tree panel events
    - Click handling for sidebar and modal detection

    Args:
        ui: Reference to the parent StrategyUI instance.
    """

    def __init__(self, ui: 'StrategyUI'):
        """Initialize the event router.

        Args:
            ui: The parent StrategyUI instance.
        """
        self.ui = ui

    def has_modal_open(self) -> bool:
        """Check if any modal sub-panel is currently open.

        Returns:
            True if any modal window or panel is open, False otherwise.
        """
        # Check for menu panel (PROJ-72)
        if self.ui.menu_panel:
            return True

        # Check for build queue screen
        if hasattr(self.ui.scene, 'build_queue_screen') and self.ui.scene.build_queue_screen is not None:
            return True

        # Check window manager for open windows (PROJ-86)
        wm = self.ui._window_manager
        if wm.fleet_orders_window is not None:
            return True
        if wm.planet_list_window is not None:
            return True
        if wm.fleet_report_window is not None:
            return True
        if wm.transfer_dialog is not None:
            return True
        if wm.build_queue_list_window is not None:
            return True
        if wm.empire_build_queue_window is not None:
            return True
        if wm.event_log_window is not None:
            return True

        # Check if workshop is being opened
        if hasattr(self.ui.scene, 'action_open_design') and self.ui.scene.action_open_design:
            return True

        return False

    def on_ui_selection(self, obj) -> None:
        """Handle selection of an object from any UI panel.

        Args:
            obj: The selected object (Planet, Fleet, etc.).
        """
        if hasattr(self.ui.scene, 'on_ui_selection'):
            self.ui.scene.on_ui_selection(obj)

    def route_event(self, event) -> None:
        """Route an event through the StrategyUI event handling chain.

        This is the main entry point for event handling. Processes pygame_gui
        events, tree panel events, button presses, and window close events.

        Args:
            event: The pygame event to process.
        """
        self.ui.manager.process_events(event)
        # PROJ-86: Use window manager for UI callbacks
        self.ui._window_manager.process_ui_callbacks(event)

        # Pass generic events to orders window if active (e.g. for confirmation dialogs)
        if self.ui._window_manager.fleet_orders_window:
            self.ui._window_manager.fleet_orders_window.handle_global_event(event)

        # Close menu panel on Escape
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE and self.ui.menu_panel:
            self.ui.close_menu_panel()
            return

        # Close menu panel on click outside
        if event.type == pygame.MOUSEBUTTONDOWN and self.ui.menu_panel:
            panel_rect = self.ui.menu_panel.get_abs_rect()
            menu_btn_rect = self.ui.btn_menu.get_abs_rect()
            if not panel_rect.collidepoint(event.pos) and not menu_btn_rect.collidepoint(event.pos):
                self.ui.close_menu_panel()

        if self.ui.system_tree.process_event(event):
            pass

        if self.ui.sector_tree.process_event(event):
            pass

        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            self._handle_button_pressed(event)

        # Handle quit-to-menu confirmation (PROJ-72)
        if event.type == pygame_gui.UI_CONFIRMATION_DIALOG_CONFIRMED:
            if hasattr(self.ui.scene, '_quit_confirm_dialog') and event.ui_element == self.ui.scene._quit_confirm_dialog:
                self.ui.scene._handle_quit_confirmed()

        # PROJ-86: Handle window close via window manager
        if event.type == pygame_gui.UI_WINDOW_CLOSE:
            self._handle_window_close(event)

    def _handle_button_pressed(self, event) -> None:
        """Handle UI_BUTTON_PRESSED events.

        Args:
            event: The pygame_gui button pressed event.
        """
        ui = self.ui

        if event.ui_element == ui.btn_planets:
            ui.open_planet_list()
        elif event.ui_element == ui.btn_design:
            if hasattr(ui.scene, 'on_design_click'):
                ui.scene.on_design_click()
        elif event.ui_element == ui.btn_build_queues:
            ui.open_build_queue_list()
        elif event.ui_element == ui.btn_all_queues:
            ui.open_empire_build_queue_window()
        elif event.ui_element == ui.btn_menu:
            ui.toggle_menu_panel()
        elif event.ui_element == ui.btn_events:
            ui.open_event_log()
        elif event.ui_element == ui.btn_raw_data:
            ui.show_raw_data_popup()
        elif event.ui_element == ui.btn_colonize:
            self._handle_colonize_button()
        elif event.ui_element == ui.btn_orders:
            obj = ui.current_selection
            if obj and is_fleet(obj):
                ui.open_orders_window(obj)
        elif event.ui_element == ui.btn_fleet_report:
            obj = ui.current_selection
            if obj and is_fleet(obj):
                ui.open_fleet_report_window(obj)
        # NOTE: btn_build_yard is handled in strategy_input_handler.py - do not duplicate here

    def _handle_colonize_button(self) -> None:
        """Handle the Colonize button press.

        Finds uncolonized planets at the selected fleet's location and
        either issues a colonize order directly (single planet) or
        prompts for planet selection (multiple planets).
        """
        ui = self.ui
        obj = ui.current_selection

        if not obj or not is_fleet(obj):
            return

        # Find Uncolonized Planets at Fleet Location
        from game.core.hex_math import hex_distance  # noqa: F401

        if not hasattr(ui.scene, 'galaxy'):
            return

        # Find System
        system = ui.scene.galaxy.get_system_of_object(obj)
        if not system:
            log_debug("Colonize: Fleet not in system?")
            return

        # Find planets at this location (SYSTEM)
        candidates = []
        for p in system.planets:
            # Any planet in system is reachable if fleet is at system
            if p.owner_id is None:  # Unowned
                candidates.append(p)

        if not candidates:
            log_debug("No unowned planets at this location.")
            return

        if len(candidates) == 1:
            # Single candidate, order directly
            if hasattr(ui.scene, 'request_colonize_order'):
                ui.scene.request_colonize_order(obj, candidates[0])
        else:
            # Multiple -> Dialog
            def on_planet_selected(planet):
                if hasattr(ui.scene, 'request_colonize_order'):
                    ui.scene.request_colonize_order(obj, planet)

            ui.prompt_planet_selection(candidates, on_planet_selected)

    def _handle_window_close(self, event) -> None:
        """Handle UI_WINDOW_CLOSE events.

        Args:
            event: The pygame_gui window close event.
        """
        wm = self.ui._window_manager

        if event.ui_element == wm.fleet_orders_window:
            wm.fleet_orders_window = None
        elif event.ui_element == wm.fleet_report_window:
            wm.fleet_report_window = None
        elif event.ui_element == wm.transfer_dialog:
            wm.transfer_dialog = None
        elif event.ui_element == wm.build_queue_list_window:
            wm.build_queue_list_window = None
        elif event.ui_element == wm.empire_build_queue_window:
            wm._on_empire_build_queue_closed()
        elif event.ui_element == wm.event_log_window:
            wm._on_event_log_closed()

    def process_custom_events(self, event) -> None:
        """Process custom UI events from window callbacks.

        Args:
            event: The pygame event to check for custom UI callbacks.
        """
        # Custom UI callbacks are processed via window manager
        self.ui._window_manager.process_ui_callbacks(event)

    def handle_click(self, mx: int, my: int, button: int) -> bool:
        """Handle mouse clicks.

        Args:
            mx: Mouse x coordinate.
            my: Mouse y coordinate.
            button: Mouse button number.

        Returns:
            True if click was handled by UI, False otherwise.
        """
        # 1. Check logical sidebar area
        if mx > self.ui.width - self.ui.sidebar_width:
            return True

        # 2. Check if ANY UI element is being hovered (e.g. windows, modals)
        # This prevents clicking "through" the planet selection window to the map
        if self.ui.manager.get_hovering_any_element():
            return True

        return False
