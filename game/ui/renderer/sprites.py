import logging
import pygame
import os
from typing import Optional
from game.core.singleton import SingletonMeta
from game.ui.colors import BLACK

logger = logging.getLogger(__name__)


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

    def load_sprites(self, base_path: str) -> None:
        """Load sprites from assets/Images/Components if available.

        Checks for 'Tiles' subdirectory first, then falls back to base directory.

        Args:
            base_path: Base path of the game installation.
        """
        components_dir = os.path.join(base_path, "assets", "Images", "Components")
        tiles_dir = os.path.join(components_dir, "Tiles")
        
        if os.path.exists(tiles_dir):
            self._load_from_directory(tiles_dir)
        elif os.path.exists(components_dir):
            self._load_from_directory(components_dir)
        else:
            logger.error(f"No sprite directory found at {tiles_dir} or {components_dir}")

    def _load_from_directory(self, directory: str) -> None:
        """Load sprites from a specific directory.

        Args:
            directory: Path to directory containing sprite files.
        """
        logger.info(f"Loading sprites from {directory}")
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
                image.set_colorkey(BLACK)
                
                loaded_sprites[index] = image
                if index > max_index:
                    max_index = index
                    
            except ValueError:
                continue
            except (FileNotFoundError, OSError, pygame.error) as e:
                logger.error(f"loading {f}: {e}")
                continue
        
        # Populate self.sprites list
        if max_index >= 0:
            self.sprites = [None] * (max_index + 1)
            for idx, img in loaded_sprites.items():
                self.sprites[idx] = img
                
        logger.info(f"Loaded {len(loaded_sprites)} sprites from directory (max index {max_index})")

    def get_sprite(self, index: int) -> Optional[pygame.Surface]:
        """Get a sprite by its index.

        Args:
            index: The sprite index (0-based).

        Returns:
            The sprite Surface, or None if index is out of range.
        """
        if 0 <= index < len(self.sprites):
            return self.sprites[index]
        return None
