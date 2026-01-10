import pygame
import pygame_gui


class StrategyInterface:
    """Handles all UI rendering and interaction for the StrategyScene."""
    
    def __init__(self, scene, screen_width, screen_height):
        self.scene = scene
        self.width = screen_width
        self.height = screen_height
        
        # UI State
        self.manager = pygame_gui.UIManager((screen_width, screen_height))
        
        # System Info Panel (Initially hidden or empty)
        self.panel_rect = pygame.Rect(10, screen_height - 210, 300, 200)
        self.info_panel = pygame_gui.elements.UIPanel(
            relative_rect=self.panel_rect,
            manager=self.manager
        )
        
        self.info_label = pygame_gui.elements.UITextBox(
            html_text="Select a system...",
            relative_rect=pygame.Rect(10, 10, 280, 180),
            manager=self.manager,
            container=self.info_panel
        )
        
    def handle_resize(self, width, height):
        """Update UI elements for new resolution."""
        self.width = width
        self.height = height
        self.manager.set_window_resolution((width, height))
        
        # Reposition Panel (Bottom Left)
        self.panel_rect.y = height - 210
        self.info_panel.set_relative_position(self.panel_rect.topleft)
        
    def show_object_info(self, obj):
        """Update info panel with object data."""
        if not obj:
            self.info_label.set_text("Select an object...")
            return
            
        text = ""
        # Check type loosely or explicitly
        if hasattr(obj, 'star_type'): # StarSystem
            text = f"<b>System:</b> {obj.name}<br>"
            text += f"<b>Star:</b> {obj.star_type.name}<br>"
            text += f"<b>Planets:</b> {len(obj.planets)}<br>"
            text += f"<b>Warp Points:</b> {len(obj.warp_points)}<br>"
            text += f"<b>Location:</b> {obj.global_location}"
            
        elif hasattr(obj, 'planet_type'): # Planet
            text = f"<b>Planet:</b> {obj.planet_type.name}<br>"
            text += f"<b>Orbit:</b> Ring {obj.orbit_distance}<br>"
            text += f"<b>Local Loc:</b> {obj.location}"
            
        elif hasattr(obj, 'ships'): # Fleet (duck typing)
            text = f"<b>Fleet:</b> {obj.id}<br>"
            text += f"<b>Owner:</b> {obj.owner_id}<br>"
            text += f"<b>Ships:</b> {len(obj.ships)}<br>"
            text += f"<b>Location:</b> {obj.location}<br>"
            text += f"<b>Dest:</b> {obj.destination}<br>"
            
        self.info_label.set_text(text)
        
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
        """Pass events to pygame_gui."""
        self.manager.process_events(event)
        
    def handle_click(self, mx, my, button):
        """Handle mouse clicks. Returns True if click was handled by UI."""
        # Check if click is inside panel
        if self.panel_rect.collidepoint(mx, my):
            return True
        return False
