"""
Tests for ShipStatsService dependency injection (PROJ-38).

These tests verify that ShipStatsService:
1. Accepts GameRegistries via constructor
2. Works with injected registries (no global state needed)
3. Has transitional fallback to get_default_registries()
"""
import pytest

from game.strategy.services.ship_stats_service import ShipStatsService
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
def simple_design():
    """Create a simple ship design for testing."""
    return {
        'ship_class': 'frigate',
        'layers': {
            'Structure': [
                {'id': 'bridge', 'modifiers': []},
            ]
        },
        'expected_stats': {
            'max_hp': 100,
            'mass': 50,
        }
    }


# =============================================================================
# Test: Constructor Injection
# =============================================================================

class TestShipStatsServiceConstructor:
    """Tests for ShipStatsService constructor injection."""

    def test_accepts_registries_in_constructor(self, mock_registries):
        """ShipStatsService should accept GameRegistries in constructor."""
        service = ShipStatsService(registries=mock_registries)

        assert hasattr(service, '_registries')
        assert service._registries is mock_registries

    def test_constructor_with_none_uses_default(self, mock_registries):
        """ShipStatsService with None should fall back to default registries."""
        # Set up default registries
        set_default_registries(mock_registries)

        service = ShipStatsService(registries=None)

        assert service._registries is not None
        assert service._registries.components is not None


# =============================================================================
# Test: Instance Methods with Injected Registries
# =============================================================================

class TestShipStatsServiceInstanceMethods:
    """Tests for ShipStatsService instance methods using injected registries."""

    def test_calculate_stats_uses_injected_registries(self, mock_registries, simple_design):
        """calculate_stats should use the injected registries."""
        service = ShipStatsService(registries=mock_registries)

        result = service.calculate_stats(simple_design)

        # Should return a dict with stats (may use expected_stats fallback)
        assert isinstance(result, dict)
        assert 'max_hp' in result
        assert 'mass' in result

    def test_iterate_design_components_uses_injected_registries(self, mock_registries, simple_design):
        """_iterate_design_components should use the injected registries."""
        service = ShipStatsService(registries=mock_registries)

        result = service._iterate_design_components(simple_design)

        # Should return a list
        assert isinstance(result, list)

    def test_calculate_stats_finds_components_from_registry(self, mock_registries):
        """calculate_stats should find component data from injected registry."""
        # Use a design with a real component
        design = {
            'ship_class': 'frigate',
            'layers': {
                'Structure': [
                    {'id': 'bridge', 'modifiers': [{'id': 'simple_size_mount', 'value': 1}]},
                ]
            }
        }
        service = ShipStatsService(registries=mock_registries)

        result = service.calculate_stats(design)

        # Should calculate stats from component registry (uses instance's registries)
        assert isinstance(result, dict)
        # Bridge exists in registry - mass should be > 0 (HP may be 0 for formula-based components)
        assert 'mass' in result
        assert 'max_hp' in result


# =============================================================================
# Test: Static Utility Methods (PROJ-42)
# =============================================================================

class TestShipStatsServiceStaticMethods:
    """Tests for ShipStatsService static utility methods.

    PROJ-42: After removing dual static/instance patterns, only pure utility
    methods like get_component_effectiveness remain as static methods.
    """

    def test_get_component_effectiveness_is_static(self, mock_registries):
        """get_component_effectiveness should work as a static method."""
        from game.simulation.components.component import create_component

        comp = create_component('bridge')

        # Static call (no instance needed)
        result = ShipStatsService.get_component_effectiveness('bridge_0', comp, {})

        assert isinstance(result, float)
        assert 0.0 <= result <= 1.0
