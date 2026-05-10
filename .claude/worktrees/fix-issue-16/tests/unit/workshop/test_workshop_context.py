"""
Tests for WorkshopContext launch configuration.

Following TDD approach: write tests first (RED), then implement (GREEN).
PROJ-211: All factory methods now require registries parameter.
"""
import pytest
from game.ui.screens.workshop_context import WorkshopContext, WorkshopMode
from game.core.registry import GameRegistries


@pytest.fixture
def mock_registries():
    """Create mock GameRegistries for testing."""
    return GameRegistries(components={}, modifiers={}, vehicle_classes={}, resources={})


class TestWorkshopContextStandalone:
    """Tests for standalone mode context."""

    def test_standalone_context_creation(self, mock_registries):
        """Can create standalone context with tech preset."""
        context = WorkshopContext.standalone(tech_preset_name="early_game", registries=mock_registries)

        assert context.mode == WorkshopMode.STANDALONE
        assert context.tech_preset_name == "early_game"
        assert context.empire_id is None
        assert context.savegame_path is None

    def test_standalone_default_preset(self, mock_registries):
        """Standalone context defaults to 'default' preset."""
        context = WorkshopContext.standalone(registries=mock_registries)

        assert context.tech_preset_name == "default"
        assert context.mode == WorkshopMode.STANDALONE

    def test_standalone_has_no_available_tech_ids(self, mock_registries):
        """Standalone mode doesn't use available_tech_ids list."""
        context = WorkshopContext.standalone(registries=mock_registries)

        assert context.available_tech_ids is None


class TestWorkshopContextIntegrated:
    """Tests for integrated mode context."""

    def test_integrated_context_creation(self, mock_registries):
        """Can create integrated context with empire and savegame."""
        context = WorkshopContext.integrated(
            empire_id=1,
            savegame_path="saves/savegame1",
            available_tech_ids=["laser_cannon", "railgun"],
            registries=mock_registries
        )

        assert context.mode == WorkshopMode.INTEGRATED
        assert context.empire_id == 1
        assert context.savegame_path == "saves/savegame1"
        assert context.available_tech_ids == ["laser_cannon", "railgun"]
        assert context.tech_preset_name is None

    def test_integrated_context_default_tech(self, mock_registries):
        """Integrated context defaults to empty tech list."""
        context = WorkshopContext.integrated(
            empire_id=1,
            savegame_path="saves/savegame1",
            registries=mock_registries
        )

        assert context.available_tech_ids == []
        assert context.mode == WorkshopMode.INTEGRATED

    def test_integrated_requires_empire_id(self, mock_registries):
        """Integrated context requires empire_id parameter."""
        with pytest.raises(TypeError):
            WorkshopContext.integrated(savegame_path="saves/savegame1", registries=mock_registries)

    def test_integrated_requires_savegame_path(self, mock_registries):
        """Integrated context requires savegame_path parameter."""
        with pytest.raises(TypeError):
            WorkshopContext.integrated(empire_id=1, registries=mock_registries)


class TestWorkshopContextCallbacks:
    """Tests for callback and return state handling."""

    def test_context_stores_callbacks(self, mock_registries):
        """Context can store on_return callback."""
        def mock_callback():
            pass

        context = WorkshopContext.standalone(registries=mock_registries)
        context.on_return = mock_callback
        context.return_state = "MENU"

        assert context.on_return is mock_callback
        assert context.return_state == "MENU"

    def test_context_callbacks_default_none(self, mock_registries):
        """Callbacks default to None if not set."""
        context = WorkshopContext.standalone(registries=mock_registries)

        assert context.on_return is None
        assert context.return_state is None

    def test_integrated_context_can_store_callbacks(self, mock_registries):
        """Integrated context also supports callbacks."""
        def mock_callback():
            pass

        context = WorkshopContext.integrated(
            empire_id=1,
            savegame_path="saves/test",
            registries=mock_registries
        )
        context.on_return = mock_callback
        context.return_state = "STRATEGY"

        assert context.on_return is mock_callback
        assert context.return_state == "STRATEGY"


class TestWorkshopContextModeDetection:
    """Tests for mode type checking."""

    def test_standalone_is_standalone(self, mock_registries):
        """Standalone context reports correct mode."""
        context = WorkshopContext.standalone(registries=mock_registries)

        assert context.mode == WorkshopMode.STANDALONE
        assert context.mode != WorkshopMode.INTEGRATED

    def test_integrated_is_integrated(self, mock_registries):
        """Integrated context reports correct mode."""
        context = WorkshopContext.integrated(
            empire_id=1,
            savegame_path="saves/test",
            registries=mock_registries
        )

        assert context.mode == WorkshopMode.INTEGRATED
        assert context.mode != WorkshopMode.STANDALONE

    def test_mode_is_enum(self, mock_registries):
        """Mode is a proper enum value."""
        context = WorkshopContext.standalone(registries=mock_registries)

        assert isinstance(context.mode, WorkshopMode)
        assert context.mode.value == "standalone"


class TestWorkshopContextImmutability:
    """Tests for context data integrity."""

    def test_mode_attribute_exists(self, mock_registries):
        """Context always has a mode attribute."""
        context = WorkshopContext.standalone(registries=mock_registries)

        assert hasattr(context, 'mode')

    def test_tech_preset_attribute_exists(self, mock_registries):
        """Context always has tech_preset_name attribute."""
        context = WorkshopContext.standalone(registries=mock_registries)

        assert hasattr(context, 'tech_preset_name')

    def test_empire_id_attribute_exists(self, mock_registries):
        """Context always has empire_id attribute."""
        context = WorkshopContext.integrated(empire_id=1, savegame_path="test", registries=mock_registries)

        assert hasattr(context, 'empire_id')

    def test_savegame_path_attribute_exists(self, mock_registries):
        """Context always has savegame_path attribute."""
        context = WorkshopContext.integrated(empire_id=1, savegame_path="test", registries=mock_registries)

        assert hasattr(context, 'savegame_path')
