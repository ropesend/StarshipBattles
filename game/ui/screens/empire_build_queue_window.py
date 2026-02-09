"""Empire-wide build queue window.

Shows all space yards (planet shipyards and fleet yards) across the entire
empire in a unified, scrollable list. Provides queue summary info and
navigation to individual hex build screens.

Created as part of PROJ-76 Phase 2.
Updated in Phase 3: Configurable column system with visibility toggles.
Updated in Phase 4: Filtering (location type, queue status, capabilities, text search).
Updated in Phase 5: Navigation (row click selects, re-click navigates to hex build screen).
Updated in Phase 6: Multi-select (Ctrl+click) and batch add to selected queues.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional, Set, TYPE_CHECKING

import pygame
from pygame_gui.elements import UIButton, UIWindow, UIPanel, UILabel, UIVerticalScrollBar, UITextEntryLine

from game.core.config import UIConfig
from game.core.logger import log_debug
from game.strategy.data.build_queue_source import (
    BuildQueueSource,
    collect_all_build_queues_for_empire,
)

if TYPE_CHECKING:
    from game.strategy.data.empire import Empire


@dataclass
class BatchAddResult:
    """Result of a batch add operation.

    Attributes:
        added: Number of queues the item was added to.
        skipped: Number of queues that were skipped (incompatible).
    """
    added: int
    skipped: int


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
            window_display_title="Empire Build Yards",
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
            {'id': 'build_rate', 'width': 80, 'title': 'Build Rate', 'visible': True},
        ]

        # --- State ---
        self.all_sources: List[BuildQueueSource] = collect_all_build_queues_for_empire(empire)
        self.filtered_sources: List[BuildQueueSource] = list(self.all_sources)
        self.selected_source: Optional[BuildQueueSource] = None
        self.selected_index: int = -1
        self.selected_indices: Set[int] = set()
        self.row_elements: list = []
        self.column_toggle_buttons: Dict[str, UIButton] = {}

        # --- Filter State ---
        self.filter_location_type: Dict[str, bool] = {'Planet': True, 'Fleet': True}
        self.filter_status: Dict[str, bool] = {'Active': True, 'Empty': True}
        self.filter_capabilities: Dict[str, bool] = {'Ships': True, 'Complexes': True}
        self.search_text: str = ""
        self.filter_toggle_buttons: Dict[str, UIButton] = {}
        self.search_entry: Optional[UITextEntryLine] = None

        # --- UI Containers ---
        # Sidebar (column toggles + filters placeholder)
        self.sidebar_panel = UIPanel(
            relative_rect=pygame.Rect(0, 0, self.sidebar_width, rect.height - 50),
            manager=manager,
            container=self,
            anchors={'left': 'left', 'top': 'top', 'bottom': 'bottom'},
        )
        self._build_sidebar_column_toggles(manager)
        self._build_sidebar_filters(manager)

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
    # Navigation
    # -------------------------------------------------------------------

    def get_hex_for_source(self, source: BuildQueueSource) -> Any:
        """Resolve the global hex coordinate for a build queue source.

        For planets, computes system.global_location + planet.location.
        For fleets, returns fleet.location directly.

        Args:
            source: The build queue source to resolve.

        Returns:
            HexCoord for the source, or None if unresolvable.
        """
        entity = source.owner_entity
        if source.context_type == "fleet":
            return getattr(entity, 'location', None)
        if source.context_type == "planet":
            if self.galaxy and hasattr(self.galaxy, 'get_system_of_planet'):
                system = self.galaxy.get_system_of_planet(entity)
                if system is not None:
                    return system.global_location + entity.location
            return None
        return None

    def navigate_to_source(self, source: BuildQueueSource) -> None:
        """Navigate to the hex build screen for a source.

        Resolves the hex coordinate, selects the source, and invokes
        the on_navigate_to_hex callback with (hex_coord, source).
        Does nothing if hex cannot be resolved or no callback is set.

        Args:
            source: The build queue source to navigate to.
        """
        hex_coord = self.get_hex_for_source(source)
        if hex_coord is None:
            return

        # Select the source in our list
        if source in self.filtered_sources:
            idx = self.filtered_sources.index(source)
            self._select_source(idx)

        if self.on_navigate_to_hex:
            log_debug(f"Navigating to hex {hex_coord} for {source.display_name}")
            self.on_navigate_to_hex(hex_coord, source)

    # -------------------------------------------------------------------
    # Multi-Select
    # -------------------------------------------------------------------

    def handle_row_click(self, index: int, ctrl_held: bool = False) -> None:
        """Handle a row click with optional Ctrl modifier for multi-select.

        Single click: select only this index.
        Ctrl+click: toggle this index in the selection set.
        Prevents empty selection on Ctrl+click deselect of last item.

        Args:
            index: Index into filtered_sources.
            ctrl_held: True if Ctrl key was held during click.
        """
        if index < 0 or index >= len(self.filtered_sources):
            return

        if ctrl_held:
            if index in self.selected_indices:
                # Don't allow deselecting the last item
                if len(self.selected_indices) > 1:
                    self.selected_indices.discard(index)
            else:
                self.selected_indices.add(index)
        else:
            self.selected_indices = {index}

        # Update legacy single-selection fields
        if len(self.selected_indices) == 1:
            sole_idx = next(iter(self.selected_indices))
            self.selected_index = sole_idx
            self.selected_source = self.filtered_sources[sole_idx]
        else:
            self.selected_index = -1
            self.selected_source = None

        log_debug(f"Selected {len(self.selected_indices)} queue(s)")

    def get_selected_sources(self) -> List[BuildQueueSource]:
        """Return the BuildQueueSource objects for all selected indices.

        Returns:
            List of selected sources, in index order.
        """
        return [
            self.filtered_sources[i]
            for i in sorted(self.selected_indices)
            if 0 <= i < len(self.filtered_sources)
        ]

    def get_selection_summary(self) -> str:
        """Return a human-readable summary of the current selection.

        Returns:
            Summary string describing what is selected.
        """
        count = len(self.selected_indices)
        if count == 0:
            return "No queues selected"
        if count == 1:
            idx = next(iter(self.selected_indices))
            if 0 <= idx < len(self.filtered_sources):
                name = self.filtered_sources[idx].display_name
                return f"1 queue selected: {name}"
            return "1 queue selected"
        return f"{count} queues selected"

    def batch_add_to_selected(
        self, item: Dict[str, Any], item_type: str,
    ) -> BatchAddResult:
        """Add an item to all selected compatible queues.

        Checks each selected source for compatibility with the item type
        before appending. Ships require can_build_ships, complexes require
        can_build_complexes.

        Args:
            item: Dict with at least 'design_id' and 'turns_remaining'.
            item_type: Either 'ship' or 'complex' to determine compatibility.

        Returns:
            BatchAddResult with added and skipped counts.
        """
        sources = self.get_selected_sources()
        added = 0
        skipped = 0

        for source in sources:
            if self._source_can_build_type(source, item_type):
                # Append a copy so each queue has its own dict
                source.construction_queue.append(dict(item))
                added += 1
            else:
                skipped += 1

        if added > 0:
            log_debug(f"Batch add: added to {added}/{added + skipped} queues")
            self._refresh_list()

        return BatchAddResult(added=added, skipped=skipped)

    @staticmethod
    def _source_can_build_type(source: BuildQueueSource, item_type: str) -> bool:
        """Check if a source can build the given item type.

        Args:
            source: The build queue source to check.
            item_type: 'ship' or 'complex'.

        Returns:
            True if the source can build that type.
        """
        if item_type == "ship":
            return source.can_build_ships
        if item_type == "complex":
            return source.can_build_complexes
        return False

    # -------------------------------------------------------------------
    # Event Handling
    # -------------------------------------------------------------------

    def process_event(self, event: pygame.event.Event) -> bool:
        """Handle mouse clicks on rows, filter toggles, and apply button."""
        handled = super().process_event(event)

        # UI button click handling
        if event.type == pygame.USEREVENT:
            ui_element = getattr(event, 'ui_element', None)
            user_type = getattr(event, 'user_type', None)
            # pygame_gui uses either user_type string or ui_element attribute
            if ui_element is not None and str(user_type) == 'ui_button_pressed':
                # Check column toggles
                self._handle_column_toggle_click(ui_element)
                # Check filter toggles
                self._handle_filter_toggle_click(ui_element)
                # Check apply button
                if hasattr(self, 'btn_apply_filters') and ui_element is self.btn_apply_filters:
                    self._handle_apply_filters_click()
                    return True

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
                    mods = pygame.key.get_mods()
                    ctrl_held = bool(mods & pygame.KMOD_CTRL)

                    if ctrl_held:
                        # Ctrl+click: multi-select toggle
                        self.handle_row_click(clicked_index, ctrl_held=True)
                    elif clicked_index == self.selected_index:
                        # Re-click on already-selected row → navigate
                        self.navigate_to_source(self.filtered_sources[clicked_index])
                    else:
                        # Normal click: single select
                        self.handle_row_click(clicked_index, ctrl_held=False)
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
            return f"{int(source.build_rate)}/turn"
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
    # Filtering
    # -------------------------------------------------------------------

    def _filter_sources(
        self, sources: List[BuildQueueSource],
    ) -> List[BuildQueueSource]:
        """Apply all active filters to a list of sources.

        Filters are combined with AND logic: a source must pass all
        enabled filters to appear in the result.

        Args:
            sources: The full list of sources to filter.

        Returns:
            Filtered list of sources matching all criteria.
        """
        result = list(sources)

        # Location type filter
        result = [
            s for s in result
            if (s.context_type == "planet" and self.filter_location_type.get('Planet', True))
            or (s.context_type == "fleet" and self.filter_location_type.get('Fleet', True))
        ]

        # Queue status filter
        result = [
            s for s in result
            if (len(s.construction_queue) > 0 and self.filter_status.get('Active', True))
            or (len(s.construction_queue) == 0 and self.filter_status.get('Empty', True))
        ]

        # Capabilities filter - show source if ANY of its capabilities match
        # an enabled filter. If all filters are on, show everything.
        if not (self.filter_capabilities.get('Ships', True)
                and self.filter_capabilities.get('Complexes', True)):
            result = [
                s for s in result
                if (s.can_build_ships and self.filter_capabilities.get('Ships', True))
                or (s.can_build_complexes and self.filter_capabilities.get('Complexes', True))
            ]

        # Text search filter
        if self.search_text.strip():
            search_lower = self.search_text.strip().lower()
            result = [
                s for s in result
                if search_lower in s.display_name.lower()
            ]

        return result

    def apply_filters(self) -> None:
        """Re-apply all filters to all_sources and refresh the display.

        Clears the current selection and rebuilds the filtered list
        and row display.
        """
        self.filtered_sources = self._filter_sources(self.all_sources)
        self.selected_source = None
        self.selected_index = -1
        self.selected_indices = set()
        self._refresh_list()

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
    # Sidebar Filter Controls
    # -------------------------------------------------------------------

    def _build_sidebar_filters(self, manager: Any) -> None:
        """Create filter toggle buttons and search box in the sidebar.

        Adds sections for Location Type, Queue Status, Capabilities,
        and a text search entry below the column toggles.

        Args:
            manager: pygame_gui UIManager instance.
        """
        sidebar_w = self.sidebar_width - 20
        # Start below column toggles: header(35) + 8 columns * 35 + gap
        y_off = 40 + len(self.columns) * 35 + 15

        # --- Location Type ---
        UILabel(
            relative_rect=pygame.Rect(10, y_off, sidebar_w, 25),
            text="LOCATION TYPE",
            manager=manager,
            container=self.sidebar_panel,
        )
        y_off += 30
        for key in ('Planet', 'Fleet'):
            prefix = "[x]" if self.filter_location_type[key] else "[ ]"
            btn = UIButton(
                relative_rect=pygame.Rect(10, y_off, sidebar_w, 30),
                text=f"{prefix} {key}",
                manager=manager,
                container=self.sidebar_panel,
            )
            self.filter_toggle_buttons[f"loc_{key}"] = btn
            y_off += 35

        y_off += 10

        # --- Queue Status ---
        UILabel(
            relative_rect=pygame.Rect(10, y_off, sidebar_w, 25),
            text="QUEUE STATUS",
            manager=manager,
            container=self.sidebar_panel,
        )
        y_off += 30
        for key in ('Active', 'Empty'):
            prefix = "[x]" if self.filter_status[key] else "[ ]"
            btn = UIButton(
                relative_rect=pygame.Rect(10, y_off, sidebar_w, 30),
                text=f"{prefix} {key}",
                manager=manager,
                container=self.sidebar_panel,
            )
            self.filter_toggle_buttons[f"status_{key}"] = btn
            y_off += 35

        y_off += 10

        # --- Capabilities ---
        UILabel(
            relative_rect=pygame.Rect(10, y_off, sidebar_w, 25),
            text="CAPABILITIES",
            manager=manager,
            container=self.sidebar_panel,
        )
        y_off += 30
        for key in ('Ships', 'Complexes'):
            prefix = "[x]" if self.filter_capabilities[key] else "[ ]"
            btn = UIButton(
                relative_rect=pygame.Rect(10, y_off, sidebar_w, 30),
                text=f"{prefix} {key}",
                manager=manager,
                container=self.sidebar_panel,
            )
            self.filter_toggle_buttons[f"cap_{key}"] = btn
            y_off += 35

        y_off += 10

        # --- Text Search ---
        UILabel(
            relative_rect=pygame.Rect(10, y_off, sidebar_w, 25),
            text="SEARCH",
            manager=manager,
            container=self.sidebar_panel,
        )
        y_off += 30
        self.search_entry = UITextEntryLine(
            relative_rect=pygame.Rect(10, y_off, sidebar_w, 30),
            manager=manager,
            container=self.sidebar_panel,
        )
        y_off += 40

        # --- Apply Button ---
        self.btn_apply_filters = UIButton(
            relative_rect=pygame.Rect(10, y_off, sidebar_w, 35),
            text="Apply Filters",
            manager=manager,
            container=self.sidebar_panel,
        )

    def _handle_filter_toggle_click(self, button: UIButton) -> None:
        """Handle a filter toggle button click.

        Identifies which filter the button controls, toggles its state,
        updates the button text, and re-applies filters.

        Args:
            button: The UIButton that was clicked.
        """
        for filter_key, btn in self.filter_toggle_buttons.items():
            if btn is not button:
                continue

            # Parse filter key: "loc_Planet", "status_Active", "cap_Ships"
            parts = filter_key.split("_", 1)
            category = parts[0]
            value = parts[1]

            if category == "loc":
                self.filter_location_type[value] = not self.filter_location_type[value]
                state = self.filter_location_type[value]
            elif category == "status":
                self.filter_status[value] = not self.filter_status[value]
                state = self.filter_status[value]
            elif category == "cap":
                self.filter_capabilities[value] = not self.filter_capabilities[value]
                state = self.filter_capabilities[value]
            else:
                return

            prefix = "[x]" if state else "[ ]"
            btn.set_text(f"{prefix} {value}")
            self.apply_filters()
            return

    def _handle_apply_filters_click(self) -> None:
        """Handle the Apply Filters button click.

        Reads the search text entry and re-applies all filters.
        """
        if self.search_entry is not None:
            self.search_text = self.search_entry.get_text()
        self.apply_filters()

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
