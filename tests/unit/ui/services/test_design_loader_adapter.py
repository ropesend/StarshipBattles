"""Unit tests for DesignLoaderAdapter.

PROJ-43: Tests for the DesignLoaderAdapter that decouples UI from direct
SimulationDesignLoader usage.

PROJ-174: Uses deprecated set_default_registries() to test fallback behavior.
"""
from unittest.mock import MagicMock, patch
import pytest
import warnings


class TestDesignLoaderAdapter:
    """Tests for DesignLoaderAdapter class."""

    def test_load_ship_from_design_data_delegates_to_loader(self):
        """Test load_ship_from_design_data calls SimulationDesignLoader."""
        from game.ui.services.design_loader_adapter import DesignLoaderAdapter

        mock_loader = MagicMock()
        mock_ship = MagicMock()
        mock_ship.name = "Test Ship"
        mock_loader.load_ship_from_design_data.return_value = mock_ship

        adapter = DesignLoaderAdapter(design_loader=mock_loader)
        design_data = {"name": "Test Ship", "class": "corvette"}
        result = adapter.load_ship_from_design_data(design_data, 960, 540)

        mock_loader.load_ship_from_design_data.assert_called_once_with(
            design_data,
            center_x=960,
            center_y=540
        )
        assert result == mock_ship

    def test_load_ship_from_design_data_returns_none_on_error(self):
        """Test load_ship_from_design_data returns None when loader fails."""
        from game.ui.services.design_loader_adapter import DesignLoaderAdapter

        mock_loader = MagicMock()
        mock_loader.load_ship_from_design_data.return_value = None

        adapter = DesignLoaderAdapter(design_loader=mock_loader)
        design_data = {"invalid": "data"}
        result = adapter.load_ship_from_design_data(design_data, 1920, 1080)

        assert result is None

    def test_load_ship_from_file_delegates_to_loader(self):
        """Test load_ship_from_file calls SimulationDesignLoader."""
        from game.ui.services.design_loader_adapter import DesignLoaderAdapter

        mock_loader = MagicMock()
        mock_ship = MagicMock()
        mock_ship.name = "Test Ship"
        mock_loader.load_ship_from_file.return_value = (mock_ship, "Loaded successfully")

        adapter = DesignLoaderAdapter(design_loader=mock_loader)
        ship, message = adapter.load_ship_from_file("test.json", 1920, 1080)

        mock_loader.load_ship_from_file.assert_called_once_with(
            "test.json", 1920, 1080
        )
        assert ship == mock_ship
        assert message == "Loaded successfully"

    def test_load_ship_from_file_returns_none_on_error(self):
        """Test load_ship_from_file returns None when loader fails."""
        from game.ui.services.design_loader_adapter import DesignLoaderAdapter

        mock_loader = MagicMock()
        mock_loader.load_ship_from_file.return_value = (None, "File not found")

        adapter = DesignLoaderAdapter(design_loader=mock_loader)
        ship, message = adapter.load_ship_from_file("missing.json", 1920, 1080)

        assert ship is None
        assert "File not found" in message

    def test_adapter_uses_real_loader_when_none_provided(self, fresh_registries):
        """Test adapter falls back to real SimulationDesignLoader when none injected."""
        from game.ui.services.design_loader_adapter import DesignLoaderAdapter
        from game.simulation.services.design_loader import SimulationDesignLoader
        from game.core.registry import set_default_registries

        # PROJ-174: Suppress deprecation warning - testing backward compatibility
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            set_default_registries(fresh_registries)

        adapter = DesignLoaderAdapter()

        # Verify the adapter created a real loader
        assert isinstance(adapter._loader, SimulationDesignLoader)

    def test_load_ship_from_design_data_with_zero_position(self):
        """Test load_ship_from_design_data passes zero coordinates to loader."""
        from game.ui.services.design_loader_adapter import DesignLoaderAdapter

        mock_loader = MagicMock()
        mock_ship = MagicMock()
        mock_loader.load_ship_from_design_data.return_value = mock_ship

        adapter = DesignLoaderAdapter(design_loader=mock_loader)
        design_data = {"name": "Test Ship"}

        # Use default 0,0 dimensions
        result = adapter.load_ship_from_design_data(design_data, 0, 0)

        mock_loader.load_ship_from_design_data.assert_called_once_with(
            design_data,
            center_x=0,
            center_y=0
        )
