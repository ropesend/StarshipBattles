import os
import pygame
import threading
from game.core.logger import log_info, log_error
from game.core.json_utils import load_json
from game.core.profiling import profile_block
from game.core.constants import ASSET_DIR
from game.core.exceptions import StateException

class ShipThemeManager:
    """
    Singleton manager for ship visual themes.

    Thread Safety:
        - Instance creation is thread-safe via double-checked locking

    Usage:
        manager = ShipThemeManager.instance()
        surface = manager.load_image("Federation", "Escort")

    Testing:
        - Use reset() to destroy instance completely
        - Use clear() to reset caches but preserve instance
    """
    _instance = None
    _lock = threading.Lock()

    @classmethod
    def instance(cls) -> 'ShipThemeManager':
        """
        Get the singleton instance, creating it if necessary.

        Thread-safe via double-checked locking pattern.

        Returns:
            The singleton ShipThemeManager instance
        """
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance


    def __init__(self):
        if ShipThemeManager._instance is not None:
            raise StateException(
                "ShipThemeManager is a singleton. Use ShipThemeManager.instance()",
                code="STM001"
            )
             
        # self.themes acts as the image cache: {theme_name: {class_name: surface}}
        self.themes = {}  
        
        # Store paths and metadata for lazy loading
        self.theme_data = {}
        
        # Cache for metrics
        self.image_metrics = {} # {theme_name: {class_name: rect}}

        # Cache for portrait images
        self.portraits = {}  # {theme_name: {class_name: surface}}

        self.base_path = None
        self.default_theme = "Federation"
        self.discovery_complete = False
        self._init_lock = threading.Lock()
        self._io_lock = threading.Lock() # For on-demand loading
        
    def clear(self):
        """Reset all caches and state. Used for test isolation."""
        with self._init_lock:
            with self._io_lock:
                self.themes = {}
                self.theme_data = {}
                self.image_metrics = {}
                self.portraits = {}
                self.discovery_complete = False
                log_info("ShipThemeManager caches cleared.")

    @classmethod
    def reset(cls):
        """
        Completely destroy the singleton instance.

        WARNING: For testing only! This destroys the singleton so a fresh
        instance is created on the next access.
        """
        with cls._lock:
            if cls._instance is not None:
                cls._instance.clear()  # Clean up state first
                cls._instance = None
        
    def initialize(self, base_path=None):
        """Discover all themes from assets/ShipThemes without loading images."""
        with self._init_lock:
            if self.discovery_complete and self.theme_data:
                return # Already initialized
                
            # base_path is now deprecated/ignored in favor of ASSET_DIR
            self.base_path = base_path 
            themes_dir = os.path.join(ASSET_DIR, "ShipThemes")
            
            if not os.path.exists(themes_dir):
                log_error(f"ShipThemes directory not found: {themes_dir}")
                return
                
            # Walk directories (Fast discovery)
            with profile_block("Theme: Discover All"):
                # Clear existing data before re-discovery to ensure consistency
                self.theme_data = {}
                for entry in os.scandir(themes_dir):
                    if entry.is_dir():
                        self._discover_theme(entry.path)
                    
            self.discovery_complete = True
            log_info(f"Discovered {len(self.theme_data)} ship themes: {list(self.theme_data.keys())}")

    def _discover_theme(self, theme_dir):
        """Read theme.json and store paths/metadata."""
        json_path = os.path.join(theme_dir, "theme.json")
        data = load_json(json_path)
        if data is None:
            return

        try:
            theme_name = data.get('name', os.path.basename(theme_dir))
            image_map = data.get('images', {})
            
            self.theme_data[theme_name] = {}
            
            for ship_class, data_entry in image_map.items():
                filename = ""
                manual_scale = 1.0
                
                if isinstance(data_entry, str):
                    filename = data_entry
                elif isinstance(data_entry, dict):
                    filename = data_entry.get('file', '')
                    manual_scale = data_entry.get('scale', 1.0)
                
                if not filename: continue
                
                img_path = os.path.join(theme_dir, filename)
                # We verify existence now to avoid errors later, but don't load
                if os.path.exists(img_path):
                    self.theme_data[theme_name][ship_class] = {
                        'path': img_path,
                        'scale': manual_scale
                    }
                else:
                    log_error(f"Image not found for {theme_name}/{ship_class}: {filename}")
                    
        except (KeyError, TypeError, ValueError) as e:
            log_error(f"Failed to discover theme {theme_dir}: {e}")

    def load_image(self, theme_name, ship_class):
        """Load the image surface for a specific theme and class. Returns cached copy if available."""
        if not self.discovery_complete:
            return self._create_fallback_image(ship_class)
            
        # Fallback to default if theme missing
        if theme_name not in self.theme_data:
            theme_name = self.default_theme
            
        # Check Cache
        if theme_name in self.themes and ship_class in self.themes[theme_name]:
            return self.themes[theme_name][ship_class]
            
        # Load on demand
        if theme_name in self.theme_data and ship_class in self.theme_data[theme_name]:
            return self._load_single_image(theme_name, ship_class)
            
        return self._create_fallback_image(ship_class)

    def _load_single_image(self, theme_name, ship_class):
        """Load a single image from disk and cache it."""
        with self._io_lock:
            # Double-check cache after acquiring lock
            if theme_name in self.themes and ship_class in self.themes[theme_name]:
                return self.themes[theme_name][ship_class]
                
            data = self.theme_data[theme_name][ship_class]
            path = data['path']
            
            try:
                with profile_block(f"Theme: Lazy Load ({ship_class})"):
                    surf = pygame.image.load(path).convert_alpha()
                    
                    # Update Cache
                    if theme_name not in self.themes: self.themes[theme_name] = {}
                    self.themes[theme_name][ship_class] = surf
                    
                    # Update Metrics
                    rect = surf.get_bounding_rect(min_alpha=20)
                    if theme_name not in self.image_metrics: self.image_metrics[theme_name] = {}
                    self.image_metrics[theme_name][ship_class] = rect
                    
                    return surf
            except FileNotFoundError as e:
                log_error(f"Lazy load failed - file not found {path}: {e}")
                return self._create_fallback_image(ship_class)
            except pygame.error as e:
                log_error(f"Lazy load failed for {path} (pygame error): {e}")
                return self._create_fallback_image(ship_class)

    def get_image_metrics(self, theme_name, ship_class):
        """Get the visible bounding rect for the image."""
        if not self.discovery_complete: return None
        
        if theme_name not in self.theme_data: theme_name = self.default_theme
        
        # Check cache
        with self._io_lock:
            if theme_name in self.image_metrics and ship_class in self.image_metrics[theme_name]:
                return self.image_metrics[theme_name][ship_class]

        # Call load_image (which handles locking internally and calculates metrics if successful)
        surf = self.load_image(theme_name, ship_class)
        
        # Re-check cache with lock
        with self._io_lock:
            if theme_name in self.image_metrics and ship_class in self.image_metrics[theme_name]:
                 return self.image_metrics[theme_name][ship_class]
            
            # If still not in metrics (e.g. fallback image), calculate on the fly
            # This ensures we never return None if discovery is complete
            if surf:
                rect = surf.get_bounding_rect(min_alpha=1)
                # Cache it for the fallback case too to prevent re-calc
                if theme_name not in self.image_metrics: self.image_metrics[theme_name] = {}
                self.image_metrics[theme_name][ship_class] = rect
                return rect
        
        return None

    def get_manual_scale(self, theme_name, ship_class):
        """Get manual scale factor for a ship (default 1.0)."""
        if not self.discovery_complete: return 1.0
        if theme_name not in self.theme_data: theme_name = self.default_theme
        
        if theme_name in self.theme_data and ship_class in self.theme_data[theme_name]:
            return self.theme_data[theme_name][ship_class].get('scale', 1.0)
        return 1.0

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
        return list(self.theme_data.keys())

    def get_portrait_image(self, theme_name, ship_class):
        """
        Get the portrait image for a specific theme and ship class.

        Portrait images are located in {theme_dir}/Portraits/{ShipClass}_Portrait.jpg
        These are artistic side-view images, as opposed to the top-down gameplay sprites.

        Args:
            theme_name: Theme name (e.g., "Atlantians")
            ship_class: Ship class name (e.g., "Battleship", "Fighter (Medium)")

        Returns:
            pygame.Surface or None if not found
        """
        if not self.discovery_complete:
            return None

        # Fallback to default if theme missing
        if theme_name not in self.theme_data:
            theme_name = self.default_theme

        # Check cache
        if theme_name in self.portraits and ship_class in self.portraits[theme_name]:
            return self.portraits[theme_name][ship_class]

        # Load on demand
        return self._load_portrait_image(theme_name, ship_class)

    def _load_portrait_image(self, theme_name, ship_class):
        """Load a portrait image from disk and cache it."""
        with self._io_lock:
            # Double-check cache after acquiring lock
            if theme_name in self.portraits and ship_class in self.portraits[theme_name]:
                return self.portraits[theme_name][ship_class]

            # Convert ship class to portrait filename format
            # e.g., "Fighter (Medium)" -> "MediumFighter_Portrait.jpg"
            # e.g., "Battleship" -> "Battleship_Portrait.jpg"
            portrait_name = self._ship_class_to_portrait_name(ship_class)
            portrait_filename = f"{portrait_name}_Portrait.jpg"

            # Get theme directory from theme_data
            # We need to find the theme directory - look at any existing path
            theme_dir = None
            if theme_name in self.theme_data and self.theme_data[theme_name]:
                # Get any path and derive theme dir from it
                any_ship = next(iter(self.theme_data[theme_name].values()))
                any_path = any_ship['path']
                # Path is like: .../ShipThemes/Atlantians/Skins/Escort.png
                # Theme dir is: .../ShipThemes/Atlantians
                theme_dir = os.path.dirname(os.path.dirname(any_path))

            if not theme_dir:
                theme_dir = os.path.join(ASSET_DIR, "ShipThemes", theme_name)

            portrait_path = os.path.join(theme_dir, "Portraits", portrait_filename)

            if os.path.exists(portrait_path):
                try:
                    surf = pygame.image.load(portrait_path).convert_alpha()

                    # Update cache
                    if theme_name not in self.portraits:
                        self.portraits[theme_name] = {}
                    self.portraits[theme_name][ship_class] = surf

                    return surf
                except FileNotFoundError as e:
                    log_error(f"Portrait file not found {portrait_path}: {e}")
                except pygame.error as e:
                    log_error(f"Failed to load portrait {portrait_path} (pygame error): {e}")

            return None

    def _ship_class_to_portrait_name(self, ship_class):
        """
        Convert ship class name to portrait filename format.

        Examples:
            "Fighter (Medium)" -> "MediumFighter"
            "Satellite (Heavy)" -> "HeavySatellite"
            "Battleship" -> "Battleship"
            "Light Cruiser" -> "LightCruiser"
        """
        # Handle compound names with parentheses (e.g., "Fighter (Medium)")
        if "(" in ship_class and ")" in ship_class:
            # Split on " (" to get base and modifier
            parts = ship_class.replace(")", "").split(" (")
            if len(parts) == 2:
                base = parts[0]  # e.g., "Fighter"
                modifier = parts[1]  # e.g., "Medium"
                return f"{modifier}{base}"

        # Handle space-separated names (e.g., "Light Cruiser")
        return ship_class.replace(" ", "")
