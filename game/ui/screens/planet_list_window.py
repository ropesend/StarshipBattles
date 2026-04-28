"""
Planet List Window - Displays a filterable, sortable list of planets.

Provides comprehensive planet management with filtering, sorting, and presets.

PROJ-188 Phase 3: Migrated to VirtualTable + PlanetDataSource + SingleSelect.
"""
from __future__ import annotations

from typing import Any
import pygame
import pygame_gui.windows
from game.core.resources import ResourceCatalog
from pygame_gui.elements import UIWindow, UIPanel, UIButton, UIDropDownMenu

_PLANETARY_IDS = [d.id for d in ResourceCatalog.from_json().by_display_group("planetary")]
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

class PlanetListWindow(UIWindow):
    def __init__(self, rect, manager, galaxy, empire, on_close_callback=None, asset_resolver=None, empires=None, registries=None, on_navigate_callback=None, race_registry=None, facade=None):
        # Initialize state that set_dimensions() depends on before super().__init__(),
        # since UIWindow.__init__ triggers rebuild() -> set_dimensions().
        self.selected_planet = None
        self.planet_detail_panel = None
        self.btn_build_queue = None
        self.btn_navigate = None
        self.last_preset_selection = None  # PROJ-199: Lazy init elimination
        self._registries = registries  # PROJ-211: Injected registries for DI
        self._race_registry = race_registry  # PROJ-290: forwarded to PlanetReportPanel for uncolonized habitability
        # PROJ-292 H1: facade enables per-species sub-block rendering on
        # colonized planets by providing `get_colony_demographic_view(planet.id)`.
        # Mirrors the pattern established in `strategy_detail_formatter._show_planet_report`.
        self._facade = facade

        super().__init__(rect, manager, window_display_title="Galactic Planet Registry", resizable=True)

        self.galaxy = galaxy
        self.empire = empire # Current player empire for "Owner" context
        self.empires = empires or []  # PROJ-198: All empires for owner name lookup
        self.on_close_callback = on_close_callback
        self.on_navigate_callback = on_navigate_callback
        self.asset_resolver = asset_resolver  # Function to get image for planet

        # --- Layout Constants ---
        self.sidebar_width = UIConfig.SIDEBAR_WIDTH
        self.header_height = UIConfig.HEADER_HEIGHT
        self.row_height = UIConfig.ROW_HEIGHT_LARGE
        self.detail_panel_width = 580
        self.panel_margin = 20
        # --- State ---
        self.all_planets = gather_planets(galaxy, empire)
        self.filtered_planets = []

        # Preset manager
        self.preset_manager = PresetManager()

        # Filter state manager (PROJ-220: extracted from inline dicts)
        self._filter_mgr = PlanetListFilterManager()

        # Compute dynamic filter ranges from actual planet data
        self._planet_ranges = compute_planet_ranges(self.all_planets)
        self._filter_mgr.filter_ranges = {
            'gravity': [self._planet_ranges['gravity'][0], self._planet_ranges['gravity'][1]],
            'temp': [self._planet_ranges['temp'][0], self._planet_ranges['temp'][1]],
            'mass': [self._planet_ranges['mass'][0], self._planet_ranges['mass'][1]]
        }

        # UI References (for reading values)
        self.ui_filters = {}

        # Default Columns (owner column uses lambda to capture self.galaxy/empire references)
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
        # Add Resource Columns
        for res in _PLANETARY_IDS:
            self.columns.append({
                'id': f'res_{res}',
                'width': 110,
                'title': res,
                'func': lambda p, r=res: get_resource_str(p, r),
                'visible': False # hidden by default
            })

        # FEAT-16: per-effect columns (one per intrinsic-ability group-key
        # present in the loaded galaxy). Hidden by default. Empty galaxy →
        # zero columns added.
        self._effect_keys = compute_planet_effect_keys(self.all_planets)
        self.columns.extend(build_effect_columns(self._effect_keys))

        # FEAT-16: seed the manager's filter_effects with one True entry
        # per discovered effect group-key. All True initially so the
        # filter is a no-op until the user unticks something.
        self._filter_mgr.filter_effects = {k: True for k in self._effect_keys}

        # UI Containers - Sidebar
        self.sidebar_panel = UIPanel(
            relative_rect=pygame.Rect(0, 0, self.sidebar_width, rect.height - 50),
            manager=manager,
            container=self,
            anchors={'left': 'left', 'top': 'top', 'bottom': 'bottom'}
        )

        # Build sidebar using extracted function
        sidebar_widgets = build_sidebar(
            manager=manager,
            sidebar_panel=self.sidebar_panel,
            sidebar_width=self.sidebar_width,
            rect_height=rect.height,
            planet_ranges=self._planet_ranges,
            columns=self.columns,
            preset_manager=self.preset_manager,
            effect_keys=self._effect_keys,
        )
        # Unpack widget references needed by main window
        self.sidebar_scroller = sidebar_widgets['sidebar_scroller']
        self.txt_name_filter = sidebar_widgets['txt_name_filter']
        self.btn_all_types = sidebar_widgets['btn_all_types']
        self.btn_none_types = sidebar_widgets['btn_none_types']
        self.btn_all_owners = sidebar_widgets['btn_all_owners']
        self.btn_none_owners = sidebar_widgets['btn_none_owners']
        self.btn_all_effects = sidebar_widgets['btn_all_effects']
        self.btn_none_effects = sidebar_widgets['btn_none_effects']
        self.btn_apply = sidebar_widgets['btn_apply']
        self.btn_save_preset = sidebar_widgets['btn_save_preset']
        self.txt_preset_name = sidebar_widgets['txt_preset_name']
        self.dd_presets = sidebar_widgets['dd_presets']
        self.ui_filters = sidebar_widgets['ui_filters']

        # FEAT-16: initialize Effects toggle button visual states to match
        # the seeded filter_effects dict (all True = all selected).
        for key, btn in self.ui_filters.get('effects', {}).items():
            btn.select()

        # Main Content Area - Panel for VirtualTable
        main_w = rect.width - self.sidebar_width - self.detail_panel_width - self.panel_margin - 10
        self.main_panel = UIPanel(
            relative_rect=pygame.Rect(self.sidebar_width, 0, main_w, rect.height - 90),
            manager=manager, container=self,
            anchors={'left': 'left', 'right': 'right', 'top': 'top', 'bottom': 'bottom'})

        # PROJ-188: Use new table infrastructure
        self.column_manager = TableColumnManager(self.columns)
        # Set default sort by owner name as per BUG-23
        self.column_manager.sort_column_id = 'owner'
        self.column_manager.sort_descending = False

        self.data_source = PlanetDataSource(self.columns, self.galaxy, self.empire)
        self.selection = SingleSelect()

        self.virtual_table = VirtualTable(
            panel=self.main_panel,
            manager=manager,
            data_source=self.data_source,
            column_manager=self.column_manager,
            selection_strategy=self.selection,
            row_height=self.row_height,
            header_height=self.header_height,
        )

        # Navigate button (bottom of main area)
        nav_y = rect.height - 80
        self.btn_navigate = UIButton(
            relative_rect=pygame.Rect(self.sidebar_width + 10, nav_y, 180, 30),
            text="Navigate to Planet",
            manager=manager,
            container=self,
        )

        # Initial Population
        self.refresh_list()

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
        sort_planets(self.filtered_planets, self.column_manager.sort_column_id, self.column_manager.sort_descending, self.columns)

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
                    logger.info(f"Build Queue button clicked for planet: {self.selected_planet.name}")
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
            # FEAT-16: Effects All/None batch buttons (None when section omitted)
            if self.btn_all_effects is not None and event.ui_element == self.btn_all_effects:
                self._set_all_filters(self.filter_effects, 'effects', True)
                return True
            if self.btn_none_effects is not None and event.ui_element == self.btn_none_effects:
                self._set_all_filters(self.filter_effects, 'effects', False)
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
            # FEAT-16: Effects toggle buttons
            for key, btn in self.ui_filters.get('effects', {}).items():
                if event.ui_element == btn:
                    self._toggle_filter(self.filter_effects, key, btn)
                    return True
            # Check column toggle buttons
            for col_id, btn in self.ui_filters.get('columns', {}).items():
                if event.ui_element == btn:
                    self._toggle_column(btn)
                    return True

        # Handle planet row clicks
        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:  # Left click
            mouse_pos = event.pos

            # Use VirtualTable to handle click
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
                        # Refresh list to apply
                        self.refresh_list()
                    except ValueError:
                        pass # Ignore invalid

        # Wheel Handling - Use VirtualTable's scrollbar
        if event.type == pygame.MOUSEWHEEL:
            m_pos = pygame.mouse.get_pos()
            # Check if mouse is over the list area
            if self.virtual_table._list_view_panel.get_abs_rect().collidepoint(m_pos):
                # Calculate scroll amount as percentage of total
                total_h = len(self.filtered_planets) * self.row_height
                if total_h > 0:
                    scroll_bar = self.virtual_table.scroll_bar
                    # One row per wheel tick
                    row_percent = self.row_height / total_h
                    # Get current percentage
                    current_pct = scroll_bar.start_percentage
                    # Calculate new (wheel up = negative y = scroll up = lower percentage)
                    new_pct = current_pct - (event.y * row_percent)
                    # Clamp to valid range
                    new_pct = max(0.0, min(1.0 - scroll_bar.visible_percentage, new_pct))
                    # Apply using official method
                    scroll_bar.set_scroll_from_start_percentage(new_pct)
                    self.virtual_table.update_visible_rows()
                return True  # Consume event

        return handled

    def update(self, time_delta) -> None:
        super().update(time_delta)

        # Scrollbar movement (cheap — only updates rows when position changed)
        if self.virtual_table.scroll_bar.check_has_moved_recently():
            self.virtual_table.update_visible_rows()

        # Slider text sync (only when slider actually moved)
        for key in ['gravity', 'temp', 'mass']:
            f = self.ui_filters.get(key)
            if not f:
                continue
            for which in ['min', 'max']:
                slider = f[which]
                if not slider.has_moved_recently:
                    continue
                txt_box = f[f'{which}_txt']
                if not txt_box.is_focused:
                    txt_box.set_text(f"{slider.get_current_value():.1f}")

        # Header sort/swap (check_presses iterates header buttons)
        header_result = self.virtual_table.check_header_presses()
        if header_result.get('swap_column'):
            col_dict, direction = header_result.get('swap_column')
            self.column_manager.swap_column(col_dict['id'], direction)
            self.virtual_table.rebuild_headers()
            self.virtual_table.rebuild_row_pool()
            self.refresh_list()
        elif header_result.get('sort_column'):
            col_id = header_result.get('sort_column')
            self.column_manager.set_sort(col_id)
            self.virtual_table.rebuild_headers()
            self.refresh_list()

        # Preset dropdown (cheap — single string comparison)
        if self.last_preset_selection is None:
            self.last_preset_selection = self.dd_presets.selected_option
        if self.dd_presets.selected_option != self.last_preset_selection:
            self.last_preset_selection = self.dd_presets.selected_option
            name = self.last_preset_selection
            if self.preset_manager.has_preset(name):
                self._apply_state(self.preset_manager.get_preset(name))

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

    def _toggle_filter(self, filter_dict, key, btn) -> None:
        """Toggle a single filter in a category."""
        state = not filter_dict[key]
        filter_dict[key] = state
        btn.select() if state else btn.unselect()
        label = getattr(btn, '_display_label', key)
        btn.set_text(f"[{label}]" if state else f"{label}")
        self.refresh_list()

    def _toggle_column(self, btn) -> None:
        """Toggle column visibility from a sidebar button."""
        col = btn.col_ref
        new_visible = self.column_manager.toggle_column(col['id'])
        if new_visible is not None:
            t = f"[x] {col['title'] or col['id']}" if new_visible else f"[ ] {col['title'] or col['id']}"
            btn.set_text(t)
            col['visible'] = new_visible
            self.virtual_table.rebuild_headers()
            self.virtual_table.rebuild_row_pool()
            self.refresh_list()

    def _save_preset(self) -> None:
        """Save the current state as a preset."""
        name = self.txt_preset_name.get_text()
        if name:
            state = self._capture_current_state()
            self.preset_manager.save_preset(name, state)
            rect = self.dd_presets.relative_rect
            container = self.dd_presets.ui_container
            self.dd_presets.kill()
            self.dd_presets = UIDropDownMenu(
                options_list=self.preset_manager.get_preset_names(),
                starting_option=name,
                relative_rect=rect,
                manager=self.ui_manager,
                container=container
            )
            self.last_preset_selection = name

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
        # Re-sync TableColumnManager with updated columns
        self.column_manager = TableColumnManager(self.columns)
        # Also update data source column reference
        self.data_source._columns = self.columns
        # Rebuild VirtualTable components
        self.virtual_table._column_manager = self.column_manager
        self.virtual_table.rebuild_headers()
        self.virtual_table.rebuild_row_pool()
        self.refresh_list()

    def _navigate_to_selected(self) -> None:
        """Navigate camera to the selected planet's system."""
        if self.selected_planet and self.on_navigate_callback:
            loc = getattr(self.selected_planet, '_cached_system_global_location', None)
            if loc:
                self.on_navigate_callback(loc)

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
        # colonized planets so `PlanetReportPanel` renders PROJ-289's
        # sub-block (habitability / happiness / growth / food ratio /
        # allocation). Uncolonized planets and legacy callers without a
        # facade fall through to the pre-PROJ-289 rendering.
        view = None
        if planet.owner_id is not None and self._facade is not None:
            view = self._facade.get_colony_demographic_view(planet.id)

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
                object_id="#build_queue_btn_planet_list"
            )

        # Update selection tracking
        self.selected_planet = planet

    def _detail_panel_geometry(self) -> tuple:
        """Calculate detail panel position and size relative to window.

        Returns:
            Tuple of (panel_x, panel_y, panel_height).
        """
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
