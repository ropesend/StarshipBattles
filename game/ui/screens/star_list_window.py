"""
Star List Window - Displays a filterable, sortable list of stars.

Provides comprehensive star browsing with filtering, sorting, and presets.
Mirrors PlanetListWindow architecture.

PROJ-231: Star List Panel.
PROJ-329B Phase 1: two-stage construction. Cheap state (galaxy data,
filter manager, columns, layout constants) lives before
``super().__init__``; widget construction (sidebar, main panel,
virtual table, navigate button, initial refresh) is behind
``StarListWindowUiBuilder`` so tests can swap in a Mock under
``bypass_init``.
"""
from __future__ import annotations

from typing import Any, Optional, TYPE_CHECKING
import pygame
from pygame_gui.elements import UIPanel, UIButton

from game.core.profiling import profile_action
from game.ui.screens.strategy_modal_window import StrategyModalWindow
from game.ui.screens.data_list_window_mixin import DataListWindowMixin

if TYPE_CHECKING:
    from game.ui.screens.strategy_window_manager import StrategyWindowManager
from pygame_gui import UI_TEXT_ENTRY_FINISHED, UI_BUTTON_PRESSED

from game.ui.config import UIConfig
import logging

logger = logging.getLogger(__name__)
from game.ui.screens.star_list_filters import (
    gather_stars, filter_stars, sort_stars,
    compute_star_ranges, get_system_name, get_star_type_display,
)
from game.ui.screens.star_list_presets import (
    StarPresetManager, capture_star_list_state, apply_star_list_state,
)
from game.ui.screens.star_list_filter_manager import StarListFilterManager
from game.ui.screens.star_list_sidebar import build_sidebar
from game.ui.components.table import VirtualTable, TableColumnManager, SingleSelect
from game.ui.screens.star_data_source import StarDataSource


class StarListWindowUiBuilder:
    """Production widget builder. Constructs sidebar_panel, sidebar
    widgets, main_panel, virtual_table, navigate button, and triggers
    the initial ``refresh_list()``.

    Reads Stage-1 state (galaxy, _star_ranges, columns, layout
    constants); writes ``screen.sidebar_panel``, ``screen.main_panel``,
    ``screen.virtual_table``, ``screen.btn_navigate``, ``screen.column_manager``,
    ``screen.data_source``, ``screen.selection``, plus the sidebar
    widget references unpacked from ``build_sidebar``.
    """

    def build(self, screen: "StarListWindow") -> None:
        rect = screen.rect
        manager = screen.ui_manager

        # UI Containers - Sidebar
        screen.sidebar_panel = UIPanel(
            relative_rect=pygame.Rect(0, 0, screen.sidebar_width, rect.height - 50),
            manager=manager,
            container=screen,
            anchors={'left': 'left', 'top': 'top', 'bottom': 'bottom'},
        )

        # Build sidebar
        sidebar_widgets = build_sidebar(
            manager=manager,
            sidebar_panel=screen.sidebar_panel,
            sidebar_width=screen.sidebar_width,
            rect_height=rect.height,
            star_ranges=screen._star_ranges,
            columns=screen.columns,
            preset_manager=screen.preset_manager,
        )
        screen.sidebar_scroller = sidebar_widgets['sidebar_scroller']
        screen.txt_name_filter = sidebar_widgets['txt_name_filter']
        screen.btn_all_types = sidebar_widgets['btn_all_types']
        screen.btn_none_types = sidebar_widgets['btn_none_types']
        screen.btn_apply = sidebar_widgets['btn_apply']
        screen.btn_save_preset = sidebar_widgets['btn_save_preset']
        screen.txt_preset_name = sidebar_widgets['txt_preset_name']
        screen.dd_presets = sidebar_widgets['dd_presets']
        screen.ui_filters = sidebar_widgets['ui_filters']

        # Main Content Area - full width after sidebar (no detail panel)
        main_w = rect.width - screen.sidebar_width - 10
        screen.main_panel = UIPanel(
            relative_rect=pygame.Rect(screen.sidebar_width, 0, main_w, rect.height - 90),
            manager=manager, container=screen,
            anchors={'left': 'left', 'right': 'right', 'top': 'top', 'bottom': 'bottom'},
        )

        # Table infrastructure
        screen.column_manager = TableColumnManager(screen.columns)
        screen.column_manager.sort_column_id = 'name'
        screen.column_manager.sort_descending = False

        screen.data_source = StarDataSource(screen.columns)
        screen.selection = SingleSelect()

        screen.virtual_table = VirtualTable(
            panel=screen.main_panel,
            manager=manager,
            data_source=screen.data_source,
            column_manager=screen.column_manager,
            selection_strategy=screen.selection,
            row_height=screen.row_height,
            header_height=screen.header_height,
        )

        # Navigate button (bottom of window)
        nav_y = rect.height - 80
        screen.btn_navigate = UIButton(
            relative_rect=pygame.Rect(screen.sidebar_width + 10, nav_y, 180, 30),
            text="Navigate to Star",
            manager=manager,
            container=screen,
        )

        # Initial population
        screen.refresh_list()


