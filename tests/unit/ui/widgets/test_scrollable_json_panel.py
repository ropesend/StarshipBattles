"""Characterization tests for ScrollableJsonPanel (PROJ-340).

Pins observed behavior of the JSON viewer widget at
``game/ui/widgets/scrollable_json_panel.py``. Patches ``get_font`` (used
during ``__init__``) so the font subsystem is bypassed; uses real
``pygame.Surface`` objects where needed and constructs ``pygame.Event``
instances directly.
"""
from __future__ import annotations

from unittest.mock import MagicMock, patch

import pygame
import pytest

from game.ui.utils.json_diff import DiffResult


@pytest.fixture
def panel_factory():
    """Factory that constructs a ScrollableJsonPanel with get_font patched.

    ``get_font`` is patched at the module-import site so the panel never
    pulls in pygame's font subsystem during construction.
    """
    def _factory(*, x: int = 0, y: int = 0, width: int = 200, height: int = 200,
                 title: str = "Panel", is_final: bool = False):
        # The widget imports get_font at module load via:
        #   from game.ui.fonts import get_font, FONT_MONO
        # so we patch the bound name inside the widget module.
        fake_font = MagicMock()
        rendered = MagicMock(spec=pygame.Surface)
        rendered.get_width.return_value = 7
        fake_font.render.return_value = rendered

        with patch(
            "game.ui.widgets.scrollable_json_panel.get_font",
            return_value=fake_font,
        ):
            from game.ui.widgets.scrollable_json_panel import (
                ScrollableJsonPanel,
            )
            return ScrollableJsonPanel(
                x=x, y=y, width=width, height=height,
                title=title, is_final=is_final,
            )
    return _factory


# ----------------------------------------------------------------------------
# set_json_with_diff input handling
# ----------------------------------------------------------------------------


class TestSetJsonWithDiff:
    def test_set_json_with_diff_handles_none_payload_with_zero_content_height(
        self, panel_factory
    ):
        panel = panel_factory()
        panel.set_json_with_diff(None, {})

        assert panel.json_lines == []
        assert panel.scroll.content_height == 0

    def test_set_json_with_diff_appends_error_line_for_invalid_json_string(
        self, panel_factory
    ):
        panel = panel_factory()
        panel.set_json_with_diff("not-json{", {})

        # First line is an "Error parsing JSON: ..." entry.
        assert panel.json_lines, "expected at least one rendered line"
        first = panel.json_lines[0]
        text = first[1]
        assert isinstance(text, str)
        assert text.startswith("Error parsing JSON:")


# ----------------------------------------------------------------------------
# _format_value (string truncation)
# ----------------------------------------------------------------------------


class TestFormatValue:
    def test_format_value_truncates_long_strings_with_ellipsis(
        self, panel_factory
    ):
        panel = panel_factory()
        long_str = "x" * 100  # > 50 chars threshold

        text, _color = panel._format_value(long_str)

        # Production: truncates to 47 + '...' and wraps in quotes.
        assert text.startswith('"')
        assert text.endswith('..."')
        # First 47 'x' chars then '...'
        assert text == '"' + ("x" * 47) + '..."'


# ----------------------------------------------------------------------------
# _get_diff_colors matrix (pinned per master plan)
# ----------------------------------------------------------------------------


class TestGetDiffColors:
    def test_get_diff_colors_suppresses_added_on_non_final_panel(
        self, panel_factory
    ):
        panel = panel_factory(is_final=False)
        panel.diff_paths = {"some.path": DiffResult.ADDED}

        text, bg = panel._get_diff_colors("some.path")

        assert text is None
        assert bg is None

    def test_get_diff_colors_suppresses_removed_on_final_panel(
        self, panel_factory
    ):
        panel = panel_factory(is_final=True)
        panel.diff_paths = {"some.path": DiffResult.REMOVED}

        text, bg = panel._get_diff_colors("some.path")

        assert text is None
        assert bg is None

    def test_get_diff_colors_shows_changed_on_both_panels(self, panel_factory):
        for is_final in (False, True):
            panel = panel_factory(is_final=is_final)
            panel.diff_paths = {"x": DiffResult.CHANGED}

            text, bg = panel._get_diff_colors("x")

            assert text == panel.changed_text
            assert bg == panel.changed_bg


# ----------------------------------------------------------------------------
# Mouse event handling
# ----------------------------------------------------------------------------


class TestHandleEvent:
    def test_handle_event_consumes_mouse_wheel_inside_bounds(
        self, panel_factory, monkeypatch
    ):
        panel = panel_factory(x=0, y=0, width=200, height=200)
        # Force can-scroll state so ScrollState.handle_mousewheel returns True.
        panel.scroll.content_height = 1000
        panel.scroll.viewport_height = 100

        # MOUSEWHEEL events use pygame.mouse.get_pos() for cursor position
        # in the production handler (event.pos isn't read here).
        monkeypatch.setattr(pygame.mouse, "get_pos", lambda: (50, 50))

        event = pygame.event.Event(pygame.MOUSEWHEEL, {"x": 0, "y": -1})
        consumed = panel.handle_event(event)

        assert consumed is True

    def test_handle_event_ignores_mouse_wheel_outside_bounds(
        self, panel_factory, monkeypatch
    ):
        panel = panel_factory(x=0, y=0, width=200, height=200)
        panel.scroll.content_height = 1000
        panel.scroll.viewport_height = 100

        # Cursor outside panel bounds.
        monkeypatch.setattr(pygame.mouse, "get_pos", lambda: (500, 500))

        event = pygame.event.Event(pygame.MOUSEWHEEL, {"x": 0, "y": -1})
        consumed = panel.handle_event(event)

        assert consumed is False

    def test_handle_event_starts_drag_on_scrollbar_mousedown(
        self, panel_factory
    ):
        panel = panel_factory(x=0, y=0, width=200, height=200)
        # Scrollable so the thumb has nonzero size.
        panel.scroll.content_height = 1000
        panel.scroll.viewport_height = 100

        # Click inside the scrollbar zone.
        # _is_in_scrollbar checks x in [width - scrollbar_width - 5, width - 5]
        # and y in [y + 35, y + height - 5].
        sb_x = 200 - panel.scrollbar_width - 5 + 2  # safely inside
        sb_y = 35 + 10  # safely inside

        event = pygame.event.Event(
            pygame.MOUSEBUTTONDOWN,
            {"button": 1, "pos": (sb_x, sb_y)},
        )
        consumed = panel.handle_event(event)

        assert consumed is True
        assert panel.scrollbar_dragging is True


# ----------------------------------------------------------------------------
# _path_has_changes nesting check
# ----------------------------------------------------------------------------


class TestPathHasChanges:
    def test_path_has_changes_matches_direct_and_nested_paths(
        self, panel_factory
    ):
        panel = panel_factory()
        panel.diff_paths = {
            "ships.0.hp": DiffResult.CHANGED,
            "tick_count": DiffResult.CHANGED,
        }

        # Direct hit.
        assert panel._path_has_changes("tick_count") is True
        # Parent path with a child diff.
        assert panel._path_has_changes("ships") is True
        assert panel._path_has_changes("ships.0") is True
        # Unrelated path.
        assert panel._path_has_changes("projectiles") is False
