"""Rendering module for drawing ships, HUD elements, and utility functions."""
import pygame
import math
from ship import LayerType


# Layer color constants
LAYER_COLORS = {
    LayerType.ARMOR: (100, 100, 100),
    LayerType.OUTER: (200, 50, 50),
    LayerType.INNER: (50, 50, 200),
    LayerType.CORE: (220, 220, 220)
}


def draw_ship(surface, ship, camera):
    """Draw a ship with its layers and components."""
    if not ship.is_alive:
        return
    
    # Transform Position
    screen_pos = camera.world_to_screen(ship.position)
    cx, cy = int(screen_pos.x), int(screen_pos.y)
    
    # Culling
    radius_screen = 50 * camera.zoom  # approx max radius
    if (cx + radius_screen < 0 or cx - radius_screen > camera.width or 
        cy + radius_screen < 0 or cy - radius_screen > camera.height):
        return

    # Helper for scaling based on zoom
    def scale(val):
        return int(val * camera.zoom)
    
    # Use ship's calculated radius (based on actual mass)
    base_radius = ship.radius
    scaled_radius = scale(base_radius)
    
    # Draw Theme Image if available
    from ship_theme import ShipThemeManager
    theme_mgr = ShipThemeManager.get_instance()
    theme_id = getattr(ship, 'theme_id', 'Federation')
    ship_img = theme_mgr.get_image(theme_id, ship.ship_class)
    
    drawn_image = False
    
    if ship_img and camera.zoom > 0.01:
        # Scale logic: "scaled so that the visible portion of the vesle is approximatly the same length as the diameter of the circle"
        # Circle diameter = 2 * base_radius. 
        target_size = 2 * scale(base_radius) # Matches diameter exactly
        
        img_w, img_h = ship_img.get_size()
        
        # Get visible metrics to ignore transparent padding
        metrics = theme_mgr.get_image_metrics(theme_id, ship.ship_class)
        visible_size = max(img_w, img_h)
        if metrics:
            visible_size = max(metrics.width, metrics.height)
            
        # Avoid division by zero
        if visible_size < 1: visible_size = 1
        
        # Get optional manual scale from theme.json (default 1.0)
        manual_scale = theme_mgr.get_manual_scale(theme_id, ship.ship_class)
        
        scale_factor = (target_size / visible_size) * manual_scale
        
        rotation_angle = -ship.angle - 90
        
        new_w = int(img_w * scale_factor)
        new_h = int(img_h * scale_factor)
        
        if new_w > 0 and new_h > 0:
            scaled_img = pygame.transform.scale(ship_img, (new_w, new_h))
            rotated_img = pygame.transform.rotate(scaled_img, rotation_angle)
            
            rect = rotated_img.get_rect(center=(cx, cy))
            surface.blit(rotated_img, rect)
            drawn_image = True
            
    # Draw Overlay Circles (Collision Radius)
    # "I want to have a empty circle that should represent the radius of the vesle when the ovelay is on"
    show_overlay = getattr(camera, 'show_overlay', False) 
    
    if show_overlay:
        pygame.draw.circle(surface, (100, 255, 100), (cx, cy), scale(base_radius), 1)
        
        # Draw Layers (from large to small)
        pygame.draw.circle(surface, LAYER_COLORS[LayerType.ARMOR], (cx, cy), scale(base_radius), 1)
        pygame.draw.circle(surface, LAYER_COLORS[LayerType.OUTER], (cx, cy), scale(base_radius * 0.8), 1)
        pygame.draw.circle(surface, LAYER_COLORS[LayerType.INNER], (cx, cy), scale(base_radius * 0.5), 1)
        pygame.draw.circle(surface, LAYER_COLORS[LayerType.CORE], (cx, cy), scale(base_radius * 0.2), 1)

        # Draw Components (Simplified visualization for Battle)
        if camera.zoom > 0.3:
            for ltype, data in ship.layers.items():
                radius = 0
                if ltype == LayerType.CORE: radius = base_radius * 0.1
                elif ltype == LayerType.INNER: radius = base_radius * 0.35
                elif ltype == LayerType.OUTER: radius = base_radius * 0.65
                elif ltype == LayerType.ARMOR: radius = base_radius * 0.9
                
                comps = data['components']
                if not comps:
                    continue
                
                angle_step = 360 / len(comps)
                current_angle = ship.angle  # Rotate with ship
                
                for comp in comps:
                    if not comp.is_active:
                        continue
                    rad = math.radians(current_angle)
                    off_x = math.cos(rad) * radius
                    off_y = math.sin(rad) * radius
                    
                    comp_world_pos = ship.position + pygame.math.Vector2(off_x, off_y)
                    comp_screen = camera.world_to_screen(comp_world_pos)
                    
                    color = (200, 200, 200)
                    if comp.has_ability('WeaponAbility'): color = (255, 50, 50)
                    elif comp.has_ability('CombatPropulsion'): color = (50, 255, 100)
                    # Phase 7: Use ability-based check instead of type_str
                    elif comp.has_ability('ArmorAbility') or comp.major_classification == 'Armor': color = (100, 100, 100)
                    
                    pygame.draw.circle(surface, color, (int(comp_screen.x), int(comp_screen.y)), max(1, scale(3)))
                    current_angle += angle_step
        
        # Draw Direction indicator
        dir_vec = ship.forward_vector()
        end_pos_screen = camera.world_to_screen(ship.position + dir_vec * (base_radius + 10))
        pygame.draw.line(surface, (255, 255, 0), (cx, cy), (int(end_pos_screen.x), int(end_pos_screen.y)), max(1, scale(2)))

    
    if not drawn_image:
        # Draw simple dot icon for low zoom if no image
        color = ship.color  # Use ship identity color
        pygame.draw.circle(surface, color, (cx, cy), max(2, scale(3)))  # Minimum 2px dot
        return


