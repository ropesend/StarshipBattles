import pygame
import time
import math
import random
from ship import Ship, LayerType
from ai import AIController
from spatial import SpatialGrid
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

pygame.font.init()
font_small = pygame.font.SysFont("arial", 12)
font_med = pygame.font.SysFont("arial", 20)
font_large = pygame.font.SysFont("arial", 32)


class Camera:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.position = pygame.math.Vector2(0, 0)
        self.zoom = 1.0
        self.min_zoom = 0.01
        self.max_zoom = 5.0
        
    def update_input(self, dt, events):
        keys = pygame.key.get_pressed()
        speed = 1000 / self.zoom # Pan faster when zoomed out
        
        move = pygame.math.Vector2(0, 0)
        if keys[pygame.K_LEFT] or keys[pygame.K_a]: move.x = -1
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]: move.x = 1
        if keys[pygame.K_UP] or keys[pygame.K_w]: move.y = -1
        if keys[pygame.K_DOWN] or keys[pygame.K_s]: move.y = 1
        
        if move.length() > 0:
            self.position += move.normalize() * speed * dt

        # Middle Mouse Panning
        if pygame.mouse.get_pressed()[1]:
            rel = pygame.mouse.get_rel()
            # Invert relations because if we drag mouse left, camera moves left (position decreases)
            # Actually, if we drag mouse left (negative x), we want to see what is on the right?
            # Standard pan: drag world. Move mouse left -> World moves left -> Camera moves right.
            # let's try: Camera moves opposite to mouse delta.
            # mouse_rel is in screen pixels. correct by zoom.
            delta = pygame.math.Vector2(rel) / self.zoom
            self.position -= delta
        else:
            pygame.mouse.get_rel() # clear relative movement

        for event in events:
            if event.type == pygame.MOUSEWHEEL:
                old_zoom = self.zoom
                # Zoom centered on mouse? For now, just center zoom is easier, or simple zoom in/out
                zoom_speed = 0.1
                if event.y > 0:
                    self.zoom *= 1.1
                else:
                    self.zoom /= 1.1
                
                self.zoom = max(self.min_zoom, min(self.max_zoom, self.zoom))

    def world_to_screen(self, world_pos):
        # Screen Center = Camera Position
        # Offset = (WorldPos - CameraPos) * Zoom
        # ScreenPos = ScreenCenter + Offset
        screen_center = pygame.math.Vector2(self.width / 2, self.height / 2)
        offset = (world_pos - self.position) * self.zoom
        return screen_center + offset

    def screen_to_world(self, screen_pos):
        screen_center = pygame.math.Vector2(self.width / 2, self.height / 2)
        offset = pygame.math.Vector2(screen_pos) - screen_center
        return self.position + (offset / self.zoom)

    def fit_objects(self, objects):
        if not objects: return
        
        min_x = min(o.position.x for o in objects)
        max_x = max(o.position.x for o in objects)
        min_y = min(o.position.y for o in objects)
        max_y = max(o.position.y for o in objects)
        
        center_x = (min_x + max_x) / 2
        center_y = (min_y + max_y) / 2
        self.position = pygame.math.Vector2(center_x, center_y)
        
        # Calculate fit zoom
        width = max_x - min_x + 500 # Margin
        height = max_y - min_y + 500
        
        zoom_x = self.width / width
        zoom_y = self.height / height
        self.zoom = min(zoom_x, zoom_y)
        self.zoom = max(self.min_zoom, min(self.max_zoom, self.zoom))

