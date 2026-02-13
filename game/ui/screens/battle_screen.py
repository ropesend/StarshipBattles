"""Battle screen module for combat simulation and UI.

Uses BattleService as an abstraction layer over BattleEngine for cleaner
separation between UI and simulation logic.

Can optionally use BattleController for unified battle mode support
(manual, test, strategy, hypothetical battles).

PROJ-40: Removed unused AIController import. BattleService is instantiated at
runtime so must remain a runtime import.
"""
import pygame
import math
import random
import time
from typing import Optional, List, TYPE_CHECKING

from game.core.logger import log_debug, log_info, log_warning
from game.core.config import PhysicsConfig
from game.ui.config import UIConfig
from game.ui.renderer.game_renderer import draw_ship
from game.ui.renderer.camera import Camera
from game.ui.screens.battle_ui import BattleUI
from game.simulation.services import BattleService
from game.ui.services.battle_ui_service import BattleUIService
# PROJ-126: Import AI factory from AI layer (UI can depend on AI)
from game.ai.ai_factory import AIControllerFactory

if TYPE_CHECKING:
    from game.simulation.battle_controller import BattleController
    from game.simulation.battle_config import BattleConfig
    from game.simulation.entities.ship import Ship



# Speed multiplier constants for simulation time control (moved from battle_input_handler)
MIN_SPEED_MULTIPLIER = 0.00390625  # 1/256 - minimum slow-motion speed
MAX_SPEED_MULTIPLIER = 16.0        # 16x - maximum fast-forward speed
NORMAL_SPEED = 1.0                 # 1x - real-time simulation speed
UI_PAUSE_SPEED = 100.0             # 100x - instant updates when UI is paused


