import pygame
import pygame_gui.windows
from game.core.constants import PLANET_RESOURCES
from pygame_gui.elements import UIWindow, UIPanel, UILabel, UIButton, UIScrollingContainer, UITextEntryLine, UIHorizontalSlider, UIDropDownMenu, UIImage, UIVerticalScrollBar
from pygame_gui import UI_TEXT_ENTRY_FINISHED, UI_BUTTON_PRESSED

from game.assets.asset_manager import AssetManager
from game.core.config import UIConfig
from game.core.logger import log_debug, log_info, log_warning
from game.core.screenshot_manager import ScreenshotManager
from game.ui.screens.planet_list_filters import (
    gather_planets, filter_planets, sort_planets, get_column_value,
    compute_planet_ranges, get_system_name, get_owner_name, get_mass_earth, get_resource_str
)
from game.ui.screens.planet_list_presets import PresetManager, capture_planet_list_state, apply_planet_list_state
from game.ui.screens.planet_list_sidebar import build_sidebar
from game.ui.screens.planet_list_columns import ColumnManager
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
        self.detail_panel_width = 600  # Width for right-side planet report panel (PROJ-54)
        self.panel_margin = 20         # Margin between list and panel (PROJ-54)
        
        # --- State ---
        self.all_planets = gather_planets(galaxy, empire)
        self.filtered_planets = []

        # Preset manager
        self.preset_manager = PresetManager()
        
        # Filter States
        self.filter_name = ""
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

        # Planet detail panel (PROJ-54)
        self.planet_detail_panel = None  # Created when planet selected
        self.selected_planet = None      # Track current selection
        self.btn_build_queue = None      # Build queue button (for owned planets)
        self._debug_next_click = False   # Debug flag for click detection

        # Default Columns
        # ID, Width, Title, Attribute/Getter, Visible
        # Note: owner column uses a lambda to capture self.galaxy/empire references
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
        
        # --- UI Containers ---
        
        # 1. Sidebar (Filters/Config)
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

        # 2. Main Content Area (Header + Scrollable List)
        # Reserve space for detail panel on right (PROJ-54)
        main_w = rect.width - self.sidebar_width - self.detail_panel_width - self.panel_margin - 10
        self.main_panel = UIPanel(
            relative_rect=pygame.Rect(self.sidebar_width, 0, main_w, rect.height - 50),
            manager=manager,
            container=self,
            anchors={'left': 'left', 'right': 'right', 'top': 'top', 'bottom': 'bottom'}
        )
        
        # Header Row
        self.header_container = UIPanel(
            relative_rect=pygame.Rect(0, 0, main_w, self.header_height),
            manager=manager,
            container=self.main_panel,
            anchors={'left': 'left', 'right': 'right', 'top': 'top'}
        )

        # Column Manager - handles column ordering, sorting, and header UI
        self.column_mgr = ColumnManager(
            self.columns, manager, self.header_container, self.header_height
        )

        # Virtual List Viewport
        # We use a panel that clips its contents.
        self.list_view_rect = pygame.Rect(0, self.header_height, main_w - 20, rect.height - 50 - self.header_height)
        self.list_panel = UIPanel(
            relative_rect=self.list_view_rect,
            manager=manager,
            container=self.main_panel,
            anchors={'left': 'left', 'right': 'right', 'top': 'top', 'bottom': 'bottom'}
        )
        
        # Scrollbar
        self.scroll_bar = UIVerticalScrollBar(
            relative_rect=pygame.Rect(-20, self.header_height, 20, self.list_view_rect.height),
            visible_percentage=1.0,
            manager=manager,
            container=self.main_panel,
            anchors={'left': 'right', 'right': 'right', 'top': 'top', 'bottom': 'bottom'}
        )
        
        # Row Pool
        self.row_pool = [] # List of dicts: {'bg': panel, 'cols': [widgets]}
        self.virtual_scroll_y = 0.0
        
        # Performance: Icon cache to avoid repeated smoothscale calls
        self._icon_cache = {}
        # Dirty tracking for row updates
        self._last_scroll_pct = -1.0
        self._last_filtered_count = -1
        
        # --- Initial Population ---
        self.column_mgr.rebuild_headers()
        self._rebuild_row_pool()
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
        self._last_scroll_pct = -1.0
        self._update_visible_rows()
        
    def _rebuild_row_pool(self):
        """Create pool of reusable row widgets."""
        # Clear existing
        if hasattr(self, 'row_pool'):
            for r in self.row_pool:
                for w in r['widgets']:
                    w['el'].kill()
                if 'bg' in r: r['bg'].kill()
        
        self.row_pool = []
        
        # How many rows fit?
        visible_h = self.list_view_rect.height
        count = int(visible_h / self.row_height) + 2 # buffer
        
        visible_cols = self.column_mgr.get_visible_columns()
        
        for i in range(count):
            # Create container for row? Or just absolute widgets?
            # Absolute widgets for speed, but Panel makes background/click easier.
            # Using Panel for row background
            
            # NOTE: We can't really set correct Y yet, so just 0
            row_panel = UIPanel(
                relative_rect=pygame.Rect(0, 0, self.list_view_rect.width, self.row_height),
                manager=self.ui_manager,
                container=self.list_panel,
                object_id='#planet_list_row' # Style hook
            )
            # Remove panel border/bg usually
            
            widgets = []
            x_off = 0
            for col in visible_cols:
                w = col['width']
                rect = pygame.Rect(x_off, 0, w, self.row_height)
                
                # We need persistent widgets we can update.
                # If it's an image, we use UIImage. If text, UILabel.
                # Problem: 'icon' column switches between UIImage and Label("?") based on content.
                # Solution: Create both, hide one? Or Just recreate that one slot?
                # Optimization: Most planets have images.
                
                if col['id'] == 'icon':
                    # Place holder image - use x_off for correct column position
                    img = UIImage(relative_rect=pygame.Rect(x_off + 5, 5, 40, 40),
                                  image_surface=pygame.Surface((40,40)),
                                  manager=self.ui_manager,
                                  container=row_panel)
                    widgets.append({'type': 'image', 'el': img, 'col': col})
                else:
                    lbl = UILabel(rect, "", self.ui_manager, container=row_panel)
                    widgets.append({'type': 'label', 'el': lbl, 'col': col})
                
                x_off += w
            
            self.row_pool.append({'bg': row_panel, 'widgets': widgets})
            
    def _update_visible_rows(self):
        """Update content of row pool based on scroll position."""
        # Dirty check: skip if nothing changed
        current_pct = self.scroll_bar.start_percentage
        current_count = len(self.filtered_planets)
        
        if (current_pct == self._last_scroll_pct and 
            current_count == self._last_filtered_count):
            return  # Nothing changed, skip update
        
        self._last_scroll_pct = current_pct
        self._last_filtered_count = current_count
        
        # Use start_percentage for consistency with the percentage-based API
        total_h = current_count * self.row_height
        scroll_y = current_pct * total_h
        start_index = int(scroll_y // self.row_height)
        offset_y = scroll_y % self.row_height
        
        # Local refs for performance
        filtered_planets = self.filtered_planets
        icon_cache = self._icon_cache
        
        for i, row_data in enumerate(self.row_pool):
            data_index = start_index + i

            row_panel = row_data['bg']

            if data_index < len(filtered_planets):
                planet = filtered_planets[data_index]

                # Store planet reference in row for selection tracking (PROJ-54)
                row_data['planet'] = planet

                y_pos = (i * self.row_height) - offset_y

                # Make visible and set position
                row_panel.show()
                row_panel.set_relative_position((0, y_pos))
                
                # Update Content
                for widget_data in row_data['widgets']:
                    col = widget_data['col']
                    el = widget_data['el']
                    
                    if widget_data['type'] == 'label':
                        val = get_column_value(planet, col)
                        el.set_text(val)
                         
                    elif widget_data['type'] == 'image':
                        # Load 128px planet image directly for 40x40 icons (PROJ-54 Phase 11)
                        # This is much more efficient than loading 512px and scaling down
                        img = None
                        if hasattr(planet, 'image_id') and planet.image_id:
                            # Use cached icon if already loaded for this planet
                            cache_key = f"icon_{planet.image_id}_{planet.image_rotation or 0}"

                            if cache_key not in icon_cache:
                                # Load 128px version directly from AssetManager
                                am = AssetManager.instance()
                                img = am.load_planet_image(planet.image_id, requested_size=128)

                                if img and img != am.get_missing_texture():
                                    # Apply rotation if specified
                                    if hasattr(planet, 'image_rotation') and planet.image_rotation and planet.image_rotation != 0.0:
                                        img = pygame.transform.rotate(img, planet.image_rotation)

                                    # Scale to 40x40 and cache
                                    icon_cache[cache_key] = pygame.transform.smoothscale(img, (40, 40))
                                else:
                                    # Image load failed - use blank
                                    img = None

                            if cache_key in icon_cache:
                                el.set_image(icon_cache[cache_key])
                            else:
                                # Fallback: blank surface
                                if '_blank_icon' not in icon_cache:
                                    icon_cache['_blank_icon'] = pygame.Surface((40, 40))
                                el.set_image(icon_cache['_blank_icon'])
                        else:
                            # No image_id - use blank surface
                            if '_blank_icon' not in icon_cache:
                                icon_cache['_blank_icon'] = pygame.Surface((40, 40))
                            el.set_image(icon_cache['_blank_icon'])
            else:
                # Scrolled past end
                row_panel.hide()
                row_data['planet'] = None  # Clear planet reference (PROJ-54)
            
    def process_event(self, event):
        handled = super().process_event(event)

        # Handle Build Queue button click (PROJ-54)
        if event.type == UI_BUTTON_PRESSED:
            if event.ui_element == self.btn_build_queue:
                if self.selected_planet:
                    # Open build queue for selected planet
                    # Note: Exact method may vary - need to determine how to trigger build queue
                    # For now, we'll emit a log message as a placeholder
                    log_info(f"Build Queue button clicked for planet: {self.selected_planet.name}")
                    # TODO: Implement actual build queue opening mechanism
                    # Possible approaches:
                    # 1. self.manager.close() then trigger build queue via callback
                    # 2. Emit custom event that parent screen handles
                    # 3. Call method on parent screen if reference exists
                return True

        # F9 key enables debug mode for next click
        if event.type == pygame.KEYDOWN and event.key == pygame.K_F9:
            self._debug_next_click = True
            log_info("=== PLANET LIST DEBUG MODE ENABLED - Click on a planet row now ===")
            return True

        # Debug: Log ALL events when debug mode is enabled
        if self._debug_next_click:
            log_info(f"DEBUG EVENT: type={event.type}, event={event}")

        # Handle planet row clicks (PROJ-54)
        # Note: Using MOUSEBUTTONUP because MOUSEBUTTONDOWN is consumed by parent UIWindow
        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:  # Left click
            mouse_pos = event.pos

            # Debug logging if enabled
            if self._debug_next_click:
                log_info(f"DEBUG: Mouse click at {mouse_pos}")
                log_info(f"DEBUG: Window rect: {self.rect}, abs_rect: {self.get_abs_rect()}")
                log_info(f"DEBUG: main_panel abs_rect: {self.main_panel.get_abs_rect()}")
                log_info(f"DEBUG: list_panel abs_rect: {self.list_panel.get_abs_rect()}")
                log_info(f"DEBUG: filtered_planets count: {len(self.filtered_planets)}")
                log_info(f"DEBUG: row_height: {self.row_height}")
                log_info(f"DEBUG: scroll_bar.start_percentage: {self.scroll_bar.start_percentage}")

            # Check if click is within the list panel area
            list_abs_rect = self.list_panel.get_abs_rect()
            if list_abs_rect.collidepoint(mouse_pos):
                # Calculate which row was clicked based on scroll position
                relative_y = mouse_pos[1] - list_abs_rect.top

                # Account for scroll offset
                scroll_pct = self.scroll_bar.start_percentage
                total_h = len(self.filtered_planets) * self.row_height
                scroll_y = scroll_pct * total_h

                # Calculate the data index of the clicked row
                absolute_y = relative_y + scroll_y
                clicked_index = int(absolute_y // self.row_height)

                if self._debug_next_click:
                    log_info(f"DEBUG: Click IS inside list_panel!")
                    log_info(f"DEBUG: relative_y={relative_y}, scroll_y={scroll_y:.1f}")
                    log_info(f"DEBUG: absolute_y={absolute_y:.1f}, clicked_index={clicked_index}")
                    self._debug_next_click = False  # Reset debug mode

                if 0 <= clicked_index < len(self.filtered_planets):
                    planet = self.filtered_planets[clicked_index]
                    log_info(f"DEBUG: Would select planet: {planet.name}")
                    if planet != self.selected_planet:
                        log_debug(f"Selecting planet: {planet.name}")
                        self._on_planet_selected(planet)
                    return True  # Consume the event
            else:
                if self._debug_next_click:
                    log_info(f"DEBUG: Click is OUTSIDE list_panel bounds!")
                    log_info(f"DEBUG: list_abs_rect: {list_abs_rect}")
                    log_info(f"DEBUG: mouse_pos: {mouse_pos}")
                    self._debug_next_click = False  # Reset debug mode

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
                    self._update_visible_rows()
                return True  # Consume event

        return handled

    def update(self, time_delta):
        super().update(time_delta)
        
        if self.btn_apply.check_pressed():
            self.refresh_list()
            
        if self.btn_all_types.check_pressed():
            for t, btn in self.ui_filters['types'].items():
                self.filter_types[t] = True
                btn.select()
                btn.set_text(f"[{t}]")
            self.refresh_list()

        if self.btn_none_types.check_pressed():
            for t, btn in self.ui_filters['types'].items():
                self.filter_types[t] = False
                btn.unselect()
                btn.set_text(f"{t}")
            self.refresh_list()
            
        # Check Scrollbar
        if self.scroll_bar.check_has_moved_recently():
             self._update_visible_rows()

        # Future enhancement: Handle resize to update viewport/row count.
        # self.list_view_rect might need updating if window resizes.
            
        # Sync Sliders -> Text (One way, unless focused? No, text value follows slider if slider moves)
        for key in ['gravity', 'temp', 'mass']:
            f = self.ui_filters[key]
            # Min
            s_val = f['min'].get_current_value()
            if not f['min_txt'].is_focused:
                 # Check tolerance to avoid fighting?
                 # Just formatting
                 current_txt = f['min_txt'].get_text()
                 new_txt = f"{s_val:.1f}"
                 if current_txt != new_txt:
                     f['min_txt'].set_text(new_txt)
            
            # Max
            s_val = f['max'].get_current_value()
            if not f['max_txt'].is_focused:
                 current_txt = f['max_txt'].get_text()
                 new_txt = f"{s_val:.1f}"
                 if current_txt != new_txt:
                     f['max_txt'].set_text(new_txt)

        # Handle Type Toggles
        for t, btn in self.ui_filters.get('types', {}).items():
            if btn.check_pressed():
                state = not self.filter_types[t]
                self.filter_types[t] = state
                if state:
                    btn.select()
                    btn.set_text(f"[{t}]")
                else:
                    btn.unselect()
                    btn.set_text(f"{t}")
                self.refresh_list()

        # Handle Owner All/None buttons (BUG-27)
        if hasattr(self, 'btn_all_owners') and self.btn_all_owners.check_pressed():
            for o, btn in self.ui_filters.get('owners', {}).items():
                self.filter_owner[o] = True
                btn.select()
                btn.set_text(f"[{o}]")
            self.refresh_list()

        if hasattr(self, 'btn_none_owners') and self.btn_none_owners.check_pressed():
            for o, btn in self.ui_filters.get('owners', {}).items():
                self.filter_owner[o] = False
                btn.unselect()
                btn.set_text(f"{o}")
            self.refresh_list()

        # Handle Owner Toggles (BUG-27)
        for o, btn in self.ui_filters.get('owners', {}).items():
            if btn.check_pressed():
                state = not self.filter_owner[o]
                self.filter_owner[o] = state
                if state:
                    btn.select()
                    btn.set_text(f"[{o}]")
                else:
                    btn.unselect()
                    btn.set_text(f"{o}")
                self.refresh_list()

        # Handle Column Toggles
        for col_id, btn in self.ui_filters.get('columns', {}).items():
            if btn.check_pressed():
                col = btn.col_ref
                self.column_mgr.toggle_visibility(col['id'])

                # Update text
                t = f"[x] {col['title'] or col['id']}" if col['visible'] else f"[ ] {col['title'] or col['id']}"
                btn.set_text(t)

                # Rebuild
                self.column_mgr.rebuild_headers()
                self._rebuild_row_pool()  # Rebuild pool to match new col visibility
                self.refresh_list()

        # Handle Header Arrows and Sort Clicks
        sort_changed, columns_changed = self.column_mgr.handle_header_clicks()
        if columns_changed:
            self._rebuild_row_pool()
            self.refresh_list()
        elif sort_changed:
            self.refresh_list()

        # Handle Presets
        # Lazy init tracker
        if not hasattr(self, 'last_preset_selection'):
            self.last_preset_selection = self.dd_presets.selected_option
            
        if self.dd_presets.selected_option != self.last_preset_selection:
            # Change detected
            self.last_preset_selection = self.dd_presets.selected_option
            name = self.last_preset_selection
            if self.preset_manager.has_preset(name):
                self._apply_state(self.preset_manager.get_preset(name))

        if self.btn_save_preset.check_pressed():
            name = self.txt_preset_name.get_text()
            if name:
                state = self._capture_current_state()
                self.preset_manager.save_preset(name, state)
                # Refresh Dropdown (Recreate)
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
        self._rebuild_row_pool()
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
        """Handle planet selection - create/update detail panel. (PROJ-54)"""
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
        # Clean up column manager
        if hasattr(self, 'column_mgr'):
            self.column_mgr.kill()

        # Clean up planet detail panel (PROJ-54)
        if self.planet_detail_panel:
            self.planet_detail_panel.kill()
            self.planet_detail_panel = None

        # Clean up button (PROJ-54)
        if self.btn_build_queue:
            self.btn_build_queue.kill()
            self.btn_build_queue = None

        if self.on_close_callback:
            self.on_close_callback()
        super().kill()
