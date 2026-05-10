"""Panel factory for BuildQueueScreen.

Creates all UI panels for the build queue screen. Extracted from build_queue_screen.py
as part of PROJ-172 Phase 4 MVVM refactoring.
PROJ-221 Phase 4: Replaced hardcoded columns with VirtualTable integration.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING, List, Optional, Dict

import pygame
import pygame_gui
import pygame_gui.elements as ui

from game.ui.panels.planet_report_panel import PlanetReportPanel
from game.strategy.services.planet_economy_projector import compute_planet_production
from game.ui.panels.design_report_panel import DesignReportPanel
from game.ui.screens.build_queue_selector import BuildQueueSelector
from game.ui.components.table import VirtualTable, TableColumnManager, SingleSelect
from game.ui.screens.build_queue_queue_data_source import (
    BuildQueueQueueDataSource,
    BUILD_QUEUE_COLUMNS,
)

if TYPE_CHECKING:
    from game.strategy.data.build_queue_source import BuildQueueSource
    from game.ui.panels.build_queue_portraits import BuildQueuePortraitLoader

logger = logging.getLogger(__name__)


# FEAT-17: bottom-of-panel footer strip that hosts the pause/unpause toggle.
# Sized to fit a comfortable click target without crowding the queue table.
_PAUSE_FOOTER_HEIGHT = 50


def _pause_button_label(is_paused: bool) -> str:
    """Toggle label per FEAT-17 spec.

    Single source of truth for the button text; reused on initial render
    and on every queue-selector refresh so re-selecting yards flips the
    label correctly.
    """
    return "Unpause Build Queue" if is_paused else "Pause Build Queue"


@dataclass
class BuildQueuePanels:
    """Container for all BuildQueueScreen panels.

    PROJ-221 Phase 4: Replaced queue_column_positions with VirtualTable components.
    """

    background: ui.UIPanel
    context_report: ui.UIPanel  # PlanetReportPanel or fleet info panel
    planet_report: Optional[PlanetReportPanel]  # Only set for planet contexts
    queue_selector: BuildQueueSelector
    design_report: DesignReportPanel
    items_list_panel: ui.UIPanel
    items_scrollable: ui.UIScrollingContainer
    build_queue_panel: ui.UIPanel
    queue_header_text: ui.UITextBox
    virtual_table: VirtualTable
    column_manager: TableColumnManager
    data_source: BuildQueueQueueDataSource
    # FEAT-17: pause/unpause toggle for the active queue source.
    btn_pause_queue: ui.UIButton
    filter_panel: ui.UIPanel
    roles_panel: ui.UIPanel
    roles_scrollable: ui.UIScrollingContainer
    bottom_bar: ui.UIPanel
    btn_close: ui.UIButton
    btn_add_to_queue: Optional[ui.UIButton]
    btn_remove_from_queue: Optional[ui.UIButton]
    btn_category_complex: ui.UIButton
    btn_category_ship: ui.UIButton
    btn_category_satellite: ui.UIButton
    btn_category_fighter: ui.UIButton
    btn_category_drop_pod: ui.UIButton
    resource_icons: Dict[str, pygame.Surface]


class BuildQueuePanelFactory:
    """Factory for creating BuildQueueScreen panels.

    Creates and positions all UI elements for the build queue screen.
    Does not manage state - that's handled by the ViewModel.
    """

    def __init__(
        self,
        manager: pygame_gui.UIManager,
        build_context,
        queue_sources: List['BuildQueueSource'],
        portrait_loader: 'BuildQueuePortraitLoader',
        on_queue_selection_changed,
        portrait_surface: Optional[pygame.Surface] = None,
        *,
        facade,
        empire,
    ) -> None:
        """Initialize the panel factory.

        Args:
            manager: pygame_gui UIManager.
            build_context: Planet or Fleet whose build queue is being managed.
            queue_sources: List of BuildQueueSource objects at this hex.
            portrait_loader: BuildQueuePortraitLoader for resource icons.
            on_queue_selection_changed: Callback for queue selector changes.
            portrait_surface: Planet portrait image surface.
            facade: ``StrategySessionFacade`` — required.  Used for the
                per-species ``ColonyDemographicView`` (PROJ-292 H1),
                ``get_registries()`` (PROJ-396 MAJ-003), and
                ``get_turn_number()`` (PROJ-396 MAJ-003).
            empire: The current empire whose resource pool is rendered in
                the bottom bar.  Passed explicitly rather than read off a
                session so this factory has no facade-bypass path.

        PROJ-396 MAJ-003: removed ``session`` parameter.  The previous
        three reads (``session.registries``, ``session.current_empire``,
        ``session.turn``) all now route through ``facade`` or the
        explicit ``empire`` kwarg.  Note: ``getattr(self.session,
        'current_empire', None)`` was already returning ``None`` in
        production (the session attribute is ``active_empire``), so the
        bottom-bar resource label was effectively dormant; passing
        ``empire`` explicitly restores the intended behavior.
        """
        self.manager = manager
        self.build_context = build_context
        self.queue_sources = queue_sources
        self.portrait_loader = portrait_loader
        self._facade = facade
        self._empire = empire
        self.on_queue_selection_changed = on_queue_selection_changed
        self.portrait_surface = portrait_surface

        # Get screen dimensions
        screen_size = manager.get_root_container().get_container().get_size()
        self.screen_width = screen_size[0]
        self.screen_height = screen_size[1]

        # Resource icons loaded once
        self.resource_icons = portrait_loader.load_resource_icons(icon_size=20)

    def create_all_panels(self, format_empire_resources) -> BuildQueuePanels:
        """Create all panels for the build queue screen.

        Args:
            format_empire_resources: Function to format empire resource display.

        Returns:
            BuildQueuePanels containing all created panels.
        """
        background = self._create_background()
        context_report, planet_report = self._create_context_report_panel(background)
        queue_selector = self._create_queue_selector_panel(background)
        design_report = self._create_design_report_panel(background)
        items_panel, items_scrollable = self._create_items_list_panel(background)
        (
            queue_panel,
            queue_header,
            virtual_table,
            column_manager,
            data_source,
            btn_pause_queue,
        ) = self._create_build_queue_panel(background)
        filter_panel, btn_complex, btn_ship, btn_sat, btn_fighter, btn_drop_pod, roles_scrollable = (
            self._create_filter_panel(background)
        )
        bottom_bar, btn_close = self._create_bottom_bar(background, format_empire_resources)

        return BuildQueuePanels(
            background=background,
            context_report=context_report,
            planet_report=planet_report,
            queue_selector=queue_selector,
            design_report=design_report,
            items_list_panel=items_panel,
            items_scrollable=items_scrollable,
            build_queue_panel=queue_panel,
            queue_header_text=queue_header,
            virtual_table=virtual_table,
            column_manager=column_manager,
            data_source=data_source,
            btn_pause_queue=btn_pause_queue,
            filter_panel=filter_panel,
            roles_panel=filter_panel,  # It is shared now
            roles_scrollable=roles_scrollable,
            bottom_bar=bottom_bar,
            btn_close=btn_close,
            btn_add_to_queue=None,
            btn_remove_from_queue=None,
            btn_category_complex=btn_complex,
            btn_category_ship=btn_ship,
            btn_category_satellite=btn_sat,
            btn_category_fighter=btn_fighter,
            btn_category_drop_pod=btn_drop_pod,
            resource_icons=self.resource_icons,
        )

    def _create_background(self) -> ui.UIPanel:
        """Create semi-transparent background overlay.

        PROJ-373 Phase 4: opts into the scoped `@fast_panel` theme class so
        pygame_gui uses the cheap `RectDrawableShape` instead of the global
        `panel` block's `RoundedRectangleShape` (eliminates ~3s of
        anti-aliased corner rasterization on first open).
        """
        return ui.UIPanel(
            relative_rect=pygame.Rect(0, 0, self.screen_width, self.screen_height),
            manager=self.manager,
            object_id="@fast_panel",
        )

    def _create_context_report_panel(self, container: ui.UIPanel) -> tuple:
        """Create context report panel (planet or fleet info).

        Returns:
            Tuple of (context_report panel, planet_report or None).
        """
        report_width = 600
        report_height = int((self.screen_height - 20) / 3)
        if report_height < 350:
            report_height = 350

        if self.build_context.context_type == "planet":
            # PROJ-292 H1: BuildQueueScreen always opens on colonized
            # planets (you can't queue construction on an uncolonized
            # world), so the facade lookup should essentially always
            # return a view.  PROJ-396 MAJ-003: ``facade`` is now a
            # required ctor kwarg, so the legacy ``_facade is None``
            # branch is gone.
            view = None
            if self.build_context.owner_id is not None:
                view = self._facade.get_colony_demographic_view(self.build_context.id)
            planet_report = PlanetReportPanel(
                manager=self.manager,
                rect=pygame.Rect(10, 10, report_width, report_height),
                planet=self.build_context,
                container=container,
                portrait_surface=self.portrait_surface,
                show_complexes=False,
                production_rates=compute_planet_production(
                    self.build_context, self._facade.get_registries()
                ),
                view=view,  # PROJ-292 H1
            )
            return planet_report, planet_report
        else:
            # Fleet context: create simple info panel
            fleet_panel = self._create_fleet_info_panel(container, report_width, report_height)
            return fleet_panel, None

    def _create_fleet_info_panel(
        self, container: ui.UIPanel, width: int, height: int
    ) -> ui.UIPanel:
        """Create simple info panel for fleet context."""
        panel = ui.UIPanel(
            relative_rect=pygame.Rect(10, 10, width, height),
            manager=self.manager,
            container=container,
            object_id="@fast_panel",
        )

        ui.UITextBox(
            relative_rect=pygame.Rect(10, 10, width - 20, 40),
            html_text=f"<b>{self.build_context.name}</b>",
            manager=self.manager,
            container=panel
        )

        ship_count = len(self.build_context.ships) if hasattr(self.build_context, 'ships') else 0
        has_yard = self.build_context.has_space_shipyard
        queue_size = len(self.build_context.construction_queue)

        info_text = f"""
        <b>Ships:</b> {ship_count}<br>
        <b>Space Yard:</b> {'Yes' if has_yard else 'No'}<br>
        <b>Queue Size:</b> {queue_size} items<br>
        """

        ui.UITextBox(
            relative_rect=pygame.Rect(10, 60, width - 20, height - 80),
            html_text=info_text,
            manager=self.manager,
            container=panel
        )

        return panel

    def _create_queue_selector_panel(self, container: ui.UIPanel) -> BuildQueueSelector:
        """Create queue selector column."""
        planet_report_height = int((self.screen_height - 20) / 3)
        if planet_report_height < 350:
            planet_report_height = 350
        filter_y = 10 + planet_report_height + 10
        filter_height = min(600, self.screen_height - filter_y - 200)

        panel_x = 10
        panel_y = filter_y + filter_height + 10
        panel_width = 600
        panel_height = self.screen_height - panel_y - 80

        return BuildQueueSelector(
            manager=self.manager,
            container=container,
            rect=pygame.Rect(panel_x, panel_y, panel_width, panel_height),
            queue_sources=self.queue_sources,
            on_selection_changed=self.on_queue_selection_changed,
        )

    def _create_design_report_panel(self, container: ui.UIPanel) -> DesignReportPanel:
        """Create design report panel."""
        design_report_width = 750
        design_report_x = self.screen_width - design_report_width - 10
        design_report_height = self.screen_height - 90

        return DesignReportPanel(
            manager=self.manager,
            rect=pygame.Rect(design_report_x, 10, design_report_width, design_report_height),
            container=container
        )

    def _create_items_list_panel(self, container: ui.UIPanel) -> tuple:
        """Create available designs panel.

        Returns:
            Tuple of (panel, scrollable_container).
        """
        panel_left = 10 + 600 + 10
        panel_width = 580

        panel_top = 10
        panel_height = self.screen_height - panel_top - 80

        panel = ui.UIPanel(
            relative_rect=pygame.Rect(panel_left, panel_top, panel_width, panel_height),
            manager=self.manager,
            container=container,
            object_id="@fast_panel",
        )

        ui.UITextBox(
            relative_rect=pygame.Rect(10, 10, panel_width - 20, 30),
            html_text="<b>Available Designs</b>",
            manager=self.manager,
            container=panel
        )

        scrollable = ui.UIScrollingContainer(
            relative_rect=pygame.Rect(10, 45, panel_width - 20, panel_height - 55),
            manager=self.manager,
            container=panel
        )

        return panel, scrollable

    def _create_build_queue_panel(self, container: ui.UIPanel) -> tuple:
        """Create build queue panel with VirtualTable.

        PROJ-221 Phase 4: Replaced hardcoded columns with VirtualTable.
        FEAT-17: added a bottom-left "Pause Build Queue" toggle button. The
        VirtualTable's panel shrinks by `_PAUSE_FOOTER_HEIGHT` to make room.

        Returns:
            Tuple of (panel, header_text, virtual_table, column_manager,
            data_source, btn_pause_queue).
        """
        panel_left = 10 + 600 + 10 + 580 + 10
        design_details_width = 750
        panel_width = self.screen_width - panel_left - design_details_width - 20
        if panel_width < 250:
            panel_width = 250

        panel_top = 10
        panel_height = self.screen_height - panel_top - 80

        panel = ui.UIPanel(
            relative_rect=pygame.Rect(panel_left, panel_top, panel_width, panel_height),
            manager=self.manager,
            container=container,
            object_id="@fast_panel",
        )

        header_text = ui.UITextBox(
            relative_rect=pygame.Rect(10, 10, panel_width - 20, 30),
            html_text="<b>Build Queue</b>",
            manager=self.manager,
            container=panel
        )

        # FEAT-17: reserve a footer strip at the bottom for the pause button.
        # The label flips between "Pause Build Queue" and "Unpause Build Queue"
        # at refresh time based on the active queue source's `is_paused`.
        footer_height = _PAUSE_FOOTER_HEIGHT
        # VirtualTable container (below header, above footer)
        table_panel = ui.UIPanel(
            relative_rect=pygame.Rect(
                0, 42, panel_width, panel_height - 52 - footer_height
            ),
            manager=self.manager,
            container=panel,
            object_id="@fast_panel",
        )

        # Get initial build rate / paused-state from first queue source
        initial_build_rate = {}
        initial_paused = False
        if self.queue_sources:
            initial_build_rate = self.queue_sources[0].build_rate or {}
            initial_paused = self.queue_sources[0].is_paused

        # Create column manager, data source, and VirtualTable
        column_manager = TableColumnManager(BUILD_QUEUE_COLUMNS)
        data_source = BuildQueueQueueDataSource(
            columns=BUILD_QUEUE_COLUMNS,
            portrait_loader=self.portrait_loader,
            build_rate=initial_build_rate,
        )
        virtual_table = VirtualTable(
            table_panel,
            self.manager,
            data_source,
            column_manager,
            SingleSelect(),
            row_height=48,
            header_height=40,
        )

        # FEAT-17: Pause/Unpause toggle button at bottom-left of the panel.
        btn_pause_queue = ui.UIButton(
            relative_rect=pygame.Rect(
                10, panel_height - footer_height + 5, 220, footer_height - 10
            ),
            text=_pause_button_label(initial_paused),
            manager=self.manager,
            container=panel,
        )

        return panel, header_text, virtual_table, column_manager, data_source, btn_pause_queue

    def _create_filter_panel(self, container: ui.UIPanel) -> tuple:
        """Create categories/filter panel.

        Returns:
            Tuple of (panel, btn_complex, btn_ship, btn_satellite, btn_fighter, btn_drop_pod, roles_scrollable).
        """
        panel_width = 600
        panel_left = 10

        planet_report_height = int((self.screen_height - 20) / 3)
        if planet_report_height < 350:
            planet_report_height = 350
        panel_top = 10 + planet_report_height + 10
        
        # Dynamically scale filter height (target 600) leaving at least 200px for below layout constraints
        panel_height = min(600, self.screen_height - panel_top - 200)

        panel = ui.UIPanel(
            relative_rect=pygame.Rect(panel_left, panel_top, panel_width, panel_height),
            manager=self.manager,
            container=container,
            object_id="@fast_panel",
        )

        ui.UITextBox(
            relative_rect=pygame.Rect(10, 10, 280, 30),
            html_text="<b>Categories</b>",
            manager=self.manager,
            container=panel
        )

        categories_scrollable = ui.UIScrollingContainer(
            relative_rect=pygame.Rect(10, 45, 280, panel_height - 55),
            manager=self.manager,
            container=panel
        )

        btn_complex = ui.UIButton(
            relative_rect=pygame.Rect(0, 0, 260, 40),
            text="Complexes",
            manager=self.manager,
            container=categories_scrollable
        )

        btn_ship = ui.UIButton(
            relative_rect=pygame.Rect(0, 45, 260, 40),
            text="Ships",
            manager=self.manager,
            container=categories_scrollable
        )

        btn_satellite = ui.UIButton(
            relative_rect=pygame.Rect(0, 90, 260, 40),
            text="Satellites",
            manager=self.manager,
            container=categories_scrollable
        )

        btn_fighter = ui.UIButton(
            relative_rect=pygame.Rect(0, 135, 260, 40),
            text="Fighters",
            manager=self.manager,
            container=categories_scrollable
        )

        btn_drop_pod = ui.UIButton(
            relative_rect=pygame.Rect(0, 180, 260, 40),
            text="Drop Pods",
            manager=self.manager,
            container=categories_scrollable
        )

        categories_scrollable.set_scrollable_area_dimensions((260, 225))

        ui.UITextBox(
            relative_rect=pygame.Rect(300, 10, 280, 30),
            html_text="<b>Roles</b>",
            manager=self.manager,
            container=panel
        )

        roles_scrollable = ui.UIScrollingContainer(
            relative_rect=pygame.Rect(300, 45, 280, panel_height - 55),
            manager=self.manager,
            container=panel
        )

        return panel, btn_complex, btn_ship, btn_satellite, btn_fighter, btn_drop_pod, roles_scrollable

    def _create_bottom_bar(self, container: ui.UIPanel, format_empire_resources) -> tuple:
        """Create bottom bar with close button and info.

        Returns:
            Tuple of (bar_panel, btn_close).
        """
        bar_height = 60
        bar_top = self.screen_height - bar_height - 10

        bar = ui.UIPanel(
            relative_rect=pygame.Rect(10, bar_top, self.screen_width - 20, bar_height),
            manager=self.manager,
            container=container,
            object_id="@fast_panel",
        )

        btn_close = ui.UIButton(
            relative_rect=pygame.Rect(10, 10, 120, 40),
            text="Close",
            manager=self.manager,
            container=bar
        )

        empire = self._empire
        if empire and hasattr(empire, 'resource_pool'):
            resource_text = format_empire_resources(empire)
        else:
            resource_text = ""

        ui.UILabel(
            relative_rect=pygame.Rect(150, 10, self.screen_width - 400, 40),
            text=resource_text,
            manager=self.manager,
            container=bar
        )

        turn_number = self._facade.get_turn_number()
        ui.UILabel(
            relative_rect=pygame.Rect(self.screen_width - 200, 10, 180, 40),
            text=f"Turn: {turn_number}",
            manager=self.manager,
            container=bar
        )

        return bar, btn_close
