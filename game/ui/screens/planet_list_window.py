import pygame
import pygame_gui.windows
from game.core.constants import PLANET_RESOURCES
from pygame_gui.elements import UIWindow, UIPanel, UIButton, UIDropDownMenu, UIVerticalScrollBar
from pygame_gui import UI_TEXT_ENTRY_FINISHED, UI_BUTTON_PRESSED

from game.core.config import UIConfig
from game.core.logger import log_debug, log_info, log_warning
from game.core.screenshot_manager import ScreenshotManager
from game.ui.screens.planet_list_filters import (
    gather_planets, filter_planets, sort_planets,
    compute_planet_ranges, get_system_name, get_owner_name, get_mass_earth, get_resource_str
)
from game.ui.screens.planet_list_presets import PresetManager, capture_planet_list_state, apply_planet_list_state
from game.ui.screens.planet_list_sidebar import build_sidebar
from game.ui.screens.planet_list_columns import ColumnManager
from game.ui.screens.planet_list_renderer import VirtualListRenderer
from game.ui.panels.planet_report_panel import PlanetReportPanel

class PlanetListWindow(UIWindow):
    def __init__(self, rect, manager, galaxy, empire, on_close_callback=None, asset_resolver=None):
        super().__init__(rect, manager, window_display_title="Galactic Planet Registry", resizable=True)
        
        self.galaxy = galaxy
        self.empire = empire # Current player empire for "Owner" context
        self.on_close_callback = on_close_callback
        self.asset_resolver = asset_resolver  # Function to get image for planet
        
        # --- Layout Constants ---
        self.sidebar_width = UIConfig.SIDEBAR_WIDTH
        self.header_height = UIConfig.HEADER_HEIGHT
        self.row_height = UIConfig.ROW_HEIGHT_LARGE
        self.detail_panel_width = 600
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

        # Planet detail panel
        self.planet_detail_panel = None
        self.selected_planet = None
        self.btn_build_queue = None

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

        # Main Content Area
        main_w = rect.width - self.sidebar_width - self.detail_panel_width - self.panel_margin - 10
        self.main_panel = UIPanel(
            relative_rect=pygame.Rect(self.sidebar_width, 0, main_w, rect.height - 50),
            manager=manager, container=self,
            anchors={'left': 'left', 'right': 'right', 'top': 'top', 'bottom': 'bottom'})
        self.header_container = UIPanel(
            relative_rect=pygame.Rect(0, 0, main_w, self.header_height),
            manager=manager, container=self.main_panel,
            anchors={'left': 'left', 'right': 'right', 'top': 'top'})
        self.column_mgr = ColumnManager(self.columns, manager, self.header_container, self.header_height)

        # Virtual List Panel
        self.list_view_rect = pygame.Rect(0, self.header_height, main_w - 20, rect.height - 50 - self.header_height)
        self.list_panel = UIPanel(
            relative_rect=self.list_view_rect, manager=manager, container=self.main_panel,
            anchors={'left': 'left', 'right': 'right', 'top': 'top', 'bottom': 'bottom'})
        self.scroll_bar = UIVerticalScrollBar(
            relative_rect=pygame.Rect(-20, self.header_height, 20, self.list_view_rect.height),
            visible_percentage=1.0, manager=manager, container=self.main_panel,
            anchors={'left': 'right', 'right': 'right', 'top': 'top', 'bottom': 'bottom'})
        self.renderer = VirtualListRenderer(self.list_panel, self.row_height, manager)

        # Initial Population
        self.column_mgr.rebuild_headers()
        self.renderer.rebuild_row_pool(self.column_mgr.get_visible_columns())
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

        # 1b. Sort using extracted function
        sort_planets(self.filtered_planets, self.column_mgr.sort_column_id, self.column_mgr.sort_descending, self.columns)
                
        # 2. Update Scrollbar
        total_h = len(self.filtered_planets) * self.row_height
        visible_h = self.list_view_rect.height
        
        if total_h > 0:
            percentage = min(1.0, visible_h / total_h)
        else:
            percentage = 1.0
            
        self.scroll_bar.set_visible_percentage(percentage)
        self.scroll_bar.scroll_position = 0.0
        self.scroll_bar.bottom_limit = max(visible_h, total_h)
        self.scroll_bar.redraw_scrollbar()
        
        # 3. Update Visible Rows (force update by resetting dirty state)
        self.renderer.force_update()
        self.renderer.update_visible_rows(self.filtered_planets, self.scroll_bar)
        
    def process_event(self, event):
        handled = super().process_event(event)

        # Handle Build Queue button click
        if event.type == UI_BUTTON_PRESSED:
            if event.ui_element == self.btn_build_queue:
                if self.selected_planet:
                    log_info(f"Build Queue button clicked for planet: {self.selected_planet.name}")
                return True

        # Handle planet row clicks
        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:  # Left click
            mouse_pos = event.pos
            list_abs_rect = self.list_panel.get_abs_rect()

            # Use renderer to calculate clicked index
            clicked_index = self.renderer.get_clicked_planet_index(
                mouse_pos, list_abs_rect, self.scroll_bar, len(self.filtered_planets)
            )

            if clicked_index >= 0:
                planet = self.filtered_planets[clicked_index]
                if planet != self.selected_planet:
                    log_debug(f"Selecting planet: {planet.name}")
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

        # Wheel Handling - Use scrollbar's official API
        if event.type == pygame.MOUSEWHEEL:
            m_pos = pygame.mouse.get_pos()
            # Check if mouse is over the list area
            if self.list_panel.get_abs_rect().collidepoint(m_pos):
                # Calculate scroll amount as percentage of total
                total_h = len(self.filtered_planets) * self.row_height
                if total_h > 0:
                    # One row per wheel tick
                    row_percent = self.row_height / total_h
                    # Get current percentage
                    current_pct = self.scroll_bar.start_percentage
                    # Calculate new (wheel up = negative y = scroll up = lower percentage)
                    new_pct = current_pct - (event.y * row_percent)
                    # Clamp to valid range
                    new_pct = max(0.0, min(1.0 - self.scroll_bar.visible_percentage, new_pct))
                    # Apply using official method
                    self.scroll_bar.set_scroll_from_start_percentage(new_pct)
                    self.renderer.update_visible_rows(self.filtered_planets, self.scroll_bar)
                return True  # Consume event

        return handled

    def update(self, time_delta):
        super().update(time_delta)

        # Apply button
        if self.btn_apply.check_pressed():
            self.refresh_list()

        # Handle scrollbar changes
        if self.scroll_bar.check_has_moved_recently():
            self.renderer.update_visible_rows(self.filtered_planets, self.scroll_bar)

        # Sync slider values to text boxes
        self._handle_slider_sync()

        # Handle filter toggles
        self._handle_filter_toggles(self.filter_types, self.btn_all_types, self.btn_none_types, 'types')
        self._handle_filter_toggles(self.filter_owner, self.btn_all_owners, self.btn_none_owners, 'owners')

        # Handle column visibility toggles
        self._handle_column_toggles()

        # Handle header sort clicks
        sort_changed, columns_changed = self.column_mgr.handle_header_clicks()
        if columns_changed:
            self.renderer.rebuild_row_pool(self.column_mgr.get_visible_columns())
            self.refresh_list()
        elif sort_changed:
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
                self.column_mgr.toggle_visibility(col['id'])
                t = f"[x] {col['title'] or col['id']}" if col['visible'] else f"[ ] {col['title'] or col['id']}"
                btn.set_text(t)
                self.column_mgr.rebuild_headers()
                self.renderer.rebuild_row_pool(self.column_mgr.get_visible_columns())
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
        self.column_mgr.rebuild_headers()
        self.renderer.rebuild_row_pool(self.column_mgr.get_visible_columns())
        self.refresh_list()

    def _take_screenshot(self):
        """Take a screenshot of the current screen including the planet list."""
        sm = ScreenshotManager.instance()
        sm.capture(label="planet_list")
        log_info("Screenshot: Planet List window captured")
        self._show_screenshot_toast()

    def _show_screenshot_toast(self):
        """Show a brief toast notification for screenshot feedback."""
        try:
            toast_rect = pygame.Rect(0, 0, UIConfig.TOAST_WIDTH, UIConfig.TOAST_HEIGHT)
            toast_rect.center = (self.rect.width // 2, 80)
            pygame_gui.windows.UIMessageWindow(
                rect=toast_rect,
                html_message="<b>Screenshot saved!</b><br>Path copied to clipboard",
                manager=self.ui_manager,
                window_title="Screenshot"
            )
        except Exception as e:
            log_warning(f"Failed to show screenshot toast: {e}")

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

        # Calculate panel position (right side of window)
        window_width = self.rect.width
        panel_x = window_width - self.detail_panel_width - 10
        panel_y = 60  # Below window header

        # Create planet report panel
        self.planet_detail_panel = PlanetReportPanel(
            manager=self.ui_manager,
            rect=pygame.Rect(panel_x, panel_y, self.detail_panel_width, 400),
            planet=planet,
            container=self,  # Window is the container
            portrait_surface=portrait_surface,
            show_complexes=False  # Match strategy UI - no separate complexes column
        )

        # Add Build Queue button if player owns planet
        if planet.owner_id == self.empire.id:
            panel_height = self.planet_detail_panel.get_height_required()
            self.btn_build_queue = UIButton(
                relative_rect=pygame.Rect(panel_x, panel_y + panel_height + 10, 200, 30),
                text="Open Build Queue",
                manager=self.ui_manager,
                container=self,
                object_id="#build_queue_btn_planet_list"
            )

        # Update selection tracking
        self.selected_planet = planet

    def kill(self):
        # Clean up renderer
        if hasattr(self, 'renderer'):
            self.renderer.kill()

        # Clean up column manager
        if hasattr(self, 'column_mgr'):
            self.column_mgr.kill()

        if self.planet_detail_panel:
            self.planet_detail_panel.kill()
            self.planet_detail_panel = None

        if self.btn_build_queue:
            self.btn_build_queue.kill()
            self.btn_build_queue = None

        if self.on_close_callback:
            self.on_close_callback()
        super().kill()
