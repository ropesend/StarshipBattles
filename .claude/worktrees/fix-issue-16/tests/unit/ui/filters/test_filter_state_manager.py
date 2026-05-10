"""Tests for FilterStateManager base class."""
import pytest

from game.ui.filters.filter_state import FilterState
from game.ui.filters.filter_state_manager import FilterStateManager


@pytest.fixture
def sample_definitions():
    """Sample filter definitions with mixed initial states."""
    return {
        "warp_capable": FilterState.IGNORE,
        "has_spaceyard": FilterState.IGNORE,
        "has_cargo": FilterState.YES,
    }


@pytest.fixture
def manager(sample_definitions):
    return FilterStateManager(sample_definitions)


class TestInitialization:
    def test_stores_initial_states(self, manager):
        assert manager.get_state("warp_capable") is FilterState.IGNORE
        assert manager.get_state("has_spaceyard") is FilterState.IGNORE
        assert manager.get_state("has_cargo") is FilterState.YES

    def test_empty_definitions(self):
        mgr = FilterStateManager({})
        assert mgr.get_all_states() == {}


class TestGetSetState:
    def test_set_state_round_trip(self, manager):
        manager.set_state("warp_capable", FilterState.YES)
        assert manager.get_state("warp_capable") is FilterState.YES

    def test_set_state_to_no(self, manager):
        manager.set_state("has_spaceyard", FilterState.NO)
        assert manager.get_state("has_spaceyard") is FilterState.NO

    def test_get_state_invalid_attribute_raises(self, manager):
        with pytest.raises(KeyError):
            manager.get_state("nonexistent")

    def test_set_state_invalid_attribute_raises(self, manager):
        with pytest.raises(KeyError):
            manager.set_state("nonexistent", FilterState.YES)


class TestGetAllStates:
    def test_returns_all_states(self, manager, sample_definitions):
        result = manager.get_all_states()
        assert result == sample_definitions

    def test_returns_copy_not_reference(self, manager):
        snapshot = manager.get_all_states()
        snapshot["warp_capable"] = FilterState.YES
        # Internal state should be unchanged
        assert manager.get_state("warp_capable") is FilterState.IGNORE


class TestResetAll:
    def test_resets_all_to_ignore(self, manager):
        manager.set_state("warp_capable", FilterState.YES)
        manager.set_state("has_spaceyard", FilterState.NO)
        manager.reset_all()
        for state in manager.get_all_states().values():
            assert state is FilterState.IGNORE

    def test_reset_preserves_keys(self, manager):
        manager.reset_all()
        assert set(manager.get_all_states().keys()) == {
            "warp_capable", "has_spaceyard", "has_cargo"
        }


class TestHasActiveFilters:
    def test_all_ignore_returns_false(self):
        mgr = FilterStateManager({
            "a": FilterState.IGNORE,
            "b": FilterState.IGNORE,
        })
        assert mgr.has_active_filters() is False

    def test_one_yes_returns_true(self):
        mgr = FilterStateManager({
            "a": FilterState.YES,
            "b": FilterState.IGNORE,
        })
        assert mgr.has_active_filters() is True

    def test_one_no_returns_true(self):
        mgr = FilterStateManager({
            "a": FilterState.IGNORE,
            "b": FilterState.NO,
        })
        assert mgr.has_active_filters() is True

    def test_empty_returns_false(self):
        mgr = FilterStateManager({})
        assert mgr.has_active_filters() is False


class TestShouldInclude:
    """Truth table for tri-state inclusion logic."""

    def test_ignore_true_includes(self, manager):
        manager.set_state("warp_capable", FilterState.IGNORE)
        assert manager.should_include("warp_capable", True) is True

    def test_ignore_false_includes(self, manager):
        manager.set_state("warp_capable", FilterState.IGNORE)
        assert manager.should_include("warp_capable", False) is True

    def test_yes_true_includes(self, manager):
        manager.set_state("warp_capable", FilterState.YES)
        assert manager.should_include("warp_capable", True) is True

    def test_yes_false_excludes(self, manager):
        manager.set_state("warp_capable", FilterState.YES)
        assert manager.should_include("warp_capable", False) is False

    def test_no_true_excludes(self, manager):
        manager.set_state("warp_capable", FilterState.NO)
        assert manager.should_include("warp_capable", True) is False

    def test_no_false_includes(self, manager):
        manager.set_state("warp_capable", FilterState.NO)
        assert manager.should_include("warp_capable", False) is True
