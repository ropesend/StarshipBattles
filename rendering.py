"""Rendering module for drawing ships, HUD elements, and utility functions."""
import pygame
import math
from ship import LayerType
from components import Weapon, Engine, Armor


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
    
    if scaled_radius < 3:
        # Draw simple dot icon for low zoom
        color = ship.color  # Use ship identity color
        pygame.draw.circle(surface, color, (cx, cy), 3)  # Fixed 3px dot
        # Direction
        dir_vec = ship.forward_vector()
        end_pos = camera.world_to_screen(ship.position + dir_vec * 100)
        pygame.draw.line(surface, (255, 255, 0), (cx, cy), (int(end_pos.x), int(end_pos.y)), 1)
        return

    # Draw Layers (from large to small)
    pygame.draw.circle(surface, LAYER_COLORS[LayerType.ARMOR], (cx, cy), scale(base_radius))
    pygame.draw.circle(surface, LAYER_COLORS[LayerType.OUTER], (cx, cy), scale(base_radius * 0.8))
    pygame.draw.circle(surface, LAYER_COLORS[LayerType.INNER], (cx, cy), scale(base_radius * 0.5))
    pygame.draw.circle(surface, LAYER_COLORS[LayerType.CORE], (cx, cy), scale(base_radius * 0.2))
    
    # Draw Direction indicator
    dir_vec = ship.forward_vector()
    end_pos_screen = camera.world_to_screen(ship.position + dir_vec * (base_radius + 10))
    pygame.draw.line(surface, (255, 255, 0), (cx, cy), (int(end_pos_screen.x), int(end_pos_screen.y)), max(1, scale(2)))

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
                if isinstance(comp, Weapon): color = (255, 50, 50)
                elif isinstance(comp, Engine): color = (50, 255, 100)
                elif isinstance(comp, Armor): color = (100, 100, 100)
                
                pygame.draw.circle(surface, color, (int(comp_screen.x), int(comp_screen.y)), max(1, scale(3)))
                current_angle += angle_step


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
