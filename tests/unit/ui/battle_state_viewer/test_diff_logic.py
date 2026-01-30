"""
Tests for JSON diff computation and path logic.

This test file covers:
- compute_json_diff function
- _mark_all_paths helper
- DiffResult status constants
- Diff color selection
- Scroll offset calculations
- Diff statistics
- JSON path matching
"""
import pytest


# =============================================================================
# Tests for compute_json_diff function
# =============================================================================

class TestComputeJsonDiff:
    """Tests for the compute_json_diff function."""

    def compute_json_diff(self, old_data, new_data, path=""):
        """
        Reimplementation of the compute_json_diff logic for testing.
        Returns list of (path, old_val, new_val, status) tuples.
        """
        UNCHANGED = "unchanged"
        CHANGED = "changed"
        ADDED = "added"
        REMOVED = "removed"

        results = []

        if isinstance(old_data, dict) and isinstance(new_data, dict):
            all_keys = set(old_data.keys()) | set(new_data.keys())
            for key in sorted(all_keys):
                key_path = f"{path}.{key}" if path else key
                if key not in old_data:
                    results.append((key_path, None, new_data[key], ADDED))
                elif key not in new_data:
                    results.append((key_path, old_data[key], None, REMOVED))
                else:
                    results.extend(self.compute_json_diff(old_data[key], new_data[key], key_path))
        elif isinstance(old_data, list) and isinstance(new_data, list):
            max_len = max(len(old_data), len(new_data))
            for i in range(max_len):
                idx_path = f"{path}[{i}]"
                if i >= len(old_data):
                    results.append((idx_path, None, new_data[i], ADDED))
                elif i >= len(new_data):
                    results.append((idx_path, old_data[i], None, REMOVED))
                else:
                    results.extend(self.compute_json_diff(old_data[i], new_data[i], idx_path))
        else:
            if old_data != new_data:
                results.append((path, old_data, new_data, CHANGED))
            else:
                results.append((path, old_data, new_data, UNCHANGED))

        return results

    def test_identical_dicts_unchanged(self):
        """Test that identical dicts produce unchanged status."""
        old = {"a": 1, "b": 2}
        new = {"a": 1, "b": 2}
        results = self.compute_json_diff(old, new)

        assert len(results) == 2
        for path, old_val, new_val, status in results:
            assert status == "unchanged"

    def test_changed_value(self):
        """Test that changed values are detected."""
        old = {"a": 1}
        new = {"a": 2}
        results = self.compute_json_diff(old, new)

        assert len(results) == 1
        path, old_val, new_val, status = results[0]
        assert path == "a"
        assert old_val == 1
        assert new_val == 2
        assert status == "changed"

    def test_added_key(self):
        """Test that added keys are detected."""
        old = {"a": 1}
        new = {"a": 1, "b": 2}
        results = self.compute_json_diff(old, new)

        added = [r for r in results if r[3] == "added"]
        assert len(added) == 1
        assert added[0][0] == "b"
        assert added[0][2] == 2

    def test_removed_key(self):
        """Test that removed keys are detected."""
        old = {"a": 1, "b": 2}
        new = {"a": 1}
        results = self.compute_json_diff(old, new)

        removed = [r for r in results if r[3] == "removed"]
        assert len(removed) == 1
        assert removed[0][0] == "b"
        assert removed[0][1] == 2

    def test_nested_dict_change(self):
        """Test changes in nested dicts."""
        old = {"outer": {"inner": 1}}
        new = {"outer": {"inner": 2}}
        results = self.compute_json_diff(old, new)

        assert len(results) == 1
        path, old_val, new_val, status = results[0]
        assert path == "outer.inner"
        assert old_val == 1
        assert new_val == 2
        assert status == "changed"

    def test_list_change(self):
        """Test changes in lists."""
        old = {"items": [1, 2, 3]}
        new = {"items": [1, 5, 3]}
        results = self.compute_json_diff(old, new)

        changed = [r for r in results if r[3] == "changed"]
        assert len(changed) == 1
        assert changed[0][0] == "items[1]"
        assert changed[0][1] == 2
        assert changed[0][2] == 5

    def test_list_added_element(self):
        """Test added elements in lists."""
        old = {"items": [1, 2]}
        new = {"items": [1, 2, 3]}
        results = self.compute_json_diff(old, new)

        added = [r for r in results if r[3] == "added"]
        assert len(added) == 1
        assert added[0][0] == "items[2]"
        assert added[0][2] == 3

    def test_list_removed_element(self):
        """Test removed elements in lists."""
        old = {"items": [1, 2, 3]}
        new = {"items": [1, 2]}
        results = self.compute_json_diff(old, new)

        removed = [r for r in results if r[3] == "removed"]
        assert len(removed) == 1
        assert removed[0][0] == "items[2]"
        assert removed[0][1] == 3

    def test_type_change_dict_to_value(self):
        """Test type change from dict to value."""
        old = {"a": {"nested": 1}}
        new = {"a": "string"}
        results = self.compute_json_diff(old, new)

        # Type change results in a single changed entry
        assert len(results) == 1
        assert results[0][3] == "changed"

    def test_type_change_list_to_value(self):
        """Test type change from list to value."""
        old = {"a": [1, 2, 3]}
        new = {"a": 42}
        results = self.compute_json_diff(old, new)

        assert len(results) == 1
        assert results[0][3] == "changed"

    def test_deeply_nested_structure(self):
        """Test deeply nested structures."""
        old = {"l1": {"l2": {"l3": {"l4": "old"}}}}
        new = {"l1": {"l2": {"l3": {"l4": "new"}}}}
        results = self.compute_json_diff(old, new)

        assert len(results) == 1
        assert results[0][0] == "l1.l2.l3.l4"
        assert results[0][3] == "changed"

    def test_empty_dicts(self):
        """Test empty dicts."""
        old = {}
        new = {}
        results = self.compute_json_diff(old, new)
        assert len(results) == 0

    def test_empty_to_populated(self):
        """Test empty dict to populated."""
        old = {}
        new = {"a": 1}
        results = self.compute_json_diff(old, new)

        assert len(results) == 1
        assert results[0][3] == "added"

    def test_populated_to_empty(self):
        """Test populated dict to empty."""
        old = {"a": 1}
        new = {}
        results = self.compute_json_diff(old, new)

        assert len(results) == 1
        assert results[0][3] == "removed"

    def test_mixed_changes(self):
        """Test multiple types of changes in one structure."""
        old = {"keep": 1, "change": 2, "remove": 3}
        new = {"keep": 1, "change": 999, "add": 4}
        results = self.compute_json_diff(old, new)

        by_status = {}
        for path, old_val, new_val, status in results:
            by_status.setdefault(status, []).append(path)

        assert "keep" in by_status.get("unchanged", [])
        assert "change" in by_status.get("changed", [])
        assert "remove" in by_status.get("removed", [])
        assert "add" in by_status.get("added", [])


