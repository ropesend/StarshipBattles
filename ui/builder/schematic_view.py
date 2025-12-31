import pygame
import math
from ship import VEHICLE_CLASSES, LayerType
from components import Weapon, BeamWeapon

# Colors
SHIP_VIEW_BG = (10, 10, 20)

class SchematicView:
    def __init__(self, rect, sprite_manager, theme_manager):
        self.rect = rect
        self.sprite_mgr = sprite_manager
        self.theme_manager = theme_manager
        self.cx = rect.centerx
        self.cy = rect.centery

    def update_rect(self, rect):
        self.rect = rect
        self.cx = rect.centerx
        self.cy = rect.centery

    def _calculate_max_r(self, ship):
        class_def = VEHICLE_CLASSES.get(ship.ship_class, {})
        ref_mass = class_def.get('max_mass', 1000)
        # Scale: Dreadnought(64000)->40->280px. Escort(1000)->10->70px.
        PIXELS_PER_MASS_ROOT = 7.0 
        return int((ref_mass ** (1/3.0)) * PIXELS_PER_MASS_ROOT)

    def get_component_at(self, pos, ship):
        """Returns (layer_type, index, component) or None.
        
        DISABLED: User requested to stop allowing interaction with components 
        when clicking on the image of the ship.
        """
        return None

    def draw(self, screen, ship, show_firing_arcs, selected_component, hovered_component):
        # Draw Background
        pygame.draw.rect(screen, SHIP_VIEW_BG, self.rect)
        
        cx, cy = self.cx, self.cy
        max_r = self._calculate_max_r(ship)
        
        # Draw Theme Image
        theme_id = getattr(ship, 'theme_id', 'Federation')
        ship_img = self.theme_manager.get_image(theme_id, ship.ship_class)
        
        if ship_img:
            img_w, img_h = ship_img.get_size()
            
            # Robust scaling using metrics if available
            metrics = self.theme_manager.get_image_metrics(theme_id, ship.ship_class)
            visible_size = max(img_w, img_h)
            if metrics:
                visible_size = max(metrics.width, metrics.height)
                
            manual_scale = self.theme_manager.get_manual_scale(theme_id, ship.ship_class)
            if manual_scale <= 0: manual_scale = 1.0
            
            # Target size is diameter of the armor ring (2 * max_r)
            target_diameter = max_r * 2.0
            
            # Prevent div by zero
            if visible_size < 1: visible_size = 1
            
            scale_factor = (target_diameter / visible_size) * manual_scale
            
            new_w = int(img_w * scale_factor)
            new_h = int(img_h * scale_factor)
            
            if new_w > 0 and new_h > 0:
                scaled_img = pygame.transform.scale(ship_img, (new_w, new_h))
                # Center image
                rect = scaled_img.get_rect(center=(cx, cy))
                screen.blit(scaled_img, rect)
            
        # Draw structure rings
        font = pygame.font.SysFont("Arial", 10)
        sorted_layers = sorted(ship.layers.items(), key=lambda x: x[1]['radius_pct'], reverse=True)
        
        for ltype, data in sorted_layers:
            pct = data['radius_pct']
            r = int(max_r * pct)
            color = (100, 100, 100)
            if ltype.name == "ARMOR": color = (100, 100, 100)
            elif ltype.name == "OUTER": color = (200, 50, 50)
            elif ltype.name == "INNER": color = (50, 50, 200)
            elif ltype.name == "CORE": color = (200, 200, 200)
            
            pygame.draw.circle(screen, color, (cx, cy), r, 2)

            # Label
            surf = font.render(ltype.name, True, (80, 80, 80))
            screen.blit(surf, (cx - surf.get_width() // 2, cy - r - 12))

        # Draw Components - DISABLED
        # (User requested to stop showing component icons on the ship structure rings)
        pass

        # Draw Arcs
        if show_firing_arcs:
            self.draw_all_firing_arcs(screen, ship)
        elif hovered_component and isinstance(hovered_component, Weapon):
            self.draw_component_firing_arc(screen, hovered_component)

    def draw_all_firing_arcs(self, screen, ship):
        for ltype, data in ship.layers.items():
            for comp in data['components']:
                if isinstance(comp, Weapon):
                    self.draw_weapon_arc(screen, comp)

    def draw_component_firing_arc(self, screen, comp):
        if isinstance(comp, Weapon):
            self.draw_weapon_arc(screen, comp)

    def draw_weapon_arc(self, screen, weapon):
        cx, cy = self.cx, self.cy
        arc_degrees = getattr(weapon, 'firing_arc', 20)
        weapon_range = getattr(weapon, 'range', 1000)
        facing = getattr(weapon, 'facing_angle', 0)
        
        display_range = min(weapon_range / 10, 300)
        
        start_angle = math.radians(90 - facing - (arc_degrees / 2))
        end_angle = math.radians(90 - facing + (arc_degrees / 2))
        
        if isinstance(weapon, BeamWeapon):
            color = (100, 255, 255, 100)
        else:
            color = (255, 200, 100, 100)
            
        points = [(cx, cy)]
        for angle in range(int(math.degrees(start_angle)), int(math.degrees(end_angle)) + 1, 2):
            rad = math.radians(angle)
            x = cx + math.cos(rad) * display_range
            y = cy - math.sin(rad) * display_range
            points.append((x, y))
        points.append((cx, cy))
        
        if len(points) > 2:
            arc_surface = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
            pygame.draw.polygon(arc_surface, (*color[:3], 50), points)
            pygame.draw.lines(arc_surface, color[:3], True, points, 2)
            screen.blit(arc_surface, (0, 0))
            
        font = pygame.font.SysFont("Arial", 10)
        mid_angle = (start_angle + end_angle) / 2
        label_x = cx + math.cos(mid_angle) * (display_range + 15)
        label_y = cy - math.sin(mid_angle) * (display_range + 15)
        label = font.render(f"{weapon_range}", True, color[:3])
        screen.blit(label, (label_x - label.get_width() // 2, label_y - label.get_height() // 2))
