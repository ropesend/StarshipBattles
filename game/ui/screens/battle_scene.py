"""Battle scene module for combat simulation and UI.

Uses BattleService as an abstraction layer over BattleEngine for cleaner
separation between UI and simulation logic.
"""
import pygame
import math
import random
import time

from game.ai.controller import AIController
from game.ui.renderer.game_renderer import draw_ship
from game.ui.renderer.camera import Camera
from game.ui.screens.battle_screen import BattleInterface
from game.simulation.services import BattleService



class BattleScene:
    """Manages battle simulation, rendering, and UI.

    Uses BattleService for battle management, providing a cleaner abstraction
    between UI concerns and simulation logic.
    """

    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height

        # Battle Service (abstraction layer over BattleEngine)
        self._battle_service = BattleService()
        # Create initial battle for backward compatibility (engine must exist)
        self._battle_service.create_battle()

        # Visual State
        self.beams = []  # distinct from engine beams, these have visual timers

        # Camera
        self.camera = Camera(screen_width, screen_height)

        # UI
        self.ui = BattleInterface(self, screen_width, screen_height)

        # Simulation Control
        self.sim_tick_counter = 0
        self.tick_rate_timer = 0.0
        self.tick_rate_count = 0
        self.current_tick_rate = 0
        self.sim_paused = False
        self.sim_speed_multiplier = 1.0

        # Headless mode
        self.headless_mode = False
        self.headless_start_time = None

        # Test mode (Combat Lab)
        self.test_mode = False  # Set to True when running from Combat Lab
        self.test_scenario = None  # The scenario being run (if in test mode)
        self.test_tick_count = 0  # Track ticks for max_ticks limit
        self.test_completed = False  # Flag indicating test has finished

        # Actions for Game class
        self.action_return_to_setup = False
        self.action_return_to_test_lab = False

    @property
    def engine(self):
        """Access the underlying BattleEngine (for backward compatibility)."""
        return self._battle_service.get_engine()

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

    def start(self, team1_ships, team2_ships, seed=None, headless=False, start_paused=False, test_mode=False, test_scenario=None):
        """Start a battle between two teams.

        Args:
            team1_ships: List of ships for team 0
            team2_ships: List of ships for team 1
            seed: Random seed for deterministic battles
            headless: Run without rendering
            start_paused: Start with simulation paused (useful for tests)
            test_mode: Running from Combat Lab (shows return button when done)
            test_scenario: The TestScenario instance (if running from Combat Lab)
        """
        self.headless_mode = headless
        self.headless_start_time = None
        if headless:
            self.headless_start_time = time.time()
            print("\n=== STARTING HEADLESS BATTLE ===")

        # Use BattleService to set up and start the battle
        self._battle_service.create_battle(seed=seed, enable_logging=True)

        # Add ships to teams via service
        for ship in team1_ships:
            self._battle_service.add_ship(ship, team_id=0)
        for ship in team2_ships:
            self._battle_service.add_ship(ship, team_id=1)

        # Start the battle
        self._battle_service.start_battle()

        self.beams = []
        self.sim_tick_counter = 0
        self.action_return_to_setup = False
        self.action_return_to_test_lab = False
        self.test_mode = test_mode
        self.test_scenario = test_scenario
        self.test_tick_count = 0

        # Reset UI
        self.ui.expanded_ships = set()
        self.ui.stats_scroll_offset = 0

        self.sim_speed_multiplier = 1.0  # Reset speed on new battle
        self.sim_paused = start_paused  # Set initial pause state

        if not headless:
            self.camera.fit_objects(self.ships)

        # DEBUG LOGGING: Check for initial derelict status
        for s in self.ships:
            fuel = s.resources.get_value("fuel")
            status_msg = f"Ship '{s.name}' (Team {s.team_id}): HP={s.hp}/{s.max_hp} Mass={s.mass} Thrust={s.total_thrust} Fuel={fuel} TurnSpeed={s.turn_speed:.2f} MaxSpeed={s.max_speed:.2f} Derelict={s.is_derelict}"
            self.engine.logger.log(status_msg)
            print(status_msg)

            if s.is_derelict:
                warn_msg = f"CRITICAL WARNING: Ship {s.name} is DERELICT on start! (Bridge? Engines? LifeSupport? Power?)"
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
        # Check if test scenario has completed
        if self.test_mode and self.test_scenario and not self.test_completed:
            self.test_tick_count += 1

            # Call scenario's update method
            self.test_scenario.update(self.engine)

            # Check if test should end (engine handles all end conditions)
            if self.engine.is_battle_over():
                # Test complete - verify results and populate results dict
                print(f"DEBUG: Test complete! ticks={self.test_tick_count}")

                # Populate results dict (similar to headless mode)
                if not hasattr(self.test_scenario, 'results') or not self.test_scenario.results:
                    self.test_scenario.results = {}
                self.test_scenario.results['ticks_run'] = self.test_tick_count
                self.test_scenario.results['ticks'] = self.test_tick_count  # Alias for consistency

                # Run verification (populates additional results)
                self.test_scenario.passed = self.test_scenario.verify(self.engine)
                print(f"DEBUG: Test {'PASSED' if self.test_scenario.passed else 'FAILED'}")
                print(f"DEBUG: Results populated: {list(self.test_scenario.results.keys())}")

                # Log test execution (for UI vs headless comparison)
                try:
                    from test_framework.runner import TestRunner
                    runner = TestRunner()
                    runner._log_test_execution(self.test_scenario, headless=False)
                except Exception as e:
                    print(f"Warning: Failed to log UI test execution: {e}")

                # Signal test completion (keep scenario reference for results retrieval)
                self.test_completed = True
                return  # Don't update engine anymore

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
        # In test mode, battle is over when scenario completes
        if self.test_mode and self.test_scenario is None and self.test_tick_count > 0:
            return True  # Test has completed
        return self._battle_service.is_battle_over()

    def get_winner(self):
        """Get the winning team. Returns 0, 1, or -1 for draw."""
        return self._battle_service.get_winner()
    
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
            self._battle_service.reset()
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
        """Print summary of headless battle results."""
        # Skip summary for test mode - test framework handles results
        if self.test_mode:
            print(f"Headless test complete: {self.sim_tick_counter} ticks")
            return

        # For normal headless battles, print summary if UI supports it
        if hasattr(self.ui, 'print_headless_summary'):
            self.ui.print_headless_summary(self.headless_start_time, self.sim_tick_counter)
        else:
            print(f"Headless battle complete: {self.sim_tick_counter} ticks")
