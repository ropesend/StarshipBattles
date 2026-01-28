"""
Tests for WorkshopViewModel dependency injection (PROJ-38).

These tests verify that WorkshopViewModel:
1. Accepts registries via context parameter
2. Passes registries to VehicleDesignService
3. Uses registries for component lookups
"""
import pytest
from unittest.mock import MagicMock

from game.ui.screens.workshop_viewmodel import WorkshopViewModel
from game.ui.screens.workshop_context import WorkshopContext, WorkshopMode
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
def mock_event_bus():
    """Create mock event bus for testing."""
    bus = MagicMock()
    bus.emit = MagicMock()
    bus.subscribe = MagicMock()
    return bus


# =============================================================================
# Test: WorkshopViewModel with Context Registries
# =============================================================================

class TestWorkshopViewModelDI:
    """Tests for WorkshopViewModel with registries injection via context."""

    def test_accepts_context_with_registries(self, mock_registries, mock_event_bus):
        """WorkshopViewModel should accept context with registries."""
        context = WorkshopContext(
            mode=WorkshopMode.STANDALONE,
            registries=mock_registries
        )

        viewmodel = WorkshopViewModel(mock_event_bus, 1280, 720, context=context)

        assert hasattr(viewmodel, '_registries')
        assert viewmodel._registries is mock_registries

    def test_passes_registries_to_service(self, mock_registries, mock_event_bus):
        """WorkshopViewModel should pass registries to VehicleDesignService."""
        context = WorkshopContext(
            mode=WorkshopMode.STANDALONE,
            registries=mock_registries
        )

        viewmodel = WorkshopViewModel(mock_event_bus, 1280, 720, context=context)

        # The service should have the same registries
        assert viewmodel._ship_service._registries is mock_registries

    def test_create_default_ship_uses_registries(self, mock_registries, mock_event_bus):
        """create_default_ship should use injected registries."""
        context = WorkshopContext(
            mode=WorkshopMode.STANDALONE,
            registries=mock_registries
        )

        viewmodel = WorkshopViewModel(mock_event_bus, 1280, 720, context=context)
        ship = viewmodel.create_default_ship("Frigate")

        assert ship is not None
        assert ship.ship_class == "Frigate"
        # Ship should have registries from viewmodel
        assert ship._registries is mock_registries


# =============================================================================
# Test: Backward Compatibility
# =============================================================================

class TestWorkshopViewModelBackwardCompatibility:
    """Tests ensuring backward compatibility with legacy interface."""

    def test_works_without_context_arg(self, mock_registries, mock_event_bus):
        """WorkshopViewModel should work without context argument (legacy pattern)."""
        # Set default registries as fallback
        set_default_registries(mock_registries)

        viewmodel = WorkshopViewModel(mock_event_bus, 1280, 720)

        assert viewmodel is not None
        # Should still be able to create ships
        ship = viewmodel.create_default_ship("Escort")
        assert ship is not None

    def test_works_with_none_context(self, mock_registries, mock_event_bus):
        """WorkshopViewModel should work with None context (legacy pattern)."""
        set_default_registries(mock_registries)

        viewmodel = WorkshopViewModel(mock_event_bus, 1280, 720, context=None)

        assert viewmodel is not None

    def test_refresh_available_components_works(self, mock_registries, mock_event_bus):
        """refresh_available_components should work with injected registries."""
        context = WorkshopContext(
            mode=WorkshopMode.STANDALONE,
            registries=mock_registries
        )

        viewmodel = WorkshopViewModel(mock_event_bus, 1280, 720, context=context)
        viewmodel.refresh_available_components()

        # Should have components from registries
        assert len(viewmodel.available_components) > 0
