import pygame
import pygame_gui
import json
import os
from game.core.constants import DATA_DIR
from pygame_gui.elements import UIWindow, UIPanel, UILabel, UIButton, UIScrollingContainer, UITextEntryLine, UISelectionList, UIHorizontalSlider, UIDropDownMenu, UIImage, UIVerticalScrollBar
from pygame_gui import UI_TEXT_ENTRY_FINISHED

class PlanetListWindow(UIWindow):
    def __init__(self, rect, manager, galaxy, empire, on_close_callback=None):
        super().__init__(rect, manager, window_display_title="Galactic Planet Registry", resizable=True)
        
        self.galaxy = galaxy
        self.empire = empire # Current player empire for "Owner" context
        self.on_close_callback = on_close_callback
        
        # --- Layout Constants ---
        self.sidebar_width = 300
        self.header_height = 40
        self.row_height = 50
        
        # --- State ---
        self.all_planets = self._gather_planets()
        self.filtered_planets = []
        
        # Filter States
        self.filter_name = ""
        self.filter_types = {'Terran': True, 'Gas': True, 'Ice': True, 'Desert': True, 'Moon': True}
        self.filter_owner = {'Player': True, 'Enemy': True, 'Unowned': True}
        self.filter_ranges = {
            'gravity': [0.0, 10.0],   # Min/Max g
            'temp': [0, 2000],       # Min/Max K
            'mass': [0.0, 500.0]    # Min/Max Earths
        }
        
        # Sort State
        self.sort_column_id = None
        self.sort_descending = False
        
        # UI References (for reading values)
        self.ui_filters = {}
        
        # Default Columns
        # ID, Width, Title, Attribute/Getter, Visible
        self.columns = [
            {'id': 'icon', 'width': 50, 'title': '', 'type': 'image', 'visible': True},
            {'id': 'name', 'width': 150, 'title': 'Name', 'attr': 'name', 'visible': True},
            {'id': 'type', 'width': 100, 'title': 'Type', 'attr': 'planet_type.name', 'visible': True},
            {'id': 'system', 'width': 120, 'title': 'System', 'func': self._get_system_name, 'visible': True},
            {'id': 'owner', 'width': 100, 'title': 'Owner', 'func': self._get_owner_name, 'visible': True},
            {'id': 'mass', 'width': 100, 'title': 'Mass (M_E)', 'func': self._get_mass_earth, 'visible': True},
            {'id': 'grav', 'width': 90, 'title': 'Grav (g)', 'func': lambda p: f"{p.surface_gravity/9.81:.2f}", 'visible': True},
            {'id': 'temp', 'width': 90, 'title': 'Temp (K)', 'attr': 'surface_temperature', 'fmt': "{:.0f}", 'visible': True},
            {'id': 'water', 'width': 90, 'title': 'Water %', 'attr': 'surface_water', 'fmt': "{:.0%}", 'visible': False},
            {'id': 'pressure', 'width': 100, 'title': 'Press (atm)', 'attr': 'total_pressure_atm', 'fmt': "{:.2f}", 'visible': False}
        ]
        
        # --- UI Containers ---
        
        # 1. Sidebar (Filters/Config)
        self.sidebar_panel = UIPanel(
            relative_rect=pygame.Rect(0, 0, self.sidebar_width, rect.height - 50),
            manager=manager,
            container=self,
            anchors={'left': 'left', 'top': 'top', 'bottom': 'bottom'}
        )
        
        self._init_sidebar()
        
        # 2. Main Content Area (Header + Scrollable List)
        main_w = rect.width - self.sidebar_width - 10
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
        
        # --- Initial Population ---
        self._rebuild_headers()
        self._rebuild_row_pool()
        self.refresh_list()
        
    def _gather_planets(self):
        """Collect all planets from the galaxy."""
        planets = []
        if self.galaxy and self.galaxy.systems:
            for s in self.galaxy.systems.values():
                for p in s.planets:
                    # Attach system ref for cached access if needed
                    p._temp_system_ref = s 
                    planets.append(p)
        return planets
        
    def _get_system_name(self, planet):
        if hasattr(planet, '_temp_system_ref'):
            return planet._temp_system_ref.name
        return "?"

    def _get_owner_name(self, planet):
        if planet.owner_id is None: return "Unowned"
        if planet.owner_id == self.empire.id: return "Player"
        return "Enemy" # Simplify for now
        
    def _get_mass_earth(self, planet):
         m_earth = 5.97e24
         return f"{planet.mass/m_earth:.2f}"

    def _init_sidebar(self):
        """Initialize Filter and Config controls."""
        # Use a scrolling container for the sidebar because filters are tall
        self.sidebar_scroller = UIScrollingContainer(
            relative_rect=pygame.Rect(0, 0, self.sidebar_width, self.rect.height - 50),
            manager=self.ui_manager,
            container=self.sidebar_panel,
            anchors={'left': 'left', 'right': 'right', 'top': 'top', 'bottom': 'bottom'}
        )
        content_container = self.sidebar_scroller.get_container()
        
        y_off = 10
        width = self.sidebar_width - 30 # Account for scrollbar
        
        # Title
        UILabel(pygame.Rect(10, y_off, width, 25), "FILTERS", self.ui_manager, container=content_container)
        y_off += 30
        
        # Name Filter
        self.txt_name_filter = UITextEntryLine(
            relative_rect=pygame.Rect(10, y_off, width, 30),
            manager=self.ui_manager,
            container=content_container
        )
        self.txt_name_filter.set_text("Search Name...")
        y_off += 40
        
        # --- Planet Type ---
        UILabel(pygame.Rect(10, y_off, width, 20), "Planet Type:", self.ui_manager, container=content_container)

        y_off += 25
        
        # All / None Buttons
        self.btn_all_types = UIButton(pygame.Rect(10, y_off, 60, 25), "All", self.ui_manager, container=content_container)
        self.btn_none_types = UIButton(pygame.Rect(80, y_off, 60, 25), "None", self.ui_manager, container=content_container)
        y_off += 30
        
        # Grid of checkboxes
        types = ['Terran', 'Gas', 'Ice', 'Desert', 'Moon']
        self.ui_filters['types'] = {}
        
        x_start = 10
        x = x_start
        for t in types:
            # Simple toggle button or checkbox? pygame_gui has specialized selection lists or just buttons.
            # Using UIButton with toggle behavior is easiest for grid.
            btn = UIButton(
                relative_rect=pygame.Rect(x, y_off, 80, 30),
                text=t,
                manager=self.ui_manager,
                container=content_container,
                object_id='@filter_toggle_on' # Assume custom ID or manage style manually
            )
            # Hack: Store state in button? Or just map it.
            # actually let's use a specialized check box if avail, but button is fine.
            # We'll simple handle clicks to toggle state.
            self.ui_filters['types'][t] = btn
            
            x += 90
            if x > width - 80:
                x = x_start
                y_off += 35
        if x != x_start: y_off += 35
        
        # --- Range Sliders ---
        # Helper to add range
        def add_range(label, key, min_limit, max_limit):
            nonlocal y_off
            UILabel(pygame.Rect(10, y_off, width, 20), label, self.ui_manager, container=content_container)
            y_off += 20
            
            # Min Row
            UILabel(pygame.Rect(10, y_off, 30, 24), "Min", self.ui_manager, container=content_container)
            s_min = UIHorizontalSlider(
                relative_rect=pygame.Rect(45, y_off, width - 105, 24),
                start_value=min_limit,
                value_range=(min_limit, max_limit),
                manager=self.ui_manager,
                container=content_container
            )
            t_min = UITextEntryLine(
                relative_rect=pygame.Rect(width - 55, y_off, 55, 24),
                manager=self.ui_manager,
                container=content_container
            )
            t_min.set_text(f"{min_limit:.1f}")
            y_off += 29
            
            # Max Row
            UILabel(pygame.Rect(10, y_off, 30, 24), "Max", self.ui_manager, container=content_container)
            s_max = UIHorizontalSlider(
                relative_rect=pygame.Rect(45, y_off, width - 105, 24),
                start_value=max_limit,
                value_range=(min_limit, max_limit),
                manager=self.ui_manager,
                container=content_container
            )
            t_max = UITextEntryLine(
                relative_rect=pygame.Rect(width - 55, y_off, 55, 24),
                manager=self.ui_manager,
                container=content_container
            )
            t_max.set_text(f"{max_limit:.1f}")
            y_off += 35
            
            self.ui_filters[key] = {
                'min': s_min, 'max': s_max,
                'min_txt': t_min, 'max_txt': t_max,
                'limits': (min_limit, max_limit)
            }

        add_range("Gravity (g)", 'gravity', 0.0, 10.0)
        add_range("Temp (K)", 'temp', 0, 2000)
        add_range("Mass (Earths)", 'mass', 0.0, 500.0) # Expanded for giants
        # Let's cap mass slider at 500 for now.
        
        # Button: Apply Filters
        self.btn_apply = UIButton(
            relative_rect=pygame.Rect(10, y_off, width, 30),
            text="Apply Filters",
            manager=self.ui_manager,
            container=content_container
        )
        y_off += 40
        
        # --- Column Configuration ---
        UILabel(pygame.Rect(10, y_off, width, 25), "COLUMNS", self.ui_manager, container=content_container)
        y_off += 30
        
        self.ui_filters['columns'] = {}
        for col in self.columns:
            # Checkbox for visibility
            # Use basic button with toggle logic or just click to toggle
            # State is in 'visible'
            t = f"[x] {col['title'] or col['id']}" if col['visible'] else f"[ ] {col['title'] or col['id']}"
            btn = UIButton(
                relative_rect=pygame.Rect(10, y_off, width, 30),
                text=t,
                manager=self.ui_manager,
                container=content_container
            )
            btn.col_ref = col
            self.ui_filters['columns'][col['id']] = btn
            y_off += 35
        
        y_off += 20
        UILabel(pygame.Rect(10, y_off, width, 25), "PRESETS", self.ui_manager, container=content_container)
        y_off += 30
        
        # Load Presets
        self.presets = self._load_presets_from_disk()
        opts = list(self.presets.keys())
        if "Default" not in opts: opts.insert(0, "Default")
        
        self.dd_presets = UIDropDownMenu(
            options_list=opts,
            starting_option="Default",
            relative_rect=pygame.Rect(10, y_off, width, 30),
            manager=self.ui_manager,
            container=content_container
        )
        y_off += 40
        
        # Save New
        self.txt_preset_name = UITextEntryLine(
            relative_rect=pygame.Rect(10, y_off, width - 60, 30),
            manager=self.ui_manager,
            container=content_container
        )
        self.txt_preset_name.set_text("New Preset Name")
        
        self.btn_save_preset = UIButton(
            relative_rect=pygame.Rect(width - 50, y_off, 50, 30),
            text="Save",
            manager=self.ui_manager,
            container=content_container
        )
        y_off += 40

        # Update scrolling area
        self.sidebar_scroller.set_scrollable_area_dimensions((width, y_off))
        
    def _rebuild_headers(self):
        """Build header row based on current self.columns"""
        # Clear existing headers
        if hasattr(self, 'header_elements'):
            for el in self.header_elements:
                el.kill()
        self.header_elements = []
        
        visible_cols = self._get_visible_columns()
        
        x_off = 0
        for i, col in enumerate(visible_cols):
            w = col['width']
            
            # Container for this header cell
            # rect = pygame.Rect(x_off, 0, w, self.header_height)
            
            # Buttons: [<] [Title] [>]
            # Size: 20px for arrows?
            arrow_w = 20
            title_w = w - (arrow_w * 2)
            
            # Left Arrow
            if i > 0: # Can move left
                btn_l = UIButton(
                    relative_rect=pygame.Rect(x_off, 0, arrow_w, self.header_height),
                    text="<",
                    manager=self.ui_manager,
                    container=self.header_container
                )
                self.header_elements.append(btn_l)
                # Store index and direction in object or dynamic map?
                btn_l.col_ref = col
                btn_l.direction = -1
            
            # Title (Clickable for Sorting)
            # visual indicator
            t_str = col['title']
            if self.sort_column_id == col['id']:
                t_str += " v" if self.sort_descending else " ^"
                
            btn_title = UIButton(
                relative_rect=pygame.Rect(x_off + arrow_w, 0, title_w, self.header_height),
                text=t_str,
                manager=self.ui_manager,
                container=self.header_container
            )
            self.header_elements.append(btn_title)
            btn_title.sort_col_ref = col
            
            # Right Arrow
            if i < len(visible_cols) - 1: # Can move right
                btn_r = UIButton(
                    relative_rect=pygame.Rect(x_off + w - arrow_w, 0, arrow_w, self.header_height),
                    text=">",
                    manager=self.ui_manager,
                    container=self.header_container
                )
                self.header_elements.append(btn_r)
                btn_r.col_ref = col
                btn_r.direction = 1
            
            x_off += w
            
    def _swap_columns(self, col_ref, direction):
        """Swap col_ref (dict) with its visual neighbor."""
        # Find index in MAIN list
        try:
            main_idx = self.columns.index(col_ref)
        except ValueError:
            return

        visible_cols = self._get_visible_columns()
        try:
            vis_idx = visible_cols.index(col_ref)
        except ValueError:
            return
            
        target_vis_idx = vis_idx + direction
        if 0 <= target_vis_idx < len(visible_cols):
            target_col = visible_cols[target_vis_idx]
            target_main_idx = self.columns.index(target_col)
            
            # Swap in main list
            self.columns[main_idx], self.columns[target_main_idx] = self.columns[target_main_idx], self.columns[main_idx]
            self._rebuild_headers()
            self._rebuild_row_pool() # Columns changed, need to rebuild widget structure
            self.refresh_list()

            
    def refresh_list(self):
        """Filter and update scrollbar."""
        # 1. Update Filter State from UI (lazy sync)
        search = self.txt_name_filter.get_text()
        if search == "Search Name...": search = ""
        
        min_g = self.ui_filters['gravity']['min'].get_current_value()
        max_g = self.ui_filters['gravity']['max'].get_current_value()
        
        min_t = self.ui_filters['temp']['min'].get_current_value()
        max_t = self.ui_filters['temp']['max'].get_current_value()
        
        # Mass
        min_m = self.ui_filters['mass']['min'].get_current_value()
        max_m = self.ui_filters['mass']['max'].get_current_value()
        
        
        self.filtered_planets = []
        for p in self.all_planets:
            match = True
            
            # Name
            if search and search.lower() not in p.name.lower(): match = False
            
            # Type (Heuristic mapping)
            p_type = 'Terran' # Default
            tn = p.planet_type.name.lower()
            if 'gas' in tn: p_type = 'Gas'
            elif 'ice' in tn: p_type = 'Ice'
            elif 'desert' in tn or 'hot' in tn: p_type = 'Desert'
            # Moon detection? usually implicit in name or parent?
            if 'moon' in tn: p_type = 'Moon'
            
            if not self.filter_types.get(p_type, True): match = False
            
            # Ranges
            g = p.surface_gravity / 9.81
            if g < min_g or g > max_g: match = False
            
            if p.surface_temperature < min_t or p.surface_temperature > max_t: match = False
            
            m_earth = p.mass / 5.97e24
            if m_earth < min_m or m_earth > max_m: match = False
            
            if match:
                self.filtered_planets.append(p)
                
        # 1b. Sort
        if self.sort_column_id:
            # Find col def
            col = next((c for c in self.columns if c['id'] == self.sort_column_id), None)
            if col:
                def sort_key(p):
                    val = None
                    if 'func' in col:
                        # This returns formatted string usually... dangerous for numeric sort
                        # But wait, helper funcs return strings currently. 
                        # We might need raw values. 
                        # Hack: Re-derive raw value for known numeric columns?
                        # Or rely on string sort? String sort "10.0" < "2.0" is bad.
                        
                        # Special case known numeric IDs or use attr if available
                        # Actually 'func' is only used for system name, owner, mass, gravity
                        if col['id'] == 'mass': return p.mass
                        if col['id'] == 'grav': return p.surface_gravity
                        val = col['func'](p)
                        
                    elif 'attr' in col:
                         attrs = col['attr'].split('.')
                         obj = p
                         for a in attrs:
                             if hasattr(obj, a): obj = getattr(obj, a)
                             else: obj = ""
                         val = obj
                    
                    if val is None: return ""
                    return val
                
                self.filtered_planets.sort(key=sort_key, reverse=self.sort_descending)
                
        # 2. Update Scrollbar
        total_h = len(self.filtered_planets) * self.row_height
        visible_h = self.list_view_rect.height
        
        if total_h > 0:
            percentage = min(1.0, visible_h / total_h)
        else:
            percentage = 1.0
            
        self.scroll_bar.set_visible_percentage(percentage)
        self.scroll_bar.scroll_position = 0.0 # Reset on refresh? Or try to keep?
        self.scroll_bar.bottom_limit = max(visible_h, total_h)
        # Force update call
        self.scroll_bar.redraw_scrollbar()
        
        # 3. Update Visible Rows
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
        
        visible_cols = self._get_visible_columns()
        
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
                    # Place holder image
                    img = UIImage(relative_rect=pygame.Rect(5, 5, 40, 40), 
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
        scroll_y = self.scroll_bar.scroll_position
        start_index = int(scroll_y // self.row_height)
        offset_y = scroll_y % self.row_height
        
        visible_h = self.list_view_rect.height
        
        for i, row_data in enumerate(self.row_pool):
            data_index = start_index + i
            
            row_panel = row_data['bg']
            
            if data_index < len(self.filtered_planets):
                planet = self.filtered_planets[data_index]
                
                # Position
                # We position the row relative to list_panel
                # Visual Y = i * row_height - offset_y
                # But to avoid "jumping" when scrolling large amounts, 
                # we just need to cover the viewport.
                
                y_pos = (i * self.row_height) - offset_y
                
                # Make visible and set position
                row_panel.show()
                row_panel.set_relative_position((0, y_pos))
                
                # Update Content
                for widget_data in row_data['widgets']:
                    col = widget_data['col']
                    el = widget_data['el']
                    
                    if widget_data['type'] == 'label':
                         val = ""
                         if 'func' in col:
                             val = col['func'](planet)
                         elif 'attr' in col:
                             attrs = col['attr'].split('.')
                             obj = planet
                             for a in attrs:
                                 if hasattr(obj, a): obj = getattr(obj, a)
                                 else: obj = "?"
                             
                             fmt = col.get('fmt')
                             if fmt and isinstance(obj, (int, float)):
                                 val = fmt.format(obj)
                             else:
                                 val = str(obj)
                         el.set_text(val)
                         
                    elif widget_data['type'] == 'image':
                        # Update image surface
                        if hasattr(planet, 'image'):
                            el.set_image(planet.image)
                        else:
                            # Fallback? Blank?
                            pass
            else:
                # Scrolled past end
                row_panel.hide()
            
    def process_event(self, event):
        handled = super().process_event(event)

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

        # Wheel Handling
        if event.type == pygame.MOUSEWHEEL:
             # Check collision with list panel
             m_pos = pygame.mouse.get_pos()
             if self.list_panel.get_abs_rect().collidepoint(m_pos):
                 self.scroll_bar.scroll_wheel_down = event.y < 0
                 self.scroll_bar.scroll_wheel_up = event.y > 0
                 # pygame_gui scrollbars handle wheel events if focused or manually poked?
                 # Actually UIVerticalScrollBar usually handles MOUSEWHEEL if hovered.
                 # But we can force it.
                 amount = 20 * event.y
                 self.scroll_bar.scroll_position -= amount
                 self.scroll_bar.scroll_position = min(self.scroll_bar.bottom_limit - self.scroll_bar.visible_percentage * self.scroll_bar.bottom_limit, max(0, self.scroll_bar.scroll_position))
                 # Clamp logic is tricky with bottom_limit definition in pygame_gui
                 # Actually simpler to let scrollbar handle it or use set_scroll_position
                 # But let's trust internal handling often works if hovered. 
                 # If not:
                 pass

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
                btn.set_text(f"{t}")
            self.refresh_list()
            
        # Check Scrollbar
        if self.scroll_bar.check_has_moved_recently():
             self._update_visible_rows()
             
        # TODO: Handle resize to update viewport/row count?
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
                
        # Handle Column Toggles
        for col_id, btn in self.ui_filters.get('columns', {}).items():
            if btn.check_pressed():
                col = btn.col_ref
                col['visible'] = not col['visible']
                
                # Update text
                t = f"[x] {col['title'] or col['id']}" if col['visible'] else f"[ ] {col['title'] or col['id']}"
                btn.set_text(t)
                
                # Rebuild
                self._rebuild_headers()
                self._rebuild_row_pool() # Rebuild pool to match new col visibility
                self.refresh_list()
                
        # Handle Header Arrows and Sort Clicks
        if hasattr(self, 'header_elements'):
            for el in self.header_elements:
                if isinstance(el, UIButton):
                    if hasattr(el, 'col_ref') and el.check_pressed():
                         # Move Column
                        self._swap_columns(el.col_ref, el.direction)
                    elif hasattr(el, 'sort_col_ref') and el.check_pressed():
                        # Sort Column
                        col = el.sort_col_ref
                        if self.sort_column_id == col['id']:
                            self.sort_descending = not self.sort_descending
                        else:
                            self.sort_column_id = col['id']
                            self.sort_descending = False
                        
                        self._rebuild_headers() # To update arrows
                        self.refresh_list()
                        
        # Handle Presets
        # Lazy init tracker
        if not hasattr(self, 'last_preset_selection'):
            self.last_preset_selection = self.dd_presets.selected_option
            
        if self.dd_presets.selected_option != self.last_preset_selection:
            # Change detected
            self.last_preset_selection = self.dd_presets.selected_option
            name = self.last_preset_selection
            if name in self.presets:
                self._apply_state(self.presets[name])
                
        if self.btn_save_preset.check_pressed():
            name = self.txt_preset_name.get_text()
            if name:
                state = self._capture_current_state()
                self.presets[name] = state
                self._save_presets_to_disk()
                print(f"Saved Preset: {name}")
                # Refresh Dropdown (Recreate)
                # Keep rect
                rect = self.dd_presets.relative_rect
                container = self.dd_presets.ui_container
                self.dd_presets.kill()
                
                opts = list(self.presets.keys())
                if "Default" not in opts: opts.insert(0, "Default")
                
                self.dd_presets = UIDropDownMenu(
                    options_list=opts,
                    starting_option=name,
                    relative_rect=rect,
                    manager=self.ui_manager,
                    container=container
                )
                self.last_preset_selection = name
            
    def _load_presets_from_disk(self):
        path = os.path.join(DATA_DIR, 'ui_presets.json')
        if os.path.exists(path):
            try:
                with open(path, 'r') as f:
                    return json.load(f)
            except:
                return {}
        return {}

    def _save_presets_to_disk(self):
        path = os.path.join(DATA_DIR, 'ui_presets.json')
        with open(path, 'w') as f:
            json.dump(self.presets, f, indent=2)

    def _capture_current_state(self):
        """Serialize current filters and column config."""
        # Columns: order and visibility
        cols_data = []
        for c in self.columns:
            cols_data.append({'id': c['id'], 'visible': c['visible']})
            
        # Filters
        filters_data = {
            'name': self.txt_name_filter.get_text(),
            'types': self.filter_types,
            'owner': self.filter_owner,
            'ranges': {
                'gravity': [self.ui_filters['gravity']['min'].get_current_value(), self.ui_filters['gravity']['max'].get_current_value()],
                'temp': [self.ui_filters['temp']['min'].get_current_value(), self.ui_filters['temp']['max'].get_current_value()],
                'mass': [self.ui_filters['mass']['min'].get_current_value(), self.ui_filters['mass']['max'].get_current_value()]
            }
        }
        
        return {
            'columns': cols_data,
            'filters': filters_data
        }

    def _apply_state(self, state):
        """Restore state."""
        # Restore Columns
        if 'columns' in state:
            # Reorder self.columns to match saved order
            saved_order = state['columns'] # List of {id, visible}
            
            new_cols = []
            # Create map of current columns
            current_map = {c['id']: c for c in self.columns}
            
            for item in saved_order:
                cid = item['id']
                if cid in current_map:
                    col = current_map[cid]
                    col['visible'] = item['visible']
                    new_cols.append(col)
                    del current_map[cid]
            
            # Append any remaining new columns (code updates)
            for c in current_map.values():
                new_cols.append(c)
                
            self.columns = new_cols
            
            # Update UI Checkboxes
            for cid, btn in self.ui_filters.get('columns', {}).items():
                # Find col
                col = next((c for c in self.columns if c['id'] == cid), None)
                if col:
                    t = f"[x] {col['title'] or col['id']}" if col['visible'] else f"[ ] {col['title'] or col['id']}"
                    btn.set_text(t)
                    
        # Restore Filters
        if 'filters' in state:
            f = state['filters']
            if 'name' in f: self.txt_name_filter.set_text(f['name'])
            if 'types' in f: self.filter_types = f['types']
            # Update Type Toggles UI? We didn't save refs explicitly in a clean way for updates.
            # But we can iterate.
            for t, btn in self.ui_filters.get('types', {}).items():
                if t in self.filter_types:
                    # Update visual state
                    if self.filter_types[t]:
                        btn.select()
                        btn.set_text(f"[{t}]")
                    else:
                        btn.unselect()
                        btn.set_text(f"{t}")
                        
            if 'ranges' in f:
                r = f['ranges']
                if 'gravity' in r: 
                    self.ui_filters['gravity']['min'].set_current_value(r['gravity'][0])
                    self.ui_filters['gravity']['max'].set_current_value(r['gravity'][1])
                if 'temp' in r:
                    self.ui_filters['temp']['min'].set_current_value(r['temp'][0])
                    self.ui_filters['temp']['max'].set_current_value(r['temp'][1])
                if 'mass' in r:
                    self.ui_filters['mass']['min'].set_current_value(r['mass'][0])
                    self.ui_filters['mass']['max'].set_current_value(r['mass'][1])
                
        self._rebuild_headers()
        self._rebuild_row_pool()
        self.refresh_list()
            
    def _get_visible_columns(self):
        """Return list of currently visible columns."""
        return [c for c in self.columns if c.get('visible', True)]

    def kill(self):
        if self.on_close_callback:
            self.on_close_callback()
        super().kill()
