import pygame
import pygame_gui
import json
import os
from game.core.constants import DATA_DIR
from pygame_gui.elements import UIWindow, UIPanel, UILabel, UIButton, UIScrollingContainer, UITextEntryLine, UISelectionList, UIHorizontalSlider, UIDropDownMenu

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
            'gravity': [0.0, 5.0],   # Min/Max g
            'temp': [0, 1000],       # Min/Max K
            'mass': [0.0, 5000.0]    # Min/Max Earths
        }
        
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
            {'id': 'mass', 'width': 80, 'title': 'Mass (M_E)', 'func': self._get_mass_earth, 'visible': True},
            {'id': 'grav', 'width': 80, 'title': 'Grav (g)', 'func': lambda p: f"{p.surface_gravity/9.81:.2f}", 'visible': True},
            {'id': 'temp', 'width': 80, 'title': 'Temp (K)', 'attr': 'surface_temperature', 'fmt': "{:.0f}", 'visible': True},
            {'id': 'water', 'width': 80, 'title': 'Water %', 'attr': 'surface_water', 'fmt': "{:.0%}", 'visible': False},
            {'id': 'pressure', 'width': 80, 'title': 'Press (atm)', 'attr': 'total_pressure_atm', 'fmt': "{:.2f}", 'visible': False}
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
        
        # Scrollable List
        self.list_container = UIScrollingContainer(
            relative_rect=pygame.Rect(0, self.header_height, main_w, rect.height - 50 - self.header_height),
            manager=manager,
            container=self.main_panel,
            anchors={'left': 'left', 'right': 'right', 'top': 'top', 'bottom': 'bottom'}
        )
        
        # --- Initial Population ---
        self._rebuild_headers()
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
            
            # Min Slider
            UILabel(pygame.Rect(10, y_off, 40, 20), "Min", self.ui_manager, container=content_container)
            s_min = UIHorizontalSlider(
                relative_rect=pygame.Rect(50, y_off, width - 60, 20),
                start_value=min_limit,
                value_range=(min_limit, max_limit),
                manager=self.ui_manager,
                container=content_container
            )
            y_off += 25
            
            # Max Slider
            UILabel(pygame.Rect(10, y_off, 40, 20), "Max", self.ui_manager, container=content_container)
            s_max = UIHorizontalSlider(
                relative_rect=pygame.Rect(50, y_off, width - 60, 20),
                start_value=max_limit,
                value_range=(min_limit, max_limit),
                manager=self.ui_manager,
                container=content_container
            )
            y_off += 30
            
            self.ui_filters[key] = (s_min, s_max)

        add_range("Gravity (g)", 'gravity', 0.0, 10.0)
        add_range("Temp (K)", 'temp', 0, 2000)
        add_range("Mass (Earths)", 'mass', 0.0, 20.0) # Gas giants are huge though? 318 Earths...
        # Let's cap mass slider at 20 (terran/super-terran focus) for now, or log scale? 
        # Linear slider for mass is tough.
        
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
            
            # Title
            lbl = UILabel(
                relative_rect=pygame.Rect(x_off + arrow_w, 0, title_w, self.header_height),
                text=col['title'],
                manager=self.ui_manager,
                container=self.header_container
            )
            self.header_elements.append(lbl)
            
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
            self.refresh_list()

            
    def refresh_list(self):
        """Filter and Rebuild the list."""
        # 1. Update Filter State from UI (lazy sync)
        search = self.txt_name_filter.get_text()
        if search == "Search Name...": search = ""
        
        min_g = self.ui_filters['gravity'][0].get_current_value()
        max_g = self.ui_filters['gravity'][1].get_current_value()
        
        min_t = self.ui_filters['temp'][0].get_current_value()
        max_t = self.ui_filters['temp'][1].get_current_value()
        
        # Mass logic needs care, but just raw value
        min_m = self.ui_filters['mass'][0].get_current_value()
        max_m = self.ui_filters['mass'][1].get_current_value()
        
        
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
                
        # 2. Rebuild UI
        # Clear existing rows
        if hasattr(self, 'row_elements'):
            for el in self.row_elements:
                el.kill()
        self.row_elements = []
        
        # 3. Populate
        total_h = len(self.filtered_planets) * self.row_height
        self.list_container.set_scrollable_area_dimensions((max(500, self.get_total_row_width()), total_h))
        
        y_off = 0
        for p in self.filtered_planets:
            self._create_row(p, y_off)
            y_off += self.row_height
            
    def get_total_row_width(self):
        return sum(c['width'] for c in self._get_visible_columns())

    def _create_row(self, planet, y_pos):
        container = self.list_container.get_container() # The internal scrollable one
        x_off = 0
        
        for col in self._get_visible_columns():
            w = col['width']
            rect = pygame.Rect(x_off, y_pos, w, self.row_height)
            
            # Content
            val = ""
            if 'func' in col:
                val = col['func'](planet)
            elif 'attr' in col:
                # Deep traverse? planet_type.name
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
            
            if col['id'] == 'icon':
                pass
            else:
                 lbl = UILabel(rect, val, self.ui_manager, container=container)
                 self.row_elements.append(lbl)
            
            x_off += w
            
    def update(self, time_delta):
        super().update(time_delta)
        
        if self.btn_apply.check_pressed():
            self.refresh_list()
            
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
                self.refresh_list()
                
        # Handle Header Arrows
        if hasattr(self, 'header_elements'):
            for el in self.header_elements:
                if isinstance(el, UIButton) and hasattr(el, 'col_ref'):
                    if el.check_pressed():
                        self._swap_columns(el.col_ref, el.direction)
                        
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
                'gravity': [self.ui_filters['gravity'][0].get_current_value(), self.ui_filters['gravity'][1].get_current_value()],
                'temp': [self.ui_filters['temp'][0].get_current_value(), self.ui_filters['temp'][1].get_current_value()],
                'mass': [self.ui_filters['mass'][0].get_current_value(), self.ui_filters['mass'][1].get_current_value()]
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
                    self.ui_filters['gravity'][0].set_current_value(r['gravity'][0])
                    self.ui_filters['gravity'][1].set_current_value(r['gravity'][1])
                # ... others implied
                
        self._rebuild_headers()
        self.refresh_list()
            
    def _get_visible_columns(self):
        """Return list of currently visible columns."""
        return [c for c in self.columns if c.get('visible', True)]

    def kill(self):
        if self.on_close_callback:
            self.on_close_callback()
        super().kill()
