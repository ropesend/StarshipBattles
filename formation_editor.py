
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

class FormationEditorScene:
    def __init__(self, screen_width, screen_height, on_return_menu):
        self.width = screen_width
        self.height = screen_height
        self.on_return_menu = on_return_menu
        
        # Data
        # list of [x, y] coordinates (World Space)
        self.arrows = [] 
        # Multi-selection: set of indices
        self.selected_indices = set()
        
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

        self.return_btn = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(self.width - 120, btn_y, 110, btn_h),
            text="Return",
            manager=self.ui_manager
        )

    # --- Coordinate Transforms ---
    def world_to_screen(self, wx, wy):
        cx, cy = self.width / 2, (self.height - self.toolbar_height) / 2
        sx = (wx * self.camera_zoom) + self.camera_pan[0] + cx
        sy = (wy * self.camera_zoom) + self.camera_pan[1] + cy
        return sx, sy

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
        xs = [self.arrows[i][0] for i in self.selected_indices]
        ys = [self.arrows[i][1] for i in self.selected_indices]
        return pygame.Rect(min(xs), min(ys), max(xs) - min(xs), max(ys) - min(ys))

    def get_resize_handles(self, bounds_rect):
        if not bounds_rect: return {}
        
        # Inflate bounds by 1 grid unit (50 units) for drawing box
        padding = 50
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
            elif event.ui_element == self.return_btn:
                self.on_return_menu()
            elif event.ui_element == self.clear_btn:
                self.clear_all()
            elif event.ui_element == self.circle_btn:
                self.generate_shape('circle')
            elif event.ui_element == self.x_btn:
                self.generate_shape('x')
            elif event.ui_element == self.line_btn:
                self.generate_shape('line')
                
        elif event.type == pygame_gui.UI_HORIZONTAL_SLIDER_MOVED:
            if event.ui_element == self.count_slider:
                val = int(event.value)
                self.shape_count = val
                self.count_entry.set_text(str(val))
        
        elif event.type == pygame_gui.UI_TEXT_ENTRY_FINISHED:
            if event.ui_element == self.count_entry:
                try:
                    val = int(event.text)
                    val = max(2, min(100, val))
                    self.shape_count = val
                    self.count_slider.set_current_value(val)
                except:
                    self.count_entry.set_text(str(self.shape_count))

        elif event.type == pygame.MOUSEWHEEL:
            if event.y > 0: self.camera_zoom *= 1.1
            elif event.y < 0: self.camera_zoom /= 1.1
                
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if not self.canvas_rect.collidepoint(event.pos): return
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
                    if len(name) == 2: # TL, TR, BL, BR
                        w = max(1, bounds.width)
                        h = max(1, bounds.height)
                        self.resize_aspect_ratio = w / h
                    else:
                        self.resize_aspect_ratio = None
                        
                    return

        wx, wy = self.screen_to_world(screen_pos[0], screen_pos[1])
        clicked_idx = self._get_arrow_at(wx, wy)
        
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

    def _update_group_resize(self, screen_pos):
        if not self.initial_group_bounds: return
        wx, wy = self.screen_to_world(screen_pos[0], screen_pos[1])
        if self.snap_enabled:
            wx = self.snap(wx)
            wy = self.snap(wy)

        # Inflate logic? No, handle calculations were based on inflated visual, but resize math should use actual bounds
        # But we need to use the visual handle position to determine the new edge.
        # This is tricky because the handle is offset.
        # Let's just assume the user drags the mouse to where they want the EDGE to be, plus padding maybe?
        # Actually user drags handle. Handle is at bounds + padding.
        # So Mouse World Pos = New Bounds Edge + Padding.
        # New Bounds Edge = Mouse World Pos - Padding.
        
        padding = 50
        
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
            current_w = nr - nl
            current_h = nb - nt
            
            # Width is master? Height is master? Depends on drag direction.
            # Simple approach: set H based on W
            target_h = current_w / self.resize_aspect_ratio
            
            # Reposition bottom or top?
            if 'B' in h:
                nb = nt + target_h
            else:
                nt = nb - target_h
        
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
            if self.snap_enabled:
                new_x = self.snap(new_x)
                new_y = self.snap(new_y)
            self.arrows[idx] = [new_x, new_y]

    def _handle_left_up(self, screen_pos):
        if self.state == 'POTENTIAL_CLICK':
             # This was a click (no drag)
             keys = pygame.key.get_pressed()
             shift = keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]
             
             # User Request: "When there are a group of selected arrows, clicking on a blank portion... should simply unselect... don't draw another."
             if self.selected_indices and not shift:
                 self.selected_indices = set()
                 # Do NOT add arrow
             else:
                 # Standard logic: Add arrow if nothing selected (or if user wants to add while holding shift?)
                 # If we just deselected, we are done.
                 # If we had nothing selected, we add an arrow.
                 if not shift: # If we processed the deselect above, we shouldn't be here if indices were > 0
                     # But self.selected_indices is now empty.
                     # We need to know if we deslected something.
                     # Actually, if we had items and didn't shift, we cleared them.
                     # The request implies we stop there. "Don't draw another".
                     
                     # Wait, if I start with 0 selected, clicking blank ADDS arrow.
                     # If I start with >0 selected, clicking blank DESELECTS and DOES NOT ADD arrow.
                     pass 
                 
                 wx, wy = self.screen_to_world(screen_pos[0], screen_pos[1])
                 if self.snap_enabled:
                     wx = self.snap(wx)
                     wy = self.snap(wy)
                 
                 # Logic check re-implemented:
                 # We need to know previous state. But we can't easily.
                 # Actually, we can check if we cleared selection in _handle_left_down?
                 # No, Left Down sets POTENTIAL_CLICK.
                 # Let's rely on checking if we *had* selection at Mouse Down?
                 # We didn't store that.
                 
                 # Let's check: Did we act on selection?
                 # If we are here, we clicked blank space.
                 # If self.selected_indices is NOT empty, we definitely deselect and stop.
                 if self.selected_indices and not shift:
                     self.selected_indices = set()
                 else:
                     # Empty selection or Shift held.
                     # If empty, add arrow.
                     # If Shift held, usually adds arrow to selection... wait, adding arrow object?
                     # "Add arrows by simply left clicking on a blank spot"
                     if not self.selected_indices: # Only add if nothing selected (or cleared)
                         self.add_arrow((wx, wy))
             
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
        self.arrows.append(list(pos))
        self.selected_indices = {len(self.arrows) - 1}
        self.update_info()

    def delete_selected(self):
        if not self.selected_indices: return
        to_delete = sorted(list(self.selected_indices), reverse=True)
        for idx in to_delete:
            if 0 <= idx < len(self.arrows):
                self.arrows.pop(idx)
        self.selected_indices = set()
        self.update_info()

    def clear_all(self):
        self.arrows = []
        self.selected_indices = set()
        self.update_info()

    def clone_selection(self):
        if not self.selected_indices: return
        sorted_indices = sorted(list(self.selected_indices))
        new_indices = set()
        offset = self.grid_size if self.snap_enabled else 20
        for idx in sorted_indices:
            ax, ay = self.arrows[idx]
            self.arrows.append([ax + offset, ay + offset])
            new_indices.add(len(self.arrows) - 1)
        self.selected_indices = new_indices
        self.update_info()

    def generate_shape(self, shape_type):
        count = self.shape_count
        radius = 200
        
        cx, cy = self.screen_to_world(self.width/2, (self.height - self.toolbar_height)/2)
        if self.snap_enabled:
             cx = self.snap(cx)
             cy = self.snap(cy)
             
        new_indices = set()
        start_idx = len(self.arrows)
        
        if shape_type == 'circle':
            for i in range(count):
                angle = (2 * math.pi * i) / count
                angle -= math.pi / 2
                ax = cx + math.cos(angle) * radius
                ay = cy + math.sin(angle) * radius
                if self.snap_enabled:
                    ax = self.snap(ax)
                    ay = self.snap(ay)
                self.arrows.append([ax, ay])
                new_indices.add(start_idx + i)
                
        elif shape_type == 'x':
            arm1_count = count // 2
            arm2_count = count - arm1_count
            for i in range(arm1_count):
                t = i / max(1, arm1_count - 1)
                ax = cx - radius + (2*radius * t)
                ay = cy - radius + (2*radius * t)
                if self.snap_enabled:
                    ax = self.snap(ax)
                    ay = self.snap(ay)
                self.arrows.append([ax, ay])
                new_indices.add(start_idx + i)
            for i in range(arm2_count):
                t = i / max(1, arm2_count - 1)
                ax = cx + radius - (2*radius * t)
                ay = cy - radius + (2*radius * t)
                if self.snap_enabled:
                    ax = self.snap(ax)
                    ay = self.snap(ay)
                self.arrows.append([ax, ay])
                new_indices.add(start_idx + arm1_count + i)
                
        elif shape_type == 'line':
            width = radius * 2
            for i in range(count):
                t = i / max(1, count - 1)
                ax = cx - radius + (width * t)
                ay = cy
                if self.snap_enabled:
                    ax = self.snap(ax)
                    ay = self.snap(ay)
                self.arrows.append([ax, ay])
                new_indices.add(start_idx + i)

        self.selected_indices = new_indices
        self.update_info()

    def save_formation(self):
        if not tk_root: return
        filename = filedialog.asksaveasfilename(
            initialdir=os.getcwd(), initialfile="formation.json",
            defaultextension=".json", filetypes=[("JSON Files", "*.json")], title="Save Formation"
        )
        if filename:
            try:
                data = {'arrows': self.arrows}
                with open(filename, 'w') as f: json.dump(data, f, indent=4)
            except Exception as e: print(f"Error saving: {e}")

    def load_formation(self):
        if not tk_root: return
        filename = filedialog.askopenfilename(
            initialdir=os.getcwd(), filetypes=[("JSON Files", "*.json")], title="Load Formation"
        )
        if filename:
            try:
                with open(filename, 'r') as f:
                    data = json.load(f)
                    if 'arrows' in data:
                        self.arrows = data['arrows']
                        self.selected_indices = set()
                        self.update_info()
            except Exception as e: print(f"Error loading: {e}")

    def update_info(self):
        count = len(self.arrows)
        sel_count = len(self.selected_indices)
        sel_str = f" | Selected: {sel_count}" if sel_count > 0 else ""
        self.info_label.set_text(f"Arrows: {count}{sel_str}")

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
            sx, sy = self.world_to_screen(ax, ay)
            if not self.canvas_rect.inflate(100,100).collidepoint(sx, sy): continue
                
            color = self.col_arrow_sel if i in self.selected_indices else self.col_arrow
            border_col = (255,255,255) if i in self.selected_indices else (0,0,0)
            
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

        if self.selected_indices:
            bounds = self.get_selection_bounds()
            if bounds:
                # Inflate Visual bounds for handles (+ padding)
                padding = 50
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
