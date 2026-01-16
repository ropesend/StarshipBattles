"""
Exit confirmation dialog for the game application.

Handles drawing and click detection for the exit confirmation dialog.
"""
import pygame

# Dialog button rects (module-level for click detection)
_exit_yes_rect = None
_exit_no_rect = None


def draw_exit_dialog(screen, font_large, font_med):
    """
    Draw the exit confirmation dialog.

    Args:
        screen: Pygame screen surface
        font_large: Large font for title
        font_med: Medium font for buttons
    """
    global _exit_yes_rect, _exit_no_rect

    width, height = screen.get_size()

    # Darken background
    s = pygame.Surface((width, height), pygame.SRCALPHA)
    s.fill((0, 0, 0, 180))
    screen.blit(s, (0, 0))

    # Dialog box
    box_w, box_h = 400, 200
    box_x = (width - box_w) // 2
    box_y = (height - box_h) // 2
    box_rect = pygame.Rect(box_x, box_y, box_w, box_h)

    pygame.draw.rect(screen, (40, 40, 50), box_rect)
    pygame.draw.rect(screen, (100, 100, 120), box_rect, 2)

    # Title
    title = font_large.render("Exit Application?", True, (255, 255, 255))
    screen.blit(title, (box_x + (box_w - title.get_width()) // 2, box_y + 40))

    # Buttons
    btn_w, btn_h = 100, 40
    spacing = 40

    # Yes button
    yes_x = box_x + box_w // 2 - btn_w - spacing // 2
    yes_y = box_y + 120
    _exit_yes_rect = pygame.Rect(yes_x, yes_y, btn_w, btn_h)

    mx, my = pygame.mouse.get_pos()
    yes_col = (180, 60, 60) if _exit_yes_rect.collidepoint(mx, my) else (150, 50, 50)

    pygame.draw.rect(screen, yes_col, _exit_yes_rect)
    pygame.draw.rect(screen, (200, 100, 100), _exit_yes_rect, 1)
    yes_txt = font_med.render("Yes", True, (255, 255, 255))
    screen.blit(yes_txt, (yes_x + (btn_w - yes_txt.get_width()) // 2, yes_y + 8))

    # No button
    no_x = box_x + box_w // 2 + spacing // 2
    no_y = box_y + 120
    _exit_no_rect = pygame.Rect(no_x, no_y, btn_w, btn_h)

    no_col = (60, 60, 80) if _exit_no_rect.collidepoint(mx, my) else (50, 50, 60)

    pygame.draw.rect(screen, no_col, _exit_no_rect)
    pygame.draw.rect(screen, (100, 100, 150), _exit_no_rect, 1)
    no_txt = font_med.render("No", True, (255, 255, 255))
    screen.blit(no_txt, (no_x + (btn_w - no_txt.get_width()) // 2, no_y + 8))


def handle_exit_dialog_click(pos):
    """
    Check if click was on Yes button.

    Args:
        pos: Mouse position tuple (x, y)

    Returns:
        True if Yes was clicked
    """
    if _exit_yes_rect and _exit_yes_rect.collidepoint(pos):
        return True
    return False


def handle_exit_dialog_cancel(pos):
    """
    Check if click was on No button.

    Args:
        pos: Mouse position tuple (x, y)

    Returns:
        True if No was clicked
    """
    if _exit_no_rect and _exit_no_rect.collidepoint(pos):
        return True
    return False
