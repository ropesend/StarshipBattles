"""
Planet List Window - Displays a filterable, sortable list of planets.

Provides comprehensive planet management with filtering, sorting, and presets.

PROJ-188 Phase 3: Migrated to VirtualTable + PlanetDataSource + SingleSelect.
"""
import pygame
import pygame_gui.windows
from game.core.constants import PLANET_RESOURCES
from pygame_gui.elements import UIWindow, UIPanel, UIButton, UIDropDownMenu
from pygame_gui import UI_TEXT_ENTRY_FINISHED, UI_BUTTON_PRESSED

from game.ui.config import UIConfig
import logging

logger = logging.getLogger(__name__)
from game.ui.services.screenshot_manager import ScreenshotManager
from game.ui.screens.planet_list_filters import (
    gather_planets, filter_planets, sort_planets,
    compute_planet_ranges, get_system_name, get_owner_name, get_mass_earth, get_resource_str
)
from game.ui.screens.planet_list_presets import PresetManager, capture_planet_list_state, apply_planet_list_state
from game.ui.screens.planet_list_sidebar import build_sidebar
from game.ui.components.table import VirtualTable, TableColumnManager, SingleSelect
from game.ui.screens.planet_data_source import PlanetDataSource
from game.ui.panels.planet_report_panel import PlanetReportPanel, compute_planet_production

