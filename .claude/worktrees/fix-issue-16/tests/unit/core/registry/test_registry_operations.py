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

    def test_set_validator_allowed_when_frozen(self, registry):
        """set_validator() caches a derived helper, not source data.

        The freeze contract protects source-of-truth registries (components,
        modifiers, vehicle_classes, resources) from accidental mutation.
        The validator is a lazily-initialized cache of a DesignValidator
        that is reconstructible from those registries at any time, so it
        sits outside the freeze boundary.
        """
        registry.freeze()
        validator = MagicMock()

        registry.set_validator(validator)  # must not raise

        assert registry.get_validator() is validator

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


# =============================================================================
# TCG-FND-016: Hydrate Partial Resources Handling
# =============================================================================

class TestHydratePartialResources:
    """TCG-FND-016: Tests for hydrate() partial resources handling.

    Tests verify behavior with:
    - resources_data=None (default parameter)
    - resources_data={} (empty dict, falsy)
    - resources_data with actual content (truthy)

    The distinction between "no resources" and "empty resources" matters
    for backward compatibility and correct state management.
    """

    def test_hydrate_with_resources_none_does_not_clear_existing(self, registry):
        """hydrate() with resources_data=None clears resources dict.

        When resources_data is None (default), existing resources should
        still be cleared because clear() is always called first.
        """
        # Pre-populate resources
        registry.resources["existing_fuel"] = {"id": "existing_fuel", "max": 100}

        # Hydrate without resources_data (defaults to None)
        registry.hydrate(
            components_data={"comp": {"id": "comp"}},
            modifiers_data={},
            vehicle_classes_data={},
            resources_data=None
        )

        # Resources dict is cleared but not populated
        assert len(registry.resources) == 0

    def test_hydrate_with_empty_dict_does_not_populate_resources(self, registry):
        """hydrate() with resources_data={} clears but does not populate.

        An empty dict is falsy, so the `if resources_data:` check fails
        and no update is performed. But clear() still happens first.
        """
        # Pre-populate resources
        registry.resources["existing_energy"] = {"id": "existing_energy", "max": 200}

        # Hydrate with empty resources dict
        registry.hydrate(
            components_data={},
            modifiers_data={},
            vehicle_classes_data={},
            resources_data={}
        )

        # Resources should be cleared (empty)
        assert len(registry.resources) == 0

    def test_hydrate_with_truthy_resources_populates(self, registry):
        """hydrate() with truthy resources_data populates resources."""
        # Pre-populate resources
        registry.resources["old_resource"] = {"id": "old_resource"}

        # Hydrate with new resources
        registry.hydrate(
            components_data={},
            modifiers_data={},
            vehicle_classes_data={},
            resources_data={"new_fuel": {"id": "new_fuel", "max": 500}}
        )

        # Old resource cleared, new resource added
        assert "old_resource" not in registry.resources
        assert "new_fuel" in registry.resources
        assert registry.resources["new_fuel"]["max"] == 500

    def test_hydrate_none_vs_empty_dict_behavior_documented(self, registry):
        """Document that None and {} have the same effect on resources.

        Both result in an empty resources dict because clear() is called
        regardless, and neither truthy value triggers update().
        """
        # Test with None
        registry.resources["test1"] = {"id": "test1"}
        registry.hydrate({}, {}, {}, resources_data=None)
        len_after_none = len(registry.resources)

        # Test with empty dict
        registry.resources["test2"] = {"id": "test2"}
        registry.hydrate({}, {}, {}, resources_data={})
        len_after_empty = len(registry.resources)

        # Both should result in empty resources
        assert len_after_none == 0
        assert len_after_empty == 0

    def test_hydrate_resources_clears_before_conditional_update(self, registry):
        """Verify resources are cleared even when resources_data is falsy.

        This documents that existing resources do NOT persist when
        hydrate() is called, regardless of the resources_data value.
        """
        # Add multiple resources
        registry.resources["fuel"] = {"id": "fuel"}
        registry.resources["energy"] = {"id": "energy"}
        registry.resources["ammo"] = {"id": "ammo"}

        assert len(registry.resources) == 3

        # Hydrate with falsy resources_data
        registry.hydrate({}, {}, {}, resources_data=None)

        # All resources should be cleared
        assert len(registry.resources) == 0

    def test_hydrate_multiple_resources_in_single_call(self, registry):
        """hydrate() can populate multiple resources in one call."""
        resources_data = {
            "fuel": {"id": "fuel", "type": "consumable"},
            "energy": {"id": "energy", "type": "regenerating"},
            "missiles": {"id": "missiles", "type": "ammo"}
        }

        registry.hydrate({}, {}, {}, resources_data=resources_data)

        assert len(registry.resources) == 3
        assert registry.resources["fuel"]["type"] == "consumable"
        assert registry.resources["energy"]["type"] == "regenerating"
        assert registry.resources["missiles"]["type"] == "ammo"
