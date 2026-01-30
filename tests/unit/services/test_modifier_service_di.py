"""
Tests for ModifierService dependency injection.

PROJ-38: Original tests for DI support.
PROJ-50: Updated for strict DI - modifier_registry is now required.

These tests verify that ModifierService:
1. Accepts modifier_registry via constructor (required)
2. Works with injected registry (no global state needed)
3. Raises TypeError when modifier_registry is None
"""
import pytest

from game.simulation.services.modifier_service import ModifierService
from game.simulation.components.component import create_component


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture
def mock_modifier_registry():
    """Create a minimal mock modifier registry for DI testing."""
    from game.simulation.components.component_constants import Modifier

    # Create mock modifiers with V2 format data dicts
    mock_modifiers = {
        'simple_size_mount': Modifier({
            'id': 'simple_size_mount',
            'name': 'Size',
            'param': {'min': 1.0, 'max': 1024.0, 'default': 1.0},
            'restrictions': {},
            'effects': []
        }),
        'test_modifier': Modifier({
            'id': 'test_modifier',
            'name': 'Test',
            'param': {'min': 0.0, 'max': 100.0, 'default': 0.0},
            'restrictions': {},
            'effects': []
        }),
        'weapon_only_modifier': Modifier({
            'id': 'weapon_only_modifier',
            'name': 'Weapon Only',
            'param': {'min': 0.0, 'max': 100.0, 'default': 0.0},
            'restrictions': {'allow_types': ['weapon']},
            'effects': []
        }),
    }
    return mock_modifiers


@pytest.fixture
def weapon_component():
    """Create a weapon component for testing."""
    return create_component("laser_cannon")


@pytest.fixture
def engine_component():
    """Create an engine component for testing."""
    return create_component("standard_engine")


# =============================================================================
# Test: Constructor Injection
# =============================================================================

class TestModifierServiceConstructor:
    """Tests for ModifierService constructor injection."""

    def test_accepts_modifier_registry_in_constructor(self, mock_modifier_registry):
        """ModifierService should accept modifier_registry in constructor."""
        service = ModifierService(modifier_registry=mock_modifier_registry)

        assert hasattr(service, '_modifiers')
        assert service._modifiers is mock_modifier_registry

    def test_constructor_with_none_raises_type_error(self):
        """PROJ-50: ModifierService with None should raise TypeError."""
        with pytest.raises(TypeError, match="modifier_registry is required"):
            ModifierService(modifier_registry=None)


# =============================================================================
# Test: Instance Methods with Injected Registry
# =============================================================================

class TestModifierServiceInstanceMethods:
    """Tests for ModifierService instance methods using injected registry."""

    def test_is_modifier_allowed_uses_injected_registry(self, mock_modifier_registry, weapon_component):
        """is_modifier_allowed should use the injected registry."""
        service = ModifierService(modifier_registry=mock_modifier_registry)

        # Test modifier in our mock registry
        result = service.is_modifier_allowed('test_modifier', weapon_component)

        assert result is True  # No restrictions, should be allowed

    def test_is_modifier_allowed_returns_false_for_unknown(self, mock_modifier_registry, weapon_component):
        """is_modifier_allowed should return False for modifiers not in injected registry."""
        service = ModifierService(modifier_registry=mock_modifier_registry)

        # This modifier is NOT in our mock registry
        result = service.is_modifier_allowed('rapid_fire', weapon_component)

        assert result is False

    def test_is_modifier_allowed_respects_restrictions(self, mock_modifier_registry, engine_component):
        """is_modifier_allowed should respect allow_types restriction from injected registry."""
        service = ModifierService(modifier_registry=mock_modifier_registry)

        # weapon_only_modifier has allow_types: ['weapon']
        result = service.is_modifier_allowed('weapon_only_modifier', engine_component)

        assert result is False  # Engine is not a weapon

    def test_get_initial_value_uses_injected_registry(self, mock_modifier_registry, weapon_component):
        """get_initial_value should use the injected registry."""
        service = ModifierService(modifier_registry=mock_modifier_registry)

        # simple_size_mount has special handling for value 1.0
        value = service.get_initial_value('simple_size_mount', weapon_component)

        assert value == 1.0

    def test_get_initial_value_returns_default_for_unknown(self, mock_modifier_registry, weapon_component):
        """get_initial_value should return 0 for unknown modifier in injected registry."""
        service = ModifierService(modifier_registry=mock_modifier_registry)

        value = service.get_initial_value('unknown_modifier', weapon_component)

        assert value == 0

    def test_get_local_min_max_uses_injected_registry(self, mock_modifier_registry, weapon_component):
        """get_local_min_max should use the injected registry."""
        service = ModifierService(modifier_registry=mock_modifier_registry)

        min_val, max_val = service.get_local_min_max('test_modifier', weapon_component)

        assert min_val == 0.0
        assert max_val == 100.0

    def test_get_local_min_max_returns_default_for_unknown(self, mock_modifier_registry, weapon_component):
        """get_local_min_max should return (0, 100) for unknown modifier."""
        service = ModifierService(modifier_registry=mock_modifier_registry)

        min_val, max_val = service.get_local_min_max('unknown_modifier', weapon_component)

        assert min_val == 0
        assert max_val == 100


# =============================================================================
# Test: Comparison of Injected vs Real Registry
# =============================================================================

class TestModifierServiceRealRegistry:
    """Tests comparing behavior with real modifiers registry."""

    def test_get_mandatory_modifiers_with_real_registry(self, weapon_component):
        """get_mandatory_modifiers should work with real modifiers registry."""
        from game.simulation.components.component import load_modifiers_data
        real_modifiers = load_modifiers_data()
        service = ModifierService(modifier_registry=real_modifiers)

        result = service.get_mandatory_modifiers(weapon_component)

        assert 'simple_size_mount' in result
        assert isinstance(result, list)

    def test_is_modifier_allowed_with_real_registry(self, weapon_component):
        """is_modifier_allowed should work with real modifiers registry."""
        from game.simulation.components.component import load_modifiers_data
        real_modifiers = load_modifiers_data()
        service = ModifierService(modifier_registry=real_modifiers)

        result = service.is_modifier_allowed('simple_size_mount', weapon_component)

        assert result is True
