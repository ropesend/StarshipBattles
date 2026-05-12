"""
Planet List Window - Displays a filterable, sortable list of planets.

Provides comprehensive planet management with filtering, sorting, and presets.

PROJ-188 Phase 3: Migrated to VirtualTable + PlanetDataSource + SingleSelect.
PROJ-329C Phase 3: two-stage construction with ``ui_builder`` test seam
+ ``PlanetListController`` for facade-coupled queries.
"""
from __future__ import annotations

from functools import lru_cache
from typing import Any, Optional, TYPE_CHECKING
import pygame
from game.core.profiling import profile_action
from game.core.resources import ResourceCatalog
from pygame_gui.elements import UIPanel, UIButton

from game.ui.screens.planet_list_controller import PlanetListController
from game.ui.screens.strategy_modal_window import StrategyModalWindow
from game.ui.screens.data_list_window_mixin import DataListWindowMixin

if TYPE_CHECKING:
    from game.ui.screens.strategy_window_manager import StrategyWindowManager


@lru_cache(maxsize=1)
def _get_planetary_ids() -> tuple[str, ...]:
    """PROJ-397 F-07: lazy-load planetary resource IDs (was module-level)."""
    return tuple(d.id for d in ResourceCatalog.from_json().by_display_group("planetary"))
from pygame_gui import UI_TEXT_ENTRY_FINISHED, UI_BUTTON_PRESSED

from game.ui.config import UIConfig
import logging

logger = logging.getLogger(__name__)
from game.ui.screens.planet_list_filters import (
    gather_planets, filter_planets, sort_planets,
    compute_planet_ranges, get_system_name, get_owner_name, get_mass_earth, get_resource_str,
    compute_planet_effect_keys,
)
from game.strategy.services.system_effects_collector import (
    make_display_name as _effect_display_name,
    format_intrinsic_ability_magnitude,
)
from game.ui.screens.planet_list_presets import PresetManager, capture_planet_list_state, apply_planet_list_state
from game.ui.filters.filter_state import FilterState
from game.ui.screens.planet_list_filter_manager import PlanetListFilterManager
from game.ui.screens.planet_list_sidebar import build_sidebar
from game.ui.components.table import VirtualTable, TableColumnManager, SingleSelect
from game.ui.screens.planet_data_source import PlanetDataSource
from game.ui.panels.planet_report_panel import PlanetReportPanel
from game.strategy.services.planet_economy_projector import compute_planet_production
from game.ui.panels.planet_report_panel import format_compact_number


def _format_population(planet) -> str:
    """Format total planet population for the list column."""
    pops = getattr(planet, 'populations', [])
    if not pops:
        return "—"
    total = sum(getattr(p, 'count', 0) for p in pops)
    return format_compact_number(total) if total > 0 else "—"


def _render_effect_cell(planet, group_key: str) -> str:
    """Render a planet's magnitude for one effect group-key, or '—' if absent.

    FEAT-16: used as the `func` for per-effect columns. Discriminates by
    damage_type for EnvironmentalDamage so a thermal-damage planet renders
    blank in the :radiation column and vice versa.
    """
    abilities = getattr(planet, 'intrinsic_abilities', None) or {}
    if ':' in group_key:
        ability_name, _discriminator = group_key.split(':', 1)
    else:
        ability_name = group_key
    data = abilities.get(ability_name)
    if data is None:
        return "—"
    # Confirm the planet's instance matches the same group-key (so a
    # radiation-damage planet doesn't render in the thermal-damage column).
    from game.strategy.services.system_effects_collector import make_group_key
    if make_group_key(ability_name, data) != group_key:
        return "—"
    rendered = format_intrinsic_ability_magnitude(ability_name, data)
    return rendered if rendered else "—"


