"""
Unit tests for Test Lab Scene UI components.

Tests popup dimensions, scrolling calculations, dialogs, tabs, and scrollbars.
Split from test_test_lab_scene.py - UI component tests.
"""
import pytest


# =============================================================================
# Tests for JSONPopup dimensions and scrolling
# =============================================================================

class TestJSONPopupDimensions:
    """Tests for JSONPopup dimension calculations."""

    def calculate_popup_dimensions(self, screen_width, screen_height, scale=0.8):
        """Calculate popup dimensions (80% of screen)."""
        width = int(screen_width * scale)
        height = int(screen_height * scale)
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        return (x, y, width, height)

    def test_standard_screen_dimensions(self):
        """Test popup dimensions for standard screen."""
        x, y, w, h = self.calculate_popup_dimensions(1920, 1080)
        assert w == 1536  # 1920 * 0.8
        assert h == 864   # 1080 * 0.8
        assert x == 192   # (1920 - 1536) / 2
        assert y == 108   # (1080 - 864) / 2

    def test_small_screen_dimensions(self):
        """Test popup dimensions for small screen."""
        x, y, w, h = self.calculate_popup_dimensions(800, 600)
        assert w == 640  # 800 * 0.8
        assert h == 480  # 600 * 0.8
        assert x == 80   # (800 - 640) / 2
        assert y == 60   # (600 - 480) / 2

    def test_popup_is_centered(self):
        """Test that popup is centered on screen."""
        screen_w, screen_h = 1920, 1080
        x, y, w, h = self.calculate_popup_dimensions(screen_w, screen_h)
        # Check centering
        assert x + w // 2 == screen_w // 2
        assert y + h // 2 == screen_h // 2


class TestJSONPopupScrolling:
    """Tests for JSONPopup scroll logic."""

    def clamp_scroll(self, scroll_offset, total_lines, visible_lines):
        """Clamp scroll offset to valid range."""
        max_scroll = max(0, total_lines - visible_lines)
        return max(0, min(scroll_offset, max_scroll))

    def test_scroll_at_top(self):
        """Test scroll clamped at top."""
        result = self.clamp_scroll(-5, 100, 20)
        assert result == 0

    def test_scroll_at_bottom(self):
        """Test scroll clamped at bottom."""
        result = self.clamp_scroll(90, 100, 20)
        assert result == 80  # max_scroll = 100 - 20 = 80

    def test_scroll_in_middle(self):
        """Test scroll in valid range."""
        result = self.clamp_scroll(50, 100, 20)
        assert result == 50

    def test_short_content_no_scroll(self):
        """Test when content fits in viewport."""
        result = self.clamp_scroll(10, 15, 20)
        assert result == 0  # Can't scroll when content < visible


# =============================================================================
# Tests for ConfirmationDialog dimensions
# =============================================================================

class TestConfirmationDialogDimensions:
    """Tests for ConfirmationDialog dimension calculations."""

    def calculate_dialog_dimensions(self, screen_width, screen_height,
                                    max_width=800, max_height=600, scale=0.6):
        """Calculate dialog dimensions (60% of screen, capped)."""
        width = min(max_width, int(screen_width * scale))
        height = min(max_height, int(screen_height * scale))
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        return (x, y, width, height)

    def test_small_screen_full_scale(self):
        """Test dialog on small screen uses full scale."""
        x, y, w, h = self.calculate_dialog_dimensions(800, 600)
        assert w == 480  # 800 * 0.6 = 480 < 800
        assert h == 360  # 600 * 0.6 = 360 < 600

    def test_large_screen_capped(self):
        """Test dialog on large screen is capped."""
        x, y, w, h = self.calculate_dialog_dimensions(2560, 1440)
        assert w == 800  # Capped at max_width
        assert h == 600  # Capped at max_height

    def test_dialog_is_centered(self):
        """Test that dialog is centered on screen."""
        screen_w, screen_h = 1920, 1080
        x, y, w, h = self.calculate_dialog_dimensions(screen_w, screen_h)
        assert x == (screen_w - w) // 2
        assert y == (screen_h - h) // 2


# =============================================================================
# Tests for ScrollableJSONViewer
# =============================================================================

