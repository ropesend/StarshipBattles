"""
Race Setup Screen - Multi-step wizard for configuring custom races.

Allows users to:
- Select visual identity (flag, portrait, ship theme)
- Configure environmental preferences (gravity, temperature, atmosphere)
- Enter descriptive text (biological, sociological)
- Review and save race configuration
"""
import os
import pygame
import pygame_gui
from typing import Callable, Optional, List, Tuple

from game.core.logger import log_debug, log_info, log_warning, log_error
from game.core.constants import ASSET_DIR
from game.strategy.data.race_config import RaceConfig
from game.strategy.systems.race_library import RaceLibrary
from game.simulation.ship_theme import ShipThemeManager


class RaceSetupScreen(pygame_gui.elements.UIWindow):
    """Tab-based window for race configuration."""

    # Tab constants (Summary is now first/landing page)
    TAB_SUMMARY = 0
    TAB_VISUALS = 1
    TAB_SHIPS = 2
    TAB_ENVIRONMENT = 3
    TAB_DESCRIPTIONS = 4

    TAB_NAMES = [
        "Summary",
        "Visuals",
        "Ships",
        "Environment",
        "Descriptions"
    ]

    # Thumbnail sizes (larger for 2560x1600 displays)
    FLAG_THUMB_SIZE = 256
    PORTRAIT_THUMB_SIZE = 256
    THEME_SHIP_SIZE = 180  # For ship preview images

    def __init__(self, rect: pygame.Rect, manager: pygame_gui.UIManager,
                 on_complete_callback: Callable[[RaceConfig], None],
                 on_cancel_callback: Callable[[], None],
                 race_to_edit: Optional[RaceConfig] = None):
        """
        Create race setup wizard window.

        Args:
            rect: Window rectangle
            manager: pygame_gui UIManager
            on_complete_callback: Callback(RaceConfig) when user saves race
            on_cancel_callback: Callback() when user cancels
            race_to_edit: Optional existing race to edit
        """
        super().__init__(
            rect,
            manager,
            window_display_title="Race Setup",
            object_id="#race_setup_window",
            resizable=False
        )

        self.on_complete_callback = on_complete_callback
        self.on_cancel_callback = on_cancel_callback

        # Working race configuration
        if race_to_edit:
            self.race_config = race_to_edit
            self.is_editing = True
        else:
            self.race_config = RaceConfig()
            self.is_editing = False

        # Current tab (start on Summary)
        self.current_step = self.TAB_SUMMARY

        # Race library for save/load
        self.race_library = RaceLibrary()

        # Asset caches
        self._flag_cache = None  # List of (flag_id, thumbnail_surface)
        self._portrait_cache = None  # List of (portrait_id, thumbnail_surface)
        self._theme_cache = None  # List of (theme_id, ship_surfaces_dict)

        # UI element references
        self.step_panels = []
        self.tab_buttons = []  # Tab buttons for navigation
        self.btn_cancel = None
        self.btn_save = None
        self.btn_load = None  # Load Race button on Summary
        self.error_label = None

        # Visual selection UI elements
        self.name_input = None
        self.flag_buttons = []
        self.portrait_buttons = []
        self.theme_buttons = []
        self.selected_flag_highlight = None
        self.selected_portrait_highlight = None
        self.selected_theme_highlight = None
        self.flag_preview_images = []
        self.portrait_preview_image = None

        self._create_ui()
        self._show_step(self.current_step)

    def _create_ui(self):
        """Create all UI elements."""
        container = self.get_container()
        content_width = container.get_size()[0] - 20
        content_height = container.get_size()[1]

        # Tab buttons at top
        self._create_tab_buttons(container, content_width)

        # Content area for tab panels (below tabs, above bottom buttons)
        panel_top = 55
        panel_height = content_height - 130  # Leave room for buttons

        # Create panels for each tab
        self._create_step_panels(container, content_width, panel_top, panel_height)

        # Bottom buttons (Cancel, Save)
        self._create_navigation_buttons(container, content_width, content_height)

        # Error label above buttons
        self.error_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(10, content_height - 90, content_width, 25),
            text="",
            manager=self.ui_manager,
            container=container
        )

    def _create_tab_buttons(self, container, content_width: int):
        """Create clickable tab buttons for navigation."""
        tab_y = 5
        num_tabs = len(self.TAB_NAMES)
        tab_width = (content_width - 10) // num_tabs
        tab_height = 40

        for i, name in enumerate(self.TAB_NAMES):
            btn = pygame_gui.elements.UIButton(
                relative_rect=pygame.Rect(10 + i * tab_width, tab_y, tab_width - 5, tab_height),
                text=name,
                manager=self.ui_manager,
                container=container,
                object_id=f"#tab_{name.lower()}"
            )
            btn.tab_index = i  # Store tab index on button
            self.tab_buttons.append(btn)

    def _create_step_panels(self, container, width: int, top: int, height: int):
        """Create panels for each tab."""
        panel_rect = pygame.Rect(10, top, width, height)

        # Panel 0: Summary (landing page)
        panel_summary = pygame_gui.elements.UIPanel(
            relative_rect=panel_rect,
            manager=self.ui_manager,
            container=container,
            object_id="#panel_summary"
        )
        self._create_summary_panel_content(panel_summary)
        self.step_panels.append(panel_summary)

        # Panel 1: Visuals (Flags and Portraits only)
        panel_visuals = pygame_gui.elements.UIPanel(
            relative_rect=panel_rect,
            manager=self.ui_manager,
            container=container,
            object_id="#panel_visuals"
        )
        self._create_visuals_panel_content(panel_visuals)
        self.step_panels.append(panel_visuals)

        # Panel 2: Ships (dedicated ship theme selection)
        panel_ships = pygame_gui.elements.UIPanel(
            relative_rect=panel_rect,
            manager=self.ui_manager,
            container=container,
            object_id="#panel_ships"
        )
        self._create_ships_panel_content(panel_ships)
        self.step_panels.append(panel_ships)

        # Panel 3: Environment Preferences
        panel_environment = pygame_gui.elements.UIPanel(
            relative_rect=panel_rect,
            manager=self.ui_manager,
            container=container,
            object_id="#panel_environment"
        )
        self._create_environment_panel_content(panel_environment)
        self.step_panels.append(panel_environment)

        # Panel 4: Descriptions
        panel_descriptions = pygame_gui.elements.UIPanel(
            relative_rect=panel_rect,
            manager=self.ui_manager,
            container=container,
            object_id="#panel_descriptions"
        )
        self._create_descriptions_panel_content(panel_descriptions)
        self.step_panels.append(panel_descriptions)

    # =========================================================================
    # Asset Discovery Methods
    # =========================================================================

    def _discover_flags(self) -> List[Tuple[str, pygame.Surface]]:
        """
        Discover all flag designs from assets folder.

        Returns:
            List of (flag_id, thumbnail_surface) tuples
        """
        if self._flag_cache is not None:
            return self._flag_cache

        flags = []
        flags_dir = os.path.join(ASSET_DIR, "Images", "Flags", "Processed")

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
                    except Exception as e:
                        log_error(f"Failed to load flag thumbnail {thumb_path}: {e}")

        flags.sort(key=lambda x: x[0])
        self._flag_cache = flags
        log_debug(f"Discovered {len(flags)} flags")
        return flags

    def _discover_portraits(self) -> List[Tuple[str, pygame.Surface]]:
        """
        Discover all race portraits from assets folder.

        Returns:
            List of (portrait_id, thumbnail_surface) tuples
        """
        if self._portrait_cache is not None:
            return self._portrait_cache

        portraits = []
        portraits_dir = os.path.join(ASSET_DIR, "Images", "Race Portraits")

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

    def _discover_themes(self) -> List[Tuple[str, dict]]:
        """
        Discover all ship themes.

        Returns:
            List of (theme_id, {ship_class: surface}) tuples
        """
        if self._theme_cache is not None:
            return self._theme_cache

        themes = []
        theme_manager = ShipThemeManager.instance()
        theme_manager.initialize()

        for theme_name in theme_manager.get_available_themes():
            ship_surfaces = {}
            # Load Escort (small) and Battleship (large) for preview
            for ship_class in ["Escort", "Battleship"]:
                surf = theme_manager.get_image(theme_name, ship_class)
                if surf:
                    # Scale to preview size
                    w, h = surf.get_size()
                    scale = min(self.THEME_SHIP_SIZE / w, self.THEME_SHIP_SIZE / h)
                    new_size = (int(w * scale), int(h * scale))
                    scaled = pygame.transform.smoothscale(surf, new_size)
                    ship_surfaces[ship_class] = scaled

            themes.append((theme_name, ship_surfaces))

        self._theme_cache = themes
        log_debug(f"Discovered {len(themes)} themes")
        return themes

    def _load_flag_full(self, flag_id: str) -> List[pygame.Surface]:
        """
        Load all three shapes for a flag at full display size.

        Args:
            flag_id: Flag directory name

        Returns:
            List of [rectangle, shield, triangle] surfaces (original size, caller scales)
        """
        shapes = []
        flags_dir = os.path.join(ASSET_DIR, "Images", "Flags", "Processed")
        flag_dir = os.path.join(flags_dir, flag_id)

        for shape in ["rectangle", "shield", "triangle"]:
            # Try 1024px first for best quality, then 512, 256, then root
            shape_path = None
            for size_dir in ["1024", "512", "256", ""]:
                if size_dir:
                    test_path = os.path.join(flag_dir, size_dir, f"{shape}.png")
                else:
                    test_path = os.path.join(flag_dir, f"{shape}.png")
                if os.path.exists(test_path):
                    shape_path = test_path
                    break

            if shape_path:
                try:
                    surf = pygame.image.load(shape_path).convert_alpha()
                    shapes.append(surf)
                except Exception as e:
                    log_error(f"Failed to load flag shape {shape_path}: {e}")
                    shapes.append(self._create_placeholder(256, 256))
            else:
                shapes.append(self._create_placeholder(256, 256))

        return shapes

    def _load_portrait_full(self, portrait_id: str) -> Optional[pygame.Surface]:
        """
        Load a portrait at full display size.

        Args:
            portrait_id: Portrait filename

        Returns:
            Surface (original size, caller scales as needed) or None
        """
        portraits_dir = os.path.join(ASSET_DIR, "Images", "Race Portraits")
        portrait_path = os.path.join(portraits_dir, portrait_id)

        if os.path.exists(portrait_path):
            try:
                surf = pygame.image.load(portrait_path).convert_alpha()
                return surf
            except Exception as e:
                log_error(f"Failed to load portrait {portrait_path}: {e}")

        return None

    def _create_placeholder(self, width: int, height: int) -> pygame.Surface:
        """Create a placeholder surface for missing assets."""
        surf = pygame.Surface((width, height), pygame.SRCALPHA)
        pygame.draw.rect(surf, (80, 80, 80), surf.get_rect(), 2)
        pygame.draw.line(surf, (80, 80, 80), (0, 0), (width, height), 1)
        pygame.draw.line(surf, (80, 80, 80), (width, 0), (0, height), 1)
        return surf

    def _sanitize_object_id(self, text: str) -> str:
        """Sanitize text for use in pygame_gui object_id (no dots or spaces)."""
        return text.replace(".", "_").replace(" ", "_")

    # =========================================================================
    # Visuals Panel (Flags and Portraits)
    # =========================================================================

    def _create_visuals_panel_content(self, panel):
        """Create content for Visuals tab: Race name, Flags, and Portraits."""
        panel_width = panel.get_relative_rect().width - 20
        panel_height = panel.get_relative_rect().height
        y = 5

        # Race Name
        pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(10, y, 120, 30),
            text="Race Name:",
            manager=self.ui_manager,
            container=panel
        )
        self.name_input = pygame_gui.elements.UITextEntryLine(
            relative_rect=pygame.Rect(130, y, 400, 35),
            manager=self.ui_manager,
            container=panel,
            placeholder_text="Enter race name..."
        )
        if self.race_config.name:
            self.name_input.set_text(self.race_config.name)
        y += 50

        # Create two columns: Flags and Portraits (larger now)
        col_width = (panel_width - 20) // 2
        gallery_height = panel_height - y - 20

        # Column 1: Flags
        self._create_flag_gallery(panel, 10, y, col_width, gallery_height)

        # Column 2: Portraits
        self._create_portrait_gallery(panel, 15 + col_width, y, col_width, gallery_height)

    def _create_flag_gallery(self, panel, x: int, y: int, width: int, height: int):
        """Create flag selection gallery with large thumbnails."""
        pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(x, y, width, 30),
            text="Select Flag:",
            manager=self.ui_manager,
            container=panel
        )
        y += 35

        # Preview area for selected flag (3 shapes at full size)
        preview_height = 280  # Larger preview for 256px shapes
        self.flag_preview_panel = pygame_gui.elements.UIPanel(
            relative_rect=pygame.Rect(x, y, width, preview_height),
            manager=self.ui_manager,
            container=panel,
            object_id="#flag_preview"
        )
        y += preview_height + 10

        # Scrolling container for thumbnails
        scroll_height = height - 35 - preview_height - 20
        self.flag_scroll = pygame_gui.elements.UIScrollingContainer(
            relative_rect=pygame.Rect(x, y, width, scroll_height),
            manager=self.ui_manager,
            container=panel,
            allow_scroll_x=False,
            allow_scroll_y=True
        )

        # Populate with flag buttons
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

        # Pre-select if editing
        if self.race_config.flag_id:
            self._on_flag_selected(self.race_config.flag_id)

    def _create_portrait_gallery(self, panel, x: int, y: int, width: int, height: int):
        """Create portrait selection gallery with large thumbnails."""
        pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(x, y, width, 30),
            text="Select Portrait:",
            manager=self.ui_manager,
            container=panel
        )
        y += 35

        # Preview area for selected portrait (larger)
        preview_height = 280  # Larger preview for 256px portrait
        self.portrait_preview_panel = pygame_gui.elements.UIPanel(
            relative_rect=pygame.Rect(x, y, width, preview_height),
            manager=self.ui_manager,
            container=panel,
            object_id="#portrait_preview"
        )
        y += preview_height + 10

        # Scrolling container for thumbnails
        scroll_height = height - 35 - preview_height - 20
        self.portrait_scroll = pygame_gui.elements.UIScrollingContainer(
            relative_rect=pygame.Rect(x, y, width, scroll_height),
            manager=self.ui_manager,
            container=panel,
            allow_scroll_x=False,
            allow_scroll_y=True
        )

        # Populate with portrait buttons
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

        # Pre-select if editing
        if self.race_config.portrait_id:
            self._on_portrait_selected(self.race_config.portrait_id)

    def _create_theme_gallery(self, panel, x: int, y: int, width: int):
        """Create ship theme selection gallery."""
        pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(x, y, width, 25),
            text="Select Ship Theme:",
            manager=self.ui_manager,
            container=panel
        )
        y += 25

        # Preview area (placeholder - shows selected theme name)
        preview_height = 70
        self.theme_preview_panel = pygame_gui.elements.UIPanel(
            relative_rect=pygame.Rect(x, y, width, preview_height),
            manager=self.ui_manager,
            container=panel,
            object_id="#theme_preview"
        )
        self.theme_preview_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(5, 5, width - 10, 30),
            text="No theme selected",
            manager=self.ui_manager,
            container=self.theme_preview_panel
        )
        y += preview_height + 5

        # List of themes (not scrolling - only 4 themes)
        themes = self._discover_themes()
        btn_height = 50

        for theme_id, ship_surfs in themes:
            btn = pygame_gui.elements.UIButton(
                relative_rect=pygame.Rect(x, y, width, btn_height),
                text=theme_id,
                manager=self.ui_manager,
                container=panel,
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
                    container=panel
                )
            if "Battleship" in ship_surfs:
                img_x = x + width - 35
                pygame_gui.elements.UIImage(
                    relative_rect=pygame.Rect(img_x, y + 5, 30, 40),
                    image_surface=ship_surfs["Battleship"],
                    manager=self.ui_manager,
                    container=panel
                )

            self.theme_buttons.append((btn, theme_id))
            y += btn_height + 5

        # Pre-select if editing or default
        if self.race_config.theme_id:
            self._on_theme_selected(self.race_config.theme_id)
        elif themes:
            self._on_theme_selected(themes[0][0])

    def _on_flag_selected(self, flag_id: str):
        """Handle flag selection."""
        self.race_config.flag_id = flag_id
        log_debug(f"Flag selected: {flag_id}")

        # Clear existing preview images
        for img in self.flag_preview_images:
            img.kill()
        self.flag_preview_images = []

        # Load and display all three shapes at larger size
        shapes = self._load_flag_full(flag_id)
        shape_names = ["rectangle", "shield", "triangle"]
        shape_size = 256  # Full size for preview
        preview_x = 10

        for i, (surf, name) in enumerate(zip(shapes, shape_names)):
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

    def _on_portrait_selected(self, portrait_id: str):
        """Handle portrait selection."""
        self.race_config.portrait_id = portrait_id
        log_debug(f"Portrait selected: {portrait_id}")

        # Clear existing preview
        if self.portrait_preview_image:
            self.portrait_preview_image.kill()
            self.portrait_preview_image = None

        # Load and display larger preview (256px)
        surf = self._load_portrait_full(portrait_id)
        if surf:
            # Scale to full preview size
            preview_size = 256
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

    def _on_theme_selected(self, theme_id: str):
        """Handle theme selection."""
        self.race_config.theme_id = theme_id
        log_debug(f"Theme selected: {theme_id}")

        # Update preview label (if old theme gallery exists)
        if hasattr(self, 'theme_preview_label') and self.theme_preview_label:
            self.theme_preview_label.set_text(f"Selected: {theme_id}")

        # Refresh ship preview in Ships panel
        self._refresh_ship_preview(theme_id)

        # Update button highlights
        for btn, tid in self.theme_buttons:
            if tid == theme_id:
                btn.select()
            else:
                btn.unselect()

    # =========================================================================
    # Ships Panel (dedicated ship theme selection)
    # =========================================================================

    def _create_ships_panel_content(self, panel):
        """Create content for Ships tab: Ship theme selection with large previews."""
        panel_width = panel.get_relative_rect().width - 20
        panel_height = panel.get_relative_rect().height
        y = 10

        # Title
        pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(10, y, panel_width, 35),
            text="Select Ship Theme",
            manager=self.ui_manager,
            container=panel
        )
        y += 45

        # Theme selector buttons at top (horizontal row)
        themes = self._discover_themes()
        btn_width = min(200, (panel_width - 20) // max(1, len(themes)))
        btn_height = 50

        for i, (theme_id, ship_surfs) in enumerate(themes):
            btn = pygame_gui.elements.UIButton(
                relative_rect=pygame.Rect(10 + i * (btn_width + 10), y, btn_width, btn_height),
                text=theme_id,
                manager=self.ui_manager,
                container=panel,
                object_id=f"#theme_{self._sanitize_object_id(theme_id)}"
            )
            btn.theme_id = theme_id
            self.theme_buttons.append((btn, theme_id))

        y += btn_height + 20

        # Ship preview area (scrolling container for ship images)
        preview_height = panel_height - y - 20
        self.ship_preview_scroll = pygame_gui.elements.UIScrollingContainer(
            relative_rect=pygame.Rect(10, y, panel_width, preview_height),
            manager=self.ui_manager,
            container=panel,
            allow_scroll_x=False,
            allow_scroll_y=True
        )

        # Store reference to container for dynamic updates
        self.ship_preview_container = self.ship_preview_scroll

        # Pre-select theme
        if self.race_config.theme_id:
            self._on_theme_selected(self.race_config.theme_id)
        elif themes:
            self._on_theme_selected(themes[0][0])

    def _refresh_ship_preview(self, theme_id: str):
        """Refresh the ship preview area with ships from the selected theme."""
        log_debug(f"_refresh_ship_preview called with theme_id: {theme_id}")

        # Clear existing ship previews
        if hasattr(self, '_ship_preview_elements'):
            for elem in self._ship_preview_elements:
                elem.kill()
        self._ship_preview_elements = []

        if not hasattr(self, 'ship_preview_scroll'):
            log_debug("ship_preview_scroll not found, returning")
            return

        container = self.ship_preview_scroll.get_container()
        if container is None:
            log_error("get_container() returned None!")
            return

        container_width = self.ship_preview_scroll.get_relative_rect().width - 30
        log_debug(f"Container width: {container_width}")

        # Representative ship classes to display
        ship_classes = [
            "Fighter (Medium)",
            "Satellite (Medium)",
            "Escort",
            "Cruiser",
            "Battleship",
            "Dreadnought"
        ]

        theme_manager = ShipThemeManager.instance()
        theme_manager.initialize()

        # Layout: 2 columns of ships, each showing portrait + top-down
        ship_size = self.THEME_SHIP_SIZE  # 180px
        col_width = container_width // 2
        row_height = ship_size + 60  # Space for ship images + label
        y = 10

        for i, ship_class in enumerate(ship_classes):
            col = i % 2
            if col == 0 and i > 0:
                y += row_height + 20

            x = 10 + col * col_width

            # Ship class label
            label = pygame_gui.elements.UILabel(
                relative_rect=pygame.Rect(x, y, col_width - 20, 30),
                text=ship_class,
                manager=self.ui_manager,
                container=container
            )
            self._ship_preview_elements.append(label)

            # Get top-down (skin) image
            skin_surf = theme_manager.get_image(theme_id, ship_class)
            log_debug(f"Ship {ship_class}: skin_surf={skin_surf is not None}")
            if skin_surf:
                # Scale to preview size
                w, h = skin_surf.get_size()
                scale = min(ship_size / w, ship_size / h)
                new_size = (int(w * scale), int(h * scale))
                scaled_skin = pygame.transform.smoothscale(skin_surf, new_size)

                # Display top-down view
                img = pygame_gui.elements.UIImage(
                    relative_rect=pygame.Rect(x, y + 35, ship_size, ship_size),
                    image_surface=scaled_skin,
                    manager=self.ui_manager,
                    container=container
                )
                self._ship_preview_elements.append(img)

            # Get portrait image
            portrait_surf = self._load_ship_portrait(theme_id, ship_class)
            log_debug(f"Ship {ship_class}: portrait_surf={portrait_surf is not None}")
            if portrait_surf:
                img = pygame_gui.elements.UIImage(
                    relative_rect=pygame.Rect(x + ship_size + 10, y + 35, ship_size, ship_size),
                    image_surface=portrait_surf,
                    manager=self.ui_manager,
                    container=container
                )
                self._ship_preview_elements.append(img)

        # Set scrollable area
        total_rows = (len(ship_classes) + 1) // 2
        self.ship_preview_scroll.set_scrollable_area_dimensions(
            (container_width, 10 + total_rows * (row_height + 20))
        )

    def _load_ship_portrait(self, theme_id: str, ship_class: str) -> Optional[pygame.Surface]:
        """
        Load a ship portrait image.

        Args:
            theme_id: Theme name (e.g., "Atlantians")
            ship_class: Ship class name (e.g., "Battleship")

        Returns:
            Scaled portrait surface or None if not found
        """
        # Convert ship class to portrait filename format
        # e.g., "Fighter (Medium)" -> "MediumFighter_Portrait.jpg"
        # e.g., "Battleship" -> "Battleship_Portrait.jpg"
        portrait_name = ship_class.replace(" ", "").replace("(", "").replace(")", "")
        # Handle special cases
        if "Fighter" in ship_class and "(" in ship_class:
            # "Fighter (Medium)" -> "MediumFighter"
            parts = ship_class.replace(")", "").split(" (")
            portrait_name = parts[1] + parts[0]
        elif "Satellite" in ship_class and "(" in ship_class:
            parts = ship_class.replace(")", "").split(" (")
            portrait_name = parts[1] + parts[0]

        portrait_filename = f"{portrait_name}_Portrait.jpg"
        portrait_path = os.path.join(ASSET_DIR, "ShipThemes", theme_id, "Portraits", portrait_filename)

        if os.path.exists(portrait_path):
            try:
                surf = pygame.image.load(portrait_path).convert_alpha()
                # Scale to preview size
                scaled = pygame.transform.smoothscale(surf, (self.THEME_SHIP_SIZE, self.THEME_SHIP_SIZE))
                return scaled
            except Exception as e:
                log_error(f"Failed to load ship portrait {portrait_path}: {e}")

        return None

    # =========================================================================
    # Environment Panel
    # =========================================================================

    def _create_environment_panel_content(self, panel):
        """Create content for Step 2: Environmental Preferences."""
        panel_width = panel.get_relative_rect().width - 20
        y = 5

        # Initialize slider references
        self.gravity_ideal_slider = None
        self.gravity_tolerance_slider = None
        self.gravity_ideal_label = None
        self.gravity_tolerance_label = None

        self.temp_ideal_slider = None
        self.temp_tolerance_slider = None
        self.temp_ideal_label = None
        self.temp_tolerance_label = None

        self.radiation_slider = None
        self.radiation_label = None

        self.atmosphere_sliders = {}
        self.atmosphere_labels = {}

        # Section 1: Gravity
        y = self._create_gravity_section(panel, y, panel_width)
        y += 15

        # Section 2: Temperature
        y = self._create_temperature_section(panel, y, panel_width)
        y += 15

        # Section 3: Radiation Tolerance
        y = self._create_radiation_section(panel, y, panel_width)
        y += 15

        # Section 4: Atmosphere Preferences
        y = self._create_atmosphere_section(panel, y, panel_width)

    def _create_gravity_section(self, panel, y: int, width: int) -> int:
        """Create gravity preference controls."""
        pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(10, y, 200, 25),
            text="Gravity Preferences:",
            manager=self.ui_manager,
            container=panel,
            object_id="#section_header"
        )
        y += 28

        # Ideal gravity: 0.1 - 3.0 g
        pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(20, y, 100, 22),
            text="Ideal (g):",
            manager=self.ui_manager,
            container=panel
        )
        self.gravity_ideal_slider = pygame_gui.elements.UIHorizontalSlider(
            relative_rect=pygame.Rect(120, y, width - 200, 22),
            start_value=self.race_config.gravity_ideal,
            value_range=(0.1, 3.0),
            manager=self.ui_manager,
            container=panel,
            click_increment=0.1
        )
        self.gravity_ideal_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(width - 70, y, 60, 22),
            text=f"{self.race_config.gravity_ideal:.1f}",
            manager=self.ui_manager,
            container=panel
        )
        y += 26

        # Tolerance: 0.0 - 1.0 g
        pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(20, y, 100, 22),
            text="Tolerance:",
            manager=self.ui_manager,
            container=panel
        )
        self.gravity_tolerance_slider = pygame_gui.elements.UIHorizontalSlider(
            relative_rect=pygame.Rect(120, y, width - 200, 22),
            start_value=self.race_config.gravity_tolerance,
            value_range=(0.0, 1.0),
            manager=self.ui_manager,
            container=panel,
            click_increment=0.05
        )
        self.gravity_tolerance_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(width - 70, y, 60, 22),
            text=f"±{self.race_config.gravity_tolerance:.2f}",
            manager=self.ui_manager,
            container=panel
        )
        y += 26

        return y

    def _create_temperature_section(self, panel, y: int, width: int) -> int:
        """Create temperature preference controls."""
        pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(10, y, 200, 25),
            text="Temperature Preferences:",
            manager=self.ui_manager,
            container=panel,
            object_id="#section_header"
        )
        y += 28

        # Ideal temperature: 200 - 400 K
        pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(20, y, 100, 22),
            text="Ideal (K):",
            manager=self.ui_manager,
            container=panel
        )
        self.temp_ideal_slider = pygame_gui.elements.UIHorizontalSlider(
            relative_rect=pygame.Rect(120, y, width - 200, 22),
            start_value=self.race_config.temperature_ideal,
            value_range=(200, 400),
            manager=self.ui_manager,
            container=panel,
            click_increment=5
        )
        self.temp_ideal_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(width - 70, y, 60, 22),
            text=f"{self.race_config.temperature_ideal:.0f}",
            manager=self.ui_manager,
            container=panel
        )
        y += 26

        # Tolerance: 0 - 100 K
        pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(20, y, 100, 22),
            text="Tolerance:",
            manager=self.ui_manager,
            container=panel
        )
        self.temp_tolerance_slider = pygame_gui.elements.UIHorizontalSlider(
            relative_rect=pygame.Rect(120, y, width - 200, 22),
            start_value=self.race_config.temperature_tolerance,
            value_range=(0, 100),
            manager=self.ui_manager,
            container=panel,
            click_increment=5
        )
        self.temp_tolerance_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(width - 70, y, 60, 22),
            text=f"±{self.race_config.temperature_tolerance:.0f}",
            manager=self.ui_manager,
            container=panel
        )
        y += 26

        return y

    def _create_radiation_section(self, panel, y: int, width: int) -> int:
        """Create radiation tolerance control."""
        pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(10, y, 200, 25),
            text="Radiation Tolerance:",
            manager=self.ui_manager,
            container=panel,
            object_id="#section_header"
        )
        y += 28

        # Radiation: -100 (sensitive) to +100 (resistant)
        pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(20, y, 100, 22),
            text="Tolerance:",
            manager=self.ui_manager,
            container=panel
        )
        self.radiation_slider = pygame_gui.elements.UIHorizontalSlider(
            relative_rect=pygame.Rect(120, y, width - 200, 22),
            start_value=self.race_config.radiation_tolerance,
            value_range=(-100, 100),
            manager=self.ui_manager,
            container=panel,
            click_increment=5
        )
        self.radiation_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(width - 70, y, 60, 22),
            text=self._format_radiation(self.race_config.radiation_tolerance),
            manager=self.ui_manager,
            container=panel
        )
        y += 26

        return y

    def _create_atmosphere_section(self, panel, y: int, width: int) -> int:
        """Create atmosphere preference controls."""
        pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(10, y, 300, 25),
            text="Atmosphere Preferences (-100 toxic to +100 beneficial):",
            manager=self.ui_manager,
            container=panel,
            object_id="#section_header"
        )
        y += 28

        # Create two columns of atmosphere sliders
        gases = list(self.race_config.atmosphere_preferences.keys())
        col_width = (width - 30) // 2

        for i, gas in enumerate(gases):
            col = i % 2
            row = i // 2
            x_offset = 10 + col * (col_width + 10)
            y_pos = y + row * 28

            # Gas label
            pygame_gui.elements.UILabel(
                relative_rect=pygame.Rect(x_offset, y_pos, 80, 22),
                text=f"{gas}:",
                manager=self.ui_manager,
                container=panel
            )

            # Slider: -100 to +100
            slider = pygame_gui.elements.UIHorizontalSlider(
                relative_rect=pygame.Rect(x_offset + 85, y_pos, col_width - 145, 22),
                start_value=self.race_config.atmosphere_preferences.get(gas, 0),
                value_range=(-100, 100),
                manager=self.ui_manager,
                container=panel,
                click_increment=5
            )
            self.atmosphere_sliders[gas] = slider

            # Value label
            value = self.race_config.atmosphere_preferences.get(gas, 0)
            label = pygame_gui.elements.UILabel(
                relative_rect=pygame.Rect(x_offset + col_width - 55, y_pos, 50, 22),
                text=self._format_atmosphere(value),
                manager=self.ui_manager,
                container=panel
            )
            self.atmosphere_labels[gas] = label

        # Calculate final y position
        rows = (len(gases) + 1) // 2
        y += rows * 28

        return y

    def _format_radiation(self, value: float) -> str:
        """Format radiation tolerance value for display."""
        if value < -50:
            return f"{value:.0f} Sens"
        elif value > 50:
            return f"+{value:.0f} Res"
        elif value >= 0:
            return f"+{value:.0f}"
        else:
            return f"{value:.0f}"

    def _format_atmosphere(self, value: float) -> str:
        """Format atmosphere preference value for display."""
        if value >= 0:
            return f"+{value:.0f}"
        else:
            return f"{value:.0f}"

    def _update_env_from_sliders(self):
        """Update race_config from environment slider values."""
        if self.gravity_ideal_slider:
            self.race_config.gravity_ideal = self.gravity_ideal_slider.get_current_value()
        if self.gravity_tolerance_slider:
            self.race_config.gravity_tolerance = self.gravity_tolerance_slider.get_current_value()
        if self.temp_ideal_slider:
            self.race_config.temperature_ideal = self.temp_ideal_slider.get_current_value()
        if self.temp_tolerance_slider:
            self.race_config.temperature_tolerance = self.temp_tolerance_slider.get_current_value()
        if self.radiation_slider:
            self.race_config.radiation_tolerance = self.radiation_slider.get_current_value()

        for gas, slider in self.atmosphere_sliders.items():
            self.race_config.atmosphere_preferences[gas] = slider.get_current_value()

    def _update_env_labels(self):
        """Update environment value display labels."""
        if self.gravity_ideal_slider and self.gravity_ideal_label:
            val = self.gravity_ideal_slider.get_current_value()
            self.gravity_ideal_label.set_text(f"{val:.1f}")

        if self.gravity_tolerance_slider and self.gravity_tolerance_label:
            val = self.gravity_tolerance_slider.get_current_value()
            self.gravity_tolerance_label.set_text(f"±{val:.2f}")

        if self.temp_ideal_slider and self.temp_ideal_label:
            val = self.temp_ideal_slider.get_current_value()
            self.temp_ideal_label.set_text(f"{val:.0f}")

        if self.temp_tolerance_slider and self.temp_tolerance_label:
            val = self.temp_tolerance_slider.get_current_value()
            self.temp_tolerance_label.set_text(f"±{val:.0f}")

        if self.radiation_slider and self.radiation_label:
            val = self.radiation_slider.get_current_value()
            self.radiation_label.set_text(self._format_radiation(val))

        for gas, slider in self.atmosphere_sliders.items():
            if gas in self.atmosphere_labels:
                val = slider.get_current_value()
                self.atmosphere_labels[gas].set_text(self._format_atmosphere(val))

    # =========================================================================
    # Descriptions Panel (Step 3)
    # =========================================================================

    def _create_descriptions_panel_content(self, panel):
        """Create content for Step 3: Text Descriptions."""
        panel_width = panel.get_relative_rect().width - 20
        panel_height = panel.get_relative_rect().height - 20
        y = 5

        # Initialize text box references
        self.bio_text_box = None
        self.bio_char_label = None
        self.socio_text_box = None
        self.socio_char_label = None

        # Calculate height for each text area (split available space)
        text_area_height = (panel_height - 100) // 2  # Minus space for labels and margins

        # Biological Description
        pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(10, y, 300, 25),
            text="Biological Description:",
            manager=self.ui_manager,
            container=panel,
            object_id="#section_header"
        )
        self.bio_char_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(panel_width - 80, y, 80, 25),
            text=f"{len(self.race_config.bio_description)}/500",
            manager=self.ui_manager,
            container=panel
        )
        y += 28

        self.bio_text_box = pygame_gui.elements.UITextEntryBox(
            relative_rect=pygame.Rect(10, y, panel_width, text_area_height),
            initial_text=self.race_config.bio_description,
            manager=self.ui_manager,
            container=panel,
            object_id="#description_box"
        )
        y += text_area_height + 15

        # Sociological Description
        pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(10, y, 300, 25),
            text="Sociological Description:",
            manager=self.ui_manager,
            container=panel,
            object_id="#section_header"
        )
        self.socio_char_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(panel_width - 80, y, 80, 25),
            text=f"{len(self.race_config.socio_description)}/500",
            manager=self.ui_manager,
            container=panel
        )
        y += 28

        self.socio_text_box = pygame_gui.elements.UITextEntryBox(
            relative_rect=pygame.Rect(10, y, panel_width, text_area_height),
            initial_text=self.race_config.socio_description,
            manager=self.ui_manager,
            container=panel,
            object_id="#description_box"
        )

    def _update_description_char_counts(self):
        """Update character count labels for description text boxes."""
        if self.bio_text_box and self.bio_char_label:
            text = self.bio_text_box.get_text()
            count = len(text)
            self.bio_char_label.set_text(f"{count}/500")

        if self.socio_text_box and self.socio_char_label:
            text = self.socio_text_box.get_text()
            count = len(text)
            self.socio_char_label.set_text(f"{count}/500")

    def _update_descriptions_from_text(self):
        """Update race_config from description text boxes."""
        if self.bio_text_box:
            text = self.bio_text_box.get_text()
            # Enforce 500 char limit
            self.race_config.bio_description = text[:500]

        if self.socio_text_box:
            text = self.socio_text_box.get_text()
            # Enforce 500 char limit
            self.race_config.socio_description = text[:500]

    # =========================================================================
    # Summary Panel (Landing Page)
    # =========================================================================

    def _create_summary_panel_content(self, panel):
        """Create content for Summary tab (landing page)."""
        panel_width = panel.get_relative_rect().width - 20
        y = 10

        # Initialize summary UI elements
        self.summary_labels = {}
        self.summary_flag_images = []
        self.summary_portrait_image = None

        # Title and Load Race button at top
        pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(10, y, 400, 40),
            text="Race Configuration Summary",
            manager=self.ui_manager,
            container=panel,
            object_id="#summary_title"
        )

        # Load Race button (right side of title)
        self.btn_load = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(panel_width - 180, y, 180, 40),
            text="Load Saved Race",
            manager=self.ui_manager,
            container=panel
        )
        y += 55

        # Three column layout for larger display
        col_width = (panel_width - 40) // 3

        # Column 1: Race Name and Flag
        col1_x = 10

        # Race Name (clickable to go to Visuals tab)
        self.summary_labels['name_header'] = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(col1_x, y, col_width, 30),
            text="Race Name:",
            manager=self.ui_manager,
            container=panel
        )
        self.summary_labels['name_value'] = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(col1_x, y + 30, col_width, 30),
            text="[Click Visuals tab to set]",
            manager=self.ui_manager,
            container=panel
        )

        # Flag preview (larger)
        self.summary_labels['flag_header'] = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(col1_x, y + 70, col_width, 30),
            text="Flag:",
            manager=self.ui_manager,
            container=panel
        )

        flag_preview_size = 280
        self.summary_flag_panel = pygame_gui.elements.UIPanel(
            relative_rect=pygame.Rect(col1_x, y + 100, col_width, flag_preview_size),
            manager=self.ui_manager,
            container=panel,
            object_id="#summary_preview"
        )

        # Column 2: Portrait and Ship Theme
        col2_x = col1_x + col_width + 15

        # Portrait preview (larger)
        self.summary_labels['portrait_header'] = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(col2_x, y, col_width, 30),
            text="Portrait:",
            manager=self.ui_manager,
            container=panel
        )

        portrait_preview_size = 280
        self.summary_portrait_panel = pygame_gui.elements.UIPanel(
            relative_rect=pygame.Rect(col2_x, y + 35, portrait_preview_size, portrait_preview_size),
            manager=self.ui_manager,
            container=panel,
            object_id="#summary_preview"
        )

        # Ship Theme
        self.summary_labels['theme_header'] = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(col2_x, y + 35 + portrait_preview_size + 15, col_width, 30),
            text="Ship Theme:",
            manager=self.ui_manager,
            container=panel
        )
        self.summary_labels['theme_value'] = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(col2_x, y + 35 + portrait_preview_size + 45, col_width, 30),
            text="[Click Ships tab to set]",
            manager=self.ui_manager,
            container=panel
        )

        # Column 3: Environment and Descriptions
        col3_x = col2_x + col_width + 15

        # Environment header
        pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(col3_x, y, col_width, 30),
            text="Environmental Preferences:",
            manager=self.ui_manager,
            container=panel,
            object_id="#section_header"
        )

        env_y = y + 35

        # Gravity
        self.summary_labels['gravity'] = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(col3_x, env_y, col_width, 28),
            text="Gravity: 1.0g ± 0.30",
            manager=self.ui_manager,
            container=panel
        )
        env_y += 30

        # Temperature
        self.summary_labels['temperature'] = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(col3_x, env_y, col_width, 28),
            text="Temperature: 293K ± 50",
            manager=self.ui_manager,
            container=panel
        )
        env_y += 30

        # Radiation
        self.summary_labels['radiation'] = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(col3_x, env_y, col_width, 28),
            text="Radiation: 0 (Neutral)",
            manager=self.ui_manager,
            container=panel
        )
        env_y += 40

        # Atmosphere summary
        pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(col3_x, env_y, col_width, 28),
            text="Atmosphere:",
            manager=self.ui_manager,
            container=panel
        )
        env_y += 28

        self.summary_labels['atmosphere'] = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(col3_x, env_y, col_width, 120),
            text="All neutral (0)",
            manager=self.ui_manager,
            container=panel
        )
        env_y += 130

        # Descriptions summary
        pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(col3_x, env_y, col_width, 28),
            text="Descriptions:",
            manager=self.ui_manager,
            container=panel
        )
        env_y += 28

        self.summary_labels['bio_status'] = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(col3_x, env_y, col_width, 28),
            text="Biological: 0 chars",
            manager=self.ui_manager,
            container=panel
        )
        env_y += 28

        self.summary_labels['socio_status'] = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(col3_x, env_y, col_width, 28),
            text="Sociological: 0 chars",
            manager=self.ui_manager,
            container=panel
        )

    def _refresh_summary(self):
        """Refresh summary panel with current race_config data."""
        log_debug("Refreshing race summary")

        # Update text descriptions from text boxes before showing summary
        self._update_descriptions_from_text()

        # Update name
        if 'name_value' in self.summary_labels:
            name = self.race_config.name or "[Click Visuals tab to set]"
            self.summary_labels['name_value'].set_text(name)

        # Update theme
        if 'theme_value' in self.summary_labels:
            theme = self.race_config.theme_id or "[Click Ships tab to set]"
            self.summary_labels['theme_value'].set_text(theme)

        # Update flag preview - scale shapes to fill the panel
        for img in self.summary_flag_images:
            img.kill()
        self.summary_flag_images = []

        if self.race_config.flag_id:
            shapes = self._load_flag_full(self.race_config.flag_id)
            # Get panel dimensions and calculate shape size to fill the space
            panel_rect = self.summary_flag_panel.get_relative_rect()
            panel_w = panel_rect.width
            panel_h = panel_rect.height

            # Shapes arranged horizontally with small gaps
            num_shapes = len(shapes)
            gap = 5
            total_gaps = (num_shapes + 1) * gap
            shape_size = min((panel_w - total_gaps) // num_shapes, panel_h - 10)

            # Center the shapes vertically
            y_offset = (panel_h - shape_size) // 2

            for i, surf in enumerate(shapes):
                scaled = pygame.transform.smoothscale(surf, (shape_size, shape_size))
                x = gap + i * (shape_size + gap)
                img = pygame_gui.elements.UIImage(
                    relative_rect=pygame.Rect(x, y_offset, shape_size, shape_size),
                    image_surface=scaled,
                    manager=self.ui_manager,
                    container=self.summary_flag_panel
                )
                self.summary_flag_images.append(img)

        # Update portrait preview (larger - 256px)
        if self.summary_portrait_image:
            self.summary_portrait_image.kill()
            self.summary_portrait_image = None

        if self.race_config.portrait_id:
            surf = self._load_portrait_full(self.race_config.portrait_id)
            if surf:
                preview_size = 256
                scaled = pygame.transform.smoothscale(surf, (preview_size, preview_size))
                self.summary_portrait_image = pygame_gui.elements.UIImage(
                    relative_rect=pygame.Rect(10, 10, preview_size, preview_size),
                    image_surface=scaled,
                    manager=self.ui_manager,
                    container=self.summary_portrait_panel
                )

        # Update gravity
        if 'gravity' in self.summary_labels:
            grav = f"Gravity: {self.race_config.gravity_ideal:.1f}g ± {self.race_config.gravity_tolerance:.2f}"
            self.summary_labels['gravity'].set_text(grav)

        # Update temperature
        if 'temperature' in self.summary_labels:
            temp = f"Temperature: {self.race_config.temperature_ideal:.0f}K ± {self.race_config.temperature_tolerance:.0f}"
            self.summary_labels['temperature'].set_text(temp)

        # Update radiation
        if 'radiation' in self.summary_labels:
            rad_val = self.race_config.radiation_tolerance
            if rad_val < -50:
                rad_desc = "Sensitive"
            elif rad_val > 50:
                rad_desc = "Resistant"
            else:
                rad_desc = "Neutral"
            rad = f"Radiation: {rad_val:+.0f} ({rad_desc})"
            self.summary_labels['radiation'].set_text(rad)

        # Update atmosphere summary
        if 'atmosphere' in self.summary_labels:
            atmo_parts = []
            for gas, value in self.race_config.atmosphere_preferences.items():
                if value != 0:
                    atmo_parts.append(f"{gas}: {value:+.0f}")
            if atmo_parts:
                atmo_text = ", ".join(atmo_parts[:4])  # Limit display
                if len(atmo_parts) > 4:
                    atmo_text += "..."
            else:
                atmo_text = "All neutral (0)"
            self.summary_labels['atmosphere'].set_text(atmo_text)

        # Update description statuses
        if 'bio_status' in self.summary_labels:
            bio_len = len(self.race_config.bio_description)
            status = "Set" if bio_len > 0 else "Empty"
            self.summary_labels['bio_status'].set_text(f"Biological: {bio_len} chars ({status})")

        if 'socio_status' in self.summary_labels:
            socio_len = len(self.race_config.socio_description)
            status = "Set" if socio_len > 0 else "Empty"
            self.summary_labels['socio_status'].set_text(f"Sociological: {socio_len} chars ({status})")

    # =========================================================================
    # Navigation
    # =========================================================================

    def _create_navigation_buttons(self, container, content_width: int, content_height: int):
        """Create bottom action buttons."""
        button_y = content_height - 60
        button_width = 120
        button_height = 40

        # Cancel button (left side)
        self.btn_cancel = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(10, button_y, button_width, button_height),
            text="Cancel",
            manager=self.ui_manager,
            container=container
        )

        # Save button (right side, always visible on Summary tab)
        self.btn_save = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(content_width - button_width + 10, button_y, button_width, button_height),
            text="Save" if not self.is_editing else "Update",
            manager=self.ui_manager,
            container=container
        )

    def _show_step(self, step_num: int):
        """
        Show the specified tab panel.

        Args:
            step_num: Tab index to show (0-4)
        """
        # Clamp step number
        step_num = max(0, min(step_num, len(self.step_panels) - 1))
        self.current_step = step_num

        log_debug(f"Showing race setup tab {step_num}: {self.TAB_NAMES[step_num]}")

        # Hide all panels, show current
        for i, panel in enumerate(self.step_panels):
            if i == step_num:
                panel.show()
            else:
                panel.hide()

        # Update tab button highlighting
        self._update_tab_highlighting()

        # Update button visibility
        self._update_navigation_buttons()

        # Clear any error message
        if self.error_label:
            self.error_label.set_text("")

        # Refresh summary if showing Summary tab
        if step_num == self.TAB_SUMMARY:
            self._refresh_summary()

    def _update_navigation_buttons(self):
        """Update navigation button visibility based on current tab."""
        # Save button is only shown on Summary tab
        if self.current_step == self.TAB_SUMMARY:
            self.btn_save.show()
        else:
            self.btn_save.hide()

    def _update_tab_highlighting(self):
        """Update tab button visual states to show current tab."""
        for i, btn in enumerate(self.tab_buttons):
            if i == self.current_step:
                # Current tab - highlighted
                btn.select()
            else:
                btn.unselect()

    def _validate_for_save(self) -> tuple[bool, str]:
        """
        Validate all required fields before saving.

        Returns:
            Tuple of (is_valid, error_message)
        """
        # Update race name from input
        if hasattr(self, 'name_input') and self.name_input:
            self.race_config.name = self.name_input.get_text().strip()

        # Name is required
        if not self.race_config.name:
            return False, "Race name is required (set in Visuals tab)"

        # Flag selection required
        if not self.race_config.flag_id:
            return False, "Please select a flag (Visuals tab)"

        # Portrait selection required
        if not self.race_config.portrait_id:
            return False, "Please select a portrait (Visuals tab)"

        # Theme selection required
        if not self.race_config.theme_id:
            return False, "Please select a ship theme (Ships tab)"

        return True, ""

    def _on_tab_clicked(self, tab_index: int):
        """Handle tab button click."""
        self._show_step(tab_index)

    def _on_load_race(self):
        """Handle Load Race button click - open file dialog to load saved race."""
        import tkinter as tk
        from tkinter import filedialog

        log_debug("Opening load race dialog")

        # Create hidden tkinter root window
        root = tk.Tk()
        root.withdraw()

        # Get races directory
        races_dir = self.race_library.races_folder

        # Open file dialog
        filepath = filedialog.askopenfilename(
            title="Load Race Configuration",
            initialdir=races_dir,
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )

        root.destroy()

        if filepath:
            # Load the race configuration
            loaded_config = RaceConfig.load(filepath)
            if loaded_config:
                log_info(f"Loaded race: {loaded_config.name}")
                self.race_config = loaded_config
                self.is_editing = True

                # Update UI to reflect loaded data
                self._populate_ui_from_config()

                # Update save button text
                if self.btn_save:
                    self.btn_save.set_text("Update")

                # Refresh the summary
                self._refresh_summary()
            else:
                self.error_label.set_text("Failed to load race file")

    def _populate_ui_from_config(self):
        """Populate all UI elements from the current race_config."""
        # Update name input
        if hasattr(self, 'name_input') and self.name_input:
            self.name_input.set_text(self.race_config.name or "")

        # Update flag selection
        if self.race_config.flag_id:
            self._on_flag_selected(self.race_config.flag_id)

        # Update portrait selection
        if self.race_config.portrait_id:
            self._on_portrait_selected(self.race_config.portrait_id)

        # Update theme selection
        if self.race_config.theme_id:
            self._on_theme_selected(self.race_config.theme_id)

        # Update environment sliders
        if hasattr(self, 'gravity_ideal_slider') and self.gravity_ideal_slider:
            self.gravity_ideal_slider.set_current_value(self.race_config.gravity_ideal)
        if hasattr(self, 'gravity_tolerance_slider') and self.gravity_tolerance_slider:
            self.gravity_tolerance_slider.set_current_value(self.race_config.gravity_tolerance)
        if hasattr(self, 'temp_ideal_slider') and self.temp_ideal_slider:
            self.temp_ideal_slider.set_current_value(self.race_config.temperature_ideal)
        if hasattr(self, 'temp_tolerance_slider') and self.temp_tolerance_slider:
            self.temp_tolerance_slider.set_current_value(self.race_config.temperature_tolerance)
        if hasattr(self, 'radiation_slider') and self.radiation_slider:
            self.radiation_slider.set_current_value(self.race_config.radiation_tolerance)

        # Update atmosphere sliders
        if hasattr(self, 'atmosphere_sliders'):
            for gas, slider in self.atmosphere_sliders.items():
                if gas in self.race_config.atmosphere_preferences:
                    slider.set_current_value(self.race_config.atmosphere_preferences[gas])

        # Update environment labels
        self._update_env_labels()

        # Update description text boxes
        if hasattr(self, 'bio_text_box') and self.bio_text_box:
            self.bio_text_box.set_text(self.race_config.bio_description or "")
        if hasattr(self, 'socio_text_box') and self.socio_text_box:
            self.socio_text_box.set_text(self.race_config.socio_description or "")

        # Update description char counts
        if hasattr(self, '_update_description_char_counts'):
            self._update_description_char_counts()

    def _on_cancel(self):
        """Handle Cancel button click."""
        log_debug("Race setup cancelled")
        self.on_cancel_callback()
        self.kill()

    def _on_save(self):
        """Handle Save button click."""
        # Validate all required fields
        is_valid, error = self._validate_for_save()
        if not is_valid:
            self.error_label.set_text(error)
            return

        # Full validation (may have warnings for missing env preferences)
        is_valid, error = self.race_config.validate()
        if not is_valid:
            log_warning(f"Saving race with validation warnings: {error}")

        # Save to library
        success, message = self.race_library.save_race(self.race_config)
        if success:
            log_info(f"Race saved: {self.race_config.name}")
            self.on_complete_callback(self.race_config)
            self.kill()
        else:
            self.error_label.set_text(message)

    def process_event(self, event: pygame.event.Event) -> bool:
        """Process pygame events."""
        handled = super().process_event(event)

        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            # Check tab buttons first
            for btn in self.tab_buttons:
                if event.ui_element == btn:
                    self._on_tab_clicked(btn.tab_index)
                    handled = True
                    break

            if not handled:
                if event.ui_element == self.btn_cancel:
                    self._on_cancel()
                    handled = True
                elif event.ui_element == self.btn_save:
                    self._on_save()
                    handled = True
                elif hasattr(self, 'btn_load') and self.btn_load and event.ui_element == self.btn_load:
                    self._on_load_race()
                    handled = True
                else:
                    # Check flag buttons
                    for btn, img, flag_id in self.flag_buttons:
                        if event.ui_element == btn:
                            self._on_flag_selected(flag_id)
                            handled = True
                            break

                    # Check portrait buttons
                    if not handled:
                        for btn, img, portrait_id in self.portrait_buttons:
                            if event.ui_element == btn:
                                self._on_portrait_selected(portrait_id)
                                handled = True
                                break

                    # Check theme buttons
                    if not handled:
                        for btn, theme_id in self.theme_buttons:
                            if event.ui_element == btn:
                                self._on_theme_selected(theme_id)
                                handled = True
                                break

        # Handle slider changes
        elif event.type == pygame_gui.UI_HORIZONTAL_SLIDER_MOVED:
            self._update_env_labels()
            self._update_env_from_sliders()
            handled = True

        # Handle text entry changes
        elif event.type == pygame_gui.UI_TEXT_ENTRY_CHANGED:
            if event.ui_element in (self.bio_text_box, self.socio_text_box):
                self._update_description_char_counts()
                self._update_descriptions_from_text()
                handled = True

        return handled
