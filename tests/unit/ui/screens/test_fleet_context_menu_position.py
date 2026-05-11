"""Layer 4 tests for issue #20: menu position clamping.

The fleet context menu opens at the right-click position. If the click
is near the right or bottom edge of the screen, the panel rect must
shift up-and-left so it remains fully on-screen.
"""
from __future__ import annotations

import pygame

from game.ui.screens.strategy_fleet_context_menu import clamp_menu_position


def test_T30_clamps_against_right_and_bottom_edges():
    rect = clamp_menu_position(
        x=2550, y=1590,
        width=200, height=300,
        screen_width=2560, screen_height=1600,
    )
    assert rect.right <= 2560
    assert rect.bottom <= 1600


def test_T31_no_clamp_when_well_inside_screen():
    rect = clamp_menu_position(
        x=20, y=20,
        width=200, height=300,
        screen_width=2560, screen_height=1600,
    )
    # Anchored at the click point (no shift required).
    assert rect.x == 20
    assert rect.y == 20


def test_clamp_against_left_edge_returns_x_zero():
    # Defensive: caller shouldn't pass negative x, but if they do we
    # clamp to 0 rather than overflow off the left edge.
    rect = clamp_menu_position(
        x=-50, y=20,
        width=200, height=300,
        screen_width=2560, screen_height=1600,
    )
    assert rect.x >= 0


def test_clamp_returns_pygame_rect():
    rect = clamp_menu_position(
        x=100, y=100, width=200, height=300,
        screen_width=2560, screen_height=1600,
    )
    assert isinstance(rect, pygame.Rect)
    assert rect.width == 200
    assert rect.height == 300
