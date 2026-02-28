"""
Tests for WorkshopContext dependency injection (PROJ-38).

These tests verify that WorkshopContext:
1. Accepts GameRegistries via constructor
2. Passes registries through factory methods
3. Falls back to get_default_registry_provider() when None

PROJ-181: Removed deprecated set_default_registries() - WorkshopContext now
          uses get_default_registry_provider() which reads from RegistryManager.
"""
import pytest

from game.ui.screens.workshop_context import WorkshopContext, WorkshopMode
from game.core.registry import GameRegistries


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture
def mock_registries():
    """Create mock GameRegistries for DI testing."""
    from game.simulation.components.component import load_components_data, load_modifiers_data
    from game.simulation.entities.ship_loader import load_vehicle_classes_data

    minimal_registries = GameRegistries(components={}, modifiers={}, vehicle_classes={}, resources={})
    return GameRegistries(
        components=load_components_data(registries=minimal_registries),
        modifiers=load_modifiers_data(),
        vehicle_classes=load_vehicle_classes_data(),
        resources={}
    )


# =============================================================================
# Test: WorkshopContext Constructor with Registries
# =============================================================================

class TestWorkshopContextConstructor:
    """Tests for WorkshopContext constructor with registries injection."""

    def test_accepts_registries_in_constructor(self, mock_registries):
        """WorkshopContext should accept GameRegistries in constructor."""
        context = WorkshopContext(
            mode=WorkshopMode.STANDALONE,
            registries=mock_registries
        )

        assert hasattr(context, 'registries')
        assert context.registries is mock_registries

    def test_constructor_with_none_uses_default_provider(self):
        """WorkshopContext with None registries should fall back to get_default_registry_provider()."""
        # PROJ-181: Uses get_default_registry_provider() which reads from RegistryManager
        # (hydrated by root conftest fixture)
        context = WorkshopContext(
            mode=WorkshopMode.STANDALONE,
            registries=None
        )

        assert context.registries is not None

    def test_constructor_without_registries_uses_default_provider(self):
        """WorkshopContext without registries arg should fall back to get_default_registry_provider()."""
        # PROJ-181: Uses get_default_registry_provider() which reads from RegistryManager
        # (hydrated by root conftest fixture)
        context = WorkshopContext(
            mode=WorkshopMode.STANDALONE
        )

        assert context.registries is not None


# =============================================================================
# Test: Factory Methods with Registries
# =============================================================================

class TestWorkshopContextFactoryMethods:
    """Tests for WorkshopContext factory methods with registries injection."""

    def test_standalone_accepts_registries(self, mock_registries):
        """standalone() factory should accept and pass registries."""
        context = WorkshopContext.standalone(
            tech_preset_name="default",
            registries=mock_registries
        )

        assert context.registries is mock_registries
        assert context.mode == WorkshopMode.STANDALONE

    def test_standalone_without_registries_uses_default_provider(self):
        """standalone() without registries should use get_default_registry_provider()."""
        # PROJ-181: Uses get_default_registry_provider() which reads from RegistryManager
        context = WorkshopContext.standalone(tech_preset_name="default")

        assert context.registries is not None

    def test_integrated_accepts_registries(self, mock_registries):
        """integrated() factory should accept and pass registries."""
        context = WorkshopContext.integrated(
            empire_id=1,
            savegame_path="saves/test",
            registries=mock_registries
        )

        assert context.registries is mock_registries
        assert context.mode == WorkshopMode.INTEGRATED

    def test_integrated_without_registries_uses_default_provider(self):
        """integrated() without registries should use get_default_registry_provider()."""
        # PROJ-181: Uses get_default_registry_provider() which reads from RegistryManager
        context = WorkshopContext.integrated(
            empire_id=1,
            savegame_path="saves/test"
        )

        assert context.registries is not None


# =============================================================================
# Test: Backward Compatibility
# =============================================================================

class TestWorkshopContextBackwardCompatibility:
    """Tests ensuring backward compatibility with legacy interface."""

    def test_standalone_works_without_registries_arg(self):
        """standalone() should work without registries argument (uses provider fallback)."""
        # PROJ-181: Uses get_default_registry_provider() which reads from RegistryManager
        context = WorkshopContext.standalone()

        assert context is not None
        assert context.mode == WorkshopMode.STANDALONE

    def test_integrated_works_without_registries_arg(self):
        """integrated() should work without registries argument (uses provider fallback)."""
        # PROJ-181: Uses get_default_registry_provider() which reads from RegistryManager
        context = WorkshopContext.integrated(
            empire_id=1,
            savegame_path="saves/test"
        )

        assert context is not None
        assert context.mode == WorkshopMode.INTEGRATED

    def test_existing_attributes_preserved(self, mock_registries):
        """All existing WorkshopContext attributes should still work."""
        context = WorkshopContext.integrated(
            empire_id=1,
            savegame_path="saves/test",
            available_tech_ids=["tech1", "tech2"],
            built_designs={"design1"},
            empire_theme_id="Federation",
            registries=mock_registries
        )

        assert context.empire_id == 1
        assert context.savegame_path == "saves/test"
        assert context.available_tech_ids == ["tech1", "tech2"]
        assert "design1" in context.built_designs
        assert context.empire_theme_id == "Federation"
