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
from __future__ import annotations

import logging
import pygame
import pygame_gui
from typing import Dict, List, Optional, Callable, TYPE_CHECKING

from game.core.string_utils import display_name
from game.strategy.data.habitability_factors import (
    iter_gas_factors,
    iter_scalar_factors,
)
from game.ui.assets import get_default_ship_theme_manager
from game.ui.widgets.preference_row import PreferenceRow

logger = logging.getLogger(__name__)
from game.ui.utils import create_section_header

if TYPE_CHECKING:
    from game.strategy.data.race_config import RaceConfig
    from game.ui.screens.race_asset_loader import RaceAssetLoader


# FEAT-14: human-readable labels for the 7 RaceConfig aptitudes. Keys match
# the `aptitude_<key>` field-name suffix on `RaceConfig`. Order = display
# order on the Summary tab.
_APTITUDE_DISPLAY: tuple[tuple[str, str], ...] = (
    ("strength", "Strength"),
    ("intelligence", "Intelligence"),
    ("constitution", "Constitution"),
    ("dexterity", "Dexterity"),
    ("tolerance_other_species", "Tolerance (other species)"),
    ("cooperation", "Cooperation"),
    ("conflict_tolerance", "Conflict Tolerance"),
)


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
        on_load_race_callback: Optional[Callable[[], None]] = None,
        on_randomize_all_callback: Optional[Callable[[], None]] = None,
    ):
        """
        Create summary panel content.

        Args:
            panel: Parent UIPanel to add controls to
            manager: pygame_gui UIManager
            race_config: RaceConfig to display values from
            asset_loader: RaceAssetLoader for loading flag/portrait images
            on_load_race_callback: Optional callback for Load Race button
            on_randomize_all_callback: Optional callback for the master
                "Randomize All" button (FEAT-12).
        """
        self.panel = panel
        self.ui_manager = manager
        self.race_config = race_config
        self._asset_loader = asset_loader
        self.on_load_race_callback = on_load_race_callback
        self.on_randomize_all_callback = on_randomize_all_callback

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

        # FEAT-14: column-3 dynamic content. The factor rows + aptitude rows
        # are rebuilt on every refresh() because (a) the gas list filters by
        # setpoint > 0 (which can change), and (b) iterating the registry
        # directly is the cleanest data-driven path.
        self._env_scroll_container: Optional[pygame_gui.elements.UIScrollingContainer] = None
        self._dynamic_env_labels: List[pygame_gui.elements.UILabel] = []

        # Load Race button
        self.btn_load: Optional[pygame_gui.elements.UIButton] = None
        # FEAT-12: master "Randomize All" button.
        self.btn_randomize_all: Optional[pygame_gui.elements.UIButton] = None

        self._create_content()

    def _create_content(self) -> None:
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
        # FEAT-12: master Randomize All button — left of Load Saved Species.
        self.btn_randomize_all = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(panel_width - 370, y, 180, 40),
            text="Randomize All",
            manager=self.ui_manager,
            container=self.panel,
            tool_tip_text=(
                "Roll a complete species — identity, visuals, ships, "
                "environment, and aptitudes — within the 100-point budget."
            ),
        )
        y += 55

        # FEAT-23: two-column layout — left ⅓ stacks Identity/Flag/Portrait,
        # right ⅔ holds the FACTOR_REGISTRY scroll container.
        left_col_width = panel_width // 3 - 15
        right_col_width = panel_width - left_col_width - 30
        col1_x = 10
        col2_x = col1_x + left_col_width + 15

        # Left column: Identity → Flag → Portrait (stacked).
        left_col_bottom = self._create_left_column_content(col1_x, y, left_col_width)

        # Right column: FACTOR_REGISTRY scroll container, top-aligned with
        # left column, bottom-aligned with the portrait.
        right_col_height = left_col_bottom - y
        self._create_environment_column(col2_x, y, right_col_width, right_col_height)

        # Ship Theme label strip + Ship preview panel below both columns.
        ship_preview_width = panel_width - 20
        ship_preview_height = 200
        theme_strip_height = 30
        theme_strip_y = left_col_bottom + 20
        ship_panel_y = theme_strip_y + theme_strip_height + 5

        self._create_ship_theme_strip(10, theme_strip_y, ship_preview_width, theme_strip_height)

        self.summary_ship_panel = pygame_gui.elements.UIPanel(
            relative_rect=pygame.Rect(10, ship_panel_y, ship_preview_width, ship_preview_height),
            manager=self.ui_manager,
            container=self.panel,
            object_id="#summary_preview"
        )

    def _create_left_column_content(self, x: int, y: int, col_width: int) -> int:
        """Create the left column (FEAT-23): Identity → Flag → Portrait, stacked.

        Returns the y-coordinate of the column's bottom edge so the right
        column's scroll container can match its height.
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

        # Flag preview
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

        flag_bottom = y + 170 + flag_preview_size

        # FEAT-23: Portrait now lives at the bottom of the left column.
        portrait_header_y = flag_bottom + 10
        self.summary_labels['portrait_header'] = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(x, portrait_header_y, col_width, 30),
            text="Portrait:",
            manager=self.ui_manager,
            container=self.panel
        )

        portrait_preview_size = 280
        portrait_y = portrait_header_y + 35
        self.summary_portrait_panel = pygame_gui.elements.UIPanel(
            relative_rect=pygame.Rect(x, portrait_y, portrait_preview_size, portrait_preview_size),
            manager=self.ui_manager,
            container=self.panel,
            object_id="#summary_preview"
        )

        return portrait_y + portrait_preview_size

    def _create_environment_column(self, x: int, y: int, col_width: int, col_height: int) -> None:
        """Create the right column (FEAT-23): FACTOR_REGISTRY scroll container.

        FEAT-14: A `UIScrollingContainer` whose content is rebuilt by
        `refresh()` from `FACTOR_REGISTRY` + the 7 aptitudes — adding a
        factor to the registry surfaces a row automatically with no change
        to this file. The constructor only allocates the container;
        `refresh()` populates everything inside.

        FEAT-23: width is now ⅔ of the panel and height matches the left
        column's bottom — long lines no longer wrap.
        """
        self._env_scroll_container = pygame_gui.elements.UIScrollingContainer(
            relative_rect=pygame.Rect(x, y, col_width, col_height),
            manager=self.ui_manager,
            container=self.panel,
        )

    def _create_ship_theme_strip(self, x: int, y: int, full_width: int, height: int) -> None:
        """Create the FEAT-23 Ship Theme label strip above the ship preview.

        Preserves the FEAT-12/14 contract: `summary_labels['theme_header']`
        and `summary_labels['theme_value']` keys still exist, so `refresh()`
        continues to update them without modification.
        """
        label_width = full_width // 4
        self.summary_labels['theme_header'] = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(x, y, label_width, height),
            text="Ship Theme:",
            manager=self.ui_manager,
            container=self.panel
        )
        self.summary_labels['theme_value'] = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(x + label_width, y, full_width - label_width, height),
            text="[Click Ships tab to set]",
            manager=self.ui_manager,
            container=self.panel
        )

    # =========================================================================
    # Formatting Methods
    # =========================================================================

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

    def _format_budget_summary(self) -> str:
        """Format point budget status."""
        from game.strategy.data.race_point_budget import RacePointBudget
        budget = RacePointBudget()
        total_cost = budget.calculate_total_cost(self.race_config)
        total = budget.total_budget
        return f"Budget: {total_cost}/{total} used"

    # =========================================================================
    # Refresh Summary
    # =========================================================================

    def refresh(self) -> None:
        """Refresh summary panel with current race_config data.

        FEAT-14: Column-3 environment + aptitudes + descriptions section is
        now rebuilt from `FACTOR_REGISTRY` + RaceConfig.aptitudes via
        `_rebuild_env_scroll_content()` — no per-factor branches here.
        Columns 1 and 2 (identity, theme, previews) keep their static-label
        + set_text refresh path.
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

        # FEAT-14: rebuild the entire column-3 scrollable content from the
        # registry + aptitudes. Replaces the per-factor set_text path.
        self._rebuild_env_scroll_content()

    # ------------------------------------------------------------------ #
    # FEAT-14: registry-driven column-3 content                            #
    # ------------------------------------------------------------------ #

    def _rebuild_env_scroll_content(self) -> None:
        """Kill any previously rendered factor / aptitude / description rows
        and rebuild them inside `self._env_scroll_container` from the
        current race_config.

        Layout:
            [Environment]
            Homeworld: ...
            <one row per scalar factor>          (iter_scalar_factors)
            <one row per gas factor with setpoint > 0>  (iter_gas_factors filtered)

            [Aptitudes]
            Budget: ...
            <one row per aptitude>               (_APTITUDE_DISPLAY × 7)
            Base Happiness: ...
            Base Reproduction Rate: ...

            [Descriptions]
            Biological: ...
            Sociological: ...

        Adding a factor to FACTOR_REGISTRY surfaces a row here automatically
        (PROJ-283/293 contract). The setpoint ± tolerance values are
        formatted via `PreferenceRow.format_value`, the canonical PROJ-293
        display contract.
        """
        # Kill old labels (refresh may be called many times during a session).
        for label in self._dynamic_env_labels:
            label.kill()
        self._dynamic_env_labels = []

        if self._env_scroll_container is None:
            return

        container = self._env_scroll_container
        # Inner width: leave room for the vertical scrollbar.
        inner_width = max(200, container.get_relative_rect().width - 30)
        row_height = 22
        section_gap = 8
        y = 4

        y = self._render_section_header("Environment", y, inner_width, row_height)
        y = self._render_env_row(
            self._format_homeworld_summary(), y, inner_width, row_height,
        )
        y = self._render_factor_rows(y, inner_width, row_height)
        y += section_gap

        y = self._render_section_header("Aptitudes", y, inner_width, row_height)
        y = self._render_env_row(
            self._format_budget_summary(), y, inner_width, row_height,
        )
        y = self._render_aptitude_rows(y, inner_width, row_height)
        y += section_gap

        y = self._render_section_header("Descriptions", y, inner_width, row_height)
        y = self._render_env_row(
            self._format_bio_status(), y, inner_width, row_height,
        )
        y = self._render_env_row(
            self._format_socio_status(), y, inner_width, row_height,
        )

        # Tell the scroll container how tall its inner content is so the
        # scrollbar appears when we overflow the visible region.
        container.set_scrollable_area_dimensions((inner_width, y + 4))

    def _render_section_header(
        self, text: str, y: int, width: int, row_height: int,
    ) -> int:
        """Render a section header inside the scroll container. Returns the
        next y position."""
        label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(0, y, width, row_height + 4),
            text=text,
            manager=self.ui_manager,
            container=self._env_scroll_container,
            object_id="#section_header",
        )
        self._dynamic_env_labels.append(label)
        return y + row_height + 4

    def _render_env_row(
        self, text: str, y: int, width: int, row_height: int,
    ) -> int:
        """Render a single text row inside the scroll container. Returns the
        next y position."""
        label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(0, y, width, row_height),
            text=text,
            manager=self.ui_manager,
            container=self._env_scroll_container,
        )
        self._dynamic_env_labels.append(label)
        return y + row_height

    def _render_factor_rows(self, y: int, width: int, row_height: int) -> int:
        """Render one row per FACTOR_REGISTRY entry (scalars unconditionally;
        gases filtered by setpoint > 0). Reuses `PreferenceRow.format_value`
        for the PROJ-293 display contract."""
        for factor in iter_scalar_factors():
            pref = self.race_config.preferences.get(factor.id)
            if pref is None:
                # Defensive — registry & race_config should stay in sync, but
                # if a save predates a registry addition we render "--".
                text = f"{factor.display_name}: --"
            else:
                setpoint_text = PreferenceRow.format_value(factor, pref.setpoint)
                tolerance_text = PreferenceRow.format_value(factor, pref.tolerance)
                text = f"{factor.display_name}: {setpoint_text} ± {tolerance_text}"
            y = self._render_env_row(text, y, width, row_height)

        for factor in iter_gas_factors():
            pref = self.race_config.preferences.get(factor.id)
            if pref is None or pref.setpoint <= 0:
                # Skip gases the race doesn't care about — matches the legacy
                # atmosphere-summary filter.
                continue
            setpoint_text = PreferenceRow.format_value(factor, pref.setpoint)
            tolerance_text = PreferenceRow.format_value(factor, pref.tolerance)
            text = f"{factor.display_name}: {setpoint_text} ± {tolerance_text}"
            y = self._render_env_row(text, y, width, row_height)

        return y

    def _render_aptitude_rows(self, y: int, width: int, row_height: int) -> int:
        """Render one row per aptitude + the two PROJ-283 derived seeds
        (`base_happiness`, `base_reproduction_rate`)."""
        rc = self.race_config
        for key, label in _APTITUDE_DISPLAY:
            value = getattr(rc, f"aptitude_{key}")
            y = self._render_env_row(f"{label}: {value}", y, width, row_height)
        # Derived seeds — kept on the Summary tab for completeness.
        y = self._render_env_row(
            f"Base Happiness: {rc.base_happiness:.2f}", y, width, row_height,
        )
        y = self._render_env_row(
            f"Base Reproduction Rate: {rc.base_reproduction_rate * 100:.1f}%",
            y, width, row_height,
        )
        return y

    def _refresh_flag_preview(self) -> None:
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

    def _refresh_portrait_preview(self) -> None:
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

    def _refresh_ship_preview(self) -> None:
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
