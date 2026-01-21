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
    """Multi-step wizard window for race configuration."""

    # Step constants
    STEP_VISUALS = 0
    STEP_ENVIRONMENT = 1
    STEP_DESCRIPTIONS = 2
    STEP_SUMMARY = 3

    STEP_NAMES = [
        "Visual Identity",
        "Environment",
        "Descriptions",
        "Summary"
    ]

    # Thumbnail sizes
    FLAG_THUMB_SIZE = 64
    PORTRAIT_THUMB_SIZE = 80
    THEME_SHIP_SIZE = 60

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

        # Current wizard step
        self.current_step = self.STEP_VISUALS

        # Race library for save/load
        self.race_library = RaceLibrary()

        # Asset caches
        self._flag_cache = None  # List of (flag_id, thumbnail_surface)
        self._portrait_cache = None  # List of (portrait_id, thumbnail_surface)
        self._theme_cache = None  # List of (theme_id, ship_surfaces_dict)

        # UI element references
        self.step_panels = []
        self.step_indicator_labels = []
        self.btn_back = None
        self.btn_next = None
        self.btn_cancel = None
        self.btn_save = None
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

        # Step indicator at top
        self._create_step_indicator(container, content_width)

        # Content area for step panels (below indicator, above buttons)
        panel_top = 50
        panel_height = content_height - 130  # Leave room for buttons

        # Create panels for each step
        self._create_step_panels(container, content_width, panel_top, panel_height)

        # Navigation buttons at bottom
        self._create_navigation_buttons(container, content_width, content_height)

        # Error label above buttons
        self.error_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(10, content_height - 90, content_width, 25),
            text="",
            manager=self.ui_manager,
            container=container
        )

    def _create_step_indicator(self, container, content_width: int):
        """Create step indicator showing wizard progress."""
        indicator_y = 10
        step_width = content_width // 4

        for i, name in enumerate(self.STEP_NAMES):
            label = pygame_gui.elements.UILabel(
                relative_rect=pygame.Rect(10 + i * step_width, indicator_y, step_width - 10, 30),
                text=f"{i + 1}. {name}",
                manager=self.ui_manager,
                container=container,
                object_id="#step_indicator"
            )
            self.step_indicator_labels.append(label)

    def _create_step_panels(self, container, width: int, top: int, height: int):
        """Create panels for each wizard step."""
        panel_rect = pygame.Rect(10, top, width, height)

        # Panel 0: Visual Selection
        panel_visuals = pygame_gui.elements.UIPanel(
            relative_rect=panel_rect,
            manager=self.ui_manager,
            container=container,
            object_id="#panel_visuals"
        )
        self._create_visuals_panel_content(panel_visuals)
        self.step_panels.append(panel_visuals)

        # Panel 1: Environment Preferences
        panel_environment = pygame_gui.elements.UIPanel(
            relative_rect=panel_rect,
            manager=self.ui_manager,
            container=container,
            object_id="#panel_environment"
        )
        self._create_environment_panel_content(panel_environment)
        self.step_panels.append(panel_environment)

        # Panel 2: Descriptions
        panel_descriptions = pygame_gui.elements.UIPanel(
            relative_rect=panel_rect,
            manager=self.ui_manager,
            container=container,
            object_id="#panel_descriptions"
        )
        self._create_descriptions_panel_content(panel_descriptions)
        self.step_panels.append(panel_descriptions)

        # Panel 3: Summary
        panel_summary = pygame_gui.elements.UIPanel(
            relative_rect=panel_rect,
            manager=self.ui_manager,
            container=container,
            object_id="#panel_summary"
        )
        self._create_summary_panel_content(panel_summary)
        self.step_panels.append(panel_summary)

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
        Load all three shapes for a flag at display size.

        Args:
            flag_id: Flag directory name

        Returns:
            List of [rectangle, shield, triangle] surfaces
        """
        shapes = []
        flags_dir = os.path.join(ASSET_DIR, "Images", "Flags", "Processed")
        flag_dir = os.path.join(flags_dir, flag_id)

        for shape in ["rectangle", "shield", "triangle"]:
            # Try 256px first, then root
            shape_path = os.path.join(flag_dir, "256", f"{shape}.png")
            if not os.path.exists(shape_path):
                shape_path = os.path.join(flag_dir, f"{shape}.png")

            if os.path.exists(shape_path):
                try:
                    surf = pygame.image.load(shape_path).convert_alpha()
                    # Scale to 64px for preview
                    scaled = pygame.transform.smoothscale(surf, (64, 64))
                    shapes.append(scaled)
                except Exception as e:
                    log_error(f"Failed to load flag shape {shape_path}: {e}")
                    shapes.append(self._create_placeholder(64, 64))
            else:
                shapes.append(self._create_placeholder(64, 64))

        return shapes

    def _load_portrait_full(self, portrait_id: str) -> Optional[pygame.Surface]:
        """
        Load a portrait at larger display size.

        Args:
            portrait_id: Portrait filename

        Returns:
            Scaled surface or None
        """
        portraits_dir = os.path.join(ASSET_DIR, "Images", "Race Portraits")
        portrait_path = os.path.join(portraits_dir, portrait_id)

        if os.path.exists(portrait_path):
            try:
                surf = pygame.image.load(portrait_path).convert_alpha()
                # Scale to 128x128 for preview
                scaled = pygame.transform.smoothscale(surf, (128, 128))
                return scaled
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
    # Visual Selection Panel (Step 1)
    # =========================================================================

    def _create_visuals_panel_content(self, panel):
        """Create content for Step 1: Visual Selection."""
        panel_width = panel.get_relative_rect().width - 20
        y = 5

        # Race Name
        pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(10, y, 100, 25),
            text="Race Name:",
            manager=self.ui_manager,
            container=panel
        )
        self.name_input = pygame_gui.elements.UITextEntryLine(
            relative_rect=pygame.Rect(110, y, 250, 30),
            manager=self.ui_manager,
            container=panel,
            placeholder_text="Enter race name..."
        )
        if self.race_config.name:
            self.name_input.set_text(self.race_config.name)
        y += 40

        # Divider
        pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(10, y, panel_width, 2),
            text="",
            manager=self.ui_manager,
            container=panel,
            object_id="#divider"
        )
        y += 10

        # Create three columns: Flags, Portraits, Themes
        col_width = (panel_width - 30) // 3

        # Column 1: Flags
        self._create_flag_gallery(panel, 10, y, col_width)

        # Column 2: Portraits
        self._create_portrait_gallery(panel, 15 + col_width, y, col_width)

        # Column 3: Themes
        self._create_theme_gallery(panel, 20 + 2 * col_width, y, col_width)

    def _create_flag_gallery(self, panel, x: int, y: int, width: int):
        """Create flag selection gallery."""
        pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(x, y, width, 25),
            text="Select Flag:",
            manager=self.ui_manager,
            container=panel
        )
        y += 25

        # Preview area for selected flag (3 shapes)
        preview_height = 70
        self.flag_preview_panel = pygame_gui.elements.UIPanel(
            relative_rect=pygame.Rect(x, y, width, preview_height),
            manager=self.ui_manager,
            container=panel,
            object_id="#flag_preview"
        )
        y += preview_height + 5

        # Scrolling container for thumbnails
        scroll_height = 280
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
        cols = max(1, (width - 20) // (thumb_size + 5))
        row = 0
        col = 0

        for flag_id, thumb_surf in flags:
            btn_x = 5 + col * (thumb_size + 5)
            btn_y = 5 + row * (thumb_size + 5)

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
        total_rows = (len(flags) + cols - 1) // cols
        self.flag_scroll.set_scrollable_area_dimensions(
            (width - 20, 10 + total_rows * (thumb_size + 5))
        )

        # Pre-select if editing
        if self.race_config.flag_id:
            self._on_flag_selected(self.race_config.flag_id)

    def _create_portrait_gallery(self, panel, x: int, y: int, width: int):
        """Create portrait selection gallery."""
        pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(x, y, width, 25),
            text="Select Portrait:",
            manager=self.ui_manager,
            container=panel
        )
        y += 25

        # Preview area for selected portrait
        preview_height = 70
        self.portrait_preview_panel = pygame_gui.elements.UIPanel(
            relative_rect=pygame.Rect(x, y, width, preview_height),
            manager=self.ui_manager,
            container=panel,
            object_id="#portrait_preview"
        )
        y += preview_height + 5

        # Scrolling container for thumbnails
        scroll_height = 280
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
        cols = max(1, (width - 20) // (thumb_size + 5))
        row = 0
        col = 0

        for portrait_id, thumb_surf in portraits:
            btn_x = 5 + col * (thumb_size + 5)
            btn_y = 5 + row * (thumb_size + 5)

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
        total_rows = (len(portraits) + cols - 1) // cols
        self.portrait_scroll.set_scrollable_area_dimensions(
            (width - 20, 10 + total_rows * (thumb_size + 5))
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

        # Load and display all three shapes
        shapes = self._load_flag_full(flag_id)
        shape_names = ["rectangle", "shield", "triangle"]
        preview_x = 5

        for i, (surf, name) in enumerate(zip(shapes, shape_names)):
            img = pygame_gui.elements.UIImage(
                relative_rect=pygame.Rect(preview_x + i * 70, 3, 64, 64),
                image_surface=surf,
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

        # Load and display larger preview
        surf = self._load_portrait_full(portrait_id)
        if surf:
            # Center the 128x128 image in the 70px tall preview panel
            # Scale down to fit
            scaled = pygame.transform.smoothscale(surf, (64, 64))
            self.portrait_preview_image = pygame_gui.elements.UIImage(
                relative_rect=pygame.Rect(5, 3, 64, 64),
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

        # Update preview label
        self.theme_preview_label.set_text(f"Selected: {theme_id}")

        # Update button highlights
        for btn, tid in self.theme_buttons:
            if tid == theme_id:
                btn.select()
            else:
                btn.unselect()

    # =========================================================================
    # Environment Panel (Step 2)
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
            color = "red" if count > 500 else "white"
            self.bio_char_label.set_text(f"{count}/500")

        if self.socio_text_box and self.socio_char_label:
            text = self.socio_text_box.get_text()
            count = len(text)
            color = "red" if count > 500 else "white"
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
    # Summary Panel (Step 4)
    # =========================================================================

    def _create_summary_panel_content(self, panel):
        """Create content for Step 4: Summary."""
        panel_width = panel.get_relative_rect().width - 20
        y = 5

        # Initialize summary UI elements
        self.summary_labels = {}
        self.summary_flag_images = []
        self.summary_portrait_image = None

        # Title
        pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(10, y, panel_width, 30),
            text="Race Configuration Summary",
            manager=self.ui_manager,
            container=panel,
            object_id="#summary_title"
        )
        y += 35

        # Two column layout
        left_col_width = panel_width // 2 - 15
        right_col_width = panel_width // 2 - 15

        # Left column: Name, Flag, Portrait previews
        left_x = 10

        # Race Name
        self.summary_labels['name_header'] = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(left_x, y, 100, 22),
            text="Race Name:",
            manager=self.ui_manager,
            container=panel
        )
        self.summary_labels['name_value'] = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(left_x + 100, y, left_col_width - 100, 22),
            text="[Not Set]",
            manager=self.ui_manager,
            container=panel
        )
        y += 28

        # Flag preview area
        self.summary_labels['flag_header'] = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(left_x, y, 100, 22),
            text="Flag:",
            manager=self.ui_manager,
            container=panel
        )
        y += 25

        self.summary_flag_panel = pygame_gui.elements.UIPanel(
            relative_rect=pygame.Rect(left_x, y, 210, 70),
            manager=self.ui_manager,
            container=panel,
            object_id="#summary_preview"
        )
        y += 75

        # Portrait preview
        self.summary_labels['portrait_header'] = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(left_x, y, 100, 22),
            text="Portrait:",
            manager=self.ui_manager,
            container=panel
        )
        y += 25

        self.summary_portrait_panel = pygame_gui.elements.UIPanel(
            relative_rect=pygame.Rect(left_x, y, 100, 100),
            manager=self.ui_manager,
            container=panel,
            object_id="#summary_preview"
        )
        y += 105

        # Ship Theme
        self.summary_labels['theme_header'] = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(left_x, y, 100, 22),
            text="Ship Theme:",
            manager=self.ui_manager,
            container=panel
        )
        self.summary_labels['theme_value'] = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(left_x + 100, y, left_col_width - 100, 22),
            text="[Not Set]",
            manager=self.ui_manager,
            container=panel
        )

        # Right column: Environment summary
        right_x = panel_width // 2 + 10
        right_y = 35

        # Environment header
        pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(right_x, right_y, right_col_width, 25),
            text="Environmental Preferences:",
            manager=self.ui_manager,
            container=panel,
            object_id="#section_header"
        )
        right_y += 28

        # Gravity
        self.summary_labels['gravity'] = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(right_x, right_y, right_col_width, 22),
            text="Gravity: 1.0g ± 0.30",
            manager=self.ui_manager,
            container=panel
        )
        right_y += 24

        # Temperature
        self.summary_labels['temperature'] = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(right_x, right_y, right_col_width, 22),
            text="Temperature: 293K ± 50",
            manager=self.ui_manager,
            container=panel
        )
        right_y += 24

        # Radiation
        self.summary_labels['radiation'] = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(right_x, right_y, right_col_width, 22),
            text="Radiation: 0 (Neutral)",
            manager=self.ui_manager,
            container=panel
        )
        right_y += 30

        # Atmosphere summary
        pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(right_x, right_y, right_col_width, 22),
            text="Atmosphere:",
            manager=self.ui_manager,
            container=panel
        )
        right_y += 22

        self.summary_labels['atmosphere'] = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(right_x, right_y, right_col_width, 80),
            text="All neutral (0)",
            manager=self.ui_manager,
            container=panel
        )
        right_y += 85

        # Descriptions summary
        pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(right_x, right_y, right_col_width, 22),
            text="Descriptions:",
            manager=self.ui_manager,
            container=panel
        )
        right_y += 22

        self.summary_labels['bio_status'] = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(right_x, right_y, right_col_width, 22),
            text="Biological: 0 chars",
            manager=self.ui_manager,
            container=panel
        )
        right_y += 22

        self.summary_labels['socio_status'] = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(right_x, right_y, right_col_width, 22),
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
            name = self.race_config.name or "[Not Set]"
            self.summary_labels['name_value'].set_text(name)

        # Update theme
        if 'theme_value' in self.summary_labels:
            theme = self.race_config.theme_id or "[Not Set]"
            self.summary_labels['theme_value'].set_text(theme)

        # Update flag preview
        for img in self.summary_flag_images:
            img.kill()
        self.summary_flag_images = []

        if self.race_config.flag_id:
            shapes = self._load_flag_full(self.race_config.flag_id)
            for i, surf in enumerate(shapes):
                img = pygame_gui.elements.UIImage(
                    relative_rect=pygame.Rect(5 + i * 68, 3, 64, 64),
                    image_surface=surf,
                    manager=self.ui_manager,
                    container=self.summary_flag_panel
                )
                self.summary_flag_images.append(img)

        # Update portrait preview
        if self.summary_portrait_image:
            self.summary_portrait_image.kill()
            self.summary_portrait_image = None

        if self.race_config.portrait_id:
            surf = self._load_portrait_full(self.race_config.portrait_id)
            if surf:
                scaled = pygame.transform.smoothscale(surf, (96, 96))
                self.summary_portrait_image = pygame_gui.elements.UIImage(
                    relative_rect=pygame.Rect(2, 2, 96, 96),
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
        """Create navigation buttons at bottom of window."""
        button_y = content_height - 60
        button_width = 100
        button_height = 40

        # Back button (left side)
        self.btn_back = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(10, button_y, button_width, button_height),
            text="< Back",
            manager=self.ui_manager,
            container=container
        )

        # Cancel button (center-left)
        self.btn_cancel = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(120, button_y, button_width, button_height),
            text="Cancel",
            manager=self.ui_manager,
            container=container
        )

        # Next button (right side)
        self.btn_next = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(content_width - button_width + 10, button_y, button_width, button_height),
            text="Next >",
            manager=self.ui_manager,
            container=container
        )

        # Save button (replaces Next on final step)
        self.btn_save = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(content_width - button_width + 10, button_y, button_width, button_height),
            text="Save" if not self.is_editing else "Update",
            manager=self.ui_manager,
            container=container
        )
        self.btn_save.hide()

    def _show_step(self, step_num: int):
        """
        Show the specified wizard step.

        Args:
            step_num: Step index to show (0-3)
        """
        # Clamp step number
        step_num = max(0, min(step_num, len(self.step_panels) - 1))
        self.current_step = step_num

        log_debug(f"Showing race setup step {step_num}: {self.STEP_NAMES[step_num]}")

        # Hide all panels, show current
        for i, panel in enumerate(self.step_panels):
            if i == step_num:
                panel.show()
            else:
                panel.hide()

        # Update step indicator highlighting
        for i, label in enumerate(self.step_indicator_labels):
            if i == step_num:
                label.text_colour = pygame.Color(255, 255, 100)  # Highlight current
            elif i < step_num:
                label.text_colour = pygame.Color(100, 255, 100)  # Completed
            else:
                label.text_colour = pygame.Color(180, 180, 180)  # Future
            label.rebuild()

        # Update button visibility
        self._update_navigation_buttons()

        # Clear any error message
        if self.error_label:
            self.error_label.set_text("")

        # Refresh summary if showing final step
        if step_num == self.STEP_SUMMARY:
            self._refresh_summary()

    def _update_navigation_buttons(self):
        """Update navigation button visibility based on current step."""
        # Back button: hide on first step
        if self.current_step == self.STEP_VISUALS:
            self.btn_back.hide()
        else:
            self.btn_back.show()

        # Next vs Save: show Save only on last step
        if self.current_step == self.STEP_SUMMARY:
            self.btn_next.hide()
            self.btn_save.show()
        else:
            self.btn_next.show()
            self.btn_save.hide()

    def _validate_current_step(self) -> tuple[bool, str]:
        """
        Validate the current step before advancing.

        Returns:
            Tuple of (is_valid, error_message)
        """
        if self.current_step == self.STEP_VISUALS:
            # Update race name from input
            if hasattr(self, 'name_input') and self.name_input:
                self.race_config.name = self.name_input.get_text().strip()

            # Name is required
            if not self.race_config.name:
                return False, "Race name is required"

            # Flag selection required
            if not self.race_config.flag_id:
                return False, "Please select a flag"

            # Portrait selection required
            if not self.race_config.portrait_id:
                return False, "Please select a portrait"

            # Theme selection required
            if not self.race_config.theme_id:
                return False, "Please select a ship theme"

        return True, ""

    def _on_back(self):
        """Handle Back button click."""
        if self.current_step > self.STEP_VISUALS:
            self._show_step(self.current_step - 1)

    def _on_next(self):
        """Handle Next button click."""
        # Validate current step
        is_valid, error = self._validate_current_step()
        if not is_valid:
            self.error_label.set_text(error)
            return

        if self.current_step < self.STEP_SUMMARY:
            self._show_step(self.current_step + 1)

    def _on_cancel(self):
        """Handle Cancel button click."""
        log_debug("Race setup cancelled")
        self.on_cancel_callback()
        self.kill()

    def _on_save(self):
        """Handle Save button click."""
        # Update name from input
        if hasattr(self, 'name_input') and self.name_input:
            self.race_config.name = self.name_input.get_text().strip()

        # Validate visual selections
        is_valid, error = self._validate_current_step()
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
            if event.ui_element == self.btn_back:
                self._on_back()
                handled = True
            elif event.ui_element == self.btn_next:
                self._on_next()
                handled = True
            elif event.ui_element == self.btn_cancel:
                self._on_cancel()
                handled = True
            elif event.ui_element == self.btn_save:
                self._on_save()
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
