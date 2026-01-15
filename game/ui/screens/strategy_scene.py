import math
import pygame
import pygame_gui
import random
import os
from game.strategy.engine.turn_engine import TurnEngine
from game.strategy.data.fleet import Fleet, FleetOrder, OrderType
from game.strategy.data.empire import Empire
from game.strategy.data.galaxy import Galaxy, StarSystem, WarpPoint, Planet
from game.strategy.data.hex_math import hex_to_pixel, pixel_to_hex, HexCoord, hex_distance
from game.ui.renderer.camera import Camera
from game.ui.screens.strategy_screen import StrategyInterface
from game.strategy.engine.commands import IssueColonizeCommand
from ui.colors import COLORS

class StrategyScene:
    """Manages strategy layer simulation, rendering, and UI."""
    
    SIDEBAR_WIDTH = 600
    TOP_BAR_HEIGHT = 50
    
    def __init__(self, screen_width, screen_height, session=None):
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # Session Management
        if session:
            self.session = session
        else:
            from game.strategy.engine.game_session import GameSession
            self.session = GameSession()
            
        # UI proxies to session state (for backward compatibility)
        # Note: self.player_empire, self.enemy_empire, etc. are now properties below.
        
        # Camera
        # Viewport crops: Sidebar (right) and Top Bar (top)
        # Offset Y = 50 (Top Bar)
        # Width = Screen - Sidebar
        # Height = Screen - Top Bar
        self.camera = Camera(screen_width - self.SIDEBAR_WIDTH, screen_height - self.TOP_BAR_HEIGHT, offset_x=0, offset_y=self.TOP_BAR_HEIGHT)
        self.camera.max_zoom = 25.0
        self.camera.zoom = 2.0 # Start Zoomed In
        
        # Focus on Player Home
        if self.player_empire.colonies:
            home_colony = self.player_empire.colonies[0]
            # Need Global Location of colony
            # Iterating systems to match planet is slow but safe for init
            home_sys = next((s for s in self.systems if home_colony in s.planets), None)
            
            if home_sys:
                target_hex = home_sys.global_location + home_colony.location
                fx, fy = hex_to_pixel(target_hex, 10) # 10 is default HEX_SIZE
                self.camera.position = pygame.math.Vector2(fx, fy)
        
        # UI
        self.ui = StrategyInterface(self, screen_width, screen_height)
        

        self.hover_hex = None
        
        # Constants
        self.HEX_SIZE = 10
        self.DETAIL_ZOOM_LEVEL = 3.0
        
        # Fleets: Managed by Empires now, but scene needs 'flat' list for rendering?
        # Or we iterate empires.
        # self.fleets = [] -> REMOVED/DEPRECATED, use self.empires access
        
        # Selected Fleet Ref
        self.selected_fleet = None
        self.selected_object = None # General selection (System, Planet, Fleet)
        self.last_selected_system = None  # Track last selected system for Shift+S quick zoom
        
        # State
        self.turn_processing = False
        self.action_open_design = False  # Flag to signal app.py to open Ship Builder
        
        # Multi-player turn management
        self.current_player_index = 0
        
        # Assets
        self.empire_assets = {} # {empire_id: {'colony': Surface, 'fleet': Surface}}
        self._load_assets()
        
    @property
    def galaxy(self): return self.session.galaxy
    
    @property
    def empires(self): return self.session.empires
    
    @property
    def systems(self): return self.session.systems
    
    @property
    def turn_engine(self): return self.session.turn_engine
    
    @property
    def player_empire(self): return self.session.player_empire
    
    @property
    def enemy_empire(self): return self.session.enemy_empire
    
    @property
    def human_player_ids(self): return self.session.human_player_ids

    def _load_assets(self):
        """Load visual assets using AssetManager."""
        from game.assets.asset_manager import get_asset_manager
        
        am = get_asset_manager()
        am.load_manifest()  # Ensure manifest is loaded
        
        # Load Empire Assets
        for emp in self.empires:
            self.empire_assets[emp.id] = {}
            if emp.theme_path and os.path.exists(emp.theme_path):
                # Colony Flag
                colony_path = os.path.join(emp.theme_path, "Flags", "Colony_Flag.jpg")
                if os.path.exists(colony_path):
                    self.empire_assets[emp.id]['colony'] = am.load_external_image(colony_path)
                
                # Fleet Icon (Battlecruiser)
                fleet_path = os.path.join(emp.theme_path, "Skins", "Battlecruiser.png")
                if os.path.exists(fleet_path):
                    self.empire_assets[emp.id]['fleet'] = am.load_external_image(fleet_path)
            else:
               # Silent warning or log?
               pass

    def handle_resize(self, width, height):
        self.screen_width = width
        self.screen_height = height
        # Adjust camera to exclude sidebar? 
        # For now, let's keep camera full width but input will be blocked by UI.
        # Ideally: self.camera.viewport_width = width - 600
        # Adjust camera to exclude sidebar
        # Adjust camera to exclude sidebar
        self.camera.width = width - self.SIDEBAR_WIDTH 
        self.camera.height = height - self.TOP_BAR_HEIGHT # Top bar offset
        # Maintain offsets
        self.camera.offset_y = self.TOP_BAR_HEIGHT
        self.ui.handle_resize(width, height)

    def request_colonize_order(self, fleet):
        """Handle colonize request from UI (Legacy entry point, redirect to on_colonize_click logic or command)."""
        # This seems to be called by StrategyInterface if we keep that logic, 
        # but we are removing logic from Interface. 
        # However, for safety/compatibility:
        self.selected_fleet = fleet
        self.on_colonize_click()
            
    def _issue_colonize_order(self, fleet, planet):
        """Issue the command to the session."""
        # Use proper planet.id instead of Python id()
        cmd = IssueColonizeCommand(fleet.id, planet.id)
        print(f"Issued IssueColonizeCommand for {planet.name}")
        
        result = self.session.handle_command(cmd)
        if not result.is_valid:
            print(f"Command Failed: {result.message}")
        else:
             self.on_ui_selection(self.selected_fleet) # Refresh UI

    def _get_system_at_hex(self, hex_coord):
        return self.galaxy.systems.get(hex_coord)

    def update(self, dt):
        self.camera.update(dt)
        self.ui.update(dt)
        
        # Update Fleets (Visual movement can be added here)
        # For turn-based, visualization happens during 'process_turn' or interpolated?
        # For now, immediate jump.
        pass

    def handle_event(self, event):
        self.ui.handle_event(event)

        # Handle UI Selection Events from the Interface
        # Handle UI Selection Events from the Interface
        # Note: StrategyInterface now uses SystemTreePanel which triggers callbacks directly via
        # self.ui.sector_tree.set_selection_callback -> self.on_ui_selection
        # So no manual event handling is needed here for lists.
        pass
                    
        # Button Events
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == self.ui.btn_next_turn:
                self.advance_turn()
            elif event.ui_element == self.ui.btn_colonize:
                self.on_colonize_click()
            elif event.ui_element == self.ui.btn_build_ship:
                self.on_build_ship_click()
            # Navigation
            elif event.ui_element == self.ui.btn_prev_colony:
                self.cycle_selection('colony', -1)
            elif event.ui_element == self.ui.btn_next_colony:
                self.cycle_selection('colony', 1)
            elif event.ui_element == self.ui.btn_prev_fleet:
                self.cycle_selection('fleet', -1)
            elif event.ui_element == self.ui.btn_next_fleet:
                self.cycle_selection('fleet', 1)

        # Fleet Movement Input
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_m:
                if self.selected_fleet:
                    self.input_mode = 'MOVE'
                    print("Input Mode: MOVE - Click designation for fleet.")
                else:
                    print("Select a fleet first.")
            elif event.key == pygame.K_j:
                if self.selected_fleet:
                    self.input_mode = 'JOIN'
                    print("Input Mode: JOIN - Select fleet to join.")
                else:
                    print("Select a fleet first.")
            elif event.key == pygame.K_ESCAPE:
                if getattr(self, 'input_mode', 'SELECT') in ('MOVE', 'COLONIZE_TARGET', 'JOIN'):
                    self.input_mode = 'SELECT'
                    print("Input Mode: SELECT")
            elif event.key == pygame.K_c:
                if self.selected_fleet:
                    self.input_mode = 'COLONIZE_TARGET'
                    print("Input Mode: COLONIZE - Select target planet.")
                else:
                    print("Select a fleet first.")
            # Quick Zoom Shortcuts
            elif event.key == pygame.K_g and (event.mod & pygame.KMOD_SHIFT):
                self._zoom_to_galaxy()
            elif event.key == pygame.K_s and (event.mod & pygame.KMOD_SHIFT):
                self._zoom_to_system()

    def advance_turn(self):
        """End current player's order phase. Process turn when all humans ready."""
        # Increment to next human player
        self.current_player_index += 1
        
        # Check if all human players have submitted orders
        if self.current_player_index >= len(self.human_player_ids):
            # All humans ready - process the full turn
            self.current_player_index = 0
            self._process_full_turn()
            # Update label for next round
            self._update_player_label()
        else:
            # Switch to next human player's view
            next_player_id = self.human_player_ids[self.current_player_index]
            print(f"Player {next_player_id + 1}'s turn to give orders.")
            # Update UI label
            self._update_player_label()
            # Center on their home colony if they have one
            next_empire = next((e for e in self.empires if e.id == next_player_id), None)
            if next_empire and next_empire.colonies:
                self.center_camera_on(next_empire.colonies[0])
    
    def _update_player_label(self):
        """Update the player indicator label."""
        player_num = self.current_player_index + 1
        self.ui.lbl_current_player.set_text(f"Player {player_num}'s Turn")
    
    @property
    def current_empire(self):
        """Get the empire for the current player (supports N players)."""
        current_player_id = self.human_player_ids[self.current_player_index]
        return next((e for e in self.empires if e.id == current_player_id), self.empires[0])
    
    def _process_full_turn(self):
        """Process the turn for all empires simultaneously."""
        self.turn_processing = True
        print("Processing Turn...")
        
        # Force Render "Processing" state
        screen = pygame.display.get_surface()
        if screen:
             self.draw(screen)
             self._draw_processing_overlay(screen)
             pygame.display.flip()
        
        # Process turn for all empires simultaneously
        self.session.process_turn()
        
        # Re-center Camera on current player's home
        current_player_id = self.human_player_ids[self.current_player_index]
        current_empire = next((e for e in self.empires if e.id == current_player_id), self.player_empire)
        if current_empire.colonies:
            self.center_camera_on(current_empire.colonies[0])
                 
        self.turn_processing = False
        
        # Refresh UI for currently selected object
        if self.selected_object:
            self.on_ui_selection(self.selected_object)
            
    def _draw_processing_overlay(self, screen):
        """Draw a modal overlay for turn processing."""
        overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150)) # Semi-transparent black
        screen.blit(overlay, (0,0))
        
        font = pygame.font.SysFont("arial", 48, bold=True)
        text = font.render("PROCESSING TURN...", True, (255, 200, 0))
        rect = text.get_rect(center=(screen.get_width()//2, screen.get_height()//2))
        screen.blit(text, rect)
        
    def on_colonize_click(self):
        """Handle colonize action."""
        if not self.selected_fleet:
            return
            
        # 1. Identify valid candidates using Engine Validation
        # We need to scan planets at location.
        # Ideally TurnEngine provides a "get_colonizable_planets(fleet)" but "validate" is what we have.
        # We'll use the scene's knowledge of location to find potential planets, 
        # then ask Engine "Is this specific planet valid?".
        
        start_sys = self._get_system_at_hex(self.selected_fleet.location)
        potential_planets = []
        
        # Gather all planets at hex (System or Peripheral)
        if start_sys:
            loc_local = self.selected_fleet.location - start_sys.global_location
            for p in start_sys.planets:
                if p.location == loc_local:
                    potential_planets.append(p)
        else:
             # Full scan (rare)
             for sys in self.systems:
                 loc_local = self.selected_fleet.location - sys.global_location
                 for p in sys.planets:
                     if p.location == loc_local:
                         potential_planets.append(p)

        # Filter by Validation
        valid_planets = []
        for p in potential_planets:
            # Validate with Engine
            res = self.turn_engine.validate_colonize_order(self.galaxy, self.selected_fleet, p)
            if res.is_valid:
                valid_planets.append(p)

        if not valid_planets:
            print("No colonizable planets at fleet location (Validation Failed).")
            return
            
        # Execute
        if len(valid_planets) == 1:
            self._issue_colonize_order(self.selected_fleet, valid_planets[0])
        else:
            print("Multiple planets detected. Requesting user selection...")
            self.ui.prompt_planet_selection(valid_planets, lambda p: self._issue_colonize_order(self.selected_fleet, p))
             
    def cycle_selection(self, obj_type, direction):
        """Cycle selection through colonies or fleets and Center Camera."""
        targets = []
        if obj_type == 'colony':
            targets = self.current_empire.colonies
        elif obj_type == 'fleet':
            targets = self.current_empire.fleets
            
        if not targets:
            print(f"No {obj_type}s to cycle.")
            return

        # Find current index
        current_idx = -1
        if self.selected_object in targets:
            current_idx = targets.index(self.selected_object)
        
        # Calc next
        next_idx = (current_idx + direction) % len(targets)
        new_obj = targets[next_idx]
        
        # Select & Center
        self.on_ui_selection(new_obj)
        self.center_camera_on(new_obj)

    def center_camera_on(self, obj):
        """Center camera on a Game Object (Planet, Fleet, System)."""
        target_hex = None
        
        if hasattr(obj, 'location'):
             # Planet location is local! Fleet is Global.
             if hasattr(obj, 'planet_type'): # Planet
                 # Find global by finding parent system
                 # Optimize: We need system ref.
                 sys = next((s for s in self.systems if obj in s.planets), None)
                 if sys:
                     target_hex = sys.global_location + obj.location
             elif hasattr(obj, 'ships'): # Fleet
                 target_hex = obj.location
             elif hasattr(obj, 'global_location'): # System
                 target_hex = obj.global_location
        
        if target_hex:
            fx, fy = hex_to_pixel(target_hex, self.HEX_SIZE)
            self.camera.position.x = fx
            self.camera.position.y = fy
            print(f"Camera centered on {obj} at {target_hex}")
        else:
            print(f"Could not center camera on {obj}")
    
    def _zoom_to_galaxy(self):
        """Zoom out to show entire galaxy (Shift+G)."""
        if not self.systems:
            return
            
        # Calculate bounds of all systems
        all_positions = []
        for sys in self.systems:
            px, py = hex_to_pixel(sys.global_location, self.HEX_SIZE)
            all_positions.append((px, py))
        
        if not all_positions:
            return
            
        min_x = min(p[0] for p in all_positions)
        max_x = max(p[0] for p in all_positions)
        min_y = min(p[1] for p in all_positions)
        max_y = max(p[1] for p in all_positions)
        
        # Center
        center_x = (min_x + max_x) / 2
        center_y = (min_y + max_y) / 2
        self.camera.position.x = center_x
        self.camera.position.y = center_y
        
        # Calculate zoom to fit all systems with margin
        width = max_x - min_x + 600  # Larger margin for more zoom out
        height = max_y - min_y + 600
        
        zoom_x = self.camera.width / width if width > 0 else 1.0
        zoom_y = self.camera.height / height if height > 0 else 1.0
        fit_zoom = min(zoom_x, zoom_y)
        
        # Set target zoom (smooth animation)
        self.camera.target_zoom = max(self.camera.min_zoom, min(self.camera.max_zoom, fit_zoom))
        self.camera.zoom = self.camera.target_zoom  # Instant for this shortcut
        
        print(f"Galaxy View: zoom={self.camera.zoom:.2f}")
    
    def _zoom_to_system(self):
        """Zoom to 3x on the last selected system (Shift+S)."""
        target_sys = self.last_selected_system
        
        # Fallback: if no system selected, try to infer from selected object
        if not target_sys and self.selected_object:
            if isinstance(self.selected_object, StarSystem):
                target_sys = self.selected_object
            elif hasattr(self.selected_object, 'location'):
                target_sys = next((s for s in self.systems if self.selected_object in s.planets or self.selected_object in s.warp_points), None)
        
        if not target_sys:
            print("No system selected for Shift+S zoom")
            return
        
        # Center on system
        px, py = hex_to_pixel(target_sys.global_location, self.HEX_SIZE)
        self.camera.position.x = px
        self.camera.position.y = py
        
        # Set zoom to 2x (smooth animation)
        self.camera.target_zoom = 2.0
        self.camera.zoom = 2.0  # Instant for this shortcut
        
        print(f"System View: {target_sys.name} at zoom=2.0")
             
    def on_build_ship_click(self):
        """Handle 'Build Ship' action."""
        if isinstance(self.selected_object, Planet):
            planet = self.selected_object
            if planet.owner_id == self.current_empire.id:
                print(f"Queueing Ship at {planet}...")
                # Add to Queue via Command using planet.id (proper ID, not Python id())
                from game.strategy.engine.commands import IssueBuildShipCommand
                
                cmd = IssueBuildShipCommand(planet.id, "Colony Ship")
                
                res = self.session.handle_command(cmd)
                if res.is_valid:
                    print("Ship added to construction queue (via Command).")
                else:
                    print(f"Build Failed: {res.message}")

    def on_design_click(self):
        """Handle 'Design' button click - opens Ship Builder."""
        print("Design button clicked - opening Ship Builder")
        self.action_open_design = True

    def update_input(self, dt, events):
        """Update camera input."""
        # Filter events for Camera: Block MouseWheel if over sidebar
        cam_events = []
        mx, my = pygame.mouse.get_pos()
        over_sidebar = (mx > self.screen_width - self.SIDEBAR_WIDTH)
        over_topbar = (my < self.TOP_BAR_HEIGHT)
        
        for e in events:
            if e.type == pygame.MOUSEWHEEL:
                if over_sidebar or over_topbar:
                    continue
            cam_events.append(e)
            
        self.camera.update_input(dt, cam_events)
        
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
                
        elif current_mode == 'JOIN':
            if button == 1: # Left Click to Join
                self._handle_join_designation(mx, my)
                return True
            elif button == 3: # Right click cancels
                self.input_mode = 'SELECT'
                print("Input Mode: SELECT")
                return True
        
        elif current_mode == 'COLONIZE_TARGET':
            if button == 1: # Left Click to select planet
                self._handle_colonize_designation(mx, my)
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
        
        clicked_system = self._get_system_at_hex(hex_clicked)
        sector_contents = []
        
        # Check Fleets (All Empires)
        for emp in self.empires:
            for f in emp.fleets:
                if f.location == hex_clicked:
                     sector_contents.append(f)
                 
        if clicked_system:
             # System object itself is NOT in the sector list (Middle Panel) 
             # It only appears in the System Info (Top Panel)
             pass 
                 
             for p in clicked_system.planets:
                 p_global = clicked_system.global_location + p.location
                 if p_global == hex_clicked:
                     sector_contents.append(p)
                         
             for wp in clicked_system.warp_points:
                 wp_global = clicked_system.global_location + wp.location
                 if wp_global == hex_clicked:
                     sector_contents.append(wp)
                     
             for star in clicked_system.stars:
                 s_global = clicked_system.global_location + star.location
                 if s_global == hex_clicked:
                     sector_contents.append(star)
                     
             # Always include Environmental Data (Radiation)
             from game.strategy.data.physics import SectorEnvironment
             local_hex = hex_clicked - clicked_system.global_location
             env = SectorEnvironment(local_hex, clicked_system)
             sector_contents.append(env)


        if clicked_system:
            sys_contents = [clicked_system] 
            sys_contents.extend(clicked_system.stars) # Include all stars
            sys_contents.extend(clicked_system.planets)
            sys_contents.extend(clicked_system.warp_points)
            self.ui.show_system_info(clicked_system, sys_contents)
            # Track this system for Shift+S zoom
            self.last_selected_system = clicked_system
        else:
            self.ui.show_system_info(None, [])
            
        self.ui.show_sector_info(hex_clicked, sector_contents)
        
        best_pick = None
        if sector_contents:
            best_pick = sector_contents[0] 
            
        if best_pick:
            self.on_ui_selection(best_pick)
            self.selected_object = best_pick
        elif clicked_system:
             self.on_ui_selection(clicked_system)
             self.selected_object = clicked_system
        else:
             self.selected_object = None
             self.ui.show_detailed_report(None, None)
             
    def on_ui_selection(self, obj):
        """Called when user selects an item in the UI list."""
        self.selected_object = obj
        
        # Track last selected system (direct or inferred from planet/warp point)
        if isinstance(obj, StarSystem):
            self.last_selected_system = obj
        elif hasattr(obj, 'location'):  # Planet, WarpPoint, etc.
            # Find parent system
            parent_sys = next((s for s in self.systems if obj in s.planets or obj in s.warp_points), None)
            if parent_sys:
                self.last_selected_system = parent_sys
        
        # --- Update Button Visibility ---
        # Get current player's empire ID
        current_player_id = self.human_player_ids[self.current_player_index]
        
        # 1. Colonize (Fleet Selected + At Planet?)
        # Logic moved to StrategyInterface.show_detailed_report
        if isinstance(obj, Fleet) and obj.owner_id == current_player_id:
            self.selected_fleet = obj
        else:
            if not isinstance(obj, Fleet): self.selected_fleet = None # Clear if not fleet
            
        # 2. Build Ship (Current Player's Planet Selected)
        # Logic moved to StrategyInterface.show_detailed_report
            
        
        # Get Portrait
        img = self._get_object_asset(obj)
        self.ui.show_detailed_report(obj, img)
        
    def _get_object_asset(self, obj):
        """Resolve the visual asset for a data object."""
        from game.assets.asset_manager import get_asset_manager
        am = get_asset_manager()

        if hasattr(obj, 'color') and hasattr(obj, 'mass'): # Star
            color = obj.color
            asset_key = 'yellow'
            if color[0] > 200 and color[1] < 100: asset_key = 'red'
            elif color[2] > 200 and color[0] < 100: asset_key = 'blue'
            elif color[0] > 200 and color[1] > 200 and color[2] > 200: asset_key = 'white'
            elif color[0] > 200 and color[1] > 150: asset_key = 'orange'
            return am.get_image('stars', asset_key)
            
        elif hasattr(obj, 'planet_type'):
            p_type_name = obj.planet_type.name.lower()
            cat = 'terran'
            if 'gas' in p_type_name: cat = 'gas'
            elif 'ice' in p_type_name: cat = 'ice'
            elif 'desert' in p_type_name or 'hot' in p_type_name: cat = 'venus'
            
            return am.get_random_from_group('planets', cat, seed_id=id(obj))
                
        elif hasattr(obj, 'destination_id'): # Warp Point
             return am.get_random_from_group('warp_points', 'default', seed_id=id(obj))
             
        elif hasattr(obj, 'ships'): # Fleet
            emp_assets = self.empire_assets.get(obj.owner_id)
            if emp_assets and 'fleet' in emp_assets:
                return emp_assets['fleet']
                 
        return None
        
    def _handle_move_designation(self, mx, my):
        """Handle designating a move target."""
        if not self.selected_fleet:
            return
            
        world_pos = self.camera.screen_to_world((mx, my))
        target_hex = pixel_to_hex(world_pos.x, world_pos.y, self.HEX_SIZE)
        
        # Check for Fleet at target
        target_fleet = self._get_fleet_at_hex(target_hex)
        
        # Define Standard Move Logic as a closure/helper
        def execute_standard_move():
            print(f"Calculating path to {target_hex}...")
            
            # Use Session to Preview Path (Visual Feedback / Validation)
            preview_path = self.session.preview_fleet_path(self.selected_fleet, target_hex)
            
            if preview_path:
                print(f"Path confirmed: {len(preview_path)} steps.")
                
                # Issue Command via Session
                from game.strategy.engine.commands import IssueMoveCommand
                cmd = IssueMoveCommand(self.selected_fleet.id, target_hex)
                
                result = self.session.handle_command(cmd)
                
                if result and result.is_valid:
                     # Reset Input unless Shift
                    keys = pygame.key.get_pressed()
                    if not (keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]):
                        self.input_mode = 'SELECT'
                        
                    self.on_ui_selection(self.selected_fleet)
                else:
                    print(f"Move Failed: {result.message if result else 'Unknown'}")
            else:
                print("Cannot find path to target (Unreachable).")

        # Define Intercept Logic
        def execute_intercept():
            print(f"Intercepting Fleet {target_fleet.id}...")
            from game.strategy.data.fleet import FleetOrder, OrderType
            # TODO: We need a Command for Intercept too!
            # For Phase 1/2, let's keep it direct or create IssueInterceptCommand?
            # Creating IssueMoveCommand with target as Fleet?
            # IssueMoveCommand expects target_hex in our current def, but type 'Any'.
            # Session handle_move expects target_hex to be passed to preview_path.
            # preview_path expects hex.
            
            # To support Intercept via Command, we need IssueInterceptCommand or overload IssueMoveCommand.
            # Let's direct map for now to unblock, but mark for todo.
            # Actually, let's just use IssueMoveCommand but we need to handle the target being a fleet.
            # BUT our IssueMoveCommand definition in Session calls preview_path(fleet, cmd.target_hex).
            
            # Fallback: keep legacy logic for Intercept for this moment as it wasn't in Phase 1 scope explicitly?
            # "Refactor StrategyScene to use IssueMoveCommand"
            # I should make IssueMoveCommand support Fleets or create IssueInterceptCommand.
            # Let's keep legacy mutation for Intercept to reduce risk, since Phase 1 didn't add InterceptCommand.
            
            new_order = FleetOrder(OrderType.MOVE_TO_FLEET, target_fleet)
            self.selected_fleet.add_order(new_order)
            
            # Reset Input
            self.input_mode = 'SELECT'
            self.on_ui_selection(self.selected_fleet)

        if target_fleet and target_fleet != self.selected_fleet:
            # Prompt User (Move vs Intercept)
            self.ui.prompt_move_choice(target_fleet, target_hex, execute_standard_move, execute_intercept)
        else:
            # No fleet, just move
            execute_standard_move()
            
    def _handle_join_designation(self, mx, my):
        """Handle designating a fleet to join."""
        if not self.selected_fleet:
            return

        world_pos = self.camera.screen_to_world((mx, my))
        target_hex = pixel_to_hex(world_pos.x, world_pos.y, self.HEX_SIZE)
        
        target_fleet = self._get_fleet_at_hex(target_hex)
        
        if not target_fleet:
            print("No fleet at target location.")
            return # Keep input mode active? Or cancel?
            
        if target_fleet == self.selected_fleet:
            print("Cannot join self.")
            return
            
        # Must be friendly? (Usually yes, but maybe mechanics allow boarding later? For now assume friendly)
        if target_fleet.owner_id != self.selected_fleet.owner_id:
            print("Cannot join enemy fleet.")
            return
            
        print(f"Queueing Join Order with Fleet {target_fleet.id}...")
        
        # 1. Move Towards
        order_move = FleetOrder(OrderType.MOVE_TO_FLEET, target_fleet)
        self.selected_fleet.add_order(order_move)
        
        # 2. Join
        order_join = FleetOrder(OrderType.JOIN_FLEET, target_fleet)
        self.selected_fleet.add_order(order_join)
        
        self.input_mode = 'SELECT'
        self.on_ui_selection(self.selected_fleet)

    def _get_fleet_at_hex(self, hex_coord):
        """Find the first fleet at the given hex."""
        for emp in self.empires:
            for f in emp.fleets:
                if f.location == hex_coord:
                    return f
        return None

    def _handle_colonize_designation(self, mx, my):
        """Handle selecting a planet for colonization with movement."""
        if not self.selected_fleet:
            return
            
        world_pos = self.camera.screen_to_world((mx, my))
        target_hex = pixel_to_hex(world_pos.x, world_pos.y, self.HEX_SIZE)
        
        # 1. Identify System at Target (Simplest lookup: System Global Location OR within radius?)
        # _get_system_at_hex usually only checks if hex IS valid part of system?
        # Actually in this simple hex map, 1 System = 1 Hex mostly, OR spread?
        # _get_system_at_hex implementation delegates to pathfinding which checks if `hex` is close to system center?
        # Let's trust _get_system_at_hex returns the system "owning" that hex.
        
        target_system = self._get_system_at_hex(target_hex)
        if not target_system:
            print("No system at target location.")
            self.input_mode = 'SELECT'
            return
        
        # 2. Get Candidates at the CLICKED Location
        # User Feedback (Step 344): "dialog ... should only include planets in that sector."
        
        local_hex = target_hex - target_system.global_location
        
        # Filter for planets exactly at this hex (Planet + Moons)
        candidates = [p for p in target_system.planets if p.owner_id is None and p.location == local_hex]
        
        if not candidates:
            print(f"No colonizable planets at hex {target_hex}.")
            # Fallback? If user clicked empty space, they probably missed. 
            # Do NOT show system-wide list.
            self.input_mode = 'SELECT'
            return

        if len(candidates) == 1:
             # Only one option, proceed (Auto-Select)
             self._queue_colonize_mission(target_hex, candidates[0], fleet=self.selected_fleet)
        else:
             # Multiple options (e.g. Planet + Moons) -> Dialog
             # CAPTURE the fleet reference now, in case selection changes while dialog is open!
             fleet_ref = self.selected_fleet
             
             def on_selected(planet):
                 # Use captured fleet_ref
                 self._queue_colonize_mission(target_hex, planet, fleet=fleet_ref)
                 # Refresh UI if this fleet is still selected (opt)
                 if self.selected_fleet == fleet_ref:
                    self.on_ui_selection(self.selected_fleet)
                 
             self.ui.prompt_planet_selection(candidates, on_selected)
        
        self.input_mode = 'SELECT'
        self.on_ui_selection(self.selected_fleet)

    def _queue_colonize_mission(self, target_hex, planet, fleet=None):
        """Helper to queue Move + Colonize."""
        # Use provided fleet ref or fallback to selection
        target_fleet = fleet if fleet else self.selected_fleet
        
        if not target_fleet: return
        
        # Determine start hex
        start_hex = target_fleet.location
        if target_fleet.orders:
             last = target_fleet.orders[-1]
             if last.type == OrderType.MOVE:
                 start_hex = last.target
        
        # Calculate Path
        path = self.calculate_hybrid_path(start_hex, target_hex)
        if path:
            # Queue MOVE
            # Only if start != target
            if start_hex != target_hex:
                move = FleetOrder(OrderType.MOVE, target_hex)
                target_fleet.add_order(move)
                if len(target_fleet.orders) == 1:
                    # Remove start hex from path before assigning
                    if path and path[0] == target_fleet.location:
                        path = path[1:]
                    target_fleet.path = path
            
            # Queue COLONIZE
            col = FleetOrder(OrderType.COLONIZE, planet)
            target_fleet.add_order(col)
            
            p_name = planet.name if planet else "Any Planet"
            print(f"Mission Queued: Colonize {p_name} at {target_hex}")
        else:
            print("Cannot find path.")

    def request_colonize_order(self, fleet, planet):
        """Request colonization order from UI (e.g. detailed panel button)."""
        self.selected_fleet = fleet
        
        # Resolve global hex of planet
        # Planet -> System -> Global
        # We need to find the system the planet belongs to.
        # Efficient lookup?
        target_hex = None
        
        # Search systems (Optimization: Map in Galaxy?)
        found_sys = None
        for sys in self.galaxy.systems.values():
             if planet in sys.planets:
                 found_sys = sys
                 break
        
        if found_sys:
             target_hex = found_sys.global_location + planet.location
             self._queue_colonize_mission(target_hex, planet)
             self.on_ui_selection(fleet) # Refresh UI to show new orders
        else:
             print("StrategyScene: Could not resolve system for planet.")

    def calculate_hybrid_path(self, start_hex, end_hex):
        """
        Calculate path combining local hex movement and interstellar warp jumps.
        Delegates to shared pathfinding module.
        """
        from game.strategy.data.pathfinding import find_hybrid_path
        return find_hybrid_path(self.galaxy, start_hex, end_hex)

    def _get_system_at_hex(self, hex_c):
        """Find which system implies ownership of this hex (simplistic radius check)."""
        # Legacy Wrapper or just remove? Keeping for now to avoid breaking other calls if any.
        from game.strategy.data.pathfinding import get_system_at_hex
        return get_system_at_hex(self.galaxy, hex_c)

    def _find_nearest_system(self, hex_c):
        """Find the nearest system to a hex coordinate (ignoring radius)."""
        from game.strategy.data.pathfinding import find_nearest_system
        return find_nearest_system(self.galaxy, hex_c)

    def draw(self, screen):
        """Render the scene."""
        # Set Clip to Galaxy Viewport
        # x=0, y=50, w=screen-sidebar, h=screen-50
        viewport_w = self.screen_width - self.SIDEBAR_WIDTH
        viewport_h = self.screen_height - self.TOP_BAR_HEIGHT
        
        # Valid clip?
        if viewport_w > 0 and viewport_h > 0:
            viewport_rect = pygame.Rect(0, self.TOP_BAR_HEIGHT, viewport_w, viewport_h)
            screen.set_clip(viewport_rect)
            
            # Fill Viewport BG
            screen.fill(COLORS['bg_deep'], viewport_rect)
        else:
            screen.fill(COLORS['bg_deep'])
        
        # Draw Galaxy Elements (Clipped)
        if self.camera.zoom >= 0.4:
            self._draw_grid(screen)
            
        self._draw_warp_lanes(screen)
        self._draw_systems(screen)
        self._draw_fleets(screen) 
        
        # Move Line Preview
        if getattr(self, 'input_mode', 'SELECT') == 'MOVE' and self.selected_fleet:
             self._draw_move_preview(screen)
        
        # Hover Highlight
        if self.hover_hex and self.camera.zoom >= 0.5:
             self._draw_hover_hex(screen)

        # Remove Clip for UI
        screen.set_clip(None)
        
        # Draw Border around Galaxy Viewport
        if viewport_w > 0 and viewport_h > 0:
             pygame.draw.rect(screen, COLORS['border_normal'], viewport_rect, 2)
        
        self.ui.draw(screen)

    def _draw_move_preview(self, screen):
        # Determine start point (Fleet Location or Last Order Target)
        start_hex = self.selected_fleet.location
        for o in reversed(self.selected_fleet.orders):
             if o.type == OrderType.MOVE:
                 start_hex = o.target
                 break
                 
        fx, fy = hex_to_pixel(start_hex, self.HEX_SIZE)
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

        grid_color = COLORS['border_subtle']
        
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
        # Use camera width for viewport center AND include viewport offsets!
        # This must match camera.world_to_screen() which adds offset_x and offset_y
        base_x = (self.camera.width / 2) - cam_x * self.camera.zoom + self.camera.offset_x
        base_y = (self.camera.height / 2) - cam_y * self.camera.zoom + self.camera.offset_y
        
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

            # Draw Colony Marker (Upper Left)
            # ONLY DRAW ON STAR IF ZOOMED OUT (Planets not visible)
            if self.camera.zoom < 0.5:
                owned_planets = [p for p in sys.planets if p.owner_id is not None]
                if owned_planets:
                     first_owner_id = owned_planets[0].owner_id
                     owner_emp = next((e for e in self.empires if e.id == first_owner_id), None)
                     if owner_emp:
                         # Calculate World Space Offset (Top Left)
                         # Use HEX_SIZE to robustly position at "Hex Corner" regardless of zoom
                         # Top Left is roughly (-1, -1) * HEX_SIZE (scaled a bit)
                         # Let's say -1.5 * HEX_SIZE to be clearly separate
                         offset_world = pygame.math.Vector2(-0.75 * self.HEX_SIZE, -0.75 * self.HEX_SIZE)
                         marker_world = world_pos + offset_world
                         marker_screen = self.camera.world_to_screen(marker_world)
                         
                         pygame.draw.circle(screen, owner_emp.color, (int(marker_screen.x), int(marker_screen.y)), 5)
                         pygame.draw.circle(screen, (255, 255, 255), (int(marker_screen.x), int(marker_screen.y)), 6, 1)
            
            primary = sys.primary_star
            if primary:
                star_radius = max(2, int((primary.diameter_hexes / 2.0) * self.camera.zoom * 2.0 * 10)) # approximate scalar 
                # Actually, previously radius=8 was base.
                # Now diameter=1 to 11. Radius 0.5 to 5.5.
                # previous code: max(4, int(radius * zoom * 2.0))
                # If radius=8, result=16*zoom.
                # New: diameter=1 (Sol-ish). radius=0.5. result=1*zoom? Too small.
                # We need to scale visual presence.
                # Let's say 1 hex diameter ~= 20 pixels on screen at zoom 1.0?
                # HEX_SIZE=10. Diameter=1 means width approx 17px.
                # So radius in pixels = (diameter/2) * 1.73 * HEX_SIZE?
                # Let's simplify: radius_px = diameter * 8 * zoom
                
                # Render Primary and Companions
                # Render Primary and Companions
                for star in sys.stars:
                    # Calculate position offset from primary
                    # Primary is at 0,0 locally.
                    # star.location is HexCoord local to system center.
                    # Need to map this to pixel offset.
                    
                    local_pixel_x, local_pixel_y = hex_to_pixel(star.location, self.HEX_SIZE)
                    
                    # hx, hy is world pixel pos of system center
                    star_screen_pos = self.camera.world_to_screen(pygame.math.Vector2(hx + local_pixel_x, hy + local_pixel_y))
                    
                    # Logic for Asset Resolution
                    asset_key = 'yellow'
                    color = star.color
                    if color[0] > 200 and color[1] < 100: asset_key = 'red'
                    elif color[2] > 200 and color[0] < 100: asset_key = 'blue'
                    elif color[0] > 200 and color[1] > 200 and color[2] > 200: asset_key = 'white'
                    elif color[0] > 200 and color[1] > 150: asset_key = 'orange'
                    
                    from game.assets.asset_manager import get_asset_manager
                    am = get_asset_manager()
                    star_img = am.get_image('stars', asset_key)
                    
                    # Size calculation
                    # Base size: diameter=1 -> 15px radius?
                    # Let's try: radius = diameter * 6 * zoom
                    screen_star_r = max(3, int(star.diameter_hexes * self.HEX_SIZE * self.camera.zoom))
                    
                    # Highlight
                    if self.selected_object == sys and star == primary:
                        pygame.draw.circle(screen, (255, 255, 255), star_screen_pos, screen_star_r + 4, 1) 
                    
                    if star_img:
                        scaled_img = pygame.transform.smoothscale(star_img, (screen_star_r*2, screen_star_r*2))
                        dest_rect = scaled_img.get_rect(center=(int(star_screen_pos.x), int(star_screen_pos.y)))
                        screen.blit(scaled_img, dest_rect)
                    else:
                        pygame.draw.circle(screen, color, star_screen_pos, screen_star_r)
                        
                    # Name if zoomed
                    if self.camera.zoom >= 0.5:
                        font_size = 12 if star == primary else 10
                        font = pygame.font.SysFont("arial", font_size)
                        text = font.render(star.name if star != primary else sys.name, True, (200, 200, 200)) # Show System Name for Primary
                        screen.blit(text, (star_screen_pos.x + 10, star_screen_pos.y))
            
            # Detail Mode (Planets)
            if self.camera.zoom >= 0.5:
                self._draw_system_details(screen, sys, world_pos)

    def _draw_system_details(self, screen, sys, sys_world_pos):
        # Group by location
        hex_groups = {}
        for p in sys.planets:
            key = (p.location.q, p.location.r)
            if key not in hex_groups: hex_groups[key] = []
            hex_groups[key].append(p)
            
        for key, planets in hex_groups.items():
            # Base position
            coord = planets[0].location
            px, py = hex_to_pixel(coord, self.HEX_SIZE)
            hex_center_world = pygame.math.Vector2(sys_world_pos.x + px, sys_world_pos.y + py)
            hex_center_screen = self.camera.world_to_screen(hex_center_world)
            
            # Gradual Expansion: Interpolate from 1.5x to 2.0x zoom
            # At 1.5x: expansion_t = 0 (all centered)
            # At 2.0x: expansion_t = 1 (fully expanded)
            EXPAND_START = 1.5
            EXPAND_END = 2.0
            expansion_t = max(0.0, min(1.0, (self.camera.zoom - EXPAND_START) / (EXPAND_END - EXPAND_START)))
            
            hex_px_radius = self.HEX_SIZE * self.camera.zoom
            
            if len(planets) > 1:
                # Sort by mass (largest = primary)
                planets.sort(key=lambda x: x.mass, reverse=True)
                largest = planets[0]
                
                # Base Size: Scaled proportionate to Primary
                base_r = hex_px_radius * 0.25
                
                # Build draw list: secondaries first, primary last (painter's algorithm)
                draw_order = planets[1:] + [planets[0]]  # Primary last
                
                for i, p in enumerate(planets):
                    # Relative Scale
                    rel_scale = p.radius / largest.radius
                    if rel_scale < 0.4: rel_scale = 0.4
                    
                    draw_r = max(2, int(base_r * rel_scale))
                    
                    # Calculate FINAL (expanded) position
                    if p == largest:
                        # Primary: shifted left when fully expanded
                        final_offset = pygame.math.Vector2(-hex_px_radius * 0.6, 0)
                        # Primary maintains larger size
                        primary_draw_r = max(2, int((hex_px_radius * 0.5) * rel_scale))
                        draw_r = primary_draw_r
                    else:
                        # Secondary: arc on right side when expanded
                        idx = planets.index(p) - 1  # Index among secondaries
                        angle = idx * (180 / max(1, len(planets)-1)) - 90
                        dist = hex_px_radius * 0.5
                        final_offset = pygame.math.Vector2(dist, 0).rotate(angle)
                    
                    # Interpolate between centered (0,0) and final offset
                    current_offset = final_offset * expansion_t
                    p_screen = hex_center_screen + current_offset
                    
                    # Store for draw order (don't draw yet)
                    p._temp_screen_pos = p_screen
                    p._temp_draw_r = draw_r
                
                # Draw in order: secondaries first, primary last
                for p in draw_order:
                    self._draw_planet_sprite(screen, p, p._temp_screen_pos, p._temp_draw_r)
                    # Selection highlight
                    if self.selected_object == p:
                        pygame.draw.circle(screen, (255, 255, 255), 
                                         (int(p._temp_screen_pos.x), int(p._temp_screen_pos.y)), 
                                         int(p._temp_draw_r) + 4, 1)

            else:
                # Single planet: draw centered
                largest = planets[0]
                base_r = 5 * self.camera.zoom 
                if 'Giant' in largest.planet_type.name: base_r *= 1.5
                
                self._draw_planet_sprite(screen, largest, hex_center_screen, int(base_r))
                
                # Selection highlight
                if self.selected_object == largest:
                    pygame.draw.circle(screen, (255, 255, 255), 
                                     (int(hex_center_screen.x), int(hex_center_screen.y)), 
                                     int(base_r) + 4, 1)

        for i, wp in enumerate(sys.warp_points):
            wx, wy = hex_to_pixel(wp.location, self.HEX_SIZE)
            w_world = pygame.math.Vector2(sys_world_pos.x + wx, sys_world_pos.y + wy)
            w_screen = self.camera.world_to_screen(w_world)
             # Highlight
            if self.selected_object == wp:
                 pygame.draw.circle(screen, (255, 255, 255), w_screen, max(12, int(12 * self.camera.zoom)), 1)
            
            # Warp Asset
            # Warp Asset
            from game.assets.asset_manager import get_asset_manager
            am = get_asset_manager()
            img = am.get_random_from_group('warp_points', 'default', seed_id=hash(wp))
            
            if img:
                 size = int(12 * self.camera.zoom)
                 scaled = pygame.transform.smoothscale(img, (size, size))
                 dest = scaled.get_rect(center=(int(w_screen.x), int(w_screen.y)))
                 
                 # Additive Blending for "Glow" effect
                 screen.blit(scaled, dest, special_flags=pygame.BLEND_ADD)
            else:
                 pygame.draw.circle(screen, (200, 0, 255), w_screen, max(2, int(5 * self.camera.zoom)))

    def _draw_planet_sprite(self, screen, planet, center_pos, size):
        # Asset Selection (Copied from original loop)
        p_type_name = planet.planet_type.name.lower()
        cat = 'terran' # default
        if 'gas' in p_type_name: cat = 'gas'
        elif 'ice' in p_type_name: cat = 'ice'
        elif 'desert' in p_type_name or 'hot' in p_type_name: cat = 'venus'
        
        from game.assets.asset_manager import get_asset_manager
        am = get_asset_manager()
        
        img = am.get_random_from_group('planets', cat, seed_id=id(planet))
        if img:
            scaled = pygame.transform.smoothscale(img, (size*2, size*2)) # Size is radius
            dest = scaled.get_rect(center=(int(center_pos.x), int(center_pos.y)))
            screen.blit(scaled, dest)
        else:
            pygame.draw.circle(screen, planet.planet_type.color, (int(center_pos.x), int(center_pos.y)), size)
            
        # Owner Marker (Colony)
        # Owner Marker (Colony Flag)
        if planet.owner_id is not None: 
             # Fetch Empire
             owner_emp = next((e for e in self.empires if e.id == planet.owner_id), None)
             
             if owner_emp:
                  # Calculate Flag Position (Top Right of Planet)
                  # Ensure it's rendered ON TOP
                  flag_offset = size * 0.8
                  marker_pos = (int(center_pos.x + flag_offset), int(center_pos.y - flag_offset))
                  
                  # Check for Flag Asset
                  emp_assets = self.empire_assets.get(owner_emp.id)
                  if emp_assets and 'colony' in emp_assets:
                      flag_img = emp_assets['colony']
                      # Scale Flag
                      # Flag aspect usually 3:2
                      f_w = max(10, int(size * 1.5))
                      f_h = int(f_w * 0.66)
                      
                      scaled_flag = pygame.transform.smoothscale(flag_img, (f_w, f_h))
                      flag_rect = scaled_flag.get_rect(bottomleft=marker_pos) # Place bottom-left at marker pos (so it sticks out top-right)
                      screen.blit(scaled_flag, flag_rect)
                      
                      # Border
                      pygame.draw.rect(screen, (255, 255, 255), flag_rect, 1)
                  else:
                      # Fallback Circle
                      pygame.draw.circle(screen, owner_emp.color, marker_pos, max(3, int(size/3)))
                      pygame.draw.circle(screen, (255, 255, 255), marker_pos, max(3, int(size/3))+1, 1)

    def _draw_fleets(self, screen):
        for emp in self.empires:
            for f in emp.fleets:
                fx, fy = hex_to_pixel(f.location, self.HEX_SIZE)
                f_screen = self.camera.world_to_screen(pygame.math.Vector2(fx, fy))
                
                # Check if fleet icon is on screen
                fleet_on_screen = (0 <= f_screen.x <= self.screen_width and 0 <= f_screen.y <= self.screen_height)
                
                # Draw fleet icon only if on screen
                if fleet_on_screen:
                    emp_assets = self.empire_assets.get(emp.id)
                    if emp_assets and 'fleet' in emp_assets:
                         img = emp_assets['fleet']
                         # Scale
                         size = int(24 * self.camera.zoom)
                         if size < 12: size = 12
                         if size > 64: size = 64
                         
                         scaled = pygame.transform.smoothscale(img, (size, size))
                         dest = scaled.get_rect(center=(int(f_screen.x), int(f_screen.y)))
                         
                         screen.blit(scaled, dest)
                         
                         # Selection Box
                         if self.selected_fleet == f:
                              pygame.draw.rect(screen, (255, 255, 0), dest.inflate(4, 4), 1)
                    else:
                        # Draw Triangle (Fallback)
                        size = 10 * self.camera.zoom
                        if size < 8: size = 8
                        if size > 30: size = 30
                        
                        points = [
                            (f_screen.x, f_screen.y - size),
                            (f_screen.x - size/2, f_screen.y + size/2),
                            (f_screen.x + size/2, f_screen.y + size/2)
                        ]
                        
                        color = emp.color
                        if self.selected_fleet == f:
                            color = (255, 255, 0)
                            
                        pygame.draw.polygon(screen, color, points)
                
                # Draw path only for the selected fleet (visible even when zoomed elsewhere)
                if f == self.selected_fleet:
                    segments = self.session.get_fleet_path_projection(f, max_turns=50)
                    
                    start_screen = f_screen
                    font = None
                    if segments and self.camera.zoom >= 0.5:
                         font = pygame.font.SysFont("arial", 18, bold=True)

                    for seg in segments:
                        end_hex = seg['end']
                        is_warp = seg['is_warp']
                        turn_idx = seg['turn']
                        
                        ex, ey = hex_to_pixel(end_hex, self.HEX_SIZE)
                        end_screen = self.camera.world_to_screen(pygame.math.Vector2(ex, ey))
                        
                        # Per-segment culling: skip if both endpoints are off-screen
                        start_on = (0 <= start_screen.x <= self.screen_width and 0 <= start_screen.y <= self.screen_height)
                        end_on = (0 <= end_screen.x <= self.screen_width and 0 <= end_screen.y <= self.screen_height)
                        
                        if not start_on and not end_on:
                            # Both off-screen, skip this segment
                            start_screen = end_screen
                            continue
                        
                        # Line Color
                        color = (0, 255, 100) # Green (Normal)
                        width = 2
                        if is_warp:
                            color = (255, 50, 50) # Red (Warp)
                            width = 1
                        
                        # Draw Line
                        pygame.draw.line(screen, color, start_screen, end_screen, width)
                        
                        # Draw Turn Number
                        if font and not is_warp and end_on:
                            # Draw number at the END of the segment (arrival hex)
                            txt = font.render(str(turn_idx), True, (200, 200, 255))
                            # Center text on hex
                            tr = txt.get_rect(center=(end_screen.x, end_screen.y))
                            screen.blit(txt, tr)
                            
                        start_screen = end_screen
                    

    def _make_background_transparent(self, image, threshold=30):
        """Remove near-black background pixels."""
        image = image.convert_alpha()
        width, height = image.get_size()
        for x in range(width):
            for y in range(height):
                c = image.get_at((x, y))
                if c[0] < threshold and c[1] < threshold and c[2] < threshold:
                    image.set_at((x, y), (0, 0, 0, 0))
        return image
