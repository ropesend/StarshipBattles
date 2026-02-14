"""Rendering module for drawing ships, HUD elements, and utility functions.

Cross-layer imports (acceptable for rendering):
- LayerType: Runtime - keys layer color map, iterates ship layers
- LayerDefaults: Runtime - default radius percentages for ship layers
"""
import pygame
import math
from game.core.constants import LayerType, LayerDefaults  # Canonical location for LayerType
from game.ui.utils import calculate_ship_image_scale, scale_and_rotate_image


# === Rendering Constants ===
# PROJ-141 CON-UI2-012: Extracted magic numbers to named constants

# Culling threshold - approximate max ship radius for screen bounds check
CULLING_MAX_RADIUS = 50

# Zoom thresholds for level-of-detail rendering
MIN_ZOOM_FOR_IMAGE = 0.01      # Below this, don't render ship images
MIN_ZOOM_FOR_COMPONENTS = 0.3  # Below this, don't render component dots

# Ship image rotation offset (ship images point up, simulation uses right=0)
IMAGE_ROTATION_OFFSET = -90

# Overlay rendering sizes
COMPONENT_DOT_RADIUS = 3       # Base radius for component dots (scaled with zoom)
DIRECTION_LINE_OFFSET = 10     # How far direction indicator extends past ship
DIRECTION_LINE_WIDTH = 2       # Width of direction indicator line

# Fallback rendering (when no ship image available)
FALLBACK_DOT_RADIUS = 3        # Base radius for simple dot icon
FALLBACK_DOT_MIN_SIZE = 2      # Minimum pixel size for fallback dot

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
    radius_screen = CULLING_MAX_RADIUS * camera.zoom
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
    from game.ui.assets import ShipThemeManager
    theme_mgr = ShipThemeManager.instance()
    theme_id = getattr(ship, 'theme_id', 'Federation')
    ship_img = theme_mgr.load_image(theme_id, ship.ship_class)
    
    drawn_image = False
    
    if ship_img and camera.zoom > MIN_ZOOM_FOR_IMAGE:
        # Scale logic: visible portion should match diameter of the collision circle
        target_size = 2 * scale(base_radius)

        # Get visible metrics to ignore transparent padding
        metrics = theme_mgr.get_image_metrics(theme_id, ship.ship_class)
        visible_size = max(metrics.width, metrics.height) if metrics else None

        # Get optional manual scale from theme.json (default 1.0)
        manual_scale = theme_mgr.get_manual_scale(theme_id, ship.ship_class)

        scale_factor = calculate_ship_image_scale(
            ship_img.get_size(), target_size, visible_size, manual_scale
        )

        rotation_angle = -ship.angle + IMAGE_ROTATION_OFFSET
        rotated_img = scale_and_rotate_image(ship_img, scale_factor, rotation_angle)

        if rotated_img.get_size() != ship_img.get_size() or scale_factor > 0:
            rect = rotated_img.get_rect(center=(cx, cy))
            surface.blit(rotated_img, rect)
            drawn_image = True
            
    # Draw Overlay Circles (Collision Radius)
    # Shows collision radius and layer boundaries when overlay mode is active
    show_overlay = getattr(camera, 'show_overlay', False) 
    
    if show_overlay:
        pygame.draw.circle(surface, (100, 255, 100), (cx, cy), scale(base_radius), 1)
        
        # Draw Layers (from large to small)
        pygame.draw.circle(surface, LAYER_COLORS[LayerType.ARMOR], (cx, cy), scale(base_radius), 1)
        pygame.draw.circle(surface, LAYER_COLORS[LayerType.OUTER], (cx, cy), scale(base_radius * LayerDefaults.OUTER_RADIUS_PCT), 1)
        pygame.draw.circle(surface, LAYER_COLORS[LayerType.INNER], (cx, cy), scale(base_radius * LayerDefaults.INNER_RADIUS_PCT), 1)
        pygame.draw.circle(surface, LAYER_COLORS[LayerType.CORE], (cx, cy), scale(base_radius * LayerDefaults.CORE_RADIUS_PCT), 1)

        # Draw Components (Simplified visualization for Battle)
        # Component dots are placed at the center of each layer ring
        if camera.zoom > MIN_ZOOM_FOR_COMPONENTS:
            for ltype, data in ship.layers.items():
                radius = 0
                if ltype == LayerType.CORE:
                    # Center of core: halfway from center to CORE boundary
                    radius = base_radius * (LayerDefaults.CORE_RADIUS_PCT / 2)
                elif ltype == LayerType.INNER:
                    # Center of inner: midpoint between CORE and INNER boundaries
                    radius = base_radius * ((LayerDefaults.CORE_RADIUS_PCT + LayerDefaults.INNER_RADIUS_PCT) / 2)
                elif ltype == LayerType.OUTER:
                    # Center of outer: midpoint between INNER and OUTER boundaries
                    radius = base_radius * ((LayerDefaults.INNER_RADIUS_PCT + LayerDefaults.OUTER_RADIUS_PCT) / 2)
                elif ltype == LayerType.ARMOR:
                    # Center of armor: midpoint between OUTER and edge (1.0)
                    radius = base_radius * ((LayerDefaults.OUTER_RADIUS_PCT + 1.0) / 2)
                
                comps = data.components
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
                    elif comp.has_ability('ArmorAbility') or comp.major_classification == 'Armor': color = (100, 100, 100)
                    
                    pygame.draw.circle(surface, color, (int(comp_screen.x), int(comp_screen.y)), max(1, scale(COMPONENT_DOT_RADIUS)))
                    current_angle += angle_step
        
        # Draw Direction indicator
        dir_vec = ship.forward_vector()
        end_pos_screen = camera.world_to_screen(ship.position + dir_vec * (base_radius + DIRECTION_LINE_OFFSET))
        pygame.draw.line(surface, (255, 255, 0), (cx, cy), (int(end_pos_screen.x), int(end_pos_screen.y)), max(1, scale(DIRECTION_LINE_WIDTH)))

    
    if not drawn_image:
        # Draw simple dot icon for low zoom if no image
        color = ship.color  # Use ship identity color
        pygame.draw.circle(surface, color, (cx, cy), max(FALLBACK_DOT_MIN_SIZE, scale(FALLBACK_DOT_RADIUS)))
        return


