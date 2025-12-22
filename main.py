"""Main game entry point - coordinates scenes and game loop."""
import pygame
import os

from ship import Ship, LayerType
from designs import create_brick, create_interceptor
from components import load_components, load_modifiers
from ui import Button
from builder_gui import BuilderSceneGUI
from sprites import SpriteManager
from camera import Camera
from battle import BattleScene, BATTLE_LOG
from battle_setup import BattleSetupScreen


# Constants
WIDTH, HEIGHT = 3840, 2160
FPS = 60
BG_COLOR = (10, 10, 20)

# Scene States
MENU = 0
BUILDER = 1
BATTLE = 2
BATTLE_SETUP = 3

# Initialize fonts
pygame.font.init()
font_small = pygame.font.SysFont("arial", 12)
font_med = pygame.font.SysFont("arial", 20)
font_large = pygame.font.SysFont("arial", 32)


class Game:
    """Main game class coordinating scenes and game loop."""
    
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
        pygame.display.set_caption("Starship Battles")
        self.clock = pygame.time.Clock()
        self.running = True
        self.state = MENU
        
        # Load game data
        base_path = os.path.dirname(os.path.abspath(__file__))
        load_components(os.path.join(base_path, "data", "components.json"))
        load_modifiers(os.path.join(base_path, "data", "modifiers.json"))
        
        # Initialize ship data (Vehicle Classes)
        from ship import initialize_ship_data
        initialize_ship_data(base_path)
        
        # Load sprites
        sprite_mgr = SpriteManager.get_instance()
        sprite_mgr.load_atlas(os.path.join(base_path, "resources", "images", "Components.bmp"))
        
        # Menu UI
        self.menu_buttons = [
            Button(WIDTH//2 - 100, HEIGHT//2 - 50, 200, 50, "Ship Builder", self.start_builder),
            Button(WIDTH//2 - 100, HEIGHT//2 + 20, 200, 50, "Battle Setup", self.start_battle_setup)
        ]
        
        # Scene objects
        self.builder_scene = BuilderSceneGUI(WIDTH, HEIGHT, self.on_builder_return)
        self.battle_setup = BattleSetupScreen()
        self.battle_scene = BattleScene(WIDTH, HEIGHT)
    
    def start_builder(self):
        """Enter ship builder."""
        self.state = BUILDER
        self.builder_scene = BuilderSceneGUI(WIDTH, HEIGHT, self.on_builder_return)
    
    def on_builder_return(self, custom_ship=None):
        """Return from builder to main menu."""
        self.state = MENU
    
    def start_battle_setup(self, preserve_teams=False):
        """Enter battle setup screen."""
        self.state = BATTLE_SETUP
        self.battle_setup.start(preserve_teams=preserve_teams)
    
    def start_battle(self, team1_ships, team2_ships, headless=False):
        """Start a battle with the given ships."""
        self.state = BATTLE
        self.battle_scene.start(team1_ships, team2_ships, headless=headless)
    
    def run(self):
        """Main game loop."""
        # Fixed time step accumulator
        accumulator = 0.0
        dt = 0.01  # 100 ticks per second = 0.01s per tick attempt
        
        while self.running:
            # We still need real frame time for rendering smoothness or UI
            # But the simulation MUST advance in fixed steps.
            frame_time = self.clock.tick(0) / 1000.0
            
            # Cap frame_time to avoid spiral of death
            if frame_time > 0.1:
                frame_time = 0.1
                
            accumulator += frame_time
            
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.VIDEORESIZE:
                    self._handle_resize(event.w, event.h)
                elif event.type == pygame.KEYDOWN:
                    self._handle_keydown(event)
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self._handle_click(event)
                elif event.type == pygame.MOUSEWHEEL:
                    self._handle_scroll(event)
                
                # Forward events to current scene
                if self.state == MENU:
                    for btn in self.menu_buttons:
                        btn.handle_event(event)
                elif self.state == BUILDER:
                    self.builder_scene.handle_event(event)
                elif self.state == BATTLE_SETUP:
                    self.battle_setup.update([event], self.screen.get_size())
            
            self._update_and_draw(frame_time, events)
            
            pygame.display.flip()
        
        pygame.quit()
    
    def _handle_resize(self, w, h):
        """Handle window resize."""
        self.battle_scene.camera.width = w
        self.battle_scene.camera.height = h
        if self.state == MENU:
            self.menu_buttons[0].rect.center = (w//2, h//2 - 50)
            self.menu_buttons[1].rect.center = (w//2, h//2 + 20)
    
    def _handle_keydown(self, event):
        """Handle key press events."""
        if self.state == BATTLE:
            if event.key == pygame.K_o:
                self.battle_scene.show_overlay = not self.battle_scene.show_overlay
            elif event.key == pygame.K_SPACE:
                self.battle_scene.sim_paused = not self.battle_scene.sim_paused
            elif event.key == pygame.K_COMMA:
                if not self.battle_scene.sim_paused:
                    self.battle_scene.sim_speed_multiplier = max(0.0625, self.battle_scene.sim_speed_multiplier / 2.0)
            elif event.key == pygame.K_PERIOD:
                if not self.battle_scene.sim_paused:
                    self.battle_scene.sim_speed_multiplier = min(16.0, self.battle_scene.sim_speed_multiplier * 2.0)
            elif event.key == pygame.K_SLASH:
                self.battle_scene.sim_speed_multiplier = 100.0 # Max Speed
                self.battle_scene.sim_paused = False
    
    def _handle_click(self, event):
        """Handle mouse click events."""
        mx, my = event.pos
        
        if self.state == BATTLE:
            if self.battle_scene.handle_click(mx, my, event.button, self.screen.get_size()):
                if self.battle_scene.action_return_to_setup:
                    self.battle_scene.action_return_to_setup = False
                    self.start_battle_setup(preserve_teams=True)
    
    def _handle_scroll(self, event):
        """Handle mouse wheel events."""
        if self.state == BATTLE:
            mx, my = pygame.mouse.get_pos()
            sw = self.screen.get_size()[0]
            if mx >= sw - self.battle_scene.stats_panel_width or mx < self.battle_scene.ui.seeker_panel_width:
                self.battle_scene.handle_scroll(event.y, self.screen.get_size()[1])
    
    def _update_and_draw(self, frame_time, events):
        """Update logic and draw current scene."""
        if self.state == MENU:
            self._draw_menu()
        elif self.state == BUILDER:
            self.builder_scene.update(frame_time)
            self.builder_scene.process_ui_time(frame_time)
            self.builder_scene.draw(self.screen)
        elif self.state == BATTLE_SETUP:
            self._update_battle_setup()
        elif self.state == BATTLE:
            self._update_battle(frame_time, events)
    
    def _draw_menu(self):
        """Draw main menu."""
        self.screen.fill((20, 20, 30))
        for btn in self.menu_buttons:
            btn.draw(self.screen)
    
    def _update_battle_setup(self):
        """Update and draw battle setup, handle actions."""
        self.battle_setup.draw(self.screen)
        
        # Check for actions
        if self.battle_setup.action_start_battle:
            self.battle_setup.action_start_battle = False
            team1, team2 = self.battle_setup.get_ships()
            self.start_battle(team1, team2)
        elif self.battle_setup.action_start_headless:
            self.battle_setup.action_start_headless = False
            team1, team2 = self.battle_setup.get_ships()
            # Print initial info
            print(f"Team 1: {len(team1)} ships ({sum(s.max_hp for s in team1):.0f} total HP)")
            print(f"Team 2: {len(team2)} ships ({sum(s.max_hp for s in team2):.0f} total HP)")
            print("Running simulation...")
            self.start_battle(team1, team2, headless=True)
        elif self.battle_setup.action_return_to_menu:
            self.battle_setup.action_return_to_menu = False
            self.state = MENU
    
    def _update_battle(self, frame_time, events):
        """Update and draw battle scene."""
        if self.battle_scene.headless_mode:
            # Headless mode - run fast without rendering
            for _ in range(1000):
                self.battle_scene.update([])
                
                tick_limit_reached = self.battle_scene.sim_tick_counter >= 3000000
                
                if self.battle_scene.is_battle_over() or tick_limit_reached:
                    self.battle_scene.print_headless_summary()
                    BATTLE_LOG.close()
                    self.battle_scene.headless_mode = False
                    self.start_battle_setup(preserve_teams=True)
                    break
            
            # Progress indicator
            if self.battle_scene.sim_tick_counter % 10000 == 0:
                t1 = sum(1 for s in self.battle_scene.ships if s.team_id == 0 and s.is_alive)
                t2 = sum(1 for s in self.battle_scene.ships if s.team_id == 1 and s.is_alive)
                print(f"  Tick {self.battle_scene.sim_tick_counter}: Team1={t1}, Team2={t2}")
        else:
            # Normal visual battle
            
            # Update Visuals (Camera, Beams) - ALWAYS run this once per frame with real time
            self.battle_scene.update_visuals(frame_time, events)
            
            # Update Simulation
            # ACCUMULATOR LOGIC for deterministic speed control
            if not self.battle_scene.sim_paused:
                dt = 0.01 # 100 ticks per second standard
                
                # We scale "time passed" by the speed multiplier
                # If multiplier is 0.5, we accumulate half as much real time -> runs half as fast
                # If multiplier is 2.0, we accumulate twice as much -> runs 2x fast
                # For "MAX SPEED" (e.g. 100x), we might just run a fixed batch per frame to avoid huge spirals
                
                speed_mult = self.battle_scene.sim_speed_multiplier
                
                if speed_mult > 10.0:
                    # Max Speed / Turbo mode: Just run fixed N ticks per frame
                    ticks_to_run = int(speed_mult) # e.g. 100 ticks per frame
                    for i in range(ticks_to_run):
                        self.battle_scene.update(events if i==0 else [])
                    
                    self.battle_scene.tick_rate_count += ticks_to_run
                else:
                    # Time-Accurate Simulation (Slow/Normal/Fast)
                    # Use a persistent accumulator logic.
                    # Note: We need a persistent accumulator attribute on the Game class or BattleScene.
                    # Since we are refactoring _update_battle which was stateless-ish, let's use a dynamic attribute or check if one exists.
                    if not hasattr(self, '_battle_accumulator'):
                        self._battle_accumulator = 0.0
                    
                    self._battle_accumulator += frame_time * speed_mult
                    
                    # Safety cap
                    if self._battle_accumulator > 1.0:
                        self._battle_accumulator = 1.0
                        
                    ticks_run_this_frame = 0
                    while self._battle_accumulator >= dt:
                        self.battle_scene.update(events if ticks_run_this_frame==0 else [])
                        self._battle_accumulator -= dt
                        ticks_run_this_frame += 1
                        
                    self.battle_scene.tick_rate_count += ticks_run_this_frame
            
            self.battle_scene.draw(self.screen)
            
            # Update tick rate calculation
            self.battle_scene.tick_rate_timer += frame_time
            if self.battle_scene.tick_rate_timer >= 1.0:
                self.battle_scene.current_tick_rate = self.battle_scene.tick_rate_count
                self.battle_scene.tick_rate_count = 0
                self.battle_scene.tick_rate_timer = 0.0
            
            # Draw tick counters
            tick_text = f"Ticks: {self.battle_scene.sim_tick_counter:,}"
            rate_text = f"TPS: {self.battle_scene.current_tick_rate:,}/s"
            zoom_text = f"Zoom: {self.battle_scene.camera.zoom:.3f}x"
            
            self.screen.blit(font_med.render(tick_text, True, (180, 180, 180)), (10, 10))
            self.screen.blit(font_med.render(rate_text, True, (180, 180, 180)), (10, 35))
            self.screen.blit(font_med.render(zoom_text, True, (150, 200, 255)), (10, 60))
            
            # Draw speed indicator
            speed_text = "PAUSED" if self.battle_scene.sim_paused else f"Speed: {self.battle_scene.sim_speed_multiplier:.2f}x"
            if self.battle_scene.sim_speed_multiplier >= 10.0: speed_text = "MAX SPEED"
            
            speed_color = (255, 100, 100) if self.battle_scene.sim_paused else (200, 200, 200)
            if self.battle_scene.sim_speed_multiplier < 1.0:
                speed_color = (255, 200, 100)
            elif self.battle_scene.sim_speed_multiplier > 1.0:
                speed_color = (100, 255, 100)
                
            self.screen.blit(font_med.render(speed_text, True, speed_color), (WIDTH//2 - 50, 10))


if __name__ == "__main__":
    game = Game()
    game.run()
