"""Renderer for BuildQueueScreen.

Handles rendering of queue items and design list. Extracted from build_queue_screen.py
as part of PROJ-172 Phase 4 MVVM refactoring.
PROJ-221 Phase 4: Simplified queue display to use VirtualTable.
"""
from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Dict, List, Optional

import pygame
import pygame_gui.elements as ui

from game.ui.screens.build_queue_helpers import format_resource_cost

if TYPE_CHECKING:
    from game.ui.screens.build_queue_panel_factory import BuildQueuePanels
    from game.ui.panels.build_queue_portraits import BuildQueuePortraitLoader

logger = logging.getLogger(__name__)


class BuildQueueRenderer:
    """Renderer for BuildQueueScreen display elements.

    Handles:
    - Refreshing the items list (available designs)
    - Refreshing the queue display via VirtualTable
    - Updating queue header text

    Does not own state - receives data from ViewModel.
    PROJ-221: Queue display delegated to VirtualTable (selection handled there).
    """

    def __init__(
        self,
        manager,
        panels: 'BuildQueuePanels',
        portrait_loader: 'BuildQueuePortraitLoader',
    ):
        """Initialize the renderer.

        Args:
            manager: pygame_gui UIManager.
            panels: BuildQueuePanels container with all UI elements.
            portrait_loader: BuildQueuePortraitLoader for design icons.
        """
        self.manager = manager
        self.panels = panels
        self.portrait_loader = portrait_loader

    def refresh_items_list(self, designs: List, selected_category: str) -> None:
        """Refresh the available designs list.

        Args:
            designs: List of design objects to display.
            selected_category: Current category filter for context.
        """
        scrollable = self.panels.items_scrollable

        # Clear existing items
        elements_to_kill = list(scrollable.get_container().elements)
        for element in elements_to_kill:
            element.kill()

        y_offset = 0
        icon_size = 36
        btn_height = 40

        for design in designs:
            raw_cost = getattr(design, 'construction_cost', None)
            cost = raw_cost if isinstance(raw_cost, dict) else {}
            row_height = btn_height + (18 if cost else 0)

            row_panel = ui.UIPanel(
                relative_rect=pygame.Rect(0, y_offset, 260, row_height),
                manager=self.manager,
                container=scrollable,
                object_id="#design_row_panel"
            )

            portrait_surface = self.portrait_loader.load_design_portrait(design, icon_size)
            if portrait_surface:
                ui.UIImage(
                    relative_rect=pygame.Rect(2, 2, icon_size, icon_size),
                    image_surface=portrait_surface,
                    manager=self.manager,
                    container=row_panel
                )

            display_name = design.name
            if not getattr(design, 'design_valid', True):
                display_name = f"{design.name} (INVD)"

            btn = ui.UIButton(
                relative_rect=pygame.Rect(icon_size + 4, 0, 260 - icon_size - 8, btn_height),
                text=display_name,
                manager=self.manager,
                container=row_panel
            )
            btn.design_id = design.design_id
            row_panel.design_id = design.design_id

            if cost:
                cost_str = format_resource_cost(cost)
                ui.UILabel(
                    relative_rect=pygame.Rect(icon_size + 4, btn_height, 260 - icon_size - 8, 20),
                    text=cost_str,
                    manager=self.manager,
                    container=row_panel
                )

            y_offset += row_height + 5

        if not designs:
            ui.UILabel(
                relative_rect=pygame.Rect(10, 10, 240, 30),
                text="No designs available",
                manager=self.manager,
                container=scrollable
            )

    def refresh_queue_display(
        self,
        queue: List[dict],
        build_rate: Dict[str, float],
        on_queue_selector_refresh=None,
    ) -> None:
        """Refresh the build queue display via VirtualTable.

        PROJ-221 Phase 4: Simplified to update data source and VirtualTable.

        Args:
            queue: List of queue item dicts.
            build_rate: Production rate per turn for the active queue.
            on_queue_selector_refresh: Callback to refresh queue selector counts.
        """
        data_source = self.panels.data_source
        virtual_table = self.panels.virtual_table

        # Update data source with current queue and rates
        data_source.set_queue(queue, build_rate)

        # Refresh VirtualTable display
        virtual_table.update_scroll_bar()
        virtual_table.force_update()
        virtual_table.update_visible_rows()

        if on_queue_selector_refresh:
            on_queue_selector_refresh()

    def update_queue_header(self, active_source) -> None:
        """Update build queue header text.

        Args:
            active_source: Active BuildQueueSource, or None for multi-select.
        """
        if active_source is not None:
            header_text = f"<b>Build Queue - {active_source.display_name}</b>"
        else:
            header_text = "<b>Build Queue</b>"
        self.panels.queue_header_text.set_text(header_text)

