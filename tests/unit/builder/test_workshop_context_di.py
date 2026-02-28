"""
Tests for WorkshopContext dependency injection (PROJ-38).

These tests verify that WorkshopContext:
1. Accepts GameRegistries via constructor
2. Passes registries through factory methods

PROJ-211: Removed fallback tests - registries is now required in factory methods.
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

    def test_constructor_allows_none_registries(self):
        """WorkshopContext constructor allows None registries (dataclass field)."""
        # Direct constructor still allows None for flexibility - factory methods enforce it
        context = WorkshopContext(
            mode=WorkshopMode.STANDALONE,
            registries=None
        )

        assert context.registries is None


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

    def test_integrated_accepts_registries(self, mock_registries):
        """integrated() factory should accept and pass registries."""
        context = WorkshopContext.integrated(
            empire_id=1,
            savegame_path="saves/test",
            registries=mock_registries
        )

        assert context.registries is mock_registries
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
