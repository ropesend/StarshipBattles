import pygame
import pygame_gui
from pygame_gui.elements import UIPanel, UILabel, UITextEntryLine, UIDropDownMenu, UITextBox, UIImage

from ship import VEHICLE_CLASSES
from ai import COMBAT_STRATEGIES

class BuilderRightPanel:
    def __init__(self, builder, manager, rect):
        self.builder = builder
        self.manager = manager
        self.rect = rect
        
        self.panel = UIPanel(
            relative_rect=rect,
            manager=manager,
            object_id='#right_panel'
        )
        
        self.setup_controls()
        self.setup_stats()
        
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

    def update_portrait_image(self):
        """Update the ship portrait based on current theme and class."""
        import os
        
        # Determine paths
        theme = getattr(self.builder.ship, 'theme_id', 'Federation')
        ship_class = self.builder.ship.ship_class
        
        # Map theme ID to folder name if necessary (simple map for now, or trust ID)
        # Theme IDs are usually "Federation", "Klingons", etc.
        # But let's check if we need mapping. The script used:
        # fed -> Federation, etc. But the game uses full names likely.
        # Let's assume theme_id matches directory name for now as per `ShipThemeManager`.
        
        # Filename: {Class}_Portrait.jpg
        # Remove spaces from class name if any? generated files have e.g. BattleCruiser_Portrait.jpg
        # But class name in game might be "Battle Cruiser"
        
        class_clean = ship_class.replace(" ", "")
        filename = f"{class_clean}_Portrait.jpg"
        
        base_path = "resources/Portraits"
        # We need absolute path or relative to CWD
        # Assuming CWD is project root
        full_path = os.path.join(base_path, theme, filename)
        
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

    def _add_stat_row(self, key, label_text, y):
        """Helper to create a left-aligned label and right-aligned value row."""
        # Left Label
        l = UILabel(pygame.Rect(10, y, 170, 20), f"{label_text}:", manager=self.manager, container=self.panel)
        # Right Value (aligned to right edge with some padding, or just a label that we align text via spaces? 
        # pygame_gui default alignment is center or left usually. 
        # Better: Create a label at x=180 width=160.
        v = UILabel(pygame.Rect(180, y, 160, 20), "--", manager=self.manager, container=self.panel)
        # We can try to set text alignment if the theme supports it, or just rely on the rect.
        
        self.stat_rows[key] = {'label': l, 'value': v}
        return y + 20

    def setup_stats(self):
        y = self.last_y
        
        # Stats Header
        UILabel(pygame.Rect(10, y, 150, 25), "── Ship Stats ──", manager=self.manager, container=self.panel)
        y += 30
        
        self.stat_rows = {}
        
        # General Stats
        general_stats = [
            ('mass', 'Mass'), ('max_hp', 'Max HP'), ('emissive_armor', 'Dmg Ignore'), 
            ('max_shields', 'Shields'), ('shield_regen', 'Shield Regen'), ('shield_cost', 'Regen Cost'),
            ('max_speed', 'Max Speed'), ('turn_rate', 'Turn Rate'), ('acceleration', 'Acceleration'),
            ('thrust', 'Total Thrust'), ('energy_gen', 'Energy Gen'), ('max_fuel', 'Max Fuel'),
            ('max_ammo', 'Max Ammo'), ('max_energy', 'Max Energy'),
            ('targeting', 'Targeting'), ('target_profile', 'Defensive Odds'), ('scan_strength', 'Offensive Odds')
        ]
        
        for key, text in general_stats:
            y = self._add_stat_row(key, text, y)
            
        y += 10
        
        # Fighter Ops Header
        UILabel(pygame.Rect(10, y, 150, 25), "── Fighter Ops ──", manager=self.manager, container=self.panel)
        y += 30
        
        fighter_stats = [
            ('fighter_capacity', 'Total Storage'),
            ('fighter_size_cap', 'Max Size Cap'),
            ('fighters_per_wave', 'Per Wave'),
            ('launch_cycle', 'Cycle Time')
        ]
        
        for key, text in fighter_stats:
            y = self._add_stat_row(key, text, y)
            
        y += 5
        
        # Layer Usage
        UILabel(pygame.Rect(10, y, 150, 20), "── Layer Usage ──", manager=self.manager, container=self.panel)
        y += 22
        self.layer_labels = {}
        # Create FIXED slots for layers to prevent overlap
        self.layer_label_slots = []
        for i in range(4): # Max 4 layers likely
            lbl = UILabel(pygame.Rect(10, y, 350, 22), f"Slot {i}: --%", manager=self.manager, container=self.panel)
            lbl.hide()
            self.layer_label_slots.append(lbl)
            y += 22 


        y += 10
        
         # Crew
        UILabel(pygame.Rect(10, y, 150, 20), "── Crew ──", manager=self.manager, container=self.panel)
        y += 22
        self.crew_labels = {}
        for c in ['crew_required', 'crew_housed', 'life_support']:
            self.crew_labels[c] = UILabel(pygame.Rect(10, y, 350, 22), f"{c}: --", manager=self.manager, container=self.panel)
            y += 22
        y += 10

        # Requirements
        UILabel(pygame.Rect(10, y, 150, 20), "── Requirements ──", manager=self.manager, container=self.panel)
        y += 22
        
        rem_h = self.rect.height - y - 10
        self.requirements_text_box = UITextBox("✓ All requirements met", pygame.Rect(10, y, self.rect.width - 25, rem_h), manager=self.manager, container=self.panel)

    def update_stats_display(self, s):
        """Update ship stats labels."""
        # Helper to set text
        def set_val(k, txt):
            if k in self.stat_rows:
                self.stat_rows[k]['value'].set_text(txt)

        # Mass with color indicator
        mass_status = "✓" if s.mass_limits_ok else "✗"
        set_val('mass', f"{s.mass:.0f} / {s.max_mass_budget} {mass_status}")
        
        set_val('max_hp', f"{s.max_hp:.0f}")
        set_val('emissive_armor', f"{getattr(s, 'emissive_armor', 0):.0f}")
        set_val('max_shields', f"{s.max_shields:.0f}")
        set_val('shield_regen', f"{s.shield_regen_rate:.1f}/s")
        set_val('shield_cost', f"{s.shield_regen_cost:.1f} E/t")
        
        set_val('max_speed', f"{s.max_speed:.0f}")
        set_val('turn_rate', f"{s.turn_speed:.0f} deg/s")
        set_val('acceleration', f"{s.acceleration_rate:.2f}")
        set_val('thrust', f"{s.total_thrust:.0f}")
        set_val('energy_gen', f"{s.energy_gen_rate:.1f}/s")
        set_val('max_fuel', f"{s.max_fuel:.0f}")
        set_val('max_ammo', f"{s.max_ammo:.0f}")
        set_val('max_energy', f"{s.max_energy:.0f}")
        
        # Targeting
        t_count = getattr(s, 'max_targets', 1)
        t_text = "Single" if t_count == 1 else f"Multi ({t_count})"
        set_val('targeting', t_text)
        
        # To-Hit Stats
        set_val('target_profile', f"{s.to_hit_profile:.4f}x")
        set_val('scan_strength', f"{s.baseline_to_hit_offense:.1f}x")

        # Fighter Stats
        f_cap = getattr(s, 'fighter_capacity', 0)
        set_val('fighter_capacity', f"{f_cap:.0f}t")
        
        f_size = getattr(s, 'fighter_size_cap', 0)
        set_val('fighter_size_cap', f"{f_size:.0f}t")
        
        f_wave = getattr(s, 'fighters_per_wave', 0)
        set_val('fighters_per_wave', f"{f_wave}")
        
        l_cycle = getattr(s, 'launch_cycle', 0)
        set_val('launch_cycle', f"{l_cycle:.1f}s")
        
        # Update layer stats
        from ship import LayerType
        layer_name_map = {
            LayerType.CORE: 'CORE',
            LayerType.INNER: 'INNER', 
            LayerType.OUTER: 'OUTER',
            LayerType.ARMOR: 'ARMOR'
        }
        
        
        # Hide all first
        # Hide all slots first
        for slot in self.layer_label_slots:
            slot.hide()
            
        # Show and update present layers
        # sort by order if possible? default dict order should be fine or LayerType value
        # Sort by radius_pct descending (Outer first) or ascending (Core first)? 
        # Usually Core first is better list? 
        # Actually logic uses radius_pct. Let's stick to consistent sorting: Core -> Inner -> Outer -> Armor or similar.
        # LayerType enum values usually are 0,1,2,3 etc.
        sorted_layers = sorted(s.layers.items(), key=lambda x: x[0].value) 
        
        slot_idx = 0
        for layer_type, layer_data in sorted_layers:
            if slot_idx < len(self.layer_label_slots):
                status = s.layer_status.get(layer_type, {})
                ratio = status.get('ratio', 0) * 100
                limit = status.get('limit', 1.0) * 100
                is_ok = status.get('ok', True)
                mass = status.get('mass', 0)
                
                status_icon = "✓" if is_ok else "✗ OVER"
                
                lbl = self.layer_label_slots[slot_idx]
                lbl.set_text(f"{layer_type.name}: {ratio:.0f}% / {limit:.0f}% ({mass:.0f}t) {status_icon}")
                lbl.show()
                slot_idx += 1
        
        # Update crew stats
        crew_capacity = max(0, s.get_ability_total('CrewCapacity'))
        crew_required = s.get_ability_total('CrewRequired')
        
        # Legacy fallback
        legacy_req = abs(min(0, s.get_ability_total('CrewCapacity')))
        crew_required += legacy_req
        
        crew_housed = crew_capacity
        
        crew_ok = crew_capacity >= crew_required
        crew_status = "✓" if crew_ok else f"✗ Missing {crew_required - crew_capacity}"
        self.crew_labels['crew_required'].set_text(f"Crew Required: {crew_required}")
        self.crew_labels['crew_housed'].set_text(f"Crew On Board: {crew_housed} {crew_status}")
        
        life_support = s.get_ability_total('LifeSupportCapacity')
        ls_ok = life_support >= crew_required
        ls_status = "✓" if ls_ok else f"✗ -{crew_required - life_support}"
        self.crew_labels['life_support'].set_text(f"Life Support: {life_support} {ls_status}")
        
        # Update requirements
        missing_reqs = s.get_missing_requirements()
        if not s.mass_limits_ok:
            missing_reqs.append("⚠ Over mass limit")
            
        warnings = s.get_validation_warnings()
        
        full_list = []
        # Errors first
        for req in missing_reqs:
            full_list.append(f"<font color='#ffaa55'>{req}</font>")
            
        # Then warnings
        for warn in warnings:
            full_list.append(f"<font color='#ffff88'>⚠ {warn}</font>")
        
        if not full_list:
            html = "<font color='#88ff88'>✓ All requirements met</font>"
        else:
            html = "<br>".join(full_list)
        
        self.requirements_text_box.html_text = html
        self.requirements_text_box.rebuild()
