import pygame
import math
from game.ui.panels.battle_panels import ShipStatsPanel, SeekerMonitorPanel, BattleControlPanel

class BattleInterface:
    """Handles all UI rendering and interaction for the BattleScene."""
    
    def __init__(self, scene, screen_width, screen_height):
        self.scene = scene
        self.width = screen_width
        self.height = screen_height
        
        # UI State
        self.show_overlay = False
        
        # Instantiate Panels
        stats_width = 450
        seeker_width = 300
        
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
        if getattr(proj, 'type', '') == 'missile':
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

        # Draw "Return to Combat Lab" button if battle is over in test mode
        if self.scene.is_battle_over():
            print(f"DEBUG: Battle is over. test_mode={self.scene.test_mode}")
            if self.scene.test_mode:
                self._draw_return_button(screen)
            else:
                print(f"DEBUG: Not drawing Combat Lab button because test_mode=False")

    def handle_click(self, mx, my, button):
        """Handle mouse clicks. Returns True if click was handled."""

        print(f"DEBUG: BattleInterface.handle_click at ({mx}, {my})")
        print(f"DEBUG: test_mode={self.scene.test_mode}, battle_over={self.scene.is_battle_over()}")

        # Check "Return to Combat Lab" button first (highest priority)
        if self.scene.test_mode and self.scene.is_battle_over():
            button_rect = self._get_return_button_rect()
            print(f"DEBUG: Return button rect: {button_rect}")
            if button_rect.collidepoint(mx, my):
                print(f"DEBUG: Return to Combat Lab button clicked!")
                self.scene.action_return_to_test_lab = True
                return True
            else:
                print(f"DEBUG: Click was not on return button")

        # Control Panel (Buttons usually top priority or overlay)
        # Check control panel first (e.g. End Battle button)
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
            for comp in s.get_components_by_ability('WeaponAbility', operational_only=True):
                weapon_ab = comp.get_ability('WeaponAbility')
                if weapon_ab and weapon_ab.range > max_range:
                    max_range = weapon_ab.range
            
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

    def _get_return_button_rect(self):
        """Get the rect for the Return to Combat Lab button."""
        button_width = 300
        button_height = 60
        x = (self.width - button_width) // 2
        y = (self.height - button_height) // 2
        return pygame.Rect(x, y, button_width, button_height)

    def _draw_return_button(self, screen):
        """Draw the Return to Combat Lab button (shown when test completes)."""
        print(f"DEBUG: Drawing Return to Combat Lab button (test_mode={self.scene.test_mode}, battle_over={self.scene.is_battle_over()})")
        button_rect = self._get_return_button_rect()

        # Check hover state
        mx, my = pygame.mouse.get_pos()
        is_hovered = button_rect.collidepoint(mx, my)

        # Draw button
        color = (0, 150, 200) if is_hovered else (0, 100, 150)
        pygame.draw.rect(screen, color, button_rect, border_radius=8)
        pygame.draw.rect(screen, (255, 255, 255), button_rect, 3, border_radius=8)

        # Draw text
        font = pygame.font.SysFont("Arial", 28, bold=True)
        text = font.render("Return to Combat Lab", True, (255, 255, 255))
        text_rect = text.get_rect(center=button_rect.center)
        screen.blit(text, text_rect)

        # Draw "TEST COMPLETE" indicator above button
        complete_font = pygame.font.SysFont("Arial", 56, bold=True)

        # Color based on test pass/fail
        if hasattr(self.scene, 'test_scenario') and self.scene.test_scenario:
            if self.scene.test_scenario.passed:
                complete_text = "TEST COMPLETE - PASSED"
                complete_color = (80, 255, 120)  # Green
            else:
                complete_text = "TEST COMPLETE - FAILED"
                complete_color = (255, 80, 80)  # Red
        else:
            complete_text = "TEST COMPLETE"
            complete_color = (255, 200, 100)  # Yellow

        complete_surface = complete_font.render(complete_text, True, complete_color)
        complete_rect = complete_surface.get_rect(center=(button_rect.centerx, button_rect.top - 120))

        # Draw background for text
        bg_rect = complete_rect.inflate(40, 20)
        pygame.draw.rect(screen, (0, 0, 0, 200), bg_rect, border_radius=10)
        pygame.draw.rect(screen, complete_color, bg_rect, 3, border_radius=10)
        screen.blit(complete_surface, complete_rect)

        # Draw battle result above button
        winner = self.scene.get_winner()
        result_text = ""
        result_color = (255, 255, 255)
        if winner == 0:
            result_text = "TEAM 0 WINS!"
            result_color = (0, 255, 0)
        elif winner == 1:
            result_text = "TEAM 1 WINS!"
            result_color = (0, 255, 0)
        else:
            result_text = "DRAW!"
            result_color = (255, 255, 0)

        result_font = pygame.font.SysFont("Arial", 48, bold=True)
        result_surface = result_font.render(result_text, True, result_color)
        result_rect = result_surface.get_rect(center=(button_rect.centerx, button_rect.top - 60))
        screen.blit(result_surface, result_rect)
