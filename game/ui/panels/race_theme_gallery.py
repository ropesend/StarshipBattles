"""
Race Theme Gallery - Ship theme selection gallery for race configuration.

PROJ-12 Phase 4: Extracted from RaceSetupScreen to decompose the god class.

Provides UI controls for:
- Displaying all available ship themes in a list
- Theme selection with visual feedback
- Preview of selected theme with sample ship images
"""
import pygame
import pygame_gui
from typing import Callable, Dict, List, Optional, Tuple, TYPE_CHECKING

from game.core.logger import log_debug
from game.simulation.ship_theme import ShipThemeManager

if TYPE_CHECKING:
    from game.strategy.data.race_config import RaceConfig


class RaceThemeGallery:
    """
    Gallery panel for selecting ship themes.

    Creates a list of theme buttons with ship preview images.
    """

    # Ship preview image sizes
    SHIP_SIZE = 180

    def __init__(
        self,
        panel: pygame_gui.elements.UIPanel,
        manager: pygame_gui.UIManager,
        race_config: 'RaceConfig',
        x: int,
        y: int,
        width: int,
        on_select_callback: Optional[Callable[[str], None]] = None
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
            on_select_callback: Optional callback(theme_id) when theme is selected
        """
        self.panel = panel
        self.ui_manager = manager
        self.race_config = race_config
        self.on_select_callback = on_select_callback

        # UI element references
        self.theme_buttons: List[Tuple[pygame_gui.elements.UIButton, str]] = []
        self.theme_preview_panel: Optional[pygame_gui.elements.UIPanel] = None
        self.theme_preview_label: Optional[pygame_gui.elements.UILabel] = None

        # Cache for discovered themes
        self._theme_cache: Optional[List[Tuple[str, Dict[str, pygame.Surface]]]] = None

        self._create_content(x, y, width)

    def _create_content(self, x: int, y: int, width: int):
        """Create all gallery content."""
        # Label
        pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(x, y, width, 25),
            text="Select Ship Theme:",
            manager=self.ui_manager,
            container=self.panel
        )
        y += 25

        # Preview area (shows selected theme name)
        preview_height = 70
        self.theme_preview_panel = pygame_gui.elements.UIPanel(
            relative_rect=pygame.Rect(x, y, width, preview_height),
            manager=self.ui_manager,
            container=self.panel,
            object_id="#theme_preview"
        )
        self.theme_preview_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(5, 5, width - 10, 30),
            text="No theme selected",
            manager=self.ui_manager,
            container=self.theme_preview_panel
        )
        y += preview_height + 5

        # List of themes (not scrolling - only a few themes)
        themes = self._discover_themes()
        btn_height = 50

        for theme_id, ship_surfs in themes:
            btn = pygame_gui.elements.UIButton(
                relative_rect=pygame.Rect(x, y, width, btn_height),
                text=theme_id,
                manager=self.ui_manager,
                container=self.panel,
                object_id=f"#theme_{self._sanitize_object_id(theme_id)}"
            )
            btn.theme_id = theme_id

            # Add ship preview images
            if "Escort" in ship_surfs:
                img_x = x + width - 70
                pygame_gui.elements.UIImage(
                    relative_rect=pygame.Rect(img_x, y + 5, 30, 40),
                    image_surface=ship_surfs["Escort"],
                    manager=self.ui_manager,
                    container=self.panel
                )
            if "Battleship" in ship_surfs:
                img_x = x + width - 35
                pygame_gui.elements.UIImage(
                    relative_rect=pygame.Rect(img_x, y + 5, 30, 40),
                    image_surface=ship_surfs["Battleship"],
                    manager=self.ui_manager,
                    container=self.panel
                )

            self.theme_buttons.append((btn, theme_id))
            y += btn_height + 5

        # Pre-select if editing or default
        if self.race_config.theme_id:
            self.on_theme_selected(self.race_config.theme_id)
        elif themes:
            self.on_theme_selected(themes[0][0])

    def _discover_themes(self) -> List[Tuple[str, Dict[str, pygame.Surface]]]:
        """
        Discover all ship themes.

        Returns:
            List of (theme_id, ship_surfaces_dict) tuples
        """
        if self._theme_cache is not None:
            return self._theme_cache

        themes = []
        theme_manager = ShipThemeManager()
        theme_ids = theme_manager.list_themes()

        for theme_id in theme_ids:
            # Load small preview images of a couple ships
            ship_surfs = {}
            for ship_class in ["Escort", "Battleship"]:
                surf = theme_manager.load_ship_thumbnail(theme_id, ship_class, size=40)
                if surf:
                    ship_surfs[ship_class] = surf
            themes.append((theme_id, ship_surfs))

        self._theme_cache = themes
        log_debug(f"Discovered {len(themes)} themes")
        return themes

    def _sanitize_object_id(self, text: str) -> str:
        """Sanitize text for use in pygame_gui object_id."""
        return text.replace(".", "_").replace(" ", "_")

    def on_theme_selected(self, theme_id: str):
        """
        Handle theme selection.

        Args:
            theme_id: ID of selected theme
        """
        self.race_config.theme_id = theme_id
        log_debug(f"Theme selected: {theme_id}")

        # Update preview label
        if self.theme_preview_label:
            self.theme_preview_label.set_text(f"Selected: {theme_id}")

        # Update button highlights
        for btn, tid in self.theme_buttons:
            if tid == theme_id:
                btn.select()
            else:
                btn.unselect()

        # Call callback if provided
        if self.on_select_callback:
            self.on_select_callback(theme_id)

    def set_from_config(self):
        """Set gallery selection from race_config (for loading saved races)."""
        if self.race_config.theme_id:
            self.on_theme_selected(self.race_config.theme_id)

    def handle_button_click(self, button: pygame_gui.elements.UIButton) -> bool:
        """
        Handle a button click event.

        Args:
            button: The button that was clicked

        Returns:
            True if this gallery handled the event, False otherwise
        """
        for btn, theme_id in self.theme_buttons:
            if button == btn:
                self.on_theme_selected(theme_id)
                return True
        return False
