"""
Unit tests for IControllable interface definition.

PROJ-12 Phase 5: TDD tests written BEFORE implementation.
Tests the AI controllable interface that decouples AI from Ship internals.

Split from test_controllable_interface.py - interface definition tests.
"""

import pytest


# =============================================================================
# Test: IControllable Interface Import and Definition
# =============================================================================

class TestIControllableDefinition:
    """Tests for IControllable interface definition."""

    def test_icontrollable_can_be_imported(self):
        """IControllable can be imported from interfaces module."""
        from game.ai.interfaces.controllable import IControllable

        assert IControllable is not None

    def test_icontrollable_is_protocol_or_abc(self):
        """IControllable is a Protocol or ABC for type checking."""
        from game.ai.interfaces.controllable import IControllable
        from typing import Protocol, runtime_checkable
        import abc

        # Should be either a Protocol or ABC
        is_protocol = isinstance(IControllable, type) and hasattr(IControllable, '__protocol_attrs__')
        is_abc = isinstance(IControllable, abc.ABCMeta)

        assert is_protocol or is_abc

    def test_icontrollable_has_get_position_method(self):
        """IControllable defines get_position method."""
        from game.ai.interfaces.controllable import IControllable

        assert hasattr(IControllable, 'get_position')

    def test_icontrollable_has_get_velocity_method(self):
        """IControllable defines get_velocity method."""
        from game.ai.interfaces.controllable import IControllable

        assert hasattr(IControllable, 'get_velocity')

    def test_icontrollable_has_get_rotation_method(self):
        """IControllable defines get_rotation method."""
        from game.ai.interfaces.controllable import IControllable

        assert hasattr(IControllable, 'get_rotation')

    def test_icontrollable_has_set_throttle_method(self):
        """IControllable defines set_throttle method."""
        from game.ai.interfaces.controllable import IControllable

        assert hasattr(IControllable, 'set_throttle')

    def test_icontrollable_has_set_turn_throttle_method(self):
        """IControllable defines set_turn_throttle method."""
        from game.ai.interfaces.controllable import IControllable

        assert hasattr(IControllable, 'set_turn_throttle')

    def test_icontrollable_has_get_team_id_method(self):
        """IControllable defines get_team_id method."""
        from game.ai.interfaces.controllable import IControllable

        assert hasattr(IControllable, 'get_team_id')

    def test_icontrollable_has_get_weapon_range_method(self):
        """IControllable defines get_weapon_range method."""
        from game.ai.interfaces.controllable import IControllable

        assert hasattr(IControllable, 'get_weapon_range')

    def test_icontrollable_has_is_alive_method(self):
        """IControllable defines is_alive method."""
        from game.ai.interfaces.controllable import IControllable

        assert hasattr(IControllable, 'is_alive')


# =============================================================================
# Test: Extended IControllable Methods (AI-specific)
# =============================================================================

class TestIControllableExtendedMethods:
    """Tests for extended IControllable methods needed by AI."""

    def test_icontrollable_has_rotate_method(self):
        """IControllable defines rotate method for AI to command turns."""
        from game.ai.interfaces.controllable import IControllable

        assert hasattr(IControllable, 'rotate')

    def test_icontrollable_has_thrust_forward_method(self):
        """IControllable defines thrust_forward method."""
        from game.ai.interfaces.controllable import IControllable

        assert hasattr(IControllable, 'thrust_forward')

    def test_icontrollable_has_get_radius_method(self):
        """IControllable defines get_radius for collision detection."""
        from game.ai.interfaces.controllable import IControllable

        assert hasattr(IControllable, 'get_radius')

    def test_icontrollable_has_get_max_speed_method(self):
        """IControllable defines get_max_speed method."""
        from game.ai.interfaces.controllable import IControllable

        assert hasattr(IControllable, 'get_max_speed')

    def test_icontrollable_has_get_current_speed_method(self):
        """IControllable defines get_current_speed method."""
        from game.ai.interfaces.controllable import IControllable

        assert hasattr(IControllable, 'get_current_speed')

    def test_icontrollable_has_get_turn_speed_method(self):
        """IControllable defines get_turn_speed method."""
        from game.ai.interfaces.controllable import IControllable

        assert hasattr(IControllable, 'get_turn_speed')

    def test_icontrollable_has_get_acceleration_rate_method(self):
        """IControllable defines get_acceleration_rate method."""
        from game.ai.interfaces.controllable import IControllable

        assert hasattr(IControllable, 'get_acceleration_rate')

    def test_icontrollable_has_get_is_thrusting_method(self):
        """IControllable defines get_is_thrusting method."""
        from game.ai.interfaces.controllable import IControllable

        assert hasattr(IControllable, 'get_is_thrusting')

    def test_icontrollable_has_set_rotation_method(self):
        """IControllable defines set_rotation method."""
        from game.ai.interfaces.controllable import IControllable

        assert hasattr(IControllable, 'set_rotation')

    def test_icontrollable_has_adjust_position_method(self):
        """IControllable defines adjust_position method."""
        from game.ai.interfaces.controllable import IControllable

        assert hasattr(IControllable, 'adjust_position')

    def test_icontrollable_has_get_layers_method(self):
        """IControllable defines get_layers method for component inspection."""
        from game.ai.interfaces.controllable import IControllable

        assert hasattr(IControllable, 'get_layers')

    def test_icontrollable_has_get_turn_throttle_method(self):
        """IControllable defines get_turn_throttle method (PROJ-24 Phase 6)."""
        from game.ai.interfaces.controllable import IControllable

        assert hasattr(IControllable, 'get_turn_throttle')


