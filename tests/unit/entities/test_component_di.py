"""
Tests for Component dependency injection (PROJ-50).

These tests verify that Component and related functions:
1. Accept GameRegistries via constructor/parameter (required)
2. Raise TypeError when registries is None
3. Work with injected registries for all operations
"""
import pytest

from game.core.exceptions import ValidationException
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
# Test: Component Constructor with Registries (PROJ-50 Strict DI)
# =============================================================================

class TestComponentConstructor:
    """Tests for Component constructor with strict registries injection."""

    def test_accepts_registries_in_constructor(self, mock_registries, minimal_component_data):
        """Component should accept GameRegistries in constructor."""
        component = Component(minimal_component_data, registries=mock_registries)

        assert hasattr(component, '_registries')
        assert component._registries is mock_registries

    def test_constructor_with_none_raises_typeerror(self, minimal_component_data):
        """Component with None registries should raise TypeError (PROJ-50 strict DI)."""
        with pytest.raises(ValidationException):
            Component(minimal_component_data, registries=None)

    def test_constructor_stores_registries(self, mock_registries, minimal_component_data):
        """Component constructor should store registries for later use."""
        component = Component(minimal_component_data, registries=mock_registries)

        assert component._registries is mock_registries
        assert component._registries.modifiers is not None


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
# Test: create_component Function with Registries (PROJ-50 Strict DI)
# =============================================================================

class TestCreateComponentFunction:
    """Tests for create_component function with strict registries parameter."""

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

    def test_create_component_without_registries_raises_typeerror(self):
        """create_component without registries should raise TypeError (PROJ-50 strict DI)."""
        with pytest.raises(ValidationException):
            create_component('bridge', registries=None)


# =============================================================================
# Test: Strict DI Enforcement (PROJ-50)
# =============================================================================

class TestStrictDIEnforcement:
    """Tests ensuring strict DI is enforced (no backward compatibility with None)."""

    def test_component_requires_registries_parameter(self, minimal_component_data, mock_registries):
        """Component must receive valid registries (PROJ-50)."""
        # Valid: with registries
        component = Component(minimal_component_data, registries=mock_registries)
        assert component._registries is mock_registries

        # Invalid: with None
        with pytest.raises(ValidationException):
            Component(minimal_component_data, registries=None)

    def test_create_component_requires_registries_parameter(self, mock_registries):
        """create_component must receive valid registries (PROJ-50)."""
        # Valid: with registries
        component = create_component('bridge', registries=mock_registries)
        assert component is not None

        # Invalid: with None
        with pytest.raises(ValidationException):
            create_component('bridge', registries=None)
