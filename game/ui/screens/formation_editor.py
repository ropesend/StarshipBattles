
import pygame
import pygame_gui
import json
import os
import math
import tkinter
from tkinter import filedialog, simpledialog

# Initialize Tkinter root and hide it
try:
    tk_root = tkinter.Tk()
    tk_root.withdraw()
except:
    tk_root = None

class FormationCore:
    def __init__(self):
        # Data
        # list of [x, y] coordinates (World Space)
        self.arrows = [] 
        # Parallel list of attributes: [{'rotation_mode': 'relative'}, ...]
        self.arrow_attrs = []
        # Multi-selection: set of indices
        self.selected_indices = set()
        self.shape_count = 5

    def add_arrow(self, pos):
        self.arrows.append(list(pos))
        self.arrow_attrs.append({'rotation_mode': 'relative'})
        self.selected_indices = {len(self.arrows) - 1}

    def move_arrow(self, from_idx, to_idx):
        if from_idx == to_idx: return
        # Adjust indices if needed to prevent OOB
        if from_idx < 0 or from_idx >= len(self.arrows): return
        if to_idx < 0: to_idx = 0
        if to_idx >= len(self.arrows): to_idx = len(self.arrows) - 1
        
        item = self.arrows.pop(from_idx)
        self.arrows.insert(to_idx, item)
        attr = self.arrow_attrs.pop(from_idx)
        self.arrow_attrs.insert(to_idx, attr)
        # Update selection to follow the item
        self.selected_indices = {to_idx}

    def delete_selected(self):
        if not self.selected_indices: return
        to_delete = sorted(list(self.selected_indices), reverse=True)
        for idx in to_delete:
            if 0 <= idx < len(self.arrows):
                self.arrows.pop(idx)
                self.arrow_attrs.pop(idx)
        self.selected_indices = set()

    def clone_selection(self, offset):
        if not self.selected_indices: return
        sorted_indices = sorted(list(self.selected_indices))
        new_indices = set()
        for idx in sorted_indices:
            ax, ay = self.arrows[idx]
            self.arrows.append([ax + offset, ay + offset])
            self.arrow_attrs.append(self.arrow_attrs[idx].copy())
            new_indices.add(len(self.arrows) - 1)
        self.selected_indices = new_indices

    def clear_all(self):
        self.arrows = []
        self.arrow_attrs = []
        self.selected_indices = set()

    def generate_shape(self, shape_type, center_pos, radius=200):
        # Use Core's shape_count
        count = self.shape_count
        cx, cy = center_pos
             
        new_indices = set()
        start_idx = len(self.arrows)
        
        if shape_type == 'circle':
            for i in range(count):
                angle = (2 * math.pi * i) / count
                angle -= math.pi / 2
                ax = cx + math.cos(angle) * radius
                ay = cy + math.sin(angle) * radius
                # Don't snap here, keep float precision
                self.arrows.append([ax, ay])
                self.arrow_attrs.append({'rotation_mode': 'relative'})
                new_indices.add(start_idx + i)

        elif shape_type == 'disc':
            # Use Phyllotaxis Spiral (Sunflower pattern) for even packing
            golden_angle = math.pi * (3 - math.sqrt(5))
            for i in range(count):
                if count > 1:
                    t = i / (count - 1)
                else: 
                    t = 0
                
                # Sqrt for area preservation (uniform density)
                r_dist = math.sqrt(t) * radius
                theta = i * golden_angle
                
                ax = cx + math.cos(theta) * r_dist
                ay = cy + math.sin(theta) * r_dist
                
                self.arrows.append([ax, ay])
                self.arrow_attrs.append({'rotation_mode': 'relative'})
                new_indices.add(start_idx + i)
                
        elif shape_type == 'x':
            arm1_count = count // 2
            arm2_count = count - arm1_count
            for i in range(arm1_count):
                t = i / max(1, arm1_count - 1)
                ax = cx - radius + (2*radius * t)
                ay = cy - radius + (2*radius * t)
                # Don't snap here
                self.arrows.append([ax, ay])
                self.arrow_attrs.append({'rotation_mode': 'relative'})
                new_indices.add(start_idx + i)
            for i in range(arm2_count):
                t = i / max(1, arm2_count - 1)
                ax = cx + radius - (2*radius * t)
                ay = cy - radius + (2*radius * t)
                # Don't snap here
                self.arrows.append([ax, ay])
                self.arrow_attrs.append({'rotation_mode': 'relative'})
                new_indices.add(start_idx + arm1_count + i)
                
        elif shape_type == 'line':
            width = radius * 2
            for i in range(count):
                t = i / max(1, count - 1)
                ax = cx - radius + (width * t)
                ay = cy
                # Don't snap here
                self.arrows.append([ax, ay])
                self.arrow_attrs.append({'rotation_mode': 'relative'})
                new_indices.add(start_idx + i)

        self.selected_indices = new_indices

    def toggle_rotation_mode(self):
        if not self.selected_indices: return
        
        # Check current state of selection
        any_relative = False
        for idx in self.selected_indices:
            if self.arrow_attrs[idx].get('rotation_mode', 'relative') == 'relative':
                any_relative = True
                break
        
        new_mode = 'fixed' if any_relative else 'relative'
        for idx in self.selected_indices:
            self.arrow_attrs[idx]['rotation_mode'] = new_mode

    def save_to_file(self, filename):
        try:
            # Serialize to new format (List of Dicts) if mixed, or just Dicts
            out_arrows = []
            for i, pos in enumerate(self.arrows):
                attr = self.arrow_attrs[i]
                # Format: {"pos": [x, y], "rotation_mode": "relative"}
                out_arrows.append({
                    "pos": pos,
                    "rotation_mode": attr.get('rotation_mode', 'relative')
                })
            
            data = {'arrows': out_arrows}
            with open(filename, 'w') as f: json.dump(data, f, indent=4)
        except Exception as e: print(f"Error saving: {e}")

    def load_from_file(self, filename):
        try:
            with open(filename, 'r') as f:
                data = json.load(f)
                if 'arrows' in data:
                    raw_arrows = data['arrows']
                    self.arrows = []
                    self.arrow_attrs = []
                    for item in raw_arrows:
                        if isinstance(item, list): # Legacy
                            self.arrows.append(item)
                            self.arrow_attrs.append({'rotation_mode': 'relative'})
                        elif isinstance(item, dict):
                            self.arrows.append(item.get('pos', [0,0]))
                            self.arrow_attrs.append({'rotation_mode': item.get('rotation_mode', 'relative')})
                    
                    self.selected_indices = set()
        except Exception as e: print(f"Error loading: {e}")

