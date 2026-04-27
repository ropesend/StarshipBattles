"""Generic chrome for the test-run-details panel.

PROJ-309 sub-phase 3.6 — extracted verbatim from `test_run_details.py`.
Test-family-agnostic helpers: header & PASSED/FAILED badge, seed+ticks
metadata line, the three action buttons (View States / Use Seed /
Copy Results), generic metrics list, and scrollbar.

All helpers take a `DetailsDrawContext` for the surface/geometry/fonts/colors
plus the run record (where applicable). The action-buttons helper returns
an `ActionButtonRects` dataclass so the panel can store the three button
rects on its own attributes — preserving the exact `handle_event` contract.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import pygame

from game.core.string_utils import display_name
from game.ui.screens.test_lab import theme

from .draw_context import DetailsDrawContext


@dataclass(frozen=True)
class ActionButtonRects:
    """The three button rects populated by `draw_action_buttons`. Any rect
    may be `None` if the button was not rendered (e.g. no battle states,
    no seed, or scrolled out of view)."""

    view_states: Optional[pygame.Rect]
    use_seed: Optional[pygame.Rect]
    copy_results: Optional[pygame.Rect]


def draw_header_and_status(
    ctx: DetailsDrawContext,
    run_record,
    run_number,
    y_offset: int,
) -> int:
    """Draw run info header and pass/fail status.

    Returns updated y_offset.
    """
    surface = ctx.surface
    # Run info header
    timestamp_str = run_record.get_formatted_timestamp()
    header_text = f"Run #{run_number} - {timestamp_str}"
    header_surf = ctx.header_font.render(header_text, True, ctx.text_color)
    surface.blit(header_surf, (ctx.x + 10, y_offset))
    y_offset += 30

    # Status
    status_text = "PASSED" if run_record.passed else "FAILED"
    status_color = ctx.pass_color if run_record.passed else ctx.fail_color
    status_surf = ctx.title_font.render(status_text, True, status_color)
    surface.blit(status_surf, (ctx.x + 10, y_offset))
    y_offset += 25

    return y_offset


def draw_metadata(
    ctx: DetailsDrawContext,
    run_record,
    y_offset: int,
) -> int:
    """Draw seed and ticks information.

    Returns updated y_offset.
    """
    surface = ctx.surface
    if run_record.seed is not None:
        seed_text = f"Seed: {run_record.seed}"
        seed_surf = ctx.small_font.render(seed_text, True, theme.TEXT_SECONDARY)
        surface.blit(seed_surf, (ctx.x + 15, y_offset))

    ticks_run = run_record.metrics.get('ticks_run')
    if ticks_run is not None:
        ticks_text = f"Ticks: {ticks_run}"
        ticks_surf = ctx.small_font.render(ticks_text, True, theme.TEXT_SECONDARY)
        # Position ticks to the right of seed (or at start if no seed)
        ticks_x = ctx.x + 180 if run_record.seed is not None else ctx.x + 15
        surface.blit(ticks_surf, (ticks_x, y_offset))

    return y_offset


def draw_action_buttons(
    ctx: DetailsDrawContext,
    run_record,
    y_offset: int,
) -> tuple[int, ActionButtonRects]:
    """Draw View States, Use Seed, and Copy Results buttons.

    Returns `(updated_y_offset, ActionButtonRects)`. The rects are written
    by the helper and consumed by `handle_event` on the panel.
    """
    surface = ctx.surface
    y_offset -= 25  # Reset for button positioning

    view_states_button_rect: Optional[pygame.Rect] = None
    use_seed_button_rect: Optional[pygame.Rect] = None
    copy_results_button_rect: Optional[pygame.Rect] = None

    # View States button (if battle states are available)
    if run_record.has_battle_states():
        button_width = 110
        button_height = 26
        button_x = ctx.x + ctx.width - button_width - 15
        button_y = y_offset - 5 + ctx.scroll_offset  # Account for scroll in positioning

        # Only show button if it's in the visible area
        if button_y >= ctx.y and button_y + button_height <= ctx.y + ctx.height:
            view_states_button_rect = pygame.Rect(button_x, button_y, button_width, button_height)

            mouse_pos = pygame.mouse.get_pos()
            is_hovered = view_states_button_rect.collidepoint(mouse_pos)
            btn_color = ctx.button_hover_color if is_hovered else ctx.button_color

            pygame.draw.rect(surface, btn_color, view_states_button_rect, border_radius=4)
            pygame.draw.rect(surface, theme.BUTTON_VIEW_STATES_BORDER, view_states_button_rect, 1, border_radius=4)

            btn_text = ctx.small_font.render("View States", True, theme.TEXT_WHITE)
            text_x = button_x + (button_width - btn_text.get_width()) // 2
            text_y = button_y + (button_height - btn_text.get_height()) // 2
            surface.blit(btn_text, (text_x, text_y))

    # Use Seed button (always show if seed is available)
    if run_record.seed is not None:
        button_width = 80
        button_height = 26
        # Position to the left of View States button (or at the right if no View States)
        if view_states_button_rect:
            button_x = view_states_button_rect.x - button_width - 10
        else:
            button_x = ctx.x + ctx.width - button_width - 15
        button_y = y_offset - 5 + ctx.scroll_offset

        # Only show button if it's in the visible area
        if button_y >= ctx.y and button_y + button_height <= ctx.y + ctx.height:
            use_seed_button_rect = pygame.Rect(button_x, button_y, button_width, button_height)

            mouse_pos = pygame.mouse.get_pos()
            is_hovered = use_seed_button_rect.collidepoint(mouse_pos)
            btn_color = ctx.button_hover_color if is_hovered else ctx.button_color

            pygame.draw.rect(surface, btn_color, use_seed_button_rect, border_radius=4)
            pygame.draw.rect(surface, theme.BUTTON_USE_SEED_BORDER, use_seed_button_rect, 1, border_radius=4)

            btn_text = ctx.small_font.render("Use Seed", True, theme.TEXT_WHITE)
            text_x = button_x + (button_width - btn_text.get_width()) // 2
            text_y = button_y + (button_height - btn_text.get_height()) // 2
            surface.blit(btn_text, (text_x, text_y))

    # Copy Results button (always show)
    button_width = 90
    button_height = 26
    # Position to the left of Use Seed button (or at the right if no Use Seed)
    if use_seed_button_rect:
        button_x = use_seed_button_rect.x - button_width - 10
    elif view_states_button_rect:
        button_x = view_states_button_rect.x - button_width - 10
    else:
        button_x = ctx.x + ctx.width - button_width - 15
    button_y = y_offset - 5 + ctx.scroll_offset

    # Only show button if it's in the visible area
    if button_y >= ctx.y and button_y + button_height <= ctx.y + ctx.height:
        copy_results_button_rect = pygame.Rect(button_x, button_y, button_width, button_height)

        mouse_pos = pygame.mouse.get_pos()
        is_hovered = copy_results_button_rect.collidepoint(mouse_pos)
        btn_color = ctx.button_hover_color if is_hovered else ctx.button_color

        pygame.draw.rect(surface, btn_color, copy_results_button_rect, border_radius=4)
        pygame.draw.rect(surface, theme.BUTTON_COPY_BORDER, copy_results_button_rect, 1, border_radius=4)

        btn_text = ctx.small_font.render("Copy Results", True, theme.TEXT_WHITE)
        text_x = button_x + (button_width - btn_text.get_width()) // 2
        text_y = button_y + (button_height - btn_text.get_height()) // 2
        surface.blit(btn_text, (text_x, text_y))

    y_offset += 40

    return y_offset, ActionButtonRects(
        view_states=view_states_button_rect,
        use_seed=use_seed_button_rect,
        copy_results=copy_results_button_rect,
    )


def draw_metrics(
    ctx: DetailsDrawContext,
    run_record,
    y_offset: int,
) -> int:
    """Draw test metrics section.

    Returns updated y_offset.
    """
    surface = ctx.surface
    metrics_title = ctx.header_font.render("Test Metrics", True, ctx.header_color)
    surface.blit(metrics_title, (ctx.x + 10, y_offset))
    y_offset += 25

    for key, value in run_record.metrics.items():
        if key not in ['validation_results', 'validation_summary']:
            if isinstance(value, float):
                value_str = f"{value:.1%}" if 0 < value < 1 else f"{value:.2f}"
            else:
                value_str = str(value)
            display_key = display_name(key)
            metric_text = f"  {display_key}: {value_str}"
            metric_surf = ctx.small_font.render(metric_text, True, ctx.text_color)
            surface.blit(metric_surf, (ctx.x + 15, y_offset))
            y_offset += 20

    y_offset += 10

    return y_offset


def draw_scrollbar(
    ctx: DetailsDrawContext,
    scroll,
) -> None:
    """Draw scrollbar indicator.

    `scroll` is a `ScrollState` (live state, not part of the frozen ctx
    because the scrollbar visualises current ratio + max_offset).
    """
    surface = ctx.surface
    visible_height = ctx.height
    total_content_height = visible_height + scroll.max_offset
    scrollbar_width = 8
    scrollbar_x = ctx.x + ctx.width - scrollbar_width - 5
    scrollbar_track_y = ctx.y + 5
    scrollbar_track_height = visible_height - 10
    thumb_height = max(30, int(visible_height * (visible_height / total_content_height)))
    thumb_y = scrollbar_track_y + int(scroll.scroll_ratio * (scrollbar_track_height - thumb_height))
    pygame.draw.rect(surface, theme.SCROLLBAR_THUMB, (scrollbar_x, thumb_y, scrollbar_width, thumb_height), border_radius=4)
