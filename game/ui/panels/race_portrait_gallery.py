"""
Race Portrait Gallery - Portrait selection gallery for race configuration.

PROJ-12 Phase 4: Extracted from RaceSetupScreen to decompose the god class.
PROJ-108 Phase 6: Refactored to extend BaseGallery.

Provides UI controls for:
- Displaying all available portraits in a scrollable gallery
- Portrait selection with visual feedback
- Preview of selected portrait at full size
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
# Mirrors the ShipThemeManager singleton pattern (PROJ-314).
_PORTRAIT_THUMBNAIL_CACHE: Optional[List[Tuple[str, pygame.Surface]]] = None


def _clear_thumbnail_caches() -> None:
    """Reset the module-level portrait thumbnail cache.

    Test fixtures call this between runs. Production code never calls
    this — assets are static at runtime.
    """
    global _PORTRAIT_THUMBNAIL_CACHE
    _PORTRAIT_THUMBNAIL_CACHE = None


class RacePortraitGallery(BaseGallery):
    """
    Gallery panel for selecting race portraits.

    Creates a scrollable gallery of portrait thumbnails with a preview area
    for the selected portrait at full size.
    """

    # Thumbnail size for gallery display
    PORTRAIT_THUMB_SIZE = 256

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
        Create portrait gallery content.

        Args:
            panel: Parent UIPanel to add controls to
            manager: pygame_gui UIManager
            race_config: RaceConfig to read/write portrait_id from/to
            x: X position within panel
            y: Y position within panel
            width: Width of gallery area
            height: Height of gallery area
            on_select_callback: Optional callback(portrait_id) when portrait is selected
            asset_loader: Optional shared RaceAssetLoader instance
        """
        # Portrait-specific preview reference
        self.portrait_preview_image: Optional[pygame_gui.elements.UIImage] = None

        super().__init__(
            panel, manager, race_config, x, y, width, height,
            on_select_callback, asset_loader
        )

    # --- BaseGallery abstract method implementations ---

    def _get_label_text(self) -> str:
        return "Select Portrait:"

    def _get_thumb_size(self) -> int:
        return self.PORTRAIT_THUMB_SIZE

    def _get_preview_size(self) -> int:
        return self.PREVIEW_SIZE

    def _get_object_id_prefix(self) -> str:
        return "portrait"

    def _get_preview_panel_object_id(self) -> str:
        return "#portrait_preview"

    def _get_current_selection(self) -> Optional[str]:
        return self.race_config.portrait_id

    def _set_selection(self, asset_id: str) -> None:
        self.race_config.portrait_id = asset_id

    def _discover_assets(self) -> List[Tuple[str, pygame.Surface]]:
        """
        Discover all race portraits from assets folder.

        Returns:
            List of (portrait_id, thumbnail_surface) tuples
        """
        global _PORTRAIT_THUMBNAIL_CACHE
        if _PORTRAIT_THUMBNAIL_CACHE is not None:
            self._asset_cache = _PORTRAIT_THUMBNAIL_CACHE
            return _PORTRAIT_THUMBNAIL_CACHE

        portraits: List[Tuple[str, pygame.Surface]] = []
        portraits_dir = os.path.join(Paths.ASSET_DIR, "Images", "Race Portraits")

        if not os.path.exists(portraits_dir):
            logger.warning(f"Portraits directory not found: {portraits_dir}")
            return portraits

        for entry in os.scandir(portraits_dir):
            if entry.is_file() and entry.name.lower().endswith((".jpg", ".jpeg", ".png")):
                try:
                    surf = pygame.image.load(entry.path).convert_alpha()
                    # Scale to thumbnail size (original is 2048x2048)
                    scaled = pygame.transform.smoothscale(
                        surf, (self.PORTRAIT_THUMB_SIZE, self.PORTRAIT_THUMB_SIZE)
                    )
                    portraits.append((entry.name, scaled))
                except (FileNotFoundError, OSError, pygame.error) as e:
                    logger.error(f"Failed to load portrait {entry.path}: {e}")

        portraits.sort(key=lambda x: x[0])
        _PORTRAIT_THUMBNAIL_CACHE = portraits
        self._asset_cache = portraits
        logger.debug(f"Discovered {len(portraits)} portraits")
        return portraits

    def _update_preview(self, asset_id: str) -> None:
        """Update preview area with selected portrait."""
        # Clear existing preview image
        if self.portrait_preview_image:
            self.portrait_preview_image.kill()
            self.portrait_preview_image = None

        # Load and display larger preview
        surf = self._asset_loader.load_portrait_full(asset_id)
        if surf:
            # Scale to full preview size
            preview_size = self.PREVIEW_SIZE
            scaled = pygame.transform.smoothscale(surf, (preview_size, preview_size))
            self.portrait_preview_image = pygame_gui.elements.UIImage(
                relative_rect=pygame.Rect(10, 10, preview_size, preview_size),
                image_surface=scaled,
                manager=self.ui_manager,
                container=self.preview_panel,
            )

