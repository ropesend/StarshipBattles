import json
import math
import tkinter
from tkinter import simpledialog
import os

import pygame
import pygame_gui
from pygame_gui.elements import (
    UIPanel, UILabel, UIButton, UIDropDownMenu, 
    UITextEntryLine, UISelectionList, UIWindow
)
from pygame_gui.windows import UIConfirmationDialog

from ship import Ship, LayerType, SHIP_CLASSES, VEHICLE_CLASSES
from components import (
    get_all_components, MODIFIER_REGISTRY, Bridge, Weapon, 
    BeamWeapon, ProjectileWeapon, SeekerWeapon, Engine, Thruster, Armor, Tank, Generator,
    CrewQuarters, LifeSupport
)
from sprites import SpriteManager
from preset_manager import PresetManager
from ship_io import ShipIO
from builder_components import ModifierEditorPanel
from ship_theme import ShipThemeManager
from ui.builder import BuilderLeftPanel, BuilderRightPanel, WeaponsReportPanel

# Initialize Tkinter root and hide it (for simpledialog)
try:
    tk_root = tkinter.Tk()
    tk_root.withdraw()
except:
    tk_root = None

# Colors
BG_COLOR = (20, 20, 30)
PANEL_BG = '#1e1e28'
SHIP_VIEW_BG = (10, 10, 20)

