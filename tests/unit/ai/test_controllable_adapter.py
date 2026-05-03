"""
Unit tests for IControllable interface contract.

Tests ABC instantiation behavior and abstract methods set.
"""
import pytest

from game.ai.interfaces.controllable import IControllable


class TestIControllableAbstractContract:
    """Tests for IControllable ABC contract behavior."""

    def test_cannot_instantiate_icontrollable(self):
        """TypeError raised when trying to instantiate IControllable directly."""
        with pytest.raises(TypeError) as exc_info:
            IControllable()

        # Error message should indicate abstract methods
        error_msg = str(exc_info.value)
        assert "abstract" in error_msg.lower() or "instantiate" in error_msg.lower()

    def test_all_abstract_methods_present(self):
        """All expected abstract methods are defined in __abstractmethods__."""
        abstract_methods = IControllable.__abstractmethods__

        # Core movement methods
        assert "get_position" in abstract_methods
        assert "get_velocity" in abstract_methods
        assert "get_rotation" in abstract_methods
        assert "set_throttle" in abstract_methods
        assert "set_turn_throttle" in abstract_methods

        # Combat methods
        assert "get_team_id" in abstract_methods
        assert "get_weapon_range" in abstract_methods
        assert "is_alive" in abstract_methods
        assert "get_current_target" in abstract_methods
        assert "set_current_target" in abstract_methods
