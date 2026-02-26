import logging
import pygame
from game.core.profiling import profile_action

logger = logging.getLogger(__name__)
from game.ui.config import UIConfig
from game.ui.colors import (
    HP_HEALTHY, HP_DAMAGED, HP_CRITICAL, RESOURCE_FUEL, TEXT_MUTED,
    TEAM_1_TEXT, TEAM_1_BANNER_BG, TEAM_2_TEXT, TEAM_2_BANNER_BG,
    TEXT_ITEM, TEXT_DIM, TEXT_SECONDARY, STATUS_DERELICT, BAR_BG,
    BG_PANEL_DARK, BORDER_PANEL, SEEKER_TITLE, STATUS_HIT_TEXT,
    STATUS_DESTROYED_TEXT, STATUS_ACTIVE_TEXT, STATUS_ACTIVE_BG,
    DAMAGE_TEXT, TARGET_TEXT, BTN_DANGER_BG, BTN_DANGER_HOVER,
    BTN_DANGER_BORDER, BTN_DANGER_TEXT, BTN_VICTORY_BG, BTN_VICTORY_BORDER,
    BTN_END_BG, BTN_END_BORDER, BTN_END_TEXT, WHITE, BTN_DANGER_HOVER_BORDER
)
from game.ui.fonts import get_default_font
from game.ui.panels.ship_stats_renderer import (
    draw_stat_bar, draw_ship_info_header, draw_ship_vitals,
    draw_ship_resources, draw_ship_combat_stats, draw_ship_weapons,
    draw_ship_components
)

class BattlePanel:
    """Base class for battle UI panels.

    PROJ-43: Provides _get_ships() for DTO-based access to ship data.
    """
    def __init__(self, scene, x, y, w, h):
        self.scene = scene
        self.rect = pygame.Rect(x, y, w, h)
        self.surface = None  # Cached surface

    def draw(self, screen):
        raise NotImplementedError

    def handle_click(self, mx, my):
        return False

    def draw_stat_bar(self, surface, x, y, width, height, pct, color):
        """Draw a progress bar - delegates to extracted function."""
        draw_stat_bar(surface, x, y, width, height, pct, color)

    def _get_ships(self):
        """Get ships from ui_service if available, otherwise fallback to scene.ships."""
        # Check if ui_service is explicitly set and has get_ships method
        ui_service = getattr(self.scene, 'ui_service', None)
        if ui_service is not None:
            try:
                # Try to get ships from ui_service
                ships = ui_service.get_ships()
                # Verify it's actually a list (not a MagicMock auto-created result)
                if isinstance(ships, list):
                    return ships
            except (AttributeError, TypeError) as e:
                logger.debug("Failed to get ships from ui_service, using fallback: %s", e)
        # Fallback to direct ships access
        return getattr(self.scene, 'ships', [])

