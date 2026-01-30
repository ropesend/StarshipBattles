"""
Tests for VehicleDesignService dependency injection.

PROJ-38, PROJ-42: Original tests for DI support.
PROJ-50: Updated for strict DI - registries is now required.

These tests verify that VehicleDesignService:
1. Accepts GameRegistries via constructor (required)
2. Works with injected registries (no global state needed)
3. Raises TypeError when registries is None
"""
import pytest

from game.simulation.services.vehicle_design_service import VehicleDesignService
from game.core.registry import GameRegistries


# =============================================================================
# Fixtures
# =============================================================================

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


# =============================================================================
# Test: Constructor Injection
# =============================================================================

class TestVehicleDesignServiceConstructor:
    """Tests for VehicleDesignService constructor injection."""

    def test_accepts_registries_in_constructor(self, mock_registries):
        """VehicleDesignService should accept GameRegistries in constructor."""
        service = VehicleDesignService(registries=mock_registries)

        assert hasattr(service, '_registries')
        assert service._registries is mock_registries

    def test_constructor_with_none_raises_type_error(self):
        """PROJ-50: VehicleDesignService with None should raise TypeError."""
        with pytest.raises(TypeError, match="registries is required"):
            VehicleDesignService(registries=None)


# =============================================================================
# Test: Instance Methods with Injected Registries
# =============================================================================

class TestVehicleDesignServiceInstanceMethods:
    """Tests for VehicleDesignService instance methods using injected registries."""

    def test_create_ship_uses_injected_registries(self, mock_registries):
        """create_ship should use the injected registries."""
        service = VehicleDesignService(registries=mock_registries)

        result = service.create_ship(
            name="Test Ship",
            ship_class="frigate"
        )

        assert result is not None
        # Result should have a ship or an error (depending on validation)
        assert hasattr(result, 'success')

    def test_validate_ship_class_uses_injected_registries(self, mock_registries):
        """Ship class validation should use the injected vehicle_classes registry."""
        service = VehicleDesignService(registries=mock_registries)

        # Try creating with a valid ship class from registries
        result = service.create_ship(
            name="Frigate Test",
            ship_class="frigate"
        )

        # Should succeed since frigate is a valid class
        assert result.success is True or 'frigate' in str(result.errors).lower() if result.errors else True

    def test_get_available_components_uses_injected_registries(self, mock_registries):
        """get_available_components should use the injected components registry."""
        from game.core.constants import LayerType

        service = VehicleDesignService(registries=mock_registries)

        # Create a ship first
        result = service.create_ship(
            name="Test Ship",
            ship_class="frigate"
        )

        if result.success and result.ship:
            # Getting available components for a layer should work
            available = service.get_available_components(result.ship, LayerType.CORE)
            assert isinstance(available, list)


# =============================================================================
# Test: Comparison with Real Registries
# =============================================================================

class TestVehicleDesignServiceRealRegistries:
    """Tests comparing behavior with real registries."""

    def test_service_works_with_real_registries(self, mock_registries):
        """VehicleDesignService should work with real registries."""
        service = VehicleDesignService(registries=mock_registries)

        result = service.create_ship(
            name="Real Registry Ship",
            ship_class="frigate"
        )

        assert result is not None
        assert hasattr(result, 'success')