# Logging
import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class SchematicView:
    def __init__(self, rect, sprite_manager, theme_manager):
        self.rect = rect
        self.sprite_mgr = sprite_manager
        self.theme_manager = theme_manager
        self.max_r = 250
        self.cx = rect.centerx
        self.cy = rect.centery

    def update_rect(self, rect):
        self.rect = rect
        self.cx = rect.centerx
        self.cy = rect.centery

    def get_component_at(self, pos, ship):
        """Returns (layer_type, index, component) or None."""
        mx, my = pos
        cx, cy = self.cx, self.cy
        max_r = self.max_r
        hit_radius = 25
        
        for ltype, data in ship.layers.items():
            radius = max_r * data['radius_pct']
                
            comps = data['components']
            if not comps: continue
                
            angle_step = 360 / len(comps)
            current_angle = 0
            
            for i, comp in enumerate(comps):
                rad = math.radians(current_angle)
                px = cx + math.cos(rad) * radius
                py = cy + math.sin(rad) * radius
                
                d = math.hypot(mx - px, my - py)
                if d < hit_radius:
                    return (ltype, i, comp)
                current_angle += angle_step
        return None

    def draw(self, screen, ship, show_firing_arcs, selected_component, hovered_component):
        # Draw Background
        pygame.draw.rect(screen, SHIP_VIEW_BG, self.rect)
        
        cx, cy = self.cx, self.cy
        max_r = self.max_r
        
        # Draw Theme Image
        theme_id = getattr(ship, 'theme_id', 'Federation')
        ship_img = self.theme_manager.get_image(theme_id, ship.ship_class)
        
        if ship_img:
            img_w, img_h = ship_img.get_size()
            target_size = max_r * 2 * 2.5
            scale = target_size / max(img_w, img_h)
            new_w = int(img_w * scale)
            new_h = int(img_h * scale)
            scaled_img = pygame.transform.scale(ship_img, (new_w, new_h))
            rect = scaled_img.get_rect(center=(cx, cy))
            screen.blit(scaled_img, rect)
            
        # Draw structure rings
        font = pygame.font.SysFont("Arial", 10)
        sorted_layers = sorted(ship.layers.items(), key=lambda x: x[1]['radius_pct'], reverse=True)
        
        for ltype, data in sorted_layers:
            pct = data['radius_pct']
            r = int(max_r * pct)
            color = (100, 100, 100)
            if ltype.name == "ARMOR": color = (100, 100, 100)
            elif ltype.name == "OUTER": color = (200, 50, 50)
            elif ltype.name == "INNER": color = (50, 50, 200)
            elif ltype.name == "CORE": color = (200, 200, 200)
            
            pygame.draw.circle(screen, color, (cx, cy), r, 2)

            # Label
            surf = font.render(ltype.name, True, (80, 80, 80))
            screen.blit(surf, (cx - surf.get_width() // 2, cy - r - 12))

        # Draw Components
        for ltype, data in ship.layers.items():
            radius = max_r * data['radius_pct']
            
            comps = data['components']
            if not comps: continue
                
            angle_step = 360 / len(comps)
            current_angle = 0
            
            for comp in comps:
                rad = math.radians(current_angle)
                px = cx + math.cos(rad) * radius
                py = cy + math.sin(rad) * radius
                
                sprite = self.sprite_mgr.get_sprite(comp.sprite_index)
                if sprite:
                    has_facing = any(m.definition.id == 'facing' for m in comp.modifiers)
                    if has_facing and hasattr(comp, 'facing_angle'):
                        rotation_angle = -comp.facing_angle
                    else:
                        rotation_angle = -current_angle - 90
                        
                    rotated = pygame.transform.rotate(sprite, rotation_angle)
                    rect = rotated.get_rect(center=(int(px), int(py)))
                    screen.blit(rotated, rect)
                    
                    if selected_component and selected_component[2] == comp:
                        pygame.draw.circle(screen, (255, 255, 0), (int(px), int(py)), 20, 2)
                else:
                    pygame.draw.rect(screen, (0, 255, 0), (px - 10, py - 10, 20, 20))
                    
                current_angle += angle_step

        # Draw Arcs
        if show_firing_arcs:
            self.draw_all_firing_arcs(screen, ship)
        elif hovered_component and isinstance(hovered_component, Weapon):
            self.draw_component_firing_arc(screen, hovered_component)

    def draw_all_firing_arcs(self, screen, ship):
        for ltype, data in ship.layers.items():
            for comp in data['components']:
                if isinstance(comp, Weapon):
                    self.draw_weapon_arc(screen, comp)

    def draw_component_firing_arc(self, screen, comp):
        if isinstance(comp, Weapon):
            self.draw_weapon_arc(screen, comp)

    def draw_weapon_arc(self, screen, weapon):
        cx, cy = self.cx, self.cy
        arc_degrees = getattr(weapon, 'firing_arc', 20)
        weapon_range = getattr(weapon, 'range', 1000)
        facing = getattr(weapon, 'facing_angle', 0)
        
        display_range = min(weapon_range / 10, 300)
        
        start_angle = math.radians(90 - facing - arc_degrees)
        end_angle = math.radians(90 - facing + arc_degrees)
        
        if isinstance(weapon, BeamWeapon):
            color = (100, 255, 255, 100)
        else:
            color = (255, 200, 100, 100)
            
        points = [(cx, cy)]
        for angle in range(int(math.degrees(start_angle)), int(math.degrees(end_angle)) + 1, 2):
            rad = math.radians(angle)
            x = cx + math.cos(rad) * display_range
            y = cy - math.sin(rad) * display_range
            points.append((x, y))
        points.append((cx, cy))
        
        if len(points) > 2:
            arc_surface = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
            pygame.draw.polygon(arc_surface, (*color[:3], 50), points)
            pygame.draw.lines(arc_surface, color[:3], True, points, 2)
            screen.blit(arc_surface, (0, 0))
            
        font = pygame.font.SysFont("Arial", 10)
        mid_angle = (start_angle + end_angle) / 2
        label_x = cx + math.cos(mid_angle) * (display_range + 15)
        label_y = cy - math.sin(mid_angle) * (display_range + 15)
        label = font.render(f"{weapon_range}", True, color[:3])
        screen.blit(label, (label_x - label.get_width() // 2, label_y - label.get_height() // 2))


class InteractionController:
    def __init__(self, builder, view):
        self.builder = builder
        self.view = view
        self.dragged_item = None
        self.selected_component = None
        self.hovered_component = None

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                # Left Click
                if self.view.rect.collidepoint(event.pos) and not self.dragged_item:
                    found = self.view.get_component_at(event.pos, self.builder.ship)
                    if found:
                        keys = pygame.key.get_pressed()
                        if keys[pygame.K_LALT] or keys[pygame.K_RALT]:
                            # Clone
                            original = found[2]
                            self.dragged_item = original.clone()
                            for m in original.modifiers:
                                new_m = m.definition.create_modifier(m.value)
                                self.dragged_item.modifiers.append(new_m)
                            self.dragged_item.recalculate_stats()
                        elif self.selected_component == found:
                            # Pick up
                            layer, index, comp = found
                            self.builder.ship.remove_component(layer, index)
                            self.dragged_item = comp
                            self.selected_component = None
                            self.builder.on_selection_changed(None)
                            self.builder.update_stats()
                        else:
                            # Select
                            self.selected_component = found
                            self.builder.on_selection_changed(found)
                    else:
                        # Deselect
                        self.selected_component = None
                        self.builder.on_selection_changed(None)
                        
        elif event.type == pygame.MOUSEBUTTONUP:
             if event.button == 1 and self.dragged_item:
                 keys = pygame.key.get_pressed()
                 shift_held = keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]
                 
                 item_to_clone = self.dragged_item
                 self._handle_drop(event.pos)
                 
                 if shift_held:
                     self.dragged_item = item_to_clone.clone()
                     for m in item_to_clone.modifiers:
                        self.dragged_item.add_modifier(m.definition.id)
                        new_m = self.dragged_item.get_modifier(m.definition.id)
                        if new_m: new_m.value = m.value
                     self.dragged_item.recalculate_stats()
                 else:
                     self.dragged_item = None

    def update(self):
        mx, my = pygame.mouse.get_pos()
        self.hovered_component = None
        if self.view.rect.collidepoint(mx, my):
             found = self.view.get_component_at((mx, my), self.builder.ship)
             if found:
                 self.hovered_component = found[2]

    def _handle_drop(self, pos):
        cx, cy = self.view.cx, self.view.cy
        max_r = self.view.max_r
        
        dist = math.hypot(pos[0] - cx, pos[1] - cy)
        
        closest_layer = None
        min_diff = float('inf')
        
        for ltype, data in self.builder.ship.layers.items():
            r = max_r * data['radius_pct']
            diff = abs(dist - r)
            if diff < min_diff:
                min_diff = diff
                closest_layer = ltype
        
        if min_diff > 40:
             closest_layer = None
        
        if closest_layer:
            comp = self.dragged_item
            if closest_layer in comp.allowed_layers:
                 # Check specific restrictions
                 reason = self.builder.ship._check_restrictions(comp, self.builder.ship.layers[closest_layer]['restrictions'])
                 if reason:
                      self.builder.show_error(f"Cannot place: {reason}")
                      return

                 if self.builder.ship.current_mass + comp.mass <= self.builder.ship.max_mass_budget:
                    self.builder.ship.add_component(comp, closest_layer)
                    self.builder.update_stats()
                 else:
                    self.builder.show_error("Mass Limit!")
            else:
                self.builder.show_error(f"Cannot place {comp.name} in {closest_layer.name}")


class BuilderSceneGUI:
    def __init__(self, screen_width, screen_height, on_start_battle):
        self.width = screen_width
        self.height = screen_height
        self.on_start_battle = on_start_battle
        
        # UI Manager
        import os
        theme_path = os.path.join(os.path.dirname(__file__), 'builder_theme.json')
        self.ui_manager = pygame_gui.UIManager(
            (screen_width, screen_height),
            theme_path=theme_path if os.path.exists(theme_path) else None
        )
        
        # Ship
        self.ship = Ship("Custom Ship", screen_width // 2, screen_height // 2, (100, 100, 255))
        self.ship.recalculate_stats()
        
        # Managers
        self.available_components = get_all_components()
        self.template_modifiers = {}
        self.sprite_mgr = SpriteManager.get_instance()
        
        base_path = os.path.dirname(os.path.abspath(__file__))
        self.preset_manager = PresetManager(os.path.join(base_path, "data", "presets.json"))
        self.theme_manager = ShipThemeManager.get_instance()
        self.theme_manager.initialize(base_path)
        
        # Layout
        self.left_panel_width = 450
        self.right_panel_width = 380
        self.bottom_bar_height = 60
        self.weapons_report_height = 600
        
        # MVC Lite
        rect = pygame.Rect(
            self.left_panel_width, 0,
            self.width - self.left_panel_width - self.right_panel_width,
            self.height - self.bottom_bar_height - self.weapons_report_height
        )
        self.view = SchematicView(rect, self.sprite_mgr, self.theme_manager)
        self.controller = InteractionController(self, self.view)
        
        self.error_message = ""
        self.error_timer = 0
        self.show_firing_arcs = False
        
        self._create_ui()
        
    def _create_ui(self):
        self.left_panel = BuilderLeftPanel(
            self, self.ui_manager,
            pygame.Rect(0, 0, self.left_panel_width, self.height - self.bottom_bar_height)
        )
        
        self.right_panel = BuilderRightPanel(
            self, self.ui_manager,
            pygame.Rect(self.width - self.right_panel_width, 0, 
                        self.right_panel_width, self.height - self.bottom_bar_height - self.weapons_report_height)
        )
        
        weapons_panel_y = self.height - self.bottom_bar_height - self.weapons_report_height
        weapons_panel_width = self.width - self.left_panel_width
        self.weapons_report_panel = WeaponsReportPanel(
            self, self.ui_manager,
            pygame.Rect(self.left_panel_width, weapons_panel_y, weapons_panel_width, self.weapons_report_height),
            self.sprite_mgr
        )
        
        # Bottom Bar Buttons
        btn_y = self.height - self.bottom_bar_height + 10
        btn_w = 140
        btn_h = 40
        spacing = 10
        
        # Define buttons to create in order
        # (Attribute Name, Text, Width)
        button_defs = [
            ('clear_btn', "Clear Design", 140),
            ('save_btn', "Save", 140),
            ('load_btn', "Load", 140),
            ('arc_toggle_btn', "Show Firing Arcs", 160),
            ('target_btn', "Select Target", 140),
            ('verbose_btn', "Toggle Verbose", 160),
            ('start_btn', "Return", 140)
        ]
        
        total_width = sum(b[2] for b in button_defs) + spacing * (len(button_defs) - 1)
        start_x = (self.width - total_width) // 2
        
        current_x = start_x
        for attr_name, text, w in button_defs:
            btn = UIButton(pygame.Rect(current_x, btn_y, w, btn_h), text, self.ui_manager)
            setattr(self, attr_name, btn)
            current_x += w + spacing
        
        self.confirm_dialog = None
        
        self.update_stats()
        self.left_panel.update_component_list()

    def update_stats(self):
        self.right_panel.update_stats_display(self.ship)
        
    def on_selection_changed(self, component_tuple):
        # component_tuple is (layer, index, comp) or None
        # We need to expose selected_component to LeftPanel if it uses it.
        # Currently LeftPanel uses builder.selected_component.
        # But now selected_component is in controller.
        # We should proxy it or alias it.
        # For legacy compatibility, let's add a property or sync it?
        # A property is better.
        self.left_panel.rebuild_modifier_ui()

    @property
    def selected_component(self):
        return self.controller.selected_component
        
    @property
    def dragged_item(self):
        return self.controller.dragged_item
        
    @dragged_item.setter
    def dragged_item(self, value):
        self.controller.dragged_item = value

    def show_error(self, msg):
        self.error_message = msg
        self.error_timer = 3.0
        
    def _show_error(self, msg):
        self.show_error(msg)
        
    def handle_event(self, event):
        self.ui_manager.process_events(event)
        
         # Pass to modifier panel
        action = self.left_panel.handle_event(event)
        if action:
            act_type, data = action
            if act_type == 'refresh_ui':
                self.left_panel.rebuild_modifier_ui()
                self.update_stats() 
            elif act_type == 'clear_settings':
                if self.controller.selected_component:
                    self.controller.selected_component = None
                    self.on_selection_changed(None)
                else:
                    self.template_modifiers = {}
                self.left_panel.rebuild_modifier_ui()
                logger.debug("Cleared settings or deselected component")
            elif act_type == 'apply_preset':
                self.template_modifiers = data
                self.left_panel.rebuild_modifier_ui()
            elif act_type == 'select_component_type':
                c = data
                self.controller.dragged_item = c.clone()
                # Apply template modifiers
                for m_id, val in self.template_modifiers.items():
                   if m_id in MODIFIER_REGISTRY:
                       mod_def = MODIFIER_REGISTRY[m_id]
                       allow = True
                       if mod_def.restrictions:
                           if 'allow_types' in mod_def.restrictions and c.type_str not in mod_def.restrictions['allow_types']:
                               allow = False
                       if allow:
                           self.controller.dragged_item.add_modifier(m_id)
                           m = self.controller.dragged_item.get_modifier(m_id)
                           if m: m.value = val
                self.controller.dragged_item.recalculate_stats()
            return
        
        self.controller.handle_event(event)
        
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == self.start_btn:
                self.on_start_battle(None)
            elif event.ui_element == self.save_btn:
                self._save_ship()
            elif event.ui_element == self.load_btn:
                self._load_ship()
            elif event.ui_element == self.clear_btn:
                self._show_clear_confirmation()
            elif event.ui_element == self.arc_toggle_btn:
                self.show_firing_arcs = not self.show_firing_arcs
                self.arc_toggle_btn.set_text("Hide Firing Arcs" if self.show_firing_arcs else "Show Firing Arcs")
            elif event.ui_element == self.target_btn:
                self._on_select_target_pressed()
            elif event.ui_element == self.verbose_btn:
                 self.weapons_report_panel.verbose_tooltip = not self.weapons_report_panel.verbose_tooltip
                 
        elif event.type == pygame_gui.UI_DROP_DOWN_MENU_CHANGED:
            if event.ui_element == self.right_panel.class_dropdown:
                self.ship.ship_class = event.text
                c_def = VEHICLE_CLASSES.get(self.ship.ship_class, {})
                self.ship.base_mass = c_def.get('hull_mass', 50)
                self.ship.vehicle_type = c_def.get('type', 'Ship')
                self.ship.recalculate_stats()
                self.update_stats()
                self.left_panel.update_component_list()
            elif hasattr(self.right_panel, 'vehicle_type_dropdown') and event.ui_element == self.right_panel.vehicle_type_dropdown:
                new_type = event.text
                if new_type != getattr(self.ship, 'vehicle_type', "Ship"):
                     valid_classes = [(n, VEHICLE_CLASSES[n].get('max_mass', 0)) for n, c in VEHICLE_CLASSES.items() if c.get('type', 'Ship') == new_type]
                     valid_classes.sort(key=lambda x: x[1])
                     valid_classes = [n for n, m in valid_classes]
                     if not valid_classes: valid_classes = ["Escort"]
                     
                     self.right_panel.class_dropdown.kill()
                     self.right_panel.class_dropdown = UIDropDownMenu(valid_classes, valid_classes[0], 
                                                        pygame.Rect(70, self.right_panel.class_dropdown.relative_rect.y, 195, 30), 
                                                        manager=self.ui_manager, container=self.right_panel.panel)
                     
                     self.ship.ship_class = valid_classes[0]
                     cls_def = VEHICLE_CLASSES.get(valid_classes[0], {})
                     self.ship.base_mass = cls_def.get('hull_mass', 50)
                     self.ship.vehicle_type = cls_def.get('type', "Ship")
                     
                     self.ship.recalculate_stats()
                     self.update_stats()
                     self.left_panel.update_component_list()
            elif hasattr(self.right_panel, 'theme_dropdown') and event.ui_element == self.right_panel.theme_dropdown:
                self.ship.theme_id = event.text
                logger.info(f"Changed theme to {event.text}")
            elif event.ui_element == self.right_panel.ai_dropdown:
                from ai import COMBAT_STRATEGIES
                selected_name = event.text
                for strategy_id, strat in COMBAT_STRATEGIES.items():
                    if strat.get('name', '') == selected_name:
                        self.ship.ai_strategy = strategy_id
                        break
                else:
                    self.ship.ai_strategy = event.text.lower().replace(' ', '_')
                    
        elif event.type == pygame_gui.UI_CONFIRMATION_DIALOG_CONFIRMED:
            if event.ui_element == self.confirm_dialog:
                self._clear_design()
                
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
            for preset_name, btn in getattr(self, 'preset_buttons', []):
                if btn.rect.collidepoint(event.pos):
                    self.preset_manager.delete_preset(preset_name)
                    self.left_panel.rebuild_modifier_ui()
                    logger.info(f"Deleted preset: {preset_name}")
                    break

    def update(self, dt):
        if self.error_timer > 0:
            self.error_timer -= dt
            
        self.left_panel.update(dt)
        self.weapons_report_panel.update()
        self.controller.update()
        self.ui_manager.update(dt)
        
        # Check name entry
        if self.right_panel.name_entry.get_text() != self.ship.name:
            self.ship.name = self.right_panel.name_entry.get_text()

    def draw(self, screen):
        screen.fill(SHIP_VIEW_BG)
        
        # Determine efficient hover
        hovered = self.controller.hovered_component
        if not hovered:
             mx, my = pygame.mouse.get_pos()
             if not self.view.rect.collidepoint(mx, my):
                 hovered_item = self.left_panel.get_hovered_list_item(mx, my)
                 if hovered_item:
                     comp_template = hovered_item.component
                     preview_comp = comp_template.clone()
                     for m_id, val in self.template_modifiers.items():
                        if m_id in MODIFIER_REGISTRY:
                            mod_def = MODIFIER_REGISTRY[m_id]
                            if mod_def.restrictions and 'allow_types' in mod_def.restrictions and preview_comp.type_str not in mod_def.restrictions['allow_types']:
                                continue
                            preview_comp.add_modifier(m_id)
                            m = preview_comp.get_modifier(m_id)
                            if m: m.value = val
                     preview_comp.recalculate_stats()
                     hovered = preview_comp
                     
        self.view.draw(screen, self.ship, self.show_firing_arcs, self.controller.selected_component, hovered)
        
        self.left_panel.draw(screen)
        self.ui_manager.draw_ui(screen)
        self.weapons_report_panel.draw(screen)
        
        if hovered and not self.controller.dragged_item:
            self._draw_tooltip(screen, hovered)
            
        if self.controller.dragged_item:
            mx, my = pygame.mouse.get_pos()
            sprite = self.sprite_mgr.get_sprite(self.controller.dragged_item.sprite_index)
            if sprite:
                screen.blit(sprite, (mx - 16, my - 16))
                
        if self.error_timer > 0:
            font = pygame.font.SysFont("Arial", 18)
            err_surf = font.render(self.error_message, True, (255, 100, 100))
            x = (self.width - err_surf.get_width()) // 2
            screen.blit(err_surf, (x, 50))
            
    def _draw_tooltip(self, screen, comp):
        mx, my = pygame.mouse.get_pos()
        font = pygame.font.SysFont("Arial", 14)
        font_sm = pygame.font.SysFont("Arial", 12)
        
        lines = []
        
        # Header
        lines.append((comp.name, (255, 255, 100)))
        
        # Classification
        classification = comp.data.get('major_classification', 'Unknown')
        lines.append((classification, (150, 255, 150)))
        
        # Basic Stats
        lines.append((f"Type: {comp.type_str}", (200, 200, 200)))
        lines.append((f"Mass: {comp.mass:.1f}t", (200, 200, 200)))
        lines.append((f"HP: {comp.max_hp:.0f}", (200, 200, 200)))
        
        # Allowed Layers
        layers = [l.name for l in comp.allowed_layers]
        lines.append((f"Layers: {', '.join(layers)}", (150, 150, 200)))
        
        # Separator
        lines.append(("---", (100, 100, 100)))
        
        # Weapon Stats
        if hasattr(comp, 'damage') and comp.damage > 0:
            lines.append((f"Damage: {comp.damage}", (255, 100, 100)))
        if hasattr(comp, 'range') and comp.range > 0:
            lines.append((f"Range: {comp.range}", (255, 165, 0)))
        if hasattr(comp, 'reload_time'):
            lines.append((f"Reload: {comp.reload_time}s", (255, 200, 100)))
        if hasattr(comp, 'ammo_cost') and comp.ammo_cost > 0:
             lines.append((f"Ammo Cost: {comp.ammo_cost}", (200, 200, 50)))
        if hasattr(comp, 'energy_cost') and comp.energy_cost > 0:
             lines.append((f"Energy Cost: {comp.energy_cost}", (100, 200, 255)))
        if hasattr(comp, 'firing_arc'):
            lines.append((f"Arc: {comp.firing_arc}°", (255, 100, 255)))
        
        # Missile Stats
        if hasattr(comp, 'endurance'):
            lines.append((f"Endurance: {comp.endurance}s", (100, 200, 255)))
        if hasattr(comp, 'turn_rate') and hasattr(comp, 'endurance'):
            lines.append((f"Turn Rate: {comp.turn_rate}°/s", (100, 255, 100)))
            if hasattr(comp, 'projectile_speed'):
                lines.append((f"Speed: {comp.projectile_speed}", (200, 200, 50)))
            
        # Engine Stats
        if hasattr(comp, 'thrust_force') and comp.thrust_force > 0:
            lines.append((f"Thrust: {comp.thrust_force}", (100, 255, 100)))
        if hasattr(comp, 'turn_speed') and comp.turn_speed > 0:
            lines.append((f"Turn Speed: {comp.turn_speed}°/s", (100, 255, 150)))
        if hasattr(comp, 'fuel_cost_per_sec') and comp.fuel_cost_per_sec > 0:
            lines.append((f"Fuel Usage: {comp.fuel_cost_per_sec}/s", (255, 165, 0)))
            
        # Resource Stats (Tank/Gen)
        if hasattr(comp, 'capacity') and comp.capacity > 0:
            rtype = getattr(comp, 'resource_type', 'Resource').title()
            lines.append((f"{rtype} Cap: {comp.capacity}", (100, 255, 255)))
        if hasattr(comp, 'energy_generation_rate') and comp.energy_generation_rate > 0:
            lines.append((f"Energy Gen: {comp.energy_generation_rate}/s", (255, 255, 0)))
            
        # Shield Stats
        if hasattr(comp, 'shield_capacity') and comp.shield_capacity > 0:
             lines.append((f"Shield Max: {comp.shield_capacity}", (0, 255, 255)))
        if hasattr(comp, 'regen_rate') and comp.regen_rate > 0:
             lines.append((f"Shield Regen: {comp.regen_rate}/s", (0, 200, 255)))
        if hasattr(comp, 'energy_cost') and hasattr(comp, 'regen_rate') and comp.energy_cost > 0:
             lines.append((f"Regen Cost: {comp.energy_cost}/s", (100, 150, 255)))
             
        # Abilities
        if comp.abilities:
            lines.append(("Abilities:", (255, 255, 255)))
            for k, v in comp.abilities.items():
                if k == "CommandAndControl":
                    lines.append(("  • Command & Control", (150, 255, 150)))
                elif k == "CrewCapacity":
                    label = "Crew Capacity" if v > 0 else "Crew Required"
                    val = v if v > 0 else -v
                    color = (150, 255, 150) if v > 0 else (255, 150, 150)
                    lines.append((f"  • {label}: {val}", color))
                elif k == "LifeSupportCapacity":
                    lines.append((f"  • Life Support: {v}", (150, 255, 255)))
                elif k == "ToHitAttackModifier":
                    lines.append((f"  • Targeting: x{v}", (255, 100, 100)))
                elif k == "ToHitDefenseModifier":
                    lines.append((f"  • ECM/Jamming: x{v}", (100, 255, 255)))
                elif k in ["ShieldProjection", "ShieldRegeneration", "EnergyConsumption", "EnergyGeneration", 
                           "FuelStorage", "AmmoStorage", "EnergyStorage", "CombatPropulsion", "ManeuveringThruster",
                           "ProjectileWeapon", "BeamWeapon", "Armor"]:
                    continue # Already shown as main stat
                else:
                    lines.append((f"  • {k}: {v}", (200, 200, 200)))
        
        # Modifiers
        if comp.modifiers:
            lines.append(("Modifiers:", (150, 255, 150)))
            for m in comp.modifiers:
                lines.append((f"  • {m.definition.name}: {m.value:.0f}", (150, 255, 150)))
                
        line_height = 18
        padding = 10
        # Filter None/Empty lines
        lines = [l for l in lines if l[0] != "---" or l[1] != (0,0,0)] # "---" is separator, handle logic below
        
        max_width = max(font.size(l[0])[0] for l in lines) + padding * 2
        box_h = len(lines) * line_height + padding * 2
        box_w = max(max_width, 220)
        
        box_x = mx + 15
        box_y = my + 15
        if box_x + box_w > self.width: box_x = mx - box_w - 15
        if box_y + box_h > self.height: box_y = my - box_h - 15
            
        pygame.draw.rect(screen, (25, 25, 35), (box_x, box_y, box_w, box_h))
        pygame.draw.rect(screen, (100, 100, 150), (box_x, box_y, box_w, box_h), 1)
        
        sprite = self.sprite_mgr.get_sprite(comp.sprite_index)
        if sprite:
            screen.blit(sprite, (box_x + box_w - 42, box_y + 8))
            
        y = box_y + padding
        for text, color in lines:
            if text == "---":
                pygame.draw.line(screen, color, (box_x + 5, y + line_height//2), (box_x + box_w - 5, y + line_height//2))
            else:
                surf = font_sm.render(text, True, color)
                screen.blit(surf, (box_x + padding, y))
            y += line_height

    def _save_ship(self):
        success, message = ShipIO.save_ship(self.ship)
        if success: print(message)
        elif message: self.show_error(message)

    def _load_ship(self):
        new_ship, message = ShipIO.load_ship(self.width, self.height)
        if new_ship:
            self.ship = new_ship
            self.right_panel.name_entry.set_text(self.ship.name)
            if self.ship.ship_class in self.right_panel.class_dropdown.options_list:
                self.right_panel.class_dropdown.selected_option = self.ship.ship_class
            # Sync AI
            # ...
            self.update_stats()
            print(message)
        elif message:
            self.show_error(message)

    def _show_clear_confirmation(self):
        self.confirm_dialog = UIConfirmationDialog(
            rect=pygame.Rect((self.width // 2 - 150, self.height // 2 - 100), (300, 200)),
            action_long_desc="Clear all components and reset to default settings?",
            manager=self.ui_manager,
            window_title="Confirm Clear"
        )

    def _clear_design(self):
        logger.info("Clearing ship design")
        for layer_type, layer_data in self.ship.layers.items():
            layer_data['components'] = []
            layer_data['hp_pool'] = 0
            layer_data['max_hp_pool'] = 0
            layer_data['mass'] = 0
            layer_data['hp'] = 0
            
        self.template_modifiers = {}
        self.ship.ai_strategy = "optimal_firing_range"
        
        self.ship.recalculate_stats()
        self.update_stats()
        self.left_panel.rebuild_modifier_ui()
        self.controller.selected_component = None
        self.on_selection_changed(None)
        
        if hasattr(self, 'weapons_report_panel'):
            self.weapons_report_panel.clear_target()

    def _on_select_target_pressed(self):
        target_ship, message = ShipIO.load_ship(self.width, self.height)
        if target_ship:
            self.weapons_report_panel.set_target(target_ship)
            logger.info(f"Selected target: {target_ship.name}")
        elif message and "Cancelled" not in message:
            self.show_error(message)

