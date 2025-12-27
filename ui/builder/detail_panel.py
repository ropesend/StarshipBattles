import pygame
import pygame_gui
import os
from pygame_gui.elements import UIPanel, UILabel, UIImage
from components import (
    Weapon, BeamWeapon, ProjectileWeapon, SeekerWeapon, 
    Engine, Thruster, Armor, Tank, Generator, CrewQuarters, LifeSupport
)

class ComponentDetailPanel:
    def __init__(self, manager, rect, image_base_path):
        self.manager = manager
        self.rect = rect
        self.image_base_path = image_base_path
        
        self.panel = UIPanel(
            relative_rect=rect,
            manager=manager,
            object_id='#detail_panel'
        )
        
        self.current_component_name = None
        self.portrait_cache = {}
        
        # Image Element
        # Width is rect.width - 20 padding
        # Aspect ratio 1:1 for portrait
        img_size = rect.width - 20
        self.image_rect = pygame.Rect(10, 10, img_size, img_size)
        self.image_element = None
        
        # Stats Text Box
        self.start_y = self.image_rect.bottom + 10
        stats_height = rect.height - self.start_y - 10
        
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
        
    def show_component(self, comp):
        if not comp:
            self._clear_display()
            self.placeholder_label.show()
            self.stats_text_box.hide()
            return
            
        self.placeholder_label.hide()
        self.stats_text_box.show()
        
        # 1. Update Image
        self._update_image(comp)
        
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
        if hasattr(comp, 'ammo_cost') and comp.ammo_cost > 0:
            add_line(f"Ammo Cost: {comp.ammo_cost}", '#C8C832')
        if hasattr(comp, 'energy_cost') and comp.energy_cost > 0:
            add_line(f"Energy Cost: {comp.energy_cost}", '#64C8FF')
        if hasattr(comp, 'firing_arc'):
            add_line(f"Arc: {comp.firing_arc}°", '#FF64FF')
            
        # Missile Stats
        if hasattr(comp, 'endurance'):
             add_line(f"Endurance: {comp.endurance}s", '#64C8FF')
        if hasattr(comp, 'turn_rate') and hasattr(comp, 'endurance'):
             add_line(f"Turn Rate: {comp.turn_rate}°/s", '#64FF64')
             if hasattr(comp, 'projectile_speed'):
                 add_line(f"Speed: {comp.projectile_speed}", '#C8C832')

        # Engine Stats
        if hasattr(comp, 'thrust_force') and comp.thrust_force > 0:
            add_line(f"Thrust: {comp.thrust_force}", '#64FF64')
        if hasattr(comp, 'turn_speed') and comp.turn_speed > 0:
            add_line(f"Turn Speed: {comp.turn_speed}°/s", '#64FF96')
        if hasattr(comp, 'fuel_cost_per_sec') and comp.fuel_cost_per_sec > 0:
            add_line(f"Fuel: {comp.fuel_cost_per_sec}/s", '#FFA500')
            
        # Resource Stats
        if hasattr(comp, 'capacity') and comp.capacity > 0:
            rtype = getattr(comp, 'resource_type', 'Resource').title()
            add_line(f"{rtype} Cap: {comp.capacity}", '#64FFFF')
        if hasattr(comp, 'energy_generation_rate') and comp.energy_generation_rate > 0:
            add_line(f"Energy Gen: {comp.energy_generation_rate}/s", '#FFFF00')
            
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
                    add_line(f"• Targeting: x{v}", '#FF6464')
                elif k == "ToHitDefenseModifier":
                    add_line(f"• ECM: x{v}", '#64FFFF')
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
                add_line(f"• {m.definition.name}: {m.value:.0f}", '#96FF96')
        
        full_html = "<br>".join(lines)
        self.stats_text_box.html_text = full_html
        self.stats_text_box.rebuild()

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

