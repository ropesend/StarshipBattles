import logging
import os
import re

import pygame
from typing import Optional
from game.core.paths import Paths

logger = logging.getLogger(__name__)

# Matches filenames like "64Portrait_Comp_001.png" or "2048Portrait_Comp_019.png"
_PORTRAIT_PATTERN = re.compile(r"(\d+)Portrait_Comp_(\d+)\.\w+$")

_default_sprite_manager: Optional['SpriteManager'] = None


class SpriteManager:
    """
    Manager for component sprite images.

    Usage:
        manager = get_default_sprite_manager()
        sprite = manager.get_sprite(index)

    Testing:
        - Use set_default_sprite_manager(SpriteManager()) to replace the default
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
            # Compose against the override root using the canonical
            # COMPONENTS_64_DIR suffix, so renames of the underlying
            # folder layout require no edits here.
            suffix = os.path.relpath(Paths.COMPONENTS_64_DIR, Paths.ROOT_DIR)
            sprite_dir = os.path.join(base_path, suffix)
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
                # Match canonical pattern: {resolution}Portrait_Comp_{number}.{ext}
                match = _PORTRAIT_PATTERN.match(f)
                if match:
                    index = int(match.group(2))

                if index < 0: continue

                full_path = os.path.join(directory, f)
                image = pygame.image.load(full_path).convert_alpha()

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


def get_default_sprite_manager() -> SpriteManager:
    """Get the module-level SpriteManager instance.

    PROJ-471 (ST-01-005): does NOT auto-create. ``create_production()``
    calls ``set_default_sprite_manager()`` once at startup; tests that use
    this accessor must prime it the same way. A missing manager indicates a
    real ordering bug (accessor reached before bootstrap) rather than a
    condition to paper over with a fresh, unloaded — and divergent — manager.

    Raises:
        RuntimeError: if no manager has been set yet.
    """
    if _default_sprite_manager is None:
        raise RuntimeError(
            "Default SpriteManager has not been set. "
            "ApplicationContext.create_production() calls "
            "set_default_sprite_manager() at startup; call it before "
            "get_default_sprite_manager() (tests must prime it explicitly)."
        )
    return _default_sprite_manager


def set_default_sprite_manager(manager: SpriteManager) -> None:
    """Set the module-level SpriteManager instance."""
    global _default_sprite_manager
    _default_sprite_manager = manager
