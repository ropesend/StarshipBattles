"""Main game entry point - coordinates scenes and game loop."""
import argparse
import pygame
import os

from ship import Ship, LayerType

# Parse command line arguments - use parse_known_args to handle being imported as a module
parser = argparse.ArgumentParser(description="Starship Battles")
parser.add_argument('--force-resolution', action='store_true',
                    help='Force 2560x1600 resolution regardless of monitor size')
# parse_known_args returns (known_args, unknown_args) - this prevents failure when
# pytest or other tools pass their own arguments
args, _ = parser.parse_known_args()
from designs import create_brick, create_interceptor
from components import load_components, load_modifiers
from ui import Button
from builder_gui import BuilderSceneGUI
from sprites import SpriteManager
from camera import Camera
from battle import BattleScene
from battle_setup import BattleSetupScreen
from formation_editor import FormationEditorScene
from ui.test_lab_scene import TestLabScene
from profiling import PROFILER, profile_action


# Constants
# WIDTH, HEIGHT are now determined at runtime, but we set defaults here
DEFAULT_WIDTH, DEFAULT_HEIGHT = 2560, 1600
WIDTH, HEIGHT = DEFAULT_WIDTH, DEFAULT_HEIGHT
FPS = 60
BG_COLOR = (10, 10, 20)

# Scene States
MENU = 0
BUILDER = 1
BATTLE = 2
BATTLE_SETUP = 3
FORMATION = 4
TEST_LAB = 5

# Initialize fonts
pygame.font.init()
font_small = pygame.font.SysFont("arial", 12)
font_med = pygame.font.SysFont("arial", 20)
font_large = pygame.font.SysFont("arial", 32)


