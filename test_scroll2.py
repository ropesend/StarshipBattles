import pygame
import pygame_gui
import pygame_gui.elements as ui

pygame.init()
window_surface = pygame.display.set_mode((1920, 1080))
manager = pygame_gui.UIManager((1920, 1080))

background = ui.UIPanel(relative_rect=pygame.Rect(0, 0, 1920, 1080), manager=manager)

panel_y = 10 + 350 + 10 + 600 + 10
panel_height = 1080 - panel_y - 80

panel = ui.UIPanel(
    relative_rect=pygame.Rect(10, panel_y, 600, panel_height),
    manager=manager,
    container=background
)

scrollable = ui.UIScrollingContainer(
    relative_rect=pygame.Rect(5, 45, 600 - 10, panel_height - 55),
    manager=manager,
    container=panel
)

print(f"Panel height: {panel_height}, Scrollable height: {panel_height - 55}")

try:
    scrollable.set_scrollable_area_dimensions((590, 800)) # Force vertical scrollbar
    print("Success!")
except Exception as e:
    print(f"Crash: {e}")
