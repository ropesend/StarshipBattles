import pygame
import math
from ship import VEHICLE_CLASSES, LayerType

from ui.colors import COLORS
SHIP_VIEW_BG = COLORS['bg_deep']

class SchematicView:
    def __init__(self, rect, sprite_manager, theme_manager):
        self.rect = rect
        self.sprite_mgr = sprite_manager
        self.theme_manager = theme_manager
        self.cx = rect.centerx
        self.cy = rect.centery
        self.arc_cache = {} # Key: (weapon_id, range, arc, facing, rect_size) -> surface

    def update_rect(self, rect):
        self.rect = rect
        self.cx = rect.centerx
        self.cy = rect.centery
        # Invalidate cache if view size changes significantly? 
        # Actually arcs are drawn relative to center, if center moves we just blit differently.
        # But if screen size changes, surface size might need to change.
        self.invalidate_cache()

    def invalidate_cache(self):
        self.arc_cache = {}

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
        elif hovered_component and hovered_component.has_ability('WeaponAbility'):
            self.draw_component_firing_arc(screen, hovered_component)

    def draw_all_firing_arcs(self, screen, ship):
        for ltype, data in ship.layers.items():
            for comp in data['components']:
                if comp.has_ability('WeaponAbility'):
                    self.draw_weapon_arc(screen, comp)

    def draw_component_firing_arc(self, screen, comp):
        if comp.has_ability('WeaponAbility'):
            self.draw_weapon_arc(screen, comp)

    def _get_cached_arc(self, screen_size, weapon):
        cx, cy = self.cx, self.cy
        # Phase 7: Use ability-based access for weapon properties
        weapon_ab = weapon.get_ability('WeaponAbility')
        arc_degrees = weapon_ab.firing_arc if weapon_ab else 20
        weapon_range = weapon_ab.range if weapon_ab else 1000
        facing = weapon_ab.facing_angle if weapon_ab else 0
        w_id = weapon.id
        
        # Cache Key: (Weapon ID, Range, Arc, Facing, Screen Size Tuple)
        # Using Weapon ID ensures unique weapons (with modifiers) are cached uniquely.
        # But if we modify the weapon, we need to invalidate or key off value.
        # Ideally we key off value.
        cache_key = (w_id, weapon_range, arc_degrees, facing, screen_size)
        
        if cache_key in self.arc_cache:
            return self.arc_cache[cache_key]
            
        display_range = min(weapon_range / 10, 300)
        
        start_angle = math.radians(90 - facing - (arc_degrees / 2))
        end_angle = math.radians(90 - facing + (arc_degrees / 2))
        
        if weapon.has_ability('BeamWeaponAbility'):
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
            arc_surface = pygame.Surface(screen_size, pygame.SRCALPHA)
            pygame.draw.polygon(arc_surface, (*color[:3], 50), points)
            pygame.draw.lines(arc_surface, color[:3], True, points, 2)
            
            # Label
            font = pygame.font.SysFont("Arial", 10)
            mid_angle = (start_angle + end_angle) / 2
            label_x = cx + math.cos(mid_angle) * (display_range + 15)
            label_y = cy - math.sin(mid_angle) * (display_range + 15)
            label = font.render(f"{weapon_range}", True, color[:3])
            arc_surface.blit(label, (label_x - label.get_width() // 2, label_y - label.get_height() // 2))
            
            self.arc_cache[cache_key] = arc_surface
            return arc_surface
        
        self.arc_cache[cache_key] = None
        return None

    def draw_weapon_arc(self, screen, weapon):
        surface = self._get_cached_arc(screen.get_size(), weapon)
        if surface:
            screen.blit(surface, (0, 0))
