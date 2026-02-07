from unittest.mock import patch, MagicMock, mock_open
import os
from game.simulation.systems.persistence import ShipIO


@patch('game.simulation.systems.persistence.tk_root', True)
class TestShipIOInteractive:

    @staticmethod
    def create_mock_ship():
        """Create a mock ship for testing."""
        mock_ship = MagicMock()
        mock_ship.name = "Test Ship"
        mock_ship.to_dict.return_value = {"name": "Test Ship", "components": []}
        return mock_ship

    @patch('game.simulation.systems.persistence.filedialog.asksaveasfilename')
    @patch('game.simulation.systems.persistence.save_json')
    @patch('game.simulation.systems.persistence.os.makedirs')
    @patch('game.simulation.systems.persistence.os.path.exists')
    def test_save_ship_success(self, mock_exists, mock_makedirs, mock_save_json, mock_asksaveas):
        """Test success flow for saving a ship."""
        mock_ship = self.create_mock_ship()
        # Setup mocks
        mock_exists.return_value = True  # Folder exists
        mock_asksaveas.return_value = "/path/to/test_ship.json"
        mock_save_json.return_value = True  # Simulate successful save

        # Execute
        success, message = ShipIO.save_ship(mock_ship)

        # Verify
        assert success is True
        assert "Saved ship to" in message

        # Verify file dialog called
        mock_asksaveas.assert_called_once()

        # Verify save_json was called with correct args
        mock_save_json.assert_called_once()
        call_args = mock_save_json.call_args
        assert call_args[0][0] == "/path/to/test_ship.json"
        assert call_args[0][1]['name'] == "Test Ship"

    @patch('game.simulation.systems.persistence.filedialog.asksaveasfilename')
    @patch('builtins.open', new_callable=mock_open)
    def test_save_ship_cancel(self, mock_file_open, mock_asksaveas):
        """Test cancelling the save dialog."""
        mock_ship = self.create_mock_ship()
        mock_asksaveas.return_value = ""  # User cancelled

        success, message = ShipIO.save_ship(mock_ship)

        assert success is False
        assert message is None
        mock_file_open.assert_not_called()

    @patch('game.simulation.systems.persistence.filedialog.asksaveasfilename')
    @patch('game.simulation.systems.persistence.save_json')
    def test_save_ship_failure(self, mock_save_json, mock_asksaveas):
        """Test file write failure."""
        mock_ship = self.create_mock_ship()
        mock_asksaveas.return_value = "/path/to/protected.json"
        mock_save_json.return_value = False  # Simulate failed save

        success, message = ShipIO.save_ship(mock_ship)

        assert success is False
        assert "Failed to save" in message

    @patch('game.simulation.systems.persistence.filedialog.askopenfilename')
    @patch('game.simulation.systems.persistence.load_json_required')
    @patch('game.simulation.systems.persistence.os.makedirs')
    def test_load_ship_corrupt(self, mock_makedirs, mock_load_json_required, mock_askopen):
        """Test loading a corrupt JSON file."""
        mock_askopen.return_value = "/path/to/corrupt.json"
        import json
        mock_load_json_required.side_effect = json.JSONDecodeError("JSON decode error", "", 0)

        ship, message = ShipIO.load_ship(800, 600)

        assert ship is None
        assert "Load failed" in message

    @patch('game.simulation.systems.persistence.filedialog.askopenfilename')
    @patch('game.simulation.systems.persistence.load_json_required')
    @patch('game.simulation.entities.ship.Ship.from_dict')
    def test_load_ship_success(self, mock_from_dict, mock_load_json_required, mock_askopen):
        """"Test success flow for loading."""
        mock_askopen.return_value = "/path/to/valid.json"
        mock_load_json_required.return_value = {"name": "Loaded Ship", "components": []}

        # Mock the deserialized ship
        mock_loaded_ship = MagicMock()
        mock_loaded_ship._loading_warnings = []
        mock_from_dict.return_value = mock_loaded_ship

        ship, message = ShipIO.load_ship(800, 600)

        assert ship is not None
        assert ship == mock_loaded_ship
        assert "Loaded ship from" in message

        # Verify recalculate_stats called
        mock_loaded_ship.recalculate_stats.assert_called_once()

    @patch('game.simulation.systems.persistence.filedialog.askopenfilename')
    def test_load_ship_cancel(self, mock_askopen):
        """Test cancelling the load dialog."""
        mock_askopen.return_value = ""

        ship, message = ShipIO.load_ship(800, 600)

        assert ship is None
        assert message is None
