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
import pygame
import pygame_gui
from typing import Callable, Optional, List, Tuple

import logging

logger = logging.getLogger(__name__)
from game.core.paths import Paths
from game.strategy.data.race_config import RaceConfig
from game.strategy.systems.race_library import RaceLibrary
from game.strategy.systems.race_randomizer import RaceRandomizer
from game.ui.assets import get_default_ship_theme_manager

# PROJ-12 Phase 4: Import extracted components
from game.ui.screens.race_browser_dialog import RaceBrowserDialog
from game.ui.screens.race_validator import RaceValidator
from game.ui.screens.race_asset_loader import RaceAssetLoader
from game.ui.panels.race_environment_panel import RaceEnvironmentPanel
from game.ui.panels.race_description_panel import RaceDescriptionPanel
from game.ui.panels.race_flag_gallery import RaceFlagGallery
from game.ui.panels.race_portrait_gallery import RacePortraitGallery
from game.ui.panels.race_theme_gallery import RaceThemeGallery
from game.ui.panels.race_summary_panel import RaceSummaryPanel
from game.ui.panels.race_identity_panel import RaceIdentityPanel
from game.ui.panels.race_aptitudes_panel import RaceAptitudesPanel


class RaceSetupScreen(pygame_gui.elements.UIWindow):
    """Tab-based window for race configuration."""

    # Tab constants (Summary is now first/landing page)
    # PROJ-66 Phase 6: Expanded from 5 to 7 tabs
    TAB_SUMMARY = 0
    TAB_IDENTITY = 1      # NEW - Race identity fields
    TAB_VISUALS = 2       # was 1
    TAB_SHIPS = 3         # was 2
    TAB_ENVIRONMENT = 4   # was 3
    TAB_APTITUDES = 5     # NEW - Point-buy aptitudes
    TAB_DESCRIPTIONS = 6  # was 4

    TAB_NAMES = [
        "Summary",
        "Identity",
        "Visuals",
        "Ships",
        "Environment",
        "Aptitudes",
        "Descriptions"
    ]

    # Thumbnail sizes (larger for 2560x1600 displays)
    # FLAG_THUMB_SIZE moved to RaceFlagGallery
    # PORTRAIT_THUMB_SIZE moved to RacePortraitGallery
    # SHIP_PREVIEW_SIZE defined locally in _refresh_ship_preview (160px)

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
            window_display_title="Species Setup",
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

        # FEAT-05: Save/Update dialog elements (created on demand)
        self._save_update_dialog = None
        self._btn_overwrite = None
        self._btn_save_new = None
        self._btn_save_cancel = None

        # Current tab (start on Summary)
        self.current_step = self.TAB_SUMMARY

        # Race library for save/load
        self.race_library = RaceLibrary()

        # PROJ-12 Phase 4: Use extracted asset loader
        self._asset_loader = RaceAssetLoader()

        # PROJ-12 Phase 4: Extracted panels
        # PROJ-44 Phase 7: Added RaceSummaryPanel
        # PROJ-66 Phase 6: Added RaceIdentityPanel, RaceAptitudesPanel
        self._summary_panel = None
        self._identity_panel = None
        self._environment_panel = None
        self._aptitudes_panel = None
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

        # PROJ-199: Lazy init elimination - ship preview elements
        self._ship_preview_elements: list = []
        self.ship_preview_scroll = None

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
        """Create panels for each tab.

        PROJ-66 Phase 6: Expanded from 5 to 7 panels (added Identity and Aptitudes).
        """
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

        # Panel 1: Identity (NEW - race name, government, faction)
        panel_identity = pygame_gui.elements.UIPanel(
            relative_rect=panel_rect,
            manager=self.ui_manager,
            container=container,
            object_id="#panel_identity"
        )
        self._create_identity_panel_content(panel_identity)
        self.step_panels.append(panel_identity)

        # Panel 2: Visuals (Flags and Portraits only - was index 1)
        panel_visuals = pygame_gui.elements.UIPanel(
            relative_rect=panel_rect,
            manager=self.ui_manager,
            container=container,
            object_id="#panel_visuals"
        )
        self._create_visuals_panel_content(panel_visuals)
        self.step_panels.append(panel_visuals)

        # Panel 3: Ships (dedicated ship theme selection - was index 2)
        panel_ships = pygame_gui.elements.UIPanel(
            relative_rect=panel_rect,
            manager=self.ui_manager,
            container=container,
            object_id="#panel_ships"
        )
        self._create_ships_panel_content(panel_ships)
        self.step_panels.append(panel_ships)

        # Panel 4: Environment Preferences (was index 3)
        panel_environment = pygame_gui.elements.UIPanel(
            relative_rect=panel_rect,
            manager=self.ui_manager,
            container=container,
            object_id="#panel_environment"
        )
        self._create_environment_panel_content(panel_environment)
        self.step_panels.append(panel_environment)

        # Panel 5: Aptitudes (NEW - point-buy aptitude system)
        panel_aptitudes = pygame_gui.elements.UIPanel(
            relative_rect=panel_rect,
            manager=self.ui_manager,
            container=container,
            object_id="#panel_aptitudes"
        )
        self._create_aptitudes_panel_content(panel_aptitudes)
        self.step_panels.append(panel_aptitudes)

        # Panel 6: Descriptions (was index 4)
        panel_descriptions = pygame_gui.elements.UIPanel(
            relative_rect=panel_rect,
            manager=self.ui_manager,
            container=container,
            object_id="#panel_descriptions"
        )
        self._create_descriptions_panel_content(panel_descriptions)
        self.step_panels.append(panel_descriptions)


    # =========================================================================
    # Identity Panel (NEW - PROJ-66 Phase 6)
    # =========================================================================

    def _create_identity_panel_content(self, panel):
        """Create content for Identity tab using RaceIdentityPanel.

        PROJ-66 Phase 6: New panel for race identity configuration.
        """
        self._identity_panel = RaceIdentityPanel(
            panel=panel,
            manager=self.ui_manager,
            race_config=self.race_config
        )

    # =========================================================================
    # Visuals Panel (Flags and Portraits)
    # =========================================================================

    def _create_visuals_panel_content(self, panel):
        """Create content for Visuals tab: Flags and Portraits.

        PROJ-66 Phase 6: Race name moved to Identity tab.
        """
        panel_width = panel.get_relative_rect().width - 20
        panel_height = panel.get_relative_rect().height
        y = 10

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
        logger.debug(f"Theme selected: {theme_id}")

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

        # PROJ-96: Side-by-side layout - theme list on left, preview grid on right
        THEME_LIST_WIDTH = 200
        CONTENT_GAP = 10
        content_y = y
        content_height = panel_height - content_y - 10

        # Theme gallery (vertical scrolling list on left)
        self._theme_gallery = RaceThemeGallery(
            panel=panel,
            manager=self.ui_manager,
            race_config=self.race_config,
            x=10,
            y=content_y,
            width=THEME_LIST_WIDTH,
            height=content_height,
            on_select_callback=self._on_theme_selected
        )

        # Ship preview area (scrolling container on right)
        preview_x = 10 + THEME_LIST_WIDTH + CONTENT_GAP
        preview_width = panel_width - THEME_LIST_WIDTH - CONTENT_GAP
        self.ship_preview_scroll = pygame_gui.elements.UIScrollingContainer(
            relative_rect=pygame.Rect(preview_x, content_y, preview_width, content_height),
            manager=self.ui_manager,
            container=panel,
            allow_scroll_x=False,
            allow_scroll_y=True
        )

        # Note: theme selection is handled by RaceThemeGallery via on_select_callback

    def _refresh_ship_preview(self, theme_id: str):
        """Refresh the ship preview area with ships from the selected theme."""
        logger.debug(f"_refresh_ship_preview called with theme_id: {theme_id}")

        # Clear existing ship previews
        for elem in self._ship_preview_elements:
            elem.kill()
        self._ship_preview_elements = []

        if self.ship_preview_scroll is None:
            logger.debug("ship_preview_scroll not found, returning")
            return

        # Use the scrolling container directly for adding elements
        container = self.ship_preview_scroll
        container_width = container.get_relative_rect().width - 30
        logger.debug(f"Container width: {container_width}")

        # Representative ship classes to display (3x3 grid = 9 ships)
        ship_classes = [
            "Fighter (Medium)", "Satellite (Medium)", "Escort",
            "Frigate", "Cruiser", "Heavy Cruiser",
            "Battleship", "Dreadnought", "Superdreadnought",
        ]

        theme_manager = get_default_ship_theme_manager()
        theme_manager.initialize()

        # Layout: 3 columns of ships, each showing top-down + portrait pair
        num_cols = 3
        portrait_size = 160  # Size for each image in the pair
        image_gap = 5  # Gap between top-down and portrait images
        col_width = container_width // num_cols
        row_height = portrait_size + 35  # label(25) + gap(5) + image + bottom_pad(5)
        row_spacing = 10

        # Calculate and set scrollable area BEFORE adding elements
        total_rows = (len(ship_classes) + num_cols - 1) // num_cols
        scroll_height = 10 + total_rows * (row_height + row_spacing) + 20
        self.ship_preview_scroll.set_scrollable_area_dimensions(
            (container_width, scroll_height)
        )

        y = 10

        for i, ship_class in enumerate(ship_classes):
            col = i % num_cols
            if col == 0 and i > 0:
                y += row_height + row_spacing

            x = 10 + col * col_width

            # Ship class label - centered above image pair
            label = pygame_gui.elements.UILabel(
                relative_rect=pygame.Rect(x, y, col_width - 10, 25),
                text=ship_class,
                manager=self.ui_manager,
                container=container
            )
            self._ship_preview_elements.append(label)

            # Get top-down (skin) image with smart scaling using visible bounding rect
            skin_surf = theme_manager.load_image(theme_id, ship_class)
            scaled_skin = None
            logger.debug(f"Ship {ship_class}: skin_surf={skin_surf is not None}")
            if skin_surf:
                img_width, img_height = skin_surf.get_size()
                metrics = theme_manager.get_image_metrics(theme_id, ship_class)

                if metrics and metrics.width > 0 and metrics.height > 0:
                    # Scale so visible portion fits portrait_size
                    scale_factor = portrait_size / max(metrics.width, metrics.height)
                    scale_factor = min(scale_factor, 3.0)  # Cap to prevent blowup
                else:
                    # Fallback to naive scaling
                    scale_factor = portrait_size / max(img_width, img_height)

                new_w = max(1, int(img_width * scale_factor))
                new_h = max(1, int(img_height * scale_factor))
                scaled_skin = pygame.transform.smoothscale(skin_surf, (new_w, new_h))

                # Crop to visible area if metrics available
                if metrics and metrics.width > 0 and metrics.height > 0:
                    crop_x = max(0, int(metrics.x * scale_factor))
                    crop_y = max(0, int(metrics.y * scale_factor))
                    crop_w = min(int(metrics.width * scale_factor), new_w - crop_x)
                    crop_h = min(int(metrics.height * scale_factor), new_h - crop_y)
                    if crop_w > 0 and crop_h > 0:
                        cropped = scaled_skin.subsurface(pygame.Rect(crop_x, crop_y, crop_w, crop_h))
                        scaled_skin = cropped

            # Get portrait image using ShipThemeManager API
            portrait_surf = theme_manager.get_portrait_image(theme_id, ship_class)
            scaled_portrait = None
            logger.debug(f"Ship {ship_class}: portrait_surf={portrait_surf is not None}")
            if portrait_surf:
                p_w, p_h = portrait_surf.get_size()
                p_scale = min(portrait_size / p_w, portrait_size / p_h)
                scaled_portrait = pygame.transform.smoothscale(
                    portrait_surf, (int(p_w * p_scale), int(p_h * p_scale))
                )

            # Calculate centered positions for image pair
            topdown_w = scaled_skin.get_width() if scaled_skin else 0
            topdown_h = scaled_skin.get_height() if scaled_skin else 0
            portrait_w = scaled_portrait.get_width() if scaled_portrait else 0
            pair_width = topdown_w + image_gap + portrait_w
            pair_x = x + (col_width - pair_width) // 2

            # Display top-down view
            if scaled_skin:
                img = pygame_gui.elements.UIImage(
                    relative_rect=pygame.Rect(pair_x, y + 30, topdown_w, topdown_h),
                    image_surface=scaled_skin,
                    manager=self.ui_manager,
                    container=container
                )
                self._ship_preview_elements.append(img)

            # Display portrait
            if scaled_portrait:
                portrait_x = pair_x + topdown_w + image_gap
                img = pygame_gui.elements.UIImage(
                    relative_rect=pygame.Rect(portrait_x, y + 30, portrait_w, portrait_size),
                    image_surface=scaled_portrait,
                    manager=self.ui_manager,
                    container=container
                )
                self._ship_preview_elements.append(img)

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

    # =========================================================================
    # Aptitudes Panel (NEW - PROJ-66 Phase 6)
    # =========================================================================

    def _create_aptitudes_panel_content(self, panel):
        """Create content for Aptitudes tab using RaceAptitudesPanel.

        PROJ-66 Phase 6: New panel for point-buy aptitude configuration.
        """
        self._aptitudes_panel = RaceAptitudesPanel(
            panel=panel,
            manager=self.ui_manager,
            race_config=self.race_config
        )

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
    # Summary Panel (Landing Page) - PROJ-44 Phase 7: Delegates to RaceSummaryPanel
    # =========================================================================

    def _create_summary_panel_content(self, panel):
        """Create content for Summary tab using extracted RaceSummaryPanel."""
        self._summary_panel = RaceSummaryPanel(
            panel=panel,
            manager=self.ui_manager,
            race_config=self.race_config,
            asset_loader=self._asset_loader,
            on_load_race_callback=self._on_load_race
        )
        # Keep btn_load reference for event handling
        self.btn_load = self._summary_panel.btn_load

    def _refresh_summary(self):
        """Refresh summary panel with current race_config data.

        PROJ-44 Phase 7: Delegates to RaceSummaryPanel.
        """
        logger.debug("Refreshing race summary")

        # Update text descriptions from text boxes before showing summary
        self._update_descriptions_from_text()

        # Delegate to RaceSummaryPanel
        if self._summary_panel:
            self._summary_panel.refresh()

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

        # Generate Random button (beside Cancel, visible on Identity/Visuals/Ships tabs)
        randomize_width = 160
        self.btn_randomize = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(10 + button_width + 10, button_y, randomize_width, button_height),
            text="Generate Random",
            manager=self.ui_manager,
            container=container
        )
        self.btn_randomize.hide()

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

        PROJ-66 Phase 6: Expanded to handle 7 tabs (0-6).

        Args:
            step_num: Tab index to show (0-6)
        """
        # Clamp step number
        step_num = max(0, min(step_num, len(self.step_panels) - 1))
        self.current_step = step_num

        logger.debug(f"Showing race setup tab {step_num}: {self.TAB_NAMES[step_num]}")

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
        elif step_num == self.TAB_APTITUDES:
            # PROJ-66: Refresh aptitudes budget when showing tab
            if self._aptitudes_panel:
                self._aptitudes_panel.update_budget_display()

    def _update_navigation_buttons(self):
        """Update navigation button visibility based on current tab."""
        # Save button is only shown on Summary tab
        if self.current_step == self.TAB_SUMMARY:
            self.btn_save.show()
        else:
            self.btn_save.hide()

        # Generate Random button shown on Identity, Visuals, and Ships tabs
        if self.current_step in (self.TAB_IDENTITY, self.TAB_VISUALS, self.TAB_SHIPS):
            self.btn_randomize.show()
        else:
            self.btn_randomize.hide()

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
        PROJ-66 Phase 6: Added identity sync and budget check.

        Returns:
            Tuple of (is_valid, error_message)
        """
        # PROJ-66: Sync identity panel values to race_config
        if self._identity_panel:
            self._identity_panel.update_config()
            # Use race_name as the primary name
            if self.race_config.race_name:
                self.race_config.name = self.race_config.race_name

        # PROJ-66: Sync aptitudes panel values to race_config
        if self._aptitudes_panel:
            self._aptitudes_panel.update_config()

        # PROJ-66: Check point budget
        if self._aptitudes_panel:
            from game.strategy.data.race_point_budget import RacePointBudget
            budget = RacePointBudget()
            if not budget.is_within_budget(self.race_config):
                remaining = budget.get_remaining_points(self.race_config)
                return False, f"Over budget by {-remaining} points (Aptitudes tab)"

        # PROJ-12: Use extracted RaceValidator
        validator = RaceValidator()
        result = validator.validate(self.race_config)
        return result.is_valid, result.message

    def _on_tab_clicked(self, tab_index: int):
        """Handle tab button click."""
        self._show_step(tab_index)

    def _on_load_race(self):
        """Handle Load Race button click - open in-game race browser dialog."""
        logger.debug("Opening race browser dialog")

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
        logger.info(f"Loaded race: {loaded_config.name}")
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
        logger.debug("Race browser cancelled")

    def _populate_ui_from_config(self):
        """Populate all UI elements from the current race_config.

        PROJ-66 Phase 6: Added identity and aptitudes panels.
        BUG-81: Update panel race_config references before populating.
        """
        # Update all panel race_config references to current config (BUG-81)
        for panel in [self._identity_panel, self._flag_gallery,
                      self._portrait_gallery, self._theme_gallery,
                      self._environment_panel, self._aptitudes_panel,
                      self._description_panel, self._summary_panel]:
            if panel is not None:
                panel.race_config = self.race_config

        # PROJ-66: Update identity panel (replaces old name_input)
        if self._identity_panel:
            self._identity_panel.set_from_config()

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

        # PROJ-66: Update aptitudes panel
        if self._aptitudes_panel:
            self._aptitudes_panel.set_from_config()

        # Update description text boxes (PROJ-12 Phase 4: Delegate to RaceDescriptionPanel)
        if self._description_panel:
            self._description_panel.set_from_config()

    def _on_randomize(self):
        """Handle Generate Random button click — dispatches by current tab."""
        if self.current_step == self.TAB_IDENTITY:
            self._randomize_identity()
        elif self.current_step == self.TAB_VISUALS:
            self._randomize_visuals()
        elif self.current_step == self.TAB_SHIPS:
            self._randomize_ships()

    def _randomize_identity(self):
        """Randomize all identity fields using portrait-aware names."""
        portrait_id = self.race_config.portrait_id or None
        result = RaceRandomizer.randomize_identity(portrait_id=portrait_id)

        self.race_config.race_name = result["race_name"]
        self.race_config.race_name_plural = result["race_name_plural"]
        self.race_config.leader_name = result["leader_name"]
        self.race_config.physical_type = result["physical_type"]
        self.race_config.government_type = result["government_type"]
        self.race_config.government_organization = result["government_organization"]
        self.race_config.leader_title = result["leader_title"]
        self.race_config.society_type = result["society_type"]
        self.race_config.faction_name = result["faction_name"]

        if self._identity_panel:
            self._identity_panel.set_from_config()

        logger.info(f"Randomized identity: {result['race_name']}")

    def _randomize_visuals(self):
        """Randomize flag and portrait selections."""
        if self._flag_gallery:
            flag_ids = [a[0] for a in self._flag_gallery._discover_assets()]
            new_flag = RaceRandomizer.randomize_flag(flag_ids)
            if new_flag:
                self.race_config.flag_id = new_flag
                self._flag_gallery.set_from_config()

        if self._portrait_gallery:
            portrait_ids = [a[0] for a in self._portrait_gallery._discover_assets()]
            new_portrait = RaceRandomizer.randomize_portrait(portrait_ids)
            if new_portrait:
                self.race_config.portrait_id = new_portrait
                self._portrait_gallery.set_from_config()

        logger.info(f"Randomized visuals: flag={self.race_config.flag_id}, portrait={self.race_config.portrait_id}")

    def _randomize_ships(self):
        """Randomize ship theme selection."""
        if self._theme_gallery:
            theme_ids = [a[0] for a in self._theme_gallery._discover_assets()]
            new_theme = RaceRandomizer.randomize_theme(theme_ids)
            if new_theme:
                self.race_config.theme_id = new_theme
                self._theme_gallery.set_from_config()
                self._refresh_ship_preview(new_theme)

        logger.info(f"Randomized ships: theme={self.race_config.theme_id}")

    def _on_cancel(self):
        """Handle Cancel button click."""
        logger.debug("Race setup cancelled")
        self.on_cancel_callback()
        self.kill()

    def _on_save(self):
        """Handle Save button click.

        FEAT-05: When editing a loaded species, shows a dialog asking whether
        to overwrite the existing species or save as a new one.
        """
        # Validate all required fields
        is_valid, error = self._validate_for_save()
        if not is_valid:
            self.error_label.set_text(error)
            return

        # Full validation (may have warnings for missing env preferences)
        validation_result = self.race_config.validate()
        if not validation_result.is_valid:
            logger.warning(f"Saving race with validation warnings: {validation_result.first_error}")

        # FEAT-05: If editing a loaded species, prompt for overwrite vs save-as-new
        if self.is_editing and self.race_config.race_id:
            self._show_save_update_dialog()
            return

        # New species — save directly
        self._do_save()

    def _do_save(self):
        """Execute the actual save to library."""
        success, message = self.race_library.save_race(self.race_config)
        if success:
            logger.info(f"Race saved: {self.race_config.name}")
            self.on_complete_callback(self.race_config)
            self.kill()
        else:
            self.error_label.set_text(message)

    def _show_save_update_dialog(self):
        """FEAT-05: Show dialog asking to overwrite or save as new species."""
        if self._save_update_dialog is not None:
            return  # Already showing

        dialog_width = 400
        dialog_height = 180
        container = self.get_container()
        cx = (container.get_size()[0] - dialog_width) // 2
        cy = (container.get_size()[1] - dialog_height) // 2

        self._save_update_dialog = pygame_gui.elements.UIWindow(
            rect=pygame.Rect(cx, cy, dialog_width, dialog_height),
            manager=self.ui_manager,
            window_display_title="Save Species",
            object_id="#save_update_dialog",
            resizable=False
        )

        dialog_container = self._save_update_dialog.get_container()
        dw = dialog_container.get_size()[0]

        # Message label
        pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(10, 10, dw - 20, 50),
            text="This species was loaded from the library.",
            manager=self.ui_manager,
            container=dialog_container
        )
        pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(10, 40, dw - 20, 50),
            text="How would you like to save it?",
            manager=self.ui_manager,
            container=dialog_container
        )

        # Buttons
        btn_width = 110
        btn_height = 36
        btn_y = 95
        spacing = 15
        total_btn_width = btn_width * 3 + spacing * 2
        start_x = (dw - total_btn_width) // 2

        self._btn_overwrite = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(start_x, btn_y, btn_width, btn_height),
            text="Overwrite",
            manager=self.ui_manager,
            container=dialog_container,
            object_id="#btn_overwrite"
        )

        self._btn_save_new = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(start_x + btn_width + spacing, btn_y, btn_width, btn_height),
            text="Save as New",
            manager=self.ui_manager,
            container=dialog_container,
            object_id="#btn_save_new"
        )

        self._btn_save_cancel = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(start_x + 2 * (btn_width + spacing), btn_y, btn_width, btn_height),
            text="Cancel",
            manager=self.ui_manager,
            container=dialog_container,
            object_id="#btn_save_cancel"
        )

    def _on_overwrite_save(self):
        """FEAT-05: Overwrite existing species (keep race_id)."""
        if self._save_update_dialog:
            self._save_update_dialog.kill()
            self._save_update_dialog = None
        self._do_save()

    def _on_save_as_new(self):
        """FEAT-05: Save as new species (clear race_id to generate fresh one)."""
        if self._save_update_dialog:
            self._save_update_dialog.kill()
            self._save_update_dialog = None
        self.race_config.race_id = None
        self.is_editing = False
        if self.btn_save:
            self.btn_save.set_text("Save")
        self._do_save()

    def _on_save_dialog_cancel(self):
        """FEAT-05: Cancel save dialog — return to editing."""
        if self._save_update_dialog:
            self._save_update_dialog.kill()
            self._save_update_dialog = None

    def process_event(self, event: pygame.event.Event) -> bool:
        """Process pygame events.

        PROJ-66 Phase 6: Added handling for identity panel dropdowns and aptitudes sliders.
        """
        handled = super().process_event(event)

        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            # Check tab buttons first
            for btn in self.tab_buttons:
                if event.ui_element == btn:
                    self._on_tab_clicked(btn.tab_index)
                    handled = True
                    break

            # FEAT-05: Save/Update dialog buttons
            if not handled and self._save_update_dialog is not None:
                if event.ui_element == self._btn_overwrite:
                    self._on_overwrite_save()
                    handled = True
                elif event.ui_element == self._btn_save_new:
                    self._on_save_as_new()
                    handled = True
                elif event.ui_element == self._btn_save_cancel:
                    self._on_save_dialog_cancel()
                    handled = True

            if not handled:
                if event.ui_element == self.btn_cancel:
                    self._on_cancel()
                    handled = True
                elif event.ui_element == self.btn_save:
                    self._on_save()
                    handled = True
                elif self.btn_load and event.ui_element == self.btn_load:
                    self._on_load_race()
                    handled = True
                elif event.ui_element == self.btn_randomize:
                    self._on_randomize()
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

        # PROJ-66 Phase 6: Handle dropdown changes (identity panel)
        elif event.type == pygame_gui.UI_DROP_DOWN_MENU_CHANGED:
            # Identity panel dropdowns
            if self._identity_panel:
                self._identity_panel.handle_event(event)
                self._identity_panel.update_config()
            # Environment panel homeworld dropdown
            if self._environment_panel:
                self._environment_panel.handle_dropdown_change(event)
            handled = True

        # Handle slider changes
        elif event.type == pygame_gui.UI_HORIZONTAL_SLIDER_MOVED:
            # PROJ-283 Phase 5 / PROJ-285 crash fix:
            # `update_labels` refreshes per-row value / tolerance / cost
            # labels and re-renders the points-remaining header (via
            # `PreferenceRow.refresh_from_sliders` -> `_on_row_change`);
            # `update_config` writes the slider values back into
            # `race_config.preferences` + `base_reproduction_rate` /
            # `base_happiness`. Both are cheap.
            if self._environment_panel:
                self._environment_panel.update_labels()
                self._environment_panel.update_config()
            # PROJ-66: Update aptitudes panel labels and budget when sliders move
            if self._aptitudes_panel:
                self._aptitudes_panel.update_config()
                self._aptitudes_panel.update_labels()
                self._aptitudes_panel.update_budget_display()
            handled = True

        # Handle text entry changes
        elif event.type == pygame_gui.UI_TEXT_ENTRY_CHANGED:
            # PROJ-66: Identity panel text inputs
            if self._identity_panel:
                self._identity_panel.handle_event(event)
                self._identity_panel.update_config()

            # Description panel text boxes
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
