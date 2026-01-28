"""
Race Setup Screen - Multi-step wizard for configuring custom races.

PROJ-12 Phase 4: Extracted RaceBrowserDialog to separate module.

Allows users to:
- Select visual identity (flag, portrait, ship theme)
- Configure environmental preferences (gravity, temperature, atmosphere)
- Enter descriptive text (biological, sociological)
- Review and save race configuration

Cross-layer imports (acceptable for UI):
- RaceConfig: Runtime - callback data and configuration state
- RaceLibrary: Runtime - save/load race configurations
"""
import os
import pygame
import pygame_gui
from typing import Callable, Optional, List, Tuple

from game.core.logger import log_debug, log_info, log_warning, log_error
from game.core.constants import ASSET_DIR
from game.strategy.data.race_config import RaceConfig
from game.strategy.systems.race_library import RaceLibrary
from game.ui.assets import ShipThemeManager

# PROJ-12 Phase 4: Import extracted components
from game.ui.screens.race_browser_dialog import RaceBrowserDialog
from game.ui.screens.race_validator import RaceValidator
from game.ui.screens.race_asset_loader import RaceAssetLoader
from game.ui.panels.race_environment_panel import RaceEnvironmentPanel
from game.ui.panels.race_description_panel import RaceDescriptionPanel
from game.ui.panels.race_flag_gallery import RaceFlagGallery
from game.ui.panels.race_portrait_gallery import RacePortraitGallery
from game.ui.panels.race_theme_gallery import RaceThemeGallery


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
    # FLAG_THUMB_SIZE moved to RaceFlagGallery
    # PORTRAIT_THUMB_SIZE moved to RacePortraitGallery
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

        # PROJ-12 Phase 4: Use extracted asset loader
        self._asset_loader = RaceAssetLoader()

        # PROJ-12 Phase 4: Extracted panels
        self._environment_panel = None
        self._description_panel = None
        self._flag_gallery = None
        self._portrait_gallery = None
        self._theme_gallery = None

        # UI element references
        self.step_panels = []
        self.tab_buttons = []  # Tab buttons for navigation
        self.btn_cancel = None
        self.btn_save = None
        self.btn_load = None  # Load Race button on Summary
        self.error_label = None

        # Visual selection UI elements (flag/portrait/theme UI moved to respective galleries)
        self.name_input = None

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


    def _load_flag_full(self, flag_id: str) -> List[pygame.Surface]:
        """
        Load all three shapes for a flag at full display size.

        PROJ-12 Phase 4: Delegates to RaceAssetLoader.
        """
        return self._asset_loader.load_flag_full(flag_id)

    def _load_portrait_full(self, portrait_id: str) -> Optional[pygame.Surface]:
        """
        Load a portrait at full display size.

        PROJ-12 Phase 4: Delegates to RaceAssetLoader.
        """
        return self._asset_loader.load_portrait_full(portrait_id)

    def _create_placeholder(self, width: int, height: int) -> pygame.Surface:
        """Create a placeholder surface for missing assets.

        PROJ-12 Phase 4: Delegates to RaceAssetLoader.
        """
        return self._asset_loader.create_placeholder(width, height)

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

        # Column 1: Flags (PROJ-12 Phase 4: Delegate to RaceFlagGallery)
        self._flag_gallery = RaceFlagGallery(
            panel=panel,
            manager=self.ui_manager,
            race_config=self.race_config,
            x=10,
            y=y,
            width=col_width,
            height=gallery_height,
            asset_loader=self._asset_loader
        )

        # Column 2: Portraits (PROJ-12 Phase 4: Delegate to RacePortraitGallery)
        self._portrait_gallery = RacePortraitGallery(
            panel=panel,
            manager=self.ui_manager,
            race_config=self.race_config,
            x=15 + col_width,
            y=y,
            width=col_width,
            height=gallery_height,
            asset_loader=self._asset_loader
        )

    def _on_theme_selected(self, theme_id: str):
        """Handle theme selection.

        PROJ-12 Phase 4: Button highlighting now handled by RaceThemeGallery.
        This method is called via on_select_callback from the gallery.
        """
        self.race_config.theme_id = theme_id
        log_debug(f"Theme selected: {theme_id}")

        # Refresh ship preview in Ships panel
        self._refresh_ship_preview(theme_id)

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

        # PROJ-12 Phase 4: Use RaceThemeGallery for theme selection
        # The gallery handles theme buttons and selection highlighting
        self._theme_gallery = RaceThemeGallery(
            panel=panel,
            manager=self.ui_manager,
            race_config=self.race_config,
            x=10,
            y=y,
            width=panel_width,
            on_select_callback=self._on_theme_selected
        )

        # Calculate remaining height for ship preview area
        # Account for theme gallery (approx 200px for label + preview + 4 theme buttons)
        theme_gallery_height = 200
        y += theme_gallery_height + 10

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

        # Note: theme selection is handled by RaceThemeGallery via on_select_callback

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

        # Use the scrolling container directly for adding elements
        container = self.ship_preview_scroll
        container_width = container.get_relative_rect().width - 30
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

        # Calculate and set scrollable area BEFORE adding elements
        total_rows = (len(ship_classes) + 1) // 2
        scroll_height = 10 + total_rows * (row_height + 20) + 50
        self.ship_preview_scroll.set_scrollable_area_dimensions(
            (container_width, scroll_height)
        )

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
    # Environment Panel (PROJ-12 Phase 4: Delegates to RaceEnvironmentPanel)
    # =========================================================================

    def _create_environment_panel_content(self, panel):
        """Create content for Environment tab using extracted RaceEnvironmentPanel."""
        self._environment_panel = RaceEnvironmentPanel(
            panel=panel,
            manager=self.ui_manager,
            race_config=self.race_config
        )

    def _update_env_from_sliders(self):
        """Update race_config from environment slider values.

        PROJ-12 Phase 4: Delegates to RaceEnvironmentPanel.
        """
        if self._environment_panel:
            self._environment_panel.update_config()

    def _update_env_labels(self):
        """Update environment value display labels.

        PROJ-12 Phase 4: Delegates to RaceEnvironmentPanel.
        """
        if self._environment_panel:
            self._environment_panel.update_labels()

    def _format_radiation(self, value: float) -> str:
        """Format radiation tolerance value for display.

        PROJ-12 Phase 4: Delegates to RaceEnvironmentPanel.
        """
        if self._environment_panel:
            return self._environment_panel._format_radiation(value)
        # Fallback if panel not initialized
        if value < -50:
            return f"{value:.0f} Sens"
        elif value > 50:
            return f"+{value:.0f} Res"
        elif value >= 0:
            return f"+{value:.0f}"
        else:
            return f"{value:.0f}"

    # =========================================================================
    # Descriptions Panel (PROJ-12 Phase 4: Delegates to RaceDescriptionPanel)
    # =========================================================================

    def _create_descriptions_panel_content(self, panel):
        """Create content for Descriptions tab using extracted RaceDescriptionPanel."""
        self._description_panel = RaceDescriptionPanel(
            panel=panel,
            manager=self.ui_manager,
            race_config=self.race_config
        )

    def _update_description_char_counts(self):
        """Update character count labels for description text boxes.

        PROJ-12 Phase 4: Delegates to RaceDescriptionPanel.
        """
        if self._description_panel:
            self._description_panel.update_char_counts()

    def _update_descriptions_from_text(self):
        """Update race_config from description text boxes.

        PROJ-12 Phase 4: Delegates to RaceDescriptionPanel.
        """
        if self._description_panel:
            self._description_panel.update_config()

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
        self.summary_ship_images = []

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

        # Ship Theme header (next to portrait)
        ship_theme_y = y + 35 + portrait_preview_size + 15
        self.summary_labels['theme_header'] = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(col2_x, ship_theme_y, col_width, 30),
            text="Ship Theme:",
            manager=self.ui_manager,
            container=panel
        )
        self.summary_labels['theme_value'] = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(col2_x, ship_theme_y + 30, col_width, 30),
            text="[Click Ships tab to set]",
            manager=self.ui_manager,
            container=panel
        )

        # Ship preview panel - full width across bottom
        # Shows 3 categories (Fighter, Satellite, Capital) with top-down + portrait views
        ship_panel_y = y + 400  # Below flag and portrait areas
        ship_preview_width = panel_width - 20  # Full width minus margins
        ship_preview_height = 200  # Height for 150px images + 30px labels + padding
        self.summary_ship_panel = pygame_gui.elements.UIPanel(
            relative_rect=pygame.Rect(10, ship_panel_y, ship_preview_width, ship_preview_height),
            manager=self.ui_manager,
            container=panel,
            object_id="#summary_preview"
        )
        self.summary_ship_images = []  # Track ship preview images for cleanup
        self.summary_ship_labels = []  # Track ship labels for cleanup

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

        # Update ship preview (show 1 ship per category with top-down + portrait views)
        for img in self.summary_ship_images:
            img.kill()
        self.summary_ship_images = []

        # Also clean up ship labels
        if hasattr(self, 'summary_ship_labels'):
            for lbl in self.summary_ship_labels:
                lbl.kill()
        self.summary_ship_labels = []

        if self.race_config.theme_id and hasattr(self, 'summary_ship_panel'):
            theme_manager = ShipThemeManager.instance()
            theme_manager.initialize()

            # Show one representative from each category with both views
            # Categories: Fighter, Satellite, Capital Ship
            ship_categories = [
                ("Fighter (Medium)", "Fighter"),
                ("Satellite (Medium)", "Satellite"),
                ("Cruiser", "Capital Ship")
            ]

            # Large images since we only show 3 ships
            ship_size = 150  # Size for each view (top-down and portrait)
            label_height = 30
            gap = 20

            # Layout: each category gets top-down + portrait side by side
            # [Top-Down | Portrait] [Label]
            cell_width = (ship_size * 2) + gap  # Two images side by side
            x = 20
            y = 10

            for ship_class, category_name in ship_categories:
                # Get top-down skin
                skin_surf = theme_manager.get_image(self.race_config.theme_id, ship_class)
                # Get portrait
                portrait_surf = theme_manager.get_portrait_image(self.race_config.theme_id, ship_class)

                # Display top-down view
                if skin_surf:
                    w, h = skin_surf.get_size()
                    scale = min(ship_size / w, ship_size / h)
                    new_size = (int(w * scale), int(h * scale))
                    scaled = pygame.transform.smoothscale(skin_surf, new_size)

                    # Center in left cell
                    img_x = x + (ship_size - new_size[0]) // 2
                    img_y = y + (ship_size - new_size[1]) // 2

                    img = pygame_gui.elements.UIImage(
                        relative_rect=pygame.Rect(img_x, img_y, new_size[0], new_size[1]),
                        image_surface=scaled,
                        manager=self.ui_manager,
                        container=self.summary_ship_panel
                    )
                    self.summary_ship_images.append(img)

                # Display portrait view
                if portrait_surf:
                    w, h = portrait_surf.get_size()
                    scale = min(ship_size / w, ship_size / h)
                    new_size = (int(w * scale), int(h * scale))
                    scaled = pygame.transform.smoothscale(portrait_surf, new_size)

                    # Center in right cell
                    img_x = x + ship_size + gap + (ship_size - new_size[0]) // 2
                    img_y = y + (ship_size - new_size[1]) // 2

                    img = pygame_gui.elements.UIImage(
                        relative_rect=pygame.Rect(img_x, img_y, new_size[0], new_size[1]),
                        image_surface=scaled,
                        manager=self.ui_manager,
                        container=self.summary_ship_panel
                    )
                    self.summary_ship_images.append(img)

                # Add category label below both images
                lbl = pygame_gui.elements.UILabel(
                    relative_rect=pygame.Rect(x, y + ship_size, cell_width, label_height),
                    text=category_name,
                    manager=self.ui_manager,
                    container=self.summary_ship_panel
                )
                self.summary_ship_labels.append(lbl)

                # Move to next category (horizontal layout)
                x += cell_width + 30

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

        # Refresh content when showing specific tabs
        if step_num == self.TAB_SUMMARY:
            self._refresh_summary()
        elif step_num == self.TAB_SHIPS:
            # Refresh ship preview when Ships tab is shown
            if self.race_config.theme_id:
                self._refresh_ship_preview(self.race_config.theme_id)

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

        PROJ-12 Phase 4: Delegates to RaceValidator.

        Returns:
            Tuple of (is_valid, error_message)
        """
        # Update race name from input
        if hasattr(self, 'name_input') and self.name_input:
            self.race_config.name = self.name_input.get_text().strip()

        # PROJ-12: Use extracted RaceValidator
        validator = RaceValidator()
        result = validator.validate(self.race_config)
        return result.is_valid, result.message

    def _on_tab_clicked(self, tab_index: int):
        """Handle tab button click."""
        self._show_step(tab_index)

    def _on_load_race(self):
        """Handle Load Race button click - open in-game race browser dialog."""
        log_debug("Opening race browser dialog")

        # Get window position for dialog placement
        window_rect = self.get_abs_rect()
        dialog_width = 600
        dialog_height = 500

        # Center dialog over the main window
        dialog_x = window_rect.centerx - dialog_width // 2
        dialog_y = window_rect.centery - dialog_height // 2

        dialog_rect = pygame.Rect(dialog_x, dialog_y, dialog_width, dialog_height)

        # Create and show the race browser dialog
        self.race_browser = RaceBrowserDialog(
            rect=dialog_rect,
            manager=self.ui_manager,
            race_library=self.race_library,
            on_select_callback=self._on_race_selected,
            on_cancel_callback=self._on_race_browser_cancelled
        )

    def _on_race_selected(self, loaded_config: RaceConfig):
        """Handle race selection from browser dialog."""
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

    def _on_race_browser_cancelled(self):
        """Handle race browser cancellation."""
        log_debug("Race browser cancelled")

    def _populate_ui_from_config(self):
        """Populate all UI elements from the current race_config."""
        # Update name input
        if hasattr(self, 'name_input') and self.name_input:
            self.name_input.set_text(self.race_config.name or "")

        # Update flag selection (PROJ-12 Phase 4: Delegate to RaceFlagGallery)
        if self._flag_gallery:
            self._flag_gallery.set_from_config()

        # Update portrait selection (PROJ-12 Phase 4: Delegate to RacePortraitGallery)
        if self._portrait_gallery:
            self._portrait_gallery.set_from_config()

        # Update theme selection (PROJ-12 Phase 4: Delegate to RaceThemeGallery)
        if self._theme_gallery:
            self._theme_gallery.set_from_config()

        # Update environment sliders (PROJ-12 Phase 4: Delegate to RaceEnvironmentPanel)
        if self._environment_panel:
            self._environment_panel.set_from_config()

        # Update description text boxes (PROJ-12 Phase 4: Delegate to RaceDescriptionPanel)
        if self._description_panel:
            self._description_panel.set_from_config()

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
                    # Check flag buttons (PROJ-12 Phase 4: Delegate to RaceFlagGallery)
                    if self._flag_gallery and self._flag_gallery.handle_button_click(event.ui_element):
                        handled = True

                    # Check portrait buttons (PROJ-12 Phase 4: Delegate to RacePortraitGallery)
                    if not handled:
                        if self._portrait_gallery and self._portrait_gallery.handle_button_click(event.ui_element):
                            handled = True

                    # Check theme buttons (PROJ-12 Phase 4: Delegate to RaceThemeGallery)
                    if not handled:
                        if self._theme_gallery and self._theme_gallery.handle_button_click(event.ui_element):
                            handled = True

        # Handle slider changes
        elif event.type == pygame_gui.UI_HORIZONTAL_SLIDER_MOVED:
            self._update_env_labels()
            self._update_env_from_sliders()
            handled = True

        # Handle text entry changes (PROJ-12 Phase 4: Check description panel text boxes)
        elif event.type == pygame_gui.UI_TEXT_ENTRY_CHANGED:
            if self._description_panel:
                desc_text_boxes = (
                    self._description_panel.bio_text_box,
                    self._description_panel.socio_text_box
                )
                if event.ui_element in desc_text_boxes:
                    self._update_description_char_counts()
                    self._update_descriptions_from_text()
                    handled = True

        return handled
