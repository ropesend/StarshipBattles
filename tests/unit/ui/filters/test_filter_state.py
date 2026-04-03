"""Tests for FilterState enum."""
import pytest

from game.ui.filters.filter_state import FilterState


class TestFilterStateEnum:
    """Tests for the FilterState tri-state enum."""

    def test_invalid_value_raises(self):
        with pytest.raises(ValueError):
            FilterState("invalid")

    def test_serialization_round_trip(self):
        for state in FilterState:
            assert FilterState(state.value) is state
