import pygame
import pygame_gui
import pygame_gui.elements as ui

pygame.init()
window_surface = pygame.display.set_mode((800, 600))
manager = pygame_gui.UIManager((800, 600))

panel = ui.UIPanel(relative_rect=pygame.Rect(10, 10, 200, 200), manager=manager)
scrollable = ui.UIScrollingContainer(relative_rect=pygame.Rect(5, 5, 190, 190), manager=manager, container=panel)

# Add buttons
for i in range(10):
    ui.UIButton(relative_rect=pygame.Rect(0, i * 30, 150, 25), text=f"Btn {i}", manager=manager, container=scrollable)

# NOW set dimensions
scrollable.set_scrollable_area_dimensions((150, 300))
print("Success with buttons after!")
