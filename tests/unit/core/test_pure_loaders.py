"""
Tests for pure loading functions (PROJ-38).

These tests verify that the new pure loading functions:
1. Return data without modifying global state
2. Work independently of the RegistryManager singleton
3. Can be used with DI patterns
"""
import pytest
import copy

from game.core.registry import RegistryManager, GameRegistries
from game.core.singleton import SingletonMeta


def _make_minimal_registries():
    """Create minimal registries for testing pure load functions."""
    return GameRegistries(components={}, modifiers={}, vehicle_classes={}, resources={})


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

        # PROJ-211: registries is now required
        result = load_components_data("data/components.json", registries=_make_minimal_registries())

        assert isinstance(result, dict)

    def test_load_components_data_contains_components(self):
        """load_components_data() should return component objects keyed by ID."""
        from game.simulation.components.component import load_components_data, Component

        # PROJ-211: registries is now required
        result = load_components_data("data/components.json", registries=_make_minimal_registries())

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

        # Call pure function - PROJ-211: registries is now required
        result = load_components_data("data/components.json", registries=_make_minimal_registries())

        # Registry should still be empty
        assert len(registry) == 0
        # But result should have data
        assert len(result) > 0

    def test_load_components_data_returns_cloned_instances(self):
        """Each call to load_components_data() should return fresh instances."""
        from game.simulation.components.component import load_components_data

        # PROJ-211: registries is now required
        result1 = load_components_data("data/components.json", registries=_make_minimal_registries())
        result2 = load_components_data("data/components.json", registries=_make_minimal_registries())

        # Should be equal but not identical
        assert set(result1.keys()) == set(result2.keys())
        # Component instances should be different objects
        for comp_id in result1:
            assert result1[comp_id] is not result2[comp_id]

    def test_load_components_data_contains_expected_component(self):
        """load_components_data() should include known components like 'bridge'."""
        from game.simulation.components.component import load_components_data

        # PROJ-211: registries is now required
        result = load_components_data("data/components.json", registries=_make_minimal_registries())

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
# Test: ResourceCatalog Loading
# =============================================================================

class TestResourceCatalogLoading:
    """Tests for the ResourceCatalog resource loading."""

    def test_resource_catalog_returns_catalog(self):
        """ResourceCatalog.from_json() should return a ResourceCatalog."""
        from game.core.resources import ResourceCatalog

        catalog = ResourceCatalog.from_json()

        assert isinstance(catalog, ResourceCatalog)

    def test_resource_catalog_contains_resources(self):
        """ResourceCatalog.from_json() should contain resource definitions."""
        from game.core.resources import ResourceCatalog

        catalog = ResourceCatalog.from_json()

        assert len(catalog.all_ids()) > 0
        # Check structure - each definition should have an id
        for defn in catalog.all_definitions():
            assert defn.id
            assert isinstance(defn.id, str)

    def test_resource_catalog_does_not_modify_registry(self):
        """ResourceCatalog.from_json() should NOT modify the global registry."""
        from game.core.resources import ResourceCatalog
        from game.core.registry import RegistryManager

        # Ensure registry is empty
        registry = RegistryManager.instance().resources
        assert len(registry) == 0

        # Load catalog
        catalog = ResourceCatalog.from_json()

        # Registry should still be empty
        assert len(registry) == 0
        # But catalog should have data
        assert len(catalog.all_ids()) > 0

    def test_resource_catalog_contains_expected_resource(self):
        """ResourceCatalog.from_json() should include known resources like 'fuel'."""
        from game.core.resources import ResourceCatalog

        catalog = ResourceCatalog.from_json()

        assert catalog.has("fuel") or catalog.has("energy") or len(catalog.all_ids()) > 0

    def test_resource_catalog_returns_empty_on_missing_file(self):
        """ResourceCatalog.from_json() should return empty catalog when file is missing."""
        from game.core.resources import ResourceCatalog

        catalog = ResourceCatalog.from_json("nonexistent_file_xyz.json")

        assert len(catalog.all_ids()) == 0


# =============================================================================
# Test: Pure Loader Functions Return Correct Data
# =============================================================================

class TestLoaderPureFunctions:
    """PROJ-195: Tests for pure loader functions (no singleton access).

    These tests verify that the pure loading functions return the expected data
    without any side effects. This pattern is portable to C#/C++/Rust where
    global singletons are not idiomatic.
    """

    def test_load_components_data_returns_expected_components(self):
        """load_components_data() should return components including 'bridge'."""
        from game.simulation.components.component import load_components_data

        # Call pure function - PROJ-211: registries is now required
        result = load_components_data("data/components.json", registries=_make_minimal_registries())

        # Verify data is returned correctly
        assert len(result) > 0
        assert "bridge" in result
        assert result["bridge"].name == "Bridge"

    def test_load_modifiers_data_returns_expected_modifiers(self):
        """load_modifiers_data() should return modifiers including 'simple_size_mount'."""
        from game.simulation.components.component import load_modifiers_data

        # Call pure function - no singleton access
        result = load_modifiers_data("data/modifiers.json")

        # Verify data is returned correctly
        assert len(result) > 0
        assert "simple_size_mount" in result

