"""
Star List Window - Displays a filterable, sortable list of stars.

Provides comprehensive star browsing with filtering, sorting, and presets.
Mirrors PlanetListWindow architecture.

PROJ-231: Star List Panel.
"""
import pygame
from pygame_gui.elements import UIWindow, UIPanel, UIButton, UIDropDownMenu
from pygame_gui import UI_TEXT_ENTRY_FINISHED, UI_BUTTON_PRESSED

from game.ui.config import UIConfig
import logging

logger = logging.getLogger(__name__)
from game.ui.services.screenshot_manager import ScreenshotManager
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


class StarListWindow(UIWindow):
    """Window displaying a filterable, sortable list of all stars in the galaxy.

    Features:
    - Sortable/reorderable columns for all star attributes
    - Sidebar filters for type, mass, temperature, luminosity, age, radius
    - Navigation to star's system location on the strategy map
    - Preset save/load for filter configurations
    """

    def __init__(self, rect, manager, galaxy, on_close_callback=None,
                 on_navigate_callback=None):
        """Initialize the Star List Window.

        Args:
            rect: Window rectangle.
            manager: pygame_gui UIManager.
            galaxy: Galaxy object containing all systems and stars.
            on_close_callback: Called when window is closed.
            on_navigate_callback: Called with HexCoord to navigate camera to star.
        """
        # Initialize state before super().__init__ (which triggers set_dimensions)
        self.selected_star = None
        self.btn_navigate = None
        self.last_preset_selection = None

        super().__init__(rect, manager, window_display_title="Galactic Star Registry", resizable=True)

        self.galaxy = galaxy
        self.on_close_callback = on_close_callback
        self.on_navigate_callback = on_navigate_callback

        # --- Layout Constants ---
        self.sidebar_width = UIConfig.SIDEBAR_WIDTH
        self.header_height = UIConfig.HEADER_HEIGHT
        self.row_height = UIConfig.ROW_HEIGHT_LARGE

        # --- State ---
        self.all_stars = gather_stars(galaxy)
        self.filtered_stars = []

        # Preset manager
        self.preset_manager = StarPresetManager()

        # Filter state manager
        self._filter_mgr = StarListFilterManager()

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

        # UI Containers - Sidebar
        self.sidebar_panel = UIPanel(
            relative_rect=pygame.Rect(0, 0, self.sidebar_width, rect.height - 50),
            manager=manager,
            container=self,
            anchors={'left': 'left', 'top': 'top', 'bottom': 'bottom'}
        )

        # Build sidebar
        sidebar_widgets = build_sidebar(
            manager=manager,
            sidebar_panel=self.sidebar_panel,
            sidebar_width=self.sidebar_width,
            rect_height=rect.height,
            star_ranges=self._star_ranges,
            columns=self.columns,
            preset_manager=self.preset_manager,
        )
        self.sidebar_scroller = sidebar_widgets['sidebar_scroller']
        self.txt_name_filter = sidebar_widgets['txt_name_filter']
        self.btn_all_types = sidebar_widgets['btn_all_types']
        self.btn_none_types = sidebar_widgets['btn_none_types']
        self.btn_apply = sidebar_widgets['btn_apply']
        self.btn_save_preset = sidebar_widgets['btn_save_preset']
        self.txt_preset_name = sidebar_widgets['txt_preset_name']
        self.dd_presets = sidebar_widgets['dd_presets']
        self.ui_filters = sidebar_widgets['ui_filters']

        # Main Content Area - full width after sidebar (no detail panel)
        main_w = rect.width - self.sidebar_width - 10
        self.main_panel = UIPanel(
            relative_rect=pygame.Rect(self.sidebar_width, 0, main_w, rect.height - 90),
            manager=manager, container=self,
            anchors={'left': 'left', 'right': 'right', 'top': 'top', 'bottom': 'bottom'}
        )

        # Table infrastructure
        self.column_manager = TableColumnManager(self.columns)
        self.column_manager.sort_column_id = 'name'
        self.column_manager.sort_descending = False

        self.data_source = StarDataSource(self.columns)
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

        # Navigate button (bottom of window)
        nav_y = rect.height - 80
        self.btn_navigate = UIButton(
            relative_rect=pygame.Rect(self.sidebar_width + 10, nav_y, 180, 30),
            text="Navigate to Star",
            manager=manager,
            container=self,
        )

        # Initial population
        self.refresh_list()

    # -----------------------------------------------------------------------
    # Filter state properties (delegate to StarListFilterManager)
    # -----------------------------------------------------------------------

    @property
    def filter_types(self):
        return self._filter_mgr.filter_types

    @filter_types.setter
    def filter_types(self, value):
        self._filter_mgr.filter_types = value

    @property
    def filter_ranges(self):
        return self._filter_mgr.filter_ranges

    @filter_ranges.setter
    def filter_ranges(self, value):
        self._filter_mgr.filter_ranges = value

    def refresh_list(self):
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

    def process_event(self, event):
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

        # Screenshot
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_F12, pygame.K_F11):
                self._take_screenshot()
                return True

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

    def update(self, time_delta):
        super().update(time_delta)

        # Scrollbar movement (cheap — only updates rows when position changed)
        if self.virtual_table.scroll_bar.check_has_moved_recently():
            self.virtual_table.update_visible_rows()

        # Slider text sync (only when slider actually moved)
        for key in ('mass', 'temperature', 'luminosity', 'age', 'radius_hexes'):
            f = self.ui_filters.get(key)
            if not f:
                continue
            for which in ('min', 'max'):
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

    def _set_all_type_filters(self, enabled: bool):
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

    def _toggle_type_filter(self, key: str, btn):
        """Toggle a single star type filter."""
        state = not self.filter_types[key]
        self.filter_types[key] = state
        btn.select() if state else btn.unselect()
        btn.set_text(f"[{key}]" if state else f"{key}")
        self.refresh_list()

    def _toggle_column(self, btn):
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

    def _save_preset(self):
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
                container=container,
            )
            self.last_preset_selection = name

    def _capture_current_state(self):
        """Serialize current filters and column config."""
        return capture_star_list_state(
            self.columns, self.txt_name_filter,
            self.filter_types, self.ui_filters,
        )

    def _apply_state(self, state):
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

    def _navigate_to_selected(self):
        """Navigate camera to the selected star's system."""
        if self.selected_star and self.on_navigate_callback:
            loc = getattr(self.selected_star, '_cached_system_global_location', None)
            if loc:
                self.on_navigate_callback(loc)

    def _take_screenshot(self):
        """Take a screenshot of the current screen."""
        sm = ScreenshotManager.instance()
        sm.capture(label="star_list")
        logger.info("Screenshot: Star List window captured")
        sm.show_toast(self.ui_manager, self.rect.width)

    def set_dimensions(self, dimensions, clamp_to_container=False):
        """Handle window resize."""
        super().set_dimensions(dimensions, clamp_to_container)

    def kill(self):
        if self.virtual_table:
            self.virtual_table.kill()

        if self.btn_navigate:
            self.btn_navigate.kill()
            self.btn_navigate = None

        if self.on_close_callback:
            self.on_close_callback()
        super().kill()
