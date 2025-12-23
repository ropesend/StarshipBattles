import pygame
import pygame_gui
from pygame_gui.elements import UIPanel, UILabel, UITextEntryLine, UIDropDownMenu, UITextBox

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
        
        self.last_y = y + 50

    def setup_stats(self):
        y = self.last_y
        
        # Stats Header
        UILabel(pygame.Rect(10, y, 150, 25), "── Ship Stats ──", manager=self.manager, container=self.panel)
        y += 30
        
        self.stat_labels = {}
        stat_names = ['mass', 'max_hp', 'max_shields', 'shield_regen', 'shield_cost', 'max_speed', 
                      'turn_rate', 'acceleration', 'thrust', 'energy_gen', 'max_fuel', 'max_ammo', 'max_energy', 'targeting',
                      'target_profile', 'scan_strength']

        
        for stat in stat_names:
            self.stat_labels[stat] = UILabel(pygame.Rect(10, y, 350, 20), f"{stat}: --", manager=self.manager, container=self.panel)
            y += 20
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
        # Mass with color indicator
        mass_status = "✓" if s.mass_limits_ok else "✗"
        self.stat_labels['mass'].set_text(f"Mass: {s.mass:.0f} / {s.max_mass_budget} {mass_status}")
        
        self.stat_labels['max_hp'].set_text(f"Max HP: {s.max_hp:.0f}")
        self.stat_labels['max_shields'].set_text(f"Shields: {s.max_shields:.0f}")
        self.stat_labels['shield_regen'].set_text(f"Shield Regen: {s.shield_regen_rate:.1f}/s")
        self.stat_labels['shield_cost'].set_text(f"Regen Cost: {s.shield_regen_cost:.1f} E/t")
        
        self.stat_labels['max_speed'].set_text(f"Max Speed: {s.max_speed:.0f}")
        self.stat_labels['turn_rate'].set_text(f"Turn Rate: {s.turn_speed:.0f} deg/s")
        self.stat_labels['acceleration'].set_text(f"Acceleration: {s.acceleration_rate:.2f}")
        self.stat_labels['thrust'].set_text(f"Total Thrust: {s.total_thrust:.0f}")
        self.stat_labels['energy_gen'].set_text(f"Energy Gen: {s.energy_gen_rate:.1f}/s")
        self.stat_labels['max_fuel'].set_text(f"Max Fuel: {s.max_fuel:.0f}")
        self.stat_labels['max_ammo'].set_text(f"Max Ammo: {s.max_ammo:.0f}")
        self.stat_labels['max_energy'].set_text(f"Max Energy: {s.max_energy:.0f}")
        
        # Targeting
        t_count = getattr(s, 'max_targets', 1)
        t_text = "Single" if t_count == 1 else f"Multi ({t_count})"
        self.stat_labels['targeting'].set_text(f"Targeting: {t_text}")
        
        # To-Hit Stats
        self.stat_labels['target_profile'].set_text(f"Defensive Odds to Hit: {s.to_hit_profile:.4f}x")
        self.stat_labels['scan_strength'].set_text(f"Offensive odds to hit: {s.baseline_to_hit_offense:.1f}x")
        
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
        
        if not missing_reqs:
            html = "<font color='#88ff88'>✓ All requirements met</font>"
        else:
            html = "<br>".join([f"<font color='#ffaa55'>{req}</font>" for req in missing_reqs])
        
        self.requirements_text_box.html_text = html
        self.requirements_text_box.rebuild()
