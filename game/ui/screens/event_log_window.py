"""Event Log Window - Displays game events with category filter tabs.

PROJ-77 Phase 4: Modal window showing turn events (production, colonies, combat).
PROJ-188 Phase 5: Migrated to VirtualTable with EventLogDataSource.
Supports filter tabs and scrollable event list sorted newest first.
FEAT-26: Per-row Replay button on combat events with a captured replay.
"""
from __future__ import annotations

import logging
from typing import Any, Callable, Optional, TYPE_CHECKING

import pygame
import pygame_gui
from pygame_gui.elements import UIPanel, UIButton
from pygame_gui.windows import UIMessageWindow

from game.core.profiling import profile_action
from game.ui.components.table import VirtualTable, TableColumnManager, NoSelect
from game.ui.screens.event_log_data_source import (
    EventLogDataSource,
    EVENT_LOG_COLUMNS,
)
from game.ui.screens.event_log_sidebar import EventLogSidebar
from game.ui.screens.strategy_modal_window import StrategyModalWindow

if TYPE_CHECKING:
    from game.simulation.replay import ReplayRecord
    from game.strategy.services.replay_resolver import ReplayResolver
    from game.ui.screens.strategy_window_manager import StrategyWindowManager

logger = logging.getLogger(__name__)


# FEAT-26: tooltip / dialog text for ReplayResolver graceful-degradation.
_REPLAY_REASON_MESSAGES = {
    "missing": "Replay not available — file missing or evicted.",
    "corrupt": "Replay file is corrupt and cannot be played.",
    "version_drift": "Replay was captured under a different game version.",
}
_REPLAY_DRIFT_TITLE = "Replay version drift"
_REPLAY_DRIFT_MESSAGE = (
    "This replay was captured under a different components.json and may "
    "not play back accurately. Continuing anyway."
)
_REPLAY_NOT_AVAILABLE_TITLE = "Replay unavailable"


# ---------------------------------------------------------------------------
# Layout constants
# ---------------------------------------------------------------------------
HEADER_HEIGHT = 50
ROW_HEIGHT = 28
TABLE_HEADER_HEIGHT = 30
FILTER_BTN_WIDTH = 100
FILTER_BTN_HEIGHT = 32
FILTER_GAP = 8
SIDEBAR_WIDTH = 180


DOUBLE_CLICK_THRESHOLD_MS = 400


class EventLogUiBuilder:
    """Production widget builder. Constructs sidebar_panel, header_panel
    + filter buttons, table_panel + VirtualTable, sidebar component, and
    triggers the initial _rebuild_list. Reads Stage-1 state (all_events,
    current_filter).
    """

    def build(self, screen: "EventLogWindow") -> None:
        screen._init_layout()
        screen._rebuild_list()


