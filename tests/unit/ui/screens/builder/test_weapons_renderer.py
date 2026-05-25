"""Focused dispatch tests for the weapons report renderer."""
from __future__ import annotations

from unittest.mock import MagicMock

import pygame
import pytest

from game.ui.screens.builder.weapons_renderer import WeaponsRenderer


class _TextSurface:
    def __init__(self, text: str) -> None:
        self.text = text

    def get_width(self) -> int:
        return len(self.text) * 7

    def get_height(self) -> int:
        return 14


class _Font:
    def __init__(self) -> None:
        self.rendered: list[tuple[str, object]] = []

    def render(self, text: str, antialias: bool, color: object) -> _TextSurface:
        self.rendered.append((text, color))
        return _TextSurface(text)


class _Screen:
    def __init__(self, width: int = 800) -> None:
        self.width = width
        self.blits: list[tuple[_TextSurface, tuple[int, int]]] = []

    def get_width(self) -> int:
        return self.width

    def blit(self, surface: _TextSurface, pos: tuple[int, int]) -> None:
        self.blits.append((surface, pos))


def _make_renderer() -> WeaponsRenderer:
    renderer = WeaponsRenderer.__new__(WeaponsRenderer)
    renderer.sprite_mgr = MagicMock()
    renderer.font = _Font()
    renderer.small_font = _Font()
    renderer.target_font = _Font()
    renderer._name_cache = {}
    renderer._icon_cache = {}
    return renderer


def test_weapons_renderer_no_weapons_message_blits_disabled_text() -> None:
    renderer = _make_renderer()
    screen = _Screen()
    rect = pygame.Rect(10, 20, 300, 100)

    renderer.draw_no_weapons_message(screen, rect)

    assert renderer.font.rendered == [
        ("No weapons equipped", renderer.COLOR_NO_WEAPONS)
    ]
    assert screen.blits[0][1] == (20, 60)


def test_weapons_renderer_target_info_formats_defense_modifier() -> None:
    renderer = _make_renderer()
    screen = _Screen()
    rect = pygame.Rect(5, 12, 300, 100)

    renderer.draw_target_info(screen, rect, "Raider", 1.234)

    assert renderer.target_font.rendered == [
        ("Target: Raider (Def Mod: 1.23)", renderer.COLOR_TARGET_INFO)
    ]
    assert screen.blits[0][1] == (665, 17)


def test_weapons_renderer_verbose_tooltip_renders_detailed_lines(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    renderer = _make_renderer()
    screen = _Screen(width=160)
    draw_rect = MagicMock()
    monkeypatch.setattr(pygame.draw, "rect", draw_rect)

    renderer.draw_tooltip(
        screen,
        {
            "pos": (150, 20),
            "range": 42,
            "accuracy": "75%",
            "damage": 16,
            "verbose": {
                "base_acc": 0.5,
                "attack_score": 2.0,
                "range_penalty": 0.25,
                "defense_score": 1.0,
                "net_score": 1.25,
            },
        },
        verbose=True,
    )

    # PROJ-494 T4.4: was an exact-ordered-list assertion against 9 format
    # strings. Replaced with structural assertions (each line contains the
    # expected key→value pair) so cosmetic format tweaks don't break the
    # test for no behavioral reason. Order is still verified.
    rendered_lines = [text for text, _ in renderer.small_font.rendered]
    expected_pairs = [
        ("Range", "42"),
        ("Base Score", "0.50"),
        ("Attack Score", "+2.00"),
        ("Range Penalty", "-0.25"),
        ("Defense Score", "-1.00"),
        ("Net Score", "1.25"),
        (None, "----"),  # divider line: just contains dashes
        ("Final Accuracy", "75%"),
        ("Damage", "16"),
    ]
    assert len(rendered_lines) == len(expected_pairs), (
        f"expected {len(expected_pairs)} lines; got {len(rendered_lines)}: {rendered_lines!r}"
    )
    for i, (label, value) in enumerate(expected_pairs):
        line = rendered_lines[i]
        if label is not None:
            assert label in line, f"line {i}: missing label {label!r} in {line!r}"
        assert value in line, f"line {i}: missing value {value!r} in {line!r}"
    assert draw_rect.call_count == 2
    assert len(screen.blits) == len(rendered_lines)
