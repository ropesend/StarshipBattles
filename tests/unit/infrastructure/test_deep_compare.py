"""Tests for the deep_compare utility used in save/load round-trip verification."""

import pytest

from tests.infrastructure.deep_compare import ComparisonResult, deep_compare


class TestDeepCompareIdentical:
    """Identical dicts should produce no differences."""

    def test_empty_dicts(self):
        assert deep_compare({}, {}) == []

    def test_flat_dict(self):
        d = {"a": 1, "b": "hello", "c": True}
        assert deep_compare(d, d.copy()) == []

    def test_nested_dict(self):
        d = {"a": {"b": {"c": 1}}}
        assert deep_compare(d, {"a": {"b": {"c": 1}}}) == []

    def test_with_lists(self):
        d = {"items": [1, 2, 3], "name": "test"}
        assert deep_compare(d, {"items": [1, 2, 3], "name": "test"}) == []

    def test_with_none_values(self):
        d = {"a": None, "b": 1}
        assert deep_compare(d, {"a": None, "b": 1}) == []


class TestDeepCompareMissingKeys:
    """Missing keys should be reported with path."""

    def test_missing_key_in_loaded(self):
        results = deep_compare({"a": 1, "b": 2}, {"a": 1})
        assert len(results) == 1
        assert results[0].path == "b"
        assert results[0].expected == 2
        assert results[0].actual is None
        assert "missing" in results[0].message.lower()

    def test_missing_nested_key(self):
        original = {"outer": {"a": 1, "b": 2}}
        loaded = {"outer": {"a": 1}}
        results = deep_compare(original, loaded)
        assert len(results) == 1
        assert results[0].path == "outer.b"


class TestDeepCompareExtraKeys:
    """Extra keys in loaded dict should be reported."""

    def test_extra_key_in_loaded(self):
        results = deep_compare({"a": 1}, {"a": 1, "b": 2})
        assert len(results) == 1
        assert results[0].path == "b"
        assert "extra" in results[0].message.lower() or "unexpected" in results[0].message.lower()

    def test_extra_nested_key(self):
        original = {"outer": {"a": 1}}
        loaded = {"outer": {"a": 1, "b": 2}}
        results = deep_compare(original, loaded)
        assert len(results) == 1
        assert results[0].path == "outer.b"


class TestDeepCompareValueDifferences:
    """Value differences should report path, expected, and actual."""

    def test_int_difference(self):
        results = deep_compare({"a": 1}, {"a": 2})
        assert len(results) == 1
        assert results[0].path == "a"
        assert results[0].expected == 1
        assert results[0].actual == 2

    def test_string_difference(self):
        results = deep_compare({"name": "alpha"}, {"name": "beta"})
        assert len(results) == 1
        assert results[0].path == "name"
        assert results[0].expected == "alpha"
        assert results[0].actual == "beta"

    def test_bool_difference(self):
        results = deep_compare({"flag": True}, {"flag": False})
        assert len(results) == 1
        assert results[0].path == "flag"

    def test_type_difference(self):
        results = deep_compare({"a": 1}, {"a": "1"})
        assert len(results) == 1
        assert results[0].path == "a"


class TestDeepCompareNestedDifferences:
    """Nested dict differences should have full path."""

    def test_deeply_nested_difference(self):
        original = {"galaxy": {"systems": [{"system": {"planets": [{"mass": 1.0}]}}]}}
        loaded = {"galaxy": {"systems": [{"system": {"planets": [{"mass": 2.0}]}}]}}
        results = deep_compare(original, loaded)
        assert len(results) == 1
        assert "galaxy" in results[0].path
        assert "systems" in results[0].path
        assert "planets" in results[0].path
        assert "mass" in results[0].path

    def test_multiple_nested_differences(self):
        original = {"a": {"x": 1, "y": 2}, "b": {"z": 3}}
        loaded = {"a": {"x": 10, "y": 2}, "b": {"z": 30}}
        results = deep_compare(original, loaded)
        assert len(results) == 2
        paths = {r.path for r in results}
        assert "a.x" in paths
        assert "b.z" in paths


