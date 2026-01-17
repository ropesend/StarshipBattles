
import os
import sys
import shutil
import uuid
import pygame
import glob
import math
import json

# --- Constants ---
DEFAULT_WINDOW_WIDTH = 1600
DEFAULT_WINDOW_HEIGHT = 900
SIDEBAR_WIDTH = 300
BG_COLOR = (30, 30, 30)
SIDEBAR_COLOR = (50, 50, 50)
TEXT_COLOR = (220, 220, 220)
HIGHLIGHT_COLOR = (100, 100, 255)
MULTI_SELECT_COLOR = (80, 80, 200)
PLACEHOLDER_COLOR = (0, 0, 0)
GRID_BG_COLOR = (40, 40, 40)
INPUT_BG_COLOR = (20, 20, 20)
ACTIVE_TAG_COLOR = (70, 150, 70)

TILE_SIZE = 128
EXPORT_TILE_SIZE = 256
SOURCE_DIR = r"C:\Dev\Starship Battles\assets\Images\Components\New Component images"
TAGS_FILE = os.path.join(SOURCE_DIR, "component_tags.json")

# --- Helper Classes ---

class TextInput:
    def __init__(self, x, y, w, h, font, placeholder="Enter tag..."):
        self.rect = pygame.Rect(x, y, w, h)
        self.font = font
        self.text = ""
        self.placeholder = placeholder
        self.active = False
        self.color_inactive = (100, 100, 100)
        self.color_active = (255, 255, 255)
        self.bg_color = INPUT_BG_COLOR

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.active = True
            else:
                self.active = False
        elif event.type == pygame.KEYDOWN:
            if self.active:
                if event.key == pygame.K_RETURN:
                    return self.text  # Return text to be processed
                elif event.key == pygame.K_BACKSPACE:
                    self.text = self.text[:-1]
                else:
                    self.text += event.unicode
        return None

    def draw(self, screen):
        # Draw BG
        color = self.color_active if self.active else self.color_inactive
        pygame.draw.rect(screen, self.bg_color, self.rect)
        pygame.draw.rect(screen, color, self.rect, 2)

        # Draw Text
        display_text = self.text if self.text else self.placeholder
        color_text = (255, 255, 255) if self.text else (150, 150, 150)
        
        # Simple clipping/scrolling not implemented, assume short tags
        txt_surf = self.font.render(display_text, True, color_text)
        
        # Clip
        screen.set_clip(self.rect.inflate(-4, -4))
        screen.blit(txt_surf, (self.rect.x + 5, self.rect.y + 5))
        screen.set_clip(None)

    def clear(self):
        self.text = ""


class ComponentItem:
    def __init__(self, path):
        self.path = path  # None if placeholder
        self.original_filename = os.path.basename(path) if path else "PLACEHOLDER"
        self.surface = None
        self.export_surface = None
        self.is_placeholder = (path is None)
        self.rect = None
        self.tags = set()
        
    def load_image(self):
        if self.is_placeholder:
            self.surface = pygame.Surface((TILE_SIZE, TILE_SIZE))
            self.surface.fill(PLACEHOLDER_COLOR)
            pygame.draw.rect(self.surface, (100, 100, 100), (0,0,TILE_SIZE,TILE_SIZE), 1)
            pygame.draw.line(self.surface, (50,50,50), (0,0), (TILE_SIZE, TILE_SIZE))
            pygame.draw.line(self.surface, (50,50,50), (TILE_SIZE,0), (0, TILE_SIZE))
            self.export_surface = pygame.Surface((EXPORT_TILE_SIZE, EXPORT_TILE_SIZE))
            self.export_surface.fill(PLACEHOLDER_COLOR)
        else:
            try:
                img = pygame.image.load(self.path)
                self.surface = pygame.transform.smoothscale(img, (TILE_SIZE, TILE_SIZE))
                self.export_surface = pygame.transform.smoothscale(img, (EXPORT_TILE_SIZE, EXPORT_TILE_SIZE))
            except Exception as e:
                print(f"Error loading {self.path}: {e}")
                self.is_placeholder = True
                self.load_image()

