import pygame
import pygame_gui
import os
from pygame_gui.elements import UIPanel, UILabel, UIImage, UIButton, UIWindow, UITextBox
from components import (
    Weapon, BeamWeapon, ProjectileWeapon, SeekerWeapon, 
    Engine, Thruster, Armor, Tank, Generator, CrewQuarters, LifeSupport
)
import json
from ui.builder.modifier_logic import ModifierLogic

class ComponentDetailPanel:
    def __init__(self, manager, rect, image_base_path, event_bus=None):
        self.manager = manager
        self.rect = rect
        self.image_base_path = image_base_path
        
        self.panel = UIPanel(
            relative_rect=rect,
            manager=manager,
            object_id='#detail_panel'
        )
        
        if event_bus:
            event_bus.subscribe("SELECTION_CHANGED", self.on_selection_changed)
        
        self.current_component = None
        self.last_html = ""
        self.last_img_comp = None
        self.portrait_cache = {}
        
        # Image Element
        # Width is rect.width - 20 padding
        # Aspect ratio 1:1 for portrait
        img_size = rect.width - 20
        self.image_rect = pygame.Rect(10, 10, img_size, img_size)
        self.image_element = None
        
        # Button Area
        button_height = 40
        button_y = rect.height - button_height - 10
        self.details_btn = UIButton(
            relative_rect=pygame.Rect(10, button_y, rect.width - 20, button_height),
            text='Component Details',
            manager=manager,
            container=self.panel
        )
        self.details_btn.hide()

        # Stats Text Box
        self.start_y = self.image_rect.bottom + 10
        stats_height = button_y - self.start_y - 10
        
        from pygame_gui.elements import UITextBox
        self.stats_text_box = UITextBox(
            html_text="",
            relative_rect=pygame.Rect(10, self.start_y, rect.width - 20, stats_height),
            manager=manager,
            container=self.panel
        )
        
        # Placeholder text when nothing is selected
        self.placeholder_label = UILabel(
            pygame.Rect(10, rect.height // 2 - 10, rect.width - 20, 20),
            "Hover or Select Component",
            manager=manager,
            container=self.panel
        )

    def on_selection_changed(self, selection_data):
         # selection_data matches what BuilderSceneGUI emits: self.selected_component
         # which is a tuple (layer, idx, comp) or None using the new system
         
         if selection_data and isinstance(selection_data, tuple):
             self.show_component(selection_data[2])
         elif hasattr(selection_data, 'id'): # Direct component
             self.show_component(selection_data)
         else:
             self.show_component(None)
        
        
    def show_component(self, comp):
        if not comp:
            self.current_component = None
            self.last_img_comp = None
            self.last_html = ""
            self._clear_display()
            self.placeholder_label.show()
            self.stats_text_box.hide()
            self.details_btn.hide()
            return
            
        self.placeholder_label.hide()
        self.stats_text_box.show()
        self.details_btn.show()
        
        # 1. Update Image (only if changed)
        if comp != self.last_img_comp:
            self._update_image(comp)
            self.last_img_comp = comp
            
        self.current_component = comp
        
        # 2. Update Stats
        lines = []
        
        def add_line(text, color='#FFFFFF'):
            # Proper HTML formatting
            if color != '#FFFFFF':
                lines.append(f"<font color='{color}'>{text}</font>")
            else:
                lines.append(text)
            
        # Header
        add_line(f"<b>{comp.name}</b>", '#FFFF64')
        add_line(f"{comp.type_str}", '#C8C8C8')
        add_line(f"Mass: {comp.mass:.1f}t", '#C8C8C8')
        add_line(f"HP: {comp.max_hp:.0f}", '#C8C8C8')
        lines.append("<br>") # Spacer
        
        # Weapon Stats
        if hasattr(comp, 'damage') and comp.damage > 0:
            add_line(f"Damage: {comp.damage}", '#FF6464')
        if hasattr(comp, 'range') and comp.range > 0:
            add_line(f"Range: {comp.range}", '#FFA500')
        if hasattr(comp, 'reload_time'):
            add_line(f"Reload: {comp.reload_time}s", '#FFC864')
        # Ability-based Resource Checks
        # Note: We check `ability_instances` if available (post-init) or raw data
        # For builder, we often have the raw component.
        
        # Helper to find ability cost/storage
        def get_ability_val(comp, ability_name, resource_name=None, field='amount'):
            if hasattr(comp, 'ability_instances'):
                for ab in comp.ability_instances:
                    if ab.__class__.__name__ == ability_name:
                         if resource_name:
                             if getattr(ab, 'resource_name', '') == resource_name:
                                 return getattr(ab, field, 0)
                         else:
                             return getattr(ab, field, 0)
            # Fallback to raw data (common in builder before simulation)
            raw_abs = getattr(comp, 'abilities', {})
            if ability_name in raw_abs:
                data = raw_abs[ability_name]
                # data is list of dicts
                if isinstance(data, list):
                    for item in data:
                        if resource_name and item.get('resource') == resource_name:
                            return item.get(field, 0)
                        elif not resource_name:
                             return item.get(field, 0)
            return 0

        # Ammo Cost (Activation)
        ammo_cost = get_ability_val(comp, 'ResourceConsumption', 'ammo', 'amount')
        if ammo_cost > 0:
            add_line(f"Ammo Cost: {ammo_cost}", '#C8C832')
            
        # Energy Cost (Activation)
        energy_cost = get_ability_val(comp, 'ResourceConsumption', 'energy', 'amount')
        if energy_cost > 0:
             add_line(f"Energy Cost: {energy_cost}", '#64C8FF')
        if hasattr(comp, 'firing_arc'):
            add_line(f"Arc: {comp.firing_arc}°", '#FF64FF')
        if hasattr(comp, 'base_accuracy'):
             add_line(f"Accuracy Score: +{comp.base_accuracy:.1f}", '#FFFF64')
            
        # Missile Stats
        if hasattr(comp, 'endurance'):
             add_line(f"Endurance: {comp.endurance}s", '#64C8FF')
        if hasattr(comp, 'hp') and isinstance(comp, SeekerWeapon):
             add_line(f"Missile HP: {comp.hp}", '#FF6464')
             # Show To-Hit Defense if present
             if hasattr(comp, 'to_hit_defense'):
                 def_val = comp.to_hit_defense
                 if def_val > 0:
                     add_line(f"Defense Score: +{def_val:.1f}", '#800080') # Purple for stealth

        if hasattr(comp, 'turn_rate') and hasattr(comp, 'endurance'):
             add_line(f"Turn Rate: {comp.turn_rate}°/s", '#64FF64')
             if hasattr(comp, 'projectile_speed'):
                 add_line(f"Speed: {comp.projectile_speed}", '#C8C832')

        # Engine Stats
        if hasattr(comp, 'thrust_force') and comp.thrust_force > 0:
            add_line(f"Thrust: {comp.thrust_force}", '#64FF64')
        if hasattr(comp, 'turn_speed') and comp.turn_speed > 0:
            add_line(f"Turn Speed: {comp.turn_speed}°/s", '#64FF96')
        # Fuel Cost (Constant)
        fuel_cost = get_ability_val(comp, 'ResourceConsumption', 'fuel', 'amount')
        if fuel_cost > 0:
            add_line(f"Fuel: {fuel_cost}/s", '#FFA500')
            
        # Resource Stats
        # Resource Storage (Capacity)
        # We need to iterate all storage abilities
        raw_abs = getattr(comp, 'abilities', {})
        if 'ResourceStorage' in raw_abs:
            storages = raw_abs['ResourceStorage']
            for s in storages:
                r_type = s.get('resource', '').title()
                amt = s.get('amount', 0)
                if amt > 0:
                    add_line(f"{r_type} Cap: {amt}", '#64FFFF')
        
        # Energy Generation
        e_gen = get_ability_val(comp, 'ResourceGeneration', 'energy', 'amount') # check 'amount' or 'rate'? 
        # definition uses 'amount', logic uses 'rate', let's check basic data structure
        # In data: { "resource": "energy", "amount": 5.0 }
        if e_gen > 0:
            add_line(f"Energy Gen: {e_gen}/s", '#FFFF00')
            
        # Shield Stats
        if hasattr(comp, 'shield_capacity') and comp.shield_capacity > 0:
             add_line(f"Shield Max: {comp.shield_capacity}", '#00FFFF')
        if hasattr(comp, 'regen_rate') and comp.regen_rate > 0:
             add_line(f"Regen: {comp.regen_rate}/s", '#00C8FF')
             
        # Abilities
        if comp.abilities:
            lines.append("<br>Abilities:")
            for k, v in comp.abilities.items():
                if k == "CommandAndControl":
                    add_line("• Command & Control", '#96FF96')
                elif k == "CrewCapacity":
                    if v > 0: add_line(f"• Crew Cap: {v}", '#96FF96')
                    else: add_line(f"• Crew Req: {-v}", '#FF9696')
                elif k == "LifeSupportCapacity":
                    add_line(f"• Life Support: {v}", '#96FFFF')
                elif k == "ToHitAttackModifier":
                    val = v.get('value', 0) if isinstance(v, dict) else v
                    sign = "+" if val >= 0 else ""
                    add_line(f"• Targeting Score: {sign}{val:.1f}", '#FF6464')
                elif k == "ToHitDefenseModifier":
                    val = v.get('value', 0) if isinstance(v, dict) else v
                    sign = "+" if val >= 0 else ""
                    add_line(f"• Evasion Score: {sign}{val:.1f}", '#64FFFF')
                elif k == "EmissiveArmor":
                    add_line(f"• Damage Ignore: {v}", '#FFFF00')
                # Skip stats already shown above
                elif k not in ["ShieldProjection", "ShieldRegeneration", "EnergyConsumption", "EnergyGeneration", 
                               "FuelStorage", "AmmoStorage", "EnergyStorage", "CombatPropulsion", "ManeuveringThruster",
                               "ProjectileWeapon", "BeamWeapon", "Armor"]:
                    add_line(f"• {k}: {v}", '#C8C8C8')
                    
        # Modifiers
        if comp.modifiers:
            lines.append("<br>Modifiers:")
            for m in comp.modifiers:
                is_mandatory = ModifierLogic.is_modifier_mandatory(m.definition.id, comp)
                
                name_str = m.definition.name
                color = '#96FF96' # Green for optional
                
                if is_mandatory:
                    name_str = f"{name_str} [A]" # Auto
                    color = '#FFD700' # Gold/Gold for mandatory
                    
                add_line(f"• {name_str}: {m.value:.2f}", color)
        
        full_html = "<br>".join(lines)
        if full_html != self.last_html:
            self.stats_text_box.html_text = full_html
            self.stats_text_box.rebuild()
            self.last_html = full_html

    def show_details_popup(self):
        if not self.current_component:
            return

        json_str = json.dumps(self.current_component.data, indent=4)
        # Simple HTML formatting for text box
        html_str = json_str.replace("\n", "<br>").replace("    ", "&nbsp;&nbsp;&nbsp;&nbsp;")
        
        win_size = (500, 600)
        start_pos = (
            (self.rect.width - win_size[0]) // 2 + self.rect.x,
            (self.rect.height - win_size[1]) // 2 + self.rect.y
        )
        # Center on screen or panel? Let's center on screen if possible, but we only have Manager.
        # Use simple centering logic or fixed pos.
        
        window = UIWindow(
            rect=pygame.Rect((100, 100), win_size),
            manager=self.manager,
            window_display_title=f"Details: {self.current_component.name}",
            resizable=True
        )
        
        text_box = UITextBox(
            html_text=f"<font face='consolas, monospace' size=4 color='#E0E0E0'>{html_str}</font>",
            relative_rect=pygame.Rect(10, 10, win_size[0]-20, win_size[1]-50),
            manager=self.manager,
            container=window,
            anchors={'left': 'left', 'right': 'right', 'top': 'top', 'bottom': 'bottom'}
        )

    def _clear_display(self):
        self.stats_text_box.html_text = ""
        self.stats_text_box.rebuild()
        if self.image_element:
            self.image_element.kill()
            self.image_element = None
            
    def _update_image(self, comp):
        # Only reload if changed
        if self.image_element:
            self.image_element.kill()
            self.image_element = None
            
        index = comp.sprite_index
        file_index = index + 1
        filename = f"2048Portrait_Comp_{file_index:03d}.jpg"
        
        full_path = os.path.join(self.image_base_path, "Components 2048", filename)
        
        surf = None
        if os.path.exists(full_path):
             if full_path in self.portrait_cache:
                 surf = self.portrait_cache[full_path]
             else:
                 try:
                    loaded = pygame.image.load(full_path).convert()
                    surf = pygame.transform.scale(loaded, (self.image_rect.width, self.image_rect.height))
                    self.portrait_cache[full_path] = surf
                 except Exception as e:
                     print(f"Failed to load portrait {full_path}: {e}")
        
        if surf:
            self.image_element = UIImage(
                relative_rect=self.image_rect,
                image_surface=surf,
                manager=self.manager,
                container=self.panel
            )
        else:
            # Placeholder
            empty = pygame.Surface((self.image_rect.width, self.image_rect.height))
            empty.fill((50, 50, 60))
            font = pygame.font.SysFont("Arial", 14)
            text = font.render(f"No Image\n{filename}", True, (200, 200, 200))
            empty.blit(text, (10, 10))
            
            self.image_element = UIImage(
                relative_rect=self.image_rect,
                image_surface=empty,
                manager=self.manager,
                container=self.panel
            )

    def set_position(self, pos):
        self.panel.set_position(pos)
        self.rect.topleft = pos

