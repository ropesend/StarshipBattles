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

    def test_path_has_changes_returns_false_for_empty_diff_paths(
        self, panel_factory
    ):
        panel = panel_factory()
        panel.diff_paths = {}

        assert panel._path_has_changes("anything") is False
        assert panel._path_has_changes("") is False
        assert panel._path_has_changes("ships.0.hp") is False

    def test_path_has_changes_returns_false_for_path_not_in_diff_or_as_prefix(
        self, panel_factory
    ):
        panel = panel_factory()
        panel.diff_paths = {"ships.0.hp": DiffResult.CHANGED}

        # Not present, not a prefix of any diff path.
        assert panel._path_has_changes("crew") is False
        # Substring overlap that is NOT a true dotted-prefix should be False.
        # 'ships.0.h' is a substring of 'ships.0.hp' but the production
        # check uses '<path>.' as a prefix (so 'ships.0.h.' which doesn't match).
        assert panel._path_has_changes("ships.0.h") is False


# ----------------------------------------------------------------------------
# set_json_with_diff: valid JSON happy path
# ----------------------------------------------------------------------------


class TestSetJsonWithDiffValid:
    def test_set_json_with_diff_valid_json_renders_with_diff_coloring(
        self, panel_factory
    ):
        panel = panel_factory(width=400, height=400, is_final=True)

        json_str = '{"hp": 50, "shield": 10}'
        diff_paths = {"hp": DiffResult.CHANGED}

        panel.set_json_with_diff(json_str, diff_paths)

        # Stored diff_paths.
        assert panel.diff_paths == diff_paths
        # Should have produced multiple lines: '{', 'hp: 50,', 'shield: 10', '}'.
        assert len(panel.json_lines) >= 4
        # Scroll content_height = lines * line_height.
        assert panel.scroll.content_height == len(panel.json_lines) * panel.line_height
        # Viewport height = panel height - 40.
        assert panel.scroll.viewport_height == panel.height - 40

        # The 'hp' line should carry the changed_bg background since it's
        # in diff_paths with CHANGED status.
        hp_line = next(
            ln for ln in panel.json_lines
            if isinstance(ln[1], tuple) and '"hp": ' in ln[1][0]
        )
        # line shape: (indent, (key_str, value_str, key_color, value_color), None, bg_color)
        bg_color = hp_line[3]
        assert bg_color == panel.changed_bg


# ----------------------------------------------------------------------------
# _format_json_with_diff: nested structures
# ----------------------------------------------------------------------------


class TestFormatJsonWithDiffNested:
    def test_format_json_with_diff_handles_nested_dict(self, panel_factory):
        panel = panel_factory()
        panel.json_lines = []
        panel.diff_paths = {}

        data = {"outer": {"inner": 1}}
        panel._format_json_with_diff(data, indent=0, path="")

        # Expect: '{', '"outer": {', '"inner": 1', '}', '}'
        assert len(panel.json_lines) == 5
        # Indentation increases for nested content.
        # Line 0: indent 0 (outer-most '{')
        # Line 1: indent 1 ('"outer": {')
        # Line 2: indent 2 ('"inner": 1')
        # Line 3: indent 1 (inner '}')
        # Line 4: indent 0 (outer '}')
        indents = [ln[0] for ln in panel.json_lines]
        assert indents == [0, 1, 2, 1, 0]

    def test_format_json_with_diff_handles_list_of_objects(self, panel_factory):
        panel = panel_factory()
        panel.json_lines = []
        panel.diff_paths = {}

        data = {"ships": [{"hp": 1}, {"hp": 2}]}
        panel._format_json_with_diff(data, indent=0, path="")

        # First-level '{', '"ships": [', then for each list item: '{', 'hp:', '}'
        # then ']' and outer '}'.
        # Confirm at least the list/object brackets exist and the second
        # object's closing brace gets a comma appended (production behavior
        # at lines 205-207 of scrollable_json_panel.py uses prepend-comma to
        # the previous closing brace when not last).
        texts = [ln[1] for ln in panel.json_lines]
        # The outer dict open + ships open + each child rendering.
        assert '{' in texts
        assert any(t == '"ships": [' for t in texts if isinstance(t, str))
        # At least one '},' (intermediate object closing with appended comma).
        assert any(t == '},' for t in texts if isinstance(t, str))
        # Final close braces.
        assert texts[-1] == '}'  # outer dict close
        assert texts[-2] == ']'  # ships list close


# ----------------------------------------------------------------------------
# _handle_scrollbar_drag
# ----------------------------------------------------------------------------


class TestHandleScrollbarDrag:
    def test_handle_scrollbar_drag_updates_scroll_offset_via_set_from_ratio(
        self, panel_factory
    ):
        panel = panel_factory(x=0, y=0, width=200, height=200)
        # Make scrollable so the thumb has a real height.
        panel.scroll.content_height = 1000
        panel.scroll.viewport_height = 100
        panel.drag_start_offset = 0

        # Drag near the bottom of the scrollbar.
        panel._handle_scrollbar_drag(my=180)

        # After drag, scroll offset should be > 0 (we moved down).
        assert panel.scroll.offset > 0

    def test_handle_scrollbar_drag_is_noop_when_available_range_zero(
        self, panel_factory
    ):
        # When content fits in viewport (cannot scroll), the production
        # code path computes available_range <= 0 and skips set_from_ratio.
        panel = panel_factory(x=0, y=0, width=200, height=200)
        panel.scroll.content_height = 50
        panel.scroll.viewport_height = 200
        panel.drag_start_offset = 0

        before = panel.scroll.offset
        panel._handle_scrollbar_drag(my=180)

        assert panel.scroll.offset == before
