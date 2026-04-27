"""Shared draw context for the Combat Lab test-run-details subpackage.

PROJ-309 sub-phase 3.6 — extracted from `test_run_details.py`. The frozen
`DetailsDrawContext` carries everything a section-renderer needs (surface,
panel rect, fonts, colors) so per-section helpers stay pure of class state
and avoid 8-positional-arg signatures. `OutcomePalette` bags the inner
constants (label color / value color / highlight color / indent /
label_width) that fuel/energy/ammo/turn/motion helpers used to take
positionally.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Tuple

if TYPE_CHECKING:
    import pygame


@dataclass(frozen=True)
class DetailsDrawContext:
    """Bundle of state passed to every per-section draw helper.

    All fields are read-only references to objects owned by
    `TestRunDetailsPanel`. Helpers must NOT mutate `surface` outside their
    section, must NOT cache the context across draws, and must NOT keep a
    reference past the call.
    """

    # Render target & panel geometry
    surface: "pygame.Surface"
    x: int
    y: int
    width: int
    height: int
    scroll_offset: int

    # Fonts
    title_font: "pygame.font.Font"
    header_font: "pygame.font.Font"
    body_font: "pygame.font.Font"
    small_font: "pygame.font.Font"

    # Standard colors used across all sections
    pass_color: Tuple[int, int, int]
    fail_color: Tuple[int, int, int]
    header_color: Tuple[int, int, int]
    text_color: Tuple[int, int, int]
    button_color: Tuple[int, int, int]
    button_hover_color: Tuple[int, int, int]


@dataclass(frozen=True)
class OutcomePalette:
    """Layout + color constants shared by the resource & propulsion outcome
    sub-renderers. Bundled so call sites pass one argument instead of five."""

    label_color: Tuple[int, int, int]
    value_color: Tuple[int, int, int]
    highlight_color: Tuple[int, int, int]
    indent: int
    label_width: int