@profile_action("Panel: PlanetRegistry.build_effect_columns")
def build_effect_columns(effect_keys: list[str]) -> list[dict]:
    """Build per-effect column definitions for the Planet List (FEAT-16).

    Args:
        effect_keys: Sorted group-keys produced by `compute_planet_effect_keys`.

    Returns:
        List of column dicts (id='effect_<group_key>', title=display name,
        func=cell renderer, visible=False). One column per key. When the
        list is empty (no planet has any effect) the result is empty.
    """
    columns: list[dict] = []
    for group_key in effect_keys:
        if ':' in group_key:
            ability_name, discriminator = group_key.split(':', 1)
            data = {'damage_type': discriminator, 'resource_type': discriminator}
        else:
            ability_name = group_key
            data = {}
        title = _effect_display_name(ability_name, data)
        columns.append({
            'id': f'effect_{group_key}',
            'width': 130,
            'title': title,
            'func': lambda p, gk=group_key: _render_effect_cell(p, gk),
            'visible': False,
        })
    return columns


class PlanetListUiBuilder:
    """Production widget builder for ``PlanetListWindow``.

    Builds the column list (default + per-resource + per-effect),
    sidebar widgets via ``build_sidebar``, the main panel + virtual
    table, the navigate button, and runs the initial ``refresh_list()``.

    The builder reads cheap-state attrs the screen pre-populated in
    Stage 1 (``galaxy``, ``empire``, ``all_planets``, ``preset_manager``,
    ``_filter_mgr``, ``_planet_ranges``, ``sidebar_width``,
    ``header_height``, ``row_height``, ``detail_panel_width``,
    ``panel_margin``, ``columns``, ``_effect_keys``) and writes the
    widget references the rest of the class operates on (sidebar
    references, ``main_panel``, ``column_manager``, ``data_source``,
    ``selection``, ``virtual_table``, ``btn_navigate``).
    """

    def build(self, screen: "PlanetListWindow") -> None:
        rect = screen.rect
        manager = screen.ui_manager

        # --- Sidebar ---
        screen.sidebar_panel = UIPanel(
            relative_rect=pygame.Rect(0, 0, screen.sidebar_width, rect.height - 50),
            manager=manager,
            container=screen,
            anchors={'left': 'left', 'top': 'top', 'bottom': 'bottom'}
        )

        sidebar_widgets = build_sidebar(
            manager=manager,
            sidebar_panel=screen.sidebar_panel,
            sidebar_width=screen.sidebar_width,
            rect_height=rect.height,
            planet_ranges=screen._planet_ranges,
            columns=screen.columns,
            preset_manager=screen.preset_manager,
            effect_keys=screen._effect_keys,
        )
        screen.sidebar_scroller = sidebar_widgets['sidebar_scroller']
        screen.txt_name_filter = sidebar_widgets['txt_name_filter']
        screen.btn_all_types = sidebar_widgets['btn_all_types']
        screen.btn_none_types = sidebar_widgets['btn_none_types']
        screen.btn_all_owners = sidebar_widgets['btn_all_owners']
        screen.btn_none_owners = sidebar_widgets['btn_none_owners']
        screen.btn_all_effects = sidebar_widgets['btn_all_effects']
        screen.btn_none_effects = sidebar_widgets['btn_none_effects']
        screen.btn_apply = sidebar_widgets['btn_apply']
        screen.btn_save_preset = sidebar_widgets['btn_save_preset']
        screen.txt_preset_name = sidebar_widgets['txt_preset_name']
        screen.dd_presets = sidebar_widgets['dd_presets']
        screen.ui_filters = sidebar_widgets['ui_filters']

        # --- Main content area ---
        main_w = (
            rect.width - screen.sidebar_width - screen.detail_panel_width
            - screen.panel_margin - 10
        )
        screen.main_panel = UIPanel(
            relative_rect=pygame.Rect(
                screen.sidebar_width, 0, main_w, rect.height - 90
            ),
            manager=manager, container=screen,
            anchors={'left': 'left', 'right': 'right',
                     'top': 'top', 'bottom': 'bottom'},
        )

        # PROJ-188: virtual table infrastructure
        screen.column_manager = TableColumnManager(screen.columns)
        # BUG-23: default sort by owner ascending
        screen.column_manager.sort_column_id = 'owner'
        screen.column_manager.sort_descending = False

        screen.data_source = PlanetDataSource(
            screen.columns, screen.galaxy, screen.empire
        )
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

        # Navigate button (bottom of main area)
        nav_y = rect.height - 80
        screen.btn_navigate = UIButton(
            relative_rect=pygame.Rect(
                screen.sidebar_width + 10, nav_y, 180, 30
            ),
            text="Navigate to Planet",
            manager=manager,
            container=screen,
        )

        # Initial population
        screen.refresh_list()


