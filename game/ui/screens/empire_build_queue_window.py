"""Empire-wide build queue window.

Shows all space yards (planet shipyards and fleet yards) across the entire
empire in a unified, scrollable list. Provides queue summary info and
navigation to individual hex build screens.

Created as part of PROJ-76 Phase 2.
Updated in Phase 3: Configurable column system with visibility toggles.
Updated in Phase 4: Filtering (location type, queue status, capabilities, text search).
Updated in Phase 5: Navigation (row click selects, re-click navigates to hex build screen).
Updated in Phase 6: Multi-select (Ctrl+click) and batch add to selected queues.
Updated in PROJ-172 Phase 3: MVVM extraction (ViewModel + Sidebar).
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional, Set, TYPE_CHECKING

import pygame
import pygame_gui
from pygame_gui.elements import UIWindow, UIPanel

from game.ui.config import UIConfig
import logging

logger = logging.getLogger(__name__)
from game.strategy.data.build_queue_source import (
    BuildQueueSource,
    collect_all_build_queues_for_empire,
)
from game.ui.screens.builder.event_bus import EventBus
from game.ui.screens.empire_build_queue_viewmodel import (
    EmpireBuildQueueViewModel,
    BuildQueueWindowEvents,
)
from game.ui.screens.empire_build_queue_sidebar import EmpireBuildQueueSidebar
from game.ui.screens.empire_build_queue_filter_manager import BuildQueueFilterManager
from game.ui.screens.empire_build_queue_data_source import BuildQueueDataSource
from game.ui.components.table import VirtualTable, TableColumnManager, MultiSelect
from game.ui.screens.empire_build_queue_formatter import (
    get_system_name,
    get_sector_text,
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

    Uses MVVM pattern: ViewModel owns state, Sidebar owns filter UI,
    Window coordinates rendering and navigation.

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

        # --- MVVM components ---
        self._event_bus = EventBus()
        sources = collect_all_build_queues_for_empire(empire)
        self._viewmodel = EmpireBuildQueueViewModel(self._event_bus, sources)

        # --- Filter Manager (for column definitions) ---
        self._filter_mgr = BuildQueueFilterManager()

        # --- UI Containers ---
        # Sidebar panel
        self.sidebar_panel = UIPanel(
            relative_rect=pygame.Rect(0, 0, self.sidebar_width, rect.height - 50),
            manager=manager,
            container=self,
            anchors={'left': 'left', 'top': 'top', 'bottom': 'bottom'},
        )

        # Sidebar component (owns filter UI)
        self._sidebar = EmpireBuildQueueSidebar(
            ui_manager=manager,
            parent_container=self.sidebar_panel,
            viewmodel=self._viewmodel,
            event_bus=self._event_bus,
            columns=self._filter_mgr.columns,
        )

        # Main content area
        main_w = rect.width - self.sidebar_width - 10
        self.main_panel = UIPanel(
            relative_rect=pygame.Rect(self.sidebar_width, 0, main_w, rect.height - 50),
            manager=manager,
            container=self,
            anchors={'left': 'left', 'right': 'right', 'top': 'top', 'bottom': 'bottom'},
        )

        # --- VirtualTable components ---
        self._data_source = BuildQueueDataSource(
            self._viewmodel, self._filter_mgr, self.galaxy
        )
        self._column_manager = TableColumnManager(self._filter_mgr.columns)
        self._selection = MultiSelect()
        self._virtual_table = VirtualTable(
            self.main_panel,
            manager,
            self._data_source,
            self._column_manager,
            self._selection,
            row_height=self.row_height,
            header_height=self.header_height,
        )

        # Store references for backward compatibility with tests
        self.scroll_bar = self._virtual_table.scroll_bar
        self.column_mgr = self._column_manager  # Alias for tests

        # Subscribe to ViewModel events
        self._event_bus.subscribe(
            BuildQueueWindowEvents.FILTERS_APPLIED,
            lambda _: self._on_filters_applied()
        )
        self._event_bus.subscribe(
            BuildQueueWindowEvents.SELECTION_CHANGED,
            lambda _: self._on_selection_changed()
        )

        # Initial population
        self._refresh_list()

    # -----------------------------------------------------------------------
    # Public API facade (delegates to ViewModel)
    # -----------------------------------------------------------------------

    @property
    def all_sources(self) -> List[BuildQueueSource]:
        """All sources (unfiltered)."""
        return self._viewmodel.all_sources

    @property
    def filtered_sources(self) -> List[BuildQueueSource]:
        """Filtered sources."""
        return self._viewmodel.filtered_sources

    @property
    def selected_source(self) -> Optional[BuildQueueSource]:
        """Single selected source, or None if zero/multiple selected."""
        sources = self._viewmodel.get_selected_sources()
        return sources[0] if len(sources) == 1 else None

    @property
    def selected_index(self) -> int:
        """Single selected index, or -1 if zero/multiple selected."""
        indices = self._viewmodel.selected_indices
        return next(iter(indices)) if len(indices) == 1 else -1

    @property
    def selected_indices(self) -> Set[int]:
        """Set of selected indices."""
        return self._viewmodel.selected_indices

    @selected_indices.setter
    def selected_indices(self, value: Set[int]) -> None:
        """Set selected indices."""
        self._viewmodel.selected_indices = value

    @property
    def filter_location_type(self) -> Dict[str, bool]:
        """Location type filter state."""
        return self._viewmodel.filter_location_type

    @filter_location_type.setter
    def filter_location_type(self, value: Dict[str, bool]) -> None:
        """Set location type filter."""
        self._viewmodel.filter_location_type = value

    @property
    def filter_status(self) -> Dict[str, bool]:
        """Queue status filter state."""
        return self._viewmodel.filter_status

    @filter_status.setter
    def filter_status(self, value: Dict[str, bool]) -> None:
        """Set queue status filter."""
        self._viewmodel.filter_status = value

    @property
    def filter_capabilities(self) -> Dict[str, bool]:
        """Capabilities filter state."""
        return self._viewmodel.filter_capabilities

    @filter_capabilities.setter
    def filter_capabilities(self, value: Dict[str, bool]) -> None:
        """Set capabilities filter."""
        self._viewmodel.filter_capabilities = value

    @property
    def search_text(self) -> str:
        """Search text."""
        return self._viewmodel.search_text

    @search_text.setter
    def search_text(self, value: str) -> None:
        """Set search text."""
        self._viewmodel.set_search_text(value)

    @property
    def columns(self) -> List[Dict[str, Any]]:
        """Column definitions (read-only access to filter manager's columns)."""
        return self._filter_mgr.columns

    @property
    def column_toggle_buttons(self) -> Dict[str, Any]:
        """Column toggle button dict from sidebar (read-only)."""
        return self._sidebar.column_toggle_buttons

    @property
    def filter_toggle_buttons(self) -> Dict[str, Any]:
        """Filter toggle button dict from sidebar (read-only)."""
        return self._sidebar.filter_toggle_buttons

    @property
    def search_entry(self) -> Any:
        """Search entry widget from sidebar (read-only)."""
        return self._sidebar.search_entry

    @property
    def btn_apply_filters(self) -> Any:
        """Apply filters button from sidebar (read-only)."""
        return self._sidebar.btn_apply_filters

    # -----------------------------------------------------------------------
    # Event Handlers
    # -----------------------------------------------------------------------

    def _on_filters_applied(self) -> None:
        """Handle filters applied event."""
        self._refresh_list()

    def _on_selection_changed(self) -> None:
        """Handle selection changed event."""
        pass  # Could update UI indicators

    # -----------------------------------------------------------------------
    # List Population
    # -----------------------------------------------------------------------

    def _refresh_list(self) -> None:
        """Update VirtualTable scroll and visible rows."""
        # Sync selection from ViewModel to VirtualTable's selection strategy
        self._selection.set_selected(self._viewmodel.selected_indices)

        # Update table
        self._virtual_table.update_scroll_bar()
        self._virtual_table.force_update()
        self._virtual_table.update_visible_rows()

    # -----------------------------------------------------------------------
    # Selection (delegated to ViewModel)
    # -----------------------------------------------------------------------

    def _select_source(self, index: int) -> None:
        """Select a source by index."""
        self._viewmodel.select_source(index, ctrl_held=False)
        if self.selected_source:
            logger.debug(f"Selected queue source: {self.selected_source.display_name}")

    def handle_row_click(self, index: int, ctrl_held: bool = False) -> None:
        """Handle a row click with optional Ctrl modifier."""
        self._viewmodel.select_source(index, ctrl_held=ctrl_held)
        logger.debug(f"Selected {len(self._viewmodel.selected_indices)} queue(s)")

    def get_selected_sources(self) -> List[BuildQueueSource]:
        """Return selected sources."""
        return self._viewmodel.get_selected_sources()

    def get_selection_summary(self) -> str:
        """Return selection summary."""
        return self._viewmodel.get_selection_summary()

    # -----------------------------------------------------------------------
    # Navigation
    # -----------------------------------------------------------------------

    def get_hex_for_source(self, source: BuildQueueSource) -> Any:
        """Resolve the global hex coordinate for a build queue source."""
        entity = source.owner_entity
        if source.context_type == "fleet":
            return entity.location
        if source.context_type == "planet":
            if self.galaxy:
                system = self.galaxy.get_system_of_planet(entity)
                if system is not None:
                    return system.global_location + entity.location
            return None
        return None

    def navigate_to_source(self, source: BuildQueueSource) -> None:
        """Navigate to the hex build screen for a source."""
        hex_coord = self.get_hex_for_source(source)
        if hex_coord is None:
            return
        if source in self.filtered_sources:
            idx = self.filtered_sources.index(source)
            self._select_source(idx)
        if self.on_navigate_to_hex:
            logger.debug(f"Navigating to hex {hex_coord} for {source.display_name}")
            self.on_navigate_to_hex(hex_coord, source)

    # -----------------------------------------------------------------------
    # Batch Operations
    # -----------------------------------------------------------------------

    def batch_add_to_selected(
        self, item: Dict[str, Any], item_type: str,
    ) -> BatchAddResult:
        """Add an item to all selected compatible queues."""
        sources = self.get_selected_sources()
        added = 0
        skipped = 0
        for source in sources:
            if self._source_can_build_type(source, item_type):
                source.construction_queue.append(dict(item))
                added += 1
            else:
                skipped += 1
        if added > 0:
            logger.debug(f"Batch add: added to {added}/{added + skipped} queues")
            self._refresh_list()
        return BatchAddResult(added=added, skipped=skipped)

    @staticmethod
    def _source_can_build_type(source: BuildQueueSource, item_type: str) -> bool:
        """Check if a source can build the given item type."""
        if item_type == "ship":
            return source.can_build_ships
        if item_type == "complex":
            return source.can_build_complexes
        return False

    # -----------------------------------------------------------------------
    # Event Handling
    # -----------------------------------------------------------------------

    def process_event(self, event: pygame.event.Event) -> bool:
        """Handle mouse clicks on rows, filter toggles, and apply button."""
        handled = super().process_event(event)

        # UI button click handling - delegate to sidebar
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if self._sidebar.handle_button_click(event.ui_element):
                # Sidebar handled it - check if column toggle
                for col_id in self._sidebar.column_toggle_buttons:
                    if self._sidebar.column_toggle_buttons[col_id] is event.ui_element:
                        self._virtual_table.rebuild_headers()
                        self._virtual_table.rebuild_row_pool()
                        self._refresh_list()
                        break
                return True

        # Row click detection via VirtualTable
        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            mouse_pos = event.pos
            clicked_index = self._virtual_table.find_clicked_row(mouse_pos)
            if clicked_index >= 0:
                mods = pygame.key.get_mods()
                ctrl_held = bool(mods & pygame.KMOD_CTRL)
                prev_selected = self.selected_index
                # Handle click via ViewModel (syncs to VirtualTable)
                self.handle_row_click(clicked_index, ctrl_held=ctrl_held)
                # Sync selection to VirtualTable
                self._selection.set_selected(self._viewmodel.selected_indices)
                self._virtual_table.update_visible_rows()
                # Re-click on same row = navigate
                if not ctrl_held and clicked_index == prev_selected:
                    self.navigate_to_source(self.filtered_sources[clicked_index])
                return True

        # Mouse wheel scrolling - handled by VirtualTable's scroll bar
        if event.type == pygame.MOUSEWHEEL:
            m_pos = pygame.mouse.get_pos()
            # Check if within table area
            table_rect = self.main_panel.get_abs_rect()
            if table_rect.collidepoint(m_pos):
                total_h = len(self.filtered_sources) * self.row_height
                if total_h > 0:
                    row_percent = self.row_height / total_h
                    current_pct = self.scroll_bar.start_percentage
                    new_pct = current_pct - (event.y * row_percent)
                    new_pct = max(0.0, min(1.0 - self.scroll_bar.visible_percentage, new_pct))
                    self.scroll_bar.set_scroll_from_start_percentage(new_pct)
                    self._virtual_table.update_visible_rows()
                return True

        return handled

    def update(self, time_delta: float) -> None:
        """Update loop - check scrollbar and header button changes."""
        super().update(time_delta)

        # Check header buttons for sort/swap changes
        header_result = self._virtual_table.check_header_presses()
        sort_col = header_result.get('sort_column')
        swap_col = header_result.get('swap_column')

        if sort_col or swap_col:
            if sort_col:
                self._column_manager.set_sort(sort_col)
            self._apply_sort_and_refresh()

        # Update visible rows if scroll position changed
        if self.scroll_bar.check_has_moved_recently():
            self._virtual_table.update_visible_rows()

    # -----------------------------------------------------------------------
    # Column System
    # -----------------------------------------------------------------------

    def _get_visible_columns(self) -> List[Dict[str, Any]]:
        """Return list of currently visible columns."""
        return self._filter_mgr.get_visible_columns()

    def _get_column_value(self, source: BuildQueueSource, col_id: str) -> str:
        """Return the display value for a column and source."""
        # System and sector need galaxy reference
        if col_id == 'system':
            return get_system_name(source, self.galaxy)
        if col_id == 'sector':
            return get_sector_text(source)
        # Delegate to ViewModel for other columns
        return self._viewmodel.get_column_value(source, col_id)

    def toggle_column_visibility(self, col_id: str) -> bool:
        """Toggle visibility of a column by ID."""
        return self._filter_mgr.toggle_column_visibility(col_id)

    # -----------------------------------------------------------------------
    # Filtering (delegated to ViewModel)
    # -----------------------------------------------------------------------

    def _filter_sources(
        self, sources: List[BuildQueueSource],
    ) -> List[BuildQueueSource]:
        """Apply all active filters to a list of sources."""
        # Sync state to ViewModel's filter manager
        self._viewmodel._filter_mgr.filter_location_type = self.filter_location_type
        self._viewmodel._filter_mgr.filter_status = self.filter_status
        self._viewmodel._filter_mgr.filter_capabilities = self.filter_capabilities
        self._viewmodel._filter_mgr.search_text = self.search_text
        return self._viewmodel._filter_mgr.filter_sources(sources)

    def apply_filters(self) -> None:
        """Re-apply all filters and refresh display."""
        # Sync state to ViewModel
        self._viewmodel._filter_mgr.filter_location_type = self.filter_location_type
        self._viewmodel._filter_mgr.filter_status = self.filter_status
        self._viewmodel._filter_mgr.filter_capabilities = self.filter_capabilities
        self._viewmodel._filter_mgr.search_text = self.search_text
        self._viewmodel.apply_filters()

    def _apply_sort_and_refresh(self) -> None:
        """Apply current sort order and refresh display."""
        self._viewmodel._filter_mgr.sort_sources(
            self._viewmodel._filtered_sources,
            self._column_manager.sort_column_id,
            self._column_manager.sort_descending,
            self._get_column_value,
        )
        self._refresh_list()

    # -----------------------------------------------------------------------
    # Data Formatters (delegates to formatter module)
    # -----------------------------------------------------------------------

    @staticmethod
    def _get_queue_summary(source: BuildQueueSource) -> str:
        """Return a short summary of queue contents."""
        from game.ui.screens.empire_build_queue_formatter import get_queue_summary
        return get_queue_summary(source)

    @staticmethod
    def _get_first_item_text(source: BuildQueueSource) -> str:
        """Return the name of the first item being built."""
        from game.ui.screens.empire_build_queue_formatter import get_first_item_text
        return get_first_item_text(source)

    @staticmethod
    def _get_capabilities_text(source: BuildQueueSource) -> str:
        """Return human-readable capabilities string."""
        from game.ui.screens.empire_build_queue_formatter import get_capabilities_text
        return get_capabilities_text(source)

    def _get_system_name(self, source: BuildQueueSource) -> str:
        """Return the system name for a queue source."""
        return get_system_name(source, self.galaxy)

    @staticmethod
    def _get_sector_text(source: BuildQueueSource) -> str:
        """Return sector/hex coordinate text for a queue source."""
        return get_sector_text(source)

    @staticmethod
    def _get_turns_left_text(source: BuildQueueSource) -> str:
        """Return turns remaining for the first item in queue."""
        from game.ui.screens.empire_build_queue_formatter import get_turns_left_text
        return get_turns_left_text(source)

    # -----------------------------------------------------------------------
    # Cleanup
    # -----------------------------------------------------------------------

    def kill(self) -> None:
        """Clean up and invoke close callback."""
        self._virtual_table.kill()
        if self.on_close_callback:
            self.on_close_callback()
        super().kill()
