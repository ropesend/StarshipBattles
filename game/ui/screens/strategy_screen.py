import os
import pygame
import pygame_gui
from game.strategy.data.fleet import OrderType
from game.ui.screens.planet_selection_window import PlanetSelectionWindow
from game.ui.screens.planet_list_window import PlanetListWindow
from game.core.constants import DATA_DIR
from game.ui.panels.strategy_widgets import SpectrumGraph, AtmosphereGraph
from game.ui.panels.system_tree_panel import SystemTreePanel
import pygame_gui.windows # for raw data popup if needed
import pygame_gui.elements as ui

class StrategyInterface:
    """Handles all UI rendering and interaction for the StrategyScene."""
    
    def __init__(self, scene, screen_width, screen_height):
        self.scene = scene
        self.width = screen_width
        self.height = screen_height
        self.sidebar_width = 600
        
        # UI State
        theme_path = os.path.join(DATA_DIR, 'builder_theme.json')
        self.manager = pygame_gui.UIManager((screen_width, screen_height), theme_path=theme_path)
        
        # --- Right Sidebar Layout (Three Panels) ---
        # 1. System Window (Top)
        # 2. Sector Window (Middle)
        # 3. Detail Window (Bottom)
        
        # Vertical partitioning
        # Let's divide by ratio or fixed px?
        # Detail needs minimal 250px for portrait.
        # Let's say top two split the remaining space.
        
        gap = 5
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
        
        # Raw Data Button (Top Right of Detail Panel Container)
        # Position relative to container, taking anchors into account.
        # If anchored top-right:
        # relative_rect x=-30 implies 30px from right edge.
        # y=10 implies 10px from top.
        
        self.btn_raw_data = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(0, 0, 20, 20),
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
        
        # Calculations for centering
        # Nav Group Width: (30+80+30) + 10 + (30+80+30) = 140 + 10 + 140 = 290
        # Main Group Width: 100 + 10 + 100 + 10 + 150 = 370
        # Total Width = 290 + 20 + 370 = 680
        
        center_x = (screen_width - self.sidebar_width) / 2
        start_x = center_x - (680 / 2)
        
        # --- Nav Buttons ---
        # Colony
        self.btn_prev_colony = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(start_x, 5, 30, 40), text="<", manager=self.manager, container=self.top_bar, object_id='@nav_btn'
        )
        self.lbl_colony = pygame_gui.elements.UILabel(
             relative_rect=pygame.Rect(start_x + 30, 5, 80, 40), text="Colony", manager=self.manager, container=self.top_bar
        )
        self.btn_next_colony = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(start_x + 110, 5, 30, 40), text=">", manager=self.manager, container=self.top_bar, object_id='@nav_btn'
        )
        
        # Fleet
        offset_fleet = 150
        self.btn_prev_fleet = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(start_x + offset_fleet, 5, 30, 40), text="<", manager=self.manager, container=self.top_bar, object_id='@nav_btn'
        )
        self.lbl_fleet = pygame_gui.elements.UILabel(
             relative_rect=pygame.Rect(start_x + offset_fleet + 30, 5, 80, 40), text="Fleet", manager=self.manager, container=self.top_bar
        )
        self.btn_next_fleet = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(start_x + offset_fleet + 110, 5, 30, 40), text=">", manager=self.manager, container=self.top_bar, object_id='@nav_btn'
        )
        
        # --- Main Buttons ---
        offset_main = 310
        self.btn_planets = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(start_x + offset_main - 110, 5, 100, 40), text="Planets", manager=self.manager, container=self.top_bar
        )
        self.btn_empire = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(start_x + offset_main, 5, 100, 40), text="Empire", manager=self.manager, container=self.top_bar
        )
        self.btn_research = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(start_x + offset_main + 110, 5, 100, 40), text="Research", manager=self.manager, container=self.top_bar
        )
        self.btn_next_turn = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(start_x + offset_main + 220, 5, 150, 40), 
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
        
        # Contextual Buttons (Detail Panel)
        # Positioned below text
        self.btn_colonize = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(220, rect_detail.height - 50, 120, 40),
            text="Colonize",
            manager=self.manager,
            container=self.detail_panel,
            visible=0 # Hidden by default
        )
        
        self.btn_build_ship = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(350, rect_detail.height - 50, 120, 40),
            text="Build Ship",
            manager=self.manager,
            container=self.detail_panel,
            visible=0 # Hidden by default
        )

        
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
        if hasattr(obj, 'stars'): return f"System: {obj.name}"
        elif hasattr(obj, 'color') and hasattr(obj, 'mass'): return f"Star: {obj.name}"
        elif hasattr(obj, 'planet_type'): return f"Planet: {obj.name}"
        elif hasattr(obj, 'destination_id'): return f"Warp Point -> {obj.destination_id}"
        elif hasattr(obj, 'ships'): return f"Fleet {obj.id} ({len(obj.ships)})"
        elif hasattr(obj, 'calculate_radiation'): return "Local Radiation Analysis"
        return "Unknown Object"

    def _get_object_asset(self, obj):
        """Proxy to scene for asset resolution."""
        if hasattr(self.scene, '_get_object_asset'):
            return self.scene._get_object_asset(obj)
        return None
        
    def _format_spectrum(self, star):
        s = star.spectrum
        html = "<br><b>Spectrum Intensity (W/m^2 rel):</b><br>"
        html += f" Gamma: {s.gamma_ray:.2e}<br>"
        html += f" X-Ray: {s.xray:.2e}<br>"
        html += f" UV:    {s.ultraviolet:.2e}<br>"
        html += f" Blue:  {s.blue:.2e}<br>"
        html += f" Green: {s.green:.2e}<br>"
        html += f" Red:   {s.red:.2e}<br>"
        html += f" IR:    {s.infrared:.2e}<br>"
        html += f" Micro: {s.microwave:.2e}<br>"
        html += f" Radio: {s.radio:.2e}<br>"
        return html

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
        # Reset state
        self.btn_raw_data.hide()
        self.graph_image.hide()
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
        
        if hasattr(obj, 'stars'): # StarSystem
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

        elif hasattr(obj, 'color') and hasattr(obj, 'mass'): # Star
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
        
        elif hasattr(obj, 'planet_type'): # Planet
            text = self.format_planet_info(obj)
             
            self.graph_image.show()
            self.btn_raw_data.show()
            surface = self.atmosphere_graph.render(obj, vertical=True)
            surface = pygame.transform.rotate(surface, -90)
            self.graph_image.set_image(surface)
            self.current_raw_data = self._format_atmosphere_raw(obj)
            
        elif hasattr(obj, 'calculate_radiation'): # SectorEnvironment
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

        elif hasattr(obj, 'ships'): # Fleet
            text = f"<b>Fleet:</b> {obj.id}<br>"
            text += f"<b>Owner:</b> {obj.owner_id}<br>"
            text += f"<b>Ships:</b> {len(obj.ships)}<br>"
            text += f"<b>Location:</b> {obj.location}<br>"
            
            text += "<b>Orders:</b><br>"
            if obj.orders:
                for i, order in enumerate(obj.orders):
                    if order.type == OrderType.MOVE:
                         text += f" {i+1}. MOVE {order.target}<br>"
                    elif order.type == OrderType.COLONIZE:
                         # target is Planet object
                         p_name = order.target.name if hasattr(order.target, 'name') else "Unknown"
                         text += f" {i+1}. COLONIZE {p_name}<br>"
                    else:
                         text += f" {i+1}. {order.type.name}<br>"
            else:
                 text += " (No Orders)<br>"

        elif hasattr(obj, 'destination_id'): # Warp Point
             text = f"<b>Warp Point</b><br>"
             text += f"<b>To:</b> {obj.destination_id}<br>"
             text += f"<b>Local Loc:</b> {obj.location}<br>"
             
        self.detail_text.html_text = text
        self.detail_text.rebuild() 
        
    def format_planet_info(self, obj):
        """Format HTML report for a planet."""
        text = f"<b>Planet:</b> {obj.name}<br>"
        text += f"<b>Type:</b> {obj.planet_type.name}<br>"
        text += f"<b>Orbit:</b> Ring {obj.orbit_distance}<br>"
        
        # Mass formatting
        m_earth = 5.97e24
        m_jup = 1.89e27
        if obj.mass >= m_jup:
            m_str = f"{obj.mass/m_jup:.2f} M_Jup"
        elif obj.mass >= m_earth:
            m_str = f"{obj.mass/m_earth:.2f} M_Earth"
        else:
            m_str = f"{obj.mass/m_earth:.4f} M_Earth"
            
        text += f"<b>Mass:</b> {m_str}<br>"
        text += f"<b>Radius:</b> {obj.radius/1000.0:.0f} km<br>"
        text += f"<b>Gravity:</b> {obj.surface_gravity/9.81:.2f} g<br>"
        text += f"<b>Temp:</b> {int(obj.surface_temperature)} K<br>"
        text += f"<b>Water:</b> {obj.surface_water*100:.0f}%<br>"
        text += f"<b>Pressure:</b> {obj.total_pressure_atm:.2f} atm<br>"
        return text

    def _format_atmosphere_raw(self, planet):
        html = f"<b>Atmosphere ({planet.total_pressure_atm:.2f} atm):</b><br>"
        for gas, pa in planet.atmosphere.items():
            html += f" {gas}: {pa:.1f} Pa<br>"
        return html

        
    def update(self, dt):
        """Update UI logic."""
        self.manager.update(dt)
 
    def draw(self, screen):
        """Draw the strategy scene UI elements."""
        self.manager.draw_ui(screen)
        
        # Draw Debug/Placeholder Text (bottom left)
        font = pygame.font.SysFont("arial", 20)
        mode_text = font.render(f"Strategy Layer | Zoom: {self.scene.camera.zoom:.2f}", True, (255, 255, 255))
        screen.blit(mode_text, (20, self.height - 30))

    def on_ui_selection(self, obj):
        """Handle selection of an object from any UI panel."""
        if hasattr(self.scene, 'on_ui_selection'):
            self.scene.on_ui_selection(obj)

    def handle_event(self, event):
        """Pass events to pygame_gui and handle custom UI logic."""
        self.manager.process_events(event)
        
        if self.system_tree.process_event(event):
             pass
             
        if self.sector_tree.process_event(event):
             pass
             
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == self.btn_planets:
                self.open_planet_list()
            elif event.ui_element == self.btn_raw_data:
                self.show_raw_data_popup()
            elif event.ui_element == self.btn_colonize:
                # Check current selection from detail panel context
                # Assuming current selection is NOT just 'obj' but stored in self.current_selection
                
                obj = self.current_selection
                
                # Logic: Issues order mostly from Fleet
                if hasattr(obj, 'ships'): # Is Fleet
                     # Find Uncolonized Planets at Fleet Location
                     from game.strategy.data.hex_math import hex_distance # Import if needed or check equality
                     
                     if not hasattr(self.scene, 'galaxy'): return
                     
                     # Fleet location
                     f_loc = obj.location
                     
                     # Find System
                     system = self.scene.galaxy.get_system_of_object(obj)
                     if not system: 
                         print("Colonize: Fleet not in system?")
                         return
                         
                     # Find planets at this location (SYSTEM)
                     candidates = []
                     for p in system.planets:
                         # Any planet in system is reachable if fleet is at system
                         if p.owner_id is None: # Unowned
                             candidates.append(p)
                                 
                     if not candidates:
                         # Feedback?
                         print("No unowned planets at this location.")
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
        width = 800 # Increased width for details
        height = 500
        x = (self.width - width) / 2
        y = (self.height - height) / 2
        
        rect = pygame.Rect(x, y, width, height)
        # Use existing class
        PlanetSelectionWindow(rect, self.manager, planets, on_select, self.format_planet_info)

    def open_planet_list(self):
        """Open the Planet List Window."""
        w, h = self.width * 0.9, self.height * 0.9
        rect = pygame.Rect((self.width - w)/2, (self.height - h)/2, w, h)
        
        # Get Empire (current player)
        empire = self.scene.current_empire
        galaxy = self.scene.galaxy
        
        PlanetListWindow(rect, self.manager, galaxy, empire, asset_resolver=self._get_object_asset)
