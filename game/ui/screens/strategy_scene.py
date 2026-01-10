import math
import pygame
import pygame_gui
from game.strategy.data.galaxy import Galaxy, StarSystem, WarpPoint, Planet
from game.strategy.data.hex_math import hex_to_pixel, pixel_to_hex, HexCoord, hex_distance
from game.ui.renderer.camera import Camera
from game.ui.screens.strategy_screen import StrategyInterface
from game.strategy.data.fleet import Fleet
import os
import random
from game.strategy.data.pathfinding import find_path_interstellar, find_path_deep_space

class StrategyScene:
    """Manages strategy layer simulation, rendering, and UI."""
    
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # Galaxy Data
        self.galaxy = Galaxy(radius=4000)
        print("StrategyScene: Generating Galaxy...")
        self.systems = self.galaxy.generate_systems(count=80, min_dist=400)
        self.galaxy.generate_warp_lanes()
        print(f"StrategyScene: Generated {len(self.systems)} systems.")
        
        # Camera
        self.camera = Camera(screen_width, screen_height)
        self.camera.max_zoom = 25.0
        self.camera.zoom = 0.1
        
        # UI
        self.ui = StrategyInterface(self, screen_width, screen_height)
        
        # Constants
        self.HEX_SIZE = 10
        self.DETAIL_ZOOM_LEVEL = 3.0
        
        # Input State
        self.selected_object = None 
        self.hover_hex = None
        
        # Fleets
        self.fleets = []
        # Create a test fleet at the first system
        if self.systems:
            start_sys = self.systems[0]
            f = Fleet(1, 0, start_sys.global_location)
            f.ships.append("TestShip")
            self.fleets.append(f)
            self.selected_fleet = f # Auto-select for testing

        # Assets
        self.assets = {}
        self._load_assets()

    def _load_assets(self):
        """Load visual assets."""
        self.assets['stars'] = {}
        self.assets['planets'] = {}
        self.assets['warp_points'] = []
        
        # Base Paths
        base_path = "assets/Images/Stellar Objects"
        star_path = os.path.join(base_path, "Stars")
        planet_base_path = os.path.join(base_path, "Planets/Planets")
        wp_path = os.path.join(base_path, "Warp Points")
        
        # Load Stars
        # Map simple colors (from generation) to asset filenames
        # Our generator uses RGB tuples. Let's map approximate colors.
        # (255, 200, 200) -> Red, (200, 200, 255) -> Blue/White, etc.
        # For now, let's just load specific files and map arbitrarily or by name if possible.
        # Files: StarBlueAsset.png, StarRedAsset.png, StarYellowAsset.png, etc.
        
        star_files = {
            'blue': 'StarBlueAsset.png',
            'red': 'StarRedAsset.png',
            'yellow': 'StarYellowAsset.png',
            'white': 'StarWhiteAsset.png',
            'orange': 'StarOrangeAsset.png',
            'neutron': 'StarNeutronAsset.png',
            'black': 'StarBlackAsset.png'
        }
        
        for k, filename in star_files.items():
            full_path = os.path.join(star_path, filename)
            if os.path.exists(full_path):
                img = pygame.image.load(full_path).convert_alpha()
                self.assets['stars'][k] = img
            else:
                print(f"Warning: Asset not found: {full_path}")
                
        # Load Planets (Scan directory)
        if os.path.exists(planet_base_path):
            files = os.listdir(planet_base_path)
            for f in files:
                if f.endswith(".png"):
                    # Categorize by prefix: planet_gas_, planet_terr_, planet_ice_, planet_ven_, planet_moon_
                    cat = "unknown"
                    if "planet_gas_" in f: cat = "gas"
                    elif "planet_terr_" in f: cat = "terran"
                    elif "planet_ice_" in f: cat = "ice"
                    elif "planet_ven_" in f: cat = "venus" # Desert/Hot
                    elif "planet_moon_" in f: cat = "moon"
                    elif "planet_earth" in f: cat = "terran"
                    elif "planet_mars" in f: cat = "terran" # weak mapping
                    
                    if cat not in self.assets['planets']:
                        self.assets['planets'][cat] = []
                    
                    full_path = os.path.join(planet_base_path, f)
                    img = pygame.image.load(full_path).convert_alpha()
                    self.assets['planets'][cat].append(img)
                    
        # Load Warp Points
        if os.path.exists(wp_path):
            for i in range(1, 4):
                fname = f"Warp_Point_{i}.jpg"
                full_path = os.path.join(wp_path, fname)
                if os.path.exists(full_path):
                    img = pygame.image.load(full_path).convert() # JPG no alpha
                   # img.set_colorkey((0,0,0)) # Optional if simple trans
                    self.assets['warp_points'].append(img)

    def handle_resize(self, width, height):
        self.screen_width = width
        self.screen_height = height
        # Adjust camera to exclude sidebar? 
        # For now, let's keep camera full width but input will be blocked by UI.
        # Ideally: self.camera.viewport_width = width - 600
        self.camera.width = width
        self.camera.height = height
        self.ui.handle_resize(width, height)

    def update(self, dt):
        self.camera.update(dt)
        self.ui.update(dt)
        
        # Update Fleets (Visual movement can be added here)
        for f in self.fleets:
            f.update(dt)

    def handle_event(self, event):
        self.ui.handle_event(event)

        # Handle UI Selection Events from the Interface
        if event.type == pygame_gui.UI_SELECTION_LIST_NEW_SELECTION:
            if event.ui_element == self.ui.sector_list:
                selected_label = event.text
                obj = self.ui.current_sector_objects.get(selected_label)
                if obj:
                    self.on_ui_selection(obj)

        # Fleet Movement Input
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_m:
                if self.selected_fleet:
                    self.input_mode = 'MOVE'
                    print("Input Mode: MOVE - Click designation for fleet.")
                else:
                    print("Select a fleet first.")
            elif event.key == pygame.K_ESCAPE:
                if getattr(self, 'input_mode', 'SELECT') == 'MOVE':
                    self.input_mode = 'SELECT'
                    print("Input Mode: SELECT")

    def update_input(self, dt, events):
        """Update camera input."""
        self.camera.update_input(dt, events)
        
        # Hover Logic
        mx, my = pygame.mouse.get_pos()
        world_pos = self.camera.screen_to_world((mx, my))
        self.hover_hex = pixel_to_hex(world_pos.x, world_pos.y, self.HEX_SIZE)

    def handle_click(self, mx, my, button):
        """Handle mouse clicks."""
        if self.ui.handle_click(mx, my, button):
            return True
        
        current_mode = getattr(self, 'input_mode', 'SELECT')
        
        if current_mode == 'MOVE':
            if button == 1: # Left Click to Move
                self._handle_move_designation(mx, my)
                return True
            elif button == 3: # Right click cancels
                self.input_mode = 'SELECT'
                print("Input Mode: SELECT")
                return True
                
        elif current_mode == 'SELECT':    
            if button == 1: # Left Click: Select
                self._handle_picking(mx, my)
                return True
            elif button == 3: # Right Click: Quick Move (Legacy/Contextual)
                if self.selected_fleet:
                    self._handle_move_designation(mx, my)
                    return True
            
        return False

    def _handle_picking(self, mx, my):
        """Raycast from screen to galaxy objects."""
        world_pos = self.camera.screen_to_world((mx, my))
        hex_clicked = pixel_to_hex(world_pos.x, world_pos.y, self.HEX_SIZE)
        
        # 1. Identify System Context
        # Find which system (if any) this hex belongs to.
        # We can reuse _get_system_at_hex logic or distance check.
        clicked_system = self._get_system_at_hex(hex_clicked)
        
        # 2. Identify Precise Objects at this Hex (Sector Content)
        sector_contents = []
        
        # Check Fleets
        for f in self.fleets:
            if f.location == hex_clicked:
                 sector_contents.append(f)
                 
        if clicked_system:
             # Check System Objects at this hex
             # Star?
             if hex_distance(hex_clicked, clicked_system.global_location) == 0:
                 sector_contents.append(clicked_system) # Star
                 
             # Planets
             for p in clicked_system.planets:
                 if p.location == hex_clicked - clicked_system.global_location: # Local to Global check?
                     # Wait, planet.location is local.
                     # hex_clicked is global.
                     # p_global = sys.global + p.local
                     p_global = clicked_system.global_location + p.location
                     if p_global == hex_clicked:
                         sector_contents.append(p)
                         
             # Warp Points
             for wp in clicked_system.warp_points:
                 wp_global = clicked_system.global_location + wp.location
                 if wp_global == hex_clicked:
                     sector_contents.append(wp)

        # 3. Populate UI
        
        # System Panel
        if clicked_system:
            sys_contents = [clicked_system] # Star
            sys_contents.extend(clicked_system.planets)
            sys_contents.extend(clicked_system.warp_points)
            # Fleets in system?
            # Ideally find all fleets in system radius.
            self.ui.show_system_info(clicked_system, sys_contents)
        else:
            self.ui.show_system_info(None, [])
            
        # Sector Panel
        self.ui.show_sector_info(hex_clicked, sector_contents)
        
        # 4. Detail View Selection Logic
        # If we clicked a specific visual element, prefer that.
        # Use existing distance logic for precision picking, or just pick first in sector list?
        # User said "The system view should show... The sector view..."
        # Let's try to pick the "most interesting" item in the sector list if available.
        
        best_pick = None
        if sector_contents:
            best_pick = sector_contents[0] # Default to first
            # Prefer fleets or planets over warp points?
            
        if best_pick:
            self.on_ui_selection(best_pick)
            self.selected_object = best_pick
        elif clicked_system:
             # If clicked empty space in system, maybe show System/Star details?
             self.on_ui_selection(clicked_system)
             self.selected_object = clicked_system
        else:
             self.selected_object = None
             self.ui.show_detailed_report(None, None)

    def on_ui_selection(self, obj):
        """Called when user selects an item in the UI list."""
        self.selected_object = obj
        
        # Get Portrait
        img = self._get_object_asset(obj)
        self.ui.show_detailed_report(obj, img)
        
    def _get_object_asset(self, obj):
        """Resolve the visual asset for a data object."""
        if hasattr(obj, 'star_type'):
            # System/Star - logic from _draw_systems
            color = obj.star_type.color
            asset_key = 'yellow'
            if color[0] > 200 and color[1] < 100: asset_key = 'red'
            elif color[2] > 200 and color[0] < 100: asset_key = 'blue'
            elif color[0] > 200 and color[1] > 200 and color[2] > 200: asset_key = 'white'
            elif color[0] > 200 and color[1] > 150: asset_key = 'orange'
            return self.assets['stars'].get(asset_key)
            
        elif hasattr(obj, 'planet_type'):
            p_type_name = obj.planet_type.name.lower()
            cat = 'terran'
            if 'gas' in p_type_name: cat = 'gas'
            elif 'ice' in p_type_name: cat = 'ice'
            elif 'desert' in p_type_name or 'hot' in p_type_name: cat = 'venus'
            
            images = self.assets['planets'].get(cat, [])
            if images:
                idx = hash(obj) % len(images)
                return images[idx]
                
        elif hasattr(obj, 'destination_id'): # Warp Point
             if self.assets['warp_points']:
                 idx = hash(obj) % len(self.assets['warp_points'])
                 return self.assets['warp_points'][idx]
                 
        return None
        
    def _handle_move_designation(self, mx, my):
        """Handle designating a move target."""
        if not self.selected_fleet:
            return
            
        world_pos = self.camera.screen_to_world((mx, my))
        target_hex = pixel_to_hex(world_pos.x, world_pos.y, self.HEX_SIZE)
        
        print(f"Calculating path to {target_hex}...")
        path = self.calculate_hybrid_path(self.selected_fleet.location, target_hex)
        
        if path:
            print(f"Path confirmed: {len(path)} steps.")
            self.selected_fleet.path = path
            self.selected_fleet.destination = target_hex
            self.input_mode = 'SELECT' # Revert to select after cmd
        else:
            print("Cannot find path to target.")

    def calculate_hybrid_path(self, start_hex, end_hex):
        """
        Calculate path combining local hex movement and interstellar warp jumps.
        Returns list of HexCoords.
        """
        # 1. Identify Start/End Systems
        # If in deep space, find NEAREST system to enter/exit the network.
        start_sys = self._get_system_at_hex(start_hex)
        if not start_sys:
            start_sys = self._find_nearest_system(start_hex)
            
        end_sys = self._get_system_at_hex(end_hex)
        if not end_sys:
            end_sys = self._find_nearest_system(end_hex)
        
        # Case A: Same System (or both Deep Space near same system)
        if start_sys and end_sys and start_sys == end_sys:
            return find_path_deep_space(start_hex, end_hex)
            
        # Case B: Interstellar
        if start_sys and end_sys:
            # 1. Find System Path
            sys_path = find_path_interstellar(start_sys, end_sys, self.galaxy)
            if not sys_path:
                # If no system path possible (disconnected graph?), fallback to direct
                return find_path_deep_space(start_hex, end_hex)
                
            full_path = []
            current_hex = start_hex
            
            # Iterate through system path to connect warp points
            # sys_path is [StartSys, NextSys, ..., EndSys]
            
            for i in range(len(sys_path) - 1):
                curr_sys = sys_path[i]
                next_sys = sys_path[i+1]
                
                # Find Warp Point in curr_sys connecting to next_sys
                target_wp = next((wp for wp in curr_sys.warp_points if wp.destination_id == next_sys.name), None)
                
                if target_wp:
                    # Calculate WP Global Hex
                    wp_global = curr_sys.global_location + target_wp.location
                    
                    # Local Path to WP
                    segment = find_path_deep_space(current_hex, wp_global)
                    if segment:
                        full_path.extend(segment)
                    
                    # "Jump" to reciprocal WP
                    arrival_wp = next((wp for wp in next_sys.warp_points if wp.destination_id == curr_sys.name), None)
                    if arrival_wp:
                        arrival_global = next_sys.global_location + arrival_wp.location
                        full_path.append(arrival_global) # The jump
                        current_hex = arrival_global
            
            # Final Leg: From last arrival WP to specific end_hex
            final_segment = find_path_deep_space(current_hex, end_hex)
            if final_segment:
                full_path.extend(final_segment)
            
            return full_path
            
        # Fallback: Just direct line (Deep Space logic)
        return find_path_deep_space(start_hex, end_hex)

    def _get_system_at_hex(self, hex_c):
        """Find which system implies ownership of this hex (simplistic radius check)."""
        # Systems are sparse, so checking radius from global center works.
        # System radius is conceptual, let's say 50 hexes?
        SYSTEM_RADIUS = 50
        
        best_sys = None
        min_dist = float('inf')
        
        for sys in self.galaxy.systems.values():
            dist = hex_distance(hex_c, sys.global_location)
            if dist < SYSTEM_RADIUS:
                if dist < min_dist:
                    min_dist = dist
                    best_sys = sys
        
        return best_sys

    def _find_nearest_system(self, hex_c):
        """Find the nearest system to a hex coordinate (ignoring radius)."""
        best_sys = None
        min_dist = float('inf')
        
        for sys in self.galaxy.systems.values():
            dist = hex_distance(hex_c, sys.global_location)
            if dist < min_dist:
                min_dist = dist
                best_sys = sys
        return best_sys

    def draw(self, screen):
        """Render the scene."""
        screen.fill((10, 10, 15)) 
        
        if self.camera.zoom >= 0.4:
            self._draw_grid(screen)
            
        self._draw_warp_lanes(screen)
        self._draw_systems(screen)
        self._draw_fleets(screen) 
        
        # Move Line Preview
        if getattr(self, 'input_mode', 'SELECT') == 'MOVE' and self.selected_fleet:
             self._draw_move_preview(screen)
        
        # Hover Highlight
        # Hover Highlight
        if self.hover_hex and self.camera.zoom >= 0.5:
             self._draw_hover_hex(screen)
        
        self.ui.draw(screen)

    def _draw_move_preview(self, screen):
        # Draw line from selected fleet to mouse cursor
        fx, fy = hex_to_pixel(self.selected_fleet.location, self.HEX_SIZE)
        f_pos = self.camera.world_to_screen(pygame.math.Vector2(fx, fy))
        
        mx, my = pygame.mouse.get_pos()
        
        pygame.draw.line(screen, (0, 255, 0), f_pos, (mx, my), 2)

    def _draw_hover_hex(self, screen):
        cx, cy = hex_to_pixel(self.hover_hex, self.HEX_SIZE)
        corners_px = []
        for i in range(6):
            angle_deg = 60 * i 
            angle_rad = math.radians(angle_deg)
            px = cx + self.HEX_SIZE * math.cos(angle_rad)
            py = cy + self.HEX_SIZE * math.sin(angle_rad)
            corners_px.append(self.camera.world_to_screen(pygame.math.Vector2(px, py)))
        
        pygame.draw.lines(screen, (100, 255, 100), True, corners_px, 2)


    def _draw_grid(self, screen):
        # 1. Culling
        tl_world = self.camera.screen_to_world((0, 0))
        tr_world = self.camera.screen_to_world((self.screen_width, 0))
        bl_world = self.camera.screen_to_world((0, self.screen_height))
        br_world = self.camera.screen_to_world((self.screen_width, self.screen_height))
        
        corners = [tl_world, tr_world, bl_world, br_world]
        q_vals = []
        r_vals = []
        for p in corners:
            h = pixel_to_hex(p.x, p.y, self.HEX_SIZE)
            q_vals.append(h.q)
            r_vals.append(h.r)
            
        min_q = min(q_vals) - 1
        max_q = max(q_vals) + 1
        min_r = min(r_vals) - 1
        max_r = max(r_vals) + 1
        
        hex_count = (max_q - min_q) * (max_r - min_r)
        if hex_count > 80000:
             return 

        grid_color = (30, 30, 40)
        
        # 2. Optimization: Jagged Lines (Snakes)
        # Instead of drawing hexes, we draw continuous lines.
        # Set 1: Vertical Snakes (Left boundaries of columns)
        # Set 2: Horizontal Segments (Top boundaries of hexes)
        
        screen_hex_size = self.HEX_SIZE * self.camera.zoom
        SQRT3 = 1.73205080757
        
        # Pre-calculate Dimensions
        # Flat Top Hex:
        # Width = 2 * s
        # Height = sqrt(3) * s
        # Col X Stride = 1.5 * s
        # Row Y Stride = sqrt(3) * s
        
        s = screen_hex_size
        col_stride_x = 1.5 * s
        row_stride_y = SQRT3 * s
        half_row_height = row_stride_y / 2
        
        # Offsets from Column Center (cx, cy)
        # Vertices: 
        # TL: (-0.5s, -h)  -> In pygame Y is down, so (-0.5s, -h)
        # L:  (-s, 0)
        # BL: (-0.5s, h)
        # TR: (0.5s, -h) ...
        
        # Global Base (screen space of 0,0)
        cam_x = self.camera.position.x
        cam_y = self.camera.position.y
        base_x = (self.screen_width / 2) - cam_x * self.camera.zoom
        base_y = (self.screen_height / 2) - cam_y * self.camera.zoom
        
        # Pre-calc offsets
        # Left Snake Vertex Offsets (relative to row center)
        # We draw the "Left Boundary" of the column: TL -> L -> BL
        # BL of row r is TL of row r+1. So we just connect them.
        v_tl = pygame.math.Vector2(-0.5 * s, -half_row_height)
        v_l  = pygame.math.Vector2(-1.0 * s, 0)
        v_bl = pygame.math.Vector2(-0.5 * s, half_row_height)
        
        # Top Segment Offsets
        # TL -> TR
        v_tr = pygame.math.Vector2(0.5 * s, -half_row_height)
        
        # Optimization: Generate Point Lists for Columns
        # We iterate columns. For each column, we generate the full vertical snake.
        
        # We need to cover min_q-1 to max_q+1 to ensure screen coverage
        
        for q in range(min_q, max_q + 2):
             cx = base_x + q * col_stride_x
             
             # Optimization: X-Culling
             if not (-50 < cx < self.screen_width + 50):
                 continue
                 
             # Shift Y based on Column?
             # y = size * sqrt(3) * (r + q/2)
             # The rows 'r' are shifted by q/2 * height?
             # Yes. y_center = base_y + row_stride * r + row_stride * 0.5 * q
             col_y_offset = base_y + (row_stride_y * 0.5 * q)
             
             # Calculate R range for this column
             # We need cy roughly 0 to screen_height
             # cy = col_y_offset + row_stride * r
             # r = (cy - col_y_offset) / row_stride
             start_r = int((-50 - col_y_offset) / row_stride_y) - 1
             end_r = int((self.screen_height + 50 - col_y_offset) / row_stride_y) + 1
             
             snake_points = []
             
             # We need to construct a continuous line.
             # Sequence: TL(r0) -> L(r0) -> BL(r0) == TL(r1) -> ...
             # We start at TL of start_r
             
             # Initial Point
             cy_start = col_y_offset + row_stride_y * start_r
             snake_points.append((cx + v_tl.x, cy_start + v_tl.y))
             
             for r in range(start_r, end_r):
                 cy = col_y_offset + row_stride_y * r
                 
                 # Append L
                 snake_points.append((cx + v_l.x, cy + v_l.y))
                 
                 # Append BL (which is start of next)
                 snake_points.append((cx + v_bl.x, cy + v_bl.y))
                 
                 # Draw Horizontal Top Segment?
                 # TL to TR
                 # We can't batch perfectly into the snake. Draw separate.
                 # Optimization: Draw horizontal lines ?
                 p1 = (cx + v_tl.x, cy + v_tl.y)
                 p2 = (cx + v_tr.x, cy + v_tr.y)
                 pygame.draw.line(screen, grid_color, p1, p2, 1)

             if len(snake_points) > 1:
                 pygame.draw.lines(screen, grid_color, False, snake_points, 1)

    def _draw_warp_lanes(self, screen): 
        drawn_pairs = set()
        for sys in self.galaxy.systems.values():
            # Get System Center (for reference, though not drawing from it anymore)
            sx, sy = hex_to_pixel(sys.global_location, self.HEX_SIZE)
            
            for wp in sys.warp_points:
                target_id = wp.destination_id
                target_sys = next((s for s in self.galaxy.systems.values() if s.name == target_id), None)
                
                if target_sys:
                    # Prevent drawing twice? 
                    # If we iterate all warp points, we will draw A->B and B->A.
                    # We can just draw them all, overdrawing is fine for lines, or track pairs.
                    # But wait, we want to draw line from WP(A) to WP(B).
                    # Need to find the corresponding warp point in target system that points back to A?
                    # Or just draw line from WP(A) to Target System Center? User asked for point-to-point?
                    # "warp lines should connect from one warp point to another"
                    
                    # Find reciprocal warp point in target system
                    reciprocal_wp = next((w for w in target_sys.warp_points if w.destination_id == sys.name), None)
                    
                    if reciprocal_wp:
                        # Draw Line from WP_A to WP_B
                        
                        # WP_A World Pos
                        wx_a, wy_a = hex_to_pixel(wp.location, self.HEX_SIZE)
                        world_a = pygame.math.Vector2(sx + wx_a, sy + wy_a)
                        
                        # WP_B World Pos
                        ts_x, ts_y = hex_to_pixel(target_sys.global_location, self.HEX_SIZE)
                        wx_b, wy_b = hex_to_pixel(reciprocal_wp.location, self.HEX_SIZE)
                        world_b = pygame.math.Vector2(ts_x + wx_b, ts_y + wy_b)
                        
                        # Screen coords
                        scr_a = self.camera.world_to_screen(world_a)
                        scr_b = self.camera.world_to_screen(world_b)
                        
                        # Unique check using sorted names of keys or roughly position
                        pair_key = tuple(sorted((f"{sys.name}_{wp.location}", f"{target_sys.name}_{reciprocal_wp.location}")))
                        if pair_key in drawn_pairs:
                             continue
                        drawn_pairs.add(pair_key)

                        pygame.draw.line(screen, (50, 50, 100), scr_a, scr_b, 1)
                    else:
                        # Fallback: Draw to system center if reciprocal not found (should be impossible in our gen)
                        ts_x, ts_y = hex_to_pixel(target_sys.global_location, self.HEX_SIZE)
                        world_b = pygame.math.Vector2(ts_x, ts_y)
                        
                        wx_a, wy_a = hex_to_pixel(wp.location, self.HEX_SIZE)
                        world_a = pygame.math.Vector2(sx + wx_a, sy + wy_a)
                        
                        scr_a = self.camera.world_to_screen(world_a)
                        scr_b = self.camera.world_to_screen(world_b)
                        pygame.draw.line(screen, (50, 50, 100), scr_a, scr_b, 1)

    def _draw_systems(self, screen):
        # Calculate View Bounds in World Space for robust Culling
        tl = self.camera.screen_to_world((0, 0))
        br = self.camera.screen_to_world((self.screen_width, self.screen_height))
        
        # Expand bounds by System Radius (~400-500 world units) to ensure planets are seen even if star is offscreen
        margin = 600 
        min_x, max_x = min(tl.x, br.x) - margin, max(tl.x, br.x) + margin
        min_y, max_y = min(tl.y, br.y) - margin, max(tl.y, br.y) + margin

        for sys in self.galaxy.systems.values():
            hx, hy = hex_to_pixel(sys.global_location, self.HEX_SIZE) 
            world_pos = pygame.math.Vector2(hx, hy)
            
            # World Space Culling
            if not (min_x < world_pos.x < max_x and min_y < world_pos.y < max_y):
                continue
                
            screen_pos = self.camera.world_to_screen(world_pos)
            
            star_radius = sys.star_type.radius if sys.star_type else 8
            
            # Resolve Asset
            # Map color to asset key
            # Default to Yellow
            asset_key = 'yellow'
            color = sys.star_type.color
            if color[0] > 200 and color[1] < 100: asset_key = 'red'
            elif color[2] > 200 and color[0] < 100: asset_key = 'blue'
            elif color[0] > 200 and color[1] > 200 and color[2] > 200: asset_key = 'white'
            elif color[0] > 200 and color[1] > 150: asset_key = 'orange'
            
            star_img = self.assets['stars'].get(asset_key)
            
            screen_star_r = max(4, int(star_radius * self.camera.zoom * 2.0)) # Scale up a bit for visual flair
            
            # Highlight
            if self.selected_object == sys:
                pygame.draw.circle(screen, (255, 255, 255), screen_pos, screen_star_r + 4, 1) # Selection Ring
            
            if star_img:
                # Scale
                scaled_img = pygame.transform.smoothscale(star_img, (screen_star_r*2, screen_star_r*2))
                dest_rect = scaled_img.get_rect(center=(int(screen_pos.x), int(screen_pos.y)))
                screen.blit(scaled_img, dest_rect)
            else:
                # Fallback
                pygame.draw.circle(screen, color, screen_pos, screen_star_r)
            
            if self.camera.zoom >= 0.5:
                font = pygame.font.SysFont("arial", 12)
                text = font.render(sys.name, True, (200, 200, 200))
                screen.blit(text, (screen_pos.x + 10, screen_pos.y))
            
            # Detail Mode
            if self.camera.zoom >= 0.5:
                self._draw_system_details(screen, sys, world_pos)

    def _draw_system_details(self, screen, sys, sys_world_pos):
        # Draw Planets & Warp Points
        for i, planet in enumerate(sys.planets):
            px, py = hex_to_pixel(planet.location, self.HEX_SIZE)
            p_world = pygame.math.Vector2(sys_world_pos.x + px, sys_world_pos.y + py)
            p_screen = self.camera.world_to_screen(p_world)
            
            # Highlight
            if self.selected_object == planet:
                 pygame.draw.circle(screen, (255, 255, 255), p_screen, max(10, int(10 * self.camera.zoom)), 1)

            # Pick Asset
            # Deterministic choice based on planet pointer or ID
            # hash(planet) stable? usually. Or use index.
            
            p_type_name = planet.planet_type.name.lower()
            cat = 'terran' # default
            if 'gas' in p_type_name: cat = 'gas'
            elif 'ice' in p_type_name: cat = 'ice'
            elif 'desert' in p_type_name or 'hot' in p_type_name: cat = 'venus'
            
            images = self.assets['planets'].get(cat, [])
            if images:
                # Deterministic index
                idx = hash(planet) % len(images)
                img = images[idx]
                
                size = int(10 * self.camera.zoom) # Base size
                if 'Giant' in planet.planet_type.name: size = int(size * 1.5)
                
                scaled = pygame.transform.smoothscale(img, (size, size))
                dest = scaled.get_rect(center=(int(p_screen.x), int(p_screen.y)))
                screen.blit(scaled, dest)
            else:
                pygame.draw.circle(screen, planet.planet_type.color, p_screen, max(2, int(3 * self.camera.zoom)))
            
        for i, wp in enumerate(sys.warp_points):
            wx, wy = hex_to_pixel(wp.location, self.HEX_SIZE)
            w_world = pygame.math.Vector2(sys_world_pos.x + wx, sys_world_pos.y + wy)
            w_screen = self.camera.world_to_screen(w_world)
             # Highlight
            if self.selected_object == wp:
                 pygame.draw.circle(screen, (255, 255, 255), w_screen, max(12, int(12 * self.camera.zoom)), 1)
            
            # Warp Asset
            if self.assets['warp_points']:
                 idx = hash(wp) % len(self.assets['warp_points'])
                 img = self.assets['warp_points'][idx]
                 
                 size = int(12 * self.camera.zoom)
                 scaled = pygame.transform.smoothscale(img, (size, size))
                 dest = scaled.get_rect(center=(int(w_screen.x), int(w_screen.y)))
                 
                 # Additive Blending for "Glow" effect
                 screen.blit(scaled, dest, special_flags=pygame.BLEND_ADD)
            else:
                 pygame.draw.circle(screen, (200, 0, 255), w_screen, max(2, int(5 * self.camera.zoom)))

    def _draw_fleets(self, screen):
        for f in self.fleets:
            fx, fy = hex_to_pixel(f.location, self.HEX_SIZE)
            f_screen = self.camera.world_to_screen(pygame.math.Vector2(fx, fy))
            
            # Draw Triangle
            size = 10 * self.camera.zoom
            if size < 8: size = 8
            if size > 30: size = 30
            
            # Simple triangle shape
            points = [
                (f_screen.x, f_screen.y - size),
                (f_screen.x - size/2, f_screen.y + size/2),
                (f_screen.x + size/2, f_screen.y + size/2)
            ]
            
            color = (0, 255, 0)
            if self.selected_fleet == f:
                color = (255, 255, 0) # Selected highlight
                
            pygame.draw.polygon(screen, color, points)
            
            # Draw Path
            if f.path:
                path_points = [f_screen]
                for node_loc in f.path:
                    nx, ny = hex_to_pixel(node_loc, self.HEX_SIZE)
                    path_points.append(self.camera.world_to_screen(pygame.math.Vector2(nx, ny)))
                
                if len(path_points) > 1:
                    pygame.draw.lines(screen, (0, 200, 0), False, path_points, 1)                    
