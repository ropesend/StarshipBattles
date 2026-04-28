"""
EmpirePanelWindow - Multi-tab empire information panel.

PROJ-99 Phase 3: Main window with Treasury, Population, and placeholder tabs.
Provides empire-wide overview of economy, species data, and future features.
"""
from __future__ import annotations

from typing import Any, Callable, Dict, List, Optional, TYPE_CHECKING

import pygame
import pygame_gui
from pygame_gui.elements import UIPanel, UIButton, UILabel, UIImage, UITextBox, UIScrollingContainer

if TYPE_CHECKING:
    from game.strategy.data.race_config import RaceConfig
    from game.core.protocols import IEmpire
    from game.core.registry import GameRegistries
    from game.ui.screens.strategy_window_manager import StrategyWindowManager
from game.core.paths import Paths
from game.strategy.services.empire_economy_service import EmpireEconomyService  # PROJ-292 M1
from game.ui.panels.empire_treasury_panel import EmpireTreasuryPanel, load_resource_icons
from game.ui.screens.race_asset_loader import RaceAssetLoader
from game.ui.screens.strategy_modal_window import StrategyModalWindow
from game.ui.utils import create_section_header


# Tab constants
TAB_TREASURY = 0
TAB_POPULATION = 1
TAB_MORE = 2

TAB_NAMES = ["Treasury", "Population", "More To Follow"]

# Layout constants
TAB_HEIGHT = 40
TAB_TOP = 5
PANEL_TOP = 55
ROW_HEIGHT = 24
SECTION_GAP = 15
APTITUDE_COL_WIDTH = 200


