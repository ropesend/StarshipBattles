"""Battle scene module for combat simulation and UI."""
import pygame
import math
import random
import time

from ai import AIController
from rendering import draw_ship
from camera import Camera
from battle_ui import BattleInterface
from battle_engine import BattleEngine



class BattleScene:
    """Manages battle simulation, rendering, and UI."""
    
    def __init__(self, screen_width, screen_height):
        # ... (rest of init)
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # Battle Engine
        self.engine = BattleEngine()
        
        # Visual State
        self.beams = [] # distinct from engine beams, these have visual timers
        
        # Camera
        self.camera = Camera(screen_width, screen_height)
        
        # UI
        self.ui = BattleInterface(self, screen_width, screen_height)
        
        # Simulation Control
        self.sim_tick_counter = 0 # shadow copy or just delegate? engine has it.
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

    def handle_resize(self, width, height):
        """Handle window resize."""
        self.screen_width = width
        self.screen_height = height
        self.camera.width = width
        self.camera.height = height
        
        # Update UI
        self.ui.handle_resize(width, height)

    @property
    def show_overlay(self):
        return self.ui.show_overlay
    
    @show_overlay.setter
    def show_overlay(self, value):
        self.ui.show_overlay = value

    @property
    def stats_panel_width(self):
        return self.ui.stats_panel.rect.width

    @property
    def ships(self):
        return self.engine.ships

    @property
    def projectiles(self):
        return self.engine.projectiles

    @property
    def ai_controllers(self):
        return self.engine.ai_controllers

    def start(self, team1_ships, team2_ships, seed=None, headless=False):
        """Start a battle between two teams."""
        self.headless_mode = headless
        self.headless_start_time = None
        if headless:
            self.headless_start_time = time.time()
            print("\n=== STARTING HEADLESS BATTLE ===")
        
        self.engine.start(team1_ships, team2_ships, seed)
        self.beams = []
        self.sim_tick_counter = 0
        self.action_return_to_setup = False
        
        # Reset UI
        self.ui.expanded_ships = set()
        self.ui.stats_scroll_offset = 0
        
        self.sim_speed_multiplier = 1.0 # Reset speed on new battle
        
        if not headless:
            self.camera.fit_objects(self.engine.ships)
        
        # Initial Logging is handled by Engine

            
        # DEBUG LOGGING: Check for initial derelict status
        # DEBUG LOGGING: Check for initial derelict status
        for s in self.ships:
            status_msg = f"Ship '{s.name}' (Team {s.team_id}): HP={s.hp}/{s.max_hp} Mass={s.mass} Thrust={s.total_thrust} Fuel={s.current_fuel} TurnSpeed={s.turn_speed:.2f} MaxSpeed={s.max_speed:.2f} Derelict={s.is_derelict}"
            self.engine.logger.log(status_msg)
            print(status_msg) # Force console output
            
            if s.is_derelict:
                warn_msg = f"WARNING: {s.name} is DERELICT at start! (Bridge? Engines? LifeSupport? Power?)"
                self.engine.logger.log(warn_msg)
                print(warn_msg)
            
            if s.total_thrust <= 0:
                warn_msg = f"WARNING: {s.name} has NO THRUST!"
                self.engine.logger.log(warn_msg)
                print(warn_msg)
                
            if s.turn_speed <= 0.01:
                warn_msg = f"WARNING: {s.name} has LOW/NO TURN SPEED ({s.turn_speed:.4f})! Mass too high for thrusters?"
                self.engine.logger.log(warn_msg)
                print(warn_msg)
        
    
    def update(self, events):
        """
        Update battle simulation for one tick.
        """
        if not self.engine.is_battle_over():
            self.sim_tick_counter = self.engine.tick_counter + 1 # Sync tick counter
            # Delegated Update
            self.engine.update()
            
            # Sync Beams for Visuals
            for b in self.engine.recent_beams:
                b_visual = b.copy()
                b_visual['timer'] = 0.15
                self.beams.append(b_visual)
            

    
    def update_visuals(self, dt, events):
        """Update visual effects like beams and camera."""
        # Process Visual-related Inputs (Keys)
        for event in events:
            if event.type == pygame.KEYDOWN:
                 if event.key == pygame.K_F3:
                     self.ui.show_overlay = not self.ui.show_overlay
                 elif event.key == pygame.K_LEFTBRACKET:
                     self._cycle_focus_ship(-1)
                 elif event.key == pygame.K_RIGHTBRACKET:
                     self._cycle_focus_ship(1)

        # Update Beams
        for b in self.beams:
            b['timer'] -= dt
        self.beams = [b for b in self.beams if b['timer'] > 0]
        
        # Update Camera
        self.camera.update(dt)
        self.camera.update_input(dt, events)

    def _cycle_focus_ship(self, direction):
        """Cycle camera focus through alive ships."""
        alive_ships = [s for s in self.engine.ships if s.is_alive]
        if not alive_ships:
            return

        current_idx = -1
        if self.camera.target in alive_ships:
            current_idx = alive_ships.index(self.camera.target)
        
        new_idx = (current_idx + direction) % len(alive_ships)
        self.camera.target = alive_ships[new_idx]

    # Note: method removed duplicate update_visuals here (it was in orig file twice?)

    def is_battle_over(self):
        """Check if the battle has ended."""
        return self.engine.is_battle_over()
    
    def get_winner(self):
        """Get the winning team. Returns 0, 1, or -1 for draw."""
        return self.engine.get_winner()
    
    def draw(self, screen):
        """Draw the battle scene."""
        screen.fill((10, 10, 20))
        
        # 1. Background Grid (UI)
        self.ui.draw_grid(screen)
        
        # 2. Loop through entities
        # Draw projectiles
        for p in self.engine.projectiles:
            trail_length = 100
            start_pos = p.position - p.velocity.normalize() * trail_length
            end_pos = p.position
            
            start = self.camera.world_to_screen(start_pos)
            end = self.camera.world_to_screen(end_pos)
            
            color = getattr(p, 'color', (255, 200, 50))
            pygame.draw.line(screen, color, start, end, 3)
            pygame.draw.circle(screen, (255, 255, 100), (int(end[0]), int(end[1])), int(getattr(p, 'radius', 4)))
        
        # Draw ships
        self.camera.show_overlay = self.ui.show_overlay # Hack to pass state to renderer
        for s in self.engine.ships:
            draw_ship(screen, s, self.camera)
        
        # Draw beams
        for b in self.beams:
            start = self.camera.world_to_screen(b['start'])
            end = self.camera.world_to_screen(b['end'])
            pygame.draw.line(screen, b['color'], start, end, 3)
        
        # 3. UI Overlays
        if self.ui.show_overlay:
            self.ui.draw_debug_overlay(screen)
        
        # Seeker panel (Left)
        self.ui.seeker_panel.draw(screen)
        
        # Stats panel (Right)
        self.ui.stats_panel.draw(screen)
        
        # Battle end UI / Controls
        self.ui.control_panel.draw(screen)
    
    def handle_click(self, mx, my, button, screen_size):
        """Handle mouse clicks. Returns True if click was handled."""
        result = self.ui.handle_click(mx, my, button)
        
        if isinstance(result, tuple) and result[0] == "focus_ship":
            self.camera.target = result[1]
            return True
            
        if result == "end_battle":
            self.engine.shutdown()
            self.action_return_to_setup = True
            return True
        
        # If UI didn't handle it and it's a left click, clear focus
        if not result and button == 1:
            self.camera.target = None
            
        return result
    
    def handle_scroll(self, scroll_y, screen_height):
        """Handle mouse wheel scrolling on stats panel."""
        self.ui.handle_scroll(scroll_y, screen_height)
    
    def print_headless_summary(self):
        """Print summary."""
        self.ui.print_headless_summary(self.headless_start_time, self.sim_tick_counter)
