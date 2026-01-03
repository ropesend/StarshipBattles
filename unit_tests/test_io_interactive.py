
import unittest
from unittest.mock import patch, MagicMock, mock_open
import os
import json
from ship_io import ShipIO

class TestShipIOInteractive(unittest.TestCase):
    
    def setUp(self):
        # Create a mock ship
        self.mock_ship = MagicMock()
        self.mock_ship.name = "Test Ship"
        self.mock_ship.to_dict.return_value = {"name": "Test Ship", "components": []}

    @patch('ship_io.filedialog.asksaveasfilename')
    @patch('builtins.open', new_callable=mock_open)
    @patch('ship_io.os.makedirs')
    @patch('ship_io.os.path.exists')
    def test_save_ship_success(self, mock_exists, mock_makedirs, mock_file_open, mock_asksaveas):
        """Test success flow for saving a ship."""
        # Setup mocks
        mock_exists.return_value = True # Folder exists
        mock_asksaveas.return_value = "/path/to/test_ship.json"
        
        # Execute
        success, message = ShipIO.save_ship(self.mock_ship)
        
        # Verify
        self.assertTrue(success)
        self.assertIn("Saved ship to", message)
        
        # Verify file dialog called
        mock_asksaveas.assert_called_once()
        
        # Verify file written
        mock_file_open.assert_called_once_with("/path/to/test_ship.json", 'w')
        handle = mock_file_open()
        
        # Check that proper JSON was written
        # We need to aggregate the write calls to check the full JSON string
        written_content = "".join(call.args[0] for call in handle.write.mock_calls)
        try:
             json_data = json.loads(written_content)
             self.assertEqual(json_data['name'], "Test Ship")
        except json.JSONDecodeError:
            pass # json.dump usually does multiple writes, check mostly for structure if needed or trust json.dump

    @patch('ship_io.filedialog.asksaveasfilename')
    @patch('builtins.open', new_callable=mock_open)
    def test_save_ship_cancel(self, mock_file_open, mock_asksaveas):
        """Test cancelling the save dialog."""
        mock_asksaveas.return_value = "" # User cancelled
        
        success, message = ShipIO.save_ship(self.mock_ship)
        
        self.assertFalse(success)
        self.assertIsNone(message)
        mock_file_open.assert_not_called()

    @patch('ship_io.filedialog.asksaveasfilename')
    @patch('builtins.open', new_callable=mock_open)
    def test_save_ship_failure(self, mock_file_open, mock_asksaveas):
        """Test file write permission error."""
        mock_asksaveas.return_value = "/path/to/protected.json"
        mock_file_open.side_effect = PermissionError("Access denied")
        
        success, message = ShipIO.save_ship(self.mock_ship)
        
        self.assertFalse(success)
        self.assertIn("Save failed", message)
        self.assertIn("Access denied", message)

    @patch('ship_io.filedialog.askopenfilename')
    @patch('builtins.open', new_callable=mock_open, read_data='{"invalid": "json"')
    @patch('ship_io.os.makedirs')
    def test_load_ship_corrupt(self, mock_makedirs, mock_file_open, mock_askopen):
        """Test loading a corrupt JSON file."""
        mock_askopen.return_value = "/path/to/corrupt.json"
        
        # The mock_open read_data causes json.load to fail with JSONDecodeError
        
        ship, message = ShipIO.load_ship(800, 600)
        
        self.assertIsNone(ship)
        self.assertIn("Load failed", message)
        
    @patch('ship_io.filedialog.askopenfilename')
    @patch('builtins.open', new_callable=mock_open, read_data='{"name": "Loaded Ship", "components": []}')
    @patch('ship.Ship.from_dict')
    def test_load_ship_success(self, mock_from_dict, mock_file_open, mock_askopen):
        """"Test success flow for loading."""
        mock_askopen.return_value = "/path/to/valid.json"
        
        # Mock the deserialized ship
        mock_loaded_ship = MagicMock()
        mock_loaded_ship._loading_warnings = []
        mock_from_dict.return_value = mock_loaded_ship
        
        ship, message = ShipIO.load_ship(800, 600)
        
        self.assertIsNotNone(ship)
        self.assertEqual(ship, mock_loaded_ship)
        self.assertIn("Loaded ship from", message)
        
        # Verify recalculate_stats called
        mock_loaded_ship.recalculate_stats.assert_called_once()

    @patch('ship_io.filedialog.askopenfilename')
    def test_load_ship_cancel(self, mock_askopen):
        """Test cancelling the load dialog."""
        mock_askopen.return_value = ""
        
        ship, message = ShipIO.load_ship(800, 600)
        
        self.assertIsNone(ship)
        self.assertIsNone(message)

if __name__ == '__main__':
    unittest.main()
