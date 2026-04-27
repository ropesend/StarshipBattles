"""
Race Theme Gallery - Ship theme selection gallery for race configuration.

PROJ-12 Phase 4: Extracted from RaceSetupScreen to decompose the god class.
PROJ-166: Refactored to extend BaseGallery, eliminating duplicate methods.

Provides UI controls for:
- Displaying all available ship themes in a list
- Theme selection with visual feedback
- Preview of selected theme with sample ship images
"""
from __future__ import annotations

import pygame
import pygame_gui
from typing import Callable, Dict, List, Optional, Tuple, TYPE_CHECKING

from game.ui.assets import get_default_ship_theme_manager
from game.ui.panels.base_gallery import BaseGallery
from game.ui.screens.race_asset_loader import RaceAssetLoader

if TYPE_CHECKING:
    from game.strategy.data.race_config import RaceConfig


class RaceThemeGallery(BaseGallery):
    """
    Gallery panel for selecting ship themes.

    Creates a list of theme buttons with ship preview images.
    """

    def __init__(
        self,
        panel: pygame_gui.elements.UIPanel,
        manager: pygame_gui.UIManager,
        race_config: 'RaceConfig',
        x: int,
        y: int,
        width: int,
        height: int,
        on_select_callback: Optional[Callable[[str], None]] = None,
        asset_loader: Optional[RaceAssetLoader] = None,
    ):
        """
        Create theme gallery content.

        Args:
            panel: Parent UIPanel to add controls to
            manager: pygame_gui UIManager
            race_config: RaceConfig to read/write theme_id from/to
            x: X position within panel
            y: Y position within panel
            width: Width of gallery area
            height: Height of gallery area
            on_select_callback: Optional callback(theme_id) when theme is selected
            asset_loader: Optional shared RaceAssetLoader instance (not used by theme gallery)
        """
        # Theme-specific cache (dict of surfaces per theme, not single surface)
        self._theme_cache: Optional[List[Tuple[str, Dict[str, pygame.Surface]]]] = None

        super().__init__(
            panel, manager, race_config, x, y, width, height,
            on_select_callback, asset_loader
        )

    # --- BaseGallery abstract method implementations ---

    def _get_label_text(self) -> str:
        """Return the label text for this gallery."""
        return "Select Ship Theme:"

    def _get_thumb_size(self) -> int:
        """Return thumbnail size (button height for list layout)."""
        return 50

    def _get_preview_size(self) -> int:
        """Return preview size (no preview panel for themes)."""
        return 0

    def _get_object_id_prefix(self) -> str:
        """Return prefix for object IDs."""
        return "theme"

    def _get_preview_panel_object_id(self) -> str:
        """Return object ID for preview panel."""
        return "#theme_preview"

    def _get_current_selection(self) -> Optional[str]:
        """Return currently selected theme ID from config."""
        return self.race_config.theme_id

    def _set_selection(self, asset_id: str) -> None:
        """Set theme selection in config."""
        self.race_config.theme_id = asset_id

    def _update_preview(self, asset_id: str) -> None:
        """No-op: ship preview handled by RaceSetupScreen callback."""
        pass

    def _discover_assets(self) -> List[Tuple[str, Dict[str, pygame.Surface]]]:  # type: ignore[override]
        """
        Discover all ship themes.

        Returns:
            List of (theme_id, ship_surfaces_dict) tuples.
            Note: Returns Dict instead of Surface - _populate_gallery is also overridden.
        """
        if self._theme_cache is not None:
            return self._theme_cache

        themes = []
        theme_manager = get_default_ship_theme_manager()
        theme_manager.initialize()
        theme_ids = theme_manager.get_available_themes()

        for theme_id in theme_ids:
            # Load small preview images of a couple ships
            ship_surfs = {}
            for ship_class in ["Escort", "Battleship"]:
                surf = theme_manager.load_image(theme_id, ship_class)
                if surf:
                    # Scale to thumbnail size
                    scaled = pygame.transform.scale(surf, (40, 40))
                    ship_surfs[ship_class] = scaled
            themes.append((theme_id, ship_surfs))

        self._theme_cache = themes
        return themes

    # --- Overridden methods for vertical list layout ---

    def _create_content(self, x: int, y: int, width: int, height: int) -> None:
        """Create theme gallery with vertical list layout (no label or preview)."""
        self.scroll_container = pygame_gui.elements.UIScrollingContainer(
            relative_rect=pygame.Rect(x, y, width, height),
            manager=self.ui_manager,
            container=self.panel,
            allow_scroll_x=False,
            allow_scroll_y=True,
        )

        self._populate_gallery(width)

        # Pre-select from config or default to first
        current = self._get_current_selection()
        if current:
            self.on_asset_selected(current)
        elif self.asset_buttons:
            self.on_asset_selected(self.asset_buttons[0][1])

    def _populate_gallery(self, width: int) -> None:
        """Populate gallery with vertical list of theme buttons."""
        themes = self._discover_assets()
        btn_height = 50
        local_y = 0

        for theme_id, ship_surfs in themes:
            btn = pygame_gui.elements.UIButton(
                relative_rect=pygame.Rect(0, local_y, width - 20, btn_height),
                text=theme_id,
                manager=self.ui_manager,
                container=self.scroll_container,
                object_id=f"#theme_{self._sanitize_object_id(theme_id)}",
            )
            btn.asset_id = theme_id

            # Add small ship preview images on the right
            if "Escort" in ship_surfs:
                pygame_gui.elements.UIImage(
                    relative_rect=pygame.Rect(width - 90, local_y + 5, 30, 40),
                    image_surface=ship_surfs["Escort"],
                    manager=self.ui_manager,
                    container=self.scroll_container,
                )
            if "Battleship" in ship_surfs:
                pygame_gui.elements.UIImage(
                    relative_rect=pygame.Rect(width - 55, local_y + 5, 30, 40),
                    image_surface=ship_surfs["Battleship"],
                    manager=self.ui_manager,
                    container=self.scroll_container,
                )

            self.asset_buttons.append((btn, theme_id))
            local_y += btn_height + 5

        # Set scrollable area dimensions
        total_height = local_y if local_y > 0 else 1
        self.scroll_container.set_scrollable_area_dimensions(
            (width - 20, total_height)
        )
