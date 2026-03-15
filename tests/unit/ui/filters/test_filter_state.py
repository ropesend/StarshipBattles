"""Tests for FilterState enum."""
import pytest

from game.ui.filters.filter_state import FilterState


class TestFilterStateEnum:
    """Tests for the FilterState tri-state enum."""

    def test_yes_value(self):
        assert FilterState.YES.value == "yes"

    def test_no_value(self):
        assert FilterState.NO.value == "no"

    def test_ignore_value(self):
        assert FilterState.IGNORE.value == "ignore"

    def test_has_three_members(self):
        assert len(list(FilterState)) == 3

    def test_identity_from_string_yes(self):
        assert FilterState("yes") is FilterState.YES

    def test_identity_from_string_no(self):
        assert FilterState("no") is FilterState.NO

    def test_identity_from_string_ignore(self):
        assert FilterState("ignore") is FilterState.IGNORE

    def test_invalid_value_raises(self):
        with pytest.raises(ValueError):
            FilterState("invalid")

    def test_serialization_round_trip(self):
        for state in FilterState:
            assert FilterState(state.value) is state