class StarListWindow(DataListWindowMixin, StrategyModalWindow):
    """Window displaying a filterable, sortable list of all stars in the galaxy.

    Features:
    - Sortable/reorderable columns for all star attributes
    - Sidebar filters for type, mass, temperature, luminosity, age, radius
    - Navigation to star's system location on the strategy map
    - Preset save/load for filter configurations

    PROJ-313: Migrated to StrategyModalWindow base class.
    """

    # Issue #28: opts into per-player UI view-state container.
    SNAPSHOT_SLOT: str = "star_list"

    # PROJ-411 Task 1.10: full-window-init span — captures the entire
    # open path including pygame_gui widget construction, VirtualTable
    # build, sidebar / main panel layout, etc.
    @profile_action("Panel: StarRegistry.window_init")
    def __init__(self, rect, manager, world, *,
                 window_manager: "StrategyWindowManager",
                 on_close_callback=None, on_navigate_callback=None,
                 ui_builder: Optional[StarListWindowUiBuilder] = None,
                 facade_state=None, empire=None):
        """Initialize the Star List Window.

        Args:
            rect: Window rectangle.
            manager: pygame_gui UIManager.
            galaxy: Galaxy object containing all systems and stars.
            window_manager: PROJ-313 StrategyWindowManager (or None outside the strategy screen).
            on_close_callback: Called when window is closed.
            on_navigate_callback: Called with HexCoord to navigate camera to star.
            ui_builder: Optional UI builder override (test seam).
            facade_state: PROJ-411 Phase 1. Optional ``FacadeSessionState``
                — passed through to ``gather_stars`` so the per-turn cache
                short-circuits the galaxy walk on re-opens within one turn.
        """
        # ---- Stage 1: cheap state (set BEFORE super().__init__) ----
        # Note: super().__init__ triggers set_dimensions which may read
        # selected_star / btn_navigate, hence those are set here.
        self.selected_star = None
        self.btn_navigate = None
        self.last_preset_selection = None

        # PROJ-347 T4.1a (Pattern §33 widget-ref placeholders): set widget
        # slots populated by the production builder to None up front, so a
        # NullStarListWindowUiBuilder test can safely call kill() without
        # AttributeError on `self.virtual_table.kill()`. The production
        # builder overwrites these in Stage 3.
        self.virtual_table = None
        self.sidebar_panel = None
        self.main_panel = None
        self.data_source = None
        self.column_manager = None
        self.selection = None

        # Cheap state previously set after super().__init__: hoisted up
        # so the builder (and bypass branch) sees it. PROJ-477 Phase 4: the
        # scene.world live seam replaces the raw galaxy.
        self.world = world
        self.on_close_callback = on_close_callback
        self.on_navigate_callback = on_navigate_callback

        # --- Layout Constants ---
        self.sidebar_width = UIConfig.REGISTRY_SIDEBAR_WIDTH
        self.header_height = UIConfig.HEADER_HEIGHT
        self.row_height = UIConfig.ROW_HEIGHT_LARGE

        # --- State ---
        # PROJ-411 Phase 1: thread facade_state through gather_stars so
        # the per-turn cache short-circuits the galaxy walk on re-opens.
        self.all_stars = gather_stars(world, facade_state=facade_state)
        self.filtered_stars = []

        # Preset manager
        self.preset_manager = StarPresetManager()

        # Filter state manager
        self._filter_mgr = StarListFilterManager()

        # Issue #28: per-empire view-state is now centrally orchestrated
        # via ``StrategyGameStateManager._per_player_ui_state``. Keep
        # ``self.empire`` for current-context queries and the pristine
        # ``_default_filter_snapshot`` for the "no saved state yet" fallback.
        self.empire = empire
        self._default_filter_snapshot: dict | None = None

        # Compute dynamic filter ranges from actual star data
        self._star_ranges = compute_star_ranges(self.all_stars)
        self._filter_mgr.filter_ranges = {
            k: [self._star_ranges[k][0], self._star_ranges[k][1]]
            for k in self._star_ranges
        }

        # UI References
        self.ui_filters = {}

        # Column definitions
        self.columns = [
            {'id': 'icon', 'width': 50, 'title': '', 'type': 'image', 'visible': True},
            {'id': 'name', 'width': 150, 'title': 'Name', 'attr': 'name', 'visible': True},
            {'id': 'type', 'width': 120, 'title': 'Type', 'func': get_star_type_display, 'visible': True},
            {'id': 'system', 'width': 120, 'title': 'System', 'func': get_system_name, 'visible': True},
            {'id': 'mass', 'width': 100, 'title': 'Mass (Sol)', 'attr': 'mass', 'fmt': '{:.3f}', 'visible': True},
            {'id': 'radius', 'width': 80, 'title': 'Radius', 'attr': 'radius_hexes', 'visible': True},
            {'id': 'temp', 'width': 100, 'title': 'Temp (K)', 'attr': 'temperature', 'fmt': '{:.0f}', 'visible': True},
            {'id': 'luminosity', 'width': 110, 'title': 'Lumin (Sol)', 'attr': 'luminosity', 'fmt': '{:.4f}', 'visible': True},
            {'id': 'age', 'width': 110, 'title': 'Age (Gyr)', 'func': lambda s: f"{s.age / 1e9:.2f}", 'visible': True},
            {'id': 'planets', 'width': 70, 'title': 'Planets', 'func': lambda s: str(getattr(s, '_cached_planet_count', 0)), 'visible': True},
            {'id': 'companions', 'width': 100, 'title': 'Companions', 'func': lambda s: str(getattr(s, '_cached_companion_count', 0)), 'visible': True},
            # Spectrum bands (hidden by default)
            {'id': 'spec_gamma', 'width': 90, 'title': 'Gamma Ray', 'func': lambda s: f"{s.spectrum.gamma_ray:.4f}", 'visible': False},
            {'id': 'spec_xray', 'width': 90, 'title': 'X-Ray', 'func': lambda s: f"{s.spectrum.xray:.4f}", 'visible': False},
            {'id': 'spec_uv', 'width': 90, 'title': 'UV', 'func': lambda s: f"{s.spectrum.ultraviolet:.4f}", 'visible': False},
            {'id': 'spec_blue', 'width': 90, 'title': 'Blue', 'func': lambda s: f"{s.spectrum.blue:.4f}", 'visible': False},
            {'id': 'spec_green', 'width': 90, 'title': 'Green', 'func': lambda s: f"{s.spectrum.green:.4f}", 'visible': False},
            {'id': 'spec_red', 'width': 90, 'title': 'Red', 'func': lambda s: f"{s.spectrum.red:.4f}", 'visible': False},
            {'id': 'spec_ir', 'width': 90, 'title': 'Infrared', 'func': lambda s: f"{s.spectrum.infrared:.4f}", 'visible': False},
            {'id': 'spec_micro', 'width': 90, 'title': 'Microwave', 'func': lambda s: f"{s.spectrum.microwave:.4f}", 'visible': False},
            {'id': 'spec_radio', 'width': 90, 'title': 'Radio', 'func': lambda s: f"{s.spectrum.radio:.4f}", 'visible': False},
        ]

        # ---- Stage 2: shell ----
        super().__init__(
            rect, manager,
            window_display_title="Galactic Star Registry",
            resizable=True,
            window_manager=window_manager,
        )

        # ---- Stage 3: widgets ----
        if getattr(self, '_window_init_bypassed', False):
            if ui_builder is not None:
                ui_builder.build(self)
            return

        (ui_builder or StarListWindowUiBuilder()).build(self)
        # PROJ-411 Task 2.10: snapshot pristine post-build state so
        # first-sight-for-this-empire opens get a clean view.
        self._default_filter_snapshot = capture_star_list_state(
            self.columns, self.txt_name_filter, self.filter_types, self.ui_filters
        )

    # -----------------------------------------------------------------------
    # Filter state properties (delegate to StarListFilterManager)
    # -----------------------------------------------------------------------

    @property
    def filter_types(self) -> Any:
        return self._filter_mgr.filter_types

    @filter_types.setter
    def filter_types(self, value) -> None:
        self._filter_mgr.filter_types = value

    @property
    def filter_ranges(self) -> Any:
        return self._filter_mgr.filter_ranges

    @filter_ranges.setter
    def filter_ranges(self, value) -> None:
        self._filter_mgr.filter_ranges = value

    def refresh_list(self) -> None:
        """Filter, sort, and update the table."""
        # 1. Get search text
        search = self.txt_name_filter.get_text()
        if search == "Search Name...":
            search = ""
        search_lower = search.lower() if search else ""

        # 2. Get range values from sliders
        min_mass = self.ui_filters['mass']['min'].get_current_value()
        max_mass = self.ui_filters['mass']['max'].get_current_value()
        min_temp = self.ui_filters['temperature']['min'].get_current_value()
        max_temp = self.ui_filters['temperature']['max'].get_current_value()
        min_lum = self.ui_filters['luminosity']['min'].get_current_value()
        max_lum = self.ui_filters['luminosity']['max'].get_current_value()
        min_age = self.ui_filters['age']['min'].get_current_value()
        max_age = self.ui_filters['age']['max'].get_current_value()
        min_radius = self.ui_filters['radius_hexes']['min'].get_current_value()
        max_radius = self.ui_filters['radius_hexes']['max'].get_current_value()

        # 3. Filter
        self.filtered_stars = filter_stars(
            self.all_stars, search_lower, self.filter_types,
            min_mass, max_mass, min_temp, max_temp,
            min_lum, max_lum, min_age, max_age,
            min_radius, max_radius,
        )

        # 4. Sort
        sort_stars(
            self.filtered_stars,
            self.column_manager.sort_column_id,
            self.column_manager.sort_descending,
            self.columns,
        )

        # 5. Update table
        self.data_source.update_data(self.filtered_stars)
        self.virtual_table.update_scroll_bar()
        self.virtual_table.force_update()
        self.virtual_table.update_visible_rows()

    def process_event(self, event) -> bool:
        handled = super().process_event(event)

        # Handle all button presses in event-driven path (not polled per-frame)
        if event.type == UI_BUTTON_PRESSED:
            if event.ui_element == self.btn_navigate:
                self._navigate_to_selected()
                return True
            if event.ui_element == self.btn_apply:
                self.refresh_list()
                return True
            if event.ui_element == self.btn_all_types:
                self._set_all_type_filters(True)
                return True
            if event.ui_element == self.btn_none_types:
                self._set_all_type_filters(False)
                return True
            if event.ui_element == self.btn_save_preset:
                self._save_preset()
                return True
            # Check type toggle buttons
            for key, btn in self.ui_filters.get('types', {}).items():
                if event.ui_element == btn:
                    self._toggle_type_filter(key, btn)
                    return True
            # Check column toggle buttons
            for col_id, btn in self.ui_filters.get('columns', {}).items():
                if event.ui_element == btn:
                    self._toggle_column(btn)
                    return True

        # Star row clicks
        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            mouse_pos = event.pos
            clicked_index = self.virtual_table.handle_click(mouse_pos)
            if clicked_index >= 0:
                star = self.data_source.get_star_at_index(clicked_index)
                if star:
                    self.selected_star = star
                return True

        # Range text entry
        if event.type == UI_TEXT_ENTRY_FINISHED:
            for key in ('mass', 'temperature', 'luminosity', 'age', 'radius_hexes'):
                if key not in self.ui_filters:
                    continue
                f = self.ui_filters[key]
                target_slider = None

                if event.ui_element == f['min_txt']:
                    target_slider = f['min']
                elif event.ui_element == f['max_txt']:
                    target_slider = f['max']

                if target_slider:
                    try:
                        val = float(event.text)
                        limits = f['limits']
                        val = max(limits[0], min(limits[1], val))
                        target_slider.set_current_value(val)
                        self.refresh_list()
                    except ValueError:
                        pass

        # Mouse wheel scrolling
        if event.type == pygame.MOUSEWHEEL:
            m_pos = pygame.mouse.get_pos()
            if self.virtual_table._list_view_panel.get_abs_rect().collidepoint(m_pos):
                total_h = len(self.filtered_stars) * self.row_height
                if total_h > 0:
                    scroll_bar = self.virtual_table.scroll_bar
                    row_percent = self.row_height / total_h
                    current_pct = scroll_bar.start_percentage
                    new_pct = current_pct - (event.y * row_percent)
                    new_pct = max(0.0, min(1.0 - scroll_bar.visible_percentage, new_pct))
                    scroll_bar.set_scroll_from_start_percentage(new_pct)
                    self.virtual_table.update_visible_rows()
                return True

        return handled

    def update(self, time_delta) -> None:
        super().update(time_delta)
        # PROJ-375 Task 3.2: shared scroll/slider/header/preset polling.
        self._run_update_template(
            ('mass', 'temperature', 'luminosity', 'age', 'radius_hexes')
        )

    # -----------------------------------------------------------------------
    # Event-driven button handlers (called from process_event, not polled)
    # -----------------------------------------------------------------------

    def _set_all_type_filters(self, enabled: bool) -> None:
        """Set all star type filters to enabled/disabled."""
        for key, btn in self.ui_filters.get('types', {}).items():
            self.filter_types[key] = enabled
            if enabled:
                btn.select()
                btn.set_text(f"[{key}]")
            else:
                btn.unselect()
                btn.set_text(f"{key}")
        self.refresh_list()

    def _toggle_type_filter(self, key: str, btn) -> None:
        """Toggle a single star type filter."""
        state = not self.filter_types[key]
        self.filter_types[key] = state
        btn.select() if state else btn.unselect()
        btn.set_text(f"[{key}]" if state else f"{key}")
        self.refresh_list()

    # `_toggle_column` and `_save_preset` provided by DataListWindowMixin.

    def _capture_current_state(self) -> Any:
        """Serialize current filters and column config."""
        return capture_star_list_state(
            self.columns, self.txt_name_filter,
            self.filter_types, self.ui_filters,
        )

    def _apply_state(self, state) -> None:
        """Restore state from preset."""
        self.columns = apply_star_list_state(
            state, self.columns, self.txt_name_filter,
            self.filter_types, self.ui_filters,
        )
        self.column_manager = TableColumnManager(self.columns)
        self.data_source._columns = self.columns
        self.virtual_table._column_manager = self.column_manager
        self.virtual_table.rebuild_headers()
        self.virtual_table.rebuild_row_pool()
        self.refresh_list()

    def _navigate_to_selected(self) -> None:
        """Navigate camera to the selected star's system."""
        if self.selected_star and self.on_navigate_callback:
            loc = getattr(self.selected_star, '_cached_system_global_location', None)
            if loc:
                self.on_navigate_callback(loc)

    def set_dimensions(self, dimensions, clamp_to_container=False) -> None:
        """Handle window resize."""
        super().set_dimensions(dimensions, clamp_to_container)

    # ---- PROJ-411 Task 2.2: Window reuse (Track A) ----
    # See PROJ-411 phase_2_checklist.md for the contract. Mirrors the
    # PlanetListWindow Task 2.1 implementation; Star Registry doesn't
    # bind to a per-empire view so ``open_for_galaxy(galaxy)`` takes
    # only the galaxy argument.

    def on_close_window_button_pressed(self) -> None:
        """Hide for reuse instead of pygame_gui's default kill()."""
        self.hide()

    def request_close(self) -> None:
        """PROJ-411 Task 2.5: Esc close path uses hide() for reuse."""
        self.hide()

    # ``hide()`` / ``show()`` inherited from StrategyModalWindow base
    # (PROJ-411 Task 2.8 consolidated the reuse-hide/show logic there).

    def _post_show_hook(self) -> None:
        """Obs 3: re-assert row-pool visibility after the show cascade.

        See ``planet_list_window.py``'s identical override for the
        contract. Mirrors ``BuildQueueScreen.show()``.
        """
        vt = getattr(self, "virtual_table", None)
        if vt is not None:
            vt.force_update()
            vt.update_visible_rows()

    def open_for_galaxy(self, world, empire=None) -> None:
        """Rebind world + empire, reset selection, show, refresh.

        Used by ``StarListRegistrar.open()`` on slot-reuse path: ~5 s
        widget construction → <500 ms re-open.

        Issue #28: per-empire view-state save/restore on empire switch
        was removed from this method. It is now handled centrally by
        ``StrategyGameStateManager`` at turn rotation.
        """
        self.world = world
        if empire is not None:
            self.empire = empire
        self.selected_star = None

        self.show()
        self.refresh_list()

    def capture_view_state(self) -> dict:
        """Issue #28: snapshot current columns + filters + ranges."""
        return capture_star_list_state(
            self.columns, self.txt_name_filter,
            self.filter_types, self.ui_filters,
        )

    def apply_view_state(self, state: dict | None) -> None:
        """Issue #28: restore a previously-captured snapshot or pristine defaults."""
        target = state if state is not None else self._default_filter_snapshot
        if target is None:
            return
        self.columns = apply_star_list_state(
            target, self.columns, self.txt_name_filter,
            self.filter_types, self.ui_filters,
        )

    # ---- end PROJ-411 Task 2.2 ----

    def kill(self) -> None:
        if self.virtual_table:
            self.virtual_table.kill()

        if self.btn_navigate:
            self.btn_navigate.kill()
            self.btn_navigate = None

        if self.on_close_callback:
            self.on_close_callback()
        super().kill()
