"""Modal "processing turn" overlay (PROJ-309 sub-phase 3.2)."""
from __future__ import annotations

from typing import Any, Callable

import pygame

from game.ui.colors import OVERLAY_PROCESSING


def draw_processing_overlay(screen: Any, font_provider: Callable[[int, bool], Any]) -> None:
    """Draw a modal overlay for turn processing."""
    overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 150))
    screen.blit(overlay, (0, 0))

    font = font_provider(48, True)
    text = font.render("PROCESSING TURN...", True, OVERLAY_PROCESSING)
    rect = text.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2))
    screen.blit(text, rect)
