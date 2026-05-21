"""
Exit confirmation dialog for the game application.

Handles drawing and click detection for the exit confirmation dialog.

PROJ-471 Task 2.13: button rects are owned per-instance by ``ExitDialog``
rather than as module-level mutable globals. Each dialog instance keeps its
own click-target state, so there is no shared module state to leak between
windows or tests.
"""
from __future__ import annotations

from typing import Any

import pygame


class ExitDialog:
    """Modal exit-confirmation dialog with per-instance button click targets.

    ``draw()`` recomputes the Yes/No button rects each frame (they depend on
    the current screen size) and stores them on the instance. ``handle_click``
    / ``handle_cancel`` test the most recently drawn rects.
    """

    def __init__(self) -> None:
        self._yes_rect: Any | None = None
        self._no_rect: Any | None = None

    def draw(self, screen: Any, font_large: Any, font_med: Any) -> None:
        """Draw the exit confirmation dialog and update button rects.

        Args:
            screen: Pygame screen surface
            font_large: Large font for title
            font_med: Medium font for buttons
        """
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
        self._yes_rect = pygame.Rect(yes_x, yes_y, btn_w, btn_h)

        mx, my = pygame.mouse.get_pos()
        yes_col = (180, 60, 60) if self._yes_rect.collidepoint(mx, my) else (150, 50, 50)

        pygame.draw.rect(screen, yes_col, self._yes_rect)
        pygame.draw.rect(screen, (200, 100, 100), self._yes_rect, 1)
        yes_txt = font_med.render("Yes", True, (255, 255, 255))
        screen.blit(yes_txt, (yes_x + (btn_w - yes_txt.get_width()) // 2, yes_y + 8))

        # No button
        no_x = box_x + box_w // 2 + spacing // 2
        no_y = box_y + 120
        self._no_rect = pygame.Rect(no_x, no_y, btn_w, btn_h)

        no_col = (60, 60, 80) if self._no_rect.collidepoint(mx, my) else (50, 50, 60)

        pygame.draw.rect(screen, no_col, self._no_rect)
        pygame.draw.rect(screen, (100, 100, 150), self._no_rect, 1)
        no_txt = font_med.render("No", True, (255, 255, 255))
        screen.blit(no_txt, (no_x + (btn_w - no_txt.get_width()) // 2, no_y + 8))

    def handle_click(self, pos: Any) -> bool:
        """Return True if ``pos`` falls on the Yes button.

        Args:
            pos: Mouse position tuple (x, y)
        """
        if self._yes_rect and self._yes_rect.collidepoint(pos):
            return True
        return False

    def handle_cancel(self, pos: Any) -> bool:
        """Return True if ``pos`` falls on the No button.

        Args:
            pos: Mouse position tuple (x, y)
        """
        if self._no_rect and self._no_rect.collidepoint(pos):
            return True
        return False
