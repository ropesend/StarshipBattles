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
