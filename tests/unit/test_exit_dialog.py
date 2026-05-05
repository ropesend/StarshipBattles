"""Unit coverage for the exit confirmation dialog helpers."""
from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass
from types import SimpleNamespace
from typing import Any

import pytest

from game import exit_dialog


@dataclass(frozen=True)
class FakeRect:
    x: int
    y: int
    w: int
    h: int

    def collidepoint(self, *args: Any) -> bool:
        if len(args) == 1:
            x, y = args[0]
        else:
            x, y = args
        return self.x <= x < self.x + self.w and self.y <= y < self.y + self.h


class FakeSurface:
    def __init__(self, size: tuple[int, int], flags: Any = None) -> None:
        self.size = size
        self.flags = flags
        self.fill_calls: list[Any] = []

    def fill(self, color: Any) -> None:
        self.fill_calls.append(color)


class FakeScreen:
    def __init__(self, size: tuple[int, int]) -> None:
        self._size = size
        self.blits: list[tuple[Any, Any]] = []

    def get_size(self) -> tuple[int, int]:
        return self._size

    def blit(self, surface: Any, pos: Any) -> None:
        self.blits.append((surface, pos))


class FakeText:
    def __init__(self, width: int) -> None:
        self._width = width

    def get_width(self) -> int:
        return self._width


class FakeFont:
    def __init__(self, width: int = 80) -> None:
        self.width = width
        self.render_calls: list[tuple[str, bool, Any]] = []

    def render(self, text: str, antialias: bool, color: Any) -> FakeText:
        self.render_calls.append((text, antialias, color))
        return FakeText(self.width)


class FakeDraw:
    def __init__(self) -> None:
        self.rect_calls: list[tuple[Any, ...]] = []

    def rect(self, *args: Any) -> None:
        self.rect_calls.append(args)


def make_fake_pygame(mouse_pos: tuple[int, int] = (0, 0)) -> SimpleNamespace:
    surfaces: list[FakeSurface] = []

    def surface_factory(size: tuple[int, int], flags: Any = None) -> FakeSurface:
        surface = FakeSurface(size, flags)
        surfaces.append(surface)
        return surface

    return SimpleNamespace(
        SRCALPHA="srcalpha",
        Surface=surface_factory,
        Rect=FakeRect,
        draw=FakeDraw(),
        mouse=SimpleNamespace(get_pos=lambda: mouse_pos),
        surfaces=surfaces,
    )


@pytest.fixture(autouse=True)
def reset_exit_dialog_rects() -> Iterator[None]:
    exit_dialog._exit_yes_rect = None
    exit_dialog._exit_no_rect = None
    yield
    exit_dialog._exit_yes_rect = None
    exit_dialog._exit_no_rect = None


def test_draw_exit_dialog_populates_button_rects_and_draws_dialog(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fake_pygame = make_fake_pygame()
    monkeypatch.setattr(exit_dialog, "pygame", fake_pygame)
    screen = FakeScreen((800, 600))
    font_large = FakeFont(width=180)
    font_med = FakeFont(width=30)

    exit_dialog.draw_exit_dialog(screen, font_large, font_med)

    assert exit_dialog._exit_yes_rect == FakeRect(280, 320, 100, 40)
    assert exit_dialog._exit_no_rect == FakeRect(420, 320, 100, 40)
    assert fake_pygame.surfaces[0].size == (800, 600)
    assert fake_pygame.surfaces[0].flags == "srcalpha"
    assert fake_pygame.surfaces[0].fill_calls == [(0, 0, 0, 180)]
    assert screen.blits[0] == (fake_pygame.surfaces[0], (0, 0))
    assert font_large.render_calls == [
        ("Exit Application?", True, (255, 255, 255))
    ]
    assert [call[0] for call in font_med.render_calls] == ["Yes", "No"]
    assert fake_pygame.draw.rect_calls[0][1] == (40, 40, 50)
    assert fake_pygame.draw.rect_calls[1][1] == (100, 100, 120)
    assert fake_pygame.draw.rect_calls[2][1] == (150, 50, 50)
    assert fake_pygame.draw.rect_calls[2][2] == FakeRect(280, 320, 100, 40)
    assert fake_pygame.draw.rect_calls[4][1] == (50, 50, 60)
    assert fake_pygame.draw.rect_calls[4][2] == FakeRect(420, 320, 100, 40)


def test_draw_exit_dialog_uses_hover_colors_after_rects_are_created(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fake_pygame = make_fake_pygame(mouse_pos=(285, 325))
    monkeypatch.setattr(exit_dialog, "pygame", fake_pygame)

    exit_dialog.draw_exit_dialog(FakeScreen((800, 600)), FakeFont(), FakeFont())

    assert fake_pygame.draw.rect_calls[2][1] == (180, 60, 60)
    assert fake_pygame.draw.rect_calls[4][1] == (50, 50, 60)


def test_yes_and_no_click_handlers_use_populated_rects(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fake_pygame = make_fake_pygame()
    monkeypatch.setattr(exit_dialog, "pygame", fake_pygame)
    exit_dialog.draw_exit_dialog(FakeScreen((800, 600)), FakeFont(), FakeFont())

    assert exit_dialog.handle_exit_dialog_click((281, 321)) is True
    assert exit_dialog.handle_exit_dialog_click((421, 321)) is False
    assert exit_dialog.handle_exit_dialog_cancel((421, 321)) is True
    assert exit_dialog.handle_exit_dialog_cancel((281, 321)) is False


def test_click_handlers_return_false_when_rects_are_none_or_reset() -> None:
    assert exit_dialog.handle_exit_dialog_click((1, 1)) is False
    assert exit_dialog.handle_exit_dialog_cancel((1, 1)) is False

    exit_dialog._exit_yes_rect = FakeRect(0, 0, 10, 10)
    exit_dialog._exit_no_rect = FakeRect(20, 0, 10, 10)
    assert exit_dialog.handle_exit_dialog_click((1, 1)) is True
    assert exit_dialog.handle_exit_dialog_cancel((21, 1)) is True

    exit_dialog._exit_yes_rect = None
    exit_dialog._exit_no_rect = None
    assert exit_dialog.handle_exit_dialog_click((1, 1)) is False
    assert exit_dialog.handle_exit_dialog_cancel((21, 1)) is False
