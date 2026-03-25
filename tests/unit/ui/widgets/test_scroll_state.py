"""Tests for ScrollState utility class."""
import pytest
import pygame

from game.ui.widgets.scroll_state import ScrollState


class TestScrollStateInit:
    """Test ScrollState construction and defaults."""

    def test_default_state(self):
        ss = ScrollState()
        assert ss.offset == 0
        assert ss.content_height == 0
        assert ss.viewport_height == 0
        assert ss.step == 20

    def test_custom_step(self):
        ss = ScrollState(step=40)
        assert ss.step == 40

    def test_initial_heights(self):
        ss = ScrollState(content_height=500, viewport_height=200)
        assert ss.content_height == 500
        assert ss.viewport_height == 200


class TestScrollStateMaxOffset:
    """Test max_offset calculation."""

    def test_max_offset_when_content_exceeds_viewport(self):
        ss = ScrollState(content_height=500, viewport_height=200)
        assert ss.max_offset == 300

    def test_max_offset_when_content_fits(self):
        ss = ScrollState(content_height=100, viewport_height=200)
        assert ss.max_offset == 0

    def test_max_offset_equal(self):
        ss = ScrollState(content_height=200, viewport_height=200)
        assert ss.max_offset == 0

    def test_max_offset_zero_heights(self):
        ss = ScrollState(content_height=0, viewport_height=0)
        assert ss.max_offset == 0


class TestScrollStateClamp:
    """Test offset clamping."""

    def test_clamp_negative(self):
        ss = ScrollState(content_height=500, viewport_height=200)
        ss.offset = -10
        ss.clamp()
        assert ss.offset == 0

    def test_clamp_over_max(self):
        ss = ScrollState(content_height=500, viewport_height=200)
        ss.offset = 400
        ss.clamp()
        assert ss.offset == 300

    def test_clamp_within_range(self):
        ss = ScrollState(content_height=500, viewport_height=200)
        ss.offset = 150
        ss.clamp()
        assert ss.offset == 150

    def test_clamp_when_content_fits(self):
        ss = ScrollState(content_height=100, viewport_height=200)
        ss.offset = 50
        ss.clamp()
        assert ss.offset == 0


class TestScrollStateReset:
    """Test offset reset."""

    def test_reset(self):
        ss = ScrollState(content_height=500, viewport_height=200)
        ss.offset = 150
        ss.reset()
        assert ss.offset == 0


class TestScrollStateUpdateContentHeight:
    """Test dynamic content height updates."""

    def test_update_content_height(self):
        ss = ScrollState(content_height=500, viewport_height=200)
        ss.offset = 250
        ss.content_height = 300
        ss.clamp()
        assert ss.offset == 100

    def test_update_viewport_height(self):
        ss = ScrollState(content_height=500, viewport_height=200)
        ss.offset = 250
        ss.viewport_height = 400
        ss.clamp()
        assert ss.offset == 100


class TestScrollStateHandleMousewheel:
    """Test MOUSEWHEEL event handling."""

    def _make_event(self, y: int) -> pygame.event.Event:
        return pygame.event.Event(pygame.MOUSEWHEEL, y=y)

    def test_scroll_down(self):
        ss = ScrollState(content_height=500, viewport_height=200, step=20)
        event = self._make_event(y=-1)
        changed = ss.handle_mousewheel(event)
        assert changed is True
        assert ss.offset == 20

    def test_scroll_up(self):
        ss = ScrollState(content_height=500, viewport_height=200, step=20)
        ss.offset = 100
        event = self._make_event(y=1)
        changed = ss.handle_mousewheel(event)
        assert changed is True
        assert ss.offset == 80

    def test_scroll_clamped_at_top(self):
        ss = ScrollState(content_height=500, viewport_height=200, step=20)
        ss.offset = 5
        event = self._make_event(y=1)
        changed = ss.handle_mousewheel(event)
        assert changed is True
        assert ss.offset == 0

    def test_scroll_clamped_at_bottom(self):
        ss = ScrollState(content_height=500, viewport_height=200, step=20)
        ss.offset = 295
        event = self._make_event(y=-1)
        changed = ss.handle_mousewheel(event)
        assert changed is True
        assert ss.offset == 300

    def test_no_change_at_top(self):
        ss = ScrollState(content_height=500, viewport_height=200, step=20)
        ss.offset = 0
        event = self._make_event(y=1)
        changed = ss.handle_mousewheel(event)
        assert changed is False
        assert ss.offset == 0

    def test_no_change_at_bottom(self):
        ss = ScrollState(content_height=500, viewport_height=200, step=20)
        ss.offset = 300
        event = self._make_event(y=-1)
        changed = ss.handle_mousewheel(event)
        assert changed is False
        assert ss.offset == 300

    def test_no_scroll_when_content_fits(self):
        ss = ScrollState(content_height=100, viewport_height=200, step=20)
        event = self._make_event(y=-1)
        changed = ss.handle_mousewheel(event)
        assert changed is False
        assert ss.offset == 0

    def test_custom_step(self):
        ss = ScrollState(content_height=500, viewport_height=200, step=40)
        event = self._make_event(y=-1)
        ss.handle_mousewheel(event)
        assert ss.offset == 40


class TestScrollStateCanScroll:
    """Test can_scroll property."""

    def test_can_scroll_true(self):
        ss = ScrollState(content_height=500, viewport_height=200)
        assert ss.can_scroll is True

    def test_can_scroll_false(self):
        ss = ScrollState(content_height=100, viewport_height=200)
        assert ss.can_scroll is False


class TestScrollStateScrollRatio:
    """Test scroll_ratio property for scrollbar thumb positioning."""

    def test_ratio_at_top(self):
        ss = ScrollState(content_height=500, viewport_height=200)
        assert ss.scroll_ratio == 0.0

    def test_ratio_at_bottom(self):
        ss = ScrollState(content_height=500, viewport_height=200)
        ss.offset = 300
        assert ss.scroll_ratio == 1.0

    def test_ratio_midway(self):
        ss = ScrollState(content_height=500, viewport_height=200)
        ss.offset = 150
        assert ss.scroll_ratio == 0.5

    def test_ratio_when_no_scroll(self):
        ss = ScrollState(content_height=100, viewport_height=200)
        assert ss.scroll_ratio == 0.0


class TestScrollStateSetFromRatio:
    """Test set_from_ratio for scrollbar drag."""

    def test_set_from_ratio_zero(self):
        ss = ScrollState(content_height=500, viewport_height=200)
        ss.set_from_ratio(0.0)
        assert ss.offset == 0

    def test_set_from_ratio_one(self):
        ss = ScrollState(content_height=500, viewport_height=200)
        ss.set_from_ratio(1.0)
        assert ss.offset == 300

    def test_set_from_ratio_half(self):
        ss = ScrollState(content_height=500, viewport_height=200)
        ss.set_from_ratio(0.5)
        assert ss.offset == 150

    def test_set_from_ratio_clamps_above(self):
        ss = ScrollState(content_height=500, viewport_height=200)
        ss.set_from_ratio(1.5)
        assert ss.offset == 300

    def test_set_from_ratio_clamps_below(self):
        ss = ScrollState(content_height=500, viewport_height=200)
        ss.set_from_ratio(-0.5)
        assert ss.offset == 0
