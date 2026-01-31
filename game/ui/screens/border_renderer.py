"""
UI Border Drawing Utilities

Provides functions to draw styled sci-fi borders using corner and edge images.
"""
import os
import pygame


class BorderRenderer:
    """Renders sci-fi style borders using corner and edge image assets."""
    
    _instance = None
    
    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def __init__(self):
        self.corners = {}
        self.edges = {}
        self._loaded = False
        
    def load_assets(self, base_path: str):
        """Load border assets from the UI images folder."""
        if self._loaded:
            return
            
        ui_path = os.path.join(base_path, "Resources", "Images", "UI")
        
        # Load corners
        corner_names = ['corner_top_left', 'corner_top_right', 
                        'corner_bottom_left', 'corner_bottom_right']
        for name in corner_names:
            path = os.path.join(ui_path, f"{name}.png")
            if os.path.exists(path):
                img = pygame.image.load(path).convert_alpha()
                self.corners[name] = img
                
        # Load edges
        edge_names = ['edge_horizontal', 'edge_vertical']
        for name in edge_names:
            path = os.path.join(ui_path, f"{name}.png")
            if os.path.exists(path):
                img = pygame.image.load(path).convert_alpha()
                self.edges[name] = img
                
        self._loaded = True
        
    def draw_border(self, surface: pygame.Surface, rect: pygame.Rect, 
                    corner_size: int = 64, edge_thickness: int = 16):
        """
        Draw a sci-fi border around the given rect.
        
        Args:
            surface: The pygame surface to draw on
            rect: The rectangle to draw the border around
            corner_size: Size of corner pieces (default 64)
            edge_thickness: Thickness of edge pieces (default 16)
        """
        if not self._loaded:
            return
            
        x, y, w, h = rect.x, rect.y, rect.width, rect.height
        
        # Draw corners
        if 'corner_top_left' in self.corners:
            corner = self.corners['corner_top_left']
            scaled = pygame.transform.scale(corner, (corner_size, corner_size))
            surface.blit(scaled, (x, y))
            
        if 'corner_top_right' in self.corners:
            corner = self.corners['corner_top_right']
            scaled = pygame.transform.scale(corner, (corner_size, corner_size))
            surface.blit(scaled, (x + w - corner_size, y))
            
        if 'corner_bottom_left' in self.corners:
            corner = self.corners['corner_bottom_left']
            scaled = pygame.transform.scale(corner, (corner_size, corner_size))
            surface.blit(scaled, (x, y + h - corner_size))
            
        if 'corner_bottom_right' in self.corners:
            corner = self.corners['corner_bottom_right']
            scaled = pygame.transform.scale(corner, (corner_size, corner_size))
            surface.blit(scaled, (x + w - corner_size, y + h - corner_size))
        
        # Draw horizontal edges (top and bottom)
        if 'edge_horizontal' in self.edges:
            edge = self.edges['edge_horizontal']
            edge_w = edge.get_width()
            
            # Top edge
            top_start = x + corner_size
            top_end = x + w - corner_size
            current = top_start
            while current < top_end:
                tile_w = min(edge_w, top_end - current)
                if tile_w > 0:
                    if tile_w < edge_w:
                        # Partial tile
                        sub = edge.subsurface((0, 0, tile_w, edge.get_height()))
                        scaled = pygame.transform.scale(sub, (tile_w, edge_thickness))
                    else:
                        scaled = pygame.transform.scale(edge, (edge_w, edge_thickness))
                    surface.blit(scaled, (current, y))
                current += edge_w
                
            # Bottom edge
            current = top_start
            while current < top_end:
                tile_w = min(edge_w, top_end - current)
                if tile_w > 0:
                    if tile_w < edge_w:
                        sub = edge.subsurface((0, 0, tile_w, edge.get_height()))
                        scaled = pygame.transform.scale(sub, (tile_w, edge_thickness))
                    else:
                        scaled = pygame.transform.scale(edge, (edge_w, edge_thickness))
                    surface.blit(scaled, (current, y + h - edge_thickness))
                current += edge_w
        
        # Draw vertical edges (left and right)
        if 'edge_vertical' in self.edges:
            edge = self.edges['edge_vertical']
            edge_h = edge.get_height()
            
            # Left edge
            left_start = y + corner_size
            left_end = y + h - corner_size
            current = left_start
            while current < left_end:
                tile_h = min(edge_h, left_end - current)
                if tile_h > 0:
                    if tile_h < edge_h:
                        sub = edge.subsurface((0, 0, edge.get_width(), tile_h))
                        scaled = pygame.transform.scale(sub, (edge_thickness, tile_h))
                    else:
                        scaled = pygame.transform.scale(edge, (edge_thickness, edge_h))
                    surface.blit(scaled, (x, current))
                current += edge_h
                
            # Right edge
            current = left_start
            while current < left_end:
                tile_h = min(edge_h, left_end - current)
                if tile_h > 0:
                    if tile_h < edge_h:
                        sub = edge.subsurface((0, 0, edge.get_width(), tile_h))
                        scaled = pygame.transform.scale(sub, (edge_thickness, tile_h))
                    else:
                        scaled = pygame.transform.scale(edge, (edge_thickness, edge_h))
                    surface.blit(scaled, (x + w - edge_thickness, current))
                current += edge_h
                
    def draw_corners_only(self, surface: pygame.Surface, rect: pygame.Rect,
                          corner_size: int = 48):
        """
        Draw only corner brackets (no edge pieces) - creates a more minimal look.
        
        Args:
            surface: The pygame surface to draw on
            rect: The rectangle to draw corners around
            corner_size: Size of corner pieces (default 48)
        """
        if not self._loaded:
            return
            
        x, y, w, h = rect.x, rect.y, rect.width, rect.height
        
        if 'corner_top_left' in self.corners:
            corner = self.corners['corner_top_left']
            scaled = pygame.transform.scale(corner, (corner_size, corner_size))
            surface.blit(scaled, (x, y))
            
        if 'corner_top_right' in self.corners:
            corner = self.corners['corner_top_right']
            scaled = pygame.transform.scale(corner, (corner_size, corner_size))
            surface.blit(scaled, (x + w - corner_size, y))
            
        if 'corner_bottom_left' in self.corners:
            corner = self.corners['corner_bottom_left']
            scaled = pygame.transform.scale(corner, (corner_size, corner_size))
            surface.blit(scaled, (x, y + h - corner_size))
            
        if 'corner_bottom_right' in self.corners:
            corner = self.corners['corner_bottom_right']
            scaled = pygame.transform.scale(corner, (corner_size, corner_size))
            surface.blit(scaled, (x + w - corner_size, y + h - corner_size))
