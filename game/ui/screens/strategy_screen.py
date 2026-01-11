import pygame
import pygame_gui
from game.strategy.data.fleet import OrderType

class StrategyInterface:
    """Handles all UI rendering and interaction for the StrategyScene."""
    
    def __init__(self, scene, screen_width, screen_height):
        self.scene = scene
        self.width = screen_width
        self.height = screen_height
        self.sidebar_width = 600
        
        # UI State
        self.manager = pygame_gui.UIManager((screen_width, screen_height))
        
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
        
        self.system_list = pygame_gui.elements.UISelectionList(
            relative_rect=pygame.Rect(10, 40, self.sidebar_width - 40, rect_system.height - 50),
            item_list=[],
            manager=self.manager,
            container=self.system_panel
        )
        
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
        
        self.sector_list = pygame_gui.elements.UISelectionList(
            relative_rect=pygame.Rect(10, 40, self.sidebar_width - 40, rect_sector.height - 50),
            item_list=[],
            manager=self.manager,
            container=self.sector_panel
        )
        
        # 3. Detail Panel (Bottom)
        rect_detail = pygame.Rect(-self.sidebar_width + 10, 10 + 2*panel_h_approx, self.sidebar_width - 20, panel_h_approx - gap)
        
        self.detail_panel = pygame_gui.elements.UIPanel(
            relative_rect=rect_detail,
            manager=self.manager,
            anchors={'left': 'right', 'right': 'right', 'top': 'top', 'bottom': 'top'}
        )
        
        # Portrait Image
        self.portrait_image = pygame_gui.elements.UIImage(
            relative_rect=pygame.Rect(10, 10, 200, 200),
            image_surface=pygame.Surface((200, 200)),
            manager=self.manager,
            container=self.detail_panel
        )
        
        # Info Text
        self.detail_text = pygame_gui.elements.UITextBox(
            html_text="Select an object for details.",
            relative_rect=pygame.Rect(220, 10, self.sidebar_width - 250, rect_detail.height - 20),
            manager=self.manager,
            container=self.detail_panel
        )
        
        # Mapping: Label -> Object
        self.current_system_objects = {}
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
        self.system_list.set_dimensions((self.sidebar_width - 40, panel_h_approx - 60))
        
        # Sector (Middle)
        self.sector_panel.set_dimensions((self.sidebar_width - 20, panel_h_approx - gap))
        self.sector_panel.set_relative_position((-self.sidebar_width + 10, 10 + panel_h_approx))
        self.sector_list.set_dimensions((self.sidebar_width - 40, panel_h_approx - 60))
        
        # Detail (Bottom)
        self.detail_panel.set_dimensions((self.sidebar_width - 20, panel_h_approx - gap))
        self.detail_panel.set_relative_position((-self.sidebar_width + 10, 10 + 2*panel_h_approx))
        self.detail_text.set_dimensions((self.sidebar_width - 250, panel_h_approx - 30))

    def show_system_info(self, system_obj, contents):
        """Populate Top List (System)."""
        if system_obj:
            self.system_header.set_text(f"System: {system_obj.name}")
        else:
            self.system_header.set_text("Deep Space (No System)")
            
        self.current_system_objects = {}
        item_labels = []
        
        for obj in contents:
            # Reusing label gen logic?
            label = self._get_label_for_obj(obj)
            # Uniquify
            if label in item_labels: label = f"{label} ({id(obj)})"
            
            item_labels.append(label)
            self.current_system_objects[label] = obj
            
        self.system_list.set_item_list(item_labels)

    def show_sector_info(self, hex_coord, contents):
        """Populate Middle List (Sector/Hex)."""
        self.sector_header.set_text(f"Sector: [{hex_coord.q}, {hex_coord.r}]")
        
        self.current_sector_objects = {}
        item_labels = []
        for obj in contents:
            label = self._get_label_for_obj(obj)
            if label in item_labels: label = f"{label} ({id(obj)})"
            item_labels.append(label)
            self.current_sector_objects[label] = obj
            
        self.sector_list.set_item_list(item_labels)
        
    def _get_label_for_obj(self, obj):
        if hasattr(obj, 'star_type'): return f"Star: {obj.star_type.name}"
        elif hasattr(obj, 'planet_type'): return f"Planet: {obj.planet_type.name}"
        elif hasattr(obj, 'destination_id'): return f"Warp Point -> {obj.destination_id}"
        elif hasattr(obj, 'ships'): return f"Fleet {obj.id} ({len(obj.ships)})"
        return "Unknown Object"
        
    def show_detailed_report(self, obj, portrait_surface=None):
        """Update the detail report implementation."""
        if not obj:
            return
            
        text = ""
        # Check type loosely or explicitly
        if hasattr(obj, 'star_type'): # StarSystem (representing the Star itself in the list)
            text = f"<b>Star:</b> {obj.name}<br>"
            text += f"<b>Class:</b> {obj.star_type.name}<br>"
            text += f"<b>Radius:</b> {obj.star_type.radius}<br>"
            text += f"<b>Temp:</b> {obj.star_type.color}<br>" # placeholder
            
        elif hasattr(obj, 'planet_type'): # Planet
            text = f"<b>Planet:</b> {obj.planet_type.name}<br>"
            text += f"<b>Orbit:</b> Ring {obj.orbit_distance}<br>"
            text += f"<b>Local Loc:</b> {obj.location}<br>"
            text += f"<br><i>Sample lore text about this {obj.planet_type.name} world.</i>"
            
        elif hasattr(obj, 'destination_id'): # Warp Point
            text = f"<b>Warp Point</b><br>"
            text += f"<b>Destination:</b> {obj.destination_id}<br>"
            text += f"<b>Local Loc:</b> {obj.location}<br>"
            
        elif hasattr(obj, 'ships'): # Fleet
            text = f"<b>Fleet:</b> {obj.id}<br>"
            text += f"<b>Owner:</b> {obj.owner_id}<br>"
            text += f"<b>Ships:</b> {len(obj.ships)}<br>"
            text += f"<b>Location:</b> {obj.location}<br>"
            text += f"<b>Location:</b> {obj.location}<br>"
            
            text += "<b>Orders:</b><br>"
            if obj.orders:
                for i, order in enumerate(obj.orders):
                    if order.type == OrderType.MOVE:
                         text += f" {i+1}. MOVE {order.target}<br>"
                    else:
                         text += f" {i+1}. {order.type.name}<br>"
            else:
                text += " (No Orders)<br>"
            
        self.detail_text.set_text(text)
        
        # Update Portrait
        if portrait_surface:
            self.portrait_image.set_image(portrait_surface)
        else:
             # Default/Fallback
             s = pygame.Surface((200, 200))
             s.fill((50, 50, 50))
             self.portrait_image.set_image(s)

        
    def update(self, dt):
        """Update UI logic."""
        self.manager.update(dt)
 
    def draw(self, screen):
        """Draw the strategy scene UI elements."""
        self.manager.draw_ui(screen)
        
        # Draw Debug/Placeholder Text
        font = pygame.font.SysFont("arial", 20)
        mode_text = font.render(f"Strategy Layer | Zoom: {self.scene.camera.zoom:.2f}", True, (255, 255, 255))
        screen.blit(mode_text, (20, 20))

    def handle_event(self, event):
        """Pass events to pygame_gui and handle custom UI logic."""
        self.manager.process_events(event)
        
        if event.type == pygame_gui.UI_SELECTION_LIST_NEW_SELECTION:
            obj = None
            if event.ui_element == self.sector_list:
                obj = self.current_sector_objects.get(event.text)
            elif event.ui_element == self.system_list:
                obj = self.current_system_objects.get(event.text)
                
            if obj:
                # We need to trigger the callback. 
                # Since we don't have a direct ref to the callback method here easily (unless we add it)
                # We can just return it? No, handle_event is void.
                # Actually, check if scene has `on_ui_selection`.
                if hasattr(self.scene, 'on_ui_selection'):
                    self.scene.on_ui_selection(obj)
                    
        
    def handle_click(self, mx, my, button):
        """Handle mouse clicks. Returns True if click was handled by UI."""
        # Check if click is inside sidebar area (simplified)
        if mx > self.width - self.sidebar_width:
            return True
        return False
