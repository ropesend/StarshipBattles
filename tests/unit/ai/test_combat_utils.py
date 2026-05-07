"""
Tests for AI combat utilities.

PROJ-108 Phase 3: Tests for consolidated combat helper functions.
"""
import pytest
from unittest.mock import Mock, MagicMock

from game.ai.combat_utils import (
    is_vector2_like,
    get_capability_cache_key,
    get_entity_id,
    get_position,
    get_rotation,
    get_all_components,
    safe_distance,
    get_hp_percent,
    is_in_pdc_arc,
)
from game.core.math import Vector2


class TestGetEntityId:
    """Tests for get_entity_id helper function."""

    def test_with_name_attribute(self):
        """get_entity_id returns name attribute when present (Ships)."""
        entity = Mock(spec=['name'])
        entity.name = "Destroyer"

        result = get_entity_id(entity)

        assert result == "Destroyer"

    def test_without_name_falls_back_to_object_id(self):
        """get_entity_id falls back to id() when no name (Projectiles)."""
        entity = Mock(spec=[])  # No name attribute

        result = get_entity_id(entity)

        # Should be the string representation of the object id
        assert result == str(id(entity))


class TestGetCapabilityCacheKey:
    """Tests for capability-cache key selection."""

    def test_prefers_runtime_id_over_name(self):
        """Runtime id is the stable capability-cache key for ships."""
        entity = Mock(spec=["id", "name"])
        entity.id = "ship-123"
        entity.name = "Duplicate Name"

        result = get_capability_cache_key(entity)

        assert result == "ship-123"

    def test_falls_back_to_name_when_id_missing(self):
        """Name is retained as a fallback for older tests and mocks."""
        entity = Mock(spec=["name"])
        entity.name = "Legacy Mock"

        result = get_capability_cache_key(entity)

        assert result == "Legacy Mock"

    def test_returns_none_without_id_or_name(self):
        """Entities without stable identity are not cacheable."""
        entity = Mock(spec=[])

        result = get_capability_cache_key(entity)

        assert result is None


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

    def test_with_direct_attribute(self):
        """get_position reads .position attribute for raw entities."""
        entity = Mock(spec=['position', 'name'])
        entity.position = Vector2(50, 75)
        entity.name = "test_entity"

        result = get_position(entity)

        assert result.x == 50
        assert result.y == 75

    def test_returns_none_when_no_position(self):
        """get_position returns None when entity has no position."""
        entity = Mock(spec=['name'])
        entity.name = "no_pos_entity"

        result = get_position(entity)

        assert result is None


class TestGetRotation:
    """Tests for get_rotation function."""

    def test_with_direct_attribute(self):
        """get_rotation reads .angle attribute for raw entities."""
        entity = Mock(spec=['angle', 'name'])
        entity.angle = 90.0
        entity.name = "test_entity"

        result = get_rotation(entity)

        assert result == 90.0

    def test_returns_zero_when_no_angle(self):
        """get_rotation returns 0.0 when entity has no angle."""
        entity = Mock(spec=['name'])
        entity.name = "no_angle_entity"

        result = get_rotation(entity)

        assert result == 0.0

    def test_returns_float(self):
        """get_rotation always returns float."""
        entity = Mock(spec=['angle'])
        entity.angle = 45  # int

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
        entity1 = Mock(spec=['position'])
        entity1.position = Vector2(0, 0)

        entity2 = Mock(spec=['position'])
        entity2.position = Vector2(3, 4)

        result = safe_distance(entity1, entity2)

        assert result == 5.0  # 3-4-5 triangle

    def test_returns_inf_when_position_none(self):
        """safe_distance returns inf when position is None."""
        entity1 = Mock(spec=['name'])
        entity1.name = "e1"

        entity2 = Mock(spec=['name'])
        entity2.name = "e2"

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

    def _make_weapon_mock(self, pdc_range, facing_angle, firing_arc):
        """Create a weapon ability mock with real check_firing_solution.

        PROJ-225: is_in_pdc_arc now delegates to check_firing_solution.
        """
        from game.simulation.components.abilities.weapons import WeaponAbility

        weapon_ability = Mock()
        weapon_ability.range = pdc_range
        weapon_ability.facing_angle = facing_angle
        weapon_ability.firing_arc = firing_arc
        weapon_ability.check_firing_solution = lambda sp, sa, tp: WeaponAbility.check_firing_solution(weapon_ability, sp, sa, tp)
        return weapon_ability

    def test_target_in_arc_returns_true(self):
        """is_in_pdc_arc returns True when target is in PDC arc."""
        weapon_ability = self._make_weapon_mock(100, 0, 90)

        pdc_comp = Mock()
        pdc_comp.has_pdc_ability = Mock(return_value=True)
        pdc_comp.get_ability = Mock(return_value=weapon_ability)

        # Create ship with direct attributes
        ship = Mock(spec=['position', 'angle', 'get_components_by_ability'])
        ship.position = Vector2(0, 0)
        ship.angle = 0
        ship.get_components_by_ability = Mock(return_value=[pdc_comp])

        # Create target in front of ship
        target = Mock(spec=['position'])
        target.position = Vector2(50, 0)

        result = is_in_pdc_arc(ship, target)

        assert result is True

    def test_target_out_of_range_returns_false(self):
        """is_in_pdc_arc returns False when target is out of range."""
        weapon_ability = self._make_weapon_mock(50, 0, 90)

        pdc_comp = Mock()
        pdc_comp.has_pdc_ability = Mock(return_value=True)
        pdc_comp.get_ability = Mock(return_value=weapon_ability)

        ship = Mock(spec=['position', 'angle', 'get_components_by_ability'])
        ship.position = Vector2(0, 0)
        ship.angle = 0
        ship.get_components_by_ability = Mock(return_value=[pdc_comp])

        # Target too far
        target = Mock(spec=['position'])
        target.position = Vector2(100, 0)

        result = is_in_pdc_arc(ship, target)

        assert result is False

    def test_no_pdc_components_returns_false(self):
        """is_in_pdc_arc returns False when ship has no PDC components."""
        ship = Mock(spec=['position', 'get_components_by_ability'])
        ship.position = Vector2(0, 0)
        ship.get_components_by_ability = Mock(return_value=[])

        target = Mock(spec=['position'])
        target.position = Vector2(10, 0)

        result = is_in_pdc_arc(ship, target)

        assert result is False

    def test_no_position_returns_false(self):
        """is_in_pdc_arc returns False when positions unavailable."""
        ship = Mock(spec=['name'])
        ship.name = "ship1"

        target = Mock(spec=['name'])
        target.name = "target1"

        result = is_in_pdc_arc(ship, target)

        assert result is False


