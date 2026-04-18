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
import logging
import pygame
import pygame_gui
from typing import Dict, List, Optional, Callable, TYPE_CHECKING

from game.core.string_utils import display_name
from game.ui.assets import get_default_ship_theme_manager

logger = logging.getLogger(__name__)
from game.ui.utils import create_section_header

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
            text="Species Configuration Summary",
            manager=self.ui_manager,
            container=self.panel,
            object_id="#summary_title"
        )

        # Load Race button (right side of title)
        self.btn_load = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(panel_width - 180, y, 180, 40),
            text="Load Saved Species",
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
        """Create column 1: Identity and Flag.

        PROJ-66 Phase 6: Updated to show faction name and identity fields.
        """
        # Faction Name (prominent at top)
        self.summary_labels['faction_header'] = create_section_header(
            "Faction:", y, col_width, self.ui_manager, self.panel, x=x
        )
        self.summary_labels['faction_value'] = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(x, y + 25, col_width, 25),
            text="[Click Identity tab to set]",
            manager=self.ui_manager,
            container=self.panel
        )

        # Race Name + Government
        self.summary_labels['race_value'] = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(x, y + 50, col_width, 22),
            text="Species: --",
            manager=self.ui_manager,
            container=self.panel
        )
        self.summary_labels['gov_value'] = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(x, y + 72, col_width, 22),
            text="Government: --",
            manager=self.ui_manager,
            container=self.panel
        )

        # Physical + Society Type
        self.summary_labels['physical_value'] = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(x, y + 94, col_width, 22),
            text="Physical: --",
            manager=self.ui_manager,
            container=self.panel
        )
        self.summary_labels['society_value'] = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(x, y + 116, col_width, 22),
            text="Society: --",
            manager=self.ui_manager,
            container=self.panel
        )

        # Flag preview (smaller to make room)
        self.summary_labels['flag_header'] = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(x, y + 145, col_width, 25),
            text="Flag:",
            manager=self.ui_manager,
            container=self.panel
        )

        flag_preview_size = 220
        self.summary_flag_panel = pygame_gui.elements.UIPanel(
            relative_rect=pygame.Rect(x, y + 170, col_width, flag_preview_size),
            manager=self.ui_manager,
            container=self.panel,
            object_id="#summary_preview"
        )

        return y + 170 + flag_preview_size

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
        """Create column 3: Environment, Aptitudes, and Descriptions.

        PROJ-66 Phase 6: Added homeworld, water, aptitudes, and budget display.
        """
        # Environment header
        create_section_header("Environment:", y, col_width, self.ui_manager, self.panel, x=x)

        env_y = y + 25

        # Homeworld Type (NEW)
        self.summary_labels['homeworld'] = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(x, env_y, col_width, 22),
            text="Homeworld: Custom",
            manager=self.ui_manager,
            container=self.panel
        )
        env_y += 22

        # Gravity
        self.summary_labels['gravity'] = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(x, env_y, col_width, 22),
            text="Gravity: 1.0g +/- 0.30",
            manager=self.ui_manager,
            container=self.panel
        )
        env_y += 22

        # Temperature
        self.summary_labels['temperature'] = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(x, env_y, col_width, 22),
            text="Temperature: 293K +/- 50",
            manager=self.ui_manager,
            container=self.panel
        )
        env_y += 22

        # Water (NEW)
        self.summary_labels['water'] = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(x, env_y, col_width, 22),
            text="Water: 50% +/- 30",
            manager=self.ui_manager,
            container=self.panel
        )
        env_y += 22

        # Radiation
        self.summary_labels['radiation'] = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(x, env_y, col_width, 22),
            text="Radiation: 0",
            manager=self.ui_manager,
            container=self.panel
        )
        env_y += 28

        # Aptitudes section (NEW)
        create_section_header("Aptitudes:", env_y, col_width, self.ui_manager, self.panel, x=x)
        env_y += 25

        # Budget status (NEW)
        self.summary_labels['budget'] = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(x, env_y, col_width, 22),
            text="Budget: 0/100 used",
            manager=self.ui_manager,
            container=self.panel
        )
        env_y += 22

        # Aptitude summary (compact format)
        self.summary_labels['aptitudes'] = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(x, env_y, col_width, 66),
            text="STR:5 INT:5 CON:5\nDEX:5 TOL:5 COO:5\nHAP:5 POP:5 CFT:5",
            manager=self.ui_manager,
            container=self.panel
        )
        env_y += 72

        # Descriptions summary
        create_section_header("Descriptions:", env_y, col_width, self.ui_manager, self.panel, x=x)
        env_y += 25

        self.summary_labels['bio_status'] = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(x, env_y, col_width, 22),
            text="Biological: 0 chars",
            manager=self.ui_manager,
            container=self.panel
        )
        env_y += 22

        self.summary_labels['socio_status'] = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(x, env_y, col_width, 22),
            text="Sociological: 0 chars",
            manager=self.ui_manager,
            container=self.panel
        )

    # =========================================================================
    # Formatting Methods
    # =========================================================================

    # PROJ-283 Phase 4: env summaries now read from `race_config.preferences`
    # (the legacy gravity_ideal/_tolerance/etc. fields are gone).
    # These formatters present a compact label until the Phase 5 UI rebuild
    # replaces this whole panel.

    def _format_gravity_summary(self) -> str:
        """Format gravity summary string (m/s² → g for display)."""
        pref = self.race_config.preferences.get("gravity")
        if pref is None:
            return "Gravity: --"
        ideal_g = pref.setpoint / 9.81
        tol_g = pref.tolerance / 9.81
        return f"Gravity: {ideal_g:.1f}g +/- {tol_g:.2f}"

    def _format_temperature_summary(self) -> str:
        """Format temperature summary string."""
        pref = self.race_config.preferences.get("temperature")
        if pref is None:
            return "Temperature: --"
        return f"Temperature: {pref.setpoint:.0f}K +/- {pref.tolerance:.0f}"

    def _format_radiation_summary(self) -> str:
        """Format radiation summary string."""
        pref = self.race_config.preferences.get("radiation")
        if pref is None:
            return "Radiation: --"
        return f"Radiation: tol {pref.tolerance:+.0f}"

    def _format_atmosphere_summary(self) -> str:
        """Format atmosphere summary string. Lists gas factors with
        non-zero setpoints (i.e., gases the race prefers to breathe)."""
        atmo_parts = []
        for fid, pref in self.race_config.preferences.items():
            if not fid.startswith("gas.") or pref.setpoint <= 0:
                continue
            formula = fid.split(".", 1)[1]
            kpa = pref.setpoint / 1000.0
            atmo_parts.append(f"{formula}: {kpa:.1f} kPa")
        if atmo_parts:
            atmo_text = ", ".join(atmo_parts[:4])
            if len(atmo_parts) > 4:
                atmo_text += "..."
        else:
            atmo_text = "All neutral"
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

    def _format_faction_summary(self) -> str:
        """Format faction name for display.

        PROJ-66 Phase 6: New formatter for identity fields.
        """
        if self.race_config.faction_name:
            return self.race_config.faction_name
        return "[Click Identity tab to set]"

    def _format_race_summary(self) -> str:
        """Format race name display."""
        race_name = self.race_config.race_name or self.race_config.name or "--"
        return f"Species: {race_name}"

    def _format_government_summary(self) -> str:
        """Format government type and organization."""
        parts = []
        if self.race_config.government_type:
            parts.append(self.race_config.government_type)
        if self.race_config.government_organization:
            parts.append(f"({self.race_config.government_organization})")
        if parts:
            return f"Government: {' '.join(parts)}"
        return "Government: --"

    def _format_physical_summary(self) -> str:
        """Format physical type."""
        if self.race_config.physical_type:
            return f"Physical: {self.race_config.physical_type}"
        return "Physical: --"

    def _format_society_summary(self) -> str:
        """Format society type."""
        if self.race_config.society_type:
            return f"Society: {self.race_config.society_type}"
        return "Society: --"

    def _format_homeworld_summary(self) -> str:
        """Format homeworld type."""
        if self.race_config.homeworld_type:
            # Convert preset ID (e.g. "CONTINENTAL") to display name (e.g. "Continental")
            hw_label = display_name(self.race_config.homeworld_type)
            return f"Homeworld: {hw_label}"
        return "Homeworld: Custom"

    def _format_water_summary(self) -> str:
        """Format water preferences (PROJ-283: read from preferences['water'])."""
        pref = self.race_config.preferences.get("water")
        if pref is None:
            return "Water: --"
        return f"Water: {pref.setpoint*100:.0f}% +/- {pref.tolerance*100:.0f}"

    def _format_budget_summary(self) -> str:
        """Format point budget status."""
        from game.strategy.data.race_point_budget import RacePointBudget
        budget = RacePointBudget()
        total_cost = budget.calculate_total_cost(self.race_config)
        total = budget.total_budget
        return f"Budget: {total_cost}/{total} used"

    def _format_aptitudes_summary(self) -> str:
        """Format aptitude values in compact 3-line format."""
        rc = self.race_config
        line1 = f"STR:{rc.aptitude_strength} INT:{rc.aptitude_intelligence} CON:{rc.aptitude_constitution}"
        line2 = f"DEX:{rc.aptitude_dexterity} TOL:{rc.aptitude_tolerance_other_species} COO:{rc.aptitude_cooperation}"
        # PROJ-283 Phase 4: happiness + population_growth aptitudes deleted;
        # display the new derived/seed fields instead.
        line3 = (
            f"HAP:{rc.base_happiness:.2f} REPRO:{rc.base_reproduction_rate*100:.1f}% "
            f"CFT:{rc.aptitude_conflict_tolerance}"
        )
        return f"{line1}\n{line2}\n{line3}"

    # =========================================================================
    # Refresh Summary
    # =========================================================================

    def refresh(self):
        """Refresh summary panel with current race_config data.

        PROJ-66 Phase 6: Added identity, homeworld, water, aptitudes, budget.
        """
        logger.debug("Refreshing race summary panel")

        # PROJ-66: Update identity fields
        if 'faction_value' in self.summary_labels:
            self.summary_labels['faction_value'].set_text(self._format_faction_summary())

        if 'race_value' in self.summary_labels:
            self.summary_labels['race_value'].set_text(self._format_race_summary())

        if 'gov_value' in self.summary_labels:
            self.summary_labels['gov_value'].set_text(self._format_government_summary())

        if 'physical_value' in self.summary_labels:
            self.summary_labels['physical_value'].set_text(self._format_physical_summary())

        if 'society_value' in self.summary_labels:
            self.summary_labels['society_value'].set_text(self._format_society_summary())

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

        # PROJ-66: Update homeworld
        if 'homeworld' in self.summary_labels:
            self.summary_labels['homeworld'].set_text(self._format_homeworld_summary())

        # Update gravity
        if 'gravity' in self.summary_labels:
            self.summary_labels['gravity'].set_text(self._format_gravity_summary())

        # Update temperature
        if 'temperature' in self.summary_labels:
            self.summary_labels['temperature'].set_text(self._format_temperature_summary())

        # PROJ-66: Update water
        if 'water' in self.summary_labels:
            self.summary_labels['water'].set_text(self._format_water_summary())

        # Update radiation
        if 'radiation' in self.summary_labels:
            self.summary_labels['radiation'].set_text(self._format_radiation_summary())

        # PROJ-66: Update aptitudes and budget
        if 'budget' in self.summary_labels:
            self.summary_labels['budget'].set_text(self._format_budget_summary())

        if 'aptitudes' in self.summary_labels:
            self.summary_labels['aptitudes'].set_text(self._format_aptitudes_summary())

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

        theme_manager = get_default_ship_theme_manager()
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
            skin_surf = theme_manager.load_image(self.race_config.theme_id, ship_class)
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
