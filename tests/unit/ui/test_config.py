"""Unit tests for game/ui/config.py

PROJ-142: TCG-UI2-003 - Tests for UIConfig layout constants.
"""
import pytest


class TestUIConfigConstants:
    """Tests for UIConfig constants validation."""

    def test_panel_padding_is_positive(self):
        """PANEL_PADDING should be positive."""
        from game.ui.config import UIConfig
        assert UIConfig.PANEL_PADDING > 0

    def test_panel_gap_is_positive(self):
        """PANEL_GAP should be positive."""
        from game.ui.config import UIConfig
        assert UIConfig.PANEL_GAP > 0

    def test_element_spacing_is_positive(self):
        """ELEMENT_SPACING should be positive."""
        from game.ui.config import UIConfig
        assert UIConfig.ELEMENT_SPACING > 0

    def test_indent_is_positive(self):
        """INDENT should be positive."""
        from game.ui.config import UIConfig
        assert UIConfig.INDENT > 0


class TestToastDimensions:
    """Tests for toast notification dimensions."""

    def test_toast_width_is_positive(self):
        """TOAST_WIDTH should be positive."""
        from game.ui.config import UIConfig
        assert UIConfig.TOAST_WIDTH > 0

    def test_toast_height_is_positive(self):
        """TOAST_HEIGHT should be positive."""
        from game.ui.config import UIConfig
        assert UIConfig.TOAST_HEIGHT > 0

    def test_toast_dimensions_reasonable(self):
        """Toast dimensions should be reasonable (not too large)."""
        from game.ui.config import UIConfig
        # Toast should fit on most screens
        assert UIConfig.TOAST_WIDTH <= 500
        assert UIConfig.TOAST_HEIGHT <= 150


class TestDialogDimensions:
    """Tests for dialog dimensions."""

    def test_confirm_dialog_width_positive(self):
        """CONFIRM_DIALOG_WIDTH should be positive."""
        from game.ui.config import UIConfig
        assert UIConfig.CONFIRM_DIALOG_WIDTH > 0

    def test_confirm_dialog_height_positive(self):
        """CONFIRM_DIALOG_HEIGHT should be positive."""
        from game.ui.config import UIConfig
        assert UIConfig.CONFIRM_DIALOG_HEIGHT > 0

    def test_confirm_dialog_larger_than_toast(self):
        """Confirm dialog should be larger than toast."""
        from game.ui.config import UIConfig
        assert UIConfig.CONFIRM_DIALOG_WIDTH >= UIConfig.TOAST_WIDTH
        assert UIConfig.CONFIRM_DIALOG_HEIGHT >= UIConfig.TOAST_HEIGHT


class TestFontSizes:
    """Tests for font size constants."""

    def test_font_title_is_positive(self):
        """FONT_TITLE should be positive."""
        from game.ui.config import UIConfig
        assert UIConfig.FONT_TITLE > 0

    def test_font_name_is_positive(self):
        """FONT_NAME should be positive."""
        from game.ui.config import UIConfig
        assert UIConfig.FONT_NAME > 0

    def test_font_stat_is_positive(self):
        """FONT_STAT should be positive."""
        from game.ui.config import UIConfig
        assert UIConfig.FONT_STAT > 0

    def test_font_sizes_hierarchy(self):
        """Font sizes should follow visual hierarchy (title > name > stat)."""
        from game.ui.config import UIConfig
        assert UIConfig.FONT_TITLE >= UIConfig.FONT_NAME
        assert UIConfig.FONT_NAME >= UIConfig.FONT_STAT


class TestPanelDimensions:
    """Tests for panel dimensions."""

    def test_stats_panel_width_positive(self):
        """STATS_PANEL_WIDTH should be positive."""
        from game.ui.config import UIConfig
        assert UIConfig.STATS_PANEL_WIDTH > 0

    def test_seeker_panel_width_positive(self):
        """SEEKER_PANEL_WIDTH should be positive."""
        from game.ui.config import UIConfig
        assert UIConfig.SEEKER_PANEL_WIDTH > 0

    def test_strategy_sidebar_width_positive(self):
        """STRATEGY_SIDEBAR_WIDTH should be positive."""
        from game.ui.config import UIConfig
        assert UIConfig.STRATEGY_SIDEBAR_WIDTH > 0

    def test_sidebar_width_positive(self):
        """SIDEBAR_WIDTH should be positive."""
        from game.ui.config import UIConfig
        assert UIConfig.SIDEBAR_WIDTH > 0


class TestBarDimensions:
    """Tests for progress/stat bar dimensions."""

    def test_bar_width_positive(self):
        """BAR_WIDTH should be positive."""
        from game.ui.config import UIConfig
        assert UIConfig.BAR_WIDTH > 0

    def test_bar_height_positive(self):
        """BAR_HEIGHT should be positive."""
        from game.ui.config import UIConfig
        assert UIConfig.BAR_HEIGHT > 0

    def test_banner_height_positive(self):
        """BANNER_HEIGHT should be positive."""
        from game.ui.config import UIConfig
        assert UIConfig.BANNER_HEIGHT > 0

    def test_ship_entry_height_positive(self):
        """SHIP_ENTRY_HEIGHT should be positive."""
        from game.ui.config import UIConfig
        assert UIConfig.SHIP_ENTRY_HEIGHT > 0


class TestVisualConstants:
    """Tests for visual appearance constants."""

    def test_panel_alpha_in_range(self):
        """PANEL_ALPHA should be in valid alpha range [0, 255]."""
        from game.ui.config import UIConfig
        assert 0 <= UIConfig.PANEL_ALPHA <= 255

    def test_panel_alpha_mostly_opaque(self):
        """PANEL_ALPHA should be mostly opaque for readability."""
        from game.ui.config import UIConfig
        assert UIConfig.PANEL_ALPHA >= 128  # At least half opaque


class TestBattleScreenConstants:
    """Tests for battle screen specific constants."""

    def test_grid_spacing_positive(self):
        """GRID_SPACING should be positive."""
        from game.ui.config import UIConfig
        assert UIConfig.GRID_SPACING > 0

    def test_trail_length_positive(self):
        """TRAIL_LENGTH should be positive."""
        from game.ui.config import UIConfig
        assert UIConfig.TRAIL_LENGTH > 0


class TestCommonDimensions:
    """Tests for common dimension constants."""

    def test_row_height_standard_positive(self):
        """ROW_HEIGHT_STANDARD should be positive."""
        from game.ui.config import UIConfig
        assert UIConfig.ROW_HEIGHT_STANDARD > 0

    def test_row_height_large_positive(self):
        """ROW_HEIGHT_LARGE should be positive."""
        from game.ui.config import UIConfig
        assert UIConfig.ROW_HEIGHT_LARGE > 0

    def test_row_height_large_larger_than_standard(self):
        """ROW_HEIGHT_LARGE should be larger than ROW_HEIGHT_STANDARD."""
        from game.ui.config import UIConfig
        assert UIConfig.ROW_HEIGHT_LARGE >= UIConfig.ROW_HEIGHT_STANDARD

    def test_header_height_positive(self):
        """HEADER_HEIGHT should be positive."""
        from game.ui.config import UIConfig
        assert UIConfig.HEADER_HEIGHT > 0


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
