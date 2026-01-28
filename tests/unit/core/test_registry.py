"""
Comprehensive tests for game/core/registry.py (RegistryManager)

This test file focuses on:
- Singleton behavior
- Thread safety
- Registration/lookup
- Clear/reset methods
- Freeze functionality
- Test isolation (critical bug identified in review)
- Utility functions (get_component_registry, etc.)
- Hydrate functionality
"""
import pytest
import threading
from unittest.mock import MagicMock


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture(autouse=True)
def reset_registry():
    """Reset registry state before and after each test.

    This fixture provides a clean singleton instance for each test in this file,
    then restores the original instance AND its data afterward to prevent
    pollution of other test files that run later in the suite.

    We save both the instance reference AND copies of its data, because the
    reset_singletons fixture (in root conftest) may clear the data between tests.

    Also saves/restores _default_registries module variable.
    """
    from game.core.registry import RegistryManager
    import game.core.registry as registry_module

    # Store original instance AND its data to restore after test
    original_instance = RegistryManager._instance
    original_default_registries = registry_module._default_registries
    original_data = None
    if original_instance is not None:
        # Deep copy the data in case it gets cleared during the test
        original_data = {
            'components': dict(original_instance.components),
            'modifiers': dict(original_instance.modifiers),
            'vehicle_classes': dict(original_instance.vehicle_classes),
            'resources': dict(original_instance.resources),
        }

    # Reset to clean state for this test
    RegistryManager.reset()

    yield

    # Restore original instance AND its data to prevent pollution
    RegistryManager._instance = original_instance
    registry_module._default_registries = original_default_registries
    if original_instance is not None and original_data is not None:
        # Restore the data that may have been cleared
        original_instance.components.clear()
        original_instance.components.update(original_data['components'])
        original_instance.modifiers.clear()
        original_instance.modifiers.update(original_data['modifiers'])
        original_instance.vehicle_classes.clear()
        original_instance.vehicle_classes.update(original_data['vehicle_classes'])
        original_instance.resources.clear()
        original_instance.resources.update(original_data['resources'])


@pytest.fixture
def registry():
    """Get a fresh registry instance."""
    from game.core.registry import RegistryManager
    RegistryManager.reset()
    return RegistryManager.instance()


# =============================================================================
# Test: Singleton Behavior
# =============================================================================

class TestSingletonBehavior:
    """Tests for RegistryManager singleton pattern."""

    def test_instance_returns_same_object(self):
        """instance() should always return the same object."""
        from game.core.registry import RegistryManager

        r1 = RegistryManager.instance()
        r2 = RegistryManager.instance()

        assert r1 is r2

    def test_direct_instantiation_raises_exception(self, registry):
        """Direct instantiation should raise when singleton exists."""
        from game.core.registry import RegistryManager

        with pytest.raises(Exception, match="singleton"):
            RegistryManager()

    def test_reset_allows_new_instance(self):
        """reset() should allow creating a new instance."""
        from game.core.registry import RegistryManager

        r1 = RegistryManager.instance()
        id1 = id(r1)

        RegistryManager.reset()

        r2 = RegistryManager.instance()
        id2 = id(r2)

        # New instance has different id
        assert id1 != id2

    def test_has_thread_lock(self):
        """RegistryManager class should have a lock for thread safety."""
        from game.core.registry import RegistryManager

        assert hasattr(RegistryManager, '_lock')
        assert isinstance(RegistryManager._lock, type(threading.Lock()))

    def test_reset_sets_instance_to_none(self):
        """reset() should set _instance to None."""
        from game.core.registry import RegistryManager

        RegistryManager.instance()
        assert RegistryManager._instance is not None

        RegistryManager.reset()
        assert RegistryManager._instance is None


# =============================================================================
# Test: Thread Safety
# =============================================================================