class EventLogWindow(StrategyModalWindow):
    """Modal window displaying game events with filter tabs.

    Shows events in a scrollable list sorted newest-first.
    Filter tabs allow viewing All, Combat, Production, Colonies, or Fleet Ops events.
    Double-clicking a row with location data navigates the camera to that location.

    PROJ-313: Migrated to StrategyModalWindow base class.
    BUG-123: ``empire_name`` (optional) surfaces the active empire in
    the window title so players can confirm per-empire scoping is active.

    Args:
        rect: Window position and size.
        manager: pygame_gui UIManager instance.
        events: List of event dicts (from facade).
        window_manager: PROJ-313 StrategyWindowManager (or None outside the strategy screen).
        on_close_callback: Called when the window is closed (registrar slot cleanup).
        on_navigate_callback: Called with [q, r] hex coords when user
            double-clicks an event row that has location data.
        empire_name: BUG-123 — when set, the window title becomes
            ``"Event Log — <empire_name> Empire"``. None falls back to
            the plain ``"Event Log"`` title (back-compat for callers
            that don't supply it, including tests).
    """

    @profile_action("Panel: EventLog.init")
    def __init__(
        self,
        rect: pygame.Rect,
        manager: Any,
        events: list[dict],
        *,
        window_manager: "StrategyWindowManager",
        on_close_callback: Optional[Callable] = None,
        on_navigate_callback: Optional[Callable] = None,
        empire_name: Optional[str] = None,
        replay_resolver: "Optional[ReplayResolver]" = None,
        launch_replay_callback: "Optional[Callable[[ReplayRecord], None]]" = None,
        ui_builder: Optional[EventLogUiBuilder] = None,
    ) -> None:
        # ---- Stage 1: cheap state ----
        # PROJ-411 Task 1.9: hold a reference rather than a defensive
        # copy. ``facade.get_all_events()`` already returns a fresh
        # per-call list (``[e.to_dict() for e in events]``), and the
        # ``EventLogDataSource`` constructor still defensively copies
        # at the data-source boundary — so a window-level copy is pure
        # waste. The window never mutates ``self.all_events`` after
        # construction.
        self.all_events = events
        self.current_filter = "all"
        self.on_close_callback = on_close_callback
        self.on_navigate_callback = on_navigate_callback
        # FEAT-26: replay launch wiring.
        self._replay_resolver = replay_resolver
        self._launch_replay_callback = launch_replay_callback

        # Double-click tracking
        self._last_click_time: int = 0
        self._last_click_row: int = -1

        # VirtualTable components (populated by builder)
        self.data_source: Optional[EventLogDataSource] = None
        self.column_manager: Optional[TableColumnManager] = None
        self.virtual_table: Optional[VirtualTable] = None

        # Sidebar component (populated by builder)
        self.sidebar: Optional[EventLogSidebar] = None

        # ---- Stage 2: shell ----
        title = (
            f"Event Log — {empire_name} Empire"
            if empire_name
            else "Event Log"
        )
        super().__init__(
            rect=rect,
            manager=manager,
            window_display_title=title,
            resizable=True,
            window_manager=window_manager,
        )

        # ---- Stage 3: widgets ----
        if getattr(self, '_window_init_bypassed', False):
            if ui_builder is not None:
                ui_builder.build(self)
            return

        (ui_builder or EventLogUiBuilder()).build(self)

    # ------------------------------------------------------------------
    # Layout
    # ------------------------------------------------------------------

    def _init_layout(self) -> None:
        """Create sidebar, filter header and table panel with VirtualTable."""
        window_rect = self.get_container().get_rect()
        content_height = window_rect.height - 50  # title bar offset

        # Sidebar panel on the left
        self.sidebar_panel = UIPanel(
            relative_rect=pygame.Rect(0, 0, SIDEBAR_WIDTH, content_height),
            manager=self.ui_manager,
            container=self,
            anchors={"left": "left", "top": "top", "bottom": "bottom"},
        )

        # Header panel with filter buttons (right of sidebar)
        header_width = window_rect.width - SIDEBAR_WIDTH
        self.header_panel = UIPanel(
            relative_rect=pygame.Rect(SIDEBAR_WIDTH, 0, header_width, HEADER_HEIGHT),
            manager=self.ui_manager,
            container=self,
            anchors={"left": "left", "right": "right", "top": "top"},
        )
        self._create_filter_buttons()

        # Table panel below header, right of sidebar (contains VirtualTable)
        table_height = content_height - HEADER_HEIGHT
        table_width = window_rect.width - SIDEBAR_WIDTH
        self.table_panel = UIPanel(
            relative_rect=pygame.Rect(SIDEBAR_WIDTH, HEADER_HEIGHT, table_width, table_height),
            manager=self.ui_manager,
            container=self,
            anchors={
                "left": "left",
                "right": "right",
                "top": "top",
                "bottom": "bottom",
            },
        )

        # Create VirtualTable components
        self.data_source = EventLogDataSource(self.all_events, self.current_filter)
        self.column_manager = TableColumnManager(EVENT_LOG_COLUMNS)
        self.virtual_table = VirtualTable(
            self.table_panel,
            self.ui_manager,
            self.data_source,
            self.column_manager,
            NoSelect(),
            row_height=ROW_HEIGHT,
            header_height=TABLE_HEADER_HEIGHT,
        )

        # Create sidebar with column toggles
        self.sidebar = EventLogSidebar(
            panel=self.sidebar_panel,
            manager=self.ui_manager,
            column_manager=self.column_manager,
        )

    def _create_filter_buttons(self) -> None:
        """Create filter tab buttons in the header."""
        x = 10
        y = (HEADER_HEIGHT - FILTER_BTN_HEIGHT) // 2

        self.btn_all = UIButton(
            relative_rect=pygame.Rect(x, y, FILTER_BTN_WIDTH, FILTER_BTN_HEIGHT),
            text="All",
            manager=self.ui_manager,
            container=self.header_panel,
        )
        x += FILTER_BTN_WIDTH + FILTER_GAP

        self.btn_combat = UIButton(
            relative_rect=pygame.Rect(x, y, FILTER_BTN_WIDTH, FILTER_BTN_HEIGHT),
            text="Combat",
            manager=self.ui_manager,
            container=self.header_panel,
        )
        x += FILTER_BTN_WIDTH + FILTER_GAP

        self.btn_production = UIButton(
            relative_rect=pygame.Rect(x, y, FILTER_BTN_WIDTH, FILTER_BTN_HEIGHT),
            text="Production",
            manager=self.ui_manager,
            container=self.header_panel,
        )
        x += FILTER_BTN_WIDTH + FILTER_GAP

        self.btn_colonies = UIButton(
            relative_rect=pygame.Rect(x, y, FILTER_BTN_WIDTH, FILTER_BTN_HEIGHT),
            text="Colonies",
            manager=self.ui_manager,
            container=self.header_panel,
        )
        x += FILTER_BTN_WIDTH + FILTER_GAP

        self.btn_fleet_ops = UIButton(
            relative_rect=pygame.Rect(x, y, FILTER_BTN_WIDTH, FILTER_BTN_HEIGHT),
            text="Fleet Ops",
            manager=self.ui_manager,
            container=self.header_panel,
        )

        self.filter_buttons = {
            "all": self.btn_all,
            "combat": self.btn_combat,
            "production": self.btn_production,
            "colonies": self.btn_colonies,
            "fleet_operations": self.btn_fleet_ops,
        }

        # Highlight the default active filter
        self.btn_all.select()

    # ------------------------------------------------------------------
    # Filtering
    # ------------------------------------------------------------------

    def get_filtered_events(self) -> list[dict]:
        """Return events matching current filter, sorted newest first.

        Delegates to DataSource for consistency.

        Returns:
            Filtered and sorted list of event dicts.
        """
        if self.data_source:
            # Delegate to data source's filtered list
            return [
                self.data_source.get_event_at_index(i)
                for i in range(self.data_source.get_row_count())
            ]

        # Fallback for tests without VirtualTable
        if self.current_filter == "all":
            filtered = list(self.all_events)
        else:
            filtered = [
                e for e in self.all_events if e.get("category") == self.current_filter
            ]
        filtered.sort(key=lambda e: e.get("turn", 0), reverse=True)
        return filtered

    def set_filter(self, category: str) -> None:
        """Switch the active filter category.

        Args:
            category: One of 'all', 'combat', 'production', 'colonies', 'fleet_operations'.
        """
        self.current_filter = category
        if self.data_source:
            self.data_source.set_filter(category)

    # ------------------------------------------------------------------
    # List Rendering
    # ------------------------------------------------------------------

    @profile_action("Panel: EventLog.rebuild_data_source")
    def _rebuild_list(self) -> None:
        """Update VirtualTable with current filter."""
        if self.data_source:
            self.data_source.set_filter(self.current_filter)
        if self.virtual_table:
            self.virtual_table.update_scroll_bar()
            self.virtual_table.force_update()
            self.virtual_table.update_visible_rows()

    def _update_filter_buttons(self) -> None:
        """Highlight the currently active filter button."""
        for key, btn in self.filter_buttons.items():
            if key == self.current_filter:
                btn.select()
            else:
                btn.unselect()

    # ------------------------------------------------------------------
    # Update loop
    # ------------------------------------------------------------------

    def update(self, time_delta: float) -> None:
        """Update loop - check header presses for column swap/sort."""
        super().update(time_delta)

        if not self.virtual_table:
            return

        # Check header buttons for sort/swap changes
        header_result = self.virtual_table.check_header_presses()
        swap_col = header_result.get('swap_column')
        sort_col = header_result.get('sort_column')

        if swap_col:
            col_dict, direction = swap_col
            self.column_manager.swap_column(col_dict['id'], direction)
            self.virtual_table.rebuild_headers()
            self.virtual_table.rebuild_row_pool()
            self._rebuild_list()
        elif sort_col:
            self.column_manager.set_sort(sort_col)
            self.virtual_table.rebuild_headers()
            self._rebuild_list()

        # Update visible rows if scroll position changed
        if self.virtual_table.scroll_bar.check_has_moved_recently():
            self.virtual_table.update_visible_rows()

    # ------------------------------------------------------------------
    # Events
    # ------------------------------------------------------------------

    def process_event(self, event: pygame.event.Event) -> bool:
        """Handle UI events for filter button clicks, column toggles, and row double-clicks."""
        handled = super().process_event(event)

        if hasattr(event, "type") and event.type == pygame_gui.UI_BUTTON_PRESSED:
            clicked = getattr(event, "ui_element", None)

            # Check filter buttons
            for key, btn in self.filter_buttons.items():
                if clicked is btn:
                    self.set_filter(key)
                    self._update_filter_buttons()
                    self._rebuild_list()
                    handled = True
                    break

            # Check sidebar column toggle buttons
            if not handled and self.sidebar:
                col_id = self.sidebar.handle_button_click(clicked)
                if col_id:
                    self.column_manager.toggle_column(col_id)
                    self.sidebar.refresh_button_labels()
                    self.virtual_table.rebuild_headers()
                    self.virtual_table.rebuild_row_pool()
                    self.virtual_table.force_update()
                    self.virtual_table.update_visible_rows()
                    handled = True

            # FEAT-26: per-row Replay button (replay_action column).
            if not handled and self.virtual_table is not None:
                action_match = self.virtual_table.check_action_button_press(
                    clicked
                )
                if action_match is not None:
                    action, row_idx = action_match
                    if action == "replay" and row_idx >= 0:
                        self._handle_replay_click(row_idx)
                        handled = True

        # FEAT-04: Double-click on row navigates to event location
        if (
            hasattr(event, "type")
            and event.type == pygame.MOUSEBUTTONUP
            and event.button == 1
            and self.virtual_table
        ):
            row_idx = self.virtual_table.find_clicked_row(event.pos)
            if row_idx >= 0:
                now = pygame.time.get_ticks()
                if (
                    row_idx == self._last_click_row
                    and (now - self._last_click_time) < DOUBLE_CLICK_THRESHOLD_MS
                ):
                    self._handle_row_navigate(row_idx)
                    self._last_click_row = -1
                    self._last_click_time = 0
                    handled = True
                else:
                    self._last_click_row = row_idx
                    self._last_click_time = now

        return handled

    def _handle_replay_click(self, row_index: int) -> None:
        """FEAT-26: dispatch a Replay button click for the row.

        Reads the row's ``replay_id`` from the data source. When present,
        invokes ``ReplayResolver.resolve(...)`` and routes by the
        ``ReplayLookup`` result:

        - ``found=True, registry_drift=False`` → fire the launch callback.
        - ``found=True, registry_drift=True`` → surface a drift warning
          dialog AND launch (clean-sheet: drift is informational, not
          blocking — playback may visually diverge but won't crash).
        - ``found=False`` → surface the reason via a UIMessageWindow.

        No-ops cleanly when ``replay_id`` is None (legacy combat row),
        or when no resolver / launch callback is wired (tests, headless).
        """
        if self.data_source is None:
            return
        replay_id = self.data_source.get_cell_replay_id(row_index)
        if not replay_id:
            return
        if self._replay_resolver is None:
            logger.debug(
                "FEAT-26 replay click ignored — no ReplayResolver wired."
            )
            return

        lookup = self._replay_resolver.resolve(replay_id)

        if not lookup.found:
            reason = lookup.reason or "missing"
            message = _REPLAY_REASON_MESSAGES.get(
                reason,
                f"Replay unavailable ({reason}).",
            )
            self._show_replay_message(_REPLAY_NOT_AVAILABLE_TITLE, message)
            return

        # PROJ-368 (post-r002): verification_status is intentionally NOT a
        # launch gate. It is a determinism diagnostic; a FAILED/ERROR sidecar
        # means the headless re-run diverged from the captured outcome, not
        # that the captured replay is unwatchable. Resolver loadability
        # (handled above) remains the only launch precondition.

        if lookup.registry_drift:
            self._show_replay_message(
                _REPLAY_DRIFT_TITLE, _REPLAY_DRIFT_MESSAGE
            )

        if self._launch_replay_callback is not None and lookup.record is not None:
            self._launch_replay_callback(lookup.record)

    def _show_replay_message(self, title: str, message: str) -> None:
        """FEAT-26: surface a graceful-degradation message to the user.

        Uses ``UIMessageWindow`` (the project's standard modal dialog).
        Sized centred over the Event Log window.
        """
        try:
            container_rect = self.get_container().get_rect()
        except Exception:  # Intentional broad catch: pygame_gui internals may not be ready in test contexts
            container_rect = pygame.Rect(0, 0, 600, 200)
        w, h = 480, 180
        dialog_rect = pygame.Rect(
            container_rect.centerx - w // 2,
            container_rect.centery - h // 2,
            w,
            h,
        )
        UIMessageWindow(
            rect=dialog_rect,
            html_message=message,
            manager=self.ui_manager,
            window_title=title,
        )

    def _handle_row_navigate(self, row_index: int) -> None:
        """Navigate to the location of an event row.

        Extracts location_hex from the event's details and calls the
        navigate callback if location data is present.

        Args:
            row_index: Index of the double-clicked row in filtered data.
        """
        if not self.data_source:
            return

        event = self.data_source.get_event_at_index(row_index)
        if event is None:
            return

        details = event.get("details", {})
        location_hex = details.get("location_hex")
        if location_hex and self.on_navigate_callback:
            self.on_navigate_callback(location_hex)

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    # ---- PROJ-411 Task 2.4: Window reuse (Track A) ----
    #
    # ``open_for_events(events, empire_name=None)`` rebinds the events
    # list, resets filter, updates the data source in place via the
    # existing ``EventLogDataSource.update_events`` API, and re-shows.
    # Hot-seat empire switch is handled transparently — the events list
    # is the only per-empire state and ``update_events`` swaps it
    # cleanly. Re-open cost target: <200 ms vs ~2.5 s for fresh.

    def on_close_window_button_pressed(self) -> None:
        """Hide for reuse instead of pygame_gui's default kill()."""
        self.hide()

    def request_close(self) -> None:
        """PROJ-411 Task 2.5: Esc close path uses hide() for reuse."""
        self.hide()

    # ``hide()`` / ``show()`` inherited from StrategyModalWindow base
    # (PROJ-411 Task 2.8 consolidated the reuse-hide/show logic there).

    def open_for_events(
        self,
        events: list[dict],
        *,
        empire_name: Optional[str] = None,
    ) -> None:
        """Rebind events, reset filter, refresh data source, show.

        Hot-seat-safe — ``EventLogDataSource.update_events`` swaps the
        events list cleanly. ``empire_name`` is propagated to the window
        title so the user sees the active empire's name reflected.
        """
        self.all_events = events
        self.current_filter = "all"
        if self.data_source is not None:
            self.data_source.update_events(events)
        # Guard against bypass_init test paths where ``title_bar`` is
        # absent — pygame_gui's ``set_display_title`` reads it directly.
        if getattr(self, "title_bar", None) is not None:
            title = (
                f"Event Log — {empire_name} Empire" if empire_name
                else "Event Log"
            )
            self.set_display_title(title)
        self.show()
        self._rebuild_list()

    # ---- end PROJ-411 Task 2.4 ----

    def kill(self) -> None:
        """Clean up and invoke close callback."""
        if self.virtual_table:
            self.virtual_table.kill()
        if self.on_close_callback:
            self.on_close_callback()
        super().kill()