class PlanetListWindow(UIWindow):
    def __init__(self, rect, manager, galaxy, empire, on_close_callback=None, asset_resolver=None):
        # Initialize state that set_dimensions() depends on before super().__init__(),
        # since UIWindow.__init__ triggers rebuild() -> set_dimensions().
        self.selected_planet = None
        self.planet_detail_panel = None
        self.btn_build_queue = None

        super().__init__(rect, manager, window_display_title="Galactic Planet Registry", resizable=True)

        self.galaxy = galaxy
        self.empire = empire # Current player empire for "Owner" context
        self.on_close_callback = on_close_callback
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

        # Filter States
        self.filter_types = {
            'Continental': True, 'Arid': True, 'Pelagic': True,
            'Magma': True, 'Cryoplanet': True, 'Barren': True,
            'Jovian': True, 'Ice Giant': True, 'Chthonian': True,
            'Ice Dwarf': True, 'Planetoid': True
        }
        self.filter_owner = {'Player': True, 'Enemy': True, 'Unowned': True}

        # Compute dynamic filter ranges from actual planet data
        self._planet_ranges = compute_planet_ranges(self.all_planets)
        self.filter_ranges = {
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
            {'id': 'owner', 'width': 140, 'title': 'Owner', 'func': lambda p: get_owner_name(p, self.galaxy, self.empire), 'visible': True},
            {'id': 'mass', 'width': 100, 'title': 'Mass (M_E)', 'func': get_mass_earth, 'visible': True},
            {'id': 'grav', 'width': 90, 'title': 'Grav (g)', 'func': lambda p: f"{p.surface_gravity/9.81:.2f}", 'visible': True},
            {'id': 'temp', 'width': 90, 'title': 'Temp (K)', 'attr': 'surface_temperature', 'fmt': "{:.0f}", 'visible': True},
            {'id': 'water', 'width': 90, 'title': 'Water %', 'attr': 'surface_water', 'fmt': "{:.0%}", 'visible': False},
            {'id': 'pressure', 'width': 100, 'title': 'Press (atm)', 'attr': 'total_pressure_atm', 'fmt': "{:.2f}", 'visible': False}
        ]
        # Add Resource Columns
        for res in PLANET_RESOURCES:
            self.columns.append({
                'id': f'res_{res}',
                'width': 110,
                'title': res,
                'func': lambda p, r=res: get_resource_str(p, r),
                'visible': False # hidden by default
            })

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
            preset_manager=self.preset_manager
        )
        # Unpack widget references needed by main window
        self.sidebar_scroller = sidebar_widgets['sidebar_scroller']
        self.txt_name_filter = sidebar_widgets['txt_name_filter']
        self.btn_all_types = sidebar_widgets['btn_all_types']
        self.btn_none_types = sidebar_widgets['btn_none_types']
        self.btn_all_owners = sidebar_widgets['btn_all_owners']
        self.btn_none_owners = sidebar_widgets['btn_none_owners']
        self.btn_apply = sidebar_widgets['btn_apply']
        self.btn_save_preset = sidebar_widgets['btn_save_preset']
        self.txt_preset_name = sidebar_widgets['txt_preset_name']
        self.dd_presets = sidebar_widgets['dd_presets']
        self.ui_filters = sidebar_widgets['ui_filters']

        # Main Content Area - Panel for VirtualTable
        main_w = rect.width - self.sidebar_width - self.detail_panel_width - self.panel_margin - 10
        self.main_panel = UIPanel(
            relative_rect=pygame.Rect(self.sidebar_width, 0, main_w, rect.height - 50),
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

        # Initial Population
        self.refresh_list()

    def refresh_list(self):
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

        # Use extracted filter function (BUG-27: added owner filter)
        self.filtered_planets = filter_planets(
            self.all_planets, search_lower, self.filter_types,
            min_g, max_g, min_t, max_t, min_m, max_m,
            filter_owner=self.filter_owner, empire=self.empire
        )

        # 1b. Sort using extracted function (use TableColumnManager state)
        sort_planets(self.filtered_planets, self.column_manager.sort_column_id, self.column_manager.sort_descending, self.columns)

        # 2. Update DataSource with filtered planets
        self.data_source.update_data(self.filtered_planets)

        # 3. Update scrollbar and visible rows
        self.virtual_table.update_scroll_bar()
        self.virtual_table.force_update()
        self.virtual_table.update_visible_rows()

    def process_event(self, event):
        handled = super().process_event(event)

        # Handle Build Queue button click
        if event.type == UI_BUTTON_PRESSED:
            if event.ui_element == self.btn_build_queue:
                if self.selected_planet:
                    logger.info(f"Build Queue button clicked for planet: {self.selected_planet.name}")
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

        # Screenshot Handling
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_F12 or event.key == pygame.K_F11:
                self._take_screenshot()
                return True

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

    def update(self, time_delta):
        super().update(time_delta)

        # Apply button
        if self.btn_apply.check_pressed():
            self.refresh_list()

        # Handle scrollbar changes
        if self.virtual_table.scroll_bar.check_has_moved_recently():
            self.virtual_table.update_visible_rows()

        # Sync slider values to text boxes
        self._handle_slider_sync()

        # Handle filter toggles
        self._handle_filter_toggles(self.filter_types, self.btn_all_types, self.btn_none_types, 'types')
        self._handle_filter_toggles(self.filter_owner, self.btn_all_owners, self.btn_none_owners, 'owners')

        # Handle column visibility toggles
        self._handle_column_toggles()

        # Handle header sort/swap clicks via VirtualTable
        header_result = self.virtual_table.check_header_presses()
        if header_result.get('swap_column'):
            # Column was swapped - rebuild everything
            self.virtual_table.rebuild_headers()
            self.virtual_table.rebuild_row_pool()
            self.refresh_list()
        elif header_result.get('sort_column'):
            # Sort changed - just refresh
            self.refresh_list()

        # Handle preset selection and save
        self._handle_preset_changes()

    def _handle_filter_toggles(self, filter_dict, btn_all, btn_none, ui_key):
        """Handle All/None buttons and individual toggles for a filter category."""
        buttons = self.ui_filters.get(ui_key, {})
        if btn_all.check_pressed():
            for key, btn in buttons.items():
                filter_dict[key] = True
                btn.select()
                btn.set_text(f"[{key}]")
            self.refresh_list()
            return
        if btn_none.check_pressed():
            for key, btn in buttons.items():
                filter_dict[key] = False
                btn.unselect()
                btn.set_text(f"{key}")
            self.refresh_list()
            return
        for key, btn in buttons.items():
            if btn.check_pressed():
                state = not filter_dict[key]
                filter_dict[key] = state
                btn.select() if state else btn.unselect()
                btn.set_text(f"[{key}]" if state else f"{key}")
                self.refresh_list()
                return

    def _handle_slider_sync(self):
        """Sync slider values to text boxes."""
        for key in ['gravity', 'temp', 'mass']:
            f = self.ui_filters[key]
            for which in ['min', 'max']:
                txt_box = f[f'{which}_txt']
                if not txt_box.is_focused:
                    new_txt = f"{f[which].get_current_value():.1f}"
                    if txt_box.get_text() != new_txt:
                        txt_box.set_text(new_txt)

    def _handle_column_toggles(self):
        """Handle column visibility toggles."""
        for col_id, btn in self.ui_filters.get('columns', {}).items():
            if btn.check_pressed():
                col = btn.col_ref
                # Use TableColumnManager to toggle
                new_visible = self.column_manager.toggle_column(col['id'])
                if new_visible is not None:
                    # Update button text
                    t = f"[x] {col['title'] or col['id']}" if new_visible else f"[ ] {col['title'] or col['id']}"
                    btn.set_text(t)
                    # Update the column list reference for presets
                    col['visible'] = new_visible
                    # Rebuild table
                    self.virtual_table.rebuild_headers()
                    self.virtual_table.rebuild_row_pool()
                    self.refresh_list()
                return

    def _handle_preset_changes(self):
        """Handle preset dropdown selection and save button."""
        # Lazy init tracker
        if not hasattr(self, 'last_preset_selection'):
            self.last_preset_selection = self.dd_presets.selected_option

        if self.dd_presets.selected_option != self.last_preset_selection:
            self.last_preset_selection = self.dd_presets.selected_option
            name = self.last_preset_selection
            if self.preset_manager.has_preset(name):
                self._apply_state(self.preset_manager.get_preset(name))

        if self.btn_save_preset.check_pressed():
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

    def _capture_current_state(self):
        """Serialize current filters and column config."""
        return capture_planet_list_state(
            self.columns, self.txt_name_filter, self.filter_types,
            self.filter_owner, self.ui_filters
        )

    def _apply_state(self, state):
        """Restore state."""
        self.columns = apply_planet_list_state(
            state, self.columns, self.txt_name_filter,
            self.filter_types, self.ui_filters
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

    def _take_screenshot(self):
        """Take a screenshot of the current screen including the planet list."""
        sm = ScreenshotManager.instance()
        sm.capture(label="planet_list")
        logger.info("Screenshot: Planet List window captured")
        # DUP-UI1-001: Use consolidated toast from ScreenshotManager
        sm.show_toast(self.ui_manager, self.rect.width)

    def _on_planet_selected(self, planet):
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
        if hasattr(self, 'asset_resolver') and self.asset_resolver:
            portrait_surface = self.asset_resolver(planet)

        # Calculate panel position and dynamic height (right side of window)
        panel_x, panel_y, panel_height = self._detail_panel_geometry()

        # Create planet report panel
        self.planet_detail_panel = PlanetReportPanel(
            manager=self.ui_manager,
            rect=pygame.Rect(panel_x, panel_y, self.detail_panel_width, panel_height),
            planet=planet,
            container=self,  # Window is the container
            portrait_surface=portrait_surface,
            show_complexes=False,  # Match strategy UI - no separate complexes column
            production_rates=compute_planet_production(planet)
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

    def _detail_panel_geometry(self):
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

    def set_dimensions(self, dimensions, clamp_to_container=False):
        """Handle window resize - reposition detail panel."""
        super().set_dimensions(dimensions, clamp_to_container)
        # Recreate the detail panel at new position if one is showing
        if self.selected_planet is not None:
            self._on_planet_selected(self.selected_planet)

    def kill(self):
        # Clean up VirtualTable
        if hasattr(self, 'virtual_table'):
            self.virtual_table.kill()

        if self.planet_detail_panel:
            self.planet_detail_panel.kill()
            self.planet_detail_panel = None

        if self.btn_build_queue:
            self.btn_build_queue.kill()
            self.btn_build_queue = None

        if self.on_close_callback:
            self.on_close_callback()
        super().kill()