class ShipStatsPanel(BattlePanel):
    """Panel for displaying ship statistics (Right side).

    PROJ-43: Uses ui_service.get_ships() to access ship data through DTOs
    when available, with fallback to scene.ships for direct access.
    Ship expansion state is tracked by ship ID (string) instead of object reference.
    """
    def __init__(self, scene, x, y, w, h):
        super().__init__(scene, x, y, w, h)
        self.expanded_ships = set()  # Set of ship IDs (strings)
        self.scroll_offset = 0
        self.content_height = 0

    def _get_ship_id(self, ship):
        """Get the ship ID for expansion tracking.

        PROJ-43: Supports both ShipDTO (has .id) and domain Ship objects
        (use .name as fallback identifier).
        """
        # Try to get .id first (for ShipDTO)
        ship_id = getattr(ship, 'id', None)
        if isinstance(ship_id, str):
            return ship_id
        # Fallback to .name (for domain Ship objects and mocks)
        ship_name = getattr(ship, 'name', None)
        if isinstance(ship_name, str):
            return ship_name
        # Last resort: use Python object id
        return str(id(ship))

    def _is_expanded(self, ship):
        """Check if a ship is expanded by its ID."""
        return self._get_ship_id(ship) in self.expanded_ships

    def _toggle_expanded(self, ship):
        """Toggle expansion state for a ship by its ID."""
        ship_id = self._get_ship_id(ship)
        if ship_id in self.expanded_ships:
            self.expanded_ships.discard(ship_id)
        else:
            self.expanded_ships.add(ship_id)

    def draw(self, screen):
        # Validate cache size
        if (self.surface is None or
            self.surface.get_width() != self.rect.width or
            self.surface.get_height() != self.rect.height):
            self.surface = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)

        # Draw to surface
        self.surface.fill((0, 0, 0, 0))
        self.surface.fill((*BG_PANEL_DARK, UIConfig.PANEL_ALPHA))

        font_title = get_default_font(UIConfig.FONT_TITLE)
        font_name = get_default_font(UIConfig.FONT_NAME)
        font_stat = get_default_font(UIConfig.FONT_STAT)

        y = 10 - self.scroll_offset
        panel_w = self.rect.width

        # PROJ-43: Use _get_ships() for DTO-based access
        ships = self._get_ships()

        # Team 1
        team1_ships = [s for s in ships if s.team_id == 0]
        team1_alive = sum(1 for s in team1_ships if s.is_alive and not s.is_derelict)

        title = font_title.render(f"TEAM 1 ({team1_alive}/{len(team1_ships)})", True, TEAM_1_TEXT)
        self.surface.blit(title, (10, y))
        y += 30

        for ship in team1_ships:
            y = self.draw_ship_entry(self.surface, ship, y, panel_w, font_name, font_stat, TEAM_1_BANNER_BG)

        y += 15

        # Team 2
        team2_ships = [s for s in ships if s.team_id == 1]
        team2_alive = sum(1 for s in team2_ships if s.is_alive and not s.is_derelict)

        title = font_title.render(f"TEAM 2 ({team2_alive}/{len(team2_ships)})", True, TEAM_2_TEXT)
        self.surface.blit(title, (10, y))
        y += 30

        for ship in team2_ships:
            y = self.draw_ship_entry(self.surface, ship, y, panel_w, font_name, font_stat, TEAM_2_BANNER_BG)

        self.content_height = y + self.scroll_offset

        screen.blit(self.surface, self.rect.topleft)
        pygame.draw.line(screen, BORDER_PANEL, self.rect.topleft, self.rect.bottomleft, 2)
        
    def draw_ship_entry(self, surface, ship, y, panel_w, font_name, font_stat, banner_color):
        """Draw a single ship entry."""
        # PROJ-43: Use _is_expanded() for ID-based expansion tracking
        arrow = "▼" if self._is_expanded(ship) else "►"
        status = ""
        if not ship.is_alive:
            status = " [DEAD]"
        elif ship.is_derelict:
            status = " [DERELICT]"

        color = TEXT_ITEM
        if not ship.is_alive:
            color = TEXT_DIM
        elif ship.is_derelict:
            color = STATUS_DERELICT
        bg_color = banner_color if ship.is_alive else BAR_BG

        pygame.draw.rect(surface, bg_color, (5, y, panel_w - 10, UIConfig.BANNER_HEIGHT))
        name_text = font_name.render(f"{arrow} {ship.name}{status}", True, color)
        surface.blit(name_text, (10, y + 3))
        y += UIConfig.SHIP_ENTRY_HEIGHT

        if self._is_expanded(ship):
            y = self.draw_ship_details(surface, ship, y, panel_w, font_stat)

        return y

    def draw_ship_details(self, surface, ship, y, panel_w, font):
        """Draw expanded ship details."""
        x_indent = UIConfig.INDENT
        bar_w = UIConfig.BAR_WIDTH
        bar_h = UIConfig.BAR_HEIGHT

        # Ship info header (file, AI strategy)
        y = draw_ship_info_header(surface, ship, x_indent, y, font)

        # Shield and HP
        y = draw_ship_vitals(surface, ship, x_indent, y, bar_w, bar_h, font)

        # Resources (fuel, energy, ammo, etc.)
        y = draw_ship_resources(surface, ship, x_indent, y, bar_w, bar_h, font)

        # Combat stats (speed, shots, crew, target)
        y = draw_ship_combat_stats(surface, ship, x_indent, y, font)

        # Weapons
        y = draw_ship_weapons(surface, ship, x_indent, y, panel_w, font)

        # Non-weapon components
        y = draw_ship_components(surface, ship, x_indent, y, font)

        return y

    def get_expanded_height(self, ship):
        base_height = 146
        if ship.max_shields > 0:
            base_height += 16
        comp_count = len(ship.get_all_components())
        comp_height = comp_count * 14
        return base_height + comp_height + 5

    @profile_action("Battle: ShipStats Click")
    def handle_click(self, mx, my):
        """Handle mouse click on the stats panel.

        PROJ-43: Uses _get_ships() for DTO-based access and tracks expansion
        by ship ID. Returns ("focus_ship", ship_id) for camera focus.
        """
        rel_x = mx
        rel_y = my + self.scroll_offset

        # PROJ-43: Use _get_ships() for DTO-based access
        ships = self._get_ships()
        team1_ships = [s for s in ships if s.team_id == 0]
        team2_ships = [s for s in ships if s.team_id == 1]

        keys = pygame.key.get_pressed()
        shift_held = keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]

        y_pos = 10 + 30  # Initial + header

        for ship in team1_ships:
            banner_height = 25
            if y_pos <= rel_y < y_pos + banner_height:
                if shift_held:
                    # PROJ-43: Return ship ID for camera focus
                    return ("focus_ship", self._get_ship_id(ship))
                # PROJ-43: Use _toggle_expanded() for ID-based tracking
                self._toggle_expanded(ship)
                return True
            y_pos += banner_height
            if self._is_expanded(ship):
                y_pos += self.get_expanded_height(ship)

        y_pos += 45
        for ship in team2_ships:
            banner_height = 25
            if y_pos <= rel_y < y_pos + banner_height:
                if shift_held:
                    # PROJ-43: Return ship ID for camera focus
                    return ("focus_ship", self._get_ship_id(ship))
                # PROJ-43: Use _toggle_expanded() for ID-based tracking
                self._toggle_expanded(ship)
                return True
            y_pos += banner_height
            if self._is_expanded(ship):
                y_pos += self.get_expanded_height(ship)

        return False


