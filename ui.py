import pygame

class Button:
    def __init__(self, x, y, w, h, text, callback, color=(100, 100, 100), hover_color=(150, 150, 150)):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.callback = callback
        self.color = color
        self.hover_color = hover_color
        self.is_hovered = False
        self.font = pygame.font.SysFont("Arial", 20)

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.is_hovered and self.callback:
                self.callback()

    def draw(self, surface):
        color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(surface, color, self.rect)
        pygame.draw.rect(surface, (255, 255, 255), self.rect, 2)
        
        text_surf = self.font.render(self.text, True, (255, 255, 255))
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

class Label:
    def __init__(self, x, y, text, font_size=20, color=(255, 255, 255)):
        self.pos = (x, y)
        self.text = text
        self.font = pygame.font.SysFont("Arial", font_size)
        self.color = color

    def update_text(self, text):
        self.text = text

    def draw(self, surface):
        surf = self.font.render(self.text, True, self.color)
        surface.blit(surf, self.pos)

class Slider:
    def __init__(self, x, y, w, h, min_val, max_val, initial_val, callback):
        self.rect = pygame.Rect(x, y, w, h)
        self.min_val = min_val
        self.max_val = max_val
        self.val = initial_val
        self.callback = callback
        self.handle_w = 20
        self.is_dragging = False
        
    def get_handle_rect(self):
        # Map val to x position
        ratio = (self.val - self.min_val) / (self.max_val - self.min_val) if self.max_val > self.min_val else 0
        handle_x = self.rect.x + ratio * (self.rect.w - self.handle_w)
        return pygame.Rect(int(handle_x), self.rect.y, self.handle_w, self.rect.h)
        
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            handle = self.get_handle_rect()
            if handle.collidepoint(event.pos) or self.rect.collidepoint(event.pos):
                self.is_dragging = True
                self.update_val(event.pos[0])
                
        elif event.type == pygame.MOUSEBUTTONUP:
            self.is_dragging = False
            
        elif event.type == pygame.MOUSEMOTION:
            if self.is_dragging:
                self.update_val(event.pos[0])
                
    def update_val(self, mouse_x):
        # Clamp x to rect
        x = max(self.rect.x, min(self.rect.x + self.rect.w - self.handle_w, mouse_x))
        # Inverse map
        ratio = (x - self.rect.x) / (self.rect.w - self.handle_w)
        new_val = self.min_val + ratio * (self.max_val - self.min_val)
        
        if new_val != self.val:
            self.val = new_val
            if self.callback:
                self.callback(self.val)

    def draw(self, surface):
        # Track
        pygame.draw.rect(surface, (100, 100, 100), self.rect)
        # Handle
