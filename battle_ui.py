
import pygame
import math
import time
from components import Weapon
from ship import LayerType
from ai import COMBAT_STRATEGIES
from rendering import draw_ship, draw_bar

class BattleInterface:
    """Handles all UI rendering and interaction for the BattleScene."""
    
    def __init__(self, scene, screen_width, screen_height):
        self.scene = scene
        self.width = screen_width
        self.height = screen_height
        
        # UI state
        self.stats_panel_width = 450
        self.seeker_panel_width = 300
        self.expanded_ships = set()
        self.stats_scroll_offset = 0
        self.stats_panel_content_height = 0
        self.show_overlay = False
        
        # Seeker Panel State
        self.tracked_seekers = [] # List of projectiles
        self.expanded_seekers = set()
        self.seeker_scroll_offset = 0
        self.seeker_panel_content_height = 0
        self.clear_vars_rect = None # Rect for "Clear Inactive" button
        
        # Surface Caching
        self.stats_panel_surface = None
        self.seeker_panel_surface = None
        
        # Interaction Rects
        self.battle_end_button_rect = None
        self.end_battle_early_rect = None

    def track_projectile(self, proj):
        """Add a projectile to the tracker if it is a missile."""
        if getattr(proj, 'type', '') == 'missile':
            self.tracked_seekers.append(proj)

    def draw(self, screen):
        """Draw the battle scene UI elements (excluding ships/projectiles)."""
        # Draw grid
        self.draw_grid(screen)
        
        # Note: Ships, projectiles, and beams are drawn by the Scene itself 
        # because they are part of the world simulation, but we could move them here too.
        # For now, we follow the plan to move UI overlays.
        
        if self.show_overlay:
            self.draw_debug_overlay(screen)
        
        # Stats panel (Right)
        self.draw_ship_stats_panel(screen)
        
        # Seeker panel (Left)
        self.draw_seeker_panel(screen)
        
        # Battle end UI
        self.draw_battle_end_ui(screen)

    def draw_seeker_panel(self, screen):
        """Draw the seeker monitor panel on the left side."""
        sw, sh = screen.get_size()
        panel_w = self.seeker_panel_width
        
        # Ensure cached surface exists and is correct size
        if (self.seeker_panel_surface is None or 
            self.seeker_panel_surface.get_width() != panel_w or 
            self.seeker_panel_surface.get_height() != sh):
            self.seeker_panel_surface = pygame.Surface((panel_w, sh), pygame.SRCALPHA)
            
        # Clear surface
        self.seeker_panel_surface.fill((0, 0, 0, 0)) # Fully transparent clear
        
        # Fill background
        self.seeker_panel_surface.fill((20, 25, 35, 230))
        
        # Draw line on Right edge (separator from game)
        pygame.draw.line(self.seeker_panel_surface, (60, 60, 80), (panel_w - 1, 0), (panel_w - 1, sh), 2)
        
        font_title = pygame.font.Font(None, 28)
        font_name = pygame.font.Font(None, 22)
        font_stat = pygame.font.Font(None, 18)
        
        y = 10 - self.seeker_scroll_offset
        
        # Header with active/total count
        active_count = sum(1 for p in self.tracked_seekers if p.status == 'active')
        total_count = len(self.tracked_seekers)
        title = font_title.render(f"SEEKER MONITOR ({active_count}/{total_count})", True, (255, 200, 100))
        self.seeker_panel_surface.blit(title, (10, y))
        y += 30
        
        # Draw seeker entries
        for i, proj in enumerate(self.tracked_seekers):
            y = self.draw_seeker_entry(self.seeker_panel_surface, proj, y, panel_w, font_name, font_stat)
            
        self.seeker_panel_content_height = y + self.seeker_scroll_offset
        
        screen.blit(self.seeker_panel_surface, (0, 0))
        
        # Floating Clear Button at bottom of left panel (Draw directly on screen to be on top of scrolling?)
        # Actually it was floating at bottom, so it should be on screen relative to window, not scrolled
        # But previous code drew it AFTER blitting panel_surf, so it was on top.
        # We can keep drawing it on screen or on panel. If on panel, it scrolls if we scroll panel?
        # No, previous code calculated `btn_y = sh - btn_h - 10`. That is fixed screen position.
        # So we should draw it on screen AFTER blitting the panel surface.
        
        btn_h = 30
        btn_y = sh - btn_h - 10
        btn_x = 10  # Left side
        btn_rect = pygame.Rect(btn_x, btn_y, panel_w - 20, btn_h)
        self.clear_vars_rect = btn_rect
        
        mouse_pos = pygame.mouse.get_pos()
        hover = btn_rect.collidepoint(mouse_pos)
        col = (60, 40, 40) if hover else (50, 30, 30)
        border = (150, 80, 80) if hover else (100, 60, 60)
        
        pygame.draw.rect(screen, col, btn_rect)
        pygame.draw.rect(screen, border, btn_rect, 1)
        
        text = font_name.render("Clear Inactive", True, (255, 150, 150))
        screen.blit(text, (btn_rect.centerx - text.get_width()//2, btn_rect.centery - text.get_height()//2))

    def draw_seeker_entry(self, surface, proj, y, panel_w, font_name, font_stat):
        """Draw single seeker entry."""
        arrow = "▼" if proj in self.expanded_seekers else "►"
        
        status = getattr(proj, 'status', 'active')
        color = (255, 255, 255)
        bg_color = (40, 40, 40)
        
        if status == 'hit':
            color = (50, 255, 50)
            status_str = "[HIT]"
        elif status == 'miss':
            color = (150, 150, 150)
            status_str = "[MISS]"
        elif status == 'destroyed':
            color = (255, 50, 50)
            status_str = "[DEAD]"
        else:
            color = (255, 255, 100)
            status_str = "[ACT]"
            bg_color = (50, 50, 60)
            
        pygame.draw.rect(surface, bg_color, (5, y, panel_w - 35, 22))
        
        # Name
        name = "Missile" # Generic
        text = font_name.render(f"{arrow} {name} {status_str}", True, color)
        surface.blit(text, (10, y + 3))
        
        # X button to remove
        if status != 'active':
            x_rect = pygame.Rect(panel_w - 25, y, 20, 22)
            pygame.draw.rect(surface, (60, 30, 30), x_rect)
            pygame.draw.rect(surface, (100, 50, 50), x_rect, 1)
            x_text = font_name.render("X", True, (255, 100, 100))
            surface.blit(x_text, (x_rect.centerx - x_text.get_width()//2, x_rect.centery - x_text.get_height()//2))
            
            # Use a special way to track clicks? 
            # We defer click handling to handle_click.
        
        y += 25
        
        if proj in self.expanded_seekers:
            y = self.draw_seeker_details(surface, proj, y, panel_w, font_stat)
            
        return y

    def draw_seeker_details(self, surface, proj, y, panel_w, font):
        """Draw expanded seeker details with stats and progress bars."""
        x_indent = 20
        bar_w = 80
        bar_h = 8
        
        # Speed
        p_vel_len = proj.velocity.length() * 100.0  # Pixels/sec approx (ticks * 100)
        max_speed = getattr(proj, 'max_speed', p_vel_len) * 100.0 if getattr(proj, 'max_speed', 0) > 0 else p_vel_len
        txt = font.render(f"Speed: {p_vel_len:.0f} px/s", True, (180, 180, 180))
        surface.blit(txt, (x_indent, y))
        y += 14
        
        # HP with bar
        hp = getattr(proj, 'hp', 0)
        max_hp = getattr(proj, 'max_hp', hp) if getattr(proj, 'max_hp', 0) > 0 else max(hp, 1)
        hp_pct = hp / max_hp if max_hp > 0 else 0
        hp_color = (0, 255, 0) if hp_pct > 0.5 else ((255, 200, 0) if hp_pct > 0.2 else (255, 50, 50))
        
        txt = font.render(f"HP: {hp:.0f}/{max_hp:.0f}", True, (180, 180, 180))
        surface.blit(txt, (x_indent, y))
        self.draw_stat_bar(surface, x_indent + 80, y, bar_w, bar_h, hp_pct, hp_color)
        y += 14
        
        # Endurance (Fuel) with bar
        endurance = getattr(proj, 'endurance', 0)
        max_endurance = getattr(proj, 'max_endurance', endurance) if getattr(proj, 'max_endurance', 0) > 0 else max(endurance, 1)
        fuel_pct = endurance / max_endurance if max_endurance > 0 else 0
        fuel_color = (255, 165, 0) if fuel_pct > 0.3 else (255, 50, 50)
        
        txt = font.render(f"Fuel: {endurance:.1f}s", True, (180, 180, 180))
        surface.blit(txt, (x_indent, y))
        self.draw_stat_bar(surface, x_indent + 80, y, bar_w, bar_h, fuel_pct, fuel_color)
        y += 14
        
        # Damage
        txt = font.render(f"Damage: {proj.damage}", True, (255, 150, 150))
        surface.blit(txt, (x_indent, y))
        y += 14
        
        # Target
        target = getattr(proj, 'target', None)
        t_name = target.name if target and hasattr(target, 'name') else "None"
        txt = font.render(f"Target: {t_name}", True, (150, 200, 150))
        surface.blit(txt, (x_indent, y))
        y += 16
        
        return y

    def draw_grid(self, screen):
        """Draw the background grid."""
        grid_spacing = 5000
        sw, sh = screen.get_size()
        camera = self.scene.camera
        
        tl = camera.screen_to_world((0, 0))
        br = camera.screen_to_world((sw, sh))
        
        start_x = int(tl.x // grid_spacing) * grid_spacing
        end_x = int(br.x // grid_spacing + 1) * grid_spacing
        start_y = int(tl.y // grid_spacing) * grid_spacing
        end_y = int(br.y // grid_spacing + 1) * grid_spacing
        
        grid_color = (30, 30, 50)
        
        for x in range(start_x, end_x + grid_spacing, grid_spacing):
            p1 = camera.world_to_screen(pygame.math.Vector2(x, start_y))
            p2 = camera.world_to_screen(pygame.math.Vector2(x, end_y))
            pygame.draw.line(screen, grid_color, p1, p2, 1)
        
        for y in range(start_y, end_y + grid_spacing, grid_spacing):
            p1 = camera.world_to_screen(pygame.math.Vector2(start_x, y))
            p2 = camera.world_to_screen(pygame.math.Vector2(end_x, y))
            pygame.draw.line(screen, grid_color, p1, p2, 1)

    def draw_debug_overlay(self, screen):
        """Draw debug information overlay."""
        camera = self.scene.camera
        for s in self.scene.ships:
            if not s.is_alive: continue
            
            # Target line
            if s.current_target and s.current_target.is_alive:
                start = camera.world_to_screen(s.position)
                end = camera.world_to_screen(s.current_target.position)
                pygame.draw.line(screen, (0, 0, 255), start, end, 1)
            
            # Weapon range
            max_range = 0
            for layer in s.layers.values():
                for comp in layer['components']:
                    if isinstance(comp, Weapon) and comp.is_active:
                        if comp.range > max_range:
                            max_range = comp.range
            
            if max_range > 0:
                r_screen = int(max_range * camera.zoom)
                if r_screen > 0:
                    center = camera.world_to_screen(s.position)
                    pygame.draw.circle(screen, (100, 100, 100), (int(center.x), int(center.y)), r_screen, 1)
            
            # Aim point
            if hasattr(s, 'aim_point') and s.aim_point:
                aim_pos_screen = camera.world_to_screen(s.aim_point)
                length = 5
                color = (0, 100, 255)
                pygame.draw.line(screen, color, (aim_pos_screen.x - length, aim_pos_screen.y - length), 
                               (aim_pos_screen.x + length, aim_pos_screen.y + length), 2)
                pygame.draw.line(screen, color, (aim_pos_screen.x - length, aim_pos_screen.y + length), 
                               (aim_pos_screen.x + length, aim_pos_screen.y - length), 2)
            
            # Firing arcs
            center = camera.world_to_screen(s.position)
            for layer in s.layers.values():
                for comp in layer['components']:
                    if isinstance(comp, Weapon) and comp.is_active:
                        ship_angle = s.angle
                        facing = comp.facing_angle
                        arc = comp.firing_arc
                        rng = comp.range * camera.zoom
                        
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

    def draw_battle_end_ui(self, screen):
        """Draw battle end overlay or ongoing battle buttons."""
        team1_alive = sum(1 for s in self.scene.ships if s.team_id == 0 and s.is_alive and not getattr(s, 'is_derelict', False))
        team2_alive = sum(1 for s in self.scene.ships if s.team_id == 1 and s.is_alive and not getattr(s, 'is_derelict', False))
        sw, sh = screen.get_size()
        
        if team1_alive == 0 or team2_alive == 0:
            # Battle over overlay (between left and right panels)
            overlay_w = sw - self.stats_panel_width - self.seeker_panel_width
            overlay = pygame.Surface((overlay_w, sh), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            screen.blit(overlay, (self.seeker_panel_width, 0))
            
            if team1_alive > 0:
                winner_text, winner_color = "TEAM 1 WINS!", (100, 200, 255)
            elif team2_alive > 0:
                winner_text, winner_color = "TEAM 2 WINS!", (255, 100, 100)
            else:
                winner_text, winner_color = "DRAW!", (200, 200, 200)
            
            win_font = pygame.font.Font(None, 72)
            win_surf = win_font.render(winner_text, True, winner_color)
            center_x = self.seeker_panel_width + (sw - self.stats_panel_width - self.seeker_panel_width) // 2
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

    def draw_ship_stats_panel(self, screen):
        """Draw the ship stats panel on the right side."""
        sw, sh = screen.get_size()
        panel_x = sw - self.stats_panel_width
        panel_w = self.stats_panel_width
        
        # Ensure cached surface
        if (self.stats_panel_surface is None or 
            self.stats_panel_surface.get_width() != panel_w or 
            self.stats_panel_surface.get_height() != sh):
            self.stats_panel_surface = pygame.Surface((panel_w, sh), pygame.SRCALPHA)
            
        # Clear
        self.stats_panel_surface.fill((0, 0, 0, 0)) # Fully transparent
        self.stats_panel_surface.fill((20, 25, 35, 230)) # Backfill
        
        font_title = pygame.font.Font(None, 28)
        font_name = pygame.font.Font(None, 22)
        font_stat = pygame.font.Font(None, 18)
        
        y = 10 - self.stats_scroll_offset
        
        # Team 1
        team1_ships = [s for s in self.scene.ships if s.team_id == 0]
        team1_alive = sum(1 for s in team1_ships if s.is_alive and not getattr(s, 'is_derelict', False))
        
        title = font_title.render(f"TEAM 1 ({team1_alive}/{len(team1_ships)})", True, (100, 200, 255))
        self.stats_panel_surface.blit(title, (10, y))
        y += 30
        
        for ship in team1_ships:
            y = self.draw_ship_entry(self.stats_panel_surface, ship, y, panel_w, font_name, font_stat, (40, 60, 80))
        
        y += 15
        
        # Team 2
        team2_ships = [s for s in self.scene.ships if s.team_id == 1]
        team2_alive = sum(1 for s in team2_ships if s.is_alive and not getattr(s, 'is_derelict', False))
        
        title = font_title.render(f"TEAM 2 ({team2_alive}/{len(team2_ships)})", True, (255, 100, 100))
        self.stats_panel_surface.blit(title, (10, y))
        y += 30
        
        for ship in team2_ships:
            y = self.draw_ship_entry(self.stats_panel_surface, ship, y, panel_w, font_name, font_stat, (80, 40, 40))
        
        self.stats_panel_content_height = y + self.stats_scroll_offset
        
        screen.blit(self.stats_panel_surface, (panel_x, 0))
        pygame.draw.line(screen, (60, 60, 80), (panel_x, 0), (panel_x, sh), 2)

    def draw_ship_entry(self, surface, ship, y, panel_w, font_name, font_stat, banner_color):
        """Draw a single ship entry in the stats panel. Returns new y position."""
        arrow = "▼" if ship in self.expanded_ships else "►"
        status = ""
        if not ship.is_alive:
            status = " [DEAD]"
        elif getattr(ship, 'is_derelict', False):
            status = " [DERELICT]"
            
        color = (200, 200, 200)
        if not ship.is_alive:
            color = (100, 100, 100)
        elif getattr(ship, 'is_derelict', False):
            color = (255, 165, 0) # Orange for Derelict
        bg_color = banner_color if ship.is_alive else (40, 40, 40)
        
        pygame.draw.rect(surface, bg_color, (5, y, panel_w - 10, 22))
        name_text = font_name.render(f"{arrow} {ship.name}{status}", True, color)
        surface.blit(name_text, (10, y + 3))
        y += 25
        
        if ship in self.expanded_ships:
            y = self.draw_ship_details(surface, ship, y, panel_w, font_stat)
        
        return y

    def draw_ship_details(self, surface, ship, y, panel_w, font):
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
        
        # Shield Bar
        if ship.max_shields > 0:
            shield_pct = ship.current_shields / ship.max_shields
            text = font.render(f"Shield: {int(ship.current_shields)}/{int(ship.max_shields)}", True, (180, 180, 180))
            surface.blit(text, (x_indent, y))
            self.draw_stat_bar(surface, x_indent + 100, y, bar_w, bar_h, shield_pct, (0, 200, 255))
            y += 16
            
        # HP Bar
        hp_pct = ship.hp / ship.max_hp if ship.max_hp > 0 else 0
        hp_color = (0, 255, 0) if hp_pct > 0.5 else ((255, 200, 0) if hp_pct > 0.2 else (255, 50, 50))
        text = font.render(f"HP: {int(ship.hp)}/{int(ship.max_hp)}", True, (180, 180, 180))
        surface.blit(text, (x_indent, y))
        self.draw_stat_bar(surface, x_indent + 100, y, bar_w, bar_h, hp_pct, hp_color)
        y += 16
        
        # Fuel Bar
        fuel_pct = ship.current_fuel / ship.max_fuel if ship.max_fuel > 0 else 0
        text = font.render(f"Fuel: {int(ship.current_fuel)}/{int(ship.max_fuel)}", True, (180, 180, 180))
        surface.blit(text, (x_indent, y))
        self.draw_stat_bar(surface, x_indent + 100, y, bar_w, bar_h, fuel_pct, (255, 165, 0))
        y += 16
        
        # Energy Bar
        energy_pct = ship.current_energy / ship.max_energy if ship.max_energy > 0 else 0
        text = font.render(f"Energy: {int(ship.current_energy)}/{int(ship.max_energy)}", True, (180, 180, 180))
        surface.blit(text, (x_indent, y))
        self.draw_stat_bar(surface, x_indent + 100, y, bar_w, bar_h, energy_pct, (100, 200, 255))
        y += 16
        
        # Ammo Bar
        ammo_pct = ship.current_ammo / ship.max_ammo if ship.max_ammo > 0 else 0
        text = font.render(f"Ammo: {int(ship.current_ammo)}/{int(ship.max_ammo)}", True, (180, 180, 180))
        surface.blit(text, (x_indent, y))
        self.draw_stat_bar(surface, x_indent + 100, y, bar_w, bar_h, ammo_pct, (200, 200, 100))
        y += 16
        
        # Speed
        text = font.render(f"Speed: {ship.current_speed:.0f}/{ship.max_speed:.0f}", True, (180, 180, 180))
        surface.blit(text, (x_indent, y))
        y += 16

        # Total Shots
        text = font.render(f"Shots: {ship.total_shots_fired}", True, (255, 200, 100))
        surface.blit(text, (x_indent, y))
        y += 16

        # Crew Stats
        crew_req = getattr(ship, 'crew_required', 0)
        crew_cur = getattr(ship, 'crew_onboard', 0)
        
        # Color warning if shortage
        crew_color = (180, 180, 180)
        if crew_cur < crew_req:
            crew_color = (255, 100, 100)
            
        text = font.render(f"Crew: {crew_cur}/{crew_req}", True, crew_color)
        surface.blit(text, (x_indent, y))
        y += 16
        
        target_name = "None"
        if ship.current_target and ship.current_target.is_alive:
            target_name = getattr(ship.current_target, 'name', getattr(ship.current_target, 'type', 'Target').title())
        
        text = font.render(f"Target: {target_name}", True, (180, 180, 180))
        surface.blit(text, (x_indent, y))
        y += 18
        
        # Secondary Targets - List them all
        sec_targets = getattr(ship, 'secondary_targets', [])
        if sec_targets:
            for i, st in enumerate(sec_targets):
                if st.is_alive:
                    st_name = getattr(st, 'name', getattr(st, 'type', 'Target').title())
                    # Maybe dim color for secondary?
                    text = font.render(f"  T{i+2}: {st_name}", True, (150, 150, 150))
                    surface.blit(text, (x_indent, y))
                    y += 16

        
        # Targeting Cap
        max_targets = getattr(ship, 'max_targets', 1)
        cap_text = "Single" if max_targets == 1 else f"Multi ({max_targets})"
        text = font.render(f"Sys: {cap_text}", True, (150, 150, 150))
        surface.blit(text, (x_indent + 200, y - 18)) # Draw roughly same line as Target? Or next line?
        # Actually let's just append to Target line or put below.
        # "Target: Alpha (+2) [Multi: 10]"
        

        
        # Weapons
        text = font.render(f"Weapons:", True, (200, 200, 150))
        surface.blit(text, (x_indent, y))
        y += 18
        
        from components import Weapon, ComponentStatus
        
        # Helper to find weapons in layers
        # Use LayerType enums, matches ship.py structure
        for layer_type in [LayerType.OUTER, LayerType.INNER, LayerType.CORE]:
            layer = ship.layers.get(layer_type)
            if not layer: continue
            
            for comp in layer['components']:
                if isinstance(comp, Weapon):
                    # Name
                    c_color = (200, 200, 200) if comp.is_active else (150, 50, 50)
                    if not comp.is_active and getattr(comp, 'status', ComponentStatus.ACTIVE) != ComponentStatus.ACTIVE:
                         c_color = (255, 100, 100) # Red if broken
                         
                    name_str = comp.name
                    if len(name_str) > 12:
                        name_str = name_str[:12] + ".."
                    
                    # Component Layout (Standard Left Alignment)
                    # Name
                    c_text = font.render(name_str, True, c_color)
                    surface.blit(c_text, (x_indent + 5, y))
                    
                    # HP Text
                    hp_text = f"{int(comp.current_hp)}/{int(comp.max_hp)}"
                    hp_val = font.render(hp_text, True, c_color)
                    surface.blit(hp_val, (x_indent + 95, y))
                    
                    # HP/Status Logic
                    hp_pct = comp.current_hp / comp.max_hp
                    hp_col = (0, 200, 0)
                    status_text = ""
                    status_color = (200, 200, 200)
                    
                    if not comp.is_active:
                        hp_col = (100, 50, 50)
                        if getattr(comp, 'status', ComponentStatus.ACTIVE) == ComponentStatus.DAMAGED:
                            status_text = "[DMG]"
                            status_color = (255, 50, 50)
                        elif getattr(comp, 'status', ComponentStatus.ACTIVE) == ComponentStatus.NO_CREW:
                            status_text = "[CREW]"
                            status_color = (255, 165, 0)
                        elif getattr(comp, 'status', ComponentStatus.ACTIVE) == ComponentStatus.NO_POWER:
                            status_text = "[PWR]"
                            status_color = (255, 255, 0)
                        elif getattr(comp, 'status', ComponentStatus.ACTIVE) == ComponentStatus.NO_FUEL:
                            status_text = "[FUEL]"
                            status_color = (255, 100, 0)
                    elif hp_pct < 0.5: 
                         hp_col = (200, 200, 0)
                         
                    # Bar
                    self.draw_stat_bar(surface, x_indent + 160, y, 60, 8, hp_pct, hp_col)
                    
                    # Status text
                    if status_text:
                        st = font.render(status_text, True, status_color)
                        surface.blit(st, (x_indent + 230, y))
                        
                    # Stats: S: X H: Y (Right Aligned)
                    stats_str = f"S:{getattr(comp, 'shots_fired', 0)} H:{getattr(comp, 'shots_hit', 0)}"
                    s_text = font.render(stats_str, True, (150, 150, 255))
                    s_x = panel_w - s_text.get_width() - 10
                    surface.blit(s_text, (s_x, y))
                    
                    y += 16
        
        y += 8
        
        # Components header
        text = font.render("Components:", True, (200, 200, 100))
        surface.blit(text, (x_indent, y))
        y += 16
        
        # Components list (Non-Weapons)
        for layer_type in [LayerType.ARMOR, LayerType.OUTER, LayerType.INNER, LayerType.CORE]:
            for comp in ship.layers[layer_type]['components']:
                if isinstance(comp, Weapon): continue
                
                hp_pct = comp.current_hp / comp.max_hp if comp.max_hp > 0 else 1.0
                
                # Determine colors and status text
                color = (150, 150, 150)
                bar_color = (0, 200, 0)
                status_text = ""
                status_color = (200, 200, 200)
                
                if not comp.is_active:
                    color = (100, 50, 50) # Darkened red/gray
                    bar_color = (100, 50, 50) 
                    
                    if getattr(comp, 'status', ComponentStatus.ACTIVE) == ComponentStatus.DAMAGED:
                        status_text = "[DMG]"
                        status_color = (255, 50, 50)
                    elif getattr(comp, 'status', ComponentStatus.ACTIVE) == ComponentStatus.NO_CREW:
                        status_text = "[CREW]"
                        status_color = (255, 165, 0)
                    elif getattr(comp, 'status', ComponentStatus.ACTIVE) == ComponentStatus.NO_POWER:
                        status_text = "[PWR]"
                        status_color = (255, 255, 0)
                    elif getattr(comp, 'status', ComponentStatus.ACTIVE) == ComponentStatus.NO_FUEL:
                        status_text = "[FUEL]"
                        status_color = (255, 100, 0)
                else:
                    # Healthy colors
                    bar_color = (0, 200, 0) if hp_pct > 0.5 else ((200, 200, 0) if hp_pct > 0.2 else (200, 50, 50))
                
                name = comp.name[:10] + ".." if len(comp.name) > 12 else comp.name
                hp_text = f"{int(comp.current_hp)}/{int(comp.max_hp)}"
                
                text = font.render(name, True, color)
                surface.blit(text, (x_indent + 5, y))
                
                hp_val = font.render(hp_text, True, color)
                surface.blit(hp_val, (x_indent + 95, y))
                
                self.draw_stat_bar(surface, x_indent + 160, y, 60, 8, hp_pct, bar_color)
                
                # Draw Status Text
                if status_text:
                    stat_render = font.render(status_text, True, status_color)
                    surface.blit(stat_render, (x_indent + 230, y))
                
                y += 14
        
        y += 5
        return y

    def draw_stat_bar(self, surface, x, y, width, height, pct, color):
        """Draw a progress bar."""
        pygame.draw.rect(surface, (40, 40, 40), (x, y, width, height))
        if pct > 0:
            fill_w = int(width * min(1.0, pct))
            pygame.draw.rect(surface, color, (x, y, fill_w, height))
        pygame.draw.rect(surface, (80, 80, 80), (x, y, width, height), 1)

    def get_expanded_height(self, ship):
        """Calculate height needed for expanded ship stats."""
        base_height = 146
        if ship.max_shields > 0:
            base_height += 16
            
        comp_count = sum(len(l['components']) for l in ship.layers.values())
        comp_height = comp_count * 14
        return base_height + comp_height + 5

    def handle_click(self, mx, my, button):
        """Handle mouse clicks. Returns True if click was handled."""
        sw = self.width
        
        # Check battle end button
        if self.battle_end_button_rect and self.battle_end_button_rect.collidepoint(mx, my):
            # This action needs to float up to scene
            return "end_battle"
        
        # Check end battle early button
        if self.end_battle_early_rect and self.end_battle_early_rect.collidepoint(mx, my):
            return "end_battle"
        
        # Check Clear Inactive button
        if self.clear_vars_rect and self.clear_vars_rect.collidepoint(mx, my):
            self.tracked_seekers = [p for p in self.tracked_seekers if p.status == 'active']
            return True

        # Check seeker panel click (LEFT side)
        if mx < self.seeker_panel_width:
             return self.handle_seeker_panel_click(mx, my + self.seeker_scroll_offset)
        
        # Check stats panel click
        panel_x = sw - self.stats_panel_width
        if mx >= panel_x:
            return self.handle_stats_panel_click(mx - panel_x, my + self.stats_scroll_offset)
        
        return False
    
    def handle_seeker_panel_click(self, rel_x, rel_y):
        """Handle clicks on Seeker Panel."""
        # Check entries
        y_pos = 10
        # Header + spacer
        y_pos += 30
        
        for proj in self.tracked_seekers:
             rect_h = 22
             if y_pos <= rel_y < y_pos + rect_h:
                 # Check X button (approx right side)
                 # X rect was at panel_w - 25, width 20
                 x_btn_x_start = self.seeker_panel_width - 25
                 if rel_x >= x_btn_x_start and rel_x <= x_btn_x_start + 20:
                     if proj.status != 'active':
                         self.tracked_seekers.remove(proj)
                         return True
                 
                 # Toggle expand
                 if proj in self.expanded_seekers:
                     self.expanded_seekers.discard(proj)
                 else:
                     self.expanded_seekers.add(proj)
                 return True
             
             y_pos += 25
             if proj in self.expanded_seekers:
                 # Height: Speed(14) + HP(14) + Fuel(14) + Damage(14) + Target(16) = 72
                 y_pos += 72
        return False

    def handle_stats_panel_click(self, rel_x, rel_y):
        """Handle clicks on the stats panel."""
        team1_ships = [s for s in self.scene.ships if s.team_id == 0]
        team2_ships = [s for s in self.scene.ships if s.team_id == 1]
        
        # Check if Shift is held
        keys = pygame.key.get_pressed()
        shift_held = keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]

        # Must match draw layout!
        # Initial y = 10
        y_pos = 10 
        
        # Skip Team 1 Header (30 height)
        y_pos += 30
        
        for ship in team1_ships:
            banner_height = 25
            if y_pos <= rel_y < y_pos + banner_height:
                if shift_held:
                    return ("focus_ship", ship)
                if ship in self.expanded_ships:
                    self.expanded_ships.discard(ship)
                else:
                    self.expanded_ships.add(ship)
                return True
            y_pos += banner_height
            if ship in self.expanded_ships:
                y_pos += self.get_expanded_height(ship)
        
        # Skip Spacer (15) + Team 2 Header (30)
        y_pos += 45 
        
        for ship in team2_ships:
            banner_height = 25
            if y_pos <= rel_y < y_pos + banner_height:
                if shift_held:
                    return ("focus_ship", ship)
                if ship in self.expanded_ships:
                    self.expanded_ships.discard(ship)
                else:
                    self.expanded_ships.add(ship)
                return True
            y_pos += banner_height
            if ship in self.expanded_ships:
                y_pos += self.get_expanded_height(ship)
        
        return False

    def handle_scroll(self, scroll_y, screen_h):
        """Handle mouse wheel scrolling on stats panel."""
        mx, my = pygame.mouse.get_pos()
        sw = self.width
        
        # Seeker panel on LEFT side
        if mx < self.seeker_panel_width:
             self.seeker_scroll_offset -= scroll_y * 30
             max_scroll = max(0, self.seeker_panel_content_height - screen_h + 50)
             self.seeker_scroll_offset = max(0, min(max_scroll, self.seeker_scroll_offset))
             
        elif mx >= sw - self.stats_panel_width:
            self.stats_scroll_offset -= scroll_y * 30
            max_scroll = max(0, self.stats_panel_content_height - screen_h + 50)
            self.stats_scroll_offset = max(0, min(max_scroll, self.stats_scroll_offset))

    def print_headless_summary(self, start_time, tick_counter):
        """Print battle summary."""
        elapsed = time.time() - start_time if start_time else 0
        
        team1_ships = [s for s in self.scene.ships if s.team_id == 0]
        team2_ships = [s for s in self.scene.ships if s.team_id == 1]
        team1_survivors = [s for s in team1_ships if s.is_alive and not getattr(s, 'is_derelict', False)]
        team2_survivors = [s for s in team2_ships if s.is_alive and not getattr(s, 'is_derelict', False)]
        
        print(f"\n=== BATTLE COMPLETE ===")
        print(f"Time: {elapsed:.2f}s, Ticks: {tick_counter}")
        
        if tick_counter >= 3000000:
            print(f"DRAW (tick limit: {tick_counter:,} ticks)")
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
