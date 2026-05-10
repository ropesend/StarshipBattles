"""Tests for game.ui.fonts module.

PROJ-196 Task 1.2: Font caching and management tests.
"""
import pytest

import pygame

from game.ui.fonts import (
    get_font,
    get_default_font,
    clear_cache,
    FONT_MAIN,
    FONT_MONO,
)


@pytest.fixture(autouse=True)
def pygame_font_init():
    """Ensure pygame font subsystem is initialized.

    Note: We don't call clear_cache() globally because it would invalidate
    fonts cached by other tests running in parallel. Tests that need a
    clean cache state should call clear_cache() explicitly.
    """
    pygame.font.init()
    yield


class TestGetFont:
    """Tests for get_font() system font caching."""

    def test_returns_same_object_for_same_args(self):
        """get_font with identical args should return cached instance."""
        font1 = get_font(24)
        font2 = get_font(24)
        assert font1 is font2

    def test_returns_different_objects_for_different_sizes(self):
        """get_font with different sizes should return different instances."""
        font_small = get_font(12)
        font_large = get_font(24)
        assert font_small is not font_large

    def test_bold_vs_non_bold_returns_different_objects(self):
        """get_font with bold vs non-bold should return different instances."""
        font_normal = get_font(24, bold=False)
        font_bold = get_font(24, bold=True)
        assert font_normal is not font_bold

    def test_with_custom_name(self):
        """get_font with custom font name should cache separately."""
        font_arial = get_font(18, FONT_MAIN)
        font_mono = get_font(18, FONT_MONO)
        assert font_arial is not font_mono

    def test_default_font_name_is_arial(self):
        """get_font default name should be FONT_MAIN (Arial)."""
        font1 = get_font(20)
        font2 = get_font(20, FONT_MAIN)
        assert font1 is font2

    def test_returns_pygame_font(self):
        """get_font should return a pygame.font.Font instance."""
        font = get_font(24)
        assert isinstance(font, pygame.font.Font)


class TestGetDefaultFont:
    """Tests for get_default_font() pygame default font caching."""

    def test_returns_same_object_for_same_size(self):
        """get_default_font with same size should return cached instance."""
        font1 = get_default_font(32)
        font2 = get_default_font(32)
        assert font1 is font2

    def test_returns_different_objects_for_different_sizes(self):
        """get_default_font with different sizes should return different instances."""
        font_small = get_default_font(16)
        font_large = get_default_font(32)
        assert font_small is not font_large

    def test_returns_pygame_font(self):
        """get_default_font should return a pygame.font.Font instance."""
        font = get_default_font(24)
        assert isinstance(font, pygame.font.Font)

    def test_different_from_sys_font(self):
        """get_default_font should return different object than get_font."""
        # These use different cache keys and different font constructors
        default_font = get_default_font(24)
        sys_font = get_font(24)
        # They are different objects (different internal font)
        assert default_font is not sys_font


class TestClearCache:
    """Tests for clear_cache() function."""

    def test_clears_cached_fonts(self):
        """clear_cache should force creation of new font instances."""
        font1 = get_font(24)
        clear_cache()
        font2 = get_font(24)
        # After clearing, should create new instance
        assert font1 is not font2

    def test_clears_default_font_cache_too(self):
        """clear_cache should clear default font cache as well."""
        font1 = get_default_font(32)
        clear_cache()
        font2 = get_default_font(32)
        assert font1 is not font2


class TestFontConstants:
    """Tests for font name constants."""

    def test_font_main_is_arial(self):
        """FONT_MAIN should be 'Arial'."""
        assert FONT_MAIN == "Arial"

    def test_font_mono_is_consolas(self):
        """FONT_MONO should be 'Consolas'."""
        assert FONT_MONO == "Consolas"
