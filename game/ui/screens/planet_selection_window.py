"""
Planet Selection Window - Simple planet selection dialog.

Used for selecting a planet from a list, typically for targeting or transfer operations.

PROJ-329A Phase 2 Task 2.3: Migrated to two-stage construction. Cheap
state (planets, callback, list label, show_any flag) lives before
``super().__init__``; widget construction is behind
``PlanetSelectionUiBuilder`` so tests can swap in a Mock under
``bypass_init``. The minimum-rect enforcement happens in Stage 1 so
the rect passed to the shell is the clamped one.
"""
from __future__ import annotations

import logging
from typing import Any, TYPE_CHECKING, Optional

import pygame
from pygame_gui.elements import UISelectionList, UIButton, UILabel

from game.assets.asset_manager import get_default_asset_manager
from game.ui.panels.planet_report_panel import PlanetReportPanel
from game.ui.screens.strategy_modal_window import StrategyModalWindow

if TYPE_CHECKING:
    from game.core.protocols import IPlanet
    from game.ui.screens.strategy_window_manager import StrategyWindowManager

logger = logging.getLogger(__name__)


# Layout constants — kept module-level so the builder + update() share them.
MIN_WINDOW_WIDTH = 950
MIN_WINDOW_HEIGHT = 650
LIST_WIDTH = 300


class PlanetSelectionUiBuilder:
    """Production widget builder. Constructs label, selection list,
    details label, Confirm button, and (optionally) the "Any Planet"
    button.

    Reads ``screen.planets``, ``screen._list_label``,
    ``screen._show_any_button`` (built in Stage 1) and writes
    ``screen.label``, ``screen.selection_list``, ``screen.lbl_details``,
    ``screen.btn_select``, ``screen.btn_any``.
    """

    def build(self, screen: "PlanetSelectionWindow") -> None:
        # Issue #24: use the content-area container rect, not screen.rect.
        # screen.rect is the outer pygame_gui window rect, inflated by
        # shadow_width on every side and including the title bar — placing
        # widgets relative to it clips them past the container's render
        # bounds. get_container().rect is the actual content area.
        rect = screen.get_container().rect

        # Left Side: List
        screen.label = UILabel(
            pygame.Rect(10, 10, LIST_WIDTH, 30),
            screen._list_label,
            screen.ui_manager,
            container=screen,
        )

        screen.selection_list = UISelectionList(
            pygame.Rect(10, 45, LIST_WIDTH, rect.height - 120),
            item_list=[p.name for p in screen.planets],
            manager=screen.ui_manager,
            container=screen,
        )

        # Right Side: Details
        details_x = LIST_WIDTH + 20
        details_w = rect.width - LIST_WIDTH - 30

        screen.lbl_details = UILabel(
            pygame.Rect(details_x, 10, details_w, 30),
            "Planet Report",
            screen.ui_manager,
            container=screen,
        )

        # Planet detail panel will be created dynamically on selection (PROJ-54)

        screen.btn_select = UIButton(
            pygame.Rect(10, rect.height - 60, 120, 30),
            "Confirm",
            screen.ui_manager,
            container=screen,
        )

        screen.btn_any = None
        if screen._show_any_button:
            screen.btn_any = UIButton(
                pygame.Rect(rect.width - 140, rect.height - 60, 130, 30),
                "Any Planet",
                screen.ui_manager,
                container=screen,
            )


