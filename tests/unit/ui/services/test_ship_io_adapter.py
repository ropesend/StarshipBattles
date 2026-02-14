"""Unit tests for ShipIOAdapter.

PROJ-43: Tests for the ShipIOAdapter that decouples UI from direct ShipIO usage.
"""
from unittest.mock import MagicMock, patch
import pytest


class TestShipIOAdapter:
    """Tests for ShipIOAdapter class."""

    def test_set_ships_folder_updates_default_folder(self):
        """Test set_ships_folder updates the underlying ShipIO default folder."""
        from game.ui.services.ship_io_adapter import ShipIOAdapter

        mock_ship_io_class = MagicMock()
        mock_ship_io_class.default_ships_folder = "ships"

        adapter = ShipIOAdapter(ship_io_class=mock_ship_io_class)
        adapter.set_ships_folder("custom_folder")

        assert mock_ship_io_class.default_ships_folder == "custom_folder"

    def test_save_ship_delegates_to_ship_io(self):
        """Test save_ship calls ShipIO.save_ship with the ship."""
        from game.ui.services.ship_io_adapter import ShipIOAdapter

        mock_ship_io_class = MagicMock()
        mock_ship_io_class.save_ship.return_value = (True, "Saved successfully")

        mock_ship = MagicMock()
        mock_ship.name = "Test Ship"

        adapter = ShipIOAdapter(ship_io_class=mock_ship_io_class)
        success, message = adapter.save_ship(mock_ship)

        mock_ship_io_class.save_ship.assert_called_once_with(mock_ship)
        assert success is True
        assert message == "Saved successfully"

    def test_save_ship_returns_failure_on_error(self):
        """Test save_ship returns failure when ShipIO fails."""
        from game.ui.services.ship_io_adapter import ShipIOAdapter

        mock_ship_io_class = MagicMock()
        mock_ship_io_class.save_ship.return_value = (False, "Save failed")

        mock_ship = MagicMock()

        adapter = ShipIOAdapter(ship_io_class=mock_ship_io_class)
        success, message = adapter.save_ship(mock_ship)

        assert success is False
        assert message == "Save failed"

    def test_load_ship_delegates_to_ship_io(self):
        """Test load_ship calls ShipIO.load_ship with dimensions."""
        from game.ui.services.ship_io_adapter import ShipIOAdapter

        mock_ship_io_class = MagicMock()
        mock_ship = MagicMock()
        mock_ship.name = "Loaded Ship"
        mock_ship_io_class.load_ship.return_value = (mock_ship, "Loaded successfully")

        adapter = ShipIOAdapter(ship_io_class=mock_ship_io_class)
        ship, message = adapter.load_ship(1920, 1080)

        mock_ship_io_class.load_ship.assert_called_once_with(1920, 1080)
        assert ship == mock_ship
        assert message == "Loaded successfully"

    def test_load_ship_returns_none_on_cancel(self):
        """Test load_ship returns (None, None) when user cancels."""
        from game.ui.services.ship_io_adapter import ShipIOAdapter

        mock_ship_io_class = MagicMock()
        mock_ship_io_class.load_ship.return_value = (None, None)

        adapter = ShipIOAdapter(ship_io_class=mock_ship_io_class)
        ship, message = adapter.load_ship(1920, 1080)

        assert ship is None
        assert message is None

    def test_load_ship_returns_none_on_error(self):
        """Test load_ship returns (None, error_message) on failure."""
        from game.ui.services.ship_io_adapter import ShipIOAdapter

        mock_ship_io_class = MagicMock()
        mock_ship_io_class.load_ship.return_value = (None, "Load failed: file not found")

        adapter = ShipIOAdapter(ship_io_class=mock_ship_io_class)
        ship, message = adapter.load_ship(1920, 1080)

        assert ship is None
        assert "Load failed" in message

    def test_adapter_uses_real_ship_io_when_none_provided(self):
        """Test adapter falls back to real ShipIO when none injected."""
        from game.ui.services.ship_io_adapter import ShipIOAdapter
        from game.ui.services.ship_io import ShipIO

        adapter = ShipIOAdapter()

        # Verify the adapter is using the real ShipIO class
        assert adapter._ship_io is ShipIO

    def test_get_ships_folder_returns_current_folder(self):
        """Test get_ships_folder returns the current default folder."""
        from game.ui.services.ship_io_adapter import ShipIOAdapter

        mock_ship_io_class = MagicMock()
        mock_ship_io_class.default_ships_folder = "my_ships"

        adapter = ShipIOAdapter(ship_io_class=mock_ship_io_class)
        result = adapter.get_ships_folder()

        assert result == "my_ships"


