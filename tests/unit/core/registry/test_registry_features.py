"""
Tests for RegistryManager features: direct access, validator, initialization, edge cases,
GameRegistries container, and default registries functions.
"""

import pytest
from unittest.mock import MagicMock

from game.core.registry import RegistryManager
from game.core.exceptions import StateException


# =============================================================================
# Test: Registry Direct Access (replaces deprecated utility functions)
# =============================================================================

class TestRegistryDirectAccess:
    """Tests for accessing registries directly through RegistryManager."""

    def test_components_dict_accessible(self, registry):
        """RegistryManager.instance().components should return components dict."""
        registry.components["test"] = {"id": "test"}

        result = RegistryManager.instance().components

        assert result is registry.components
        assert "test" in result

    def test_modifiers_dict_accessible(self, registry):
        """RegistryManager.instance().modifiers should return modifiers dict."""
        registry.modifiers["mod"] = {"id": "mod"}

        result = RegistryManager.instance().modifiers

        assert result is registry.modifiers
        assert "mod" in result

    def test_vehicle_classes_dict_accessible(self, registry):
        """RegistryManager.instance().vehicle_classes should return vehicle_classes dict."""
        registry.vehicle_classes["Cruiser"] = {"name": "Cruiser"}

        result = RegistryManager.instance().vehicle_classes

        assert result is registry.vehicle_classes
        assert "Cruiser" in result

    def test_resources_dict_accessible(self, registry):
        """RegistryManager.instance().resources should return resources dict."""
        registry.resources["fuel"] = {"id": "fuel"}

        result = RegistryManager.instance().resources

        assert result is registry.resources
        assert "fuel" in result

    def test_get_validator_returns_validator(self, registry):
        """RegistryManager.instance().get_validator() should return the validator."""
        mock_validator = MagicMock()
        registry.set_validator(mock_validator)

        result = RegistryManager.instance().get_validator()

        assert result is mock_validator

    def test_get_validator_returns_none_when_not_set(self, registry):
        """RegistryManager.instance().get_validator() should return None when not set."""
        result = RegistryManager.instance().get_validator()

        assert result is None


# =============================================================================
# Test: Validator
# =============================================================================

class TestValidator:
    """Tests for validator management."""

    def test_get_validator_initial_none(self, registry):
        """get_validator() should return None initially."""
        assert registry.get_validator() is None

    def test_set_validator_stores_validator(self, registry):
        """set_validator() should store the validator."""
        mock = MagicMock()
        registry.set_validator(mock)

        assert registry.get_validator() is mock

    def test_set_validator_replaces_existing(self, registry):
        """set_validator() should replace existing validator."""
        mock1 = MagicMock()
        mock2 = MagicMock()

        registry.set_validator(mock1)
        registry.set_validator(mock2)

        assert registry.get_validator() is mock2


# =============================================================================
# Test: Initialization
# =============================================================================

class TestInitialization:
    """Tests for registry initialization."""

    def test_initial_components_empty(self, registry):
        """New registry should have empty components."""
        assert registry.components == {}

    def test_initial_modifiers_empty(self, registry):
        """New registry should have empty modifiers."""
        assert registry.modifiers == {}

    def test_initial_vehicle_classes_empty(self, registry):
        """New registry should have empty vehicle_classes."""
        assert registry.vehicle_classes == {}

    def test_initial_resources_empty(self, registry):
        """New registry should have empty resources."""
        assert registry.resources == {}

    def test_initial_validator_none(self, registry):
        """New registry should have validator=None."""
        assert registry._validator is None

    def test_initial_frozen_false(self, registry):
        """New registry should have _frozen=False."""
        assert registry._frozen is False


# =============================================================================
# Test: Edge Cases
# =============================================================================

class TestEdgeCases:
    """Tests for edge cases."""

    def test_empty_string_key(self, registry):
        """Can use empty string as key."""
        registry.components[""] = {"id": ""}

        assert "" in registry.components

    def test_unicode_key(self, registry):
        """Can use unicode keys."""
        registry.components["\u4e2d\u6587"] = {"id": "unicode"}

        assert "\u4e2d\u6587" in registry.components

    def test_none_value(self, registry):
        """Can store None as value."""
        registry.components["test"] = None

        assert registry.components["test"] is None

    def test_complex_nested_value(self, registry):
        """Can store complex nested structures."""
        complex_data = {
            "id": "complex",
            "nested": {
                "level1": {
                    "level2": [1, 2, 3, {"level3": "deep"}]
                }
            }
        }
        registry.components["complex"] = complex_data

        assert registry.components["complex"]["nested"]["level1"]["level2"][3]["level3"] == "deep"

    def test_delete_key(self, registry):
        """Can delete keys from registry dicts."""
        registry.components["test"] = {"id": "test"}
        del registry.components["test"]

        assert "test" not in registry.components

    def test_multiple_clears(self, registry):
        """Multiple clear() calls should not cause issues."""
        registry.components["a"] = {"id": "a"}

        registry.clear()
        registry.clear()
        registry.clear()

        assert len(registry.components) == 0

    def test_hydrate_with_empty_dicts(self, registry):
        """hydrate() with empty dicts should just clear."""
        registry.components["a"] = {"id": "a"}

        registry.hydrate({}, {}, {})

        assert len(registry.components) == 0

    def test_hydrate_with_none_resources(self, registry):
        """hydrate() with None resources should not crash."""
        registry.hydrate(
            components_data={"a": {"id": "a"}},
            modifiers_data={},
            vehicle_classes_data={},
            resources_data=None
        )

        assert len(registry.components) == 1
        assert len(registry.resources) == 0


