"""
Tests for UI logic in battle state viewer.

This test file covers:
- Diff color selection
- Scroll offset calculations
- Diff statistics
"""
import pytest


# =============================================================================
# Tests for diff color selection logic
# =============================================================================

class TestDiffColorSelection:
    """Tests for diff color selection based on status."""

    def get_diff_color(self, status, is_final=True):
        """
        Get color for a diff status.

        Args:
            status: One of "unchanged", "changed", "added", "removed"
            is_final: Whether this is a final (leaf) value

        Returns:
            RGB tuple for the color
        """
        # Colors from battle_state_viewer.py
        COLOR_UNCHANGED = (180, 180, 180)
        COLOR_CHANGED = (255, 255, 100)      # Yellow
        COLOR_ADDED = (100, 255, 100)        # Green
        COLOR_REMOVED = (255, 100, 100)      # Red
        COLOR_PATH_HIGHLIGHT = (200, 200, 255)  # Light blue for parent paths

        if not is_final:
            # Parent paths of changed items get subtle highlight
            if status in ("changed", "added", "removed"):
                return COLOR_PATH_HIGHLIGHT
            return COLOR_UNCHANGED

        if status == "changed":
            return COLOR_CHANGED
        elif status == "added":
            return COLOR_ADDED
        elif status == "removed":
            return COLOR_REMOVED
        else:
            return COLOR_UNCHANGED

    def test_unchanged_color(self):
        """Test color for unchanged items."""
        color = self.get_diff_color("unchanged")
        assert color == (180, 180, 180)

    def test_changed_color(self):
        """Test color for changed items (yellow)."""
        color = self.get_diff_color("changed")
        assert color == (255, 255, 100)

    def test_added_color(self):
        """Test color for added items (green)."""
        color = self.get_diff_color("added")
        assert color == (100, 255, 100)

    def test_removed_color(self):
        """Test color for removed items (red)."""
        color = self.get_diff_color("removed")
        assert color == (255, 100, 100)

    def test_parent_path_highlight(self):
        """Test that parent paths of changed items get highlighted."""
        color = self.get_diff_color("changed", is_final=False)
        assert color == (200, 200, 255)

    def test_unchanged_parent_no_highlight(self):
        """Test that unchanged parents don't get highlighted."""
        color = self.get_diff_color("unchanged", is_final=False)
        assert color == (180, 180, 180)


# =============================================================================
# Tests for scroll offset calculations
# =============================================================================

class TestScrollOffsetCalculations:
    """Tests for scroll offset calculations."""

    def clamp_scroll(self, scroll_offset, content_height, viewport_height):
        """Clamp scroll offset to valid range."""
        max_scroll = max(0, content_height - viewport_height)
        return max(0, min(scroll_offset, max_scroll))

    def test_scroll_at_top(self):
        """Test scroll clamped at top."""
        result = self.clamp_scroll(-10, 1000, 500)
        assert result == 0

    def test_scroll_at_bottom(self):
        """Test scroll clamped at bottom."""
        result = self.clamp_scroll(600, 1000, 500)
        assert result == 500  # max_scroll = 1000 - 500

    def test_scroll_in_middle(self):
        """Test scroll in valid range."""
        result = self.clamp_scroll(250, 1000, 500)
        assert result == 250

    def test_content_smaller_than_viewport(self):
        """Test when content fits in viewport."""
        result = self.clamp_scroll(100, 400, 500)
        assert result == 0  # max_scroll = 0 when content < viewport

    def test_scroll_by_line(self):
        """Test scrolling by line height."""
        line_height = 20
        current_scroll = 100
        new_scroll = current_scroll + (3 * line_height)  # Scroll 3 lines
        result = self.clamp_scroll(new_scroll, 1000, 500)
        assert result == 160


# =============================================================================
# Tests for diff statistics calculation
# =============================================================================

class TestDiffStatistics:
    """Tests for diff statistics calculation."""

    def calculate_diff_stats(self, diff_results):
        """
        Calculate statistics from diff results.

        Args:
            diff_results: List of (path, old_val, new_val, status) tuples

        Returns:
            Dict with counts by status
        """
        stats = {"unchanged": 0, "changed": 0, "added": 0, "removed": 0}
        for path, old_val, new_val, status in diff_results:
            if status in stats:
                stats[status] += 1
        return stats

    def test_empty_results(self):
        """Test stats for empty results."""
        stats = self.calculate_diff_stats([])
        assert stats["unchanged"] == 0
        assert stats["changed"] == 0
        assert stats["added"] == 0
        assert stats["removed"] == 0

    def test_mixed_results(self):
        """Test stats for mixed results."""
        results = [
            ("a", 1, 1, "unchanged"),
            ("b", 1, 2, "changed"),
            ("c", None, 3, "added"),
            ("d", 4, None, "removed"),
            ("e", 5, 5, "unchanged"),
        ]
        stats = self.calculate_diff_stats(results)
        assert stats["unchanged"] == 2
        assert stats["changed"] == 1
        assert stats["added"] == 1
        assert stats["removed"] == 1

    def test_all_changed(self):
        """Test stats when all items changed."""
        results = [
            ("a", 1, 2, "changed"),
            ("b", 3, 4, "changed"),
        ]
        stats = self.calculate_diff_stats(results)
        assert stats["changed"] == 2
        assert stats["unchanged"] == 0
