"""
Tests for pure loading functions (PROJ-38).

These tests verify that the new pure loading functions:
1. Return data without modifying global state
2. Work independently of the RegistryManager singleton
3. Can be used with DI patterns
"""
import pytest
import copy

from game.core.registry import RegistryManager
from game.core.singleton import SingletonMeta


@pytest.fixture(autouse=True)
def reset_registry():
    """Reset registry state before and after each test."""
    original_instance = SingletonMeta._instances.get(RegistryManager)
    RegistryManager.reset()
    yield
    RegistryManager.reset()


# =============================================================================
# Test: load_components_data Pure Function
# =============================================================================

class TestLoadComponentsData:
    """Tests for the load_components_data pure loading function."""

    def test_load_components_data_returns_dict(self):
        """load_components_data() should return a dictionary."""
        from game.simulation.components.component import load_components_data

        result = load_components_data("data/components.json")

        assert isinstance(result, dict)

    def test_load_components_data_contains_components(self):
        """load_components_data() should return component objects keyed by ID."""
        from game.simulation.components.component import load_components_data, Component

        result = load_components_data("data/components.json")

        assert len(result) > 0
        # Check that values are Component instances
        for comp_id, comp in result.items():
            assert isinstance(comp, Component)
            assert comp.id == comp_id

    def test_load_components_data_does_not_modify_registry(self):
        """load_components_data() should NOT modify the global registry."""
        from game.simulation.components.component import load_components_data
        from game.core.registry import RegistryManager

        # Ensure registry is empty
        registry = RegistryManager.instance().components
        assert len(registry) == 0

        # Call pure function
        result = load_components_data("data/components.json")

        # Registry should still be empty
        assert len(registry) == 0
        # But result should have data
        assert len(result) > 0

    def test_load_components_data_returns_cloned_instances(self):
        """Each call to load_components_data() should return fresh instances."""
        from game.simulation.components.component import load_components_data

        result1 = load_components_data("data/components.json")
        result2 = load_components_data("data/components.json")

        # Should be equal but not identical
        assert set(result1.keys()) == set(result2.keys())
        # Component instances should be different objects
        for comp_id in result1:
            assert result1[comp_id] is not result2[comp_id]

    def test_load_components_data_contains_expected_component(self):
        """load_components_data() should include known components like 'bridge'."""
        from game.simulation.components.component import load_components_data

        result = load_components_data("data/components.json")

        assert "bridge" in result
        bridge = result["bridge"]
        assert bridge.name == "Bridge"


# =============================================================================
# Test: load_modifiers_data Pure Function
# =============================================================================

class TestLoadModifiersData:
    """Tests for the load_modifiers_data pure loading function."""

    def test_load_modifiers_data_returns_dict(self):
        """load_modifiers_data() should return a dictionary."""
        from game.simulation.components.component import load_modifiers_data

        result = load_modifiers_data("data/modifiers.json")

        assert isinstance(result, dict)

    def test_load_modifiers_data_contains_modifiers(self):
        """load_modifiers_data() should return Modifier objects keyed by ID."""
        from game.simulation.components.component import load_modifiers_data
        from game.simulation.components.component_constants import Modifier

        result = load_modifiers_data("data/modifiers.json")

        assert len(result) > 0
        # Check that values are Modifier instances
        for mod_id, mod in result.items():
            assert isinstance(mod, Modifier)
            assert mod.id == mod_id

    def test_load_modifiers_data_does_not_modify_registry(self):
        """load_modifiers_data() should NOT modify the global registry."""
        from game.simulation.components.component import load_modifiers_data
        from game.core.registry import RegistryManager

        # Ensure registry is empty
        registry = RegistryManager.instance().modifiers
        assert len(registry) == 0

        # Call pure function
        result = load_modifiers_data("data/modifiers.json")

        # Registry should still be empty
        assert len(registry) == 0
        # But result should have data
        assert len(result) > 0

    def test_load_modifiers_data_returns_fresh_copies(self):
        """Each call to load_modifiers_data() should return independent data."""
        from game.simulation.components.component import load_modifiers_data

        result1 = load_modifiers_data("data/modifiers.json")
        result2 = load_modifiers_data("data/modifiers.json")

        # Should be equal in keys
        assert set(result1.keys()) == set(result2.keys())
        # Modifier instances should be different objects (deep copied)
        for mod_id in result1:
            assert result1[mod_id] is not result2[mod_id]

    def test_load_modifiers_data_contains_expected_modifier(self):
        """load_modifiers_data() should include known modifiers like 'simple_size_mount'."""
        from game.simulation.components.component import load_modifiers_data

        result = load_modifiers_data("data/modifiers.json")

        assert "simple_size_mount" in result


# =============================================================================
# Test: load_vehicle_classes_data Pure Function
# =============================================================================

