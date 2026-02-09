"""Strategy interface for the strategy screen.

Cross-layer imports (acceptable for UI):
- Protocols: Runtime - duck typing for object identification
"""
from __future__ import annotations

import os
from typing import Optional

import pygame
import pygame_gui
from game.core.logger import log_debug
from game.core.config import UIConfig
from game.core.input_actions import InputAction
from game.core.protocols import (
    is_star_system, is_star, is_planet, is_fleet,
    is_warp_point, is_sector_environment
)
from game.ui.screens.planet_selection_window import PlanetSelectionWindow
from game.ui.screens.planet_list_window import PlanetListWindow
from game.ui.screens.fleet_orders_window import FleetOrdersWindow
from game.ui.screens.fleet_report_window import FleetReportWindow
from game.ui.screens.build_queue_list_window import BuildQueueListWindow
from game.ui.screens.strategy_menu_panel import StrategyMenuPanel, PANEL_WIDTH, PANEL_HEIGHT
from game.ui.screens.empire_build_queue_window import EmpireBuildQueueWindow
from game.ui.screens.event_log_window import EventLogWindow
from game.core.paths import Paths
from game.ui.panels.strategy_widgets import SpectrumGraph, AtmosphereGraph
from game.ui.panels.system_tree_panel import SystemTreePanel
from game.ui.panels.planet_report_panel import PlanetReportPanel
from game.ui.screens.strategy_detail_fmt import (
    format_spectrum_html, format_atmosphere_raw, get_label_for_object,
    format_fleet_info
)
from game.core.constants import PLANET_RESOURCES
import pygame_gui.windows
import pygame_gui.elements as ui