class Game:
    """Main game class coordinating scenes and game loop."""
    
    def __init__(self):
        pygame.init()
        
        # Monitor detection
        info = pygame.display.Info()
        monitor_w = info.current_w
        monitor_h = info.current_h
        
        global WIDTH, HEIGHT
        
        # Check for forced resolution
        if args.force_resolution:
            WIDTH, HEIGHT = 2560, 1600
        # Logic: Use 4K if available, else 2560x1600, else smaller?
        elif monitor_w >= 3840 and monitor_h >= 2160:
            WIDTH, HEIGHT = 3840, 2160
        elif monitor_w >= 2560 and monitor_h >= 1600:
            WIDTH, HEIGHT = 2560, 1600
        else:
             # Fallback for smaller screens (e.g. 1920x1080)
             WIDTH, HEIGHT = int(monitor_w * 0.9), int(monitor_h * 0.9)

        self.screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
        pygame.display.set_caption(f"Starship Battles ({WIDTH}x{HEIGHT})")
        
        self.clock = pygame.time.Clock()
        self.running = True
        self.show_exit_dialog = False
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
        sprite_mgr.load_sprites(base_path)
        
        # Menu UI
        self.update_menu_buttons()
        
        # Scene objects
        self.builder_scene = BuilderSceneGUI(WIDTH, HEIGHT, self.on_builder_return)
        self.battle_setup = BattleSetupScreen()
        self.battle_scene = BattleScene(WIDTH, HEIGHT)
        self.formation_scene = FormationEditorScene(WIDTH, HEIGHT, self.on_formation_return)
        self.test_lab_scene = TestLabScene(self)
    
    def update_menu_buttons(self):
        self.menu_buttons = [
            Button(WIDTH//2 - 100, HEIGHT//2 - 80, 200, 50, "Ship Builder", self.start_builder),
            Button(WIDTH//2 - 100, HEIGHT//2 - 10, 200, 50, "Battle Setup", self.start_battle_setup),
            Button(WIDTH//2 - 100, HEIGHT//2 + 60, 200, 50, "Formation Editor", self.start_formation_editor),
            Button(WIDTH//2 - 100, HEIGHT//2 + 130, 200, 50, "Combat Lab", self.start_test_lab)
        ]

    @profile_action("App: Start Builder")
    def start_builder(self):
        """Enter ship builder."""
        self.state = BUILDER
        self.builder_scene = BuilderSceneGUI(WIDTH, HEIGHT, self.on_builder_return)
    
    def on_builder_return(self, custom_ship=None):
        """Return from builder to main menu."""
        self.state = MENU
    
    @profile_action("App: Start Battle Setup")
    def start_battle_setup(self, preserve_teams=False):
        """Enter battle setup screen."""
        self.state = BATTLE_SETUP
        self.return_state = BATTLE_SETUP
        self.battle_setup.start(preserve_teams=preserve_teams)

    @profile_action("App: Start Formation Editor")
    def start_formation_editor(self):
        """Enter formation editor."""
        self.state = FORMATION
        self.formation_scene.handle_resize(WIDTH, HEIGHT)

    def on_formation_return(self):
        """Return from formation editor."""
        self.state = MENU
    
    def start_test_lab(self):
        """Enter Combat Lab."""
        self.state = TEST_LAB
        self.return_state = TEST_LAB
        self.test_lab_scene.scan_scenarios()
    
    def start_battle(self, team1_ships, team2_ships, headless=False):
        """Start a battle with the given ships."""
        self.state = BATTLE
        if self.battle_scene.screen_width != WIDTH or self.battle_scene.screen_height != HEIGHT:
             self.battle_scene.handle_resize(WIDTH, HEIGHT)
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
            
            # Global Exit Handling
            if self.show_exit_dialog:
                for event in events:
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                        self.show_exit_dialog = False
                    elif event.type == pygame.MOUSEBUTTONDOWN:
                         # Use global mouse handling for the dialog
                         if self._handle_exit_dialog_click(event.pos):
                             self.running = False
                         elif self._handle_exit_dialog_cancel(event.pos):
                             self.show_exit_dialog = False
            else:
                 # Normal handling
                 for event in events:
                    if event.type == pygame.QUIT:
                        self.running = False
                        
                    # Universal Exit Command
                    elif event.type == pygame.KEYDOWN and event.key == pygame.K_x and (event.mod & pygame.KMOD_ALT):
                        self.show_exit_dialog = True
                    
                    # Profiling Toggle
                    elif event.type == pygame.KEYDOWN and event.key == pygame.K_F9:
                        active = PROFILER.toggle()
                        print(f"Profiling {'ENABLED' if active else 'DISABLED'}")
                        
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
                    elif self.state == FORMATION:
                        self.formation_scene.handle_event(event)
                    elif self.state == TEST_LAB:
                        self.test_lab_scene.handle_input([event])
            
            self._update_and_draw(frame_time, events)
            
            pygame.display.flip()
        
        pygame.quit()
    
    def _handle_resize(self, w, h):
        """Handle window resize."""
        global WIDTH, HEIGHT
        WIDTH, HEIGHT = w, h
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
        
        if self.state == MENU:
            self.update_menu_buttons()
        elif self.state == BATTLE:
            self.battle_scene.handle_resize(w, h)
        elif self.state == BUILDER:
             if hasattr(self.builder_scene, 'handle_resize'):
                 self.builder_scene.handle_resize(w, h)
        elif self.state == FORMATION:
             self.formation_scene.handle_resize(w, h)
        elif self.state == TEST_LAB:
             # Test lab handles resize if implemented, otherwise just re-draws
             self.test_lab_scene._create_ui()
    
    def _handle_keydown(self, event):
        """Handle key press events."""
        if self.state == BATTLE:
            if event.key == pygame.K_o:
                self.battle_scene.show_overlay = not self.battle_scene.show_overlay
            elif event.key == pygame.K_SPACE:
                self.battle_scene.sim_paused = not self.battle_scene.sim_paused
            elif event.key == pygame.K_COMMA:
                self.battle_scene.sim_speed_multiplier = max(0.00390625, self.battle_scene.sim_speed_multiplier / 2.0)
            elif event.key == pygame.K_PERIOD:
                self.battle_scene.sim_speed_multiplier = min(16.0, self.battle_scene.sim_speed_multiplier * 2.0)
            elif event.key == pygame.K_m:
                 self.battle_scene.sim_speed_multiplier = 1.0
            elif event.key == pygame.K_SLASH:
                self.battle_scene.sim_speed_multiplier = 100.0 # Max Speed
    
    def _handle_click(self, event):
        """Handle mouse click events."""
        mx, my = event.pos
        
        if self.state == BATTLE:
            if self.battle_scene.handle_click(mx, my, event.button, self.screen.get_size()):
                if self.battle_scene.action_return_to_setup:
                    self.battle_scene.action_return_to_setup = False
                    
                    if hasattr(self, 'return_state') and self.return_state == TEST_LAB:
                        self.start_test_lab()
                    else:
                        self.start_battle_setup(preserve_teams=True)
    
    def _handle_scroll(self, event):
        """Handle mouse wheel events."""
        if self.state == BATTLE:
            mx, my = pygame.mouse.get_pos()
            sw = self.screen.get_size()[0]
            if mx >= sw - self.battle_scene.stats_panel_width or mx < self.battle_scene.ui.seeker_panel.rect.width:
                self.battle_scene.handle_scroll(event.y, self.screen.get_size()[1])
    
    def _update_and_draw(self, frame_time, events):
        """Update logic and draw current scene."""
        if self.state == MENU:
            self._draw_menu()
        elif self.state == BUILDER:
            self.builder_scene.update(frame_time)

            self.builder_scene.draw(self.screen)
        elif self.state == BATTLE_SETUP:
            self._update_battle_setup()
        elif self.state == BATTLE:
            self._update_battle(frame_time, events)
        elif self.state == FORMATION:
            self.formation_scene.update(frame_time)
            self.formation_scene.draw(self.screen)
        elif self.state == TEST_LAB:
            self.test_lab_scene.draw(self.screen)

        if self.show_exit_dialog:
             self._draw_exit_dialog()

    def _draw_exit_dialog(self):
        """Draw the exit confirmation dialog."""
        s = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        s.fill((0, 0, 0, 180)) # Darken background
        self.screen.blit(s, (0,0))
        
        # Box
        box_w, box_h = 400, 200
        box_x = (WIDTH - box_w) // 2
        box_y = (HEIGHT - box_h) // 2
        box_rect = pygame.Rect(box_x, box_y, box_w, box_h)
        
        pygame.draw.rect(self.screen, (40, 40, 50), box_rect)
        pygame.draw.rect(self.screen, (100, 100, 120), box_rect, 2)
        
        # Text
        title = font_large.render("Exit Application?", True, (255, 255, 255))
        self.screen.blit(title, (box_x + (box_w - title.get_width())//2, box_y + 40))
        
        # Buttons
        global exit_yes_rect, exit_no_rect
        btn_w, btn_h = 100, 40
        spacing = 40
        
        # Yes
        yes_x = box_x + box_w//2 - btn_w - spacing//2
        yes_y = box_y + 120
        exit_yes_rect = pygame.Rect(yes_x, yes_y, btn_w, btn_h)
        
        mx, my = pygame.mouse.get_pos()
        yes_col = (180, 60, 60) if exit_yes_rect.collidepoint(mx, my) else (150, 50, 50)
        
        pygame.draw.rect(self.screen, yes_col, exit_yes_rect)
        pygame.draw.rect(self.screen, (200, 100, 100), exit_yes_rect, 1)
        yes_txt = font_med.render("Yes", True, (255, 255, 255))
        self.screen.blit(yes_txt, (yes_x + (btn_w - yes_txt.get_width())//2, yes_y + 8))
        
        # No
        no_x = box_x + box_w//2 + spacing//2
        no_y = box_y + 120
        exit_no_rect = pygame.Rect(no_x, no_y, btn_w, btn_h)
        
        no_col = (60, 60, 80) if exit_no_rect.collidepoint(mx, my) else (50, 50, 60)
        
        pygame.draw.rect(self.screen, no_col, exit_no_rect)
        pygame.draw.rect(self.screen, (100, 100, 150), exit_no_rect, 1)
        no_txt = font_med.render("No", True, (255, 255, 255))
        self.screen.blit(no_txt, (no_x + (btn_w - no_txt.get_width())//2, no_y + 8))

    def _handle_exit_dialog_click(self, pos):
        global exit_yes_rect
        if 'exit_yes_rect' in globals() and exit_yes_rect and exit_yes_rect.collidepoint(pos):
            return True
        return False
        
    def _handle_exit_dialog_cancel(self, pos):
        global exit_no_rect
        if 'exit_no_rect' in globals() and exit_no_rect and exit_no_rect.collidepoint(pos):
             return True
        return False
    
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
                    self.battle_scene.engine.shutdown()
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
                    
                    import time
                    t0 = time.time()
                    for i in range(ticks_to_run):
                        self.battle_scene.update(events if i==0 else [])
                    t1 = time.time()
                    
                    elapsed = t1 - t0
                    if elapsed > 0.05: # Warn if taking > 50ms per frame
                         print(f"Slow Frame: {ticks_to_run} ticks took {elapsed*1000:.1f}ms (Avg {elapsed/ticks_to_run*1000:.3f}ms/tick)")

                    
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
            
            # Draw to the right of seeker panel (panel is 300px wide)
            panel_offset = self.battle_scene.ui.seeker_panel.rect.width + 10
            self.screen.blit(font_med.render(tick_text, True, (180, 180, 180)), (panel_offset, 10))
            self.screen.blit(font_med.render(rate_text, True, (180, 180, 180)), (panel_offset, 35))
            self.screen.blit(font_med.render(zoom_text, True, (150, 200, 255)), (panel_offset, 60))
            
            # Draw speed indicator
            if self.battle_scene.sim_speed_multiplier >= 10.0:
                 speed_val_text = "MAX SPEED"
            else:
                 speed_val_text = f"{self.battle_scene.sim_speed_multiplier:.4g}x"

            if self.battle_scene.sim_paused:
                 speed_text = f"PAUSED ({speed_val_text})"
            else:
                 speed_text = f"Speed: {speed_val_text}"
            
            speed_color = (255, 100, 100) if self.battle_scene.sim_paused else (200, 200, 200)
            if self.battle_scene.sim_speed_multiplier < 1.0:
                speed_color = (255, 200, 100)
            elif self.battle_scene.sim_speed_multiplier > 1.0:
                speed_color = (100, 255, 100)
                
            self.screen.blit(font_med.render(speed_text, True, speed_color), (WIDTH//2 - 50, 10))


            if PROFILER.is_active():
                prof_text = font_med.render("PROFILING ACTIVE", True, (255, 50, 50))
                self.screen.blit(prof_text, (WIDTH - 180, 10))

if __name__ == "__main__":
    game = Game()
    game.run()
    # Save profiling data
    PROFILER.save_history()
