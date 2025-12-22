"""Battle scene module for combat simulation and UI."""
import pygame
import math
import random
import time

from ai import AIController
from spatial import SpatialGrid
from rendering import draw_ship
from camera import Camera
from battle_ui import BattleInterface

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
        
        # UI
        self.ui = BattleInterface(self, screen_width, screen_height)
        
        # Simulation
        self.sim_tick_counter = 0
        self.tick_rate_timer = 0.0
        self.tick_rate_count = 0
        self.current_tick_rate = 0
        self.sim_paused = False
        self.sim_speed_multiplier = 1.0
        
        # Headless mode
        self.headless_mode = False
        self.headless_start_time = None
        
        # Actions for Game class
        self.action_return_to_setup = False

    @property
    def show_overlay(self):
        return self.ui.show_overlay
    
    @show_overlay.setter
    def show_overlay(self, value):
        self.ui.show_overlay = value

    @property
    def stats_panel_width(self):
        return self.ui.stats_panel_width

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
        self.action_return_to_setup = False
        
        # Reset UI
        self.ui.expanded_ships = set()
        self.ui.stats_scroll_offset = 0
        
        # Start logging
        BATTLE_LOG.start_session()
        BATTLE_LOG.log(f"Battle started: {len(team1_ships)} vs {len(team2_ships)} ships")
        
        self.sim_speed_multiplier = 1.0 # Reset speed on new battle
        
        if not headless:
            self.camera.fit_objects(self.ships)
    
    def update(self, events):
        """
        Update battle simulation for one tick.
        """
        # Note: Camera input is now handled in update_visuals or main.py independently
        
        if not self.is_battle_over():
            self.sim_tick_counter += 1
        
        # 1. Update Grid
        self.grid.clear()
        alive_ships = [s for s in self.ships if s.is_alive]
        for s in alive_ships:
            self.grid.insert(s)
        
        # 2. Update AI & Ships
        for ai in self.ai_controllers:
            ai.update()
        for s in self.ships:
            s.update()
        
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
                    'type': 'projectile',
                    'pos': attack['position'],
                    'vel': attack['velocity'],
                    'damage': attack['damage'],
                    'range': attack['range'],
                    'distance_traveled': 0,
                    'owner': attack['source'],
                    'radius': 3,
                    'color': attack.get('color', (255, 255, 0))
                })
            elif attack['type'] == 'missile':
                BATTLE_LOG.log(f"Missile fired at {attack.get('target', 'unknown')}")
                self.projectiles.append({
                    'type': 'missile',
                    'pos': attack['position'],
                    'vel': attack['velocity'],
                    'damage': attack['damage'],
                    'range': attack['range'], # We can use range as max distance if needed, but endurance handles it
                    'distance_traveled': 0,
                    'owner': attack['source'],
                    'radius': 5,
                    'color': attack.get('color', (255, 50, 50)),
                    'target': attack.get('target'),
                    'turn_rate': attack.get('turn_rate', 30),
                    'max_speed': attack.get('max_speed', 10),
                    'endurance': attack.get('endurance', 5.0), # In seconds
                    'hp': attack.get('hp', 1)
                })
            elif attack['type'] == 'beam':
                self._process_beam_attack(attack)
        
        # 4. Ship-to-Ship Collisions (Ramming)
        self._process_ramming()
        
        # 5. Update Projectiles
        self._update_projectiles()
        
        # 6. Update Beams (Cleanup only, or moved to visual update?)
        # Actually beams are purely visual, but they are generated here.
        # Timer decrement should be in update_visuals.
    
    def update_visuals(self, dt, events):
        """
        Update visual elements (beams, camera) based on real-time delta.
        Independent of simulation ticks.
        """
        self.camera.update_input(dt, events)
        
        # Update Beams
        if dt > 0:
            for b in self.beams:
                b['timer'] -= dt
            self.beams = [b for b in self.beams if b['timer'] > 0]
            
        # Keyboard cycle handling
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFTBRACKET:
                    self._cycle_camera_focus(-1)
                elif event.key == pygame.K_RIGHTBRACKET:
                    self._cycle_camera_focus(1)

    def _cycle_camera_focus(self, direction):
        """Cycle camera focus through living ships."""
        alive_ships = [s for s in self.ships if s.is_alive]
        if not alive_ships: return
        
        current_idx = -1
        if self.camera.target in alive_ships:
            current_idx = alive_ships.index(self.camera.target)
        
        new_idx = (current_idx + direction) % len(alive_ships)
        self.camera.target = alive_ships[new_idx]
    
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
            'timer': 0.15, # VISUAL ONLY: 0.15 seconds duration. Does not affect physics.
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
    
    def _update_projectiles(self):
        """Update projectile positions and check collisions."""
        projectiles_to_remove = set()
        
        for idx, p in enumerate(self.projectiles):
            if idx in projectiles_to_remove:
                continue
            
            p_pos_t0 = p['pos']
            p_vel = p['vel']
            p_vel_length = p_vel.length()

            # Missile Logic
            if p.get('type') == 'missile':
                # Endurance check
                p['endurance'] -= 0.01
                if p['endurance'] <= 0:
                    projectiles_to_remove.add(idx)
                    continue

                # Guidance
                target = p.get('target')
                if target and target.is_alive:
                    # Calculate lead
                    # solve_lead expects (pos, vel, t_pos, t_vel, speed)
                    # For guided missiles, we want to know intersect time assuming we steer continuously at max_speed.
                    # Passing current p['vel'] breaks the math if missile is turning or speed varies.
                    # Passing (0,0) treats it as "Interceptor launching from P0 at Speed S".
                    t = p['owner'].solve_lead(p_pos_t0, pygame.math.Vector2(0, 0), target.position, target.velocity, p['max_speed'])
                    
                    aim_pos = target.position
                    if t > 0:
                        aim_pos = target.position + target.velocity * t
                    
                    desired_vec = aim_pos - p_pos_t0
                    if desired_vec.length_squared() > 0:
                        desired_dir = desired_vec.normalize()
                        current_dir = p_vel.normalize() if p_vel.length() > 0 else pygame.math.Vector2(1, 0)
                        
                        # angle_to returns angle from current to desired
                        angle_diff = current_dir.angle_to(desired_dir)
                        max_turn = p['turn_rate'] / 100.0 # Degrees per tick
                        
                        # Handle wrapping if needed, but angle_to handles -180 to 180 usually
                        # Just clamp
                        if abs(angle_diff) > max_turn:
                            rotation = max_turn if angle_diff > 0 else -max_turn
                        else:
                            rotation = angle_diff
                        
                        new_vel = current_dir.rotate(rotation) * p['max_speed']
                        p['vel'] = new_vel
                        p_vel = new_vel
                        p_vel_length = p_vel.length()
            
            # Pos update per tick
            p_pos_t1 = p_pos_t0 + p_vel 
            
            hit_occurred = False
            
            query_pos = (p_pos_t0 + p_pos_t1) * 0.5
            # Radius checks for 1 tick of movement
            query_radius = p_vel_length + 100
            nearby_ships = self.grid.query_radius(query_pos, query_radius)
            
            for s in nearby_ships:
                if not s.is_alive: continue
                if s.team_id == p['owner'].team_id: continue
                
                # CCD
                s_vel = s.velocity
                s_pos_t1 = s.position
                s_pos_t0 = s_pos_t1 - s_vel # Backtrack 1 tick
                
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
                    t_clamped = max(0, min(t, 1.0)) # Clamped to 1 tick
                    
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
                p['distance_traveled'] += p_vel_length
                
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
        
        # 1. Background Grid (UI)
        self.ui.draw_grid(screen)
        
        # 2. Loop through entities
        # Draw projectiles
        for p in self.projectiles:
            trail_length = 100
            start = self.camera.world_to_screen(p['pos'] - p['vel'].normalize() * trail_length)
            end = self.camera.world_to_screen(p['pos'])
            pygame.draw.line(screen, (255, 200, 50), start, end, 3)
            pygame.draw.circle(screen, (255, 255, 100), (int(end[0]), int(end[1])), 4)
        
        # Draw ships
        self.camera.show_overlay = self.ui.show_overlay # Hack to pass state to renderer
        for s in self.ships:
            draw_ship(screen, s, self.camera)
        
        # Draw beams
        for b in self.beams:
            start = self.camera.world_to_screen(b['start'])
            end = self.camera.world_to_screen(b['end'])
            pygame.draw.line(screen, b['color'], start, end, 3)
        
        # 3. UI Overlays
        if self.ui.show_overlay:
            self.ui.draw_debug_overlay(screen)
        
        # Stats panel
        self.ui.draw_ship_stats_panel(screen)
        
        # Battle end UI
        self.ui.draw_battle_end_ui(screen)
    
    def handle_click(self, mx, my, button, screen_size):
        """Handle mouse clicks. Returns True if click was handled."""
        result = self.ui.handle_click(mx, my, button)
        
        if isinstance(result, tuple) and result[0] == "focus_ship":
            self.camera.target = result[1]
            return True
            
        if result == "end_battle":
            BATTLE_LOG.close()
            self.action_return_to_setup = True
            return True
        
        # If UI didn't handle it and it's a left click, clear focus
        if not result and button == 1:
            self.camera.target = None
            
        return result
    
    def handle_scroll(self, scroll_y, screen_height):
        """Handle mouse wheel scrolling on stats panel."""
        self.ui.handle_scroll(scroll_y)
    
    def print_headless_summary(self):
        """Print summary."""
        self.ui.print_headless_summary(self.headless_start_time, self.sim_tick_counter)