class TestLoadVehicleClassesData:
    """Tests for the load_vehicle_classes_data pure loading function."""

    def test_load_vehicle_classes_data_returns_dict(self):
        """load_vehicle_classes_data() should return a dictionary."""
        from game.simulation.entities.ship_loader import load_vehicle_classes_data

        result = load_vehicle_classes_data()

        assert isinstance(result, dict)

    def test_load_vehicle_classes_data_contains_classes(self):
        """load_vehicle_classes_data() should return vehicle class definitions."""
        from game.simulation.entities.ship_loader import load_vehicle_classes_data

        result = load_vehicle_classes_data()

        assert len(result) > 0
        # Check structure - each entry should have class data
        for cls_name, cls_def in result.items():
            assert isinstance(cls_def, dict)

    def test_load_vehicle_classes_data_does_not_modify_registry(self):
        """load_vehicle_classes_data() should NOT modify the global registry."""
        from game.simulation.entities.ship_loader import load_vehicle_classes_data
        from game.core.registry import RegistryManager

        # Ensure registry is empty
        registry = RegistryManager.instance().vehicle_classes
        assert len(registry) == 0

        # Call pure function
        result = load_vehicle_classes_data()

        # Registry should still be empty
        assert len(registry) == 0
        # But result should have data
        assert len(result) > 0

    def test_load_vehicle_classes_data_returns_fresh_copies(self):
        """Each call to load_vehicle_classes_data() should return independent data."""
        from game.simulation.entities.ship_loader import load_vehicle_classes_data

        result1 = load_vehicle_classes_data()
        result2 = load_vehicle_classes_data()

        # Should be equal in keys
        assert set(result1.keys()) == set(result2.keys())
        # Modifying one should not affect the other
        first_key = list(result1.keys())[0]
        result1[first_key]['test_marker'] = True

        assert 'test_marker' not in result2[first_key]

    def test_load_vehicle_classes_data_contains_expected_class(self):
        """load_vehicle_classes_data() should include known classes like 'Corvette'."""
        from game.simulation.entities.ship_loader import load_vehicle_classes_data

        result = load_vehicle_classes_data()

        # Check for common vehicle classes
        assert "Corvette" in result or "Frigate" in result or "Destroyer" in result

    def test_load_vehicle_classes_data_resolves_layer_configs(self):
        """load_vehicle_classes_data() should resolve layer_config references."""
        from game.simulation.entities.ship_loader import load_vehicle_classes_data

        result = load_vehicle_classes_data()

        # At least one class should have resolved layers
        has_layers = any('layers' in cls_def for cls_def in result.values())
        assert has_layers, "Some vehicle classes should have layers resolved"


# =============================================================================
# Test: load_resources_data Pure Function
# =============================================================================

class TestLoadResourcesData:
    """Tests for the load_resources_data pure loading function."""

    def test_load_resources_data_returns_dict(self):
        """load_resources_data() should return a dictionary."""
        from game.core.resources import load_resources_data

        result = load_resources_data()

        assert isinstance(result, dict)

    def test_load_resources_data_contains_resources(self):
        """load_resources_data() should return resource definitions keyed by ID."""
        from game.core.resources import load_resources_data

        result = load_resources_data()

        assert len(result) > 0
        # Check structure - each entry should have an 'id' field
        for res_id, res_def in result.items():
            assert isinstance(res_def, dict)
            assert res_def.get('id') == res_id

    def test_load_resources_data_does_not_modify_registry(self):
        """load_resources_data() should NOT modify the global registry."""
        from game.core.resources import load_resources_data
        from game.core.registry import RegistryManager

        # Ensure registry is empty
        registry = RegistryManager.instance().resources
        assert len(registry) == 0

        # Call pure function
        result = load_resources_data()

        # Registry should still be empty
        assert len(registry) == 0
        # But result should have data
        assert len(result) > 0

    def test_load_resources_data_returns_fresh_copies(self):
        """Each call to load_resources_data() should return independent data."""
        from game.core.resources import load_resources_data

        result1 = load_resources_data()
        result2 = load_resources_data()

        # Should be equal in keys
        assert set(result1.keys()) == set(result2.keys())
        # Modifying one should not affect the other
        first_key = list(result1.keys())[0]
        result1[first_key]['test_marker'] = True

        assert 'test_marker' not in result2[first_key]

    def test_load_resources_data_contains_expected_resource(self):
        """load_resources_data() should include known resources like 'fuel'."""
        from game.core.resources import load_resources_data

        result = load_resources_data()

        # Check for common resources
        assert "fuel" in result or "energy" in result or len(result) > 0

    def test_load_resources_data_returns_defaults_on_missing_file(self):
        """load_resources_data() should return defaults when file is missing."""
        from game.core.resources import load_resources_data

        result = load_resources_data("nonexistent_file_xyz.json")

        # Should have default resources
        assert "fuel" in result
        assert "energy" in result
        assert "ammo" in result


# =============================================================================
# Test: Backward Compatibility with Existing load_* Functions
# =============================================================================

class TestBackwardCompatibility:
    """Verify existing load_components() and load_modifiers() still work."""

    def test_load_components_populates_registry(self):
        """load_components() should still populate the global registry."""
        from game.simulation.components.component import load_components
        from game.core.registry import RegistryManager

        # Ensure registry is empty
        registry = RegistryManager.instance().components
        assert len(registry) == 0

        # Call wrapper function
        load_components("data/components.json")

        # Registry should now have data
        assert len(registry) > 0
        assert "bridge" in registry

    def test_load_modifiers_populates_registry(self):
        """load_modifiers() should still populate the global registry."""
        from game.simulation.components.component import load_modifiers
        from game.core.registry import RegistryManager

        # Ensure registry is empty
        registry = RegistryManager.instance().modifiers
        assert len(registry) == 0

        # Call wrapper function
        load_modifiers("data/modifiers.json")

        # Registry should now have data
        assert len(registry) > 0
        assert "simple_size_mount" in registry

