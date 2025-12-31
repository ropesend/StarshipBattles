import pygame
import pygame_gui
from pygame_gui.elements import UIPanel, UILabel, UITextEntryLine, UIDropDownMenu, UITextBox, UIImage

from ship import VEHICLE_CLASSES
from ai import COMBAT_STRATEGIES

class StatRow:
    """Helper class to manage a single statistic row (Label | Value | Unit) with caching."""
    def __init__(self, key, label_text, manager, container, x, y, width):
        self.key = key
        # Layout: Label 50%, Value 30%, Unit 20%
        lbl_w = int(width * 0.50)
        val_w = int(width * 0.30)
        unit_w = width - lbl_w - val_w
        
        self.label = UILabel(pygame.Rect(x, y, lbl_w, 20), f"{label_text}:", 
                           manager=manager, container=container, object_id="#stat_label")
        self.value = UILabel(pygame.Rect(x + lbl_w, y, val_w, 20), "--", 
                           manager=manager, container=container, object_id="#stat_value")
        self.unit = UILabel(pygame.Rect(x + lbl_w + val_w, y, unit_w, 20), "", 
                          manager=manager, container=container, object_id="#stat_unit")
        
        self._last_val = None
        self._last_unit = None
        self._visible = True

    def update(self, val_text, unit_text=""):
        if self._last_val != val_text:
            self.value.set_text(val_text)
            self._last_val = val_text
            
        if self._last_unit != unit_text:
            self.unit.set_text(unit_text)
            self._last_unit = unit_text

    def set_visible(self, visible):
        if self._visible == visible:
            return
            
        if visible:
            self.label.show()
            self.value.show()
            self.unit.show()
        else:
            self.label.hide()
            self.value.hide()
            self.unit.hide()
        self._visible = visible

# Configuration for Stat Sections




