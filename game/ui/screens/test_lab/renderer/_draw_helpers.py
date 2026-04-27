"""Visual draw primitives for Combat Lab renderer panels.

PROJ-309 sub-phase 3.3 — extracted from `renderer.py`. All helpers are
module-level functions taking primitive args (surface, font, x, y, …) so
sub-phase 3.6's `test_run_details/` subpackage can reuse them too.

Note: leading underscore on the module name signals "package-private —
imported only by sibling renderer panels."
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

import pygame

from game.ui.colors import TEST_PASS, TEST_FAIL, BLACK
from game.ui.screens.test_lab import theme
from game.core.config import DisplayConfig

from ._condition_logic import is_condition_verified

WIDTH, HEIGHT = DisplayConfig.DEFAULT_WIDTH, DisplayConfig.DEFAULT_HEIGHT

_TEXT_COLOR = theme.TEXT


def draw_section(
    screen: pygame.Surface,
    body_font: pygame.font.Font,
    small_font: pygame.font.Font,
    x: int,
    y: int,
    label: str,
    text: str,
    color: Tuple[int, int, int],
) -> int:
    """Draw a single-line metadata section."""
    # Label
    label_surf = body_font.render(f"{label}:", True, color)
    screen.blit(label_surf, (x, y))
    y += 25

    # Text
    text_surf = small_font.render(text, True, _TEXT_COLOR)
    screen.blit(text_surf, (x + 10, y))
    y += 22

    return y


def draw_section_wrapped(
    screen: pygame.Surface,
    body_font: pygame.font.Font,
    small_font: pygame.font.Font,
    x: int,
    y: int,
    label: str,
    text: str,
    color: Tuple[int, int, int],
    max_width: int,
) -> int:
    """Draw a metadata section with text wrapping."""
    # Label
    label_surf = body_font.render(f"{label}:", True, color)
    screen.blit(label_surf, (x, y))
    y += 25

    # Wrapped text
    y = draw_wrapped_text(screen, small_font, text, x + 10, y, max_width - 40, _TEXT_COLOR)
    y += 5

    return y


def draw_bullet_list(
    screen: pygame.Surface,
    body_font: pygame.font.Font,
    small_font: pygame.font.Font,
    x: int,
    y: int,
    label: str,
    items: List[str],
    color: Tuple[int, int, int],
    metadata_width: int,
    validation_results: Optional[List[Dict]] = None,
) -> int:
    """Draw a bullet list section with optional validation indicators."""
    # Label
    label_surf = body_font.render(f"{label}:", True, color)
    screen.blit(label_surf, (x, y))
    y += 25

    # Items
    if not items:
        none_surf = small_font.render("None", True, theme.TEXT_VERY_DIM)
        screen.blit(none_surf, (x + 20, y))
        y += 22
    else:
        for item in items:
            bullet_surf = small_font.render(f"* {item}", True, _TEXT_COLOR)
            screen.blit(bullet_surf, (x + 10, y))

            # Check if this item is verified by validation results
            if validation_results and is_condition_verified(item, validation_results):
                # Draw green "V" on right edge
                v_surf = body_font.render("V", True, TEST_PASS)
                v_x = x + metadata_width - 40  # Right edge with padding
                screen.blit(v_surf, (v_x, y - 2))

            y += 22

    return y


def draw_wrapped_text(
    screen: pygame.Surface,
    small_font: pygame.font.Font,
    text: str,
    x: int,
    y: int,
    max_width: int,
    color: Tuple[int, int, int],
) -> int:
    """Draw text with word wrapping."""
    words = text.split(' ')
    lines = []
    current_line: List[str] = []

    for word in words:
        test_line = ' '.join(current_line + [word])
        test_surf = small_font.render(test_line, True, color)

        if test_surf.get_width() <= max_width:
            current_line.append(word)
        else:
            if current_line:
                lines.append(' '.join(current_line))
            current_line = [word]

    if current_line:
        lines.append(' '.join(current_line))

    # Draw lines
    for line in lines:
        line_surf = small_font.render(line, True, color)
        screen.blit(line_surf, (x, y))
        y += 20

    return y


def draw_validation_flag(
    screen: pygame.Surface,
    small_font: pygame.font.Font,
    x: int,
    y: int,
    scenario_info: Dict[str, Any],
) -> None:
    """
    Draw a colored flag/circle indicating validation status.

    Green circle = All validations passed
    Yellow circle = Warnings present
    Red circle = Failures present
    Gray circle = No validation data (test not run yet)
    """
    radius = 10

    # Check for validation results
    last_run_results = scenario_info.get('last_run_results')

    if not last_run_results:
        # No run data at all - gray circle
        color = theme.SEED_RANDOM
        symbol = None
    elif 'validation_results' in last_run_results:
        # New-style validation results with per-check dicts
        validation_summary = last_run_results.get('validation_summary', {})
        fail_count = validation_summary.get('fail', 0)
        warn_count = validation_summary.get('warn', 0)

        if fail_count > 0:
            color = TEST_FAIL
            symbol = "X"
        elif warn_count > 0:
            color = theme.STATUS_WARNING
            symbol = "!"
        else:
            color = TEST_PASS
            symbol = "V"
    elif last_run_results.get('validation', {}).get('passed') is not None:
        # Fallback: old-style validation with a single 'passed' bool
        passed = last_run_results['validation']['passed']
        color = TEST_PASS if passed else TEST_FAIL
        symbol = "V" if passed else "X"
    else:
        # No validation data - gray circle
        color = theme.SEED_RANDOM
        symbol = None

    # Draw circle
    pygame.draw.circle(screen, color, (x, y), radius)
    pygame.draw.circle(screen, BLACK, (x, y), radius, 2)  # Black outline

    # Draw symbol if present
    if symbol:
        symbol_surf = small_font.render(symbol, True, BLACK)
        symbol_rect = symbol_surf.get_rect(center=(x, y))
        screen.blit(symbol_surf, symbol_rect)


def draw_output_log(
    screen: pygame.Surface,
    small_font: pygame.font.Font,
    output_log: List[str],
) -> None:
    """Draw the output log at the bottom."""
    y = HEIGHT - 90
    for i, msg in enumerate(output_log[-3:]):
        color = theme.STATUS_FAIL if "ERROR" in msg else theme.TEXT_DIM
        txt = small_font.render(msg, True, color)
        screen.blit(txt, (20, y + i * 20))
