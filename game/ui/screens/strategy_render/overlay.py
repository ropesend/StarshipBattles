"""Modal "processing turn" overlay (PROJ-309 sub-phase 3.2)."""
from __future__ import annotations

from typing import Any, Callable

import pygame

from game.ui.colors import OVERLAY_PROCESSING


def draw_processing_overlay(
    screen: Any,
    font_provider: Callable[[int, bool], Any],
    message: str = "PROCESSING TURN...",
) -> None:
    """Draw a modal overlay for turn processing.

    Args:
        screen: The pygame surface to draw onto.
        font_provider: Callable returning a font for (size, bold).
        message: Optional override text. Defaults to "PROCESSING TURN...".
            FEAT-20 callers (dev `run_n_turns`) pass progress text such as
            "PROCESSING TURN 3 / 10... (Esc to cancel)".
    """
    overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 150))
    screen.blit(overlay, (0, 0))

    font = font_provider(48, True)
    text = font.render(message, True, OVERLAY_PROCESSING)
    rect = text.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2))
    screen.blit(text, rect)
