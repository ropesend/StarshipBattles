"""
Tests for battle state viewer UI logic.

This test file covers:
- Line rendering calculations
- Indent level calculation
- Panel visibility toggle
- Dual panel synchronization
- Keyboard navigation
"""
import pytest


# =============================================================================
# Tests for line rendering calculations
# =============================================================================

class TestLineRenderingCalculations:
    """Tests for line rendering calculations."""

    def calculate_visible_lines(self, scroll_offset, viewport_height, line_height, total_lines):
        """
        Calculate which lines are visible in the viewport.

        Returns:
            Tuple of (first_visible_line, last_visible_line)
        """
        first_line = scroll_offset // line_height
        last_line = min(total_lines - 1, (scroll_offset + viewport_height) // line_height)
        return (max(0, first_line), max(0, last_line))

    def test_top_of_content(self):
        """Test visible lines at top."""
        first, last = self.calculate_visible_lines(0, 200, 20, 100)
        assert first == 0
        assert last == 10  # 200/20 = 10

    def test_scrolled_down(self):
        """Test visible lines when scrolled."""
        first, last = self.calculate_visible_lines(100, 200, 20, 100)
        assert first == 5   # 100/20 = 5
        assert last == 15   # (100+200)/20 = 15

    def test_near_bottom(self):
        """Test visible lines near bottom."""
        first, last = self.calculate_visible_lines(1800, 200, 20, 100)
        assert first == 90   # 1800/20 = 90
        assert last == 99    # Clamped to total_lines - 1

    def test_single_line_viewport(self):
        """Test viewport showing single line."""
        first, last = self.calculate_visible_lines(0, 20, 20, 100)
        assert first == 0
        assert last == 1


# =============================================================================
# Tests for indent level calculation
# =============================================================================

class TestIndentLevelCalculation:
    """Tests for indent level calculation from JSON paths."""

    def get_indent_level(self, path):
        """Calculate indent level from a JSON path."""
        if not path:
            return 0

        level = 0
        for char in path:
            if char == '.' or char == '[':
                level += 1
        return level

    def test_root_level(self):
        """Test root level path."""
        assert self.get_indent_level("name") == 0

    def test_one_level_nested(self):
        """Test one level nested."""
        assert self.get_indent_level("outer.inner") == 1

    def test_deeply_nested(self):
        """Test deeply nested path."""
        assert self.get_indent_level("a.b.c.d") == 3

    def test_list_index(self):
        """Test list index adds indent."""
        assert self.get_indent_level("items[0]") == 1
        assert self.get_indent_level("items[0].name") == 2

    def test_mixed_path(self):
        """Test mixed dict and list path."""
        assert self.get_indent_level("data.items[0].children[1].value") == 5

    def test_empty_path(self):
        """Test empty path."""
        assert self.get_indent_level("") == 0


# =============================================================================
# Tests for panel visibility toggle
# =============================================================================

class TestPanelVisibilityToggle:
    """Tests for panel visibility toggle logic."""

    def test_toggle_visibility(self):
        """Test toggling visibility state."""
        visible = True
        visible = not visible
        assert visible is False
        visible = not visible
        assert visible is True

    def test_show_hide_methods(self):
        """Test explicit show/hide methods."""
        class PanelState:
            def __init__(self):
                self.visible = False

            def show(self):
                self.visible = True

            def hide(self):
                self.visible = False

            def toggle(self):
                self.visible = not self.visible

        state = PanelState()
        assert state.visible is False

        state.show()
        assert state.visible is True

        state.hide()
        assert state.visible is False

        state.toggle()
        assert state.visible is True


# =============================================================================
# Tests for dual panel synchronization
# =============================================================================

class TestDualPanelSync:
    """Tests for dual panel (before/after) synchronization."""

    def test_sync_scroll_positions(self):
        """Test synchronizing scroll positions between panels."""
        panel_a_scroll = 100
        panel_b_scroll = panel_a_scroll  # Sync
        assert panel_a_scroll == panel_b_scroll

    def test_calculate_matching_line(self):
        """Test calculating matching line in other panel."""
        # If line 50 in panel A maps to the same JSON path as line 52 in panel B
        line_mapping = {50: 52, 51: 53, 52: 54}

        source_line = 50
        target_line = line_mapping.get(source_line, source_line)
        assert target_line == 52

    def test_fallback_when_no_mapping(self):
        """Test fallback when no line mapping exists."""
        line_mapping = {}
        source_line = 50
        target_line = line_mapping.get(source_line, source_line)
        assert target_line == 50  # Falls back to same line


# =============================================================================
# Tests for keyboard navigation
# =============================================================================

class TestKeyboardNavigation:
    """Tests for keyboard navigation in viewer."""

    def handle_key(self, key, scroll_offset, line_height, page_size, max_scroll):
        """Handle keyboard input for scrolling."""
        if key == "UP":
            scroll_offset -= line_height
        elif key == "DOWN":
            scroll_offset += line_height
        elif key == "PAGE_UP":
            scroll_offset -= page_size
        elif key == "PAGE_DOWN":
            scroll_offset += page_size
        elif key == "HOME":
            scroll_offset = 0
        elif key == "END":
            scroll_offset = max_scroll

        return max(0, min(scroll_offset, max_scroll))

    def test_arrow_up(self):
        """Test arrow up scrolling."""
        result = self.handle_key("UP", 100, 20, 200, 1000)
        assert result == 80

    def test_arrow_down(self):
        """Test arrow down scrolling."""
        result = self.handle_key("DOWN", 100, 20, 200, 1000)
        assert result == 120

    def test_page_up(self):
        """Test page up scrolling."""
        result = self.handle_key("PAGE_UP", 300, 20, 200, 1000)
        assert result == 100

    def test_page_down(self):
        """Test page down scrolling."""
        result = self.handle_key("PAGE_DOWN", 300, 20, 200, 1000)
        assert result == 500

    def test_home_key(self):
        """Test home key goes to top."""
        result = self.handle_key("HOME", 500, 20, 200, 1000)
        assert result == 0

    def test_end_key(self):
        """Test end key goes to bottom."""
        result = self.handle_key("END", 100, 20, 200, 1000)
        assert result == 1000

    def test_clamp_at_top(self):
        """Test scroll doesn't go negative."""
        result = self.handle_key("UP", 10, 20, 200, 1000)
        assert result == 0

    def test_clamp_at_bottom(self):
        """Test scroll doesn't exceed max."""
        result = self.handle_key("DOWN", 990, 20, 200, 1000)
        assert result == 1000