class PlanetSelectionWindow(StrategyModalWindow):
    def __init__(
        self,
        rect,
        manager,
        planets,
        on_selection_callback,
        *,
        window_manager: "StrategyWindowManager",
        window_title: str = "Select Planet to Colonize",
        list_label: str = "Habitable bodies:",
        show_any_button: bool = True,
        facade: Any = None,
        ui_builder: Optional[PlanetSelectionUiBuilder] = None,
    ):
        """
        Initialize planet selection window.

        Args:
            rect: Window position and size rectangle.
            manager: pygame_gui UIManager instance.
            planets: List of planet objects to select from.
            on_selection_callback: Called with selected planet (or None for "Any").
            window_title: Window title text (default: colonization use case).
            list_label: Label text above planet list (default: "Habitable bodies:").
            show_any_button: Whether to show "Any Planet" button (default: True).
            facade: Optional strategy session facade. PROJ-397 Phase 3
                Task 3.2: when provided, the per-planet
                ``PlanetReportPanel`` fetches a fresh
                ``ColonyDemographicView`` via
                ``facade.economy.colony_demographic_view(planet.id)`` so
                colonized rows render the indented per-species
                sub-block (PROJ-289 layout). When ``None`` (e.g. legacy
                test fixtures), the panel falls back to ``view=None``
                and PROJ-289's data-rich layout is skipped, but no
                stale legacy rendering remains in
                ``format_planet_info``.
            ui_builder: Optional UI builder override (test seam).
        """
        # ---- Stage 1: cheap state ----
        # Enforce minimum size for full planet report display
        if rect.width < MIN_WINDOW_WIDTH:
            rect.width = MIN_WINDOW_WIDTH
        if rect.height < MIN_WINDOW_HEIGHT:
            rect.height = MIN_WINDOW_HEIGHT

        self.planets = planets
        self.callback = on_selection_callback
        self._list_label = list_label
        self._show_any_button = show_any_button
        self._facade = facade
        self.current_selection_name = None

        # Planet detail panel (PROJ-54)
        self.planet_detail_panel = None  # Created when planet selected
        self.selected_planet = None      # Track current selection
        # Default widget slot for the optional "Any" button so tests
        # that don't run the builder can still read it.
        self.btn_any = None

        # ---- Stage 2: shell ----
        super().__init__(
            rect, manager, window_display_title=window_title,
            window_manager=window_manager,
        )

        # ---- Stage 3: widgets ----
        if getattr(self, '_window_init_bypassed', False):
            if ui_builder is not None:
                ui_builder.build(self)
            return

        (ui_builder or PlanetSelectionUiBuilder()).build(self)

    def update(self, time_delta: float) -> None:
        super().update(time_delta)

        # Check for selection change (PROJ-54)
        selected_name = self.selection_list.get_single_selection()
        if selected_name != self.current_selection_name:
            self.current_selection_name = selected_name

            # Find planet object
            planet: 'IPlanet | None' = None
            if selected_name:
                planet = next((p for p in self.planets if p.name == selected_name), None)

            # Check if actual planet object changed
            if planet != self.selected_planet:
                # Kill old panel if exists
                if self.planet_detail_panel:
                    self.planet_detail_panel.kill()
                    self.planet_detail_panel = None

                if planet:
                    # Create planet report panel
                    details_x = LIST_WIDTH + 20
                    details_y = 45
                    details_width = self.rect.width - LIST_WIDTH - 30
                    # Leave room for buttons at bottom (buttons at rect.height - 60, so stop at -80)
                    details_height = self.rect.height - 130

                    # Load planet portrait image
                    portrait_surface = None
                    if planet.image_id:
                        am = get_default_asset_manager()
                        portrait_surface = am.load_planet_image(planet.image_id, requested_size=512)
                        # Apply rotation if specified
                        if portrait_surface and planet.image_rotation:
                            portrait_surface = pygame.transform.rotate(portrait_surface, planet.image_rotation)

                    # PROJ-397 Phase 3 Task 3.2: fetch a fresh
                    # ``ColonyDemographicView`` so the panel renders the
                    # PROJ-289 per-species sub-block instead of falling
                    # back to the legacy single-line layout (which was
                    # deleted from `format_planet_info` in this phase).
                    # Uncolonized planets short-circuit before the view
                    # is consulted, so only the colonized branch needs it.
                    view = None
                    if self._facade is not None and planet.owner_id is not None:
                        view = self._facade.economy.colony_demographic_view(planet.id)

                    self.planet_detail_panel = PlanetReportPanel(
                        manager=self.ui_manager,
                        rect=pygame.Rect(details_x, details_y, details_width, details_height),
                        planet=planet,
                        container=self,
                        portrait_surface=portrait_surface,
                        show_complexes=False,   # Match strategy UI - no separate complexes column
                        view=view,
                    )

                self.selected_planet = planet

        if self.btn_select.check_pressed():
            selected_name = self.selection_list.get_single_selection()
            logger.debug(f"PlanetSelectionWindow: Confirm Pressed. Selection: {selected_name}")
            if selected_name:
                # Find planet
                choice = next((p for p in self.planets if p.name == selected_name), None)
                if choice:
                     logger.debug(f"PlanetSelectionWindow: Calling callback with {choice.name}")
                     self.callback(choice)
                     self.kill()
            else:
                logger.debug("PlanetSelectionWindow: No selection made.")

        if self.btn_any and self.btn_any.check_pressed():
            # "Any Planet" -> Return None to defer selection to arrival
            self.callback(None)
            self.kill()

    def kill(self) -> None:
        """Clean up resources when window is closed. (PROJ-54)"""
        # Clean up planet detail panel
        if self.planet_detail_panel:
            self.planet_detail_panel.kill()
            self.planet_detail_panel = None

        # Call parent cleanup
        super().kill()
