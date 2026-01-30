import os
import pygame
import threading
from game.core.json_utils import load_json
from game.core.logger import log_error, log_info, log_warning
from game.core.paths import Paths
from game.core.exceptions import StateException


class AssetManager:
    """
    Singleton manager for game assets (images, etc.).

    Thread Safety:
        - Instance creation is thread-safe via double-checked locking

    Usage:
        manager = AssetManager.instance()
        image = manager.load_image("category", "key")

    Testing:
        - Use reset() to destroy instance completely
        - Use clear() to reset caches but preserve instance
    """
    _instance = None
    _lock = threading.Lock()

    def __init__(self):
        if AssetManager._instance is not None:
            raise StateException(
                "AssetManager is a singleton. Use AssetManager.instance()",
                code="AM001"
            )
        self.assets = {}  # Cache: {key: Surface} or {key: [Surfaces]}
        self.manifest = {}
        self.manifest_path = Paths.ASSET_MANIFEST_FILE
        self.missing_texture = None

    @classmethod
    def instance(cls) -> 'AssetManager':
        """
        Get the singleton instance, creating it if necessary.

        Thread-safe via double-checked locking pattern.

        Returns:
            The singleton AssetManager instance
        """
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance

    @classmethod
    def reset(cls):
        """
        Completely destroy the singleton instance.

        WARNING: For testing only! This destroys the singleton so a fresh
        instance is created on the next access.
        """
        with cls._lock:
            cls._instance = None

    def clear(self):
        """Reset all caches. Used for test isolation."""
        self.assets = {}
        self.manifest = {}
        self.missing_texture = None 
        
    def load_manifest(self, path=None):
        """Load the asset manifest JSON."""
        if path:
            self.manifest_path = path
            
        if not os.path.exists(self.manifest_path):
            log_error(f"Asset Manifest not found: {self.manifest_path}")
            return

        data = load_json(self.manifest_path)
        if data:
            self.manifest = data
            log_info(f"Loaded asset manifest from {self.manifest_path}")
        else:
            log_error(f"Failed to load asset manifest from {self.manifest_path}")

    def load_image(self, category, key):
        """Load a single image from the manifest. Returns cached copy if available."""
        # Check cache
        cache_key = f"{category}.{key}"
        if cache_key in self.assets:
            return self.assets[cache_key]
        
        # Resolve path
        cat_data = self.manifest.get(category, {})
        file_path = cat_data.get(key)
        
        if not file_path:
            log_warning(f"Asset not found in manifest: {category}.{key}")
            return self.get_missing_texture()

        # Load
        try:
            return self._load_image(cache_key, file_path)
        except FileNotFoundError as e:
            log_error(f"Image file not found {file_path}: {e}")
            return self.get_missing_texture()
        except pygame.error as e:
            log_error(f"Failed to load image {file_path} (pygame error): {e}")
            return self.get_missing_texture()

    def load_group(self, category, group_key):
        """Load a group of images (e.g., planet variations). Returns cached copy if available."""
        cache_key = f"{category}.{group_key}"
        if cache_key in self.assets:
            return self.assets[cache_key]
            
        cat_data = self.manifest.get(category, {})
        file_paths = cat_data.get(group_key)
        
        if not file_paths or not isinstance(file_paths, list):
            log_warning(f"Asset group not found in manifest: {category}.{group_key}")
            return [self.get_missing_texture()]

        images = []
        for i, path in enumerate(file_paths):
            sub_key = f"{cache_key}.{i}"
            try:
                images.append(self._load_image(sub_key, path))
            except FileNotFoundError as e:
                log_error(f"Group image file not found {path}: {e}")
            except pygame.error as e:
                log_error(f"Failed to load group image {path} (pygame error): {e}")
        
        self.assets[cache_key] = images
        return images
        
    def get_random_from_group(self, category, group_key, seed_id=None):
        """Get a specific item from a group deterministically using an ID."""
        group = self.load_group(category, group_key)
        if not group:
            return self.get_missing_texture()

        if seed_id is not None:
             idx = seed_id % len(group)
             return group[idx]
        return group[0]

    def get_star_color_key(self, rgb: tuple) -> str:
        """
        Determine the star asset key based on RGB color values.

        Uses thresholds defined in manifest's 'star_colors' section.
        Returns 'yellow' as default if no rules match.

        Args:
            rgb: Tuple of (r, g, b) color values (0-255)

        Returns:
            Star asset key string (e.g., 'red', 'blue', 'yellow')
        """
        star_colors = self.manifest.get('star_colors', {})
        r, g, b = rgb[0], rgb[1], rgb[2]

        for color_name, thresholds in star_colors.items():
            if not thresholds:  # Empty dict = default (yellow)
                continue

            matches = True
            if 'r_min' in thresholds and r <= thresholds['r_min']:
                matches = False
            if 'r_max' in thresholds and r >= thresholds['r_max']:
                matches = False
            if 'g_min' in thresholds and g <= thresholds['g_min']:
                matches = False
            if 'g_max' in thresholds and g >= thresholds['g_max']:
                matches = False
            if 'b_min' in thresholds and b <= thresholds['b_min']:
                matches = False
            if 'b_max' in thresholds and b >= thresholds['b_max']:
                matches = False

            if matches:
                return color_name

        return 'yellow'  # default

    def load_external_image(self, path):
        """Load an image from an absolute or relative path, using the cache."""
        if not path:
             return self.get_missing_texture()
             
        # Normalize path for cache key
        norm_path = os.path.normpath(path)
        cache_key = f"external.{norm_path}"
        
        if cache_key in self.assets:
             return self.assets[cache_key]
             
        try:
             return self._load_image(cache_key, norm_path)
        except FileNotFoundError as e:
             log_error(f"External image file not found {path}: {e}")
             return self.get_missing_texture()
        except pygame.error as e:
             log_error(f"Failed to load external image {path} (pygame error): {e}")
             return self.get_missing_texture()

    def _load_image(self, cache_key, path):
        """Internal load helper."""
        if not os.path.exists(path):
            raise FileNotFoundError(f"File not found: {path}")
            
        # Extension handling
        if path.lower().endswith('.jpg') or path.lower().endswith('.jpeg'):
             img = pygame.image.load(path).convert()
        else:
             img = pygame.image.load(path).convert_alpha()
             
        self.assets[cache_key] = img
        return img
        
    def get_missing_texture(self):
        """Return a placeholder texture."""
        if self.missing_texture:
            return self.missing_texture
            
        s = pygame.Surface((32, 32))
        s.fill((255, 0, 255)) # Hot pink
        self.missing_texture = s
        return s

# Global Accessor (uses singleton pattern now)
def get_asset_manager():
    """Get the AssetManager singleton instance."""
    return AssetManager.instance()
