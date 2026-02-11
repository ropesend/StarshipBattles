"""
Tests for AI combat utilities.

PROJ-108 Phase 3: Tests for consolidated combat helper functions.
"""
import pytest
from unittest.mock import Mock, MagicMock

from game.ai.combat_utils import (
    is_vector2_like,
    get_position,
    get_rotation,
    get_all_components,
    safe_distance,
    get_hp_percent,
    is_in_pdc_arc,
)
from game.core.math import Vector2


class TestIsVector2Like:
    """Tests for is_vector2_like function."""

    def test_real_vector2_returns_true(self):
        """Real Vector2 object returns True."""
        vec = Vector2(10, 20)
        assert is_vector2_like(vec) is True

    def test_mock_vector2_returns_false(self):
        """MagicMock returns False even with Vector2 attributes."""
        mock = MagicMock()
        mock.x = 10
        mock.y = 20
        mock.distance_to = Mock(return_value=5.0)
        assert is_vector2_like(mock) is False

    def test_regular_object_without_interface_returns_false(self):
        """Object without Vector2 interface returns False."""
        obj = Mock(spec=['foo', 'bar'])
        assert is_vector2_like(obj) is False


class TestGetPosition:
    """Tests for get_position function."""

    def test_with_interface_method(self):
        """get_position uses get_position() interface when available."""
        entity = Mock()
        entity.get_position = Mock(return_value=Vector2(100, 200))

        result = get_position(entity)

        assert result.x == 100
        assert result.y == 200
        entity.get_position.assert_called_once()

    def test_with_direct_attribute_fallback(self):
        """get_position falls back to .position attribute."""
        entity = Mock(spec=['position', 'id'])
        entity.position = Vector2(50, 75)
        entity.id = "test_entity"

        result = get_position(entity)

        assert result.x == 50
        assert result.y == 75

    def test_interface_returns_mock_uses_fallback(self):
        """get_position uses fallback when interface returns mock."""
        entity = Mock()
        entity.get_position = Mock(return_value=MagicMock())  # Returns mock, not real Vector2
        entity.position = Vector2(30, 40)

        result = get_position(entity)

        assert result.x == 30
        assert result.y == 40


class TestGetRotation:
    """Tests for get_rotation function."""

    def test_with_interface_method(self):
        """get_rotation uses get_rotation() interface when available."""
        entity = Mock()
        entity.get_rotation = Mock(return_value=45.0)

        result = get_rotation(entity)

        assert result == 45.0
        entity.get_rotation.assert_called_once()

    def test_with_direct_attribute_fallback(self):
        """get_rotation falls back to .angle attribute."""
        entity = Mock(spec=['angle', 'id'])
        entity.angle = 90.0
        entity.id = "test_entity"

        result = get_rotation(entity)

        assert result == 90.0

    def test_returns_float(self):
        """get_rotation always returns float."""
        entity = Mock()
        entity.get_rotation = Mock(return_value=45)  # int

        result = get_rotation(entity)

        assert isinstance(result, float)
        assert result == 45.0


class TestGetAllComponents:
    """Tests for get_all_components function."""

    def test_with_interface_method(self):
        """get_all_components uses interface when available."""
        comp1 = Mock()
        comp2 = Mock()
        entity = Mock()
        entity.get_all_components = Mock(return_value=[comp1, comp2])

        result = get_all_components(entity)

        assert result == [comp1, comp2]

    def test_without_interface_returns_empty(self):
        """get_all_components returns empty list without interface."""
        entity = Mock(spec=['name'])

        result = get_all_components(entity)

        assert result == []


class TestSafeDistance:
    """Tests for safe_distance function."""

    def test_with_valid_positions(self):
        """safe_distance calculates distance correctly."""
        entity1 = Mock()
        entity1.get_position = Mock(return_value=Vector2(0, 0))

        entity2 = Mock()
        entity2.get_position = Mock(return_value=Vector2(3, 4))

        result = safe_distance(entity1, entity2)

        assert result == 5.0  # 3-4-5 triangle

    def test_returns_inf_when_position_none(self):
        """safe_distance returns inf when position is None."""
        entity1 = Mock(spec=['id'])
        entity1.id = "e1"

        entity2 = Mock(spec=['id'])
        entity2.id = "e2"

        result = safe_distance(entity1, entity2)

        assert result == float('inf')


