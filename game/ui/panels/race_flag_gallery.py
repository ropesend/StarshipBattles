"""
Race Flag Gallery - Flag selection gallery for race configuration.

PROJ-12 Phase 4: Extracted from RaceSetupScreen to decompose the god class.
PROJ-108 Phase 6: Refactored to extend BaseGallery.

Provides UI controls for:
- Displaying all available flags in a scrollable gallery
- Flag selection with visual feedback
- Preview of selected flag in all three shapes
"""
import logging
import os
from typing import Callable, List, Optional, Tuple, TYPE_CHECKING

import pygame
import pygame_gui

from game.core.paths import Paths

logger = logging.getLogger(__name__)
from game.ui.panels.base_gallery import BaseGallery
from game.ui.screens.race_asset_loader import RaceAssetLoader

if TYPE_CHECKING:
    from game.strategy.data.race_config import RaceConfig


# Issue #11: module-level thumbnail cache shared across gallery instances.
# Mirrors the ShipThemeManager singleton pattern (PROJ-314). Cleared via
# _clear_thumbnail_caches() in test fixtures.
_FLAG_THUMBNAIL_CACHE: Optional[List[Tuple[str, pygame.Surface]]] = None


def _clear_thumbnail_caches() -> None:
    """Reset the module-level flag thumbnail cache.

    Test fixtures call this between runs so a prior test's decoded
    surfaces don't leak into the next test. Production code never calls
    this — assets are static at runtime.
    """
    global _FLAG_THUMBNAIL_CACHE
    _FLAG_THUMBNAIL_CACHE = None


class RaceFlagGallery(BaseGallery):
    """
    Gallery panel for selecting race flags.

    Creates a scrollable gallery of flag thumbnails with a preview area
    for the selected flag showing all three shapes (rectangle, shield, triangle).
    """

    # Thumbnail size for gallery display
    FLAG_THUMB_SIZE = 256

    # Full size for preview display
    PREVIEW_SIZE = 256

    def __init__(
        self,
        panel: pygame_gui.elements.UIPanel,
        manager: pygame_gui.UIManager,
        race_config: "RaceConfig",
        x: int,
        y: int,
        width: int,
        height: int,
        on_select_callback: Optional[Callable[[str], None]] = None,
        asset_loader: Optional[RaceAssetLoader] = None,
    ):
        """
        Create flag gallery content.

        Args:
            panel: Parent UIPanel to add controls to
            manager: pygame_gui UIManager
            race_config: RaceConfig to read/write flag_id from/to
            x: X position within panel
            y: Y position within panel
            width: Width of gallery area
            height: Height of gallery area
            on_select_callback: Optional callback(flag_id) when flag is selected
            asset_loader: Optional shared RaceAssetLoader instance
        """
        # Flag-specific preview references (multiple shapes)
        self.flag_preview_images: List[pygame_gui.elements.UIImage] = []

        super().__init__(
            panel, manager, race_config, x, y, width, height,
            on_select_callback, asset_loader
        )

    # --- BaseGallery abstract method implementations ---

    def _get_label_text(self) -> str:
        return "Select Flag:"

    def _get_thumb_size(self) -> int:
        return self.FLAG_THUMB_SIZE

    def _get_preview_size(self) -> int:
        return self.PREVIEW_SIZE

    def _get_object_id_prefix(self) -> str:
        return "flag"

    def _get_preview_panel_object_id(self) -> str:
        return "#flag_preview"

    def _get_current_selection(self) -> Optional[str]:
        return self.race_config.flag_id

    def _set_selection(self, asset_id: str) -> None:
        self.race_config.flag_id = asset_id

    def _discover_assets(self) -> List[Tuple[str, pygame.Surface]]:
        """
        Discover all flag designs from assets folder.

        Returns:
            List of (flag_id, thumbnail_surface) tuples
        """
        global _FLAG_THUMBNAIL_CACHE
        if _FLAG_THUMBNAIL_CACHE is not None:
            self._asset_cache = _FLAG_THUMBNAIL_CACHE
            return _FLAG_THUMBNAIL_CACHE

        flags: List[Tuple[str, pygame.Surface]] = []
        flags_dir = Paths.FLAGS_DIR

        if not os.path.exists(flags_dir):
            logger.warning(f"Flags directory not found: {flags_dir}")
            return flags

        for entry in os.scandir(flags_dir):
            if entry.is_dir() and entry.name.startswith("flag_"):
                # Issue #11: prefer 256/rectangle.png directly (already at
                # FLAG_THUMB_SIZE). Falls back to 128/ with smoothscale,
                # then root rectangle.png if the resolution dirs are absent.
                thumb_256 = os.path.join(entry.path, "256", "rectangle.png")
                thumb_128 = os.path.join(entry.path, "128", "rectangle.png")
                thumb_root = os.path.join(entry.path, "rectangle.png")
                if os.path.exists(thumb_256):
                    thumb_path = thumb_256
                    needs_scale = False
                elif os.path.exists(thumb_128):
                    thumb_path = thumb_128
                    needs_scale = True
                elif os.path.exists(thumb_root):
                    thumb_path = thumb_root
                    needs_scale = True
                else:
                    continue

                try:
                    surf = pygame.image.load(thumb_path).convert_alpha()
                    if needs_scale:
                        surf = pygame.transform.smoothscale(
                            surf, (self.FLAG_THUMB_SIZE, self.FLAG_THUMB_SIZE)
                        )
                    flags.append((entry.name, surf))
                except (FileNotFoundError, OSError, pygame.error) as e:
                    logger.error(f"Failed to load flag thumbnail {thumb_path}: {e}")

        flags.sort(key=lambda x: x[0])
        _FLAG_THUMBNAIL_CACHE = flags
        self._asset_cache = flags
        logger.debug(f"Discovered {len(flags)} flags")
        return flags

    def _update_preview(self, asset_id: str) -> None:
        """Update preview area with selected flag (all three shapes)."""
        # Clear existing preview images
        for img in self.flag_preview_images:
            img.kill()
        self.flag_preview_images = []

        # Load and display all three shapes at larger size
        shapes = self._asset_loader.load_flag_full(asset_id)
        shape_size = self.PREVIEW_SIZE
        preview_x = 10

        for i, surf in enumerate(shapes):
            # Scale to full preview size
            scaled = pygame.transform.smoothscale(surf, (shape_size, shape_size))
            img = pygame_gui.elements.UIImage(
                relative_rect=pygame.Rect(
                    preview_x + i * (shape_size + 15), 10, shape_size, shape_size
                ),
                image_surface=scaled,
                manager=self.ui_manager,
                container=self.preview_panel,
            )
            self.flag_preview_images.append(img)