class FormationEditorScene:
    def __init__(self, screen_width, screen_height, on_return_menu):
        self.width = screen_width
        self.height = screen_height
        self.on_return_menu = on_return_menu
        
        # Instantiate Core Model
        self.core = FormationCore()
        
        # Camera
        
        # Camera
        self.camera_zoom = 1.0
        self.camera_pan = [0, 0] # Offset in World Space
        
        # Settings
        self.grid_size = 50
        self.snap_enabled = True
        self.show_grid = True
        self.shape_count = 5 # Default count for shape generation
        
        # Interaction States
        self.state = 'IDLE' # IDLE, DRAGGING_ITEMS, BOX_SELECT, RESIZING_GROUP, PANNING, POTENTIAL_CLICK
        self.drag_start_world = None
        self.drag_start_screen = None
        self.drag_offsets = {} # index -> (offset_x, offset_y)
        self.resize_handle = None # 'TL', 'TR', 'BL', 'BR', 'T', 'R', 'B', 'L'
        self.initial_group_bounds = None # Rect
        self.initial_arrow_positions = {} # index -> (x,y)
        self.current_selection_rect = None # For marquee
        self.resize_aspect_ratio = None # To maintain aspect ratio
        
        # Renumbering
        self.renumber_mode = False
        self.renumber_target = 1
        
        # UI Manager
        self.ui_manager = pygame_gui.UIManager((screen_width, screen_height))
        
        # Layout
        self.toolbar_height = 80 # Increased for more controls
        self.canvas_rect = pygame.Rect(0, 0, screen_width, screen_height - self.toolbar_height)
        
        # Setup UI
        self._create_ui()
        
        # Colors
        self.col_bg = (30, 30, 40)
        self.col_grid = (45, 45, 55)
        self.col_axis = (60, 60, 70)
        self.col_arrow = (100, 200, 255)
        self.col_arrow_sel = (255, 255, 100)
        self.col_box = (100, 255, 100)

    def _create_ui(self):
        btn_y = self.height - 70
        btn_w = 110
        btn_h = 30
        spacing = 5
        start_x = 10
        
        # Top Row of Toolbar
        current_x = start_x
        
        self.clear_btn = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(current_x, btn_y, btn_w, btn_h),
            text="Clear All",
            manager=self.ui_manager
        )
        current_x += btn_w + spacing
        
        self.snap_btn = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(current_x, btn_y, btn_w, btn_h),
            text="Snap: ON",
            manager=self.ui_manager
        )
        current_x += btn_w + spacing

        self.clone_btn = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(current_x, btn_y, btn_w, btn_h),
            text="Clone Group",
            manager=self.ui_manager
        )
        current_x += btn_w + spacing
        
        self.delete_btn = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(current_x, btn_y, btn_w, btn_h),
            text="Delete",
            manager=self.ui_manager
        )
        current_x += btn_w + spacing
        
        self.save_btn = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(current_x, btn_y, btn_w, btn_h),
            text="Save",
            manager=self.ui_manager
        )
        current_x += btn_w + spacing
        
        self.load_btn = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(current_x, btn_y, btn_w, btn_h),
            text="Load",
            manager=self.ui_manager
        )
        current_x += btn_w + spacing
        
        self.rotation_mode_btn = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(current_x, btn_y, 140, btn_h),
            text="Rot: Relative",
            manager=self.ui_manager
        )
        current_x += 140 + spacing
        
        self.info_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(current_x, btn_y, 250, btn_h),
            text="Arrows: 0",
            manager=self.ui_manager
        )
        
        # Bottom Row of Toolbar (Shape generation)
        btn_y += 35
        current_x = start_x
        
        pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(current_x, btn_y, 80, btn_h),
            text="Shape Gen:",
            manager=self.ui_manager
        )
        current_x += 80 + spacing

        self.count_slider = pygame_gui.elements.UIHorizontalSlider(
            relative_rect=pygame.Rect(current_x, btn_y, 150, btn_h),
            start_value=5,
            value_range=(2, 50),
            manager=self.ui_manager
        )
        current_x += 150 + spacing
        
        self.count_entry = pygame_gui.elements.UITextEntryLine(
            relative_rect=pygame.Rect(current_x, btn_y, 50, btn_h),
            manager=self.ui_manager
        )
        self.count_entry.set_text("5")
        current_x += 50 + spacing
        
        self.circle_btn = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(current_x, btn_y, 80, btn_h),
            text="Circle",
            manager=self.ui_manager
        )
        current_x += 80 + spacing
        
        self.disc_btn = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(current_x, btn_y, 80, btn_h),
            text="Disc",
            manager=self.ui_manager
        )
        current_x += 80 + spacing
        
        self.x_btn = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(current_x, btn_y, 80, btn_h),
            text="X Shape",
            manager=self.ui_manager
        )
        current_x += 80 + spacing

        self.line_btn = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(current_x, btn_y, 80, btn_h),
            text="Line",
            manager=self.ui_manager
        )
        current_x += 80 + spacing

        # Renumber Controls
        self.renumber_mode_btn = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(current_x, btn_y, 110, btn_h),
            text="Renumber: OFF",
            manager=self.ui_manager
        )
        current_x += 110 + spacing

        self.renumber_slider = pygame_gui.elements.UIHorizontalSlider(
            relative_rect=pygame.Rect(current_x, btn_y, 100, btn_h),
            start_value=1,
            value_range=(1, 50),
            manager=self.ui_manager
        )
        current_x += 100 + spacing
        
        self.renumber_entry = pygame_gui.elements.UITextEntryLine(
            relative_rect=pygame.Rect(current_x, btn_y, 40, btn_h),
            manager=self.ui_manager
        )
        self.renumber_entry.set_text("1")
        current_x += 40 + spacing

        self.return_btn = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(self.width - 120, btn_y, 110, btn_h),
            text="Return",
            manager=self.ui_manager
        )

    @property
    def arrows(self): return self.core.arrows

    @property
    def arrow_attrs(self): return self.core.arrow_attrs
    
    @property
    def selected_indices(self): return self.core.selected_indices
    
    @selected_indices.setter
    def selected_indices(self, val): self.core.selected_indices = val
    
    # --- Coordinate Transforms ---
    def world_to_screen(self, wx, wy):
        cx, cy = self.width / 2, (self.height - self.toolbar_height) / 2
        sx = (wx * self.camera_zoom) + self.camera_pan[0] + cx
        sy = (wy * self.camera_zoom) + self.camera_pan[1] + cy
        return sx, sy

    def move_arrow(self, from_idx, to_idx):
        self.core.move_arrow(from_idx, to_idx)
        self.update_info()

    def screen_to_world(self, sx, sy):
        cx, cy = self.width / 2, (self.height - self.toolbar_height) / 2
        wx = (sx - self.camera_pan[0] - cx) / self.camera_zoom
        wy = (sy - self.camera_pan[1] - cy) / self.camera_zoom
        return wx, wy

    def snap(self, val):
        if not self.snap_enabled: return val
        return round(val / self.grid_size) * self.grid_size

    def get_selection_bounds(self):
        if not self.selected_indices: return None
        xs = []
        ys = []
        for i in self.selected_indices:
            ax, ay = self.arrows[i]
            if self.snap_enabled:
                ax = self.snap(ax)
                ay = self.snap(ay)
            xs.append(ax)
            ys.append(ay)
        return pygame.Rect(min(xs), min(ys), max(xs) - min(xs), max(ys) - min(ys))

    def get_resize_handles(self, bounds_rect):
        if not bounds_rect: return {}
        
        # Inflate bounds by 1 grid unit for drawing box
        padding = self.grid_size
        inflated = bounds_rect.inflate(padding*2, padding*2)
        
        l, t = self.world_to_screen(inflated.left, inflated.top)
        r, b = self.world_to_screen(inflated.right, inflated.bottom)
        w, h = r - l, b - t
        
        handles = {}
        hs = 8 # handle size
        
        # Corners
        handles['TL'] = pygame.Rect(l - hs, t - hs, hs*2, hs*2)
        handles['TR'] = pygame.Rect(r - hs, t - hs, hs*2, hs*2)
        handles['BL'] = pygame.Rect(l - hs, b - hs, hs*2, hs*2)
        handles['BR'] = pygame.Rect(r - hs, b - hs, hs*2, hs*2)
        
        if w > 40: # Only if large enough
             handles['T'] = pygame.Rect(l + w/2 - hs, t - hs, hs*2, hs*2)
             handles['B'] = pygame.Rect(l + w/2 - hs, b - hs, hs*2, hs*2)
        if h > 40:
             handles['L'] = pygame.Rect(l - hs, t + h/2 - hs, hs*2, hs*2)
             handles['R'] = pygame.Rect(r - hs, t + h/2 - hs, hs*2, hs*2)
             
        return handles

    # --- Interaction ---
    def handle_event(self, event):
        self.ui_manager.process_events(event)
        
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == self.snap_btn:
                self.snap_enabled = not self.snap_enabled
                self.snap_btn.set_text(f"Snap: {'ON' if self.snap_enabled else 'OFF'}")
            elif event.ui_element == self.clone_btn:
                self.clone_selection()
            elif event.ui_element == self.delete_btn:
                self.delete_selected()
            elif event.ui_element == self.save_btn:
                self.save_formation()
            elif event.ui_element == self.load_btn:
                self.load_formation()
            elif event.ui_element == self.rotation_mode_btn:
                self._toggle_rotation_mode()
            elif event.ui_element == self.return_btn:
                self.on_return_menu()
            elif event.ui_element == self.clear_btn:
                self.clear_all()
            elif event.ui_element == self.circle_btn:
                self.generate_shape('circle')
            elif event.ui_element == self.disc_btn:
                self.generate_shape('disc')
            elif event.ui_element == self.x_btn:
                self.generate_shape('x')
            elif event.ui_element == self.line_btn:
                self.generate_shape('line')
            elif event.ui_element == self.renumber_mode_btn:
                self.renumber_mode = not self.renumber_mode
                self.renumber_mode_btn.set_text(f"Renumber: {'ON' if self.renumber_mode else 'OFF'}")
                if self.renumber_mode:
                    self.state = 'IDLE' 
                    
        elif event.type == pygame_gui.UI_HORIZONTAL_SLIDER_MOVED:
            if event.ui_element == self.count_slider:
                val = int(event.value)
                self.shape_count = val
                self.core.shape_count = val
                self.count_entry.set_text(str(val))
            elif event.ui_element == self.renumber_slider:
                val = int(event.value)
                self.renumber_target = val
                self.renumber_entry.set_text(str(val))
        
        elif event.type == pygame_gui.UI_TEXT_ENTRY_FINISHED:
            if event.ui_element == self.count_entry:
                try:
                    val = int(event.text)
                    val = max(2, min(100, val))
                    self.shape_count = val
                    self.core.shape_count = val
                    self.count_slider.set_current_value(val)
                except:
                    self.count_entry.set_text(str(self.shape_count))
            elif event.ui_element == self.renumber_entry:
                try:
                    val = int(event.text)
                    val = max(1, min(len(self.arrows), val))
                    self.renumber_target = val
                    self.renumber_slider.set_current_value(val)
                except:
                    self.renumber_entry.set_text(str(self.renumber_target))

        elif event.type == pygame.MOUSEWHEEL:
            if event.y > 0: self.camera_zoom *= 1.1
            elif event.y < 0: self.camera_zoom /= 1.1
                
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                mx, my = pygame.mouse.get_pos()
                if self.canvas_rect.collidepoint((mx, my)):
                    wx, wy = self.screen_to_world(mx, my)
                    if self.snap_enabled:
                        wx = self.snap(wx)
                        wy = self.snap(wy)
                    self.add_arrow((wx, wy))

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if not self.canvas_rect.collidepoint(event.pos): return
            
            # Check Up/Down Arrow Clicks first (Screen Space UI)
            if len(self.selected_indices) == 1:
                idx = list(self.selected_indices)[0]
                res = self._check_renumber_arrows(event.pos, idx)
                if res == 'up': # Decrease Index (Move to 1)
                     self.move_arrow(idx, max(0, idx - 1))
                     return
                elif res == 'down': # Increment Index (Move to End)
                     self.move_arrow(idx, min(len(self.arrows) - 1, idx + 1))
                     return

            if event.button == 3: # Right click -> Pan
                self.state = 'PANNING'
                self.drag_start_screen = event.pos
                self.drag_start_world = self.camera_pan[:]
            elif event.button == 1: # Left click
                self._handle_left_down(event.pos)

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                self._handle_left_up(event.pos)
            elif event.button == 3:
                if self.state == 'PANNING':
                    self.state = 'IDLE'

        elif event.type == pygame.MOUSEMOTION:
            self._handle_mouse_motion(event.pos)

    def _handle_left_down(self, screen_pos):
        wx, wy = self.screen_to_world(screen_pos[0], screen_pos[1])
        clicked_idx = self._get_arrow_at(wx, wy)
        
        # Renumber Mode Handling
        if self.renumber_mode and clicked_idx is not None:
             # Move clicked arrow to target position
             target_idx = self.renumber_target - 1 # 1-based to 0-based
             # Clamp target
             target_idx = max(0, min(len(self.arrows)-1, target_idx))
             self.move_arrow(clicked_idx, target_idx)
             return # Swallow event
             
        keys = pygame.key.get_pressed()
        shift = keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]
        
        bounds = self.get_selection_bounds()
        if bounds:
            handles = self.get_resize_handles(bounds)
            for name, rect in handles.items():
                if rect.collidepoint(screen_pos):
                    self.state = 'RESIZING_GROUP'
                    self.resize_handle = name
                    self.initial_group_bounds = bounds
                    self.initial_arrow_positions = {i: self.arrows[i][:] for i in self.selected_indices}
                    self.drag_start_screen = screen_pos
                    
                    # Store Aspect Ratio if resizing corner
                    # Aspect Ratio should be of the BOX (bounds + padding) or the CONTENT?
                    # Visually, the user resizes the BOX.
                    # Padded box dimensions:
                    w = max(1, bounds.width + self.grid_size*2)
                    h = max(1, bounds.height + self.grid_size*2)
                    
                    if len(name) == 2: # TL, TR, BL, BR
                        self.resize_aspect_ratio = w / h
                    else:
                        self.resize_aspect_ratio = None
                        
                    return
        
        # Re-fetch index if handle check failed (it might have been cleared by early return above, but safe to fetch again)
        # Actually logic flow: if handle clicked, we return. 
        # So hereafter, either we clicked arrow or blank.
        
        if clicked_idx is not None:
            if shift:
                if clicked_idx in self.selected_indices:
                    self.selected_indices.remove(clicked_idx)
                else:
                    self.selected_indices.add(clicked_idx)
            else:
                if clicked_idx not in self.selected_indices:
                    self.selected_indices = {clicked_idx}
            
            if self.selected_indices:
                self.state = 'DRAGGING_ITEMS'
                self.drag_start_world = (wx, wy)
                self.drag_offsets = {}
                for idx in self.selected_indices:
                    self.drag_offsets[idx] = (self.arrows[idx][0] - wx, self.arrows[idx][1] - wy)
            return
        
        # Clicked Blank Space
        # If selection exists and no handle/arrow clicked, we first check if it's a drag or click in mouse_up.
        # But if user just wants to deselect, logic happens later.
        
        self.state = 'POTENTIAL_CLICK'
        self.drag_start_screen = screen_pos
        self.drag_start_world = (wx, wy)

    def _check_renumber_arrows(self, screen_pos, idx):
        # Calculate arrow positions identical to draw()
        ax, ay = self.arrows[idx]
        if self.snap_enabled:
            ax = self.snap(ax)
            ay = self.snap(ay)
            
        sx, sy = self.world_to_screen(ax, ay)
        scale = 20 * self.camera_zoom 
        
        # Up Arrow Rect (Approximate hit box)
        up_rect = pygame.Rect(sx - 15, sy - scale - 30, 30, 30)
        # Down Arrow Rect
        down_rect = pygame.Rect(sx - 15, sy + scale - 5, 30, 30)
        
        if up_rect.collidepoint(screen_pos): return 'up'
        if down_rect.collidepoint(screen_pos): return 'down'
        return None

    def _handle_mouse_motion(self, screen_pos):
        if self.state == 'PANNING':
            dx = screen_pos[0] - self.drag_start_screen[0]
            dy = screen_pos[1] - self.drag_start_screen[1]
            self.camera_pan[0] = self.drag_start_world[0] + dx
            self.camera_pan[1] = self.drag_start_world[1] + dy
            
        elif self.state == 'DRAGGING_ITEMS':
            wx, wy = self.screen_to_world(screen_pos[0], screen_pos[1])
            if self.snap_enabled: pass 
            
            for idx, (off_x, off_y) in self.drag_offsets.items():
                target_x = wx + off_x
                target_y = wy + off_y
                if self.snap_enabled:
                    target_x = self.snap(target_x)
                    target_y = self.snap(target_y)
                self.arrows[idx] = [target_x, target_y]
                
        elif self.state == 'RESIZING_GROUP':
             self._update_group_resize(screen_pos)
             
        elif self.state == 'POTENTIAL_CLICK':
            dist = math.hypot(screen_pos[0] - self.drag_start_screen[0], screen_pos[1] - self.drag_start_screen[1])
            if dist > 5:
                # If we had a selection and started dragging blank space, clear it?
                # User asked: "clicking on a blank portion should unselect, don't draw another"
                # But previously: drag creates marquee.
                # Reconcile: Click = Deselect (handled in Up). Drag = Marquee (handled here).
                # But wait, does user want marquee at all? "When there are a group of selected arrows, clicking blank... unselect"
                # This implies dragging blank while selected might mean something else? Or usually it means deselect+marquee.
                
                # Let's keep marquee logic, but ensure click clears selection.
                self.state = 'BOX_SELECT'
                keys = pygame.key.get_pressed()
                if not (keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]):
                     self.selected_indices = set()
                     
    def _toggle_rotation_mode(self):
        self.core.toggle_rotation_mode()
        self.update_info()

    def _update_group_resize(self, screen_pos):
        if not self.initial_group_bounds: return
        wx, wy = self.screen_to_world(screen_pos[0], screen_pos[1])
        if self.snap_enabled:
            wx = self.snap(wx)
            wy = self.snap(wy)

        padding = self.grid_size
        
        b = self.initial_group_bounds
        # Bounds used for math
        l, t, r, bot = b.left, b.top, b.right, b.bottom
        nl, nt, nr, nb = l, t, r, bot
        
        h = self.resize_handle
        
        # Adjust input wx, wy to be 'edge' positions by removing padding bias depending on handle side
        # e.g. Right handle is at r + padding. So valid 'r' is wx - padding.
        
        target_x = wx
        target_y = wy
        
        if 'L' in h: nl = min(target_x + padding, nr - 10)
        if 'R' in h: nr = max(target_x - padding, nl + 10)
        if 'T' in h: nt = min(target_y + padding, nb - 10)
        if 'B' in h: nb = max(target_y - padding, nt + 10)
        
        # Aspect Ratio Lock for Corners
        if self.resize_aspect_ratio:
            # Padded dimensions logic
            current_padded_w = (nr - nl) + padding*2
            current_padded_h = (nb - nt) + padding*2
            
            # Maintain ratio of padded box
            # ratio = w / h -> w = ratio * h
            
            # If changing Width (L/R driven), adjust Height
            if 'L' in h or 'R' in h:
                target_padded_h = current_padded_w / self.resize_aspect_ratio
                target_h_content = target_padded_h - padding*2
                
                # Center vertical expansion or from opposite side?
                # Usually Aspect Scale is from opposite corner.
                # If dragging TR, Bottom Left is anchor.
                
                # If T/B not in handle, we need to decide which way to expand.
                # If top-row (TL, TR), B is anchor.
                if 'T' in h: # dragging corner
                     nt = nb - target_h_content
                elif 'B' in h:
                     nb = nt + target_h_content
                else: # Just side drag? Aspect ratio usually only for corners.
                     # If handle is just 'L', we don't aspect restrict?
                     # Code in handle_left_down sets ratio only for corners.
                     # So we are essentially guaranteed T or B is present if ratio is set.
                     pass

            elif 'T' in h or 'B' in h:
                target_padded_w = current_padded_h * self.resize_aspect_ratio
                target_w_content = target_padded_w - padding*2
                
                if 'L' in h:
                    nl = nr - target_w_content
                elif 'R' in h:
                    nr = nl + target_w_content
        
        old_w = max(1, r - l)
        old_h = max(1, bot - t)
        new_w = max(1, nr - nl)
        new_h = max(1, nb - nt)
        
        scale_x = new_w / old_w
        scale_y = new_h / old_h
        
        for idx in self.selected_indices:
            orig_x, orig_y = self.initial_arrow_positions[idx]
            rel_x = orig_x - l
            rel_y = orig_y - t
            new_x = nl + rel_x * scale_x
            new_y = nt + rel_y * scale_y
        for idx in self.selected_indices:
            orig_x, orig_y = self.initial_arrow_positions[idx]
            rel_x = orig_x - l
            rel_y = orig_y - t
            new_x = nl + rel_x * scale_x
            new_y = nt + rel_y * scale_y
            # Do NOT snap here to preserve floating point relative positions during scaling
            # Visual snapping happens in draw()
            self.arrows[idx] = [new_x, new_y]

    def _handle_left_up(self, screen_pos):
        if self.state == 'POTENTIAL_CLICK':
             # This was a click (no drag)
             keys = pygame.key.get_pressed()
             shift = keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]
             
             if self.selected_indices and not shift:
                 self.selected_indices = set()

             
             self.state = 'IDLE'
             
        elif self.state == 'BOX_SELECT':
            start_wx, start_wy = self.drag_start_world
            end_wx, end_wy = self.screen_to_world(screen_pos[0], screen_pos[1])
            l = min(start_wx, end_wx)
            r = max(start_wx, end_wx)
            t = min(start_wy, end_wy)
            b = max(start_wy, end_wy)
            box_rect = pygame.Rect(l, t, r-l, b-t)
            
            keys = pygame.key.get_pressed()
            shift = keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]
            new_selection = set()
            for i, (ax, ay) in enumerate(self.arrows):
                if box_rect.collidepoint(ax, ay):
                    new_selection.add(i)
            if shift: self.selected_indices.update(new_selection)
            else: self.selected_indices = new_selection
            self.state = 'IDLE'
        else:
            self.state = 'IDLE'
            self.resize_handle = None
            self.initial_group_bounds = None
        self.update_info()

    def _get_arrow_at(self, wx, wy):
        mx, my = self.world_to_screen(wx, wy)
        click_radius = 25 # Increased for easy clicking
        for i in range(len(self.arrows) - 1, -1, -1):
             ax, ay = self.arrows[i]
             sx, sy = self.world_to_screen(ax, ay)
             dist = math.hypot(mx - sx, my - sy)
             if dist < click_radius: return i
        return None

    def add_arrow(self, pos):
        self.core.add_arrow(pos)
        self.update_info()

    def delete_selected(self):
        self.core.delete_selected()
        self.update_info()

    def clone_selection(self):
        offset = self.grid_size if self.snap_enabled else 20
        self.core.clone_selection(offset)
        self.update_info()

    def clear_all(self):
        self.core.clear_all()
        self.update_info()

    def generate_shape(self, shape_type):
        cx, cy = self.screen_to_world(self.width/2, (self.height - self.toolbar_height)/2)
        if self.snap_enabled:
             cx = self.snap(cx)
             cy = self.snap(cy)
        
        self.core.shape_count = self.shape_count
        self.core.generate_shape(shape_type, (cx, cy))
        self.update_info()

    def save_formation(self):
        if not tk_root: return
        base_path = os.path.dirname(os.path.abspath(__file__))
        initial_dir = os.path.join(base_path, "data", "formations")
        if not os.path.exists(initial_dir): os.makedirs(initial_dir)

        filename = filedialog.asksaveasfilename(
            initialdir=initial_dir, initialfile="formation.json",
            defaultextension=".json", filetypes=[("JSON Files", "*.json")], title="Save Formation"
        )
        if filename:
            self.core.save_to_file(filename)

    def load_formation(self):
        if not tk_root: return
        base_path = os.path.dirname(os.path.abspath(__file__))
        initial_dir = os.path.join(base_path, "data", "formations")
        if not os.path.exists(initial_dir): os.makedirs(initial_dir)

        filename = filedialog.askopenfilename(
            initialdir=initial_dir, filetypes=[("JSON Files", "*.json")], title="Load Formation"
        )
        if filename:
            self.core.load_from_file(filename)
            self.update_info()

    def update_info(self):
        count = len(self.arrows)
        sel_count = len(self.selected_indices)
        sel_str = f" | Selected: {sel_count}" if sel_count > 0 else ""
        self.info_label.set_text(f"Arrows: {count}{sel_str}")
        
        # Update Rotation Btn text based on selection
        if hasattr(self, 'rotation_mode_btn'):
            if not self.selected_indices:
                self.rotation_mode_btn.set_text("Rot: -")
                self.rotation_mode_btn.disable()
            else:
                self.rotation_mode_btn.enable()
                # Check consistency
                modes = set()
                for idx in self.selected_indices:
                    modes.add(self.arrow_attrs[idx].get('rotation_mode', 'relative'))
                
                if len(modes) > 1:
                    self.rotation_mode_btn.set_text("Rot: Mixed")
                elif 'fixed' in modes:
                    self.rotation_mode_btn.set_text("Rot: Fixed")
                else:
                    self.rotation_mode_btn.set_text("Rot: Relative")
        
        # Manually update slider range if possible, or just clamp input
        if hasattr(self, 'renumber_slider'):
             # Pygame_gui doesn't easy exposure of range adjustment without rebuilding, 
             # but we can try setting the value range directly if accessible, or rebuild.
             # Rebuilding is expensive in update loop.
             # Let's just assume 50 is enough or create it with dynamic max if we rebuild whole UI.
             pass

    def update(self, dt):
        self.ui_manager.update(dt)

    def draw(self, screen):
        screen.fill(self.col_bg)
        if self.show_grid: self._draw_grid(screen)
        
        ox, oy = self.world_to_screen(0, 0)
        pygame.draw.line(screen, self.col_axis, (ox, 0), (ox, self.height - self.toolbar_height), 2)
        pygame.draw.line(screen, self.col_axis, (0, oy), (self.width, oy), 2)
        
        font = pygame.font.SysFont("Arial", 14, bold=True)
        # Visual Update: Large Triangles ("Arrows")
        scale = 20 * self.camera_zoom # increased size
        
        for i, (ax, ay) in enumerate(self.arrows):
            if self.snap_enabled:
                ax = self.snap(ax)
                ay = self.snap(ay)
            
            sx, sy = self.world_to_screen(ax, ay)
            if not self.canvas_rect.inflate(100,100).collidepoint(sx, sy): continue
                
            color = self.col_arrow_sel if i in self.selected_indices else self.col_arrow
            border_col = (255,255,255) if i in self.selected_indices else (0,0,0)
            
            # Check attribute
            attr = self.arrow_attrs[i]
            is_fixed = attr.get('rotation_mode', 'relative') == 'fixed'
            if is_fixed:
                color = (100, 255, 100) if i not in self.selected_indices else (200, 255, 200)
            
            # Draw Triangle
            # Point Up
            points = [
                (sx, sy - scale),
                (sx - scale*0.8, sy + scale*0.8),
                (sx + scale*0.8, sy + scale*0.8)
            ]
            
            pygame.draw.polygon(screen, color, points)
            pygame.draw.polygon(screen, border_col, points, 2)
            
            # Draw Number
            if scale > 10:
                txt = font.render(str(i + 1), True, (0, 0, 0))
                # rough center
                screen.blit(txt, (int(sx) - txt.get_width()//2, int(sy)))

        # Draw Single Selection Extras (Renumber arrows)
        if len(self.selected_indices) == 1:
            idx = list(self.selected_indices)[0]
            ax, ay = self.arrows[idx]
            if self.snap_enabled:
                ax = self.snap(ax)
                ay = self.snap(ay)
                
            sx, sy = self.world_to_screen(ax, ay)
            
            # Up Arrow (Decrease Number)
            up_poly = [(sx, sy - scale - 25), (sx - 10, sy - scale - 10), (sx + 10, sy - scale - 10)]
            pygame.draw.polygon(screen, (200, 200, 200), up_poly)
            
            # Down Arrow (Increase Number)
            down_poly = [(sx, sy + scale + 25), (sx - 10, sy + scale + 10), (sx + 10, sy + scale + 10)]
            pygame.draw.polygon(screen, (200, 200, 200), down_poly)

        if self.selected_indices:
            bounds = self.get_selection_bounds()
            if bounds:
                # Inflate Visual bounds for handles (+ padding)
                padding = self.grid_size
                inflated = bounds.inflate(padding*2, padding*2)
                
                l, t = self.world_to_screen(inflated.left, inflated.top)
                r, b = self.world_to_screen(inflated.right, inflated.bottom)
                screen_bounds = pygame.Rect(l, t, r-l, b-t)
                pygame.draw.rect(screen, self.col_box, screen_bounds, 1)
                handles = self.get_resize_handles(bounds)
                for h_rect in handles.values():
                    pygame.draw.rect(screen, self.col_box, h_rect)

        if self.state == 'BOX_SELECT' or self.state == 'POTENTIAL_CLICK':
             mx, my = pygame.mouse.get_pos()
             sx, sy = self.drag_start_screen
             rect = pygame.Rect(min(sx, mx), min(sy, my), abs(mx-sx), abs(my-sy))
             if self.state == 'BOX_SELECT':
                 surf = pygame.Surface(rect.size, pygame.SRCALPHA)
                 surf.fill((100, 255, 100, 50))
                 screen.blit(surf, rect.topleft)
                 pygame.draw.rect(screen, (100, 255, 100), rect, 1)

        pygame.draw.rect(screen, (20, 20, 30), (0, self.height - self.toolbar_height, self.width, self.toolbar_height))
        self.ui_manager.draw_ui(screen)

    def _draw_grid(self, screen):
        wx0, wy0 = self.screen_to_world(0, 0)
        wx1, wy1 = self.screen_to_world(self.width, self.height - self.toolbar_height)
        start_x = math.floor(wx0 / self.grid_size) * self.grid_size
        end_x = math.ceil(wx1 / self.grid_size) * self.grid_size
        start_y = math.floor(wy0 / self.grid_size) * self.grid_size
        end_y = math.ceil(wy1 / self.grid_size) * self.grid_size
        grid_col = self.col_grid
        x = start_x
        while x <= end_x:
            sx, _ = self.world_to_screen(x, 0)
            pygame.draw.line(screen, grid_col, (sx, 0), (sx, self.height - self.toolbar_height))
            x += self.grid_size
        y = start_y
        while y <= end_y:
             _, sy = self.world_to_screen(0, y)
             pygame.draw.line(screen, grid_col, (0, sy), (self.width, sy))
             y += self.grid_size

    def handle_resize(self, w, h):
        self.width = w
        self.height = h
        self.ui_manager.set_window_resolution((w, h))
        self.canvas_rect = pygame.Rect(0, 0, w, h - self.toolbar_height)
        self.ui_manager.clear_and_reset()
        self._create_ui()
