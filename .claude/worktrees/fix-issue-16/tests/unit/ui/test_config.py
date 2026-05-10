"""Unit tests for game/ui/config.py

PROJ-142: TCG-UI2-003 - Tests for UIConfig layout constants.
PROJ-157: Removed trivial positivity checks, keeping relationship/validation tests.
"""
import pytest


class TestToastDimensions:
    """Tests for toast notification dimensions."""

    def test_toast_dimensions_reasonable(self):
        """Toast dimensions should be reasonable (not too large)."""
        from game.ui.config import UIConfig
        # Toast should fit on most screens
        assert UIConfig.TOAST_WIDTH <= 500
        assert UIConfig.TOAST_HEIGHT <= 150


class TestDialogDimensions:
    """Tests for dialog dimensions."""

    def test_confirm_dialog_larger_than_toast(self):
        """Confirm dialog should be larger than toast."""
        from game.ui.config import UIConfig
        assert UIConfig.CONFIRM_DIALOG_WIDTH >= UIConfig.TOAST_WIDTH
        assert UIConfig.CONFIRM_DIALOG_HEIGHT >= UIConfig.TOAST_HEIGHT


class TestFontSizes:
    """Tests for font size constants."""

    def test_font_sizes_hierarchy(self):
        """Font sizes should follow visual hierarchy (title > name > stat)."""
        from game.ui.config import UIConfig
        assert UIConfig.FONT_TITLE >= UIConfig.FONT_NAME
        assert UIConfig.FONT_NAME >= UIConfig.FONT_STAT


class TestVisualConstants:
    """Tests for visual appearance constants."""

    def test_panel_alpha_in_range(self):
        """PANEL_ALPHA should be in valid alpha range [0, 255]."""
        from game.ui.config import UIConfig
        assert 0 <= UIConfig.PANEL_ALPHA <= 255


class TestCommonDimensions:
    """Tests for common dimension constants."""

    def test_row_height_large_larger_than_standard(self):
        """ROW_HEIGHT_LARGE should be larger than ROW_HEIGHT_STANDARD."""
        from game.ui.config import UIConfig
        assert UIConfig.ROW_HEIGHT_LARGE >= UIConfig.ROW_HEIGHT_STANDARD


class TestUIConfigAllConstantsAreIntegers:
    """Tests that all UIConfig constants are integers."""

    def test_all_constants_are_integers(self):
        """All UIConfig attributes should be integers."""
        from game.ui.config import UIConfig

        # Get all non-private class attributes
        attributes = [
            attr for attr in dir(UIConfig)
            if not attr.startswith('_') and not callable(getattr(UIConfig, attr))
        ]

        for attr in attributes:
            value = getattr(UIConfig, attr)
            assert isinstance(value, int), f"UIConfig.{attr} should be int, got {type(value)}"
