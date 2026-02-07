"""
Race Portrait Gallery - Portrait selection gallery for race configuration.

PROJ-12 Phase 4: Extracted from RaceSetupScreen to decompose the god class.

Provides UI controls for:
- Displaying all available portraits in a scrollable gallery
- Portrait selection with visual feedback
- Preview of selected portrait at full size
"""
import os
import pygame
import pygame_gui
from typing import Callable, List, Optional, Tuple, TYPE_CHECKING

from game.core.logger import log_debug, log_error, log_warning
from game.core.paths import Paths
from game.ui.screens.race_asset_loader import RaceAssetLoader

if TYPE_CHECKING:
    from game.strategy.data.race_config import RaceConfig


class RacePortraitGallery:
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
        race_config: 'RaceConfig',
        x: int,
        y: int,
        width: int,
        height: int,
        on_select_callback: Optional[Callable[[str], None]] = None,
        asset_loader: Optional[RaceAssetLoader] = None
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
        self.panel = panel
        self.ui_manager = manager
        self.race_config = race_config
        self.on_select_callback = on_select_callback

        # Use provided or create new asset loader
        self._asset_loader = asset_loader or RaceAssetLoader()

        # UI element references
        self.portrait_buttons: List[Tuple[pygame_gui.elements.UIButton, pygame_gui.elements.UIImage, str]] = []
        self.portrait_preview_image: Optional[pygame_gui.elements.UIImage] = None
        self.portrait_scroll: Optional[pygame_gui.elements.UIScrollingContainer] = None
        self.portrait_preview_panel: Optional[pygame_gui.elements.UIPanel] = None

        # Cache for discovered portraits
        self._portrait_cache: Optional[List[Tuple[str, pygame.Surface]]] = None

        self._create_content(x, y, width, height)

    def _create_content(self, x: int, y: int, width: int, height: int):
        """Create all gallery content."""
        # Label
        pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(x, y, width, 30),
            text="Select Portrait:",
            manager=self.ui_manager,
            container=self.panel
        )
        y += 35

        # Preview area for selected portrait
        preview_height = 280
        self.portrait_preview_panel = pygame_gui.elements.UIPanel(
            relative_rect=pygame.Rect(x, y, width, preview_height),
            manager=self.ui_manager,
            container=self.panel,
            object_id="#portrait_preview"
        )
        y += preview_height + 10

        # Scrolling container for thumbnails
        scroll_height = height - 35 - preview_height - 20
        self.portrait_scroll = pygame_gui.elements.UIScrollingContainer(
            relative_rect=pygame.Rect(x, y, width, scroll_height),
            manager=self.ui_manager,
            container=self.panel,
            allow_scroll_x=False,
            allow_scroll_y=True
        )

        # Populate with portrait buttons
        self._populate_gallery(width)

        # Pre-select if editing
        if self.race_config.portrait_id:
            self.on_portrait_selected(self.race_config.portrait_id)

    def _discover_portraits(self) -> List[Tuple[str, pygame.Surface]]:
        """
        Discover all race portraits from assets folder.

        Returns:
            List of (portrait_id, thumbnail_surface) tuples
        """
        if self._portrait_cache is not None:
            return self._portrait_cache

        portraits = []
        portraits_dir = os.path.join(Paths.ASSET_DIR, "Images", "Race Portraits")

        if not os.path.exists(portraits_dir):
            log_warning(f"Portraits directory not found: {portraits_dir}")
            return portraits

        for entry in os.scandir(portraits_dir):
            if entry.is_file() and entry.name.lower().endswith(('.jpg', '.jpeg', '.png')):
                try:
                    surf = pygame.image.load(entry.path).convert_alpha()
                    # Scale to thumbnail size (original is 2048x2048)
                    scaled = pygame.transform.smoothscale(
                        surf, (self.PORTRAIT_THUMB_SIZE, self.PORTRAIT_THUMB_SIZE)
                    )
                    portraits.append((entry.name, scaled))
                except Exception as e:
                    log_error(f"Failed to load portrait {entry.path}: {e}")

        portraits.sort(key=lambda x: x[0])
        self._portrait_cache = portraits
        log_debug(f"Discovered {len(portraits)} portraits")
        return portraits

    def _populate_gallery(self, width: int):
        """Populate gallery with portrait buttons."""
        portraits = self._discover_portraits()
        thumb_size = self.PORTRAIT_THUMB_SIZE
        spacing = 10
        cols = max(1, (width - 20) // (thumb_size + spacing))
        row = 0
        col = 0

        for portrait_id, thumb_surf in portraits:
            btn_x = 5 + col * (thumb_size + spacing)
            btn_y = 5 + row * (thumb_size + spacing)

            btn = pygame_gui.elements.UIButton(
                relative_rect=pygame.Rect(btn_x, btn_y, thumb_size, thumb_size),
                text="",
                manager=self.ui_manager,
                container=self.portrait_scroll,
                object_id=f"#portrait_{self._sanitize_object_id(portrait_id)}"
            )
            btn.portrait_id = portrait_id

            # Create image element on top of button
            img = pygame_gui.elements.UIImage(
                relative_rect=pygame.Rect(btn_x, btn_y, thumb_size, thumb_size),
                image_surface=thumb_surf,
                manager=self.ui_manager,
                container=self.portrait_scroll
            )

            self.portrait_buttons.append((btn, img, portrait_id))

            col += 1
            if col >= cols:
                col = 0
                row += 1

        # Set scrollable area height
        total_rows = (len(portraits) + cols - 1) // cols if cols > 0 else 1
        self.portrait_scroll.set_scrollable_area_dimensions(
            (width - 20, 10 + total_rows * (thumb_size + spacing))
        )

    def _sanitize_object_id(self, text: str) -> str:
        """Sanitize text for use in pygame_gui object_id."""
        return text.replace(".", "_").replace(" ", "_")

    def on_portrait_selected(self, portrait_id: str):
        """
        Handle portrait selection.

        Args:
            portrait_id: ID of selected portrait
        """
        self.race_config.portrait_id = portrait_id
        log_debug(f"Portrait selected: {portrait_id}")

        # Clear existing preview image
        if self.portrait_preview_image:
            self.portrait_preview_image.kill()
            self.portrait_preview_image = None

        # Load and display larger preview
        surf = self._asset_loader.load_portrait_full(portrait_id)
        if surf:
            # Scale to full preview size
            preview_size = self.PREVIEW_SIZE
            scaled = pygame.transform.smoothscale(surf, (preview_size, preview_size))
            self.portrait_preview_image = pygame_gui.elements.UIImage(
                relative_rect=pygame.Rect(10, 10, preview_size, preview_size),
                image_surface=scaled,
                manager=self.ui_manager,
                container=self.portrait_preview_panel
            )

        # Update button highlights
        for btn, img, pid in self.portrait_buttons:
            if pid == portrait_id:
                btn.select()
            else:
                btn.unselect()

        # Call callback if provided
        if self.on_select_callback:
            self.on_select_callback(portrait_id)

    def set_from_config(self):
        """Set gallery selection from race_config (for loading saved races)."""
        if self.race_config.portrait_id:
            self.on_portrait_selected(self.race_config.portrait_id)

    def handle_button_click(self, button: pygame_gui.elements.UIButton) -> bool:
        """
        Handle a button click event.

        Args:
            button: The button that was clicked

        Returns:
            True if this gallery handled the event, False otherwise
        """
        for btn, img, portrait_id in self.portrait_buttons:
            if button == btn:
                self.on_portrait_selected(portrait_id)
                return True
        return False
