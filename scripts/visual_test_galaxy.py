import sys
import os
import pygame
import math

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from game.strategy.data.galaxy import Galaxy, StarSystem
from game.strategy.data.hex_math import hex_to_pixel
# Imports for snapping
from game.strategy.data.hex_math import pixel_to_hex, HexCoord
from game.ui.renderer.camera import Camera

WIDTH, HEIGHT = 1600, 900
HEX_SIZE = 10 # Pixel size of hex for rendering

def main():
    pygame.init()
    # Use global/non-hardcoded for resize
    current_w, current_h = WIDTH, HEIGHT
    screen = pygame.display.set_mode((current_w, current_h), pygame.RESIZABLE)
    pygame.display.set_caption("Galaxy Gen Visualizer - Phase 2")
    clock = pygame.time.Clock()
    
    # 1. Generate Galaxy
    print("Generating Galaxy...")
    galaxy = Galaxy(radius=4000) # Increased from 500 to 4000 (8x visual scale, massive area)
    # Spaced out stars: min_dist 60 -> 400. Count 50 -> 100 (so they aren't too lonely, but very spread)
    systems = galaxy.generate_systems(count=80, min_dist=400)
    galaxy.generate_warp_lanes() # Auto-link
    print(f"Generated {len(systems)} systems.")
    
    # 2. Setup Camera
    camera = Camera(current_w, current_h)
    camera.position = pygame.math.Vector2(0, 0) # Center on Galaxy Center (0,0)
    camera.zoom = 0.1 # Start much further out to see the huge galaxy
    
    running = True
    while running:
        dt = clock.tick(60) / 1000.0
        events = pygame.event.get()
        
        for event in events:
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.VIDEORESIZE:
                current_w, current_h = event.w, event.h
                screen = pygame.display.set_mode((current_w, current_h), pygame.RESIZABLE)
                camera.width = current_w
                camera.height = current_h
                
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                # Regenerate
                print("Regenerating...")
                galaxy = Galaxy(radius=4000)
                systems = galaxy.generate_systems(count=80, min_dist=400)
                galaxy.generate_warp_lanes()
                
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_p:
               # Debug print nearby systems
               pass
        
        # Update Camera
        camera.update_input(dt, events)
        
        # Draw Background
        screen.fill((10, 10, 15))
        
        # --- GRID RENDERING ---
        if camera.zoom > 1.5:
            # Get corners in world space
            tl_world = camera.screen_to_world((0, 0))
            tr_world = camera.screen_to_world((current_w, 0))
            bl_world = camera.screen_to_world((0, current_h))
            br_world = camera.screen_to_world((current_w, current_h))
            
            # Convert to hex coords
            corners = [
                pixel_to_hex(tl_world.x, tl_world.y, HEX_SIZE),
                pixel_to_hex(tr_world.x, tr_world.y, HEX_SIZE),
                pixel_to_hex(bl_world.x, bl_world.y, HEX_SIZE),
                pixel_to_hex(br_world.x, br_world.y, HEX_SIZE)
            ]
            
            # Find bounds
            min_q = min(c.q for c in corners) - 2
            max_q = max(c.q for c in corners) + 2
            min_r = min(c.r for c in corners) - 2
            max_r = max(c.r for c in corners) + 2
            
            grid_color = (30, 30, 40)
            
            for q in range(min_q, max_q):
                for r in range(min_r, max_r):
                    hc = HexCoord(q, r)
                    cx, cy = hex_to_pixel(hc, HEX_SIZE)
                    
                    corners_px = []
                    for i in range(6):
                        angle_deg = 60 * i 
                        angle_rad = math.radians(angle_deg)
                        px = cx + HEX_SIZE * math.cos(angle_rad)
                        py = cy + HEX_SIZE * math.sin(angle_rad)
                        corners_px.append(camera.world_to_screen(pygame.math.Vector2(px, py)))
                    
                    pygame.draw.lines(screen, grid_color, True, corners_px, 1)

        # --- WARP LANE RENDERING (Global / Unculled for continuity) ---
        # Draw these FIRST so stars draw ON TOP
        
        processed_links = set()
        
        for sys in galaxy.systems.values():
            # Calculate System Position
            sx, sy = hex_to_pixel(sys.global_location, HEX_SIZE)
            sys_pos = pygame.math.Vector2(sx, sy)
            
            # Simple line drawing between systems for better visual scaling?
            # Or use correct warp points... let's stick to simple lines for high zoom out
            # High Detail: Warp Points
            
            # Draw Warp Lanes connecting specific Warp Points
            for wp in sys.warp_points:
                target_id = wp.destination_id
                target = next((s for s in galaxy.systems.values() if s.name == target_id), None)
                
                if target and sys.name < target.name: # Draw once per pair
                    # Find corresponding WP in target system
                    target_wp = next((w for w in target.warp_points if w.destination_id == sys.name), None)
                    
                    if target_wp:
                        # Success: We have both WPs.
                        # Calculate Global Pos for WP A
                        wx_a_local, wy_a_local = hex_to_pixel(wp.location, HEX_SIZE)
                        global_ax = sx + wx_a_local
                        global_ay = sy + wy_a_local
                        
                        # Calculate Global Pos for WP B
                        tx, ty = hex_to_pixel(target.global_location, HEX_SIZE)
                        wx_b_local, wy_b_local = hex_to_pixel(target_wp.location, HEX_SIZE)
                        global_bx = tx + wx_b_local
                        global_by = ty + wy_b_local
                        
                        # Screen Coords
                        screen_a = camera.world_to_screen(pygame.math.Vector2(global_ax, global_ay))
                        screen_b = camera.world_to_screen(pygame.math.Vector2(global_bx, global_by))
                        
                        # Draw Line
                        pygame.draw.line(screen, (40, 40, 80), screen_a, screen_b, 1)
                    else:
                        # Fallback (Shouldn't happen with correct generation): Center to center
                        tx, ty = hex_to_pixel(target.global_location, HEX_SIZE)
                        s_screen = camera.world_to_screen(sys_pos)
                        t_screen = camera.world_to_screen(pygame.math.Vector2(tx, ty))
                        pygame.draw.line(screen, (40, 0, 0), s_screen, t_screen, 1) # Red error line

        # --- SYSTEM RENDERING ---
        DETAIL_ZOOM_LEVEL = 3.0
        
        # Sort systems by Y for pseudo-depth? Not needed in 2D top down really.
        
        for sys in galaxy.systems.values():
            hx, hy = hex_to_pixel(sys.global_location, HEX_SIZE) 
            world_pos = pygame.math.Vector2(hx, hy)
            screen_pos = camera.world_to_screen(world_pos)
            
            # Visibility check
            if -200 < screen_pos.x < current_w + 200 and -200 < screen_pos.y < current_h + 200:
                
                # Get Primary Star Properties
                primary = sys.primary_star
                # Render all stars
                if primary:
                    # Draw Primary at center (hx, hy)
                    # Convert diameter (hexes) to pixels
                    # diameter_hexes is the full width. Radius is half.
                    # HEX_SIZE is center-to-corner radius of a single hex.
                    # So 1 hex width (flat to flat) is sqrt(3) * HEX_SIZE
                    # But diameter_hexes usually refers to grid units.
                    # Let's assume diameter_hexes means "this many hexes wide".
                    # Radius in pixels = (diameter / 2) * (width of hex)
                    # Width of hex ~= 1.73 * HEX_SIZE
                    # But let's keep it simple: scale visually.
                    
                    for star in sys.stars:
                         # Calculate position offset from primary
                         # Primary is at 0,0 locally.
                         # Companions are at star.orbit_distance, star.orbit_angle relative
                         
                         # Convert polar to cartesian (hex units) then to pixels
                         # Or just polar to pixels directly?
                         # Hex units...
                         # Distance is in Hexes.
                         # hex_to_pixel usually takes a HexCoord.
                         # We can simulate a HexCoord or just do math.
                         # r = star.orbit_distance * (hex_width?)
                         # Let's say hex distance N means N steps.
                         
                         dist_pixels = 0
                         if star.orbit_distance > 0:
                             # Approx pixel distance
                             dist_pixels = star.orbit_distance * HEX_SIZE * 1.5 
                             # 1.5 is the x-spacing of hexes, good approx.
                             
                             rel_x = math.cos(star.orbit_angle) * dist_pixels
                             rel_y = math.sin(star.orbit_angle) * dist_pixels
                         else:
                             rel_x, rel_y = 0, 0
                             
                         star_screen_pos = camera.world_to_screen(pygame.math.Vector2(hx + rel_x, hy + rel_y))
                         
                         # Size
                         # Base radius in pixels
                         # Let's make 1 hex diameter = 2 * HEX_SIZE pixels roughly
                         radius_px = max(2, int((star.diameter_hexes / 2.0) * HEX_SIZE * 2.0 * camera.zoom))
                         
                         pygame.draw.circle(screen, star.color, star_screen_pos, radius_px)
                         
                         # Add label for companions if zoomed
                         if camera.zoom > 5.0 and star.orbit_distance > 0:
                             s_font = pygame.font.SysFont("arial", 10)
                             s_text = s_font.render(star.name, True, (200, 200, 200))
                             screen.blit(s_text, (star_screen_pos.x, star_screen_pos.y - radius_px - 10))
                
                # --- SYSTEM DETAIL MODE ---
                if camera.zoom > DETAIL_ZOOM_LEVEL:
                    # Draw Orbits & Planets using Hex Coords
                    # 1 hex = HEX_SIZE pixels in world space? 
                    # Actually, the Galaxy Map uses HEX_SIZE=10 for system placement.
                    # Local System Map might use the same scale? 
                    # If Planet is at Hex(0, 5), that is 5 * hex_width away.
                    
                    # Draw Local Hex Grid (Faint)
                    # Range: say 20 hexes radius
                    
                    # Draw Planets
                    for planet in sys.planets:
                        # Convert local hex to pixel offset
                        px_offset, py_offset = hex_to_pixel(planet.location, HEX_SIZE)
                        
                        # Add to System World Pos
                        p_world_x = hx + px_offset
                        p_world_y = hy + py_offset
                        
                        p_screen = camera.world_to_screen(pygame.math.Vector2(p_world_x, p_world_y))
                        
                        # Draw Planet
                        p_color = planet.planet_type.color
                        p_rad = max(2, int(3 * camera.zoom))
                        pygame.draw.circle(screen, p_color, p_screen, p_rad)
                        
                        # Draw Planet Name (Very faint or small unless super zoomed)
                        if camera.zoom > 5.0:
                            p_font = pygame.font.SysFont("arial", 10)
                            p_text = p_font.render(planet.name, True, (150, 150, 150))
                            screen.blit(p_text, (p_screen.x + 5, p_screen.y - 5))
                        
                        # Draw faint ring for orbit indication? 
                        # We can use hex_distance or just circles as approximation
                        # Or draw the specific hex ring?
                        # Drawing circles is easier for visual "Ring 5" check
                        ring_radius_px = planet.orbit_distance * HEX_SIZE * math.sqrt(3) # approx?
                        # Actually hex_to_pixel magnitude
                        
                        # Let's just draw the planet for now as requested "render planets at exact hex location"
                
                # Stars already drawn above in loop
                
                # Draw Warp Points (Close zoom)
                # Draw Warp Points (Close zoom)
                if camera.zoom > 1.5:
                    for wp in sys.warp_points:
                        # Draw Line to Destination System (in Galaxy Map)
                        # if camera.zoom < 0.5: usually just lines between systems
                        # But here in Detail Mode, we might want to see the Warp Point itself
                        
                        # Convert local hex to pixel
                        wx, wy = hex_to_pixel(wp.location, HEX_SIZE)
                        
                        # World Pos relative to system center
                        w_world_x = hx + wx
                        w_world_y = hy + wy
                        
                        w_screen = camera.world_to_screen(pygame.math.Vector2(w_world_x, w_world_y))
                        
                        # Draw Warp Point (Purple)
                        pygame.draw.circle(screen, (200, 0, 255), w_screen, max(2, int(5 * camera.zoom)))
                        
                        # Draw line to center?
                        # pygame.draw.line(screen, (50, 0, 50), screen_pos, w_screen, 1)

                # Name
                if camera.zoom > 0.8:
                    font = pygame.font.SysFont("arial", 12)
                    text = font.render(sys.name, True, (200, 200, 200))
                    screen.blit(text, (screen_pos.x + 10, screen_pos.y))
        
        # Center Marker
        center_screen = camera.world_to_screen(pygame.math.Vector2(0, 0))
        pygame.draw.circle(screen, (50, 50, 60), center_screen, 5 * camera.zoom)

        # UI
        font = pygame.font.SysFont("arial", 20)
        mode_text = font.render(f"Systems: {len(galaxy.systems)} | Zoom: {camera.zoom:.2f} | Detail Mode: {camera.zoom > DETAIL_ZOOM_LEVEL}", True, (255, 255, 255))
        screen.blit(mode_text, (20, 20))
        
        if camera.zoom > DETAIL_ZOOM_LEVEL:
            instr = font.render("SCROLL to Zoom in/out to see Planets (Zoom > 5.0 for names)", True, (100, 255, 100))
            screen.blit(instr, (20, 45))
        
        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()