class Button:
    def __init__(self, rect, text, callback, color=(70, 70, 70), hover_color=(90, 90, 90), text_color=TEXT_COLOR):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.callback = callback
        self.color = color
        self.hover_color = hover_color
        self.text_color = text_color
        self.is_hovered = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.is_hovered and event.button == 1:
                self.callback()
                return True
        return False

    def draw(self, screen, font):
        c = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(screen, c, self.rect, border_radius=5)
        pygame.draw.rect(screen, (100,100,100), self.rect, 1, border_radius=5)
        
        txt_surf = font.render(self.text, True, self.text_color)
        text_rect = txt_surf.get_rect(center=self.rect.center)
        screen.blit(txt_surf, text_rect)

class App:
    def __init__(self):
        pygame.init()
        self.width = DEFAULT_WINDOW_WIDTH
        self.height = DEFAULT_WINDOW_HEIGHT
        self.screen = pygame.display.set_mode((self.width, self.height), pygame.RESIZABLE)
        pygame.display.set_caption("Component Manager Tool")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Arial", 16)
        self.small_font = pygame.font.SysFont("Arial", 14)
        self.title_font = pygame.font.SysFont("Arial", 20, bold=True)
        
        self.items = []
        self.loading = True
        
        # State
        self.selected_indices = set()
        self.last_selected_index = None # For Shift-Click
        
        # Drag State
        self.is_dragging = False
        self.dragged_items = []     # List of ComponentItem objects
        self.drag_leader_idx = None # Original index of the item clicked to start drag
        self.drag_offset_x = 0
        self.drag_offset_y = 0
        
        self.scroll_y = 0
        self.target_insert_index = None
        
        # Tags System
        self.all_tags = set()
        self.active_filters = set()
        self.tag_input = TextInput(20, 200, SIDEBAR_WIDTH - 40, 30, self.font)
        
        # Layout
        self.grid_start_x = SIDEBAR_WIDTH + 20
        self.grid_start_y = 20
        self.grid_spacing = 10
        self.recalc_layout()
        
        # Buttons
        self.buttons = [
            Button((20, 20, SIDEBAR_WIDTH-40, 40), "Add Placeholder", self.add_placeholder),
            Button((20, 70, SIDEBAR_WIDTH-40, 40), "Delete Selected", self.delete_selected),
            Button((20, 120, SIDEBAR_WIDTH-40, 50), "PROCESS & SAVE", self.process_and_save, color=(40, 100, 40), hover_color=(50, 140, 50)),
            Button((20, 240, SIDEBAR_WIDTH-40, 30), "Add Tag to Selected", self.add_tag_from_input),
            Button((20, 280, SIDEBAR_WIDTH-40, 30), "Clear Filters", self.clear_filters)
        ]

    def recalc_layout(self):
        available_width = self.width - self.grid_start_x - 20
        self.grid_cols = max(1, available_width // (TILE_SIZE + self.grid_spacing))

    def load_files(self):
        print("Loading files...")
        if not os.path.exists(SOURCE_DIR):
            os.makedirs(SOURCE_DIR, exist_ok=True)

        # Load Tags
        file_tags = {}
        if os.path.exists(TAGS_FILE):
            try:
                with open(TAGS_FILE, 'r') as f:
                    file_tags = json.load(f)
            except json.JSONDecodeError:
                print("Error loading tags file.")

        extensions = ['*.jpg', '*.jpeg', '*.png']
        files = []
        for ext in extensions:
            files.extend(glob.glob(os.path.join(SOURCE_DIR, ext)))
        
        files.sort()
        
        count = 0 
        for f in files:
            filename = os.path.basename(f)
            if "Component_Tilemap" in filename:
                continue

            item = ComponentItem(f)
            
            # Apply tags
            if filename in file_tags:
                item.tags = set(file_tags[filename])
                self.all_tags.update(item.tags)
            
            item.load_image()
            self.items.append(item)
            count += 1
            
            if count % 10 == 0:
                self.screen.fill(BG_COLOR)
                txt = self.font.render(f"Loading {count} / {len(files)}", True, TEXT_COLOR)
                self.screen.blit(txt, (self.width//2 - 50, self.height//2))
                pygame.display.flip()
            
        self.loading = False
        print("Loading complete.")

    def save_tags_file(self):
        data = {}
        for item in self.items:
            if not item.is_placeholder and item.path:
                fname = os.path.basename(item.path)
                if item.tags:
                     data[fname] = list(item.tags)
        
        with open(TAGS_FILE, 'w') as f:
            json.dump(data, f, indent=2)

    # --- Actions ---

    def add_placeholder(self):
        item = ComponentItem(None)
        item.load_image()
        # Insert after last selection or at end
        if self.selected_indices:
            idx = max(self.selected_indices)
            self.items.insert(idx + 1, item)
        else:
            self.items.append(item)

    def delete_selected(self):
        backup_dir = os.path.join(SOURCE_DIR, "Backup")
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)

        # Delete in reverse order to preserve indices
        for idx in sorted(list(self.selected_indices), reverse=True):
            if idx < len(self.items):
                item = self.items[idx]
                
                # Move to backup
                if item.path and os.path.exists(item.path):
                    try:
                        fname = os.path.basename(item.path)
                        dst = os.path.join(backup_dir, fname)
                        if os.path.exists(dst):
                            name, ext = os.path.splitext(fname)
                            dst = os.path.join(backup_dir, f"{name}_{uuid.uuid4().hex[:8]}{ext}")
                        
                        shutil.move(item.path, dst)
                        print(f"Moved {fname} to Backup")
                    except Exception as e:
                        print(f"Error moving {item.path} to backup: {e}")
                
                self.items.pop(idx)
                
        self.selected_indices.clear()
        self.last_selected_index = None

    def add_tag_from_input(self):
        tag = self.tag_input.text.strip()
        if tag:
            self.add_tag_to_selection(tag)
            self.tag_input.clear()

    def add_tag_to_selection(self, tag):
        if not self.selected_indices:
            return
        
        for idx in self.selected_indices:
            if idx < len(self.items):
                self.items[idx].tags.add(tag)
        
        self.all_tags.add(tag)
        self.save_tags_file()

    def remove_tag_from_selection(self, tag):
        if not self.selected_indices:
            return
        for idx in self.selected_indices:
            if idx < len(self.items):
                if tag in self.items[idx].tags:
                    self.items[idx].tags.remove(tag)
        self.save_tags_file()
        
    def delete_tag_globally(self, tag):
        if tag in self.all_tags:
            self.all_tags.remove(tag)
        
        for item in self.items:
            if tag in item.tags:
                item.tags.remove(tag)
        self.save_tags_file()

    def clear_filters(self):
        self.active_filters.clear()

    def toggle_filter(self, tag):
        if tag in self.active_filters:
            self.active_filters.remove(tag)
        else:
            self.active_filters.add(tag)

    def process_and_save(self):
        if self.active_filters:
            print("Cannot process while filters are active! clear filters first.")
            return
            
        print("Processing...")
        MAP_COLS = 24
        MAP_ROWS = math.ceil(len(self.items) / MAP_COLS)
        
        map_width = MAP_COLS * EXPORT_TILE_SIZE
        map_height = MAP_ROWS * EXPORT_TILE_SIZE
        
        tilemap_surf = pygame.Surface((map_width, map_height))
        tilemap_surf.fill((0,0,0))
        
        font_overlay = pygame.font.SysFont("Arial", 40, bold=True)
        def draw_text_with_outline(surf, text, x, y, font):
            s_black = font.render(text, True, (0,0,0))
            s_white = font.render(text, True, (255,255,255))
            for dx, dy in [(-2,-2),(-2,2),(2,-2),(2,2),(0,2),(0,-2),(2,0),(-2,0)]:
                 surf.blit(s_black, (x+dx, y+dy))
            surf.blit(s_white, (x, y))

        # Ensure Backup dir exists for rogue files
        backup_dir = os.path.join(SOURCE_DIR, "Backup")
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)

        temp_renames = [] 
        new_tag_data = {}
        
        for i, item in enumerate(self.items):
            row = i // MAP_COLS
            col = i % MAP_COLS
            dest_x = col * EXPORT_TILE_SIZE
            dest_y = row * EXPORT_TILE_SIZE
            
            tilemap_surf.blit(item.export_surface, (dest_x, dest_y))
            draw_text_with_outline(tilemap_surf, str(i), dest_x + 5, dest_y + 5, font_overlay)
            
            new_name = f"2048Portrait_Comp_{i:03d}.jpg"
            
            if item.is_placeholder:
                unique_ph_name = f"TEMP_PH_{uuid.uuid4()}.jpg"
                unique_ph_path = os.path.join(SOURCE_DIR, unique_ph_name)
                
                if not getattr(self, '_cached_ph_surf', None):
                    self._cached_ph_surf = pygame.Surface((2048, 2048))
                    self._cached_ph_surf.fill((0,0,0))
                    pygame.draw.line(self._cached_ph_surf, (20,20,20), (0,0), (2048, 2048), 10)
                    pygame.draw.line(self._cached_ph_surf, (20,20,20), (2048,0), (0, 2048), 10)
                
                pygame.image.save(self._cached_ph_surf, unique_ph_path)
                
                temp_renames.append((unique_ph_path, new_name))

            elif item.path:
                temp_renames.append((item.path, new_name))
                if item.tags:
                    new_tag_data[new_name] = list(item.tags)
        
        tilemap_path = os.path.join(SOURCE_DIR, "Component_Tilemap.jpg")
        pygame.image.save(tilemap_surf, tilemap_path)
        
        # Rename logic
        # 1. Rename ALL tracked items to Temp first.
        temp_map = {}
        
        for old_path, new_name in temp_renames:
             # Always rename to temp to clear the namespace
            temp_name = f"TEMP_{uuid.uuid4()}.jpg"
            temp_full = os.path.join(SOURCE_DIR, temp_name)
            try:
                os.rename(old_path, temp_full)
                temp_map[temp_full] = os.path.join(SOURCE_DIR, new_name)
                
                # Update item path in memory
                for it in self.items:
                    if it.path == old_path:
                        it.path = str(temp_full) 
                        break
            except Exception as e:
                print(f"Error renaming {old_path} to temp: {e}")

        # 2. CLEAR ROGUE FILES
        # Now that all our valid items are named TEMP_..., 
        # any file matching 2048Portrait_Comp_XXX.jpg is a rogue/ghost file.
        rogue_pattern = os.path.join(SOURCE_DIR, "2048Portrait_Comp_*.jpg")
        rogue_files = glob.glob(rogue_pattern)
        for rf in rogue_files:
            try:
                fname = os.path.basename(rf)
                dst = os.path.join(backup_dir, f"ROGUE_{fname}")
                if os.path.exists(dst):
                     dst = os.path.join(backup_dir, f"ROGUE_{uuid.uuid4().hex[:4]}_{fname}")
                shutil.move(rf, dst)
                print(f"Moved rogue file {fname} to Backup")
            except Exception as e:
                print(f"Error moving rogue file {rf}: {e}")
        
        # 3. Rename Temp to Final
        for temp_path, final_path in temp_map.items():
            try:
                os.rename(temp_path, final_path)
                
                for it in self.items:
                    if it.path == temp_path:
                        it.path = final_path
                        if it.is_placeholder:
                            it.is_placeholder = False
                            
            except Exception as e:
                print(f"Error renaming final to {final_path}: {e}")
                
        # Reload to ensure consistency
        self.items = []
        self.load_files()
                
        with open(TAGS_FILE, 'w') as f:
            json.dump(new_tag_data, f, indent=2)

        print("Processing complete.")

    def get_visible_items(self):
        if not self.active_filters:
            if self.is_dragging:
                return [(i, item) for i, item in enumerate(self.items) if item not in self.dragged_items]
            return [(i, item) for i, item in enumerate(self.items)]
        
        filtered = []
        for i, item in enumerate(self.items):
            if self.active_filters.issubset(item.tags):
                filtered.append((i, item))
        return filtered

    def get_index_at_pos(self, pos, current_layout_items):
        mx, my = pos
        adj_y = my - self.grid_start_y + self.scroll_y
        
        if mx < self.grid_start_x: return None
        
        col = (mx - self.grid_start_x) // (TILE_SIZE + self.grid_spacing)
        row = adj_y // (TILE_SIZE + self.grid_spacing)
        
        if 0 <= col < self.grid_cols and row >= 0:
            idx = row * self.grid_cols + col
            if 0 <= idx <= len(current_layout_items):
                return idx
        return None

    def run(self):
        self.load_files()
        
        running = True
        while running:
            # Current layout items are what we render. 
            visible_layout_items = self.get_visible_items()
            
            # Events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                elif event.type == pygame.VIDEORESIZE:
                    self.width = event.w
                    self.height = event.h
                    self.screen = pygame.display.set_mode((self.width, self.height), pygame.RESIZABLE)
                    self.recalc_layout()

                # Text Input
                if self.tag_input.handle_event(event):
                    self.add_tag_from_input()
                
                # Buttons
                handled = False
                for btn in self.buttons:
                    if btn.handle_event(event):
                        handled = True
                        break
                if handled: continue
                
                # Mouse events
                if event.type == pygame.MOUSEBUTTONDOWN:
                     mx, my = event.pos
                     
                     if event.button == 1 and mx < SIDEBAR_WIDTH:
                         focus_items = self.dragged_items if self.is_dragging else [self.items[i] for i in self.selected_indices if i < len(self.items)]
                         
                         common_tags = set()
                         if focus_items:
                            first = True
                            for item in focus_items:
                                if first: 
                                    common_tags = set(item.tags)
                                    first = False
                                else:
                                    common_tags &= item.tags
                         
                         y_tag = 350
                         for t in sorted(list(common_tags)):
                             x_chk_rect = pygame.Rect(30, y_tag, 20, 18)
                             if x_chk_rect.collidepoint(mx, my):
                                 self.remove_tag_from_selection(t)
                                 break
                             y_tag += 20
                         
                         y_filter = 600
                         sorted_tags = sorted(list(self.all_tags))
                         for t in sorted_tags:
                             row_rect = pygame.Rect(20, y_filter, SIDEBAR_WIDTH-40, 22)
                             
                             if row_rect.collidepoint(mx, my):
                                 btn_w = 25
                                 x_del = row_rect.right - btn_w
                                 x_sub = x_del - btn_w
                                 x_add = x_sub - btn_w
                                 
                                 if mx > x_del:
                                     self.delete_tag_globally(t)
                                     break
                                 elif mx > x_sub:
                                     self.remove_tag_from_selection(t)
                                     break
                                 elif mx > x_add:
                                     self.add_tag_to_selection(t)
                                     break
                                 else:
                                     self.toggle_filter(t)
                                     break
                             
                             y_filter += 24
                             if y_filter > self.height - 20: break

                     else:
                         clicked_layout_idx = self.get_index_at_pos(event.pos, visible_layout_items)
                         
                         if clicked_layout_idx is not None and clicked_layout_idx < len(visible_layout_items):
                             real_index, clicked_item = visible_layout_items[clicked_layout_idx]
                         else:
                             clicked_item = None
                             real_index = None

                         if clicked_item:
                             if event.button == 1:
                                 keys = pygame.key.get_pressed()
                                 ctrl_held = keys[pygame.K_LCTRL] or keys[pygame.K_RCTRL]
                                 shift_held = keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]
                                 
                                 if shift_held and self.last_selected_index is not None:
                                     start_pos = -1
                                     for i, (ridx, item) in enumerate(visible_layout_items):
                                         if ridx == self.last_selected_index:
                                             start_pos = i
                                             break
                                     
                                     if start_pos != -1:
                                         pos_min = min(start_pos, clicked_layout_idx)
                                         pos_max = max(start_pos, clicked_layout_idx)
                                         if not ctrl_held:
                                             self.selected_indices.clear()
                                         for k in range(pos_min, pos_max + 1):
                                             self.selected_indices.add(visible_layout_items[k][0])
                                 
                                 elif ctrl_held:
                                     if real_index in self.selected_indices:
                                         self.selected_indices.remove(real_index)
                                     else:
                                         self.selected_indices.add(real_index)
                                     self.last_selected_index = real_index
                                     
                                 else:
                                     self.selected_indices = {real_index}
                                     self.last_selected_index = real_index

                             elif event.button == 3:
                                 if not self.active_filters:
                                     if real_index not in self.selected_indices:
                                         self.selected_indices = {real_index}
                                         self.last_selected_index = real_index
                                     
                                     self.is_dragging = True
                                     self.dragged_items = []
                                     for idx in self.selected_indices:
                                         if idx < len(self.items):
                                             self.dragged_items.append(self.items[idx])
                                     
                                     self.drag_leader_idx = real_index
                                     if clicked_item.rect:
                                         self.drag_offset_x = clicked_item.rect.x - event.pos[0]
                                         self.drag_offset_y = clicked_item.rect.y - event.pos[1]

                     if event.button == 4: # Scroll Up
                         self.scroll_y = max(0, self.scroll_y - 50)
                     elif event.button == 5: # Scroll Down
                         self.scroll_y += 50
                         
                elif event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 3: # RIGHT RELEASE -> DROP
                        if self.is_dragging:
                            layout_drop_idx = self.get_index_at_pos(event.pos, visible_layout_items)
                            
                            if layout_drop_idx is not None:
                                remaining_items = [item for (ridx, item) in visible_layout_items]
                                final_new_items = remaining_items[:layout_drop_idx] + self.dragged_items + remaining_items[layout_drop_idx:]
                                self.items = final_new_items
                                
                                self.selected_indices.clear()
                                start_new_idx = len(remaining_items[:layout_drop_idx])
                                for k in range(len(self.dragged_items)):
                                    self.selected_indices.add(start_new_idx + k)
                            
                            self.is_dragging = False
                            self.dragged_items = []
                            self.target_insert_index = None

                elif event.type == pygame.MOUSEMOTION:
                    if self.is_dragging:
                        self.target_insert_index = self.get_index_at_pos(event.pos, visible_layout_items)

            # --- Drawing ---
            
            self.screen.fill(BG_COLOR)
            
            # 1. Grid Area
            total_rows = math.ceil(len(visible_layout_items) / self.grid_cols)
            content_height = total_rows * (TILE_SIZE + self.grid_spacing)
            items_height_visible = self.height - 40
            
            if content_height < items_height_visible:
                pass
            else:
                self.scroll_y = max(0, min(self.scroll_y, content_height - items_height_visible + 100))

            start_row = self.scroll_y // (TILE_SIZE + self.grid_spacing)
            end_row = (self.scroll_y + self.height) // (TILE_SIZE + self.grid_spacing) + 1
            
            start_layout_idx = start_row * self.grid_cols
            end_layout_idx = min(len(visible_layout_items), end_row * self.grid_cols)
            
            for i in range(start_layout_idx, end_layout_idx):
                real_idx_if_not_dragging, item = visible_layout_items[i] 
                
                col = i % self.grid_cols
                row = i // self.grid_cols
                x = self.grid_start_x + col * (TILE_SIZE + self.grid_spacing)
                y = self.grid_start_y + row * (TILE_SIZE + self.grid_spacing) - self.scroll_y
                
                if y + TILE_SIZE < 0 or y > self.height: continue
                
                item.rect = pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)
                
                if not self.is_dragging:
                    if real_idx_if_not_dragging in self.selected_indices:
                        color = HIGHLIGHT_COLOR if len(self.selected_indices) == 1 else MULTI_SELECT_COLOR
                        pygame.draw.rect(self.screen, color, (x-4, y-4, TILE_SIZE+8, TILE_SIZE+8))
                
                if item.surface:
                    self.screen.blit(item.surface, (x, y))
                
                idx_display = i 
                idx_surf = self.font.render(str(idx_display), True, (255, 255, 0))
                pygame.draw.rect(self.screen, (0,0,0), (x, y, idx_surf.get_width()+4, idx_surf.get_height()+2))
                self.screen.blit(idx_surf, (x+2, y+1))
                
                if item.tags:
                     pygame.draw.circle(self.screen, ACTIVE_TAG_COLOR, (x + TILE_SIZE - 10, y + 10), 6)
                     
                if self.is_dragging and self.target_insert_index == i:
                     pygame.draw.rect(self.screen, (255, 255, 255), (x-8, y, 6, TILE_SIZE))
            
            if self.is_dragging and self.target_insert_index == len(visible_layout_items):
                 if visible_layout_items:
                     last_i = len(visible_layout_items)
                     col = last_i % self.grid_cols
                     row = last_i // self.grid_cols
                     x = self.grid_start_x + col * (TILE_SIZE + self.grid_spacing)
                     y = self.grid_start_y + row * (TILE_SIZE + self.grid_spacing) - self.scroll_y
                     pygame.draw.rect(self.screen, (255, 255, 255), (x-8, y, 6, TILE_SIZE))
                 else:
                     pygame.draw.rect(self.screen, (255, 255, 255), (self.grid_start_x, self.grid_start_y, 6, TILE_SIZE))


            # 2. Draw Sidebar
            pygame.draw.rect(self.screen, SIDEBAR_COLOR, (0, 0, SIDEBAR_WIDTH, self.height))
            
            for btn in self.buttons:
                btn.draw(self.screen, self.font)
            self.tag_input.draw(self.screen)
            
            labels = [
                (180, f"Sel: {len(self.selected_indices)}"),
                (320, "Selected Tags:"),
                (570, "All Tags / Filters:")
            ]
            for y, text in labels:
                 if text:
                     surf = self.title_font.render(text, True, TEXT_COLOR)
                     self.screen.blit(surf, (20, y))
            
            focus_items = self.dragged_items if self.is_dragging else [self.items[i] for i in self.selected_indices if i < len(self.items)]
            
            if focus_items:
                common_tags = set()
                first = True
                for item in focus_items:
                    if first: 
                        common_tags = set(item.tags)
                        first = False
                    else:
                        common_tags &= item.tags
                
                y_tag = 350
                for t in sorted(list(common_tags)):
                     x_rect = pygame.Rect(30, y_tag+2, 16, 16)
                     pygame.draw.rect(self.screen, (150, 50, 50), x_rect, border_radius=3)
                     
                     surf = self.small_font.render(f"    {t}", True, (150, 255, 150))
                     self.screen.blit(surf, (30, y_tag))
                     y_tag += 20

            # Tags List
            y_filter = 600
            sorted_all_tags = sorted(list(self.all_tags))
            for t in sorted_all_tags:
                is_active = t in self.active_filters
                color = ACTIVE_TAG_COLOR if is_active else (100, 100, 100)
                text_col = (255, 255, 255) if is_active else (180, 180, 180)
                
                r = pygame.Rect(20, y_filter, SIDEBAR_WIDTH-40, 22)
                pygame.draw.rect(self.screen, color, r, border_radius=4)
                
                surf = self.small_font.render(t, True, text_col)
                self.screen.set_clip(pygame.Rect(25, y_filter, 150, 22))
                self.screen.blit(surf, (25, y_filter + 2))
                self.screen.set_clip(None)
                
                btn_w = 25
                x_base = r.right
                
                rect_del = pygame.Rect(x_base - btn_w, y_filter, btn_w, 22)
                pygame.draw.rect(self.screen, (180, 60, 60), rect_del)
                d_surf = self.small_font.render("x", True, (255,255,255))
                self.screen.blit(d_surf, (rect_del.x + 8, rect_del.y + 2))

                rect_sub = pygame.Rect(x_base - btn_w*2, y_filter, btn_w, 22)
                pygame.draw.rect(self.screen, (150, 150, 60), rect_sub)
                m_surf = self.small_font.render("-", True, (255,255,255))
                self.screen.blit(m_surf, (rect_sub.x + 8, rect_sub.y + 2))

                rect_add = pygame.Rect(x_base - btn_w*3, y_filter, btn_w, 22)
                pygame.draw.rect(self.screen, (60, 150, 60), rect_add)
                p_surf = self.small_font.render("+", True, (255,255,255))
                self.screen.blit(p_surf, (rect_add.x + 7, rect_add.y + 2))
                
                pygame.draw.line(self.screen, (30,30,30), (rect_add.right, y_filter), (rect_add.right, y_filter+22))
                pygame.draw.line(self.screen, (30,30,30), (rect_sub.right, y_filter), (rect_sub.right, y_filter+22))

                y_filter += 24
                if y_filter > self.height - 20: break

            if self.is_dragging and self.dragged_items:
                mx, my = pygame.mouse.get_pos()
                
                count = len(self.dragged_items)
                stack_limit = min(count, 3) 
                
                for s in range(stack_limit - 1, -1, -1):
                    off = s * 5
                    preview_item = self.dragged_items[0]
                    dest_x = mx + self.drag_offset_x - off
                    dest_y = my + self.drag_offset_y - off
                    
                    pygame.draw.rect(self.screen, (50, 50, 50), (dest_x, dest_y, TILE_SIZE, TILE_SIZE))
                    if preview_item.surface:
                        self.screen.blit(preview_item.surface, (dest_x, dest_y))
                    
                    pygame.draw.rect(self.screen, border_radius=0, color=(255,255,255), rect=(dest_x, dest_y, TILE_SIZE, TILE_SIZE), width=1)
                
                if count > 1:
                    badge_surf = self.title_font.render(f"{count}", True, (255, 255, 255))
                    pygame.draw.circle(self.screen, (200, 50, 50), (mx + self.drag_offset_x + TILE_SIZE, my + self.drag_offset_y), 15)
                    br = badge_surf.get_rect(center=(mx + self.drag_offset_x + TILE_SIZE, my + self.drag_offset_y))
                    self.screen.blit(badge_surf, br)

            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    App().run()
