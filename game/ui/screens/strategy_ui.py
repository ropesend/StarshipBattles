"""Strategy interface for the strategy screen.

Cross-layer imports (acceptable for UI):
- Protocols: Runtime - duck typing for object identification

PROJ-86: Decomposed into helper modules:
- strategy_panel_manager.py: Panel creation and resize
- strategy_event_router.py: Event routing and handling
- strategy_window_manager.py: Window lifecycle management
- strategy_detail_formatter.py: Detail panel formatting
"""
from __future__ import annotations

import os
from typing import Optional

import pygame
import pygame_gui
from game.ui.config import UIConfig
from game.ui.fonts import get_font
from game.core.paths import Paths
from game.core.resources import ResourceCatalog
from game.ui.screens.build_queue_helpers import RESOURCE_ABBREVS

_PLANETARY_IDS = [d.id for d in ResourceCatalog.from_json().by_display_group("planetary")]
from game.ui.screens.strategy_menu_panel import StrategyMenuPanel, PANEL_WIDTH, PANEL_HEIGHT
from game.ui.screens.strategy_window_manager import StrategyWindowManager
from game.ui.screens.strategy_detail_formatter import StrategyDetailFormatter
from game.ui.screens.strategy_panel_manager import (
    create_strategy_panels,
    resize_strategy_panels,
    apply_hotkey_tooltips,
)
from game.ui.screens.strategy_event_router import StrategyEventRouter
from game.ui.colors import WHITE