class TestScrollableJSONViewer:
    """Tests for ScrollableJSONViewer logic."""

    def calculate_visible_lines(self, height, title_height, line_height):
        """Calculate number of visible lines."""
        content_height = height - title_height
        return max(1, content_height // line_height)

    def calculate_max_scroll(self, total_lines, visible_lines):
        """Calculate maximum scroll offset."""
        return max(0, total_lines - visible_lines)

    def test_visible_lines_calculation(self):
        """Test visible lines calculation."""
        result = self.calculate_visible_lines(500, 30, 18)
        # (500 - 30) / 18 = 470 / 18 = 26.1 -> 26
        assert result == 26

    def test_visible_lines_minimum(self):
        """Test visible lines minimum is 1."""
        result = self.calculate_visible_lines(40, 30, 18)
        # (40 - 30) / 18 = 0.5 -> 0, but min is 1
        assert result == 1

    def test_max_scroll_calculation(self):
        """Test max scroll calculation."""
        result = self.calculate_max_scroll(100, 26)
        assert result == 74

    def test_max_scroll_short_content(self):
        """Test max scroll is 0 for short content."""
        result = self.calculate_max_scroll(10, 26)
        assert result == 0


# =============================================================================
# Tests for TabbedShipPanel tab calculations
# =============================================================================

class TestTabbedShipPanelTabs:
    """Tests for TabbedShipPanel tab calculations."""

    def calculate_tab_width(self, panel_width, num_tabs, margin=5, max_tab_width=120):
        """Calculate tab width based on panel and tab count."""
        available_width = panel_width - 20  # 10px padding each side
        calculated_width = available_width // num_tabs - margin
        return min(max_tab_width, calculated_width)

    def test_few_tabs_use_max_width(self):
        """Test that few tabs use maximum width."""
        # Panel 600px wide, 3 tabs: (600-20)/3 - 5 = 188, capped at 120
        result = self.calculate_tab_width(600, 3)
        assert result == 120

    def test_many_tabs_shrink_width(self):
        """Test that many tabs shrink to fit."""
        # Panel 400px wide, 6 tabs: (400-20)/6 - 5 = 58
        result = self.calculate_tab_width(400, 6)
        assert result == 58

    def test_single_tab(self):
        """Test single tab."""
        # Panel 400px wide, 1 tab: (400-20)/1 - 5 = 375, capped at 120
        result = self.calculate_tab_width(400, 1)
        assert result == 120


class TestTabSelection:
    """Tests for tab selection logic."""

    def is_point_in_tab(self, point, tab_rect):
        """Check if point is inside tab rect."""
        x, y = point
        rx, ry, rw, rh = tab_rect
        return rx <= x <= rx + rw and ry <= y <= ry + rh

    def test_point_in_tab(self):
        """Test point inside tab."""
        result = self.is_point_in_tab((150, 50), (100, 30, 100, 30))
        assert result is True

    def test_point_outside_tab(self):
        """Test point outside tab."""
        result = self.is_point_in_tab((50, 50), (100, 30, 100, 30))
        assert result is False

    def test_point_on_edge(self):
        """Test point on tab edge."""
        result = self.is_point_in_tab((100, 30), (100, 30, 100, 30))
        assert result is True


# =============================================================================
# Tests for TestRunDetailsPanel scroll calculations
# =============================================================================

class TestDetailsScrollCalculations:
    """Tests for TestRunDetailsPanel scroll calculations."""

    def calculate_content_height(self, metrics_count, validation_count,
                                  base_height=150, metric_height=20,
                                  validation_height=40, gap=50):
        """Calculate content height based on items."""
        return base_height + metrics_count * metric_height + gap + validation_count * validation_height

    def calculate_max_scroll(self, content_height, visible_height):
        """Calculate max scroll offset."""
        return max(0, content_height - visible_height)

    def test_content_height_calculation(self):
        """Test content height with metrics and validations."""
        # 5 metrics, 3 validations
        result = self.calculate_content_height(5, 3)
        # 150 + 5*20 + 50 + 3*40 = 150 + 100 + 50 + 120 = 420
        assert result == 420

    def test_content_height_no_items(self):
        """Test content height with no items."""
        result = self.calculate_content_height(0, 0)
        # 150 + 0 + 50 + 0 = 200
        assert result == 200

    def test_max_scroll_needed(self):
        """Test max scroll when content exceeds viewport."""
        result = self.calculate_max_scroll(420, 300)
        assert result == 120

    def test_max_scroll_not_needed(self):
        """Test max scroll when content fits."""
        result = self.calculate_max_scroll(200, 300)
        assert result == 0


# =============================================================================
# Tests for scrollbar calculations
# =============================================================================

class TestScrollbarCalculations:
    """Tests for scrollbar thumb position and size."""

    def calculate_thumb_height(self, viewport_height, total_lines, visible_lines, min_height=20):
        """Calculate scrollbar thumb height."""
        if total_lines <= visible_lines:
            return viewport_height
        ratio = visible_lines / total_lines
        return max(min_height, int(viewport_height * ratio))

    def calculate_thumb_position(self, viewport_y, viewport_height, thumb_height,
                                  scroll_offset, max_scroll):
        """Calculate scrollbar thumb Y position."""
        if max_scroll == 0:
            return viewport_y
        scroll_ratio = scroll_offset / max_scroll
        return viewport_y + int((viewport_height - thumb_height) * scroll_ratio)

    def test_thumb_height_short_content(self):
        """Test thumb height when content fits."""
        result = self.calculate_thumb_height(400, 10, 20)
        assert result == 400  # Full viewport height

    def test_thumb_height_long_content(self):
        """Test thumb height with long content."""
        result = self.calculate_thumb_height(400, 100, 20)
        # ratio = 20/100 = 0.2, 400 * 0.2 = 80
        assert result == 80

    def test_thumb_height_minimum(self):
        """Test thumb height respects minimum."""
        result = self.calculate_thumb_height(400, 1000, 20)
        # ratio = 20/1000 = 0.02, 400 * 0.02 = 8, but min is 20
        assert result == 20

    def test_thumb_position_at_top(self):
        """Test thumb position at top of scroll."""
        result = self.calculate_thumb_position(100, 400, 80, 0, 80)
        assert result == 100

    def test_thumb_position_at_bottom(self):
        """Test thumb position at bottom of scroll."""
        result = self.calculate_thumb_position(100, 400, 80, 80, 80)
        # 100 + (400 - 80) * 1.0 = 100 + 320 = 420
        assert result == 420

    def test_thumb_position_in_middle(self):
        """Test thumb position in middle of scroll."""
        result = self.calculate_thumb_position(100, 400, 80, 40, 80)
        # 100 + (400 - 80) * 0.5 = 100 + 160 = 260
        assert result == 260
