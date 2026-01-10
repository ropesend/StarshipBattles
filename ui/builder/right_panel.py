import pygame
import pygame_gui
from pygame_gui.elements import UIPanel, UILabel, UITextEntryLine, UIDropDownMenu, UITextBox, UIImage
from pygame_gui.core import UIElement

from game.core.registry import RegistryManager
from game.ai.controller import STRATEGY_MANAGER

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

class BuilderRightPanel:
    def __init__(self, builder, manager, rect, event_bus=None, viewmodel=None):
        self.builder = builder
        self.viewmodel = viewmodel or builder.viewmodel
        self.manager = manager
        self.rect = rect
        self.event_bus = event_bus
        
        if event_bus:
            event_bus.subscribe("SHIP_UPDATED", self.on_ship_updated)
            event_bus.subscribe("REGISTRY_RELOADED", self.on_registry_reloaded)
        
        self.panel = UIPanel(
            relative_rect=rect,
            manager=manager,
            object_id='#right_panel'
        )
        
        self.setup_controls()
        self.setup_stats()
        
    def on_registry_reloaded(self, data):
        """Handle registry reload event - refresh all controls with new data."""
        self.refresh_controls()

    def on_ship_updated(self, ship):
        # Check if resource keys match our current rows
        # If mismatch, we must rebuild the layout to add/remove rows
        from ui.builder.stats_config import get_logistics_rows
        
        current_keys = set(self.rows_map.keys())
        
        # Calculate expected keys for dynamic section
        new_log_rows = get_logistics_rows(ship)
        new_log_keys = set(r.key for r in new_log_rows)
        
        # We need to know if the SET of keys in new_log_rows differs from what we HAVE for logistics.
        # But self.rows_map contains ALL rows (Main, Shield, etc).
        # We can check if all new_log_keys are present in current_keys.
        # AND if we have any "stale" keys that are arguably logistics keys?
        # Simpler: If any new key is missing -> REBUILD
        
        missing_keys = new_log_keys - current_keys
        if missing_keys:
             self.rebuild_stats()
             # Fall through to update

        # Also check if any EXISTING key that looks like a resource key is NO LONGER valid?
        # E.g. removed 'Biomass'.
        # This is harder without knowing which keys are logistics.
        # But generally, adding components is the main builder action. Removing implies set subtraction.
        # Using self.logistics_keys stored in setup_stats would be better.
        
        elif hasattr(self, 'current_logistics_keys'):
            if new_log_keys != self.current_logistics_keys:
                 self.rebuild_stats()
                 # Fall through to update

        self.update_stats_display(ship)

    def setup_controls(self):
        y = 10
        width = self.rect.width
        col_w = width - 20
        
        # Name
        UILabel(pygame.Rect(10, y, 60, 25), "Name:", manager=self.manager, container=self.panel)
        self.name_entry = UITextEntryLine(pygame.Rect(70, y, 195, 30), manager=self.manager, container=self.panel)
        self.name_entry.set_text(self.viewmodel.ship.name)
        y += 40
        
        # Theme
        UILabel(pygame.Rect(10, y, 60, 25), "Theme:", manager=self.manager, container=self.panel)
        theme_options = self.builder.theme_manager.get_available_themes()
        curr_theme = getattr(self.viewmodel.ship, 'theme_id', 'Federation')
        if theme_options and curr_theme not in theme_options: curr_theme = theme_options[0]
        
        self.theme_dropdown = UIDropDownMenu(theme_options, curr_theme, pygame.Rect(70, y, 195, 30), manager=self.manager, container=self.panel)
        y += 40
        
        # Vehicle Type
        UILabel(pygame.Rect(10, y, 60, 25), "Type:", manager=self.manager, container=self.panel)
        # Get unique types
        types = sorted(list(set(c.get('type', 'Ship') for c in RegistryManager.instance().vehicle_classes.values())))
        if not types: types = ["Ship"]
        
        curr_type = getattr(self.viewmodel.ship, 'vehicle_type', "Ship")
        if curr_type not in types: curr_type = types[0]
        
        self.vehicle_type_dropdown = UIDropDownMenu(types, curr_type, pygame.Rect(70, y, 195, 30), manager=self.manager, container=self.panel)
        y += 40

        # Class
        UILabel(pygame.Rect(10, y, 60, 25), "Class:", manager=self.manager, container=self.panel)
        # Filter classes by current type and sort by max_mass (smallest to largest)
        class_options = [(name, cls.get('max_mass', 0)) for name, cls in RegistryManager.instance().vehicle_classes.items() if cls.get('type', 'Ship') == curr_type]
        class_options.sort(key=lambda x: x[1])  # Sort by max_mass
        class_options = [name for name, _ in class_options]  # Extract just names
        if not class_options: class_options = ["Escort"]

        curr_class = self.viewmodel.ship.ship_class
        if curr_class not in class_options: curr_class = class_options[0]
        
        self.class_dropdown = UIDropDownMenu(class_options, curr_class, pygame.Rect(70, y, 195, 30), manager=self.manager, container=self.panel)
        y += 40
        
        # AI
        UILabel(pygame.Rect(10, y, 60, 25), "AI:", manager=self.manager, container=self.panel)
        
        strategies = STRATEGY_MANAGER.strategies if STRATEGY_MANAGER else {}
        ai_options = [strat.get('name', sid.replace('_', ' ').title()) for sid, strat in strategies.items()]
        
        # Ensure we have at least one option
        if not ai_options:
            ai_options = ['Standard Ranged']
        
        # Find display name for ship's current strategy
        ai_display = None
        for sid, strat in strategies.items():
            if sid == self.viewmodel.ship.ai_strategy:
                ai_display = strat.get('name', sid.replace('_', ' ').title())
                break
        
        # Fallback to first option if ship's strategy is not in new data-driven system
        if ai_display is None or ai_display not in ai_options:
            ai_display = ai_options[0]
                
        self.ai_dropdown = UIDropDownMenu(ai_options, ai_display, pygame.Rect(70, y, 195, 30), manager=self.manager, container=self.panel)
        
        # Portrait Image (Side by Side)
        self.portrait_image = None
        img_x = 280
        img_size = 200 # Approx match height of 5 rows (200px)
        self.portrait_rect = pygame.Rect(img_x, 10, img_size, img_size) # Fixed slot
        
        self.update_portrait_image()
        
        y += 40 # Ends at 210
        self.last_y = max(y, 10 + img_size) + 10

    def refresh_controls(self):
        """Update all UI controls to match the current ship state."""
        import pygame
        from pygame_gui.elements import UIDropDownMenu
        
        s = self.viewmodel.ship
        
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
        types = sorted(list(set(c.get('type', 'Ship') for c in RegistryManager.instance().vehicle_classes.values())))
        if not types: types = ["Ship"]
        
        curr_type = getattr(s, 'vehicle_type', "Ship")
        # Ensure consistency from class if vehicle_type not set or mismatched
        class_def = RegistryManager.instance().vehicle_classes.get(s.ship_class, {})
        if class_def:
             curr_type = class_def.get('type', curr_type)
        
        if curr_type not in types: curr_type = types[0]
        
        self.vehicle_type_dropdown = UIDropDownMenu(types, curr_type, type_rect, manager=self.manager, container=self.panel)
        
        # 4. Recreate Class
        class_options = [(name, cls.get('max_mass', 0)) for name, cls in RegistryManager.instance().vehicle_classes.items() if cls.get('type', 'Ship') == curr_type]
        class_options.sort(key=lambda x: x[1])  # Sort by max_mass
        class_options = [name for name, _ in class_options]  # Extract just names
        if not class_options: class_options = ["Escort"]

        curr_class = s.ship_class
        if curr_class not in class_options: 
            if curr_class in RegistryManager.instance().vehicle_classes: 
                 curr_class = class_options[0]
        
        self.class_dropdown = UIDropDownMenu(class_options, curr_class, class_rect, manager=self.manager, container=self.panel)
        
        # 5. Recreate AI
        strategies = STRATEGY_MANAGER.strategies if STRATEGY_MANAGER else {}
        ai_options = [strat.get('name', sid.replace('_', ' ').title()) for sid, strat in strategies.items()]
        
        # Ensure we have at least one option
        if not ai_options:
            ai_options = ['Standard Ranged']
        
        # Find display name for ship's current strategy
        ai_display = None
        for sid, strat in strategies.items():
            if sid == s.ai_strategy:
                ai_display = strat.get('name', sid.replace('_', ' ').title())
                break
        
        # Fallback to first option if ship's strategy is not in new data-driven system
        if ai_display is None or ai_display not in ai_options:
            ai_display = ai_options[0]
                
        self.ai_dropdown = UIDropDownMenu(ai_options, ai_display, ai_rect, manager=self.manager, container=self.panel)

        # 6. Update Portrait
        self.update_portrait_image()

        # 7. Rebuild Stats (Logic might satisfy dynamic resources)
        self.rebuild_stats()


    def update_portrait_image(self):
        """Update the ship portrait based on current theme and class."""
        import os
        import re
        
        # Determine paths
        theme = getattr(self.viewmodel.ship, 'theme_id', 'Federation')
        ship_class = self.viewmodel.ship.ship_class
        
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
        full_path = os.path.join(base_path, theme, filename)
        
        # Check for new location: assets/ShipThemes/{theme}/Portraits
        new_loc = os.path.join("assets", "ShipThemes", theme, "Portraits", filename)
        if os.path.exists(new_loc):
            full_path = new_loc
            
        if not os.path.exists(full_path):
            # Try with spaces?
            full_path_space = os.path.join(base_path, theme, f"{ship_class}_Portrait.jpg")
            if os.path.exists(full_path_space):
                full_path = full_path_space
            else:
                 # Fallback to Default Portrait
                 default_path = os.path.join("assets", "Images", "Default_Ship_Portrait.png")
                 if os.path.exists(default_path):
                     full_path = default_path
                 else:
                     if self.portrait_image:
                         self.portrait_image.kill()
                         self.portrait_image = None
                     return

        try:
            image_surf = pygame.image.load(full_path).convert_alpha()
            
            # Scale to fit width, maintaining aspect
            max_w = self.portrait_rect.width
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
        # Create Scroll Container for Stats
        # Starts after controls (last_y) and takes remaining height
        
        # Calculate available height
        y = self.last_y
        total_h = self.rect.height - y - 10
        if total_h < 100: total_h = 100
        
        self.stats_scroll = pygame_gui.elements.UIScrollingContainer(
            relative_rect=pygame.Rect(0, y, self.rect.width, total_h),
            manager=self.manager,
            container=self.panel,
            anchors={'left': 'left', 'right': 'right', 'top': 'top', 'bottom': 'bottom'}
        )
        
        # We need a container for the scrolling content (inner)
        # However, UIScrollingContainer acts as the container source. 
        # Elements should be parented to self.stats_scroll
        
        # Columns
        # Width available inside scrollbar (assume 20px scrollbar)
        list_w = self.stats_scroll.get_container().get_rect().width
        full_w = list_w
        
        col_gap = 10
        margin = 10
        avail_w = full_w - (2 * margin) - col_gap
        col_w = avail_w // 2
        
        col1_x = margin
        col2_x = margin + col_w + col_gap
        
        # Start Y inside container (0-indexed)
        y = 10 
        start_y = y
        
        self.rows_map = {} # Store StatRow instances by key
        
        # === Generic Helper to Build Section ===
        def build_section(title, stats_list, x, start_y):
            curr_y = start_y
            UILabel(pygame.Rect(x, curr_y, col_w, 25), f"── {title} ──", manager=self.manager, container=self.stats_scroll)
            curr_y += 30
            
            for stat_def in stats_list:
                row = StatRow(stat_def.key, stat_def.label, self.manager, self.stats_scroll, x, curr_y, col_w)
                row.definition = stat_def # Attach definition to row for update loop
                self.rows_map[stat_def.key] = row
                curr_y += 20
            
            return curr_y + 10

        from ui.builder.stats_config import STATS_CONFIG, get_logistics_rows

        # FREEZING CONFIG
        self.stats_config = STATS_CONFIG
        
        # === Column 1: Main, Maneuvering, Shields, Armor, Targeting ===
        y = start_y
        
        y = build_section("Main Systems", self.stats_config.get('main', []), col1_x, y)
        y = build_section("Maneuvering", self.stats_config.get('maneuvering', []), col1_x, y)
        y = build_section("Shields", self.stats_config.get('shields', []), col1_x, y)
        
        # Armor
        y = build_section("Armor", self.stats_config.get('armor', []), col1_x, y)
        
        # Layers (Special Case: Dynamic) - Inserted under Armor
        
        # -- Added Header "Layers" --
        UILabel(pygame.Rect(col1_x, y, col_w, 20), "Layers", manager=self.manager, container=self.stats_scroll)
        y += 20
        # ---------------------------
        
        self.layer_rows = []
        for i in range(4):
            sr = StatRow(f"layer_{i}", f"Slot {i}", self.manager, self.stats_scroll, col1_x, y, col_w)
            sr.set_visible(False)
            self.layer_rows.append(sr)
            y += 22
        y += 10
        
        y = build_section("Targeting", self.stats_config.get('targeting', []), col1_x, y)
        col1_max_y = y
        
        # === Column 2: Logistics, Crew, Fighter ===
        y = start_y
        
        # Helper for Dynamic Logistics
        log_rows = get_logistics_rows(self.viewmodel.ship)
        
        # Store keys for dirty checking later
        self.current_logistics_keys = set(r.key for r in log_rows)
        
        y = build_section("Logistics", log_rows, col2_x, y)

        y = build_section("Crew Logistics", self.stats_config.get('crewlogistics', []), col2_x, y)
        y = build_section("Fighter Support", self.stats_config.get('fightersupport', []), col2_x, y)
        
        col2_max_y = y
        
        # === Requirements (Bottom, Split) ===
        y = max(col1_max_y, col2_max_y) + 10
        
        # Split Headers
        UILabel(pygame.Rect(col1_x, y, col_w, 20), "── Requirements ──", manager=self.manager, container=self.stats_scroll)
        UILabel(pygame.Rect(col2_x, y, col_w, 20), "── Recommendations ──", manager=self.manager, container=self.stats_scroll)
        y += 25
        
        # Box heights (enough for content, not fixed to panel bottom anymore)
        rem_h = 200 # Fixed reasonable height inside scroll
        
        self.req_box_left = UITextBox("✓ All requirements met", pygame.Rect(col1_x, y, col_w, rem_h), manager=self.manager, container=self.stats_scroll)
        self.req_box_right = UITextBox("", pygame.Rect(col2_x, y, col_w, rem_h), manager=self.manager, container=self.stats_scroll)

        y += rem_h + 10
        
        # Update Scroll Area
        self.stats_scroll.set_scrollable_area_dimensions((full_w, y))

    def rebuild_stats(self):
        """Completely rebuild the stats scroll container (e.g. after ship load)."""
        if hasattr(self, 'stats_scroll'):
            self.stats_scroll.kill()
        self.setup_stats()

    def update_stats_display(self, s):
        """Update ship stats labels using Data-Driven Config."""
        
        # Iterate over instantiated rows directly
        # This allows us to handle dynamic rows that aren't in the static config
        for key, row in self.rows_map.items():
            if hasattr(row, 'definition'):
                stat_def = row.definition
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
        from game.simulation.entities.ship import LayerType
        
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