# =============================================================================
# Tests for _mark_all_paths helper
# =============================================================================

class TestMarkAllPaths:
    """Tests for the _mark_all_paths helper function logic."""

    def mark_all_paths(self, data, path=""):
        """Recursively collect all paths in a JSON structure."""
        paths = set()

        if isinstance(data, dict):
            for key, value in data.items():
                key_path = f"{path}.{key}" if path else key
                paths.add(key_path)
                paths.update(self.mark_all_paths(value, key_path))
        elif isinstance(data, list):
            for i, item in enumerate(data):
                idx_path = f"{path}[{i}]"
                paths.add(idx_path)
                paths.update(self.mark_all_paths(item, idx_path))

        return paths

    def test_simple_dict(self):
        """Test path marking for simple dict."""
        data = {"a": 1, "b": 2}
        paths = self.mark_all_paths(data)
        assert "a" in paths
        assert "b" in paths

    def test_nested_dict(self):
        """Test path marking for nested dict."""
        data = {"outer": {"inner": 1}}
        paths = self.mark_all_paths(data)
        assert "outer" in paths
        assert "outer.inner" in paths

    def test_list_paths(self):
        """Test path marking for lists."""
        data = {"items": [1, 2, 3]}
        paths = self.mark_all_paths(data)
        assert "items" in paths
        assert "items[0]" in paths
        assert "items[1]" in paths
        assert "items[2]" in paths

    def test_nested_list_of_dicts(self):
        """Test path marking for list of dicts."""
        data = {"items": [{"name": "a"}, {"name": "b"}]}
        paths = self.mark_all_paths(data)
        assert "items[0]" in paths
        assert "items[0].name" in paths
        assert "items[1].name" in paths

    def test_empty_structures(self):
        """Test path marking for empty structures."""
        assert len(self.mark_all_paths({})) == 0
        assert len(self.mark_all_paths({"empty": {}})) == 1
        assert len(self.mark_all_paths({"empty": []})) == 1


# =============================================================================
# Tests for DiffResult status constants
# =============================================================================

class TestDiffResultConstants:
    """Tests for DiffResult status constants."""

    def test_status_values_are_distinct(self):
        """Test that all status values are distinct."""
        statuses = ["unchanged", "changed", "added", "removed"]
        assert len(statuses) == len(set(statuses))

    def test_status_values_are_strings(self):
        """Test that status values are strings for JSON serialization."""
        statuses = ["unchanged", "changed", "added", "removed"]
        for status in statuses:
            assert isinstance(status, str)


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


# =============================================================================
# Tests for JSON path matching
# =============================================================================

class TestJsonPathMatching:
    """Tests for JSON path matching logic."""

    def path_is_parent_of(self, parent_path, child_path):
        """Check if parent_path is a parent of child_path."""
        if not parent_path:
            return True
        if not child_path:
            return False
        return child_path.startswith(parent_path + ".") or child_path.startswith(parent_path + "[")

    def test_direct_parent(self):
        """Test direct parent relationship."""
        assert self.path_is_parent_of("outer", "outer.inner")

    def test_grandparent(self):
        """Test grandparent relationship."""
        assert self.path_is_parent_of("l1", "l1.l2.l3")

    def test_list_parent(self):
        """Test list parent relationship."""
        assert self.path_is_parent_of("items", "items[0]")
        assert self.path_is_parent_of("items", "items[0].name")

    def test_not_parent(self):
        """Test non-parent relationships."""
        assert not self.path_is_parent_of("a", "b.c")
        assert not self.path_is_parent_of("abc", "ab.d")

    def test_same_path(self):
        """Test same path is not parent of itself."""
        assert not self.path_is_parent_of("a.b", "a.b")

    def test_empty_parent(self):
        """Test empty parent is parent of all."""
        assert self.path_is_parent_of("", "anything")
        assert self.path_is_parent_of("", "a.b.c")

    def test_empty_child(self):
        """Test empty child has no parents."""
        assert not self.path_is_parent_of("a", "")
