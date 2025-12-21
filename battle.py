"""Battle scene module for combat simulation and UI."""
import pygame
import math
import random
import time

from ship import LayerType
from ai import AIController, COMBAT_STRATEGIES
from spatial import SpatialGrid
from components import Weapon
from camera import Camera
from rendering import draw_ship, draw_bar


class BattleLogger:
    """Toggleable logger that writes battle events to file."""
    
    def __init__(self, filename="battle_log.txt", enabled=True):
        self.enabled = enabled
        self.filename = filename
        self.file = None
        
    def start_session(self):
        """Start a new logging session."""
        if self.enabled:
            self.file = open(self.filename, 'w')
            self.log("=== BATTLE LOG STARTED ===")
    
    def log(self, message):
        """Log a message if logging is enabled."""
        if self.enabled and self.file:
            self.file.write(f"{message}\n")
            self.file.flush()
    
    def close(self):
        """Close the log file."""
        if self.file:
            self.log("=== BATTLE LOG ENDED ===")
            self.file.close()
            self.file = None


# Global battle logger instance
BATTLE_LOG = BattleLogger(enabled=True)


class BattleScene:
    """Manages battle simulation, rendering, and UI."""
    
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # Battle state
        self.ships = []
        self.ai_controllers = []
        self.projectiles = []
        self.beams = []
        self.grid = SpatialGrid(cell_size=2000)
        
        # Camera
        self.camera = Camera(screen_width, screen_height)
        
        # Simulation
        self.sim_tick_counter = 0
        self.tick_rate_timer = 0.0
        self.tick_rate_count = 0
        self.current_tick_rate = 0
        self.sim_paused = False
        self.sim_speed_multiplier = 1.0
        
        # UI state
        self.stats_panel_width = 350
        self.expanded_ships = set()
        self.stats_scroll_offset = 0
        self._stats_panel_content_height = 0
        self.show_overlay = False
        
        # Headless mode
        self.headless_mode = False
        self.headless_start_time = None
        
        # Button rects for click detection
        self.battle_end_button_rect = None
        self.end_battle_early_rect = None
        
        # Actions for Game class
        self.action_return_to_setup = False
    
    def start(self, team1_ships, team2_ships, seed=None, headless=False):
        """Start a battle between two teams."""
        self.headless_mode = headless
        self.headless_start_time = None
        if headless:
            self.headless_start_time = time.time()
            print("\n=== STARTING HEADLESS BATTLE ===")
        
        if seed is not None:
            random.seed(seed)
        
        self.ships = []
        self.ai_controllers = []
        
        # Handle single ship args
        if not isinstance(team1_ships, list): team1_ships = [team1_ships]
        if not isinstance(team2_ships, list): team2_ships = [team2_ships]
        
        # Setup Team 1
        for s in team1_ships:
            s.team_id = 0
            self.ships.append(s)
            self.ai_controllers.append(AIController(s, self.grid, 1))
        
        # Setup Team 2
        for s in team2_ships:
            s.team_id = 1
            self.ships.append(s)
            self.ai_controllers.append(AIController(s, self.grid, 0))
        
        self.projectiles = []
        self.beams = []
        self.sim_tick_counter = 0
        self.expanded_ships = set()
        self.stats_scroll_offset = 0
        self.action_return_to_setup = False
        
        # Start logging
        BATTLE_LOG.start_session()
        BATTLE_LOG.log(f"Battle started: {len(team1_ships)} vs {len(team2_ships)} ships")
        
        if not headless:
            self.camera.fit_objects(self.ships)
    
    def update(self, dt, events, camera_dt=None):
        """Update battle simulation for one tick."""
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
            if hasattr(s, 'just_fired_projectiles') and s.just_fired_projectiles:
                new_attacks.extend(s.just_fired_projectiles)
                s.just_fired_projectiles = []
        
        for attack in new_attacks:
            if attack['type'] == 'projectile':
                BATTLE_LOG.log(f"Projectile fired at {attack['position']}")
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
                self._process_beam_attack(attack)
        
        # 4. Ship-to-Ship Collisions (Ramming)
        self._process_ramming()
        
        # 5. Update Projectiles
        self._update_projectiles(dt)
        
        # 6. Update Beams
        for b in self.beams:
            b['timer'] -= dt
        self.beams = [b for b in self.beams if b['timer'] > 0]
    
    def _process_beam_attack(self, attack):
        """Process a beam weapon attack."""
        start_pos = attack['origin']
        direction = attack['direction']
        max_range = attack['range']
        target = attack.get('target')
        
        end_pos = start_pos + direction * max_range
        
        if target and target.is_alive:
            f = start_pos - target.position
            a = direction.dot(direction)
            b = 2 * f.dot(direction)
            c = f.dot(f) - target.radius**2
            
            discriminant = b*b - 4*a*c
            
            if discriminant >= 0:
                t1 = (-b - math.sqrt(discriminant)) / (2*a)
                t2 = (-b + math.sqrt(discriminant)) / (2*a)
                
                valid_t = []
                if 0 <= t1 <= max_range: valid_t.append(t1)
                if 0 <= t2 <= max_range: valid_t.append(t2)
                
                if valid_t:
                    hit_dist = min(valid_t)
                    beam_comp = attack['component']
                    chance = beam_comp.calculate_hit_chance(hit_dist)
                    
                    if random.random() < chance:
                        target.take_damage(attack['damage'])
                        end_pos = start_pos + direction * hit_dist
        
        self.beams.append({
            'start': start_pos,
            'end': end_pos,
            'timer': 30,
            'color': (100, 255, 255)
        })
    
    def _process_ramming(self):
        """Process ship-to-ship ramming collisions."""
        for s in self.ships:
            if not s.is_alive: continue
            if getattr(s, 'ai_strategy', '') != 'kamikaze': continue
            
            target = s.current_target
            if not target or not target.is_alive: continue
            
            collision_radius = s.radius + target.radius
            
            if s.position.distance_to(target.position) < collision_radius:
                hp_rammer = s.hp
                hp_target = target.hp
                
                if hp_rammer < hp_target:
                    s.take_damage(hp_rammer + 9999)
                    target.take_damage(hp_rammer * 0.5)
                    BATTLE_LOG.log(f"Ramming: {s.name} destroyed by {target.name}!")
                elif hp_target < hp_rammer:
                    target.take_damage(hp_target + 9999)
                    s.take_damage(hp_target * 0.5)
                    BATTLE_LOG.log(f"Ramming: {target.name} destroyed by {s.name}!")
                else:
                    s.take_damage(hp_rammer + 9999)
                    target.take_damage(hp_target + 9999)
                    BATTLE_LOG.log(f"Ramming: Mutual destruction!")
    
    def _update_projectiles(self, dt):
        """Update projectile positions and check collisions."""
        projectiles_to_remove = set()
        
        for idx, p in enumerate(self.projectiles):
            if idx in projectiles_to_remove:
                continue
            
            p_pos_t0 = p['pos']
            p_vel = p['vel']
            p_vel_length = p_vel.length()
            p_pos_t1 = p_pos_t0 + p_vel * dt
            
            hit_occurred = False
            
            query_pos = (p_pos_t0 + p_pos_t1) * 0.5
            query_radius = p_vel_length * dt + 100
            nearby_ships = self.grid.query_radius(query_pos, query_radius)
            
            for s in nearby_ships:
                if not s.is_alive: continue
                if s.team_id == p['owner'].team_id: continue
                
                # CCD
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
        
        if projectiles_to_remove:
            self.projectiles = [p for i, p in enumerate(self.projectiles) if i not in projectiles_to_remove]
    
    def is_battle_over(self):
        """Check if the battle has ended."""
        team1_alive = sum(1 for s in self.ships if s.team_id == 0 and s.is_alive)
        team2_alive = sum(1 for s in self.ships if s.team_id == 1 and s.is_alive)
        return team1_alive == 0 or team2_alive == 0
    
    def get_winner(self):
        """Get the winning team. Returns 0, 1, or -1 for draw."""
        team1_alive = sum(1 for s in self.ships if s.team_id == 0 and s.is_alive)
        team2_alive = sum(1 for s in self.ships if s.team_id == 1 and s.is_alive)
        if team1_alive > 0 and team2_alive == 0:
            return 0
        elif team2_alive > 0 and team1_alive == 0:
            return 1
        return -1
    
    def draw(self, screen):
        """Draw the battle scene."""
        screen.fill((10, 10, 20))
        sw, sh = screen.get_size()
        
        # Draw grid
        self._draw_grid(screen)
        
        # Draw projectiles
        for p in self.projectiles:
            trail_length = 100
            start = self.camera.world_to_screen(p['pos'] - p['vel'].normalize() * trail_length)
            end = self.camera.world_to_screen(p['pos'])
            pygame.draw.line(screen, (255, 200, 50), start, end, 3)
            pygame.draw.circle(screen, (255, 255, 100), (int(end[0]), int(end[1])), 4)
        
        # Draw ships
        for s in self.ships:
            draw_ship(screen, s, self.camera)
        
        # Draw beams
        for b in self.beams:
            start = self.camera.world_to_screen(b['start'])
            end = self.camera.world_to_screen(b['end'])
            pygame.draw.line(screen, b['color'], start, end, 3)
        
        # Debug overlay
        if self.show_overlay:
            self._draw_debug_overlay(screen)
        
        # Stats panel
        self._draw_ship_stats_panel(screen)
        
        # Battle end UI
        self._draw_battle_end_ui(screen)
    
    def _draw_grid(self, screen):
        """Draw the background grid."""
        grid_spacing = 5000
        sw, sh = screen.get_size()
        
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
            pygame.draw.line(screen, grid_color, p1, p2, 1)
        
        for y in range(start_y, end_y + grid_spacing, grid_spacing):
            p1 = self.camera.world_to_screen(pygame.math.Vector2(start_x, y))
            p2 = self.camera.world_to_screen(pygame.math.Vector2(end_x, y))
            pygame.draw.line(screen, grid_color, p1, p2, 1)
    
    def _draw_debug_overlay(self, screen):
        """Draw debug information overlay."""
        for s in self.ships:
            if not s.is_alive: continue
            
            # Target line
            if s.current_target and s.current_target.is_alive:
                start = self.camera.world_to_screen(s.position)
                end = self.camera.world_to_screen(s.current_target.position)
                pygame.draw.line(screen, (0, 0, 255), start, end, 1)
            
            # Weapon range
            max_range = 0
            for layer in s.layers.values():
                for comp in layer['components']:
                    if isinstance(comp, Weapon) and comp.is_active:
                        if comp.range > max_range:
                            max_range = comp.range
            
            if max_range > 0:
                r_screen = int(max_range * self.camera.zoom)
                if r_screen > 0:
                    center = self.camera.world_to_screen(s.position)
                    pygame.draw.circle(screen, (100, 100, 100), (int(center.x), int(center.y)), r_screen, 1)
            
            # Aim point
            if hasattr(s, 'aim_point') and s.aim_point:
                aim_pos_screen = self.camera.world_to_screen(s.aim_point)
                length = 5
                color = (0, 100, 255)
                pygame.draw.line(screen, color, (aim_pos_screen.x - length, aim_pos_screen.y - length), 
                               (aim_pos_screen.x + length, aim_pos_screen.y + length), 2)
                pygame.draw.line(screen, color, (aim_pos_screen.x - length, aim_pos_screen.y + length), 
                               (aim_pos_screen.x + length, aim_pos_screen.y - length), 2)
            
            # Firing arcs
            center = self.camera.world_to_screen(s.position)
            for layer in s.layers.values():
                for comp in layer['components']:
                    if isinstance(comp, Weapon) and comp.is_active:
                        ship_angle = s.angle
                        facing = comp.facing_angle
                        arc = comp.firing_arc
                        rng = comp.range * self.camera.zoom
                        
                        start_angle = math.radians(ship_angle + facing - arc)
                        end_angle = math.radians(ship_angle + facing + arc)
                        
                        x1 = center.x + math.cos(start_angle) * rng
                        y1 = center.y + math.sin(start_angle) * rng
                        x2 = center.x + math.cos(end_angle) * rng
                        y2 = center.y + math.sin(end_angle) * rng
                        
                        arc_col = (255, 165, 0)
                        pygame.draw.line(screen, arc_col, center, (x1, y1), 1)
                        pygame.draw.line(screen, arc_col, center, (x2, y2), 1)
                        
                        try:
                            rect = pygame.Rect(center.x - rng, center.y - rng, rng*2, rng*2)
                            r_start = math.radians(ship_angle + facing - arc)
                            r_end = math.radians(ship_angle + facing + arc)
                            pygame.draw.arc(screen, arc_col, rect, -r_end, -r_start, 1)
                        except Exception:
                            pass
    
    def _draw_battle_end_ui(self, screen):
        """Draw battle end overlay or ongoing battle buttons."""
        team1_alive = sum(1 for s in self.ships if s.team_id == 0 and s.is_alive)
        team2_alive = sum(1 for s in self.ships if s.team_id == 1 and s.is_alive)
        sw, sh = screen.get_size()
        
        if team1_alive == 0 or team2_alive == 0:
            # Battle over overlay
            overlay = pygame.Surface((sw - self.stats_panel_width, sh), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            screen.blit(overlay, (0, 0))
            
            if team1_alive > 0:
                winner_text, winner_color = "TEAM 1 WINS!", (100, 200, 255)
            elif team2_alive > 0:
                winner_text, winner_color = "TEAM 2 WINS!", (255, 100, 100)
            else:
                winner_text, winner_color = "DRAW!", (200, 200, 200)
            
            win_font = pygame.font.Font(None, 72)
            win_surf = win_font.render(winner_text, True, winner_color)
            center_x = (sw - self.stats_panel_width) // 2
            screen.blit(win_surf, (center_x - win_surf.get_width() // 2, sh // 2 - 80))
            
            btn_font = pygame.font.Font(None, 36)
            btn_w, btn_h = 250, 50
            btn_x = center_x - btn_w // 2
            btn_y = sh // 2
            
            pygame.draw.rect(screen, (50, 80, 120), (btn_x, btn_y, btn_w, btn_h))
            pygame.draw.rect(screen, (100, 150, 200), (btn_x, btn_y, btn_w, btn_h), 2)
            btn_text = btn_font.render("Return to Battle Setup", True, (255, 255, 255))
            screen.blit(btn_text, (btn_x + btn_w // 2 - btn_text.get_width() // 2, btn_y + 12))
            
            self.battle_end_button_rect = pygame.Rect(btn_x, btn_y, btn_w, btn_h)
        else:
            # Ongoing battle - show End Battle button
            btn_font = pygame.font.Font(None, 24)
            btn_w, btn_h = 120, 30
            btn_x, btn_y = 10, 70
            
            pygame.draw.rect(screen, (80, 40, 40), (btn_x, btn_y, btn_w, btn_h))
            pygame.draw.rect(screen, (150, 80, 80), (btn_x, btn_y, btn_w, btn_h), 1)
            btn_text = btn_font.render("End Battle", True, (255, 200, 200))
            screen.blit(btn_text, (btn_x + btn_w // 2 - btn_text.get_width() // 2, btn_y + 7))
            
            self.end_battle_early_rect = pygame.Rect(btn_x, btn_y, btn_w, btn_h)
    
    def _draw_ship_stats_panel(self, screen):
        """Draw the ship stats panel on the right side."""
        sw, sh = screen.get_size()
        panel_x = sw - self.stats_panel_width
        panel_w = self.stats_panel_width
        
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
            y = self._draw_ship_entry(panel_surf, ship, y, panel_w, font_name, font_stat, (40, 60, 80))
        
        y += 15
        
        # Team 2
        team2_ships = [s for s in self.ships if s.team_id == 1]
        team2_alive = sum(1 for s in team2_ships if s.is_alive)
        
        title = font_title.render(f"TEAM 2 ({team2_alive}/{len(team2_ships)})", True, (255, 100, 100))
        panel_surf.blit(title, (10, y))
        y += 30
        
        for ship in team2_ships:
            y = self._draw_ship_entry(panel_surf, ship, y, panel_w, font_name, font_stat, (80, 40, 40))
        
        self._stats_panel_content_height = y + self.stats_scroll_offset
        
        screen.blit(panel_surf, (panel_x, 0))
        pygame.draw.line(screen, (60, 60, 80), (panel_x, 0), (panel_x, sh), 2)
    
    def _draw_ship_entry(self, surface, ship, y, panel_w, font_name, font_stat, banner_color):
        """Draw a single ship entry in the stats panel. Returns new y position."""
        arrow = "▼" if ship in self.expanded_ships else "►"
        status = "" if ship.is_alive else " [DEAD]"
        color = (200, 200, 200) if ship.is_alive else (100, 100, 100)
        bg_color = banner_color if ship.is_alive else (40, 40, 40)
        
        pygame.draw.rect(surface, bg_color, (5, y, panel_w - 10, 22))
        name_text = font_name.render(f"{arrow} {ship.name}{status}", True, color)
        surface.blit(name_text, (10, y + 3))
        y += 25
        
        if ship in self.expanded_ships:
            y = self._draw_ship_details(surface, ship, y, panel_w, font_stat)
        
        return y
    
    def _draw_ship_details(self, surface, ship, y, panel_w, font):
        """Draw expanded ship details. Returns new y position."""
        x_indent = 20
        bar_w = 120
        bar_h = 10
        
        # Source file
        if hasattr(ship, 'source_file') and ship.source_file:
            text = font.render(f"File: {ship.source_file}", True, (150, 150, 200))
            surface.blit(text, (x_indent, y))
            y += 16
        
        # AI Strategy
        strat_name = COMBAT_STRATEGIES.get(ship.ai_strategy, {}).get('name', ship.ai_strategy)
        text = font.render(f"AI: {strat_name}", True, (150, 200, 150))
        surface.blit(text, (x_indent, y))
        y += 16
        
        # HP Bar
        hp_pct = ship.hp / ship.max_hp if ship.max_hp > 0 else 0
        hp_color = (0, 255, 0) if hp_pct > 0.5 else ((255, 200, 0) if hp_pct > 0.2 else (255, 50, 50))
        text = font.render(f"HP: {int(ship.hp)}/{int(ship.max_hp)}", True, (180, 180, 180))
        surface.blit(text, (x_indent, y))
        self._draw_stat_bar(surface, x_indent + 100, y, bar_w, bar_h, hp_pct, hp_color)
        y += 16
        
        # Fuel Bar
        fuel_pct = ship.current_fuel / ship.max_fuel if ship.max_fuel > 0 else 0
        text = font.render(f"Fuel: {int(ship.current_fuel)}/{int(ship.max_fuel)}", True, (180, 180, 180))
        surface.blit(text, (x_indent, y))
        self._draw_stat_bar(surface, x_indent + 100, y, bar_w, bar_h, fuel_pct, (255, 165, 0))
        y += 16
        
        # Energy Bar
        energy_pct = ship.current_energy / ship.max_energy if ship.max_energy > 0 else 0
        text = font.render(f"Energy: {int(ship.current_energy)}/{int(ship.max_energy)}", True, (180, 180, 180))
        surface.blit(text, (x_indent, y))
        self._draw_stat_bar(surface, x_indent + 100, y, bar_w, bar_h, energy_pct, (100, 200, 255))
        y += 16
        
        # Ammo Bar
        ammo_pct = ship.current_ammo / ship.max_ammo if ship.max_ammo > 0 else 0
        text = font.render(f"Ammo: {int(ship.current_ammo)}/{int(ship.max_ammo)}", True, (180, 180, 180))
        surface.blit(text, (x_indent, y))
        self._draw_stat_bar(surface, x_indent + 100, y, bar_w, bar_h, ammo_pct, (200, 200, 100))
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
        
        # Components list
        for layer_type in [LayerType.ARMOR, LayerType.OUTER, LayerType.INNER, LayerType.CORE]:
            for comp in ship.layers[layer_type]['components']:
                hp_pct = comp.current_hp / comp.max_hp if comp.max_hp > 0 else 1.0
                color = (150, 150, 150) if comp.is_active else (80, 80, 80)
                bar_color = (0, 200, 0) if hp_pct > 0.5 else ((200, 200, 0) if hp_pct > 0.2 else (200, 50, 50))
                if not comp.is_active:
                    bar_color = (60, 60, 60)
                
                name = comp.name[:10] + ".." if len(comp.name) > 12 else comp.name
                hp_text = f"{int(comp.current_hp)}/{int(comp.max_hp)}"
                text = font.render(name, True, color)
                surface.blit(text, (x_indent + 5, y))
                hp_val = font.render(hp_text, True, color)
                surface.blit(hp_val, (x_indent + 95, y))
                self._draw_stat_bar(surface, x_indent + 160, y, 60, 8, hp_pct, bar_color)
                
                if hasattr(comp, 'fire_count') and comp.fire_count > 0:
                    fire_text = font.render(f"x{comp.fire_count}", True, (255, 200, 100))
                    surface.blit(fire_text, (x_indent + 230, y))
                
                y += 14
        
        y += 5
        return y
    
    def _draw_stat_bar(self, surface, x, y, width, height, pct, color):
        """Draw a progress bar."""
        pygame.draw.rect(surface, (40, 40, 40), (x, y, width, height))
        if pct > 0:
            fill_w = int(width * min(1.0, pct))
            pygame.draw.rect(surface, color, (x, y, fill_w, height))
        pygame.draw.rect(surface, (80, 80, 80), (x, y, width, height), 1)
    
    def _get_expanded_height(self, ship):
        """Calculate height needed for expanded ship stats."""
        base_height = 16 + 16 + 5 * 16 + 18 + 16  # 146
        comp_count = sum(len(l['components']) for l in ship.layers.values())
        comp_height = comp_count * 14
        return base_height + comp_height + 5
    
    def handle_click(self, mx, my, button, screen_size):
        """Handle mouse clicks. Returns True if click was handled."""
        sw, sh = screen_size
        
        # Check battle end button
        if self.battle_end_button_rect and self.battle_end_button_rect.collidepoint(mx, my):
            BATTLE_LOG.close()
            self.action_return_to_setup = True
            return True
        
        # Check end battle early button
        if self.end_battle_early_rect and self.end_battle_early_rect.collidepoint(mx, my):
            BATTLE_LOG.close()
            self.action_return_to_setup = True
            return True
        
        # Check stats panel click
        panel_x = sw - self.stats_panel_width
        if mx >= panel_x:
            return self._handle_stats_panel_click(mx - panel_x, my + self.stats_scroll_offset)
        
        return False
    
    def _handle_stats_panel_click(self, rel_x, rel_y):
        """Handle clicks on the stats panel."""
        team1_ships = [s for s in self.ships if s.team_id == 0]
        team2_ships = [s for s in self.ships if s.team_id == 1]
        
        y_pos = 10 + 30  # Header
        
        for ship in team1_ships:
            banner_height = 25
            if y_pos <= rel_y < y_pos + banner_height:
                if ship in self.expanded_ships:
                    self.expanded_ships.discard(ship)
                else:
                    self.expanded_ships.add(ship)
                return True
            y_pos += banner_height
            if ship in self.expanded_ships:
                y_pos += self._get_expanded_height(ship)
        
        y_pos += 15 + 30  # Gap + Team 2 header
        
        for ship in team2_ships:
            banner_height = 25
            if y_pos <= rel_y < y_pos + banner_height:
                if ship in self.expanded_ships:
                    self.expanded_ships.discard(ship)
                else:
                    self.expanded_ships.add(ship)
                return True
            y_pos += banner_height
            if ship in self.expanded_ships:
                y_pos += self._get_expanded_height(ship)
        
        return False
    
    def handle_scroll(self, scroll_y, screen_height):
        """Handle mouse wheel scrolling on stats panel."""
        self.stats_scroll_offset -= scroll_y * 30
        max_scroll = max(0, self._stats_panel_content_height - screen_height + 50)
        self.stats_scroll_offset = max(0, min(max_scroll, self.stats_scroll_offset))
    
    def print_headless_summary(self):
        """Print battle summary for headless mode."""
        elapsed = time.time() - self.headless_start_time if self.headless_start_time else 0
        
        team1_ships = [s for s in self.ships if s.team_id == 0]
        team2_ships = [s for s in self.ships if s.team_id == 1]
        team1_survivors = [s for s in team1_ships if s.is_alive]
        team2_survivors = [s for s in team2_ships if s.is_alive]
        
        print(f"\n=== BATTLE COMPLETE ===")
        print(f"Time: {elapsed:.2f}s, Ticks: {self.sim_tick_counter}")
        
        if self.sim_tick_counter >= 3000000:
            print(f"DRAW (tick limit: {self.sim_tick_counter:,} ticks)")
        elif len(team1_survivors) > 0 and len(team2_survivors) == 0:
            print("WINNER: Team 1!")
        elif len(team2_survivors) > 0 and len(team1_survivors) == 0:
            print("WINNER: Team 2!")
        else:
            print("DRAW!")
        
        print(f"\nTeam 1: {len(team1_survivors)}/{len(team1_ships)} survived")
        for s in team1_survivors:
            print(f"  - {s.name}: {s.hp:.0f}/{s.max_hp:.0f} HP")
        
        print(f"\nTeam 2: {len(team2_survivors)}/{len(team2_ships)} survived")
        for s in team2_survivors:
            print(f"  - {s.name}: {s.hp:.0f}/{s.max_hp:.0f} HP")
        
        print("=" * 30 + "\n")