class TestThreadSafety:
    """Tests for thread-safe operations."""

    def test_concurrent_instance_access(self):
        """Multiple threads calling instance() should get same instance."""
        from game.core.registry import RegistryManager

        RegistryManager.reset()
        results = []
        errors = []

        def get_instance():
            try:
                results.append(RegistryManager.instance())
            except Exception as e:
                errors.append(e)

        threads = [threading.Thread(target=get_instance) for _ in range(10)]

        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(errors) == 0
        assert len(results) == 10

        # All should be same instance
        first = results[0]
        assert all(r is first for r in results)

    def test_concurrent_registration(self, registry):
        """Multiple threads registering components should not corrupt data."""

        def register_components(prefix):
            for i in range(10):
                registry.components[f"{prefix}_{i}"] = {"id": f"{prefix}_{i}"}

        threads = [
            threading.Thread(target=register_components, args=(f"thread_{i}",))
            for i in range(5)
        ]

        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # Should have 50 components (5 threads x 10 components each)
        assert len(registry.components) == 50

    def test_concurrent_clear_is_safe(self, registry):
        """Concurrent clear operations should not crash."""
        registry.components["test"] = {"id": "test"}

        errors = []

        def clear_registry():
            try:
                registry.clear()
            except Exception as e:
                errors.append(e)

        threads = [threading.Thread(target=clear_registry) for _ in range(5)]

        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # No errors
        assert len(errors) == 0
        # Registry should be empty
        assert len(registry.components) == 0


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
        """clear() should raise RuntimeError when frozen."""
        registry.freeze()

        with pytest.raises(RuntimeError, match="frozen"):
            registry.clear()


# =============================================================================
# Test: Freeze Functionality
# =============================================================================

class TestFreezeFunctionality:
    """Tests for the freeze() method."""

    def test_freeze_sets_frozen_flag(self, registry):
        """freeze() should set _frozen to True."""
        assert registry._frozen == False

        registry.freeze()

        assert registry._frozen == True

    def test_set_validator_raises_when_frozen(self, registry):
        """set_validator() should raise when frozen."""
        registry.freeze()

        with pytest.raises(RuntimeError, match="frozen"):
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
        assert registry._frozen == False


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
        """hydrate() should raise RuntimeError when frozen."""
        registry.freeze()

        with pytest.raises(RuntimeError, match="frozen"):
            registry.hydrate({}, {}, {})


# =============================================================================
# Test: Utility Functions
# =============================================================================

class TestUtilityFunctions:
    """Tests for utility functions (get_component_registry, etc.)."""

    def test_get_component_registry_returns_components(self, registry):
        """get_component_registry() should return components dict."""
        from game.core.registry import get_component_registry

        registry.components["test"] = {"id": "test"}

        result = get_component_registry()

        assert result is registry.components
        assert "test" in result

    def test_get_modifier_registry_returns_modifiers(self, registry):
        """get_modifier_registry() should return modifiers dict."""
        from game.core.registry import get_modifier_registry

        registry.modifiers["mod"] = {"id": "mod"}

        result = get_modifier_registry()

        assert result is registry.modifiers
        assert "mod" in result

    def test_get_vehicle_classes_returns_classes(self, registry):
        """get_vehicle_classes() should return vehicle_classes dict."""
        from game.core.registry import get_vehicle_classes

        registry.vehicle_classes["Cruiser"] = {"name": "Cruiser"}

        result = get_vehicle_classes()

        assert result is registry.vehicle_classes
        assert "Cruiser" in result

    def test_get_resource_registry_returns_resources(self, registry):
        """get_resource_registry() should return resources dict."""
        from game.core.registry import get_resource_registry

        registry.resources["fuel"] = {"id": "fuel"}

        result = get_resource_registry()

        assert result is registry.resources
        assert "fuel" in result

    def test_get_validator_returns_validator(self, registry):
        """get_validator() should return the validator."""
        from game.core.registry import get_validator

        mock_validator = MagicMock()
        registry.set_validator(mock_validator)

        result = get_validator()

        assert result is mock_validator

    def test_get_validator_returns_none_when_not_set(self, registry):
        """get_validator() should return None when not set."""
        from game.core.registry import get_validator

        result = get_validator()

        assert result is None


