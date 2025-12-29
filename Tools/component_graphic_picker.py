import pygame
import json
import os
import math
import sys

# --- Constants ---
WINDOW_WIDTH = 1400
WINDOW_HEIGHT = 900
BG_COLOR = (30, 30, 30)
TEXT_COLOR = (220, 220, 220)
HIGHLIGHT_COLOR = (70, 70, 120)
ROW_BG_COLOR = (45, 45, 45)
ROW_HEIGHT = 140
IMG_PREVIEW_SIZE = 128
PICKER_TILE_SIZE = 128
PICKER_GAP = 10

BASE_DIR = r"C:\Dev\Starship Battles"
COMPONENTS_JSON = os.path.join(BASE_DIR, "data", "components.json")
IMAGES_DIR = os.path.join(BASE_DIR, "Resources", "Images", "Components", "Components 512")

# --- Helper Classes ---

class Button:
    def __init__(self, rect, text, callback, color=(60, 60, 60), hover_color=(80, 80, 80), text_color=TEXT_COLOR):
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

class ComponentRow:
    def __init__(self, data, font):
        self.data = data
        self.id = data.get("id", "Unknown")
        self.name = data.get("name", "Unknown")
        self.sprite_index = data.get("sprite_index", 0)
        self.font = font
        self.rect = None # Set by layout
        self.surface = None
        self.load_image()

    def load_image(self):
        # Format: 2048Portrait_Comp_{i:03d}.jpg
        # SpriteManager aligns Comp_001 to index 0.
        # So index X corresponds to file X+1.
        filename = f"2048Portrait_Comp_{self.sprite_index + 1:03d}.jpg"
        path = os.path.join(IMAGES_DIR, filename)
        
        self.surface = pygame.Surface((IMG_PREVIEW_SIZE, IMG_PREVIEW_SIZE))
        self.surface.fill((0,0,0))
        
        if os.path.exists(path):
            try:
                img = pygame.image.load(path)
                self.surface = pygame.transform.smoothscale(img, (IMG_PREVIEW_SIZE, IMG_PREVIEW_SIZE))
            except Exception as e:
                print(f"Error loading {path}: {e}")
        else:
            # Draw placeholder X
            pygame.draw.line(self.surface, (255,0,0), (0,0), (IMG_PREVIEW_SIZE, IMG_PREVIEW_SIZE), 2)
            pygame.draw.line(self.surface, (255,0,0), (IMG_PREVIEW_SIZE,0), (0, IMG_PREVIEW_SIZE), 2)

    def draw(self, screen, x, y, width, is_hovered):
        self.rect = pygame.Rect(x, y, width, ROW_HEIGHT)
        
        bg = HIGHLIGHT_COLOR if is_hovered else ROW_BG_COLOR
        pygame.draw.rect(screen, bg, self.rect, border_radius=5)
        
        # Image
        screen.blit(self.surface, (x + 10, y + (ROW_HEIGHT - IMG_PREVIEW_SIZE)//2))
        
        # Text
        name_surf = self.font.render(f"{self.name}", True, (255, 255, 255))
        id_surf = self.font.render(f"ID: {self.id}", True, (180, 180, 180))
        idx_surf = self.font.render(f"Sprite Index: {self.sprite_index}", True, (150, 200, 255))
        
        tx = x + 10 + IMG_PREVIEW_SIZE + 20
        screen.blit(name_surf, (tx, y + 20))
        screen.blit(id_surf, (tx, y + 55))
        screen.blit(idx_surf, (tx, y + 90))

class ImagePicker:
    def __init__(self, callback_select, callback_cancel):
        self.callback_select = callback_select
        self.callback_cancel = callback_cancel
        self.scroll_y = 0
        self.images = [] # (index, surface)
        self.load_images()
        self.highlight_index = 0 # Index in self.images
        
    def load_images(self):
        # Scan directory for all valid images
        print("Loading picker images...")
        files = os.listdir(IMAGES_DIR)
        files.sort()
        
        for f in files:
            if f.startswith("2048Portrait_Comp_") and f.endswith(".jpg"):
                try:
                    # Extract index
                    # 2048Portrait_Comp_085.jpg -> 85
                    # SpriteManager logic: Index = FileNum - 1
                    part = f.replace("2048Portrait_Comp_", "").replace(".jpg", "")
                    file_num = int(part)
                    idx = file_num - 1
                    
                    if idx < 0: continue
                    
                    path = os.path.join(IMAGES_DIR, f)
                    # Load small version for performance? 
                    # They are already "512" (named 2048 but in 512 folder), but scaling down 512 to 128 is fine.
                    img = pygame.image.load(path)
                    surf = pygame.transform.smoothscale(img, (PICKER_TILE_SIZE, PICKER_TILE_SIZE))
                    self.images.append((idx, surf))
                except Exception as e:
                    print(f"Skipping {f}: {e}")
        print(f"Loaded {len(self.images)} images for picker.")

    def ensure_visible(self, index, cols, frame_h):
        # Scroll to make sure index is visible
        row = index // cols
        tile_h = PICKER_TILE_SIZE + PICKER_GAP
        y_pos = row * tile_h
        
        if y_pos < self.scroll_y:
            self.scroll_y = y_pos
        elif y_pos + tile_h > self.scroll_y + frame_h:
            self.scroll_y = y_pos + tile_h - frame_h

    def draw_and_handle(self, screen, events, width, height):
        # Draw overlay bg
        overlay = pygame.Surface((width, height))
        overlay.fill((20, 20, 20))
        overlay.set_alpha(240)
        screen.blit(overlay, (0,0))
        
        # Title
        font = pygame.font.SysFont("Arial", 24, bold=True)
        title = font.render("Select New Graphic (Arrows to move, Space/Enter to select, ESC to cancel)", True, (255, 255, 255))
        screen.blit(title, (width//2 - title.get_width()//2, 20))

        # Grid calc
        frame_x = 50
        frame_y = 70
        frame_w = width - 100
        frame_h = height - 100
        
        cols = max(1, frame_w // (PICKER_TILE_SIZE + PICKER_GAP))
        
        # Events for this modal
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.callback_cancel()
                elif event.key == pygame.K_LEFT:
                    self.highlight_index = max(0, self.highlight_index - 1)
                    self.ensure_visible(self.highlight_index, cols, frame_h)
                elif event.key == pygame.K_RIGHT:
                    self.highlight_index = min(len(self.images)-1, self.highlight_index + 1)
                    self.ensure_visible(self.highlight_index, cols, frame_h)
                elif event.key == pygame.K_UP:
                    self.highlight_index = max(0, self.highlight_index - cols)
                    self.ensure_visible(self.highlight_index, cols, frame_h)
                elif event.key == pygame.K_DOWN:
                    self.highlight_index = min(len(self.images)-1, self.highlight_index + cols)
                    self.ensure_visible(self.highlight_index, cols, frame_h)
                elif event.key in (pygame.K_SPACE, pygame.K_RETURN):
                    if 0 <= self.highlight_index < len(self.images):
                        real_idx, _ = self.images[self.highlight_index]
                        self.callback_select(real_idx)
                        
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 4: # Scroll Up
                    self.scroll_y = max(0, self.scroll_y - 50)
                elif event.button == 5: # Scroll Down
                    self.scroll_y += 50
                elif event.button == 1:
                    # Check click
                    mx, my = event.pos
                    # Adjust for scroll and offset
                    rel_x = mx - frame_x
                    rel_y = my - frame_y + self.scroll_y
                    
                    if 0 <= rel_x <= frame_w and 0 <= my >= frame_y:
                         c = rel_x // (PICKER_TILE_SIZE + PICKER_GAP)
                         r = rel_y // (PICKER_TILE_SIZE + PICKER_GAP)
                         
                         idx = r * cols + c
                         if 0 <= idx < len(self.images):
                              self.highlight_index = idx # Update highlight on click too
                              # Optional: Require double click? Or just space?
                              # Existing logic was click to select.
                              # Keeping click to select for consistency, unless user really hates it.
                              # But modifying to update highlight first.
                              real_idx, _ = self.images[idx]
                              self.callback_select(real_idx)

        # Draw Grid
        start_row = self.scroll_y // (PICKER_TILE_SIZE + PICKER_GAP)
        end_row = (self.scroll_y + frame_h) // (PICKER_TILE_SIZE + PICKER_GAP) + 1
        
        start_idx = start_row * cols
        end_idx = min(len(self.images), end_row * cols)
        
        font_small = pygame.font.SysFont("Arial", 12)
        
        for i in range(start_idx, end_idx):
            r_idx, surf = self.images[i]
            
            # Position
            c = i % cols
            r = i // cols
            
            x = frame_x + c * (PICKER_TILE_SIZE + PICKER_GAP)
            y = frame_y + r * (PICKER_TILE_SIZE + PICKER_GAP) - self.scroll_y
            
            if y + PICKER_TILE_SIZE < frame_y: continue
            if y > frame_y + frame_h: continue
            
            screen.blit(surf, (x, y))
            
            # Draw ID
            lbl = font_small.render(str(r_idx), True, (255, 255, 0))
            pygame.draw.rect(screen, (0,0,0), (x, y, lbl.get_width()+4, lbl.get_height()+2))
            screen.blit(lbl, (x+2, y+1))
            
            # Border
            color = (80, 80, 80)
            thick = 1
            if i == self.highlight_index:
                color = (0, 255, 0)
                thick = 3
                
            pygame.draw.rect(screen, color, (x, y, PICKER_TILE_SIZE, PICKER_TILE_SIZE), thick)

class App:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.RESIZABLE)
        pygame.display.set_caption("Component Graphic Picker")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Arial", 18)
        self.title_font = pygame.font.SysFont("Arial", 22, bold=True)
        
        self.rows = []
        self.scroll_y = 0
        self.json_data = None
        
        self.load_data()
        
        # State
        self.picking_mode = False
        self.picker = None
        self.selected_row = None
        self.just_entered_picking_mode = False # Flag to skip first frame events
        
        # Buttons
        self.btn_save = Button((WINDOW_WIDTH - 220, 20, 200, 40), "SAVE CHANGES", self.save_data, color=(30, 100, 30))
        
    def load_data(self):
        try:
            with open(COMPONENTS_JSON, 'r') as f:
                self.json_data = json.load(f)
                
            self.rows = []
            for comp in self.json_data.get("components", []):
                self.rows.append(ComponentRow(comp, self.font))
                
        except Exception as e:
            print(f"Failed to load JSON: {e}")

    def save_data(self):
        if not self.json_data: return
        
        # Sync rows back to json_data
        # Actually ComponentRow references the dictionary object directly, so self.json_data is already updated!
        # We just need to dump it.
        
        try:
            with open(COMPONENTS_JSON, 'w') as f:
                json.dump(self.json_data, f, indent=4)
            print("Saved components.json")
            
            # Flash effect or something?
            
        except Exception as e:
            print(f"Error saving: {e}")

    def on_image_selected(self, new_index):
        if self.selected_row:
            self.selected_row.sprite_index = new_index
            self.selected_row.data['sprite_index'] = new_index
            self.selected_row.load_image() # Reload preview
            
        self.picking_mode = False
        self.picker = None
        self.selected_row = None

    def on_picker_cancel(self):
        self.picking_mode = False
        self.picker = None
        self.selected_row = None

    def run(self):
        running = True
        while running:
            events = pygame.event.get()
            
            if self.picking_mode:
                if self.just_entered_picking_mode:
                    # Skip processing events this frame for the picker to avoid immediate closing
                    self.just_entered_picking_mode = False
                    # But we should still allow quitting if that was the event? 
                    # Generally safely ignoring one frame of inputs is fine.
                    pass
                else:
                    self.picker.draw_and_handle(self.screen, events, self.screen.get_width(), self.screen.get_height())
            else:
                for event in events:
                    if event.type == pygame.QUIT:
                        running = False
                    elif event.type == pygame.VIDEORESIZE:
                        self.screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
                        self.btn_save.rect.x = event.w - 220
                    
                    self.btn_save.handle_event(event)
                    
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if event.button == 4:
                            self.scroll_y = max(0, self.scroll_y - 50)
                        elif event.button == 5:
                            # Clamp?
                            total_h = len(self.rows) * (ROW_HEIGHT + 10) + 100
                            max_scroll = max(0, total_h - self.screen.get_height())
                            self.scroll_y = min(max_scroll, self.scroll_y + 50)
                            
                        elif event.button == 1:
                            # Check row clicks
                            mx, my = event.pos
                            # If not on button
                            if not self.btn_save.rect.collidepoint(mx, my):
                                # Find clicked row
                                list_y = 80 - self.scroll_y
                                for row in self.rows:
                                    r_rect = pygame.Rect(20, list_y, self.screen.get_width()-40, ROW_HEIGHT)
                                    if r_rect.collidepoint(mx, my):
                                        self.selected_row = row
                                        self.picking_mode = True
                                        self.just_entered_picking_mode = True
                                        self.picker = ImagePicker(self.on_image_selected, self.on_picker_cancel)
                                        break
                                    list_y += ROW_HEIGHT + 10
            
            # --- Draw ---
            if not self.picking_mode:
                self.screen.fill(BG_COLOR)
                self.draw_list()
                
                # Header always on top (unless picker covers it)
                pygame.draw.rect(self.screen, BG_COLOR, (0, 0, self.screen.get_width(), 80))
                title = self.title_font.render("Component Graphic Picker - Click a component to change graphic", True, TEXT_COLOR)
                self.screen.blit(title, (20, 25))
                self.btn_save.draw(self.screen, self.font)
            
            # If picking mode, the picker handles its own drawing in draw_and_handle
            # But wait, we just skipped draw_and_handle if just_entered_picking_mode is True.
            # We must still draw it!
            if self.picking_mode and self.just_entered_picking_mode:
                 self.picker.draw_and_handle(self.screen, [], self.screen.get_width(), self.screen.get_height())
                 
            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()
        sys.exit()

    def draw_list(self):
        start_y = 80 - self.scroll_y
        mx, my = pygame.mouse.get_pos()
        
        for row in self.rows:
            # Cull
            if start_y + ROW_HEIGHT < 0:
                start_y += ROW_HEIGHT + 10
                continue
            if start_y > self.screen.get_height():
                break
                
            w = self.screen.get_width() - 40
            
            if self.picking_mode:
                is_hovered = False
            else:
                 is_hovered = (20 <= mx <= 20+w) and (start_y <= my <= start_y + ROW_HEIGHT)
            
            row.draw(self.screen, 20, start_y, w, is_hovered)
            start_y += ROW_HEIGHT + 10

if __name__ == "__main__":
    app = App()
    app.run()
