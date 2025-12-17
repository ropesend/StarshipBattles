import pygame
import time
import math
from ship import Ship, LayerType
from ai import AIController
from designs import create_brick, create_interceptor
from components import load_components, Bridge, Weapon, Engine, Thruster, Armor, Tank
from ui import Button
from builder import BuilderScene
from sprites import SpriteManager

# Constants
WIDTH, HEIGHT = 1200, 900
FPS = 60
BG_COLOR = (10, 10, 20)

LAYER_COLORS = {
    LayerType.ARMOR: (100, 100, 100),
    LayerType.OUTER: (200, 50, 50),
    LayerType.INNER: (50, 50, 200),
    LayerType.CORE: (220, 220, 220)
}

def draw_ship(surface, ship):
    if not ship.is_alive: return
    
    cx, cy = int(ship.position.x), int(ship.position.y)
    
    # Draw Layers (from large to small)
    base_radius = 40 
    
    # Armor (100%)
    pygame.draw.circle(surface, LAYER_COLORS[LayerType.ARMOR], (cx, cy), base_radius)
    # Outer (80%)
    pygame.draw.circle(surface, LAYER_COLORS[LayerType.OUTER], (cx, cy), int(base_radius * 0.8))
    # Inner (50%)
    pygame.draw.circle(surface, LAYER_COLORS[LayerType.INNER], (cx, cy), int(base_radius * 0.5))
    # Core (20%)
    pygame.draw.circle(surface, LAYER_COLORS[LayerType.CORE], (cx, cy), int(base_radius * 0.2))
    
    # Draw Direction indicator
    end_pos = ship.position + ship.forward_vector() * (base_radius + 10)
    pygame.draw.line(surface, (255, 255, 0), (cx, cy), (int(end_pos.x), int(end_pos.y)), 2)

    # Draw Components (Simplified visualization for Battle)
    # We use small colored dots because full sprites are too big for this zoom level
    for ltype, data in ship.layers.items():
        radius = 0
        if ltype == LayerType.CORE: radius = base_radius * 0.1
        elif ltype == LayerType.INNER: radius = base_radius * 0.35
        elif ltype == LayerType.OUTER: radius = base_radius * 0.65
        elif ltype == LayerType.ARMOR: radius = base_radius * 0.9
        
        comps = data['components']
        if not comps: continue
        
        angle_step = 360 / len(comps)
        current_angle = ship.angle # Rotate with ship
        
        for comp in comps:
            if not comp.is_active: continue
            rad = math.radians(current_angle)
            px = cx + math.cos(rad) * radius
            py = cy + math.sin(rad) * radius
            
            # Tiny dot
            color = (200, 200, 200)
            if isinstance(comp, Weapon): color = (255, 50, 50)
            elif isinstance(comp, Engine): color = (50, 255, 100)
            elif isinstance(comp, Armor): color = (100, 100, 100)
            
            pygame.draw.circle(surface, color, (int(px), int(py)), 3)
            current_angle += angle_step

def draw_bar(surface, x, y, w, h, pct, color):
    pct = max(0, min(1, pct))
    pygame.draw.rect(surface, (50, 50, 50), (x, y, w, h))
    pygame.draw.rect(surface, color, (x, y, w * pct, h))
    pygame.draw.rect(surface, (200, 200, 200), (x, y, w, h), 1)

def draw_hud(surface, ship, x, y):
    font_title = pygame.font.SysFont("Arial", 16, bold=True)
    font_med = pygame.font.SysFont("Arial", 14)
    font_small = pygame.font.SysFont("Arial", 12)
    
    # 1. Header
    status_color = (100, 255, 100) if ship.is_alive else (255, 50, 50)
    name_text = font_title.render(f"{ship.name}", True, status_color)
    surface.blit(name_text, (x, y))
    y += 20
    
    # 2. Physics Stats
    if ship.mass > 0:
        # F = ma -> a = F/m
        accel = ship.total_thrust / ship.mass
        # Terminal Velocity with linear drag: v_term = a / drag
        # PhysicsBody default drag is 0.5, but Ship sets it to 0.3
        top_speed = accel / ship.drag if ship.drag > 0 else 0
        
        stats_text = f"Top Speed: {int(top_speed)}"
        accel_text = f"Accel: {accel:.1f}"
        
        s_surf = font_med.render(stats_text, True, (200, 200, 255))
        a_surf = font_med.render(accel_text, True, (200, 200, 255))
        surface.blit(s_surf, (x, y))
        surface.blit(a_surf, (x + 120, y))
        y += 20
    
    # 3. Resources
    # Fuel
    draw_bar(surface, x, y, 100, 8, ship.current_fuel / ship.max_fuel if ship.max_fuel > 0 else 0, (255, 165, 0))
    surface.blit(font_small.render("Fuel", True, (200, 200, 200)), (x + 105, y - 2))
    y += 12
    # Ammo
    draw_bar(surface, x, y, 100, 8, ship.current_ammo / ship.max_ammo if ship.max_ammo > 0 else 0, (255, 50, 50))
    surface.blit(font_small.render("Ammo", True, (200, 200, 200)), (x + 105, y - 2))
    y += 20
    
    # 4. Component List
    # We will list components by layer
    y_start = y
    
    layer_order = [LayerType.ARMOR, LayerType.OUTER, LayerType.INNER, LayerType.CORE]
    
    for ltype in layer_order:
        # Layer Header
        l_text = font_med.render(f"[{ltype.name}]", True, (150, 150, 150))
        surface.blit(l_text, (x, y))
        y += 18
        
        components = ship.layers[ltype]['components']
        if not components:
            none_text = font_small.render("  (Empty)", True, (100, 100, 100))
            surface.blit(none_text, (x, y))
            y += 14
            continue
            
        for comp in components:
            # Color based on status
            c_color = (200, 200, 200)
            if not comp.is_active:
                c_color = (80, 80, 80) # Destroyed
            elif comp.current_hp < comp.max_hp * 0.5:
                c_color = (255, 100, 100) # Damaged
                
            c_name = font_small.render(f"  {comp.name}", True, c_color)
            surface.blit(c_name, (x, y))
            
            # HP Bar for component
            if comp.max_hp > 0:
                bx = x + 120
                pct = comp.current_hp / comp.max_hp
                bar_color = (50, 200, 50) if comp.is_active else (50, 50, 50)
                if pct < 0.5: bar_color = (200, 200, 50)
                if pct < 0.2: bar_color = (200, 50, 50)
                
                draw_bar(surface, bx, y + 2, 60, 6, pct, bar_color)
            
            y += 14
            
    # Draw Border around HUD
    # pygame.draw.rect(surface, (50, 50, 60), (x - 10, 10, 230, y), 1)

