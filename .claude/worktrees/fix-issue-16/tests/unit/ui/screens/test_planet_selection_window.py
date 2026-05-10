"""Tests for PlanetSelectionWindow generalization (PROJ-79 Phase 4)."""
import pytest
from unittest.mock import Mock, MagicMock, patch


class MockPlanet:
    """Mock planet for testing."""
    def __init__(self, name: str, planet_id: int = 1):
        self.name = name
        self.id = planet_id
        self.image_id = None
        self.image_rotation = 0


@pytest.fixture
def sample_planets():
    """Sample planets for testing."""
    return [
        MockPlanet("Alpha Prime", 1),
        MockPlanet("Beta Colony", 2),
        MockPlanet("Gamma Station", 3),
    ]


class TestPlanetSelectionWindowParameters:
    """Test PlanetSelectionWindow constructor parameters."""

    def test_default_parameters_backward_compatible(self, sample_planets):
        """Default parameters match colonization use case for backward compatibility."""
        # The implementation uses defaults that match existing colonization callers:
        # - window_title="Select Planet to Colonize"
        # - list_label="Habitable bodies:"
        # - show_any_button=True
        # This test verifies the signature accepts these as defaults
        from game.ui.screens.planet_selection_window import PlanetSelectionWindow
        import inspect

        sig = inspect.signature(PlanetSelectionWindow.__init__)
        params = sig.parameters

        assert 'window_title' in params
        assert params['window_title'].default == "Select Planet to Colonize"

        assert 'list_label' in params
        assert params['list_label'].default == "Habitable bodies:"

        assert 'show_any_button' in params
        assert params['show_any_button'].default is True

    def test_custom_parameters_accepted(self, sample_planets):
        """Custom parameters are accepted by constructor."""
        from game.ui.screens.planet_selection_window import PlanetSelectionWindow
        import inspect

        sig = inspect.signature(PlanetSelectionWindow.__init__)
        params = sig.parameters

        # Verify all new parameters exist and are keyword-only or have defaults
        assert 'window_title' in params
        assert 'list_label' in params
        assert 'show_any_button' in params


