"""Modal "processing turn" overlay (PROJ-309 sub-phase 3.2)."""
from __future__ import annotations

from typing import Any, Callable

import pygame

from game.ui.colors import OVERLAY_PROCESSING


def draw_processing_overlay(
    screen: Any,
    font_provider: Callable[[int, bool], Any],
    message: str = "PROCESSING TURN...",
    *,
    current_tick: int | None = None,
    total_ticks: int | None = None,
) -> None:
    """Draw a modal overlay for turn processing.

    Args:
        screen: The pygame surface to draw onto.
        font_provider: Callable returning a font for (size, bold).
        message: Optional override text. Defaults to "PROCESSING TURN...".
            FEAT-20 callers (dev `run_n_turns`) pass progress text such as
            "PROCESSING TURN 3 / 10... (Esc to cancel)".
        current_tick: Issue #7 — when both ``current_tick`` and ``total_ticks``
            are non-None, a smaller secondary line ``Tick N / M`` is rendered
            below the main label so the player can see live tick progress.
            Size 28 non-bold (vs the 48-bold main label) — chosen to mirror
            the font_size / small_size hierarchy used elsewhere in the renderer.
        total_ticks: See ``current_tick``.
    """
    overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 150))
    screen.blit(overlay, (0, 0))

    cx = screen.get_width() // 2
    cy = screen.get_height() // 2

    main_font = font_provider(48, True)
    main_text = main_font.render(message, True, OVERLAY_PROCESSING)
    main_rect = main_text.get_rect(center=(cx, cy))
    screen.blit(main_text, main_rect)

    if current_tick is not None and total_ticks is not None:
        sub_font = font_provider(28, False)
        sub_text = sub_font.render(
            f"Tick {current_tick} / {total_ticks}", True, OVERLAY_PROCESSING
        )
        sub_rect = sub_text.get_rect(center=(cx, main_rect.bottom + 24))
        screen.blit(sub_text, sub_rect)
