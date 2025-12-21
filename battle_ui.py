
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
        self.stats_panel_width = 350
        self.expanded_ships = set()
        self.stats_scroll_offset = 0
        self.stats_panel_content_height = 0
        self.show_overlay = False
        
        # Button rects for click detection
        self.battle_end_button_rect = None
        self.end_battle_early_rect = None

    def draw(self, screen):
        """Draw the battle scene UI elements (excluding ships/projectiles)."""
        # Draw grid
        self.draw_grid(screen)
        
        # Note: Ships, projectiles, and beams are drawn by the Scene itself 
        # because they are part of the world simulation, but we could move them here too.
        # For now, we follow the plan to move UI overlays.
        
        if self.show_overlay:
            self.draw_debug_overlay(screen)
        
        # Stats panel
        self.draw_ship_stats_panel(screen)
        
        # Battle end UI
        self.draw_battle_end_ui(screen)

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
        team1_alive = sum(1 for s in self.scene.ships if s.team_id == 0 and s.is_alive)
        team2_alive = sum(1 for s in self.scene.ships if s.team_id == 1 and s.is_alive)
        sw, sh = screen.get_size()
        
        if team1_alive == 0 or team2_alive == 0:
            # Battle over overlay
            overlay = pygame.Surface((sw - self.stats_panel_width, sh), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            screen.blit(overlay, (0, 0))
            
            if team1_alive > 0:
                winner_text, winner_color = "TEAM 1 WINS!", (100, 200, 255)
            elif team2_alive > 0:
                winner_text, winner_color = "TEAM 2 WINS!", (255, 100, 100)
            else:
                winner_text, winner_color = "DRAW!", (200, 200, 200)
            
            win_font = pygame.font.Font(None, 72)
            win_surf = win_font.render(winner_text, True, winner_color)
            center_x = (sw - self.stats_panel_width) // 2
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
        
        panel_surf = pygame.Surface((panel_w, sh), pygame.SRCALPHA)
        panel_surf.fill((20, 25, 35, 230))
        
        font_title = pygame.font.Font(None, 28)
        font_name = pygame.font.Font(None, 22)
        font_stat = pygame.font.Font(None, 18)
        
        y = 10 - self.stats_scroll_offset
        
        # Team 1
        team1_ships = [s for s in self.scene.ships if s.team_id == 0]
        team1_alive = sum(1 for s in team1_ships if s.is_alive)
        
        title = font_title.render(f"TEAM 1 ({team1_alive}/{len(team1_ships)})", True, (100, 200, 255))
        panel_surf.blit(title, (10, y))
        y += 30
        
        for ship in team1_ships:
            y = self.draw_ship_entry(panel_surf, ship, y, panel_w, font_name, font_stat, (40, 60, 80))
        
        y += 15
        
        # Team 2
        team2_ships = [s for s in self.scene.ships if s.team_id == 1]
        team2_alive = sum(1 for s in team2_ships if s.is_alive)
        
        title = font_title.render(f"TEAM 2 ({team2_alive}/{len(team2_ships)})", True, (255, 100, 100))
        panel_surf.blit(title, (10, y))
        y += 30
        
        for ship in team2_ships:
            y = self.draw_ship_entry(panel_surf, ship, y, panel_w, font_name, font_stat, (80, 40, 40))
        
        self.stats_panel_content_height = y + self.stats_scroll_offset
        
        screen.blit(panel_surf, (panel_x, 0))
        pygame.draw.line(screen, (60, 60, 80), (panel_x, 0), (panel_x, sh), 2)

    def draw_ship_entry(self, surface, ship, y, panel_w, font_name, font_stat, banner_color):
        """Draw a single ship entry in the stats panel. Returns new y position."""
        arrow = "▼" if ship in self.expanded_ships else "►"
        status = "" if ship.is_alive else " [DEAD]"
        color = (200, 200, 200) if ship.is_alive else (100, 100, 100)
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
        
        # Target
        target_name = "None"
        if ship.current_target and ship.current_target.is_alive:
            target_name = ship.current_target.name
        text = font.render(f"Target: {target_name}", True, (180, 180, 180))
        surface.blit(text, (x_indent, y))
        y += 18
        
        # Components header
        text = font.render("Components:", True, (200, 200, 100))
        surface.blit(text, (x_indent, y))
        y += 16
        
        # Components list
        for layer_type in [LayerType.ARMOR, LayerType.OUTER, LayerType.INNER, LayerType.CORE]:
            for comp in ship.layers[layer_type]['components']:
                hp_pct = comp.current_hp / comp.max_hp if comp.max_hp > 0 else 1.0
                color = (150, 150, 150) if comp.is_active else (80, 80, 80)
                bar_color = (0, 200, 0) if hp_pct > 0.5 else ((200, 200, 0) if hp_pct > 0.2 else (200, 50, 50))
                if not comp.is_active:
                    bar_color = (60, 60, 60)
                
                name = comp.name[:10] + ".." if len(comp.name) > 12 else comp.name
                hp_text = f"{int(comp.current_hp)}/{int(comp.max_hp)}"
                text = font.render(name, True, color)
                surface.blit(text, (x_indent + 5, y))
                hp_val = font.render(hp_text, True, color)
                surface.blit(hp_val, (x_indent + 95, y))
                self.draw_stat_bar(surface, x_indent + 160, y, 60, 8, hp_pct, bar_color)
                
                if hasattr(comp, 'fire_count') and comp.fire_count > 0:
                    fire_text = font.render(f"x{comp.fire_count}", True, (255, 200, 100))
                    surface.blit(fire_text, (x_indent + 230, y))
                
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
        
        # Check stats panel click
        panel_x = sw - self.stats_panel_width
        if mx >= panel_x:
            return self.handle_stats_panel_click(mx - panel_x, my + self.stats_scroll_offset)
        
        return False

    def handle_stats_panel_click(self, rel_x, rel_y):
        """Handle clicks on the stats panel."""
        team1_ships = [s for s in self.scene.ships if s.team_id == 0]
        team2_ships = [s for s in self.scene.ships if s.team_id == 1]
        
        y_pos = 40  # Header
        
        for ship in team1_ships:
            banner_height = 25
            if y_pos <= rel_y < y_pos + banner_height:
                if ship in self.expanded_ships:
                    self.expanded_ships.discard(ship)
                else:
                    self.expanded_ships.add(ship)
                return True
            y_pos += banner_height
            if ship in self.expanded_ships:
                y_pos += self.get_expanded_height(ship)
        
        y_pos += 45  # Gap + Team 2 header
        
        for ship in team2_ships:
            banner_height = 25
            if y_pos <= rel_y < y_pos + banner_height:
                if ship in self.expanded_ships:
                    self.expanded_ships.discard(ship)
                else:
                    self.expanded_ships.add(ship)
                return True
            y_pos += banner_height
            if ship in self.expanded_ships:
                y_pos += self.get_expanded_height(ship)
        
        return False

    def handle_scroll(self, scroll_y):
        """Handle mouse wheel scrolling on stats panel."""
        self.stats_scroll_offset -= scroll_y * 30
        max_scroll = max(0, self.stats_panel_content_height - self.height + 50)
        self.stats_scroll_offset = max(0, min(max_scroll, self.stats_scroll_offset))

    def print_headless_summary(self, start_time, tick_counter):
        """Print battle summary."""
        elapsed = time.time() - start_time if start_time else 0
        
        team1_ships = [s for s in self.scene.ships if s.team_id == 0]
        team2_ships = [s for s in self.scene.ships if s.team_id == 1]
        team1_survivors = [s for s in team1_ships if s.is_alive]
        team2_survivors = [s for s in team2_ships if s.is_alive]
        
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