class StrategyUI:
    """Handles all UI rendering and interaction for the StrategyScreen.

    PROJ-86: Decomposed into helper modules:
    - strategy_panel_manager: Panel creation and layout
    - strategy_event_router: Event routing and handling
    - strategy_window_manager: Window lifecycle management
    - strategy_detail_formatter: Detail panel formatting
    """

    def __init__(self, scene, screen_width, screen_height, input_mapper=None):
        self.scene = scene
        self.width = screen_width
        self.height = screen_height
        self._mapper = input_mapper
        self.sidebar_width = UIConfig.STRATEGY_SIDEBAR_WIDTH

        # PROJ-86: Window state managed by StrategyWindowManager
        # Only keep references needed by local logic
        self.planet_report_panel = None  # planet report panel instance (PROJ-54)
        self.menu_panel = None           # strategy menu dropdown (PROJ-72)

        # UI State
        theme_path = os.path.join(Paths.DATA_DIR, 'builder_theme.json')
        self.manager = pygame_gui.UIManager((screen_width, screen_height), theme_path=theme_path)
        self.manager.preload_fonts([
            {'name': 'noto_sans', 'point_size': 14, 'style': 'bold', 'antialiased': 1}
        ])

        # PROJ-86: Create all panels and widgets via panel manager
        widgets = create_strategy_panels(
            self.manager, screen_width, screen_height,
            self.sidebar_width, self.on_ui_selection
        )

        # Unpack widget references onto self
        self.system_panel = widgets.system_panel
        self.sector_panel = widgets.sector_panel
        self.detail_panel = widgets.detail_panel
        self.top_bar = widgets.top_bar
        self.resource_bar = widgets.resource_bar
        self.system_header = widgets.system_header
        self.system_tree = widgets.system_tree
        self.sector_header = widgets.sector_header
        self.sector_tree = widgets.sector_tree
        self.portrait_image = widgets.portrait_image
        self.detail_text = widgets.detail_text
        self.graph_image = widgets.graph_image
        self.graph_rect = widgets.graph_rect
        self.btn_raw_data = widgets.btn_raw_data
        self.btn_colonize = widgets.btn_colonize
        self.btn_build_yard = widgets.btn_build_yard
        self.btn_planet_orders = widgets.btn_planet_orders  # PROJ-238
        self.btn_orders = widgets.btn_orders
        self.btn_fleet_report = widgets.btn_fleet_report
        self.btn_build_fleet = widgets.btn_build_fleet
        self.btn_prev_colony = widgets.btn_prev_colony
        self.lbl_colony = widgets.lbl_colony
        self.btn_next_colony = widgets.btn_next_colony
        self.btn_prev_fleet = widgets.btn_prev_fleet
        self.lbl_fleet = widgets.lbl_fleet
        self.btn_next_fleet = widgets.btn_next_fleet
        self.btn_planets = widgets.btn_planets
        self.btn_stars = widgets.btn_stars
        self.btn_empire = widgets.btn_empire
        self.btn_research = widgets.btn_research
        self.btn_design = widgets.btn_design
        self.btn_build_queues = widgets.btn_build_queues
        self.btn_all_queues = widgets.btn_all_queues
        self.btn_menu = widgets.btn_menu
        self.btn_events = widgets.btn_events
        self.btn_next_turn = widgets.btn_next_turn
        self.lbl_current_player = widgets.lbl_current_player
        self.lbl_resources = widgets.lbl_resources
        self.spectrum_graph = widgets.spectrum_graph
        self.atmosphere_graph = widgets.atmosphere_graph
        self.panels = widgets.panels

        # State
        self.current_raw_data = ""
        self.current_sector_objects = {}
        self.current_selection = None

        # Apply hotkey tooltips to buttons (PROJ-71)
        self._apply_hotkey_tooltips()
        self._update_resource_display()

        # PROJ-86: Initialize detail formatter
        self._detail_formatter = StrategyDetailFormatter(
            scene=self.scene,
            manager=self.manager,
            detail_panel=self.detail_panel,
            widgets={
                'portrait_image': self.portrait_image,
                'detail_text': self.detail_text,
                'graph_image': self.graph_image,
                'btn_raw_data': self.btn_raw_data,
                'btn_colonize': self.btn_colonize,
                'btn_build_yard': self.btn_build_yard,
                'btn_planet_orders': self.btn_planet_orders,  # PROJ-238
                'btn_orders': self.btn_orders,
                'btn_fleet_report': self.btn_fleet_report,
                'btn_build_fleet': self.btn_build_fleet,
            },
            graphs={
                'spectrum_graph': self.spectrum_graph,
                'atmosphere_graph': self.atmosphere_graph,
            },
            graph_rect=self.graph_rect,
            screen_size=(screen_width, screen_height),
        )

        # PROJ-86: Initialize window manager
        self.window_manager = StrategyWindowManager(
            scene=self.scene,
            manager=self.manager,
            width=self.width,
            height=self.height,
            input_mapper=self._mapper,
            asset_resolver=self._get_object_asset,
        )

        # PROJ-86: Initialize event router
        self._event_router = StrategyEventRouter(self)

    # =========================================================================
    # Hotkey Tooltip Enrichment (PROJ-71)
    # =========================================================================

    def _apply_hotkey_tooltips(self) -> None:
        """Apply hotkey hint tooltips to strategy UI buttons."""
        apply_hotkey_tooltips(self, self._mapper)

    # =========================================================================
    # Menu Panel Management (PROJ-72)
    # =========================================================================

    def toggle_menu_panel(self):
        """Toggle the strategy menu dropdown panel open/closed."""
        if self.menu_panel:
            self.close_menu_panel()
        else:
            self.open_menu_panel()

    def open_menu_panel(self):
        """Open the strategy menu dropdown panel below the Menu button."""
        btn_rect = self.btn_menu.get_abs_rect()
        panel_rect = pygame.Rect(btn_rect.x, btn_rect.bottom + 2, PANEL_WIDTH, PANEL_HEIGHT)
        self.menu_panel = StrategyMenuPanel(panel_rect, self.manager, self._on_menu_option_selected)

    def close_menu_panel(self):
        """Close and destroy the strategy menu dropdown panel."""
        if self.menu_panel:
            self.menu_panel.kill()
            self.menu_panel = None

    def _on_menu_option_selected(self, option):
        """Handle a menu option selection from the dropdown panel.

        Args:
            option: The option identifier string from StrategyMenuPanel.
        """
        self.close_menu_panel()
        self.scene.on_menu_option(option)

    # =========================================================================
    # Visibility
    # =========================================================================

    def hide_ui(self):
        """Hide all main strategy UI panels."""
        for panel in self.panels:
            panel.hide()

    def show_ui(self):
        """Show all main strategy UI panels."""
        for panel in self.panels:
            panel.show()

        # BUG-26: Re-layout tree panels to ensure proper positioning after hide/show
        if self.system_tree:
            self.system_tree.layout()
        if self.sector_tree:
            self.sector_tree.layout()


        
    def handle_resize(self, width, height):
        """Update UI elements for new resolution."""
        self.width = width
        self.height = height
        self.manager.set_window_resolution((width, height))

        # PROJ-86: Delegate panel resize to panel manager
        resize_strategy_panels(self, self.manager, width, height, self.sidebar_width)

        # PROJ-86: Update detail formatter with new dimensions
        self._detail_formatter.update_screen_size(width, height)
        self._detail_formatter.update_graph_rect(self.graph_rect)
        self._detail_formatter.update_graphs(self.spectrum_graph, self.atmosphere_graph)

        # PROJ-86: Update window manager with new dimensions
        self.window_manager.handle_resize(width, height)

    def show_system_info(self, system_obj, contents):
        """Populate Top List (System) using Tree View."""
        if system_obj:
            self.system_header.set_text(f"System: {system_obj.name}")
        else:
            self.system_header.set_text("Deep Space (No System)")
            
        self.system_tree.set_items(contents, self)

    def show_sector_info(self, hex_coord, contents):
        """Populate Middle List (Sector/Hex)."""
        self.sector_header.set_text(f"Sector: [{hex_coord.q}, {hex_coord.r}]")
        
        # Use Tree Panel now with flat view
        self.sector_tree.set_items(contents, self, flat_view=True)
        
    def _get_label_for_obj(self, obj):
        return self._detail_formatter._get_label_for_obj(obj)

    def _get_object_asset(self, obj):
        """Proxy to scene for asset resolution."""
        return self.scene._get_object_asset(obj)
        
    def _format_spectrum(self, star):
        return self._detail_formatter._format_spectrum(star)

    def _compute_planet_production(self, planet) -> dict:
        """Compute per-resource production rates for a colony planet."""
        return self._detail_formatter.compute_planet_production(planet)

    def show_raw_data_popup(self):
        """Show raw data in a message window."""
        self._detail_formatter.show_raw_data_popup()

    def show_detailed_report(self, obj, portrait_surface=None):
        """Update the detail report for the selected object."""
        self._detail_formatter.show_detailed_report(obj, portrait_surface)
        # Sync state back from formatter for event handlers that access it
        self.planet_report_panel = self._detail_formatter.planet_report_panel
        self.current_selection = self._detail_formatter.current_selection
        self.current_raw_data = self._detail_formatter.current_raw_data

    def _format_atmosphere_raw(self, planet):
        return self._detail_formatter._format_atmosphere_raw(planet)

        
    def _update_resource_display(self):
        """Update the empire resource bar with current pool values."""
        # Guard: current_player_index may not be set during init
        if not hasattr(self.scene, 'current_player_index'):
            return
        if not self.scene.current_empire:
            return
        empire = self.scene.current_empire

        parts = []
        for res in _PLANETARY_IDS:
            current = empire.get_resource(res)
            cap = empire.max_storage.get(res, 0.0)
            abbr = RESOURCE_ABBREVS.get(res, res[:3])
            if cap > 0:
                parts.append(f"{abbr}: {int(current)}/{int(cap)}")
            elif current > 0:
                parts.append(f"{abbr}: {int(current)}")

        if parts:
            self.lbl_resources.set_text("  |  ".join(parts))
        else:
            self.lbl_resources.set_text("No resources")

    def update(self, dt):
        """Update UI logic."""
        self.manager.update(dt)
        self._update_resource_display()
 
    def draw(self, screen):
        """Draw the strategy scene UI elements."""
        self.manager.draw_ui(screen)

        # Only draw zoom indicator if strategy layer has focus (no sub-panels open)
        if not self._has_modal_open():
            font = get_font(20)
            mode_text = font.render(f"Strategy Layer | Zoom: {self.scene.camera.zoom:.2f}", True, WHITE)
            screen.blit(mode_text, (20, self.height - 30))

    def _has_modal_open(self) -> bool:
        """Check if any modal sub-panel is currently open."""
        return self._event_router.has_modal_open()

    def on_ui_selection(self, obj):
        """Handle selection of an object from any UI panel."""
        self._event_router.on_ui_selection(obj)

    def handle_event(self, event):
        """Pass events to pygame_gui and handle custom UI logic."""
        self._event_router.route_event(event)

    def handle_click(self, mx, my, button):
        """Handle mouse clicks. Returns True if click was handled by UI."""
        return self._event_router.handle_click(mx, my, button)


        
    # =========================================================================
    # Window Management Delegation (PROJ-86)
    # =========================================================================

    def prompt_planet_selection(self, planets, on_select):
        """Open a modal window to select a planet."""
        self.window_manager.prompt_planet_selection(planets, on_select)

    def prompt_fleet_selection(self, fleets, on_select):
        """Open a modal window to select a fleet to join."""
        self.window_manager.prompt_fleet_selection(fleets, on_select)

    def show_system_picker(self, systems, current_system, on_selected):
        """Open a modal window to select a star system for warp point creation."""
        self.window_manager.open_system_selection(systems, current_system, on_selected)

    def prompt_move_choice(self, fleet, target_hex, on_move_sector, on_intercept_fleet):
        """Dialog to choose between moving to the sector or intercepting the fleet."""
        self.window_manager.prompt_move_choice(fleet, target_hex, on_move_sector, on_intercept_fleet)

    def open_planet_list(self):
        """Open the Planet List Window."""
        self.window_manager.open_planet_list()

    def open_star_list(self):
        """Open the Star List Window."""
        self.window_manager.open_star_list()

    def open_build_queue_list(self):
        """Open the Build Queue List Window (BUG-67)."""
        self.window_manager.open_build_queue_list()

    def open_empire_build_queue_window(self):
        """Open the Empire-Wide Build Queue Window (PROJ-76)."""
        self.window_manager.open_empire_build_queue_window()

    def close_empire_build_queue_window(self):
        """Close the Empire-Wide Build Queue Window if open."""
        self.window_manager.close_empire_build_queue_window()

    def open_event_log(self):
        """Open the Event Log Window showing all events (PROJ-77)."""
        self.window_manager.open_event_log()

    def open_event_log_with_events(self, events: list):
        """Open the Event Log Window with a specific event list."""
        self.window_manager.open_event_log_with_events(events)

    def open_orders_window(self, entity, entity_type: str = "fleet"):
        """Open the Orders Window for a fleet or planet.

        PROJ-238: Generalized to support any IOrderable entity.
        """
        self.window_manager.open_orders_window(entity, entity_type=entity_type)

    def open_fleet_report_window(self, fleet):
        """Open the Fleet Report Window."""
        self.window_manager.open_fleet_report_window(fleet)

    def open_transfer_dialog(self, source_fleet, hex_coord):
        """Open the cargo/population transfer dialog."""
        self.window_manager.open_transfer_dialog(source_fleet, hex_coord)

    def open_cargo_quick_dialog(self, fleet, hex_coord, direction: str):
        """Open the quick cargo drop/load dialog (PROJ-100)."""
        self.window_manager.open_cargo_quick_dialog(fleet, hex_coord, direction)

    def open_empire_panel(self):
        """Open the Empire Panel Window."""
        self.window_manager.open_empire_panel()

    def show_confirmation_dialog(
        self, title: str, message: str, on_confirm, is_warning: bool = False
    ):
        """Show a confirmation dialog for dangerous actions.

        PROJ-198: Used by superweapons for planet/star destruction confirmation.

        Args:
            title: Dialog window title.
            message: Message to display (can be multi-line).
            on_confirm: Callback when user confirms.
            is_warning: If True, indicates a dangerous/irreversible action.
        """
        self.window_manager.show_confirmation_dialog(title, message, on_confirm, is_warning)

    def show_ship_picker(self, ships, ability_name: str, on_selected):
        """Show ship picker dialog for multi-select.

        PROJ-198: Used by superweapons for self-destruct ship selection.
        Currently auto-selects all ships; full picker dialog is a future enhancement.

        Args:
            ships: List of ships to pick from.
            ability_name: Ability name (for display).
            on_selected: Callback with list of selected ship IDs.
        """
        self.window_manager.show_ship_picker(ships, ability_name, on_selected)
