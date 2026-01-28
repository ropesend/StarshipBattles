"""
Tests for Component dependency injection (PROJ-38).

These tests verify that Component and related functions:
1. Accept GameRegistries via constructor/parameter
2. Work with injected registries (no global state needed)
3. Have transitional fallback to get_default_registries()
"""
import pytest

from game.simulation.components.component import Component, create_component
from game.core.registry import GameRegistries, set_default_registries


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture(autouse=True)
def restore_default_registries():
    """Restore _default_registries after each test to prevent pollution."""
    import game.core.registry as registry_module
    original = registry_module._default_registries
    yield
    registry_module._default_registries = original


@pytest.fixture
def mock_registries():
    """Create mock GameRegistries for DI testing."""
    from game.simulation.components.component import load_components_data, load_modifiers_data
    from game.simulation.entities.ship_loader import load_vehicle_classes_data

    return GameRegistries(
        components=load_components_data(),
        modifiers=load_modifiers_data(),
        vehicle_classes=load_vehicle_classes_data(),
        resources={}
    )


@pytest.fixture
def minimal_component_data():
    """Create minimal component data for testing."""
    return {
        'id': 'test_component',
        'name': 'Test Component',
        'type': 'utility',
        'mass': 10,
        'hp': 100,
        'cost': 50,
        'abilities': {},
        'modifiers': []
    }


# =============================================================================
# Test: Component Constructor with Registries
# =============================================================================

class TestComponentConstructor:
    """Tests for Component constructor with registries injection."""

    def test_accepts_registries_in_constructor(self, mock_registries, minimal_component_data):
        """Component should accept GameRegistries in constructor."""
        component = Component(minimal_component_data, registries=mock_registries)

        assert hasattr(component, '_registries')
        assert component._registries is mock_registries

    def test_constructor_with_none_uses_default(self, mock_registries, minimal_component_data):
        """Component with None registries should fall back to default registries."""
        set_default_registries(mock_registries)

        component = Component(minimal_component_data, registries=None)

        assert component._registries is not None
        assert component._registries.modifiers is not None

    def test_constructor_without_registries_uses_default(self, mock_registries, minimal_component_data):
        """Component without registries arg should fall back to default registries."""
        set_default_registries(mock_registries)

        # Legacy pattern - no registries argument
        component = Component(minimal_component_data)

        assert component._registries is not None


# =============================================================================
# Test: add_modifier Uses Injected Registry
# =============================================================================

class TestComponentAddModifier:
    """Tests for add_modifier using injected registries."""

    def test_add_modifier_uses_injected_registry(self, mock_registries, minimal_component_data):
        """add_modifier should use the injected modifiers registry."""
        component = Component(minimal_component_data, registries=mock_registries)

        # simple_size_mount exists in all registries
        result = component.add_modifier('simple_size_mount', 2.0)

        assert result is True
        modifier = component.get_modifier('simple_size_mount')
        assert modifier is not None
        assert modifier.value == 2.0

    def test_add_modifier_returns_false_for_unknown(self, mock_registries, minimal_component_data):
        """add_modifier should return False for modifiers not in injected registry."""
        # Create a registry with empty modifiers
        empty_registries = GameRegistries(
            components=mock_registries.components,
            modifiers={},  # Empty modifiers
            vehicle_classes=mock_registries.vehicle_classes,
            resources={}
        )
        component = Component(minimal_component_data, registries=empty_registries)

        result = component.add_modifier('simple_size_mount', 2.0)

        assert result is False


# =============================================================================
# Test: create_component Function with Registries
# =============================================================================

class TestCreateComponentFunction:
    """Tests for create_component function with registries parameter."""

    def test_create_component_accepts_registries(self, mock_registries):
        """create_component should accept registries parameter."""
        component = create_component('bridge', registries=mock_registries)

        assert component is not None
        assert component.id == 'bridge'
        assert component._registries is mock_registries

    def test_create_component_passes_registries_to_component(self, mock_registries):
        """create_component should pass registries to Component constructor."""
        component = create_component('laser_cannon', registries=mock_registries)

        assert component is not None
        assert component._registries is mock_registries

    def test_create_component_without_registries_uses_default(self, mock_registries):
        """create_component without registries should use default registries."""
        set_default_registries(mock_registries)

        component = create_component('bridge')

        assert component is not None


# =============================================================================
# Test: Backward Compatibility
# =============================================================================

class TestComponentBackwardCompatibility:
    """Tests ensuring backward compatibility with legacy interface."""

    def test_component_works_without_registries_arg(self, minimal_component_data):
        """Component should work without registries argument (legacy pattern)."""
        component = Component(minimal_component_data)

        assert component is not None
        assert component.id == 'test_component'

    def test_create_component_works_without_registries_arg(self):
        """create_component should work without registries argument."""
        component = create_component('bridge')

        assert component is not None
        assert component.id == 'bridge'

    def test_add_modifier_works_without_explicit_registries(self, minimal_component_data):
        """add_modifier should work on component created without explicit registries."""
        component = Component(minimal_component_data)

        # Should use default registry
        result = component.add_modifier('simple_size_mount', 2.0)

        assert result is True