class SeekerMonitorPanel(BattlePanel):
    """Panel for monitoring missiles and seekers (Left side).

    PROJ-43: Expansion state is tracked by projectile ID (string) instead
    of object reference, similar to ShipStatsPanel.
    """
    def __init__(self, scene, x, y, w, h):
        super().__init__(scene, x, y, w, h)
        self.tracked_seekers = []
        self.expanded_seekers = set()  # Set of projectile IDs (strings)
        self.scroll_offset = 0
        self.clear_btn_rect = None
        self.content_height = 0

    def _get_projectile_id(self, proj):
        """Get the projectile ID for expansion tracking.

        PROJ-43: Supports both ProjectileDTO (has .id) and domain Projectile
        objects (use Python object id as fallback).
        """
        # Try to get .id first (for ProjectileDTO)
        proj_id = getattr(proj, 'id', None)
        if isinstance(proj_id, str):
            return proj_id
        # Last resort: use Python object id
        return str(id(proj))

    def _is_seeker_expanded(self, proj):
        """Check if a projectile is expanded by its ID."""
        return self._get_projectile_id(proj) in self.expanded_seekers

    def _toggle_seeker_expanded(self, proj):
        """Toggle expansion state for a projectile by its ID."""
        proj_id = self._get_projectile_id(proj)
        if proj_id in self.expanded_seekers:
            self.expanded_seekers.discard(proj_id)
        else:
            self.expanded_seekers.add(proj_id)

    def add_seeker(self, proj):
        self.tracked_seekers.append(proj)

    def clear_inactive(self):
        self.tracked_seekers = [p for p in self.tracked_seekers if p.status == 'active']

    def draw(self, screen):
        # Validate cache
        if (self.surface is None or 
            self.surface.get_width() != self.rect.width or 
            self.surface.get_height() != self.rect.height):
            self.surface = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
            
        self.surface.fill((0, 0, 0, 0))
        self.surface.fill((*BG_PANEL_DARK, 230))
        
        # Draw line on Right edge
        pygame.draw.line(self.surface, BORDER_PANEL, (self.rect.width - 1, 0), (self.rect.width - 1, self.rect.height), 2)
        
        font_title = get_default_font(28)
        font_name = get_default_font(22)
        font_stat = get_default_font(18)
        
        y = 10 - self.scroll_offset
        panel_w = self.rect.width
        
        active_count = sum(1 for p in self.tracked_seekers if p.status == 'active')
        total_count = len(self.tracked_seekers)
        title = font_title.render(f"SEEKER MONITOR ({active_count}/{total_count})", True, SEEKER_TITLE)
        self.surface.blit(title, (10, y))
        y += 30
        
        for proj in self.tracked_seekers:
            y = self.draw_seeker_entry(self.surface, proj, y, panel_w, font_name, font_stat)
            
        self.content_height = y + self.scroll_offset
        
        screen.blit(self.surface, self.rect.topleft)
        
        # Clear Inactive Button (Floating at bottom)
        btn_h = 30
        btn_y = self.rect.bottom - btn_h - 10
        btn_x = self.rect.x + 10
        self.clear_btn_rect = pygame.Rect(btn_x, btn_y, self.rect.width - 20, btn_h)
        
        mouse_pos = pygame.mouse.get_pos()
        hover = self.clear_btn_rect.collidepoint(mouse_pos)
        col = BTN_DANGER_HOVER if hover else BTN_DANGER_BG
        border = BTN_DANGER_HOVER_BORDER if hover else BTN_DANGER_BORDER
        
        pygame.draw.rect(screen, col, self.clear_btn_rect)
        pygame.draw.rect(screen, border, self.clear_btn_rect, 1)
        
        text = font_name.render("Clear Inactive", True, BTN_DANGER_TEXT)
        text_rect = text.get_rect(center=self.clear_btn_rect.center)
        screen.blit(text, text_rect)
    
    def draw_seeker_entry(self, surface, proj, y, panel_w, font_name, font_stat):
        # PROJ-43: Use _is_seeker_expanded() for ID-based expansion tracking
        arrow = "▼" if self._is_seeker_expanded(proj) else "►"
        status = getattr(proj, 'status', 'active')

        if status == 'hit':
            color = STATUS_HIT_TEXT
            status_str = "[HIT]"
            bg_color = BAR_BG
        elif status == 'miss':
            color = TEXT_MUTED
            status_str = "[MISS]"
            bg_color = BAR_BG
        elif status == 'destroyed':
            color = STATUS_DESTROYED_TEXT
            status_str = "[DEAD]"
            bg_color = BAR_BG
        else:
            color = STATUS_ACTIVE_TEXT
            status_str = "[ACT]"
            bg_color = STATUS_ACTIVE_BG

        pygame.draw.rect(surface, bg_color, (5, y, panel_w - 35, 22))

        name = "Missile"
        text = font_name.render(f"{arrow} {name} {status_str}", True, color)
        surface.blit(text, (10, y + 3))

        # X button
        if status != 'active':
            x_rect = pygame.Rect(panel_w - 25, y, 20, 22)
            pygame.draw.rect(surface, BTN_DANGER_BG, x_rect)
            pygame.draw.rect(surface, BTN_DANGER_BORDER, x_rect, 1)
            x_text = font_name.render("X", True, TEAM_2_TEXT)
            x_rect_center = x_rect.center
            surface.blit(x_text, (x_rect_center[0] - x_text.get_width()//2, x_rect_center[1] - x_text.get_height()//2))

        y += 25

        if self._is_seeker_expanded(proj):
            y = self.draw_seeker_details(surface, proj, y, panel_w, font_stat)

        return y

    def draw_seeker_details(self, surface, proj, y, panel_w, font):
        x_indent = 20
        bar_w = 80
        bar_h = 8
        
        # Speed
        p_vel_len = proj.velocity.length() * 100.0
        max_speed = getattr(proj, 'max_speed', p_vel_len) * 100.0 if getattr(proj, 'max_speed', 0) > 0 else p_vel_len
        txt = font.render(f"Speed: {p_vel_len:.0f} px/s", True, TEXT_SECONDARY)
        surface.blit(txt, (x_indent, y))
        y += 14
        
        # HP
        hp = getattr(proj, 'hp', 0)
        max_hp = getattr(proj, 'max_hp', hp) if getattr(proj, 'max_hp', 0) > 0 else max(hp, 1)
        hp_pct = hp / max_hp if max_hp > 0 else 0
        hp_color = HP_HEALTHY if hp_pct > 0.5 else (HP_DAMAGED if hp_pct > 0.2 else HP_CRITICAL)
        
        txt = font.render(f"HP: {hp:.0f}/{max_hp:.0f}", True, TEXT_SECONDARY)
        surface.blit(txt, (x_indent, y))
        self.draw_stat_bar(surface, x_indent + 80, y, bar_w, bar_h, hp_pct, hp_color)
        y += 14
        
        # Fuel
        endurance = getattr(proj, 'endurance', 0)
        max_endurance = getattr(proj, 'max_endurance', endurance) if getattr(proj, 'max_endurance', 0) > 0 else max(endurance, 1)
        fuel_pct = endurance / max_endurance if max_endurance > 0 else 0
        fuel_color = RESOURCE_FUEL if fuel_pct > 0.3 else HP_CRITICAL
        
        txt = font.render(f"Fuel: {endurance:.1f}s", True, TEXT_SECONDARY)
        surface.blit(txt, (x_indent, y))
        self.draw_stat_bar(surface, x_indent + 80, y, bar_w, bar_h, fuel_pct, fuel_color)
        y += 14
        
        # Damage
        txt = font.render(f"Damage: {proj.damage}", True, DAMAGE_TEXT)
        surface.blit(txt, (x_indent, y))
        y += 14
        
        # Target
        target = getattr(proj, 'target', None)
        t_name = target.name if target and hasattr(target, 'name') else "None"
        txt = font.render(f"Target: {t_name}", True, TARGET_TEXT)
        surface.blit(txt, (x_indent, y))
        y += UIConfig.ELEMENT_SPACING
        
        return y
    
    @profile_action("Battle: SeekerPanel Click")
    def handle_click(self, mx, my):
        """Handle mouse click on the seeker panel.

        PROJ-43: Uses ID-based expansion tracking via _toggle_seeker_expanded().
        """
        # Check Clear Inactive - this is in absolute screen coords because we draw it to screen
        if self.clear_btn_rect and self.clear_btn_rect.collidepoint(mx, my):
            self.clear_inactive()
            return True

        rel_x = mx - self.rect.x
        rel_y = my - self.rect.y + self.scroll_offset

        y_pos = 10 + 30

        for proj in self.tracked_seekers:
            rect_h = 22
            if y_pos <= rel_y < y_pos + rect_h:
                # Check X button
                x_btn_x_start = self.rect.width - 25
                if rel_x >= x_btn_x_start and rel_x <= x_btn_x_start + 20:
                    if proj.status != 'active':
                        self.tracked_seekers.remove(proj)
                        return True

                # PROJ-43: Use _toggle_seeker_expanded() for ID-based tracking
                self._toggle_seeker_expanded(proj)
                return True

            y_pos += 25
            if self._is_seeker_expanded(proj):
                y_pos += 72
        return False

class BattleControlPanel(BattlePanel):
    """Panel for battle control buttons.

    PROJ-43: Uses _get_ships() for DTO-based access to ship data.
    """
    def __init__(self, scene, x, y, w, h):
        super().__init__(scene, x, y, w, h)
        self.battle_end_button_rect = None
        self.end_battle_early_rect = None

    def draw(self, screen):
        # PROJ-43: Use _get_ships() for DTO-based access
        ships = self._get_ships()
        team1_alive = sum(1 for s in ships if s.team_id == 0 and s.is_alive and not s.is_derelict)
        team2_alive = sum(1 for s in ships if s.team_id == 1 and s.is_alive and not s.is_derelict)
        sw, sh = screen.get_size()

        # In test mode, defer to the engine's is_battle_over() which respects TIME_BASED mode
        # This prevents showing victory screen for single-ship tests that need to run for N ticks
        if hasattr(self.scene, 'test_mode') and self.scene.test_mode:
            # Test mode - use engine's is_battle_over() which handles TIME_BASED correctly
            is_over = self.scene.is_battle_over() if hasattr(self.scene, 'is_battle_over') else False
        else:
            # Normal battle - use HP-based check
            is_over = team1_alive == 0 or team2_alive == 0

        if is_over:
            # Battle Over
            if team1_alive > 0:
                winner_text, winner_color = "TEAM 1 WINS!", TEAM_1_TEXT
            elif team2_alive > 0:
                winner_text, winner_color = "TEAM 2 WINS!", TEAM_2_TEXT
            else:
                winner_text, winner_color = "DRAW!", TEXT_ITEM
            
            # Draw semi-transparent overlay
            if self.surface is None or self.surface.get_size() != self.rect.size:
                self.surface = pygame.Surface(self.rect.size, pygame.SRCALPHA)
            
            self.surface.fill((0, 0, 0, 150)) 
            screen.blit(self.surface, self.rect.topleft)
            
            win_font = get_default_font(72)
            win_surf = win_font.render(winner_text, True, winner_color)
            center_x = self.rect.centerx
            screen.blit(win_surf, (center_x - win_surf.get_width() // 2, sh // 2 - 80))
            
            btn_font = get_default_font(36)
            btn_w, btn_h = 250, 50
            btn_x = center_x - btn_w // 2
            btn_y = sh // 2
            
            pygame.draw.rect(screen, BTN_VICTORY_BG, (btn_x, btn_y, btn_w, btn_h))
            pygame.draw.rect(screen, BTN_VICTORY_BORDER, (btn_x, btn_y, btn_w, btn_h), 2)
            btn_text = btn_font.render("Return to Battle Setup", True, WHITE)
            screen.blit(btn_text, (btn_x + btn_w // 2 - btn_text.get_width() // 2, btn_y + 12))
            
            self.battle_end_button_rect = pygame.Rect(btn_x, btn_y, btn_w, btn_h)
            self.end_battle_early_rect = None
        else:
            # Ongoing battle - Floating End Button (Top Left typically)
            # Was drawn at (10, 70) in battle_ui. 
            # We can treat this panel as "fullscreen overlay" or just manage the button.
            # Let's draw it directly on screen.
            
            btn_font = get_default_font(24)
            btn_w, btn_h = 120, 30
            btn_x, btn_y = 10, 70
            
            # Ensure it's not covered by Seeker Panel (width 300)
            # Actually in the original code, the seeker panel is 300 wide. 10,70 is inside the seeker panel?
            # Looking at `draw_seeker_panel`: draws at (0,0), width 300.
            # `draw_battle_end_ui`: draws button at (10, 70).
            # So the End Battle button was ON TOP of the Seeker Panel?
            # Or hidden?
            # `draw` order in battle_ui: Grid, Overlay, Stats(Right), Seeker(Left), BattleEnd.
            # So BattleEnd is drawn LAST, on top of Seeker Panel.
            # We should probably put this button in SeekerPanel? Or keep it separate.
            # Requirement: "Create BattleControlPanel".
            
            pygame.draw.rect(screen, BTN_END_BG, (btn_x, btn_y, btn_w, btn_h))
            pygame.draw.rect(screen, BTN_END_BORDER, (btn_x, btn_y, btn_w, btn_h), 1)
            btn_text = btn_font.render("End Battle", True, BTN_END_TEXT)
            screen.blit(btn_text, (btn_x + btn_w // 2 - btn_text.get_width() // 2, btn_y + 7))
            
            self.end_battle_early_rect = pygame.Rect(btn_x, btn_y, btn_w, btn_h)
            self.battle_end_button_rect = None
    
    @profile_action("Battle: ControlPanel Click")
    def handle_click(self, mx, my):
        if self.battle_end_button_rect and self.battle_end_button_rect.collidepoint(mx, my):
            return "end_battle"
        if self.end_battle_early_rect and self.end_battle_early_rect.collidepoint(mx, my):
            return "end_battle"
        return False