def draw_ship(surface, ship, camera):
    if not ship.is_alive: return
    
    # Transform Position
    screen_pos = camera.world_to_screen(ship.position)
    cx, cy = int(screen_pos.x), int(screen_pos.y)
    
    # Culling
    radius_screen = 50 * camera.zoom # approx max radius
    if (cx + radius_screen < 0 or cx - radius_screen > camera.width or 
        cy + radius_screen < 0 or cy - radius_screen > camera.height):
        return

    # Helper for scaling based on zoom
    def scale(val):
        return int(val * camera.zoom)
    
    # Layers
    base_radius = 40
    scaled_radius = scale(base_radius)
    
    if scaled_radius < 3:
        # Draw simple dot icon for low zoom
        color = ship.color # Use ship identity color
        pygame.draw.circle(surface, color, (cx, cy), 3) # Fixed 3px dot
        # Direction
        dir_vec = ship.forward_vector()
        end_pos = camera.world_to_screen(ship.position + dir_vec * 100)
        pygame.draw.line(surface, (255, 255, 0), (cx, cy), (int(end_pos.x), int(end_pos.y)), 1)
        return

    # Draw Layers (from large to small)
    
    # Armor (100%)
    pygame.draw.circle(surface, LAYER_COLORS[LayerType.ARMOR], (cx, cy), scale(base_radius))
    # Outer (80%)
    pygame.draw.circle(surface, LAYER_COLORS[LayerType.OUTER], (cx, cy), scale(base_radius * 0.8))
    # Inner (50%)
    pygame.draw.circle(surface, LAYER_COLORS[LayerType.INNER], (cx, cy), scale(base_radius * 0.5))
    # Core (20%)
    pygame.draw.circle(surface, LAYER_COLORS[LayerType.CORE], (cx, cy), scale(base_radius * 0.2))
    
    # Draw Direction indicator
    # Need to rotate vector, but length scales is enough
    dir_vec = ship.forward_vector()
    end_pos_screen = camera.world_to_screen(ship.position + dir_vec * (base_radius + 10))
    pygame.draw.line(surface, (255, 255, 0), (cx, cy), (int(end_pos_screen.x), int(end_pos_screen.y)), max(1, scale(2)))

    # Draw Components (Simplified visualization for Battle)
    # We use small colored dots because full sprites are too big for this zoom level
    # Only draw details if zoom is high enough
    if camera.zoom > 0.3:
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
                # World offset
                off_x = math.cos(rad) * radius
                off_y = math.sin(rad) * radius
                
                # We can just transform the final world pos
                comp_world_pos = ship.position + pygame.math.Vector2(off_x, off_y)
                comp_screen = camera.world_to_screen(comp_world_pos)
                
                # Tiny dot
                color = (200, 200, 200)
                if isinstance(comp, Weapon): color = (255, 50, 50)
                elif isinstance(comp, Engine): color = (50, 255, 100)
                elif isinstance(comp, Armor): color = (100, 100, 100)
                
                pygame.draw.circle(surface, color, (int(comp_screen.x), int(comp_screen.y)), max(1, scale(3)))
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
    y += 12
    # Energy
    draw_bar(surface, x, y, 100, 8, ship.current_energy / ship.max_energy if ship.max_energy > 0 else 0, (50, 100, 255))
    surface.blit(font_small.render("Energy", True, (200, 200, 200)), (x + 105, y - 2))
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
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
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
        self.beams = []
        
        # Menu UI
        self.menu_buttons = [
            Button(WIDTH//2 - 100, HEIGHT//2 - 50, 200, 50, "Quick Battle", self.start_quick_battle),
            Button(WIDTH//2 - 100, HEIGHT//2 + 20, 200, 50, "Ship Builder", self.start_builder)
        ]
        
        # Builder
        self.builder_scene = BuilderScene(WIDTH, HEIGHT, self.on_builder_finish)
        
        # Camera
        self.camera = Camera(WIDTH, HEIGHT)
        
        # Spatial Grid
        self.grid = SpatialGrid(cell_size=2000)
        self.ships = []
        self.ai_controllers = []

    def start_quick_battle(self):
        # 5v5 Battle
        team1_ships = []
        for i in range(5):
            # Line formation
            s = create_brick(20000, 40000 + i * 5000) 
            s.team_id = 0
            team1_ships.append(s)
            
        team2_ships = []
        for i in range(5):
             # Cluster formation
            s = create_interceptor(80000, 40000 + i * 5000)
            s.team_id = 1
            s.angle = 180 # Face left
            team2_ships.append(s)
            
        self.start_battle(team1_ships, team2_ships)

    def start_builder(self):
        self.state = BUILDER
        self.builder_scene = BuilderScene(WIDTH, HEIGHT, self.on_builder_finish)

    def on_builder_finish(self, custom_ship):
        # Position custom ship in team 1
        team1 = [custom_ship]
        # create 4 friends
        for i in range(4):
            team1.append(create_brick(0,0))
            
        # Place them
        for i, s in enumerate(team1):
            s.position = pygame.math.Vector2(20000, 40000 + i * 5000)
            s.recalculate_stats() # Just in case

        team2 = []
        for i in range(5):
            s = create_interceptor(80000, 40000 + i * 5000)
            s.angle = 180
            team2.append(s)
        
        self.start_battle(team1, team2)

    def start_battle(self, team1_list, team2_list):
        self.ships = []
        self.ai_controllers = []
        
        # Handle single ship args if passed
        if not isinstance(team1_list, list): team1_list = [team1_list]
        if not isinstance(team2_list, list): team2_list = [team2_list]
        
        # Setup Team 1
        for s in team1_list:
            s.team_id = 0
            self.ships.append(s)
            self.ai_controllers.append(AIController(s, self.grid, 1))
            
        # Setup Team 2
        for s in team2_list:
            s.team_id = 1
            self.ships.append(s)
            self.ai_controllers.append(AIController(s, self.grid, 0))

        self.projectiles = []
        self.beams = []
        self.state = BATTLE
        self.camera.fit_objects(self.ships)

    def update_battle(self, dt, events):
        self.camera.update_input(dt, events)
        
        # 1. Update Grid
        self.grid.clear()
        alive_ships = [s for s in self.ships if s.is_alive]
        for s in alive_ships:
            self.grid.insert(s)
            
        # 2. Update AI & Ships
        for ai in self.ai_controllers:
            ai.update(dt)
            
        for s in self.ships:
            s.update(dt)
        
        # 3. Process Attacks
        new_attacks = []
        for s in alive_ships:
            attacks = s.fire_weapons()
            if attacks:
                new_attacks.extend(attacks)
            
        for attack in new_attacks:
            if attack['type'] == 'projectile':
                self.projectiles.append(attack)
            elif attack['type'] == 'beam':
                # Beam Logic
                start_pos = attack['origin']
                direction = attack['direction']
                max_range = attack['range']
                target = attack.get('target')
                
                end_pos = start_pos + direction * max_range
                
                if target and target.is_alive:
                     # Raycast against this specific target
                    f = start_pos - target.position
                    
                    a = direction.dot(direction)
                    b = 2 * f.dot(direction)
                    c = f.dot(f) - 40**2 
                    
                    discriminant = b*b - 4*a*c
                    hit_dist = 0
                    hit = False
                    
                    if discriminant >= 0:
                        t1 = (-b - math.sqrt(discriminant)) / (2*a)
                        t2 = (-b + math.sqrt(discriminant)) / (2*a)
                        
                        valid_t = []
                        if 0 <= t1 <= max_range: valid_t.append(t1)
                        if 0 <= t2 <= max_range: valid_t.append(t2)
                        
                        if valid_t:
                            hit_dist = min(valid_t)
                            hit = True
                            
                    if hit:
                        beam_comp = attack['component']
                        chance = beam_comp.calculate_hit_chance(hit_dist)
                        # Fixed size mod
                        final_chance = chance
                        
                        if random.random() < final_chance:
                            target.take_damage(attack['damage'])
                            end_pos = start_pos + direction * hit_dist
                            # print(f"Beam HIT!")

                self.beams.append({
                    'start': start_pos,
                    'end': end_pos,
                    'timer': 0.2, 
                    'color': (100, 255, 255)
                })

        # Update Projectiles
        for p in self.projectiles[:]:
            p['pos'] += p['vel'] * dt
            p['distance_traveled'] += p['vel'].length() * dt
            
            # Optimization: Only check target
            target = p.get('target')
            
            hit = False
            if target and target.is_alive:
                 if p['pos'].distance_to(target.position) < 40:
                    target.take_damage(p['damage'])
                    hit = True
            
            if hit or p['distance_traveled'] > p['range']:
                if p in self.projectiles:
                    self.projectiles.remove(p)
        
        # Update Beams (Visuals)
        for b in self.beams[:]:
            b['timer'] -= dt
            if b['timer'] <= 0:
                self.beams.remove(b)

    def draw_battle(self):
        self.screen.fill(BG_COLOR)
        
        # Grid
        grid_spacing = 5000
        sw, sh = self.screen.get_size()
        
        tl = self.camera.screen_to_world((0, 0))
        br = self.camera.screen_to_world((sw, sh))
        
        start_x = int(tl.x // grid_spacing) * grid_spacing
        end_x = int(br.x // grid_spacing + 1) * grid_spacing
        start_y = int(tl.y // grid_spacing) * grid_spacing
        end_y = int(br.y // grid_spacing + 1) * grid_spacing
        
        grid_color = (30, 30, 50)
        
        for x in range(start_x, end_x + grid_spacing, grid_spacing):
            p1 = self.camera.world_to_screen(pygame.math.Vector2(x, start_y))
            p2 = self.camera.world_to_screen(pygame.math.Vector2(x, end_y))
            pygame.draw.line(self.screen, grid_color, p1, p2, 1)
            
        for y in range(start_y, end_y + grid_spacing, grid_spacing):
            p1 = self.camera.world_to_screen(pygame.math.Vector2(start_x, y))
            p2 = self.camera.world_to_screen(pygame.math.Vector2(end_x, y))
            pygame.draw.line(self.screen, grid_color, p1, p2, 1)

        for s in self.ships:
            draw_ship(self.screen, s, self.camera)
            if s.is_alive:
                pos = self.camera.world_to_screen(s.position)
                if s.max_hp > 0:
                    draw_bar(self.screen, pos.x - 20, pos.y - 60, 40, 5, s.hp / s.max_hp, (0, 255, 0))
        
        for p in self.projectiles:
            start = self.camera.world_to_screen(p['pos'])
            vel_norm = p['vel'].normalize() if p['vel'].length() > 0 else pygame.math.Vector2(1,0)
            end = self.camera.world_to_screen(p['pos'] - vel_norm * 10)
            pygame.draw.line(self.screen, (255, 255, 0), start, end, 2)
            
        for b in self.beams:
            alpha = int(255 * (b['timer'] / 0.2))
            color = b['color'] 
            start = self.camera.world_to_screen(b['start'])
            end = self.camera.world_to_screen(b['end'])
            pygame.draw.line(self.screen, color, start, end, max(1, int(3 * self.camera.zoom)))
            
        # Draw HUD
        s1_live = sum(1 for s in self.ships if s.team_id == 0 and s.is_alive)
        s2_live = sum(1 for s in self.ships if s.team_id == 1 and s.is_alive)
        
        self.screen.blit(font_med.render(f"Team 1: {s1_live}", True, (100, 200, 255)), (10, 10))
        self.screen.blit(font_med.render(f"Team 2: {s2_live}", True, (255, 100, 100)), (sw - 150, 10))

    def run(self):
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0
            
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.VIDEORESIZE:
                    self.camera.width = event.w
                    self.camera.height = event.h
                    # Update menu buttons position?
                    if self.state == MENU:
                         self.menu_buttons[0].rect.center = (event.w//2, event.h//2 - 50)
                         self.menu_buttons[1].rect.center = (event.w//2, event.h//2 + 20)
                
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
                self.update_battle(dt, events)
                self.draw_battle()
                
            pygame.display.flip()
        
        pygame.quit()

if __name__ == "__main__":
    game = Game()
    game.run()
