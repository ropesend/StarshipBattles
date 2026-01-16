import os
import pygame
import logging
import threading
from game.core.json_utils import load_json


class AssetManager:
    """
    Singleton manager for game assets (images, etc.).

    Thread Safety:
        - Instance creation is thread-safe via double-checked locking

    Usage:
        manager = AssetManager.instance()
        image = manager.get_image("category", "key")

    Testing:
        - Use reset() to destroy instance completely
        - Use clear() to reset caches but preserve instance
    """
    _instance = None
    _lock = threading.Lock()

    def __init__(self):
        if AssetManager._instance is not None:
            raise Exception("AssetManager is a singleton. Use AssetManager.instance()")
        self.assets = {}  # Cache: {key: Surface} or {key: [Surfaces]}
        self.manifest = {}
        self.manifest_path = "assets/asset_manifest.json"
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
            logging.error(f"Asset Manifest not found: {self.manifest_path}")
            return

        data = load_json(self.manifest_path)
        if data:
            self.manifest = data
            logging.info(f"Loaded asset manifest from {self.manifest_path}")
        else:
            logging.error(f"Failed to load asset manifest from {self.manifest_path}")

    def get_image(self, category, key):
        """Get a single image. Loads if not cached."""
        # Check cache
        cache_key = f"{category}.{key}"
        if cache_key in self.assets:
            return self.assets[cache_key]
        
        # Resolve path
        cat_data = self.manifest.get(category, {})
        file_path = cat_data.get(key)
        
        if not file_path:
            logging.warning(f"Asset not found in manifest: {category}.{key}")
            return self.get_missing_texture()
            
        # Load
        try:
            return self._load_image(cache_key, file_path)
        except Exception as e:
            logging.error(f"Failed to load image {file_path}: {e}")
            return self.get_missing_texture()

    def get_group(self, category, group_key):
        """Get a list of images (e.g., planet variations)."""
        cache_key = f"{category}.{group_key}"
        if cache_key in self.assets:
            return self.assets[cache_key]
            
        cat_data = self.manifest.get(category, {})
        file_paths = cat_data.get(group_key)
        
        if not file_paths or not isinstance(file_paths, list):
            logging.warning(f"Asset group not found in manifest: {category}.{group_key}")
            return [self.get_missing_texture()]
            
        images = []
        for i, path in enumerate(file_paths):
            sub_key = f"{cache_key}.{i}"
            try:
                images.append(self._load_image(sub_key, path))
            except Exception as e:
                logging.error(f"Failed to load group image {path}: {e}")
        
        self.assets[cache_key] = images
        return images
        
    def get_random_from_group(self, category, group_key, seed_id=None):
        """Get a specific item from a group deterministically using an ID."""
        group = self.get_group(category, group_key)
        if not group:
            return self.get_missing_texture()
            
        if seed_id is not None:
             idx = seed_id % len(group)
             return group[idx]
        return group[0]

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
        except Exception as e:
             logging.error(f"Failed to load external image {path}: {e}")
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
