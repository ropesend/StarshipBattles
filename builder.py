import json
import tkinter
import pygame
from tkinter import filedialog
from tkinter import filedialog
from ui import Button, Label, Slider
from ship import Ship, LayerType
from components import get_all_components, MODIFIER_REGISTRY, Bridge, Weapon, Engine, Thruster, Armor, Tank
from sprites import SpriteManager

# Initialize Tkinter root and hide it
root = tkinter.Tk()
root.withdraw()

# Colors
PALETTE_BG = (30, 30, 40)
SHIP_VIEW_BG = (10, 10, 20)
INFO_BG = (30, 30, 40)

class BuilderScene:
    def __init__(self, screen_width, screen_height, on_start_battle):
        self.width = screen_width
        self.height = screen_height
        self.on_start_battle = on_start_battle
        
        # Ship being built
        self.ship = Ship("Custom Ship", screen_width // 2, screen_height // 2, (100, 100, 255))
        
        # UI Layout
        self.palette_width = 250
        self.info_width = 250
        
        # Component Palette Items
        self.available_components = get_all_components()
        
        self.buttons = []
        self.labels = []
        
        # Inspector UI State
        self.selected_component = None # (layer, index, component)
        self.inspector_buttons = []
        self.inspector_sliders = []
        self.inspector_labels = []
        
        # Create Buttons (Start, Save, Load)
        
        # Create Buttons (Start, Save, Load)
        btn_width = 220
        btn_height = 40
        btn_x = screen_width - self.info_width + 15
        
        self.start_btn = Button(btn_x, screen_height - 60, btn_width, btn_height, "START BATTLE", self.try_start)
        self.save_btn = Button(btn_x, screen_height - 110, btn_width, btn_height, "SAVE DESIGN", self.save_ship)
        self.load_btn = Button(btn_x, screen_height - 160, btn_width, btn_height, "LOAD DESIGN", self.load_ship)
        
        self.buttons.extend([self.start_btn, self.save_btn, self.load_btn])

        # Dragging State
        self.dragged_item = None # Instance being dragged
        self.dragged_icon_rect = None
        
        self.error_message = ""
        self.error_timer = 0
        
        # Areas
        self.palette_rect = pygame.Rect(0, 0, self.palette_width, screen_height)
        self.info_rect = pygame.Rect(screen_width - self.info_width, 0, self.info_width, screen_height)
        
        self.sprite_mgr = SpriteManager.get_instance()

    def try_start(self):
        # Validation
        if self.ship.current_mass > self.ship.max_mass_budget:
            self.show_error("Mass Limit Exceeded!")
            return
            
        has_bridge = any(isinstance(c, Bridge) for c in self.ship.layers[LayerType.CORE]['components'])
        has_bridge = has_bridge or any(isinstance(c, Bridge) for l in self.ship.layers.values() for c in l['components'])
        
        if not has_bridge:
            self.show_error("Ship needs a Bridge!")
            return
            
        self.on_start_battle(self.ship)

    def save_ship(self):
        data = self.ship.to_dict()
        filename = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON Files", "*.json")])
        if filename:
            try:
                with open(filename, 'w') as f:
                    json.dump(data, f, indent=4)
                print(f"Saved ship to {filename}")
            except Exception as e:
                self.show_error(f"Save failed: {e}")

    def load_ship(self):
        filename = filedialog.askopenfilename(filetypes=[("JSON Files", "*.json")])
        if filename:
            try:
                with open(filename, 'r') as f:
                    data = json.load(f)
                
                # Reconstruct ship
                new_ship = Ship.from_dict(data)
                
                # Update position and recalculate mass/stats
                new_ship.position = pygame.math.Vector2(self.width // 2, self.height // 2)
                new_ship.recalculate_stats()
                
                self.ship = new_ship
                print(f"Loaded ship from {filename}")
            except Exception as e:
                self.show_error(f"Load failed: {e}")

    def show_error(self, msg):
        self.error_message = msg
        self.error_timer = 3.0

    def update(self, dt):
        if self.error_timer > 0:
            self.error_timer -= dt

    def handle_event(self, event):
        for btn in self.buttons:
            btn.handle_event(event)
            
        # Inspector controls
        for btn in self.inspector_buttons:
             btn.handle_event(event)
        for s in self.inspector_sliders:
             s.handle_event(event)

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                # Check Palette click
                if self.palette_rect.collidepoint(event.pos):
                    # Simple list detection
                    y_offset = 50
                    for comp in self.available_components:
                        rect = pygame.Rect(10, y_offset, 220, 40)
                        if rect.collidepoint(event.pos):
                            self.dragged_item = comp.clone() # Clone for dragging
                            break
                        y_offset += 50
                else:
                    # Check if clicking on an existing component on the ship
                    found = self.get_component_at_pos(event.pos)
                    if found:
                        if self.selected_component and self.selected_component == found:
                            # Already selected, pick it up
                            layer, index, comp = found
                            self.ship.remove_component(layer, index)
                            self.dragged_item = comp
                            self.selected_component = None 
                            self.rebuild_inspector()
                        else:
                            # Select it
                            self.select_component(found)
                    else:
                         self.selected_component = None
                         self.rebuild_inspector()
            elif event.button == 3: # Right click to remove
                # Check ship layers
                pass # TODO: Implement removal logic

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1 and self.dragged_item:
                # Drop
                self.handle_drop(event.pos)
                self.dragged_item = None

    def get_component_at_pos(self, pos):
        """Returns (layer_type, index, component) or None"""
        mx, my = pos
        cx, cy = self.width // 2, self.height // 2
        max_r = 300
        
        # We need to replicate the 'draw' logic to find positions
        # Iterate backwards to pick top-most if overlapping? 
        # Actually draw order is Core -> Armor, so Armor is top.
        
        # Check layers in reverse draw order (top to bottom) is usually best for clicking
        # But here draw order is: Armor(Largest) -> Outer -> Inner -> Core?
        # No, draw code:
        # pygame.draw.circle(screen, ..., max_r, 2) # Armor
        # ...
        # Inner loop iterates layers, but which order?
        # dict iteration order.
        
        # Let's iterate all components and find closest one < some radius
        
        # Detection radius
        hit_radius = 20
        
        for ltype, data in self.ship.layers.items():
            radius = 0
            if ltype == LayerType.CORE: radius = max_r * 0.1
            elif ltype == LayerType.INNER: radius = max_r * 0.35
            elif ltype == LayerType.OUTER: radius = max_r * 0.65
            elif ltype == LayerType.ARMOR: radius = max_r * 0.9
            
            comps = data['components']
            if not comps: continue
            
            angle_step = 360 / len(comps)
            current_angle = 0
            
            import math
            
            for i, comp in enumerate(comps):
                rad = math.radians(current_angle)
                px = cx + math.cos(rad) * radius
                py = cy + math.sin(rad) * radius
                
                # Distance check
                d = math.hypot(mx - px, my - py)
                if d < hit_radius:
                    return (ltype, i, comp)
                
                current_angle += angle_step
        return None

    def handle_drop(self, pos):
        ship_center = (self.width // 2, self.height // 2)
        dist = pygame.math.Vector2(pos[0] - ship_center[0], pos[1] - ship_center[1]).length()
        
        max_r = 300
        layer = None
        if dist < max_r * 0.2:
            layer = LayerType.CORE
        elif dist < max_r * 0.5:
            layer = LayerType.INNER
        elif dist < max_r * 0.8:
            layer = LayerType.OUTER
        elif dist < max_r * 1.0:
            layer = LayerType.ARMOR
            
        if layer:
            comp = self.dragged_item # Already cloned
            if layer in comp.allowed_layers:
                if self.ship.current_mass + comp.mass <= self.ship.max_mass_budget:
                    self.ship.add_component(comp, layer)
                else:
                    self.show_error("Mass Limit!")
            else:
                self.show_error(f"Cannot place {comp.name} in {layer.name}")

    def draw(self, screen):
        # Draw Backgrounds
        screen.fill(SHIP_VIEW_BG)
        pygame.draw.rect(screen, PALETTE_BG, self.palette_rect)
        pygame.draw.rect(screen, INFO_BG, self.info_rect)
        
        # Draw Palette
        y_offset = 50
        font = pygame.font.SysFont("Arial", 16)
        if not self.available_components:
            err = font.render("NO COMPONENTS LOADED", True, (255, 0, 0))
            screen.blit(err, (10, 100))
            
        for comp in self.available_components:
            rect = pygame.Rect(10, y_offset, 220, 40)
            
            # Hover effect
            mx, my = pygame.mouse.get_pos()
            if rect.collidepoint((mx, my)):
                pygame.draw.rect(screen, (80, 80, 90), rect)
            else:
                pygame.draw.rect(screen, (60, 60, 70), rect)
                
            # Draw Sprite
            sprite = self.sprite_mgr.get_sprite(comp.sprite_index)
            if sprite:
                screen.blit(sprite, (20, y_offset + 4))
            else:
                # Fallback
                pygame.draw.rect(screen, (255, 0, 255), (20, y_offset + 4, 32, 32))
            
            text = font.render(f"{comp.name} ({comp.mass}t)", True, (255, 255, 255))
            screen.blit(text, (60, y_offset + 10))
            y_offset += 50
            
        # Draw Ship Schematic
        cx, cy = self.width // 2, self.height // 2
        max_r = 300
        # Draw rings
        pygame.draw.circle(screen, (100, 100, 100), (cx, cy), max_r, 2) # Armor
        pygame.draw.circle(screen, (200, 50, 50), (cx, cy), int(max_r * 0.8), 2) # Outer
        pygame.draw.circle(screen, (50, 50, 200), (cx, cy), int(max_r * 0.5), 2) # Inner
        pygame.draw.circle(screen, (200, 200, 200), (cx, cy), int(max_r * 0.2), 2) # Core
        
        # Draw Mounted Components
        for ltype, data in self.ship.layers.items():
            radius = 0
            if ltype == LayerType.CORE: radius = max_r * 0.1
            elif ltype == LayerType.INNER: radius = max_r * 0.35
            elif ltype == LayerType.OUTER: radius = max_r * 0.65
            elif ltype == LayerType.ARMOR: radius = max_r * 0.9
            
            comps = data['components']
            if not comps: continue
            
            angle_step = 360 / len(comps)
            current_angle = 0
            for comp in comps:
                # Convert polar to cartesian
                import math
                rad = math.radians(current_angle)
                px = cx + math.cos(rad) * radius
                py = cy + math.sin(rad) * radius
                
                # Draw Sprite Rotated
                sprite = self.sprite_mgr.get_sprite(comp.sprite_index)
                if sprite:
                    # Rotate sprite outwards
                    # Sprite default UP? or RIGHT?
                    # Let's assume UP is default.
                    # Rotation angle: -current_angle - 90 (Pygame rotation is CCW, standard math is CCW from Right)
                    # Let's try simple rotation
                    rotated_sprite = pygame.transform.rotate(sprite, -current_angle - 90)
                    rect = rotated_sprite.get_rect(center=(int(px), int(py)))
                    screen.blit(rotated_sprite, rect)
                else:
                    pygame.draw.rect(screen, (0, 255, 0), (px - 10, py - 10, 20, 20))
                
                current_angle += angle_step

        # Draw Stats
        sx = self.width - self.info_width + 10
        sy = 50
        
        lines = [
            f"Mass: {self.ship.current_mass} / {self.ship.max_mass_budget}",
            f"Thrust: {self.ship.total_thrust}",
            f"Turn: {self.ship.turn_speed}",
            f"HP (Armor): {self.ship.layers[LayerType.ARMOR].get('hp_pool', 0)}"
        ]
        
        for line in lines:
            txt = font.render(line, True, (255, 255, 255))
            screen.blit(txt, (sx, sy))
            sy += 30

        # Draw Error
        if self.error_timer > 0:
            err_surf = font.render(self.error_message, True, (255, 100, 100))
            screen.blit(err_surf, (self.width // 2 - err_surf.get_width() // 2, 50))

        # Draw Dragged Item
        if self.dragged_item:
            mx, my = pygame.mouse.get_pos()
            sprite = self.sprite_mgr.get_sprite(self.dragged_item.sprite_index)
            if sprite:
                screen.blit(sprite, (mx - 16, my - 16))
            else:
               txt = font.render(self.dragged_item.name, True, (255, 255, 0))
               screen.blit(txt, (mx + 15, my + 15))

        if self.selected_component:
             pygame.draw.rect(screen, (40, 40, 50), (self.width - self.info_width, 200, self.info_width, 400))
             
             for lbl in self.inspector_labels:
                 lbl.draw(screen)
             for btn in self.inspector_buttons:
                 btn.draw(screen)
             for slid in self.inspector_sliders:
                 slid.draw(screen)

        # Draw UI
        for btn in self.buttons:
            btn.draw(screen)

    def select_component(self, selection):
        self.selected_component = selection
        self.rebuild_inspector()
        
    def rebuild_inspector(self):
        self.inspector_buttons = []
        self.inspector_sliders = []
        self.inspector_labels = []
        
        if not self.selected_component: return
        
        layer, index, comp = self.selected_component
        
        # Header
        x = self.width - self.info_width + 10
        y = 210
        self.inspector_labels.append(Label(x, y, f"Editing: {comp.name}", 16, (100, 255, 100)))
        y += 30
        
        # Stats
        self.inspector_labels.append(Label(x, y, f"Mass: {comp.mass:.1f}", 14))
        y += 20
        self.inspector_labels.append(Label(x, y, f"HP: {comp.max_hp:.1f}", 14))
        y += 30
        
        # Modifiers
        self.inspector_labels.append(Label(x, y, "Modifiers:", 16, (200, 200, 100)))
        y += 25
        
        for mod_id, mod_def in MODIFIER_REGISTRY.items():
            # Check compatibility
            allowed = True
            if 'deny_types' in mod_def.restrictions and comp.type_str in mod_def.restrictions['deny_types']:
                allowed = False
            if 'allow_types' in mod_def.restrictions and comp.type_str not in mod_def.restrictions['allow_types']:
                allowed = False
                
            if not allowed: continue
            
            # Check if applied
            applied_mod = comp.get_modifier(mod_id)
            is_active = (applied_mod is not None)
            
            # Toggle Button
            color = (50, 150, 50) if is_active else (80, 80, 80)
            btn_txt = f"[x] {mod_def.name}" if is_active else f"[ ] {mod_def.name}"
            
            def toggle_cb(m_id=mod_id, c=comp):
                if c.get_modifier(m_id):
                    c.remove_modifier(m_id)
                else:
                    c.add_modifier(m_id)
                self.ship.recalculate_stats()
                self.rebuild_inspector()
                
            self.inspector_buttons.append(Button(x, y, 200, 30, btn_txt, toggle_cb, color))
            y += 40
            
            # If active and parametric, show slider
            if is_active and mod_def.type_str == 'linear':
                # Slider
                val_lbl = Label(x + 10, y, f"{mod_def.param_name}: {applied_mod.value:.0f}", 12)
                self.inspector_labels.append(val_lbl)
                y += 20
                
                def slide_cb(val, m=applied_mod, l=val_lbl, pname=mod_def.param_name, c=comp):
                    m.value = val
                    l.update_text(f"{pname}: {val:.0f}")
                    c.recalculate_stats()
                    self.ship.recalculate_stats()
                    # We should technically refresh labels but this works for slider label
                    
                slider = Slider(x, y, 200, 20, mod_def.min_val, mod_def.max_val, applied_mod.value, slide_cb)
                self.inspector_sliders.append(slider)
                y += 30