class BuilderRightPanel:
    def __init__(self, builder, manager, rect, event_bus=None):
        self.builder = builder
        self.manager = manager
        self.rect = rect
        
        if event_bus:
            event_bus.subscribe("SHIP_UPDATED", self.on_ship_updated)
        
        self.panel = UIPanel(
            relative_rect=rect,
            manager=manager,
            object_id='#right_panel'
        )
        
        self.setup_controls()
        self.setup_stats()
        
    def on_ship_updated(self, ship):
        self.update_stats_display(ship)

    def setup_controls(self):
        y = 10
        width = self.rect.width
        col_w = width - 20
        
        # Name
        UILabel(pygame.Rect(10, y, 60, 25), "Name:", manager=self.manager, container=self.panel)
        self.name_entry = UITextEntryLine(pygame.Rect(70, y, 195, 30), manager=self.manager, container=self.panel)
        self.name_entry.set_text(self.builder.ship.name)
        y += 40
        
        # Theme
        UILabel(pygame.Rect(10, y, 60, 25), "Theme:", manager=self.manager, container=self.panel)
        theme_options = self.builder.theme_manager.get_available_themes()
        curr_theme = getattr(self.builder.ship, 'theme_id', 'Federation')
        if theme_options and curr_theme not in theme_options: curr_theme = theme_options[0]
        
        self.theme_dropdown = UIDropDownMenu(theme_options, curr_theme, pygame.Rect(70, y, 195, 30), manager=self.manager, container=self.panel)
        y += 40
        
        # Vehicle Type
        UILabel(pygame.Rect(10, y, 60, 25), "Type:", manager=self.manager, container=self.panel)
        # Get unique types
        types = sorted(list(set(c.get('type', 'Ship') for c in VEHICLE_CLASSES.values())))
        if not types: types = ["Ship"]
        
        curr_type = getattr(self.builder.ship, 'vehicle_type', "Ship")
        if curr_type not in types: curr_type = types[0]
        
        self.vehicle_type_dropdown = UIDropDownMenu(types, curr_type, pygame.Rect(70, y, 195, 30), manager=self.manager, container=self.panel)
        y += 40

        # Class
        UILabel(pygame.Rect(10, y, 60, 25), "Class:", manager=self.manager, container=self.panel)
        # Filter classes by current type and sort by max_mass (smallest to largest)
        class_options = [(name, cls.get('max_mass', 0)) for name, cls in VEHICLE_CLASSES.items() if cls.get('type', 'Ship') == curr_type]
        class_options.sort(key=lambda x: x[1])  # Sort by max_mass
        class_options = [name for name, _ in class_options]  # Extract just names
        if not class_options: class_options = ["Escort"]

        curr_class = self.builder.ship.ship_class
        if curr_class not in class_options: curr_class = class_options[0]
        
        self.class_dropdown = UIDropDownMenu(class_options, curr_class, pygame.Rect(70, y, 195, 30), manager=self.manager, container=self.panel)
        y += 40
        
        # AI
        UILabel(pygame.Rect(10, y, 60, 25), "AI:", manager=self.manager, container=self.panel)
        ai_options = [strat.get('name', sid.replace('_', ' ').title()) for sid, strat in COMBAT_STRATEGIES.items()]
        
        ai_display = self.builder.ship.ai_strategy.replace('_', ' ').title()
        for sid, strat in COMBAT_STRATEGIES.items():
            if sid == self.builder.ship.ai_strategy:
                ai_display = strat.get('name', ai_display)
                break
                
        self.ai_dropdown = UIDropDownMenu(ai_options, ai_display, pygame.Rect(70, y, 195, 30), manager=self.manager, container=self.panel)
        
        # Portrait Image (Side by Side)
        # Controls end around y ≈ 10 + 4*40 = 170. Next is 210.
        # Let's put image at x=280, y=10.
        # Height ≈ 200 (5 rows * 40). Width ≈ 200.
        self.portrait_image = None
        img_x = 280
        img_size = 200 # Approx match height of 5 rows (200px)
        self.portrait_rect = pygame.Rect(img_x, 10, img_size, img_size) # Fixed slot
        
        self.update_portrait_image()
        
        # Set last_y to below the TALLEST element (controls or image)
        # Controls: y starts 10, 5 rows of 40 = 210.
        y += 40 # Ends at 210
        
        self.last_y = max(y, 10 + img_size) + 10

    def refresh_controls(self):
        """Update all UI controls to match the current ship state."""
        import pygame
        from pygame_gui.elements import UIDropDownMenu
        
        s = self.builder.ship
        
        # 1. Name
        self.name_entry.set_text(s.name)
        
        # Preservation of Rects
        theme_rect = self.theme_dropdown.relative_rect
        type_rect = self.vehicle_type_dropdown.relative_rect
        class_rect = self.class_dropdown.relative_rect
        ai_rect = self.ai_dropdown.relative_rect
        
        # Kill old dropdowns
        self.theme_dropdown.kill()
        self.vehicle_type_dropdown.kill()
        self.class_dropdown.kill()
        self.ai_dropdown.kill()
        
        # 2. Recreate Theme
        theme_options = self.builder.theme_manager.get_available_themes()
        curr_theme = getattr(s, 'theme_id', 'Federation')
        if theme_options and curr_theme not in theme_options: curr_theme = theme_options[0]
        
        self.theme_dropdown = UIDropDownMenu(theme_options, curr_theme, theme_rect, manager=self.manager, container=self.panel)
        
        # 3. Recreate Type
        # Get unique types
        types = sorted(list(set(c.get('type', 'Ship') for c in VEHICLE_CLASSES.values())))
        if not types: types = ["Ship"]
        
        curr_type = getattr(s, 'vehicle_type', "Ship")
        # Ensure consistency from class if vehicle_type not set or mismatched
        class_def = VEHICLE_CLASSES.get(s.ship_class, {})
        if class_def:
             curr_type = class_def.get('type', curr_type)
        
        if curr_type not in types: curr_type = types[0]
        
        self.vehicle_type_dropdown = UIDropDownMenu(types, curr_type, type_rect, manager=self.manager, container=self.panel)
        
        # 4. Recreate Class
        class_options = [(name, cls.get('max_mass', 0)) for name, cls in VEHICLE_CLASSES.items() if cls.get('type', 'Ship') == curr_type]
        class_options.sort(key=lambda x: x[1])  # Sort by max_mass
        class_options = [name for name, _ in class_options]  # Extract just names
        if not class_options: class_options = ["Escort"]

        curr_class = s.ship_class
        if curr_class not in class_options: 
            # If current class is not in the list (e.g. type changed implicitly), force it or pick first?
            # Ideally we keep the class if valid.
            if curr_class in VEHICLE_CLASSES:
                 # It exists but wasn't in list? Means type mismatch in logic above.
                 # Just default to first option if we can't find it.
                 curr_class = class_options[0]
        
        self.class_dropdown = UIDropDownMenu(class_options, curr_class, class_rect, manager=self.manager, container=self.panel)
        
        # 5. Recreate AI
        ai_options = [strat.get('name', sid.replace('_', ' ').title()) for sid, strat in COMBAT_STRATEGIES.items()]
        
        ai_display = s.ai_strategy.replace('_', ' ').title()
        for sid, strat in COMBAT_STRATEGIES.items():
            if sid == s.ai_strategy:
                ai_display = strat.get('name', ai_display)
                break
                
        self.ai_dropdown = UIDropDownMenu(ai_options, ai_display, ai_rect, manager=self.manager, container=self.panel)

        # 6. Update Portrait
        self.update_portrait_image()


    def update_portrait_image(self):
        """Update the ship portrait based on current theme and class."""
        import os
        import re
        
        # Determine paths
        theme = getattr(self.builder.ship, 'theme_id', 'Federation')
        ship_class = self.builder.ship.ship_class
        
        # Map theme ID to folder name if necessary (simple map for now, or trust ID)
        # Theme IDs are usually "Federation", "Klingons", etc.
        # But let's check if we need mapping. The script used:
        # fed -> Federation, etc. But the game uses full names likely.
        # Let's assume theme_id matches directory name for now as per `ShipThemeManager`.
        
        # Filename Logic:
        # Standard: "Battle Cruiser" -> "BattleCruiser_Portrait.jpg"
        # Subtypes: "Fighter (Small)" -> "SmallFighter_Portrait.jpg"
        
        match = re.match(r"(.*)\s+\((.*)\)", ship_class)
        if match:
             base = match.group(1).strip().replace(" ", "")
             sub = match.group(2).strip().replace(" ", "")
             class_clean = f"{sub}{base}"
        else:
             class_clean = ship_class.replace(" ", "")

        filename = f"{class_clean}_Portrait.jpg"
        
        base_path = "resources/Portraits"
        # We need absolute path or relative to CWD
        # Assuming CWD is project root
        full_path = os.path.join(base_path, theme, filename)
        
        # Check for new location: Resources/ShipThemes/{theme}/Portraits
        new_loc = os.path.join("Resources", "ShipThemes", theme, "Portraits", filename)
        if os.path.exists(new_loc):
            full_path = new_loc
            
        if not os.path.exists(full_path):
            # Try with spaces?
            full_path_space = os.path.join(base_path, theme, f"{ship_class}_Portrait.jpg")
            if os.path.exists(full_path_space):
                full_path = full_path_space
            else:
                 # Fallback or None
                 if self.portrait_image:
                     self.portrait_image.kill()
                     self.portrait_image = None
                 return

        try:
            image_surf = pygame.image.load(full_path).convert_alpha()
            
            # Scale to fit width, maintaining aspect
            max_w = self.portrait_rect.width
            # Allow height to match width (square)
            max_h = self.portrait_rect.height
            
            img_w, img_h = image_surf.get_size()
            scale = min(max_w / img_w, max_h / img_h)
            
            if scale < 1.0:
                new_w = int(img_w * scale)
                new_h = int(img_h * scale)
                image_surf = pygame.transform.smoothscale(image_surf, (new_w, new_h))
            
            # Center it
            final_w, final_h = image_surf.get_size()
            center_x = self.portrait_rect.x + (max_w - final_w) // 2
            center_y = self.portrait_rect.y + (max_h - final_h) // 2
            
            # Update rect to centered position
            display_rect = pygame.Rect(center_x, center_y, final_w, final_h)
            
            if self.portrait_image:
                self.portrait_image.kill()
                
            self.portrait_image = UIImage(
                relative_rect=display_rect,
                image_surface=image_surf,
                manager=self.manager,
                container=self.panel
            )
            
        except Exception as e:
            print(f"Failed to load portrait {full_path}: {e}")




    def setup_stats(self):
        y = self.last_y
        
        # Columns
        # Width available
        full_w = self.rect.width
        col_gap = 10
        margin = 10
        avail_w = full_w - (2 * margin) - col_gap
        col_w = avail_w // 2
        
        col1_x = margin
        col2_x = margin + col_w + col_gap
        
        start_y = y
        
        self.rows_map = {} # Store StatRow instances by key
        
        # === Generic Helper to Build Section ===
        def build_section(title, stats_list, x, start_y):
            curr_y = start_y
            UILabel(pygame.Rect(x, curr_y, col_w, 25), f"── {title} ──", manager=self.manager, container=self.panel)
            curr_y += 30
            
            for stat_def in stats_list:
                row = StatRow(stat_def.key, stat_def.label, self.manager, self.panel, x, curr_y, col_w)
                row.definition = stat_def # Attach definition to row for update loop
                self.rows_map[stat_def.key] = row
                curr_y += 20
            
            return curr_y + 10

        from ui.builder.stats_config import STATS_GENERAL, STATS_FIGHTER, STATS_CREW, STATS_ENDURANCE

        # FREEZING CONFIG (Snapshot for this instance)
        self.config_general = STATS_GENERAL
        self.config_fighter = STATS_FIGHTER
        self.config_crew = STATS_CREW
        self.config_endurance = STATS_ENDURANCE
        
        # === Column 1: Ship Stats ===
        col1_max_y = build_section("Ship Stats", self.config_general, col1_x, start_y)
        
        # === Column 2: Fighter, Layers, Crew, Endurance ===
        y = start_y
        
        # Fighter
        y = build_section("Fighter Ops", self.config_fighter, col2_x, y)
        
        # Layers (Special Case: Dynamic)
        UILabel(pygame.Rect(col2_x, y, col_w, 20), "── Layer Usage ──", manager=self.manager, container=self.panel)
        y += 22
        self.layer_rows = []
        for i in range(4):
            sr = StatRow(f"layer_{i}", f"Slot {i}", self.manager, self.panel, col2_x, y, col_w)
            sr.set_visible(False)
            self.layer_rows.append(sr)
            y += 22
        y += 10
        
        # Crew
        y = build_section("Crew", self.config_crew, col2_x, y)
        
        # Endurance
        y = build_section("Combat Endurance", self.config_endurance, col2_x, y)
        
        col2_max_y = y
        
        # === Requirements (Bottom, Split) ===
        y = max(col1_max_y, col2_max_y) + 10
        
        # Split Headers
        UILabel(pygame.Rect(col1_x, y, col_w, 20), "── Requirements ──", manager=self.manager, container=self.panel)
        UILabel(pygame.Rect(col2_x, y, col_w, 20), "── Recommendations ──", manager=self.manager, container=self.panel)
        y += 25
        
        rem_h = self.rect.height - y - 10
        if rem_h < 50: rem_h = 50 # Minimum height
        
        self.req_box_left = UITextBox("✓ All requirements met", pygame.Rect(col1_x, y, col_w, rem_h), manager=self.manager, container=self.panel)
        self.req_box_right = UITextBox("", pygame.Rect(col2_x, y, col_w, rem_h), manager=self.manager, container=self.panel)

    def update_stats_display(self, s):
        """Update ship stats labels using Data-Driven Config."""
        
        # Update General/Fighter/Crew/Endurance via Generic Loop
        all_configs = self.config_general + self.config_fighter + self.config_crew + self.config_endurance
        
        for stat_def in all_configs:
            row = self.rows_map.get(stat_def.key)
            if row:
                val = stat_def.get_value(s)
                
                # Check validation
                is_ok, status_txt = stat_def.get_status(s, val)
                
                fmt_val = stat_def.format_value(val)
                unit_val = stat_def.get_display_unit(s, val)
                
                final_unit = f"{unit_val}"
                if status_txt:
                     final_unit += f" {status_txt}"
                     
                row.update(fmt_val, final_unit)
        
        # Update layer stats (Still somewhat special case due to dynamic list)
        from ship import LayerType
        
        # Hide all first
        for row in self.layer_rows:
            row.set_visible(False)
            
        sorted_layers = sorted(s.layers.items(), key=lambda x: x[0].value) 
        
        slot_idx = 0
        for layer_type, layer_data in sorted_layers:
            if slot_idx < len(self.layer_rows):
                status = s.layer_status.get(layer_type, {})
                ratio = status.get('ratio', 0) * 100
                limit = status.get('limit', 1.0) * 100
                is_ok = status.get('ok', True)
                mass = status.get('mass', 0)
                
                status_icon = "✓" if is_ok else "✗"
                
                row = self.layer_rows[slot_idx]
                
                # Update Label directly since it changes per slot in this dynamic list
                row.label.set_text(f"{layer_type.name}:")
                row.update(f"{ratio:.0f}% / {limit:.0f}%", f" ({mass:.0f}t) {status_icon}")
                
                row.set_visible(True)
                
                slot_idx += 1
        
        # Update requirements (Left)
        missing_reqs = s.get_missing_requirements()
        if not s.mass_limits_ok:
            missing_reqs.append("⚠ Over mass limit")
            
        full_list_req = []
        for req in missing_reqs:
            full_list_req.append(f"<font color='#ffaa55'>{req}</font>")
        
        if not full_list_req:
            html_left = "<font color='#88ff88'>✓ All met</font>"
        else:
            html_left = "<br>".join(full_list_req)
        
        self.req_box_left.html_text = html_left
        self.req_box_left.rebuild()

        # Update warnings (Right)
        warnings = s.get_validation_warnings()
        full_list_warn = []
        for warn in warnings:
            full_list_warn.append(f"<font color='#ffff88'>⚠ {warn}</font>")
            
        if not full_list_warn:
            html_right = "<font color='#888888'>No recommendations</font>"
        else:
            html_right = "<br>".join(full_list_warn)
            
        self.req_box_right.html_text = html_right
        self.req_box_right.rebuild()