def draw_bar(surface, x, y, w, h, pct, color):
    """Draw a progress bar with background and border."""
    pct = max(0, min(1, pct))
    pygame.draw.rect(surface, (50, 50, 50), (x, y, w, h))
    pygame.draw.rect(surface, color, (x, y, w * pct, h))
    pygame.draw.rect(surface, (200, 200, 200), (x, y, w, h), 1)


def draw_hud(surface, ship, x, y):
    """Draw ship HUD with stats and component list."""
    font_title = pygame.font.SysFont("Arial", 16, bold=True)
    font_med = pygame.font.SysFont("Arial", 14)
    font_small = pygame.font.SysFont("Arial", 12)
    
    # Header
    status_color = (100, 255, 100) if ship.is_alive else (255, 50, 50)
    name_text = font_title.render(f"{ship.name}", True, status_color)
    surface.blit(name_text, (x, y))
    y += 20
    
    # Physics Stats
    if ship.mass > 0:
        accel = ship.total_thrust / ship.mass
        top_speed = accel / ship.drag if ship.drag > 0 else 0
        
        stats_text = f"Top Speed: {int(top_speed)}"
        accel_text = f"Accel: {accel:.1f}"
        
        s_surf = font_med.render(stats_text, True, (200, 200, 255))
        a_surf = font_med.render(accel_text, True, (200, 200, 255))
        surface.blit(s_surf, (x, y))
        surface.blit(a_surf, (x + 120, y))
        y += 20
    
    # Resources
    draw_bar(surface, x, y, 100, 8, ship.current_fuel / ship.max_fuel if ship.max_fuel > 0 else 0, (255, 165, 0))
    surface.blit(font_small.render("Fuel", True, (200, 200, 200)), (x + 105, y - 2))
    y += 12
    draw_bar(surface, x, y, 100, 8, ship.current_ammo / ship.max_ammo if ship.max_ammo > 0 else 0, (255, 50, 50))
    surface.blit(font_small.render("Ammo", True, (200, 200, 200)), (x + 105, y - 2))
    y += 12
    draw_bar(surface, x, y, 100, 8, ship.current_energy / ship.max_energy if ship.max_energy > 0 else 0, (50, 100, 255))
    surface.blit(font_small.render("Energy", True, (200, 200, 200)), (x + 105, y - 2))
    y += 20
    
    # Component List
    layer_order = [LayerType.ARMOR, LayerType.OUTER, LayerType.INNER, LayerType.CORE]
    
    for ltype in layer_order:
        l_text = font_med.render(f"[{ltype.name}]", True, (150, 150, 150))
        surface.blit(l_text, (x, y))
        y += 18
        
        components = ship.layers[ltype]['components']
        if not components:
            none_text = font_small.render("  (Empty)", True, (100, 100, 100))
            surface.blit(none_text, (x, y))
            y += 14
            continue
            
        for comp in components:
            c_color = (200, 200, 200)
            if not comp.is_active:
                c_color = (80, 80, 80)
            elif comp.current_hp < comp.max_hp * 0.5:
                c_color = (255, 100, 100)
                
            c_name = font_small.render(f"  {comp.name}", True, c_color)
            surface.blit(c_name, (x, y))
            
            if comp.max_hp > 0:
                bx = x + 120
                pct = comp.current_hp / comp.max_hp
                bar_color = (50, 200, 50) if comp.is_active else (50, 50, 50)
                if pct < 0.5: bar_color = (200, 200, 50)
                if pct < 0.2: bar_color = (200, 50, 50)
                
                draw_bar(surface, bx, y + 2, 60, 6, pct, bar_color)
            
            y += 14