# =============================================================================
# Test: Test Isolation (CRITICAL)
# =============================================================================

class TestIsolation:
    """
    CRITICAL: Tests for test isolation behavior.

    These tests verify that the registry can be properly isolated between tests
    to prevent data accumulation bugs.
    """

    def test_reset_provides_clean_slate(self):
        """reset() should provide completely clean state."""
        from game.core.registry import RegistryManager

        # Populate with data
        r1 = RegistryManager.instance()
        r1.components["a"] = {"id": "a"}
        r1.modifiers["b"] = {"id": "b"}
        r1.vehicle_classes["c"] = {"name": "c"}
        r1.resources["d"] = {"id": "d"}
        r1.set_validator(MagicMock())
        r1.freeze()

        # Reset
        RegistryManager.reset()

        # Get new instance
        r2 = RegistryManager.instance()

        # All should be empty/default
        assert len(r2.components) == 0
        assert len(r2.modifiers) == 0
        assert len(r2.vehicle_classes) == 0
        assert len(r2.resources) == 0
        assert r2._validator is None
        assert r2._frozen == False

    def test_clear_provides_clean_state_without_reset(self, registry):
        """clear() should empty all data without destroying instance."""
        registry.components["a"] = {"id": "a"}
        registry.modifiers["b"] = {"id": "b"}

        registry.clear()

        assert len(registry.components) == 0
        assert len(registry.modifiers) == 0

    def test_stale_references_after_reset(self):
        """
        WARNING: Stale references after reset can cause issues.

        When reset() is called, code holding old dict references will see
        stale data. The clear() method is safer as it preserves dict identity.
        """
        from game.core.registry import RegistryManager

        r1 = RegistryManager.instance()
        old_components = r1.components
        old_components["test"] = {"id": "test"}

        RegistryManager.reset()

        r2 = RegistryManager.instance()

        # New instance has different dict
        assert r2.components is not old_components

        # Old reference still has data (stale)
        assert "test" in old_components
        # New instance is clean
        assert "test" not in r2.components

    def test_dict_identity_preserved_with_clear(self, registry):
        """clear() preserves dict identity, avoiding stale references."""
        old_components = registry.components
        registry.components["test"] = {"id": "test"}

        registry.clear()

        # Same dict object
        assert registry.components is old_components
        # But data is cleared
        assert "test" not in old_components

    def test_data_accumulation_bug_scenario(self):
        """
        BUG DOC: Demonstrate data accumulation if clear() not called.

        Without proper cleanup between tests, data accumulates in the
        singleton registry.
        """
        from game.core.registry import RegistryManager

        RegistryManager.reset()

        # Simulate first test
        r1 = RegistryManager.instance()
        r1.components["from_test_1"] = {"id": "from_test_1"}

        # Simulate second test (without cleanup)
        r2 = RegistryManager.instance()
        r2.components["from_test_2"] = {"id": "from_test_2"}

        # BUG: Both are present (data accumulated)
        assert "from_test_1" in r2.components
        assert "from_test_2" in r2.components
        assert len(r2.components) == 2  # Should be 1 if properly isolated


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
        assert registry._frozen == False


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

class TestDefaultRegistries:
    """
    Tests for set_default_registries() and get_default_registries() functions.

    PROJ-38: These functions allow setting a global default GameRegistries
    instance for transitional fallback during incremental migration.
    """

    def test_get_default_registries_raises_when_not_set(self):
        """get_default_registries() should raise RuntimeError when not set."""
        from game.core.registry import get_default_registries, GameRegistries
        import game.core.registry as registry_module

        # Ensure default is not set
        registry_module._default_registries = None

        with pytest.raises(RuntimeError, match="not set"):
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