# =============================================================================
# Test: GameRegistries Container (PROJ-38)
# =============================================================================

class TestGameRegistries:
    """
    Tests for the GameRegistries frozen dataclass container.

    PROJ-38: This container enables DI by bundling all registries together
    as an immutable package that can be passed to consumers.
    """

    def test_game_registries_is_frozen_dataclass(self):
        """GameRegistries should be a frozen dataclass."""
        from game.core.registry import GameRegistries
        from dataclasses import is_dataclass, FrozenInstanceError

        assert is_dataclass(GameRegistries)

        # Create an instance
        gr = GameRegistries(
            components={"a": 1},
            modifiers={"b": 2},
            vehicle_classes={"c": 3},
            resources={"d": 4}
        )

        # Should raise when trying to modify
        with pytest.raises(FrozenInstanceError):
            gr.components = {"new": "value"}

    def test_game_registries_stores_all_registries(self):
        """GameRegistries should store all four registry types."""
        from game.core.registry import GameRegistries

        components = {"laser": {"id": "laser"}}
        modifiers = {"boost": {"id": "boost"}}
        vehicle_classes = {"Cruiser": {"name": "Cruiser"}}
        resources = {"fuel": {"id": "fuel"}}

        gr = GameRegistries(
            components=components,
            modifiers=modifiers,
            vehicle_classes=vehicle_classes,
            resources=resources
        )

        assert gr.components is components
        assert gr.modifiers is modifiers
        assert gr.vehicle_classes is vehicle_classes
        assert gr.resources is resources

    def test_game_registries_requires_all_fields(self):
        """GameRegistries should require all four fields."""
        from game.core.registry import GameRegistries

        # Missing fields should raise TypeError
        with pytest.raises(TypeError):
            GameRegistries(components={})  # Missing modifiers, vehicle_classes, resources

        with pytest.raises(TypeError):
            GameRegistries(
                components={},
                modifiers={}
            )  # Missing vehicle_classes, resources

    def test_game_registries_immutable_but_contents_mutable(self):
        """GameRegistries container is immutable but dicts inside are mutable."""
        from game.core.registry import GameRegistries

        components = {"laser": {"id": "laser"}}
        gr = GameRegistries(
            components=components,
            modifiers={},
            vehicle_classes={},
            resources={}
        )

        # Can modify the dict contents
        gr.components["new_item"] = {"id": "new_item"}

        assert "new_item" in gr.components


# =============================================================================
# Test: Default Registries Functions (PROJ-38)
# =============================================================================

@pytest.mark.filterwarnings("ignore::DeprecationWarning")
class TestDefaultRegistries:
    """
    Tests for set_default_registries() and get_default_registries() functions.

    PROJ-38/PROJ-174: These functions allow setting a global default GameRegistries
    instance for transitional fallback. Now deprecated in favor of IRegistryProvider.
    Tests filter DeprecationWarning since they test the deprecated API itself.
    """

    def test_get_default_registries_raises_when_not_set(self):
        """get_default_registries() should raise StateException when not set."""
        from game.core.registry import get_default_registries, GameRegistries
        import game.core.registry as registry_module

        # Ensure default is not set
        registry_module._default_registries = None

        with pytest.raises(StateException, match="not set"):
            get_default_registries()

    def test_set_default_registries_stores_instance(self):
        """set_default_registries() should store the GameRegistries instance."""
        from game.core.registry import (
            GameRegistries,
            set_default_registries,
            get_default_registries
        )
        import game.core.registry as registry_module

        # Reset state
        registry_module._default_registries = None

        gr = GameRegistries(
            components={"a": 1},
            modifiers={"b": 2},
            vehicle_classes={"c": 3},
            resources={"d": 4}
        )

        set_default_registries(gr)

        result = get_default_registries()
        assert result is gr

    def test_get_default_registries_returns_same_instance(self):
        """get_default_registries() should return the exact same instance."""
        from game.core.registry import (
            GameRegistries,
            set_default_registries,
            get_default_registries
        )
        import game.core.registry as registry_module

        # Reset state
        registry_module._default_registries = None

        gr = GameRegistries(
            components={},
            modifiers={},
            vehicle_classes={},
            resources={}
        )

        set_default_registries(gr)

        result1 = get_default_registries()
        result2 = get_default_registries()

        assert result1 is result2
        assert result1 is gr
