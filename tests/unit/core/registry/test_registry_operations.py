"""
Tests for RegistryManager registration, lookup, clear, freeze, and hydrate operations.
"""

import pytest
from unittest.mock import MagicMock

from game.core.registry import RegistryManager
from game.core.exceptions import FrozenStateException


# =============================================================================
# Test: Registration and Lookup
# =============================================================================

class TestRegistrationLookup:
    """Tests for registration and lookup operations."""

    def test_register_component(self, registry):
        """Can register a component."""
        registry.components["test_comp"] = {"id": "test_comp", "name": "Test"}

        assert "test_comp" in registry.components
        assert registry.components["test_comp"]["name"] == "Test"

    def test_register_modifier(self, registry):
        """Can register a modifier."""
        registry.modifiers["test_mod"] = {"id": "test_mod", "value": 10}

        assert "test_mod" in registry.modifiers
        assert registry.modifiers["test_mod"]["value"] == 10

    def test_register_vehicle_class(self, registry):
        """Can register a vehicle class."""
        registry.vehicle_classes["Cruiser"] = {"name": "Cruiser", "mass": 5000}

        assert "Cruiser" in registry.vehicle_classes
        assert registry.vehicle_classes["Cruiser"]["mass"] == 5000

    def test_register_resource(self, registry):
        """Can register a resource."""
        registry.resources["energy"] = {"id": "energy", "max": 100}

        assert "energy" in registry.resources
        assert registry.resources["energy"]["max"] == 100

    def test_lookup_nonexistent_raises_keyerror(self, registry):
        """Looking up nonexistent key raises KeyError."""
        with pytest.raises(KeyError):
            _ = registry.components["nonexistent"]

    def test_get_method_returns_none_for_nonexistent(self, registry):
        """Using .get() returns None for nonexistent key."""
        result = registry.components.get("nonexistent")

        assert result is None

    def test_overwrite_existing_key(self, registry):
        """Can overwrite an existing key."""
        registry.components["test"] = {"version": 1}
        registry.components["test"] = {"version": 2}

        assert registry.components["test"]["version"] == 2


# =============================================================================
# Test: Clear Method
# =============================================================================

class TestClearMethod:
    """Tests for the clear() method."""

    def test_clear_empties_components(self, registry):
        """clear() should empty components dict."""
        registry.components["a"] = {"id": "a"}
        registry.components["b"] = {"id": "b"}

        assert len(registry.components) == 2

        registry.clear()

        assert len(registry.components) == 0

    def test_clear_empties_modifiers(self, registry):
        """clear() should empty modifiers dict."""
        registry.modifiers["m1"] = {"id": "m1"}

        assert len(registry.modifiers) == 1

        registry.clear()

        assert len(registry.modifiers) == 0

    def test_clear_empties_vehicle_classes(self, registry):
        """clear() should empty vehicle_classes dict."""
        registry.vehicle_classes["Cruiser"] = {"name": "Cruiser"}

        assert len(registry.vehicle_classes) == 1

        registry.clear()

        assert len(registry.vehicle_classes) == 0

    def test_clear_empties_resources(self, registry):
        """clear() should empty resources dict."""
        registry.resources["fuel"] = {"id": "fuel"}

        assert len(registry.resources) == 1

        registry.clear()

        assert len(registry.resources) == 0

    def test_clear_resets_validator(self, registry):
        """clear() should set validator to None."""
        mock_validator = MagicMock()
        registry.set_validator(mock_validator)

        assert registry._validator is not None

        registry.clear()

        assert registry._validator is None

    def test_clear_preserves_dict_identity(self, registry):
        """clear() should preserve dict identity (not replace dict)."""
        components_id = id(registry.components)
        modifiers_id = id(registry.modifiers)

        registry.components["test"] = {"id": "test"}
        registry.clear()

        # Same dict objects, just emptied
        assert id(registry.components) == components_id
        assert id(registry.modifiers) == modifiers_id

    def test_clear_raises_when_frozen(self, registry):
        """clear() should raise FrozenStateException when frozen."""
        registry.freeze()

        with pytest.raises(FrozenStateException, match="frozen"):
            registry.clear()


# =============================================================================
# Test: Freeze Functionality
# =============================================================================

