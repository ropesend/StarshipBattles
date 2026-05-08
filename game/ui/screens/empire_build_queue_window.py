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
from pygame_gui.elements import UIPanel

from game.ui.config import UIConfig
from game.ui.screens.strategy_modal_window import StrategyModalWindow
import logging

logger = logging.getLogger(__name__)
from game.strategy.data.build_queue_source import (
    BuildQueueSource,
    collect_all_build_queues_for_empire,
)
from game.ui.screens.builder.event_bus import WorkshopEventBus
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
    from game.ui.screens.strategy_window_manager import StrategyWindowManager


@dataclass
class BatchAddResult:
    """Result of a batch add operation.

    Attributes:
        added: Number of queues the item was added to.
        skipped: Number of queues that were skipped (incompatible).
    """
    added: int
    skipped: int


class EmpireBuildQueueUiBuilder:
    """Production widget builder. Constructs sidebar_panel, sidebar
    component, main_panel, virtual_table, wires event-bus subscribers,
    and triggers the initial _refresh_list. Reads Stage-1 MVVM state.
    """

    def build(self, screen: "EmpireBuildQueueWindow") -> None:
        rect = screen.rect
        manager = screen.ui_manager

        # --- UI Containers ---
        # Sidebar panel
        screen.sidebar_panel = UIPanel(
            relative_rect=pygame.Rect(0, 0, screen.sidebar_width, rect.height - 50),
            manager=manager,
            container=screen,
            anchors={'left': 'left', 'top': 'top', 'bottom': 'bottom'},
        )

        # Sidebar component (owns filter UI)
        screen._sidebar = EmpireBuildQueueSidebar(
            ui_manager=manager,
            parent_container=screen.sidebar_panel,
            viewmodel=screen._viewmodel,
            event_bus=screen._event_bus,
            columns=screen._filter_mgr.columns,
        )

        # Main content area
        main_w = rect.width - screen.sidebar_width - 10
        screen.main_panel = UIPanel(
            relative_rect=pygame.Rect(screen.sidebar_width, 0, main_w, rect.height - 50),
            manager=manager,
            container=screen,
            anchors={'left': 'left', 'right': 'right', 'top': 'top', 'bottom': 'bottom'},
        )

        # --- VirtualTable components ---
        screen._data_source = BuildQueueDataSource(
            screen._viewmodel, screen._filter_mgr, screen.galaxy
        )
        screen._column_manager = TableColumnManager(screen._filter_mgr.columns)
        screen._selection = MultiSelect()
        screen._virtual_table = VirtualTable(
            screen.main_panel,
            manager,
            screen._data_source,
            screen._column_manager,
            screen._selection,
            row_height=screen.row_height,
            header_height=screen.header_height,
        )

        # Store reference for scroll wheel handling
        screen.scroll_bar = screen._virtual_table.scroll_bar

        # Subscribe to ViewModel events
        screen._event_bus.subscribe(
            BuildQueueWindowEvents.FILTERS_APPLIED,
            lambda _: screen._on_filters_applied(),
        )
        screen._event_bus.subscribe(
            BuildQueueWindowEvents.SELECTION_CHANGED,
            lambda _: screen._on_selection_changed(),
        )

        # Initial population
        screen._refresh_list()


