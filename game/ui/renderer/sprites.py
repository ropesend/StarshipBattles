import pygame
import os
from game.core.logger import log_info, log_error
from game.core.singleton import SingletonMeta


class SpriteManager(metaclass=SingletonMeta):
    """
    Singleton manager for component sprite images.

    Thread Safety:
        - Instance creation is thread-safe via SingletonMeta

    Usage:
        manager = SpriteManager.instance()
        sprite = manager.get_sprite(index)

    Testing:
        - Use reset() to destroy instance completely
    """

    def __init__(self):
        self.sprites = []
        self.tile_size = 36

    def load_sprites(self, base_path):
        """
        Loads sprites from assets/Images/Components if available.
        Checks for 'Tiles' subdirectory first, then falls back to base directory.
        """
        components_dir = os.path.join(base_path, "assets", "Images", "Components")
        tiles_dir = os.path.join(components_dir, "Tiles")
        
        if os.path.exists(tiles_dir):
            self._load_from_directory(tiles_dir)
        elif os.path.exists(components_dir):
            self._load_from_directory(components_dir)
        else:
            log_error(f"No sprite directory found at {tiles_dir} or {components_dir}")

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
            except (FileNotFoundError, OSError, pygame.error) as e:
                log_error(f"loading {f}: {e}")
                continue
        
        # Populate self.sprites list
        if max_index >= 0:
            self.sprites = [None] * (max_index + 1)
            for idx, img in loaded_sprites.items():
                self.sprites[idx] = img
                
        log_info(f"Loaded {len(loaded_sprites)} sprites from directory (max index {max_index})")

    def get_sprite(self, index):
        if 0 <= index < len(self.sprites):
            return self.sprites[index]
        return None # Should handle missing sprite ideally