# Scene States
MENU = 0
BUILDER = 1
BATTLE = 2

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Starship Battles")
        self.clock = pygame.time.Clock()
        self.running = True
        self.state = MENU
        
        # Build absolute path to resources
        import os
        base_path = os.path.dirname(os.path.abspath(__file__))
        print(f"DEBUG: Base Path: {base_path}")
        
        # Initialize Game Data
        comp_path = os.path.join(base_path, "components.json")
        load_components(comp_path)
        
        # Initialize Sprites
        sprite_mgr = SpriteManager.get_instance()
        atlas_path = os.path.join(base_path, "resources", "images", "Components.bmp")
        sprite_mgr.load_atlas(atlas_path)
        
        # Battle State Data
        self.ship1 = None
        self.ship2 = None
        self.ai1 = None
        self.ai2 = None
        self.projectiles = []
        
        # Menu UI
        self.menu_buttons = [
            Button(WIDTH//2 - 100, HEIGHT//2 - 50, 200, 50, "Quick Battle", self.start_quick_battle),
            Button(WIDTH//2 - 100, HEIGHT//2 + 20, 200, 50, "Ship Builder", self.start_builder)
        ]
        
        # Builder
        self.builder_scene = BuilderScene(WIDTH, HEIGHT, self.on_builder_finish)

    def start_quick_battle(self):
        self.start_battle(create_brick(200, HEIGHT // 2), create_interceptor(WIDTH - 200, HEIGHT // 2))

    def start_builder(self):
        self.state = BUILDER
        self.builder_scene = BuilderScene(WIDTH, HEIGHT, self.on_builder_finish)

    def on_builder_finish(self, custom_ship):
        # We need to position the custom ship and create an enemy
        custom_ship.position = pygame.math.Vector2(200, HEIGHT // 2)
        # Recalculate stats one last time to be sure
        custom_ship.recalculate_stats()
        
        enemy = create_brick(WIDTH - 200, HEIGHT // 2)
        
        self.start_battle(custom_ship, enemy)

    def start_battle(self, s1, s2):
        self.ship1 = s1
        self.ship2 = s2
        self.ai1 = AIController(self.ship1, self.ship2)
        self.ai2 = AIController(self.ship2, self.ship1)
        self.projectiles = []
        self.state = BATTLE

    def update_battle(self, dt):
        self.ai1.update(dt)
        self.ai2.update(dt)
        self.ship1.update(dt)
        self.ship2.update(dt)
        
        # Collect Projectiles
        if hasattr(self.ship1, 'just_fired_projectiles'):
            self.projectiles.extend(self.ship1.just_fired_projectiles)
        if hasattr(self.ship2, 'just_fired_projectiles'):
            self.projectiles.extend(self.ship2.just_fired_projectiles)
            
        # Update Projectiles
        for p in self.projectiles[:]:
            p['pos'] += p['vel'] * dt
            p['distance_traveled'] += p['vel'].length() * dt
            
            # Collisions
            hit = False
            for target in [self.ship1, self.ship2]:
                if target == p['owner']: continue
                if not target.is_alive: continue
                if p['pos'].distance_to(target.position) < 40:
                    target.take_damage(p['damage'])
                    hit = True
                    break
            
            if hit or p['distance_traveled'] > p['range']:
                self.projectiles.remove(p)

    def draw_battle(self):
        self.screen.fill(BG_COLOR)
        draw_ship(self.screen, self.ship1)
        draw_ship(self.screen, self.ship2)
        
        for p in self.projectiles:
            start = p['pos']
            end = p['pos'] - p['vel'].normalize() * 10
            pygame.draw.line(self.screen, (255, 255, 0), start, end, 2)
            
        draw_hud(self.screen, self.ship1, 10, 10)
        draw_hud(self.screen, self.ship2, WIDTH - 250, 10)

    def run(self):
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0
            
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    self.running = False
                
                if self.state == MENU:
                    for btn in self.menu_buttons:
                        btn.handle_event(event)
                elif self.state == BUILDER:
                    self.builder_scene.handle_event(event)
            
            # Logic & Draw
            if self.state == MENU:
                self.screen.fill((20, 20, 30))
                for btn in self.menu_buttons:
                    btn.draw(self.screen)
            elif self.state == BUILDER:
                self.builder_scene.update(dt)
                self.builder_scene.draw(self.screen)
            elif self.state == BATTLE:
                self.update_battle(dt)
                self.draw_battle()
                
            pygame.display.flip()
        
        pygame.quit()

if __name__ == "__main__":
    game = Game()
    game.run()
