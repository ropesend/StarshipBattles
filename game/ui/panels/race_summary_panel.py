"""
Race Summary Panel - Displays race configuration summary on landing page.

PROJ-44 Phase 7 Task 7.1: Extracted from RaceSetupScreen to decompose the god class.

Provides a summary view of the current race configuration including:
- Race name
- Flag preview (all three shapes)
- Portrait preview
- Ship theme name and preview
- Environmental preferences summary
- Description status
"""
import pygame
import pygame_gui
from typing import Dict, List, Optional, Callable, TYPE_CHECKING

from game.core.logger import log_debug
from game.ui.assets import ShipThemeManager

if TYPE_CHECKING:
    from game.strategy.data.race_config import RaceConfig
    from game.ui.screens.race_asset_loader import RaceAssetLoader


class RaceSummaryPanel:
    """
    Panel for displaying race configuration summary.

    Creates and manages the summary view with previews of all
    selected visual elements and text summaries of configuration.
    """

    def __init__(
        self,
        panel: pygame_gui.elements.UIPanel,
        manager: pygame_gui.UIManager,
        race_config: 'RaceConfig',
        asset_loader: 'RaceAssetLoader',
        on_load_race_callback: Optional[Callable[[], None]] = None
    ):
        """
        Create summary panel content.

        Args:
            panel: Parent UIPanel to add controls to
            manager: pygame_gui UIManager
            race_config: RaceConfig to display values from
            asset_loader: RaceAssetLoader for loading flag/portrait images
            on_load_race_callback: Optional callback for Load Race button
        """
        self.panel = panel
        self.ui_manager = manager
        self.race_config = race_config
        self._asset_loader = asset_loader
        self.on_load_race_callback = on_load_race_callback

        # UI element references
        self.summary_labels: Dict[str, pygame_gui.elements.UILabel] = {}
        self.summary_flag_images: List[pygame_gui.elements.UIImage] = []
        self.summary_portrait_image: Optional[pygame_gui.elements.UIImage] = None
        self.summary_ship_images: List[pygame_gui.elements.UIImage] = []
        self.summary_ship_labels: List[pygame_gui.elements.UILabel] = []

        # Panel references for image placement
        self.summary_flag_panel: Optional[pygame_gui.elements.UIPanel] = None
        self.summary_portrait_panel: Optional[pygame_gui.elements.UIPanel] = None
        self.summary_ship_panel: Optional[pygame_gui.elements.UIPanel] = None

        # Load Race button
        self.btn_load: Optional[pygame_gui.elements.UIButton] = None

        self._create_content()

    def _create_content(self):
        """Create all panel content."""
        panel_width = self.panel.get_relative_rect().width - 20
        y = 10

        # Title and Load Race button at top
        pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(10, y, 400, 40),
            text="Race Configuration Summary",
            manager=self.ui_manager,
            container=self.panel,
            object_id="#summary_title"
        )

        # Load Race button (right side of title)
        self.btn_load = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(panel_width - 180, y, 180, 40),
            text="Load Saved Race",
            manager=self.ui_manager,
            container=self.panel
        )
        y += 55

        # Three column layout for larger display
        col_width = (panel_width - 40) // 3

        # Column 1: Race Name and Flag
        col1_x = 10
        y = self._create_column1_content(col1_x, y, col_width)

        # Column 2: Portrait and Ship Theme
        col2_x = col1_x + col_width + 15
        self._create_column2_content(col2_x, y - 55, col_width)  # Offset y for alignment

        # Column 3: Environment and Descriptions
        col3_x = col2_x + col_width + 15
        self._create_column3_content(col3_x, y - 55, col_width)

        # Ship preview panel - full width across bottom
        ship_panel_y = y + 400 - 55  # Below flag and portrait areas
        ship_preview_width = panel_width - 20  # Full width minus margins
        ship_preview_height = 200  # Height for 150px images + 30px labels + padding
        self.summary_ship_panel = pygame_gui.elements.UIPanel(
            relative_rect=pygame.Rect(10, ship_panel_y, ship_preview_width, ship_preview_height),
            manager=self.ui_manager,
            container=self.panel,
            object_id="#summary_preview"
        )

    def _create_column1_content(self, x: int, y: int, col_width: int) -> int:
        """Create column 1: Race Name and Flag."""
        # Race Name (clickable to go to Visuals tab)
        self.summary_labels['name_header'] = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(x, y, col_width, 30),
            text="Race Name:",
            manager=self.ui_manager,
            container=self.panel
        )
        self.summary_labels['name_value'] = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(x, y + 30, col_width, 30),
            text="[Click Visuals tab to set]",
            manager=self.ui_manager,
            container=self.panel
        )

        # Flag preview (larger)
        self.summary_labels['flag_header'] = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(x, y + 70, col_width, 30),
            text="Flag:",
            manager=self.ui_manager,
            container=self.panel
        )

        flag_preview_size = 280
        self.summary_flag_panel = pygame_gui.elements.UIPanel(
            relative_rect=pygame.Rect(x, y + 100, col_width, flag_preview_size),
            manager=self.ui_manager,
            container=self.panel,
            object_id="#summary_preview"
        )

        return y + 100 + flag_preview_size

    def _create_column2_content(self, x: int, y: int, col_width: int):
        """Create column 2: Portrait and Ship Theme."""
        # Portrait preview (larger)
        self.summary_labels['portrait_header'] = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(x, y, col_width, 30),
            text="Portrait:",
            manager=self.ui_manager,
            container=self.panel
        )

        portrait_preview_size = 280
        self.summary_portrait_panel = pygame_gui.elements.UIPanel(
            relative_rect=pygame.Rect(x, y + 35, portrait_preview_size, portrait_preview_size),
            manager=self.ui_manager,
            container=self.panel,
            object_id="#summary_preview"
        )

        # Ship Theme header (next to portrait)
        ship_theme_y = y + 35 + portrait_preview_size + 15
        self.summary_labels['theme_header'] = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(x, ship_theme_y, col_width, 30),
            text="Ship Theme:",
            manager=self.ui_manager,
            container=self.panel
        )
        self.summary_labels['theme_value'] = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(x, ship_theme_y + 30, col_width, 30),
            text="[Click Ships tab to set]",
            manager=self.ui_manager,
            container=self.panel
        )

    def _create_column3_content(self, x: int, y: int, col_width: int):
        """Create column 3: Environment and Descriptions."""
        # Environment header
        pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(x, y, col_width, 30),
            text="Environmental Preferences:",
            manager=self.ui_manager,
            container=self.panel,
            object_id="#section_header"
        )

        env_y = y + 35

        # Gravity
        self.summary_labels['gravity'] = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(x, env_y, col_width, 28),
            text="Gravity: 1.0g +/- 0.30",
            manager=self.ui_manager,
            container=self.panel
        )
        env_y += 30

        # Temperature
        self.summary_labels['temperature'] = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(x, env_y, col_width, 28),
            text="Temperature: 293K +/- 50",
            manager=self.ui_manager,
            container=self.panel
        )
        env_y += 30

        # Radiation
        self.summary_labels['radiation'] = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(x, env_y, col_width, 28),
            text="Radiation: 0 (Neutral)",
            manager=self.ui_manager,
            container=self.panel
        )
        env_y += 40

        # Atmosphere summary
        pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(x, env_y, col_width, 28),
            text="Atmosphere:",
            manager=self.ui_manager,
            container=self.panel
        )
        env_y += 28

        self.summary_labels['atmosphere'] = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(x, env_y, col_width, 120),
            text="All neutral (0)",
            manager=self.ui_manager,
            container=self.panel
        )
        env_y += 130

        # Descriptions summary
        pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(x, env_y, col_width, 28),
            text="Descriptions:",
            manager=self.ui_manager,
            container=self.panel
        )
        env_y += 28

        self.summary_labels['bio_status'] = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(x, env_y, col_width, 28),
            text="Biological: 0 chars",
            manager=self.ui_manager,
            container=self.panel
        )
        env_y += 28

        self.summary_labels['socio_status'] = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(x, env_y, col_width, 28),
            text="Sociological: 0 chars",
            manager=self.ui_manager,
            container=self.panel
        )

    # =========================================================================
    # Formatting Methods
    # =========================================================================

    def _format_gravity_summary(self) -> str:
        """Format gravity summary string."""
        return f"Gravity: {self.race_config.gravity_ideal:.1f}g +/- {self.race_config.gravity_tolerance:.2f}"

    def _format_temperature_summary(self) -> str:
        """Format temperature summary string."""
        return f"Temperature: {self.race_config.temperature_ideal:.0f}K +/- {self.race_config.temperature_tolerance:.0f}"

    def _format_radiation_summary(self) -> str:
        """Format radiation summary string."""
        rad_val = self.race_config.radiation_tolerance
        if rad_val < -50:
            rad_desc = "Sensitive"
        elif rad_val > 50:
            rad_desc = "Resistant"
        else:
            rad_desc = "Neutral"
        return f"Radiation: {rad_val:+.0f} ({rad_desc})"

    def _format_atmosphere_summary(self) -> str:
        """Format atmosphere summary string."""
        atmo_parts = []
        prefs = self.race_config.atmosphere_preferences
        if prefs:
            for gas, value in prefs.items():
                if value != 0:
                    atmo_parts.append(f"{gas}: {value:+.0f}")
        if atmo_parts:
            atmo_text = ", ".join(atmo_parts[:4])  # Limit display
            if len(atmo_parts) > 4:
                atmo_text += "..."
        else:
            atmo_text = "All neutral (0)"
        return atmo_text

    def _format_bio_status(self) -> str:
        """Format biological description status string."""
        bio_len = len(self.race_config.bio_description)
        status = "Set" if bio_len > 0 else "Empty"
        return f"Biological: {bio_len} chars ({status})"

    def _format_socio_status(self) -> str:
        """Format sociological description status string."""
        socio_len = len(self.race_config.socio_description)
        status = "Set" if socio_len > 0 else "Empty"
        return f"Sociological: {socio_len} chars ({status})"

    # =========================================================================
    # Refresh Summary
    # =========================================================================

    def refresh(self):
        """Refresh summary panel with current race_config data."""
        log_debug("Refreshing race summary panel")

        # Update name
        if 'name_value' in self.summary_labels:
            name = self.race_config.name or "[Click Visuals tab to set]"
            self.summary_labels['name_value'].set_text(name)

        # Update theme
        if 'theme_value' in self.summary_labels:
            theme = self.race_config.theme_id or "[Click Ships tab to set]"
            self.summary_labels['theme_value'].set_text(theme)

        # Update flag preview
        self._refresh_flag_preview()

        # Update portrait preview
        self._refresh_portrait_preview()

        # Update ship preview
        self._refresh_ship_preview()

        # Update gravity
        if 'gravity' in self.summary_labels:
            self.summary_labels['gravity'].set_text(self._format_gravity_summary())

        # Update temperature
        if 'temperature' in self.summary_labels:
            self.summary_labels['temperature'].set_text(self._format_temperature_summary())

        # Update radiation
        if 'radiation' in self.summary_labels:
            self.summary_labels['radiation'].set_text(self._format_radiation_summary())

        # Update atmosphere summary
        if 'atmosphere' in self.summary_labels:
            self.summary_labels['atmosphere'].set_text(self._format_atmosphere_summary())

        # Update description statuses
        if 'bio_status' in self.summary_labels:
            self.summary_labels['bio_status'].set_text(self._format_bio_status())

        if 'socio_status' in self.summary_labels:
            self.summary_labels['socio_status'].set_text(self._format_socio_status())

    def _refresh_flag_preview(self):
        """Refresh flag preview images."""
        # Clear previous flag images
        for img in self.summary_flag_images:
            img.kill()
        self.summary_flag_images = []

        if not self.race_config.flag_id or not self.summary_flag_panel:
            return

        shapes = self._asset_loader.load_flag_full(self.race_config.flag_id)
        if not shapes:
            return

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

    def _refresh_portrait_preview(self):
        """Refresh portrait preview image."""
        # Clear previous portrait image
        if self.summary_portrait_image:
            self.summary_portrait_image.kill()
            self.summary_portrait_image = None

        if not self.race_config.portrait_id or not self.summary_portrait_panel:
            return

        surf = self._asset_loader.load_portrait_full(self.race_config.portrait_id)
        if not surf:
            return

        preview_size = 256
        scaled = pygame.transform.smoothscale(surf, (preview_size, preview_size))
        self.summary_portrait_image = pygame_gui.elements.UIImage(
            relative_rect=pygame.Rect(10, 10, preview_size, preview_size),
            image_surface=scaled,
            manager=self.ui_manager,
            container=self.summary_portrait_panel
        )

    def _refresh_ship_preview(self):
        """Refresh ship preview images."""
        # Clear previous ship images
        for img in self.summary_ship_images:
            img.kill()
        self.summary_ship_images = []

        # Also clean up ship labels
        for lbl in self.summary_ship_labels:
            lbl.kill()
        self.summary_ship_labels = []

        if not self.race_config.theme_id or not self.summary_ship_panel:
            return

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

    def handle_button_click(self, ui_element) -> bool:
        """
        Handle button click events.

        Args:
            ui_element: The UI element that was clicked

        Returns:
            True if the event was handled, False otherwise
        """
        if ui_element == self.btn_load and self.on_load_race_callback:
            self.on_load_race_callback()
            return True
        return False
