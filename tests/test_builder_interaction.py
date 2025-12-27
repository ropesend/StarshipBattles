
import unittest
import sys
import os
import pygame
from unittest.mock import MagicMock, patch

# Dummy video driver
os.environ["SDL_VIDEODRIVER"] = "dummy"
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from builder_gui import InteractionController
from ship import LayerType

class TestBuilderGUIFix(unittest.TestCase):
    def setUp(self):
        pygame.init()
        self.mock_builder = MagicMock()
        self.mock_view = MagicMock()
        self.controller = InteractionController(self.mock_builder, self.mock_view)
        
        # Setup mock ship
        self.mock_ship = MagicMock()
        self.mock_builder.ship = self.mock_ship
        
        # Setup dragged item
        self.mock_comp = MagicMock()
        self.mock_comp.allowed_layers = [LayerType.CORE]
        self.mock_comp.name = "TestComp"
        self.mock_comp.mass = 10
        self.controller.dragged_item = self.mock_comp
        
        # Setup layer panel mock
        self.mock_builder.layer_panel = MagicMock()

    def test_handle_drop_valid(self):
        """Test _handle_drop with valid component and layer."""
        # Setup: Hit a layer
        self.mock_builder.layer_panel.get_target_layer_at.return_value = LayerType.CORE
        
        # Mock VALIDATOR
        with patch('ship.VALIDATOR') as mock_validator:
            mock_validator.validate_addition.return_value.is_valid = True
            
            # Mock ship.add_component to return True
            self.mock_ship.add_component.return_value = True
            
            # Action
            self.controller._handle_drop((100, 100))
            
            # Verify
            mock_validator.validate_addition.assert_called()
            self.mock_ship.add_component.assert_called_with(self.mock_comp, LayerType.CORE)
            self.mock_builder.update_stats.assert_called()

    def test_handle_drop_invalid_restriction(self):
        """Test _handle_drop when validator rejects."""
        self.mock_builder.layer_panel.get_target_layer_at.return_value = LayerType.CORE
        
        with patch('ship.VALIDATOR') as mock_validator:
            mock_validator.validate_addition.return_value.is_valid = False
            mock_validator.validate_addition.return_value.errors = ["Some Restriction"]
            
            self.controller._handle_drop((100, 100))
            
            self.mock_builder.show_error.assert_called_with("Cannot place: Some Restriction")
            self.mock_ship.add_component.assert_not_called()

if __name__ == '__main__':
    unittest.main()