# =============================================================================
# Test: Formation Support Methods
# =============================================================================

class TestIControllableFormationMethods:
    """Tests for formation-related IControllable methods."""

    def test_icontrollable_has_get_formation_members_method(self):
        """IControllable defines get_formation_members method."""
        from game.ai.interfaces.controllable import IControllable

        assert hasattr(IControllable, 'get_formation_members')

    def test_icontrollable_has_get_formation_master_method(self):
        """IControllable defines get_formation_master method."""
        from game.ai.interfaces.controllable import IControllable

        assert hasattr(IControllable, 'get_formation_master')

    def test_icontrollable_has_is_in_formation_method(self):
        """IControllable defines is_in_formation method."""
        from game.ai.interfaces.controllable import IControllable

        assert hasattr(IControllable, 'is_in_formation')

    def test_icontrollable_has_get_formation_offset_method(self):
        """IControllable defines get_formation_offset method."""
        from game.ai.interfaces.controllable import IControllable

        assert hasattr(IControllable, 'get_formation_offset')

    def test_icontrollable_has_set_in_formation_method(self):
        """IControllable defines set_in_formation method."""
        from game.ai.interfaces.controllable import IControllable

        assert hasattr(IControllable, 'set_in_formation')

    def test_icontrollable_has_set_formation_master_method(self):
        """IControllable defines set_formation_master method."""
        from game.ai.interfaces.controllable import IControllable

        assert hasattr(IControllable, 'set_formation_master')


# =============================================================================
# Test: Combat State Methods
# =============================================================================

class TestIControllableCombatMethods:
    """Tests for combat-related IControllable methods."""

    def test_icontrollable_has_set_trigger_pulled_method(self):
        """IControllable defines set_trigger_pulled method."""
        from game.ai.interfaces.controllable import IControllable

        assert hasattr(IControllable, 'set_trigger_pulled')

    def test_icontrollable_has_get_current_target_method(self):
        """IControllable defines get_current_target method."""
        from game.ai.interfaces.controllable import IControllable

        assert hasattr(IControllable, 'get_current_target')

    def test_icontrollable_has_set_current_target_method(self):
        """IControllable defines set_current_target method."""
        from game.ai.interfaces.controllable import IControllable

        assert hasattr(IControllable, 'set_current_target')

    def test_icontrollable_has_get_max_targets_method(self):
        """IControllable defines get_max_targets method."""
        from game.ai.interfaces.controllable import IControllable

        assert hasattr(IControllable, 'get_max_targets')

    def test_icontrollable_has_get_secondary_targets_method(self):
        """IControllable defines get_secondary_targets method."""
        from game.ai.interfaces.controllable import IControllable

        assert hasattr(IControllable, 'get_secondary_targets')

    def test_icontrollable_has_set_secondary_targets_method(self):
        """IControllable defines set_secondary_targets method."""
        from game.ai.interfaces.controllable import IControllable

        assert hasattr(IControllable, 'set_secondary_targets')

    def test_icontrollable_has_get_components_by_ability_method(self):
        """IControllable defines get_components_by_ability method."""
        from game.ai.interfaces.controllable import IControllable

        assert hasattr(IControllable, 'get_components_by_ability')
