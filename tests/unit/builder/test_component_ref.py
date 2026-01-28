"""Tests for ComponentRef dataclass pattern.

ComponentRef provides a typed wrapper around component references,
replacing error-prone tuple access patterns like (layer_type, index, component).
"""
from dataclasses import FrozenInstanceError
import pytest
from unittest.mock import MagicMock

from game.core.constants import LayerType
from game.ui.screens.builder.component_ref import ComponentRef


class TestComponentRefBasics:
    """Test ComponentRef creation and basic attributes."""

    def test_create_with_all_fields(self):
        """ComponentRef should accept all fields explicitly."""
        component = MagicMock()
        component.id = "test_component_001"

        ref = ComponentRef(
            component=component,
            layer_type=LayerType.OUTER,
            index=5
        )

        assert ref.component is component
        assert ref.layer_type == LayerType.OUTER
        assert ref.index == 5

    def test_create_with_defaults(self):
        """ComponentRef should allow optional layer_type and index."""
        component = MagicMock()
        component.id = "test_component_002"

        ref = ComponentRef(component=component)

        assert ref.component is component
        assert ref.layer_type is None
        assert ref.index is None

    def test_component_id_property(self):
        """ComponentRef should expose component.id via property."""
        component = MagicMock()
        component.id = "weapon_laser_mk2"

        ref = ComponentRef(component=component, layer_type=LayerType.OUTER, index=0)

        assert ref.component_id == "weapon_laser_mk2"

    def test_is_placed_when_in_layer(self):
        """is_placed should return True when component has layer and index."""
        component = MagicMock()
        component.id = "test"

        ref = ComponentRef(component=component, layer_type=LayerType.HULL, index=0)

        assert ref.is_placed is True

    def test_is_not_placed_when_no_layer(self):
        """is_placed should return False when layer_type is None."""
        component = MagicMock()
        component.id = "test"

        ref = ComponentRef(component=component)

        assert ref.is_placed is False

    def test_is_not_placed_when_no_index(self):
        """is_placed should return False when index is None."""
        component = MagicMock()
        component.id = "test"

        ref = ComponentRef(component=component, layer_type=LayerType.HULL, index=None)

        assert ref.is_placed is False


class TestComponentRefFromTuple:
    """Test migration helper for converting legacy tuples."""

    def test_from_tuple_with_valid_tuple(self):
        """ComponentRef.from_tuple should convert (layer, index, component)."""
        component = MagicMock()
        component.id = "engine_impulse"
        legacy_tuple = (LayerType.CORE, 3, component)

        ref = ComponentRef.from_tuple(legacy_tuple)

        assert ref.component is component
        assert ref.layer_type == LayerType.CORE
        assert ref.index == 3

    def test_from_tuple_preserves_none_values(self):
        """ComponentRef.from_tuple should handle None in tuple."""
        component = MagicMock()
        component.id = "test"
        legacy_tuple = (None, None, component)

        ref = ComponentRef.from_tuple(legacy_tuple)

        assert ref.component is component
        assert ref.layer_type is None
        assert ref.index is None


class TestComponentRefEquality:
    """Test equality and identity semantics."""

    def test_equality_based_on_component_identity(self):
        """Two refs with same component should be equal."""
        component = MagicMock()
        component.id = "test"

        ref1 = ComponentRef(component=component, layer_type=LayerType.HULL, index=0)
        ref2 = ComponentRef(component=component, layer_type=LayerType.HULL, index=0)

        assert ref1 == ref2

    def test_inequality_with_different_components(self):
        """Two refs with different components should not be equal."""
        comp1 = MagicMock()
        comp1.id = "test1"
        comp2 = MagicMock()
        comp2.id = "test2"

        ref1 = ComponentRef(component=comp1, layer_type=LayerType.HULL, index=0)
        ref2 = ComponentRef(component=comp2, layer_type=LayerType.HULL, index=0)

        assert ref1 != ref2

    def test_inequality_with_different_positions(self):
        """Refs with same component but different positions should not be equal."""
        component = MagicMock()
        component.id = "test"

        ref1 = ComponentRef(component=component, layer_type=LayerType.HULL, index=0)
        ref2 = ComponentRef(component=component, layer_type=LayerType.HULL, index=1)

        assert ref1 != ref2


class TestComponentRefHashability:
    """Test that ComponentRef can be used in sets and as dict keys."""

    def test_hashable_for_sets(self):
        """ComponentRef should be usable in sets."""
        component = MagicMock()
        component.id = "test"

        ref = ComponentRef(component=component, layer_type=LayerType.HULL, index=0)

        # Should not raise
        ref_set = {ref}
        assert ref in ref_set

    def test_hashable_for_dict_keys(self):
        """ComponentRef should be usable as dict keys."""
        component = MagicMock()
        component.id = "test"

        ref = ComponentRef(component=component, layer_type=LayerType.HULL, index=0)

        # Should not raise
        ref_dict = {ref: "value"}
        assert ref_dict[ref] == "value"

    def test_hash_stable_across_equal_refs(self):
        """Equal ComponentRefs should have same hash."""
        component = MagicMock()
        component.id = "test"

        ref1 = ComponentRef(component=component, layer_type=LayerType.HULL, index=0)
        ref2 = ComponentRef(component=component, layer_type=LayerType.HULL, index=0)

        assert hash(ref1) == hash(ref2)


class TestComponentRefImmutability:
    """Test that ComponentRef is immutable (frozen)."""

    def test_cannot_modify_component(self):
        """ComponentRef.component should not be reassignable."""
        component = MagicMock()
        component.id = "test"
        ref = ComponentRef(component=component)

        with pytest.raises(FrozenInstanceError):
            ref.component = MagicMock()

    def test_cannot_modify_layer_type(self):
        """ComponentRef.layer_type should not be reassignable."""
        component = MagicMock()
        component.id = "test"
        ref = ComponentRef(component=component, layer_type=LayerType.HULL)

        with pytest.raises(FrozenInstanceError):
            ref.layer_type = LayerType.OUTER

    def test_cannot_modify_index(self):
        """ComponentRef.index should not be reassignable."""
        component = MagicMock()
        component.id = "test"
        ref = ComponentRef(component=component, index=0)

        with pytest.raises(FrozenInstanceError):
            ref.index = 1
