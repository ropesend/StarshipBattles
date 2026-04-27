"""Battle screen module for combat simulation and UI.

Uses BattleService as an abstraction layer over BattleEngine for cleaner
separation between UI and simulation logic.

Can optionally use BattleController for unified battle mode support
(manual, test, strategy, hypothetical battles).

PROJ-40: Removed unused AIController import. BattleService is instantiated at
runtime so must remain a runtime import.
"""
from __future__ import annotations

import logging
import pygame
import time
from typing import Any, Optional, List, TYPE_CHECKING

from game.core.config import PhysicsConfig

logger = logging.getLogger(__name__)
from game.ui.config import UIConfig
from game.ui.renderer.game_renderer import draw_ship
from game.ui.renderer.camera import Camera
from game.ui.screens.battle_ui import BattleUI
from game.simulation.services import BattleService
from game.ui.services.battle_ui_service import BattleUIService
from game.simulation.battle_controller import BattleController
# PROJ-126: Import AI factory from AI layer (UI can depend on AI)
from game.ai.ai_factory import AIControllerFactory
from game.ui.effects.hit_effects import (
    HitEffect, HitEffectType, create_hit_effect,
    update_effects, draw_effects, MAX_ACTIVE_EFFECTS,
)
from game.simulation.combat.combat_events import CombatEventType, CombatEvent
from game.ui.fonts import get_font
from game.ui.colors import (
    BG_BATTLE, PROJECTILE_STANDARD, HUD_TEXT, HUD_ZOOM_TEXT,
    SPEED_PAUSED, SPEED_SLOWMO, SPEED_FAST, TEXT_ITEM, PROJECTILE_GLOW,
    PROFILING_TEXT
)

