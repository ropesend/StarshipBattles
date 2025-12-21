import os
import json
import pygame
from logger import log_info, log_error

class ShipThemeManager:
    _instance = None
    
    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = ShipThemeManager()
        return cls._instance
        
    def __init__(self):
        if ShipThemeManager._instance is not None:
             raise Exception("This class is a singleton!")
             
        self.themes = {}  # {theme_name: {class_name: surface}}
        self.base_path = None
        self.default_theme = "Federation"
        self.loaded = False
        
    def initialize(self, base_path):
        """Load all themes from resources/ShipThemes."""
        self.base_path = base_path
        themes_dir = os.path.join(base_path, "resources", "ShipThemes")
        
        if not os.path.exists(themes_dir):
            log_error(f"ShipThemes directory not found: {themes_dir}")
            return
            
        # Walk directories
        for entry in os.scandir(themes_dir):
            if entry.is_dir():
                self._load_theme(entry.path)
                
        self.loaded = True
        log_info(f"Loaded {len(self.themes)} ship themes: {list(self.themes.keys())}")

    def _load_theme(self, theme_dir):
        """Load a specific theme directory using theme.json."""
        json_path = os.path.join(theme_dir, "theme.json")
        if not os.path.exists(json_path):
            return # Skip directories without theme.json
            
        try:
            with open(json_path, 'r') as f:
                data = json.load(f)
                
            theme_name = data.get('name', os.path.basename(theme_dir))
            image_map = data.get('images', {})
            
            self.themes[theme_name] = {}
            
            for ship_class, filename in image_map.items():
                img_path = os.path.join(theme_dir, filename)
                if os.path.exists(img_path):
                    try:
                        surf = pygame.image.load(img_path).convert_alpha()
                        self.themes[theme_name][ship_class] = surf
                    except Exception as e:
                        log_error(f"Failed to load image {img_path}: {e}")
                else:
                    log_error(f"Image not found for {theme_name}/{ship_class}: {filename}")
                    
        except Exception as e:
            log_error(f"Failed to load theme {theme_dir}: {e}")

    def get_image(self, theme_name, ship_class):
        """Get the image surface for a specific theme and class."""
        if not self.loaded:
            return self._create_fallback_image(ship_class)
            
        # Fallback to default if theme missing
        if theme_name not in self.themes:
            theme_name = self.default_theme
            
        if theme_name in self.themes:
            if ship_class in self.themes[theme_name]:
                return self.themes[theme_name][ship_class]
            
        return self._create_fallback_image(ship_class)

    def _create_fallback_image(self, ship_class):
        """Generate a placeholder image."""
        # Simple colored rectangle with text
        surf = pygame.Surface((100, 100), pygame.SRCALPHA)
        pygame.draw.rect(surf, (100, 100, 100), surf.get_rect(), 2)
        pygame.draw.line(surf, (100, 100, 100), (50, 20), (50, 80), 2)
        pygame.draw.line(surf, (100, 100, 100), (20, 50), (80, 50), 2)
        return surf

    def get_available_themes(self):
        """Return list of available theme names."""
        return list(self.themes.keys())
