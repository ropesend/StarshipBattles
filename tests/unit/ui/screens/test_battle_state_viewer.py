"""Focused dispatch tests for the battle state viewer overlay."""
from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import MagicMock

import pygame
import pytest

from game.ui.screens.battle_state_viewer import BattleStateViewer


class _TextSurface:
    def __init__(self, text: str) -> None:
        self.text = text

    def get_width(self) -> int:
        return len(self.text) * 8

    def get_height(self) -> int:
        return 16


class _Font:
    def __init__(self) -> None:
        self.rendered: list[str] = []

    def render(self, text: str, antialias: bool, color: object) -> _TextSurface:
        self.rendered.append(text)
        return _TextSurface(text)

    def size(self, text: str) -> tuple[int, int]:
        return (len(text) * 8, 16)


class _Surface:
    def __init__(self) -> None:
        self.blits: list[tuple[object, tuple[int, int]]] = []

    def blit(self, surface: object, pos: tuple[int, int]) -> None:
        self.blits.append((surface, pos))


def _make_viewer(*, visible: bool = True) -> BattleStateViewer:
    viewer = BattleStateViewer.__new__(BattleStateViewer)
    viewer.screen_width = 800
    viewer.screen_height = 600
    viewer.visible = visible
    viewer.margin = 40
    viewer.close_button_rect = pygame.Rect(660, 520, 100, 35)
    viewer.initial_panel = MagicMock()
    viewer.final_panel = MagicMock()
    viewer.header_font = _Font()
    viewer.button_font = _Font()
    viewer.legend_font = _Font()
    viewer.overlay_color = (0, 0, 0, 200)
    viewer.header_color = (255, 255, 255)
    viewer.button_color = (10, 20, 30)
    viewer.button_hover_color = (30, 40, 50)
    viewer.test_id = None
    viewer.run_number = None
    viewer.diff_stats = {"changed": 0, "added": 0, "removed": 0}
    return viewer


def test_battle_state_viewer_hidden_event_and_draw_do_not_dispatch() -> None:
    viewer = _make_viewer(visible=False)
    surface = _Surface()

    assert viewer.handle_event(SimpleNamespace(type=pygame.MOUSEMOTION)) is False
    viewer.draw(surface)

    viewer.initial_panel.handle_event.assert_not_called()
    viewer.final_panel.handle_event.assert_not_called()
    viewer.initial_panel.draw.assert_not_called()
    viewer.final_panel.draw.assert_not_called()
    assert surface.blits == []


def test_battle_state_viewer_panel_event_dispatch_stops_after_initial_panel() -> None:
    viewer = _make_viewer()
    viewer.initial_panel.handle_event.return_value = True
    viewer.final_panel.handle_event.return_value = True
    event = SimpleNamespace(type=pygame.MOUSEWHEEL, y=-1)

    assert viewer.handle_event(event) is True

    viewer.initial_panel.handle_event.assert_called_once_with(event)
    viewer.final_panel.handle_event.assert_not_called()


def test_battle_state_viewer_panel_event_dispatch_reaches_final_panel() -> None:
    viewer = _make_viewer()
    viewer.initial_panel.handle_event.return_value = False
    viewer.final_panel.handle_event.return_value = True
    event = SimpleNamespace(type=pygame.MOUSEWHEEL, y=1)

    assert viewer.handle_event(event) is True

    viewer.initial_panel.handle_event.assert_called_once_with(event)
    viewer.final_panel.handle_event.assert_called_once_with(event)


def test_battle_state_viewer_close_events_hide_without_panel_dispatch() -> None:
    viewer = _make_viewer()
    close_click = SimpleNamespace(
        type=pygame.MOUSEBUTTONDOWN,
        button=1,
        pos=viewer.close_button_rect.center,
    )

    assert viewer.handle_event(close_click) is False
    assert viewer.visible is False
    viewer.initial_panel.handle_event.assert_not_called()
    viewer.final_panel.handle_event.assert_not_called()

    viewer.visible = True
    escape = SimpleNamespace(type=pygame.KEYDOWN, key=pygame.K_ESCAPE)

    assert viewer.handle_event(escape) is False
    assert viewer.visible is False


def test_battle_state_viewer_draw_dispatches_panels_legend_and_close_button(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    viewer = _make_viewer()
    viewer.test_id = "scenario-a"
    viewer.run_number = 3
    surface = _Surface()
    draw_rect = MagicMock()
    monkeypatch.setattr(pygame.mouse, "get_pos", lambda: (0, 0))
    monkeypatch.setattr(pygame.draw, "rect", draw_rect)
    viewer._draw_legend = MagicMock()

    viewer.draw(surface)

    viewer.initial_panel.draw.assert_called_once_with(surface)
    viewer.final_panel.draw.assert_called_once_with(surface)
    viewer._draw_legend.assert_called_once_with(surface)
    assert "Battle States - scenario-a (Run #3)" in viewer.header_font.rendered
    assert "Close (ESC)" in viewer.button_font.rendered
    assert draw_rect.call_count == 2
