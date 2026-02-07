"""
Race Flag Gallery - Flag selection gallery for race configuration.

PROJ-12 Phase 4: Extracted from RaceSetupScreen to decompose the god class.

Provides UI controls for:
- Displaying all available flags in a scrollable gallery
- Flag selection with visual feedback
- Preview of selected flag in all three shapes
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


class RaceFlagGallery:
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
        race_config: 'RaceConfig',
        x: int,
        y: int,
        width: int,
        height: int,
        on_select_callback: Optional[Callable[[str], None]] = None,
        asset_loader: Optional[RaceAssetLoader] = None
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
        self.panel = panel
        self.ui_manager = manager
        self.race_config = race_config
        self.on_select_callback = on_select_callback

        # Use provided or create new asset loader
        self._asset_loader = asset_loader or RaceAssetLoader()

        # UI element references
        self.flag_buttons: List[Tuple[pygame_gui.elements.UIButton, pygame_gui.elements.UIImage, str]] = []
        self.flag_preview_images: List[pygame_gui.elements.UIImage] = []
        self.flag_scroll: Optional[pygame_gui.elements.UIScrollingContainer] = None
        self.flag_preview_panel: Optional[pygame_gui.elements.UIPanel] = None

        # Cache for discovered flags
        self._flag_cache: Optional[List[Tuple[str, pygame.Surface]]] = None

        self._create_content(x, y, width, height)

    def _create_content(self, x: int, y: int, width: int, height: int):
        """Create all gallery content."""
        # Label
        pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(x, y, width, 30),
            text="Select Flag:",
            manager=self.ui_manager,
            container=self.panel
        )
        y += 35

        # Preview area for selected flag (3 shapes)
        preview_height = 280
        self.flag_preview_panel = pygame_gui.elements.UIPanel(
            relative_rect=pygame.Rect(x, y, width, preview_height),
            manager=self.ui_manager,
            container=self.panel,
            object_id="#flag_preview"
        )
        y += preview_height + 10

        # Scrolling container for thumbnails
        scroll_height = height - 35 - preview_height - 20
        self.flag_scroll = pygame_gui.elements.UIScrollingContainer(
            relative_rect=pygame.Rect(x, y, width, scroll_height),
            manager=self.ui_manager,
            container=self.panel,
            allow_scroll_x=False,
            allow_scroll_y=True
        )

        # Populate with flag buttons
        self._populate_gallery(width)

        # Pre-select if editing
        if self.race_config.flag_id:
            self.on_flag_selected(self.race_config.flag_id)

    def _discover_flags(self) -> List[Tuple[str, pygame.Surface]]:
        """
        Discover all flag designs from assets folder.

        Returns:
            List of (flag_id, thumbnail_surface) tuples
        """
        if self._flag_cache is not None:
            return self._flag_cache

        flags = []
        flags_dir = os.path.join(Paths.ASSET_DIR, "Images", "Flags", "Processed")

        if not os.path.exists(flags_dir):
            log_warning(f"Flags directory not found: {flags_dir}")
            return flags

        for entry in os.scandir(flags_dir):
            if entry.is_dir() and entry.name.startswith("flag_"):
                # Load the 128px rectangle thumbnail
                thumb_path = os.path.join(entry.path, "128", "rectangle.png")
                if not os.path.exists(thumb_path):
                    # Fallback to root rectangle
                    thumb_path = os.path.join(entry.path, "rectangle.png")

                if os.path.exists(thumb_path):
                    try:
                        surf = pygame.image.load(thumb_path).convert_alpha()
                        # Scale to thumbnail size
                        scaled = pygame.transform.smoothscale(
                            surf, (self.FLAG_THUMB_SIZE, self.FLAG_THUMB_SIZE)
                        )
                        flags.append((entry.name, scaled))
                    except (FileNotFoundError, OSError, pygame.error) as e:
                        log_error(f"Failed to load flag thumbnail {thumb_path}: {e}")

        flags.sort(key=lambda x: x[0])
        self._flag_cache = flags
        log_debug(f"Discovered {len(flags)} flags")
        return flags

    def _populate_gallery(self, width: int):
        """Populate gallery with flag buttons."""
        flags = self._discover_flags()
        thumb_size = self.FLAG_THUMB_SIZE
        spacing = 10
        cols = max(1, (width - 20) // (thumb_size + spacing))
        row = 0
        col = 0

        for flag_id, thumb_surf in flags:
            btn_x = 5 + col * (thumb_size + spacing)
            btn_y = 5 + row * (thumb_size + spacing)

            btn = pygame_gui.elements.UIButton(
                relative_rect=pygame.Rect(btn_x, btn_y, thumb_size, thumb_size),
                text="",
                manager=self.ui_manager,
                container=self.flag_scroll,
                object_id=f"#flag_{self._sanitize_object_id(flag_id)}"
            )
            btn.flag_id = flag_id

            # Create image element on top of button
            img = pygame_gui.elements.UIImage(
                relative_rect=pygame.Rect(btn_x, btn_y, thumb_size, thumb_size),
                image_surface=thumb_surf,
                manager=self.ui_manager,
                container=self.flag_scroll
            )

            self.flag_buttons.append((btn, img, flag_id))

            col += 1
            if col >= cols:
                col = 0
                row += 1

        # Set scrollable area height
        total_rows = (len(flags) + cols - 1) // cols if cols > 0 else 1
        self.flag_scroll.set_scrollable_area_dimensions(
            (width - 20, 10 + total_rows * (thumb_size + spacing))
        )

    def _sanitize_object_id(self, text: str) -> str:
        """Sanitize text for use in pygame_gui object_id."""
        return text.replace(".", "_").replace(" ", "_")

    def on_flag_selected(self, flag_id: str):
        """
        Handle flag selection.

        Args:
            flag_id: ID of selected flag
        """
        self.race_config.flag_id = flag_id
        log_debug(f"Flag selected: {flag_id}")

        # Clear existing preview images
        for img in self.flag_preview_images:
            img.kill()
        self.flag_preview_images = []

        # Load and display all three shapes at larger size
        shapes = self._asset_loader.load_flag_full(flag_id)
        shape_size = self.PREVIEW_SIZE
        preview_x = 10

        for i, surf in enumerate(shapes):
            # Scale to full preview size
            scaled = pygame.transform.smoothscale(surf, (shape_size, shape_size))
            img = pygame_gui.elements.UIImage(
                relative_rect=pygame.Rect(preview_x + i * (shape_size + 15), 10, shape_size, shape_size),
                image_surface=scaled,
                manager=self.ui_manager,
                container=self.flag_preview_panel
            )
            self.flag_preview_images.append(img)

        # Update button highlights
        for btn, img, fid in self.flag_buttons:
            if fid == flag_id:
                btn.select()
            else:
                btn.unselect()

        # Call callback if provided
        if self.on_select_callback:
            self.on_select_callback(flag_id)

    def set_from_config(self):
        """Set gallery selection from race_config (for loading saved races)."""
        if self.race_config.flag_id:
            self.on_flag_selected(self.race_config.flag_id)

    def handle_button_click(self, button: pygame_gui.elements.UIButton) -> bool:
        """
        Handle a button click event.

        Args:
            button: The button that was clicked

        Returns:
            True if this gallery handled the event, False otherwise
        """
        for btn, img, flag_id in self.flag_buttons:
            if button == btn:
                self.on_flag_selected(flag_id)
                return True
        return False