class TestDeepCompareListOrdering:
    """Lists should be compared with ordering by default."""

    def test_same_elements_different_order(self):
        results = deep_compare({"items": [1, 2, 3]}, {"items": [3, 2, 1]})
        assert len(results) > 0  # Order matters for lists

    def test_list_length_difference(self):
        results = deep_compare({"items": [1, 2]}, {"items": [1, 2, 3]})
        assert len(results) > 0

    def test_list_with_index_path(self):
        results = deep_compare({"items": [1, 2, 3]}, {"items": [1, 99, 3]})
        assert len(results) == 1
        assert "items[1]" in results[0].path


class TestDeepCompareFloatTolerance:
    """Float comparison should use configurable tolerance."""

    def test_within_default_tolerance(self):
        results = deep_compare({"val": 1.0}, {"val": 1.0 + 1e-11})
        assert results == []

    def test_outside_default_tolerance(self):
        results = deep_compare({"val": 1.0}, {"val": 1.0 + 1e-9})
        assert len(results) == 1

    def test_custom_tolerance(self):
        results = deep_compare({"val": 1.0}, {"val": 1.001}, float_tolerance=0.01)
        assert results == []

    def test_custom_tolerance_exceeded(self):
        results = deep_compare({"val": 1.0}, {"val": 1.1}, float_tolerance=0.01)
        assert len(results) == 1

    def test_very_small_floats(self):
        """Spectrum values can be as small as 1e-47."""
        val = 1.23e-47
        results = deep_compare({"spectrum": val}, {"spectrum": val})
        assert results == []

    def test_zero_float_comparison(self):
        results = deep_compare({"val": 0.0}, {"val": 0.0})
        assert results == []


class TestDeepCompareNoneHandling:
    """None vs missing key should be distinguished."""

    def test_none_value_matches_none(self):
        results = deep_compare({"a": None}, {"a": None})
        assert results == []

    def test_none_vs_missing_key(self):
        """A key with value None is different from a missing key."""
        results = deep_compare({"a": None, "b": 1}, {"b": 1})
        assert len(results) == 1
        assert results[0].path == "a"

    def test_none_vs_value(self):
        results = deep_compare({"a": None}, {"a": 1})
        assert len(results) == 1

    def test_value_vs_none(self):
        results = deep_compare({"a": 1}, {"a": None})
        assert len(results) == 1


class TestDeepCompareUnorderedLists:
    """Sets serialized as lists should support unordered comparison."""

    def test_unordered_comparison(self):
        results = deep_compare(
            {"designs": [3, 1, 2]},
            {"designs": [1, 2, 3]},
            unordered_lists={"designs"},
        )
        assert results == []

    def test_unordered_with_nested_path(self):
        results = deep_compare(
            {"empire": {"designs": ["b", "a", "c"]}},
            {"empire": {"designs": ["c", "b", "a"]}},
            unordered_lists={"empire.designs"},
        )
        assert results == []

    def test_unordered_different_elements(self):
        results = deep_compare(
            {"designs": [1, 2, 3]},
            {"designs": [1, 2, 4]},
            unordered_lists={"designs"},
        )
        assert len(results) > 0

    def test_unordered_different_lengths(self):
        results = deep_compare(
            {"designs": [1, 2]},
            {"designs": [1, 2, 3]},
            unordered_lists={"designs"},
        )
        assert len(results) > 0


class TestDeepCompareIgnoreFields:
    """Ignored fields should not produce differences."""

    def test_ignore_top_level_field(self):
        results = deep_compare(
            {"a": 1, "b": 2},
            {"a": 1, "b": 99},
            ignore_fields={"b"},
        )
        assert results == []

    def test_ignore_nested_field(self):
        results = deep_compare(
            {"outer": {"a": 1, "b": 2}},
            {"outer": {"a": 1, "b": 99}},
            ignore_fields={"outer.b"},
        )
        assert results == []

    def test_non_ignored_field_still_reported(self):
        results = deep_compare(
            {"a": 1, "b": 2},
            {"a": 99, "b": 99},
            ignore_fields={"b"},
        )
        assert len(results) == 1
        assert results[0].path == "a"


class TestComparisonResult:
    """ComparisonResult dataclass should have correct fields."""

    def test_fields(self):
        r = ComparisonResult(path="a.b", expected=1, actual=2, message="value differs")
        assert r.path == "a.b"
        assert r.expected == 1
        assert r.actual == 2
        assert r.message == "value differs"

    def test_repr(self):
        r = ComparisonResult(path="a", expected=1, actual=2, message="differs")
        s = repr(r)
        assert "a" in s