class TestGetHpPercent:
    """Tests for get_hp_percent function."""

    def test_basic_calculation(self):
        """get_hp_percent calculates percentage correctly."""
        comp1 = Mock()
        comp1.max_hp = 100
        comp1.current_hp = 80

        comp2 = Mock()
        comp2.max_hp = 50
        comp2.current_hp = 25

        ship = Mock()
        ship.get_all_components = Mock(return_value=[comp1, comp2])

        result = get_hp_percent(ship)

        # Total max: 150, total current: 105 -> 0.7
        assert result == 0.7

    def test_no_components_returns_one(self):
        """get_hp_percent returns 1.0 when no components."""
        ship = Mock()
        ship.get_all_components = Mock(return_value=[])

        result = get_hp_percent(ship)

        assert result == 1.0

    def test_zero_max_hp_returns_one(self):
        """get_hp_percent returns 1.0 when max HP is zero."""
        comp = Mock()
        comp.max_hp = 0
        comp.current_hp = 0

        ship = Mock()
        ship.get_all_components = Mock(return_value=[comp])

        result = get_hp_percent(ship)

        assert result == 1.0


class TestIsInPdcArc:
    """Tests for is_in_pdc_arc function."""

    def test_target_in_arc_returns_true(self):
        """is_in_pdc_arc returns True when target is in PDC arc."""
        # Create PDC component
        weapon_ability = Mock()
        weapon_ability.range = 100
        weapon_ability.facing_angle = 0
        weapon_ability.firing_arc = 90

        pdc_comp = Mock()
        pdc_comp.has_pdc_ability = Mock(return_value=True)
        pdc_comp.get_ability = Mock(return_value=weapon_ability)

        # Create ship
        ship = Mock()
        ship.get_position = Mock(return_value=Vector2(0, 0))
        ship.get_rotation = Mock(return_value=0)
        ship.get_components_by_ability = Mock(return_value=[pdc_comp])

        # Create target in front of ship
        target = Mock()
        target.get_position = Mock(return_value=Vector2(50, 0))

        result = is_in_pdc_arc(ship, target)

        assert result is True

    def test_target_out_of_range_returns_false(self):
        """is_in_pdc_arc returns False when target is out of range."""
        weapon_ability = Mock()
        weapon_ability.range = 50
        weapon_ability.facing_angle = 0
        weapon_ability.firing_arc = 90

        pdc_comp = Mock()
        pdc_comp.has_pdc_ability = Mock(return_value=True)
        pdc_comp.get_ability = Mock(return_value=weapon_ability)

        ship = Mock()
        ship.get_position = Mock(return_value=Vector2(0, 0))
        ship.get_rotation = Mock(return_value=0)
        ship.get_components_by_ability = Mock(return_value=[pdc_comp])

        # Target too far
        target = Mock()
        target.get_position = Mock(return_value=Vector2(100, 0))

        result = is_in_pdc_arc(ship, target)

        assert result is False

    def test_no_pdc_components_returns_false(self):
        """is_in_pdc_arc returns False when ship has no PDC components."""
        ship = Mock()
        ship.get_position = Mock(return_value=Vector2(0, 0))
        ship.get_components_by_ability = Mock(return_value=[])

        target = Mock()
        target.get_position = Mock(return_value=Vector2(10, 0))

        result = is_in_pdc_arc(ship, target)

        assert result is False

    def test_no_position_returns_false(self):
        """is_in_pdc_arc returns False when positions unavailable."""
        ship = Mock(spec=['id'])
        ship.id = "ship1"

        target = Mock(spec=['id'])
        target.id = "target1"

        result = is_in_pdc_arc(ship, target)

        assert result is False
