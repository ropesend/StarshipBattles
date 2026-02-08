"""Empire-wide build queue window.

Shows all space yards (planet shipyards and fleet yards) across the entire
empire in a unified, scrollable list. Provides queue summary info and
navigation to individual hex build screens.

Created as part of PROJ-76 Phase 2.
Updated in Phase 3: Configurable column system with visibility toggles.
"""
from __future__ import annotations

from typing import Any, Callable, Dict, List, Optional, TYPE_CHECKING

import pygame
from pygame_gui.elements import UIButton, UIWindow, UIPanel, UILabel, UIVerticalScrollBar

from game.core.config import UIConfig
from game.core.logger import log_debug
from game.strategy.data.build_queue_source import (
    BuildQueueSource,
    collect_all_build_queues_for_empire,
)

if TYPE_CHECKING:
    from game.strategy.data.empire import Empire


class EmpireBuildQueueWindow(UIWindow):
    """Window showing all empire build queues in a scrollable list.

    Displays every space yard (planet base queues, planetary shipyard
    facilities, fleet space yards) with queue summary info. Clicking a
    row selects it; navigation to the hex build screen is handled via
    callback in a later phase.

    Args:
        rect: Window rectangle on screen.
        manager: pygame_gui UIManager instance.
        empire: Empire whose queues to display.
        galaxy: Galaxy instance for system name lookups.
        on_close_callback: Called when window is closed.
        on_navigate_to_hex: Called with (hex_coord, source) when user
            navigates to a specific queue.
    """

    def __init__(
        self,
        rect: pygame.Rect,
        manager: Any,
        empire: Empire,
        galaxy: Any,
        on_close_callback: Optional[Callable] = None,
        on_navigate_to_hex: Optional[Callable] = None,
    ) -> None:
        super().__init__(
            rect, manager,
            window_display_title="Empire Build Queues",
            resizable=True,
        )

        self.empire = empire
        self.galaxy = galaxy
        self.on_close_callback = on_close_callback
        self.on_navigate_to_hex = on_navigate_to_hex

        # --- Layout constants ---
        self.sidebar_width = UIConfig.SIDEBAR_WIDTH
        self.header_height = UIConfig.HEADER_HEIGHT
        self.row_height = UIConfig.ROW_HEIGHT_LARGE

        # --- Column Definitions ---
        self.columns: List[Dict[str, Any]] = [
            {'id': 'location', 'width': 180, 'title': 'Location', 'visible': True},
            {'id': 'system', 'width': 120, 'title': 'System', 'visible': True},
            {'id': 'sector', 'width': 80, 'title': 'Sector', 'visible': True},
            {'id': 'queue_count', 'width': 80, 'title': 'Items', 'visible': True},
            {'id': 'first_item', 'width': 150, 'title': 'Building', 'visible': True},
            {'id': 'turns_left', 'width': 80, 'title': 'Turns', 'visible': True},
            {'id': 'capabilities', 'width': 100, 'title': 'Can Build', 'visible': True},
            {'id': 'build_rate', 'width': 80, 'title': 'Rate/Turn', 'visible': False},
        ]

        # --- State ---
        self.all_sources: List[BuildQueueSource] = collect_all_build_queues_for_empire(empire)
        self.filtered_sources: List[BuildQueueSource] = list(self.all_sources)
        self.selected_source: Optional[BuildQueueSource] = None
        self.selected_index: int = -1
        self.row_elements: list = []
        self.column_toggle_buttons: Dict[str, UIButton] = {}

        # --- UI Containers ---
        # Sidebar (column toggles + filters placeholder)
        self.sidebar_panel = UIPanel(
            relative_rect=pygame.Rect(0, 0, self.sidebar_width, rect.height - 50),
            manager=manager,
            container=self,
            anchors={'left': 'left', 'top': 'top', 'bottom': 'bottom'},
        )
        self._build_sidebar_column_toggles(manager)

        # Main content area
        main_w = rect.width - self.sidebar_width - 10
        self.main_panel = UIPanel(
            relative_rect=pygame.Rect(self.sidebar_width, 0, main_w, rect.height - 50),
            manager=manager,
            container=self,
            anchors={'left': 'left', 'right': 'right', 'top': 'top', 'bottom': 'bottom'},
        )

        # Header row for column titles
        self.header_container = UIPanel(
            relative_rect=pygame.Rect(0, 0, main_w, self.header_height),
            manager=manager,
            container=self.main_panel,
            anchors={'left': 'left', 'right': 'right', 'top': 'top'},
        )
        self._build_header_labels(manager, main_w)

        # Scrollable list area
        self.list_view_rect = pygame.Rect(
            0, self.header_height,
            main_w - 20, rect.height - 50 - self.header_height,
        )
        self.list_panel = UIPanel(
            relative_rect=self.list_view_rect,
            manager=manager,
            container=self.main_panel,
            anchors={'left': 'left', 'right': 'right', 'top': 'top', 'bottom': 'bottom'},
        )

        # Vertical scrollbar
        self.scroll_bar = UIVerticalScrollBar(
            relative_rect=pygame.Rect(
                -20, self.header_height, 20, self.list_view_rect.height,
            ),
            visible_percentage=1.0,
            manager=manager,
            container=self.main_panel,
            anchors={'left': 'right', 'right': 'right', 'top': 'top', 'bottom': 'bottom'},
        )

        # Initial population
        self._refresh_list()

    # -------------------------------------------------------------------
    # Header
    # -------------------------------------------------------------------

    def _build_header_labels(self, manager: Any, main_w: int) -> None:
        """Create column title labels in the header from visible columns."""
        # Clear existing header labels
        for child in getattr(self, '_header_labels', []):
            child.kill()
        self._header_labels: list = []

        x = 10
        for col in self._get_visible_columns():
            lbl = UILabel(
                relative_rect=pygame.Rect(x, 5, col['width'], 30),
                text=col['title'],
                manager=manager,
                container=self.header_container,
            )
            self._header_labels.append(lbl)
            x += col['width'] + 10

    # -------------------------------------------------------------------
    # List Population
    # -------------------------------------------------------------------

    def _refresh_list(self) -> None:
        """Rebuild the visible row list from filtered_sources."""
        # Kill existing row elements
        for elem in self.row_elements:
            elem.kill()
        self.row_elements.clear()

        # Update scrollbar
        total_h = len(self.filtered_sources) * self.row_height
        visible_h = self.list_view_rect.height
        percentage = min(1.0, visible_h / total_h) if total_h > 0 else 1.0
        self.scroll_bar.set_visible_percentage(percentage)
        self.scroll_bar.scroll_position = 0.0
        self.scroll_bar.bottom_limit = max(visible_h, total_h)
        self.scroll_bar.redraw_scrollbar()

        # Create row labels using column configuration
        visible_cols = self._get_visible_columns()
        for i, source in enumerate(self.filtered_sources):
            y = i * self.row_height
            x = 10

            for col in visible_cols:
                text = self._get_column_value(source, col['id'])
                lbl = UILabel(
                    relative_rect=pygame.Rect(x, y, col['width'], self.row_height),
                    text=text,
                    manager=self.ui_manager,
                    container=self.list_panel,
                )
                self.row_elements.append(lbl)
                x += col['width'] + 10

    # -------------------------------------------------------------------
    # Selection
    # -------------------------------------------------------------------

    def _select_source(self, index: int) -> None:
        """Select a source by index in filtered_sources.

        Args:
            index: Index into filtered_sources. Invalid indices are ignored.
        """
        if index < 0 or index >= len(self.filtered_sources):
            return
        self.selected_index = index
        self.selected_source = self.filtered_sources[index]
        log_debug(f"Selected queue source: {self.selected_source.display_name}")

    # -------------------------------------------------------------------
    # Event Handling
    # -------------------------------------------------------------------

    def process_event(self, event: pygame.event.Event) -> bool:
        """Handle mouse clicks on rows."""
        handled = super().process_event(event)

        # Row click detection
        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            mouse_pos = event.pos
            list_abs_rect = self.list_panel.get_abs_rect()

            if list_abs_rect.collidepoint(mouse_pos):
                # Calculate which row was clicked
                scroll_offset = 0.0
                total_h = len(self.filtered_sources) * self.row_height
                if total_h > 0:
                    scroll_offset = self.scroll_bar.start_percentage * total_h

                local_y = mouse_pos[1] - list_abs_rect.y + scroll_offset
                clicked_index = int(local_y // self.row_height)

                if 0 <= clicked_index < len(self.filtered_sources):
                    self._select_source(clicked_index)
                    return True

        # Mouse wheel scrolling
        if event.type == pygame.MOUSEWHEEL:
            m_pos = pygame.mouse.get_pos()
            if self.list_panel.get_abs_rect().collidepoint(m_pos):
                total_h = len(self.filtered_sources) * self.row_height
                if total_h > 0:
                    row_percent = self.row_height / total_h
                    current_pct = self.scroll_bar.start_percentage
                    new_pct = current_pct - (event.y * row_percent)
                    new_pct = max(0.0, min(1.0 - self.scroll_bar.visible_percentage, new_pct))
                    self.scroll_bar.set_scroll_from_start_percentage(new_pct)
                return True

        return handled

    def update(self, time_delta: float) -> None:
        """Update loop - check scrollbar changes."""
        super().update(time_delta)

        if self.scroll_bar.check_has_moved_recently():
            # Future: update visible rows for virtual scrolling
            pass

    # -------------------------------------------------------------------
    # Data Formatters
    # -------------------------------------------------------------------

    @staticmethod
    def _get_queue_summary(source: BuildQueueSource) -> str:
        """Return a short summary of queue contents.

        Args:
            source: The build queue source to summarize.

        Returns:
            Dash if empty, otherwise item count string.
        """
        count = len(source.construction_queue)
        if count == 0:
            return "-"
        return f"{count} item{'s' if count != 1 else ''}"

    @staticmethod
    def _get_first_item_text(source: BuildQueueSource) -> str:
        """Return the name of the first item being built.

        Args:
            source: The build queue source.

        Returns:
            Design ID of first item, or dash if empty.
        """
        if not source.construction_queue:
            return "-"
        first = source.construction_queue[0]
        design_id = first.get("design_id", "Unknown")
        turns = first.get("turns_remaining", "?")
        return f"{design_id} ({turns}t)"

    @staticmethod
    def _get_capabilities_text(source: BuildQueueSource) -> str:
        """Return human-readable capabilities string.

        Args:
            source: The build queue source.

        Returns:
            'Ships', 'Complexes', 'Ships & Complexes', or 'None'.
        """
        if source.can_build_ships and source.can_build_complexes:
            return "Ships & Complexes"
        if source.can_build_ships:
            return "Ships"
        if source.can_build_complexes:
            return "Complexes"
        return "None"

    # -------------------------------------------------------------------
    # Column System
    # -------------------------------------------------------------------

    def _get_visible_columns(self) -> List[Dict[str, Any]]:
        """Return list of currently visible columns.

        Returns:
            List of column dicts where visible is True.
        """
        return [c for c in self.columns if c.get('visible', True)]

    def _get_column_value(self, source: BuildQueueSource, col_id: str) -> str:
        """Return the display value for a column and source.

        Args:
            source: The build queue source to extract data from.
            col_id: Column identifier string.

        Returns:
            Human-readable string value for the cell.
        """
        if col_id == 'location':
            return source.display_name
        if col_id == 'system':
            return self._get_system_name(source)
        if col_id == 'sector':
            return self._get_sector_text(source)
        if col_id == 'queue_count':
            return self._get_queue_summary(source)
        if col_id == 'first_item':
            return self._get_first_item_text(source)
        if col_id == 'turns_left':
            return self._get_turns_left_text(source)
        if col_id == 'capabilities':
            return self._get_capabilities_text(source)
        if col_id == 'build_rate':
            return "1/turn"
        return ""

    def toggle_column_visibility(self, col_id: str) -> bool:
        """Toggle visibility of a column by ID.

        Args:
            col_id: ID of the column to toggle.

        Returns:
            True if visibility was toggled, False if column not found.
        """
        for col in self.columns:
            if col['id'] == col_id:
                col['visible'] = not col['visible']
                return True
        return False

    # -------------------------------------------------------------------
    # Sidebar Column Toggles
    # -------------------------------------------------------------------

    def _build_sidebar_column_toggles(self, manager: Any) -> None:
        """Create column visibility toggle buttons in the sidebar.

        Args:
            manager: pygame_gui UIManager instance.
        """
        sidebar_w = self.sidebar_width - 20

        UILabel(
            relative_rect=pygame.Rect(10, 10, sidebar_w, 25),
            text="COLUMNS",
            manager=manager,
            container=self.sidebar_panel,
        )

        y_off = 40
        for col in self.columns:
            prefix = "[x]" if col['visible'] else "[ ]"
            label = col['title'] or col['id']
            btn = UIButton(
                relative_rect=pygame.Rect(10, y_off, sidebar_w, 30),
                text=f"{prefix} {label}",
                manager=manager,
                container=self.sidebar_panel,
            )
            self.column_toggle_buttons[col['id']] = btn
            y_off += 35

    def _handle_column_toggle_click(self, button: UIButton) -> None:
        """Handle a column toggle button click.

        Finds which column the button corresponds to, toggles its
        visibility, updates the button text, and rebuilds the display.

        Args:
            button: The UIButton that was clicked.
        """
        for col_id, btn in self.column_toggle_buttons.items():
            if btn is button:
                self.toggle_column_visibility(col_id)
                col = next(c for c in self.columns if c['id'] == col_id)
                prefix = "[x]" if col['visible'] else "[ ]"
                label = col['title'] or col['id']
                btn.set_text(f"{prefix} {label}")
                # Rebuild header and list with new column visibility
                self._build_header_labels(self.ui_manager, 0)
                self._refresh_list()
                return

    # -------------------------------------------------------------------
    # Additional Data Formatters
    # -------------------------------------------------------------------

    def _get_system_name(self, source: BuildQueueSource) -> str:
        """Return the system name for a queue source.

        Args:
            source: The build queue source.

        Returns:
            System name string, or dash if unavailable.
        """
        entity = source.owner_entity
        if source.context_type == "planet":
            system = getattr(entity, 'system_name', None)
            if system:
                return str(system)
            # Try galaxy lookup
            if self.galaxy and hasattr(self.galaxy, 'get_system_of_planet'):
                sys_obj = self.galaxy.get_system_of_planet(entity)
                if sys_obj:
                    return getattr(sys_obj, 'name', '-')
        elif source.context_type == "fleet":
            location = getattr(entity, 'location', None)
            if location and self.galaxy and hasattr(self.galaxy, 'get_system_at_hex'):
                sys_obj = self.galaxy.get_system_at_hex(location)
                if sys_obj:
                    return getattr(sys_obj, 'name', '-')
        return "-"

    @staticmethod
    def _get_sector_text(source: BuildQueueSource) -> str:
        """Return sector/hex coordinate text for a queue source.

        Args:
            source: The build queue source.

        Returns:
            Hex coordinate string, or dash if unavailable.
        """
        entity = source.owner_entity
        if source.context_type == "fleet":
            location = getattr(entity, 'location', None)
            if location is not None:
                return str(location)
        elif source.context_type == "planet":
            # Planets may have hex or relative location
            hex_loc = getattr(entity, 'global_hex', None) or getattr(entity, 'location', None)
            if hex_loc is not None:
                return str(hex_loc)
        return "-"

    @staticmethod
    def _get_turns_left_text(source: BuildQueueSource) -> str:
        """Return turns remaining for the first item in queue.

        Args:
            source: The build queue source.

        Returns:
            Turns remaining string, or dash if empty.
        """
        if not source.construction_queue:
            return "-"
        first = source.construction_queue[0]
        turns = first.get("turns_remaining", "?")
        return f"{turns}t"

    # -------------------------------------------------------------------
    # Cleanup
    # -------------------------------------------------------------------

    def kill(self) -> None:
        """Clean up and invoke close callback."""
        for elem in self.row_elements:
            elem.kill()
        self.row_elements.clear()

        if self.on_close_callback:
            self.on_close_callback()

        super().kill()
