import pygame
import math
from components import Weapon, ComponentStatus
from ship import LayerType
from ai import COMBAT_STRATEGIES

class BattlePanel:
    """Base class for battle UI panels."""
    def __init__(self, scene, x, y, w, h):
        self.scene = scene
        self.rect = pygame.Rect(x, y, w, h)
        self.surface = None  # Cached surface
    
    def draw(self, screen):
        raise NotImplementedError
    
    def handle_click(self, mx, my):
        return False

    def draw_stat_bar(self, surface, x, y, width, height, pct, color):
        """Draw a progress bar."""
        pygame.draw.rect(surface, (40, 40, 40), (x, y, width, height))
        if pct > 0:
            fill_w = int(width * min(1.0, pct))
            pygame.draw.rect(surface, color, (x, y, fill_w, height))
        pygame.draw.rect(surface, (80, 80, 80), (x, y, width, height), 1)

class ShipStatsPanel(BattlePanel):
    """Panel for displaying ship statistics (Right side)."""
    def __init__(self, scene, x, y, w, h):
        super().__init__(scene, x, y, w, h)
        self.expanded_ships = set()
        self.scroll_offset = 0
        self.content_height = 0
    
    def draw(self, screen):
        # Validate cache size
        if (self.surface is None or 
            self.surface.get_width() != self.rect.width or 
            self.surface.get_height() != self.rect.height):
            self.surface = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
            
        # Draw to surface
        self.surface.fill((0, 0, 0, 0))
        self.surface.fill((20, 25, 35, 230))
        
        font_title = pygame.font.Font(None, 28)
        font_name = pygame.font.Font(None, 22)
        font_stat = pygame.font.Font(None, 18)
        
        y = 10 - self.scroll_offset
        panel_w = self.rect.width
        
        # Team 1
        team1_ships = [s for s in self.scene.ships if s.team_id == 0]
        team1_alive = sum(1 for s in team1_ships if s.is_alive and not getattr(s, 'is_derelict', False))
        
        title = font_title.render(f"TEAM 1 ({team1_alive}/{len(team1_ships)})", True, (100, 200, 255))
        self.surface.blit(title, (10, y))
        y += 30
        
        for ship in team1_ships:
            y = self.draw_ship_entry(self.surface, ship, y, panel_w, font_name, font_stat, (40, 60, 80))
        
        y += 15
        
        # Team 2
        team2_ships = [s for s in self.scene.ships if s.team_id == 1]
        team2_alive = sum(1 for s in team2_ships if s.is_alive and not getattr(s, 'is_derelict', False))
        
        title = font_title.render(f"TEAM 2 ({team2_alive}/{len(team2_ships)})", True, (255, 100, 100))
        self.surface.blit(title, (10, y))
        y += 30
        
        for ship in team2_ships:
            y = self.draw_ship_entry(self.surface, ship, y, panel_w, font_name, font_stat, (80, 40, 40))
        
        self.content_height = y + self.scroll_offset
        
        screen.blit(self.surface, self.rect.topleft)
        pygame.draw.line(screen, (60, 60, 80), self.rect.topleft, self.rect.bottomleft, 2)
        
    def draw_ship_entry(self, surface, ship, y, panel_w, font_name, font_stat, banner_color):
        """Draw a single ship entry."""
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
            color = (255, 165, 0)
        bg_color = banner_color if ship.is_alive else (40, 40, 40)
        
        pygame.draw.rect(surface, bg_color, (5, y, panel_w - 10, 22))
        name_text = font_name.render(f"{arrow} {ship.name}{status}", True, color)
        surface.blit(name_text, (10, y + 3))
        y += 25
        
        if ship in self.expanded_ships:
            y = self.draw_ship_details(surface, ship, y, panel_w, font_stat)
        
        return y

    def draw_ship_details(self, surface, ship, y, panel_w, font):
        """Draw expanded ship details."""
        x_indent = 20
        bar_w = 120
        bar_h = 10
        
        if hasattr(ship, 'source_file') and ship.source_file:
            text = font.render(f"File: {ship.source_file}", True, (150, 150, 200))
            surface.blit(text, (x_indent, y))
            y += 16
        
        strat_name = COMBAT_STRATEGIES.get(ship.ai_strategy, {}).get('name', ship.ai_strategy)
        text = font.render(f"AI: {strat_name}", True, (150, 200, 150))
        surface.blit(text, (x_indent, y))
        y += 16
        
        # Shield
        if ship.max_shields > 0:
            shield_pct = ship.current_shields / ship.max_shields
            text = font.render(f"Shield: {int(ship.current_shields)}/{int(ship.max_shields)}", True, (180, 180, 180))
            surface.blit(text, (x_indent, y))
            self.draw_stat_bar(surface, x_indent + 100, y, bar_w, bar_h, shield_pct, (0, 200, 255))
            y += 16
            
        # HP
        hp_pct = ship.hp / ship.max_hp if ship.max_hp > 0 else 0
        hp_color = (0, 255, 0) if hp_pct > 0.5 else ((255, 200, 0) if hp_pct > 0.2 else (255, 50, 50))
        text = font.render(f"HP: {int(ship.hp)}/{int(ship.max_hp)}", True, (180, 180, 180))
        surface.blit(text, (x_indent, y))
        self.draw_stat_bar(surface, x_indent + 100, y, bar_w, bar_h, hp_pct, hp_color)
        y += 16
        
        # Fuel
        fuel_pct = ship.current_fuel / ship.max_fuel if ship.max_fuel > 0 else 0
        text = font.render(f"Fuel: {int(ship.current_fuel)}/{int(ship.max_fuel)}", True, (180, 180, 180))
        surface.blit(text, (x_indent, y))
        self.draw_stat_bar(surface, x_indent + 100, y, bar_w, bar_h, fuel_pct, (255, 165, 0))
        y += 16
        
        # Energy
        energy_pct = ship.current_energy / ship.max_energy if ship.max_energy > 0 else 0
        text = font.render(f"Energy: {int(ship.current_energy)}/{int(ship.max_energy)}", True, (180, 180, 180))
        surface.blit(text, (x_indent, y))
        self.draw_stat_bar(surface, x_indent + 100, y, bar_w, bar_h, energy_pct, (100, 200, 255))
        y += 16
        
        # Ammo
        ammo_pct = ship.current_ammo / ship.max_ammo if ship.max_ammo > 0 else 0
        text = font.render(f"Ammo: {int(ship.current_ammo)}/{int(ship.max_ammo)}", True, (180, 180, 180))
        surface.blit(text, (x_indent, y))
        self.draw_stat_bar(surface, x_indent + 100, y, bar_w, bar_h, ammo_pct, (200, 200, 100))
        y += 16
        
        # Speed
        text = font.render(f"Speed: {ship.current_speed:.0f}/{ship.max_speed:.0f}", True, (180, 180, 180))
        surface.blit(text, (x_indent, y))
        y += 16

        # Shots
        text = font.render(f"Shots: {ship.total_shots_fired}", True, (255, 200, 100))
        surface.blit(text, (x_indent, y))
        y += 16

        # Crew
        crew_req = getattr(ship, 'crew_required', 0)
        crew_cur = getattr(ship, 'crew_onboard', 0)
        crew_color = (180, 180, 180)
        if crew_cur < crew_req:
            crew_color = (255, 100, 100)
        text = font.render(f"Crew: {crew_cur}/{crew_req}", True, crew_color)
        surface.blit(text, (x_indent, y))
        y += 16
        
        # Target
        target_name = "None"
        if ship.current_target and ship.current_target.is_alive:
            target_name = getattr(ship.current_target, 'name', getattr(ship.current_target, 'type', 'Target').title())
        text = font.render(f"Target: {target_name}", True, (180, 180, 180))
        surface.blit(text, (x_indent, y))
        y += 18
        
        # Secondary Targets
        sec_targets = getattr(ship, 'secondary_targets', [])
        if sec_targets:
            for i, st in enumerate(sec_targets):
                if st.is_alive:
                    st_name = getattr(st, 'name', getattr(st, 'type', 'Target').title())
                    text = font.render(f"  T{i+2}: {st_name}", True, (150, 150, 150))
                    surface.blit(text, (x_indent, y))
                    y += 16
        
        # Targeting Cap
        max_targets = getattr(ship, 'max_targets', 1)
        cap_text = "Single" if max_targets == 1 else f"Multi ({max_targets})"
        text = font.render(f"Sys: {cap_text}", True, (150, 150, 150))
        surface.blit(text, (x_indent + 200, y - 18))
        
        # Weapons
        text = font.render(f"Weapons:", True, (200, 200, 150))
        surface.blit(text, (x_indent, y))
        y += 18
        
        for layer_type in [LayerType.OUTER, LayerType.INNER, LayerType.CORE]:
            layer = ship.layers.get(layer_type)
            if not layer: continue
            
            for comp in layer['components']:
                if isinstance(comp, Weapon):
                    c_color = (200, 200, 200) if comp.is_active else (150, 50, 50)
                    if not comp.is_active and getattr(comp, 'status', ComponentStatus.ACTIVE) != ComponentStatus.ACTIVE:
                         c_color = (255, 100, 100)
                         
                    name_str = comp.name
                    if len(name_str) > 12:
                        name_str = name_str[:12] + ".."
                    
                    c_text = font.render(name_str, True, c_color)
                    surface.blit(c_text, (x_indent + 5, y))
                    
                    hp_text = f"{int(comp.current_hp)}/{int(comp.max_hp)}"
                    hp_val = font.render(hp_text, True, c_color)
                    surface.blit(hp_val, (x_indent + 95, y))
                    
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
                         
                    self.draw_stat_bar(surface, x_indent + 160, y, 60, 8, hp_pct, hp_col)
                    
                    if status_text:
                        st = font.render(status_text, True, status_color)
                        surface.blit(st, (x_indent + 230, y))
                    
                    stats_str = f"S:{getattr(comp, 'shots_fired', 0)} H:{getattr(comp, 'shots_hit', 0)}"
                    s_text = font.render(stats_str, True, (150, 150, 255))
                    s_x = panel_w - s_text.get_width() - 10
                    surface.blit(s_text, (s_x, y))
                    
                    y += 16
        
        y += 8
        
        # Detailed Components
        text = font.render("Components:", True, (200, 200, 100))
        surface.blit(text, (x_indent, y))
        y += 16
        
        for layer_type in [LayerType.ARMOR, LayerType.OUTER, LayerType.INNER, LayerType.CORE]:
            for comp in ship.layers[layer_type]['components']:
                if isinstance(comp, Weapon): continue
                
                hp_pct = comp.current_hp / comp.max_hp if comp.max_hp > 0 else 1.0
                color = (150, 150, 150)
                bar_color = (0, 200, 0)
                status_text = ""
                status_color = (200, 200, 200)
                
                if not comp.is_active:
                    color = (100, 50, 50)
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
                    bar_color = (0, 200, 0) if hp_pct > 0.5 else ((200, 200, 0) if hp_pct > 0.2 else (200, 50, 50))
                
                name = comp.name[:10] + ".." if len(comp.name) > 12 else comp.name
                hp_text = f"{int(comp.current_hp)}/{int(comp.max_hp)}"
                
                text = font.render(name, True, color)
                surface.blit(text, (x_indent + 5, y))
                
                hp_val = font.render(hp_text, True, color)
                surface.blit(hp_val, (x_indent + 95, y))
                
                self.draw_stat_bar(surface, x_indent + 160, y, 60, 8, hp_pct, bar_color)
                
                if status_text:
                    stat_render = font.render(status_text, True, status_color)
                    surface.blit(stat_render, (x_indent + 230, y))
                
                y += 14
        
        y += 5
        return y

    def get_expanded_height(self, ship):
        base_height = 146
        if ship.max_shields > 0:
            base_height += 16
        comp_count = sum(len(l['components']) for l in ship.layers.values())
        comp_height = comp_count * 14
        return base_height + comp_height + 5

    def handle_click(self, mx, my):
        # Convert absolute mx to relative (my is already absolute, but we need relative for layout)
        # But wait, logic in battle_ui passed relative coordinates.
        # Here we should expect relative coordinates or handle it.
        # Let's assume standard event handling: receiver gets local coords or we transform.
        # The BattleInterface.handle_click transformed it. 
        # "return self.handle_stats_panel_click(mx - panel_x, my + self.stats_scroll_offset)"
        
        # Let's stick to the interface receiving (mx, my) relative to the panel's origin
        # BUT we also need to account for scroll offset.
        # So expects: rel_x, rel_y (where rel_y includes scroll? No, normally Mouse pos is local to TopLeft)
        # In battle_ui, it passed `my + self.stats_scroll_offset`. 
        
        rel_x = mx
        rel_y = my + self.scroll_offset
        
        team1_ships = [s for s in self.scene.ships if s.team_id == 0]
        team2_ships = [s for s in self.scene.ships if s.team_id == 1]
        
        keys = pygame.key.get_pressed()
        shift_held = keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]
        
        y_pos = 10 + 30 # Initial + header
        
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


