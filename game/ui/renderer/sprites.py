import pygame
import os
import threading
from game.core.logger import log_info, log_error

class SpriteManager:
    """
    Singleton manager for component sprite images.

    Thread Safety:
        - Instance creation is thread-safe via double-checked locking

    Usage:
        manager = SpriteManager.instance()
        sprite = manager.get_sprite(index)

    Testing:
        - Use reset() to destroy instance completely
    """
    _instance = None
    _lock = threading.Lock()

    def __init__(self):
        if SpriteManager._instance is not None:
            raise Exception("SpriteManager is a singleton. Use SpriteManager.instance()")
        self.atlas = None
        self.sprites = []
        self.tile_size = 36

    @classmethod
    def instance(cls) -> 'SpriteManager':
        """
        Get the singleton instance, creating it if necessary.

        Thread-safe via double-checked locking pattern.

        Returns:
            The singleton SpriteManager instance
        """
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance

    # Backwards compatibility alias
    get_instance = instance

    @classmethod
    def reset(cls):
        """
        Completely destroy the singleton instance.

        WARNING: For testing only! This destroys the singleton so a fresh
        instance is created on the next access.
        """
        with cls._lock:
            cls._instance = None

    def load_sprites(self, base_path):
        """
        Loads sprites from assets/Images/Components if available.
        Checks for 'Tiles' subdirectory first, then falls back to base directory.
        Falls back to loading atlas from older path if not.
        """
        components_dir = os.path.join(base_path, "assets", "Images", "Components")
        tiles_dir = os.path.join(components_dir, "Tiles")
        
        if os.path.exists(tiles_dir):
            self._load_from_directory(tiles_dir)
        elif os.path.exists(components_dir):
            self._load_from_directory(components_dir)
        else:
             # Fallback to old atlas
             atlas_path = os.path.join(base_path, "assets", "Images", "Components.bmp")
             self._load_atlas_file(atlas_path)

    def _load_from_directory(self, directory):
        log_info(f"Loading sprites from {directory}")
        # Reset sprites
        self.sprites = []
        
        files = os.listdir(directory)
        loaded_sprites = {}
        max_index = -1
        
        for f in files:
            lower_name = f.lower()
            if not lower_name.endswith(('.bmp', '.jpg', '.png')):
                continue
                
            index = -1
            try:
                # Parsing logic for different naming conventions
                if f.startswith("Comp_"):
                    # Comp_001.bmp
                    prefix_removed = f[5:] 
                    number_part = prefix_removed.split('.')[0]
                    index = int(number_part) - 1
                elif f.startswith("2048Portrait_Comp_"):
                    # 2048Portrait_Comp_001.jpg
                    prefix_removed = f[18:]
                    number_part = prefix_removed.split('.')[0]
                    index = int(number_part) - 1
                
                if index < 0: continue
                
                full_path = os.path.join(directory, f)
                image = pygame.image.load(full_path).convert()
                image.set_colorkey((0, 0, 0))
                
                loaded_sprites[index] = image
                if index > max_index:
                    max_index = index
                    
            except ValueError:
                continue
            except Exception as e:
                log_error(f"loading {f}: {e}")
                continue
        
        # Populate self.sprites list
        if max_index >= 0:
            self.sprites = [None] * (max_index + 1)
            for idx, img in loaded_sprites.items():
                self.sprites[idx] = img
                
        log_info(f"Loaded {len(loaded_sprites)} sprites from directory (max index {max_index})")

    def _load_atlas_file(self, path):
        if not os.path.exists(path):
            log_error(f"Atlas file not found at {path}")
            return
            
        try:
            # For BMP, usually convert() is safer than convert_alpha() unless it's 32-bit BMP
            self.atlas = pygame.image.load(path).convert() 
            # Assume black is transparent for now? Or Magenta? 
            # Let's auto-detect top-left pixel or just no transparency key for now
            self.atlas.set_colorkey((0, 0, 0)) # Common for BMP sprites
            
            self._slice_sprites()
            log_info(f"Loaded Atlas: {path} ({self.atlas.get_width()}x{self.atlas.get_height()})")

        except Exception as e:
            log_error(f"Exception loading atlas: {e}")
            import traceback
            traceback.print_exc()

    def _slice_sprites(self):
        self.sprites = []
        if not self.atlas: return
        
        cols = self.atlas.get_width() // self.tile_size
        rows = self.atlas.get_height() // self.tile_size
        
        # Assume generic grid order: left to right, top to bottom
        for y in range(rows):
            for x in range(cols):
                rect = pygame.Rect(x * self.tile_size, y * self.tile_size, self.tile_size, self.tile_size)
                self.sprites.append(self.atlas.subsurface(rect))

    def get_sprite(self, index):
        if 0 <= index < len(self.sprites):
            return self.sprites[index]
        return None # Should handle missing sprite ideally
