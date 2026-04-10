"""
Tests for pure functions in Combat Lab renderer.

PROJ-266 Phase 3: Tests for _format_check_pair() and _is_condition_verified()
which are extractable pure functions with no pygame dependency.
"""

from unittest.mock import MagicMock, patch


# =============================================================================
# _format_check_pair Tests
# =============================================================================


class TestFormatCheckPair:
    """Tests for TestLabRenderer._format_check_pair()."""

    def _call(self, expected, actual):
        """Call _format_check_pair as a static method."""
        from game.ui.screens.test_lab.renderer import TestLabRenderer
        return TestLabRenderer._format_check_pair(expected, actual)

    def test_both_none_returns_dashes(self):
        exp, act = self._call(None, None)
        assert exp == "—"
        assert act == "—"

    def test_both_boolean(self):
        exp, act = self._call(True, False)
        assert exp == "True"
        assert act == "False"

    def test_expected_boolean_actual_numeric(self):
        """Boolean takes priority over numeric formatting."""
        exp, act = self._call(True, 42)
        assert exp == "True"
        assert act == "42"

    def test_large_numeric_1_decimal(self):
        """Values >= 10000 use 1 decimal place."""
        exp, act = self._call(15000.123, 15000.456)
        assert "15,000.1" in exp
        assert "15,000.5" in act

    def test_medium_numeric_4_decimals(self):
        """Values >= 1 use 4 decimal places."""
        exp, act = self._call(5.123456, 5.654321)
        assert "5.1235" in exp
        assert "5.6543" in act

    def test_small_numeric_6_decimals(self):
        """Values < 1 use 6 decimal places."""
        exp, act = self._call(0.001234, 0.005678)
        assert "0.001234" in exp
        assert "0.005678" in act

    def test_integer_values_still_formatted(self):
        """Integer values get decimal formatting too."""
        exp, act = self._call(100, 200)
        assert "100" in exp
        assert "200" in act

    def test_mixed_types_stringify(self):
        """Mixed types (one string, one numeric) are stringified."""
        exp, act = self._call("hello", 42)
        assert exp == "hello"
        assert act == "42"

    def test_one_none_one_value(self):
        """One None value shows dash."""
        exp, act = self._call(None, 42)
        assert exp == "—"
        assert act == "42"

    def test_both_strings(self):
        exp, act = self._call("foo", "bar")
        assert exp == "foo"
        assert act == "bar"


# =============================================================================
# _is_condition_verified Tests
# =============================================================================


class TestIsConditionVerified:
    """Tests for TestLabRenderer._is_condition_verified()."""

    def _make_renderer(self):
        """Create renderer instance for method calls."""
        from game.ui.screens.test_lab.renderer import TestLabRenderer
        with patch.object(TestLabRenderer, '__init__', lambda self, *a, **kw: None):
            r = TestLabRenderer.__new__(TestLabRenderer)
        return r

    def test_direct_mapping_pass(self):
        """Condition matching a PASS validation returns True."""
        r = self._make_renderer()
        results = [{"name": "Beam Weapon Damage", "status": "PASS", "expected": 5, "actual": 5}]

        assert r._is_condition_verified("Beam Damage: 5 per hit", results) is True

    def test_direct_mapping_fail(self):
        """Condition matching a FAIL validation returns False."""
        r = self._make_renderer()
        results = [{"name": "Beam Weapon Damage", "status": "FAIL", "expected": 5, "actual": 3}]

        assert r._is_condition_verified("Beam Damage: 5 per hit", results) is False

    def test_no_matching_validation(self):
        """Condition with no matching validation returns False."""
        r = self._make_renderer()
        results = [{"name": "Unrelated Check", "status": "PASS", "expected": 1, "actual": 1}]

        assert r._is_condition_verified("Beam Damage: 5 per hit", results) is False

    def test_unmapped_condition_returns_false(self):
        """Condition text not in mapping returns False."""
        r = self._make_renderer()
        results = [{"name": "Something", "status": "PASS", "expected": 1, "actual": 1}]

        assert r._is_condition_verified("Completely Unknown Condition", results) is False

    def test_empty_results_returns_false(self):
        """Empty validation results returns False."""
        r = self._make_renderer()

        assert r._is_condition_verified("Beam Damage: 5", []) is False

    def test_range_penalty_regex_pass(self):
        """Range Penalty with correct arithmetic returns True."""
        r = self._make_renderer()
        results = [{"name": "Accuracy Falloff", "status": "PASS", "expected": 0.002, "actual": 0.002}]

        # 50 * 0.002 = 0.1
        assert r._is_condition_verified("Range Penalty: 50 * 0.002 = 0.1", results) is True

    def test_range_penalty_wrong_arithmetic(self):
        """Range Penalty with wrong arithmetic returns False."""
        r = self._make_renderer()
        results = [{"name": "Accuracy Falloff", "status": "PASS", "expected": 0.002, "actual": 0.002}]

        # 50 * 0.002 = 0.5 is wrong (should be 0.1)
        assert r._is_condition_verified("Range Penalty: 50 * 0.002 = 0.5", results) is False

    def test_range_penalty_falloff_not_verified(self):
        """Range Penalty returns False when falloff isn't verified."""
        r = self._make_renderer()
        results = [{"name": "Accuracy Falloff", "status": "FAIL", "expected": 0.002, "actual": 0.003}]

        assert r._is_condition_verified("Range Penalty: 50 * 0.002 = 0.1", results) is False

    def test_mapped_to_none_returns_false(self):
        """Condition mapped to None (e.g., Distance) returns False."""
        r = self._make_renderer()
        results = [{"name": "Distance", "status": "PASS", "expected": 100, "actual": 100}]

        assert r._is_condition_verified("Distance: 100", results) is False