class EmpireBuildQueueWindow(StrategyModalWindow):
    """Window showing all empire build queues in a scrollable list.

    Uses MVVM pattern: ViewModel owns state, Sidebar owns filter UI,
    Window coordinates rendering and navigation.

    PROJ-313: Migrated to StrategyModalWindow. Auto-registers with the
    window manager for modal tracking.

    Args:
        rect: Window rectangle on screen.
        manager: pygame_gui UIManager instance.
        empire: Empire whose queues to display.
        galaxy: Galaxy instance for system name lookups.
        window_manager: PROJ-313 StrategyWindowManager (or None outside the strategy screen).
        on_close_callback: Called when window is closed (registrar slot cleanup).
        on_navigate_to_hex: Called with (hex_coord, source) when user
            navigates to a specific queue.
    """

    def __init__(
        self,
        rect: pygame.Rect,
        manager: Any,
        empire: Empire,
        galaxy: Any,
        *,
        window_manager: "StrategyWindowManager",
        on_close_callback: Optional[Callable] = None,
        on_navigate_to_hex: Optional[Callable] = None,
        facade: Any,
        ui_builder: Optional["EmpireBuildQueueUiBuilder"] = None,
    ) -> None:
        """Initialize the empire build queue window.

        PROJ-208 Phase 3: Added facade parameter for CQRS-compliant command dispatch.
        PROJ-313: Migrated to StrategyModalWindow base class.
        PROJ-329B Phase 2: two-stage construction with ``ui_builder`` test seam.
        PROJ-382 Phase 1: ``facade`` is required; ``session=`` kwarg removed.
        """
        # ---- Stage 1: cheap state ----
        self.empire = empire
        self.galaxy = galaxy
        self.on_close_callback = on_close_callback
        self.on_navigate_to_hex = on_navigate_to_hex
        # PROJ-208 / PROJ-382 Phase 1: command dispatch through facade only.
        self._facade = facade

        # --- Layout constants ---
        self.sidebar_width = UIConfig.SIDEBAR_WIDTH
        self.header_height = UIConfig.HEADER_HEIGHT
        self.row_height = UIConfig.ROW_HEIGHT_LARGE

        # --- MVVM components --- (cheap; pure-python, no pygame_gui)
        self._event_bus = WorkshopEventBus()
        sources = collect_all_build_queues_for_empire(
            empire, registries=facade.get_registries()
        )
        self._viewmodel = EmpireBuildQueueViewModel(self._event_bus, sources)

        # --- Filter Manager (for column definitions) ---
        self._filter_mgr = BuildQueueFilterManager()

        # MAJ-001 fix (review req_20260504_220257_d0b194): Pattern §33
        # widget-ref placeholders. Initialized to None here so that a
        # NullEmpireBuildQueueWindowUiBuilder test can safely call kill()
        # without AttributeError on `self._virtual_table.kill()` etc.
        # The production builder overwrites these in Stage 3.
        self.sidebar_panel = None
        self.main_panel = None
        self._sidebar = None
        self._virtual_table = None
        self.scroll_bar = None
        self._data_source = None
        self._column_manager = None
        self._selection = None

        # ---- Stage 2: shell ----
        super().__init__(
            rect, manager,
            window_display_title="Empire Build Yards",
            resizable=True,
            window_manager=window_manager,
        )

        # ---- Stage 3: widgets ----
        if getattr(self, '_window_init_bypassed', False):
            if ui_builder is not None:
                ui_builder.build(self)
            return

        (ui_builder or EmpireBuildQueueUiBuilder()).build(self)

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
        """Add an item to all selected compatible queues.

        PROJ-208: Routes additions through AddToConstructionQueueCommand when session available.
        """
        sources = self.get_selected_sources()
        added = 0
        skipped = 0
        for source in sources:
            if self._source_can_build_type(source, item_type):
                self._add_item_to_source(source, item, item_type)
                added += 1
            else:
                skipped += 1
        if added > 0:
            logger.debug(f"Batch add: added to {added}/{added + skipped} queues")
            self._refresh_list()
        return BatchAddResult(added=added, skipped=skipped)

    def _add_item_to_source(
        self, source: BuildQueueSource, item: Dict[str, Any], item_type: str
    ) -> None:
        """Add item to a source's queue via command or direct append.

        PROJ-208: Routes through AddToConstructionQueueCommand when session available.
        PROJ-208 Phase 3: Prefers facade over session for CQRS consistency.
        """
        # PROJ-208: Use getattr for test compatibility (tests may bypass __init__)
        # PROJ-382 Phase 1: facade-only dispatch.
        facade = getattr(self, '_facade', None)
        if facade is not None:
            from game.strategy.engine.commands import AddToConstructionQueueCommand, BuildEntityType
            entity = source.owner_entity
            entity_type = BuildEntityType.PLANET if hasattr(entity, 'planet_type') else BuildEntityType.FLEET
            entity_id = getattr(entity, 'id', 0)
            design_id = item.get('design_id', '')
            cmd = AddToConstructionQueueCommand(
                entity_id=entity_id,
                entity_type=entity_type,
                design_id=design_id,
                category=item_type,
                index=None,  # Append
                target_planet_id=item.get('target_planet_id'),
                queue_id=source.queue_id if source.queue_id else None,
            )
            facade.handle_command(cmd)
        else:
            # Legacy fallback for tests without facade injection
            source.construction_queue.append(dict(item))

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
        """Update loop - check scrollbar, header, and tri-state filter changes."""
        super().update(time_delta)

        # Check tri-state filter widgets
        self._sidebar.check_tri_state_presses()

        # Check header buttons for sort/swap changes
        header_result = self._virtual_table.check_header_presses()
        swap_col = header_result.get('swap_column')
        sort_col = header_result.get('sort_column')

        if swap_col:
            col_dict, direction = swap_col
            self._column_manager.swap_column(col_dict['id'], direction)
            self._virtual_table.rebuild_headers()
            self._virtual_table.rebuild_row_pool()
            self._refresh_list()
        elif sort_col:
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

    def apply_filters(self) -> None:
        """Re-apply all filters and refresh display."""
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
        """Clean up and invoke close callback.

        MAJ-001 fix (review req_20260504_220257_d0b194): guard against
        None _virtual_table to support Null-builder tests that bypass
        Stage 3 widget construction.
        """
        if self._virtual_table is not None:
            self._virtual_table.kill()
        if self.on_close_callback:
            self.on_close_callback()
        super().kill()
