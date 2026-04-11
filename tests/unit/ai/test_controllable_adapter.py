"""
Unit tests for IControllable interface contract.

Tests ABC instantiation behavior, abstract methods set,
and concrete implementation requirements.
"""
import pytest
from unittest.mock import MagicMock

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

    def test_concrete_subclass_must_implement_all(self):
        """Partial implementation raises TypeError on instantiation."""

        class PartialControllable(IControllable):
            """Only implements some methods."""

            def get_position(self):
                return (0, 0)

            def get_velocity(self):
                return (0, 0)

            # Missing all other required methods

        with pytest.raises(TypeError) as exc_info:
            PartialControllable()

        assert "abstract" in str(exc_info.value).lower()


class TestMockImplementation:
    """Tests that a full mock implementation satisfies the interface."""

    def test_mock_implementation_satisfies_interface(self):
        """A complete mock implementation can be instantiated."""

        class MockControllable(IControllable):
            """Full mock implementation of IControllable."""

            def get_position(self):
                return (100.0, 200.0)

            def get_velocity(self):
                return (1.0, 0.0)

            def get_rotation(self):
                return 45.0

            def set_throttle(self, throttle):
                pass

            def set_turn_throttle(self, throttle):
                pass

            def get_turn_throttle(self):
                return 0.0

            def get_team_id(self):
                return 1

            def get_weapon_range(self):
                return 500.0

            def is_alive(self):
                return True

            def rotate(self, angle):
                pass

            def thrust_forward(self):
                pass

            def get_radius(self):
                return 30.0

            def get_max_speed(self):
                return 100.0

            def get_current_speed(self):
                return 50.0

            def get_turn_speed(self):
                return 90.0

            def get_acceleration_rate(self):
                return 10.0

            def get_is_thrusting(self):
                return False

            def set_rotation(self, angle):
                pass

            def adjust_position(self, offset):
                pass

            def get_layers(self):
                return []

            def set_trigger_pulled(self, pulled):
                pass

            def get_current_target(self):
                return None

            def set_current_target(self, target):
                pass

            def get_max_targets(self):
                return 1

            def get_secondary_targets(self):
                return []

            def set_secondary_targets(self, targets):
                pass

            def get_components_by_ability(self, ability_type):
                return []

            def get_all_components(self):
                return []

            def get_ai_strategy(self):
                return None

            def get_vehicle_type(self):
                return "ship"

        # Should instantiate without error
        mock = MockControllable()

        # Verify it works as expected
        assert mock.get_position() == (100.0, 200.0)
        assert mock.is_alive() is True
        assert mock.get_team_id() == 1

    def test_isinstance_check_with_mock(self):
        """isinstance check works with mock implementation."""

        class FullMockControllable(IControllable):
            """Complete implementation for isinstance test."""

            # Implement all abstract methods with minimal stubs
            def get_position(self): return (0, 0)
            def get_velocity(self): return (0, 0)
            def get_rotation(self): return 0.0
            def set_throttle(self, t): pass
            def set_turn_throttle(self, t): pass
            def get_turn_throttle(self): return 0.0
            def get_team_id(self): return 0
            def get_weapon_range(self): return 0.0
            def is_alive(self): return True
            def rotate(self, a): pass
            def thrust_forward(self): pass
            def get_radius(self): return 0.0
            def get_max_speed(self): return 0.0
            def get_current_speed(self): return 0.0
            def get_turn_speed(self): return 0.0
            def get_acceleration_rate(self): return 0.0
            def get_is_thrusting(self): return False
            def set_rotation(self, a): pass
            def adjust_position(self, o): pass
            def get_layers(self): return []
            def set_trigger_pulled(self, p): pass
            def get_current_target(self): return None
            def set_current_target(self, t): pass
            def get_max_targets(self): return 0
            def get_secondary_targets(self): return []
            def set_secondary_targets(self, t): pass
            def get_components_by_ability(self, a): return []
            def get_all_components(self): return []
            def get_ai_strategy(self): return None
            def get_vehicle_type(self): return "ship"

        mock = FullMockControllable()
        assert isinstance(mock, IControllable)
