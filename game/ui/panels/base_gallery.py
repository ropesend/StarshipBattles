"""
Base Gallery - Abstract base class for scrollable asset selection galleries.

PROJ-108 Phase 6: Extracted shared code from RacePortraitGallery and RaceFlagGallery.
DUP-UI1-005 resolution.

Provides common functionality for:
- Scrollable thumbnail gallery
- Preview area for selected asset
- Button click handling
- Selection highlighting
"""
import logging
from abc import ABC, abstractmethod
from typing import Callable, List, Optional, Tuple, TYPE_CHECKING

import pygame
import pygame_gui

from game.ui.screens.race_asset_loader import RaceAssetLoader

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from game.strategy.data.race_config import RaceConfig


class BaseGallery(ABC):
    """
    Abstract base class for scrollable asset selection galleries.

    Subclasses must implement:
    - _get_label_text(): Return the label text (e.g., "Select Portrait:")
    - _get_thumb_size(): Return thumbnail size in pixels
    - _get_preview_size(): Return preview size in pixels
    - _get_object_id_prefix(): Return prefix for object IDs (e.g., "portrait", "flag")
    - _get_preview_panel_object_id(): Return object ID for preview panel
    - _discover_assets(): Return list of (asset_id, thumbnail_surface) tuples
    - _get_current_selection(): Return currently selected asset ID from config
    - _set_selection(asset_id): Set selection in config
    - _update_preview(asset_id): Update preview area for selected asset
    """

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
        Create gallery content.

        Args:
            panel: Parent UIPanel to add controls to
            manager: pygame_gui UIManager
            race_config: RaceConfig to read/write asset selection from/to
            x: X position within panel
            y: Y position within panel
            width: Width of gallery area
            height: Height of gallery area
            on_select_callback: Optional callback(asset_id) when asset is selected
            asset_loader: Optional shared RaceAssetLoader instance
        """
        self.panel = panel
        self.ui_manager = manager
        self.race_config = race_config
        self.on_select_callback = on_select_callback

        # Use provided or create new asset loader
        self._asset_loader = asset_loader or RaceAssetLoader()

        # UI element references
        self.asset_buttons: List[Tuple[pygame_gui.elements.UIButton, str]] = []
        self.scroll_container: Optional[
            pygame_gui.elements.UIScrollingContainer
        ] = None
        self.preview_panel: Optional[pygame_gui.elements.UIPanel] = None

        # Cache for discovered assets
        self._asset_cache: Optional[List[Tuple[str, pygame.Surface]]] = None

        self._create_content(x, y, width, height)

    @abstractmethod
    def _get_label_text(self) -> str:
        """Return the label text for this gallery."""

    @abstractmethod
    def _get_thumb_size(self) -> int:
        """Return thumbnail size in pixels."""

    @abstractmethod
    def _get_preview_size(self) -> int:
        """Return preview size in pixels."""

    @abstractmethod
    def _get_object_id_prefix(self) -> str:
        """Return prefix for object IDs (e.g., 'portrait', 'flag')."""

    @abstractmethod
    def _get_preview_panel_object_id(self) -> str:
        """Return object ID for preview panel (e.g., '#portrait_preview')."""

    @abstractmethod
    def _discover_assets(self) -> List[Tuple[str, pygame.Surface]]:
        """
        Discover all assets from assets folder.

        Returns:
            List of (asset_id, thumbnail_surface) tuples
        """

    @abstractmethod
    def _get_current_selection(self) -> Optional[str]:
        """Return currently selected asset ID from config."""

    @abstractmethod
    def _set_selection(self, asset_id: str) -> None:
        """Set selection in config."""

    @abstractmethod
    def _update_preview(self, asset_id: str) -> None:
        """Update preview area for selected asset."""

    def _create_content(self, x: int, y: int, width: int, height: int):
        """Create all gallery content."""
        # Label
        pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(x, y, width, 30),
            text=self._get_label_text(),
            manager=self.ui_manager,
            container=self.panel,
        )
        y += 35

        # Preview area for selected asset
        preview_height = 280
        self.preview_panel = pygame_gui.elements.UIPanel(
            relative_rect=pygame.Rect(x, y, width, preview_height),
            manager=self.ui_manager,
            container=self.panel,
            object_id=self._get_preview_panel_object_id(),
        )
        y += preview_height + 10

        # Scrolling container for thumbnails
        scroll_height = height - 35 - preview_height - 20
        self.scroll_container = pygame_gui.elements.UIScrollingContainer(
            relative_rect=pygame.Rect(x, y, width, scroll_height),
            manager=self.ui_manager,
            container=self.panel,
            allow_scroll_x=False,
            allow_scroll_y=True,
        )

        # Populate with asset buttons
        self._populate_gallery(width)

        # Pre-select if editing
        current = self._get_current_selection()
        if current:
            self.on_asset_selected(current)

    def _populate_gallery(self, width: int):
        """Populate gallery with asset buttons."""
        assets = self._discover_assets()
        thumb_size = self._get_thumb_size()
        prefix = self._get_object_id_prefix()
        spacing = 10
        cols = max(1, (width - 20) // (thumb_size + spacing))
        row = 0
        col = 0

        for asset_id, thumb_surf in assets:
            btn_x = 5 + col * (thumb_size + spacing)
            btn_y = 5 + row * (thumb_size + spacing)

            btn = pygame_gui.elements.UIButton(
                relative_rect=pygame.Rect(btn_x, btn_y, thumb_size, thumb_size),
                text="",
                manager=self.ui_manager,
                container=self.scroll_container,
                object_id=f"#{prefix}_{self._sanitize_object_id(asset_id)}",
            )
            # Store asset_id on button for identification
            btn.asset_id = asset_id

            # Create image element on top of button
            img = pygame_gui.elements.UIImage(
                relative_rect=pygame.Rect(btn_x, btn_y, thumb_size, thumb_size),
                image_surface=thumb_surf,
                manager=self.ui_manager,
                container=self.scroll_container,
            )

            self.asset_buttons.append((btn, asset_id))

            col += 1
            if col >= cols:
                col = 0
                row += 1

        # Set scrollable area height
        total_rows = (len(assets) + cols - 1) // cols if cols > 0 else 1
        self.scroll_container.set_scrollable_area_dimensions(
            (width - 20, 10 + total_rows * (thumb_size + spacing))
        )

    def _sanitize_object_id(self, text: str) -> str:
        """Sanitize text for use in pygame_gui object_id."""
        return text.replace(".", "_").replace(" ", "_")

    def on_asset_selected(self, asset_id: str):
        """
        Handle asset selection.

        Args:
            asset_id: ID of selected asset
        """
        self._set_selection(asset_id)
        logger.debug(f"{self._get_object_id_prefix().capitalize()} selected: {asset_id}")

        # Update preview area (subclass-specific)
        self._update_preview(asset_id)

        # Update button highlights
        for btn, aid in self.asset_buttons:
            if aid == asset_id:
                btn.select()
            else:
                btn.unselect()

        # Call callback if provided
        if self.on_select_callback:
            self.on_select_callback(asset_id)

    def set_from_config(self):
        """Set gallery selection from race_config (for loading saved races)."""
        current = self._get_current_selection()
        if current:
            self.on_asset_selected(current)

    def handle_button_click(self, button: pygame_gui.elements.UIButton) -> bool:
        """
        Handle a button click event.

        Args:
            button: The button that was clicked

        Returns:
            True if this gallery handled the event, False otherwise
        """
        for btn, asset_id in self.asset_buttons:
            if button == btn:
                self.on_asset_selected(asset_id)
                return True
        return False