class TestFreezeFunctionality:
    """Tests for the freeze() method."""

    def test_freeze_sets_frozen_flag(self, registry):
        """freeze() should set _frozen to True."""
        assert registry._frozen is False

        registry.freeze()

        assert registry._frozen is True

    def test_set_validator_raises_when_frozen(self, registry):
        """set_validator() should raise FrozenStateException when frozen."""
        registry.freeze()

        with pytest.raises(FrozenStateException, match="frozen"):
            registry.set_validator(MagicMock())

    def test_freeze_allows_reads(self, registry):
        """Frozen registry should still allow reads."""
        registry.components["test"] = {"id": "test"}
        registry.freeze()

        # Should not raise
        result = registry.components["test"]
        assert result["id"] == "test"

    def test_freeze_allows_dict_modifications(self, registry):
        """
        BUG DOC: Freeze doesn't prevent direct dict modifications.

        The freeze check only applies to methods that call _check_frozen(),
        not to direct dict operations like components["key"] = value.
        """
        registry.freeze()

        # Direct dict modification bypasses freeze check
        registry.components["new"] = {"id": "new"}

        # BUG: This succeeds even when frozen
        assert "new" in registry.components

    def test_initial_frozen_is_false(self, registry):
        """New registry should have _frozen=False."""
        assert registry._frozen is False


# =============================================================================
# Test: Hydrate Method
# =============================================================================

class TestHydrateMethod:
    """Tests for the hydrate() method."""

    def test_hydrate_populates_components(self, registry):
        """hydrate() should populate components."""
        components_data = {"comp1": {"id": "comp1"}, "comp2": {"id": "comp2"}}

        registry.hydrate(
            components_data=components_data,
            modifiers_data={},
            vehicle_classes_data={}
        )

        assert len(registry.components) == 2
        assert "comp1" in registry.components

    def test_hydrate_populates_modifiers(self, registry):
        """hydrate() should populate modifiers."""
        modifiers_data = {"mod1": {"id": "mod1"}}

        registry.hydrate(
            components_data={},
            modifiers_data=modifiers_data,
            vehicle_classes_data={}
        )

        assert len(registry.modifiers) == 1
        assert "mod1" in registry.modifiers

    def test_hydrate_populates_vehicle_classes(self, registry):
        """hydrate() should populate vehicle_classes."""
        classes_data = {"Cruiser": {"name": "Cruiser"}}

        registry.hydrate(
            components_data={},
            modifiers_data={},
            vehicle_classes_data=classes_data
        )

        assert len(registry.vehicle_classes) == 1
        assert "Cruiser" in registry.vehicle_classes

    def test_hydrate_populates_resources_when_provided(self, registry):
        """hydrate() should populate resources when provided."""
        resources_data = {"fuel": {"id": "fuel"}}

        registry.hydrate(
            components_data={},
            modifiers_data={},
            vehicle_classes_data={},
            resources_data=resources_data
        )

        assert len(registry.resources) == 1
        assert "fuel" in registry.resources

    def test_hydrate_clears_before_populating(self, registry):
        """hydrate() should clear existing data before populating."""
        registry.components["old"] = {"id": "old"}
        registry.modifiers["old_mod"] = {"id": "old_mod"}

        registry.hydrate(
            components_data={"new": {"id": "new"}},
            modifiers_data={"new_mod": {"id": "new_mod"}},
            vehicle_classes_data={}
        )

        assert "old" not in registry.components
        assert "old_mod" not in registry.modifiers
        assert "new" in registry.components
        assert "new_mod" in registry.modifiers

    def test_hydrate_preserves_dict_identity(self, registry):
        """hydrate() should preserve dict identity (update in-place)."""
        components_id = id(registry.components)

        registry.hydrate(
            components_data={"test": {"id": "test"}},
            modifiers_data={},
            vehicle_classes_data={}
        )

        # Same dict object
        assert id(registry.components) == components_id

    def test_hydrate_raises_when_frozen(self, registry):
        """hydrate() should raise FrozenStateException when frozen."""
        registry.freeze()

        with pytest.raises(FrozenStateException, match="frozen"):
            registry.hydrate({}, {}, {})