# =============================================================================
# TCG-FND-017: is_in_pdc_arc Edge Cases
# =============================================================================

class TestIsInPdcArcEdgeCases:
    """TCG-FND-017: Tests for is_in_pdc_arc edge cases.

    Tests cover:
    - Target at same position as ship (zero-length vector)
    - Target directly behind the ship (180 degrees)
    - Target at exact arc boundary
    """

    def _create_pdc_ship(self, position, rotation, pdc_range, facing_angle, firing_arc):
        """Helper to create a ship with PDC weapon using direct attributes.

        PROJ-225: weapon_ability.check_firing_solution now uses the real
        WeaponAbility method since is_in_pdc_arc delegates to it.
        """
        from game.simulation.components.abilities.weapons import WeaponAbility

        weapon_ability = Mock()
        weapon_ability.range = pdc_range
        weapon_ability.facing_angle = facing_angle
        weapon_ability.firing_arc = firing_arc
        # Bind real check_firing_solution method to the mock
        weapon_ability.check_firing_solution = lambda sp, sa, tp: WeaponAbility.check_firing_solution(weapon_ability, sp, sa, tp)

        pdc_comp = Mock()
        pdc_comp.has_pdc_ability = Mock(return_value=True)
        pdc_comp.get_ability = Mock(return_value=weapon_ability)

        ship = Mock(spec=['position', 'angle', 'get_components_by_ability'])
        ship.position = position
        ship.angle = rotation
        ship.get_components_by_ability = Mock(return_value=[pdc_comp])

        return ship

    def _create_target(self, position):
        """Helper to create a target with direct position attribute."""
        target = Mock(spec=['position'])
        target.position = position
        return target

    def test_target_at_same_position_returns_false(self):
        """Target at same position as ship returns False (zero-length vector).

        This tests the guard: if vec_to_target.length_squared() == 0: continue
        """
        ship = self._create_pdc_ship(
            position=Vector2(100, 100),
            rotation=0,
            pdc_range=100,
            facing_angle=0,
            firing_arc=90
        )

        # Target at exact same position as ship
        target = self._create_target(Vector2(100, 100))

        result = is_in_pdc_arc(ship, target)

        # Should return False - can't determine angle to target at same position
        assert result is False

    def test_target_directly_behind_ship_returns_false(self):
        """Target 180 degrees behind ship is outside 90-degree forward arc."""
        ship = self._create_pdc_ship(
            position=Vector2(0, 0),
            rotation=0,  # Facing right (positive X)
            pdc_range=100,
            facing_angle=0,  # Weapon faces ship's forward direction
            firing_arc=90    # 45 degrees each side of forward
        )

        # Target directly behind ship (negative X)
        target = self._create_target(Vector2(-50, 0))

        result = is_in_pdc_arc(ship, target)

        # 180 degrees from facing is outside 90-degree arc
        assert result is False

    def test_target_at_exact_arc_boundary_inside(self):
        """Target at exactly half the firing arc should be in arc."""
        ship = self._create_pdc_ship(
            position=Vector2(0, 0),
            rotation=0,  # Facing right (positive X)
            pdc_range=100,
            facing_angle=0,
            firing_arc=90  # 45 degrees each side
        )

        # Target at exactly 45 degrees (the boundary)
        # With atan2, 45 degrees above the X axis
        import math
        dist = 50
        x = dist * math.cos(math.radians(45))
        y = dist * math.sin(math.radians(45))
        target = self._create_target(Vector2(x, y))

        result = is_in_pdc_arc(ship, target)

        # At exactly 45 degrees with 90-degree arc (45 each side), should be in
        assert result is True

    def test_target_just_outside_arc_boundary(self):
        """Target just outside the firing arc boundary returns False."""
        ship = self._create_pdc_ship(
            position=Vector2(0, 0),
            rotation=0,  # Facing right (positive X)
            pdc_range=100,
            facing_angle=0,
            firing_arc=90  # 45 degrees each side
        )

        # Target at 50 degrees (just outside 45-degree boundary)
        import math
        dist = 50
        x = dist * math.cos(math.radians(50))
        y = dist * math.sin(math.radians(50))
        target = self._create_target(Vector2(x, y))

        result = is_in_pdc_arc(ship, target)

        # At 50 degrees with 45-degree half-arc, should be outside
        assert result is False

    def test_target_in_rear_arc_with_rear_facing_weapon(self):
        """Target behind ship is in arc if weapon faces rear."""
        ship = self._create_pdc_ship(
            position=Vector2(0, 0),
            rotation=0,  # Ship facing right (positive X)
            pdc_range=100,
            facing_angle=180,  # Weapon faces rear
            firing_arc=90
        )

        # Target behind the ship
        target = self._create_target(Vector2(-50, 0))

        result = is_in_pdc_arc(ship, target)

        # Target is behind ship, weapon faces rear - should be in arc
        assert result is True

    def test_rotated_ship_with_target_in_arc(self):
        """Ship rotation affects arc calculation correctly."""
        ship = self._create_pdc_ship(
            position=Vector2(0, 0),
            rotation=90,  # Ship facing up (positive Y)
            pdc_range=100,
            facing_angle=0,  # Weapon faces ship's forward
            firing_arc=90
        )

        # Target above ship (in front when ship faces up)
        target = self._create_target(Vector2(0, 50))

        result = is_in_pdc_arc(ship, target)

        # Target is in front of rotated ship - should be in arc
        assert result is True

    def test_rotated_ship_with_target_behind(self):
        """Ship rotation affects arc - target behind rotated ship."""
        ship = self._create_pdc_ship(
            position=Vector2(0, 0),
            rotation=90,  # Ship facing up (positive Y)
            pdc_range=100,
            facing_angle=0,
            firing_arc=90
        )

        # Target below ship (behind when ship faces up)
        target = self._create_target(Vector2(0, -50))

        result = is_in_pdc_arc(ship, target)

        # Target is behind rotated ship - should not be in arc
        assert result is False

    def test_wide_firing_arc_covers_180_degrees(self):
        """180-degree firing arc covers front hemisphere."""
        ship = self._create_pdc_ship(
            position=Vector2(0, 0),
            rotation=0,
            pdc_range=100,
            facing_angle=0,
            firing_arc=180  # 90 degrees each side
        )

        # Target at 89 degrees (just within 90-degree half-arc)
        import math
        dist = 50
        x = dist * math.cos(math.radians(89))
        y = dist * math.sin(math.radians(89))
        target = self._create_target(Vector2(x, y))

        result = is_in_pdc_arc(ship, target)

        assert result is True

    def test_very_narrow_firing_arc(self):
        """Very narrow firing arc (10 degrees) still works."""
        ship = self._create_pdc_ship(
            position=Vector2(0, 0),
            rotation=0,
            pdc_range=100,
            facing_angle=0,
            firing_arc=10  # Only 5 degrees each side
        )

        # Target directly in front (0 degrees)
        target = self._create_target(Vector2(50, 0))

        result = is_in_pdc_arc(ship, target)

        assert result is True

    def test_target_at_exact_range_boundary(self):
        """Target at exactly max range is still within range."""
        ship = self._create_pdc_ship(
            position=Vector2(0, 0),
            rotation=0,
            pdc_range=100,
            facing_angle=0,
            firing_arc=90
        )

        # Target at exactly 100 units away (the max range)
        target = self._create_target(Vector2(100, 0))

        result = is_in_pdc_arc(ship, target)

        # At exact range boundary, dist (100) is not > range (100), so should pass range check
        assert result is True

    def test_target_just_past_range_boundary(self):
        """Target just past max range returns False."""
        ship = self._create_pdc_ship(
            position=Vector2(0, 0),
            rotation=0,
            pdc_range=100,
            facing_angle=0,
            firing_arc=90
        )

        # Target at 100.1 units away (just past max range)
        target = self._create_target(Vector2(100.1, 0))

        result = is_in_pdc_arc(ship, target)

        # Just past range - should fail
        assert result is False
