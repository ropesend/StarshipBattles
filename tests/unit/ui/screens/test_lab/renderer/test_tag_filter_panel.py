from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pygame

from game.ui.screens.test_lab import theme
from game.ui.screens.test_lab.renderer.tag_filter_panel import TagFilterPanel


class RecordingFont:
    """Font fake that records rendered text and color without relying on pixels."""

    def __init__(self) -> None:
        self.renders: list[tuple[str, tuple[int, int, int]]] = []

    def render(self, text: str, antialias: bool, color: tuple[int, int, int]) -> pygame.Surface:
        self.renders.append((text, color))
        return pygame.Surface((max(1, len(text)), 10))


class FakeUiState:
    def __init__(self, *, active: set[str] | None = None, excluded: set[str] | None = None) -> None:
        self.active = active or set()
        self.excluded = excluded or set()

    def is_tag_active(self, tag: str) -> bool:
        return tag in self.active

    def is_tag_excluded(self, tag: str) -> bool:
        return tag in self.excluded

    def get_active_tag_filters(self) -> set[str]:
        return self.active

    def get_excluded_tags(self) -> set[str]:
        return self.excluded


def _panel(font: RecordingFont) -> TagFilterPanel:
    return TagFilterPanel(
        small_font=font,
        header_color=(1, 2, 3),
        text_color=(4, 5, 6),
        category_bg=(7, 8, 9),
        border_color=(10, 11, 12),
    )


def _draw(
    *,
    tags: set[str],
    ui_state: FakeUiState | None = None,
    mouse_pos: tuple[int, int] = (0, 0),
) -> tuple[RecordingFont, SimpleNamespace, MagicMock]:
    font = RecordingFont()
    screen = pygame.Surface((400, 260))
    registry = MagicMock()
    registry.get_all_tags.return_value = tags
    viewmodel = SimpleNamespace(tag_filter_rects={}, tag_clear_rect=None)
    controller = SimpleNamespace(ui_state=ui_state or FakeUiState())

    with patch("game.ui.screens.test_lab.renderer.tag_filter_panel.pygame.mouse.get_pos", return_value=mouse_pos):
        _panel(font).draw(screen, 10, 20, controller, registry, viewmodel)

    return font, viewmodel, registry


def test_draw_prioritizes_common_tags_limits_to_eight_and_writes_viewmodel_rects() -> None:
    tags = {
        "zeta",
        "precision",
        "alpha",
        "quick",
        "high-tick",
        "beta",
        "gamma",
        "delta",
        "epsilon",
        "theta",
    }

    _font, viewmodel, registry = _draw(tags=tags)

    assert list(viewmodel.tag_filter_rects) == [
        "high-tick",
        "precision",
        "quick",
        "alpha",
        "beta",
        "delta",
        "epsilon",
        "gamma",
    ]
    assert all(isinstance(rect, pygame.Rect) for rect in viewmodel.tag_filter_rects.values())
    assert viewmodel.tag_clear_rect is None
    registry.get_all_tags.assert_called_once_with()


def test_draw_marks_active_and_excluded_tags_and_shows_combined_clear_count() -> None:
    font = RecordingFont()
    screen = pygame.Surface((400, 260))
    registry = MagicMock()
    registry.get_all_tags.return_value = {"precision", "alpha", "quick"}
    viewmodel = SimpleNamespace(tag_filter_rects={}, tag_clear_rect=None)
    controller = SimpleNamespace(ui_state=FakeUiState(active={"precision"}, excluded={"alpha"}))

    with (
        patch("game.ui.screens.test_lab.renderer.tag_filter_panel.pygame.mouse.get_pos", return_value=(0, 0)),
        patch("game.ui.screens.test_lab.renderer.tag_filter_panel.pygame.draw.rect") as draw_rect,
    ):
        _panel(font).draw(screen, 10, 20, controller, registry, viewmodel)

    rendered = [text for text, _color in font.renders]
    rect_colors = [call.args[1] for call in draw_rect.call_args_list]

    assert "V precision" in rendered
    assert "X alpha" in rendered
    assert "Clear" in rendered
    assert "+1 / -1" in rendered
    assert theme.TAG_ACTIVE_BG in rect_colors
    assert theme.TAG_EXCLUDED_BG in rect_colors
    assert theme.CLEAR_BUTTON_BG in rect_colors
    assert isinstance(viewmodel.tag_clear_rect, pygame.Rect)


def test_draw_uses_hover_style_for_normal_tag() -> None:
    font, viewmodel, _registry = _draw(tags={"quick"}, mouse_pos=(12, 47))

    assert ("quick", (4, 5, 6)) in font.renders
    assert viewmodel.tag_clear_rect is None


def test_draw_uses_hover_style_for_clear_button() -> None:
    font = RecordingFont()
    screen = pygame.Surface((400, 260))
    registry = MagicMock()
    registry.get_all_tags.return_value = {"quick"}
    viewmodel = SimpleNamespace(tag_filter_rects={}, tag_clear_rect=None)
    controller = SimpleNamespace(ui_state=FakeUiState(active={"quick"}))

    with (
        patch("game.ui.screens.test_lab.renderer.tag_filter_panel.pygame.mouse.get_pos", return_value=(12, 80)),
        patch("game.ui.screens.test_lab.renderer.tag_filter_panel.pygame.draw.rect") as draw_rect,
    ):
        _panel(font).draw(screen, 10, 20, controller, registry, viewmodel)

    rect_colors = [call.args[1] for call in draw_rect.call_args_list]

    assert "Clear" in [text for text, _color in font.renders]
    assert "+1 tags" in [text for text, _color in font.renders]
    assert theme.CLEAR_BUTTON_HOVER in rect_colors
    assert isinstance(viewmodel.tag_clear_rect, pygame.Rect)
