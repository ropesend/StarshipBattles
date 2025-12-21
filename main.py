import pygame
import time
import math
import random
import json
from ship import Ship, LayerType
from ai import AIController
from spatial import SpatialGrid
from designs import create_brick, create_interceptor
from components import load_components, load_modifiers, Bridge, Weapon, Engine, Thruster, Armor, Tank
from ui import Button
from builder_gui import BuilderSceneGUI
from sprites import SpriteManager

# Constants
WIDTH, HEIGHT = 3840, 2160
FPS = 60
FIXED_DT = 1.0 / 60.0  # Fixed simulation timestep for determinism
BG_COLOR = (10, 10, 20)

LAYER_COLORS = {
    LayerType.ARMOR: (100, 100, 100),
    LayerType.OUTER: (200, 50, 50),
    LayerType.INNER: (50, 50, 200),
    LayerType.CORE: (220, 220, 220)
}

# Ship Stats Panel (replaces Tkinter inspector popups)
# Panel state initialized in start_battle()


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
    
    # Use ship's calculated radius (based on actual mass)
    base_radius = ship.radius
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
BATTLE_SETUP = 3

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
        comp_path = os.path.join(base_path, "data", "components.json")
        load_components(comp_path)
        mod_path = os.path.join(base_path, "data", "modifiers.json")
        load_modifiers(mod_path)
        
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
            Button(WIDTH//2 - 100, HEIGHT//2 - 50, 200, 50, "Ship Builder", self.start_builder),
            Button(WIDTH//2 - 100, HEIGHT//2 + 20, 200, 50, "Battle Setup", self.start_battle_setup)
        ]
        
        # Builder (using pygame_gui)
        self.builder_scene = BuilderSceneGUI(WIDTH, HEIGHT, self.on_builder_return)
        
        # Camera
        self.camera = Camera(WIDTH, HEIGHT)
        
        # Spatial Grid
        self.grid = SpatialGrid(cell_size=2000)
        self.ships = []
        self.ai_controllers = []
        
        # Debug Overlay
        self.show_overlay = False
        
        # Simulation Speed Control
        self.sim_speed_multiplier = 1.0  # 1.0 = max speed, lower = slower
        self.sim_paused = False
        self.sim_tick_counter = 0  # For throttling UI updates
        
        # Ship Stats Panel (integrated, replaces Tkinter popups)
        self.stats_panel_width = 350
        self.expanded_ships = set()  # Ships currently expanded in panel
        self.stats_scroll_offset = 0

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
        self.builder_scene = BuilderSceneGUI(WIDTH, HEIGHT, self.on_builder_return)

    def on_builder_return(self, custom_ship=None):
        """Return from builder to main menu."""
        self.state = MENU
        
    def scan_ship_designs(self):
        """Scan for available ship design JSON files."""
        import os
        import glob
        base_path = os.path.dirname(os.path.abspath(__file__))
        json_files = glob.glob(os.path.join(base_path, "*.json"))
        
        designs = []
        for filepath in json_files:
            filename = os.path.basename(filepath)
            # Skip config files
            if filename in ['builder_theme.json', 'component_presets.json']:
                continue
            # Try to load and verify it's a ship design
            try:
                with open(filepath, 'r') as f:
                    data = json.load(f)
                if 'name' in data and 'layers' in data:
                    designs.append({
                        'path': filepath,
                        'name': data.get('name', filename),
                        'ship_class': data.get('ship_class', 'Unknown'),
                        'ai_strategy': data.get('ai_strategy', 'optimal_firing_range')
                    })
            except:
                pass
        return designs
    
    def start_battle_setup(self):
        """Enter battle setup screen."""
        self.state = BATTLE_SETUP
        self.available_ship_designs = self.scan_ship_designs()
        self.setup_team1 = []  # List of {'design': design_dict, 'strategy': str}
        self.setup_team2 = []
        self.setup_scroll_offset = 0
        
        # Import AI strategies
        from ai import COMBAT_STRATEGIES
        self.ai_strategies = list(COMBAT_STRATEGIES.keys())
    
    def update_battle_setup(self, events):
        """Handle battle setup screen input."""
        from ai import COMBAT_STRATEGIES
        
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos
                sw, sh = self.screen.get_size()
                
                # Column positions
                col1_x = 50  # Available ships
                col2_x = sw // 3 + 50  # Team 1
                col3_x = 2 * sw // 3 + 50  # Team 2
                
                # Check available ships list (left column)
                if col1_x <= mx < col1_x + 250:
                    for i, design in enumerate(self.available_ship_designs):
                        y = 150 + i * 40
                        if y <= my < y + 35:
                            # Click on ship design
                            if event.button == 1:  # Left click - add to team 1
                                self.setup_team1.append({
                                    'design': design,
                                    'strategy': design.get('ai_strategy', 'optimal_firing_range')
                                })
                            elif event.button == 3:  # Right click - add to team 2
                                self.setup_team2.append({
                                    'design': design,
                                    'strategy': design.get('ai_strategy', 'optimal_firing_range')
                                })
                            break
                
                # Check team 1 remove buttons
                if col2_x <= mx < col2_x + 300:
                    for i, entry in enumerate(self.setup_team1):
                        y = 150 + i * 60
                        # Remove button (X)
                        if y + 25 <= my < y + 50 and mx >= col2_x + 200:
                            self.setup_team1.pop(i)
                            break
                        # Cycle strategy on click
                        if y <= my < y + 25:
                            current_idx = self.ai_strategies.index(entry['strategy']) if entry['strategy'] in self.ai_strategies else 0
                            entry['strategy'] = self.ai_strategies[(current_idx + 1) % len(self.ai_strategies)]
                            break
                
                # Check team 2 remove buttons
                if col3_x <= mx < col3_x + 300:
                    for i, entry in enumerate(self.setup_team2):
                        y = 150 + i * 60
                        # Remove button
                        if y + 25 <= my < y + 50 and mx >= col3_x + 200:
                            self.setup_team2.pop(i)
                            break
                        # Cycle strategy
                        if y <= my < y + 25:
                            current_idx = self.ai_strategies.index(entry['strategy']) if entry['strategy'] in self.ai_strategies else 0
                            entry['strategy'] = self.ai_strategies[(current_idx + 1) % len(self.ai_strategies)]
                            break
                
                # Begin Battle button
                btn_y = sh - 80
                if sw // 2 - 100 <= mx < sw // 2 + 100 and btn_y <= my < btn_y + 50:
                    if self.setup_team1 and self.setup_team2:
                        self.start_battle_from_setup()
                
                # Return button
                if sw // 2 + 120 <= mx < sw // 2 + 240 and btn_y <= my < btn_y + 50:
                    self.state = MENU
    
    def draw_battle_setup(self):
        """Draw battle setup screen."""
        from ai import COMBAT_STRATEGIES
        
        self.screen.fill((20, 25, 35))
        sw, sh = self.screen.get_size()
        
        # Title
        title_font = pygame.font.Font(None, 64)
        title = title_font.render("BATTLE SETUP", True, (200, 200, 255))
        self.screen.blit(title, (sw // 2 - title.get_width() // 2, 30))
        
        label_font = pygame.font.Font(None, 36)
        item_font = pygame.font.Font(None, 28)
        
        col1_x = 50
        col2_x = sw // 3 + 50
        col3_x = 2 * sw // 3 + 50
        
        # Available Ships (left column)
        lbl = label_font.render("Available Ships (L/R click to add)", True, (150, 150, 200))
        self.screen.blit(lbl, (col1_x, 110))
        
        for i, design in enumerate(self.available_ship_designs):
            y = 150 + i * 40
            text = item_font.render(f"{design['name']} ({design['ship_class']})", True, (200, 200, 200))
            pygame.draw.rect(self.screen, (40, 45, 55), (col1_x, y, 250, 35))
            pygame.draw.rect(self.screen, (80, 80, 100), (col1_x, y, 250, 35), 1)
            self.screen.blit(text, (col1_x + 10, y + 8))
        
        # Team 1 (middle column)
        lbl = label_font.render("Team 1 (click to change AI)", True, (100, 200, 255))
        self.screen.blit(lbl, (col2_x, 110))
        
        for i, entry in enumerate(self.setup_team1):
            y = 150 + i * 60
            design = entry['design']
            strategy = entry['strategy']
            strat_name = COMBAT_STRATEGIES.get(strategy, {}).get('name', strategy)
            
            pygame.draw.rect(self.screen, (30, 50, 70), (col2_x, y, 280, 55))
            pygame.draw.rect(self.screen, (100, 150, 200), (col2_x, y, 280, 55), 1)
            
            name_text = item_font.render(design['name'], True, (255, 255, 255))
            strat_text = item_font.render(f"AI: {strat_name}", True, (150, 200, 255))
            x_text = item_font.render("[X]", True, (255, 100, 100))
            
            self.screen.blit(name_text, (col2_x + 10, y + 5))
            self.screen.blit(strat_text, (col2_x + 10, y + 30))
            self.screen.blit(x_text, (col2_x + 240, y + 30))
        
        # Team 2 (right column)
        lbl = label_font.render("Team 2 (click to change AI)", True, (255, 100, 100))
        self.screen.blit(lbl, (col3_x, 110))
        
        for i, entry in enumerate(self.setup_team2):
            y = 150 + i * 60
            design = entry['design']
            strategy = entry['strategy']
            strat_name = COMBAT_STRATEGIES.get(strategy, {}).get('name', strategy)
            
            pygame.draw.rect(self.screen, (70, 30, 30), (col3_x, y, 280, 55))
            pygame.draw.rect(self.screen, (200, 100, 100), (col3_x, y, 280, 55), 1)
            
            name_text = item_font.render(design['name'], True, (255, 255, 255))
            strat_text = item_font.render(f"AI: {strat_name}", True, (255, 150, 150))
            x_text = item_font.render("[X]", True, (255, 100, 100))
            
            self.screen.blit(name_text, (col3_x + 10, y + 5))
            self.screen.blit(strat_text, (col3_x + 10, y + 30))
            self.screen.blit(x_text, (col3_x + 240, y + 30))
        
        # Buttons at bottom
        btn_y = sh - 80
        
        # Begin Battle button
        btn_color = (50, 150, 50) if (self.setup_team1 and self.setup_team2) else (50, 50, 50)
        pygame.draw.rect(self.screen, btn_color, (sw // 2 - 100, btn_y, 200, 50))
        pygame.draw.rect(self.screen, (100, 200, 100), (sw // 2 - 100, btn_y, 200, 50), 2)
        btn_text = label_font.render("BEGIN BATTLE", True, (255, 255, 255))
        self.screen.blit(btn_text, (sw // 2 - btn_text.get_width() // 2, btn_y + 12))
        
        # Return button
        pygame.draw.rect(self.screen, (80, 80, 80), (sw // 2 + 120, btn_y, 120, 50))
        pygame.draw.rect(self.screen, (150, 150, 150), (sw // 2 + 120, btn_y, 120, 50), 2)
        ret_text = label_font.render("RETURN", True, (200, 200, 200))
        self.screen.blit(ret_text, (sw // 2 + 180 - ret_text.get_width() // 2, btn_y + 12))
    
    def start_battle_from_setup(self):
        """Start battle using ships selected in battle setup."""
        team1_ships = []
        for i, entry in enumerate(self.setup_team1):
            with open(entry['design']['path'], 'r') as f:
                data = json.load(f)
            ship = Ship.from_dict(data)
            ship.position = pygame.math.Vector2(20000, 30000 + i * 5000)
            ship.ai_strategy = entry['strategy']
            ship.recalculate_stats()
            team1_ships.append(ship)
        
        team2_ships = []
        for i, entry in enumerate(self.setup_team2):
            with open(entry['design']['path'], 'r') as f:
                data = json.load(f)
            ship = Ship.from_dict(data)
            ship.position = pygame.math.Vector2(80000, 30000 + i * 5000)
            ship.angle = 180
            ship.ai_strategy = entry['strategy']
            ship.recalculate_stats()
            team2_ships.append(ship)
        
        self.start_battle(team1_ships, team2_ships)
    def start_battle(self, team1_list, team2_list, seed=None):
        """Start a battle between two teams.
        
        Args:
            team1_list: List of ships for team 1
            team2_list: List of ships for team 2
            seed: Optional RNG seed for reproducible/deterministic battles
        """
        # Seed RNG for deterministic battles if specified
        if seed is not None:
            random.seed(seed)
            
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

    def update_battle(self, dt, events, camera_dt=None):
        # Use separate camera_dt for smooth camera movement
        self.camera.update_input(camera_dt if camera_dt else dt, events)
        
        self.sim_tick_counter += 1
        
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
            # We don't force fire here anymore. 
            # Ship.update() handles firing if trigger is pulled.
            # We just collect the results.
            if hasattr(s, 'just_fired_projectiles') and s.just_fired_projectiles:
                new_attacks.extend(s.just_fired_projectiles)
                s.just_fired_projectiles = [] # Clear buffer
            
        for attack in new_attacks:
            if attack['type'] == 'projectile':
                self.projectiles.append({
                    'pos': attack['position'],
                    'vel': attack['velocity'],
                    'damage': attack['damage'],
                    'range': attack['range'],
                    'distance_traveled': 0,
                    'owner': attack['source'],
                    'radius': 3,
                    'color': attack.get('color', (255, 255, 0))
                })
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
                    # Use actual target radius + tolerance? Or just radius.
                    c = f.dot(f) - target.radius**2 
                    
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

        # Ship-to-Ship Collisions (Ramming)
        # Only check ships in 'kamikaze' mode against their specific target
        for s in self.ships:
            if not s.is_alive: continue
            if getattr(s, 'ai_strategy', '') != 'kamikaze': continue
            
            target = s.current_target
            if not target or not target.is_alive: continue
            
            # Check collision with target only
            collision_radius = s.radius + target.radius
            
            if s.position.distance_to(target.position) < collision_radius:
                # Ramming collision!
                hp_rammer = s.hp
                hp_target = target.hp
                
                if hp_rammer < hp_target:
                    # Rammer is weaker -> destroyed
                    # Target takes 50% of rammer's remaining HP as damage
                    s.take_damage(hp_rammer + 9999)
                    target.take_damage(hp_rammer * 0.5)
                    print(f"Ramming: {s.name} destroyed by {target.name}! ({target.name} took {hp_rammer * 0.5:.0f} damage)")
                elif hp_target < hp_rammer:
                    # Target is weaker -> destroyed
                    # Rammer takes 50% of target's remaining HP as damage
                    target.take_damage(hp_target + 9999)
                    s.take_damage(hp_target * 0.5)
                    print(f"Ramming: {target.name} destroyed by {s.name}! ({s.name} took {hp_target * 0.5:.0f} damage)")
                else:
                    # Equal HP - both die
                    s.take_damage(hp_rammer + 9999)
                    target.take_damage(hp_target + 9999)
                    print(f"Ramming: Mutual destruction between {s.name} and {target.name}!")

        # Update Projectiles
        # Pre-calculate ship states for CCD
        ship_states = []
        for s in self.ships:
            if not s.is_alive: continue
            # Ship is at t1. Backtrack to t0.
            s_vel = s.velocity
            s_pos_t1 = s.position
            s_pos_t0 = s_pos_t1 - s_vel * dt
            ship_states.append({
                'ship': s,
                'pos_t0': s_pos_t0,
                'vel': s_vel,
                'team_id': s.team_id,
                'radius': s.radius
            })

        # Optimized projectile update using set for removal tracking
        projectiles_to_remove = set()
        
        for idx, p in enumerate(self.projectiles):
            if idx in projectiles_to_remove:
                continue
                
            p_pos_t0 = p['pos']
            p_vel = p['vel']
            p_vel_length = p_vel.length()  # Cache this calculation
            p_pos_t1 = p_pos_t0 + p_vel * dt
            
            hit_occurred = False
            
            # Use spatial grid for broad-phase collision detection
            # Query ships near the projectile's path (use midpoint + buffer)
            query_pos = (p_pos_t0 + p_pos_t1) * 0.5
            query_radius = p_vel_length * dt + 100  # Path length + buffer
            nearby_ships = self.grid.query_radius(query_pos, query_radius)
            
            for s in nearby_ships:
                if not s.is_alive: continue
                if s.team_id == p['owner'].team_id: continue  # No friendly fire
                
                # Continuous Collision Detection (CCD)
                s_vel = s.velocity
                s_pos_t1 = s.position
                s_pos_t0 = s_pos_t1 - s_vel * dt
                
                D0 = p_pos_t0 - s_pos_t0
                DV = p_vel - s_vel
                
                dv_sq = DV.dot(DV)
                collision_radius = s.radius + 5
                
                hit = False
                
                if dv_sq == 0:
                    if D0.length() < collision_radius:
                        hit = True
                else:
                    t = -D0.dot(DV) / dv_sq
                    t_clamped = max(0, min(t, dt))
                    
                    p_at_t = p_pos_t0 + p_vel * t_clamped
                    s_at_t = s_pos_t0 + s_vel * t_clamped
                    
                    if p_at_t.distance_to(s_at_t) < collision_radius:
                        hit = True
                        
                if hit:
                    s.take_damage(p['damage'])
                    hit_occurred = True
                    break
            
            if hit_occurred:
                projectiles_to_remove.add(idx)
            else:
                p['pos'] = p_pos_t1
                p['distance_traveled'] += p_vel_length * dt
                
                if p['distance_traveled'] > p['range']:
                    projectiles_to_remove.add(idx)
        
        # Batch remove projectiles using list comprehension (O(N) instead of O(N^2))
        if projectiles_to_remove:
            self.projectiles = [p for i, p in enumerate(self.projectiles) if i not in projectiles_to_remove]
        
        # Update Beams - decrement timers and filter expired
        for b in self.beams:
            b['timer'] -= dt
        self.beams = [b for b in self.beams if b['timer'] > 0]

    def draw_debug_overlay(self):
        for s in self.ships:
            if not s.is_alive: continue
            
            # 1. Target Line
            if s.current_target and s.current_target.is_alive:
                start = self.camera.world_to_screen(s.position)
                end = self.camera.world_to_screen(s.current_target.position)
                pygame.draw.line(self.screen, (0, 0, 255), start, end, 1)
                
            # 2. Weapon Range
            # Find max weapon range
            max_range = 0
            for layer in s.layers.values():
                for comp in layer['components']:
                    if isinstance(comp, Weapon) and comp.is_active:
                        if comp.range > max_range:
                            max_range = comp.range
            
            if max_range > 0:
                # Convert radius to screen space
                r_screen = int(max_range * self.camera.zoom)
                if r_screen > 0:
                    center = self.camera.world_to_screen(s.position)
                    pygame.draw.circle(self.screen, (100, 100, 100), (int(center.x), int(center.y)), r_screen, 1)

            # 3. Aim Point (Blue X)
            if hasattr(s, 'aim_point') and s.aim_point:
                 aim_pos_screen = self.camera.world_to_screen(s.aim_point)
                 # Draw Blue X
                 length = 5
                 color = (0, 100, 255)
                 pygame.draw.line(self.screen, color, (aim_pos_screen.x - length, aim_pos_screen.y - length), (aim_pos_screen.x + length, aim_pos_screen.y + length), 2)
                 pygame.draw.line(self.screen, color, (aim_pos_screen.x - length, aim_pos_screen.y + length), (aim_pos_screen.x + length, aim_pos_screen.y - length), 2)

            # 4. Firing Arcs
            center = self.camera.world_to_screen(s.position)
            for layer in s.layers.values():
                for comp in layer['components']:
                    if isinstance(comp, Weapon) and comp.is_active:
                        # Angle Logic
                        ship_angle = s.angle
                        facing = comp.facing_angle
                        arc = comp.firing_arc
                        rng = comp.range * self.camera.zoom
                        
                        start_angle = math.radians(ship_angle + facing - arc)
                        end_angle = math.radians(ship_angle + facing + arc)
                        
                        # Draw Arc Lines
                        # Center to Start
                        x1 = center.x + math.cos(start_angle) * rng
                        y1 = center.y + math.sin(start_angle) * rng
                        
                        x2 = center.x + math.cos(end_angle) * rng
                        y2 = center.y + math.sin(end_angle) * rng
                        
                        # Color based on trigger status?
                        arc_col = (255, 165, 0) # Orange
                        
                        pygame.draw.line(self.screen, arc_col, center, (x1, y1), 1)
                        pygame.draw.line(self.screen, arc_col, center, (x2, y2), 1)
                        # Maybe draw a small arc connecting them?
                        rect = pygame.Rect(center.x - rng, center.y - rng, rng*2, rng*2)
                        # Pygame arc takes radians but negated for screen coords? 
                        # Pygame arc angles are in degrees, 0 is right, CCW?
                        # ship.angle is usually degrees.
                        # Convert to Pygame angles (-degrees)
                        # import math - REMOVED
                        deg_start = -(ship_angle + facing + arc)
                        deg_end = -(ship_angle + facing - arc)
                        
                        try:
                            # Pygame arc angles are in degrees, 0 is right, CCW
                            # start_angle (radians) is clockwise from right?
                            # pygame.draw.arc: start_angle, stop_angle in radians.
                            # Standard cartesian: 0 right, PI/2 up (in pygame Y is down, so PI/2 is down?)
                            # Actually in pygame:
                            # 0 is right (positive X)
                            # PI/2 is bottom (positive Y)
                            # PI is left
                            # 3*PI/2 is top
                            
                            # Our angle system: 0 is right (1,0). Y is down. Same.
                            # ship.angle is degrees.
                            
                            r_start = math.radians(ship_angle + facing - arc)
                            r_end = math.radians(ship_angle + facing + arc)
                            
                            # Pygame requires start < stop? No, just radians.
                            # But it draws counter-clockwise from start to stop.
                            # If we want -arc to +arc (clockwise? no, angle increases clockwise in screen coords?)
                            # Wait, in standard math, angle increases CCW. In screen (Y down), angle increases CW?
                            # math.cos(0.1) -> x>0, y>0? 
                            # If y is down, y>0 is down. So 0.1 rad is down-right.
                            # So angles increase Clockwise.
                            
                            # We want to draw from (angle - arc) to (angle + arc).
                            # If we draw from (angle - arc) to (angle + arc), we get the wedge.
                            
                            pygame.draw.arc(self.screen, arc_col, rect, -r_end, -r_start, 1) 
                            # Note: pygame.draw.arc uses standard cartesian (Y up) for angles? 
                            # Or just normal radians but Y is flipped?
                            # Usually simple line drawing is safer.
                            
                        except:
                            pass

    def handle_stats_panel_click(self, mx, my, button):
        """Handle mouse clicks on the ship stats panel."""
        sw, sh = self.screen.get_size()
        panel_x = sw - self.stats_panel_width
        
        # Only handle clicks in panel area
        if mx < panel_x:
            return False
        
        # Calculate relative position in panel
        rel_x = mx - panel_x
        rel_y = my + self.stats_scroll_offset  # Scroll-adjusted y position
        
        print(f"DEBUG CLICK: mouse=({mx},{my}), panel_x={panel_x}, rel_y={rel_y}, scroll={self.stats_scroll_offset}")
        
        # Build list of ships in display order
        team1_ships = [s for s in self.ships if s.team_id == 0]
        team2_ships = [s for s in self.ships if s.team_id == 1]
        
        y_pos = 10  # Panel starts at y=10
        
        # Team 1 header
        y_pos += 30
        print(f"DEBUG: After Team 1 header, y_pos={y_pos}")
        
        for ship in team1_ships:
            banner_height = 25
            print(f"DEBUG: Ship '{ship.name}' banner range: {y_pos} to {y_pos + banner_height}, rel_y={rel_y}")
            if y_pos <= rel_y < y_pos + banner_height:
                # Clicked on ship banner - toggle expansion
                print(f"DEBUG: HIT! Toggling ship '{ship.name}'")
                if ship in self.expanded_ships:
                    self.expanded_ships.discard(ship)
                else:
                    self.expanded_ships.add(ship)
                return True
            y_pos += banner_height
            
            if ship in self.expanded_ships:
                # Skip over expanded content
                exp_height = self._get_expanded_height(ship)
                print(f"DEBUG: Ship '{ship.name}' is expanded, adding {exp_height} to y_pos")
                y_pos += exp_height
        
        # Team 2 header
        y_pos += 15  # Gap between teams
        y_pos += 30  # Team 2 header
        print(f"DEBUG: After Team 2 header, y_pos={y_pos}")
        
        for ship in team2_ships:
            banner_height = 25
            print(f"DEBUG: Ship '{ship.name}' banner range: {y_pos} to {y_pos + banner_height}, rel_y={rel_y}")
            if y_pos <= rel_y < y_pos + banner_height:
                print(f"DEBUG: HIT! Toggling ship '{ship.name}'")
                if ship in self.expanded_ships:
                    self.expanded_ships.discard(ship)
                else:
                    self.expanded_ships.add(ship)
                return True
            y_pos += banner_height
            
            if ship in self.expanded_ships:
                exp_height = self._get_expanded_height(ship)
                print(f"DEBUG: Ship '{ship.name}' is expanded, adding {exp_height} to y_pos")
                y_pos += exp_height
        
        print(f"DEBUG: No hit, final y_pos={y_pos}")
        return False
    
    def _get_expanded_height(self, ship):
        """Calculate height needed for expanded ship stats."""
        # Base stats: 6 lines (HP, Fuel, Energy, Ammo, Speed, Target)
        base_height = 6 * 18
        # Components: count all components
        comp_count = sum(len(l['components']) for l in ship.layers.values())
        comp_height = comp_count * 16 + 20  # +20 for header
        return base_height + comp_height + 10  # +10 padding
    
    def _draw_bar(self, surface, x, y, width, height, pct, color):
        """Draw a progress bar."""
        pygame.draw.rect(surface, (40, 40, 40), (x, y, width, height))
        if pct > 0:
            fill_w = int(width * min(1.0, pct))
            pygame.draw.rect(surface, color, (x, y, fill_w, height))
        pygame.draw.rect(surface, (80, 80, 80), (x, y, width, height), 1)
    
    def draw_ship_stats_panel(self):
        """Draw the integrated ship stats panel on the right side."""
        sw, sh = self.screen.get_size()
        panel_x = sw - self.stats_panel_width
        panel_w = self.stats_panel_width
        
        # Panel background
        panel_surf = pygame.Surface((panel_w, sh), pygame.SRCALPHA)
        panel_surf.fill((20, 25, 35, 230))
        
        font_title = pygame.font.Font(None, 28)
        font_name = pygame.font.Font(None, 22)
        font_stat = pygame.font.Font(None, 18)
        
        y = 10 - self.stats_scroll_offset
        
        # Team 1
        team1_ships = [s for s in self.ships if s.team_id == 0]
        team1_alive = sum(1 for s in team1_ships if s.is_alive)
        
        title = font_title.render(f"TEAM 1 ({team1_alive}/{len(team1_ships)})", True, (100, 200, 255))
        panel_surf.blit(title, (10, y))
        y += 30
        
        for ship in team1_ships:
            # Ship banner
            arrow = "▼" if ship in self.expanded_ships else "►"
            status = "" if ship.is_alive else " [DEAD]"
            color = (200, 200, 200) if ship.is_alive else (100, 100, 100)
            banner_color = (40, 60, 80) if ship.is_alive else (40, 40, 40)
            
            pygame.draw.rect(panel_surf, banner_color, (5, y, panel_w - 10, 22))
            name_text = font_name.render(f"{arrow} {ship.name}{status}", True, color)
            panel_surf.blit(name_text, (10, y + 3))
            y += 25
            
            if ship in self.expanded_ships:
                y = self._draw_ship_details(panel_surf, ship, y, panel_w, font_stat)
        
        y += 15
        
        # Team 2
        team2_ships = [s for s in self.ships if s.team_id == 1]
        team2_alive = sum(1 for s in team2_ships if s.is_alive)
        
        title = font_title.render(f"TEAM 2 ({team2_alive}/{len(team2_ships)})", True, (255, 100, 100))
        panel_surf.blit(title, (10, y))
        y += 30
        
        for ship in team2_ships:
            arrow = "▼" if ship in self.expanded_ships else "►"
            status = "" if ship.is_alive else " [DEAD]"
            color = (200, 200, 200) if ship.is_alive else (100, 100, 100)
            banner_color = (80, 40, 40) if ship.is_alive else (40, 40, 40)
            
            pygame.draw.rect(panel_surf, banner_color, (5, y, panel_w - 10, 22))
            name_text = font_name.render(f"{arrow} {ship.name}{status}", True, color)
            panel_surf.blit(name_text, (10, y + 3))
            y += 25
            
            if ship in self.expanded_ships:
                y = self._draw_ship_details(panel_surf, ship, y, panel_w, font_stat)
        
        # Store total content height for scrolling
        self._stats_panel_content_height = y + self.stats_scroll_offset
        
        # Blit panel to screen
        self.screen.blit(panel_surf, (panel_x, 0))
        
        # Draw border
        pygame.draw.line(self.screen, (60, 60, 80), (panel_x, 0), (panel_x, sh), 2)
    
    def _draw_ship_details(self, surface, ship, y, panel_w, font):
        """Draw expanded ship details. Returns new y position."""
        x_indent = 20
        bar_w = 120
        bar_h = 10
        
        # HP Bar
        hp_pct = ship.hp / ship.max_hp if ship.max_hp > 0 else 0
        hp_color = (0, 255, 0) if hp_pct > 0.5 else ((255, 200, 0) if hp_pct > 0.2 else (255, 50, 50))
        text = font.render(f"HP: {int(ship.hp)}/{int(ship.max_hp)}", True, (180, 180, 180))
        surface.blit(text, (x_indent, y))
        self._draw_bar(surface, x_indent + 100, y, bar_w, bar_h, hp_pct, hp_color)
        y += 16
        
        # Fuel Bar
        fuel_pct = ship.current_fuel / ship.max_fuel if ship.max_fuel > 0 else 0
        text = font.render(f"Fuel: {int(ship.current_fuel)}/{int(ship.max_fuel)}", True, (180, 180, 180))
        surface.blit(text, (x_indent, y))
        self._draw_bar(surface, x_indent + 100, y, bar_w, bar_h, fuel_pct, (255, 165, 0))
        y += 16
        
        # Energy Bar
        energy_pct = ship.current_energy / ship.max_energy if ship.max_energy > 0 else 0
        text = font.render(f"Energy: {int(ship.current_energy)}/{int(ship.max_energy)}", True, (180, 180, 180))
        surface.blit(text, (x_indent, y))
        self._draw_bar(surface, x_indent + 100, y, bar_w, bar_h, energy_pct, (100, 200, 255))
        y += 16
        
        # Ammo Bar
        ammo_pct = ship.current_ammo / ship.max_ammo if ship.max_ammo > 0 else 0
        text = font.render(f"Ammo: {int(ship.current_ammo)}/{int(ship.max_ammo)}", True, (180, 180, 180))
        surface.blit(text, (x_indent, y))
        self._draw_bar(surface, x_indent + 100, y, bar_w, bar_h, ammo_pct, (200, 200, 100))
        y += 16
        
        # Speed
        text = font.render(f"Speed: {ship.current_speed:.0f}/{ship.max_speed:.0f}", True, (180, 180, 180))
        surface.blit(text, (x_indent, y))
        y += 16
        
        # Target
        target_name = "None"
        if ship.current_target and ship.current_target.is_alive:
            target_name = ship.current_target.name
        text = font.render(f"Target: {target_name}", True, (180, 180, 180))
        surface.blit(text, (x_indent, y))
        y += 18
        
        # Components header
        text = font.render("Components:", True, (200, 200, 100))
        surface.blit(text, (x_indent, y))
        y += 16
        
        # Draw each component
        for layer_type in [LayerType.ARMOR, LayerType.OUTER, LayerType.INNER, LayerType.CORE]:
            for comp in ship.layers[layer_type]['components']:
                hp_pct = comp.current_hp / comp.max_hp if comp.max_hp > 0 else 1.0
                color = (150, 150, 150) if comp.is_active else (80, 80, 80)
                bar_color = (0, 200, 0) if hp_pct > 0.5 else ((200, 200, 0) if hp_pct > 0.2 else (200, 50, 50))
                if not comp.is_active:
                    bar_color = (60, 60, 60)
                
                # Truncate name if too long
                name = comp.name[:10] + ".." if len(comp.name) > 12 else comp.name
                # Show name and HP numerically
                hp_text = f"{int(comp.current_hp)}/{int(comp.max_hp)}"
                text = font.render(name, True, color)
                surface.blit(text, (x_indent + 5, y))
                hp_val = font.render(hp_text, True, color)
                surface.blit(hp_val, (x_indent + 95, y))
                self._draw_bar(surface, x_indent + 160, y, 60, 8, hp_pct, bar_color)
                y += 14
        
        y += 5  # Padding after components
        return y
                        
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
        
        # Draw Objects
        for p in self.projectiles:
             # simple line
             start = self.camera.world_to_screen(p['pos'] - p['vel'].normalize() * 10)
             end = self.camera.world_to_screen(p['pos'])
             pygame.draw.line(self.screen, (255, 255, 0), start, end, 2)
             
        for s in self.ships:
            draw_ship(self.screen, s, self.camera)
            
        # Beams
        for b in self.beams:
            start = self.camera.world_to_screen(b['start'])
            end = self.camera.world_to_screen(b['end'])
            pygame.draw.line(self.screen, b['color'], start, end, 3)

        # Debug overlay (if enabled)
        if self.show_overlay:
            self.draw_debug_overlay()
        
        # Ship Stats Panel (right side)
        self.draw_ship_stats_panel()
        
        # Check for battle end and show return button
        team1_alive = sum(1 for s in self.ships if s.team_id == 0 and s.is_alive)
        team2_alive = sum(1 for s in self.ships if s.team_id == 1 and s.is_alive)
        
        if team1_alive == 0 or team2_alive == 0:
            # Battle is over!
            sw, sh = self.screen.get_size()
            
            # Semi-transparent overlay
            overlay = pygame.Surface((sw - self.stats_panel_width, sh), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            self.screen.blit(overlay, (0, 0))
            
            # Winner text
            if team1_alive > 0:
                winner_text = "TEAM 1 WINS!"
                winner_color = (100, 200, 255)
            elif team2_alive > 0:
                winner_text = "TEAM 2 WINS!"
                winner_color = (255, 100, 100)
            else:
                winner_text = "DRAW!"
                winner_color = (200, 200, 200)
            
            win_font = pygame.font.Font(None, 72)
            win_surf = win_font.render(winner_text, True, winner_color)
            center_x = (sw - self.stats_panel_width) // 2
            self.screen.blit(win_surf, (center_x - win_surf.get_width() // 2, sh // 2 - 80))
            
            # Return to Battle Setup button
            btn_font = pygame.font.Font(None, 36)
            btn_w, btn_h = 250, 50
            btn_x = center_x - btn_w // 2
            btn_y = sh // 2
            
            pygame.draw.rect(self.screen, (50, 80, 120), (btn_x, btn_y, btn_w, btn_h))
            pygame.draw.rect(self.screen, (100, 150, 200), (btn_x, btn_y, btn_w, btn_h), 2)
            btn_text = btn_font.render("Return to Battle Setup", True, (255, 255, 255))
            self.screen.blit(btn_text, (btn_x + btn_w // 2 - btn_text.get_width() // 2, btn_y + 12))
            
            # Store button rect for click detection
            self.battle_end_button_rect = pygame.Rect(btn_x, btn_y, btn_w, btn_h)

    def run(self):
        accumulator = 0.0
        
        while self.running:
            frame_time = self.clock.tick(0) / 1000.0  # No FPS cap - run as fast as possible
            
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
                elif event.type == pygame.KEYDOWN:
                    if self.state == BATTLE:
                        if event.key == pygame.K_o:
                            self.show_overlay = not self.show_overlay
                        elif event.key == pygame.K_SPACE:
                            # Toggle pause
                            self.sim_paused = not self.sim_paused
                        elif event.key == pygame.K_COMMA:
                            # Slow down simulation
                            if not self.sim_paused:
                                self.sim_speed_multiplier = max(0.0625, self.sim_speed_multiplier / 2.0)
                        elif event.key == pygame.K_PERIOD:
                            # Speed up simulation
                            if not self.sim_paused:
                                self.sim_speed_multiplier = min(1.0, self.sim_speed_multiplier * 2.0)
                        elif event.key == pygame.K_SLASH:
                            # Reset to max speed
                            self.sim_speed_multiplier = 1.0
                            self.sim_paused = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if self.state == BATTLE:
                        mx, my = event.pos
                        # Check if battle is over and return button clicked
                        if hasattr(self, 'battle_end_button_rect') and self.battle_end_button_rect.collidepoint(mx, my):
                            self.start_battle_setup()
                        # Check if click is on stats panel
                        elif not self.handle_stats_panel_click(mx, my, event.button):
                            # Click was not on panel - could add other click handling here
                            pass
                elif event.type == pygame.MOUSEWHEEL:
                    if self.state == BATTLE:
                        # Scroll stats panel
                        mx, my = pygame.mouse.get_pos()
                        sw = self.screen.get_size()[0]
                        if mx >= sw - self.stats_panel_width:
                            self.stats_scroll_offset -= event.y * 30
                            # Clamp scroll
                            max_scroll = max(0, getattr(self, '_stats_panel_content_height', 0) - self.screen.get_size()[1] + 50)
                            self.stats_scroll_offset = max(0, min(max_scroll, self.stats_scroll_offset))
                
                if self.state == MENU:
                    for btn in self.menu_buttons:
                        btn.handle_event(event)
                elif self.state == BUILDER:
                    self.builder_scene.handle_event(event)
                elif self.state == BATTLE_SETUP:
                    self.update_battle_setup([event])
            
            # Logic & Draw
            if self.state == MENU:
                self.screen.fill((20, 20, 30))
                for btn in self.menu_buttons:
                    btn.draw(self.screen)
            elif self.state == BUILDER:
                self.builder_scene.update(frame_time)
                self.builder_scene.process_ui_time(frame_time)
                self.builder_scene.draw(self.screen)
            elif self.state == BATTLE_SETUP:
                self.draw_battle_setup()
            elif self.state == BATTLE:
                # Tick-based simulation - one physics step per frame
                # sim_speed_multiplier controls how many ticks per frame
                if not self.sim_paused:
                    # Run physics ticks based on speed multiplier
                    ticks_to_run = max(1, int(self.sim_speed_multiplier))
                    for _ in range(ticks_to_run):
                        self.update_battle(
                            1.0,  # Fixed dt=1.0 per tick (time-independent)
                            events if _ == 0 else [],
                            camera_dt=frame_time if _ == 0 else 0
                        )
                else:
                    # Still allow camera movement when paused
                    self.camera.update_input(frame_time, events)
                
                self.draw_battle()
                
                # Draw speed indicator
                speed_text = "PAUSED" if self.sim_paused else f"Speed: {self.sim_speed_multiplier:.2f}x"
                speed_color = (255, 100, 100) if self.sim_paused else (200, 200, 200)
                if self.sim_speed_multiplier < 1.0:
                    speed_color = (255, 200, 100)  # Orange for slowed
                self.screen.blit(font_med.render(speed_text, True, speed_color), (WIDTH//2 - 50, 10))
                
            pygame.display.flip()
        
        pygame.quit()

if __name__ == "__main__":
    game = Game()
    game.run()