if TYPE_CHECKING:
    from game.simulation.battle_controller import BattleController
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

        # NOQA: legacy-retained — Combat Lab instance vars kept for
        # back-compat with older visual test scenarios. Removal tracked
        # in follow-up to PROJ-270 Phase 10.
        self.headless_mode = False
        self.headless_start_time = None
        self.test_mode = False
        self.test_scenario = None
        self.test_tick_count = 0
        self.test_completed = False

        # Visual hit effects
        self.hit_effects: list = []

        # Font for HUD (no lazy-init needed - get_font() is cached)
        self._hud_font = get_font(20)

    # === Unified Entry Point ===

    def start_battle(self, controller: 'BattleController') -> None:
        """Start a battle using a configured BattleController.

        This is the SINGLE entry point for all battle modes. The controller
        must be fully configured and started before calling this method.

        Args:
            controller: Configured and started BattleController
        """
        self._controller = controller
        self._battle_service = controller.service
        self._ui_service = BattleUIService(self._battle_service)

        # Reset visual state
        self.beams = []
        self.hit_effects = []
        self.sim_tick_counter = 0
        self.sim_speed_multiplier = 1.0
        self._accumulator = 0.0

        config = controller.config
        self.sim_paused = config.start_paused if config else False
        self.headless_mode = config.headless if config else False

        # Subscribe to combat events for visual effects
        self._subscribe_combat_events()

        # Reset UI
        self.ui.expanded_ships = set()
        self.ui.stats_scroll_offset = 0

        # Fit camera to ships
        headless = config.headless if config else False
        if not headless and self.ships:
            self.camera.fit_objects(self.ships)

        logger.info(f"Battle started via unified entry: {len(self.ships)} ships")

    def get_controller(self) -> Optional['BattleController']:
        """Get the current BattleController (if any)."""
        return self._controller

    @property
    def engine(self) -> Any:
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

    def handle_resize(self, width, height) -> None:
        """Handle window resize."""
        self.screen_width = width
        self.screen_height = height
        self.camera.width = width
        self.camera.height = height
        
        # Update UI
        self.ui.handle_resize(width, height)

    @property
    def show_overlay(self) -> Any:
        return self.ui.show_overlay
    
    @show_overlay.setter
    def show_overlay(self, value) -> None:
        self.ui.show_overlay = value

    @property
    def stats_panel_width(self) -> Any:
        return self.ui.stats_panel.rect.width

    @property
    def ships(self) -> Any:
        return self.engine.ships

    @property
    def projectiles(self) -> Any:
        return self.engine.projectiles

    @property
    def ai_controllers(self) -> Any:
        return self.engine.ai_controllers

    def handle_event(self, event) -> None:
        """Handle a single pygame event (IScene protocol)."""
        if event.type == pygame.KEYDOWN:
            self._handle_keydown(event)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = event.pos
            result = self.ui.handle_click(mx, my, event.button)
            if isinstance(result, tuple) and result[0] == "focus_ship":
                focus_target = self._resolve_focus_target(result[1])
                if focus_target is not None:
                    self.camera.target = focus_target
            elif result == "end_battle":
                self._on_battle_ended()
            elif not result and event.button == 1:
                self.camera.target = None
        elif event.type == pygame.MOUSEWHEEL:
            self.camera.update_input(0, [event], allow_wasd=False)

    def _resolve_focus_target(self, focus_target) -> Any | None:
        """Resolve a panel focus result into something the camera can follow."""
        if focus_target is None:
            return None

        if hasattr(focus_target, 'position'):
            return focus_target

        engine = self.engine
        if engine is not None:
            for ship in engine.ships:
                if getattr(ship, 'id', None) == focus_target:
                    return ship

        ui_service = self.ui_service
        if ui_service is not None:
            try:
                for ship in ui_service.get_ships():
                    if getattr(ship, 'id', None) == focus_target:
                        return ship
            except (AttributeError, TypeError):
                pass

        return None

    def _handle_keydown(self, event) -> None:
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

    def update(self, dt: float) -> None:
        """Update battle simulation (IScene protocol).

        Args:
            dt: Time since last frame in seconds
        """
        if self.headless_mode:
            self._update_headless()
        else:
            self._update_visual(dt)

    def _update_headless(self) -> None:
        """Run headless battle simulation (fast mode without rendering)."""
        for _ in range(1000):
            self._run_single_tick()

            if self.is_battle_over():
                self.print_headless_summary()
                self.engine.shutdown()
                self._on_battle_ended()
                return

        # Progress indicator
        if self.sim_tick_counter % 10000 == 0:
            t1 = sum(1 for s in self.ships if s.team_id == 0 and s.is_alive)
            t2 = sum(1 for s in self.ships if s.team_id == 1 and s.is_alive)
            logger.debug(f"  Tick {self.sim_tick_counter}: Team1={t1}, Team2={t2}")

    def _update_visual(self, dt: float) -> None:
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
                    logger.warning(f"Slow Frame: {ticks_to_run} ticks took {elapsed*1000:.1f}ms")

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

    def _run_single_tick(self) -> None:
        """Run a single simulation tick via the controller."""
        if self.engine.is_battle_over():
            return

        # PROJ-270 Phase 10: controller is the only sanctioned per-tick
        # driver — eliminates the `else: self.engine.update()` bypass
        # that would otherwise skip outcome extraction and the retreat
        # manager.
        if self._controller is None:
            from game.core.exceptions import StateException
            raise StateException(
                "BattleScreen._run_single_tick called without a controller — "
                "invariant violation. Visual battles must always have a "
                "BattleController bound via start_battle()."
            )
        self._controller.update()

        self.sim_tick_counter = self.engine.tick_counter

        # Sync Beams for Visuals
        for b in self.engine.recent_beams:
            b_visual = b.copy()
            b_visual['timer'] = 0.15
            self.beams.append(b_visual)

    def _update_visual_effects(self, dt: float) -> None:
        """Update visual effects like beams, hit effects, and camera."""
        # Update Beams
        for b in self.beams:
            b['timer'] -= dt
        self.beams = [b for b in self.beams if b['timer'] > 0]

        # Update hit effects
        self.hit_effects = update_effects(self.hit_effects, dt)

        # Process camera input (middle-mouse pan, arrow keys)
        # WASD disabled to avoid conflicts with speed/pause keys
        self.camera.update_input(dt, [], allow_wasd=False)

        # Update Camera (smooth zoom, target follow)
        self.camera.update(dt)

    def _update_tick_rate(self, dt: float) -> None:
        """Update tick rate calculation for HUD display."""
        self.tick_rate_timer += dt
        if self.tick_rate_timer >= 1.0:
            self.current_tick_rate = self.tick_rate_count
            self.tick_rate_count = 0
            self.tick_rate_timer = 0.0

    def _on_battle_ended(self) -> None:
        """Unified exit path for all battle modes.

        Routes to results screen or directly to destination based on config.
        Pulls `BattleOutcome` from the controller (populated by
        `BattleController._extract_outcome_on_battle_end`) and feeds it to
        `extract_battle_results`.
        """
        from game.ui.screens.battle_results_data import extract_battle_results

        config = self._controller.config if self._controller else None
        dest = config.return_destination.value if config else "battle_setup"
        show = config.show_results if config else True

        if show:
            outcome = self._controller.get_outcome()
            results = extract_battle_results(outcome, return_destination=dest)
            self._battle_service.reset()
            if self.scene_callback:
                self.scene_callback("show_results",
                    results=results,
                    return_destination=dest)
        else:
            self._battle_service.reset()
            if self.scene_callback:
                self.scene_callback("return_to_destination", destination=dest)

    def _cycle_focus_ship(self, direction) -> None:
        """Cycle camera focus through alive ships."""
        alive_ships = [s for s in self.engine.ships if s.is_alive]
        if not alive_ships:
            return

        current_idx = -1
        if self.camera.target in alive_ships:
            current_idx = alive_ships.index(self.camera.target)
        
        new_idx = (current_idx + direction) % len(alive_ships)
        self.camera.target = alive_ships[new_idx]


    # === Combat Event Handlers (Visual Effects) ===

    def _subscribe_combat_events(self) -> None:
        """Subscribe to combat events on the engine's event bus."""
        bus = self.engine.combat_events
        bus.subscribe(CombatEventType.SHIELD_HIT, self._on_shield_hit)
        bus.subscribe(CombatEventType.COMPONENT_HIT, self._on_component_hit)
        bus.subscribe(CombatEventType.COMPONENT_DESTROYED, self._on_component_destroyed)
        bus.subscribe(CombatEventType.SHIP_DESTROYED, self._on_ship_destroyed)

    def _add_hit_effect(self, effect_type: HitEffectType, ship) -> None:
        """Create and add a hit effect, respecting the cap."""
        if len(self.hit_effects) >= MAX_ACTIVE_EFFECTS:
            return
        self.hit_effects.append(create_hit_effect(effect_type, ship))

    def _on_shield_hit(self, event: CombatEvent) -> None:
        self._add_hit_effect(HitEffectType.SHIELD_HIT, event.target_ship)

    def _on_component_hit(self, event: CombatEvent) -> None:
        self._add_hit_effect(HitEffectType.ARMOR_HIT, event.target_ship)

    def _on_component_destroyed(self, event: CombatEvent) -> None:
        self._add_hit_effect(HitEffectType.COMPONENT_DESTROYED, event.target_ship)

    def _on_ship_destroyed(self, event: CombatEvent) -> None:
        self._add_hit_effect(HitEffectType.SHIP_DESTROYED, event.target_ship)

    def is_battle_over(self) -> Any:
        """Check if the battle has ended."""
        # In test mode, battle is over when scenario completes
        if self.test_mode and self.test_scenario is None and self.test_tick_count > 0:
            return True  # Test has completed
        return self._battle_service.is_battle_over()

    def get_winner(self) -> Any:
        """Get the winning team. Returns 0, 1, or -1 for draw."""
        return self._battle_service.get_winner()
    
    def draw(self, screen) -> None:
        """Draw the battle scene."""
        screen.fill(BG_BATTLE)
        
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
            
            color = getattr(p, 'color', PROJECTILE_STANDARD)
            pygame.draw.line(screen, color, start, end, 3)
            pygame.draw.circle(screen, PROJECTILE_GLOW, (int(end[0]), int(end[1])), int(getattr(p, 'radius', 4)))
        
        # Draw ships
        self.camera.show_overlay = self.ui.show_overlay # Hack to pass state to renderer
        for s in self.engine.ships:
            draw_ship(screen, s, self.camera)
        
        # Draw beams
        for b in self.beams:
            start = self.camera.world_to_screen(b['start'])
            end = self.camera.world_to_screen(b['end'])
            pygame.draw.line(screen, b['color'], start, end, 3)

        # Draw hit effects
        draw_effects(self.hit_effects, screen, self.camera)

        # 3. UI Overlays
        if self.ui.show_overlay:
            self.ui.draw_debug_overlay(screen)
        
        # Seeker panel (Left)
        self.ui.seeker_panel.draw(screen)
        
        # Stats panel (Right)
        self.ui.stats_panel.draw(screen)
        
        # Battle end UI / Controls
        self.ui.control_panel.draw(screen)
    

    def draw_hud(self, screen, font=None, profiler_active=False) -> None:
        """Draw battle HUD elements (tick counters, speed indicator).

        Args:
            screen: Pygame screen surface
            font: Font for rendering text (uses default if None)
            profiler_active: Whether profiler is active
        """
        if font is None:
            font = self._hud_font

        width = screen.get_width()

        # Tick counters
        tick_text = f"Ticks: {self.sim_tick_counter:,}"
        rate_text = f"TPS: {self.current_tick_rate:,}/s"
        zoom_text = f"Zoom: {self.camera.zoom:.3f}x"

        # Draw to the right of seeker panel
        panel_offset = self.ui.seeker_panel.rect.width + 10
        screen.blit(font.render(tick_text, True, HUD_TEXT), (panel_offset, 10))
        screen.blit(font.render(rate_text, True, HUD_TEXT), (panel_offset, 35))
        screen.blit(font.render(zoom_text, True, HUD_ZOOM_TEXT), (panel_offset, 60))

        # Speed indicator
        if self.sim_speed_multiplier >= 10.0:
            speed_val_text = "MAX SPEED"
        else:
            speed_val_text = f"{self.sim_speed_multiplier:.4g}x"

        if self.sim_paused:
            speed_text = f"PAUSED ({speed_val_text})"
        else:
            speed_text = f"Speed: {speed_val_text}"

        speed_color = SPEED_PAUSED if self.sim_paused else TEXT_ITEM
        if self.sim_speed_multiplier < 1.0:
            speed_color = SPEED_SLOWMO
        elif self.sim_speed_multiplier > 1.0:
            speed_color = SPEED_FAST

        screen.blit(font.render(speed_text, True, speed_color), (width // 2 - 50, 10))

        # Profiler indicator
        if profiler_active:
            prof_text = font.render("PROFILING ACTIVE", True, PROFILING_TEXT)
            screen.blit(prof_text, (width - 180, 10))

        # PROJ-271 Phase 8 Task 8.2: active external modifier indicator.
        # Shows users that fleet/environmental modifiers (storm,
        # boosters, suppressors) are live — otherwise their numeric
        # effect on ship stats is invisible.
        mod_lines = self.get_active_modifier_labels()
        if mod_lines:
            y_offset = 90
            title = font.render("Active Modifiers:", True, HUD_TEXT)
            screen.blit(title, (panel_offset, y_offset))
            for i, line in enumerate(mod_lines):
                surf = font.render(line, True, HUD_TEXT)
                screen.blit(surf, (panel_offset, y_offset + 22 + i * 18))

    def get_active_modifier_labels(self) -> list:
        """Return formatted active-modifier lines for HUD display.

        PROJ-271 Phase 8 Task 8.2: surfaces `FleetAuraManager.get_active_bonuses`
        for user-visible modifier feedback. Returns an empty list when
        no controller/engine is available or no modifiers are active.
        """
        controller = getattr(self, '_controller', None)
        if controller is None:
            return []
        service = getattr(controller, '_service', None) or getattr(controller, 'service', None)
        if service is None:
            return []
        try:
            engine = service.get_engine()
        except (AttributeError, TypeError):
            return []
        if engine is None:
            return []
        aura_manager = getattr(engine, 'aura_manager', None)
        if aura_manager is None:
            return []
        lines = []
        # Collect team IDs present in the battle.
        team_ids = sorted({s.team_id for s in getattr(engine, 'ships', [])})
        for team_id in team_ids:
            try:
                bonuses = aura_manager.get_active_bonuses(team_id)
            except (AttributeError, TypeError):
                continue
            for b in bonuses:
                ability = b.get('ability', '?')
                value = b.get('value', 0)
                source = b.get('source', '?')
                # PROJ-272 Phase 11: non-numeric guard. Defensive skip
                # if a future aura produces a non-numeric value — don't
                # crash the HUD.
                if not isinstance(value, (int, float)):
                    logger.warning(
                        "get_active_modifier_labels: non-numeric value %r "
                        "for ability %r, skipping.", value, ability,
                    )
                    continue
                # PROJ-272 Phase 11: stat-key-aware sign format.
                # `_mult` keys → "0.75x" (no sign, clear multiplicative)
                # `_add` keys → "+50.00" / "-20.00" (explicit additive direction)
                # Other keys → neutral "{value:.2f}"
                if ability.endswith('_mult'):
                    formatted = f"{value:.2f}x"
                elif ability.endswith('_add'):
                    formatted = f"{value:+.2f}"
                else:
                    formatted = f"{value:.2f}"
                lines.append(f"T{team_id} {ability}={formatted} ({source})")
        return lines

    def print_headless_summary(self) -> None:
        """Print summary of headless battle results."""
        # Skip summary for test mode - test framework handles results
        if self.test_mode:
            logger.info(f"Headless test complete: {self.sim_tick_counter} ticks")
            return

        # For normal headless battles, print summary if UI supports it
        if hasattr(self.ui, 'print_headless_summary'):
            self.ui.print_headless_summary(self.headless_start_time, self.sim_tick_counter)
        else:
            logger.info(f"Headless battle complete: {self.sim_tick_counter} ticks")
