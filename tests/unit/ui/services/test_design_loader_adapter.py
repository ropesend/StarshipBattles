"""Unit tests for DesignLoaderAdapter.

PROJ-43: Tests for the DesignLoaderAdapter that decouples UI from direct
SimulationDesignLoader usage.

PROJ-211: registry_provider is now required. Tests updated to pass registries
or use fresh_registries fixture.
"""
from unittest.mock import MagicMock, patch
import pytest


class TestDesignLoaderAdapter:
    """Tests for DesignLoaderAdapter class."""

    def test_load_ship_from_design_data_delegates_to_loader(self, fresh_registries):
        """Test load_ship_from_design_data calls SimulationDesignLoader."""
        from game.ui.services.design_loader_adapter import DesignLoaderAdapter

        mock_loader = MagicMock()
        mock_ship = MagicMock()
        mock_ship.name = "Test Ship"
        mock_loader.load_ship_from_design_data.return_value = mock_ship

        # PROJ-211: Must provide registry_provider (even though we inject loader)
        adapter = DesignLoaderAdapter(design_loader=mock_loader, registry_provider=fresh_registries)
        design_data = {"name": "Test Ship", "class": "corvette"}
        result = adapter.load_ship_from_design_data(design_data, 960, 540)

        mock_loader.load_ship_from_design_data.assert_called_once_with(
            design_data,
            center_x=960,
            center_y=540
        )
        assert result == mock_ship

    def test_load_ship_from_design_data_returns_none_on_error(self, fresh_registries):
        """Test load_ship_from_design_data returns None when loader fails."""
        from game.ui.services.design_loader_adapter import DesignLoaderAdapter

        mock_loader = MagicMock()
        mock_loader.load_ship_from_design_data.return_value = None

        adapter = DesignLoaderAdapter(design_loader=mock_loader, registry_provider=fresh_registries)
        design_data = {"invalid": "data"}
        result = adapter.load_ship_from_design_data(design_data, 1920, 1080)

        assert result is None

    def test_load_ship_from_file_delegates_to_loader(self, fresh_registries):
        """Test load_ship_from_file calls SimulationDesignLoader."""
        from game.ui.services.design_loader_adapter import DesignLoaderAdapter

        mock_loader = MagicMock()
        mock_ship = MagicMock()
        mock_ship.name = "Test Ship"
        mock_loader.load_ship_from_file.return_value = (mock_ship, "Loaded successfully")

        adapter = DesignLoaderAdapter(design_loader=mock_loader, registry_provider=fresh_registries)
        ship, message = adapter.load_ship_from_file("test.json", 1920, 1080)

        mock_loader.load_ship_from_file.assert_called_once_with(
            "test.json", 1920, 1080
        )
        assert ship == mock_ship
        assert message == "Loaded successfully"

    def test_load_ship_from_file_returns_none_on_error(self, fresh_registries):
        """Test load_ship_from_file returns None when loader fails."""
        from game.ui.services.design_loader_adapter import DesignLoaderAdapter

        mock_loader = MagicMock()
        mock_loader.load_ship_from_file.return_value = (None, "File not found")

        adapter = DesignLoaderAdapter(design_loader=mock_loader, registry_provider=fresh_registries)
        ship, message = adapter.load_ship_from_file("missing.json", 1920, 1080)

        assert ship is None
        assert "File not found" in message

    def test_adapter_uses_real_loader_when_none_provided(self, fresh_registries):
        """Test adapter creates real SimulationDesignLoader when none injected."""
        from game.ui.services.design_loader_adapter import DesignLoaderAdapter
        from game.simulation.services.design_loader import SimulationDesignLoader

        # PROJ-211: Must provide registry_provider
        adapter = DesignLoaderAdapter(registry_provider=fresh_registries)

        # Verify the adapter created a real loader
        assert isinstance(adapter._loader, SimulationDesignLoader)

    def test_load_ship_from_design_data_with_zero_position(self, fresh_registries):
        """Test load_ship_from_design_data passes zero coordinates to loader."""
        from game.ui.services.design_loader_adapter import DesignLoaderAdapter

        mock_loader = MagicMock()
        mock_ship = MagicMock()
        mock_loader.load_ship_from_design_data.return_value = mock_ship

        adapter = DesignLoaderAdapter(design_loader=mock_loader, registry_provider=fresh_registries)
        design_data = {"name": "Test Ship"}

        # Use default 0,0 dimensions
        result = adapter.load_ship_from_design_data(design_data, 0, 0)

        mock_loader.load_ship_from_design_data.assert_called_once_with(
            design_data,
            center_x=0,
            center_y=0
        )

    def test_raises_when_none_provider_and_no_loader(self, fresh_registries):
        """PROJ-211: Test adapter raises ValidationException when None provider and no loader."""
        from game.ui.services.design_loader_adapter import DesignLoaderAdapter
        from game.core.exceptions import ValidationException

        with pytest.raises(ValidationException) as exc_info:
            DesignLoaderAdapter(registry_provider=None)

        assert "registry_provider is required" in str(exc_info.value)

    def test_allows_injected_loader_without_registries(self):
        """Injecting a loader bypasses registry requirement."""
        from game.ui.services.design_loader_adapter import DesignLoaderAdapter

        mock_loader = MagicMock()

        # When a loader is provided, registries are not checked
        adapter = DesignLoaderAdapter(design_loader=mock_loader, registry_provider=None)

        assert adapter._loader is mock_loader