class PlanetListWindow(DataListWindowMixin, StrategyModalWindow):
    @profile_action("Panel: PlanetRegistry.window_init")
    def __init__(self, rect, manager, galaxy, empire, *,
                 window_manager: "StrategyWindowManager",
                 on_close_callback=None, asset_resolver=None, empires=None,
                 registries=None, on_navigate_callback=None,
                 race_registry=None, facade=None,
                 ui_builder: Optional[PlanetListUiBuilder] = None,
                 controller: Optional[PlanetListController] = None):
        # ---- Stage 1: cheap state + delegates (no facade I/O) ----
        # State that set_dimensions() may depend on must exist before the
        # super().__init__() call, since UIWindow.__init__ can trigger
        # rebuild() -> set_dimensions().
        self.selected_planet = None
        self.planet_detail_panel = None
        self.btn_build_queue = None
        self.btn_navigate = None
        self.last_preset_selection = None  # PROJ-199: lazy init elimination

        # PROJ-347 T4.1b (Pattern §33 widget-ref placeholders): set widget
        # slots populated by the production builder to None up front, so a
        # NullPlanetListWindowUiBuilder test can safely call kill() without
        # AttributeError on `self.virtual_table.kill()`. The production
        # builder overwrites these in Stage 3.
        self.virtual_table = None
        self.sidebar_panel = None
        self.main_panel = None
        self.data_source = None
        self.column_manager = None
        self.selection = None
        self._registries = registries  # PROJ-211: injected registries (DI)
        self._race_registry = race_registry  # PROJ-290
        # PROJ-292 H1: facade enables per-species sub-block rendering on
        # colonized planets via ``get_colony_demographic_view(planet.id)``.
        self._facade = facade

        self.galaxy = galaxy
        self.empire = empire  # Current player empire
        self.empires = empires or []  # PROJ-198: all empires for owner lookup
        self.on_close_callback = on_close_callback
        # PROJ-348 T5.3: navigate dispatch routes through controller (line ~321);
        # window no longer caches the callback. Parameter still threads to the
        # controller via the constructor passthrough below.
        self.asset_resolver = asset_resolver

        # Layout constants
        self.sidebar_width = UIConfig.REGISTRY_SIDEBAR_WIDTH
        self.header_height = UIConfig.HEADER_HEIGHT
        self.row_height = UIConfig.ROW_HEIGHT_LARGE
        self.detail_panel_width = 580
        self.panel_margin = 20

        # Filter / preset state
        # PROJ-411 Phase 1: pass facade_state when available so the
        # per-turn cache short-circuits the galaxy walk on re-opens.
        # Use getattr to tolerate test stubs that lack `facade_state`.
        _proj411_state = getattr(facade, "facade_state", None) if facade is not None else None
        self.all_planets = gather_planets(galaxy, empire, facade_state=_proj411_state)
        self.filtered_planets: list = []
        self.preset_manager = PresetManager()
        self._filter_mgr = PlanetListFilterManager()
        # PROJ-411 Task 2.10: per-empire filter snapshots so hot-seat
        # players don't see each other's filter state. Captured on
        # empire switch; default snapshot is taken at the end of Stage 3
        # below so first-time-for-this-empire opens get a fresh view.
        self._filter_snapshots_by_empire: dict[int, dict] = {}
        self._default_filter_snapshot: dict | None = None

        # Compute dynamic filter ranges from actual planet data
        self._planet_ranges = compute_planet_ranges(self.all_planets)
        self._filter_mgr.filter_ranges = {
            'gravity': [self._planet_ranges['gravity'][0], self._planet_ranges['gravity'][1]],
            'temp': [self._planet_ranges['temp'][0], self._planet_ranges['temp'][1]],
            'mass': [self._planet_ranges['mass'][0], self._planet_ranges['mass'][1]],
        }

        self.ui_filters: dict = {}

        # Default columns (owner column captures self.galaxy/empire references)
        self.columns = [
            {'id': 'icon', 'width': 50, 'title': '', 'type': 'image', 'visible': True},
            {'id': 'name', 'width': 150, 'title': 'Name', 'attr': 'name', 'visible': True},
            {'id': 'type', 'width': 100, 'title': 'Type', 'attr': 'planet_type.name', 'visible': True},
            {'id': 'system', 'width': 120, 'title': 'System', 'func': get_system_name, 'visible': True},
            {'id': 'owner', 'width': 140, 'title': 'Owner', 'func': lambda p: get_owner_name(p, self.empires, self.empire), 'visible': True},
            {'id': 'mass', 'width': 100, 'title': 'Mass (M_E)', 'func': get_mass_earth, 'visible': True},
            {'id': 'grav', 'width': 90, 'title': 'Grav (g)', 'func': lambda p: f"{p.surface_gravity/9.81:.2f}", 'visible': True},
            {'id': 'temp', 'width': 90, 'title': 'Temp (K)', 'attr': 'surface_temperature', 'fmt': "{:.0f}", 'visible': True},
            {'id': 'water', 'width': 90, 'title': 'Water %', 'attr': 'surface_water', 'fmt': "{:.0%}", 'visible': False},
            {'id': 'pressure', 'width': 100, 'title': 'Press (atm)', 'attr': 'total_pressure_atm', 'fmt': "{:.2f}", 'visible': False},
            {'id': 'population', 'width': 120, 'title': 'Population', 'func': lambda p: _format_population(p), 'visible': False},
        ]
        for res in _get_planetary_ids():
            self.columns.append({
                'id': f'res_{res}',
                'width': 110,
                'title': res,
                'func': lambda p, r=res: get_resource_str(p, r),
                'visible': False,
            })

        # FEAT-16: per-effect columns (one per intrinsic-ability group-key
        # present in the loaded galaxy). Hidden by default. Empty galaxy →
        # zero columns added.
        self._effect_keys = compute_planet_effect_keys(self.all_planets)
        self.columns.extend(build_effect_columns(self._effect_keys))

        # FEAT-25: seed manager filter_effects with FilterState.IGNORE per
        # discovered effect group-key (no-op default).
        self._filter_mgr.filter_effects = {
            k: FilterState.IGNORE for k in self._effect_keys
        }

        # PROJ-329C controller — wraps the facade's
        # ``get_colony_demographic_view`` plus the navigate callback.
        self.controller = controller or PlanetListController(
            facade=facade,
            on_navigate_callback=on_navigate_callback,
        )

        # ---- Stage 2: shell ----
        super().__init__(
            rect, manager,
            window_display_title="Galactic Planet Registry",
            resizable=True,
            window_manager=window_manager,
        )

        # ---- Stage 3: widgets ----
        if getattr(self, '_window_init_bypassed', False):
            if ui_builder is not None:
                ui_builder.build(self)
            return

        (ui_builder or PlanetListUiBuilder()).build(self)
        # PROJ-411 Task 2.10: snapshot the pristine post-build filter
        # state so empire switches that see a new empire for the first
        # time apply defaults instead of inheriting the prior empire's
        # filters.
        self._default_filter_snapshot = capture_planet_list_state(
            self.columns, self.txt_name_filter, self.filter_types,
            self.filter_owner, self.ui_filters,
            filter_effects=self.filter_effects,
        )

    # -----------------------------------------------------------------------
    # Filter state properties (delegate to PlanetListFilterManager)
    # -----------------------------------------------------------------------

    @property
    def filter_types(self) -> Any:
        """Planet type filter dict (mutable reference)."""
        return self._filter_mgr.filter_types

    @filter_types.setter
    def filter_types(self, value) -> None:
        """Set planet type filter dict."""
        self._filter_mgr.filter_types = value

    @property
    def filter_owner(self) -> Any:
        """Owner category filter dict (mutable reference)."""
        return self._filter_mgr.filter_owner

    @filter_owner.setter
    def filter_owner(self, value) -> None:
        """Set owner category filter dict."""
        self._filter_mgr.filter_owner = value

    @property
    def filter_effects(self) -> Any:
        """FEAT-16: Effects filter dict (mutable reference)."""
        return self._filter_mgr.filter_effects

    @filter_effects.setter
    def filter_effects(self, value) -> None:
        """Set Effects filter dict."""
        self._filter_mgr.filter_effects = value

    @property
    def filter_ranges(self) -> Any:
        """Range filter dict (mutable reference)."""
        return self._filter_mgr.filter_ranges

    @filter_ranges.setter
    def filter_ranges(self, value) -> None:
        """Set range filter dict."""
        self._filter_mgr.filter_ranges = value

    def refresh_list(self) -> None:
        """Filter and update scrollbar."""
        # 1. Update Filter State from UI (lazy sync)
        search = self.txt_name_filter.get_text()
        if search == "Search Name...":
            search = ""
        search_lower = search.lower() if search else ""

        min_g = self.ui_filters['gravity']['min'].get_current_value()
        max_g = self.ui_filters['gravity']['max'].get_current_value()
        min_t = self.ui_filters['temp']['min'].get_current_value()
        max_t = self.ui_filters['temp']['max'].get_current_value()
        min_m = self.ui_filters['mass']['min'].get_current_value()
        max_m = self.ui_filters['mass']['max'].get_current_value()

        # Use extracted filter function (BUG-27: added owner filter; FEAT-16: Effects)
        self.filtered_planets = filter_planets(
            self.all_planets, search_lower, self.filter_types,
            min_g, max_g, min_t, max_t, min_m, max_m,
            filter_owner=self.filter_owner, empire=self.empire,
            filter_effects=self.filter_effects,
        )

        # 1b. Sort using extracted function (use TableColumnManager state)
        sort_planets(
            self.filtered_planets,
            self.column_manager.sort_column_id,
            self.column_manager.sort_descending,
            self.columns,
        )

        # 2. Update DataSource with filtered planets
        self.data_source.update_data(self.filtered_planets)

        # 3. Update scrollbar and visible rows
        self.virtual_table.update_scroll_bar()
        self.virtual_table.force_update()
        self.virtual_table.update_visible_rows()

    def process_event(self, event) -> bool:
        handled = super().process_event(event)

        # Handle all button presses in event-driven path (not polled per-frame)
        if event.type == UI_BUTTON_PRESSED:
            if event.ui_element == self.btn_build_queue:
                if self.selected_planet:
                    logger.info(
                        f"Build Queue button clicked for planet: "
                        f"{self.selected_planet.name}"
                    )
                return True
            if event.ui_element == self.btn_navigate:
                self._navigate_to_selected()
                return True
            if event.ui_element == self.btn_apply:
                self.refresh_list()
                return True
            if event.ui_element == self.btn_all_types:
                self._set_all_filters(self.filter_types, 'types', True)
                return True
            if event.ui_element == self.btn_none_types:
                self._set_all_filters(self.filter_types, 'types', False)
                return True
            if event.ui_element == self.btn_all_owners:
                self._set_all_filters(self.filter_owner, 'owners', True)
                return True
            if event.ui_element == self.btn_none_owners:
                self._set_all_filters(self.filter_owner, 'owners', False)
                return True
            # FEAT-25: Effects All/None batch buttons → FilterState.YES / IGNORE
            if self.btn_all_effects is not None and event.ui_element == self.btn_all_effects:
                self._set_all_effects(FilterState.YES)
                return True
            if self.btn_none_effects is not None and event.ui_element == self.btn_none_effects:
                self._set_all_effects(FilterState.IGNORE)
                return True
            if event.ui_element == self.btn_save_preset:
                self._save_preset()
                return True
            # Check type toggle buttons
            for key, btn in self.ui_filters.get('types', {}).items():
                if event.ui_element == btn:
                    self._toggle_filter(self.filter_types, key, btn)
                    return True
            # Check owner toggle buttons
            for key, btn in self.ui_filters.get('owners', {}).items():
                if event.ui_element == btn:
                    self._toggle_filter(self.filter_owner, key, btn)
                    return True
            # FEAT-25: Effects tri-state radios
            for key, widget in self.ui_filters.get('effects', {}).items():
                new_state = widget.check_pressed(event.ui_element)
                if new_state is not None:
                    widget.set_state(new_state)
                    self.filter_effects[key] = new_state
                    self.refresh_list()
                    return True
            # Check column toggle buttons
            for col_id, btn in self.ui_filters.get('columns', {}).items():
                if event.ui_element == btn:
                    self._toggle_column(btn)
                    return True

        # Handle planet row clicks
        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:  # Left click
            mouse_pos = event.pos
            clicked_index = self.virtual_table.handle_click(mouse_pos)

            if clicked_index >= 0:
                planet = self.data_source.get_planet_at_index(clicked_index)
                if planet and planet != self.selected_planet:
                    logger.debug(f"Selecting planet: {planet.name}")
                    self._on_planet_selected(planet)
                return True  # Consume the event

        if event.type == UI_TEXT_ENTRY_FINISHED:
            # Check if it matches any of our range text boxes
            for key in ['gravity', 'temp', 'mass']:
                f = self.ui_filters[key]
                val = 0.0
                target_slider = None

                if event.ui_element == f['min_txt']:
                    target_slider = f['min']
                elif event.ui_element == f['max_txt']:
                    target_slider = f['max']

                if target_slider:
                    try:
                        val = float(event.text)
                        # Clamp to limits
                        limits = f['limits']
                        val = max(limits[0], min(limits[1], val))
                        target_slider.set_current_value(val)
                        self.refresh_list()
                    except ValueError:
                        pass  # Ignore invalid

        # Wheel handling — use VirtualTable's scrollbar
        if event.type == pygame.MOUSEWHEEL:
            m_pos = pygame.mouse.get_pos()
            if self.virtual_table._list_view_panel.get_abs_rect().collidepoint(m_pos):
                total_h = len(self.filtered_planets) * self.row_height
                if total_h > 0:
                    scroll_bar = self.virtual_table.scroll_bar
                    row_percent = self.row_height / total_h
                    current_pct = scroll_bar.start_percentage
                    new_pct = current_pct - (event.y * row_percent)
                    new_pct = max(0.0, min(1.0 - scroll_bar.visible_percentage, new_pct))
                    scroll_bar.set_scroll_from_start_percentage(new_pct)
                    self.virtual_table.update_visible_rows()
                return True  # Consume event

        return handled

    def update(self, time_delta) -> None:
        super().update(time_delta)
        # PROJ-375 Task 3.2: shared scroll/slider/header/preset polling.
        self._run_update_template(['gravity', 'temp', 'mass'])

    # -----------------------------------------------------------------------
    # Event-driven button handlers (called from process_event, not polled)
    # -----------------------------------------------------------------------

    def _set_all_filters(self, filter_dict, ui_key, enabled) -> None:
        """Set all filters in a category to enabled/disabled."""
        for key, btn in self.ui_filters.get(ui_key, {}).items():
            filter_dict[key] = enabled
            label = getattr(btn, '_display_label', key)
            if enabled:
                btn.select()
                btn.set_text(f"[{label}]")
            else:
                btn.unselect()
                btn.set_text(f"{label}")
        self.refresh_list()

    def _set_all_effects(self, state: FilterState) -> None:
        """Set every Effects filter row to the same FilterState (FEAT-25)."""
        for key, widget in self.ui_filters.get('effects', {}).items():
            self.filter_effects[key] = state
            widget.set_state(state)
        self.refresh_list()

    def _toggle_filter(self, filter_dict, key, btn) -> None:
        """Toggle a single filter in a category."""
        state = not filter_dict[key]
        filter_dict[key] = state
        btn.select() if state else btn.unselect()
        label = getattr(btn, '_display_label', key)
        btn.set_text(f"[{label}]" if state else f"{label}")
        self.refresh_list()

    # `_toggle_column` and `_save_preset` provided by DataListWindowMixin.

    def _capture_current_state(self) -> Any:
        """Serialize current filters and column config."""
        return capture_planet_list_state(
            self.columns, self.txt_name_filter, self.filter_types,
            self.filter_owner, self.ui_filters,
            filter_effects=self.filter_effects,
        )

    def _apply_state(self, state) -> None:
        """Restore state."""
        self.columns = apply_planet_list_state(
            state, self.columns, self.txt_name_filter,
            self.filter_types, self.ui_filters,
            filter_owner=self.filter_owner,
            filter_effects=self.filter_effects,
        )
        self.column_manager = TableColumnManager(self.columns)
        self.data_source._columns = self.columns
        self.virtual_table._column_manager = self.column_manager
        self.virtual_table.rebuild_headers()
        self.virtual_table.rebuild_row_pool()
        self.refresh_list()

    def _navigate_to_selected(self) -> None:
        """Navigate camera to the selected planet's system.

        PROJ-348 T5.3: route navigation through `controller.navigate_to`
        rather than calling `self.on_navigate_callback` directly. The
        controller owns the navigate-dispatch boundary; the window stays
        focused on widget concerns.
        """
        if not self.selected_planet:
            return
        loc = getattr(
            self.selected_planet, '_cached_system_global_location', None
        )
        if loc and self.controller is not None:
            self.controller.navigate_to(loc)

    def _on_planet_selected(self, planet) -> None:
        """Handle planet selection - create/update detail panel."""
        # Kill old panel if exists
        if self.planet_detail_panel:
            self.planet_detail_panel.kill()
            self.planet_detail_panel = None

        # Kill old button if exists
        if self.btn_build_queue:
            self.btn_build_queue.kill()
            self.btn_build_queue = None

        if planet is None:
            self.selected_planet = None
            return

        # Get portrait surface (use asset_resolver if available)
        portrait_surface = None
        if self.asset_resolver:
            portrait_surface = self.asset_resolver(planet)

        # Calculate panel position and dynamic height (right side of window)
        panel_x, panel_y, panel_height = self._detail_panel_geometry()

        # PROJ-292 H1: resolve the per-species demographic view for
        # colonized planets (delegates to controller, which gates on
        # owner_id + facade presence). Uncolonized planets and legacy
        # callers without a facade fall through to the pre-PROJ-289
        # rendering with view=None.
        view = self._resolve_demographic_view(planet)

        # Create planet report panel
        self.planet_detail_panel = PlanetReportPanel(
            manager=self.ui_manager,
            rect=pygame.Rect(panel_x, panel_y, self.detail_panel_width, panel_height),
            planet=planet,
            container=self,  # Window is the container
            portrait_surface=portrait_surface,
            show_complexes=False,  # Match strategy UI - no separate complexes column
            production_rates=compute_planet_production(planet, self._registries),
            empire=self.empire,  # PROJ-290
            race_registry=self._race_registry,  # PROJ-290
            view=view,  # PROJ-292 H1
        )

        # Add Build Queue button if player owns planet
        if planet.owner_id == self.empire.id:
            required_height = self.planet_detail_panel.get_height_required()
            btn_y = panel_y + min(panel_height, required_height) + 10
            self.btn_build_queue = UIButton(
                relative_rect=pygame.Rect(panel_x, btn_y, 200, 30),
                text="Open Build Yard",
                manager=self.ui_manager,
                container=self,
                object_id="#build_queue_btn_planet_list",
            )

        # Update selection tracking
        self.selected_planet = planet

    def _resolve_demographic_view(self, planet) -> Optional[Any]:
        """PROJ-292 H1: resolve per-species view for colonized planets.

        PROJ-348 T5.4: the legacy ``__new__``-bypass fallback was deleted.
        Bypass-init tests must wire a real ``PlanetListController`` (see
        ``tests/unit/ui/screens/test_planet_list_window.py:_make_planet_list_window``).
        """
        return self.controller.resolve_demographic_view(planet)

    def _detail_panel_geometry(self) -> tuple:
        """Calculate detail panel position and size relative to window."""
        window_width = self.rect.width
        window_height = self.rect.height
        panel_x = window_width - self.detail_panel_width - 10
        panel_y = 60  # Below window title bar
        # Dynamic height: fill available space minus margins
        panel_height = max(450, window_height - panel_y - 80)
        return panel_x, panel_y, panel_height

    def set_dimensions(self, dimensions, clamp_to_container=False) -> None:
        """Handle window resize - reposition detail panel."""
        super().set_dimensions(dimensions, clamp_to_container)
        # Recreate the detail panel at new position if one is showing
        if self.selected_planet is not None:
            self._on_planet_selected(self.selected_planet)

    # ---- PROJ-411 Task 2.1: Window reuse (Track A) ----
    #
    # PROJ-376 BuildQueueScreen template. The X-button close path now
    # hides the window instead of killing it; the registrar keeps the
    # slot populated across user-close/re-open cycles. ``open_for_galaxy``
    # rebinds context and resets per-open state. Esc-close still calls
    # ``kill()`` for parity with the existing event-router contract.

    def on_close_window_button_pressed(self) -> None:
        """Override pygame_gui default kill() — hide for reuse instead."""
        self.hide()

    def request_close(self) -> None:
        """PROJ-411 Task 2.5: Esc close path uses hide() for reuse."""
        self.hide()

    # ``hide()`` / ``show()`` inherited from StrategyModalWindow base
    # (PROJ-411 Task 2.8 consolidated the reuse-hide/show logic there).

    def open_for_galaxy(
        self,
        galaxy,
        empire,
        *,
        facade=None,
    ) -> None:
        """Rebind context + reset per-open state + show the window.

        Called by ``PlanetListRegistrar.open()`` when reusing an already-
        constructed instance instead of constructing a fresh one. Net
        cost should be <500 ms vs ~4.4 s for fresh construction.

        PROJ-411 Task 2.10: filter state is per-empire. Same-empire
        re-opens preserve in-place state for repeat lookups; empire
        switches save the outgoing player's view and restore the
        incoming player's (or defaults on first sight).
        """
        outgoing_empire = self.empire
        # The per-empire snapshot path requires Stage-3 widgets to exist;
        # ``_default_filter_snapshot`` is the sentinel for that (None when
        # bypass_init skipped widget construction in tests).
        snapshots_active = self._default_filter_snapshot is not None
        empire_switched = (
            snapshots_active
            and outgoing_empire is not None
            and outgoing_empire is not empire
        )

        if empire_switched:
            self._filter_snapshots_by_empire[outgoing_empire.id] = (
                capture_planet_list_state(
                    self.columns, self.txt_name_filter, self.filter_types,
                    self.filter_owner, self.ui_filters,
                    filter_effects=self.filter_effects,
                )
            )

        self.galaxy = galaxy
        self.empire = empire
        self._facade = facade
        self.selected_planet = None

        if empire_switched:
            target = self._filter_snapshots_by_empire.get(
                empire.id, self._default_filter_snapshot
            )
            self.columns = apply_planet_list_state(
                target, self.columns, self.txt_name_filter,
                self.filter_types, self.ui_filters,
                filter_owner=self.filter_owner,
                filter_effects=self.filter_effects,
            )

        self.show()
        self.refresh_list()

    # ---- end PROJ-411 Task 2.1 ----

    def kill(self) -> None:
        # Clean up VirtualTable
        if self.virtual_table:
            self.virtual_table.kill()

        if self.planet_detail_panel:
            self.planet_detail_panel.kill()
            self.planet_detail_panel = None

        if self.btn_build_queue:
            self.btn_build_queue.kill()
            self.btn_build_queue = None

        if self.btn_navigate:
            self.btn_navigate.kill()
            self.btn_navigate = None

        if self.on_close_callback:
            self.on_close_callback()
        super().kill()


__all__ = [
    "PlanetListWindow",
    "PlanetListUiBuilder",
    "build_effect_columns",
]
