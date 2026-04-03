"""
Battle UI - Handles all UI rendering and interaction for the BattleScreen.

Provides HUD elements, ship stats panels, seeker monitors, and battle control panel.
"""
import logging
import pygame
import math
from game.core.constants import AttackType

logger = logging.getLogger(__name__)
from game.ui.config import UIConfig
from game.ui.panels.battle_panels import ShipStatsPanel, SeekerMonitorPanel, BattleControlPanel
from game.ui.colors import (
    GRID_BG_BATTLE, DEBUG_TARGET_LINE, DEBUG_WEAPON_RANGE, DEBUG_AIM_POINT,
    DEBUG_FIRING_ARC,
)

class BattleUI:
    """Handles all UI rendering and interaction for the BattleScreen."""

    def __init__(self, scene, screen_width, screen_height):
        self.scene = scene
        self.width = screen_width
        self.height = screen_height

        # UI State
        self.show_overlay = False

        # Instantiate Panels
        stats_width = UIConfig.STATS_PANEL_WIDTH
        seeker_width = UIConfig.SEEKER_PANEL_WIDTH

        # Right Panel
        self.stats_panel = ShipStatsPanel(scene, screen_width - stats_width, 0, stats_width, screen_height)

        # Left Panel
        self.seeker_panel = SeekerMonitorPanel(scene, 0, 0, seeker_width, screen_height)
        
        # Control Panel (Overlay/Buttons)
        # We can give it full screen rect to handle overlays, or specific areas
        # The logic inside draws overlays or buttons. Let's give it full screen to manage global overlays.
        self.control_panel = BattleControlPanel(scene, 0, 0, screen_width, screen_height)

    def track_projectile(self, proj):
        """Add a projectile to the tracker if it is a missile."""
        if getattr(proj, 'type', None) == AttackType.MISSILE:
            self.seeker_panel.add_seeker(proj)

    def handle_resize(self, width, height):
        """Update UI elements for new resolution."""
        self.width = width
        self.height = height
        
        # Stats Panel (Right)
        stats_w = self.stats_panel.rect.width
        self.stats_panel.rect.x = width - stats_w
        self.stats_panel.rect.height = height
        # Invalidate surface cache
        self.stats_panel.surface = None
        
        # Seeker Panel (Left)
        self.seeker_panel.rect.height = height
        self.seeker_panel.surface = None
        
        # Control Panel (Overlay)
        self.control_panel.rect.width = width
        self.control_panel.rect.height = height
        self.control_panel.surface = None

    def draw(self, screen):
        """Draw the battle scene UI elements (excluding ships/projectiles)."""
        # Draw grid
        self.draw_grid(screen)

        if self.show_overlay:
            self.draw_debug_overlay(screen)

        # Draw Panels
        self.stats_panel.draw(screen)
        self.seeker_panel.draw(screen)
        self.control_panel.draw(screen)

    def handle_click(self, mx, my, button):
        """Handle mouse clicks. Returns True if click was handled."""

        # Control Panel (End Battle / View Results button)
        res = self.control_panel.handle_click(mx, my)
        if res:
            return res

        # Seeker Panel
        if self.seeker_panel.rect.collidepoint(mx, my):
             if self.seeker_panel.handle_click(mx, my):
                 return True

        # Stats Panel
        if self.stats_panel.rect.collidepoint(mx, my):
            res = self.stats_panel.handle_click(mx, my)
            if res:
                return res

        return False

    def handle_scroll(self, scroll_y, screen_height):
        """Handle mouse wheel scroll. Currently no scrollable content in battle view."""
        pass

    def draw_grid(self, screen):
        """Draw the background grid."""
        grid_spacing = UIConfig.GRID_SPACING
        sw, sh = screen.get_size()
        camera = self.scene.camera
        
        tl = camera.screen_to_world((0, 0))
        br = camera.screen_to_world((sw, sh))
        
        start_x = int(tl.x // grid_spacing) * grid_spacing
        end_x = int(br.x // grid_spacing + 1) * grid_spacing
        start_y = int(tl.y // grid_spacing) * grid_spacing
        end_y = int(br.y // grid_spacing + 1) * grid_spacing
        
        grid_color = GRID_BG_BATTLE
        
        for x in range(start_x, end_x + grid_spacing, grid_spacing):
            p1 = camera.world_to_screen(pygame.math.Vector2(x, start_y))
            p2 = camera.world_to_screen(pygame.math.Vector2(x, end_y))
            pygame.draw.line(screen, grid_color, p1, p2, 1)
        
        for y in range(start_y, end_y + grid_spacing, grid_spacing):
            p1 = camera.world_to_screen(pygame.math.Vector2(start_x, y))
            p2 = camera.world_to_screen(pygame.math.Vector2(end_x, y))
            pygame.draw.line(screen, grid_color, p1, p2, 1)

    def draw_debug_overlay(self, screen):
        """Draw debug information overlay for battle visualization.

        Renders the following debug elements for each ship:
        - Target lines: Blue lines from ship to current target
        - Weapon range circles: Red circles showing maximum weapon range
        - Aim points: Green crosses at predicted intercept positions
        - Firing arcs: Yellow arc lines showing turret rotation limits
        """
        camera = self.scene.camera
        for s in self.scene.ships:
            if not s.is_alive: continue
            
            # Target line
            if s.current_target and s.current_target.is_alive:
                start = camera.world_to_screen(s.position)
                end = camera.world_to_screen(s.current_target.position)
                pygame.draw.line(screen, DEBUG_TARGET_LINE, start, end, 1)
            
            # Weapon range
            max_range = 0
            for comp in s.get_components_by_ability('WeaponAbility', operational_only=True):
                weapon_ab = comp.get_ability('WeaponAbility')
                if weapon_ab and weapon_ab.range > max_range:
                    max_range = weapon_ab.range
            
            if max_range > 0:
                r_screen = int(max_range * camera.zoom)
                if r_screen > 0:
                    center = camera.world_to_screen(s.position)
                    pygame.draw.circle(screen, DEBUG_WEAPON_RANGE, (int(center.x), int(center.y)), r_screen, 1)
            
            # Aim point
            if hasattr(s, 'aim_point') and s.aim_point:
                aim_pos_screen = camera.world_to_screen(s.aim_point)
                length = 5
                pygame.draw.line(screen, DEBUG_AIM_POINT, (aim_pos_screen.x - length, aim_pos_screen.y - length),
                               (aim_pos_screen.x + length, aim_pos_screen.y + length), 2)
                pygame.draw.line(screen, DEBUG_AIM_POINT, (aim_pos_screen.x - length, aim_pos_screen.y + length),
                               (aim_pos_screen.x + length, aim_pos_screen.y - length), 2)
            
            # Firing arcs
            center = camera.world_to_screen(s.position)
            for comp in s.get_components_by_ability('WeaponAbility', operational_only=True):
                weapon_ab = comp.get_ability('WeaponAbility')
                if not weapon_ab:
                    continue
                ship_angle = s.angle
                facing = weapon_ab.facing_angle
                arc = weapon_ab.firing_arc
                rng = weapon_ab.range * camera.zoom

                start_angle = math.radians(ship_angle + facing - arc)
                end_angle = math.radians(ship_angle + facing + arc)

                x1 = center.x + math.cos(start_angle) * rng
                y1 = center.y + math.sin(start_angle) * rng
                x2 = center.x + math.cos(end_angle) * rng
                y2 = center.y + math.sin(end_angle) * rng

                pygame.draw.line(screen, DEBUG_FIRING_ARC, center, (x1, y1), 1)
                pygame.draw.line(screen, DEBUG_FIRING_ARC, center, (x2, y2), 1)

                try:
                    rect = pygame.Rect(center.x - rng, center.y - rng, rng*2, rng*2)
                    r_start = math.radians(ship_angle + facing - arc)
                    r_end = math.radians(ship_angle + facing + arc)
                    pygame.draw.arc(screen, DEBUG_FIRING_ARC, rect, -r_end, -r_start, 1)
                except (ValueError, pygame.error) as e:
                    # Arc drawing can fail with invalid rect dimensions (e.g., negative or zero)
                    logger.debug(f"Arc drawing failed for ship {s.name}: {e}")