class BattleScreen:
    """Manages battle simulation, rendering, and UI.

    Implements IScene protocol for standardized scene handling.

    Uses BattleService for battle management, providing a cleaner abstraction
    between UI concerns and simulation logic.

    Can optionally use BattleController for unified battle orchestration
    across all battle modes (manual, test, strategy, hypothetical).
    """

    def __init__(self, screen_width: int, screen_height: int, scene_callback=None):
        """Initialize battle screen.

        Args:
            screen_width: Screen width in pixels
            screen_height: Screen height in pixels
            scene_callback: Callback function for scene transitions.
                           Called with (action, **kwargs) where action is:
                           - "return_to_setup": Return to battle setup (preserve teams)
                           - "return_to_test_lab": Return to Combat Lab
        """
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.scene_callback = scene_callback

        # Battle Service (abstraction layer over BattleEngine)
        self._battle_service = BattleService()
        # PROJ-126: Create AI factory and inject into battle service
        self._ai_factory = AIControllerFactory()
        # Create initial battle so engine exists before start() is called
        self._battle_service.create_battle(ai_factory=self._ai_factory)

        # Battle UI Service (PROJ-43: Clean interface for UI to access battle state)
        # Provides DTOs instead of direct domain object access
        self._ui_service = BattleUIService(self._battle_service)

        # Optional BattleController (for unified battle mode support)
        self._controller: Optional['BattleController'] = None

        # Visual State
        self.beams = []  # distinct from engine beams, these have visual timers

        # Camera
        self.camera = Camera(screen_width, screen_height)

        # UI
        self.ui = BattleUI(self, screen_width, screen_height)

        # Simulation Control
        self.sim_tick_counter = 0
        self.tick_rate_timer = 0.0
        self.tick_rate_count = 0
        self.current_tick_rate = 0
        self.sim_paused = False
        self.sim_speed_multiplier = 1.0

        # Accumulator for time-accurate simulation (moved from Game)
        self._accumulator = 0.0

        # Headless mode
        self.headless_mode = False
        self.headless_start_time = None

        # Test mode (Combat Lab)
        self.test_mode = False  # Set to True when running from Combat Lab
        self.test_scenario = None  # The scenario being run (if in test mode)
        self.test_tick_count = 0  # Track ticks for max_ticks limit
        self.test_completed = False  # Flag indicating test has finished

        # Font for HUD (passed in or created)
        self._hud_font = None

    # === Controller Integration ===

    def set_controller(self, controller: 'BattleController') -> None:
        """
        Set the BattleController for unified battle orchestration.

        When a controller is set, the scene delegates battle management
        to the controller instead of using BattleService directly.

        Args:
            controller: Configured BattleController instance
        """
        self._controller = controller
        # Sync battle service reference and UI service
        if controller:
            self._battle_service = controller.service
            self._ui_service = BattleUIService(self._battle_service)

    def get_controller(self) -> Optional['BattleController']:
        """Get the current BattleController (if any)."""
        return self._controller

    def start_with_controller(
        self,
        controller: 'BattleController',
        start_paused: bool = False
    ) -> None:
        """
        Start a battle using a pre-configured BattleController.

        This is the preferred way to start battles for strategy and
        hypothetical modes.

        Args:
            controller: Configured and started BattleController
            start_paused: Whether to start paused
        """
        self._controller = controller
        self._battle_service = controller.service
        self._ui_service = BattleUIService(self._battle_service)

        # Reset visual state
        self.beams = []
        self.sim_tick_counter = 0

        # Get mode from controller config
        config = controller.config
        if config:
            self.headless_mode = config.headless
            self.test_mode = config.mode.value == "test"
            self.test_scenario = config.test_scenario

        self.test_tick_count = 0
        self.test_completed = False

        # Reset UI
        self.ui.expanded_ships = set()
        self.ui.stats_scroll_offset = 0

        self.sim_speed_multiplier = 1.0
        self.sim_paused = start_paused

        # Fit camera to ships
        if not self.headless_mode and self.ships:
            self.camera.fit_objects(self.ships)

        log_info(f"Battle started via controller: {len(self.ships)} ships")

    @property
    def engine(self):
        """Access the underlying BattleEngine."""
        return self._battle_service.get_engine()

    @property
    def ui_service(self) -> BattleUIService:
        """Access the BattleUIService for DTO-based battle state queries.

        PROJ-43: Provides clean interface for UI components to access battle
        state through DTOs instead of direct domain object access.

        Returns:
            BattleUIService instance for this scene
        """
        return self._ui_service

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
            log_info("=== STARTING HEADLESS BATTLE ===")

        # Use BattleService to set up and start the battle
        # PROJ-126: Reuse same AI factory instance
        self._battle_service.create_battle(seed=seed, enable_logging=True, ai_factory=self._ai_factory)

        # Update UI service reference (PROJ-43)
        self._ui_service = BattleUIService(self._battle_service)

        # Add ships to teams via service
        for ship in team1_ships:
            self._battle_service.add_ship(ship, team_id=0)
        for ship in team2_ships:
            self._battle_service.add_ship(ship, team_id=1)

        # Start the battle
        self._battle_service.start_battle()

        self.beams = []
        self.sim_tick_counter = 0
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
            log_info(status_msg)

            if s.is_derelict:
                warn_msg = f"CRITICAL WARNING: Ship {s.name} is DERELICT on start! (Bridge? Engines? LifeSupport? Power?)"
                self.engine.logger.log(warn_msg)
                log_warning(warn_msg)

            if s.total_thrust <= 0:
                warn_msg = f"WARNING: {s.name} has NO THRUST!"
                self.engine.logger.log(warn_msg)
                log_warning(warn_msg)

            if s.turn_speed <= 0.01:
                warn_msg = f"WARNING: {s.name} has LOW/NO TURN SPEED ({s.turn_speed:.4f})! Mass too high for thrusters?"
                self.engine.logger.log(warn_msg)
                log_warning(warn_msg)

    def handle_event(self, event):
        """Handle a single pygame event (IScene protocol)."""
        if event.type == pygame.KEYDOWN:
            self._handle_keydown(event)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = event.pos
            result = self.ui.handle_click(mx, my, event.button)
            if isinstance(result, tuple) and result[0] == "focus_ship":
                self.camera.target = result[1]
            elif result == "end_battle":
                self._battle_service.reset()
                self._trigger_return_to_setup()
            elif not result and event.button == 1:
                self.camera.target = None
        elif event.type == pygame.MOUSEWHEEL:
            self.ui.handle_scroll(event.y, self.screen_height)

    def _handle_keydown(self, event):
        """Handle keyboard shortcuts during battle."""
        key = event.key

        # Visual controls (from update_visuals)
        if key == pygame.K_F3:
            self.ui.show_overlay = not self.ui.show_overlay
        elif key == pygame.K_LEFTBRACKET:
            self._cycle_focus_ship(-1)
        elif key == pygame.K_RIGHTBRACKET:
            self._cycle_focus_ship(1)
        # Speed/pause controls (from BattleInputHandler)
        elif key == pygame.K_o:
            self.show_overlay = not self.show_overlay
        elif key == pygame.K_SPACE:
            self.sim_paused = not self.sim_paused
        elif key == pygame.K_COMMA:
            self.sim_speed_multiplier = max(MIN_SPEED_MULTIPLIER, self.sim_speed_multiplier / 2.0)
        elif key == pygame.K_PERIOD:
            self.sim_speed_multiplier = min(MAX_SPEED_MULTIPLIER, self.sim_speed_multiplier * 2.0)
        elif key == pygame.K_m:
            self.sim_speed_multiplier = NORMAL_SPEED
        elif key == pygame.K_SLASH:
            self.sim_speed_multiplier = UI_PAUSE_SPEED

    def update(self, dt: float):
        """Update battle simulation (IScene protocol).

        Args:
            dt: Time since last frame in seconds
        """
        if self.headless_mode:
            self._update_headless()
        else:
            self._update_visual(dt)

    def _update_headless(self):
        """Run headless battle simulation (fast mode without rendering)."""
        for _ in range(1000):
            self._run_single_tick()

            tick_limit_reached = self.sim_tick_counter >= 3000000

            if self.is_battle_over() or tick_limit_reached:
                self.print_headless_summary()
                self.engine.shutdown()
                self.headless_mode = False

                if self.test_mode:
                    log_debug("Headless test complete, returning to Combat Lab")
                    self._trigger_return_to_test_lab()
                else:
                    self._trigger_return_to_setup()
                return

        # Progress indicator
        if self.sim_tick_counter % 10000 == 0:
            t1 = sum(1 for s in self.ships if s.team_id == 0 and s.is_alive)
            t2 = sum(1 for s in self.ships if s.team_id == 1 and s.is_alive)
            log_debug(f"  Tick {self.sim_tick_counter}: Team1={t1}, Team2={t2}")

    def _update_visual(self, dt: float):
        """Update visual battle simulation with proper timing."""
        # Update visuals (camera, beams) - always run once per frame
        self._update_visual_effects(dt)

        # Update simulation
        if not self.sim_paused:
            tick_dt = PhysicsConfig.TICK_RATE
            speed_mult = self.sim_speed_multiplier

            if speed_mult > 10.0:
                # Max Speed / Turbo mode: Run fixed N ticks per frame
                ticks_to_run = int(speed_mult)

                t0 = time.time()
                for _ in range(ticks_to_run):
                    self._run_single_tick()
                t1 = time.time()

                elapsed = t1 - t0
                if elapsed > 0.05:
                    log_warning(f"Slow Frame: {ticks_to_run} ticks took {elapsed*1000:.1f}ms")

                self.tick_rate_count += ticks_to_run
            else:
                # Time-accurate simulation (slow/normal/fast)
                self._accumulator += dt * speed_mult

                # Safety cap
                if self._accumulator > 1.0:
                    self._accumulator = 1.0

                ticks_run_this_frame = 0
                while self._accumulator >= tick_dt:
                    self._run_single_tick()
                    self._accumulator -= tick_dt
                    ticks_run_this_frame += 1

                self.tick_rate_count += ticks_run_this_frame

        # Update tick rate for HUD
        self._update_tick_rate(dt)

    def _run_single_tick(self):
        """Run a single simulation tick."""
        # Check if test scenario has completed
        if self.test_mode and self.test_scenario and not self.test_completed:
            self.test_tick_count += 1

            # Call scenario's update method
            self.test_scenario.update(self.engine)

            # Check if test should end (engine handles all end conditions)
            if self.engine.is_battle_over():
                # Test complete - verify results and populate results dict
                log_debug(f"Test complete! ticks={self.test_tick_count}")

                # Populate results dict (similar to headless mode)
                if not hasattr(self.test_scenario, 'results') or not self.test_scenario.results:
                    self.test_scenario.results = {}
                self.test_scenario.results['ticks_run'] = self.test_tick_count
                self.test_scenario.results['ticks'] = self.test_tick_count  # Alias for consistency

                # Run verification (populates additional results)
                self.test_scenario.passed = self.test_scenario.verify(self.engine)
                log_debug(f"Test {'PASSED' if self.test_scenario.passed else 'FAILED'}")
                log_debug(f"Results populated: {list(self.test_scenario.results.keys())}")

                # Log test execution (for UI vs headless comparison)
                try:
                    from test_framework.runner import TestRunner
                    runner = TestRunner()
                    runner.log_test_execution(self.test_scenario, headless=False)
                except (ImportError, AttributeError, OSError) as e:
                    log_warning(f"Failed to log UI test execution: {e}")

                # Signal test completion (keep scenario reference for results retrieval)
                self.test_completed = True
                return  # Don't update engine anymore

        if not self.engine.is_battle_over():
            self.sim_tick_counter = self.engine.tick_counter + 1  # Sync tick counter
            # Delegated Update
            self.engine.update()

            # Sync Beams for Visuals
            for b in self.engine.recent_beams:
                b_visual = b.copy()
                b_visual['timer'] = 0.15
                self.beams.append(b_visual)

    def _update_visual_effects(self, dt: float):
        """Update visual effects like beams and camera."""
        # Update Beams
        for b in self.beams:
            b['timer'] -= dt
        self.beams = [b for b in self.beams if b['timer'] > 0]

        # Update Camera
        self.camera.update(dt)

    def _update_tick_rate(self, dt: float):
        """Update tick rate calculation for HUD display."""
        self.tick_rate_timer += dt
        if self.tick_rate_timer >= 1.0:
            self.current_tick_rate = self.tick_rate_count
            self.tick_rate_count = 0
            self.tick_rate_timer = 0.0

    def _trigger_return_to_setup(self):
        """Trigger return to setup via scene_callback."""
        if self.scene_callback:
            self.scene_callback("return_to_setup")

    def _trigger_return_to_test_lab(self):
        """Trigger return to Combat Lab via scene_callback."""
        if self.scene_callback:
            self.scene_callback("return_to_test_lab")

    def trigger_return_to_test_lab(self):
        """Public method to trigger return to Combat Lab.

        Used by BattleUI when the user clicks the "Return to Combat Lab" button.
        """
        self._trigger_return_to_test_lab()

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
            trail_length = UIConfig.TRAIL_LENGTH
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
    

    def draw_hud(self, screen, font=None, profiler_active=False):
        """Draw battle HUD elements (tick counters, speed indicator).

        Args:
            screen: Pygame screen surface
            font: Font for rendering text (uses default if None)
            profiler_active: Whether profiler is active
        """
        if font is None:
            if self._hud_font is None:
                self._hud_font = pygame.font.SysFont("arial", 20)
            font = self._hud_font

        width = screen.get_width()

        # Tick counters
        tick_text = f"Ticks: {self.sim_tick_counter:,}"
        rate_text = f"TPS: {self.current_tick_rate:,}/s"
        zoom_text = f"Zoom: {self.camera.zoom:.3f}x"

        # Draw to the right of seeker panel
        panel_offset = self.ui.seeker_panel.rect.width + 10
        screen.blit(font.render(tick_text, True, (180, 180, 180)), (panel_offset, 10))
        screen.blit(font.render(rate_text, True, (180, 180, 180)), (panel_offset, 35))
        screen.blit(font.render(zoom_text, True, (150, 200, 255)), (panel_offset, 60))

        # Speed indicator
        if self.sim_speed_multiplier >= 10.0:
            speed_val_text = "MAX SPEED"
        else:
            speed_val_text = f"{self.sim_speed_multiplier:.4g}x"

        if self.sim_paused:
            speed_text = f"PAUSED ({speed_val_text})"
        else:
            speed_text = f"Speed: {speed_val_text}"

        speed_color = (255, 100, 100) if self.sim_paused else (200, 200, 200)
        if self.sim_speed_multiplier < 1.0:
            speed_color = (255, 200, 100)
        elif self.sim_speed_multiplier > 1.0:
            speed_color = (100, 255, 100)

        screen.blit(font.render(speed_text, True, speed_color), (width // 2 - 50, 10))

        # Profiler indicator
        if profiler_active:
            prof_text = font.render("PROFILING ACTIVE", True, (255, 50, 50))
            screen.blit(prof_text, (width - 180, 10))

    def print_headless_summary(self):
        """Print summary of headless battle results."""
        # Skip summary for test mode - test framework handles results
        if self.test_mode:
            log_info(f"Headless test complete: {self.sim_tick_counter} ticks")
            return

        # For normal headless battles, print summary if UI supports it
        if hasattr(self.ui, 'print_headless_summary'):
            self.ui.print_headless_summary(self.headless_start_time, self.sim_tick_counter)
        else:
            log_info(f"Headless battle complete: {self.sim_tick_counter} ticks")