class StrategyUI:
    """Handles all UI rendering and interaction for the StrategyScreen."""

    def __init__(self, scene, screen_width, screen_height, input_mapper=None):
        self.scene = scene
        self.width = screen_width
        self.height = screen_height
        self._mapper = input_mapper
        self.sidebar_width = UIConfig.STRATEGY_SIDEBAR_WIDTH
        self.fleet_orders_window = None  # active window instance
        self.planet_list_window = None   # planet list window instance (BUG-22)
        self.build_queue_list_window = None  # build queue list window (BUG-67)
        self.fleet_report_window = None  # fleet report window instance (PROJ-03)
        self.planet_report_panel = None  # planet report panel instance (PROJ-54)
        self.transfer_dialog = None      # cargo transfer dialog instance (PROJ-68)
        self.menu_panel = None           # strategy menu dropdown (PROJ-72)
        self.empire_build_queue_window = None  # empire-wide build queue window (PROJ-76)
        self.event_log_window = None           # event log window (PROJ-77)

        # UI State
        theme_path = os.path.join(Paths.DATA_DIR, 'builder_theme.json')
        self.manager = pygame_gui.UIManager((screen_width, screen_height), theme_path=theme_path)

        # --- Right Sidebar Layout (Three Panels) ---
        # 1. System Window (Top)
        # 2. Sector Window (Middle)
        # 3. Detail Window (Bottom)

        # Vertical partitioning
        # Let's divide by ratio or fixed px?
        # Detail needs minimal 250px for portrait.
        # Let's say top two split the remaining space.

        gap = UIConfig.PANEL_GAP
        panel_h_approx = (screen_height - 20) / 3
        
        # 1. System Panel (Top)
        rect_system = pygame.Rect(-self.sidebar_width + 10, 10, self.sidebar_width - 20, panel_h_approx - gap)
        
        self.system_panel = pygame_gui.elements.UIPanel(
            relative_rect=rect_system,
            manager=self.manager,
            anchors={'left': 'right', 'right': 'right', 'top': 'top', 'bottom': 'top'}
        )
        
        self.system_header = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(10, 10, self.sidebar_width - 40, 30),
            text="System: Deep Space",
            manager=self.manager,
            container=self.system_panel
        )
        
        self.system_tree = SystemTreePanel(
            relative_rect=pygame.Rect(10, 40, self.sidebar_width - 40, rect_system.height - 50),
            manager=self.manager,
            container=self.system_panel
        )
        self.system_tree.set_selection_callback(self.on_ui_selection)
        
        # 2. Sector Panel (Middle)
        rect_sector = pygame.Rect(-self.sidebar_width + 10, 10 + panel_h_approx, self.sidebar_width - 20, panel_h_approx - gap)
        
        self.sector_panel = pygame_gui.elements.UIPanel(
            relative_rect=rect_sector,
            manager=self.manager,
            anchors={'left': 'right', 'right': 'right', 'top': 'top', 'bottom': 'top'}
        )
        
        self.sector_header = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(10, 10, self.sidebar_width - 40, 30),
            text="Sector: Unknown",
            manager=self.manager,
            container=self.sector_panel
        )
        
        self.sector_tree = SystemTreePanel(
            relative_rect=pygame.Rect(10, 40, self.sidebar_width - 40, rect_sector.height - 50),
            manager=self.manager,
            container=self.sector_panel
        )
        self.sector_tree.set_selection_callback(self.on_ui_selection)
        
        # 3. Detail Panel (Bottom)
        rect_detail = pygame.Rect(-self.sidebar_width + 10, 10 + 2*panel_h_approx, self.sidebar_width - 20, panel_h_approx - gap)
        
        self.detail_panel = pygame_gui.elements.UIPanel(
            relative_rect=rect_detail,
            manager=self.manager,
            anchors={'left': 'right', 'right': 'right', 'top': 'top', 'bottom': 'top'}
        )
        
        # Portrait Image
        self.portrait_image = pygame_gui.elements.UIImage(
            relative_rect=pygame.Rect(10, 10, 150, 150),
            image_surface=pygame.Surface((150, 150)),
            manager=self.manager,
            container=self.detail_panel
        )
        
        # Info Text (Right of Portrait)
        text_w = self.sidebar_width - 180
        text_h = rect_detail.height - 20
        self.detail_text = pygame_gui.elements.UITextBox(
            html_text="Select an object for details.",
            relative_rect=pygame.Rect(170, 10, text_w, text_h),
            manager=self.manager,
            container=self.detail_panel
        )
        
        # Graph Image (Below Portrait)
        # Rotated 90 degrees, so it will be visually vertical.
        graph_y = 170
        graph_h = rect_detail.height - 180
        if graph_h < 50: graph_h = 50 
        
        self.graph_rect = pygame.Rect(10, graph_y, 150, graph_h)
        self.graph_image = pygame_gui.elements.UIImage(
            relative_rect=self.graph_rect,
            image_surface=pygame.Surface((150, graph_h)),
            manager=self.manager,
            container=self.detail_panel
        )
        
        # Raw Data Button (Top Right of Graph Box)
        # Position at top-right corner of the graph_rect
        btn_x = self.graph_rect.right - 22  # Inside right edge of graph
        btn_y = self.graph_rect.top + 2     # Inside top edge of graph

        self.btn_raw_data = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(btn_x, btn_y, 20, 20),
            text="",
            manager=self.manager,
            container=self.detail_panel,
            anchors={'left': 'left', 'right': 'left', 'top': 'top', 'bottom': 'top'},
            object_id="@small_icon_button"
        )
        self.btn_raw_data.hide()
        
        # Widgets
        # Initialize with SWAPPED dimensions because we will rotate the result 90 degrees.
        # Visually: 150(W) x H. Functionally: H(W) x 150(H) before rotation.
        self.spectrum_graph = SpectrumGraph(int(self.graph_rect.height), int(self.graph_rect.width))
        self.atmosphere_graph = AtmosphereGraph(int(self.graph_rect.height), int(self.graph_rect.width))
        
        self.current_raw_data = "" # store for popup
        
        # Mapping: Label -> Object
        self.current_sector_objects = {} 
        self.current_selection = None
        
        # --- Top Bar ---
        self.top_bar = pygame_gui.elements.UIPanel(
            relative_rect=pygame.Rect(0, 0, screen_width - self.sidebar_width, 50),
            manager=self.manager,
            anchors={'left': 'left', 'right': 'right', 'top': 'top', 'bottom': 'top'}
        )
        
        button_width = 150
        gap = 10
        # Button Groups
        # Nav Group: [< Col >] [< Fleet >]
        # Main Group: [Empire] [Research] [Next Turn]
        
        # --- Top Bar Layout ---
        # Strategy: Left Align after Player Label to avoid centering overlap issues.
        # Player Label ends at x=210.
        
        start_x = 230 
        
        # --- Nav Buttons ---
        # Group 1: Colony (Width ~140)
        self.btn_prev_colony = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(start_x, 5, 30, 40), text="<", manager=self.manager, container=self.top_bar, object_id='@nav_btn'
        )
        self.lbl_colony = pygame_gui.elements.UILabel(
             relative_rect=pygame.Rect(start_x + 30, 5, 80, 40), text="Colony", manager=self.manager, container=self.top_bar
        )
        self.btn_next_colony = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(start_x + 110, 5, 30, 40), text=">", manager=self.manager, container=self.top_bar, object_id='@nav_btn'
        )
        
        # Group 2: Fleet (Width ~140)
        # Position: Right of Colony Group + Gap
        fleet_start_x = start_x + 140 + 20 
        
        self.btn_prev_fleet = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(fleet_start_x, 5, 30, 40), text="<", manager=self.manager, container=self.top_bar, object_id='@nav_btn'
        )
        self.lbl_fleet = pygame_gui.elements.UILabel(
             relative_rect=pygame.Rect(fleet_start_x + 30, 5, 80, 40), text="Fleet", manager=self.manager, container=self.top_bar
        )
        self.btn_next_fleet = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(fleet_start_x + 110, 5, 30, 40), text=">", manager=self.manager, container=self.top_bar, object_id='@nav_btn'
        )
        
        # --- Main Buttons ---
        # Position: Right of Fleet Group + Gap
        # Fleet ends at fleet_start_x + 140
        main_start_x = fleet_start_x + 140 + 40
        btn_w = 100
        gap = 10
        
        self.btn_planets = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(main_start_x, 5, btn_w, 40), text="Planets", manager=self.manager, container=self.top_bar
        )
        self.btn_empire = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(main_start_x + 1*(btn_w+gap), 5, btn_w, 40), text="Empire", manager=self.manager, container=self.top_bar
        )
        self.btn_research = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(main_start_x + 2*(btn_w+gap), 5, btn_w, 40), text="Research", manager=self.manager, container=self.top_bar
        )
        self.btn_design = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(main_start_x + 3*(btn_w+gap), 5, btn_w, 40), text="Design", manager=self.manager, container=self.top_bar
        )
        self.btn_build_queues = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(main_start_x + 4*(btn_w+gap), 5, btn_w, 40), text="Build Yards", manager=self.manager, container=self.top_bar
        )
        self.btn_all_queues = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(main_start_x + 5*(btn_w+gap), 5, btn_w, 40), text="All Queues", manager=self.manager, container=self.top_bar
        )

        # Menu Button (replaces Save Game - options now in dropdown)
        self.btn_menu = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(main_start_x + 6*(btn_w+gap), 5, btn_w, 40),
            text="Menu",
            manager=self.manager,
            container=self.top_bar
        )

        # Event Log Button (PROJ-77)
        self.btn_events = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(main_start_x + 7*(btn_w+gap), 5, btn_w, 40),
            text="Log",
            manager=self.manager,
            container=self.top_bar
        )

        # End Turn (Larger)
        self.btn_next_turn = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(main_start_x + 8*(btn_w+gap), 5, 150, 40),
            text="End Turn",
            manager=self.manager,
            container=self.top_bar
        )
        
        # Player indicator label (far left of top bar)
        self.lbl_current_player = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(10, 5, 200, 40),
            text="Player 1's Turn",
            manager=self.manager,
            container=self.top_bar
        )

        # Empire resource display (below top bar, full width)
        resource_bar_y = 50  # Just below top bar
        resource_bar_height = 24
        self.resource_bar = pygame_gui.elements.UIPanel(
            relative_rect=pygame.Rect(0, resource_bar_y, screen_width - self.sidebar_width, resource_bar_height),
            manager=self.manager,
            anchors={'left': 'left', 'right': 'right', 'top': 'top', 'bottom': 'top'}
        )
        self.lbl_resources = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(10, 0, screen_width - self.sidebar_width - 20, resource_bar_height),
            text="",
            manager=self.manager,
            container=self.resource_bar
        )
        self._update_resource_display()

        # Contextual Buttons (Detail Panel)
        # Positioned below text
        self.btn_colonize = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(220, rect_detail.height - 50, 120, 40),
            text="Colonize",
            manager=self.manager,
            container=self.detail_panel,
            visible=0 # Hidden by default
        )
        
        self.btn_build_yard = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(350, rect_detail.height - 50, 120, 40),
            text="Build Yard",
            manager=self.manager,
            container=self.detail_panel,
            visible=0 # Hidden by default
        )
        
        self.btn_orders = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(80, rect_detail.height - 50, 120, 40),
            text="Orders",
            manager=self.manager,
            container=self.detail_panel,
            visible=0 # Hidden by default
        )

        self.btn_fleet_report = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(210, rect_detail.height - 50, 120, 40),
            text="Fleet Report",
            manager=self.manager,
            container=self.detail_panel,
            visible=0 # Hidden by default
        )

        # Fleet build button (PROJ-67: Fleet Space Yards)
        self.btn_build_fleet = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(340, rect_detail.height - 50, 120, 40),
            text="Build",
            manager=self.manager,
            container=self.detail_panel,
            visible=0  # Hidden by default
        )
        
        self.panels = [
            self.top_bar,
            self.resource_bar,
            self.system_panel,
            self.sector_panel,
            self.detail_panel
        ]

        # Apply hotkey tooltips to buttons (PROJ-71)
        self._apply_hotkey_tooltips()

    # =========================================================================
    # Hotkey Tooltip Enrichment (PROJ-71)
    # =========================================================================

    def _apply_hotkey_tooltips(self) -> None:
        """Apply hotkey hint tooltips to strategy UI buttons.

        Uses the InputMapper to look up the display text for each button's
        associated action. If the mapper is None or an action is unbound,
        the button retains its default tooltip (none).
        """
        if not self._mapper:
            return

        # Map buttons to their InputAction
        button_actions = {
            self.btn_next_turn: InputAction.STRATEGY_NEXT_TURN,
            self.btn_planets: InputAction.STRATEGY_OPEN_PLANETS,
            self.btn_empire: InputAction.STRATEGY_OPEN_EMPIRE,
            self.btn_research: InputAction.STRATEGY_OPEN_RESEARCH,
            self.btn_design: InputAction.STRATEGY_OPEN_DESIGN,
            self.btn_build_queues: InputAction.STRATEGY_OPEN_BUILD_QUEUES,
            self.btn_prev_colony: InputAction.STRATEGY_PREV_COLONY,
            self.btn_next_colony: InputAction.STRATEGY_NEXT_COLONY,
            self.btn_prev_fleet: InputAction.STRATEGY_PREV_FLEET,
            self.btn_next_fleet: InputAction.STRATEGY_NEXT_FLEET,
            self.btn_colonize: InputAction.FLEET_COLONIZE,
            self.btn_orders: InputAction.DETAIL_PANEL_ORDERS,
            self.btn_fleet_report: InputAction.DETAIL_PANEL_FLEET_REPORT,
            self.btn_build_fleet: InputAction.DETAIL_PANEL_BUILD,
        }

        for btn, action in button_actions.items():
            hint = self._mapper.get_display_text(action)
            if hint:
                btn.set_tooltip(hint)

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
        if hasattr(self, 'system_tree'):
            self.system_tree.layout()
        if hasattr(self, 'sector_tree'):
            self.sector_tree.layout()


        
    def handle_resize(self, width, height):
        """Update UI elements for new resolution."""
        self.width = width
        self.height = height
        self.manager.set_window_resolution((width, height))
        
        panel_h_approx = (height - 20) / 3
        gap = 5
        
        # System (Top)
        self.system_panel.set_dimensions((self.sidebar_width - 20, panel_h_approx - gap))
        self.system_panel.set_relative_position((-self.sidebar_width + 10, 10))
        self.system_tree.set_dimensions((self.sidebar_width - 40, panel_h_approx - 60))
        
        # Sector (Middle)
        self.sector_panel.set_dimensions((self.sidebar_width - 20, panel_h_approx - gap))
        self.sector_panel.set_relative_position((-self.sidebar_width + 10, 10 + panel_h_approx))
        self.sector_tree.set_dimensions((self.sidebar_width - 40, panel_h_approx - 60))
        
        # Detail (Bottom)
        self.detail_panel.set_dimensions((self.sidebar_width - 20, panel_h_approx - gap))
        self.detail_panel.set_relative_position((-self.sidebar_width + 10, 10 + 2*panel_h_approx))
        
        # Detail Text (Right side)
        text_w = self.sidebar_width - 180
        text_h = self.detail_panel.rect.height - 20
        self.detail_text.set_dimensions((text_w, text_h))
        self.detail_text.set_relative_position((170, 10))
        
        # Graph (Left side, under Portrait)
        # Portrait is 150x150 at (10,10)
        # Graph Y = 170.
        graph_y = 170
        graph_h = self.detail_panel.rect.height - 180
        if graph_h < 50: graph_h = 50
        
        # NOTE: We can't resize the 'graph_image' UIImage easily if it expects fixed surface?
        # Actually UIImage resizes if we set dimensions? No, it scales the image?
        # We need to recreate the surface or just set dimensions container?
        # PygameGUI UIImage doesn't auto-resize surface. But we can update the rect.
        # But we also need to recreate the Graph Rendering widgets to match new size?
        # Yes, SpectrumGraph stores width/height.
        self.graph_rect = pygame.Rect(10, graph_y, 150, graph_h)
        self.graph_image.set_dimensions((150, graph_h))
        self.graph_image.set_relative_position((10, graph_y))
        
        # Re-init graphs with new size (SWAPPED for rotation)
        self.spectrum_graph = SpectrumGraph(int(self.graph_rect.height), int(self.graph_rect.width))
        self.atmosphere_graph = AtmosphereGraph(int(self.graph_rect.height), int(self.graph_rect.width))

        # Position Raw Data Button: Top-Right of Graph
        # Graph is at (10, graph_y) to (160, graph_y + h)
        # Button is 20x20.
        btn_x = self.graph_rect.right - 22 # Inside right edge
        btn_y = self.graph_rect.top + 2    # Inside top edge
        self.btn_raw_data.set_relative_position((btn_x, btn_y))

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
        return get_label_for_object(obj)

    def _get_object_asset(self, obj):
        """Proxy to scene for asset resolution."""
        if hasattr(self.scene, '_get_object_asset'):
            return self.scene._get_object_asset(obj)
        return None
        
    def _format_spectrum(self, star):
        return format_spectrum_html(star)

    def show_raw_data_popup(self):
        """Show raw data in a message window."""
        if self.current_raw_data:
            win_rect = pygame.Rect(0, 0, 400, 400)
            win_rect.center = (self.width/2, self.height/2)
            pygame_gui.windows.UIMessageWindow(
                rect=win_rect,
                html_message=self.current_raw_data,
                manager=self.manager,
                window_title="Raw Data Analysis"
            )

    def show_detailed_report(self, obj, portrait_surface=None):
        """Update the detail report implementation."""
        self.current_selection = obj # UPDATE STATE

        # Reset state
        self.btn_raw_data.hide()
        self.graph_image.hide()

        # Default hidden, shown based on context below
        self.btn_colonize.hide()
        self.btn_build_yard.hide()
        self.btn_orders.hide()
        self.btn_fleet_report.hide()
        self.btn_build_fleet.hide()
        self.current_raw_data = ""

        # Clean up planet report panel if switching to non-planet object
        if self.planet_report_panel is not None:
            self.planet_report_panel.kill()
            self.planet_report_panel = None
            # Show the old widgets again for non-planet objects
            self.portrait_image.show()
            self.detail_text.show()

        # Determine Current Player (Local to UI or passed?) 
        # StrategyInterface doesn't know "Current Player" easily without accessing scene.
        # But scene.current_empire exists.
        current_empire_id = -1
        if hasattr(self.scene, 'current_empire'):
            current_empire_id = self.scene.current_empire.id

        self.current_raw_data = ""
        
        if portrait_surface:
             # Resize portrait if needed to fit 150x150?
             scaled = pygame.transform.smoothscale(portrait_surface, (150, 150))
             self.portrait_image.set_image(scaled)
        else:
             self.portrait_image.set_image(pygame.Surface((150, 150))) # clear
             
        if not obj:
            self.detail_text.set_text("Select an object for details.")
            return
            
        text = ""
        
        if is_star_system(obj):
            # Show Primary Star Info
            primary = obj.primary_star
            if primary:
                text = f"<b>System:</b> {obj.name}<br>"
                text += f"<b>Primary:</b> {primary.name}<br>"
                text += f"<b>Type:</b> {primary.star_type.name}<br>"
                text += f"<b>Mass:</b> {primary.mass:.2f} Sol<br>"
                text += f"<b>Temp:</b> {int(primary.temperature)} K<br>"
                text += f"<b>Stars:</b> {len(obj.stars)}<br>"

                # Graph
                self.graph_image.show()
                self.btn_raw_data.show()
                surface = self.spectrum_graph.render(primary, vertical=True)
                surface = pygame.transform.rotate(surface, -90)
                self.graph_image.set_image(surface)
                self.current_raw_data = self._format_spectrum(primary)
            else:
                 text = f"<b>System:</b> {obj.name}<br>(Empty System)"

        elif is_star(obj):
            text = f"<b>Star:</b> {obj.name}<br>"
            text += f"<b>Type:</b> {obj.star_type.name}<br>"
            text += f"<b>Mass:</b> {obj.mass:.2f} Sol<br>"
            text += f"<b>Temp:</b> {int(obj.temperature)} K<br>"
            text += f"<b>Diam:</b> {obj.diameter_hexes:.1f} Hex<br>"
            
            self.graph_image.show()
            self.btn_raw_data.show()
            surface = self.spectrum_graph.render(obj, vertical=True)
            surface = pygame.transform.rotate(surface, -90)
            self.graph_image.set_image(surface)
            self.current_raw_data = self._format_spectrum(obj)

        elif is_planet(obj):
            # Hide old widgets - using PlanetReportPanel instead
            self.portrait_image.hide()
            self.detail_text.hide()
            # graph_image already hidden at start of method

            # Calculate available height for panel
            # Constrain panel to not cover the Build Yard button (PROJ-54)
            # Button is at a fixed position from initialization
            detail_panel_height = self.detail_panel.rect.height
            button_relative_y = self.btn_build_yard.relative_rect.y  # Button's Y position in detail panel
            panel_max_height = min(detail_panel_height - 60, button_relative_y - 20)  # 20px margin above button

            # Create planet report panel (NO complexes for strategy UI)
            self.planet_report_panel = PlanetReportPanel(
                manager=self.manager,
                rect=pygame.Rect(10, 10, 580, panel_max_height),
                planet=obj,
                container=self.detail_panel,
                portrait_surface=portrait_surface,
                show_complexes=False  # Strategy UI doesn't show facility list
            )

            # Show Build Yard button for owned planets (PROJ-54)
            if obj.owner_id == current_empire_id:
                self.btn_build_yard.show()

            # No text needed - panel handles all display
            text = ""

        elif is_sector_environment(obj):
            # Calculate dynamic radiation
            spec = obj.calculate_radiation()
            # Mock a star-like object so _format_spectrum works
            class MockStar:
                spectrum = spec
            
            text = f"<b>Local Environment</b><br>"
            text += f"<b>System:</b> {obj.system.name}<br>"
            text += f"<b>Local:</b> {obj.local_hex}<br>"
            text += f"<br><b>Total Incident Radiation:</b><br>"
            text += f"{spec.get_total_output():.2e} W/m^2 (relative)<br>"
            
            self.graph_image.show()
            self.btn_raw_data.show()
            surface = self.spectrum_graph.render(MockStar, vertical=True)
            surface = pygame.transform.rotate(surface, -90)
            self.graph_image.set_image(surface)
            self.current_raw_data = self._format_spectrum(MockStar)

        elif is_fleet(obj):
            text = format_fleet_info(obj)

            # Show Fleet Buttons
            if obj.owner_id == current_empire_id:
                 self.btn_orders.show()
                 self.btn_fleet_report.show()

                 # PROJ-67: Show Build button for fleets with space shipyard
                 if obj.has_space_shipyard:
                     self.btn_build_fleet.show()

                 # Check if we can colonize (Ask Engine)
                 # We query for 'Any Planet' (target=None) to see if *something* is possible here.
                 if hasattr(self.scene, 'turn_engine'):
                     # We need galaxy ref
                     res = self.scene.turn_engine.validate_colonize_order(self.scene.galaxy, obj, None)
                     if res.is_valid:
                         self.btn_colonize.show()

        elif is_warp_point(obj):
             text = f"<b>Warp Point</b><br>"
             text += f"<b>To:</b> {obj.destination_id}<br>"
             text += f"<b>Local Loc:</b> {obj.location}<br>"
             
        self.detail_text.html_text = text
        self.detail_text.rebuild()

    def _format_atmosphere_raw(self, planet):
        return format_atmosphere_raw(planet)

        
    def _update_resource_display(self):
        """Update the empire resource bar with current pool values."""
        if not hasattr(self.scene, 'current_empire'):
            return
        empire = self.scene.current_empire
        if empire is None:
            return

        # Resource abbreviations for compact display
        abbrevs = {"Metals": "Met", "Organics": "Org", "Vapors": "Vap",
                   "Radioactives": "Rad", "Exotics": "Exo"}

        parts = []
        for res in PLANET_RESOURCES:
            current = empire.get_resource(res)
            cap = empire.max_storage.get(res, 0.0)
            abbr = abbrevs.get(res, res[:3])
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
            font = pygame.font.SysFont("arial", 20)
            mode_text = font.render(f"Strategy Layer | Zoom: {self.scene.camera.zoom:.2f}", True, (255, 255, 255))
            screen.blit(mode_text, (20, self.height - 30))

    def _has_modal_open(self) -> bool:
        """Check if any modal sub-panel is currently open."""
        # Check for menu panel (PROJ-72)
        if self.menu_panel:
            return True

        # Check for build queue screen
        if hasattr(self.scene, 'build_queue_screen') and self.scene.build_queue_screen is not None:
            return True

        # Check for fleet orders window
        if self.fleet_orders_window is not None:
            return True

        # Check for planet list window (BUG-22)
        if self.planet_list_window is not None:
            return True

        # Check for fleet report window (PROJ-03)
        if self.fleet_report_window is not None:
            return True

        # Check for transfer dialog (PROJ-68)
        if self.transfer_dialog is not None:
            return True

        # Check for build queue list window (BUG-67)
        if self.build_queue_list_window is not None:
            return True

        # Check for empire build queue window (PROJ-76)
        if self.empire_build_queue_window is not None:
            return True

        # Check for event log window (PROJ-77)
        if self.event_log_window is not None:
            return True

        # Check if workshop is being opened
        if hasattr(self.scene, 'action_open_design') and self.scene.action_open_design:
            return True

        return False

    def on_ui_selection(self, obj):
        """Handle selection of an object from any UI panel."""
        if hasattr(self.scene, 'on_ui_selection'):
            self.scene.on_ui_selection(obj)

    def handle_event(self, event):
        """Pass events to pygame_gui and handle custom UI logic."""
        self.manager.process_events(event)
        self.process_custom_ui_events(event)
        
        # Pass generic events to orders window if active (e.g. for confirmation dialogs)
        if self.fleet_orders_window:
             self.fleet_orders_window.handle_global_event(event)
        
        # Close menu panel on Escape
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE and self.menu_panel:
            self.close_menu_panel()
            return

        # Close menu panel on click outside
        if event.type == pygame.MOUSEBUTTONDOWN and self.menu_panel:
            panel_rect = self.menu_panel.get_abs_rect()
            menu_btn_rect = self.btn_menu.get_abs_rect()
            if not panel_rect.collidepoint(event.pos) and not menu_btn_rect.collidepoint(event.pos):
                self.close_menu_panel()

        if self.system_tree.process_event(event):
             pass

        if self.sector_tree.process_event(event):
             pass

        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == self.btn_planets:
                self.open_planet_list()
            elif event.ui_element == self.btn_design:
                if hasattr(self.scene, 'on_design_click'):
                    self.scene.on_design_click()
            elif event.ui_element == self.btn_build_queues:
                self.open_build_queue_list()
            elif event.ui_element == self.btn_all_queues:
                self.open_empire_build_queue_window()
            elif event.ui_element == self.btn_menu:
                self.toggle_menu_panel()
            elif event.ui_element == self.btn_events:
                self.open_event_log()
            elif event.ui_element == self.btn_raw_data:
                self.show_raw_data_popup()
            elif event.ui_element == self.btn_colonize:
                # Logic: Issues order mostly from Fleet
                obj = self.current_selection
                if obj and is_fleet(obj):
                     # Find Uncolonized Planets at Fleet Location
                     from game.strategy.data.hex_math import hex_distance # Import if needed or check equality
                     
                     if not hasattr(self.scene, 'galaxy'): return
                     
                     # Fleet location
                     f_loc = obj.location
                     
                     # Find System
                     system = self.scene.galaxy.get_system_of_object(obj)
                     if not system:
                         log_debug("Colonize: Fleet not in system?")
                         return
                         
                     # Find planets at this location (SYSTEM)
                     candidates = []
                     for p in system.planets:
                         # Any planet in system is reachable if fleet is at system
                         if p.owner_id is None: # Unowned
                             candidates.append(p)
                                 
                     if not candidates:
                         # Feedback?
                         log_debug("No unowned planets at this location.")
                         return
                         
                     if len(candidates) == 1:
                         # Single candidate, order directly
                         if hasattr(self.scene, 'request_colonize_order'):
                             self.scene.request_colonize_order(obj, candidates[0])
                     else:
                         # Multiple -> Dialog
                         # Define callback wrapper
                         def on_planet_selected(planet):
                             if hasattr(self.scene, 'request_colonize_order'):
                                 self.scene.request_colonize_order(obj, planet)
                                 
                         self.prompt_planet_selection(candidates, on_planet_selected)
            
            elif event.ui_element == self.btn_orders:
                 obj = self.current_selection
                 if obj and is_fleet(obj):
                      self.open_orders_window(obj)

            elif event.ui_element == self.btn_fleet_report:
                 obj = self.current_selection
                 if obj and is_fleet(obj):
                      self.open_fleet_report_window(obj)

            # NOTE: btn_build_yard is handled in strategy_input_handler.py - do not duplicate here
            pass

        # Handle quit-to-menu confirmation (PROJ-72)
        if event.type == pygame_gui.UI_CONFIRMATION_DIALOG_CONFIRMED:
            if hasattr(self.scene, '_quit_confirm_dialog') and event.ui_element == self.scene._quit_confirm_dialog:
                self.scene._handle_quit_confirmed()

        if event.type == pygame_gui.UI_WINDOW_CLOSE:
            if event.ui_element == self.fleet_orders_window:
                self.fleet_orders_window = None
            elif event.ui_element == self.fleet_report_window:
                self.fleet_report_window = None
            elif event.ui_element == self.transfer_dialog:
                self.transfer_dialog = None
            elif event.ui_element == self.build_queue_list_window:
                self.build_queue_list_window = None
            elif event.ui_element == self.empire_build_queue_window:
                self._on_empire_build_queue_closed()
            elif event.ui_element == self.event_log_window:
                self._on_event_log_closed()

    def handle_click(self, mx, my, button):
        """Handle mouse clicks. Returns True if click was handled by UI."""
        # 1. Check logical sidebar area
        if mx > self.width - self.sidebar_width:
            return True
            
        # 2. Check if ANY UI element is being hovered (e.g. windows, modals)
        # This prevents clicking "through" the planet selection window to the map
        if self.manager.get_hovering_any_element():
             return True
             
        return False


        
    def prompt_planet_selection(self, planets, on_select):
        """Open a modal window to select a planet."""
        # Large window to fit full planet report (matches strategy UI detail panel)
        width = 950
        height = 650
        x = (self.width - width) / 2
        y = (self.height - height) / 2

        rect = pygame.Rect(x, y, width, height)
        # Use PlanetSelectionWindow (PROJ-54 - now uses PlanetReportPanel internally)
        PlanetSelectionWindow(rect, self.manager, planets, on_select)

    def prompt_move_choice(self, fleet, target_hex, on_move_sector, on_intercept_fleet):
        """
        Dialog to choose between moving to the sector or intercepting the fleet.
        """
        # We can use a confirmation dialog with custom buttons or a small custom window.
        # pygame_gui doesn't natively support "3 buttons" easily in standard dialogs without custom class.
        # Let's use a standard UIConfirmationDialog but we need 2 positive options? No.
        # Let's use a small custom UIWindow or UIMessageWindow?
        # Simpler: A Custom UIWindow with 2 Buttons.
        
        width = 300
        height = 150
        x = (self.width - width) / 2
        y = (self.height - height) / 2
        rect = pygame.Rect(x, y, width, height)
        
        win = pygame_gui.elements.UIWindow(
            rect=rect,
            manager=self.manager,
            window_display_title="Select Move Type"
        )
        
        pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(10, 10, 280, 30),
            text=f"Fleet detected at target.",
            manager=self.manager,
            container=win
        )
        
        btn_sector = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(10, 50, 280, 30),
            text="Move to Sector (Static)",
            manager=self.manager,
            container=win
        )
        
        btn_intercept = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(10, 90, 280, 30),
            text="Intercept Fleet (Dynamic)",
            manager=self.manager,
            container=win
        )
        
        # We need to bind click events. 
        # Since we can't easily pass callbacks to generic UIElements without a wrapper class or external event handling,
        # we will use a small inline class or rely on the fact that StrategyInterface handles events?
        # StrategyInterface.handle_event handles UI_BUTTON_PRESSED.
        # But we don't store references to these dyanmic buttons easily.
        
        # Pattern: Store callback map?
        # self.active_callbacks[btn_element] = callback
        
        if not hasattr(self, 'ui_callbacks'):
            self.ui_callbacks = {}
            
        self.ui_callbacks[btn_sector] = lambda: (on_move_sector(), win.kill())
        self.ui_callbacks[btn_intercept] = lambda: (on_intercept_fleet(), win.kill())

    def process_custom_ui_events(self, event):
        """Helper to process custom callbacks."""
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if hasattr(self, 'ui_callbacks') and event.ui_element in self.ui_callbacks:
                self.ui_callbacks[event.ui_element]()
                del self.ui_callbacks[event.ui_element] # Cleanup


    def open_planet_list(self):
        """Open the Planet List Window."""
        w, h = self.width * 0.9, self.height * 0.9
        rect = pygame.Rect((self.width - w)/2, (self.height - h)/2, w, h)

        # Get Empire (current player)
        empire = self.scene.current_empire
        galaxy = self.scene.galaxy

        # Store reference to track window state (BUG-22)
        self.planet_list_window = PlanetListWindow(
            rect, self.manager, galaxy, empire,
            on_close_callback=self._on_planet_list_closed,
            asset_resolver=self._get_object_asset
        )

    def _on_planet_list_closed(self):
        """Callback when planet list window is closed."""
        self.planet_list_window = None

    def open_build_queue_list(self):
        """Open the Build Queue List Window (BUG-67)."""
        if self.build_queue_list_window:
            self.build_queue_list_window.kill()

        empire = self.scene.current_empire

        w, h = 700, 500
        rect = pygame.Rect((self.width - w) / 2, (self.height - h) / 2, w, h)

        self.build_queue_list_window = BuildQueueListWindow(
            rect, self.manager, empire,
            on_close_callback=self._on_build_queue_list_closed,
            input_mapper=self._mapper
        )

    def _on_build_queue_list_closed(self):
        """Callback when build queue list window is closed."""
        self.build_queue_list_window = None

    def open_empire_build_queue_window(self):
        """Open the Empire-Wide Build Queue Window (PROJ-76)."""
        if self.empire_build_queue_window:
            self.empire_build_queue_window.kill()

        empire = self.scene.current_empire
        galaxy = self.scene.galaxy

        w, h = int(self.width * 0.9), int(self.height * 0.9)
        rect = pygame.Rect((self.width - w) / 2, (self.height - h) / 2, w, h)

        self.empire_build_queue_window = EmpireBuildQueueWindow(
            rect, self.manager, empire, galaxy,
            on_close_callback=self._on_empire_build_queue_closed,
            on_navigate_to_hex=self.scene.on_navigate_to_hex_build,
        )

    def _on_empire_build_queue_closed(self):
        """Callback when empire build queue window is closed."""
        self.empire_build_queue_window = None

    def open_event_log(self):
        """Open the Event Log Window showing all events (PROJ-77).

        Fetches all events from the facade and displays them in
        a modal window with filter tabs.
        """
        if self.event_log_window:
            self.event_log_window.kill()

        events = self.scene._facade.get_all_events() if hasattr(self.scene, '_facade') else []

        w, h = int(self.width * 0.7), int(self.height * 0.7)
        rect = pygame.Rect((self.width - w) / 2, (self.height - h) / 2, w, h)

        self.event_log_window = EventLogWindow(
            rect, self.manager, events,
            on_close_callback=self._on_event_log_closed,
        )

    def open_event_log_with_events(self, events: list):
        """Open the Event Log Window with a specific event list.

        Used at turn start to show only the current turn's events.

        Args:
            events: List of event dicts to display.
        """
        if self.event_log_window:
            self.event_log_window.kill()

        w, h = int(self.width * 0.7), int(self.height * 0.7)
        rect = pygame.Rect((self.width - w) / 2, (self.height - h) / 2, w, h)

        self.event_log_window = EventLogWindow(
            rect, self.manager, events,
            on_close_callback=self._on_event_log_closed,
        )

    def _on_event_log_closed(self):
        """Callback when event log window is closed."""
        self.event_log_window = None

    def open_orders_window(self, fleet):
        """Open the Fleet Orders Window."""
        if self.fleet_orders_window:
            self.fleet_orders_window.kill()

        w, h = 400, 500
        rect = pygame.Rect((self.width - w)/2, (self.height - h)/2, w, h)

        self.fleet_orders_window = FleetOrdersWindow(
            rect, self.manager, fleet, input_mapper=self._mapper
        )

    def open_fleet_report_window(self, fleet):
        """Open the Fleet Report Window."""
        if self.fleet_report_window:
            self.fleet_report_window.kill()

        # Match PlanetListWindow size (90% of screen)
        w, h = self.width * 0.9, self.height * 0.9
        rect = pygame.Rect((self.width - w)/2, (self.height - h)/2, w, h)

        self.fleet_report_window = FleetReportWindow(
            rect,
            self.manager,
            fleet,
            on_close_callback=self._on_fleet_report_closed
        )

    def _on_fleet_report_closed(self):
        """Callback when fleet report window is closed."""
        self.fleet_report_window = None

    def open_transfer_dialog(self, source_fleet, hex_coord):
        """
        Open the cargo/population transfer dialog.
        
        PROJ-68: Hex-aware selection between multiple ships and colonies.
        """
        if self.transfer_dialog is not None:
            self.transfer_dialog.kill()
            self.transfer_dialog = None
            
        from game.ui.screens.transfer_dialog import TransferDialog
        
        win_w, win_h = 600, 500
        win_rect = pygame.Rect(0, 0, win_w, win_h)
        win_rect.center = (self.width // 2, self.height // 2)
        
        self.transfer_dialog = TransferDialog(
            relative_rect=win_rect,
            manager=self.manager,
            source_fleet=source_fleet,
            hex_coord=hex_coord,
            scene=self.scene,
            input_mapper=self._mapper
        )

