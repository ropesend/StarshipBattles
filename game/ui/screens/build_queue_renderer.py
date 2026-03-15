"""Renderer for BuildQueueScreen.

Handles rendering of queue items and design list. Extracted from build_queue_screen.py
as part of PROJ-172 Phase 4 MVVM refactoring.
"""
from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Dict, List, Optional, Set

import pygame
import pygame_gui.elements as ui

from game.core.constants import PLANET_RESOURCES
from game.ui.screens.build_queue_helpers import format_resource_cost
from game.ui.colors import TEAM_1_TEXT

if TYPE_CHECKING:
    from game.ui.screens.build_queue_panel_factory import BuildQueuePanels
    from game.ui.panels.build_queue_portraits import BuildQueuePortraitLoader

logger = logging.getLogger(__name__)


class BuildQueueRenderer:
    """Renderer for BuildQueueScreen display elements.

    Handles:
    - Refreshing the items list (available designs)
    - Refreshing the queue display (current build queue)
    - Drawing selection highlights and drag previews

    Does not own state - receives data from ViewModel.
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

        # Queue item panels (rebuilt on each refresh)
        self.queue_items: List = []

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
            raw_cost = getattr(design, 'resource_cost', None)
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

            btn = ui.UIButton(
                relative_rect=pygame.Rect(icon_size + 4, 0, 260 - icon_size - 8, btn_height),
                text=design.name,
                manager=self.manager,
                container=row_panel
            )
            btn.design_id = design.design_id
            row_panel.design_id = design.design_id

            if cost:
                cost_str = format_resource_cost(cost)
                ui.UILabel(
                    relative_rect=pygame.Rect(icon_size + 4, btn_height, 260 - icon_size - 8, 16),
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
        selected_queue_index: Optional[int],
        is_multi_select: bool,
        selected_sources: List = None,
        on_queue_selector_refresh = None,
    ) -> List:
        """Refresh the build queue display.

        Args:
            queue: List of queue item dicts.
            selected_queue_index: Currently selected item index.
            is_multi_select: True if multiple queue sources are selected.
            selected_sources: List of selected sources for multi-select display.
            on_queue_selector_refresh: Callback to refresh queue selector counts.

        Returns:
            List of queue item panels for selection tracking.
        """
        scrollable = self.panels.queue_scrollable
        column_positions = self.panels.queue_column_positions

        # Clear existing queue items
        elements_to_kill = list(scrollable.get_container().elements)
        for element in elements_to_kill:
            element.kill()
        self.queue_items = []

        # Multi-select mode: show message instead of queue contents
        if is_multi_select and selected_sources:
            selected_names = [s.display_name for s in selected_sources]
            msg_lines = "<br>".join(f"- {name}" for name in selected_names)
            ui.UITextBox(
                relative_rect=pygame.Rect(10, 10, scrollable.get_container().get_size()[0] - 20, 200),
                html_text=f"<b>Adding to {len(selected_sources)} queues:</b><br>{msg_lines}",
                manager=self.manager,
                container=scrollable
            )
            if on_queue_selector_refresh:
                on_queue_selector_refresh()
            return self.queue_items

        # Display each item in the queue
        y_offset = 0
        icon_size = 40

        for idx, item in enumerate(queue):
            design_id = item.get("design_id", "Unknown")
            turns = item.get("turns_remaining", 0)
            item_type = item.get("type", "ship")

            is_selected = (idx == selected_queue_index)
            panel_object_id = "#queue_item_selected" if is_selected else "#queue_item"

            total_cost = item.get("total_cost")
            panel_height = 48

            item_panel = ui.UIPanel(
                relative_rect=pygame.Rect(0, y_offset, scrollable.get_container().get_size()[0] - 20, panel_height),
                manager=self.manager,
                container=scrollable,
                object_id=panel_object_id
            )
            item_panel.queue_index = idx
            item_panel.item_data = item
            item_panel.is_selected = is_selected

            portrait_surface = self.portrait_loader.load_queue_item_portrait(design_id, item_type, icon_size)
            if portrait_surface:
                ui.UIImage(
                    relative_rect=pygame.Rect(4, 4, icon_size, icon_size),
                    image_surface=portrait_surface,
                    manager=self.manager,
                    container=item_panel
                )

            name_x = icon_size + 8
            ui.UILabel(
                relative_rect=pygame.Rect(name_x, 14, 400, 20),
                text=f"{design_id} ({item_type})",
                manager=self.manager,
                container=item_panel
            )

            turns_x = column_positions.get("Turns", 165) - 10
            ui.UILabel(
                relative_rect=pygame.Rect(turns_x, 14, 45, 20),
                text=f"{turns}",
                manager=self.manager,
                container=item_panel
            )

            if total_cost and turns > 0:
                resources_consumed = item.get("resources_consumed", {})
                for resource in PLANET_RESOURCES:
                    total_amt = total_cost.get(resource, 0)
                    consumed = resources_consumed.get(resource, 0)
                    remaining = max(0, total_amt - consumed)
                    if remaining > 0:
                        col_x = column_positions.get(resource, 0) - 10
                        if remaining >= 1:
                            cost_text = f"{int(remaining)}"
                        else:
                            cost_text = f"{remaining:.1f}"
                        ui.UILabel(
                            relative_rect=pygame.Rect(col_x, 14, 50, 20),
                            text=cost_text,
                            manager=self.manager,
                            container=item_panel
                        )

            self.queue_items.append(item_panel)
            y_offset += panel_height + 3

        if not queue:
            ui.UILabel(
                relative_rect=pygame.Rect(10, 10, 300, 30),
                text="Queue is empty",
                manager=self.manager,
                container=scrollable
            )

        if on_queue_selector_refresh:
            on_queue_selector_refresh()

        return self.queue_items

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

    def draw_selection_highlight(
        self,
        screen: pygame.Surface,
        selected_queue_index: Optional[int],
    ) -> None:
        """Draw selection highlight on selected queue item.

        Args:
            screen: pygame surface to draw on.
            selected_queue_index: Currently selected item index.
        """
        if selected_queue_index is None:
            return

        for item_panel in self.queue_items:
            if getattr(item_panel, 'queue_index', -1) == selected_queue_index:
                abs_rect = item_panel.get_abs_rect()
                pygame.draw.rect(screen, TEAM_1_TEXT, abs_rect, 3)
                break