class SeekerMonitorPanel(BattlePanel):
    """Panel for monitoring missiles and seekers (Left side)."""
    def __init__(self, scene, x, y, w, h):
        super().__init__(scene, x, y, w, h)
        self.tracked_seekers = []
        self.expanded_seekers = set()
        self.scroll_offset = 0
        self.clear_btn_rect = None
        self.content_height = 0
        
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
        self.surface.fill((20, 25, 35, 230))
        
        # Draw line on Right edge
        pygame.draw.line(self.surface, (60, 60, 80), (self.rect.width - 1, 0), (self.rect.width - 1, self.rect.height), 2)
        
        font_title = pygame.font.Font(None, 28)
        font_name = pygame.font.Font(None, 22)
        font_stat = pygame.font.Font(None, 18)
        
        y = 10 - self.scroll_offset
        panel_w = self.rect.width
        
        active_count = sum(1 for p in self.tracked_seekers if p.status == 'active')
        total_count = len(self.tracked_seekers)
        title = font_title.render(f"SEEKER MONITOR ({active_count}/{total_count})", True, (255, 200, 100))
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
        col = (60, 40, 40) if hover else (50, 30, 30)
        border = (150, 80, 80) if hover else (100, 60, 60)
        
        pygame.draw.rect(screen, col, self.clear_btn_rect)
        pygame.draw.rect(screen, border, self.clear_btn_rect, 1)
        
        text = font_name.render("Clear Inactive", True, (255, 150, 150))
        text_rect = text.get_rect(center=self.clear_btn_rect.center)
        screen.blit(text, text_rect)
    
    def draw_seeker_entry(self, surface, proj, y, panel_w, font_name, font_stat):
        arrow = "▼" if proj in self.expanded_seekers else "►"
        status = getattr(proj, 'status', 'active')
        
        if status == 'hit':
            color = (50, 255, 50)
            status_str = "[HIT]"
            bg_color = (40, 40, 40)
        elif status == 'miss':
            color = (150, 150, 150)
            status_str = "[MISS]"
            bg_color = (40, 40, 40)
        elif status == 'destroyed':
            color = (255, 50, 50)
            status_str = "[DEAD]"
            bg_color = (40, 40, 40)
        else:
            color = (255, 255, 100)
            status_str = "[ACT]"
            bg_color = (50, 50, 60)
            
        pygame.draw.rect(surface, bg_color, (5, y, panel_w - 35, 22))
        
        name = "Missile"
        text = font_name.render(f"{arrow} {name} {status_str}", True, color)
        surface.blit(text, (10, y + 3))
        
        # X button
        if status != 'active':
            x_rect = pygame.Rect(panel_w - 25, y, 20, 22)
            pygame.draw.rect(surface, (60, 30, 30), x_rect)
            pygame.draw.rect(surface, (100, 50, 50), x_rect, 1)
            x_text = font_name.render("X", True, (255, 100, 100))
            x_rect_center = x_rect.center
            surface.blit(x_text, (x_rect_center[0] - x_text.get_width()//2, x_rect_center[1] - x_text.get_height()//2))
            
        y += 25
        
        if proj in self.expanded_seekers:
            y = self.draw_seeker_details(surface, proj, y, panel_w, font_stat)
            
        return y

    def draw_seeker_details(self, surface, proj, y, panel_w, font):
        x_indent = 20
        bar_w = 80
        bar_h = 8
        
        # Speed
        p_vel_len = proj.velocity.length() * 100.0
        max_speed = getattr(proj, 'max_speed', p_vel_len) * 100.0 if getattr(proj, 'max_speed', 0) > 0 else p_vel_len
        txt = font.render(f"Speed: {p_vel_len:.0f} px/s", True, (180, 180, 180))
        surface.blit(txt, (x_indent, y))
        y += 14
        
        # HP
        hp = getattr(proj, 'hp', 0)
        max_hp = getattr(proj, 'max_hp', hp) if getattr(proj, 'max_hp', 0) > 0 else max(hp, 1)
        hp_pct = hp / max_hp if max_hp > 0 else 0
        hp_color = (0, 255, 0) if hp_pct > 0.5 else ((255, 200, 0) if hp_pct > 0.2 else (255, 50, 50))
        
        txt = font.render(f"HP: {hp:.0f}/{max_hp:.0f}", True, (180, 180, 180))
        surface.blit(txt, (x_indent, y))
        self.draw_stat_bar(surface, x_indent + 80, y, bar_w, bar_h, hp_pct, hp_color)
        y += 14
        
        # Fuel
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
    
    def handle_click(self, mx, my):
        # Check Clear Inactive - this is in absolute screen coords because we draw it to screen
        # So we should check it first before relative logic?
        # Actually BattleInterface passes absolute mx, my.
        if self.clear_btn_rect and self.clear_btn_rect.collidepoint(mx, my):
            self.clear_inactive()
            return True
            
        # Check relative clicks
        # Check if click is within panel rect at all? 
        # BattleInterface checks if mx < panel_width.
        
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
                 
                 # Toggle expand
                 if proj in self.expanded_seekers:
                     self.expanded_seekers.discard(proj)
                 else:
                     self.expanded_seekers.add(proj)
                 return True
             
             y_pos += 25
             if proj in self.expanded_seekers:
                 y_pos += 72
        return False

class BattleControlPanel(BattlePanel):
    """Panel for battle control buttons."""
    def __init__(self, scene, x, y, w, h):
        super().__init__(scene, x, y, w, h)
        self.battle_end_button_rect = None
        self.end_battle_early_rect = None
        
    def draw(self, screen):
        team1_alive = sum(1 for s in self.scene.ships if s.team_id == 0 and s.is_alive and not getattr(s, 'is_derelict', False))
        team2_alive = sum(1 for s in self.scene.ships if s.team_id == 1 and s.is_alive and not getattr(s, 'is_derelict', False))
        sw, sh = screen.get_size()
        
        if team1_alive == 0 or team2_alive == 0:
            # Battle Over
            if team1_alive > 0:
                winner_text, winner_color = "TEAM 1 WINS!", (100, 200, 255)
            elif team2_alive > 0:
                winner_text, winner_color = "TEAM 2 WINS!", (255, 100, 100)
            else:
                winner_text, winner_color = "DRAW!", (200, 200, 200)
            
            # Draw semi-transparent overlay
            if self.surface is None or self.surface.get_size() != self.rect.size:
                self.surface = pygame.Surface(self.rect.size, pygame.SRCALPHA)
            
            self.surface.fill((0, 0, 0, 150)) 
            screen.blit(self.surface, self.rect.topleft)
            
            win_font = pygame.font.Font(None, 72)
            win_surf = win_font.render(winner_text, True, winner_color)
            center_x = self.rect.centerx
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
            self.end_battle_early_rect = None
        else:
            # Ongoing battle - Floating End Button (Top Left typically)
            # Was drawn at (10, 70) in battle_ui. 
            # We can treat this panel as "fullscreen overlay" or just manage the button.
            # Let's draw it directly on screen.
            
            btn_font = pygame.font.Font(None, 24)
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
            
            pygame.draw.rect(screen, (80, 40, 40), (btn_x, btn_y, btn_w, btn_h))
            pygame.draw.rect(screen, (150, 80, 80), (btn_x, btn_y, btn_w, btn_h), 1)
            btn_text = btn_font.render("End Battle", True, (255, 200, 200))
            screen.blit(btn_text, (btn_x + btn_w // 2 - btn_text.get_width() // 2, btn_y + 7))
            
            self.end_battle_early_rect = pygame.Rect(btn_x, btn_y, btn_w, btn_h)
            self.battle_end_button_rect = None
    
    def handle_click(self, mx, my):
        if self.battle_end_button_rect and self.battle_end_button_rect.collidepoint(mx, my):
            return "end_battle"
        if self.end_battle_early_rect and self.end_battle_early_rect.collidepoint(mx, my):
            return "end_battle"
        return False