class EmpirePanelWindow(StrategyModalWindow):
    """
    Multi-tab window displaying empire-wide information.

    Tabs:
    - Treasury: Production, expenses, and storage by resource type
    - Population: Species portrait, flag, identity, aptitudes, environment
    - More To Follow: Placeholder for future features

    PROJ-313: Migrated to StrategyModalWindow base class.
    """

    def __init__(
        self,
        rect: pygame.Rect,
        manager: pygame_gui.UIManager,
        empire: 'IEmpire',
        *,
        window_manager: "StrategyWindowManager",
        on_close_callback: Optional[Callable[[], None]] = None,
        registries: 'GameRegistries' = None,
        race_registry: Optional[Any] = None,
    ):
        """
        Create empire panel window.

        Args:
            rect: Window position and size
            manager: pygame_gui UIManager
            empire: Empire object with race_config, resource_pool, etc.
            window_manager: PROJ-313 StrategyWindowManager (or None outside the strategy screen).
            on_close_callback: Optional callback when window closes (registrar slot cleanup).
            registries: GameRegistries for DI (required)
            race_registry: PROJ-290 — optional `IRaceRegistry` threaded
                through to `EmpireEconomyCalculator` so the Treasury tab
                renders the multi-resource Population Upkeep row. When
                None, the row stays hidden.
        """
        super().__init__(
            rect,
            manager,
            window_display_title="Empire Overview",
            resizable=False,
            window_manager=window_manager,
        )

        self.empire: 'IEmpire' = empire
        self.on_close_callback = on_close_callback
        self._registries = registries  # PROJ-211: Injected registries
        self._race_registry = race_registry  # PROJ-290

        # Tab state
        self.tab_buttons: List[UIButton] = []
        self.step_panels: List[UIPanel] = []
        self.current_tab = TAB_TREASURY

        # Asset loader
        self._asset_loader = RaceAssetLoader()

        # Load resource icons
        self._resource_icons = load_resource_icons()

        # Panel references
        self._treasury_panel: Optional[EmpireTreasuryPanel] = None

        # Create UI
        self._create_ui()
        self._show_tab(TAB_TREASURY)

    def _create_ui(self) -> None:
        """Create all UI elements."""
        container = self.get_container()
        content_width = container.get_size()[0] - 20
        content_height = container.get_size()[1]

        # Tab buttons at top
        self._create_tab_buttons(container, content_width)

        # Content panels below tabs
        panel_height = content_height - PANEL_TOP - 20
        self._create_tab_panels(container, content_width, PANEL_TOP, panel_height)

    def _create_tab_buttons(self, container, width: int) -> None:
        """Create clickable tab buttons for navigation."""
        num_tabs = len(TAB_NAMES)
        btn_width = (width - 10) // num_tabs

        for i, name in enumerate(TAB_NAMES):
            btn = UIButton(
                relative_rect=pygame.Rect(10 + i * btn_width, TAB_TOP, btn_width - 5, TAB_HEIGHT),
                text=name,
                manager=self.ui_manager,
                container=container,
                object_id=f"#tab_{name.lower().replace(' ', '_')}"
            )
            btn.tab_index = i
            self.tab_buttons.append(btn)

    def _create_tab_panels(self, container, width: int, top: int, height: int) -> None:
        """Create panels for each tab."""
        panel_rect = pygame.Rect(10, top, width, height)

        # Treasury panel
        panel_treasury = UIPanel(
            relative_rect=panel_rect,
            manager=self.ui_manager,
            container=container,
            object_id="#panel_treasury"
        )
        self._build_treasury_tab(panel_treasury)
        self.step_panels.append(panel_treasury)

        # Population panel
        panel_population = UIPanel(
            relative_rect=panel_rect,
            manager=self.ui_manager,
            container=container,
            object_id="#panel_population"
        )
        self._build_population_tab(panel_population)
        self.step_panels.append(panel_population)

        # Placeholder panel
        panel_more = UIPanel(
            relative_rect=panel_rect,
            manager=self.ui_manager,
            container=container,
            object_id="#panel_more"
        )
        self._build_placeholder_tab(panel_more)
        self.step_panels.append(panel_more)

    def _show_tab(self, tab_index: int) -> None:
        """
        Show the specified tab panel.

        Args:
            tab_index: Tab index to show (0-2)
        """
        # Clamp to valid range
        tab_index = max(0, min(tab_index, len(self.step_panels) - 1))
        self.current_tab = tab_index

        # Hide all panels, show target
        for i, panel in enumerate(self.step_panels):
            if i == tab_index:
                panel.show()
            else:
                panel.hide()

        # Update tab button highlighting
        for i, btn in enumerate(self.tab_buttons):
            if i == tab_index:
                btn.select()
            else:
                btn.unselect()

    def _build_treasury_tab(self, panel: UIPanel) -> None:
        """Build Treasury tab content using EmpireTreasuryPanel.

        PROJ-290: threads `economy_config` + `race_registry` into the
        calculator so the empire-wide population-upkeep row (Section 3)
        has its source data. Deps are sourced from module-level default
        / optional facade attribute — None for either short-circuits
        the calculator's upkeep aggregation to `{}` (row auto-hides).
        """
        from game.strategy.config.economy_config import get_default_economy_config

        economy = get_default_economy_config()
        race_registry = getattr(self, "_race_registry", None)
        # PROJ-292 M1: UI consumes the service facade, not the engine-layer
        # calculator directly.
        service = EmpireEconomyService(
            registries=self._registries,
            economy_config=economy,
            race_registry=race_registry,
        )
        snapshot = service.get_snapshot(self.empire)
        self._treasury_panel = EmpireTreasuryPanel(
            panel,
            self.ui_manager,
            snapshot,
            self._resource_icons
        )

    def _build_population_tab(self, panel: UIPanel) -> None:
        """Build Population tab with species card."""
        # Get panel dimensions for scroll container
        panel_rect = panel.get_relative_rect()
        container_width = panel_rect.width - 20
        container_height = panel_rect.height - 20

        # Create scrolling container
        scroll_container = UIScrollingContainer(
            relative_rect=pygame.Rect(10, 10, container_width, container_height),
            manager=self.ui_manager,
            container=panel
        )

        # Get race config (IEmpire protocol guarantees race_config property exists)
        race_config = self.empire.race_config

        if race_config is None:
            # No species data
            UILabel(
                relative_rect=pygame.Rect(10, 10, container_width - 20, 30),
                text="No species data available",
                manager=self.ui_manager,
                container=scroll_container
            )
            return

        # Render species card
        y_offset = self._render_species_card(scroll_container, race_config, 10, container_width - 40)

        # Set scrollable area height
        scroll_container.set_scrollable_area_dimensions(
            (container_width - 20, y_offset + 20)
        )

    def _render_species_card(
        self,
        container: UIScrollingContainer,
        race_config: 'RaceConfig',
        y_offset: int,
        content_width: int
    ) -> int:
        """
        Render a complete species card.

        Args:
            container: Scroll container to add elements to
            race_config: RaceConfig object
            y_offset: Starting y position
            content_width: Available width for content

        Returns:
            Final y offset after all content
        """
        # === Portrait + Flag row ===
        y_offset = self._render_portrait_flag_row(container, race_config, y_offset)

        # === Identity section ===
        y_offset = self._render_identity_section(container, race_config, y_offset, content_width)

        # === Aptitudes section ===
        y_offset = self._render_aptitudes_section(container, race_config, y_offset, content_width)

        # === Environment section ===
        y_offset = self._render_environment_section(container, race_config, y_offset, content_width)

        # === Descriptions section ===
        y_offset = self._render_descriptions_section(container, race_config, y_offset, content_width)

        return y_offset

    def _render_portrait_flag_row(
        self,
        container: UIScrollingContainer,
        race_config: 'RaceConfig',
        y_offset: int
    ) -> int:
        """Render portrait and flag images."""
        # Portrait (128x128) - IEmpire has portrait_id, RaceConfig has portrait_id as fallback
        portrait_id = self.empire.portrait_id or race_config.portrait_id
        if portrait_id:
            portrait_surf = self._asset_loader.load_portrait_full(portrait_id)
            if portrait_surf:
                scaled = pygame.transform.smoothscale(portrait_surf, (128, 128))
                UIImage(
                    relative_rect=pygame.Rect(10, y_offset, 128, 128),
                    image_surface=scaled,
                    manager=self.ui_manager,
                    container=container
                )

        # Flag (96x64) - rectangle shape - IEmpire has flag_id, RaceConfig has flag_id as fallback
        flag_id = self.empire.flag_id or race_config.flag_id
        if flag_id:
            shapes = self._asset_loader.load_flag_full(flag_id)
            if shapes and len(shapes) > 0:
                # shapes[0] is rectangle
                scaled = pygame.transform.smoothscale(shapes[0], (96, 64))
                UIImage(
                    relative_rect=pygame.Rect(150, y_offset, 96, 64),
                    image_surface=scaled,
                    manager=self.ui_manager,
                    container=container
                )

        return y_offset + 140

    def _render_identity_section(
        self,
        container: UIScrollingContainer,
        race_config: 'RaceConfig',
        y_offset: int,
        content_width: int
    ) -> int:
        """Render identity section with faction/race info."""
        # Section header
        create_section_header("Identity", y_offset, content_width, self.ui_manager, container, height=ROW_HEIGHT)
        y_offset += ROW_HEIGHT + 5

        # Identity fields - RaceConfig dataclass guarantees all fields exist with defaults
        identity_fields = [
            ("Faction Name", race_config.faction_name),
            ("Race Name", race_config.race_name),
            ("Government Type", race_config.government_type),
            ("Government Organization", race_config.government_organization),
            ("Leader", f"{race_config.leader_title} {race_config.leader_name}".strip()),
            ("Physical Type", race_config.physical_type),
            ("Society Type", race_config.society_type),
        ]

        for label, value in identity_fields:
            if value:  # Skip empty fields
                UILabel(
                    relative_rect=pygame.Rect(20, y_offset, content_width - 20, ROW_HEIGHT),
                    text=f"{label}: {value}",
                    manager=self.ui_manager,
                    container=container
                )
                y_offset += ROW_HEIGHT

        return y_offset + SECTION_GAP

    def _render_aptitudes_section(
        self,
        container: UIScrollingContainer,
        race_config: 'RaceConfig',
        y_offset: int,
        content_width: int
    ) -> int:
        """Render aptitudes in 3-column layout."""
        # Section header
        create_section_header("Aptitudes", y_offset, content_width, self.ui_manager, container, height=ROW_HEIGHT)
        y_offset += ROW_HEIGHT + 5

        # Aptitude names and display labels - RaceConfig dataclass has defaults
        aptitudes = [
            ("Strength", race_config.aptitude_strength),
            ("Intelligence", race_config.aptitude_intelligence),
            ("Constitution", race_config.aptitude_constitution),
            ("Dexterity", race_config.aptitude_dexterity),
            ("Species Tolerance", race_config.aptitude_tolerance_other_species),
            ("Cooperation", race_config.aptitude_cooperation),
            # PROJ-283 Phase 4: happiness + pop_growth aptitudes deleted; show
            # the new derived fields (formatted to match the int aptitude column).
            ("Happiness", f"{race_config.base_happiness:.2f}"),
            ("Repro Rate", f"{race_config.base_reproduction_rate*100:.1f}%"),
            ("Conflict Tolerance", race_config.aptitude_conflict_tolerance),
        ]

        # 3 columns layout
        col_width = min(APTITUDE_COL_WIDTH, content_width // 3)
        for i, (name, value) in enumerate(aptitudes):
            col = i % 3
            row = i // 3
            x = 20 + col * col_width
            y = y_offset + row * ROW_HEIGHT

            UILabel(
                relative_rect=pygame.Rect(x, y, col_width - 10, ROW_HEIGHT),
                text=f"{name}: {value}",
                manager=self.ui_manager,
                container=container
            )

        # Calculate rows used
        num_rows = (len(aptitudes) + 2) // 3  # Ceiling division
        y_offset += num_rows * ROW_HEIGHT + SECTION_GAP

        return y_offset

    def _render_environment_section(
        self,
        container: UIScrollingContainer,
        race_config: 'RaceConfig',
        y_offset: int,
        content_width: int
    ) -> int:
        """Render environmental preferences."""
        # Section header
        create_section_header("Environmental Preferences", y_offset, content_width, self.ui_manager, container, height=ROW_HEIGHT)
        y_offset += ROW_HEIGHT + 5

        # PROJ-283 Phase 4: env summaries now read from `race_config.preferences`
        # (the legacy gravity_ideal/_tolerance/etc. fields are gone).
        prefs = race_config.preferences
        gravity_pref = prefs.get("gravity")
        temp_pref = prefs.get("temperature")
        water_pref = prefs.get("water")
        rad_pref = prefs.get("radiation")

        env_fields = [
            f"Gravity: {gravity_pref.setpoint/9.81:.1f}g (+/- {gravity_pref.tolerance/9.81:.1f}g)"
                if gravity_pref else "Gravity: --",
            f"Temperature: {temp_pref.setpoint:.0f}K (+/- {temp_pref.tolerance:.0f}K)"
                if temp_pref else "Temperature: --",
            f"Water: {water_pref.setpoint*100:.0f}% (+/- {water_pref.tolerance*100:.0f}%)"
                if water_pref else "Water: --",
            f"Radiation Tolerance: {rad_pref.tolerance:.0f}"
                if rad_pref else "Radiation Tolerance: --",
        ]

        for text in env_fields:
            UILabel(
                relative_rect=pygame.Rect(20, y_offset, content_width - 20, ROW_HEIGHT),
                text=text,
                manager=self.ui_manager,
                container=container
            )
            y_offset += ROW_HEIGHT

        return y_offset + SECTION_GAP

    def _render_descriptions_section(
        self,
        container: UIScrollingContainer,
        race_config: 'RaceConfig',
        y_offset: int,
        content_width: int
    ) -> int:
        """Render bio and socio descriptions."""
        bio = race_config.bio_description
        socio = race_config.socio_description

        if bio:
            # Biology header
            create_section_header("Biology", y_offset, content_width, self.ui_manager, container, height=ROW_HEIGHT)
            y_offset += ROW_HEIGHT

            # Bio text box
            UITextBox(
                html_text=bio,
                relative_rect=pygame.Rect(20, y_offset, content_width - 30, 100),
                manager=self.ui_manager,
                container=container
            )
            y_offset += 100 + SECTION_GAP

        if socio:
            # Society header
            create_section_header("Society", y_offset, content_width, self.ui_manager, container, height=ROW_HEIGHT)
            y_offset += ROW_HEIGHT

            # Socio text box
            UITextBox(
                html_text=socio,
                relative_rect=pygame.Rect(20, y_offset, content_width - 30, 100),
                manager=self.ui_manager,
                container=container
            )
            y_offset += 100 + SECTION_GAP

        return y_offset

    def _build_placeholder_tab(self, panel: UIPanel) -> None:
        """Build placeholder tab with coming soon message."""
        panel_rect = panel.get_relative_rect()

        UILabel(
            relative_rect=pygame.Rect(0, panel_rect.height // 2 - 15, panel_rect.width, 30),
            text="More panels coming soon...",
            manager=self.ui_manager,
            container=panel,
            object_id="#placeholder_text"
        )

    def process_event(self, event: pygame.event.Event) -> bool:
        """
        Process UI events.

        Args:
            event: pygame event

        Returns:
            True if event was handled
        """
        handled = super().process_event(event)

        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            # Check tab buttons
            for btn in self.tab_buttons:
                if event.ui_element == btn:
                    self._show_tab(btn.tab_index)
                    return True

        return handled

    def kill(self) -> None:
        """Clean up and fire close callback."""
        if self.on_close_callback:
            self.on_close_callback()
        super().kill()
