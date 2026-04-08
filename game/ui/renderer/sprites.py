import logging
import os
import re

import pygame
from typing import Optional
from game.core.paths import Paths
from game.core.singleton import SingletonMeta
from game.ui.colors import BLACK

logger = logging.getLogger(__name__)

# Matches filenames like "64Portrait_Comp_001.png" or "2048Portrait_Comp_019.png"
_PORTRAIT_PATTERN = re.compile(r"(\d+)Portrait_Comp_(\d+)\.\w+$")
# Matches legacy filenames like "Comp_001.bmp"
_LEGACY_PATTERN = re.compile(r"Comp_(\d+)\.\w+$")


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

    def load_sprites(self, base_path: str = None) -> None:
        """Load sprites from the 64px component image directory.

        Args:
            base_path: Optional project root override. Uses Paths.COMPONENTS_64_DIR if None.
        """
        if base_path is not None:
            sprite_dir = os.path.join(
                base_path, "assets", "Images", "Components", "Components 64"
            )
        else:
            sprite_dir = Paths.COMPONENTS_64_DIR

        if os.path.exists(sprite_dir):
            self._load_from_directory(sprite_dir)
        else:
            logger.error(f"Sprite directory not found: {sprite_dir}")

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
                # Try portrait pattern: {resolution}Portrait_Comp_{number}.{ext}
                match = _PORTRAIT_PATTERN.match(f)
                if match:
                    index = int(match.group(2)) - 1
                else:
                    # Try legacy pattern: Comp_{number}.{ext}
                    match = _LEGACY_PATTERN.match(f)
                    if match:
                        index = int(match.group(1)) - 1

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