class TestShipIOAdapterErrorPaths:
    """PROJ-142: TCG-UI2-005 - Additional error path tests for ShipIOAdapter."""

    def test_save_ship_with_permission_error_message(self):
        """Test save_ship handles permission error messages correctly."""
        from game.ui.services.ship_io_adapter import ShipIOAdapter

        mock_ship_io_class = MagicMock()
        mock_ship_io_class.save_ship.return_value = (False, "Permission denied: C:/readonly/ship.json")

        mock_ship = MagicMock()

        adapter = ShipIOAdapter(ship_io_class=mock_ship_io_class)
        success, message = adapter.save_ship(mock_ship)

        assert success is False
        assert "Permission denied" in message

    def test_save_ship_with_disk_full_error(self):
        """Test save_ship handles disk full error correctly."""
        from game.ui.services.ship_io_adapter import ShipIOAdapter

        mock_ship_io_class = MagicMock()
        mock_ship_io_class.save_ship.return_value = (False, "No space left on device")

        mock_ship = MagicMock()

        adapter = ShipIOAdapter(ship_io_class=mock_ship_io_class)
        success, message = adapter.save_ship(mock_ship)

        assert success is False
        assert message is not None

    def test_load_ship_with_corrupt_file_error(self):
        """Test load_ship handles corrupt file error correctly."""
        from game.ui.services.ship_io_adapter import ShipIOAdapter

        mock_ship_io_class = MagicMock()
        mock_ship_io_class.load_ship.return_value = (None, "Invalid JSON: unexpected token")

        adapter = ShipIOAdapter(ship_io_class=mock_ship_io_class)
        ship, message = adapter.load_ship(1920, 1080)

        assert ship is None
        assert "Invalid JSON" in message

    def test_load_ship_with_missing_file_error(self):
        """Test load_ship handles missing file error correctly."""
        from game.ui.services.ship_io_adapter import ShipIOAdapter

        mock_ship_io_class = MagicMock()
        mock_ship_io_class.load_ship.return_value = (None, "File not found: ship.json")

        adapter = ShipIOAdapter(ship_io_class=mock_ship_io_class)
        ship, message = adapter.load_ship(1920, 1080)

        assert ship is None
        assert "File not found" in message

    def test_load_ship_with_incompatible_version_error(self):
        """Test load_ship handles incompatible version error correctly."""
        from game.ui.services.ship_io_adapter import ShipIOAdapter

        mock_ship_io_class = MagicMock()
        mock_ship_io_class.load_ship.return_value = (None, "Incompatible ship version: 2.0")

        adapter = ShipIOAdapter(ship_io_class=mock_ship_io_class)
        ship, message = adapter.load_ship(1920, 1080)

        assert ship is None
        assert "Incompatible" in message

    def test_set_ships_folder_with_empty_path(self):
        """Test set_ships_folder handles empty path."""
        from game.ui.services.ship_io_adapter import ShipIOAdapter

        mock_ship_io_class = MagicMock()
        mock_ship_io_class.default_ships_folder = "ships"

        adapter = ShipIOAdapter(ship_io_class=mock_ship_io_class)
        adapter.set_ships_folder("")

        # Empty path should be set (caller responsibility to validate)
        assert mock_ship_io_class.default_ships_folder == ""

    def test_load_ship_with_zero_dimensions(self):
        """Test load_ship handles zero dimensions gracefully."""
        from game.ui.services.ship_io_adapter import ShipIOAdapter

        mock_ship_io_class = MagicMock()
        mock_ship = MagicMock()
        mock_ship_io_class.load_ship.return_value = (mock_ship, "Loaded")

        adapter = ShipIOAdapter(ship_io_class=mock_ship_io_class)
        ship, message = adapter.load_ship(0, 0)

        # Should delegate to ShipIO even with zero dimensions
        mock_ship_io_class.load_ship.assert_called_once_with(0, 0)

    def test_load_ship_with_negative_dimensions(self):
        """Test load_ship handles negative dimensions gracefully."""
        from game.ui.services.ship_io_adapter import ShipIOAdapter

        mock_ship_io_class = MagicMock()
        mock_ship_io_class.load_ship.return_value = (None, "Invalid dimensions")

        adapter = ShipIOAdapter(ship_io_class=mock_ship_io_class)
        ship, message = adapter.load_ship(-100, -100)

        # Should delegate to ShipIO
        mock_ship_io_class.load_ship.assert_called_once_with(-100, -100)
